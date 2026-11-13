# -*- coding: utf-8 -*-
"""
trailer-am.py — Tổng hợp nhạc trailer + SFX 10 giây, đồng bộ beat sheet intro.
Không dùng asset ngoài (tổng hợp bằng numpy): drone nền, riser, braam/impact,
whoosh, tiếng biển/khói/pháo/lửa, boom tiêu đề. Ra WAV 48k stereo.
Nhạc/SFX cuối cùng của tập làm ở P6; đây là bản cho trailer để đánh giá.

  python -I -X utf8 trailer-am.py --out <trailer-am.wav>
"""
import argparse
import numpy as np
import scipy.signal as sg
from scipy.io import wavfile

SR = 48000
DUR = 10.0
N = int(SR * DUR)
rng = np.random.default_rng(1905)


def lp(x, fc, order=4):
    b, a = sg.butter(order, min(fc, SR / 2 - 1) / (SR / 2), "low")
    return sg.lfilter(b, a, x)


def hp(x, fc, order=4):
    b, a = sg.butter(order, max(fc, 5) / (SR / 2), "high")
    return sg.lfilter(b, a, x)


def bp(x, f1, f2, order=4):
    b, a = sg.butter(order, [max(f1, 5) / (SR / 2), min(f2, SR / 2 - 1) / (SR / 2)], "band")
    return sg.lfilter(b, a, x)


def env(n, a=0.01, r=0.3, hold=0.0):
    """attack-hold-release tuyến tính."""
    na, nh = int(a * SR), int(hold * SR)
    nr = n - na - nh
    if nr < 0:
        na = int(n * 0.1); nh = 0; nr = n - na
    e = np.concatenate([np.linspace(0, 1, na),
                        np.ones(max(0, nh)),
                        np.linspace(1, 0, max(1, nr))])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def tone(freq, dur, amp=1.0, f_end=None, kind="sine", a=0.005, r=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if f_end:
        ph = 2 * np.pi * np.cumsum(np.linspace(freq, f_end, n)) / SR
    else:
        ph = 2 * np.pi * freq * t
    if kind == "sine":
        w = np.sin(ph)
    elif kind == "saw":
        w = sg.sawtooth(ph)
    elif kind == "square":
        w = sg.square(ph)
    else:
        w = np.sin(ph)
    return w * env(n, a, r if r is not None else dur * 0.6) * amp


def noise(dur):
    return rng.standard_normal(int(dur * SR))


def place(master, sig, t, pan=0.0):
    """pan -1..1 (L..R)."""
    i = int(t * SR)
    n = min(len(sig), N - i)
    if n <= 0:
        return
    gl, gr = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    master[i:i + n, 0] += sig[:n] * gl
    master[i:i + n, 1] += sig[:n] * gr


def brass(dur=1.0, base=70, amp=0.5):
    """Braam kiểu kèn đồng: nhiều hoạ âm + quãng năm, thân trung, vào hơi chậm."""
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5 * t)
    s = np.zeros(n)
    for f, g in [(base, 1.0), (base * 1.5, 0.6), (base * 2, 0.5), (base * 3, 0.25)]:
        s += g * sg.sawtooth(2 * np.pi * f * np.cumsum(vib) / SR)
    s = bp(s, 110, 2600)                      # thân kèn, bỏ sub rền
    s += tone(base / 2, dur, 0.5, base * 0.45, "sine", 0.03, dur * 0.65)  # nền trầm vừa
    e = env(n, 0.045, dur * 0.7)
    return np.tanh(s * e * 1.3) * amp


def strings(dur, base=110, amp=0.3):
    """Lớp dây căng: saws lệch nhẹ + vibrato, băng thông trung, dâng dần."""
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t)
    s = np.zeros(n)
    for f, det in [(base, 1.0), (base * 1.5, 1.003), (base * 2, 0.997)]:
        s += sg.sawtooth(2 * np.pi * f * det * np.cumsum(vib) / SR)
    s = bp(s, 150, 2500)
    s *= np.linspace(0.2, 1.0, n) ** 1.5      # dâng
    return s * amp / 3


def taiko(dur=0.3, amp=0.4, f0=75):
    """Trống taiko: thân gỗ trầm, tắt nhanh (khác kick EDM)."""
    body = tone(f0, dur, 1.0, f0 * 0.55, "sine", 0.002, dur * 0.8)
    thump = lp(noise(dur), 220) * env(int(dur * SR), 0.001, dur * 0.6) * 0.5
    return np.tanh((body + thump) * 1.2) * amp


def boom(dur=0.9, f0=80, amp=0.6):
    s = tone(f0, dur, 1.0, f0 * 0.35, "sine", 0.002, dur * 0.7)
    cl = hp(noise(0.08), 1500) * env(int(0.08 * SR), 0.001, 0.07)
    out = s.copy()
    out[:len(cl)] += cl * 0.6
    return np.tanh(out * 1.4) * amp


def whoosh(dur=0.5, amp=0.35, up=True):
    nz = noise(dur)
    n = len(nz)
    fc = np.linspace(400, 5000, n) if up else np.linspace(5000, 400, n)
    # quét băng thông bằng tần số trung bình (xấp xỉ)
    out = bp(nz, 300, 6000) * env(n, 0.05, dur * 0.6)
    # AM nhẹ tạo cảm giác lướt
    out *= (0.6 + 0.4 * np.linspace(0, 1, n) if up else 0.6 + 0.4 * np.linspace(1, 0, n))
    return out * amp


