"""Ghép L01–L29 theo khoảng nghỉ thiết kế (voice-plan.json: gap_before), L01 vào ở 2,65 s, loudnorm −18.
python ghep-giong.py <audio_dir> <thu_muc_cau> <out.wav>"""
import json, subprocess, sys, os
A, d, out = sys.argv[1], sys.argv[2], sys.argv[3]
plan = json.load(open(os.path.join(A, "voice-plan.json")))
seg = {s["id"]: s for s in json.load(open(os.path.join(d, "doc-tung-cau.json"), encoding="utf-8"))}
t, rows = None, []
for p in plan:
    s = seg[p["id"]]; t = 2.65 if t is None else t + p["gap_before"]
    rows.append(dict(id=p["id"], file=os.path.join(d, p["id"] + ".wav"), start=round(t, 3), dur=s["dur"])); t += s["dur"]
json.dump(rows, open(os.path.join(d, "plan.json"), "w"), indent=1)
inp, flt = [], []
for i, r in enumerate(rows):
    inp += ["-i", r["file"]]; ms = int(round(r["start"] * 1000)); flt.append(f"[{i}]adelay={ms}|{ms}[a{i}]")
fc = ";".join(flt) + ";" + "".join(f"[a{i}]" for i in range(len(rows))) + f"amix=inputs={len(rows)}:normalize=0,apad=pad_dur=1.0,loudnorm=I=-18:TP=-2:LRA=11[o]"
subprocess.run(["ffmpeg", "-y", "-v", "error", *inp, "-filter_complex", fc, "-map", "[o]", "-ar", "48000", out], check=True)
print("end %.2f s" % t)
