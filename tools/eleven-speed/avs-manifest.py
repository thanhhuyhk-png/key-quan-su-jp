"""Dựng lại edit_manifest.v2.json của tập DBP theo bản mới: cảnh theo edl, bản trộn master, giọng tách 29 câu,
nhạc/tiếng động/gõ phím làm lớp tham khảo (tắt tiếng) từ mix json. Giữ meta/ass/markers cũ, rev +1.
python avs-manifest.py <root> <edl.json> <mix.json> <voice_plan.json> <ep_name> <mix_label>"""
import json, sys, os, subprocess, math
R, edlj, mixj, planj, ep, label = sys.argv[1:7]
FPS = 24
F = lambda s: int(round(s * FPS))
dur_cache = {}
def dur(rel):
    if rel not in dur_cache:
        dur_cache[rel] = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(R, rel)]))
    return dur_cache[rel]
mp = os.path.join(R, "edit_manifest.v2.json"); m = json.load(open(mp, encoding="utf-8"))
edl = json.load(open(edlj)); mix = json.load(open(mixj, encoding="utf-8")); plan = json.load(open(planj))
total = sum(s["frames"] for s in edl)
v0, f = [], 0
for s in edl:
    v0.append(dict(id=s["scene"], kind="veo", src=f"render/scenes/{s['scene']}.mp4", t0_f=f, t1_f=f + s["frames"], in_f=0, out_f=s["frames"])); f += s["frames"]
keep = {t["id"]: t for t in m["tracks"]}
tracks = [dict(keep["v0"], clips=v0), keep["o1"], keep["o2"]]
mix_master = os.path.relpath(mixj, R).replace("\\", "/").replace(".json", "-master.wav")
tracks.append(dict(id="a_mix", kind="audio", name=label, clips=[dict(id="mix_0", kind="audio", src=mix_master, t0_f=0, t1_f=total, in_f=0, out_f=total, vol=1)]))
vo = []
for p in plan:
    src = p["file"] if p["file"].startswith("audio/") else "audio/" + p["file"]
    n = F(p["dur"]); t0 = F(p["start"]); vo.append(dict(id=f"vo_{p['id']}", kind="audio", src=src, t0_f=t0, t1_f=t0 + n, in_f=0, out_f=n, vol=1))
tracks.append(dict(id="a_vo", kind="audio", name=f"Lời đọc ({len(vo)} câu)", voice=True, muted=True, clips=vo))
mv = mix["music"]["volume"]
for i, b in enumerate(mix["music"]["beds"]):
    src = "audio/" + b["file"]; t0, t1 = F(b["from"]), F(b["to"]); L = t1 - t0; d = F(dur(src))
    c = dict(id=f"bed_{i}", kind="audio", src=src, t0_f=t0, t1_f=t1, in_f=0, out_f=min(L, d) if not b.get("loop") else L, vol=round(mv * b.get("volume", 1), 3))
    if not b.get("loop") and d < L: c["t1_f"] = t0 + d
    tracks.append(dict(id=f"a1_{i}", kind="audio", name=f"Nhạc + nền {i+1}", muted=True, clips=[c]))
lanes, ends = [], []
go = []
for i, c in enumerate(sorted(mix["cues"], key=lambda c: c["t"])):
    src = "audio/" + c["sound"]; d = dur(src); L = c.get("cut", d); L = min(L, d)
    t = c["t"] - (L if c.get("align") == "end" else 0); t0 = max(0, F(t)); n = max(1, F(L))
    clip = dict(id=f"cue_{i:03d}", kind="audio", src=src, t0_f=t0, t1_f=t0 + n, in_f=0, out_f=n, vol=round(10 ** (c.get("db", -16) / 20), 4))
    if c["sound"].startswith("sfx-type/"): go.append(clip); continue
    for k, e in enumerate(ends):
        if e <= t0: lanes[k].append(clip); ends[k] = t0 + n; break
    else: lanes.append([clip]); ends.append(t0 + n)
for k, cl in enumerate(lanes):
    tracks.append(dict(id=f"a_sfx_{k}", kind="audio", name=f"Tiếng động {k+1}", muted=True, clips=cl))
gl, ge = [], []
for clip in go:
    for k, e in enumerate(ge):
        if e <= clip["t0_f"]: gl[k].append(clip); ge[k] = clip["t1_f"]; break
    else: gl.append([clip]); ge.append(clip["t1_f"])
for k, cl in enumerate(gl):
    tracks.append(dict(id=f"a_go_{k}", kind="audio", name=f"Gõ máy chữ {k+1}", muted=True, clips=cl))
m["tracks"] = tracks; m["meta"]["duration_f"] = total; m["meta"]["ep"] = ep; m["rev"] = m["rev"] + 1
json.dump(m, open(mp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("rev", m["rev"], "track", len(tracks), "clip", sum(len(t.get("clips", [])) for t in tracks), "dài", total, "khung")
