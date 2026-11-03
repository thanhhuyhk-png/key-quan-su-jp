"""Tra cảnh đã render và đã duyệt của bản Demo (bản Full V3, 30/10/2026) để tập 1 dùng lại nguyên hình.

Mỗi cảnh 3D của Demo nằm trong một video nhóm có hậu kỳ (hinh/<nhóm>-v3.mp4); khung tập Demo f ↔ khung f − lệch của nhóm.
Hình nhóm 3D sạch chữ (chữ hook chỉ có ở trang mo-man cho HK1–HK5, không dùng ở đây).
"""
import sys
import json, subprocess
from pathlib import Path
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

GOC = Path(__file__).resolve().parent
DEMO = OUT / "261030-dbp-ban-full"
DEMO_PC = json.loads((GOC.parents[1] / "dien-bien-phu-mau/san-xuat/ban-full/phan-canh.json").read_text(encoding="utf-8"))
DEMO_CANH = {c["id"]: c for c in DEMO_PC["canh"]}
FINAL = DEMO / "final/dbp-full-v3.mp4"
NHOM = [("mo-man", 0, 260), ("giua", 929, 1005), ("ba-dot", 1792, 2294), ("may-bay", 2698, 2810)]
# Chuỗi Dốc Chuối của Demo (T-C1…T-E4, render bản thử v2 đã hậu kỳ, không chữ): chỉ có trong bản Demo cuối, lấy thẳng từ đó (v3)
DOC_CHUOI = (1243, 1619)
FILM = OUT / "261025-dien-bien-phu-mau/assets/film/viet-nam-tren-duong-thang-loi-karmen-1955.mp4"
FPS = 24


def nhom_cua(ma):
    """(file nhóm, khung đầu cảnh trong file, khung cuối nhóm trong file) của cảnh 3D Demo `ma`."""
    a, b = DEMO_CANH[ma]["khung"]
    if DOC_CHUOI[0] <= a and b <= DOC_CHUOI[1]:
        return FINAL, a, DOC_CHUOI[1]
    for ten, d, e in NHOM:
        if d <= a and b <= e:
            # hết nhóm hoặc tới cảnh đầu tiên phía sau không phải 3D (khung của nó trong video nhóm để đen)
            het = min([c["khung"][0] for c in DEMO_PC["canh"] if a < c["khung"][0] < e and c["nguon"] != "3d"] or [e])
            return DEMO / f"hinh/{ten}-v3.mp4", a - d, het - d
    raise SystemExit(f"{ma}: không phải cảnh 3D của Demo")


def cat_demo(ma, lech, n, vf=""):
    """Bộ lọc ffmpeg (đầu vào, chuỗi lọc) lấy n khung của cảnh Demo `ma` từ khung lệch `lech` (được chạy sang cảnh sau
    trong cùng nhóm, không đổi tốc độ)."""
    f, a, het = nhom_cua(ma)
    if a + lech + n > het:
        raise SystemExit(f"{ma}: cần khung {a + lech}..{a + lech + n}, nhóm chỉ tới {het}")
    return ["-i", str(f)], f"trim=start_frame={a + lech}:end_frame={a + lech + n},setpts=PTS-STARTPTS,fps={FPS},scale=1920:1080,setsar=1{vf}"
