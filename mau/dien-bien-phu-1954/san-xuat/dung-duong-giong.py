"""Ghép đường giọng tập 1 từ các lượt đọc ElevenLabs (mỗi lượt ≤ 5.000 ký tự, đọc liền nhiều chương).

Mỗi lượt: cân về cùng độ to, cắt từng câu ở chỗ lặng nhất (tools/eleven-speed/cat-cau.py, mốc chữ của chính TTS),
rồi nối các câu theo thứ tự lời đọc, chèn khoảng lặng có tên của phan-canh.md tại ranh câu.
Ra: <giong>/giong-v2.wav (48 kHz mono) và san-xuat/moc-cau.json (mốc từng chữ, khoảng lặng) cho kiem-phan-canh.py.

python -I dung-duong-giong.py <thư mục giọng>   (thư mục có phan.json, phan-<x>.wav, phan-<x>.json)
"""
import json, re, subprocess, sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
G = Path(sys.argv[1])
CAT = GOC.parents[2] / "tools" / "eleven-speed" / "cat-cau.py"
LUFS = -18.0  # mức chung của các lượt trước khi trộn (master −14 ở bước trộn)
cau = [l.strip() for l in (GOC.parent / "ke-hoach" / "loi-doc-v5.txt").read_text(encoding="utf-8").split("\n") if l.strip()]
# chặn tái phạm: lời có cách nói user đã sửa và chốt (kenh/cach-noi-da-chot.tsv) thì không dựng giọng
if subprocess.run([sys.executable, "-I", str(GOC.parents[2] / "tools" / "lichsu" / "kiem-da-chot.py"),
                   str(GOC.parent / "ke-hoach" / "loi-doc-v5.txt")]).returncode:
    sys.exit("lời đọc phạm sổ cách nói đã chốt: sửa lời trước khi dựng giọng")
van = (GOC / "phan-canh.md").read_text(encoding="utf-8")
lang = {m[1]: (m[2], float(m[3])) for m in re.finditer(r"^\| ([A-Z][A-Z0-9]) \| (\S+) \| ([\d.]+) \|", van, re.M)}


LECH_LOI = set()  # câu mà chữ đã đọc ở lượt gốc khác lời hiện hành: bắt buộc có bản đọc lại thay vào


def do_to(f: Path) -> float:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err)[-1])


def cat_luot(wav: Path, kq_json: Path, a: int, b: int) -> list:
    """Cân độ to một lượt đọc câu a..b, cắt từng câu; trả [(số câu, đoạn âm, mốc chữ tương đối)]."""
    stem = wav.with_suffix("")
    words = [w for w in json.loads(kq_json.read_text(encoding="utf-8"))["results"][0]["words"] if not w["text"].startswith("[")]
    Path(f"{stem}-words.json").write_text(json.dumps({"words": words}, ensure_ascii=False), encoding="utf-8")
    # chữ đã gửi TTS (một câu một dòng, dòng đầu có thẻ [fast-paced]): so và cắt theo đúng chữ đã đọc, vì lời có thể đã sửa
    # sau lượt đọc (câu sửa có bản đọc lại trong sua/, thay vào sau)
    da_doc = [re.sub(r"^\[[^\]]*\]\s*", "", l.strip()) for l in wav.with_suffix(".txt").read_text(encoding="utf-8").split("\n") if l.strip()]
    assert len(da_doc) == b - a + 1, f"{wav.name}: {len(da_doc)} dòng chữ, cần {b - a + 1}"
    Path(f"{stem}-loi.txt").write_text("\n".join(da_doc) + "\n", encoding="utf-8")
    y, sr = sf.read(wav)
    sf.write(f"{stem}-can.wav", y * 10 ** ((LUFS - do_to(wav)) / 20), sr)
    out = Path(f"{stem}-cau")
    subprocess.run([sys.executable, "-I", "-X", "utf8", str(CAT), f"{stem}-can.wav", f"{stem}-words.json", f"{stem}-loi.txt", str(out)], check=True)
    seg = json.loads((out / "seg.json").read_text(encoding="utf-8"))
    assert len(seg) == b - a + 1, f"{wav.name}: {len(seg)} câu, cần {b - a + 1}"
    kq, wi = [], 0
    for j, s in enumerate(seg):
        n = a + j
        tok = da_doc[j].split()
        if da_doc[j] != cau[n - 1]:
            LECH_LOI.add(n)
        mine = words[wi:wi + len(tok)]
        if len(mine) != len(tok) or any(re.sub(r"\W", "", m["text"].lower()) != re.sub(r"\W", "", t.lower()) for m, t in zip(mine, tok)):
            sys.exit(f"câu {n}: chữ TTS không khớp lời ({[m['text'] for m in mine][:5]} / {tok[:5]})")
        wi += len(tok)
        kq.append((n, sf.read(s["file"])[0], [m["start_ms"] / 1000 - s["src_start"] for m in mine]))
    return kq


