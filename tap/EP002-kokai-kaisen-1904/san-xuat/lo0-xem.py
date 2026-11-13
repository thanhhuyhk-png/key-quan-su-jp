# -*- coding: utf-8 -*-
"""
lo0-xem.py — bản xem Lô 0 EP002: trailer 10 s (âm trailer-am.wav) + 開幕 S001–S024 (giọng v2 + nhạc nền hạ khi có giọng).
Chưa có tiếng động (SFX) vì chờ duyệt mua; nhạc dùng lại bản có sẵn của EP001 (suno-ch3-1).
  python -I -X utf8 lo0-xem.py
Ra: <output>/preview/lo0-xem-v1.mp4
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
FPS = 24
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))["canh"]
LO0 = [c for c in PC if int(c["id"][1:]) <= 24]
DUR = round(LO0[-1]["t1"] * FPS) / FPS


def sh(a):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + a, capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        sys.exit(r.stderr[-800:])


lst = PV / "lo0-list.txt"
lst.write_text("\n".join(f"file '{(P5 / (c['id'] + '.mp4')).as_posix()}'" for c in LO0) + "\n", encoding="utf-8")
body = PV / "lo0-hinh.mp4"
sh(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(body)])
voice = OUT / "giong" / "giong-v2.wav"
nhac = duong("output") / "261111-nihonkai-kaisen-1905" / "nhac" / "suno-ch3-1.mp3"
am = PV / "lo0-am.wav"
fc = (f"[0:a]atrim=0:{DUR:.3f},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume=1.0[v];"
      f"[1:a]atrim=0:{DUR:.3f},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,volume=-19dB,afade=t=in:d=1.5,afade=t=out:st={DUR - 2.5:.2f}:d=2.5[m];"
      f"[v]asplit=2[v1][v2];[m][v2]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=450[md];"
      f"[v1][md]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5[o]")
sh(["-i", str(voice), "-i", str(nhac), "-filter_complex", fc, "-map", "[o]", "-ar", "48000", str(am)])
than = PV / "lo0-than.mp4"
sh(["-i", str(body), "-i", str(am), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-t", f"{DUR:.3f}", str(than)])
intro = PV / "lo0-intro.mp4"
sh(["-i", str(PV / "intro-v2.mp4"), "-i", str(PV / "trailer-am-D.wav"), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS),
    "-af", "aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-14:TP=-1.5", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-t", "10.0", str(intro)])
than2 = PV / "lo0-than2.mp4"
sh(["-i", str(than), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "256k", "-ar", "48000", str(than2)])
cl = PV / "lo0-c.txt"
cl.write_text(f"file '{intro.name}'\nfile '{than2.name}'\n", encoding="utf-8")
ra = PV / "lo0-xem-v1.mp4"
sh(["-f", "concat", "-safe", "0", "-i", str(cl), "-c", "copy", str(ra)])
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ra)], capture_output=True, text=True)
print(f"Xong → {ra}  ({float(r.stdout):.2f} s; trailer 10 s + 開幕 {DUR:.2f} s)")
