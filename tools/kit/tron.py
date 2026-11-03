"""Trộn âm theo mix.json: giọng, nhạc nền (nối, lặp, mờ, ease, ép nhỏ theo giọng) và tiếng động (cue).

Cùng lược đồ mix.json mà repo đã dùng; cùng số học để bản trộn khớp bản đã duyệt:
  - nguồn nào cũng qua aresample 48000 + aformat stereo (mono → stereo hạ 3 dB mỗi kênh, do ffmpeg);
  - cue: gain = db − đỉnh tệp (đo SAU phép trên, volumedetect) làm tròn 0,1 dB; `cut` chỉ lấy `cut` giây đầu, mờ 0,3 s cuối;
  - có `limit` thì alimiter level=false (giữ nguyên mức); KHÔNG có thì alimiter mặc định (auto level, kéo mức lên) — đúng hành vi cũ;
  - đệm apad TRƯỚC limiter vì sau limiter tệp có thể ngắn đi.
Đồ thị ffmpeg ghi ra TỆP script nên trộn hàng nghìn cue không vướng giới hạn dòng lệnh Windows. Mỗi tệp âm KHÁC NHAU
thường thêm một «-i» vào dòng lệnh; khi tổng vượt GIOI_HAN_DONG_LENH (Windows cho ~32.000 ký tự) thì tệp cue được liên kết
(hoặc chép) vào thư mục tạm với tên ngắn và đọc bằng «amovie=» trong đồ thị, ffmpeg chạy với thư mục đó làm thư mục hiện hành.

Hỗ trợ: duration, voice, sfx_dir, fade_out, limit, music{volume, duck, beds[file|files, from, to, fade_in, fade_out, loop,
crossfade, volume, lufs, ease]}, cues[sound, t, db, cut, align:"start"]. `bus`, `weight` được đọc và bỏ qua có cảnh báo
(bản cũ cũng không dùng). Chưa hỗ trợ (báo lỗi, không bỏ lặng lẽ): align peak|end, gain:"in_band", âm «a+b» nhiều lớp,
âm tra theo «bộ:tên», `--stems`, mọi khoá khác.
"""
from __future__ import annotations

import argparse
import functools
import json
import math
import os
import re
import shutil
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from am_cuoi import do_ebur128  # noqa: E402
from chung import LoiKit, chay_lenh, ghi_nguyen_tu, json_an_toan  # noqa: E402

RATE = 48000
DUCK_MAC_DINH = {"threshold": 0.02, "ratio": 8, "attack": 20, "release": 350}
DUCK_MIEN = {"threshold": (0.000976563, 1), "ratio": (1, 20), "attack": (0.01, 2000), "release": (0.01, 9000)}
KHOA_GOC = {"duration", "voice", "sfx_dir", "fade_out", "limit", "music", "cues"}
KHOA_NEN = {"volume", "duck", "beds"}
KHOA_BED = {"file", "files", "from", "to", "fade_in", "fade_out", "loop", "crossfade", "volume", "lufs", "ease"}
KHOA_CUE = {"sound", "t", "db", "cut", "align", "gain", "weight", "bus"}
DUOI_AM = (".mp3", ".wav", ".ogg", ".m4a", ".flac")
FMT_IN = f"aresample={RATE},aformat=sample_fmts=fltp:channel_layouts=stereo"
TEN_CACHE = ".kit-dinh-cache.json"
GIOI_HAN_DONG_LENH = 24000  # ký tự; Windows cho 32.767, chừa chỗ cho tên chương trình và các cờ


def fmt(x: float) -> str:
    """Số gọn cho đồ thị: tối đa 4 số lẻ, bỏ số 0 thừa."""
    s = f"{x:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def ms_tron(giay: float) -> int:
    """Giây → mili giây, làm tròn nửa lên như Math.round (Python round() làm tròn chẵn)."""
    return math.floor(giay * 1000 + 0.5)


def la_so(x) -> bool:
    """Số hữu hạn (không phải bool, NaN, Infinity: json.loads của Python nhận NaN/Infinity)."""
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def la_chuoi_ten(x) -> bool:
    return isinstance(x, str) and bool(x.strip())


