"""Ghép hình tập 1 theo phan-canh.json: mỗi cảnh lấy video của lô (thẻ, tư liệu, bản đồ, 3D), phủ lớp chữ nếu có,
cảnh chưa dựng thành ô giữ chỗ (mã + mô tả, chỉ để soi nhịp); nối đúng tổng khung rồi ghép âm.

python -I -X utf8 ghep-hinh.py [--am <wav>] [--ra <mp4>] [--lam-lai]
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))
import intro  # noqa: E402
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")
H = OUT / "261101-dien-bien-phu-1954/hinh"
FONT = (GOC.parents[2] / "template/fonts/BeVietnamPro-SemiBold.ttf").as_posix().replace(":", r"\:")
FPS = 24
NGUON = {"the": "the", "anh": "tu-lieu", "karmen": "tu-lieu", "map3d": "ban-do", "vnmap": "ban-do", "3d": "3d", "3d-moi": "3d", "demo": "3d", "can-tim": "3d"}
MOC = json.loads((GOC / "moc-cau.json").read_text(encoding="utf-8"))
# v3: rung máy theo cú nổ chính của các tổ hợp tiến công (cùng mốc với dung-am.py khi_the): mã cảnh → [(khoảng lặng, lệch s, biên độ px)]
RUNG = {"C4-02b": [("H1", 0.95, 10), ("H1", 1.4, 22)], "C4-28b": [("H2", 0.65, 14)], "C5-24b": [("H3", 0.65, 10)],
        "C5-30b": [("H4", 0.9, 18)], "C3-31b": [("WB", 0.02, 7)]}


DAU = OUT / "261102-dbp-v3/dau-kenh.png"  # dau-kenh.py
DAU_LE = (56, 44)  # lề phải, lề trên (px)
AN_DAU = ("MO30", "C1-19", "C3-20", "C3-21", "KT-10", "KT-22", "KT-23", "KT-24", "KT-25")  # tiêu đề, ảnh và lời lãnh tụ, tưởng niệm


def an_dau(pc):
    """Các khoảng (giây phim) không hiện dấu kênh: intro trailer và các cảnh AN_DAU."""
    o = intro.INTRO_GIAY
    return [(0.0, o)] + [(c["t0"] + o, c["t1"] + o) for c in pc["canh"] if c["id"] in AN_DAU]


# Dấu kênh linh hoạt 4 góc (user 02/11/2026 15:55): mỗi cảnh một góc trống, chỉ đổi ở cú cắt, đi vòng theo nhịp phim.
DAU_WH = (229, 50)
VONG = ("tp", "dt", "tt", "dp")  # trên phải → dưới trái → trên trái → dưới phải
GOC_XY = {"tp": (1920 - DAU_LE[0] - DAU_WH[0], DAU_LE[1]), "dt": (DAU_LE[0], 1080 - DAU_LE[1] - DAU_WH[1]),
          "tt": (DAU_LE[0], DAU_LE[1]), "dp": (1920 - DAU_LE[0] - DAU_WH[0], 1080 - DAU_LE[1] - DAU_WH[1])}
NHIP, PHAT_DOI, PHAT_LECH_NHIP, BAN = 75.0, 0.8, 0.5, 0.035  # giây mỗi chặng; phạt đổi góc; phạt lệch góc của chặng; ngưỡng bận


THAM_DO = f"{DAU_WH}{DAU_LE}-24-40-3k"  # tham số phép đo (ô dấu, lề, nới, ngưỡng cạnh, số khung): đổi thì đo lại


def ban_goc(f, n):
    """Độ bận của 4 góc trong một cảnh: tỉ lệ điểm cạnh mạnh (chữ, chi tiết) trong ô dấu nới 24 px, lấy lớn nhất của 3 khung."""
    import numpy as np
    kq = {k: 0.0 for k in GOC_XY}
    for p in (0.15, 0.5, 0.85):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{p * n / FPS:.3f}", "-i", str(f), "-frames:v", "1", "-vf", "format=gray",
                              "-f", "rawvideo", "-"], capture_output=True).stdout
        if len(raw) < 1920 * 1080:
            continue
        y = np.frombuffer(raw[:1920 * 1080], np.uint8).reshape(1080, 1920).astype(np.int16)
        for k, (x0, y0) in GOC_XY.items():
            o = y[max(0, y0 - 24):y0 + DAU_WH[1] + 24, max(0, x0 - 24):x0 + DAU_WH[0] + 24]
            canh = np.maximum(np.abs(np.diff(o, axis=0))[:, :-1], np.abs(np.diff(o, axis=1))[:-1, :])
            kq[k] = max(kq[k], float((canh > 40).mean()))
    return kq


def chon_goc(pc, ban):
    """Chọn góc từng cảnh (quy hoạch động): góc bận phạt nặng, đổi góc phạt, lệch góc của chặng 75 s phạt nhẹ.
    Cảnh ẩn dấu không tính phí và đổi góc ở đó miễn phí. Trả {mã cảnh: góc}."""
    an = set(AN_DAU)
    ds = pc["canh"]
    vo = {k: VONG.index(k) for k in VONG}
    phi = []
    for c in ds:
        if c["id"] in an:
            phi.append({k: 0.0 for k in VONG})
            continue
        nhip = VONG[int(c["t0"] // NHIP) % 4]
        phi.append({k: (10.0 if ban[c["id"]][k] > BAN else ban[c["id"]][k] * 10) + (PHAT_LECH_NHIP if k != nhip else 0) for k in VONG})
    tot, ve = [dict(phi[0])], [{}]
    for i in range(1, len(ds)):
        mien = ds[i]["id"] in an or ds[i - 1]["id"] in an
        tot.append({}), ve.append({})
        for k in VONG:
            j = min(VONG, key=lambda q: tot[i - 1][q] + (0 if q == k or mien else PHAT_DOI) + vo[q] * 1e-6)
            tot[i][k] = tot[i - 1][j] + (0 if j == k or mien else PHAT_DOI) + phi[i][k]
            ve[i][k] = j
    k = min(VONG, key=lambda q: tot[-1][q])
    chon = [k]
    for i in range(len(ds) - 1, 0, -1):
        k = ve[i][k]
        chon.append(k)
    return {c["id"]: g for c, g in zip(ds, reversed(chon))}


def loc_dau(pc, goc):
    """Bộ lọc ffmpeg cho dấu kênh: vị trí theo góc từng đoạn, mờ vào 0,4 s mỗi khi hiện ở góc mới, ẩn ở AN_DAU và intro."""
    doan_ = []  # (a, b, góc) các đoạn liền hiện cùng một góc; a, b = giây của khung đầu cảnh trong phim đã nối
    k0 = round(pc["canh"][0]["t0"] * FPS)
    for c in pc["canh"]:
        g = None if c["id"] in AN_DAU else goc[c["id"]]
        a = (intro.INTRO_KHUNG + round(c["t0"] * FPS) - k0) / FPS
        b = (intro.INTRO_KHUNG + round(c["t1"] * FPS) - k0) / FPS
        if doan_ and doan_[-1][2] == g:
            doan_[-1][1] = b
        else:
            doan_.append([a, b, g])
    hien = [(a, b, g) for a, b, g in doan_ if g]
    h = 0.5 / FPS
    tron = lambda f: "".join(f"if(lt(t,{b - h:.4f}),{f(a, g)}," for a, b, g in hien) + "0" + ")" * len(hien)
    x = tron(lambda a, g: GOC_XY[g][0])
    y = tron(lambda a, g: GOC_XY[g][1])
    mo = "".join(f"if(gte(T,{a - h:.4f})*lt(T,{b - h:.4f}),min(1,(T-{a - h:.4f})/0.4)," for a, b, g in hien) + "0" + ")" * len(hien)
    return (f"[2:v]format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='alpha(X,Y)*{mo}'[d];"
            f"[0:v][d]overlay=x='{x}':y='{y}':eval=frame,"), hien


def goc_dau(pc):
    """Đo độ bận 4 góc trên từng cảnh đã ghép (lưu đệm theo mtime), chọn góc, ghi hinh/ghep/goc-dau.json."""
    dem_f = H / "ghep" / "goc-dau.json"
    dem = json.loads(dem_f.read_text(encoding="utf-8")) if dem_f.exists() else {}
    ban = {}
    for c in pc["canh"]:
        f = H / "ghep" / f"{c['id']}.mp4"
        n = round(c["t1"] * FPS) - round(c["t0"] * FPS)
        if not f.exists():  # cảnh chưa ghép (chạy --den, đang dựng lại): không đo, coi như trống
            dem[c["id"]], ban[c["id"]] = {"ban": {k: 0.0 for k in GOC_XY}}, {k: 0.0 for k in GOC_XY}
            continue
        cu = dem.get(c["id"], {})
        if cu.get("mtime") != f.stat().st_mtime or cu.get("tham") != THAM_DO:
            cu = {"mtime": f.stat().st_mtime, "tham": THAM_DO, "ban": ban_goc(f, n)}
            dem[c["id"]] = cu
        ban[c["id"]] = dict(cu["ban"])
        # góc bị chữ chiếm theo dữ liệu lớp chữ (thẻ tên nằm cao hơn ô dấu nên phép đo cạnh không thấy)
        lop = GOC.parents[2] / "template" / "overlay" / "shots" / "dbp1" / f"{c['id']}.js"
        shot = json.loads(lop.read_text(encoding="utf-8").split("window.SHOT = ", 1)[1].rstrip().rstrip(";")) if lop.exists() else {}
        if shot.get("thes"):
            ban[c["id"]]["dt"] = 1.0
        if shot.get("date") or c["kieu"] == "the":
            ban[c["id"]]["tt"] = 1.0
    goc = chon_goc(pc, ban)
    for c in pc["canh"]:
        dem[c["id"]]["goc"] = goc[c["id"]]
    dem_f.write_text(json.dumps(dem, ensure_ascii=False, indent=0), encoding="utf-8")
    hien = [c for c in pc["canh"] if c["id"] not in AN_DAU]
    doi = sum(1 for a, b in zip(hien, hien[1:]) if goc[a["id"]] != goc[b["id"]])
    ket = [c["id"] for c in hien if ban[c["id"]][goc[c["id"]]] > BAN]
    print(f"dấu kênh: {doi} lần đổi góc trên {len(hien)} cảnh; " + ", ".join(f"{k} {sum(goc[c['id']] == k for c in hien)}" for k in VONG)
          + f"; cảnh không có góc trống: {' '.join(ket) or 'không'}")
    return goc


def rung(c):
    """Bộ lọc rung tắt dần (phóng 4 % rồi xê dịch khung cắt) cho cảnh có cú nổ; "" nếu không."""
    if c["id"] not in RUNG:
        return ""
    lam = [(MOC["lang"][ten][0] + lech - c["t0"], a) for ten, lech, a in RUNG[c["id"]]]
    dx = "+".join(f"{a}*gte(t,{t0:.3f})*exp(-(t-{t0:.3f})*7)*sin(2*PI*13*(t-{t0:.3f}))" for t0, a in lam)
    dy = "+".join(f"{a * 0.7:.1f}*gte(t,{t0:.3f})*exp(-(t-{t0:.3f})*7)*cos(2*PI*17*(t-{t0:.3f}))" for t0, a in lam)
    return f",scale=2000:1125,crop=1920:1080:x='40+{dx}':y='22+{dy}'"


MA_HOA = ["-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", str(FPS)]


def do_sang(f):
    """Độ sáng trung bình (YAVG) từng khung."""
    o = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-vf", "signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-", "-f", "null", "-"],
                       capture_output=True, text=True).stdout
    return [float(x.split("=")[1]) for x in o.split() if x.startswith("lavfi.signalstats.YAVG=")]


def den_dau(y, toi_da=8):
    """Số khung đầu tối hẳn (trang 3D chưa kịp sáng, 0,1–0,3 s đen như giật hình): khung đầu dưới nửa độ sáng khung sáng đầu tiên."""
    if len(y) < toi_da + 2:
        return 0
    tran = max(y[:toi_da + 2])
    b = next(k for k, v in enumerate(y) if v >= 0.5 * tran)
    return b if 0 < b <= toi_da and y[0] < 12 else 0  # chỉ khung gần đen (khung tối của cảnh đêm có chớp là cố ý)


def khung_loi(f, nguong=20.0, y=None):
    """Chỉ số khung có độ sáng trung bình lệch > nguong so với cả khung trước và khung sau."""
    y = y if y is not None else do_sang(f)
    n = len(y)
    if n < 3:
        return []
    ke = lambda k: (1, 2) if k == 0 else (n - 2, n - 3) if k == n - 1 else (k - 1, k + 1)  # mép cảnh: so hai khung cùng phía
    return [k for k in range(n) if all(abs(y[k] - y[j]) > nguong for j in ke(k))]


def nhap_nhay_dau(y, nguong=20.0, toi_da=8):
    """Số khung đầu phải thay khi đầu cảnh nhấp nháy: khung cuối cùng trong toi_da khung đầu lệch mức ổn định
    (trung vị khung 5–15) quá ngưỡng, cộng 1; 0 nếu không có."""
    if len(y) < 16:
        return 0
    on = sorted(y[5:16])[5]
    lech = [k for k in range(toi_da) if abs(y[k] - on) > nguong]
    return lech[-1] + 1 if lech else 0


def doan(c, n, lam_lai):
    """Một cảnh đã phủ chữ, đúng n khung → hinh/ghep/<mã>.mp4. Trả (đường dẫn, có nguồn thật không)."""
    ra = H / "ghep" / f"{c['id']}.mp4"
    nguon = H / NGUON[c["kieu"]] / f"{c['id']}.mp4"
    lop = H / "lop-chu" / f"{c['id']}.mov"
    that = nguon.exists()
    moi_nhat = max([nguon.stat().st_mtime] + ([lop.stat().st_mtime] if lop.exists() else [])) if that else 0
    if ra.exists() and not lam_lai and that and ra.stat().st_mtime > moi_nhat and c["id"] not in RUNG:
        return ra, True
    if that:
        vao = ["-i", str(nguon)]
        # Trang 3D có khi vẽ hỏng một khung (chớp sáng/tối, thường ở 1–2 khung đầu): thay khung lệch hẳn cả hai bên bằng khung trước.
        sua = ""
        if c["kieu"] in ("3d", "3d-moi"):
            y = do_sang(nguon)
            if not re.search(r"nổ|chớp|lửa|bùng", c["hinh"]):
                # đầu cảnh nhấp nháy nhiều khung liền (vd C1-22: 41, 79, 79, 41, 79, 41…): so với mức ổn định khung 5–15
                m = nhap_nhay_dau(y)
                sua = (f",freezeframes=first=0:last={m - 1}:replace={m}" if m else "") + "".join(
                    f",freezeframes=first={k}:last={k}:replace={k - 1 if k else 1}" for k in khung_loi(nguon, y=y) if k >= m)
            b = den_dau(y)  # khung đầu đen (cả cảnh có nổ): giữ khung sáng đầu tiên
            if b:
                sua = f",freezeframes=first=0:last={b - 1}:replace={b}" + sua
        # freezeframes cần hai đầu vào (luồng gốc, luồng lấy khung thay): mỗi lần thay thì tách luồng làm hai
        loc, nhan = "[0:v]fps=24,scale=1920:1080,setsar=1", "g0"
        for i, ff in enumerate(x for x in sua.split(",") if x):
            loc += f",split=2[g{i}a][g{i}b];[g{i}a][g{i}b]{ff}"
            nhan = f"g{i + 1}"
            loc += f"[{nhan}];[{nhan}]null"
        loc += f"{rung(c)}[b]"
    else:
        chu = f"{c['id']} · {c['nguon']}\\n{c['hinh'][:90]}".replace("'", "’").replace(":", r"\:").replace(",", r"\,")
        vao = ["-f", "lavfi", "-i", f"color=c=0x15130f:s=1920x1080:r={FPS}:d={n / FPS:.4f}"]
        loc = f"[0:v]drawtext=fontfile='{FONT}':text='{chu}':fontcolor=0xd6c9a3:fontsize=34:x=120:y=480:line_spacing=18[b]"
    if lop.exists():
        vao += ["-i", str(lop)]
        loc += ";[1:v]format=rgba[o];[b][o]overlay=0:0:format=auto,format=yuv420p[v]"
    else:
        loc += ";[b]format=yuv420p[v]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *vao, "-filter_complex", loc, "-map", "[v]", "-an", "-frames:v", str(n), *MA_HOA, str(ra)], check=True)
    return ra, that


def soi_dau(pc, ra):
    """Khung Full HD (cỡ thật) giữa mỗi đoạn hiện dấu, có dấu ở góc đã chọn: ra/<stt>-<mã cảnh>-<góc>.jpg."""
    from PIL import Image
    ra.mkdir(parents=True, exist_ok=True)
    goc = goc_dau(pc)
    dau = Image.open(DAU).convert("RGBA")
    i, truoc = 0, None
    for c in pc["canh"]:
        g = None if c["id"] in AN_DAU else goc[c["id"]]
        if g and g != truoc:
            i += 1
            t = (c["t1"] - c["t0"]) * 0.6
            tam = ra / "tam.png"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(H / "ghep" / f"{c['id']}.mp4"), "-frames:v", "1", str(tam)], check=True)
            im = Image.open(tam).convert("RGBA")
            im.alpha_composite(dau, GOC_XY[g])
            im.convert("RGB").save(ra / f"{i:02d}-{c['id']}-{g}.jpg", quality=92)
        truoc = g
    (ra / "tam.png").unlink(missing_ok=True)
    print(f"{i} khung soi ở {ra}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--am", default=json.loads((GOC / "moc-cau.json").read_text(encoding="utf-8"))["giong"])
    ap.add_argument("--ra", default=str(H.parent / "xem-truoc" / "tap1-nhap.mp4"))
    ap.add_argument("--lam-lai", action="store_true")
    ap.add_argument("--den", type=float, default=None, help="chỉ ghép tới giây phim này (tính cả intro)")
    ap.add_argument("--soi-dau", metavar="THU_MUC", help="chỉ chọn góc dấu kênh trên các cảnh đã ghép, xuất khung Full HD ở mỗi lần đổi góc")
    o = ap.parse_args()
    pc = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))
    if o.soi_dau:
        soi_dau(pc, Path(o.soi_dau))
        return
    (H / "ghep").mkdir(parents=True, exist_ok=True)
    # v2: intro trailer (intro.py) đứng trước lời; mọi cảnh lùi INTRO_KHUNG
    ds, tong, thieu = [f"file '{(intro.RA / 'intro.mp4').as_posix()}'"], intro.INTRO_KHUNG, []
    for c in pc["canh"]:
        if o.den and tong >= o.den * FPS:
            break
        n = round(c["t1"] * FPS) - round(c["t0"] * FPS)
        f, that = doan(c, n, o.lam_lai)
        ds.append(f"file '{f.as_posix()}'")
        tong += n
        if not that:
            thieu.append(c["id"])
    lst = H / "ghep" / "danh-sach.txt"
    lst.write_text("\n".join(ds) + "\n", encoding="utf-8")
    Path(o.ra).parent.mkdir(parents=True, exist_ok=True)
    if o.den:
        tong = min(tong, round(o.den * FPS))
    # dấu kênh (dau-kenh.py) linh hoạt 4 góc, ẩn ở intro, tiêu đề, lời lãnh tụ, đoạn tưởng niệm cuối phim
    from PIL import Image
    if Image.open(DAU).size != DAU_WH:  # vị trí 4 góc tính theo cỡ này
        sys.exit(f"dấu kênh {DAU} cỡ {Image.open(DAU).size}, cần {DAU_WH}: sửa DAU_WH")
    goc = goc_dau(pc)
    dau, _ = loc_dau(pc, goc)
    # đoạn render trình duyệt mang cờ dải màu đầy đủ (yuvj420p, pc), phim và intro dải TV: đưa hết về TV một lần
    loc = dau + "scale=out_range=tv,format=yuv420p[v]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", o.am, "-loop", "1", "-framerate", str(FPS), "-i", str(DAU),
                    "-filter_complex", loc, "-map", "[v]", "-map", "1:a", *MA_HOA, "-color_range", "tv", "-c:a", "aac_mf", "-b:a", "256k", "-frames:v", str(tong), "-t", f"{tong / FPS:.4f}", o.ra], check=True)
    so = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets",
                         "-of", "csv=p=0", o.ra], capture_output=True, text=True).stdout.strip().rstrip(",")
    print(f"{len(ds)} cảnh, {so} khung (cần {tong}); giữ chỗ {len(thieu)}: {' '.join(thieu)}")
    if int(so) != tong:
        sys.exit("SỐ KHUNG LỆCH")


if __name__ == "__main__":
    main()
