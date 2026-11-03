"""Lô L4 + L5: 90 cảnh 3D của tập 1 trên sân khấu và kho 3D của bản mẫu (trang3d/tap1.js).

Mỗi cảnh: cảnh mẫu mượn trạng thái vật thể (proto, thuộc một trang nhóm của bản mẫu), độ lệch vào cảnh mẫu (off, giây),
biến thể máy (bien: xoay độ, keo hệ số khoảng cách, cao mét; giá trị đơn hoặc [đầu, cuối]). Cảnh '3d:<mã>' dùng lại đúng
cảnh mẫu (bien rỗng). Ra <output>/261101-dien-bien-phu-1954/hinh/3d/<mã>.mp4, đúng số khung.

python -I -X utf8 dung-3d.py [--stills] [--render] [MÃ ...]
"""
import json, subprocess, sys
from pathlib import Path
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
DUNG_TRANG = ["node", str(REPO_GOC / "tools/kit/dung-trang.mjs")]  # dựng trang HTML thành mp4/mov/ảnh
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

GOC = Path(__file__).resolve().parent
TRANG = GOC / "trang3d"
RA = OUT / "261101-dien-bien-phu-1954/hinh/3d"
FPS = 24
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))
CANH = {c["id"]: c for c in PC["canh"]}

NHOM = {  # bảng nhóm của bản mẫu (mã cảnh, khung đầu); sân khấu từng mã; cách nhìn; mốc gốc thời gian của sân khấu bản thử
    "moman": dict(cat=[["HK1", 0], ["HK2", 21], ["HK3", 31], ["HK4", 41], ["HK5", 51], ["MM1", 64], ["MM2", 108], ["MM3", 161], ["MM4", 192], ["MM5", 216], ["MM6", 242], ["het", 260]],
                  san={"HK1": "a1Dem", "HK4": "a1Dem", "HK2": "bauTroi", "MM5": "himLam", "MM6": "himLam"}, mac="tranDia", nhin="ngay", phoi=.92),
    "giua": dict(cat=[["TN1", 929], ["TN2", 967], ["het", 1005]], san={}, mac="sanBay", nhin="ngay", phoi=.9),
    "badot": dict(cat=[["BD1", 1792], ["BD2", 1840], ["BD3", 1870], ["BD4", 1897], ["BD5", 1936], ["BD6", 1990], ["BD7", 2011], ["BD8", 2036],
                       ["BD9", 2107], ["BD10", 2155], ["BD11", 2184], ["BD12", 2217], ["BD13", 2242], ["het", 2294]],
                  san={"BD2": "himLamDem", "BD3": "himLamDem", "BD8": "sanBay", "BD10": "a1Cat", "BD11": "a1Cat", "BD12": "a1Cat"}, mac="a1Dem", nhin="dem", phoi=1.0,
                  chop=[[93.45, .55, .2], [92.36, .1, .1]]),
    "maybay": dict(cat=[["MB1", 2698], ["MB2", 2722], ["MB3", 2739], ["het", 2810]], san={"MB3": "sanBay"}, mac="bauTroi", nhin="ngay", phoi=.9),
    "thu": dict(cat=[["A1", 0], ["A2", 39], ["B1", 96], ["B2", 137], ["C1", 172], ["C2", 215], ["D1", 266], ["D2", 319], ["D3", 345], ["D4", 381],
                     ["E1", 403], ["E2", 436], ["E3", 466], ["E4", 484], ["F1", 548], ["F2", 591], ["F3", 647], ["het", 700]],
                san={}, mac=None, nhin="thu", phoi=1.3),
}
SAN_THU = {"A": ("A", "A1"), "B": ("B", "B1"), "C": ("Cc", "C1"), "D": ("D", "D1"), "E": ("D", "D1"), "F": ("F", "F1")}
NGAY_BD8 = dict(nhin="ngay", phoi=.9)

