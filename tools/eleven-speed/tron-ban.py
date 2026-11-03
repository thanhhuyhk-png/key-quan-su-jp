"""Hoàn tất bản trộn: base mix + cue gõ phím lấy từ typing json mới + giọng mới → kit.py tron → master 2 lượt → mux.
python tron-ban.py <root> <tag> <voice_track_rel_audio> <picture.mp4> <out.mp4>"""
import json, subprocess, sys, os, random, re
R, tag, voice, pic, outmp4 = [os.path.abspath(x) if i != 1 and i != 2 else x for i, x in enumerate(sys.argv[1:6])]
A = os.path.join(R, "audio")
m = json.load(open(os.path.join(A, f"mix-{tag}-base.json"), encoding="utf-8")); m["voice"] = voice
rnd = random.Random(1954); keys = ["key1", "key2", "key3"]; n = 0
for s in ("S13", "S29"):
    for ev in json.load(open(os.path.join(R, "render", f"typing-{s}.json"), encoding="utf-8")):
        k = ev["kind"]; snd = "space" if k == "space" else ("bell" if k == "bell" else rnd.choice(keys))
        db = -22 if snd == "space" else (-18 if snd == "bell" else round(-21 + rnd.uniform(-2.5, 2.5), 1))
        m["cues"].append({"sound": f"sfx-type/{snd}.mp3", "t": round(ev["t"], 3), "db": db, "cut": 0.35 if snd != "bell" else 1.2}); n += 1
mj = os.path.join(A, f"mix-{tag}.json"); json.dump(m, open(mj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
raw = os.path.join(A, f"mix-{tag}.wav"); master = os.path.join(A, f"mix-{tag}-master.wav")
KIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit", "kit.py")
subprocess.run([sys.executable, "-I", "-X", "utf8", KIT, "tron", mj, "--out", raw, "--force"], check=True, cwd=A)
p1 = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
j = json.loads(re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", p1)[-1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,alimiter=limit=0.82:level=false")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-af", af, "-ar", "48000", master], check=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", pic, "-i", master, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k", "-shortest", outmp4], check=True)
print("gõ phím", n, "cue ·", outmp4)
