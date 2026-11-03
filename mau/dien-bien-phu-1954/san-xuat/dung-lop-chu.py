"""Lớp chữ trong suốt cho mọi cảnh ảnh, phim, 3D của tập 1 (khối template/overlay), đúng số khung từng cảnh.

Đọc cột "Chữ trên hình" của phan-canh.json: mỗi cụm "…" (hoặc "Thẻ tên …") thành một thẻ góc dưới, chia đều thời gian
cảnh nếu có nhiều cụm; phần "Nguồn: …" không in vào thẻ (đã nằm ở dòng ghi nguồn). Nhãn "…" → nhãn ngày góc trên.
Chữ nhấn đúng lúc đọc ở CHU_NHAN. Ghi nguồn góc phải dưới = ghi_nguon của cảnh (thẻ và bản đồ tự vẽ nguồn, không qua đây).
Ra <output>/261101-dien-bien-phu-1954/hinh/lop-chu/<mã>.mov (ProRes 4444, nền trong suốt).

python -I -X utf8 dung-lop-chu.py [--stills] [--render] [MÃ ...]
"""
import json, re, subprocess, sys
from pathlib import Path
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
DUNG_TRANG = ["node", str(REPO_GOC / "tools/kit/dung-trang.mjs")]  # dựng trang HTML thành mp4/mov/ảnh
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

GOC = Path(__file__).resolve().parent
TPL = GOC.parents[2] / "template"
RA = OUT / "261101-dien-bien-phu-1954/hinh/lop-chu"
FPS = 24
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))
MOC = json.loads((GOC / "moc-cau.json").read_text(encoding="utf-8"))
CHU_NHAN = {"C3-10": ("Hai… ba… nào", "@84:26"), "KT-03": ("Giơ tay lên!", "@207:16"), "C5-18": ("như con đom đóm", "@168:18")}
KIEU = ("anh", "karmen", "3d", "3d-moi", "demo", "can-tim")


def giay(neo, t0):
    n, _, k = neo[1:].partition(":")
    return round(MOC["cau"][int(n) - 1][int(k or 0)] - t0, 3)


def tach_the(chu):
    """Các cụm thẻ trong cột chữ → [(tên, chi tiết)]; bỏ phần Nguồn, bỏ chú thích '(không có ảnh)'."""
    if chu.startswith("Chữ ") or chu.startswith("Nhãn"):
        return []
    cum = re.findall(r'"([^"]+)"', chu) if '"' in chu else []
    if chu.startswith("Thẻ tên"):
        cum = [chu.split("Thẻ tên", 1)[1].strip().strip('"')]
    the = []
    for x in cum:
        x = re.sub(r"\s*\((không có ảnh|chữ, không ảnh)\)", "", x)
        phan = [p.strip() for p in x.split(" · ") if p.strip() and not p.strip().startswith("Nguồn")]
        if len(phan) > 1 and phan[0][:1].islower():  # cụm đầu là mô tả (chữ thường): tên người ở cụm sau lên làm tên thẻ
            phan = [phan[1], phan[0]] + phan[2:]
        if phan:
            the.append((phan[0], " · ".join(phan[1:])))
    return the


def shot(c, n):
    d = n / FPS
    t0 = round(c["t0"] * FPS) / FPS
    s = dict(duration=d, credit=("Ảnh: " if c["kieu"] == "anh" else "") + c["ghi_nguon"], thes=[], texts=[])
    m = re.match(r'Nhãn(?: ngày)? "([^"·]+)', c["chu"])
    if m:
        s["date"] = dict(text=m[1].strip(), from_=0.2)
    the = tach_the(c["chu"])
    for i, (ten, ct) in enumerate(the):
        a, b = d * i / len(the), d * (i + 1) / len(the)
        s["thes"].append(dict(name=ten, detail=ct, from_=round(a + 0.25, 3), to=round(b - 0.3, 3), size=54 if len(ten) < 40 else 40))
    if c["id"] in CHU_NHAN:
        txt, neo = CHU_NHAN[c["id"]]
        s["texts"].append(dict(text=txt, from_=giay(neo, t0), y=540, size=110))
    return json.loads(json.dumps(s).replace('"from_"', '"from"'))


def main():
    chon = [a for a in sys.argv[1:] if not a.startswith("--")]
    canh = [c for c in PC["canh"] if c["kieu"] in KIEU and (not chon or c["id"] in chon)]
    thu = TPL / "overlay" / "shots" / "dbp1"
    thu.mkdir(exist_ok=True)
    RA.mkdir(parents=True, exist_ok=True)
    for c in canh:
        c["n"] = round(c["t1"] * FPS) - round(c["t0"] * FPS)
        (thu / f"{c['id']}.js").write_text("// Sinh bởi tap/EP001-dien-bien-phu-1954/san-xuat/dung-lop-chu.py, đừng sửa tay.\nwindow.SHOT = "
                                           + json.dumps(shot(c, c["n"]), ensure_ascii=False) + ";\n", encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(TPL / "tools" / "build_shots.py"), "overlay"], check=True, capture_output=True)
    for c in canh:
        trang = TPL / "overlay" / f"dbp1-{c['id']}.html"
        if "--stills" in sys.argv:
            subprocess.run([*DUNG_TRANG, str(trang), "--stills", f"{c['n'] / FPS * 0.5:.2f}", "--out-dir",
                            str(RA.parent / "story" / "lop-chu" / c["id"])], check=True, capture_output=True)
        if "--render" in sys.argv:
            subprocess.run([*DUNG_TRANG, str(trang), "--out", str(RA / f"{c['id']}.mov"), "--fps", str(FPS), "--transparent", "--force"],
                           check=True, capture_output=True)
            print(c["id"], flush=True)
    print(f"{len(canh)} lớp chữ xong")


if __name__ == "__main__":
    main()
