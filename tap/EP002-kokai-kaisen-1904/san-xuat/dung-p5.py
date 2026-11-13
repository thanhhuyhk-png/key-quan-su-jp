# -*- coding: utf-8 -*-
"""
dung-p5.py — Dựng hình thân phim EP002 黄海海戦 1904 từ phan-canh.json (P5, chép từ EP001 JP 13/11/2026).

Một cảnh = một tệp MP4 1920×1080 24 fps đúng số khung round(t1·24) − round(t0·24), ra
<output>/261111-nihonkai-kaisen-1905/hinh/p5/<mã>.mp4 (chỉ hình, không tiếng).
  - clip:<Vxx>   clip AI (Flow): crop viền phim 4 % (V12, V19, V21: crop trái 13 %), mỗi lần dùng cắt đoạn khác nhau.
  - anh:<KEY>    ảnh tư liệu: Ken Burns bằng ffmpeg zoompan, tông cũ nhẹ, hạt, vignette; chân dung = contain.
  - ban-do:<m>   bản đồ vẽ PIL theo bảng màu kênh (nền #111111, kem #f0e8d8, đỏ #cc2222): tsushima, tjifa, koukai
                 (yoru, tsuigeki, sekai, sekkin: lô sau).
  - the:<tên>    thẻ số liệu PIL (chữ vào dần, số tô đỏ).
Chữ trên hình = lớp PNG trong suốt phủ khi ghép (nhãn «AI生成», thẻ tên, ghi nguồn ảnh).

Chạy:  python -I -X utf8 dung-p5.py [--lo N | --tu S001 --den S028] [--stills] [--lam-lai] [S0xx ...]
       --stills: chỉ dựng 3 khung/cảnh vào hinh/p5-stills để soi (nhanh).
Lô: 0 = S001–S028 (開幕 ~72 s).
"""
import csv, json, math, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
REPO = next(p for p in GOC.parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO / "tools"))
from cau_hinh import duong  # noqa: E402

OUT = duong("output") / "261113-kokai-kaisen-1904"
RA = OUT / "hinh" / "p5"
FONTB = str(REPO / "template/fonts/NotoSerifJP-Bold.ttf")
FONTR = str(REPO / "template/fonts/NotoSerifJP-Regular.ttf")
W, H, FPS = 1920, 1080, 24
NEN = (17, 17, 17); KEM = (240, 232, 216); KEMP = (207, 200, 186); DO = (204, 34, 34); DOS = (155, 28, 28)
XAM = (110, 110, 106); LUOI = (34, 34, 33); DAT = (38, 37, 35)
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))
ANH = {r["tep"]: r for r in csv.DictReader(open(GOC / "anh.tsv", encoding="utf-8"), delimiter="\t")}
CLIP = {r["ma"]: r for r in csv.DictReader(open(GOC / "clip.tsv", encoding="utf-8"), delimiter="\t")}
BOBIEN = None  # EP002: bản đồ chỉ dựng 3D (dung-3d.py); bản PIL cũ của EP001 không dùng
CROP_TRAI = {"V12", "V19", "V21"}
CHAN_DUNG = {"TOGOP", "VIT", "ADM1", "ADM2"}  # chân dung: contain, không cắt, không tách nền


def fnt(sz, bold=True):
    return ImageFont.truetype(FONTB if bold else FONTR, sz)


def khung_cua(c):
    a = round(c["t0"] * FPS)
    b = round(c["t1"] * FPS)
    return max(1, b - a), a


def ff(args, **kw):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args, capture_output=True, text=True, encoding="utf-8", **kw)
    if r.returncode:
        raise RuntimeError(r.stderr[-800:])


ENC = ["-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]


# ------------------------------------------------------------------ lớp chữ (PNG trong suốt)
def vien_chu(d, xy, s, f, fill, anchor="la", w=4):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=w, stroke_fill=(0, 0, 0, 255))


NHAN_AI = True  # EP002 (13/11): bỏ chữ «AI生成» nhưng giữ nhãn nhỏ «イラスト» trên clip AI (luật kit: hình minh hoạ ghi chữ trên hình)


