"""Lô L6 (v2, 02/11/2026): bản trộn tập 1 theo sàn của bản Demo — intro súng đạn, mỗi cú cắt một tiếng, thẻ có tiếng gõ,
lớp nền chiến trường, tiếng lớn trong khe lặng thật, nhạc to hơn có cú đập.

Bài học v1 (user chê "SFX mờ nhạt"): v1 nén mọi tiếng động về −30 dB để STT đạt → cả phim nhạt (5 tiếng/phút).
v2: tiếng NGẮN trong lời ở −20…−26 dB (tiếng gõ, tiếng chụp, tiếng vụt: không lấp nguyên âm), tiếng LỚN chỉ trong khe lặng
đo được (am/khe-lang-v2.txt, giọng riêng −45 dB); STT bản trộn ≥ 97 % kiểm sau.
Mọi mốc phim = mốc giọng + INTRO_GIAY (intro.py); giọng đặt lùi bằng khoảng lặng đầu.

python -I -X utf8 dung-am.py [--den <giây phim>] [--tron] [--ten mix-v2]
  --den: chỉ trộn tới giây đó (bản 3 phút để user so) · --tron: chạy kit.py tron rồi master −14 LUFS (tăng cố định + alimiter)
"""
import argparse, importlib.util, json, random, re, subprocess, sys
from pathlib import Path

import numpy as np
import soundfile as sf

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))
import intro  # noqa: E402
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

AM = OUT / "261102-dbp-v3/am"
AM2 = OUT / "261102-dbp-v2/am"
NHAC = OUT / "261025-dien-bien-phu-mau/audio/music"
SFX = OUT / "261025-dien-bien-phu-mau/audio/sfx"
RVB = OUT / "261025-dien-bien-phu-mau/audio/sfx-rvb"
GO = OUT / "261025-dien-bien-phu-mau/audio/sfx-type"
FULL = OUT / "261030-dbp-ban-full/am/sfx"
THU = OUT / "261030-dbp-ban-thu-v2/am/sfx"
MOI = AM2 / "sfx"
MOI3 = AM / "sfx"  # v3: tổ hợp tiến công (pháo loạt, hô xung phong, hỏa tiễn, cờ)
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))
MOC = json.loads((GOC / "moc-cau.json").read_text(encoding="utf-8"))
L = MOC["lang"]
O = intro.INTRO_GIAY
KHE = [tuple(map(float, d.split())) for d in (AM / "khe-lang-v4.txt").read_text().split("\n") if d.strip()]
random.seed(54)

# Từ khoá cột Âm → (tệp, dB trong lời, dB trong khe, cắt tối đa s). Một cảnh nhận tối đa hai tiếng đầu tiên khớp.
TU_KHOA = [
    (r"NỔ LỚN", FULL / "no-hook.mp3", -20, -2, 3.0), (r"pháo nổ|pháo bắn|pháo dồn", FULL / "phao-ban.mp3", -22, -6, 2.0),
    (r"nổ xa|nổ rất xa|nổ trầm", MOI / "phao-xa.mp3", -22, -8, 2.5), (r"cao xạ", SFX / "phao-cao-xa.mp3", -22, -8, 1.5),
    (r"động cơ|máy bay", SFX / "may-bay-c47.mp3", -22, -12, 2.0), (r"thép gai|thép bật", FULL / "thep-gai.mp3", -22, -12, 1.5),
    (r"bao cát", FULL / "bao-cat.mp3", -22, -12, 1.5), (r"gỗ hòm|hòm", MOI / "hom-go.mp3", -20, -10, 1.5),
    (r"thùng", MOI / "thung-phuy.mp3", -20, -10, 1.5), (r"kẽo kẹt|xác", MOI / "xac-may-bay.mp3", -20, -12, 2.5),
    (r"xẻng", FULL / "xeng-dat.mp3", -22, -12, 1.5), (r"dây", THU / "day-cang-ket.mp3", -22, -12, 1.5),
    (r"bánh", THU / "banh-nghien-soi.mp3", -24, -14, 1.5), (r"lửa", FULL / "lua-chay.mp3", -24, -14, 2.0),
    (r"dế", FULL / "con-trung-dem.mp3", -24, -16, 3.0), (r"nan xe", FULL / "nan-xe-dap.mp3", -22, -14, 1.5),
    (r"đất rơi|đất lạo|đất cào", FULL / "dat-lao-xao.mp3", -22, -14, 1.5), (r"lá", FULL / "la-nguy-trang.mp3", -24, -16, 1.5),
    (r"súng máy", SFX / "sung-may.mp3", -22, -8, 1.5), (r"súng|hô", SFX / "sung-truong.mp3", -24, -10, 1.0),
    (r"nòng|kim loại", FULL / "khoa-nong.mp3", -22, -10, 1.0), (r"đạn va", FULL / "khoa-nong.mp3", -24, -12, 1.0),
    (r"bước chân", THU / "buoc-chan-doc.mp3", -24, -14, 1.5), (r"tán dù|dù chạm|kiện hàng", FULL / "bao-cat.mp3", -24, -14, 1.0),
    (r"điện đài|máy chữ", MOI / "dien-dai.mp3", -26, -16, 2.0),
]
# Tiếng cú cắt theo loại cảnh vào: (tệp, dB trong lời, dB trong khe)
CAT = {"anh": (MOI / "chup-anh.mp3", -16, -8), "karmen": (MOI / "vut.wav", -20, -10), "demo": (MOI / "vut.wav", -20, -10),
       "3d": (MOI / "vut.wav", -22, -12), "3d-moi": (MOI / "vut.wav", -22, -12), "map3d": (MOI / "vut.wav", -22, -12),
       "vnmap": (MOI / "giay-ban-do.mp3", -20, -10)}


