# -*- coding: utf-8 -*-
"""
kiem-nhip-hinh.py — máy kiểm nhịp hình của người dùng (rieng/, kit không ghi vào), chạy ở cuối P3 và trước render P5.

  python -I -X utf8 rieng/tools/kiem-nhip-hinh.py tap/<EPxxx-slug> [--hinh <thư mục Sxxx.mp4>] [--sheet <thư mục ra>] [--md <tệp báo cáo>]

Đọc san-xuat/phan-canh.json; chương lấy từ ke-hoach/chuong.tsv (tên<TAB>câu đầu<TAB>câu cuối) nếu có,
không thì từ hằng CHUONG trong san-xuat/kiem-phan-canh.py. Ngưỡng: rieng/tools/nguong-nhip-hinh.toml.
Kiểm:
  1. dùng lại: clip, ảnh (số lần + khoảng cách), thẻ chữ đúng 1 lần, cặp [bản đồ + góc máy], bản đồ mỗi chương
  2. dòng chảy hình thật: khoảng dài nhất không có hình thật, tỉ lệ hình thật, hai cảnh thật liền nhau khác cỡ
  3. kho: số ảnh + clip khác nhau mỗi phút
  4. nhịp: cảnh/phút cả tập (chặn) và từng chương (cảnh báo)
  5. (--hinh) lặp hình bằng dHash khung giữa mọi cảnh; (--sheet) một contact sheet mỗi chương để soi bằng mắt
Mã ra: 0 = đạt, 1 = có lỗi CHẶN, 2 = lỗi dữ liệu đầu vào.
"""
import ast, csv, json, subprocess, sys, tomllib
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
NGUONG = Path(__file__).resolve().parent / "nguong-nhip-hinh.toml"


def doc_chuong(tap):
    t = tap / "ke-hoach" / "chuong.tsv"
    if t.exists():
        return [(r[0], int(r[1]), int(r[2])) for r in csv.reader(open(t, encoding="utf-8"), delimiter="\t") if r and not r[0].startswith("#")]
    k = tap / "san-xuat" / "kiem-phan-canh.py"
    if k.exists():
        for nut in ast.parse(k.read_text(encoding="utf-8")).body:
            if isinstance(nut, ast.Assign) and any(getattr(x, "id", "") == "CHUONG" for x in nut.targets):
                return [tuple(x) for x in ast.literal_eval(nut.value)]
    return []


def gan_chuong(canh, CH):
    """mã cảnh → tên chương theo câu đầu của cảnh; cảnh không gắn câu (khoảng lặng) theo cảnh trước."""
    ra, cur = {}, (CH[0][0] if CH else "cả tập")
    for c in canh:
        n = (c.get("cau") or [None])[0]
        if n is not None:
            for ten, a, b in CH:
                if a <= n <= b:
                    cur = ten
                    break
        ra[c["id"]] = cur
    return ra


