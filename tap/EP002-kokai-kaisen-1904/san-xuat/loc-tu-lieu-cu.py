# -*- coding: utf-8 -*-
"""
loc-tu-lieu-cu.py — Hoá cũ ảnh/clip cho giống video tư liệu thật (1905 風).

Chạy bản sạch (AI/bản đồ/ảnh) qua một chuỗi ffmpeg: hạ phân giải, mờ nhẹ,
phai tông + sepia, nâng đen hạ trắng (bạc màu), quầng sáng (halation),
vignette tối góc, hạt phim, bụi + vết xước dọc, nén JPEG hai lần.

Mức 0..1 (mặc định 0.5). 1.0 làm nhiễu quá tay mất chi tiết → dùng 0.5.
Ảnh gốc giữ trong goc/, ảnh đã lọc ra thư mục cha (giống ghi chú chủ kênh).

Dùng:
  # một ảnh
  python -I -X utf8 loc-tu-lieu-cu.py anh.png --out anh-cu.jpg --muc 0.5
  # cả thư mục goc/ -> thư mục cha
  python -I -X utf8 loc-tu-lieu-cu.py --goc assets-moi/ai/goc --muc 0.5
  # clip (giữ chuyển động, hạt phim động, bỏ nén JPEG)
  python -I -X utf8 loc-tu-lieu-cu.py clip.mp4 --out clip-cu.mp4 --video --muc 0.5
"""
import argparse, os, random, subprocess, sys, tempfile

ANH = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")
VIDEO = (".mp4", ".mov", ".mkv", ".webm", ".avi")


def chay(args):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        sys.stderr.write(p.stderr[-2000:] + "\n")
        raise SystemExit(f"ffmpeg lỗi ({p.returncode}): {' '.join(args[:4])}…")
    return p


def chuoi_loc(m, video=False, W=1920, H=1080, seed=0):
    """Dựng filtergraph ffmpeg theo mức m (0..1). Đầu vào [0:v], ra [v]."""
    rnd = random.Random(seed)
    down = 1 - 0.30 * m           # hạ rồi nâng lại -> mất nét, thô như bản scan
    blur = round(0.9 * m, 3)      # mờ nhẹ
    sat = round(1 - 0.55 * m, 3)  # phai màu
    rm = round(0.10 * m, 3)       # ngả đỏ vùng trung (sepia)
    bm = round(-0.10 * m, 3)      # bớt xanh vùng trung
    blk = round(0.06 * m, 3)      # nâng đen (bạc màu)
    wht = round(1 - 0.09 * m, 3)  # hạ trắng
    grain = round(22 * m, 1)      # hạt phim
    vig = round(3.14159 / (6 - 1.6 * m), 4)  # m lớn -> tối góc hơn
    halo = round(0.28 * m, 3)     # quầng sáng vùng sáng

    f = (
        f"[0:v]scale=iw*{down}:ih*{down}:flags=bilinear,"
        f"scale={W}:{H}:flags=bilinear,"
        f"hue=s={sat},"
        f"colorbalance=rm={rm}:bm={bm}:rh={round(rm*0.6,3)}:bh={round(bm*0.6,3)},"
        f"curves=all='0/{blk} 0.5/0.5 1/{wht}',"
        f"gblur=sigma={blur},"
        "split=2[base][hl];"
        "[hl]gblur=sigma=16:steps=2,curves=all='0/0 0.55/0 1/1'[glow];"
        f"[base][glow]blend=all_mode=screen:all_opacity={halo}[lit];"
        f"[lit]noise=alls={grain}:allf={'t+u' if video else 'u'},"
        f"vignette=angle={vig}[g0];"
    )
    # lớp bụi + xước dọc, chồng kiểu screen
    dust_op = round(0.10 * m, 3)
    f += (
        f"color=c=black:s={W}x{H}{':d=1' if not video else ''}[dk];"
        f"[dk]geq=lum='255*gt(random({seed+1}),{round(1-0.0006*m,5)})':cb=128:cr=128[dust];"
        f"[g0][dust]blend=all_mode=screen:all_opacity={dust_op}[g1];"
    )
    # 2-4 vệt xước dọc mảnh ở vị trí ngẫu nhiên
    n_scr = rnd.randint(2, 4)
    last = "g1"
    for i in range(n_scr):
        x = rnd.randint(int(W * 0.08), int(W * 0.92))
        w = rnd.choice([1, 1, 2])
        a = round(rnd.uniform(0.04, 0.12) * (0.5 + m), 3)
        out = f"s{i}"
        f += (f"[{last}]drawbox=x={x}:y=0:w={w}:h={H}:"
              f"color=white@{a}:t=fill[{out}];")
        last = out
    f += f"[{last}]format={'yuv420p' if video else 'rgb24'}[v]"
    return f