# Cảnh 3D mới: (cảnh mẫu, biến thể máy, độ lệch giây). Cảnh '3d:<mã>' tự lấy cảnh mẫu cùng tên.
MOI = {
    "MO01": ("BD8", dict(keo=[.7, .6], cao=80)), "MO02": ("BD8", dict(xoay=[180, 190], cao=-100)), "MO04": ("BD8", dict(xoay=[10, 12])),
    "MO06": ("BD8", dict(cao=200, keo=[1.4, 1.5])), "MO09": ("TN2", dict(keo=[2.5, 2.3])), "MO11": ("MM5", dict(xoay=[120, 125], keo=1.8)),
    "MO12": ("TN2", dict(xoay=[-30, -25], keo=[1.6, 1.5])), "MO13": ("MM5", dict(keo=[.35, .3])), "MO15": ("MB3", dict(cao=60, xoay=[0, 15])),
    "MO29": ("MM5", dict(xoay=[-120, -115], keo=2.0, cao=-10)), "C1-10": ("BD8", dict(cao=250, keo=[1.8, 1.9])), "C1-21": ("B1", dict(xoay=[10, 15])),
    "C1-22": ("B2", dict(keo=[.8, .7])), "C2-03": ("TN1", dict(cao=200, keo=2)), "C2-04": ("MM5", dict(keo=[.25, .22])),
    "C2-08": ("TN2", dict(xoay=[60, 70], keo=[1.8, 1.7])), "C2-10": ("TN2", dict(xoay=[150, 160], keo=[1.5, 1.4])), "C2-12": ("MM5", dict(xoay=[170, 175], keo=1.6)),
    "C2-14": ("TN2", dict(xoay=[200, 210], keo=[1.2, 1.1])), "C2-16": ("BD8", dict(xoay=[90, 95], cao=250, keo=[.6, .55])), "C2-26": ("MM5", dict(keo=[.3, .28], cao=-5)),
    "C2-27": ("TN2", dict(xoay=[160, 165], keo=[1.3, 1.2])), "C2-28": ("MM5", dict(cao=120, keo=[2.2, 2.5], xoay=[60, 62])), "C3-07": ("A1", dict(xoay=[30, 35])),
    "C3-11": ("D3", dict(xoay=[0, 5])), "C3-12": ("A2", dict(cao=30, keo=[1.6, 1.7])), "C3-16": ("MM1", dict(xoay=[30, 35])),
    "C3-24": ("C2", dict(xoay=[-40, -35])), "C3-25": ("MM5", dict(xoay=[-40, -30])), "C3-30": ("C2", dict(keo=[1.5, 1.6], cao=10)),
    "C3-35": ("MM1", dict(xoay=[-40, -35], keo=[1.3, 1.2])), "C3-37b": ("TN2", dict(cao=20, keo=[2.5, 2.6])), "C3-39": ("MM5", dict(cao=40, keo=1.6, xoay=[20, 25])),
    "C4-05": ("BD3", dict(xoay=[-30, -25])), "C4-07": ("BD6", dict(keo=[.7, .6])), "C4-08": ("C1", dict(keo=[.8, .7])),
    "C4-10": ("BD3", dict(cao=80, keo=[1.5, 1.6])), "C4-15": ("BD6", dict(xoay=[-30, -25])), "C4-24": ("TN1", dict(xoay=[40, 45], keo=[.7, .6])),
    "C4-27": ("BD8", dict(keo=[.4, .35], cao=100)), "C4-34": ("BD9", dict(cao=100)), "C4-36": ("BD8", dict(cao=150, keo=.7, xoay=[200, 205])),
    "C4-39": ("BD8", dict(xoay=[-40, -35], keo=.6, cao=-60)), "C4-38": ("BD8", dict(keo=[.8, .7], xoay=[30, 35], cao=40)), "C4-42": ("TN2", dict(xoay=[-90, -85], keo=[.6, .55])), "C4-43": ("BD8", dict(xoay=[150, 155], cao=-80)),
    "C5-02": ("BD8", dict(cao=350, keo=[1.2, 1.3])), "C5-05": ("BD8", dict(xoay=[-60, -55])), "C5-06": ("MM3", dict(xoay=[20, 25])),
    "C5-07": ("MB1", dict(keo=[2.5, 2.6])), "C5-09": ("MB1", dict(xoay=[-40, -35], keo=1.8)), "C5-10": ("BD8", dict(xoay=[100, 105], cao=150)),
    "C5-11": ("BD8", dict(cao=300, keo=1.0)), "C5-18": ("BD11", dict(keo=[.6, .55])), "C5-19": ("BD10", dict(xoay=[20, 25], keo=[.8, .75])),
    "C5-20": ("MB3", {}), "C5-23": ("BD8", dict(keo=[.5, .45], cao=-50)), "C5-29": ("BD13", dict(keo=[1.5, 1.6]), 1.0),
    "C5-31": ("BD13", dict(keo=[2, 2.1], cao=30), 2.0), "C5-34": ("MM1", dict(keo=[.4, .35])), "C5-37": ("MM5", dict(cao=180, keo=[2.4, 2.8], xoay=[-60, -58])),
    "C6-13": ("F1", dict(xoay=[60, 65])), "C6-20": ("MM5", dict(xoay=[90, 95])), "KT-03": ("TN2", dict(xoay=90, keo=[.9, .85])),
    "KT-05": ("TN2", dict(keo=[.3, .28])), "KT-13": ("A2", {}), "KT-19": ("A2", dict(keo=[.9, .85]), 1.5),
    "KT-21": ("MM5", dict(cao=120, keo=[2, 2.2])),
}
MAU_TEN = {"thu-A2": "A2", "T-A1": "A1", "T-C1": "C1", "T-C2": "C2", "T-D1": "D1", "T-D3": "D3", "T-E4": "E4", "T-F1": "F1", "T-F2": "F2", "T-F3": "F3"}