def lop_chu(c, tmp):
    """Trả đường dẫn PNG lớp chữ hoặc None."""
    kieu = c["kieu"]
    chu = c["chu"]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    co = False
    m = re.search(r'Thẻ tên "([^"]+)"', chu)
    if m:
        ten = m.group(1)
        f = fnt(56)
        w = d.textlength(ten, font=f)
        d.rectangle([84, H - 190, 94, H - 118], fill=DO + (255,))
        vien_chu(d, (114, H - 154), ten, f, KEM + (255,), "lm")
        co = True
    if NHAN_AI and "イラスト" in chu:
        f = fnt(30, False)
        vien_chu(d, (70, H - 60), "イラスト", f, KEMP + (235,), "lm", 3)
        co = True
    m = re.search(r'Chú thích "([^"]+)"', chu)
    if m:
        f = fnt(30, False)
        vien_chu(d, (70, H - 60), m.group(1), f, KEMP + (235,), "lm", 3)
        co = True
    if kieu == "anh":
        r = ANH[c["ten"]]
        nguon = ("写真: Wikimedia Commons" if "Commons" in r["ghi_nguon"] else "写真: 国立国会図書館" if "国立国会図書館" in r["ghi_nguon"] else "写真")
        if r["hang"] == "A?":
            nguon += " (出典要確認)" if False else ""
        f = fnt(26, False)
        vien_chu(d, (W - 70, H - 60), nguon, f, KEMP + (230,), "rm", 3)
        co = True
    if not co:
        return None
    p = tmp / f"lop_{c['id']}.png"
    im.save(p)
    return p


def them_lop(base_mp4, lop, n, out):
    """Phủ lớp chữ (fade in 0,3 s sau khi vào cảnh) lên video."""
    d = n / FPS
    ff(["-i", str(base_mp4), "-loop", "1", "-t", f"{d + 0.6:.3f}", "-i", str(lop), "-filter_complex",
        "[1:v]format=rgba,fade=in:st=0.25:d=0.35:alpha=1[o];[0:v][o]overlay=0:0:shortest=1,format=yuv420p", "-frames:v", str(n)] + ENC + [str(out)])


# ------------------------------------------------------------------ clip AI
def dung_clip(c, n, dung_lan, out):
    ma = c["ten"]
    src = CLIP[ma]["file"]
    start = [0.15, 1.3, 0.6][dung_lan % 3]
    dur = n / FPS
    start = min(start, max(0.0, CLIP_DAI(ma) - dur - 0.1))
    if ma in CROP_TRAI:
        vf = "crop=iw*0.80:ih*0.80:iw*0.17:ih*0.10"
    else:
        vf = "crop=iw*0.92:ih*0.92:iw*0.04:ih*0.04"
    # tăng nhẹ độ tương phản để đồng tông với ảnh; scale về 1920×1080
    vf += f",scale={W}:{H}:flags=lanczos,eq=contrast=1.06:brightness=-0.01,fps={FPS},tpad=stop_mode=clone:stop=4"
    ff(["-ss", f"{start:.2f}", "-i", src, "-vf", vf, "-frames:v", str(n)] + ENC + [str(out)])


def CLIP_DAI(ma):
    return float(CLIP[ma]["dai"]) - 0.0


# ------------------------------------------------------------------ ảnh tư liệu (Ken Burns)
PAN = [  # (zoom0, zoom1, x0, y0, x1, y1) theo tỉ lệ vùng cửa sổ
    (1.00, 1.14, 0.50, 0.50, 0.55, 0.48),
    (1.12, 1.00, 0.35, 0.55, 0.45, 0.50),
    (1.04, 1.16, 0.65, 0.45, 0.50, 0.55),
    (1.14, 1.04, 0.50, 0.40, 0.50, 0.55),
]


