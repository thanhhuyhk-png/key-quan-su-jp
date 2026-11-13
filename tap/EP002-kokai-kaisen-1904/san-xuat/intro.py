# -*- coding: utf-8 -*-
"""
intro.py — Dựng trailer mở đầu 10 giây (黄海海戦 1904, EP002; chép từ EP001) ra MP4 24fps.

Cấu trúc theo beat sheet đã duyệt (mục 2 của đạo diễn): 7 nhịp + thẻ tiêu đề,
cắt 1–1.3 s. Mỗi nhịp lấy hình theo thứ tự ưu tiên:
  1) clip/ảnh THẬT nếu có ở <clips>/<scene>.(mp4|mov|png|jpg)  (footage tư liệu, clip AI đã tạo tay…)
  2) nếu không: Ô GIỮ CHỖ — nền gradient theo tông cảnh + chữ Nhật (để soi NHỊP sớm)
Mỗi nhịp tự chạy qua chuỗi hoá cũ của loc-tu-lieu-cu.py (mức --muc, mặc định 0.5)
để AI + tư liệu thật + bản đồ về một tông "bản scan 1905".

Mốc phim của cả tập phải LÙI INTRO_KHUNG = round(10*24) = 240 khung (ghi ra intro.json).

Dùng:
  python -I -X utf8 intro.py                      # render nháp bằng ô giữ chỗ
  python -I -X utf8 intro.py --clips clips --muc 0.5
  python -I -X utf8 intro.py --out <đường dẫn>/intro.mp4
Luật: chữ trên hình AI phải có nhãn 「イラスト」 (xem ho-so-kenh/luat-noi-dung.md);
nhãn đó thêm ở lớp chữ P5, không nướng vào clip gốc.
"""
import argparse, json, os, subprocess, sys, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 24
W, H = 1920, 1080
FONT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "template", "fonts", "NotoSerifJP-Bold.ttf"))

# nạp chuoi_loc từ loc-tu-lieu-cu.py (tên có gạch nối → import bằng spec)
_spec = importlib.util.spec_from_file_location("loctulieu", os.path.join(HERE, "loc-tu-lieu-cu.py"))
_lt = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_lt)

# beat sheet: (scene, t0, t1, chữ, nhấn to?, tông nền gradient)
BEATS = [
    ("black", 0.0, 0.6, "",                 False, "#000000:#0a0a0a"),
    ("sea",   0.6, 1.8, "6対4",            True,  "#0c1116:#1a0f0c"),
    ("line",  1.8, 3.0, "沈没 0隻",         True,  "#0c1218:#10171c"),
    ("guns",  3.0, 4.1, "一発の砲弾",        False, "#1a0f0a:#06090c"),
    ("route", 4.1, 5.3, "",                 False, "#0c1218:#0a1016"),
    ("tjifa", 5.3, 6.4, "午後6時40分ごろ",    False, "#0b1116:#0b1116"),
    ("fire",  6.4, 7.3, "日没まで あと1時間20分", False, "#2a1206:#0a0c0e"),
    ("title", 7.3, 10.0, "",                False, "#000000:#000000"),
]
INTRO_KHUNG = round(10.0 * FPS)


def chay(args):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        sys.stderr.write(p.stderr[-2000:] + "\n")
        raise SystemExit(f"ffmpeg lỗi: {' '.join(str(x) for x in args[:5])}…")
    return p


def tim_clip(clips_dir, scene):
    if not clips_dir:
        return None
    for ext in (".mp4", ".mov", ".mkv", ".png", ".jpg", ".jpeg", ".webp"):
        p = os.path.join(clips_dir, scene + ext)
        if os.path.exists(p):
            return p
    return None


def esc(txt):
    return txt.replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")


FONTP = FONT.replace("\\", "/").replace(":", r"\:")