def dung_the():
    spec = importlib.util.spec_from_file_location("dung_the", GOC / "dung-the.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def trong_khe(t, nua=0.04):
    """t (giờ giọng) nằm trong khe lặng đo được hoặc khoảng lặng có tên."""
    return any(a - nua <= t <= b for a, b in KHE) or any(a - nua <= t <= b for a, b in L.values())


def khe_sau(n):
    """Khe lặng ngay sau câu n (giây giọng): (đầu, cuối); None nếu câu n không có khe đo được (khe phải bắt đầu ≤ 1 s sau chữ cuối)."""
    t = MOC["cau"][n - 1][-1]
    return next(((a, b) for a, b in KHE if t < a <= t + 1.0), None)


def cat_san(tep, dai):
    """Cắt sẵn [0, dai] của tep, tắt gọn 15 ms (cut của bộ trộn mờ 0,3 s nên không tắt đúng mốc)."""
    ra = AM / "sfx-cat" / f"{Path(tep).stem}-{int(dai * 1000)}.wav"
    if not ra.exists():
        ra.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tep), "-t", f"{dai:.3f}", "-af", f"afade=t=out:st={max(0, dai - .015):.3f}:d=0.015",
                        "-ar", "48000", "-ac", "2", str(ra)], check=True)
    return ra.as_posix()


# Bus không gian (hau-ky-am.py): tiếng giao diện (gõ, vụt, chụp, giấy) khô; tiếng chiến trường theo cảnh: hầm/hào bí và gần,
# còn lại vang vào núi (thung lũng). Intro giữ khô để khoảng chân không cắt gọn.
GIAO_DIEN = re.compile(r"key\d|space|bell|go-|vut|chup-anh|giay-ban-do|cham-cat|dem-so|but-khoanh|lat-so|dong-dau|dien-dai|dap-tram")
HAM = re.compile(r"hầm|hào|đường hầm|lòng đất")


def bus_cua(tep, t_phim):
    if GIAO_DIEN.search(Path(tep).stem):
        return "kho"
    c = next((c for c in PC["canh"] if c["t0"] + O <= t_phim < c["t1"] + O), None)
    return "ham" if c and HAM.search(c["hinh"] + " " + c["am"]) else "ngoai"


def cue(ds, tep, t_giong, db, cut=None, hero=False, phim=False, bus=None):
    """Thêm tiếng ở mốc giọng t_giong (hoặc mốc phim nếu phim=True)."""
    o = dict(sound=Path(tep).as_posix(), t=round(t_giong if phim else t_giong + O, 3), db=db, align="start")
    if cut:
        o["cut"] = round(cut, 3)
    if hero:
        o["weight"] = "hero"
    o["bus"] = bus or bus_cua(tep, o["t"])
    ds.append(o)


# Đoạn lắng (sóng cảm xúc): câu giải thích, bối cảnh → tiếng thưa, nhỏ, nhạc êm. (câu đầu, câu cuối)
LANG_DOAN = [(25, 30), (34, 37), (60, 66), (96, 99), (107, 111), (144, 147), (187, 194), (212, 215), (219, 223)]


def lang_doan(t):
    return any(MOC["cau"][a - 1][0] - 0.2 <= t <= MOC["cau"][b - 1][-1] + 0.5 for a, b in LANG_DOAN)


def tieng_canh(ds):
    """Mỗi cú cắt một tiếng; tiếng theo cột Âm (tối đa hai). Đoạn lắng: nhỏ hơn 6 dB, không gõ nhãn."""
    for i, c in enumerate(PC["canh"]):
        t0 = c["t0"]
        khe = trong_khe(t0)
        bot = 6 if lang_doan(t0) else 0
        if i and c["kieu"] in CAT:
            tep, dl, dk = CAT[c["kieu"]]
            cue(ds, tep, t0 - (0.12 if "vut" in tep.name else 0), (dk if khe else dl) - bot, cut=1.0)
            if khe and not bot:
                cue(ds, MOI / "cham-cat.mp3", t0, -12, cut=0.8)
        # thẻ tên, nhãn ngày trên lớp chữ hiện ra: gõ phím ngắn (như nhãn của Demo), trong lời rất nhỏ
        if c["kieu"] != "the" and re.search(r'"[^"]+"', c["chu"]) and not bot:
            for k in range(6):
                t = t0 + 0.25 + k * 0.07
                cue(ds, GO / f"key{random.randint(1, 3)}.mp3", t, -16 if trong_khe(t) else -26)
        n = 0
        for mau, tep, dl, dk, cat in TU_KHOA:
            if n < 2 and re.search(mau, c["am"]):
                cue(ds, tep, t0 + 0.1 + 0.25 * n, (dk if khe else dl) - bot, cut=min(cat, c["t1"] - c["t0"] + 0.3), hero=khe and dk > -9 and not bot)
                n += 1