def dung_anh(c, n, idx, out):
    key = c["ten"]
    r = ANH[key]
    src = r["file"]
    dur = n / FPS
    z0, z1, x0, y0, x1, y1 = PAN[idx % len(PAN)]
    gr = "hue=s=0.22,eq=contrast=1.08:brightness=-0.02:gamma=0.95,noise=alls=7:allf=t+u,vignette=PI/4.5"
    if key in CHAN_DUNG:
        # contain: ảnh đứng cao 900 giữa khung nền tối
        fc = (f"[0:v]scale=-2:900:flags=lanczos,{gr}[a];color=c=0x111111:s={W}x{H}:r={FPS}[b];"
              f"[b][a]overlay=(W-w)/2:(H-h)/2+10:shortest=1,zoompan=z='1+0.05*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS}")
        ff(["-loop", "1", "-t", f"{dur + 0.5:.3f}", "-framerate", str(FPS), "-i", src, "-filter_complex", fc, "-frames:v", str(n)] + ENC + [str(out)])
        return
    # cover: phóng 3000 px rồi zoompan (tránh rung do làm tròn)
    zexpr = f"{z0}+({z1}-{z0})*on/{n}"
    xexpr = f"(iw-iw/zoom)*({x0}+({x1}-{x0})*on/{n})"
    yexpr = f"(ih-ih/zoom)*({y0}+({y1}-{y0})*on/{n})"
    fc = (f"[0:v]scale=3200:1800:force_original_aspect_ratio=increase:flags=lanczos,crop=3200:1800,"
          f"zoompan=z='{zexpr}':x='{xexpr}':y='{yexpr}':d={n}:s={W}x{H}:fps={FPS},{gr}")
    ff(["-i", src, "-filter_complex", fc, "-frames:v", str(n)] + ENC + [str(out)])


# ------------------------------------------------------------------ bản đồ và thẻ (PIL)
def nen_luoi(d, t=0.0):
    d.rectangle([0, 0, W, H], fill=NEN)
    for x in range(0, W, 120):
        d.line([x, 0, x, H], fill=LUOI)
    for y in range(0, H, 120):
        d.line([0, y, W, y], fill=LUOI)


def khung_do(d):
    for (x, y, sx, sy) in ((40, 40, 1, 1), (W - 40, 40, -1, 1), (40, H - 40, 1, -1), (W - 40, H - 40, -1, -1)):
        d.line([x, y, x + 90 * sx, y], fill=DO, width=5)
        d.line([x, y, x, y + 90 * sy], fill=DO, width=5)


def chu(d, xy, s, sz, fill=KEM, anchor="mm", bold=True, w=3):
    d.text(xy, s, font=fnt(sz, bold), fill=fill, anchor=anchor, stroke_width=w, stroke_fill=(0, 0, 0))


def tam_giac(d, x, y, rot, fill, sc=1.0):
    pts = [(0, -17 * sc), (11 * sc, 13 * sc), (-11 * sc, 13 * sc)]
    r = math.radians(rot)
    d.polygon([(x + px * math.cos(r) - py * math.sin(r), y + px * math.sin(r) + py * math.cos(r)) for px, py in pts], fill=fill)


