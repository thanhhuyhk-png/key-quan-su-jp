"""Đo đuôi từng cụm nói: thời gian tắt từ mức nói xuống -45 dB dưới đỉnh cụm (ms). Đuôi < 25 ms = nghi bị cắt cụt.
python -I tail.py <wav...>"""
import sys, numpy as np, soundfile as sf
sys.stdout.reconfigure(encoding="utf-8")
for p in sys.argv[1:]:
    y, sr = sf.read(p, always_2d=True); y = y.mean(1)
    hop = int(sr * 0.005); n = len(y) // hop
    env = 20 * np.log10(np.sqrt((y[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    floor = np.percentile(env, 5); speech = env > floor + 25
    # cụm nói: chuỗi speech, kết thúc khi có ≥ 300 ms không nói
    ends, i = [], 0
    while i < n:
        if speech[i]:
            j = i
            while j < n and (speech[j] or speech[j:j + 60].any()): j += 1
            seg = env[i:j]
            if j - i > 80:
                pk = np.percentile(seg, 90); k = j - 1
                # đếm từ khung cuối còn ≥ pk-12 dB đến khung ≤ pk-45 dB
                last_loud = i + np.where(seg >= pk - 12)[0][-1]
                m = last_loud
                while m < n and env[m] > pk - 45: m += 1
                ends.append(((m - last_loud) * 5, last_loud * hop / sr))
            i = j
        else: i += 1
    short = [(round(t, 1), d) for d, t in ends if d < 25]
    print(f"{p.split('/')[-1]:38s} cụm {len(ends):3d} · đuôi trung vị {np.median([d for d,_ in ends]):4.0f} ms · cụt (<25 ms): {len(short)} {short[:12]}")