def cau_hinh(ma):
    c = CANH[ma]
    n = round(c["t1"] * FPS) - round(c["t0"] * FPS)
    if c["kieu"] == "3d" and ma not in MOI:  # cảnh mẫu hỏng ở kho hiện tại (BD7) được thay trong MOI
        proto, bien, off = MAU_TEN.get(c["ten"], c["ten"]), {}, 0.0
    else:
        x = MOI[ma]
        proto, bien, off = x[0], x[1], (x[2] if len(x) > 2 else 0.0)
    ten_nhom = next(k for k, g in NHOM.items() if any(r[0] == proto for r in g["cat"]))
    g = NHOM[ten_nhom]
    s = dict(cat=g["cat"], proto=proto, d=n / FPS, k0=dict(g["cat"])[proto], nhin=g["nhin"], phoi=g["phoi"], bien=bien or None, chop=g.get("chop", []))
    t_mau = dict(g["cat"])[proto] / FPS + off
    if ten_nhom == "thu":
        s["san"], s["goc"] = SAN_THU[proto[0]]
    else:
        s["san"] = g["san"].get(proto, g["mac"])
    s["te0"] = round(t_mau, 4)
    # Cảnh mới dài hơn cảnh mẫu: co đồng hồ vật lý để máy đi đúng đường đã duyệt (chậm hình bằng đồng hồ, không đổi tốc độ video).
    cat = g["cat"]
    i = [r[0] for r in cat].index(proto)
    dp = (cat[i + 1][1] - cat[i][1]) / FPS - off
    s["toc"] = round(min(1.0, max(dp, 0.3) / (n / FPS)), 4)
    if proto == "BD8":
        s.update(NGAY_BD8)
    if proto == "BD13":
        s["nhinThem"] = dict(phoi=.6, dof=dict(tieuCu=100, khau=3, max=4), bong=dict(ban=3, manh=.6))
    if proto == "BD9":
        s["phoi"] = 2.2
    if proto == "E4":
        s["phoi"] = 1.8
    if proto in ("HK1", "HK4"):
        s["phoi"] = 1.0
    return s, n


