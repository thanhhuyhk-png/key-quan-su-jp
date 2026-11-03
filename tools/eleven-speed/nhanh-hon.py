"""Tăng nhịp đọc giữ nguyên cao độ: kéo nhanh từng câu voice8 bằng rubberband (giữ formant),
thu khoảng nghỉ theo cùng tỉ lệ (trừ khoảng mở đầu và khoảng thẻ thư khen trước L27).
python nhanh-hon.py <audio_dir> <tempo> <out_dir>"""
import json, subprocess, sys, os
A, tempo, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
os.makedirs(out, exist_ok=True)
plan = json.load(open(os.path.join(A, "voice-plan.json")))
seg = {s["id"]: s for s in json.load(open(os.path.join(A, "voice8/seg.json")))}
KEEP = {"L27"}  # khoảng nghỉ cho thẻ văn bản, giữ nguyên
rows, t = [], None
for p in plan:
    s = seg[p["id"]]; f = os.path.join(out, p["id"] + ".wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(A, s["file"]),
                    "-af", f"rubberband=tempo={tempo}:pitch=1:formant=preserved:transients=smooth:detector=soft:window=standard:smoothing=on", f], check=True)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
    gap = p["gap_before"] if p["id"] in KEEP else p["gap_before"] / tempo
    t = 2.65 if t is None else t + gap
    rows.append(dict(id=p["id"], file=f, start=round(t, 3), dur=round(dur, 3),
                     speech_start=round(t + s["lead"] / tempo, 3), speech_end=round(t + dur - s["tail_after_speech"] / tempo, 3)))
    t += dur
json.dump(rows, open(os.path.join(out, "plan.json"), "w"), indent=1)
inp, flt = [], []
for i, r in enumerate(rows):
    inp += ["-i", r["file"]]; ms = int(round(r["start"] * 1000)); flt.append(f"[{i}]adelay={ms}|{ms}[a{i}]")
fc = ";".join(flt) + ";" + "".join(f"[a{i}]" for i in range(len(rows))) + f"amix=inputs={len(rows)}:normalize=0,apad=pad_dur=1.0,loudnorm=I=-18:TP=-2:LRA=11[o]"
track = os.path.join(A, f"voice-track-v7-nhanh{tempo}.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", *inp, "-filter_complex", fc, "-map", "[o]", "-ar", "48000", track], check=True)
print(track, "end %.2f s" % t)
