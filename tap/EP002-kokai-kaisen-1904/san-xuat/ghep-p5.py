# -*- coding: utf-8 -*-
"""
ghep-p5.py (EP002) — Ghép hình thân phim (hinh/p5/Sxxx.mp4) + giọng v2 (+ nhạc/SFX nếu có) + trailer 10 s đầu.

  python -I -X utf8 ghep-p5.py [--am <wav đã trộn>] [--ra <mp4>]
Không có --am: dùng giọng v2 chuẩn hoá -16 LUFS (bản xem nhịp hình, chưa có nhạc/tiếng động).
Kiểm: số khung từng cảnh (đúng round(t1·24)−round(t0·24)), tổng khung, thiếu cảnh thì dừng.
"""
import json, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
REPO = next(p for p in GOC.parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO / "tools"))
from cau_hinh import duong  # noqa: E402

OUT = duong("output") / "261113-kokai-kaisen-1904"
P5 = OUT / "hinh" / "p5"
PV = OUT / "preview"
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))
FPS = 24


def sh(args):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args, capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        sys.exit(r.stderr[-600:])


def frames(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return int(r.stdout.strip().strip(","))


def main():
    a = sys.argv[1:]
    am = Path(a[a.index("--am") + 1]) if "--am" in a else None
    ra = Path(a[a.index("--ra") + 1]) if "--ra" in a else PV / "p5-day-du.mp4"
    PV.mkdir(exist_ok=True)
    thieu, lech = [], []
    tong = 0
    ds = []
    for c in PC["canh"]:
        f = P5 / f"{c['id']}.mp4"
        exp = round(c["t1"] * FPS) - round(c["t0"] * FPS)
        if not f.exists():
            thieu.append(c["id"])
            continue
        ds.append(f)
        tong += exp
    if thieu:
        sys.exit(f"Thiếu {len(thieu)} cảnh: {thieu[:12]}…")
    print(f"{len(ds)} cảnh, tổng khung kỳ vọng {tong} ({tong / FPS:.1f} s)")
    if "--kiem-khung" in a:
        for c, f in zip(PC["canh"], ds):
            exp = round(c["t1"] * FPS) - round(c["t0"] * FPS)
            g = frames(f)
            if g != exp:
                lech.append((c["id"], exp, g))
        print("lệch khung:", lech or "không")
        if lech:
            sys.exit(1)
    lst = P5.parent / "p5-list.txt"
    lst.write_text("\n".join(f"file 'p5/{f.name}'" for f in ds) + "\n", encoding="utf-8")
    body = PV / "p5-hinh.mp4"
    sh(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(body)])
    voice = OUT / "giong" / "giong-v2.wav"
    dur = tong / FPS
    if am:
        ain = ["-i", str(am)]
        af = []
    else:
        ain = ["-i", str(voice)]
        af = ["-af", "aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-16:TP=-2"]
    than = PV / "p5-than.mp4"
    sh(["-i", str(body)] + ain + ["-map", "0:v", "-map", "1:a"] + af + ["-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-t", f"{dur:.3f}", str(than)])
    intro_n = PV / "intro-n.mp4"
    sh(["-i", str(OUT / "preview" / "lo0-intro.mp4"), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-af", "alimiter=limit=0.8:level=disabled", "-c:a", "aac", "-ar", "48000", "-ac", "2", str(intro_n)])
    cl = PV / "p5-c.txt"
    cl.write_text(f"file '{intro_n.name}'\nfile '{than.name}'\n", encoding="utf-8")
    sh(["-f", "concat", "-safe", "0", "-i", str(cl), "-c", "copy", str(ra)])
    print(f"Xong → {ra}  ({frames(ra)} khung)")


if __name__ == "__main__":
    main()