def ease(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def proj_tsushima():
    lon0, lon1, lat0, lat1 = BOBIEN["khung"]
    kx = math.cos(math.radians((lat0 + lat1) / 2))
    sc = min(W / ((lon1 - lon0) * kx), H / (lat1 - lat0)) * 0.96
    ox = (W - (lon1 - lon0) * kx * sc) / 2
    oy = (H - (lat1 - lat0) * sc) / 2
    return lambda lon, lat: (ox + (lon - lon0) * kx * sc, H - oy - (lat - lat0) * sc)


def f_tsushima(k, base):
    im = Image.new("RGB", (W, H), NEN)
    d = ImageDraw.Draw(im)
    if base is None:
        pr = proj_tsushima()
        b = Image.new("RGB", (W, H), NEN)
        bd = ImageDraw.Draw(b)
        nen_luoi(bd)
        for v in BOBIEN["vong"]:
            pts = [pr(x, y) for x, y in v]
            if len(pts) > 3 and max(p[0] for p in pts) > -50 and min(p[0] for p in pts) < W + 50:
                bd.polygon(pts, fill=DAT, outline=KEMP)
        base = (b, pr)
    b, pr = base
    im = b.copy()
    d = ImageDraw.Draw(im)
    khung_do(d)
    chu(d, (W / 2, 78), "対馬海峡 ・ 1905年5月27日", 46, KEMP)
    # hạm đội Nga: tuyến tiến từ SW lên NE qua eo biển; hạm đội Nhật: tuyến chặn từ Chinhae
    ru = [pr(126.8, 32.9), pr(128.6, 33.7), pr(129.6, 34.4), pr(130.6, 35.4)]
    ja = [pr(128.6, 35.0), pr(129.4, 34.6), pr(129.9, 34.4)]
    u = ease(k * 1.15)
    seg = u * (len(ru) - 1)
    i = min(int(seg), len(ru) - 2)
    f = seg - i
    pos = (ru[i][0] + (ru[i + 1][0] - ru[i][0]) * f, ru[i][1] + (ru[i + 1][1] - ru[i][1]) * f)
    for a, bb in zip(ru, ru[1:]):
        d.line([a, bb], fill=XAM, width=4)
    for n_ in range(5):
        tam_giac(d, pos[0] - n_ * 22, pos[1] + n_ * 12, 40, XAM, 1.2)
    chu(d, (pos[0] - 70, pos[1] + 70), "バルチック艦隊", 34, KEMP, "rm")
    uj = ease(k * 1.4 - 0.1)
    if uj > 0:
        for n_ in range(5):
            x = ja[0][0] + (ja[1][0] - ja[0][0]) * uj + n_ * 26
            y = ja[0][1] + (ja[1][1] - ja[0][1]) * uj - n_ * 4
            tam_giac(d, x, y, -70, DO, 1.2)
        chu(d, (ja[1][0] + 40, ja[1][1] - 70), "連合艦隊", 34, (224, 88, 63), "lm")
    chu(d, (pr(129.3, 34.45)[0], pr(129.3, 34.45)[1] - 36), "対馬", 30, KEM, "mm")
    chu(d, (W - 90, H - 70), "作図(概略)・地形: Natural Earth", 24, KEMP, "rm", False, 2)
    return im, base


TJIFA_VAR = [0, 0.45, 0.2, 0.7]
TJIFA_CAP = ["全砲門を向ける ⇔ 先頭艦しか撃てない", "横列 = 全砲塔 / 縦列 = 先頭艦のみ", "T字を支えるのは 速力の差", "15ノット 対 11ノット"]
_VAR_HIEN_TAI = {"v": 0}


def f_tjifa(k, base):
    k = min(1.0, TJIFA_VAR[_VAR_HIEN_TAI["v"] % 4] + k * (1 - TJIFA_VAR[_VAR_HIEN_TAI["v"] % 4]))
    im = Image.new("RGB", (W, H), NEN)
    d = ImageDraw.Draw(im)
    nen_luoi(d)
    khung_do(d)
    cx, top = W * 0.5, H * 0.34
    adv = ease(k * 1.1)
    for i in range(6):
        tam_giac(d, cx, H * 0.84 - i * 72 - adv * 60, 0, XAM, 1.3)
    chu(d, (cx - 90, H * 0.80), "ロシア艦隊(縦列)", 36, KEMP, "rm")
    line = max(0.0, min(1.0, k * 1.6 - 0.1))
    for i in range(6):
        x = cx - 360 + i * 144
        if (x - (cx - 360)) / 720 <= line + 1e-6:
            tam_giac(d, x, top, 90, DO, 1.3)
    chu(d, (cx + 400, top), "連合艦隊(横列)", 36, (224, 88, 63), "lm")
    if k > 0.45:
        for i in range(5):
            x = cx - 240 + i * 120
            d.line([x, top + 46, cx, top + 190], fill=(224, 88, 63), width=5)
            d.polygon([(cx, top + 190), (cx - 11, top + 172), (cx + 11, top + 172)], fill=(224, 88, 63))
    chu(d, (cx + 470, H * 0.52), "T字", 190, KEM)
    chu(d, (cx, H * 0.93), TJIFA_CAP[_VAR_HIEN_TAI["v"] % 4], 38, KEMP)
    chu(d, (W - 90, 70), "作図(概略)", 24, KEMP, "rm", False, 2)
    return im, None


def f_koukai(k, base):
    im = Image.new("RGB", (W, H), NEN)
    d = ImageDraw.Draw(im)
    nen_luoi(d)
    khung_do(d)
    pts = [(260, 220, "バルト海"), (420, 400, "北海"), (560, 560, "喜望峰"), (820, 720, "マダガスカル"),
           (1180, 650, "マラッカ"), (1420, 560, "カムラン湾"), (1620, 330, "対馬")]
    chu(d, (W / 2, 78), "バルチック艦隊の航路 ・ 約7か月", 46, KEMP)
    u = ease(k * 1.2) * (len(pts) - 1)
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        f = max(0.0, min(1.0, u - i))
        if f > 0:
            for t in range(0, int(100 * f)):
                x = a[0] + (b[0] - a[0]) * t / 100
                y = a[1] + (b[1] - a[1]) * t / 100
                if t % 3 == 0:
                    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(224, 88, 63))
    for i, (x, y, s) in enumerate(pts):
        r = 11 if i < int(u) + 1 else 7
        d.ellipse([x - r, y - r, x + r, y + r], fill=DO if i < int(u) + 1 else XAM)
        chu(d, (x, y - 40), s, 34, KEM if i < int(u) + 1 else XAM)
    chu(d, (W - 90, H - 70), "作図(概略)", 24, KEMP, "rm", False, 2)
    return im, None



