"""Kiểm file video cuối: độ to, đỉnh thật, cỡ, fps, khung đen, đứng hình, khung chớp, lặng, lệch dài hình/âm.

Một lượt ffmpeg (blackdetect, freezedetect, signalstats, ebur128, silencedetect) + ffprobe. Chữ ra cùng khuôn công cụ cũ
để `soi-qc.py --check` đọc được: dòng đầu `✓|!|✗ ...`, dòng hai là cỡ·fps·độ dài·độ to, rồi mỗi phát hiện một dòng
`! <thông báo>  → <cách sửa>` (cảnh báo) hoặc `✗ ...` (lỗi); mốc thời gian trong thông báo dạng `m:ss.s`.
«Không đạt» vẫn thoát mã 0 (chỉ lỗi thật như không mở được file mới là 1).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from am_cuoi import doc_ebur128  # noqa: E402
from chung import LoiKit, chay_lenh, json_an_toan  # noqa: E402

NGUONG_LUFS = 1.5      # |I − đích| lớn hơn thì cảnh báo
NGUONG_DINH = -1.0     # dBFS: đỉnh thật cao hơn thì cảnh báo
NGUONG_CHOP = 30       # độ lệch sáng (YAVG) của khung chớp so với khung kế bên
NGUONG_CHOP_NEN = 15   # hai khung kế bên phải gần nhau hơn mức này (đổi cảnh một lần thì không phải chớp)
MAX_CHOP = 10


def moc(t: float) -> str:
    """Giây → m:ss.s (làm tròn 0,1 s)."""
    t = max(0.0, t)
    d = round(t * 10) / 10
    return f"{int(d // 60)}:{d % 60:04.1f}"


def doc_black(txt: str) -> list[dict]:
    return [{"start": float(m[1]), "end": float(m[2]), "duration": float(m[3])}
            for m in re.finditer(r"black_start:([\d.]+)\s+black_end:([\d.]+)\s+black_duration:([\d.]+)", txt)]


def doc_freeze(txt: str, dai: float) -> list[dict]:
    ra, bd = [], None
    for m in re.finditer(r"freeze_(start|end|duration):\s*([\d.]+)", txt):
        if m[1] == "start":
            if bd:
                ra.append(bd)
            bd = {"start": float(m[2]), "end": None, "duration": None}
        elif bd and m[1] == "end":
            bd["end"] = float(m[2])
        elif bd:
            bd["duration"] = float(m[2])
    if bd:
        ra.append(bd)
    for b in ra:  # đứng hình tới hết file: ffmpeg không in freeze_end
        b["end"] = b["end"] if b["end"] is not None else dai
        b["duration"] = b["duration"] if b["duration"] is not None else b["end"] - b["start"]
    return ra


def doc_silence(txt: str, dai: float) -> list[dict]:
    ra, bd = [], None
    for m in re.finditer(r"silence_start:\s*(-?[\d.]+)|silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)", txt):
        if m[1] is not None:
            if bd:
                ra.append(bd)
            bd = {"start": max(0.0, float(m[1])), "end": None, "duration": None}
        elif bd:
            bd["end"], bd["duration"] = float(m[2]), float(m[3])
    if bd:
        ra.append(bd)
    for b in ra:  # lặng tới hết file
        b["end"] = b["end"] if b["end"] is not None else dai
        b["duration"] = b["duration"] if b["duration"] is not None else b["end"] - b["start"]
    return ra


def doc_yavg(txt: str) -> list[tuple[float, float]]:
    """[(giây, độ sáng trung bình)] từ đầu ra metadata=print của signalstats."""
    ra, t = [], 0.0
    for dong in txt.splitlines():
        m = re.search(r"pts_time:([\d.]+)", dong)
        if m:
            t = float(m[1])
            continue
        m = re.match(r"lavfi\.signalstats\.YAVG=([\d.]+)", dong.strip())
        if m:
            ra.append((t, float(m[1])))
    return ra


def tim_chop(y: list[tuple[float, float]]) -> list[dict]:
    """Chạy ≤ 2 khung lệch ≥ 30 mức sáng so với khung ngay trước VÀ ngay sau, hai khung này gần nhau (< 15)."""
    ra, i = [], 1
    while i < len(y) - 1:
        for n in (1, 2):
            if i + n >= len(y):
                break
            truoc, sau = y[i - 1][1], y[i + n][1]
            mau = y[i:i + n]
            if abs(truoc - sau) < NGUONG_CHOP_NEN and all(abs(v - truoc) >= NGUONG_CHOP and abs(v - sau) >= NGUONG_CHOP for _, v in mau):
                ra.append({"t": y[i][0], "frames": n, "kind": "sáng" if mau[0][1] > truoc else "tối"})
                i += n
                break
        i += 1
    return ra


def doc_fps(chu: str) -> float:
    if "/" in chu:
        a, b = chu.split("/")
        return float(a) / float(b) if float(b) else 0.0
    return float(chu or 0)


def phan_tich_probe(pj: dict) -> dict:
    """ffprobe -show_streams -show_format -of json → {duration, video, audio}."""
    dai = float(pj.get("format", {}).get("duration") or 0)
    hinh = am = None
    for s in pj.get("streams", []):
        if s.get("codec_type") == "video" and hinh is None and not s.get("disposition", {}).get("attached_pic") \
                and s.get("codec_name") not in ("mjpeg", "png"):
            w, h = int(s["width"]), int(s["height"])
            xoay = next((abs(int(float(d["rotation"]))) for d in s.get("side_data_list", []) if "rotation" in d), 0)
            if xoay in (90, 270):
                w, h = h, w
            hinh = {"width": w, "height": h, "fps": round(doc_fps(s.get("r_frame_rate", "0")), 3), "codec": s.get("codec_name"),
                    "duration": float(s.get("duration") or dai)}
        elif s.get("codec_type") == "audio" and am is None:
            am = {"codec": s.get("codec_name"), "duration": float(s.get("duration") or dai)}
    return {"duration": dai, "video": hinh, "audio": am}


def phan_xu(do: dict, yc: dict) -> list[dict]:
    """Từ số đo → danh sách phát hiện {id, level: fail|warn, message, fix}. `yc`: lufs, size, fps, freeze_min, silence_min."""
    ra: list[dict] = []

    def them(id_, level, msg, fix):
        ra.append({"id": id_, "level": level, "message": msg, "fix": fix})

    dai, v, a = do["duration"], do["video"], do["audio"]
    if not v:
        them("no_picture", "fail", "không có luồng hình", "kiểm lại file đầu vào")
    if not a:
        them("no_sound", "warn", "không có luồng âm", "ghép âm master vào (kit.py ghep)")
    den = do["black"]
    if v and dai and sum(b["duration"] for b in den) >= 0.9 * dai:
        them("all_black", "fail", "gần như cả phim là khung đen", "kiểm lại bước dựng hình")
    elif v:
        for b in den:
            if b["duration"] < 1 and (b["start"] <= 0.05 or b["end"] >= dai - 0.05):
                continue
            them("black", "warn", f"khung đen {moc(b['start'])}–{moc(b['end'])} ({b['duration']:.2f} s)", "soi lại cảnh ở mốc này")
    for c in do["flashes"][:MAX_CHOP]:
        them("flash", "warn", f"khung chớp {c['kind']} ở {moc(c['t'])} ({c['frames']} khung)", "soi từng khung quanh mốc này")
    for f in do["frozen"]:
        them("frozen", "warn", f"hình đứng yên {moc(f['start'])}–{moc(f['end'])} ({f['duration']:.1f} s)", "thẻ/ảnh đứng yên cố ý thì bỏ qua")
    if a:
        I, dinh = do["lufs"], do["true_peak"]
        if I is None or I == float("-inf") or I < -60:
            them("silent_sound", "fail", "âm gần như im lặng hoặc không đo được độ to", "kiểm lại bước trộn")
        else:
            if abs(I - yc["lufs"]) > NGUONG_LUFS:
                them("loudness", "warn", f"độ to {I:.1f} LUFS, đích {yc['lufs']:.0f} (lệch quá {NGUONG_LUFS} LU)", "kit.py master --lufs rồi ghép lại")
            if dinh is not None and dinh > NGUONG_DINH:
                them("peak", "warn", f"đỉnh thật {dinh:.1f} dBFS, cao hơn {NGUONG_DINH:.0f}", "kit.py master --tp thấp hơn rồi ghép lại")
        for s in do["silences"]:
            if s["start"] <= 0.05 or s["end"] >= a["duration"] - 0.05:
                continue
            them("silence", "warn", f"im lặng {moc(s['start'])}–{moc(s['end'])} ({s['duration']:.1f} s) giữa phim", "cố ý (khoảng thở) thì bỏ qua")
    if v and a:
        if v["duration"] - a["duration"] > 0.5:
            them("sound_short", "warn", f"âm ngắn hơn hình {v['duration'] - a['duration']:.1f} s", "âm phải phủ hết hình")
        elif a["duration"] - v["duration"] > 0.5:
            them("picture_short", "warn", f"hình ngắn hơn âm {a['duration'] - v['duration']:.1f} s", "hình phải phủ hết âm")
    if v and yc.get("size"):
        w, h = (int(x) for x in yc["size"].lower().split("x"))
        if (v["width"], v["height"]) != (w, h):
            them("size", "fail", f"cỡ hình {v['width']}×{v['height']}, cần {w}×{h}", "dựng/xuất lại đúng cỡ")
    if v and yc.get("fps") and abs(v["fps"] - yc["fps"]) > 0.05:
        them("fps", "fail", f"{v['fps']:g} fps, cần {yc['fps']:g}", "dựng/xuất lại đúng fps")
    return ra


def ket_luan(findings: list[dict]) -> str:
    if any(f["level"] == "fail" for f in findings):
        return "not_ready"
    return "look" if findings else "ready"


def dinh_dang(tep: str, verdict: str, do: dict, findings: list[dict]) -> str:
    n = len(findings)
    dau = {"ready": f"✓ Sẵn sàng giao: {tep}", "look": f"! {n} điều cần xem: {tep}", "not_ready": f"✗ Chưa đạt: {tep}"}[verdict]
    v = do["video"]
    kich = f"{v['width']}×{v['height']} {v['fps']:g} fps · " if v else ""
    am = f" · {do['lufs']:.1f} LUFS, đỉnh {do['true_peak']:.1f} dBFS" if do["audio"] and do["lufs"] is not None else ""
    dong = [dau, f"  {kich}{do['duration']:.1f} s{am}"]
    for f in findings:
        dong.append(f"{'✗' if f['level'] == 'fail' else '!'} {f['message']}  → {f['fix']}")
    return "\n".join(dong)


# --- chạy -----------------------------------------------------------------------------------------------------------

def do_video(tep: str, yc: dict) -> dict:
    pj = json.loads(chay_lenh(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", tep]).stdout.decode("utf-8", "replace"))
    tt = phan_tich_probe(pj)
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", tep]
    if tt["video"]:
        cmd += ["-map", "0:v:0", "-vf", f"blackdetect=d=0.1:pix_th=0.03,freezedetect=n=-70dB:d={yc['freeze_min']},"
                                        f"signalstats,metadata=mode=print:key=lavfi.signalstats.YAVG:file=-"]
    if tt["audio"]:
        cmd += ["-map", "0:a:0", "-af", f"ebur128=peak=true:framelog=quiet,silencedetect=noise=-50dB:d={yc['silence_min']}"]
    cmd += ["-f", "null", "-"]
    try:
        r = subprocess.run(cmd, capture_output=True)
    except FileNotFoundError as e:
        raise LoiKit("không tìm thấy ffmpeg. Cài bằng: winget install Gyan.FFmpeg (rồi mở lại cửa sổ lệnh)") from e
    if r.returncode != 0:
        duoi = "\n".join(r.stderr.decode("utf-8", "replace").strip().splitlines()[-8:])
        raise LoiKit(f"ffmpeg không đọc hết được {tep}:\n{duoi}")
    err, out = r.stderr.decode("utf-8", "replace"), r.stdout.decode("utf-8", "replace")
    lufs = dinh = None
    if tt["audio"]:
        try:
            e = doc_ebur128(err)
            lufs, dinh = e["I"], e["dinh"]
        except LoiKit:
            pass
    dv = tt["video"]["duration"] if tt["video"] else 0
    return {**tt, "lufs": lufs, "true_peak": dinh, "black": doc_black(err), "frozen": doc_freeze(err, dv),
            "flashes": tim_chop(doc_yavg(out)), "silences": doc_silence(err, tt["audio"]["duration"] if tt["audio"] else 0)}


def dang_ky(p: argparse.ArgumentParser) -> None:
    p.add_argument("video")
    p.add_argument("--lufs", type=float, default=-14.0, help="độ to đích (mặc định −14)")
    p.add_argument("--size", help="cỡ hình cần, vd 1920x1080")
    p.add_argument("--fps", type=float, help="fps cần, vd 24")
    p.add_argument("--freeze-min", type=float, default=2.0, help="đứng hình tối thiểu (giây) mới báo (mặc định 2)")
    p.add_argument("--silence-min", type=float, default=2.0, help="im lặng tối thiểu (giây) mới báo (mặc định 2)")
    p.add_argument("--json", action="store_true")


def chay(a: argparse.Namespace) -> int:
    if not Path(a.video).is_file():
        raise LoiKit(f"không thấy {a.video}")
    if a.size and not re.fullmatch(r"\d+[xX]\d+", a.size):
        raise LoiKit("--size phải dạng WxH, vd 1920x1080")
    yc = {"lufs": a.lufs, "size": a.size, "fps": a.fps, "freeze_min": a.freeze_min, "silence_min": a.silence_min}
    do = do_video(a.video, yc)
    findings = phan_xu(do, yc)
    verdict = ket_luan(findings)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if a.json:
        print(json.dumps(json_an_toan({"file": a.video, "verdict": verdict, "findings": findings,
                                      "streams": {"duration": do["duration"], "video": do["video"], "audio": do["audio"]},
                                      "measured": {k: do[k] for k in ("lufs", "true_peak", "black", "frozen", "flashes", "silences")}}),
                         ensure_ascii=False, indent=2))
    else:
        print(dinh_dang(a.video, verdict, do, findings))
    return 0