# --- đọc kế hoạch ---------------------------------------------------------------------------------------------------

def chuan_ease(ease, ten: str = "ease") -> list[dict]:
    if not isinstance(ease, list):
        raise LoiKit(f"«{ten}» phải là danh sách bước {{at, to, over}}")
    buoc: list[dict] = []
    for k, e in enumerate(ease, 1):
        e = e if isinstance(e, dict) else {}
        s = {"at": e.get("at"), "to": e.get("to"), "over": e.get("over", 0)}
        if not (la_so(s["at"]) and s["at"] >= 0):
            raise LoiKit(f"{ten} bước {k}: «at» phải là giây ≥ 0")
        if not (la_so(s["to"]) and 0 <= s["to"] <= 4):
            raise LoiKit(f"{ten} bước {k}: «to» phải từ 0 đến 4 (1 = lớp nền như đã đặt)")
        if not (la_so(s["over"]) and s["over"] >= 0):
            raise LoiKit(f"{ten} bước {k}: «over» phải là giây ≥ 0")
        if buoc and s["at"] < buoc[-1]["at"] + buoc[-1]["over"]:
            raise LoiKit(f"{ten} bước {k} bắt đầu lúc {fmt(s['at'])} s, trước khi bước {k - 1} xong ({fmt(buoc[-1]['at'] + buoc[-1]['over'])} s): "
                         f"các bước ease phải nối tiếp")
        buoc.append(s)
    return buoc


def ease_expr(buoc: list[dict]) -> str:
    """Biểu thức volume theo t: mức bắt đầu 1; mỗi bước đổi tuyến tính tới «to» trong «over» giây kể từ «at»."""
    muc, phan = 1.0, []
    for s in buoc:
        phan.append({**s, "tu": muc})
        muc = s["to"]
    bt = fmt(muc)
    for s in reversed(phan):
        doc = (f"if(lt(t,{fmt(s['at'] + s['over'])}),{fmt(s['tu'])}+({fmt(s['to'] - s['tu'])})*(t-{fmt(s['at'])})/{fmt(s['over'])},{bt})"
               if s["over"] > 0 else bt)
        bt = f"if(lt(t,{fmt(s['at'])}),{fmt(s['tu'])},{doc})"
    return bt


def gain_cue(db: float, dinh: float) -> float:
    return round(db - dinh, 1)


def do_dai_ffprobe(tep) -> float:
    r = chay_lenh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(tep)])
    try:
        return float(r.stdout.decode().strip())
    except ValueError as e:
        raise LoiKit(f"không đọc được độ dài của {tep}") from e


def _duong(ten: str, goc: Path) -> str:
    p = Path(ten)
    return str(p if p.is_absolute() else goc / p)


def tim_am(ten, goc: Path, sfx_dir: str) -> str:
    if not isinstance(ten, str) or not ten:
        raise LoiKit("cue thiếu «sound»")
    if "+" in ten:
        raise LoiKit(f"âm «{ten}» nhiều lớp (a+b) chưa hỗ trợ")
    if "/" in ten or "\\" in ten or "." in ten:
        return _duong(ten, goc)
    if ":" in ten:
        raise LoiKit(f"âm «{ten}» tra theo bộ âm (bộ:tên) chưa hỗ trợ; ghi đường dẫn tệp")
    for duoi in DUOI_AM:
        p = Path(_duong(sfx_dir, goc)) / (ten + duoi)
        if p.exists():
            return str(p)
    raise LoiKit(f"không tìm thấy âm «{ten}» trong {sfx_dir} (đã thử {', '.join(DUOI_AM)})")


