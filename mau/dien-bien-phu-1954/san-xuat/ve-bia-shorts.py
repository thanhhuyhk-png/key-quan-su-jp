"""Ảnh bìa 9:16 cho 5 Shorts EP001: nền dọc của kênh (thẻ đỏ, câu hỏi vàng) + một khung tư liệu thật lấy từ chính video Final.

Chuẩn bìa kênh (kenh/thumbnail-chuan.md): nền chỉ dùng ảnh, phim tư liệu thật, không 3D, không ảnh lãnh tụ.
S4 (Dốc Chuối) toàn đồ hoạ 3D, nên mượn khung phim Karmen cảnh kéo pháo trong S1.

Chạy: python -I -X utf8 tap/EP001-dien-bien-phu-1954/san-xuat/ve-bia-shorts.py
Ra:   Final/shorts/EP001-Snn-<slug>/EP001-Snn-bia.jpg
"""
import importlib.util
import subprocess
import tempfile
from pathlib import Path

GOC = Path(__file__).resolve().parent
SHORTS_DIR = GOC.parent / "Final" / "shorts"

spec = importlib.util.spec_from_file_location("shorts", GOC / "shorts.py")
shorts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shorts)

# mã -> (Shorts lấy khung, giây, ghi chú khung)
KHUNG = {
    "S1": ("S1", 46.6, "phim «Việt Nam» (Karmen, 1955): bộ đội đẩy bánh pháo"),
    "S2": ("S2", 39.0, "ảnh TTLTQG III / TTXVN: bộ đội chuyển đạn pháo"),
    "S3": ("S3", 8.5, "phim «Việt Nam» (Karmen, 1955): kho hòm hàng tiếp tế"),
    "S4": ("S1", 46.0, "phim «Việt Nam» (Karmen, 1955): bộ đội kéo pháo trong rừng"),
    "S5": ("S5", 2.5, "ảnh TTLTQG III: dân công thồ xe đạp"),
}
KHUNG_Y = shorts.KIEU["doc"]["y"]  # y của khung phim 16:9 trên nền dọc


def thu_muc(ma: str) -> Path:
    so = int(ma[1:])
    ds = list(SHORTS_DIR.glob(f"EP001-S{so:02d}-*"))
    assert len(ds) == 1, ds
    return ds[0]


def ve(ma: str) -> Path:
    nguon, giay, _ = KHUNG[ma]
    vao = thu_muc(nguon) / f"EP001-S{int(nguon[1:]):02d}.mp4"
    ra = thu_muc(ma) / f"EP001-S{int(ma[1:]):02d}-bia.jpg"
    with tempfile.TemporaryDirectory() as t:
        tam = Path(t)
        shorts.ve_nen(shorts.SHORTS[ma], "doc", tam)
        # Trích khung ra ảnh trước: ghép thẳng nền 1 khung với video đã tua có lúc không nhận được khung (ra ô đen).
        khung = tam / "khung.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{giay}", "-i", str(vao), "-frames:v", "1",
                        "-vf", f"crop=1080:608:0:{KHUNG_Y}", str(khung)], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tam / "nen.png"), "-i", str(khung),
                        "-filter_complex", f"[0:v][1:v]overlay=0:{KHUNG_Y}", "-frames:v", "1", "-q:v", "2", str(ra)], check=True)
    return ra


if __name__ == "__main__":
    for ma in KHUNG:
        print(ve(ma))