def _co_so_tsushima(base):
    if base is None:
        pr = proj_tsushima()
        b = Image.new("RGB", (W, H), NEN)
        bd = ImageDraw.Draw(b)
        nen_luoi(bd)
        for v in BOBIEN["vong"]:
            pts = [pr(x, y) for x, y in v]
            if len(pts) > 3 and max(p[0] for p in pts) > -50 and min(p[0] for p in pts) < W + 50:
                bd.polygon(pts, fill=DAT, outline=KEMP)
        base = (b, pr)
    return base


def f_yoru(k, base):
    base = _co_so_tsushima(base)
    b, pr = base
    im = b.point(lambda v: int(v * 0.55))
    d = ImageDraw.Draw(im)
    khung_do(d)
    chu(d, (W / 2, 78), "夜襲 ・ 5月27日 日没後", 46, KEMP)
    tgt = pr(129.9, 34.55)
    rng = [pr(129.5, 34.2), pr(129.7, 34.3), pr(129.85, 34.4)]
    for n_ in range(6):
        tam_giac(d, tgt[0] - 20 + n_ * 18, tgt[1] + 8 - n_ * 4, 40, XAM, 1.1)
    chu(d, (tgt[0] - 150, tgt[1] + 60), "ロシア艦隊", 34, KEMP, "rm")
    u = ease(k * 1.3)
    for i in range(8):
        ang = math.radians(-60 + i * 17)
        sx, sy = tgt[0] + math.cos(ang) * 420, tgt[1] - math.sin(ang) * 300 + 120
        x = sx + (tgt[0] - sx) * u * 0.85
        y = sy + (tgt[1] - sy) * u * 0.85
        d.line([sx, sy, x, y], fill=(224, 88, 63), width=3)
        tam_giac(d, x, y, math.degrees(math.atan2(tgt[1] - sy, tgt[0] - sx)) + 90, DO, 1.0)
    chu(d, (W - 560, H - 160), "駆逐艦21隻 ・ 水雷艇45隻", 40, (224, 88, 63), "mm")
    chu(d, (W - 90, H - 70), "作図(概略)・地形: Natural Earth", 24, KEMP, "rm", False, 2)
    return im, base


