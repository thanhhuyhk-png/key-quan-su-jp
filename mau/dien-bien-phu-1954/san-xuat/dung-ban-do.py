"""Lô L3: 43 cảnh địa hình lòng chảo (template/map3d) và 8 cảnh bản đồ chính trị (template/vnmap) của tập 1.

Mỗi cảnh một SHOT ở BD bên dưới, đúng số khung (24 fps); mốc "@N" / "@N:k" = lúc đọc chữ k câu N, đổi sang giây
tính từ đầu cảnh. Ghi nguồn = nguồn nền bản đồ của engine + " · Số liệu: …" của cảnh (lớp chữ chung không vẽ ghi nguồn
cho cảnh bản đồ). vnmap luôn có Hoàng Sa, Trường Sa, "Biển Đông" (nhãn mặc định); khung Tây Bắc dừng ở ≤ 105,5° Đông.
Ra <output>/261101-dien-bien-phu-1954/hinh/ban-do/<mã>.mp4

python -I -X utf8 dung-ban-do.py [--stills] [--render] [MÃ ...]
"""
import json, subprocess, sys
from pathlib import Path
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
DUNG_TRANG = ["node", str(REPO_GOC / "tools/kit/dung-trang.mjs")]  # dựng trang HTML thành mp4/mov/ảnh
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

GOC = Path(__file__).resolve().parent
TPL = GOC.parents[2] / "template"
RA = OUT / "261101-dien-bien-phu-1954/hinh/ban-do"
FPS = 24
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))
MOC = json.loads((GOC / "moc-cau.json").read_text(encoding="utf-8"))
CANH = {c["id"]: c for c in PC["canh"]}
NEN = {"map3d": "Địa hình: AWS Terrain Tiles (SRTM, công cộng) · Ảnh vệ tinh: Sentinel-2 cloudless 2016 (EOX, CC BY 4.0) · Vị trí: OpenStreetMap (ODbL); mũi tên, đường hào, vị trí đơn vị: minh họa",
       "vnmap": "Bản đồ: Natural Earth (phạm vi công cộng) · Hoàng Sa, Trường Sa thuộc Việt Nam"}
XANH, DO = "rgba(93,134,184,0.36)", "#d8382a"


def cam(lat, lon, dist, heading, pitch, lat2=None, lon2=None, dist2=None, heading2=None, pitch2=None, fov=40):
    """Máy quay hai mốc: đầu cảnh → cuối cảnh (thời điểm cuối điền khi dựng)."""
    return [dict(t=0, lat=lat, lon=lon, dist=dist, heading=heading, pitch=pitch, fov=fov),
            dict(t="END", lat=lat2 or lat, lon=lon2 or lon, dist=dist2 or dist, heading=heading if heading2 is None else heading2,
                 pitch=pitch2 or pitch, fov=fov, ease="sine")]


TOAN = cam(21.375, 103.02, 22, 10, 60, dist2=20, heading2=6)
TRUNG_TAM = cam(21.389, 103.016, 9.5, 290, 52, dist2=8, heading2=282)
HAM_PHAO_TA = [dict(lat=21.43, lon=103.052), dict(lat=21.45, lon=103.03), dict(lat=21.41, lon=103.07), dict(lat=21.37, lon=103.065),
               dict(lat=21.44, lon=102.975), dict(lat=21.35, lon=103.055), dict(lat=21.455, lon=103.0)]
GIA = [dict(lat=21.425, lon=103.062), dict(lat=21.39, lon=103.075), dict(lat=21.46, lon=103.015), dict(lat=21.36, lon=103.07)]
DAI_DOAN = [("ĐẠI ĐOÀN 308", 21.445, 102.965), ("ĐẠI ĐOÀN 312", 21.45, 103.06), ("ĐẠI ĐOÀN 316", 21.385, 103.075),
            ("ĐẠI ĐOÀN 304", 21.31, 103.035), ("ĐẠI ĐOÀN 351", 21.425, 103.09)]
C1 = dict(lat=21.3868, lon=103.0196, label="ĐỒI C1", sub="vị trí minh họa", side="dich")
TRENCH_SB = [dict(path=[[21.3975, 102.986], [21.397, 102.998], [21.397, 103.0075]], style="trench", width=45),
             dict(path=[[21.3965, 103.03], [21.397, 103.018], [21.397, 103.0085]], style="trench", width=45)]


