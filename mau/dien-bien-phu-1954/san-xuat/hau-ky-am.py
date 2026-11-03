"""Hậu kỳ âm v3 kiểu nhà đài: chuỗi plugin VST3 thật (FabFilter, Valhalla) qua pedalboard, bộ máy VST của Goha AVS.

Vào: các stem do `dung-am.py --tron` xuất ở <am>/<ten>-*.wav (48 kHz):
  giong (đã lùi intro) · nhac (lớp nền, chưa duck) · tieng-intro · tieng-kho · tieng-ngoai · tieng-ham.
Chuỗi:
  giọng: Pro-Q 3 (cắt dưới 75 Hz, bớt đục 280 Hz, rõ chữ 3,2 kHz, sáng 10 kHz) → Pro-DS (khử xì ≤ 3,5 dB) → Pro-C 2 Vocal
         2,5:1; không vang (giữ chữ rõ).
  nhạc: Pro-Q 3 khoét 2,5 kHz chừa chỗ cho chữ → duck sidechain theo đường bao giọng thật (−8 dB, nhả 0,45 s).
  tiếng: ngoài trời vang vào núi (Valhalla Room "Dark Space", 3,2 s, trễ 45 ms); hầm, hào bí và gần (Dark Room 0,7 s, cắt
         cao 5 kHz); tiếng giao diện có phòng nhỏ rất mỏng; intro khô (khoảng chân không cắt gọn).
  tổng: Pro-C 2 Bus 1,5:1 dán các lớp → Pro-L 2 đỉnh thật, tăng dần tới −14 LUFS, trần −3,5 dBTP (mã hoá AAC đẩy đỉnh lên 2–5 dB; dùng aac_mf 256k, xem ghep-hinh.py).
Ra: <ten>-master.wav và <ten>-stem-*.wav (để nghe soát từng lớp).

<vst_python> -X utf8 hau-ky-am.py --am <thư mục am> --ten mix-v3
"""
import sys
import argparse
import re
import subprocess
from pathlib import Path

import numpy as np
from pedalboard import Pedalboard, HighpassFilter, load_plugin
from pedalboard.io import AudioFile
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402

SR = 48000
VST = str(duong("vst3"))


def nap(ten: str, **ts):
    p = load_plugin(f"{VST}/{ten}.vst3")
    for k, v in ts.items():
        setattr(p, k, v)
    return p


def eq(*bang):
    """Pro-Q 3 với các dải (kiểu, tần số, gain, q)."""
    p = nap("FabFilter/FabFilter Pro-Q 3")
    for i, (kieu, f, g, q) in enumerate(bang, 1):
        setattr(p, f"band_{i}_used", "Used")
        setattr(p, f"band_{i}_shape", kieu)
        setattr(p, f"band_{i}_frequency", f)
        if kieu in ("Bell", "Low Shelf", "High Shelf"):
            setattr(p, f"band_{i}_gain", g)
        if kieu == "Low Cut":
            setattr(p, f"band_{i}_slope", "24 dB/oct")
        setattr(p, f"band_{i}_q", q)
    return p


def phong(kieu: str, giay: float, tre: float, cat_cao: float):
    return nap("ValhallaDSP/ValhallaRoom", type=kieu, decay=f"{giay:.2f} s ", predelay=tre, highcut=cat_cao, mix=100.0)


def doc(f: Path) -> np.ndarray:
    with AudioFile(str(f)) as a:
        assert a.samplerate == SR, (f, a.samplerate)
        x = a.read(a.frames)
    return np.vstack([x, x]) if x.shape[0] == 1 else x


def ghi(f: Path, x: np.ndarray) -> None:
    with AudioFile(str(f), "w", SR, x.shape[0], bit_depth=32) as a:
        a.write(x.astype(np.float32))


def chay(board, x: np.ndarray) -> np.ndarray:
    return board(x.astype(np.float32), SR, reset=True)


def db(v: float) -> float:
    return 10 ** (v / 20)


def lufs(f: Path) -> tuple[float, float]:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", err)[-1])