def f_tsuigeki(k, base):
    base = _co_so_tsushima(base)
    b, pr = base
    im = b.copy()
    d = ImageDraw.Draw(im)
    khung_do(d)
    chu(d, (W / 2, 78), "追撃 ・ 5月28日", 46, KEMP)
    u = ease(k * 1.2)
    ru0 = pr(129.4, 34.9)
    for i in range(5):
        x = ru0[0] - 40 + u * 220 - i * 26
        y = ru0[1] - 20 - u * 230 + i * 14
        tam_giac(d, x, y, 20, XAM, 1.1)
    chu(d, (ru0[0] + 130, ru0[1] - 110), "ロシア残存艦(北へ)", 32, KEMP, "lm")
    for i in range(5):
        x = ru0[0] - 150 + u * 220 - i * 24
        y = ru0[1] + 100 - u * 230 + i * 16
        tam_giac(d, x, y, 20, DO, 1.1)
    chu(d, (ru0[0] - 200, ru0[1] + 140), "連合艦隊(追撃)", 32, (224, 88, 63), "rm")
    if k > 0.75:
        chu(d, (W / 2, H - 120), "午前10時過ぎ ネボガトフ少将 降伏", 44, KEM)
    chu(d, (W - 90, H - 70), "作図(概略)・地形: Natural Earth", 24, KEMP, "rm", False, 2)
    return im, base


def f_sekkin(k, base):
    base = _co_so_tsushima(base)
    b, pr = base
    im = b.copy()
    d = ImageDraw.Draw(im)
    khung_do(d)
    chu(d, (W / 2, 78), "両艦隊の接近 ・ 午後", 46, KEMP)
    u = ease(k * 1.15)
    a0, a1 = pr(128.7, 34.8), pr(129.5, 34.45)
    b0, b1 = pr(130.9, 33.6), pr(129.8, 34.15)
    for i in range(4):
        x = a0[0] + (a1[0] - a0[0]) * u - i * 22
        y = a0[1] + (a1[1] - a0[1]) * u - i * 10
        tam_giac(d, x, y, 120, DO, 1.2)
    for i in range(5):
        x = b0[0] + (b1[0] - b0[0]) * u + i * 22
        y = b0[1] + (b1[1] - b0[1]) * u + i * 12
        tam_giac(d, x, y, -40, XAM, 1.2)
    chu(d, (a0[0] - 20, a0[1] - 60), "連合艦隊", 34, (224, 88, 63), "rm")
    chu(d, (b0[0] + 20, b0[1] + 60), "バルチック艦隊", 34, KEMP, "lm")
    chu(d, (W - 90, H - 70), "作図(概略)・地形: Natural Earth", 24, KEMP, "rm", False, 2)
    return im, base


def f_sekai(k, base):
    im = Image.new("RGB", (W, H), NEN)
    d = ImageDraw.Draw(im)
    nen_luoi(d)
    khung_do(d)
    chu(d, (W / 2, 78), "日本海海戦の影響", 46, KEMP)
    nodes = [(1480, 520, "日本", DO), (500, 360, "イギリス", XAM), (460, 740, "アメリカ", XAM), (860, 320, "ドイツ", XAM), (1250, 280, "ロシア", XAM)]
    u = ease(k * 1.3)
    for i, (x, y, s_, col) in enumerate(nodes[1:], 1):
        a = ease(u * 4 - i * 0.7)
        if a > 0:
            d.line([nodes[0][0], nodes[0][1], x, y], fill=tuple(int(NEN[j] + (DOS[j] - NEN[j]) * a) for j in range(3)), width=3)
    for i, (x, y, s_, col) in enumerate(nodes):
        a = 1.0 if i == 0 else ease(u * 4 - i * 0.5)
        if a <= 0:
            continue
        r = int(18 + 10 * a)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        chu(d, (x, y - 50), s_, 40, KEM)
    if k > 0.6:
        chu(d, (W / 2, H - 130), "速さと砲力を競う、大艦巨砲の時代へ", 44, KEM)
    chu(d, (W - 90, H - 70), "作図(概略)", 24, KEMP, "rm", False, 2)
    return im, None


def f_nhan(kieu):
    return {"tsushima": f_tsushima, "tjifa": f_tjifa, "koukai": f_koukai, "yoru": f_yoru, "tsuigeki": f_tsuigeki, "sekkin": f_sekkin, "sekai": f_sekai}.get(kieu)


ZOOM = {0: None, 1: (1.18, 0.50, 0.46), 2: (1.24, 0.58, 0.50), 3: (1.14, 0.44, 0.54)}  # (hệ số, tâm x, tâm y theo khung)