def loc_anh(src, dst, m, seed):
    """Lọc một ảnh: ffmpeg -> JPEG, rồi nén JPEG lần hai (compound artifact)."""
    q1 = max(2, round(3 + 8 * m))     # q lần 1
    q2 = max(2, round(2 + 7 * m))     # q lần 2
    fg = chuoi_loc(m, video=False, seed=seed)
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    tmp.close()
    try:
        chay(["ffmpeg", "-y", "-i", src, "-filter_complex", fg,
               "-map", "[v]", "-q:v", str(q1), "-frames:v", "1", tmp.name])
        # nén JPEG lần hai
        chay(["ffmpeg", "-y", "-i", tmp.name, "-q:v", str(q2), dst])
    finally:
        os.unlink(tmp.name)


def loc_video(src, dst, m, seed):
    fg = chuoi_loc(m, video=True, seed=seed)
    crf = max(18, round(20 + 10 * m))
    chay(["ffmpeg", "-y", "-i", src, "-filter_complex", fg, "-map", "[v]",
           "-c:v", "libx264", "-crf", str(crf), "-pix_fmt", "yuv420p",
           "-an", dst])


def main():
    ap = argparse.ArgumentParser(description="Hoá cũ ảnh/clip giống tư liệu 1905")
    ap.add_argument("input", nargs="?", help="ảnh hoặc clip; bỏ trống nếu dùng --goc")
    ap.add_argument("--goc", help="thư mục goc/ : lọc mọi ảnh ra thư mục cha")
    ap.add_argument("--out", help="đường ra (một file)")
    ap.add_argument("--muc", type=float, default=0.5, help="mức 0..1 (mặc định 0.5)")
    ap.add_argument("--video", action="store_true", help="xử lý như clip")
    ap.add_argument("--seed", type=int, default=1905)
    a = ap.parse_args()
    m = max(0.0, min(1.0, a.muc))

    if a.goc:
        goc = os.path.abspath(a.goc)
        ra = os.path.dirname(goc) if os.path.basename(goc) == "goc" else goc + "-loc"
        os.makedirs(ra, exist_ok=True)
        files = sorted(f for f in os.listdir(goc) if f.lower().endswith(ANH))
        if not files:
            raise SystemExit(f"Không có ảnh trong {goc}")
        for i, f in enumerate(files):
            src = os.path.join(goc, f)
            dst = os.path.join(ra, os.path.splitext(f)[0] + ".jpg")
            loc_anh(src, dst, m, a.seed + i)
            print(f"  [{i+1}/{len(files)}] {f} -> {os.path.relpath(dst)}")
        print(f"Xong {len(files)} ảnh (mức {m}) -> {ra}")
        return

    if not a.input:
        raise SystemExit("Cần <input> hoặc --goc")
    ext = os.path.splitext(a.input)[1].lower()
    is_video = a.video or ext in VIDEO
    out = a.out or (os.path.splitext(a.input)[0] + ("-cu.mp4" if is_video else "-cu.jpg"))
    (loc_video if is_video else loc_anh)(a.input, out, m, a.seed)
    print(f"Xong (mức {m}) -> {out}")


if __name__ == "__main__":
    main()