def riser(dur=1.2, amp=0.3):
    nz = noise(dur)
    n = len(nz)
    out = hp(nz, 300)
    out *= np.linspace(0, 1, n) ** 2          # dâng
    out *= (1 + 0.3 * np.sin(2 * np.pi * np.linspace(0, 30, n)))  # rung
    return out * amp


def ping(freq=800, dur=1.0, amp=0.25):
    return tone(freq, dur, amp, kind="sine", a=0.001, r=dur * 0.95)


def sea(dur, amp=0.22):
    nz = lp(noise(dur), 1200)
    n = len(nz)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * 0.6 * np.arange(n) / SR)  # sóng vỗ
    return nz * swell * env(n, 0.1, 0.3) * amp


def fire(dur, amp=0.3):
    base = lp(noise(dur), 900)
    n = len(base)
    flick = 0.6 + 0.4 * rng.standard_normal(n)
    flick = lp(flick, 25)
    crackle = hp(noise(dur), 2500)
    crmask = (rng.random(n) > 0.995).astype(float)
    crackle = crackle * lp(crmask, 400) * 3
    return (base * flick + crackle * 0.5) * env(n, 0.05, 0.25) * amp


def steam(dur, amp=0.18):
    rum = lp(noise(dur), 300)
    n = len(rum)
    chug = 0.7 + 0.3 * sg.square(2 * np.pi * 3.2 * np.arange(n) / SR)  # nhịp máy
    hiss = hp(noise(dur), 4000) * 0.15
    return (rum * chug + hiss) * env(n, 0.08, 0.25) * amp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sfx-only", action="store_true",
                    help="chỉ SFX (bỏ nhạc tổng hợp) để chồng lên nền nhạc Suno")
    a = ap.parse_args()
    sfx = a.sfx_only
    M = np.zeros((N, 2), dtype=np.float64)

    if not sfx:
        # DRONE nền trầm cả bài (sine + lọc thấp), dâng dần, hụt sau tiêu đề
        dr = lp(tone(41, DUR, 0.5, kind="sine", a=0.3, r=0.5)
                + tone(55, DUR, 0.3, kind="sine", a=0.3, r=0.5), 180)
        g = np.interp(np.arange(N) / SR, [0, 6.4, 7.0, 7.42, 10], [0.25, 0.8, 0.9, 0.5, 0.3])
        dr *= g
        M[:, 0] += dr; M[:, 1] += dr
        # Lớp DÂY căng dâng 4.1 -> 7.3 (cinematic, không EDM)
        place(M, strings(3.2, 110, 0.32), 4.1)

    # 0.0 black: sub rumble dâng
    place(M, lp(noise(0.9), 120) * np.linspace(0, 1, int(0.9 * SR)) ** 2 * 0.4, 0.0)
    # 0.62 sea: braam kèn đồng + biển (swell ngược dẫn vào)
    place(M, whoosh(0.35, 0.28, up=False), 0.32)
    if not sfx:
        place(M, brass(1.0, 55, 0.5), 0.62)
    place(M, sea(1.2, 0.22), 0.62)
    # 1.83 line: whoosh + hơi nước/máy
    place(M, whoosh(0.5, 0.26), 1.73)
    place(M, steam(1.2, 0.2), 1.83)
    # 3.04 guns: 2 cú pháo
    place(M, boom(0.9, 80, 0.6), 3.02, pan=-0.2)
    place(M, boom(0.7, 95, 0.5), 3.55, pan=0.25)
    # 4.17 route: riser + sonar ping (+ taiko dồn nếu không có Suno)
    place(M, riser(1.2, 0.26), 4.1)
    place(M, ping(760, 1.1, 0.18), 4.17)
    if not sfx:
        for tb, g2 in [(4.17, 0.30), (4.9, 0.32), (5.5, 0.34), (6.0, 0.36), (6.4, 0.40)]:
            place(M, taiko(0.3, g2, 72), tb)
        # 5.37 tjifa: dây căng cao (pad tonal — chỉ khi không có Suno)
        place(M, bp(tone(330, 1.0, 0.5, kind="saw", a=0.2, r=0.4), 250, 2200) * 0.22, 5.37)
    # 5.75 ping kim loại khi T字 hiện
    place(M, ping(1200, 0.8, 0.2), 5.75)
    # 6.4 fire: roar (+ braam cao trào nếu không có Suno)
    place(M, fire(0.95, 0.32), 6.4)
    if not sfx:
        place(M, brass(0.85, 68, 0.42), 6.4)
    place(M, riser(0.9, 0.28), 6.4)

    if not sfx:
        # DIP trước tiêu đề cho cú boom nổ bật (chỉ bed tổng hợp; Suno tự có đà)
        duck = np.interp(np.arange(N) / SR, [7.08, 7.16, 7.36, 7.46], [1.0, 0.18, 0.15, 1.0])
        duck = np.where((np.arange(N) / SR >= 7.05) & (np.arange(N) / SR <= 7.5), duck, 1.0)
        M *= duck[:, None]
    # 7.42 title: BOOM lớn + sub drop (căn đúng cú cắt tiêu đề) — giữ cả khi có Suno
    place(M, boom(2.3, 60, 0.9), 7.42)
    place(M, tone(38, 2.3, 0.5, 30, "sine", 0.005, 2.1), 7.42)

    # giới hạn mềm + chuẩn hoá đỉnh
    M = np.tanh(M * 1.1)
    peak = np.max(np.abs(M))
    if peak > 0:
        M *= 0.97 / peak
    wavfile.write(a.out, SR, M.astype(np.float32))
    print(f"Xong nhạc+SFX 10s -> {a.out}  (đỉnh {20*np.log10(peak):.1f} dBFS trước chuẩn hoá)")


if __name__ == "__main__":
    main()