def zoom_im(im, z):
    if z is None:
        return im
    f, cx, cy = z
    w, h = int(W / f), int(H / f)
    x = int(min(max(cx * W - w / 2, 0), W - w))
    y = int(min(max(cy * H - h / 2, 0), H - h))
    return im.crop((x, y, x + w, y + h)).resize((W, H), Image.LANCZOS)


def dung_frames(fn_frame, n, out, tmp, stills=False, var=0):
    base = None
    _VAR_HIEN_TAI["v"] = var
    co_zoom = fn_frame not in (f_tjifa, f_koukai, f_sekai) and not getattr(fn_frame, "__name__", "") == "fr"
    d = tmp / "f"
    d.mkdir(exist_ok=True)
    chon = {0, n // 2, n - 1} if stills else set(range(n))
    for i in range(n):
        if i not in chon:
            continue
        k = i / max(1, n - 1)
        im, base = fn_frame(k, base)
        zoom_im(im, ZOOM.get(var % 4) if co_zoom else None).save(d / f"{i:05d}.png")
    if stills:
        return sorted(d.glob("*.png"))
    ff(["-framerate", str(FPS), "-i", str(d / "%05d.png")] + ENC + [str(out)])
    shutil.rmtree(d, ignore_errors=True)
    return None


def f_the(c):
    ten = c["ten"]
    m = re.search(r"Thẻ số liệu: (.+)$", c["hinh"])
    van = m.group(1) if m else c["hinh"]
    nguon = re.search(r"Nguồn: ([^\"·]+)", c["chu"])
    nguon = nguon.group(1).strip() if nguon else ""
    ngay = {"knot": "日本海海戦", "ngay": "日本海海戦", "ketqua": "海戦の結果", "phao": "主砲の数"}.get(ten, "日本海海戦 · 1905")
    dong = [x.strip() for x in re.split(r"\s/\s| \| ", van)]

    def fr(k, base):
        im = Image.new("RGB", (W, H), NEN)
        d = ImageDraw.Draw(im)
        nen_luoi(d)
        khung_do(d)
        a = ease(k * 4)
        chu(d, (W / 2, 190), ngay, 44, DOS if False else (176, 60, 60), "mm", True, 2)
        d.line([W / 2 - 160, 240, W / 2 + 160, 240], fill=DO, width=4)
        ny = H / 2 - (len(dong) - 1) * 95
        for i, s in enumerate(dong):
            ai = ease(k * 5 - i * 0.55)
            if ai <= 0:
                continue
            sz = int(150 if len(s) <= 7 else 110 if len(s) <= 11 else 84 if len(s) <= 18 else 66)
            sz = int(sz * (0.92 + 0.08 * ai))
            f = fnt(sz)
            # tô đỏ phần số và đơn vị
            parts = re.split(r"([0-9０-９,.:]+(?:ノット|隻|門|名|m)?)", s)
            tw = sum(d.textlength(p, font=f) for p in parts)
            x = W / 2 - tw / 2
            for p in parts:
                if not p:
                    continue
                col = (224, 88, 63) if re.match(r"[0-9０-９]", p) else KEM
                col = tuple(int(NEN[j] + (col[j] - NEN[j]) * ai) for j in range(3))
                d.text((x, ny + i * 190), p, font=f, fill=col, anchor="lm", stroke_width=3, stroke_fill=(0, 0, 0))
                x += d.textlength(p, font=f)
        if nguon:
            chu(d, (W / 2, H - 110), f"出典: {nguon}", 28, KEMP, "mm", False, 2)
        return im, None
    return fr


# ------------------------------------------------------------------ chạy
def dung_canh(c, tmp, dung_lan, idx, stills=False, var=0):
    n, _ = khung_cua(c)
    kieu = c["kieu"]
    out = RA / f"{c['id']}.mp4"
    base = tmp / f"{c['id']}_base.mp4"
    if stills:
        if kieu in ("ban-do", "the"):
            fn = f_nhan(c["ten"].split("+")[0]) if kieu == "ban-do" else f_the(c)
            if fn is None:
                return None
            return dung_frames(fn, n, None, tmp, True, var)
        return None
    if kieu == "clip":
        dung_clip(c, n, dung_lan, base)
    elif kieu == "anh":
        dung_anh(c, n, idx, base)
    elif kieu == "ban-do":
        # bản đồ 3D (three.js + tàu Meshy) — bản PIL cũ chỉ còn khi đặt BAN_DO_PIL=1
        if os.environ.get("BAN_DO_PIL") == "1":
            fn = f_nhan(c["ten"].split("+")[0])
            if fn is None:
                raise RuntimeError(f"{c['id']}: bản đồ '{c['ten']}' chưa có (lô sau)")
            dung_frames(fn, n, base, tmp, False, var)
        else:
            import importlib.util as _iu
            _sp = _iu.spec_from_file_location("dung_3d", GOC / "dung-3d.py")
            _m = _iu.module_from_spec(_sp); _sp.loader.exec_module(_m)
            _m.render_ban_do(c, base)
    elif kieu == "the":
        import importlib.util as _iu
        _sp = _iu.spec_from_file_location("dung_the_dong", GOC / "dung-the-dong.py")
        _m = _iu.module_from_spec(_sp); _sp.loader.exec_module(_m)
        _m.render_the(c, base)
    else:
        raise RuntimeError(f"{c['id']}: kiểu {kieu} chưa hỗ trợ")
    lop = lop_chu(c, tmp)
    if lop:
        them_lop(base, lop, n, out)
    else:
        shutil.copy(base, out)
    base.unlink(missing_ok=True)
    return out


def main():
    a = sys.argv[1:]
    stills = "--stills" in a
    lam_lai = "--lam-lai" in a
    ids = [x for x in a if re.fullmatch(r"S\d{3}", x)]
    canh = PC["canh"]
    if "--lo" in a:
        lo = int(a[a.index("--lo") + 1])
        rng = {0: ("S001", "S028"), 1: ("S029", "S299")}[lo]
        i0 = next(i for i, c in enumerate(canh) if c["id"] == rng[0])
        i1 = next(i for i, c in enumerate(canh) if c["id"] == rng[1])
        chon = canh[i0:i1 + 1]
    elif "--tu" in a:
        i0 = next(i for i, c in enumerate(canh) if c["id"] == a[a.index("--tu") + 1])
        i1 = next(i for i, c in enumerate(canh) if c["id"] == a[a.index("--den") + 1])
        chon = canh[i0:i1 + 1]
    else:
        chon = [c for c in canh if c["id"] in ids]
    # đếm lần dùng trước cảnh đang dựng (cho clip khác đoạn và ảnh khác đường máy)
    dung_clip_n, dung_anh_n = {}, {}
    lan = {}
    for c in canh:
        if c["kieu"] == "clip":
            lan[c["id"]] = dung_clip_n.get(c["ten"], 0)
            dung_clip_n[c["ten"]] = lan[c["id"]] + 1
    var_ban_do = {}
    cnt = {}
    for c in canh:
        if c["kieu"] == "ban-do":
            m = c["ten"].split("+")[0]
            var_ban_do[c["id"]] = cnt.get(m, 0)
            cnt[m] = cnt.get(m, 0) + 1
    RA.mkdir(parents=True, exist_ok=True)
    dst = (OUT / "hinh" / "p5-stills") if stills else RA
    dst.mkdir(parents=True, exist_ok=True)
    tong = 0
    for idx, c in enumerate(canh):
        if c not in chon:
            continue
        out = RA / f"{c['id']}.mp4"
        if out.exists() and not lam_lai and not stills:
            print(f"  {c['id']} đã có, bỏ qua")
            continue
        tmp = Path(tempfile.mkdtemp(prefix="p5_"))
        try:
            r = dung_canh(c, tmp, lan.get(c["id"], 0), idx, stills, var_ban_do.get(c["id"], 0))
            if stills and r:
                for k, p in enumerate(r):
                    shutil.copy(p, dst / f"{c['id']}_{k}.png")
            elif not stills:
                n, _ = khung_cua(c)
                tong += n
                print(f"  {c['id']} {c['nguon']:<18} {n} khung → {out.name}")
        except Exception as e:
            print(f"  LỖI {c['id']}: {e}")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print(f"Xong. {tong} khung dựng.")


if __name__ == "__main__":
    main()
