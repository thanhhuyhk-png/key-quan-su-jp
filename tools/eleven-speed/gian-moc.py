"""Giãn mốc dựng theo đường giọng mới: nội suy tuyến tính từng khúc giữa mốc đầu/cuối lời của từng câu (cũ → mới).
Ra: mốc 33 cảnh (định dạng film_dbp --timing) + bản trộn mới (dời cue/bed/ease, bỏ cue gõ phím để lấy lại sau).
python gian-moc.py <out_dir_root> <new_plan.json> <warp_old.json> <old_edl.json> <old_mix.json> <tag>"""
import json, sys, os, numpy as np
R, newp, warpj, edlj, mixj, tag = sys.argv[1:7]
FPS = 24
old = list(json.load(open(warpj))["old"])
old[6] = 14.40  # mốc cuối L03 cũ ghi lệch (14,96 > đầu L04 14,51); lấy theo voice-timeline-v3
plan = json.load(open(newp))
tail = old[-1] - old[-2]                      # đuôi sau câu cuối (5,38 s) giữ nguyên
new = [0.0] + [v for p in plan for v in (p["speech_start"], p["speech_end"])] + [plan[-1]["speech_end"] + tail]
assert len(new) == len(old) and all(np.diff(old) > 0) and all(np.diff(new) > 0), "mốc không tăng dần"
warp = lambda t: float(np.interp(t, old, new))
# cảnh
edl = json.load(open(edlj)); acc, rows, prev = 0, [], 0
for s in edl:
    o0 = acc / FPS; acc += s["old_frames"]; o1 = acc / FPS
    f1 = int(round(warp(o1) * FPS)); rows.append(dict(scene=s["scene"], start_s=round(prev / FPS, 3), end_s=round(f1 / FPS, 3), frames=f1 - prev, old_frames=s["old_frames"])); prev = f1
json.dump(rows, open(os.path.join(R, "render", f"edl-{tag}-timing.json"), "w"), indent=1)
# trộn
m = json.load(open(mixj, encoding="utf-8"))
m["duration"] = round(new[-1], 3)
for b in m["music"]["beds"]:
    b["from"] = round(warp(b["from"]), 3); b["to"] = round(warp(b["to"]), 3)
    for e in b.get("ease", []): e["at"] = round(warp(e["at"]), 3)
m["cues"] = [dict(c, t=round(warp(c["t"]), 3)) for c in m["cues"] if not c["sound"].startswith("sfx-type/")]
json.dump(m, open(os.path.join(R, "audio", f"mix-{tag}-base.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(dict(old=old, new=new), open(os.path.join(R, "audio", f"warp-{tag}.json"), "w"), indent=1)
print("cảnh:", len(rows), "tổng", rows[-1]["end_s"], "s /", prev, "khung; cue giữ", len(m["cues"]))
