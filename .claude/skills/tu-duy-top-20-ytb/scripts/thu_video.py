"""Thu danh sách video của kênh YouTube bằng yt-dlp, theo hợp đồng dữ liệu của do_kenh.py.

Dùng:
  python thu_video.py <kênh>... --out-dir <thư mục> [--ds kenh.txt] [--nghi 3] [--so-dai 100] [--lam-lai]
    <kênh>: id kênh (UC…), @handle hoặc URL kênh. --ds: mỗi dòng '<kênh>' hoặc '<tên><TAB><kênh>'.
  Mỗi kênh ghi <khoá>.tsv (id, ngay_dang, thoi_luong_s, view, like, binh_luan, is_short, tieu_de) và <khoá>.meta.json.

Cách làm (mỗi kênh):
  1. --flat-playlist tab /videos và /shorts chỉ để LẤY DANH SÁCH id (mới → cũ). Số view của flat bị làm tròn và tiêu đề bị
     dịch theo ngôn ngữ giao diện, nên mọi số liệu và tiêu đề lấy từ metadata đầy đủ của từng video.
  2. Chọn video cần đọc: 100 video dài mới nhất (cửa sổ liên tục để tính hệ số), 10 video dài nhiều view nhất (theo flat,
     để chọn top rồi đọc số thật), 8 video dài cũ nhất, 15 Shorts mới nhất, 8 Shorts cũ nhất.
  3. Đọc metadata đầy đủ tuần tự (yt-dlp, không cookie, nghỉ giữa các lệnh). Video hội viên đọc không được: đếm vào
     so_hoi_vien (cờ HOI_VIEN). Ngày video đầu = nhỏ nhất trong các video cũ nhất ĐỌC ĐƯỢC.
  4. meta.json có cua_so_tu (ngày của video thứ 100 trong cửa sổ): truyền cho do_kenh.py kenh --cua-so-tu.
Lỗi yt-dlp (mã thoát ≠ 0 ở tab, lô đọc không ra dòng nào, quá thời gian, 429) là LỖI: không ghi file, mã thoát ≠ 0, lần sau
thử lại. Đọc thiếu > 5 % video (không kể hội viên) thì vẫn ghi file nhưng meta có "loi": lần sau tự làm lại, do_kenh.py
--meta từ chối dùng.
Chỉ một tiến trình mỗi thư mục đầu ra: file thu_video.pid (ghi nguyên tử); PID cũ còn sống VÀ dòng lệnh chứa thu_video thì
từ chối chạy (mã 3). Python bị dừng đột ngột có thể để yt-dlp mồ côi: kiểm bằng Get-CimInstance Win32_Process.
Tốc độ: ~1,2 giây mỗi video đọc cộng nghỉ giữa yêu cầu (xem GIAY_MOI_VIDEO); chạy nền xem references/nguon-du-lieu.md.
Chỉ dùng thư viện chuẩn; cần yt-dlp trong PATH.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

NGHI_MAC_DINH = 3.0
SO_DAI_CUA_SO = 100
SO_TOP_VIEW = 10
SO_CU = 8
SO_SHORT_MOI = 15
LO_DUMP = 50
VONG_TIM_NGAY_DAU = 3          # số lần thử thêm 8 video cũ kế tiếp khi cả 8 video cũ nhất là hội viên
GIAY_MOI_VIDEO = 3.0           # ước thận trọng khi đọc lô có --sleep-requests 1 (1 video: 2,2 giây → 3,9 giây); đo lại ở lô lớn
TIMEOUT_GIAY = 1800            # một lệnh yt-dlp quá thời gian này thì coi là lỗi
NGHI_YEU_CAU_GIAY = 1          # --sleep-requests khi đọc lô
TY_LE_THIEU_TOI_DA = 0.05      # đọc thiếu quá mức này (không kể hội viên) thì meta ghi "loi"
COT_TSV = ["id", "ngay_dang", "thoi_luong_s", "view", "like", "binh_luan", "is_short", "tieu_de"]
FLAT_FMT = "%(id)s\t%(duration)s\t%(view_count)s"
DUMP_FMT = "%(.{id,timestamp,duration,view_count,like_count,comment_count,title,channel_id})j"


class DangChay(RuntimeError):
    """Còn một tiến trình thu_video.py khác đang chạy trên cùng thư mục đầu ra."""


class LoiThu(RuntimeError):
    """yt-dlp lỗi hoặc không trả dữ liệu: kênh này chưa thu được, không ghi file."""


# ---------- tiến trình, file PID ----------

def con_song(pid: int) -> bool:
    """Tiến trình pid còn sống không. Không dùng os.kill(pid, 0) trên Windows (nó kết thúc tiến trình)."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        h = k32.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return ctypes.get_last_error() == 5          # 5 = bị từ chối quyền: tiến trình có tồn tại
        try:
            ma = wintypes.DWORD()
            return bool(k32.GetExitCodeProcess(h, ctypes.byref(ma))) and ma.value == 259   # STILL_ACTIVE
        finally:
            k32.CloseHandle(h)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def dong_lenh_tien_trinh(pid: int) -> str | None:
    """Dòng lệnh của tiến trình pid; None nếu không đọc được."""
    try:
        if os.name == "nt":
            lenh = f"(Get-CimInstance Win32_Process -Filter 'ProcessId={int(pid)}').CommandLine"
            r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", lenh], capture_output=True,
                               text=True, encoding="utf-8", errors="replace", timeout=30)
            return r.stdout.strip() or None
        return Path(f"/proc/{int(pid)}/cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace").strip() or None
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def _doc_pid(path: Path) -> int:
    try:
        return int(Path(path).read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return 0


@contextlib.contextmanager
def giu_pid(path: Path, doc_dong_lenh=dong_lenh_tien_trinh):
    """Giành file PID bằng tạo file nguyên tử (O_EXCL). File đã có: từ chối nếu PID đó còn sống và dòng lệnh chứa
    'thu_video' (hoặc không đọc được dòng lệnh); ngược lại coi là file cũ, xoá rồi giành lại. Xoá file khi xong."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    for _ in range(3):
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            cu = _doc_pid(path)
            if cu and con_song(cu):
                dong = doc_dong_lenh(cu)
                if dong is None or "thu_video" in dong:
                    raise DangChay(f"thu_video.py đang chạy (PID {cu}, {path}). Kiểm tiến trình bằng: "
                                   "Get-CimInstance Win32_Process (cả python lẫn yt-dlp) trước khi quyết định dừng hay chạy lại")
            with contextlib.suppress(OSError):
                path.unlink()
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        break
    else:
        raise DangChay(f"không giành được file PID {path}")
    try:
        yield
    finally:
        with contextlib.suppress(OSError, ValueError):
            if path.read_text(encoding="utf-8").strip() == str(os.getpid()):
                path.unlink()


# ---------- yt-dlp ----------

def lenh_co_ban(lang: str = "en") -> list[str]:
    """Lệnh gốc: bỏ cấu hình ngoài (có thể chứa cookie trình duyệt), không cookie, giao diện tiếng Anh."""
    return ["yt-dlp", "--ignore-config", "--no-warnings", "--encoding", "utf-8", "--extractor-args", f"youtube:lang={lang}"]


def chay_ytdlp(args: list[str], timeout: int = TIMEOUT_GIAY) -> tuple[str, str, int]:
    try:
        p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    except FileNotFoundError:
        raise LoiThu("không tìm thấy yt-dlp trong PATH") from None
    except subprocess.TimeoutExpired:
        raise LoiThu(f"yt-dlp chạy quá {timeout} giây, đã dừng") from None
    return p.stdout, p.stderr, p.returncode


def dong_loi(stderr: str) -> str:
    """Dòng lỗi đầu tiên (hoặc dòng không rỗng đầu tiên) của stderr, để đưa vào thông báo."""
    dong = [d.strip() for d in stderr.splitlines() if d.strip() and not d.startswith("Deprecated Feature")]
    loi = [d for d in dong if d.startswith("ERROR")]
    return (loi or dong or ["(không có thông báo lỗi)"])[0][:300]


def _tab_vang_mat(stderr: str) -> bool:
    return re.search(r"does not have an? \w+ tab", stderr, re.I) is not None


def url_kenh(kenh: str) -> str:
    k = kenh.strip()
    if re.match(r"https?://", k):
        return re.sub(r"/(videos|shorts|streams|featured|about|playlists)/?$", "", k.rstrip("/"))
    if k.startswith("@"):
        return f"https://www.youtube.com/{k}"
    return f"https://www.youtube.com/channel/{k}"


def khoa_tep(kenh: str) -> str:
    k = url_kenh(kenh)
    return re.sub(r"[^\w@.\-]", "_", k.rsplit("/", 1)[-1])


def phan_tich_flat(stdout: str) -> list[dict]:
    out = []
    for dong in stdout.splitlines():
        a = dong.split("\t")
        if len(a) < 3 or not a[0].strip():
            continue
        try:
            v = int(float(a[2]))
        except ValueError:
            v = 0
        try:
            d = int(float(a[1]))
        except ValueError:
            d = None
        out.append({"id": a[0].strip(), "duration": d, "views": v})
    return out


def _s(x) -> str:
    return "" if x is None else str(x)


def phan_tich_dump(stdout: str) -> list[dict]:
    out = []
    for dong in stdout.splitlines():
        try:
            d = json.loads(dong)
        except ValueError:
            continue
        if not isinstance(d, dict) or not d.get("id"):
            continue
        ts = d.get("timestamp")
        ngay = datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S") if ts else ""
        out.append({"id": d["id"], "ngay_dang": ngay,
                    "thoi_luong_s": _s(int(d["duration"])) if d.get("duration") is not None else "",
                    "view": _s(d.get("view_count")), "like": _s(d.get("like_count")),
                    "binh_luan": _s(d.get("comment_count")),
                    "tieu_de": re.sub(r"[\t\r\n]+", " ", _s(d.get("title"))).strip(),
                    "channel_id": _s(d.get("channel_id"))})
    return out


def dem_loi(stderr: str) -> dict:
    hoi_vien, khac = [], 0
    for dong in stderr.splitlines():
        if not dong.startswith("ERROR"):
            continue
        m = re.match(r"ERROR: \[[^\]]+\] ([^:\s]+): (.*)", dong)
        thong_bao = (m.group(2) if m else dong).lower()
        if "members-only" in thong_bao or "join this channel" in thong_bao:
            hoi_vien.append(m.group(1) if m else "?")
        else:
            khac += 1
    return {"so_hoi_vien": len(hoi_vien), "hoi_vien_ids": hoi_vien, "loi_khac": khac}


# ---------- chọn video, ngày ----------

def chon_id(dai: list[dict], short: list[dict], so_dai: int = SO_DAI_CUA_SO, top_view: int = SO_TOP_VIEW,
            so_cu: int = SO_CU, so_short_moi: int = SO_SHORT_MOI) -> dict:
    """dai, short: danh sách flat mới → cũ ({'id', 'views'})."""
    cua_so = [x["id"] for x in dai[:so_dai]]
    pho_bien = [x["id"] for x in sorted(dai, key=lambda x: -x["views"])[:top_view]]
    cu_dai = [x["id"] for x in dai[-so_cu:]] if dai else []
    short_moi = [x["id"] for x in short[:so_short_moi]]
    short_cu = [x["id"] for x in short[-so_cu:]] if short else []
    return {"cua_so": cua_so, "pho_bien": pho_bien, "cu_dai": cu_dai, "short_moi": short_moi, "short_cu": short_cu,
            "tat_ca": list(dict.fromkeys(cua_so + pho_bien + cu_dai + short_moi + short_cu))}


def ngay_nho_nhat(rows: list[dict], ids) -> str | None:
    cho = set(ids)
    ngay = [r["ngay_dang"][:10] for r in rows if r["id"] in cho and r.get("ngay_dang")]
    return min(ngay) if ngay else None


# ---------- thu một kênh ----------

def _doc_meta_cu(meta_f: Path) -> dict | None:
    try:
        return json.loads(meta_f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def thu_kenh(kenh: str, out_dir: Path, chay=chay_ytdlp, nghi: float = NGHI_MAC_DINH, ngu=time.sleep,
             lam_lai: bool = False, lang: str = "en", ten: str | None = None, so_dai: int = SO_DAI_CUA_SO,
             log=print) -> dict:
    """Thu một kênh. Raise LoiThu khi yt-dlp lỗi/không ra dữ liệu (không ghi file). Đọc thiếu nhiều: ghi file kèm
    meta['loi'] (lần sau tự làm lại)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    khoa = khoa_tep(kenh)
    tsv, meta_f = out_dir / f"{khoa}.tsv", out_dir / f"{khoa}.meta.json"
    if not lam_lai and tsv.exists() and meta_f.exists():
        cu = _doc_meta_cu(meta_f)
        if cu is not None and not cu.get("loi"):
            return cu
    t0 = time.time()
    goc, lenh = url_kenh(kenh), lenh_co_ban(lang)
    da_goi = [False]

    def goi(them: list[str]):
        if da_goi[0]:
            ngu(nghi)                  # nghỉ giữa các lệnh yt-dlp, chạy tuần tự
        da_goi[0] = True
        return chay(lenh + them)

    def doc_tab(tab: str) -> list[dict]:
        o, e, rc = goi(["--flat-playlist", "--print", FLAT_FMT, f"{goc}/{tab}"])
        if rc != 0 and not _tab_vang_mat(e):
            raise LoiThu(f"liệt kê tab /{tab} lỗi (mã {rc}): {dong_loi(e)}")
        return phan_tich_flat(o)

    def doc(ids: list[str]) -> tuple[list[dict], dict]:
        rows, loi = [], {"so_hoi_vien": 0, "hoi_vien_ids": [], "loi_khac": 0}
        for i in range(0, len(ids), LO_DUMP):
            lo = ids[i:i + LO_DUMP]
            f = out_dir / f"_ids_{khoa}.txt"
            f.write_text("\n".join(f"https://www.youtube.com/watch?v={x}" for x in lo), encoding="utf-8")
            try:
                o, e, rc = goi(["--skip-download", "--ignore-errors", "--sleep-requests", str(NGHI_YEU_CAU_GIAY),
                                "-a", str(f), "--print", DUMP_FMT])
            finally:
                with contextlib.suppress(OSError):
                    f.unlink()
            r = phan_tich_dump(o)
            d = dem_loi(e)
            if not r and len(set(lo)) > len(set(d["hoi_vien_ids"])):
                raise LoiThu(f"đọc lô {len(lo)} video không ra dòng nào (mã {rc}): {dong_loi(e)}")
            rows += r
            loi["so_hoi_vien"] += d["so_hoi_vien"]
            loi["hoi_vien_ids"] += d["hoi_vien_ids"]
            loi["loi_khac"] += d["loi_khac"]
        return rows, loi

    dai = doc_tab("videos")
    short = doc_tab("shorts")
    if not dai and not short:
        raise LoiThu("kênh không có video nào (tab /videos và /shorts đều rỗng)")
    c = chon_id(dai, short, so_dai=so_dai)
    log(f"{ten or khoa}: {len(dai)} video dài, {len(short)} Shorts; đọc {len(c['tat_ca'])} video "
        f"(≈ {len(c['tat_ca']) * GIAY_MOI_VIDEO / 60:.0f} phút)")
    rows, loi = doc(c["tat_ca"])
    yeu_cau = set(c["tat_ca"])
    dau_dai = ngay_nho_nhat(rows, c["cu_dai"])
    for vong in range(1, VONG_TIM_NGAY_DAU + 1):
        if dau_dai is not None or len(dai) <= SO_CU * vong:
            break
        tiep = [x["id"] for x in dai[max(0, len(dai) - SO_CU * (vong + 1)):len(dai) - SO_CU * vong]]
        moi = [i for i in tiep if i not in yeu_cau]
        them_rows, them_loi = doc(moi)
        yeu_cau |= set(moi)
        rows += them_rows
        for k in ("so_hoi_vien", "loi_khac"):
            loi[k] += them_loi[k]
        loi["hoi_vien_ids"] += them_loi["hoi_vien_ids"]
        dau_dai = ngay_nho_nhat(rows, tiep)
    dau_short = ngay_nho_nhat(rows, c["short_cu"])
    dau = min([d for d in (dau_dai, dau_short) if d], default=None)

    ma_short = {x["id"] for x in short}
    theo_id = {r["id"]: r for r in rows}
    hoi_vien = set(loi["hoi_vien_ids"])
    thieu = sorted(yeu_cau - set(theo_id) - hoi_vien)
    ds = sorted(theo_id.values(), key=lambda r: r["ngay_dang"], reverse=True)
    with tsv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(COT_TSV)
        for r in ds:
            w.writerow([r["id"], r["ngay_dang"], r["thoi_luong_s"], r["view"], r["like"], r["binh_luan"],
                        "1" if r["id"] in ma_short else "0", r["tieu_de"]])
    cua_so_doc = [theo_id[i] for i in c["cua_so"] if i in theo_id and theo_id[i]["ngay_dang"]]
    meta = {"ten": ten, "kenh": kenh, "channel_id": next((r["channel_id"] for r in ds if r["channel_id"]), ""),
            "n_dai_flat": len(dai), "n_short_flat": len(short), "tong_flat": len(dai) + len(short),
            "ngay_video_dau": dau, "dau_dai": dau_dai, "dau_short": dau_short,
            "cua_so_tu": min(r["ngay_dang"][:10] for r in cua_so_doc) if cua_so_doc else None,
            "n_dai_cua_so": len(cua_so_doc), "so_hoi_vien": loi["so_hoi_vien"], "hoi_vien_ids": loi["hoi_vien_ids"],
            "loi_khac": loi["loi_khac"], "so_yeu_cau": len(yeu_cau), "so_thieu": len(thieu), "thieu_ids": thieu[:50],
            "co": [c_ for c_, bat in (("HOI_VIEN", loi["so_hoi_vien"]), ("DOC_THIEU", thieu)) if bat],
            "pho_bien": c["pho_bien"], "so_dong": len(ds), "giay": round(time.time() - t0)}
    if thieu and len(thieu) / len(yeu_cau) > TY_LE_THIEU_TOI_DA:
        meta["loi"] = (f"đọc thiếu {len(thieu)}/{len(yeu_cau)} video (không kể {loi['so_hoi_vien']} hội viên), "
                       f"vượt {TY_LE_THIEU_TOI_DA:.0%}")
    meta_f.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return meta


# ---------- dòng lệnh ----------

def doc_ds(path: Path) -> list[tuple[str, str | None]]:
    out = []
    for dong in Path(path).read_text(encoding="utf-8-sig").splitlines():
        if not dong.strip() or dong.lstrip().startswith("#"):
            continue
        t = [x.strip() for x in dong.split("\t") if x.strip()]
        out.append((t[-1], t[0] if len(t) > 1 else None))
    return out


def main(argv=None, chay=chay_ytdlp) -> int:
    for st in (sys.stdout, sys.stderr):
        if hasattr(st, "reconfigure"):
            st.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kenh", nargs="*", help="id kênh (UC…), @handle hoặc URL")
    ap.add_argument("--ds", help="file danh sách kênh, mỗi dòng '<kênh>' hoặc '<tên><TAB><kênh>'")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--nghi", type=float, default=NGHI_MAC_DINH, help="giây nghỉ giữa các lệnh yt-dlp (mặc định 3)")
    ap.add_argument("--so-dai", type=int, default=SO_DAI_CUA_SO, help="số video dài mới nhất trong cửa sổ (mặc định 100)")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--lam-lai", action="store_true", help="đọc lại kể cả kênh đã có file")
    ns = ap.parse_args(argv)
    ds = [(k, None) for k in ns.kenh] + (doc_ds(Path(ns.ds)) if ns.ds else [])
    if not ds:
        ap.error("cần ít nhất một kênh (đối số hoặc --ds)")
    out_dir = Path(ns.out_dir)
    n_loi = 0
    try:
        with giu_pid(out_dir / "thu_video.pid"):
            for i, (k, ten) in enumerate(ds):
                if i:
                    time.sleep(ns.nghi)
                try:
                    m = thu_kenh(k, out_dir, chay=chay, nghi=ns.nghi, lam_lai=ns.lam_lai, lang=ns.lang, ten=ten,
                                 so_dai=ns.so_dai)
                except Exception as e:      # một kênh lỗi không làm hỏng cả lô, nhưng mã thoát sẽ khác 0
                    print(f"LỖI {ten or k}: {e}", file=sys.stderr, flush=True)
                    n_loi += 1
                    continue
                if m.get("loi"):
                    print(f"LỖI {ten or k}: {m['loi']} (đã ghi file để xem; lần sau tự làm lại)", file=sys.stderr, flush=True)
                    n_loi += 1
                    continue
                print(f"XONG {ten or k}: {m['so_dong']} dòng, video đầu {m['ngay_video_dau']}, cửa sổ từ {m['cua_so_tu']}, "
                      f"hội viên {m['so_hoi_vien']}, thiếu {m['so_thieu']}, {m['giay']} giây", flush=True)
    except DangChay as e:
        print(str(e), file=sys.stderr)
        return 3
    if n_loi:
        print(f"XONG CÓ LỖI: {n_loi}/{len(ds)} kênh chưa thu được", file=sys.stderr, flush=True)
        return 1
    print("XONG TẤT CẢ", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
