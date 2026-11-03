"""Kiểm phân cảnh tập theo template/chuan-dao-dien.md và luật cứng CLAUDE.md.

Đọc bảng trong phan-canh.md (nguồn sự thật), lời đọc ke-hoach/loi-doc-v5.txt, tư liệu anh.tsv.
Ghi phan-canh.json (cho P5), tai-san-can-dung.md và mục Tóm tắt trong phan-canh.md.
Giây: ước tính 242 tiếng/phút cho tới khi có moc-cau.json (mốc chữ thật sau P4:
{"cau": [[t_chữ_0, t_chữ_1, ...], ...], "het": t_cuối, "lang": {"P1": [t0, t1], ...}}).

Chạy: python -I kiem-phan-canh.py [--md <bảng khác>]   (thoát mã 1 nếu trượt luật)
"""
import csv, json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
MD = Path(sys.argv[sys.argv.index("--md") + 1]) if "--md" in sys.argv else GOC / "phan-canh.md"
LOI = GOC.parent / "ke-hoach" / "loi-doc-v5.txt"
MOC = GOC / "moc-cau.json"
TIENG_GIAY = 60 / 242
CHUONG = [("Mở", 1, 24), ("Ch1 Lòng chảo", 25, 49), ("Ch2 Con nhím", 50, 76), ("Ch3 Đổi cách đánh", 77, 113),
          ("Ch4 Pháo nổ, hào siết", 114, 152), ("Ch5 Lấy đi bầu trời", 153, 185), ("Ch6 Hai loại con số", 186, 205),
          ("Kết", 206, 223)]
NGUON_SO = ("Báo Nhân Dân", "Báo QĐND", "TTXVN", "Báo Chính phủ", "Tư liệu văn kiện Đảng", "VTV", "Báo Văn hóa")
KARMEN = "Phim «Việt Nam» (R. Karmen, 1955) · tư liệu có cảnh dựng lại · trích, tắt tiếng gốc"
CAM = {"navarre-time-cover-1953": "tranh bìa Time, bản quyền chưa rõ (C)",
       "operation-castor-1er-bep-05775": "ảnh màu khoá chờ xác minh tô màu", "operation-castor-1er-bep-05777": "ảnh màu khoá chờ xác minh tô màu",
       "giap-xem-ban-do-01": "ảnh lãnh tụ A? chưa khoá nguồn", "giap-duyet-phao-cao-xa-01": "ảnh lãnh tụ A? chưa khoá nguồn",
       "bac-ho-giap-hoach-dinh-01": "ảnh lãnh tụ A? chưa khoá nguồn", "cong-kenh-giap-mung-cong-01": "ảnh lãnh tụ A? chưa khoá nguồn",
       "bac-ho-gan-huy-hieu-hoang-dang-vinh-01": "ảnh lãnh tụ A? chưa khoá nguồn",
       "giao-thong-hao-cat-doi-san-bay-muong-thanh-01": "logo TTXVN đè giữa ảnh", "dao-hao-danh-dui-01": "logo TTXVN đè giữa ảnh",
       "geneve-phai-doan-vndch-khai-mac-01": "logo TTXVN đè giữa ảnh", "geneve-ky-hiep-dinh-dinh-chien-01": "logo TTXVN đè giữa ảnh",
       "dan-cong-vuot-suoi-01": "nguồn lưu trữ chưa xác minh"}
LANH_TU_ANH = {"bac-ho-bo-chinh-tri-quyet-dinh-mo-chien-dich-01"}
LANH_TU_LOI = ("Hồ Chí Minh", "Võ Nguyên Giáp", "Đại tướng")
KIEU = ("anh", "karmen", "3d", "3d-moi", "demo", "map3d", "vnmap", "the", "can-tim")
# Bản Demo đã duyệt chỉ có trên máy chủ kit; máy khác (tập mẫu trong kit) không có thì coi như chưa có cảnh 3D Demo nào.
_TEP_DEMO = Path(__file__).resolve().parents[2] / "dien-bien-phu-mau/san-xuat/ban-full/phan-canh.json"
_DEMO = json.loads(_TEP_DEMO.read_text(encoding="utf-8")) if _TEP_DEMO.exists() else {"canh": []}
DEMO_3D = {c["id"] for c in _DEMO["canh"] if c["nguon"] == "3d"}
# chuỗi Dốc Chuối của Demo (render bản thử v2, khung 1243–1619 của bản Demo cuối, demo.DOC_CHUOI) cũng dùng được
DEMO_3D |= {c["id"] for c in _DEMO["canh"] if c["nguon"].startswith("thu:") and 1243 <= c["khung"][0] and c["khung"][1] <= 1619}
SAN_KHAU = {"bau-troi", "san-bay", "ham-phap", "rung-nui", "rung-nua", "keo-phao", "tran-dia", "him-lam", "chien-hao",
            "a1-cat", "a1-dem", "a1-hom-nay", "hau-phuong"}
