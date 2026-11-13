# -*- coding: utf-8 -*-
"""than-sfx.py — SFX nhẹ cho thân phim: tick khi cắt cảnh (thẻ), whoosh khi vào bản đồ.
  python -I -X utf8 than-sfx.py --canh <scenes.json> --out <sfx.wav>
"""
import argparse, json
import numpy as np
import scipy.signal as sg
from scipy.io import wavfile
SR = 48000


def env(n, a, r):
    na = int(a*SR); nr = max(1, n-na)
    return np.concatenate([np.linspace(0, 1, na), np.linspace(1, 0, nr)])[:n]


def tick(f=2200, dur=0.05, amp=0.12):
    n = int(dur*SR); t = np.arange(n)/SR
    return np.sin(2*np.pi*f*t)*env(n, 0.001, dur)*amp


def whoosh(dur=0.35, amp=0.14):
    n = int(dur*SR); nz = np.random.randn(n)
    b, a = sg.butter(4, [300/(SR/2), 5000/(SR/2)], "band")
    return sg.lfilter(b, a, nz)*env(n, 0.05, dur*0.7)*amp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--canh", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    data = json.load(open(a.canh, encoding="utf-8"))
    canh = data["canh"]; het = data.get("het") or canh[-1]["t1"]
    N = int(het*SR)+SR; M = np.zeros((N, 2))

    def place(sig, t, pan=0.0):
        i = int(t*SR); n = min(len(sig), N-i)
        if n <= 0: return
        gl, gr = np.sqrt((1-pan)/2), np.sqrt((1+pan)/2)
        M[i:i+n, 0] += sig[:n]*gl; M[i:i+n, 1] += sig[:n]*gr
    for c in canh:
        if "ban-do" in c["nguon"]:
            place(whoosh(), c["t0"]-0.02, pan=np.random.uniform(-0.3, 0.3))
        else:
            place(tick(amp=0.1), c["t0"], pan=np.random.uniform(-0.2, 0.2))
    M = np.tanh(M*1.05)
    pk = np.max(np.abs(M))
    if pk > 0: M *= 0.9/pk
    wavfile.write(a.out, SR, M.astype(np.float32)[:int(het*SR)])
    print(f"SFX thân {het:.1f}s -> {a.out}")


if __name__ == "__main__":
    main()
