"""Kiểm phân cảnh EP002 黄海海戦 1904 (chép từ máy kiểm EP001 JP, 13/11/2026). Bản cũ: EP001 日本海海戦 theo template/chuan-dao-dien.md và luật cứng CLAUDE.md.

Bản thích ứng cho kênh 戦陣再審 (quân sự Nhật), sửa từ máy kiểm tập mẫu:
- Tách câu theo KÝ TỰ (tiếng Nhật không có dấu cách); tốc độ 327 ký tự/phút (đo trên giọng thật EP001).
- Nguồn số liệu chính thống Nhật (JACAR, 国立国会図書館, NARA, Wikipedia có nguồn).
- Loại hình: anh, the, ban-do (bản đồ hải chiến vẽ code), can-tim. Không có 3D/vnmap/karmen (Tiết kiệm + không phải nội dung VN).
- Luật bản đồ Việt Nam (Hoàng Sa) chỉ kích hoạt nếu hình nhắc Việt Nam; tập này không có.

Chạy: python -I kiem-phan-canh.py [--md <bảng khác>]   (thoát mã 1 nếu trượt luật)
"""
import csv, json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
MD = Path(sys.argv[sys.argv.index("--md") + 1]) if "--md" in sys.argv else GOC / "phan-canh.md"
LOI = GOC.parent / "ke-hoach" / "loi-doc-v3.txt"
MOC = GOC / "moc-cau.json"
TIENG_GIAY = 60 / 327  # 327 ký tự/phút (đo trên giọng thật EP001: 7.663 ký tự / 23:24)
CHUONG = [("開幕 (hook)", 1, 12), ("第1章 前夜", 13, 59), ("第2章 東郷の制約", 60, 98),
          ("第3章 午後1時", 99, 130), ("第4章 追撃", 131, 164), ("第5章 午後5時半", 165, 213),
          ("第6章 日没", 214, 246), ("第7章 その後", 247, 284), ("結", 285, 303)]
NGUON_SO = ("JACAR", "国立国会図書館", "国立公文書館", "NARA", "Wikipedia")
CAM = {"MAPW1": "bản đồ Viễn Đông cổ (Biển Đông)", "MAPW2": "bản đồ Viễn Đông cổ (Biển Đông)", "CRUISE": "đề gốc đuổi tàu buôn", "RURIK": "người sống sót chưa soi thương tích", "HATSUSE": "không có trong trận"}  # bí danh trong anh.tsv; lap-phan-canh.py cũng chặn theo mã gốc
LANH_TU_ANH = set()          # không có ảnh 天皇
LANH_TU_LOI = ("天皇", "昭和天皇", "明治天皇")  # không xuất hiện trong kịch bản; giữ để chặn nếu lỡ thêm
KIEU = ("anh", "the", "ban-do", "can-tim", "clip")
BAN_DO = {"koukai", "ryojun", "kosen1", "tsuigeki", "kosen2", "senkai", "sanran", "churitsu", "ulsan"}  # mã bản đồ vẽ code EP002
CO = {"dac-ta", "can", "trung", "toan", "toan-xa", "ban-do", "the", "anh"}
GOC_MAY = {"thap", "ngang", "cao", "tren-xuong", "chech", "phang"}
loi_ = []


def sai(msg):
    loi_.append(msg)


# Lời đọc: mỗi câu tách thành danh sách KÝ TỰ; dòng trống giữa bài là khoảng lặng
cau, lang_md = [], {}
for dong in LOI.read_text(encoding="utf-8").rstrip("\n").split("\n"):
    if dong.strip():
        cau.append(list(dong.strip()))
N = len(cau)

van = MD.read_text(encoding="utf-8")
for m in re.finditer(r"^\| ([A-Z][A-Z0-9]) \| (\S+) \| ([\d.]+) \|", van, re.M):
    lang_md[m[1]] = (m[2], float(m[3]))

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

ANH = {r["tep"]: r for r in csv.DictReader(open(GOC / "anh.tsv", encoding="utf-8"), delimiter="\t")}
CLIP = {r["ma"]: r for r in csv.DictReader(open(GOC / "clip.tsv", encoding="utf-8"), delimiter="	")}  # clip AI (Flow), nhãn AI生成 bắt buộc

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

if CANH[0]["neo"] != "1":
    sai(f"{CANH[0]['id']}: cảnh đầu phải neo ở câu 1")
CANH[0]["t0"] = 0.0
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
    if ten[0] not in "TUVWXYZ" and not any(c["neo"] == ten for c in CANH):
        sai(f"khoảng lặng {ten}: không có cảnh nào neo vào")