def chu_hook(txt, big):
    """drawtext chữ hook (nhấn to đỏ giữa, hoặc kem dưới)."""
    if not txt:
        return []
    sz = 230 if big else 96
    c = "0xCC2222" if big else "0xF0E8D8"
    y = "(h-text_h)/2" if big else "h*0.78"
    return [f"drawtext=fontfile='{FONTP}':text='{esc(txt)}':fontcolor={c}:"
            f"fontsize={sz}:x=(w-text_w)/2:y={y}:shadowcolor=black:shadowx=4:shadowy=4"]


def nhan_ai():
    """Nhãn 「AI生成イメージ」 bắt buộc cho hình AI (luật ngách mục 5)."""
    return [f"drawtext=fontfile='{FONTP}':text='AI生成イメージ':fontcolor=0x9a9a9a:"
            f"fontsize=28:x=w-text_w-50:y=h-62:shadowcolor=black:shadowx=2:shadowy=2"]


def nhan_dohoa():
    """Nhãn 「作図」 cho đồ hoạ vector tự vẽ (bản đồ, sơ đồ) — không phải AI."""
    return [f"drawtext=fontfile='{FONTP}':text='作図：戦陣再審':fontcolor=0x9a9a9a:"
            f"fontsize=26:x=w-text_w-50:y=h-60:shadowcolor=black:shadowx=2:shadowy=2"]


VECTOR = {"route", "tjifa"}  # cảnh đồ hoạ tự vẽ (không dán nhãn AI)


def nguon_giu_cho(scene, c0, c1, dur, tmp):
    """Ô giữ chỗ: chỉ gradient tối theo tông cảnh (chữ vẽ sau ở phu_chu)."""
    out = os.path.join(tmp, f"src_{scene}.mp4")
    grad = (f"gradients=s={W}x{H}:c0={c0}:c1={c1}:x0=0:y0=0:x1=0:y1={H}:"
            f"nb_colors=2:d={dur}:r={FPS}")
    chay(["ffmpeg", "-y", "-f", "lavfi", "-i", grad,
          "-vf", "format=yuv420p", "-t", f"{dur}", "-c:v", "libx264", "-crf", "18", out])
    return out


def phu_chu(src, dur, tmp, scene, txt, big, is_ai, is_placeholder, is_vector=False):
    """Vẽ chữ SAU lớp hoá cũ: chữ hook nét, thẻ tiêu đề, nhãn AI, nhãn ô giữ chỗ."""
    draw = []
    if scene == "title":
        def dt(t, sz, c, y):
            return (f"drawtext=fontfile='{FONTP}':text='{esc(t)}':fontcolor={c}:"
                    f"fontsize={sz}:x=(w-text_w)/2:y={y}:shadowcolor=black:shadowx=3:shadowy=3")
        draw += [
            dt("黄海海戦", 200, "0xF0E8D8", "h*0.33"),
            "drawbox=x=(iw-600)/2:y=ih*0.33+230:w=600:h=6:color=0xCC2222:t=fill",
            dt("1904 ・ 逃げ切りまで、あと何時間", 64, "0xE0583F", "h*0.33+270"),
            dt("旅順艦隊はなぜ逃げ切れなかったのか", 38, "0xCFC8BA", "h*0.33+360"),
        ]
    else:
        draw += chu_hook(txt, big)
    # chủ kênh 13/11/2026: bỏ chữ «AI生成», nhãn «作図：tên kênh» và tên kênh khỏi video; hình AI giữ nhãn nhỏ «イラスト» (luật kit)
    if is_ai:
        draw += [f"drawtext=fontfile='{FONTP}':text='イラスト':fontcolor=0xCFC8BA:fontsize=30:x=70:y=h-70:shadowcolor=black:shadowx=2:shadowy=2"]
    if not draw:
        return src
    out = os.path.join(tmp, f"fin_{scene}.mp4")
    chay(["ffmpeg", "-y", "-i", src, "-vf", ",".join(draw), "-t", f"{dur}",
          "-r", str(FPS), "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", out])
    return out