def doc_ke_hoach(plan: dict, goc: Path, do_dai=do_dai_ffprobe) -> dict:
    """Kiểm và chuẩn hoá mix.json. `goc` = thư mục chứa mix.json (đường dẫn tương đối tính từ đây)."""
    if not isinstance(plan, dict):
        raise LoiKit("mix.json phải là một đối tượng JSON")
    la = sorted(set(plan) - KHOA_GOC)
    if la:
        raise LoiKit(f"khoá {', '.join(la)} chưa hỗ trợ ở mức ngoài cùng (hỗ trợ: {', '.join(sorted(KHOA_GOC))})")
    warnings: list[str] = []
    if plan.get("voice") is not None and not la_chuoi_ten(plan["voice"]):
        raise LoiKit("«voice» phải là đường dẫn tệp (chuỗi)")
    voice = _duong(plan["voice"], goc) if plan.get("voice") else None
    tong = plan.get("duration")
    if tong is None:
        if not voice:
            raise LoiKit("cần «duration» hoặc «voice» để biết độ dài bản trộn")
        tong = do_dai(voice)
    if not (la_so(tong) and tong > 0):
        raise LoiKit("«duration» phải là số giây > 0")
    limit = plan.get("limit")
    if limit is not None and not (la_so(limit) and 0.0625 <= limit <= 1):
        raise LoiKit("«limit» phải từ 0.0625 đến 1")
    sfx_dir = plan.get("sfx_dir", "audio/sfx")
    if not la_chuoi_ten(sfx_dir):
        raise LoiKit("«sfx_dir» phải là đường dẫn thư mục (chuỗi)")
    fade_out = plan.get("fade_out", 0)
    if not (la_so(fade_out) and fade_out >= 0):
        raise LoiKit("«fade_out» phải là số giây ≥ 0")

    nen = plan.get("music", {})
    if not isinstance(nen, dict):
        raise LoiKit("«music» phải là đối tượng {volume, duck, beds}")
    la = sorted(set(nen) - KHOA_NEN)
    if la:
        raise LoiKit(f"khoá {', '.join(la)} trong «music» chưa hỗ trợ")
    duck = nen.get("duck", True)
    if isinstance(duck, dict):
        for k, v in duck.items():
            if k not in DUCK_MAC_DINH:
                raise LoiKit(f"«duck» không có khoá «{k}» (threshold, ratio, attack, release)")
            lo, hi = DUCK_MIEN[k]
            if not (la_so(v) and lo <= v <= hi):
                raise LoiKit(f"«duck.{k}» phải từ {lo} đến {hi}")
        duck = {**DUCK_MAC_DINH, **duck}
    elif duck is True:
        duck = dict(DUCK_MAC_DINH)
    elif duck is False:
        duck = None
    else:
        raise LoiKit("«duck» phải là true, false hoặc {threshold, ratio, attack, release}")

    beds = []
    ds_nen = nen.get("beds", [])
    if not isinstance(ds_nen, list):
        raise LoiKit("«music.beds» phải là danh sách các lớp nền")
    for i, b in enumerate(ds_nen, 1):
        if not isinstance(b, dict):
            raise LoiKit(f"lớp nền {i} phải là đối tượng {{file, from, to, ...}}")
        la = sorted(set(b) - KHOA_BED)
        if la:
            raise LoiKit(f"khoá {', '.join(la)} của lớp nền {i} chưa hỗ trợ")
        files = b.get("files") or ([b["file"]] if b.get("file") else [])
        if not files:
            raise LoiKit(f"lớp nền {i} thiếu «file» hoặc «files»")
        if not isinstance(files, list) or not all(la_chuoi_ten(f) for f in files):
            raise LoiKit(f"lớp nền {i}: «file» là một đường dẫn, «files» là danh sách đường dẫn (chuỗi)")
        files = [_duong(f, goc) for f in files]
        for k, toi_thieu in (("from", 0), ("to", 0), ("fade_in", 0), ("fade_out", 0), ("crossfade", 0), ("volume", 0)):
            if k in b and not (la_so(b[k]) and b[k] >= toi_thieu):
                raise LoiKit(f"lớp nền {i}: «{k}» phải là số ≥ {toi_thieu}")
        if b.get("lufs") is not None and not la_so(b["lufs"]):
            raise LoiKit(f"lớp nền {i}: «lufs» phải là số (độ to đích)")
        tu, den = b.get("from", 0), min(b.get("to", tong), tong)
        dai = den - tu
        if dai <= 0:
            warnings.append(f"lớp nền {i} bắt đầu sau khi phim hết: bỏ")
            continue
        cf = b.get("crossfade", 2)
        if not b.get("loop"):
            co = sum(do_dai(f) for f in files) - cf * (len(files) - 1)
            if co < dai - 0.5:
                warnings.append(f"lớp nền {i} dài {co:.1f} s nhưng đoạn của nó {dai:.1f} s: sau đó im (làm dài hơn, hoặc «loop»: true)")
        beds.append({"files": files, "from": tu, "to": den, "len": dai, "loop": bool(b.get("loop")), "crossfade": cf,
                     "fade_in": b.get("fade_in", 1), "fade_out": b.get("fade_out", 2.5), "volume": b.get("volume", 1),
                     "lufs": b.get("lufs"), "ease": chuan_ease(b["ease"], f"ease của lớp nền {i}") if b.get("ease") else []})

    cues, bo_qua = [], {"bus": 0, "weight": 0}
    ds_cue = plan.get("cues", [])
    if not isinstance(ds_cue, list):
        raise LoiKit("«cues» phải là danh sách các cue {sound, t, db, cut}")
    for i, c in enumerate(ds_cue, 1):
        if not isinstance(c, dict):
            raise LoiKit(f"cue {i} phải là đối tượng {{sound, t, db, cut}}")
        la = sorted(set(c) - KHOA_CUE)
        if la:
            raise LoiKit(f"khoá {', '.join(la)} của cue {i} chưa hỗ trợ")
        if c.get("align", "start") != "start":
            raise LoiKit(f"cue {i}: align «{c['align']}» chưa hỗ trợ (chỉ «start»)")
        if c.get("gain"):
            raise LoiKit(f"cue {i}: gain «{c['gain']}» (in_band) chưa hỗ trợ")
        for k in bo_qua:
            bo_qua[k] += k in c
        db = c.get("db", -16)
        if not (la_so(c.get("t")) and la_so(db) and db <= 0):
            raise LoiKit(f"cue {i}: «t» phải là số giây, «db» số ≤ 0")
        if c.get("cut") is not None and not (la_so(c["cut"]) and c["cut"] > 0):
            raise LoiKit(f"cue {i}: «cut» phải là số giây > 0")
        cues.append({"sound": tim_am(c.get("sound"), goc, sfx_dir), "t": c["t"], "db": db, "cut": c.get("cut")})
    for k, n in bo_qua.items():
        if n:
            warnings.append(f"khoá «{k}» ở {n} cue được bỏ qua (không có tác dụng trong lúc trộn)")
    if not (voice or beds or cues):
        raise LoiKit("không có gì để trộn: cần voice, lớp nền hoặc cue")
    vol = nen.get("volume", 0.2)
    if not (la_so(vol) and 0 <= vol <= 4):
        raise LoiKit("«music.volume» phải từ 0 đến 4")
    return {"total": float(tong), "voice": voice, "fade_out": fade_out, "limit": 0.95 if limit is None else limit,
            "limit_co_dinh": limit is not None, "volume": vol, "duck": duck, "beds": beds, "cues": cues, "warnings": warnings}


