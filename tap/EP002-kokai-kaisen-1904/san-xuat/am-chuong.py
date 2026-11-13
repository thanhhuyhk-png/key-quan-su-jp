# -*- coding: utf-8 -*-
"""
am-chuong.py — Ghép tiếng cho một chương đã dựng hình bằng dung-than.py:
cắt giọng đúng đoạn chương, SFX cắt cảnh (than-sfx.py), nhạc nền chương (nếu có), loudnorm -14 LUFS.

  python -I -X utf8 am-chuong.py --chuong Ch1 [--nhac <mp3/wav>] [--nhac-db -22]
Ra: <output>/.../preview/than-<chuong>.mp4
"""
import argparse, importlib.util, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("dt", HERE / "dung-than.py")
dt = importlib.util.module_from_spec(spec); spec.loader.exec_module(dt)
OUT = dt.OUT
THAN = OUT / "hinh" / "than"
FPS = 24

ap = argparse.ArgumentParser()
ap.add_argument("--chuong", required=True)
ap.add_argument("--nhac")
ap.add_argument("--nhac-db", type=float, default=-22)
a = ap.parse_args()
ma = a.chuong.lower()
_, c0, c1 = dt.CHUONG[a.chuong]
canh = json.load(open(HERE / "phan-canh.json", encoding="utf-8"))["canh"]
sel = [c for c in canh if c0 <= c["cau"][0] <= c1]
f0, f1 = round(sel[0]["t0"] * FPS), round(sel[-1]["t1"] * FPS)
t0, dur = f0 / FPS, (f1 - f0) / FPS
sh = [dict(c, t0=c["t0"] - t0, t1=c["t1"] - t0) for c in sel]
cj = THAN / f"{ma}-canh.json"
json.dump({"canh": sh, "het": dur}, open(cj, "w", encoding="utf-8"), ensure_ascii=False)
sfx = THAN / f"{ma}-sfx.wav"
subprocess.run([sys.executable, "-I", "-X", "utf8", str(HERE / "than-sfx.py"), "--canh", str(cj), "--out", str(sfx)], check=True)
giong = OUT / "giong" / "giong-v1.wav"
inp = ["-ss", f"{t0:.4f}", "-t", f"{dur:.4f}", "-i", str(giong), "-i", str(sfx)]
fc = ("[0:a]aformat=sample_rates=48000:channel_layouts=stereo[v];[1:a]volume=0.5[s];")
if a.nhac:
    inp += ["-stream_loop", "-1", "-i", a.nhac]
    fc += (f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={a.nhac_db}dB,"
           f"afade=t=in:d=1.5,afade=t=out:st={dur-2:.2f}:d=2[n];"
           "[v]asplit[v1][v2];[n][v2]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[nd];"
           "[v1][s][nd]amix=inputs=3:duration=first:normalize=0[m0];")
else:
    fc += "[v][s]amix=inputs=2:duration=first:normalize=0[m0];"
fc += f"[m0]atrim=0:{dur:.4f},loudnorm=I=-14:TP=-1.5:LRA=9[m]"
wav = THAN / f"{ma}-mix.wav"
subprocess.run(["ffmpeg", "-y", "-v", "error", *inp, "-filter_complex", fc, "-map", "[m]", "-ar", "48000", str(wav)], check=True)
out = OUT / "preview" / f"than-{ma}.mp4"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(THAN / f"{ma}.mp4"), "-i", str(wav), "-c:v", "copy",
                "-c:a", "aac", "-b:a", "256k", "-shortest", str(out)], check=True)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
tail = r[r.rfind("Summary"):]
print(out)
print([l.strip() for l in tail.splitlines() if "I:" in l or "Peak:" in l])
