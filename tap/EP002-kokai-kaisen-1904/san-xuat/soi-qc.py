"""Soi QC file cuối tập 1 (P6): ba tờ để mắt người duyệt, ghi cạnh file video.

(1) soi-ban-do-<ten>.jpg: mọi cảnh vnmap × 3 khung (đầu, giữa, cuối): soát Hoàng Sa, Trường Sa, "Biển Đông", không lưỡi bò.
(2) to-khung-64-<ten>.jpg: 64 mốc đều trên cả phim (seek từng mốc; select+tile trên file concat chỉ ra vài ô cuối).
(3) check-<ten>.md: cảnh báo (dòng `!`) và lỗi (dòng `✗`) của `kit.py kiem` (đọc từ tệp --check) tra về mã cảnh, mô tả, độ lệch trong cảnh,
    để phân loại cố ý (khung đầu thẻ nền tối, thẻ/ảnh đứng yên) hay lỗi.

python -I -X utf8 soi-qc.py <video> --ten v4 [--check <tệp kết quả kit.py kiem>]
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))
INTRO_GIAY = 10.0

FPS = 24


def khung(f: str, t: float, w: int, h: int, tam: Path) -> Image.Image:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", f, "-frames:v", "1", "-vf", f"scale={w}:{h}", str(tam)], check=True)
    return Image.open(tam).copy()


def to_ban_do(f: str, pc: dict, ra: Path, tam: Path) -> int:
    o = INTRO_GIAY
    bd = [c for c in pc["canh"] if "Hoàng Sa" in c["hinh"]]
    w, h = 640, 360
    to = Image.new("RGB", (3 * w, len(bd) * h))
    d = ImageDraw.Draw(to)
    for r, c in enumerate(bd):
        a, b = c["t0"] + o, c["t1"] + o
        for k, t in enumerate((a + 0.1, (a + b) / 2, b - 0.1)):
            to.paste(khung(f, t, w, h, tam), (k * w, r * h))
        d.text((6, r * h + 6), c["id"], fill=(255, 255, 0))
    to.save(ra, quality=85)
    return len(bd)


def to_64(f: str, ra: Path, tam: Path) -> None:
    dai = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                               capture_output=True, text=True).stdout)
    w, h = 320, 180
    to = Image.new("RGB", (8 * w, 8 * h))
    d = ImageDraw.Draw(to)
    for i in range(64):
        t = (i + 0.5) * dai / 64
        to.paste(khung(f, t, w, h, tam), ((i % 8) * w, (i // 8) * h))
        d.text(((i % 8) * w + 4, (i // 8) * h + 4), f"{int(t // 60)}:{t % 60:04.1f}", fill=(255, 255, 0))
    to.save(ra, quality=80)


def tra_canh(check: Path, pc: dict, ra: Path) -> int:
    """Mỗi dòng cảnh báo (`!`) hoặc lỗi (`✗`) có mốc m:ss.s → mã cảnh chứa mốc đó (thời gian phim trừ intro)."""
    o = INTRO_GIAY
    dong = ["| Cảnh báo | Mốc phim | Cảnh | Lệch trong cảnh (s) | Nguồn | Hình |", "|---|---|---|---|---|---|"]
    n = 0
    for l in check.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.search(r"(\d+):(\d{2}(?:\.\d+)?)", l)
        if not l.lstrip().startswith(("!", "✗")) or not m:
            continue
        t = int(m[1]) * 60 + float(m[2]) - o
        c = next((c for c in pc["canh"] if c["t0"] <= t < c["t1"]), None)
        if c is None:  # mốc trong intro hoặc sau cảnh cuối
            dong.append(f"| {l.strip()[2:80]} | {m[0]} | (intro) | | | |")
        else:
            i = pc["canh"].index(c)
            ranh = f" (ranh với {pc['canh'][i + 1]['id']})" if c["t1"] - t < 0.1 and i + 1 < len(pc["canh"]) else ""  # mốc check làm tròn 0,1 s
            dong.append(f"| {l.strip()[2:80]} | {m[0]} | {c['id']}{ranh} | {t - c['t0']:.2f} | {c['nguon']} | {c['hinh'][:60]} |")
        n += 1
    ra.write_text("\n".join(dong) + "\n", encoding="utf-8")
    return n


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--ten", required=True, help="hậu tố tên tờ soi, vd v4 (không ghi đè tờ bản trước)")
    ap.add_argument("--check", help="tệp kết quả `kit.py kiem` để tra cảnh báo và lỗi về mã cảnh")
    o = ap.parse_args()
    pc = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))
    thu = Path(o.video).parent
    tam = thu / "k-soi.jpg"
    n = to_ban_do(o.video, pc, thu / f"soi-ban-do-{o.ten}.jpg", tam)
    to_64(o.video, thu / f"to-khung-64-{o.ten}.jpg", tam)
    tam.unlink(missing_ok=True)
    print(f"{n} cảnh vnmap → soi-ban-do-{o.ten}.jpg; 64 mốc → to-khung-64-{o.ten}.jpg")
    if o.check:
        print(f"{tra_canh(Path(o.check), pc, thu / f'check-{o.ten}.md')} cảnh báo → check-{o.ten}.md")


if __name__ == "__main__":
    main()