seg_all = []
for p in json.loads((G / "phan.json").read_text()):
    seg_all += cat_luot(G / f"phan-{p['phan']}.wav", G / f"phan-{p['phan']}.json", p["tu"], p["den"])
# Câu đọc lại (luật giọng: đọc câu trước–câu đó–câu sau một lần, lấy câu giữa): sua/sua-<n>.wav, .json
# sua/dem-khung.json: danh sách câu đọc lại sau khi phim đã dựng (đệm bội số khung, xem dưới)
DEM_KHUNG = set(json.loads((G / "sua" / "dem-khung.json").read_text())) if (G / "sua" / "dem-khung.json").exists() else set()
for f in sorted((G / "sua").glob("sua-*.json")):
    if not re.fullmatch(r"sua-\d+\.json", f.name):
        continue
    n = int(f.stem[4:])
    giua = cat_luot(f.with_suffix(".wav"), f, n - 1, n + 1)[1]
    if n in DEM_KHUNG:
        # đệm lặng cuối câu (< 1 khung) để độ dài lệch bản cũ đúng bội số khung 24 fps:
        # mọi cảnh phía sau dời nguyên khung, không lệch ±1 khung do làm tròn
        them = (len(seg_all[n - 1][1]) - len(giua[1])) % (48000 // 24)
        giua = (n, np.concatenate([giua[1], np.zeros(them)]), giua[2])
    seg_all[n - 1] = giua
    print(f"câu {n}: thay bằng bản đọc lại")
    LECH_LOI.discard(n)
if LECH_LOI:
    sys.exit(f"câu {sorted(LECH_LOI)}: lời đã sửa nhưng chưa có bản đọc lại (sua/sua-<n>.wav, .json, .txt)")

# Nối: câu → khoảng lặng có tên sau câu đó (và khoảng lặng nối sau khoảng lặng)
sau = {}
for ten, (s, giay) in lang.items():
    sau.setdefault(s, []).append((ten, giay))
SR, parts, moc, moc_lang, t = 48000, [], [], {}, 0.0


def chen(khoa: str) -> None:
    global t
    for ten, giay in sau.get(khoa, []):
        parts.append(np.zeros(int(round(giay * SR))))
        moc_lang[ten] = [round(t, 3), round(t + giay, 3)]
        t += giay
        chen(ten)


def diem_cat(y: np.ndarray, t_chu: float) -> int:
    """Mẫu lặng nhất (khung 10 ms) trong 0,35 s trước chữ bắt đầu ở t_chu: chỗ cắt để chèn lặng giữa dòng."""
    a, b, w = max(0, int((t_chu - 0.35) * SR)), max(1, int((t_chu - 0.02) * SR)), int(0.01 * SR)
    nang = [float(np.sqrt(np.mean(y[i:i + w] ** 2))) for i in range(a, b - w, w // 2)] or [0.0]
    return a + int(np.argmin(nang)) * (w // 2) + w // 2


for n, y, rel in seg_all:
    # khoảng lặng giữa dòng: khoá "n:k" = lặng sau chữ k (đếm từ 0) của câu n (vd tiếng dây đứt giữa các câu ngắn của một dòng)
    giua = sorted((int(k.split(":")[1]), k) for k in sau if k.startswith(f"{n}:"))
    t0, pos, them, lech = t, 0, 0.0, [0.0] * len(rel)
    for k, khoa in giua:
        i = diem_cat(y, rel[k + 1])
        parts.append(y[pos:i])
        t += (i - pos) / SR
        pos, truoc = i, t
        chen(khoa)
        them += t - truoc
        lech[k + 1:] = [them] * (len(rel) - k - 1)
    moc.append([round(t0 + max(r, 0.0) + d, 3) for r, d in zip(rel, lech)])
    parts.append(y[pos:])
    t += (len(y) - pos) / SR
    chen(str(n))
full = np.concatenate(parts)
sf.write(G / "giong-v2.wav", full, SR, subtype="PCM_24")
(GOC / "moc-cau.json").write_text(json.dumps({"giong": str(G / "giong-v2.wav").replace("\\", "/"), "cau": moc,
                                              "het": round(t, 3), "lang": moc_lang}, ensure_ascii=False), encoding="utf-8")
print(f"{len(seg_all)} câu, {t:.2f} s ({t // 60:.0f}:{t % 60:05.2f}); khoảng lặng: {moc_lang}")
