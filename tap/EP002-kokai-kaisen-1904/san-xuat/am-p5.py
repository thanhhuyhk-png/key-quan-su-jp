# -*- coding: utf-8 -*-
"""
am-p5.py — EP002 黄海海戦: trộn âm thân phim = giọng v2 + nhạc theo chương (hạ khi có giọng) + tiếng động đặt theo cảnh.
Chép từ EP001 JP, chỉnh: chương theo câu (kiem-phan-canh CHUONG), kho nhạc = 6 bản EP001 + 2 bản mới (suno-e2-*),
kho tiếng động = 22 tiếng EP001 + 8 tiếng mới (dong-ho-*, phao-xa, tau-quay-gap, den-pha-dem, ngu-loi-phong, hoang-hon-bien, phao-cong-thanh).
  python -I -X utf8 am-p5.py            # ra <output>/am/p5-tron.wav (chưa master) + cue.json
Rồi: kit.py master --am p5-tron.wav --ra p5-master.wav --lufs -14 --tp -1.5 ; ghep-p5.py --am p5-master.wav
"""
import json, random, subprocess, sys
from pathlib import Path
import numpy as np
import scipy.signal as sg

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
REPO = next(p for p in GOC.parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO / "tools"))
from cau_hinh import duong  # noqa: E402

OUT = duong("output") / "261113-kokai-kaisen-1904"
OUT1 = duong("output") / "261111-nihonkai-kaisen-1905"
SR = 48000
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))["canh"]
MOC = json.loads((GOC / "moc-cau.json").read_text(encoding="utf-8"))
HET = round(PC[-1]["t1"] * 24) / 24
random.seed(5)
rng = np.random.default_rng(5)

# chương theo câu (khớp kiem-phan-canh.py): tên, câu đầu
CH = [("mo", 1), ("ch1", 13), ("ch2", 60), ("ch3", 99), ("ch4", 131), ("ch5", 165), ("ch6", 214), ("ch7", 247), ("ket", 285)]
ranh = {}
for i, (ten, a) in enumerate(CH):
    t0 = MOC["cau"][a - 1][0]
    t1 = MOC["cau"][CH[i + 1][1] - 1][0] if i + 1 < len(CH) else HET
    ranh[ten] = (0.0 if i == 0 else t0, t1)

# đoạn nhạc: (tên, [các tệp nối], chương đầu, chương cuối, dB); tệp suno-e2-* ở EP002, còn lại dùng lại của EP001
DOAN = [
    ("mo", ["suno-ch3-1.mp3"], "mo", "mo", -21),
    ("c12", ["suno-ch12-1.mp3", "suno-ch12-2.mp3"], "ch1", "ch2", -22),
    ("c34", ["suno-ch3-2.mp3", "suno-ch67-1.mp3"], "ch3", "ch4", -22),
    ("c5", ["suno-e2-ch5-1.mp3", "suno-e2-ch5-2.mp3"], "ch5", "ch5", -19),
    ("c67", ["suno-e2-ch67-1.mp3", "suno-e2-ch67-2.mp3", "suno-e2-ch67-1.mp3"], "ch6", "ch7", -22),
    ("ket", ["suno-ket-1.mp3"], "ket", "ket", -21),
]


def nhac_tep(f):
    for d in (OUT / "nhac", OUT1 / "nhac"):
        if (d / f).exists():
            return d / f
    raise FileNotFoundError(f)


def doc(p, mono=False):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True)
    a = np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2).astype(np.float64)
    return a


def nen(a, n):
    out = np.zeros((n, 2))
    m = min(n, len(a))
    out[:m] = a[:m]
    return out