# --- đồ thị ---------------------------------------------------------------------------------------------------------

def dung_do_thi(kh: dict, dinh: dict, loud: dict, amovie: bool = False) -> tuple[list[str], str]:
    """Trả (danh sách đối số -i, văn bản đồ thị). `dinh`: đỉnh dBFS từng tệp cue; `loud`: LUFS từng tệp nền có «lufs».

    amovie=True: tệp cue vào đồ thị bằng «amovie=<tên>» (tên tương đối với thư mục hiện hành của ffmpeg, phải là tên
    đơn giản không cần thoát ký tự) thay cho «-i», để số tệp âm khác nhau không đội dòng lệnh. Giọng và nền vẫn «-i»."""
    inputs: list[str] = []
    g: list[str] = []

    def them(f: str, qua_amovie: bool = False) -> str:
        """Nhãn nguồn để viết trong đồ thị: «0:a» (đầu vào -i) hoặc «mN» (đầu ra amovie)."""
        if qua_amovie:
            nhan = f"m{sum(1 for x in g if x.startswith('amovie='))}"
            g.append(f"amovie={f}[{nhan}]")
            return nhan
        inputs.extend(["-i", f])
        return f"{len(inputs) // 2 - 1}:a"

    tong = fmt(kh["total"])
    mix: list[str] = []
    nen_co = bool(kh["beds"])
    ep = bool(kh["voice"] and kh["duck"] and nen_co)
    if kh["voice"]:
        v = them(kh["voice"])
        g.append(f"[{v}]{FMT_IN}" + (",asplit=2[vo][vkey]" if ep else "[vo]"))
        if ep:
            g.append(f"[vkey]apad=whole_dur={tong}[key]")
        mix.append("[vo]")
    for i, b in enumerate(kh["beds"]):
        idx = [them(f) for f in b["files"]]
        chuoi = idx[0]
        for k in range(1, len(idx)):
            g.append(f"[{chuoi}][{idx[k]}]acrossfade=d={fmt(b['crossfade'])}[b{i}j{k}]")
            chuoi = f"b{i}j{k}"
        gain = b["volume"]
        if b["lufs"] is not None:
            muc = [loud[f] for f in b["files"]]
            gain *= 10 ** ((b["lufs"] - sum(muc) / len(muc)) / 20)
        ms = ms_tron(b["from"])
        ease = f",volume='{ease_expr(b['ease'])}':eval=frame" if b["ease"] else ""
        g.append(f"[{chuoi}]{FMT_IN}{',aloop=loop=-1:size=2e9' if b['loop'] else ''},atrim=0:{fmt(b['len'])},asetpts=N/SR/TB,"
                 f"afade=t=in:d={fmt(b['fade_in'])},afade=t=out:st={fmt(max(0, b['len'] - b['fade_out']))}:d={fmt(b['fade_out'])},"
                 f"volume={gain:.4f},adelay={ms}|{ms}{ease}[bed{i}]")
    if nen_co:
        ten_nen = "[beds]" if ep else "[music]"
        g.append("".join(f"[bed{i}]" for i in range(len(kh["beds"]))) + f"amix=inputs={len(kh['beds'])}:normalize=0,volume={fmt(kh['volume'])}{ten_nen}")
        if ep:
            d = kh["duck"]
            g.append(f"[beds][key]sidechaincompress=threshold={fmt(d['threshold'])}:ratio={fmt(d['ratio'])}:attack={fmt(d['attack'])}:release={fmt(d['release'])}[music]")
        mix.append("[music]")

    theo_am: dict[str, list[int]] = {}
    for k, c in enumerate(kh["cues"]):
        theo_am.setdefault(c["sound"], []).append(k)
    for am, ds in theo_am.items():
        n = them(am, amovie)
        g.append(f"[{n}]{FMT_IN}" + (f",asplit={len(ds)}" + "".join(f"[s{k}]" for k in ds) if len(ds) > 1 else f"[s{ds[0]}]"))
        for k in ds:
            c = kh["cues"][k]
            ms = max(0, ms_tron(c["t"]))
            cat = ""
            if c["cut"]:
                cat = f"atrim=0:{fmt(c['cut'])},afade=t=out:st={fmt(max(0, c['cut'] - 0.3))}:d={fmt(min(0.3, c['cut']))},"
            g.append(f"[s{k}]{cat}volume={gain_cue(c['db'], dinh[am]):.1f}dB,adelay={ms}|{ms}[x{k}]")
            mix.append(f"[x{k}]")
    fade = (f",afade=t=out:st={fmt(max(0, kh['total'] - kh['fade_out']))}:d={fmt(min(kh['fade_out'], kh['total']))}" if kh["fade_out"] > 0 else "")
    lim = f"alimiter=limit={fmt(kh['limit'])}" + (":level=false" if kh["limit_co_dinh"] else "")
    g.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0,apad=whole_dur={tong},{lim},atrim=0:{tong}{fade}[out]")
    return inputs, ";\n".join(g)