def tran_dia(from_=0.2, gia=False, chop=None):
    pts = [dict(lat=p["lat"], lon=p["lon"], side="ta", noLabel=True, from_=from_ + i * 0.08, size=22) for i, p in enumerate(HAM_PHAO_TA)]
    if gia:
        pts += [dict(lat=p["lat"], lon=p["lon"], side="ta", noLabel=True, from_=gia, size=22) for p in GIA]
    fl = []
    if chop is not None:
        fl = [dict(lat=p["lat"], lon=p["lon"], at=chop + i * 0.07, count=3, every=0.25, size=110) for i, p in enumerate(HAM_PHAO_TA + (GIA if gia else []))]
    return pts, fl


BD = {
    # ---- Mở
    "MO08": dict(base="shot-a-toan-canh"),
    "MO21": dict(camera=TOAN, routes=[dict(path=[[21.33, 103.16], [21.37, 103.08], [21.397, 103.008]], style="route", from_=0.3, dur=2.0, width=50, label="ĐƯỜNG TRỜI", labelAt=0.5, labelFrom=1.2)],
                 points=[dict(id="sanbay", from_=0.2, size=26)]),
    "MO23": dict(camera=cam(21.385, 103.012, 14, 0, 58, dist2=12), zones=[dict(id=z, from_=0.2 + i * 0.25, color=XANH) for i, z in enumerate(("bac", "trungtam", "nam"))],
                 points=[dict(id=p, from_=0.9 + i * 0.1, noLabel=True) for i, p in enumerate(("himlam", "doclap", "bankeo", "a1", "d1", "e2", "ham", "sanbay", "hongcum"))]),
    "MO24": dict(camera=cam(21.40, 103.035, 20, 300, 56, heading2=292), pts_tran_dia=dict(from_=0.3), rings=[dict(lat=21.43, lon=103.052, from_=1.0, radius=900, color=DO)]),
    "MO25": dict(camera=TRUNG_TAM, routes=[dict(path="hao-ngoai", style="trench", from_=0.2, dur=1.6, width=45), dict(path="hao-trong", style="trench", from_=1.2, dur=1.6, width=45)] + [dict(r, from_=2.0 + i * 0.3, dur=1.0) for i, r in enumerate(TRENCH_SB)]),
    "MO28": dict(base="shot-a-toan-canh", camera=[dict(t=0, lat=21.388, lon=103.014, dist=12, heading=27, pitch=33, fov=40), dict(t="END", lat=21.33, lon=103.05, dist=55, heading=12, pitch=56, fov=40, ease="inOut")], points=[]),
    # ---- Ch1
    "C1-12": dict(camera=TOAN, points=[dict(id="dbp", from_=0.3, size=34, lift=60)]),
    "C1-13": dict(camera=cam(21.38, 103.012, 26, 0, 86, dist2=24), routes=[
        dict(path=[[21.455, 103.012], [21.296, 103.012]], style="route", from_=0.2, dur=1.6, width=55, label="18 KM", labelAt=0.25, labelFrom=1.0),
        dict(path=[[21.385, 102.978], [21.385, 103.045]], style="route", from_="@35:9", dur=1.0, width=55, label="6–8 KM", labelAt=0.8, labelFrom="@35:10")]),
    "C1-17": dict(camera=TOAN, zones=[dict(id="trungtam", from_=0.2, color=XANH)], routes=[
        dict(path=p, style="attack", from_=0.5 + i * 0.35, dur=1.4) for i, p in enumerate([[[21.48, 102.97], [21.43, 102.99], [21.40, 103.0]], [[21.47, 103.08], [21.42, 103.05], [21.395, 103.02]], [[21.32, 103.09], [21.36, 103.05], [21.385, 103.025]]])],
        rings=[dict(id="dbp", from_=1.8, radius=3000, color="#5d86b8")]),
    "C1-20": dict(camera=cam(21.38, 103.02, 20, 30, 58, heading2=36), points=[dict(id="dbp", from_=0.2, size=34, lift=60)]),
    "C1-25": dict(camera=[dict(t=0, lat=21.39, lon=103.015, dist=14, heading=20, pitch=50, fov=40), dict(t="END", lat=21.39, lon=103.012, dist=5, heading=28, pitch=30, fov=40, ease="inOut")]),
    # ---- Ch2
    "C2-05": dict(base="shot-b-ba-phan-khu"),
    "C2-13": dict(camera=cam(21.385, 103.014, 13, 340, 55, dist2=11, heading2=350), zones=[dict(id=z, from_=0.1, color=XANH) for z in ("bac", "trungtam", "nam")],
                  points=[dict(id=p, from_=0.2 + i * 0.12, noLabel=True) for i, p in enumerate(("himlam", "doclap", "bankeo", "a1", "d1", "e2", "ham", "sanbay", "hongcum"))],
                  rings=[dict(id=p, from_=0.8 + i * 0.1, radius=260, color="#5d86b8") for i, p in enumerate(("himlam", "doclap", "bankeo", "a1", "d1", "e2", "ham", "sanbay", "hongcum"))]),
    "C2-17": dict(camera=cam(21.37, 103.01, 15, 0, 58, dist2=13), points=[dict(id="sanbay", from_=0.2), dict(id="hongcum", from_=0.6, label="SÂN BAY HỒNG CÚM")],
                  rings=[dict(id="sanbay", from_=0.4, radius=500, color="#e5a93b"), dict(id="hongcum", from_=0.8, radius=500, color="#e5a93b")]),
    "C2-25": dict(copy="C2-13", camera=cam(21.375, 103.03, 16, 300, 50, heading2=292)),
    # ---- Ch3
    "C3-02": dict(base="shot-c-keo-phao", route_scale=0.45),
    "C3-06": dict(base="shot-c-keo-phao", camera=cam(21.475, 103.098, 15, 300, 56, heading2=310)),
    "C3-13": dict(camera=TOAN, points=[dict(lat=la, lon=lo, label=t, sub="vị trí minh họa", side="ta", from_=0.3 + i * 0.25, size=24) for i, (t, la, lo) in enumerate(DAI_DOAN)],
                  zones=[dict(id="trungtam", from_=0.1, color=XANH)]),
    "C3-19": dict(camera=cam(21.389, 103.014, 18, 20, 60, dist2=15), exposure=0.55, saturation=0.25),
    "C3-23": dict(camera=TRUNG_TAM, zones=[dict(id="trungtam", from_=0, color=XANH)],
                  points=[dict(id=p, from_=0.2 + i * 0.12, noLabel=True) for i, p in enumerate(("a1", "d1", "e2", "ham", "sanbay"))]
                  + [dict(lat=21.384 + (i % 4) * 0.004, lon=102.998 + (i // 4) * 0.006, side="dich", noLabel=True, from_=0.8 + i * 0.07, size=16) for i, _ in enumerate(range(16))]),
    "C3-34": dict(camera=cam(21.40, 103.03, 21, 320, 58, heading2=312), pts_tran_dia=dict(from_=0.2)),
    "C3-36": dict(camera=cam(21.40, 103.035, 18, 290, 52, heading2=282), pts_tran_dia=dict(from_=-1, gia="@110:5"),
                  rings=[dict(lat=p["lat"], lon=p["lon"], from_="@110:6", radius=350, color=DO) for p in GIA]),
    # ---- Ch4
    "C4-03": dict(base="shot-d-dot-1", cut=(0, 3.2), pts_tran_dia=dict(from_=0, chop=0.1)),
    "C4-06": dict(camera=cam(21.41, 103.035, 19, 300, 54, heading2=296), pts_tran_dia=dict(from_=0, gia=0, chop=0.3)),
    "C4-11": dict(base="shot-d-dot-1", cut=(1.6, 5.2)),
    "C4-13": dict(base="shot-d-dot-1", cut=(5.0, 9.0)),
    "C4-20": dict(camera=TOAN, routes=[dict(path=[[21.45, 102.98], [21.46, 103.05], [21.40, 103.08], [21.33, 103.05], [21.33, 102.98], [21.40, 102.96], [21.45, 102.98]],
                                             style="route", from_=0.2, dur=4.2, width=40, label="MÁY BAY TRINH SÁT", labelAt=0.1, labelFrom=0.8)]),
    "C4-26": dict(camera=cam(21.395, 103.008, 6, 0, 60, dist2=5), points=[dict(id="sanbay", from_=0, hit=0.6)]),
    "C4-29": dict(base="shot-e-dot-2-hao"),
    "C4-31": dict(base="shot-e-dot-2-hao", cut=(4.5, 9.0), points=[dict(C1, from_="@140:9"), dict(id="e2", from_="@140:11"), dict(id="d1", from_="@140:12"), dict(id="a1", from_="@140:14")]),
    "C4-37": dict(camera=cam(21.389, 103.012, 12, 0, 62, dist2=10), routes=[dict(path=p, style="trench", from_=0.1 + i * 0.25, dur=1.4, width=45) for i, p in enumerate(("hao-ngoai", "hao-trong", "hao-e2", "hao-d1", "hao-a1"))] + TRENCH_SB),
    "C4-41": dict(copy="C4-37", camera=cam(21.389, 103.014, 8, 270, 50, dist2=6.5, heading2=262), zones=[dict(id="trungtam", from_=0, color=XANH)]),
    # ---- Ch5
    "C5-12": dict(camera=cam(21.397, 103.008, 5, 340, 55, dist2=4.2), points=[dict(id="sanbay", from_=0)],
                  routes=[dict(r, from_=0.2 + i * 0.2, dur=2.2) for i, r in enumerate(TRENCH_SB)]),
    "C5-21": dict(base="shot-f-dot-3-a1", points=[dict(id="a1", from_=0.2), dict(C1, from_=0.4)],
                  rings=[dict(id="a1", from_=0.6, radius=220, color=DO), dict(lat=C1["lat"], lon=C1["lon"], from_=0.8, radius=220, color=DO)]),
    "C5-24": dict(camera=cam(21.392, 103.03, 11, 250, 45, heading2=244), exposure=0.6,
                  routes=[dict(path=[[21.43, 103.07], [21.405, 103.04], [21.389, 103.014]], style="attack", from_=0.1 + i * 0.25, dur=0.6, width=18) for i in range(4)]),
    "C5-32": dict(camera=cam(21.389, 103.013, 10, 0, 55, dist2=8), zones=[dict(id="trungtam", from_=0, color=XANH)],
                  routes=[dict(path=p, style="attack", from_=0.2 + i * 0.2, dur=1.5) for i, p in enumerate([
                      [[21.42, 103.0], [21.40, 103.008]], [[21.40, 103.05], [21.39, 103.025]], [[21.36, 103.035], [21.378, 103.02]],
                      [[21.36, 102.99], [21.378, 103.0]], [[21.41, 102.985], [21.395, 102.998]]])]),
    "C5-33": dict(copy="MO25", camera=cam(21.392, 103.02, 16, 330, 58, dist2=14), pts_tran_dia=dict(from_=0.1)),
    "C6-08": dict(copy="C3-13", camera=cam(21.38, 103.025, 20, 340, 56, heading2=332)),
    "C6-19": dict(camera=TOAN, routes=[dict(path=[[21.33, 103.16], [21.37, 103.08], [21.397, 103.008]], style="route", from_=0, dur=0.01, width=50, label="ĐƯỜNG TRỜI", labelAt=0.5, labelFrom=0, fadeAt=0.3),
                                       dict(path=[[21.52, 103.14], [21.47, 103.09], [21.43, 103.052]], style="route", from_="@203", dur=2.0, width=60, label="ĐƯỜNG XE THỒ", labelAt=0.4, labelFrom="@203:3",
                                            troops=dict(kind="file", count=5, size=28, gap=26))]),
    # ---- Kết
    "KT-01": dict(base="shot-g-ket-ham", titles=[]),
    "KT-12": dict(copy="MO23", camera=cam(21.383, 103.012, 16, 10, 60, dist2=14)),
    "KT-14": dict(copy="C5-12", camera=cam(21.397, 103.008, 6.5, 20, 58, dist2=5)),
    "KT-18": dict(base="shot-c-keo-phao", camera=cam(21.48, 103.10, 16, 312, 54, dist2=14.5, heading2=322)),
}
VN = {
    "C1-02": dict(camera=[dict(t=0, lon=106.5, lat=15.0, zoom=52), dict(t="END", lon=106.0, lat=16.0, zoom=58, ease="sine")],
                  markers=[dict(lon=103.012, lat=21.388, label="ĐIỆN BIÊN PHỦ", from_="@25:25", size=26)]),
    "C1-06": dict(camera=[dict(t=0, lon=106.0, lat=16.0, zoom=58), dict(t="END", lon=106.2, lat=16.4, zoom=62, ease="sine")],
                  markers=[dict(lon=lo, lat=la, label="", from_=0.3 + i * 0.12, size=16) for i, (lo, la) in enumerate(
                      [(105.8, 21.0), (106.3, 20.6), (106.1, 21.3), (105.6, 20.4), (106.5, 20.2), (105.9, 19.4), (106.6, 17.0), (107.2, 16.2), (105.8, 15.9), (108.2, 14.0), (106.7, 10.8), (105.9, 10.2)])]),
    "C1-07": dict(base="vn-a-bay-xuong-dbp"),
    "C1-08": dict(camera=[dict(t=0, lon=104.0, lat=21.0, zoom=470), dict(t="END", lon=103.6, lat=21.2, zoom=500, ease="sine")],
                  labels=[dict(text="TÂY BẮC", lon=103.6, lat=21.8, kind="vn", from_=0.3), dict(text="LÀO", lon=102.4, lat=20.3, kind="nuoc", from_=0.5)],
                  markers=[dict(lon=103.012, lat=21.388, label="ĐIỆN BIÊN PHỦ", from_=0.6, size=30)]),
    "C1-14": dict(camera=[dict(t=0, lon=103.4, lat=20.9, zoom=480), dict(t="END", lon=103.2, lat=20.6, zoom=470, ease="sine")],
                  labels=[dict(text="THƯỢNG LÀO", lon=102.6, lat=20.2, kind="nuoc", from_=0.4)],
                  markers=[dict(lon=103.012, lat=21.388, label="ĐIỆN BIÊN PHỦ", from_=0, size=30)]),
    "C2-15": dict(camera=[dict(t=0, lon=106.0, lat=17.5, zoom=60), dict(t="END", lon=105.6, lat=18.2, zoom=66, ease="sine")],
                  markers=[dict(lon=105.85, lat=21.03, label="HÀ NỘI", from_=0.3, size=26, dy=40), dict(lon=103.012, lat=21.388, label="ĐIỆN BIÊN PHỦ", from_=0.6, size=26, dx=-250, dy=-30)]),
    "C6-07": dict(camera=[dict(t=0, lon=103.5, lat=21.0, zoom=480), dict(t="END", lon=103.3, lat=21.2, zoom=520, ease="sine")],
                  labels=[dict(text="TÂY BẮC", lon=103.6, lat=21.9, kind="vn", from_=0.2)],
                  markers=[dict(lon=103.012, lat=21.388, label="ĐIỆN BIÊN PHỦ", from_=0.2, size=30)]),
    "KT-16": dict(camera=[dict(t=0, lon=107.5, lat=15.5, zoom=62), dict(t="END", lon=107.2, lat=15.2, zoom=52, ease="sine")]),
}


def giai(v, t0, end):
    if v == "END":
        return round(end, 3)
    if isinstance(v, str) and v.startswith("@"):
        n, _, k = v[1:].partition(":")
        return round(MOC["cau"][int(n) - 1][int(k or 0)] - t0, 3)
    if isinstance(v, dict):
        return {("from" if k == "from_" else k): giai(x, t0, end) for k, x in v.items()}
    if isinstance(v, list):
        return [giai(x, t0, end) for x in v]
    return v


def nap_goc(khoi, ten):
    """Đọc window.SHOT của shot gốc (đối tượng JS đơn giản → JSON qua node)."""
    js = (TPL / khoi / "shots" / f"{ten}.js").read_text(encoding="utf-8")
    out = subprocess.run(["node", "-e", "const window={};" + js + ";process.stdout.write(JSON.stringify(window.SHOT))"], capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return json.loads(out)


def cau_hinh(ma):
    c = CANH[ma]
    f0, f1 = round(c["t0"] * FPS), round(c["t1"] * FPS)
    d = (f1 - f0) / FPS
    khoi = c["kieu"]
    spec = dict((BD if khoi == "map3d" else VN)[ma])
    while "copy" in spec:
        goc = dict((BD if khoi == "map3d" else VN)[spec.pop("copy")])
        goc.update(spec)
        spec = goc
    s = {}
    if "base" in spec:
        s = nap_goc(khoi, spec.pop("base"))
        a, b = spec.pop("cut", (0, s["duration"]))
        s["fit"] = d * s["duration"] / (b - a)  # co cả shot gốc rồi cắt đoạn [a, b] bằng --from/--to
        s["_cat"] = (a * s["fit"] / s["duration"], b * s["fit"] / s["duration"])
        r = spec.pop("route_scale", None)
        if r:  # chỉ lấy phần đầu shot gốc: co để tỉ lệ r của shot vừa đúng thời lượng cảnh
            s["fit"], s["_cat"] = d / r, (0, d)
        s.pop("date", None)
    spec.pop("cut", None)
    td = spec.pop("pts_tran_dia", None)
    s.update(giai(spec, f0 / FPS, d))
    if td is not None:
        g = lambda k, mac: giai(td.get(k, mac), f0 / FPS, d)
        pts, fl = tran_dia(from_=g("from_", 0.2), gia=g("gia", False), chop=g("chop", None))
        s["points"] = s.get("points", []) + giai(pts, 0, d)
        s["flashes"] = s.get("flashes", []) + giai(fl, 0, d)
    s.setdefault("duration", d)
    if "fit" not in s:
        s["duration"] = d
    so = c["ghi_nguon"].split("Số liệu: ")[1] if "Số liệu: " in c["ghi_nguon"] else ""
    s["credit"] = NEN[khoi] + (f" · Số liệu: {so}" if so else "")
    if khoi == "vnmap":
        s["mau"] = "quan-su"  # v2: bản đồ tham mưu in giấy (màu lịch sử, quân sự)
    s.pop("date", None)
    return s, f1 - f0


def main():
    ma = [c["id"] for c in PC["canh"] if c["kieu"] in ("map3d", "vnmap")]
    lech = sorted(set(ma) ^ (set(BD) | set(VN)))
    if lech:
        sys.exit(f"BD/VN lệch bảng phân cảnh: {lech}")
    chon = [a for a in sys.argv[1:] if not a.startswith("--")] or ma
    RA.mkdir(parents=True, exist_ok=True)
    for m in chon:
        s, _ = cau_hinh(m)
        khoi = CANH[m]["kieu"]
        thu = TPL / khoi / "shots" / "dbp1"
        thu.mkdir(exist_ok=True)
        cat = s.pop("_cat", None)
        (thu / f"{m}.js").write_text("// Sinh bởi tap/EP001-dien-bien-phu-1954/san-xuat/dung-ban-do.py, đừng sửa tay.\nwindow.SHOT = "
                                     + json.dumps(s, ensure_ascii=False) + ";\n", encoding="utf-8")
        (thu / f"{m}.cat.json").write_text(json.dumps(cat), encoding="utf-8")
    for k in ("map3d", "vnmap"):
        subprocess.run([sys.executable, "-I", str(TPL / "tools" / "build_shots.py"), k], check=True, capture_output=True)
    for m in chon:
        khoi = CANH[m]["kieu"]
        _, n = cau_hinh(m)
        cat = json.loads((TPL / khoi / "shots" / "dbp1" / f"{m}.cat.json").read_text())
        a = cat[0] if cat else 0
        trang = TPL / khoi / f"dbp1-{m}.html"
        if "--stills" in sys.argv:
            subprocess.run([*DUNG_TRANG, str(trang), "--stills", f"{a + 0.3:.2f},{a + n / FPS * 0.6:.2f},{a + n / FPS - 0.1:.2f}",
                            "--out-dir", str(RA.parent / "story" / "ban-do" / m)], check=True, capture_output=True)
        if "--render" in sys.argv:
            ra = RA / f"{m}.mp4"
            lenh = [*DUNG_TRANG, str(trang), "--out", str(ra), "--fps", str(FPS), "--force"]
            if cat:
                lenh += ["--from", f"{a:.4f}", "--to", f"{a + n / FPS:.4f}"]
            subprocess.run(lenh, check=True, capture_output=True)
            so = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets",
                                 "-of", "csv=p=0", str(ra)], capture_output=True, text=True).stdout.strip().rstrip(",")
            print(f"{m}: {so} khung (cần {n}){'' if int(so) == n else '  LỆCH'}", flush=True)
    print(f"{len(chon)} cảnh bản đồ xong")


if __name__ == "__main__":
    main()