def kiem(canh, CH, N, het=None):
    """trả (chặn, cảnh báo, số đo) — hàm thuần để thử đột biến."""
    chan, bao, so = [], [], {}
    D, F, K, NH = N["dung_lai"], N["dong_chay"], N["kho"], N["nhip"]
    that, bdo = set(N["kieu_that"]), set(N["kieu_ban_do"])
    het = het or (canh[-1]["t1"] if canh else 0)
    CHM = gan_chuong(canh, CH)
    phut = het / 60 if het else 0

    # 1. dùng lại
    lan = defaultdict(list)
    for c in canh:
        lan[(c["kieu"], c["ten"])].append(c)
    for (kieu, ten), ds in lan.items():
        if kieu == "clip":
            if len(ds) > D["clip_toi_da"]:
                chan.append(f"[dùng lại] clip {ten} dùng {len(ds)} lần (tối đa {D['clip_toi_da']}): {', '.join(x['id'] for x in ds)}")
            for a, b in zip(ds, ds[1:]):
                if b["t0"] - a["t1"] < D["clip_cach_giay"]:
                    chan.append(f"[dùng lại] clip {ten}: {a['id']} → {b['id']} cách {b['t0'] - a['t1']:.0f} s < {D['clip_cach_giay']} s")
        elif kieu == "anh":
            if len(ds) > D["anh_toi_da"]:
                chan.append(f"[dùng lại] ảnh {ten} dùng {len(ds)} lần (tối đa {D['anh_toi_da']}): {', '.join(x['id'] for x in ds)}")
            for a, b in zip(ds, ds[1:]):
                if b["t0"] - a["t1"] < D["anh_cach_giay"]:
                    chan.append(f"[dùng lại] ảnh {ten}: {a['id']} → {b['id']} cách {b['t0'] - a['t1']:.0f} s < {D['anh_cach_giay']} s")
        elif kieu == "the" and len(ds) > D["the_toi_da"]:
            chan.append(f"[dùng lại] thẻ {ten} dùng {len(ds)} lần (tối đa {D['the_toi_da']}): {', '.join(x['id'] for x in ds)}")
    cap = Counter((c["ten"], c.get("goc")) for c in canh if c["kieu"] in bdo)
    for (ten, goc), n in sorted(cap.items(), key=lambda x: -x[1]):
        if n > D["cap_ban_do_goc_toi_da"]:
            chan.append(f"[3D] cặp [{ten} + {goc}] dùng {n} lần (tối đa {D['cap_ban_do_goc_toi_da']})")
    # trần mỗi bản đồ trong một chương: theo độ dài chương (ban_do_moi_phut_chuong), không dưới ban_do_moi_chuong
    dai_ch = defaultdict(float)
    for c in canh:
        dai_ch[CHM[c["id"]]] += c["t1"] - c["t0"]
    def tran_ch(ch):
        return max(D["ban_do_moi_chuong"], int(D.get("ban_do_moi_phut_chuong", 0) * dai_ch[ch] / 60))
    mc = Counter((CHM[c["id"]], c["ten"]) for c in canh if c["kieu"] in bdo)
    for (ch, ten), n in sorted(mc.items(), key=lambda x: -x[1]):
        if n > tran_ch(ch):
            chan.append(f"[3D] {ch} ({dai_ch[ch] / 60:.1f} phút): bản đồ {ten} có {n} cảnh (tối đa {tran_ch(ch)})")
    nbc = len({c["ten"] for c in canh if c["kieu"] in bdo})
    so["boi_canh_3d"] = nbc
    can_bc = D.get("boi_canh_moi_phut", 0) * phut
    if nbc and nbc < can_bc:
        chan.append(f"[3D] chỉ có {nbc} bản đồ/bối cảnh 3D khác nhau, cần ≥ {can_bc:.0f} ({D['boi_canh_moi_phut']}/phút)")

    # 2. dòng chảy hình thật
    last, dai, o = 0.0, 0.0, None
    for c in canh:
        if c["kieu"] in that:
            if c["t0"] - last > dai:
                dai, o = c["t0"] - last, (last, c["t0"], c["id"])
            last = c["t1"]
    if het - last > dai:
        dai, o = het - last, (last, het, "hết phim")
    so["khoang_khong_that"] = round(dai, 1)
    last = 0.0
    for c in canh:
        if c["kieu"] in that:
            g = c["t0"] - last
            if g > F["khoang_khong_that_giay"]:
                chan.append(f"[dòng chảy] {last:.1f}–{c['t0']:.1f} s: {g:.1f} s không có hình thật (tối đa {F['khoang_khong_that_giay']} s), trước {c['id']}")
            last = c["t1"]
    if het - last > F["khoang_khong_that_giay"]:
        chan.append(f"[dòng chảy] {last:.1f} s → hết phim: {het - last:.1f} s không có hình thật")
    tl = sum(1 for c in canh if c["kieu"] in that) / len(canh) if canh else 0
    so["ty_le_that"] = round(tl, 3)
    if not (F["ty_le_that_min"] <= tl <= F["ty_le_that_max"]):
        chan.append(f"[dòng chảy] tỉ lệ hình thật {tl:.0%} ngoài khoảng {F['ty_le_that_min']:.0%}–{F['ty_le_that_max']:.0%}")
    if F.get("cam_lien_cung_co", True):
        for a, b in zip(canh, canh[1:]):
            if a["kieu"] in that and b["kieu"] in that and a.get("co") == b.get("co"):
                chan.append(f"[dòng chảy] {a['id']} → {b['id']}: hai cảnh hình thật liền nhau cùng cỡ «{a.get('co')}»")

    # 3. kho
    khac = len({(c["kieu"], c["ten"]) for c in canh if c["kieu"] in that})
    mp = khac / phut if phut else 0
    so["tai_san_khac_nhau"], so["tai_san_moi_phut"] = khac, round(mp, 2)
    if mp < K["tai_san_moi_phut"]:
        chan.append(f"[kho] {khac} ảnh + clip khác nhau = {mp:.2f}/phút < {K['tai_san_moi_phut']}/phút (cần ≥ {K['tai_san_moi_phut'] * phut:.0f})")

    # 4. nhịp
    cpm = len(canh) / phut if phut else 0
    so["canh_moi_phut"] = round(cpm, 1)
    if cpm < NH["canh_moi_phut"]:
        chan.append(f"[nhịp] {cpm:.1f} cảnh/phút < {NH['canh_moi_phut']}")
    theo = defaultdict(list)
    for c in canh:
        theo[CHM[c["id"]]].append(c)
    for ch, ds in theo.items():
        g = ds[-1]["t1"] - ds[0]["t0"]
        if g > 20 and len(ds) / (g / 60) < NH["canh_moi_phut_chuong"]:
            bao.append(f"[nhịp] {ch}: {len(ds) / (g / 60):.1f} cảnh/phút < {NH['canh_moi_phut_chuong']}")
    return chan, bao, so


