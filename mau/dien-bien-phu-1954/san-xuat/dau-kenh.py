"""Dấu kênh (watermark) Goha Studio theo bộ nhận diện (kenh/thuong-hieu.md, hướng C user chốt 02/11/2026):
vạch đỏ son + chữ GOHA (nét logo gốc, màu kem) + "STUDIO" Oswald giãn chữ, kem mờ 58 %, nền trong suốt.

Ô dấu cố định 229×50 px ở khung 1920×1080 (ghep-hinh.py DAU_WH đặt 4 góc theo cỡ này; đổi cỡ thì sửa cả hai).
Đặt góc trên phải khi ghép: nhãn ngày ở góc trên trái, ghi nguồn ở góc dưới phải, nên không đè nhau.

python -I -X utf8 dau-kenh.py [--ra <png>] [--mau <video> --giay t1,t2,...]   (--mau: ảnh soi dấu trên các khung của video)
"""
import sys
import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

GOC = Path(__file__).resolve().parent
REPO = GOC.parents[2]
FONT = REPO / "template" / "fonts" / "Oswald-VF.ttf"
CHU_GOHA = REPO / "kenh" / "thuong-hieu" / "png" / "goha-chu-kem.png"  # xuất bởi kenh/thuong-hieu/ma-nguon/xuat-bo.py
RA = OUT / "261102-dbp-v3/dau-kenh.png"
O_DAU = (229, 50)  # px ở khung 1920×1080, khớp ghep-hinh.py DAU_WH
CAO_GOHA, CO_STUDIO, GIAN, LE_PHAI, LE_TREN = 24, 17, 6, 56, 44
KEM, DO, MO = (235, 228, 200), (220, 90, 60), 0.58


def ve_dau() -> Image.Image:
    goha = Image.open(CHU_GOHA).convert("RGBA")
    goha = goha.resize((round(goha.width * CAO_GOHA / goha.height), CAO_GOHA), Image.LANCZOS)
    f = ImageFont.truetype(str(FONT), CO_STUDIO)
    f.set_variation_by_axes([600])
    chu = "STUDIO"
    rong = [f.getlength(c) for c in chu]
    w_st = sum(rong) + GIAN * (len(chu) - 1)
    w = 4 + 10 + goha.width + 11 + w_st
    lop = Image.new("RGBA", O_DAU, (0, 0, 0, 0))
    x0, yg = round((O_DAU[0] - w) / 2), (O_DAU[1] - CAO_GOHA) // 2
    if x0 < 3:
        raise SystemExit(f"dấu rộng {w:.0f} px, vượt ô {O_DAU}")
    d = ImageDraw.Draw(lop)
    d.rectangle([x0, yg - 1, x0 + 3, yg + CAO_GOHA], fill=DO + (255,))  # vạch đỏ son
    lop.alpha_composite(goha, (x0 + 14, yg))
    x = x0 + 14 + goha.width + 11
    tren = yg + CAO_GOHA - f.getbbox("S")[3]  # chân STUDIO bằng chân chữ GOHA
    for c, r in zip(chu, rong):
        d.text((round(x), tren), c, font=f, fill=KEM + (255,))
        x += r + GIAN
    bong = Image.new("RGBA", lop.size, (0, 0, 0, 0))
    bong.putalpha(lop.getchannel("A").filter(ImageFilter.GaussianBlur(3)).point(lambda a: int(a * 0.55)))
    tong = Image.alpha_composite(bong, lop)
    tong.putalpha(tong.getchannel("A").point(lambda a: int(a * MO)))
    return tong


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra", default=str(RA))
    ap.add_argument("--mau")
    ap.add_argument("--giay", default="")
    o = ap.parse_args()
    dau = ve_dau()
    Path(o.ra).parent.mkdir(parents=True, exist_ok=True)
    dau.save(o.ra)
    print(f"dấu {dau.size[0]}×{dau.size[1]} px → {o.ra}")
    if o.mau:
        khung = []
        for t in o.giay.split(","):
            tam = Path(o.ra).with_name("k.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", o.mau, "-frames:v", "1", str(tam)], check=True)
            im = Image.open(tam).convert("RGBA")
            im.alpha_composite(dau, (1920 - LE_PHAI - dau.size[0], LE_TREN))
            khung.append(im.convert("RGB"))
            im.convert("RGB").save(Path(o.ra).with_name(f"soi-dau-kenh-1080-{len(khung)}.jpg"), quality=95)  # cỡ thật Full HD
        to = Image.new("RGB", (1920, 540 * ((len(khung) + 1) // 2)))
        for i, im in enumerate(khung):
            to.paste(im.resize((960, 540)), ((i % 2) * 960, (i // 2) * 540))
        ra = Path(o.ra).with_name("soi-dau-kenh.jpg")
        to.save(ra, quality=90)
        # ảnh cận góc trên phải ở cỡ thật để soi nét chữ
        im = khung[0].crop((1920 - 640, 0, 1920, 200))
        im.save(Path(o.ra).with_name("soi-dau-kenh-can.jpg"), quality=92)
        print("soi →", ra)


if __name__ == "__main__":
    main()