def vao(M, sig, t, g=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= len(M) or i + len(sig) <= 0:
        return
    s0 = max(0, -i)
    n = min(len(sig) - s0, len(M) - max(i, 0))
    gl, gr = np.sqrt((1 - pan) / 2) * 1.414, np.sqrt((1 + pan) / 2) * 1.414
    seg = sig[s0:s0 + n] * g
    M[max(i, 0):max(i, 0) + n, 0] += seg[:, 0] * gl
    M[max(i, 0):max(i, 0) + n, 1] += seg[:, 1] * gr


def mo_dan(a, tin=1.5, tout=2.5):
    a = a.copy()
    fi, fo = int(tin * SR), int(tout * SR)
    if fi:
        a[:fi] *= np.linspace(0, 1, fi)[:, None]
    if fo:
        a[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return a


def noi(files, dai):
    """nối các bản nhạc bằng crossfade 4 s tới khi đủ dài"""
    cf = int(4 * SR)
    cur = doc(nhac_tep(files[0]))
    for f in files[1:]:
        if len(cur) >= dai * SR + cf:
            break
        nx = doc(nhac_tep(f))
        w = np.linspace(0, 1, cf)[:, None]
        mix = cur[-cf:] * (1 - w) + nx[:cf] * w
        cur = np.concatenate([cur[:-cf], mix, nx[cf:]])
    return cur


# nếu tiếng mới chưa tải được (ai33 trả 503 khi đọc task), dùng tiếng gần nghĩa trong kho EP001
ALIAS = {"dong-ho-tick": "tick-the", "dong-ho-chuong": "chuong-tau", "phao-xa": "ngu-chuy-pao-lon", "tau-quay-gap": "dong-co-tau",
         "den-pha-dem": "whoosh-nhanh", "ngu-loi-phong": "whoosh-ban-do", "hoang-hon-bien": "gio-bien", "phao-cong-thanh": "ngu-chuy-pao-lon"}
DONG_HO = {"nichibotsu", "nichibotsu2", "shogo", "t13", "t13b", "t1730", "t1730b", "t1840", "t1840c", "t20"}
DEM_SO = {"chin0", "nokori", "rokoku", "dai1", "suirai", "kyori15", "sokudo", "kyori67", "hidan", "nido", "kikan"}
SO_SANH = {"kazu", "hikaku", "kazu2"}


def main():
    N = int(HET * SR)
    K = {}
    for d in (OUT1 / "sfx", OUT / "sfx"):
        for p in d.glob("*.mp3"):
            K[p.stem] = doc(p)

    # ---- giọng (loudnorm −16 bằng ffmpeg để bằng bản nháp)
    tmp = OUT / "am"
    tmp.mkdir(exist_ok=True)
    gv = tmp / "giong-16.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(OUT / "giong" / "giong-v2.wav"), "-af",
                    "aformat=sample_rates=48000:channel_layouts=stereo,loudnorm=I=-16:TP=-2", str(gv)], check=True)
    V = nen(doc(gv), N)

    # ---- đường hạ nhạc theo giọng
    env = np.abs(V).max(axis=1)
    b, a = sg.butter(2, 3.0 / (SR / 2))
    env = sg.filtfilt(b, a, env)
    thr = 0.02
    duck = 1.0 - 0.45 * np.clip(env / thr, 0, 1)

    # ---- nhạc
    NM = np.zeros((N, 2))
    for ten, files, c0, c1, db in DOAN:
        t0, t1 = ranh[c0][0], ranh[c1][1]
        dai = t1 - t0 + 3
        a = noi(files, dai)[: int(dai * SR)]
        a = mo_dan(a, 2.0, 3.0) * (10 ** (db / 20))
        vao(NM, a, max(0, t0 - 0.5), 1.0)
    NM *= duck[:, None]

    # ---- tiếng động
    SF = np.zeros((N, 2))
    cue = []

    def c(ten, t, db=-14, pan=None, dai=None, tin=0.0, tout=0.0):
        ten0 = ten
        if ten not in K and ALIAS.get(ten) in K:
            ten = ALIAS[ten]
        if ten not in K or t < 0 or t >= HET:
            return
        s = K[ten]
        if dai:
            s = s[: int(dai * SR)]
        if tin or tout:
            s = mo_dan(s, tin, tout)
        p = random.uniform(-0.4, 0.4) if pan is None else pan
        vao(SF, s, t, 10 ** (db / 20), p)
        cue.append({"t": round(t, 2), "tieng": ten0, "dung": ten, "db": db})

    ch_cua = lambda t: next(k for k, (a0, a1) in ranh.items() if a0 <= t < a1 + 1e-6)
    ban_do_dem = 0
    ch5_dem = 0
    senkai_dau = False
    for k, s in enumerate(PC):
        t0, t1 = s["t0"], s["t1"]
        ch = ch_cua(t0)
        kieu, ten = s["kieu"], s.get("ten", "")
        d = t1 - t0
        if kieu == "ban-do":
            ban_do_dem += 1
            c("whoosh-ban-do" if ban_do_dem % 2 else "whoosh-nhanh", t0 - 0.1, -17)
            if ten in ("koukai", "churitsu", "ulsan"):
                c("gio-bien", t0, -26, 0, dai=min(d + 0.5, 10), tin=0.6, tout=1.0)
            elif ten in ("ryojun",):
                if t0 > 1100:   # tháng 12: 28cm
                    c("phao-cong-thanh", t0 + 0.3, -17, dai=min(d, 3))
                    c("no-xa", t0 + 1.8, -20)
                else:
                    c("tau-song-bien", t0, -28, 0, dai=min(d + 0.5, 10), tin=0.6, tout=1.0)
            elif ten in ("kosen1", "tsuigeki", "kosen2", "sanran"):
                c("tau-song-bien", t0, -27, 0, dai=min(d + 0.5, 10), tin=0.6, tout=1.0)
                if ten == "kosen1":
                    c("phao-xa", t0 + 0.4, -18)
                if ten == "kosen2":
                    c("pao-loat", t0 + 0.2, -19)
            elif ten == "senkai":
                if t0 > 700 and not senkai_dau:
                    senkai_dau = True
                    c("tau-quay-gap", t0, -15, dai=min(d + 0.5, 4), tout=1.0)
                else:
                    c("tau-song-bien", t0, -27, 0, dai=min(d + 0.5, 10), tin=0.6, tout=1.0)
        elif kieu == "the":
            c("tick-the", t0, -15)
            if ten in DONG_HO:
                c("dong-ho-tick", t0 + 0.2, -22, dai=min(2.4, d))
                c("dong-ho-chuong", t0 + 1.2, -17 if ten in ("t1840", "t1840c", "t20") else -20)
            if ten in DEM_SO:
                c("dem-so", t0 + 0.15, -20, dai=min(2.6, d))
            if ten in SO_SANH:
                c("thud-so", t0 + 0.6, -15)
            if ten in ("chin0", "t1840", "nido"):
                c("thud-so", t0, -13)
            if ten in ("t1840", "t1840c", "t1730"):
                c("tim-dap", t0, -19, dai=min(4, d))
            if ten in ("t1730", "t13"):
                c("ngu-chuy-pao-lon", t0 + 0.2, -15)
            if ten in ("yoru",):
                c("suong-dem", t0, -24, 0, dai=min(d, 6), tin=0.6, tout=1.0)
        elif kieu == "anh":
            c("trang-giay" if k % 3 else "may-anh", t0, -20)
        elif kieu == "clip":
            ma = s["ten"]
            if ma == "V14":
                c("den-pha-dem", t0, -19, dai=min(d, 3))
            elif ma in ("V03", "V24"):
                c("hoang-hon-bien", t0, -24, 0, dai=min(d + 0.5, 6), tin=0.6, tout=1.0)
            elif ch in ("ch1", "ch2"):
                c("dong-co-tau", t0, -26, 0, dai=min(d + 0.5, 8), tin=0.5, tout=1.0)
        # trận chiến Ch5: pháo và nổ theo nhịp cảnh hình (không phải ban-do/the)
        if ch == "ch5" and kieu in ("anh", "clip"):
            ch5_dem += 1
            thu = ["ngu-chuy-pao-lon", "pao-loat", "dan-roi-nuoc", "no-xa", "no-gan"]
            c(thu[ch5_dem % len(thu)], t0 + 0.05, -15 if ch5_dem % 2 else -17)
        if ch == "ch7" and kieu == "clip" and k % 4 == 0:
            c("coi-tau", t0, -20, dai=min(3, d))
    # tiếng báo trước Ch5, mốc 18:40 và kết
    c("hoang-hot", ranh["ch5"][0] - 5.5, -19, 0)
    c("chuong-tau", ranh["ket"][0] + 0.5, -22, 0)

    # ---- trộn
    M = V + NM + SF
    pk = np.abs(M).max()
    print(f"đỉnh trước master {pk:.2f}; {len(cue)} cue ({len(cue) / (HET / 60):.1f}/phút)")
    if pk > 0.95:
        M *= 0.95 / pk
    wav = tmp / "p5-tron.wav"
    out = (M * 32767).astype(np.int16)
    import wave
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
    (tmp / "cue.json").write_text(json.dumps(cue, ensure_ascii=False), encoding="utf-8")
    print(wav)


if __name__ == "__main__":
    main()