# ------------------------------------------------------------------ lặp hình (pixel)
def khung_giua(canh, hinh, cache):
    from PIL import Image
    cache.mkdir(parents=True, exist_ok=True)
    ra = {}
    for c in canh:
        v, j = hinh / f"{c['id']}.mp4", cache / f"{c['id']}.jpg"
        if not v.exists():
            continue
        if not j.exists() or j.stat().st_mtime < v.stat().st_mtime:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.0, c['dai'] / 2):.3f}", "-i", str(v), "-frames:v", "1", "-vf", "scale=480:-2", str(j)], check=False)
        if j.exists():
            ra[c["id"]] = Image.open(j).convert("RGB")
    return ra


def dhash(im, n=16):
    g = im.convert("L").resize((n + 1, n))
    p = list(g.tobytes())
    return [1 if p[r * (n + 1) + x] > p[r * (n + 1) + x + 1] else 0 for r in range(n) for x in range(n)]


def lap_hinh(canh, khung, N):
    L = N["lap_hinh"]
    hs = {k: dhash(v) for k, v in khung.items()}
    bits = 256
    lap, cap = [], []
    truoc = []
    for c in canh:
        h = hs.get(c["id"])
        if h is None:
            continue
        gan = None
        for i, h2 in truoc:
            d = sum(a != b for a, b in zip(h, h2)) / bits
            if d <= L["nguong_hash"]:
                gan = (i, d)
                break
        if gan:
            lap.append(c["id"]); cap.append((c["id"], gan[0], gan[1]))
        truoc.append((c["id"], h))
    tl = len(lap) / len(hs) if hs else 0
    return tl, cap, len(hs)