CO = {"dac-ta", "can", "trung", "toan", "toan-xa", "ban-do", "the", "anh", "phim"}
GOC_MAY = {"thap", "ngang", "cao", "tren-xuong", "chech", "cat-lop", "phang"}
loi_ = []


def sai(msg):
    loi_.append(msg)


# Lời đọc: câu có chữ đánh số 1..N; dòng trống giữa bài là khoảng lặng P1, P2, ...
cau, lang_md = [], {}
for dong in LOI.read_text(encoding="utf-8").rstrip("\n").split("\n"):
    if dong.strip():
        cau.append(dong.strip().split())
N = len(cau)

van = MD.read_text(encoding="utf-8")
for m in re.finditer(r"^\| ([A-Z][A-Z0-9]) \| (\S+) \| ([\d.]+) \|", van, re.M):
    lang_md[m[1]] = (m[2], float(m[3]))

# Dòng thời gian ước tính: chữ và khoảng lặng nối nhau; khoảng lặng "sau" một câu hoặc một khoảng lặng khác
sau_cau = {}
for ten, (sau, giay) in lang_md.items():
    sau_cau.setdefault(sau, []).append((ten, giay))
moc_chu, moc_lang, t = {}, {}, 0.0


def chen_lang(khoa):
    global t
    for ten, giay in sau_cau.get(khoa, []):
        moc_lang[ten] = (t, t + giay)
        t += giay
        chen_lang(ten)


that = json.loads(MOC.read_text(encoding="utf-8")) if MOC.exists() else None
for i, tu in enumerate(cau, 1):
    if that:
        moc_chu.update({(i, k): s for k, s in enumerate(that["cau"][i - 1])})
    else:
        for k in range(len(tu)):
            moc_chu[(i, k)] = t
            t += TIENG_GIAY
        chen_lang(str(i))
if that:
    moc_lang = {k: tuple(v) for k, v in that["lang"].items()}
    t = that["het"]
HET = t

# Tư liệu ảnh
ANH = {r["tep"]: r for r in csv.DictReader(open(GOC / "anh.tsv", encoding="utf-8"), delimiter="\t")}

# Bảng phân cảnh
bang = re.search(r"<!-- BANG -->\n(.*?)<!-- /BANG -->", van, re.S)
if not bang:
    sys.exit("phan-canh.md: không thấy cặp mốc <!-- BANG --> ... <!-- /BANG -->")
CANH = []
for dong in bang[1].splitlines()[2:]:
    o = [x.strip() for x in dong.strip()[1:-1].split("|")]
    if len(o) != 7:
        sai(f"dòng bảng không đủ 7 cột: {dong[:60]}")
        continue
    id_, neo, nguon, cg, hinh, chu, am = o
    co, _, goc = cg.partition("/")
    CANH.append(dict(id=id_, neo=neo, nguon=nguon, co=co, goc=goc, hinh=hinh, chu=chu, am=am))


def vi_tri(neo):
    """(giây bắt đầu, khoá thứ tự) của một neo."""
    if neo in moc_lang:
        return moc_lang[neo][0]
    m = re.fullmatch(r"(\d+)(?::(\d+))?", neo)
    if not m:
        return None
    i, k = int(m[1]), int(m[2] or 0)
    if not (1 <= i <= N and 0 <= k < len(cau[i - 1])):
        return None
    return moc_chu[(i, k)]


def cau_cua(t0, t1):
    """Số các câu có chữ nằm trong [t0, t1)."""
    return sorted({i for (i, k), s in moc_chu.items() if t0 - 1e-6 <= s < t1 - 1e-6})


ids = set()
for c in CANH:
    if c["id"] in ids:
        sai(f"{c['id']}: trùng mã cảnh")
    ids.add(c["id"])
    c["t0"] = vi_tri(c["neo"])
    if c["t0"] is None:
        sai(f"{c['id']}: neo '{c['neo']}' không có trong lời đọc hay bảng khoảng lặng")
if loi_:
    print("TRƯỢT:\n- " + "\n- ".join(loi_))
    sys.exit(1)