# 2. Kiểu nguồn, cỡ, góc, ghi nguồn
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
            sai(f"{c['id']}: tư liệu cấm '{ten}' ({CAM[ten]})")
        elif ten not in ANH:
            sai(f"{c['id']}: ảnh '{ten}' chưa có trong anh.tsv")
        else:
            c["hang"], c["ghi_nguon"] = ANH[ten]["hang"], ANH[ten]["ghi_nguon"]
    elif kieu == "clip":
        if ten not in CLIP:
            sai(f"{c['id']}: clip '{ten}' chưa có trong clip.tsv")
        else:
            c["hang"], c["ghi_nguon"] = "AI", "AI生成 (Flow Veo 3.1)"
            if not re.search(r"AI生成|イラスト", c["chu"]):  # luật kit: hình minh hoạ phải ghi chữ «minh hoạ» trên hình; EP002 dùng «イラスト» nhỏ
                sai(f"{c['id']}: clip AI phải có nhãn «イラスト» (hoặc «AI生成») ở cột Chữ")
    elif kieu == "ban-do":
        if ten.split("+")[0] not in BAN_DO:
            sai(f"{c['id']}: mã bản đồ '{ten}' không thuộc {sorted(BAN_DO)}")
    elif kieu == "can-tim":
        c["hang"], c["ghi_nguon"] = "?", "chờ tư liệu có giấy phép"
        if "chưa có" not in c["hinh"]:
            sai(f"{c['id']}: tư liệu cần tìm phải ghi phương án thay ('chưa có …')")
    so_nguon = re.findall(r"Nguồn: ([^\"·/()]+)", c["chu"])
    nhan_nam = c["kieu"] == "anh" and re.fullmatch(r'Nhãn "\d{4}"|Chú thích "[^"]*"', c["chu"])  # EP002: ngày chụp ảnh là siêu dữ liệu của anh.tsv
    # Số: cả Ả Rập \d và số kanji (一二三四五六七八九〇十百千万); đơn vị hải chiến ノット/隻/門/名
    co_so = re.search(r"[\d一二三四五六七八九〇十百千万]", re.sub(r'Thẻ tên "[^"]*"', "", c["chu"]))  # tên tàu/người (三笠, アレクサンドル3世) không phải số liệu
    if co_so and not so_nguon and not nhan_nam and c["nguon"] != "the:tieu-de":
        sai(f"{c['id']}: chữ trên hình có số nhưng không ghi 'Nguồn:'")
    for n in so_nguon:
        for x in re.split(r",\s*", n.strip()):
            if not x.startswith(NGUON_SO):
                sai(f"{c['id']}: nguồn số liệu '{x}' ngoài danh sách {NGUON_SO}")
    if c["hang"] == "code" and so_nguon:
        ds = ", ".join(dict.fromkeys(x.strip() for n in so_nguon for x in n.split(",")))
        c["ghi_nguon"] = ("Nguồn: " if kieu == "the" else "Đồ họa minh họa · Nguồn: ") + ds

# 3. Trần thời lượng B và A?
for c in CANH:
    if c["hang"] in ("B", "A?") and c["dai"] > 5.0:
        sai(f"{c['id']}: tư liệu hạng {c['hang']} dài {c['dai']} s > 5 s")

# 4. 天皇 (lãnh tụ Nhật): không có trong kịch bản; chặn nếu lỡ có ảnh AI/dựng
for c in CANH:
    loi_canh = "".join("".join(cau[i - 1]) for i in c["cau"])
    if any(x in loi_canh for x in LANH_TU_LOI) and c["kieu"] not in ("anh", "the", "ban-do"):
        sai(f"{c['id']}: lời nhắc 天皇, chỉ được ảnh thật/thẻ/bản đồ")

# 5. Bản đồ có Việt Nam (luật cứng CLAUDE.md): bản đồ tới サイゴン phải có Hoàng Sa, Trường Sa (Việt Nam), Biển Đông
VN = re.compile(r"サイゴン|Sài Gòn|仏領インドシナ|Việt Nam|Hoàng Sa|Trường Sa|Biển Đông|南シナ海")
for c in CANH:
    if c["kieu"] == "ban-do" and c["ten"] == "churitsu" or (VN.search(c["hinh"] + c["chu"]) and c["kieu"] in ("ban-do", "anh")):
        if c["kieu"] != "ban-do":
            sai(f"{c['id']}: nhắc vùng Việt Nam/サイゴン nhưng không phải bản đồ vẽ code theo luật cứng")
        elif not all(x in c["hinh"] for x in ("Hoàng Sa", "Trường Sa", "Biển Đông")) or "không đường lưỡi bò" not in c["hinh"]:
            sai(f"{c['id']}: bản đồ có vùng Việt Nam phải ghi Hoàng Sa, Trường Sa (Việt Nam), Biển Đông, «không đường lưỡi bò»")
    if re.search(r"南シナ海|VNCH|lưỡi bò(?! )", c["chu"]):
        sai(f"{c['id']}: chữ trên hình có 南シナ海/VNCH/lưỡi bò")

# 6. Không tả thương tích (bộ lọc chính sách mục 4)
for c in CANH:
    if re.search(r"thương tích|máu|xác người|死体|血", c["hinh"]) and "không" not in c["hinh"]:
        sai(f"{c['id']}: không tả thương tích/máu")

# 7. Hai cảnh liền nhau không cùng cỡ+góc khi một bên là cảnh "quay" (ảnh thật)
quay = lambda c: c["kieu"] in ("anh", "clip")
for x, y in zip(CANH, CANH[1:]):
    if (quay(x) or quay(y)) and (x["co"], x["goc"]) == (y["co"], y["goc"]):
        sai(f"{x['id']} → {y['id']}: cùng cỡ '{x['co']}' và góc '{x['goc']}'")

