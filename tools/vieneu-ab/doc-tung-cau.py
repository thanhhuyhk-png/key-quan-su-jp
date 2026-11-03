"""Đọc từng câu bằng VieNeu (cùng một giọng tham chiếu), tự đọc lại câu nào bị cắt cụt đuôi.
Cụt = mẫu cuối của một chunk còn biên độ lớn rồi rơi thẳng xuống 0 (chunk dừng giữa âm).
python -I doc-tung-cau.py <script.txt (mỗi câu một dòng)> <voice> <out_dir> [dtype auto|float32] [--retries 5]"""
import sys, os, json, numpy as np
sys.stdout.reconfigure(encoding="utf-8")
from vieneu import Vieneu

src, voice, out = sys.argv[1], sys.argv[2], sys.argv[3]
dtype = sys.argv[4] if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else "auto"
retries = int(sys.argv[sys.argv.index("--retries") + 1]) if "--retries" in sys.argv else 5
lines = [l.strip() for l in open(src, encoding="utf-8") if l.strip()]
tts = Vieneu(dtype=dtype)
sr = tts.sample_rate
WIN = int(sr * 0.01)

def cut_points(w):
    """Chỗ một đoạn tiếng rơi thẳng vào chuỗi số 0 ≥ 50 ms mà 10 ms trước đó còn đỉnh > 0,02."""
    z = np.abs(w) < 1e-6
    e = np.diff(np.r_[0, z.astype(np.int8), 0]); st, en = np.where(e == 1)[0], np.where(e == -1)[0]
    bad = [s for s, t in zip(st, en) if t - s > sr * 0.05 and s > 0 and np.abs(w[max(0, s - WIN):s]).max() > 0.02]
    if np.abs(w[-WIN:]).max() > 0.02: bad.append(len(w))
    return bad

report = []
for i, text in enumerate(lines, 1):
    lid = f"L{i:02d}"
    best = None
    for k in range(retries + 1):
        w = tts.infer(text, voice=voice, show_progress=False)
        bad = cut_points(w)
        if best is None or len(bad) < len(best[1]): best = (w, bad, k + 1)
        if not bad: break
    w, bad, tries = best
    tts.save(w, os.path.join(out, f"{lid}.wav"))
    report.append({"id": lid, "text": text, "tries": tries, "cut": [round(b / sr, 2) for b in bad], "dur": round(len(w) / sr, 3)})
    print(f"{lid} lần {tries} {'CỤT ' + str(report[-1]['cut']) if bad else 'ok'} · {text[:50]}", flush=True)
json.dump(report, open(os.path.join(out, "doc-tung-cau.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
