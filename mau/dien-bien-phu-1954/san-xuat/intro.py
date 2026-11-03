"""Intro trailer tập 1 (v2): súng đạn trước lời, kế thừa hook đã duyệt của bản Demo rồi kéo dài theo phách nhạc.

Phách nhạc hook-1 (librosa): 1,28 · 1,70 · 2,11 · 2,53 · 2,95 · 3,37 · 3,78 · 4,20 · 4,64 · 5,06 · 5,50 · 5,94 · 6,36 s.
- Khung 0–50: nguyên hook Demo (HK1–HK4, có chữ "ĐIỆN BIÊN PHỦ · 13/3 – 7/5/1954"), tiếng và mức như bản trộn Demo.
- Khung 51–152: chín cú cắt đúng phách, mỗi cú một khoảnh khắc thật hoặc 3D đã duyệt, mỗi cú một tiếng; chữ tiêu đề đứng yên.
- 6,36 s: cắt hết tiếng (khoảng chân không), HK5 khoá nòng "CẠCH", lời vào ở INTRO_GIAY + mốc chữ đầu (nhạc dâng lại 6,9 s).
Mọi mốc của phim (hình, giọng, tiếng) lùi đúng INTRO_KHUNG.

python -I -X utf8 intro.py [--render]   → <output>/261102-dbp-v2/intro/intro.mp4 (+ tờ soi intro-soi.jpg)
"""
import subprocess, sys
from pathlib import Path

import numpy as np
from PIL import Image

GOC = Path(__file__).resolve().parent
sys.path[:0] = [str(GOC), str(GOC.parents[2] / "template" / "tools")]
from film_dbp import KARMEN_CAT, KARMEN_MAU  # noqa: E402
from demo import FILM, FINAL, FPS, cat_demo  # noqa: E402
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

RA = OUT / "261102-dbp-v2/intro"
LOP = OUT / "261030-dbp-ban-full/hinh/karmen/HK1-lop.mov"
INTRO_KHUNG = 165
INTRO_GIAY = INTRO_KHUNG / FPS  # 6,875 s
LANG = 6.36  # phách cuối: cắt hết tiếng, nhạc hụt

# (nguồn, điểm vào, số khung, rung máy) — nguồn: final (khung Demo) | karmen (giây trong phim gốc) | Demo 3D (mã cảnh, khung lệch)
DOAN = [
    ("final", 0, 51, 0),          # HK1–HK4 Demo: nổ khung 0, C-47 lướt, loạt pháo, xung phong
    ("MB1", 13, 10, 6),           # động cơ C-47 trúng đạn cao xạ, lửa bùng, khói đen
    ("karmen", 2610.70, 10, 14),  # cột nổ lớn giữa cánh đồng
    ("karmen", 2588.45, 10, 4),   # khẩu pháo trong rừng nhả khói
    ("karmen", 2601.50, 10, 0),   # bộ đội vượt hào xung phong, nổ sau lưng
    ("BD13", 0, 20, 18),          # bộc phá A1: cột đất lửa
    ("BD3", 4, 10, 8),            # đồi Độc Lập trong đêm, chớp nổ trên đỉnh
    ("karmen", 2622.20, 11, 3),   # chiến hào, thép gai, bộ đội vượt
    ("karmen", 2617.40, 11, 4),   # bộ đội tiến qua khói nổ trên sườn đồi
    ("karmen", 2592.30, 10, 8),   # nổ trên đồi xa, khói phủ cánh đồng
    ("final", 51, 12, 0),         # HK5 Demo: bóng pháo thủ ở khoá nòng, CẠCH
]
assert sum(d[2] for d in DOAN) == INTRO_KHUNG

# Tiếng intro: (tệp, giây, dB, hero). Bốn cú đầu y hệt bản trộn Demo (am/mix-full.json); sau đó mỗi cú cắt một tiếng.
DEMO_AM = f"{OUT.as_posix()}/261030-dbp-ban-full/am/"
V11 = f"{OUT.as_posix()}/261025-dien-bien-phu-mau/audio/"


def moc(k):
    return round(sum(d[2] for d in DOAN[:k]) / FPS, 3)


CUES = [
    (DEMO_AM + "sfx-cat/hk1-no.wav", 0.0, -1, True), (DEMO_AM + "sfx-cat/hk2-luot.wav", 0.18, -4, True),
    (DEMO_AM + "sfx-cat/hk2-cao-xa.wav", 0.875, -12, False), (DEMO_AM + "sfx-cat/hk3-gan.wav", 1.29, -2, True),
    (DEMO_AM + "sfx-cat/hk3-loat.wav", 1.29, -5, False), (DEMO_AM + "sfx-cat/hk4-vut.wav", 1.708, -10, False),
    (DEMO_AM + "sfx-cat/hk4-sung.wav", 1.708, -20, False),
    (DEMO_AM + "sfx-cat/mb1-cao-xa.wav", moc(1), -6, True), (DEMO_AM + "sfx-cat/mb1-dong-co.wav", moc(1), -9, False),
    (V11 + "sfx-rvb/no-lon-gan.wav", moc(2), -3, True),
    (DEMO_AM + "sfx/phao-ban.mp3", moc(3), -4, True),
    (DEMO_AM + "sfx-cat/hk4-vut.wav", moc(4), -8, False), (DEMO_AM + "sfx-cat/hk4-sung.wav", moc(4), -12, False),
    (DEMO_AM + "sfx/no-hook.mp3", moc(5), 0, True), (DEMO_AM + "sfx/rung-tram.mp3", moc(5), -6, False),
    (V11 + "sfx-rvb/dan-rit-no.wav", moc(6) - 0.3, -6, True),
    (V11 + "sfx/sung-may.mp3", moc(7), -8, False), (DEMO_AM + "sfx-cat/hk4-vut.wav", moc(7), -10, False),
    (V11 + "sfx/sung-truong.mp3", moc(8), -8, False), (V11 + "sfx-rvb/dan-rit-no.wav", moc(8), -10, False),
    (V11 + "sfx-rvb/phao-loat-xa.wav", moc(9), -3, True),
    (DEMO_AM + "sfx-cat/hk5-khoa.wav", moc(10) + 0.085, -6, True),
]