def duong_bao(v: np.ndarray, tan: float = 0.06, nha: float = 0.45) -> np.ndarray:
    """Mức 0..1 "đang có lời" theo đường bao RMS 20 ms của giọng (ngưỡng −42 dBFS), vào nhanh, nhả chậm."""
    m = np.abs(v).max(axis=0)
    n = int(0.02 * SR)
    k = len(m) // n
    r = np.sqrt((m[:k * n].reshape(k, n) ** 2).mean(axis=1))
    on = (r > db(-42)).astype(np.float32)
    a, b = 1 - np.exp(-0.02 / tan), 1 - np.exp(-0.02 / nha)
    e, out = 0.0, np.empty_like(on)
    for i, x in enumerate(on):
        e += (a if x > e else b) * (x - e)
        out[i] = e
    return np.interp(np.arange(v.shape[1]), np.arange(k) * n + n / 2, out).astype(np.float32)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--am", required=True)
    ap.add_argument("--ten", default="mix-v3")
    ap.add_argument("--duck", type=float, default=-8.0, help="nhạc hạ bao nhiêu dB dưới lời")
    o = ap.parse_args()
    am = Path(o.am)
    f = lambda k: am / f"{o.ten}-{k}.wav"
    giong, nhac = doc(f("giong")), doc(f("nhac"))
    tg = {b: doc(f(f"tieng-{b}")) for b in ("intro", "kho", "ngoai", "ham")}
    n = min([giong.shape[1], nhac.shape[1]] + [x.shape[1] for x in tg.values()])
    giong, nhac = giong[:, :n], nhac[:, :n]
    tg = {b: x[:, :n] for b, x in tg.items()}

    # giọng: một chuỗi cố định nhẹ cả phim, không vang (vang chỉ cho tiếng động; giữ chữ rõ cho STT và người xem);
    # khử xì tối đa 3,5 dB vì tiếng Việt nhiều s, x, ch, tr
    v = chay(Pedalboard([eq(("Low Cut", 75, 0, 0.7), ("Bell", 280, -2.5, 1.0), ("Bell", 3200, 2.0, 0.9), ("High Shelf", 10000, 1.5, 0.7)),
                         nap("FabFilter/FabFilter Pro-DS", mode="Single Vocal", threshold=-30.0, range=3.5),
                         nap("FabFilter/FabFilter Pro-C 2", style="Vocal", ratio="2.50:1", threshold=-24.0, knee=12.0, attack=5.0,
                             release=120.0, auto_gain=False)]), giong)
    # nhạc: khoét chỗ cho chữ rồi duck theo đường bao giọng
    m = chay(Pedalboard([eq(("Bell", 2500, -2.5, 0.8), ("Low Cut", 35, 0, 0.7))]), nhac)
    m *= db(o.duck) ** duong_bao(giong)[None, :]
    # tiếng theo bus không gian; đuôi vang hạ 9 dB khi có lời (sidechain theo giọng: đuôi vang 3,2 s phủ chữ "chèn" ở v3 nháp)
    co_loi = db(-9) ** duong_bao(giong, tan=0.03, nha=0.3)[None, :]
    ngoai = tg["ngoai"] + chay(Pedalboard([HighpassFilter(120), phong("Dark Space", 3.2, 45.0, 6000.0)]), tg["ngoai"]) * db(-7) * co_loi
    ham = chay(Pedalboard([eq(("High Cut", 5000, 0, 0.7))]), tg["ham"])
    ham = ham + chay(Pedalboard([phong("Dark Room", 0.7, 8.0, 3500.0)]), ham) * db(-6) * co_loi
    kho = tg["kho"] + chay(Pedalboard([phong("Medium Room", 0.4, 5.0, 7000.0)]), tg["kho"]) * db(-18)
    stem = {"giong": v, "nhac": m, "tieng": ngoai + ham + kho + tg["intro"]}
    for k, x in stem.items():
        ghi(f(f"stem-{k}"), x)
    tong = sum(stem.values())
    keo = nap("FabFilter/FabFilter Pro-C 2", style="Bus", ratio="1.50:1", threshold=-16.0, knee=18.0, attack=30.0, release=250.0,
              auto_gain=False)
    tong = chay(Pedalboard([keo]), tong)
    tho = f("tong-tho")
    ghi(tho, tong)
    # Pro-L 2: tăng gain tới −14 LUFS, trần −3,5 dBTP để sau AAC (aac_mf) còn ≤ −1 dBTP (lặp vì limiter ăn bớt độ to)
    i0, _ = lufs(tho)
    g = max(0.0, -14.0 - i0)
    ra = f("master")
    for _ in range(3):
        lim = nap("FabFilter/FabFilter Pro-L 2", style="Modern", true_peak_limiting=True, oversampling="4x", output_level=-3.5, gain=min(30.0, g))
        ghi(ra, chay(Pedalboard([lim]), tong * (db(g - 30) if g > 30 else 1)))
        i, tp = lufs(ra)
        print(f"Pro-L 2 gain {g:.2f} dB → {i:.2f} LUFS, đỉnh {tp:.2f} dBFS")
        if abs(i + 14) < 0.2:
            break
        g += -14 - i
    print(f"master → {ra}")


if __name__ == "__main__":
    main()
