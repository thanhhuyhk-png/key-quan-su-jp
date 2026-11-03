"""Ghép các câu giọng đã chọn thành một đường giọng theo khoảng nghỉ, xuất mốc thời gian từng câu.

Dùng: python build-voice-track.py <voice_dir> <plan.json> <out.wav> <timeline.json>
plan.json: [{"id":"L01","file":"L01-...-t0.wav","gap_before":2.0}, ...]  (gap_before: giây im trước câu)
"""
import json, subprocess, sys

vdir, plan_p, out_wav, tl_p = sys.argv[1:5]
plan = json.load(open(plan_p, encoding="utf-8"))
t, parts, tl = 0.0, [], []
for p in plan:
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                              f"{vdir}/{p['file']}"], capture_output=True, text=True).stdout)
    t += p["gap_before"]
    tl.append({"id": p["id"], "start": round(t, 3), "end": round(t + d, 3)})
    parts.append((p["gap_before"], f"{vdir}/{p['file']}"))
    t += d
args, filt = [], []
for i, (gap, f) in enumerate(parts):
    args += ["-i", f]
    filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,adelay={int(gap*1000)}[a{i}]")
filt.append("".join(f"[a{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", ";".join(filt), "-map", "[out]", out_wav], check=True)
json.dump({"total": round(t + 2.0, 3), "lines": tl}, open(tl_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"tong {t:.2f}s, {len(tl)} cau")
