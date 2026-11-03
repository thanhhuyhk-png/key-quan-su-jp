"""Cắt bản đọc cả bài thành từng câu theo mốc chữ STT. Điểm cắt = chỗ lặng nhất trong khe giữa hai câu,
mỗi câu giữ đuôi tự nhiên tới điểm cắt (không fade vào lời). python cat-cau.py <full.wav> <words.json> <script.txt> <out_dir>"""
import json, re, sys, os, difflib, unicodedata, numpy as np, soundfile as sf
wav, wj, st, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
norm = lambda w: unicodedata.normalize("NFC", re.sub(r"[^\w]", "", w.lower()))
lines = [l.strip() for l in open(st, encoding="utf-8") if l.strip() and not l.strip().startswith("[")]
lines = [re.sub(r"^\[[^\]]*\]\s*", "", l) for l in lines]
ref, owner = [], []
for i, l in enumerate(lines):
    for w in l.split():
        if norm(w): ref.append(norm(w)); owner.append(i)
W = [dict(text=w["text"], start=w["start_ms"] / 1000, end=w["end_ms"] / 1000) for w in json.load(open(wj, encoding="utf-8"))["words"] if not w.get("audio_event")]
hyp = [norm(w["text"]) for w in W]
sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False)
fi, la = {}, {}   # chỉ số từ STT khớp đầu/cuối mỗi câu (STT viết số bằng chữ số nên mép câu có thể không khớp)
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        li = owner[a + k]; fi.setdefault(li, b + k); la[li] = b + k
missing = [i for i in range(len(lines)) if i not in fi]
assert not missing, f"không khớp câu: {missing}"
# ranh câu i|i+1 = khe dài nhất giữa hai từ STT liền nhau trong đoạn [cuối-khớp(i), đầu-khớp(i+1)]
first, last = {0: W[0]["start"]}, {len(lines) - 1: W[-1]["end"]}
for i in range(len(lines) - 1):
    a, b = la[i], fi[i + 1]
    k = max(range(a, b), key=lambda j: W[j + 1]["start"] - W[j]["end"]) if b > a else a
    last[i], first[i + 1] = W[k]["end"], W[k + 1]["start"]
y, sr = sf.read(wav); y = y if y.ndim == 1 else y.mean(1)
hop = int(sr * 0.005); env = np.sqrt(np.convolve(y ** 2, np.ones(hop * 4) / (hop * 4), "same"))
cuts = [0]
for i in range(len(lines) - 1):
    a, b = last[i] + 0.06, first[i + 1] - 0.03
    if b <= a: c = (last[i] + first[i + 1]) / 2
    else:
        ia, ib = int(a * sr), int(b * sr); c = (ia + int(np.argmin(env[ia:ib]))) / sr
    cuts.append(c)
cuts.append(len(y) / sr)
seg = []
for i, l in enumerate(lines):
    a, b = cuts[i], cuts[i + 1]
    # bỏ khoảng lặng đầu: từ điểm cắt (lặng) tới mẫu đầu tiên vượt -45 dB, chừa 30 ms (mốc STT hay trễ hơn phụ âm đầu)
    ia, ib = int(a * sr), int(b * sr); loud = np.flatnonzero(np.abs(y[ia:ib]) > 10 ** (-45 / 20))
    a2 = max(a, (ia + (loud[0] if loud.size else 0)) / sr - 0.03)
    piece = y[int(a2 * sr):int(b * sr)]
    f = os.path.join(out, f"L{i+1:02d}.wav"); sf.write(f, piece, sr)
    seg.append(dict(id=f"L{i+1:02d}", file=f.replace("\\", "/"), dur=round(len(piece) / sr, 3), lead=round(first[i] - a2, 3),
                    tail_after_speech=round(b - last[i], 3), src_start=round(a2, 3), text=l))
json.dump(seg, open(os.path.join(out, "seg.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(seg), "câu; đuôi ngắn nhất %.2f s; khe ngắn nhất %.2f s" % (min(s["tail_after_speech"] for s in seg[:-1]), min(first[i+1]-last[i] for i in range(len(lines)-1))))
