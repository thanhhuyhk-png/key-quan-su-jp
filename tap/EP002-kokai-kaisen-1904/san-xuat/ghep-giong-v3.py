# -*- coding: utf-8 -*-
"""
ghep-giong-v3.py (vá lần 2: câu 151–152 bị cụt, đọc lại khối khoi-3; nguồn giong-v2.wav + stt-v2) — EP002 P4: vá giong-v1.wav (hai lượt eleven_v4 bị nuốt câu 82–104 và 254–269) bằng hai khối đọc lại.

Cách làm (theo bài học EP001): so lời chuẩn với STT Deepgram của giong-v1 bằng difflib; lấy từ STT đầu/cuối của câu liền
trước và liền sau chỗ hỏng; cắt ở chỗ lặng nhất của khe (năng lượng nhỏ nhất); chèn khối đọc lại đã cắt lặng đầu/cuối,
đệm 0,35 s hai bên. Ghi giong-v2-tho.wav; cân −18 LUFS làm bằng ffmpeg ở bước sau.

Chạy: python -I -X utf8 ghep-giong-v2.py
"""
import json, sys
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import soundfile as sf

sys.stdout.reconfigure(encoding="utf-8")
G = Path("E:/Goha-JP/output/261113-kokai-kaisen-1904/giong")
KH = Path(__file__).resolve().parents[1] / "ke-hoach"
src = Path(__file__).resolve().parents[3] / "rieng" / "tools" / "so-loi-ja.py"
ns = {}
exec(src.read_text(encoding="utf-8").split("def main")[0], ns)
ch = ns["chuan_hoa"]

L = [l.strip() for l in (G / "loi-tts.txt").read_text(encoding="utf-8").split("\n") if l.strip()]
W = [w for w in json.loads((G / "stt-v2/giong-v2.words.json").read_text(encoding="utf-8"))["words"] if not w.get("audio_event")]
ref, own = "", []
for i, l in enumerate(L, 1):
    c = ch(l); ref += c; own += [i] * len(c)
stt, wid = "", []
for k, w in enumerate(W):
    c = ch(w["text"]); stt += c; wid += [k] * len(c)
sm = SequenceMatcher(None, ref, stt, autojunk=False)
tot = {}
for o in own:
    tot[o] = tot.get(o, 0) + 1
hit, first, last = {}, {}, {}
for a, b, n in sm.get_matching_blocks():
    for k in range(n):
        i, w = own[a + k], wid[b + k]
        hit[i] = hit.get(i, 0) + 1
        first.setdefault(i, w); first[i] = min(first[i], w); last[i] = max(last.get(i, w), w)
ok = lambda i: hit.get(i, 0) / tot[i] >= 0.5
y, sr = sf.read(G / "giong-v2a.wav")
y = y if y.ndim == 1 else y.mean(1)
hop = int(sr * 0.005)
env = np.sqrt(np.convolve(y ** 2, np.ones(hop * 4) / (hop * 4), "same"))


def cat_giua(w_truoc, w_sau):
    """Điểm cắt (giây) = chỗ lặng nhất trong khe giữa từ STT w_truoc và w_sau."""
    a, b = W[w_truoc]["end_ms"] / 1000 + 0.03, W[w_sau]["start_ms"] / 1000 - 0.03
    if b <= a:
        return (a + b) / 2
    ia, ib = int(a * sr), int(b * sr)
    return (ia + int(np.argmin(env[ia:ib]))) / sr


# (câu hỏng đầu, cuối; khối đọc lại; tên)
VA = [(151, 152, "khoi-3")]
cuts = []
for a, b, ten in VA:
    truoc = max(i for i in range(1, a) if ok(i))     # câu tốt liền trước
    sau = b + 1  # câu liền sau khối (hai câu 151–152 cũ bị thay hết)
    # từ cuối của câu trước (chỉ tính câu ok) và từ đầu của câu sau
    t0 = cat_giua(last[truoc], last[truoc] + 1)
    t1 = cat_giua(first[sau] - 1, first[sau])  # first[sau]: từ STT đầu tiên khớp của câu sau
    cuts.append((t0, t1, ten, truoc, sau))
    print(f"{ten}: bỏ {t0:.2f}–{t1:.2f} s ({t1 - t0:.1f} s hỏng) giữa câu {truoc} và {sau}")

PAD = np.zeros(int(0.35 * sr))


def doc_lai(ten):
    z, s2 = sf.read(G / "doc-lai" / f"{ten}.wav")
    z = z if z.ndim == 1 else z.mean(1)
    e = np.sqrt(np.convolve(z ** 2, np.ones(hop * 4) / (hop * 4), "same"))
    on = np.where(e > 0.003)[0]
    z = z[max(on[0] - int(0.05 * s2), 0): on[-1] + int(0.08 * s2)]
    assert s2 == sr
    return np.concatenate([PAD, z, PAD])


out, pos = [], 0.0
for t0, t1, ten, _, _ in cuts:
    out.append(y[int(pos * sr): int(t0 * sr)])
    out.append(doc_lai(ten))
    pos = t1
out.append(y[int(pos * sr):])
res = np.concatenate(out)
sf.write(G / "giong-v2b-tho.wav", res, sr, subtype="PCM_16")
print(f"giong-v2b-tho.wav: {len(res) / sr:.2f} s")