def trang_html(ma, s):
    mau = "../../../dien-bien-phu-mau/san-xuat"
    kho = "../../../../template/kho-quan-su/3d"
    js = ["vendor/three.min.js", "engine/kho3d.js", "engine/vat-lieu.js", "engine/hinh.js", "engine/san-khau.js", "engine/hau-ky.js", "engine/nguoi3d.js"]
    js = [f"{kho}/{x}" for x in js] + [f"{kho}/vat-the/{x}.js" for x in (
        "dbp-1954/ta/phao-105", "dbp-1954/ta/phao-37", "dbp-1954/ta/bo-doi", "dbp-1954/ta/dan-cong", "dbp-1954/ta/xe-dap-tho", "dbp-1954/ta/chien-hao",
        "dbp-1954/ta/xeng", "dbp-1954/phap/c47", "dbp-1954/phap/ham-vom", "dbp-1954/phap/lo-cot", "dbp-1954/phap/thep-gai", "dbp-1954/phap/du-tiep-te",
        "dbp-1954/dia-hinh/doi-a1", "hieu-ung/vu-no")]
    js += [f"{mau}/ban-thu-3d/trang/{x}.js" for x in ("chung", "canh-ab", "canh-c", "canh-doc-chuoi", "canh-f")]
    js += [f"{mau}/ban-full/trang/{x}.js" for x in ("chung-full", "canh-san-bay", "canh-bau-troi", "canh-tran-dia", "canh-him-lam", "canh-a1-dem", "canh-a1-cat")]
    the = "\n".join(f'<script src="{x}"></script>' for x in js)
    return (f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><style>@font-face{{font-family:Oswald;font-weight:200 700;'
            f'src:url("../../../../template/fonts/Oswald-VF.ttf")}}html,body{{margin:0;background:#000}}canvas{{display:block;position:absolute;left:0;top:0}}</style></head>\n'
            f'<body><canvas id="gl"></canvas><canvas id="lop"></canvas>\n<!-- Sinh bởi dung-3d.py ({ma}), đừng sửa tay. -->\n{the}\n'
            f'<script>window.CANH3D = {json.dumps(s, ensure_ascii=False)};</script>\n<script src="tap1.js"></script>\n</body></html>\n')


def main():
    ma = [c["id"] for c in PC["canh"] if c["kieu"] in ("3d", "3d-moi")]
    thieu = [m for m in ma if CANH[m]["kieu"] == "3d-moi" and m not in MOI]
    if thieu:
        sys.exit(f"MOI thiếu: {thieu}")
    chon = [a for a in sys.argv[1:] if not a.startswith("--")] or ma
    RA.mkdir(parents=True, exist_ok=True)
    for m in chon:
        s, n = cau_hinh(m)
        trang = TRANG / f"{m}.html"
        trang.write_text(trang_html(m, s), encoding="utf-8")
        if "--stills" in sys.argv:
            subprocess.run([*DUNG_TRANG, str(trang), "--stills", f"{0.05 if '--day-du' in sys.argv else s['d'] / 2:.2f}" + (f",{s['d'] / 2:.2f},{s['d'] - 0.05:.2f}" if '--day-du' in sys.argv else ""), "--out-dir",
                            str(RA.parent / "story" / "3d" / m)], check=True, capture_output=True)
            print(m, "ảnh tĩnh", flush=True)
        if "--render" in sys.argv:
            ra = RA / f"{m}.mp4"
            subprocess.run([*DUNG_TRANG, str(trang), "--out", str(ra), "--fps", str(FPS), "--force"], check=True, capture_output=True)
            so = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets",
                                 "-of", "csv=p=0", str(ra)], capture_output=True, text=True).stdout.strip().rstrip(",")
            print(f"{m}: {so} khung (cần {n}){'' if int(so) == n else '  LỆCH'}", flush=True)
    print(f"{len(chon)} cảnh 3D xong")


if __name__ == "__main__":
    main()