def lop_chu():
    """Tách chữ tiêu đề và dòng ghi nguồn Karmen từ lớp chữ HK1 của Demo (khung 12) thành hai PNG trong suốt."""
    goc = RA / "hk1-lop.png"
    if not goc.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(LOP), "-vf", "select=eq(n\\,12)", "-frames:v", "1", str(goc)], check=True)
    goc_px = np.array(Image.open(goc).convert("RGBA"))
    for ten, a, b in (("tieu-de", 0, 900), ("ghi-nguon", 990, goc_px.shape[0])):
        out = goc_px.copy()
        out[:a, :, 3] = 0
        out[b:, :, 3] = 0
        Image.fromarray(out).save(RA / f"{ten}.png")


def rung(px):
    """Rung máy tắt dần từ đầu đoạn (px điểm ảnh), kiểu sóng chấn động."""
    if not px:
        return ""
    return (f",scale=2016:1134,crop=1920:1080:x='48+{px}*sin(n*2.7)*exp(-n/5)':y='27+{px}*0.6*cos(n*3.3)*exp(-n/5)'")


def render():
    RA.mkdir(parents=True, exist_ok=True)
    lop_chu()
    vao, loc, nhan = [], [], []
    for k, (src, a, n, px) in enumerate(DOAN):
        i = k
        if src == "final":
            vao += ["-i", str(FINAL)]
            loc.append(f"[{i}:v]trim=start_frame={a}:end_frame={a + n},setpts=PTS-STARTPTS,fps={FPS}[s{k}]")
            nhan.append(f"[s{k}]")
            continue
        if src == "karmen":
            vao += ["-ss", f"{a:.3f}", "-i", str(FILM)]
            loc.append(f"[{i}:v]fps={FPS},trim=end_frame={n},setpts=PTS-STARTPTS,{KARMEN_CAT},scale=1920:1080:flags=lanczos,setsar=1,{KARMEN_MAU}{rung(px)}[s{k}]")
        else:
            v, f = cat_demo(src, a, n, rung(px))
            vao += v
            loc.append(f"[{i}:v]{f}[s{k}]")
        nhan.append(f"[s{k}]")
    i = len(DOAN)
    vao += ["-loop", "1", "-i", str(RA / "tieu-de.png"), "-loop", "1", "-i", str(RA / "ghi-nguon.png")]
    a51, b153 = sum(d[2] for d in DOAN[:1]), sum(d[2] for d in DOAN[:-1])
    # Ghi nguồn Karmen chỉ hiện trên các cú phim Karmen của đoạn nối dài.
    kar = "+".join(f"between(n\\,{sum(d[2] for d in DOAN[:k])}\\,{sum(d[2] for d in DOAN[:k + 1]) - 1})"
                   for k, d in enumerate(DOAN) if d[0] == "karmen")
    loc.append(f"{''.join(nhan)}concat=n={len(nhan)}:v=1:a=0,format=yuv420p[m]")
    loc.append(f"[{i}:v]format=rgba,trim=end_frame={INTRO_KHUNG}[t];[{i + 1}:v]format=rgba,trim=end_frame={INTRO_KHUNG}[g]")
    loc.append(f"[m][t]overlay=0:0:enable='between(n\\,{a51}\\,{b153 - 1})'[m2];[m2][g]overlay=0:0:enable='{kar}',format=yuv420p[v]")
    ra = RA / "intro.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *vao, "-filter_complex", ";".join(loc), "-map", "[v]", "-an",
                    "-frames:v", str(INTRO_KHUNG), "-r", str(FPS), "-c:v", "libx264", "-crf", "16", "-preset", "medium", str(ra)], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(ra), "-vf", "fps=8,scale=384:-1,tile=8x7", "-frames:v", "1", str(RA / "intro-soi.jpg")], check=True)
    n = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets",
                        "-of", "csv=p=0", str(ra)], capture_output=True, text=True).stdout.strip().rstrip(",")
    print(f"intro: {n} khung (cần {INTRO_KHUNG}){'' if int(n) == INTRO_KHUNG else '  LỆCH'}")


if __name__ == "__main__":
    if "--render" in sys.argv:
        render()