def nguon_that(path, dur, tmp, scene):
    """Clip/ảnh thật → chuẩn hoá 1920x1080, FPS, cắt/giữ đúng dur."""
    out = os.path.join(tmp, f"src_{scene}.mp4")
    is_img = path.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    pre = ["-loop", "1", "-t", f"{dur}"] if is_img else []
    # scale phủ khung + Ken Burns nhẹ cho ảnh tĩnh
    if is_img:
        zp = f"scale=2400:-1,zoompan=z='min(zoom+0.0008,1.12)':d={round(dur*FPS)}:s={W}x{H}:fps={FPS}"
    else:
        zp = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    chay(["ffmpeg", "-y"] + pre + ["-i", path, "-an",
          "-vf", f"{zp},format=yuv420p", "-t", f"{dur}", "-r", str(FPS),
          "-c:v", "libx264", "-crf", "18", out])
    return out


def hoa_cu(src, dur, muc, tmp, scene, idx):
    """Chạy nguồn qua chuỗi hoá cũ (video)."""
    out = os.path.join(tmp, f"cu_{scene}.mp4")
    fg = _lt.chuoi_loc(muc, video=True, W=W, H=H, seed=1905 + idx)
    chay(["ffmpeg", "-y", "-i", src, "-filter_complex", fg, "-map", "[v]",
          "-t", f"{dur}", "-r", str(FPS), "-c:v", "libx264", "-crf", "20",
          "-pix_fmt", "yuv420p", out])
    return out


def main():
    ap = argparse.ArgumentParser(description="Dựng trailer mở đầu 10s ra MP4")
    ap.add_argument("--clips", help="thư mục chứa footage/clip AI thật: <scene>.mp4|png")
    ap.add_argument("--muc", type=float, default=0.5, help="mức hoá cũ 0..1")
    ap.add_argument("--out", default=os.path.join(HERE, "intro-nhap.mp4"))
    ap.add_argument("--giu-tmp", action="store_true")
    a = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="intro_")
    segs = []
    print(f"Font: {FONT}  (có: {os.path.exists(FONT)})")
    for i, (scene, t0, t1, txt, big, grad) in enumerate(BEATS):
        dur = round(t1 - t0, 3)
        c0, c1 = grad.split(":")
        real = tim_clip(a.clips, scene)
        is_vec = scene in VECTOR
        if real:
            src = nguon_that(real, dur, tmp, scene); ph = False
            is_ai = not is_vec
            tag = f"{'ĐỒ HOẠ' if is_vec else 'AI'}({os.path.basename(real)})"
        else:
            src = nguon_giu_cho(scene, c0, c1, dur, tmp); is_ai = False; ph = True
            tag = "ô giữ chỗ"
        cu = hoa_cu(src, dur, a.muc, tmp, scene, i)
        fin = phu_chu(cu, dur, tmp, scene, txt, big, is_ai, ph, is_vec and bool(real))
        segs.append(fin)
        print(f"  [{i+1}/{len(BEATS)}] {scene:6s} {dur:.2f}s  {tag}")

    # concat
    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for s in segs:
            f.write(f"file '{s.replace(chr(92),'/')}'\n")
    # audio drone tạm để file có tiếng (nhạc thật ở P6)
    chay(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
          "-f", "lavfi", "-i", "sine=frequency=55:sample_rate=48000",
          "-shortest", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-b:a", "128k", "-af", "volume=0.08", a.out])

    meta = {"intro_khung": INTRO_KHUNG, "fps": FPS, "dur_s": 10.0,
            "beats": [{"scene": b[0], "t0": b[1], "t1": b[2], "txt": b[3]} for b in BEATS],
            "ghi_chu": "Mọi mốc phim của tập LÙI intro_khung khung. Clip thật bỏ vào --clips/<scene>.*"}
    mj = os.path.join(HERE, "intro.json")
    json.dump(meta, open(mj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if not a.giu_tmp:
        for s in os.listdir(tmp):
            try: os.unlink(os.path.join(tmp, s))
            except OSError: pass
        try: os.rmdir(tmp)
        except OSError: pass
    print(f"\nXong → {a.out}")
    print(f"INTRO_KHUNG = {INTRO_KHUNG} (ghi {mj}); mốc phim toàn tập lùi {INTRO_KHUNG} khung.")


if __name__ == "__main__":
    main()