# 1. Neo tăng dần, cảnh đầu ở 0, cảnh cuối kéo tới hết
if CANH[0]["neo"] != "1":
    sai(f"{CANH[0]['id']}: cảnh đầu phải neo ở câu 1")
CANH[0]["t0"] = 0.0  # hình bắt đầu từ khung 0, kể cả hơi thở trước chữ đầu
for x, y in zip(CANH, CANH[1:]):
    if y["t0"] <= x["t0"] + 1e-6:
        sai(f"{x['id']} → {y['id']}: neo không tăng dần")
for x, y in zip(CANH, CANH[1:] + [None]):
    x["t1"] = y["t0"] if y else HET
    x["dai"] = round(x["t1"] - x["t0"], 2)
    x["cau"] = cau_cua(x["t0"], x["t1"])
phu = sorted({i for c in CANH for i in c["cau"]})
if phu != list(range(1, N + 1)):
    sai(f"lời đọc không phủ đủ {N} câu (thiếu {sorted(set(range(1, N + 1)) - set(phu))[:8]})")
for ten in moc_lang:
    # khoảng thở (tên T*…Z*): lời ngừng để bảng chữ gõ xong, cảnh trước giữ hình qua khoảng thở
    if ten[0] not in "TUVWXYZ" and not any(c["neo"] == ten for c in CANH):
        sai(f"khoảng lặng {ten}: không có cảnh nào neo vào (khoảng lặng phải có hình riêng)")

# 2. Kiểu nguồn, cỡ, góc, ghi nguồn trên hình
for c in CANH:
    kieu, _, ten = c["nguon"].partition(":")
    c["kieu"], c["ten"] = kieu, ten
    if kieu not in KIEU or not ten:
        sai(f"{c['id']}: nguồn hình '{c['nguon']}' không thuộc {KIEU}")
    if c["co"] not in CO or c["goc"] not in GOC_MAY:
        sai(f"{c['id']}: cỡ/góc '{c['co']}/{c['goc']}' không thuộc danh mục")
    c["hang"], c["ghi_nguon"] = "code", "Đồ họa minh họa"
    if kieu == "anh":
        if ten in CAM:
            sai(f"{c['id']}: tư liệu cấm dùng '{ten}' ({CAM[ten]})")
        elif ten not in ANH:
            sai(f"{c['id']}: ảnh '{ten}' chưa có trong anh.tsv")
        else:
            c["hang"], c["ghi_nguon"] = ANH[ten]["hang"], ANH[ten]["ghi_nguon"]
    elif kieu == "karmen":
        c["hang"], c["ghi_nguon"] = "B", KARMEN
        if not re.fullmatch(r"\d\d:\d\d(\.\d+)?", ten):
            sai(f"{c['id']}: mốc Karmen '{ten}' phải dạng mm:ss")
    elif kieu == "can-tim":
        c["hang"], c["ghi_nguon"] = "?", "chờ tư liệu có giấy phép"
        if "chưa có" not in c["hinh"]:
            sai(f"{c['id']}: tư liệu cần tìm phải ghi phương án thay ('chưa có …')")
    elif kieu == "demo" and ten.split("+")[0].rstrip(">") not in DEMO_3D:
        sai(f"{c['id']}: 'demo:{ten}' không phải cảnh 3D đã render của bản Demo")
    elif kieu == "3d-moi" and ten not in SAN_KHAU:
        sai(f"{c['id']}: sân khấu 3D '{ten}' không có trong danh mục {sorted(SAN_KHAU)}")
    so_nguon = re.findall(r"Nguồn: ([^\"·/()]+)", c["chu"])
    nhan_nam = c["kieu"] == "anh" and re.fullmatch(r'Nhãn "\d{4}"', c["chu"])  # năm của ảnh: nguồn là ghi nguồn ảnh
    if re.search(r"\d", c["chu"]) and not so_nguon and not nhan_nam and c["nguon"] != "the:tieu-de/phim":
        sai(f"{c['id']}: chữ trên hình có số nhưng không ghi 'Nguồn:'")
    for n in so_nguon:
        for x in re.split(r",\s*", n.strip()):
            if not x.startswith(NGUON_SO):
                sai(f"{c['id']}: nguồn số liệu '{x}' ngoài danh sách chính thống {NGUON_SO}")
    if c["hang"] == "code" and so_nguon:
        ds = ", ".join(dict.fromkeys(x.strip() for n in so_nguon for x in n.split(",")))
        c["ghi_nguon"] = ("Nguồn: " if kieu == "the" else "Đồ họa minh họa · Số liệu: ") + ds

