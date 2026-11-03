"""Đo độ ổn định giọng theo từng cụm nói (tách ở khoảng lặng): độ to dB, cao độ trung vị Hz. python -I stability.py <wav...>"""
import sys, numpy as np, soundfile as sf, librosa
sys.stdout.reconfigure(encoding="utf-8")
for p in sys.argv[1:]:
    y, sr = sf.read(p, always_2d=True); y = y.mean(1).astype(np.float32)
    y = librosa.resample(y, orig_sr=sr, target_sr=16000); sr = 16000
    iv = librosa.effects.split(y, top_db=35, frame_length=1024, hop_length=256)
    iv = [(a, b) for a, b in iv if (b - a) / sr > 0.6]
    db, f0s = [], []
    for a, b in iv:
        s = y[a:b]; db.append(20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9))
        f0, vf, _ = librosa.pyin(s, fmin=60, fmax=300, sr=sr, frame_length=1024)
        f = f0[vf & ~np.isnan(f0)]; f0s.append(np.median(f) if len(f) else np.nan)
    db, f0s = np.array(db), np.array(f0s)
    jump = np.nanmax(np.abs(np.diff(db))) if len(db) > 1 else 0
    fj = np.nanmax(np.abs(np.diff(f0s))) if len(f0s) > 1 else 0
    print(f"{p.split('/')[-1]:40s} cụm={len(iv):3d} | độ to lệch chuẩn {db.std():4.1f} dB, nhảy lớn nhất {jump:4.1f} dB | cao độ TB {np.nanmean(f0s):5.0f} Hz, lệch chuẩn {np.nanstd(f0s):4.1f} Hz, nhảy lớn nhất {fj:4.0f} Hz")