def _rng(seed):
    """mulberry32 y hệt template/lib/common.js rng (để lịch gõ trùng khung hình)."""
    a = seed & 0xFFFFFFFF
    im = lambda x, y: (x * y) & 0xFFFFFFFF

    def r():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = im(a ^ (a >> 15), 1 | a)
        t = ((t + im(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return r


def lich_go(s):
    """Lịch gõ của thẻ máy chữ, chép từ planTyping (template/cards/typewriter.js): [(giây trong thẻ, 'key'|'space'|'end')]."""
    r, out, prev = _rng(s.get("seed", 29)), [], 0.0
    for b in s["blocks"]:
        chars = []
        tu = b["text"].split(" ")
        for wi, w in enumerate(tu):
            chars += [(ch, "key") for ch in w]
            if wi < len(tu) - 1:
                chars.append((" ", "space"))
        units = [1 + 0.35 * (2 * r() - 1) for _ in chars]
        pause = []
        for i, (ch, _) in enumerate(chars):
            if i < len(chars) - 1 and ch in ",.;:!?…":
                pause.append((0.15 if ch == "," else 0.17) + r() * (0.05 if ch == "," else 0.08))
            else:
                pause.append(0.0)
        start = b["start"] if b.get("start") is not None else prev + b.get("gap", 0.25)
        U, P = sum(units), sum(pause)
        cmin, cmax = b.get("cps", [14, 20])
        dl = b.get("deadline")
        dl = s["duration"] + dl if dl is not None and dl < 0 else dl
        cps = min(max(U / max(0.1, dl - start - P) if dl else 17, cmin), cmax)
        t = start
        for i, (ch, k) in enumerate(chars):
            t += units[i] / cps
            out.append((t, k))
            r(); r(); r()
            t += pause[i]
        prev = t - pause[-1] + b.get("after", 0)
    out.append((max(x for x, _ in out), "end"))
    return out


_MAU = {}


def tron_go(ma, go, d):
    """Trộn các phím (giây trong thẻ, tên tiếng) thành am/sfx-cat/go-<mã>.wav dài d giây (48 kHz stereo)."""
    sr = 48000
    y = np.zeros((int(d * sr) + sr, 2))
    for t, ten in go:
        if ten not in _MAU:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(GO / f"{ten}.mp3"), "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"],
                                 capture_output=True, check=True).stdout
            _MAU[ten] = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
        x, i = _MAU[ten], int((t + (0.08 if ten == "bell" else 0)) * sr)
        n = min(len(x), len(y) - i)
        y[i:i + n] += x[:n]
    ra = AM / "sfx-cat" / f"go-{ma}.wav"
    ra.parent.mkdir(parents=True, exist_ok=True)
    sf.write(ra, y, sr)
    return ra


def tieng_the(ds):
    """Tiếng trong thẻ: gõ từng chữ (van-kien), đếm số, khoanh bút, mở sổ, đóng dấu, đập chương."""
    m = dung_the()
    for c in PC["canh"]:
        if c["kieu"] != "the" or c["id"] not in m.THE:
            continue
        s, _ = m.cau_hinh(c["id"])
        t0, d = round(c["t0"] * 24) / 24, s["duration"]
        typ = s["type"]
        if typ in ("so-lieu", "lich", "dong-thoi-gian", "hai-cot") and not trong_khe(t0):
            cue(ds, MOI / "giay-ban-do.mp3", t0 - 0.05, -20, cut=1.2)
        if typ == "may-chu":
            # gõ máy chữ: chỉ gõ thành tiếng trong khoảng thở (điểm nghỉ), chuông cuối; trộn sẵn thành một tệp mỗi thẻ
            # (gộp phím thành ít cue cho bản trộn gọn; bản cũ còn vướng giới hạn dòng lệnh Windows)
            go = [(t, "bell" if k == "end" else "space" if k == "space" else f"key{random.randint(1, 3)}")
                  for t, k in lich_go(s) if t < d and trong_khe(t0 + t)]
            if go:
                cue(ds, tron_go(c["id"], go, d), t0, -14)
        elif typ == "van-kien":
            for b in s.get("blocks", []):
                tu = b["text"].split()
                for k in range(len(tu)):
                    t = t0 + b.get("from", 0) + k * b.get("perWord", 0.06)
                    if t < t0 + d:
                        cue(ds, GO / f"key{random.randint(1, 3)}.mp3", t, -15 if trong_khe(t) else -24)
            cue(ds, MOI / "dien-dai.mp3", t0, -28, cut=min(2.0, d))
        elif typ == "so-lieu":
            for it in s.get("items", []):
                cue(ds, MOI / "dem-so.mp3", t0 + it.get("from", 0.3), -20, cut=it.get("dur", 1.2))
        elif typ == "lich":
            cue(ds, MOI / "but-khoanh.mp3", t0 + s.get("circleAt", 0.8), -18)
        elif typ == "hai-cot":
            for col in s.get("cols", []):
                if col.get("from", 0) >= 0:
                    cue(ds, MOI / "lat-so.mp3", t0 + col.get("from", 0), -18)
                for l in col.get("lines", []):
                    if l.get("at", -1) >= 0:
                        cue(ds, GO / f"key{random.randint(1, 3)}.mp3", t0 + l["at"], -20)
        elif typ == "dong-thoi-gian":
            for ln in s.get("lanes", []):
                cue(ds, MOI / "vut.wav", t0 + ln.get("activeFrom", 0.3), -22)
        elif typ == "hook":
            for j, l in enumerate(s.get("lines", [])):
                if l.get("shake", 0) >= 6:  # chỉ dòng chính có rung (dòng phụ không tiếng)
                    cue(ds, MOI / "dong-dau.mp3", t0 + l["at"], -8, hero=True)
                    cue(ds, MOI / "dap-tram.mp3", t0 + l["at"], -8, cut=1.6, hero=True)
        elif typ == "chuong":
            cue(ds, MOI / "dap-tram.mp3", t0 + s.get("hit", 0.1), -4, hero=True)
            cue(ds, RVB / "hit-chuong.wav", t0 + s.get("hit", 0.1), -8, hero=True)


def nhan_khe(ds):
    """Tiếng lớn vào khe lặng thật (đặt tay theo ý đồ từng câu)."""
    a, b = khe_sau(1)  # 195 tấn → hòm hàng đập xuống
    cue(ds, MOI / "hom-go.mp3", a, -1, cut=b - a + 0.4, hero=True)
    # tiếng nhấn tắt gọn trong khe (v3: STT bắt được đuôi nhấn −4…−8 dB tràn 0,5 s vào chữ đầu câu sau ở câu 24, 142, 181)
    gon = lambda k, cat: min(cat, k[1] - k[0] + 0.05)
    k = khe_sau(4)  # "không tới được tay người nhận" → pháo xa dội vách núi
    cue(ds, MOI / "phao-xa.mp3", k[0], -4, cut=gon(k, 1.6), hero=True)
    k = khe_sau(11)  # "Ba phát." → đạn rít + nổ
    a = k[0]
    cue(ds, MOI / "dan-xe-gio.mp3", a - 0.25, -12, cut=0.6)
    cue(ds, RVB / "no-lon-gan.wav", a + 0.05, -1, cut=gon(k, 1.4) - 0.05, hero=True)
    # "tập đoàn cứ điểm không còn nữa": câu 14 không có khe (câu 15 vào ngay) → đập trầm nhỏ ngay đầu chữ cuối, ngắn
    cue(ds, MOI / "dap-tram.mp3", MOC["cau"][13][-1], -14, cut=0.8)
    k = khe_sau(23)  # "chiều mười ba tháng ba" → loạt pháo xa
    cue(ds, RVB / "phao-loat-xa.wav", k[0], -6, cut=gon(k, 1.5), hero=True)
    # Tiêu đề phim (P1): nổ trầm + đập, rồi để nhạc
    p1 = L["P1"][0]
    cue(ds, FULL / "no-hook.mp3", p1 + 0.4, -8, cut=2.5, hero=True)  # tiếng đập do thẻ tiêu đề (tieng_the) đặt
    # Cả phim (02/11/2026): mỗi nhấn một khe đo được sau câu then chốt; câu không có khe thì bỏ (không đè lời)
    NHAN = [(92, MOI / "dap-tram.mp3", -12, 1.0),        # "giờ bắn ấy không đến"
            (113, MOI / "dap-tram.mp3", -12, 0.8),       # "chiều mười ba tháng ba" → vào chương 4
            (115, MOI / "dap-tram.mp3", -8, 0.9),        # "Chiến dịch Điện Biên Phủ bắt đầu." (loạt pháo ở H1 ngay trước)
            (117, MOI / "phao-xa.mp3", -6, 1.6),         # "Pháo binh Pháp bắn trả."
            (119, MOI / "phao-xa.mp3", -10, 1.2),        # đạn rơi vào trận địa nghi binh
            (122, RVB / "phao-loat-xa.wav", -8, 1.4),    # làm chủ Him Lam, Độc Lập
            (127, FULL / "phao-ban.mp3", -8, 1.2),       # pháo ta vẫn không bị khống chế
            (135, SFX / "may-bay-c47.mp3", -12, 1.6),    # đường băng không còn đón máy bay
            (141, RVB / "phao-loat-xa.wav", -8, 1.4),    # tiến công từng điểm cao
            (147, FULL / "xeng-dat.mp3", -12, 1.2),      # hào bò sát tới từng cứ điểm
            (158, SFX / "phao-cao-xa.mp3", -8, 1.4),     # đại đội cao xạ nổ súng
            (160, MOI / "dap-tram.mp3", -10, 1.0),       # hào cắt đôi sân bay
            (174, MOI / "dan-xe-gio.mp3", -8, 0.9),      # hỏa tiễn H6
            (180, RVB / "phao-loat-xa.wav", -4, 1.8),    # tổng công kích
            (182, MOI / "dap-tram.mp3", -12, 0.8),       # "Pháo lớn đã tới."
            (183, MOI / "dap-tram.mp3", -10, 0.8),       # "Bầu trời đã mất."
            (207, MOI / "dap-tram.mp3", -10, 1.0),       # "Giơ tay lên!"
            (208, MOI / "dong-dau.mp3", -12, 0.6)]       # Đờ Cát-xtơ-ri bị bắt
    for n, tep, db, cat in NHAN:
        k = khe_sau(n)
        if k:
            cue(ds, tep, k[0], db, cut=gon(k, cat), hero=db > -9)
    # Bộc phá A1 (khoảng lặng A1): rung trầm trước, nổ gần chồng lên tiếng nổ của cảnh (cột Âm "NỔ LỚN")
    a1 = L["A1"][0]
    cue(ds, FULL / "rung-tram.mp3", a1 - 0.05, -6, cut=3.0, hero=True)
    cue(ds, RVB / "no-lon-gan.wav", a1 + 0.05, -2, cut=2.4, hero=True)


def to_hop(ds, moc, lop):
    """Một tổ hợp nhiều lớp đặt từ mốc (giờ giọng): [(lệch s, tệp, dB, cắt s)]; lớp ≥ −6 dB tính là tiếng nhấn (hero)."""
    for lech, tep, db, cat in lop:
        cue(ds, tep, moc + lech, db, cut=cat, hero=db >= -6)


def khi_the(ds):
    """v3: các mốc phát động tiến công thành khoảng lặng có tên, mỗi mốc một tổ hợp 6–8 lớp (pháo bắn đi → đạn rít → nổ dồn
    vọng núi → rung trầm → đất rơi; súng máy, hô xung phong xa); Dốc Chuối kể bằng tiếng dây, bánh pháo; cờ 7/5 bay trong gió.
    Mọi tiếng lớn nằm trong khoảng lặng (lời ngừng); dưới lời chỉ còn đuôi, nhỏ."""
    w = lambda n, k: MOC["cau"][n - 1][k]
    h1, h2, h3, h4 = (L[k][0] for k in ("H1", "H2", "H3", "H4"))
    # H1 · 13/3 17:05, loạt pháo mở màn vào Him Lam (đỉnh lớn nhất trước A1)
    to_hop(ds, h1, [(0.0, MOI3 / "phao-loat-gan.mp3", -3, 2.6), (0.35, MOI3 / "dan-rit-nhieu.mp3", -11, 1.5),
                    (0.9, MOI3 / "no-don-xa.mp3", -4, 2.6), (1.0, FULL / "rung-tram.mp3", -6, 2.4),
                    (1.35, RVB / "no-lon-gan.wav", -3, 1.6), (1.9, MOI3 / "sung-may-gan.mp3", -13, 1.5),
                    (1.85, MOI3 / "ho-xung-phong-xa.mp3", -14, 1.6), (2.1, MOI3 / "dat-roi.mp3", -12, 1.3)])
    # H2 · 30/3 đợt hai: pháo loạt, súng máy, hô xa (cấp hai, ngắn hơn)
    to_hop(ds, h2, [(0.0, MOI3 / "phao-loat-gan.mp3", -5, 1.4), (0.3, MOI3 / "dan-rit-nhieu.mp3", -13, 1.0),
                    (0.6, MOI3 / "no-don-xa.mp3", -6, 1.5), (0.6, FULL / "rung-tram.mp3", -9, 1.4),
                    (0.5, MOI3 / "sung-may-gan.mp3", -10, 1.5), (0.5, MOI3 / "ho-xung-phong-xa.mp3", -12, 1.5)])
    # H3 · hỏa tiễn H6 rít qua đầu, nổ dày (sau câu 174)
    to_hop(ds, h3, [(-0.05, MOI3 / "hoa-tien-loat.mp3", -4, 1.5), (0.6, MOI3 / "no-don-xa.mp3", -7, 1.0),
                    (0.4, MOI3 / "sung-may-gan.mp3", -13, 1.0), (0.7, FULL / "rung-tram.mp3", -10, 1.0)])
    # H4 · hiệu lệnh toàn mặt trận ngay sau A1: rộng và dày, đỉnh thấp hơn A1 ~3 dB; nổ lô cốt khớp hình (≈0,85 s)
    to_hop(ds, h4, [(0.0, MOI3 / "phao-loat-gan.mp3", -12, 1.7), (0.15, MOI3 / "sung-may-gan.mp3", -13, 1.7),
                    (0.1, MOI3 / "ho-xung-phong-xa.mp3", -12, 1.7), (0.85, RVB / "no-lon-gan.wav", -11, 0.9),
                    (1.15, MOI3 / "dat-roi.mp3", -14, 0.6)])
    # Dốc Chuối: dây căng dưới lời → tao dây quất, dây đứt (WB) → pháo trôi, bánh nghiến sỏi (WC) → bánh pháo khựng, thép rên,
    # sỏi lăn xuống vực (WD) → lặng, gió (W8). Tiếng của khẩu pháo và dây, không tiếng va vào người.
    wa, wb, wc, wd = (L[k][0] for k in ("WA", "WB", "WC", "WD"))
    cue(ds, THU / "day-cang-ket.mp3", w(105, 18) - 0.3, -24, cut=1.6)
    cue(ds, THU / "day-cang-ket.mp3", wa, -14, cut=0.6)
    cue(ds, THU / "tao-day-bat.mp3", wb - 0.12, -10, cut=0.4)
    cue(ds, THU / "dut-day-hero.wav", wb, -3, cut=1.0, hero=True)
    cue(ds, THU / "phao-lao-doc.mp3", w(105, 23), -26, cut=2.0)
    cue(ds, THU / "phao-lao-doc.mp3", wc - 0.1, -4, cut=1.1, hero=True)  # khối thép hơn hai tấn lao dốc: phải nặng
    cue(ds, THU / "banh-nghien-soi.mp3", wc, -6, cut=1.0, hero=True)
    cue(ds, FULL / "rung-tram.mp3", wc, -12, cut=1.0)
    cue(ds, FULL / "khoa-nong.mp3", wd, -5, cut=0.6, hero=True)  # càng pháo, khối thép khựng lại
    cue(ds, MOI / "dap-tram.mp3", wd, -10, cut=0.9)
    cue(ds, THU / "thep-ren.mp3", wd + 0.1, -9, cut=0.9)
    cue(ds, THU / "banh-nghien-soi.mp3", wd, -12, cut=0.45)
    cue(ds, FULL / "dat-lao-xao.mp3", wd + 0.35, -16, cut=0.7)
    # 7/5: lá cờ trên nóc hầm chỉ huy (câu 210, Z7): cờ bay phần phật, reo thắng trận vọng xa
    z7 = L["Z7"][0]
    cue(ds, MOI3 / "co-bay.mp3", w(210, 0), -24, cut=z7 - w(210, 0) + 1.0)
    cue(ds, MOI3 / "co-bay.mp3", z7, -12, cut=1.2)
    cue(ds, MOI3 / "reo-thang-xa.mp3", z7 - 0.1, -10, cut=1.3)


def tuan_tu(ease):
    """Bộ trộn cần các bước ease nối tiếp: bước sau bắt đầu khi bước trước xong (dời bước chồng ra sau)."""
    out, het = [], -1.0
    for e in sorted(ease, key=lambda e: e["at"]):
        e = dict(e, at=round(max(e["at"], het + 0.001), 3))
        out.append(e)
        het = e["at"] + e["over"]
    return out


def tho(ease, a, b, muc, mong=0.3):
    """Nhạc hạ mỏng trong khoảng thở [a, b] (giây phim) rồi trở lại mức muc trước khi lời tiếp."""
    ease += [dict(at=round(a, 3), to=mong, over=0.35), dict(at=round(b - 0.35, 3), to=muc, over=0.4)]


THO = "TUVWXYZH"  # tiền tố tên khoảng thở (bảng khoảng lặng của phan-canh.md)
DAY = {"W8": 0.06, "WB": 0.15, "WC": 0.15, "WD": 0.15, "H1": 0.0, "H2": 0.2, "H3": 0.2, "H4": 0.15, "T5": 0.12, "V3": 0.12, "W1": 0.1, "W8": 0.15, "X1": 0.06, "X8": 0.1, "Y3": 0.25, "Z5": 0.08}  # đáy sóng của các chương


def nen(het):
    """Nhạc, lớp nền theo sóng cảm xúc (giây phim). Mở: đỉnh intro → dồn, thở ở mỗi bảng chữ, đáy ở câu hỏi lớn → dâng vào
    tiêu đề. Mỗi chương một bản: Ch1 tài liệu êm; Ch2 battle-2 nhỏ, dâng ở "nếu chúng sai"; Ch3 hành khúc kéo pháo, hạ ở lời
    Bác, lặng sau Tô Vĩnh Diện, gần tắt ở câu hỏi rồi tắt hẳn trước cú đập chương 4; Ch4 battle-1 + nền chiến trường;
    Ch5 battle-2, tắt hẳn ở đáy trong lòng hầm, nổ A1 trong lặng; Ch6 hành khúc 2 dâng sau tiếng nổ, đáy ở người hy sinh;
    Kết requiem, hạ ở thư khen, tắt dần ở hàng mộ. Mỗi khoảng thở: nhạc hạ mỏng rồi trở lại; đáy (DAY) hạ sâu."""
    T = lambda t: round(t + O, 3)
    C = lambda n: MOC["cau"][n - 1][0]
    p1, p2, a1, p3, gn, kt = (L[k] for k in ("P1", "P2", "A1", "P3", "GN", "KT"))
    th = {k: (T(a), T(b)) for k, (a, b) in L.items() if k[0] in THO}

    def tho_trong(ease, a, z, muc=1.0, mong=0.3):
        for k, (x, y) in th.items():
            if a < x and y < z:
                tho(ease, x, y, muc, DAY.get(k, mong))
        return ease

    hook1 = [dict(at=intro.LANG - 0.02, to=0, over=0.02), dict(at=intro.LANG + 0.3, to=0.55, over=0.25)]
    for k, (a, b) in th.items():
        if b <= T(p1[0]):
            tho(hook1, a, b, 0.55, DAY.get(k, 0.3))
    hook1 += [dict(at=T(C(19)), to=0.65, over=1.0), dict(at=T(C(23)), to=0.85, over=2.0), dict(at=T(p1[0]), to=1.25, over=0.5)]
    tai_lieu = []
    for k, (a, b) in th.items():
        if T(p1[1]) < a < T(C(50)):
            tho(tai_lieu, a, b, 0.75 if a < T(C(31)) else 0.95, DAY.get(k, 0.35))
    tai_lieu += [dict(at=T(C(31)) - 0.5, to=0.95, over=1.5), dict(at=T(C(34)), to=0.75, over=2.0)]
    c2 = tho_trong([dict(at=T(C(73)), to=1.5, over=3.0)], T(C(50)), T(C(73)))
    c2 = tho_trong(c2, T(C(73)), T(C(77)), 1.5)
    c3 = tho_trong([dict(at=T(p2[0]) - 0.3, to=0.25, over=0.5), dict(at=T(p2[1]) - 0.2, to=1.0, over=0.8),
                    dict(at=T(C(113)), to=0.9, over=1.2), dict(at=T(C(114)) - 0.5, to=0, over=0.3)], T(C(77)), T(C(105)) - 0.6)
    # Dốc Chuối (câu 105 → hết W8): nhạc chỉ còn mỏng 40 % để nín thở, lời và tiếng dây, bánh pháo nổi lên; rồi trở lại
    w8 = L["W8"]
    c3 = tho_trong(c3 + [dict(at=T(C(105)) - 0.6, to=0.4, over=0.6)], T(C(105)) - 0.5, T(w8[0]) - 0.1, 0.4)
    c3 = tho_trong(c3 + [dict(at=T(w8[0]), to=0.06, over=0.4), dict(at=T(w8[1]) - 0.4, to=1.0, over=0.8)], T(w8[1]) + 0.5, T(C(113)))
    c4 = tho_trong([], T(C(114)), T(C(153)), 1.0, 0.35)
    y6 = L["Y6"]
    c5 = tho_trong([dict(at=T(y6[0]), to=0, over=0.6), dict(at=T(y6[1]), to=0.45, over=0.4), dict(at=T(a1[0]) - 0.25, to=0, over=0.2)],
                   T(C(153)), T(y6[0]) - 0.1)  # đáy chương 5: tắt hẳn trong lòng hầm trước tiếng nổ
    z7 = L["Z7"]
    c6 = tho_trong([dict(at=T(a1[1]) + 0.6, to=0, over=0.01), dict(at=T(a1[1]) + 1.2, to=1.0, over=1.5),
                    dict(at=T(C(206)), to=0.55, over=1.5), dict(at=T(C(210)) - 0.2, to=1.35, over=1.2)], T(a1[1]) + 3, T(C(210)) - 0.5)
    kt_ = tho_trong([dict(at=T(p3[0]) - 0.3, to=0.25, over=0.5), dict(at=T(gn[0]), to=0.9, over=1.0), dict(at=T(kt[0]) - 2, to=0.3, over=2)],
                    T(z7[1]), T(p3[0]) - 0.5, 0.9)
    kt_ = tho_trong(kt_, T(gn[1]), T(kt[0]) - 2.5, 0.9)
    f = lambda ten: (NHAC / f"dien-bien-phu-{ten}.m4a").as_posix()
    b = [dict(file=f("hook-1"), **{"from": 0.0}, to=T(p1[1]) + 0.3, loop=True, volume=1.3, fade_in=0.0, fade_out=1.5, ease=tuan_tu(hook1)),
         dict(file=f("documentary-score-1"), **{"from": T(p1[1]) - 0.8}, to=T(C(50)) + 0.4, loop=True, volume=0.75,
              fade_in=2.0, fade_out=1.2, ease=tuan_tu(tai_lieu)),
         dict(file=f("battle-score-2"), **{"from": T(C(50)) - 0.4}, to=T(C(77)) + 0.3, loop=True, volume=0.55, fade_in=1.0, fade_out=1.2,
              ease=tuan_tu(c2)),
         dict(file=f("heroic-march-1"), **{"from": T(C(77)) - 0.3}, to=T(C(114)) - 0.2, loop=True, volume=0.8, fade_in=1.0, fade_out=0.1,
              ease=tuan_tu(c3)),
         dict(file=f("battle-score-1"), **{"from": T(C(114))}, to=T(C(153)) + 0.3, loop=True, volume=0.9, fade_in=0.05, fade_out=1.2,
              ease=tuan_tu(c4)),
         dict(file=f("battle-score-2"), **{"from": T(C(153)) - 0.3}, to=T(a1[1]) + 0.8, loop=True, volume=0.85, fade_in=1.0, fade_out=0.5,
              ease=tuan_tu(c5)),
         dict(file=f("heroic-march-2"), **{"from": T(a1[1]) + 0.6}, to=T(z7[1]) + 0.8, loop=True, volume=0.85, fade_in=0.05, fade_out=1.2,
              ease=tuan_tu(c6)),
         dict(file=f("victory-requiem-1"), **{"from": T(z7[1]) - 0.3}, to=het, loop=True, volume=0.9, fade_in=1.5, fade_out=2.5,
              ease=tuan_tu(kt_)),
         dict(file=(SFX / "gio-nui.mp3").as_posix(), **{"from": O}, to=het, loop=True, volume=0.32, fade_in=1, fade_out=3,
              ease=[dict(at=T(a1[0]) - 0.25, to=0, over=0.2), dict(at=T(a1[1]), to=1, over=1.5)]),
         dict(file=(MOI / "chien-truong-xa.mp3").as_posix(), **{"from": O}, to=T(p1[0]) + 1, loop=True, volume=0.30, fade_in=1.5, fade_out=2),
         dict(file=(MOI / "chien-truong-xa.mp3").as_posix(), **{"from": T(C(114)) + 1}, to=T(a1[0]), loop=True, volume=0.30, fade_in=2.0,
              fade_out=0.3, ease=[dict(at=T(y6[0]), to=0, over=0.6), dict(at=T(y6[1]), to=0.6, over=1.0)]),
         # sau A1 và H4: chiến trường còn gầm dưới câu 179–180, cắt phụt về lặng ở câu 181 ("Ba quyết định đã đi hết một vòng.")
         dict(file=(MOI / "chien-truong-xa.mp3").as_posix(), **{"from": T(a1[1]) + 0.3}, to=T(C(181)) - 0.05, loop=True, volume=0.42,
              fade_in=0.3, fade_out=0.12)]
    return [x for x in b if x["from"] < het]


def _doc(tep, sr=48000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(tep), "-f", "f32le", "-ac", "2", "-ar", str(sr), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)


def tron_tieng(ds, het, ra, fade_out=1.5):
    """Trộn sẵn mọi tiếng động thành một lớp, cùng phép của kit.py tron: đỉnh cả tệp → "db", cắt "cut" mờ 0,3 s cuối, đặt ở "t".
    (nhanh hơn trộn hơn 1.000 cue qua ffmpeg; bộ trộn cũ còn vỡ ENAMETOOLONG khi quá ~300 cue.)"""
    sr = 48000
    y = np.zeros((int((het + 2) * sr), 2), dtype=np.float32)
    kho, dinh = {}, {}
    for c in ds:
        f = c["sound"]
        if f not in kho:
            kho[f] = _doc(f, sr)
            dinh[f] = 20 * np.log10(max(float(np.abs(kho[f]).max()), 1e-9))
        x = kho[f]
        if c.get("cut"):
            x = x[:int(round(c["cut"] * sr))].copy()
            m = min(int(0.3 * sr), len(x))
            x[len(x) - m:] *= np.linspace(1, 0, m, dtype=np.float32)[:, None]
        g = 10 ** (round(c["db"] - dinh[f], 1) / 20)
        i = max(0, int(round(c["t"] * 1000)) * sr // 1000)
        n = min(len(x), len(y) - i)
        if n > 0:
            y[i:i + n] += g * x[:n]
    y = y[:int(round(het * sr))]
    m = int(fade_out * sr)
    y[-m:] *= np.linspace(1, 0, m, dtype=np.float32)[:, None]
    sf.write(ra, y, sr, subtype="FLOAT")
    return ra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--den", type=float, default=None)
    ap.add_argument("--tron", action="store_true")
    ap.add_argument("--ten", default="mix-v3")
    o = ap.parse_args()
    het = min(o.den or 1e9, MOC["het"] + O)
    # intro: mọi tiếng tắt gọn ở phách lặng (khoảng chân không), trừ CẠCH; bus riêng, không vang
    ds = [dict(sound=cat_san(f, intro.LANG - t) if t < intro.LANG else Path(f).as_posix(), t=t, db=db, align="start", bus="intro",
               **({"weight": "hero"} if h else {})) for f, t, db, h in intro.CUES]
    tieng_canh(ds)
    tieng_the(ds)
    nhan_khe(ds)
    khi_the(ds)
    ds = sorted((x for x in ds if O - 0.2 <= x["t"] < het or x["t"] < O), key=lambda x: x["t"])
    giong = AM / f"{o.ten}-giong.wav"
    y, sr = sf.read(MOC["giong"])
    sf.write(giong, np.concatenate([np.zeros((int(round(O * sr)),) + y.shape[1:]), y])[:int(round(het * sr))], sr)
    # nhạc: chỉ các lớp nền, KHÔNG duck ở đây (hau-ky-am.py duck bằng sidechain theo giọng thật)
    m = dict(duration=round(het, 3), fade_out=1.5, music=dict(volume=0.36, duck=False, beds=nen(het)), cues=[])
    thieu = sorted({x["sound"] for x in ds if not Path(x["sound"]).exists()} | {b["file"] for b in m["music"]["beds"] if not Path(b["file"]).exists()})
    if thieu:
        sys.exit(f"thiếu tệp âm: {thieu}")
    mj = AM / f"{o.ten}-nhac.json"
    mj.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    (AM / f"{o.ten}-tieng.json").write_text(json.dumps(ds, ensure_ascii=False, indent=0), encoding="utf-8")
    phut = (het - O) / 60
    dem = {b: sum(1 for x in ds if x["bus"] == b) for b in ("intro", "kho", "ngoai", "ham")}
    print(f"{len(ds)} tiếng động ({sum(1 for x in ds if x['t'] >= O) / phut:.0f}/phút sau intro) theo bus {dem}, {len(m['music']['beds'])} lớp nền")
    if o.tron:
        subprocess.run([sys.executable, "-I", "-X", "utf8", str(REPO_GOC / "tools/kit/kit.py"), "tron", str(mj),
                        "--out", str(AM / f"{o.ten}-nhac.wav"), "--force"], check=True)
        for b in dem:
            tron_tieng([x for x in ds if x["bus"] == b], het, AM / f"{o.ten}-tieng-{b}.wav")
        # chuỗi plugin VST3 (FabFilter, Valhalla) chạy trong python có pedalboard của Goha AVS
        subprocess.run([str(duong("vst_python")), "-X", "utf8", str(GOC / "hau-ky-am.py"), "--am", str(AM), "--ten", o.ten], check=True)


if __name__ == "__main__":
    main()
