"""Vẽ ảnh bìa tập 1 (bản A, B, C để thử Test & Compare) từ template/thumbnail-dbp.html.

Chạy: python -I -X utf8 tap/EP001-dien-bien-phu-1954/san-xuat/ve-thumbnail.py
Ra: tap/EP001-dien-bien-phu-1954/Final/EP001-thumbnail-a.jpg, -b.jpg, -c.jpg (1280×720, ≤ 2 MB)
    và bản soi cỡ điện thoại 168×94 ở <output>/261101-dien-bien-phu-1954/thumbnail/.
Chuẩn: kenh/thumbnail-chuan.md. Chữ đã quét bộ lọc chính sách; ảnh có trong anh.tsv và sổ tài sản.
"""
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlencode
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

GOC = Path(__file__).resolve().parents[3]
TAP = GOC / "tap/EP001-dien-bien-phu-1954"
ANH = OUT / "261025-dien-bien-phu-mau/assets/photo"
SOI = OUT / "261101-dien-bien-phu-1954/thumbnail"
CHROME = str(duong("chrome"))

BAN = {
    # Chữ 02/11/2026: câu hỏi mở vòng lặp, đúng nghĩa đen theo sổ (mã trong ngoặc); chỉ ảnh tư liệu thật.
    "a": dict(anh=ANH / "keo-phao-01.jpg", x="62", y="45", w="68", h1="KÉO PHÁO VÀO", h2="SAO LẠI KÉO RA?",  # M10, M5
              the="ĐIỆN BIÊN PHỦ · 1954", nguon="Ảnh tư liệu: TTLTQG III / TTXVN"),
    "b": dict(anh=ANH / "chuyen-dan-vao-ham-phao-01.jpg", x="60", y="50", w="68", h1="PHÁO TA",
              h2="GIẤU Ở ĐÂU?",  # D2c, D5a
              the="ĐIỆN BIÊN PHỦ · 1954", nguon="Ảnh tư liệu: TTLTQG III / TTXVN"),
    "c": dict(anh=ANH / "tan-cong-him-lam-01.jpg", x="12", y="40", w="74", h1="PHÁP BẮN 6.000 VIÊN",
              h2="RƠI VÀO ĐÂU?",  # A6b, D5c
              the="ĐIỆN BIÊN PHỦ · 3/1954", nguon="Ảnh tư liệu: TTLTQG III / TTXVN"),
}


def main() -> None:
    SOI.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tam:
        tam = Path(tam)
        shutil.copy(GOC / "template/thumbnail-dbp.html", tam)
        for f in ("Oswald-VF.ttf", "BeVietnamPro-ExtraBold.ttf", "BeVietnamPro-SemiBold.ttf"):
            shutil.copy(GOC / "template/fonts" / f, tam)
        shutil.copy(GOC / "kenh/thuong-hieu/phim/logo-anh-bia.png", tam)
        for ma, p in BAN.items():
            shutil.copy(p["anh"], tam)
            p = {**p, "anh": Path(p["anh"]).name}
            png = tam / f"{ma}.png"
            url = (tam / "thumbnail-dbp.html").as_uri() + "?" + urlencode(p)
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            "--allow-file-access-from-files", "--window-size=1280,720",
                            "--virtual-time-budget=8000", f"--screenshot={png}", url],
                           check=True, capture_output=True)
            ra = TAP / f"Final/thumbnail-{ma}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-q:v", "2", str(ra)], check=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-vf", "scale=168:94:flags=area",
                            str(SOI / f"soi-168-{ma}.png")], check=True)
            print(ra, f"{ra.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