# 3. Trần thời lượng tư liệu hạng B và A? (3–5 s, ghi nguồn)
for c in CANH:
    if c["hang"] in ("B", "A?") and c["dai"] > 5.0:
        sai(f"{c['id']}: tư liệu hạng {c['hang']} dài {c['dai']} s > 5 s")

# 4. Lãnh tụ: không 3D, ảnh chỉ bản A đã khoá, lời lãnh tụ chỉ ở chữ, không giọng
for c in CANH:
    loi_canh = " ".join(" ".join(cau[i - 1]) for i in c["cau"])
    if any(x in loi_canh for x in LANH_TU_LOI) and c["kieu"] in ("3d", "3d-moi", "demo"):
        sai(f"{c['id']}: lời nhắc lãnh tụ, cảnh không được dựng 3D")
    if c["kieu"] == "anh" and c["ten"] in LANH_TU_ANH and "lanhTu" not in c["hinh"]:
        sai(f"{c['id']}: ảnh lãnh tụ phải chạy chế độ lanhTu (chỉ phóng chậm, không đè chữ)")
    if "Chủ tịch Hồ Chí Minh" in c["chu"] and "lời Chủ tịch" in c["chu"] + c["hinh"] and c["cau"]:
        sai(f"{c['id']}: lời lãnh tụ phải nằm trong khoảng lặng, không trùng lời đọc")

# 5. Bản đồ: khung chạm biển phải có Hoàng Sa, Trường Sa; địa hình lòng chảo không chạm biển
for c in CANH:
    if c["kieu"] == "vnmap" and "Hoàng Sa" not in c["hinh"] and "không chạm biển" not in c["hinh"]:
        sai(f"{c['id']}: vnmap phải ghi khung có Hoàng Sa, Trường Sa hoặc 'không chạm biển'")
    if c["kieu"] != "vnmap" and re.search(r"Hà Nội|đồng bằng|Đông Dương|[Bb]iển|Vịnh", c["hinh"]) and "không chạm biển" not in c["hinh"]:
        sai(f"{c['id']}: hình có đồng bằng/biển phải dùng vnmap (luôn có Hoàng Sa, Trường Sa)")
    if re.search(r"lưỡi bò|VNCH", c["hinh"] + c["chu"]):
        sai(f"{c['id']}: cấm đường lưỡi bò, cờ VNCH")

# 6. Kho 3D: không 3D lá cờ; không 3D pháo 105 cho loạt mở màn 13/3 (câu 114–120)
for c in CANH:
    if c["kieu"] in ("3d", "3d-moi", "demo"):
        if re.search(r"\bcờ\b", c["hinh"]):
            sai(f"{c['id']}: không dựng 3D lá cờ")
        if any(114 <= i <= 120 for i in c["cau"]) and "105" in c["hinh"] and "Pháp" not in c["hinh"]:
            sai(f"{c['id']}: loạt mở màn 13/3 không dùng 3D pháo 105 của ta")

# 7. Hai cảnh liền nhau không cùng cỡ và góc khi một bên là cảnh quay (3D, phim, ảnh)
quay = lambda c: c["kieu"] in ("3d", "3d-moi", "demo", "karmen", "anh")
for x, y in zip(CANH, CANH[1:]):
    if (quay(x) or quay(y)) and (x["co"], x["goc"]) == (y["co"], y["goc"]):
        sai(f"{x['id']} → {y['id']}: cùng cỡ '{x['co']}' và góc '{x['goc']}'")

# 8. Mật độ cắt và cận đặc tả theo chương; anh hùng không cảnh thương tích
thong_ke = []
for ten, a, b in CHUONG:
    nh = []  # cảnh thuộc chương theo câu đầu; cảnh khoảng lặng thuộc câu liền trước
    for c in CANH:
        dau = c["cau"][0] if c["cau"] else max([i for (i, k), s in moc_chu.items() if s < c["t0"]] or [1])
        if a <= dau <= b:
            nh.append(c)
    giay = sum(c["dai"] for c in nh)
    mat_do = len(nh) / giay * 60 if giay else 0
    dt = sum(c["co"] == "dac-ta" for c in nh)
    thong_ke.append((ten, len(nh), giay, mat_do, dt))
    if mat_do < 9:
        sai(f"{ten}: {mat_do:.1f} cảnh/phút < 9")
    if not dt:
        sai(f"{ten}: không có cận đặc tả")
tong_md = len(CANH) / HET * 60
if not 10 <= tong_md <= 20:
    sai(f"cả tập {tong_md:.1f} cảnh/phút, ngoài 10–20")
