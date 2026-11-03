"""Âm cuối: `master` (tăng mức cố định tới LUFS đích + chặn đỉnh) và `ghep` (hình + master → mp4, đo lại trên mp4).

Vì sao không có `deliver`/loudnorm: loudnorm tự đổi chế độ khi cần nâng nhiều, bộ mã `aac` gốc của ffmpeg vọt đỉnh ở tiếng nổ.
Ở đây gain là MỘT con số cố định, alimiter chặn đỉnh, và đỉnh thật được đo lại trên chính file ra (mp4 cho `ghep`).
Hàm `do_ebur128` dùng chung với kiem.py.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import LoiKit, chay_lenh, ghi_nguyen_tu, json_an_toan  # noqa: E402

DINH_AN_TOAN_MP4 = -1.0  # dBTP: quá mức này thì cảnh báo (YouTube/mạng xã hội mã hoá lại sẽ vọt đỉnh)
SO = r"([-+]?(?:\d+\.?\d*|inf))"


def _so(chu: str) -> float:
    return float(chu)  # float("-inf") hợp lệ


def doc_ebur128(stderr: str) -> dict:
    """Lấy I (LUFS tích hợp) và đỉnh thật (dBFS) ở khối «Summary:» cuối cùng của ebur128=peak=true."""
    i = stderr.rfind("Summary:")
    if i < 0:
        raise LoiKit("không đọc được kết quả ebur128 (file không có âm, hoặc ffmpeg báo lỗi trước khi đo)")
    kh = stderr[i:]
    mi = re.search(r"\bI:\s+" + SO + r"\s+LUFS", kh)
    md = re.search(r"\bPeak:\s+" + SO + r"\s+dBFS", kh)
    if not mi or not md:
        raise LoiKit("kết quả ebur128 thiếu dòng I hoặc Peak (cần ebur128=peak=true)")
    return {"I": _so(mi[1]), "dinh": _so(md[1])}


def do_ebur128(tep: str | Path) -> dict:
    """Đo I và đỉnh thật của luồng âm đầu tiên (không giải mã hình)."""
    r = chay_lenh(["ffmpeg", "-hide_banner", "-nostats", "-i", str(tep), "-map", "0:a:0", "-vn",
                   "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"])
    return doc_ebur128(r.stderr.decode("utf-8", "replace"))


def gain_toi_dich(i_hien_tai: float, dich: float) -> float:
    return round(dich - i_hien_tai, 2)


def tran_limiter(tp: float) -> float:
    """dBFS → biên độ tuyến tính cho alimiter (miền hợp lệ 0,0625..1 = −24..0 dB)."""
    if not -24.0 <= tp <= 0.0:
        raise LoiKit(f"--tp {tp} ngoài miền −24..0 dB (alimiter chỉ nhận 0,0625..1)")
    return round(10 ** (tp / 20), 6)


def bo_ma_am() -> tuple[str, str | None]:
    """aac_mf (Media Foundation, Windows) nếu có; không thì aac của ffmpeg kèm cảnh báo."""
    ds = chay_lenh(["ffmpeg", "-hide_banner", "-encoders"]).stdout.decode("utf-8", "replace")
    if re.search(r"^\s*A\S*\s+aac_mf\b", ds, re.M):
        return "aac_mf", None
    return "aac", ("máy này không có bộ mã aac_mf, dùng aac của ffmpeg: đỉnh có thể vọt ở tiếng nổ, "
                   "xem kết quả đo lại bên dưới và hạ --tp nếu vượt −1 dBTP")


def lenh_ghep(hinh: str, am: str, ra: str, bo_ma: str) -> list[str]:
    return ["ffmpeg", "-y", "-v", "error", "-i", hinh, "-i", am, "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", bo_ma, "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", ra]


def _in(kq: dict, as_json: bool, dong: list[str]) -> None:
    if as_json:
        print(json.dumps(json_an_toan(kq), ensure_ascii=False, indent=2))
    else:
        print("\n".join(dong))


def dang_ky_master(p: argparse.ArgumentParser) -> None:
    p.add_argument("--am", required=True, help="bản trộn (WAV) cần master")
    p.add_argument("--ra", required=True, help="WAV master ra")
    p.add_argument("--lufs", type=float, default=-14.0, help="độ to đích LUFS tích hợp (mặc định −14)")
    p.add_argument("--tp", type=float, default=-3.0, help="trần đỉnh dBFS cho alimiter (mặc định −3, chừa chỗ cho mã hoá AAC)")
    p.add_argument("--force", action="store_true", help="ghi đè file ra")
    p.add_argument("--json", action="store_true")


def chay_master(a: argparse.Namespace) -> int:
    if not Path(a.am).is_file():
        raise LoiKit(f"không thấy {a.am}")
    vao = do_ebur128(a.am)
    if vao["I"] == float("-inf"):
        raise LoiKit(f"{a.am} im lặng hoàn toàn, không có gì để tăng")
    gain = gain_toi_dich(vao["I"], a.lufs)
    af = f"volume={gain}dB,alimiter=limit={tran_limiter(a.tp)}:attack=3:release=60:level=false"
    with ghi_nguyen_tu(Path(a.ra), ghi_de=a.force) as tam:
        chay_lenh(["ffmpeg", "-y", "-v", "error", "-i", a.am, "-af", af, "-ar", "48000", "-c:a", "pcm_s24le", "-f", "wav", str(tam)])
    ra = do_ebur128(a.ra)
    canh_bao = []
    if abs(ra["I"] - a.lufs) > 0.5:
        canh_bao.append(f"độ to sau chặn đỉnh là {ra['I']:.1f} LUFS, lệch đích {a.lufs:.1f}: bản trộn quá nhiều đỉnh nhọn, "
                        f"cân nhắc nâng --tp hoặc hạ tiếng động to")
    kq = {"ra": str(a.ra), "I_vao": vao["I"], "gain_db": gain, "I": ra["I"], "dinh": ra["dinh"], "lufs_dich": a.lufs, "tp": a.tp,
          "canh_bao": canh_bao}
    _in(kq, a.json, [f"master {a.ra}: vào {vao['I']:.1f} LUFS, tăng {gain:+.2f} dB → ra I = {ra['I']:.1f} LUFS, đỉnh thật {ra['dinh']:.1f} dBFS"]
        + [f"! {c}" for c in canh_bao])
    return 0


def dang_ky_ghep(p: argparse.ArgumentParser) -> None:
    p.add_argument("--hinh", required=True, help="video (giữ nguyên hình, -c:v copy)")
    p.add_argument("--am", required=True, help="WAV master")
    p.add_argument("--ra", required=True, help="mp4 ra")
    p.add_argument("--force", action="store_true")
    p.add_argument("--json", action="store_true")


def chay_ghep(a: argparse.Namespace) -> int:
    for f in (a.hinh, a.am):
        if not Path(f).is_file():
            raise LoiKit(f"không thấy {f}")
    bo_ma, canh_bao_ma = bo_ma_am()
    with ghi_nguyen_tu(Path(a.ra), ghi_de=a.force) as tam:
        chay_lenh(lenh_ghep(a.hinh, a.am, str(tam), bo_ma))
    ra = do_ebur128(a.ra)
    canh_bao = [canh_bao_ma] if canh_bao_ma else []
    if ra["dinh"] > DINH_AN_TOAN_MP4:
        canh_bao.append(f"ĐỈNH THẬT TRÊN MP4 = {ra['dinh']:.1f} dBFS, vượt {DINH_AN_TOAN_MP4:.0f} dBTP: master lại với --tp thấp hơn rồi ghép lại")
    kq = {"ra": str(a.ra), "ma_hoa_am": bo_ma, "I": ra["I"], "dinh": ra["dinh"], "canh_bao": canh_bao}
    _in(kq, a.json, [f"ghép {a.ra}: âm {bo_ma} 256k; đo lại trên mp4: I = {ra['I']:.1f} LUFS, đỉnh thật {ra['dinh']:.1f} dBFS"]
        + [f"! {c}" for c in canh_bao])
    return 0