# --- đo đỉnh (có cache) ---------------------------------------------------------------------------------------------

def do_dinh_mot(tep) -> float:
    """Đỉnh dBFS (volumedetect max_volume) SAU phép aresample + stereo, đúng nguồn của gain cue."""
    r = chay_lenh(["ffmpeg", "-hide_banner", "-nostats", "-i", str(tep), "-vn", "-af", f"{FMT_IN},volumedetect", "-f", "null", "-"])
    m = re.search(r"max_volume:\s*(\S+) dB", r.stderr.decode("utf-8", "replace"))
    if not m:
        raise LoiKit(f"không đo được đỉnh của {tep} (không có âm?)")
    if float(m[1]) <= -90:
        raise LoiKit(f"{tep} im lặng hoàn toàn, không thể đặt mức theo đỉnh")
    return float(m[1])


def do_dinh_nhieu(files, cache: Path) -> dict[str, float]:
    """Đỉnh từng tệp; kết quả lưu ở `cache` theo (đường dẫn, mtime, cỡ) nên lần sau không đo lại tệp không đổi."""
    cu = {}
    if cache.exists():
        try:
            cu = json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cu = {}
    can, ra = [], {}
    for f in dict.fromkeys(str(x) for x in files):
        st = Path(f).stat()
        khoa = str(Path(f).resolve())
        m = cu.get(khoa)
        if m and m.get("mtime_ns") == st.st_mtime_ns and m.get("size") == st.st_size:
            ra[f] = m["dinh"]
        else:
            can.append((f, khoa, st))
    if can:
        with ThreadPoolExecutor(max_workers=8) as ex:
            for (f, khoa, st), d in zip(can, ex.map(lambda x: do_dinh_mot(x[0]), can)):
                ra[f] = d
                cu[khoa] = {"mtime_ns": st.st_mtime_ns, "size": st.st_size, "dinh": d}
        try:
            cache.write_text(json.dumps(cu, ensure_ascii=False), encoding="utf-8")
        except OSError:
            pass  # cache chỉ để chạy nhanh hơn; thư mục chỉ đọc, ổ đầy thì bỏ qua
    return ra