# 7b. Luật chuẩn hình (chủ kênh chốt 11/11/2026, theo tập Peleliu): lặp hình và chuỗi không hình thật
THAT = ("anh", "clip")
dung_ = {}
for c in CANH:
    if c["kieu"] in THAT:
        dung_.setdefault(c["nguon"], []).append(c)
for khoa, ds_ in dung_.items():
    # cảnh liền kề cùng tài sản tính một lần
    lan = [ds_[0]] + [y for x, y in zip(ds_, ds_[1:]) if y["id"] != CANH[CANH.index(x) + 1]["id"]]
    if len(lan) > 3:
        sai(f"{khoa}: dùng {len(lan)} lần (> 3)")
    for x, y in zip(lan, lan[1:]):
        if y["t0"] - x["t1"] < 60:
            sai(f"{khoa}: {x['id']} → {y['id']} cách {y['t0'] - x['t1']:.0f} s < 60 s")
    for c in ds_:
        if c["kieu"] == "clip" and c["dai"] > 7.9 + 1e-6:
            sai(f"{c['id']}: clip AI dài {c['dai']} s > 7,9 s (độ dài clip)")
chay = 0
for c in CANH:
    chay = 0 if c["kieu"] in THAT else chay + 1
    if chay > 4:
        sai(f"{c['id']}: {chay} cảnh liền không có ảnh/clip (tối đa 4)")
        chay = 0
SO_THAT = len({c["nguon"] for c in CANH if c["kieu"] in THAT})

# 8. Mật độ và đặc tả theo chương
thong_ke = []
for ten, a, b in CHUONG:
    nh = []
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

# Ghi phan-canh.json
ra = dict(ten="EP002 · 黄海海戦 1904 · phân cảnh", fps=24, uoc_tinh=not that, het=round(HET, 2),
          lang={k: [round(a, 2), round(b, 2)] for k, (a, b) in moc_lang.items()},
          canh=[{k: (round(v, 2) if isinstance(v, float) else v) for k, v in c.items()} for c in CANH])
CHINH = MD == GOC / "phan-canh.md"
if CHINH:
    (GOC / "phan-canh.json").write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")

# Tài sản cần dựng
nhom = {}
for c in CANH:
    khoa = c["nguon"] if c["kieu"] in ("anh", "can-tim") else c["kieu"] + ":" + c["ten"].split("+")[0]
    nhom.setdefault(c["kieu"], {}).setdefault(khoa, []).append(c)
ten_kieu = {"ban-do": "Bản đồ hải chiến (vẽ code)", "the": "Thẻ chữ, số, infographic (code)",
            "anh": "Ảnh tư liệu (archival PD/CC)", "clip": "Clip AI (Flow, nhãn AI生成)", "can-tim": "Tư liệu cần tìm (có phương án thay)"}
ds = ["# EP002 · tài sản cần dựng (máy sinh từ phan-canh.md, không sửa tay)", ""]
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

# Tóm tắt
dem = {k: sum(len(v) for v in g.values()) for k, g in nhom.items()}
tulieu = [c for c in CANH if c["kieu"] == "anh"]
tom = [f"- **{len(CANH)} cảnh, {HET:.0f} s ({HET // 60:.0f}:{HET % 60:02.0f}), {tong_md:.1f} cảnh/phút** "
       f"({'ước tính 327 ký tự/phút' if not that else 'mốc chữ thật'}).",
       "- Theo kiểu: " + ", ".join(f"{k} {v}" for k, v in dem.items()) + ".",
       f"- Ảnh/clip khác nhau: {SO_THAT} (ảnh {len({c['nguon'] for c in CANH if c['kieu']=='anh'})}, clip AI {len({c['nguon'] for c in CANH if c['kieu']=='clip'})}).",
       f"- Tư liệu thật (ảnh): {len(tulieu)} cảnh"
       + (f"; hạng B/A? dài nhất {max((c['dai'] for c in CANH if c['hang'] in ('B','A?')), default=0):.1f} s." if any(c['hang'] in ('B','A?') for c in CANH) else "."),
       "", "| Chương | Cảnh | Giây | Cảnh/phút | Đặc tả |", "|---|---|---|---|---|"]
tom += [f"| {t_} | {n} | {g:.0f} | {m:.1f} | {d} |" for t_, n, g, m, d in thong_ke]
van = re.sub(r"(<!-- TOM -->\n).*?(<!-- /TOM -->)", lambda m: m[1] + "\n".join(tom) + "\n" + m[2], van, flags=re.S)
if CHINH:
    MD.write_text(van, encoding="utf-8", newline="\n")

print("\n".join(tom))
if loi_:
    print("\nTRƯỢT:\n- " + "\n- ".join(loi_))
    sys.exit(1)
print("\nĐẠT: neo liền, phủ đủ lời, nguồn mọi cảnh, trần 5 s B/A?, bản đồ, cỡ/góc, mật độ, đặc tả")