for c in CANH:
    if re.search(r"thương tích|máu|xác người", c["hinh"]) and "không" not in c["hinh"]:
        sai(f"{c['id']}: không tả thương tích")

# Ghi phan-canh.json
ra = dict(ten="Tập 1 · Điện Biên Phủ 1954 · phân cảnh", fps=24, uoc_tinh=not that, het=round(HET, 2),
          lang={k: [round(a, 2), round(b, 2)] for k, (a, b) in moc_lang.items()},
          canh=[{k: (round(v, 2) if isinstance(v, float) else v) for k, v in c.items()} for c in CANH])
CHINH = MD == GOC / "phan-canh.md"  # bảng thử (--md) không ghi đè đầu ra
if CHINH:
    (GOC / "phan-canh.json").write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")

# Danh sách tài sản cần dựng
nhom = {}
for c in CANH:
    khoa = c["kieu"] + (":" + c["ten"].split("/")[0] if c["kieu"] in ("3d-moi", "the", "map3d", "vnmap") else "")
    nhom.setdefault(c["kieu"], {}).setdefault(khoa if c["kieu"] not in ("anh", "karmen", "3d", "can-tim") else c["nguon"], []).append(c)
ten_kieu = {"demo": "Cảnh 3D đã render và duyệt của bản Demo (dùng nguyên hình)", "3d": "Cảnh 3D của bản mẫu, dựng lại theo thời lượng mới", "3d-moi": "Cảnh 3D mới trên sân khấu có sẵn",
            "map3d": "Bản đồ địa hình lòng chảo (map3d)", "vnmap": "Bản đồ chính trị (vnmap, có Hoàng Sa, Trường Sa)",
            "the": "Thẻ chữ, số (cards)", "anh": "Ảnh tư liệu (archival)", "karmen": "Phim Karmen (hạng B, ≤ 5 s, tắt tiếng)",
            "can-tim": "Tư liệu cần tìm (có phương án thay)"}
ds = ["# Tập 1 · tài sản cần dựng (máy sinh từ phan-canh.md, không sửa tay)", ""]
for kieu in KIEU:
    if kieu not in nhom:
        continue
    g = nhom[kieu]
    ds += [f"## {ten_kieu[kieu]}: {sum(len(v) for v in g.values())} cảnh", "", "| Món | Cảnh | Tổng giây | Hạng |", "|---|---|---|---|"]
    for k, v in g.items():
        ds.append(f"| `{k}` | {', '.join(c['id'] for c in v)} | {sum(c['dai'] for c in v):.1f} | {v[0]['hang']} |")
    ds.append("")
if CHINH:
    (GOC / "tai-san-can-dung.md").write_text("\n".join(ds), encoding="utf-8", newline="\n")

# Tóm tắt vào phan-canh.md
dem = {k: sum(len(v) for v in g.values()) for k, g in nhom.items()}
tom = [f"- **{len(CANH)} cảnh, {HET:.0f} s ({HET // 60:.0f}:{HET % 60:02.0f}), {tong_md:.1f} cảnh/phút** "
       f"({'ước tính 242 tiếng/phút' if not that else 'mốc chữ thật'}).",
       "- Theo kiểu: " + ", ".join(f"{k} {v}" for k, v in dem.items()) + ".",
       f"- Tư liệu thật (ảnh + phim): {dem.get('anh', 0) + dem.get('karmen', 0)} cảnh, "
       f"{sum(c['dai'] for c in CANH if c['kieu'] in ('anh', 'karmen')):.0f} s; hạng B/A? dài nhất "
       f"{max(c['dai'] for c in CANH if c['hang'] in ('B', 'A?')):.1f} s.",
       "", "| Chương | Cảnh | Giây | Cảnh/phút | Đặc tả |", "|---|---|---|---|---|"]
tom += [f"| {t_} | {n} | {g:.0f} | {m:.1f} | {d} |" for t_, n, g, m, d in thong_ke]
van = re.sub(r"(<!-- TOM -->\n).*?(<!-- /TOM -->)", lambda m: m[1] + "\n".join(tom) + "\n" + m[2], van, flags=re.S)
if CHINH:
    MD.write_text(van, encoding="utf-8", newline="\n")

print("\n".join(tom))
if loi_:
    print("\nTRƯỢT:\n- " + "\n- ".join(loi_))
    sys.exit(1)
print("\nĐẠT: neo liền, phủ đủ lời, nguồn trên mọi cảnh, trần 5 s cho B/A?, lãnh tụ, bản đồ, cỡ/góc, mật độ, đặc tả")