def contact_sheet(canh, khung, CH, ra):
    from PIL import Image, ImageDraw
    ra.mkdir(parents=True, exist_ok=True)
    theo, CHM = defaultdict(list), gan_chuong(canh, CH)
    for c in canh:
        theo[CHM[c["id"]]].append(c)
    tep = []
    for i, (ch, ds) in enumerate(theo.items(), 1):
        ds = [c for c in ds if c["id"] in khung]
        if not ds:
            continue
        cot, w, h = 8, 240, 135
        hang = (len(ds) + cot - 1) // cot
        m = Image.new("RGB", (cot * w, hang * (h + 18) + 30), (17, 17, 17))
        d = ImageDraw.Draw(m)
        d.text((6, 6), f"{ch} · {len(ds)} cảnh", fill=(240, 232, 216))
        for j, c in enumerate(ds):
            x, y = (j % cot) * w, 30 + (j // cot) * (h + 18)
            m.paste(khung[c["id"]].resize((w - 4, h)), (x + 2, y))
            d.text((x + 4, y + h + 2), f"{c['id']} {c['kieu']}:{c['ten']}"[:34], fill=(207, 200, 186))
        p = ra / f"sheet-{i:02d}.jpg"; m.save(p, quality=82); tep.append(p)
    return tep


def main():
    a = sys.argv[1:]
    if not a or a[0].startswith("-"):
        print(__doc__); return 2
    tap = Path(a[0])
    pj = tap / "san-xuat" / "phan-canh.json"
    if not pj.exists():
        print(f"Không thấy {pj}"); return 2
    PC = json.loads(pj.read_text(encoding="utf-8"))
    canh = PC["canh"]
    CH = doc_chuong(tap)
    N = tomllib.loads(NGUONG.read_text(encoding="utf-8"))
    chan, bao, so = kiem(canh, CH, N, PC.get("het"))
    dong = [f"# Kiểm nhịp hình · {PC.get('ten', tap.name)}", "",
            f"- {len(canh)} cảnh, {so['canh_moi_phut']} cảnh/phút; hình thật {so['ty_le_that']:.0%}; khoảng không hình thật dài nhất {so['khoang_khong_that']} s",
            f"- {so['tai_san_khac_nhau']} ảnh + clip khác nhau ({so['tai_san_moi_phut']}/phút); chương: {len(CH) or 'không đọc được (tính cả tập là một chương)'}"]
    if "--hinh" in a or "--sheet" in a:
        hinh = Path(a[a.index("--hinh") + 1]) if "--hinh" in a else None
        if not hinh or not hinh.is_dir():
            print("--hinh <thư mục chứa Sxxx.mp4> là bắt buộc cho lặp hình / contact sheet"); return 2
        khung = khung_giua(canh, hinh, hinh.parent / "_nhip-hinh" / hinh.name)
        thieu = len(canh) - len(khung)
        tl, cap, n = lap_hinh(canh, khung, N)
        dong.append(f"- lặp hình (dHash khung giữa, ≤ {N['lap_hinh']['nguong_hash']:.0%} bit khác): {tl:.0%} của {n} cảnh" + (f"; thiếu video {thieu} cảnh" if thieu else ""))
        if tl > N["lap_hinh"]["ty_le_lap_max"]:
            chan.append(f"[lặp hình] {tl:.0%} cảnh trông giống một cảnh trước (tối đa {N['lap_hinh']['ty_le_lap_max']:.0%}); ví dụ: "
                        + ", ".join(f"{x}≈{y}" for x, y, _ in cap[:12]))
        if thieu:
            bao.append(f"[lặp hình] thiếu video {thieu} cảnh, chưa so được")
        if "--sheet" in a:
            for p in contact_sheet(canh, khung, CH, Path(a[a.index("--sheet") + 1])):
                dong.append(f"- contact sheet: {p}")
    dong += ["", f"## CHẶN: {len(chan)}"] + [f"- {x}" for x in chan] + ["", f"## Cảnh báo: {len(bao)}"] + [f"- {x}" for x in bao]
    dong.append("")
    dong.append("KẾT QUẢ: " + ("ĐẠT" if not chan else f"KHÔNG ĐẠT ({len(chan)} lỗi chặn) — sửa phân cảnh rồi chạy lại trước khi render bản dài"))
    txt = "\n".join(dong)
    print(txt)
    if "--md" in a:
        Path(a[a.index("--md") + 1]).write_text(txt + "\n", encoding="utf-8")
    return 1 if chan else 0


if __name__ == "__main__":
    sys.exit(main())