@functools.lru_cache(maxsize=1)
def co_kieu_moi() -> bool:
    """ffmpeg có «-/filter_complex <tệp>» không? Thử chạy thật một đồ thị nhỏ (bản dựng theo ngày như «2023-12-01-git»
    không đoán được từ số phiên bản). Không có thì dùng «-filter_complex_script»."""
    with tempfile.TemporaryDirectory() as td:
        tep = Path(td) / "thu.txt"
        tep.write_text("anullsrc=d=0.01[out]", encoding="utf-8")
        try:
            chay_lenh(["ffmpeg", "-v", "error", "-/filter_complex", str(tep), "-map", "[out]", "-f", "null", "-"])
        except LoiKit as e:
            if "Unrecognized option" in str(e) or "Option not found" in str(e):
                return False
            raise
    return True


def uoc_do_dai_dong_lenh(inputs: list[str], tep_do_thi: str, out: str) -> int:
    return 200 + len(tep_do_thi) + len(out) + sum(len(x) + 3 for x in inputs)


def lien_ket_cue(kh: dict, dinh: dict, thu_muc: Path) -> tuple[dict, dict]:
    """Đặt mỗi tệp cue khác nhau vào `thu_muc` dưới tên ngắn (liên kết cứng, không được thì chép). Trả (kh mới, dinh mới)."""
    ten_ngan: dict[str, str] = {}
    for c in kh["cues"]:
        if c["sound"] not in ten_ngan:
            moi = f"a{len(ten_ngan)}{Path(c['sound']).suffix}"
            try:
                os.link(c["sound"], thu_muc / moi)
            except OSError:
                shutil.copy2(c["sound"], thu_muc / moi)
            ten_ngan[c["sound"]] = moi
    kh2 = {**kh, "cues": [{**c, "sound": ten_ngan[c["sound"]]} for c in kh["cues"]]}
    return kh2, {ten_ngan[f]: d for f, d in dinh.items()}


