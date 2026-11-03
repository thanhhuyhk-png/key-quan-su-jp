"""Lô L2: ảnh tư liệu (khối template/archival, Ken Burns) và phim Karmen (ffmpeg) của tập 1, đúng số khung từng cảnh.

Hình sạch, không chữ: thẻ, nhãn ngày, ghi nguồn nằm ở lớp chữ chung của cả phim (dung-lop-chu.py).
Ảnh lãnh tụ: lanhTu (chỉ phóng rất chậm toàn ảnh, giữ màu gốc). Phim Karmen: cắt 4:3 phủ 16:9, màu chung bản mẫu, tắt tiếng.
Ra <output>/261101-dien-bien-phu-1954/hinh/tu-lieu/<mã>.mp4

python -I -X utf8 dung-tu-lieu.py [--stills] [--render] [MÃ ...]
"""
import json, os, subprocess, sys
from pathlib import Path

GOC = Path(__file__).resolve().parent
TPL = GOC.parents[2] / "template"
sys.path.insert(0, str(TPL / "tools"))
from film_dbp import KARMEN_CAT, KARMEN_MAU  # noqa: E402
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
DUNG_TRANG = ["node", str(REPO_GOC / "tools/kit/dung-trang.mjs")]  # dựng trang HTML thành mp4/mov/ảnh
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

RA = OUT / "261101-dien-bien-phu-1954/hinh/tu-lieu"
KHO = [OUT / "261025-dien-bien-phu-mau/assets/photo", OUT / "261101-dien-bien-phu-1954/assets-moi"]
FILM = OUT / "261025-dien-bien-phu-mau/assets/film/viet-nam-tren-duong-thang-loi-karmen-1955.mp4"
FPS = 24
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))
MAU = {"luu-phao-105-bao-tang-ha-noi-01", "luu-phao-105-bao-tang-ha-noi-02", "cao-xa-37mm-bao-tang-ha-noi-01",
       "ham-de-castries-2022", "geneve-hiep-dinh-1954-ban-chup-luu-tru-phap"}  # ảnh màu hôm nay: giữ màu gốc
# Đường máy theo lượt: (x0, y0, zoom0) → (x1, y1, zoom1); chọn xoay vòng để hai ảnh liền nhau không cùng chuyển động.
DUONG = [((0.5, 0.5, 1.02), (0.5, 0.46, 1.12)), ((0.44, 0.5, 1.1), (0.56, 0.5, 1.1)), ((0.5, 0.45, 1.14), (0.5, 0.52, 1.04)),
         ((0.56, 0.52, 1.1), (0.45, 0.48, 1.1)), ((0.5, 0.55, 1.04), (0.52, 0.48, 1.13))]


def tim_anh(ten):
    for d in KHO:
        for duoi in (".jpg", ".png"):
            if (d / f"{ten}{duoi}").exists():
                return d / f"{ten}{duoi}"
    sys.exit(f"không thấy ảnh {ten}")


def so_khung(f):
    o = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout
    return int(o.strip().rstrip(","))


def shot_anh(c, i):
    anh = tim_anh(c["ten"])
    rel = Path(os.path.relpath(anh, TPL / "archival"))  # output khác ổ đĩa với repo thì relpath báo lỗi: đặt cùng ổ
    d = c["n"] / FPS
    if "lanhTu" in c["hinh"]:
        return dict(duration=d, image=rel.as_posix(), lanhTu=True, grade="goc",
                    move=[dict(t=0, x=0.5, y=0.5, zoom=1.0), dict(t=d, x=0.5, y=0.5, zoom=1.05, ease="linear")])
    (x0, y0, z0), (x1, y1, z1) = DUONG[i % len(DUONG)]
    mau = c["ten"] in MAU
    return dict(duration=d, image=rel.as_posix(), grade="goc" if mau else "bw-am", seed=i + 3,
                shake=0 if mau else 0.6, flicker=0 if mau else 0.015, grain=0.06 if mau else 0.16,
                move=[dict(t=0, x=x0, y=y0, zoom=z0), dict(t=d, x=x1, y=y1, zoom=z1, ease="sine")])


def main():
    chon = [a for a in sys.argv[1:] if not a.startswith("--")]
    canh = [c for c in PC["canh"] if c["kieu"] in ("anh", "karmen") and (not chon or c["id"] in chon)]
    RA.mkdir(parents=True, exist_ok=True)
    thu = TPL / "archival" / "shots" / "dbp1"
    thu.mkdir(exist_ok=True)
    for i, c in enumerate(canh):
        c["n"] = round(c["t1"] * FPS) - round(c["t0"] * FPS)
        ra = RA / f"{c['id']}.mp4"
        if c["kieu"] == "anh":
            (thu / f"{c['id']}.js").write_text("// Sinh bởi tap/EP001-dien-bien-phu-1954/san-xuat/dung-tu-lieu.py, đừng sửa tay.\nwindow.SHOT = "
                                               + json.dumps(shot_anh(c, i), ensure_ascii=False) + ";\n", encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(TPL / "tools" / "build_shots.py"), "archival"], check=True, capture_output=True)
    for c in canh:
        ra = RA / f"{c['id']}.mp4"
        if c["kieu"] == "anh":
            trang = TPL / "archival" / f"dbp1-{c['id']}.html"
            if "--stills" in sys.argv:
                subprocess.run([*DUNG_TRANG, str(trang), "--stills", f"0.1,{c['n'] / FPS - 0.1:.2f}", "--out-dir",
                                str(RA.parent / "story" / "tu-lieu" / c["id"])], check=True, capture_output=True)
            if "--render" in sys.argv:
                subprocess.run([*DUNG_TRANG, str(trang), "--out", str(ra), "--fps", str(FPS), "--force"], check=True, capture_output=True)
        elif "--render" in sys.argv or "--stills" in sys.argv:
            m, s = c["ten"].split(":")
            vf = f"fps={FPS},{KARMEN_CAT},scale=1920:1080:flags=lanczos,setsar=1,{KARMEN_MAU},format=yuv420p"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{int(m) * 60 + float(s):.3f}", "-i", str(FILM), "-vf", vf, "-an",
                            "-frames:v", str(c["n"]), "-r", str(FPS), "-c:v", "libx264", "-crf", "16", "-preset", "medium", str(ra)], check=True)
            if "--stills" in sys.argv:
                d = RA.parent / "story" / "tu-lieu" / c["id"]
                d.mkdir(parents=True, exist_ok=True)
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(ra), "-vf", "select=eq(n\\,0)+eq(n\\," + str(c["n"] - 1) + "),tile=2x1,scale=1280:-1",
                                "-frames:v", "1", str(d / "sheet.jpg")], check=True)
        if "--render" in sys.argv:
            n = so_khung(ra)
            print(f"{c['id']}: {n} khung (cần {c['n']}){'' if n == c['n'] else '  LỆCH'}", flush=True)
    print(f"{len(canh)} cảnh tư liệu xong")


if __name__ == "__main__":
    main()