# --- lệnh -----------------------------------------------------------------------------------------------------------

def dang_ky(p: argparse.ArgumentParser) -> None:
    p.add_argument("mix", help="mix.json (đường dẫn tương đối trong đó tính từ thư mục chứa nó)")
    p.add_argument("--out", required=True, help="WAV 48 kHz stereo ra")
    p.add_argument("--force", action="store_true", help="ghi đè file ra")
    p.add_argument("--json", action="store_true")


def chay(a: argparse.Namespace) -> int:
    mix = Path(a.mix).resolve()
    if not mix.is_file():
        raise LoiKit(f"không thấy {a.mix}")
    try:
        plan = json.loads(mix.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        raise LoiKit(f"{mix.name} không phải JSON hợp lệ: {e}") from e
    kh = doc_ke_hoach(plan, mix.parent)
    tep = [kh["voice"]] if kh["voice"] else []
    tep += [f for b in kh["beds"] for f in b["files"]] + [c["sound"] for c in kh["cues"]]
    thieu = sorted({f for f in tep if not Path(f).is_file()})
    if thieu:
        raise LoiKit("thiếu tệp âm: " + ", ".join(thieu))
    out = Path(a.out)
    if out.exists() and not a.force:
        raise LoiKit(f"{out} đã có; thêm --force để ghi đè")
    dinh = do_dinh_nhieu([c["sound"] for c in kh["cues"]], mix.parent / TEN_CACHE) if kh["cues"] else {}
    loud = {}
    for b in kh["beds"]:
        if b["lufs"] is not None:
            for f in b["files"]:
                muc = do_ebur128(f)["I"]
                if muc == float("-inf"):
                    raise LoiKit(f"không đo được độ to của lớp nền {f} (im lặng)")
                loud[f] = muc
    inputs, do_thi = dung_do_thi(kh, dinh, loud)
    with tempfile.TemporaryDirectory() as td:
        tep_do_thi = Path(td) / "do-thi.txt"
        tam_cue = Path(td) / "cue"
        thu_muc_chay = None
        with ghi_nguyen_tu(out, ghi_de=a.force) as tam:
            ra_tuyet_doi = str(tam.resolve())
            if uoc_do_dai_dong_lenh(inputs, str(tep_do_thi), ra_tuyet_doi) > GIOI_HAN_DONG_LENH:
                tam_cue.mkdir()
                kh2, dinh2 = lien_ket_cue(kh, dinh, tam_cue)
                inputs, do_thi = dung_do_thi(kh2, dinh2, loud, amovie=True)
                thu_muc_chay = tam_cue
            tep_do_thi.write_text(do_thi, encoding="utf-8")
            co = "-/filter_complex" if co_kieu_moi() else "-filter_complex_script"
            chay_lenh(["ffmpeg", "-y", "-v", "error", *inputs, co, str(tep_do_thi), "-map", "[out]", "-ar", str(RATE), "-f", "wav", ra_tuyet_doi],
                      cwd=thu_muc_chay)
    kq = {"out": str(out), "duration": kh["total"], "voice": kh["voice"],
          "beds": [{"files": b["files"], "from": b["from"], "to": b["to"], "loop": b["loop"]} for b in kh["beds"]],
          "cues": len(kh["cues"]), "sounds": {Path(c["sound"]).stem: c["sound"] for c in kh["cues"]},
          "warnings": kh["warnings"], "lufs": do_ebur128(out)["I"]}
    if a.json:
        print(json.dumps(json_an_toan(kq), ensure_ascii=False, indent=2))
    else:
        print(f"trộn {out}: {kq['duration']:.1f} s, {len(kh['beds'])} lớp nền, {kq['cues']} cue, I = {kq['lufs']:.1f} LUFS")
        for w in kh["warnings"]:
            print(f"! {w}")
    return 0
