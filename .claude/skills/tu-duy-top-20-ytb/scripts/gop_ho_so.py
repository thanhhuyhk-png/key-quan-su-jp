"""Gộp số đo và phần định tính thành JSON hồ sơ Top 20 (cấu trúc ở references/mau-google-sheet.md) cho xuat_sheet.py.

Dùng:
  python gop_ho_so.py --do-kenh <thư mục do-kenh> --video-dir <thư mục TSV video> --dinh-tinh <dinh-tinh.json|kenh.tsv>
        --out ho-so-top20.json [--xep-hang xep-hang.json] [--as-of 2026-10-22] [--so-top-view 10] [--he-so-toi-thieu 3]

Đầu vào:
  --do-kenh      thư mục có <id kênh>.json do `do_kenh.py kenh --json` ghi (chỉ số + hệ số từng video).
  --video-dir    thư mục có <id kênh>.tsv (danh sách video, thu_video.py ghi) để lấy link, tiêu đề, like, thời lượng.
  --dinh-tinh    JSON {du_an, ngay_do, ngay_moc_truoc, muc_tieu, model_link, doi_chung, nhan_ban, theo_doi, chu_y,
                 kenh: {<id>: {ten, link, giu_loai, nhom, ngach, dinh_dang, tuoi_khan_gia, tuoi_muc_tin, ly_do, hoc_gi,
                 khong_hoc_gi, chu_y, nguon_so, ...}}, video: {<id video>: {de_tai, goc_tiep_can, tu_huyet, kieu_mo, anh_bia,
                 dinh_phat_lai, yeu_cau_binh_luan, kiem_tra_so, ghi_chu}}}; "kenh" cũng nhận danh sách có trường id.
                 Đuôi .tsv: bảng kênh (cột id, ten, giu_loai, nhom, ...), không có phần khác.
  --xep-hang     JSON do `do_kenh.py xep-hang --json` ghi: điểm, hạng, khoảng hạng, lý do ghi đè.
Bảng định tính KHÔNG ghi đè số đo (chỉ số kênh, điểm, hạng, cờ; trùng khoá thì giữ số đo và cảnh báo), trừ video_30_ngay.
Mỗi kênh có file đo thì vào hồ sơ; kênh chỉ có trong bảng định tính (ví dụ kênh bị loại) cũng vào (tab Khảo sát).
Video vào hồ sơ: top view (--so-top-view) cộng mọi video hệ số ≥ --he-so-toi-thieu. Kiểm tra số thật tự động chỉ ra
chua_chin | so_bo | nghi (không bao giờ 'dat': 'dat' cần người đọc bình luận, ghi trong bảng định tính).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import do_kenh as dk  # noqa: E402

SO_TOP_VIEW = 10
HE_SO_TOI_THIEU = 3.0
LIKE_TOI_THIEU_PCT = 0.5        # like dưới mức này (% view) thì nghi
HE_SO_KIEM_KY = 10.0
KHUNG_CHUA_CO = "[CHƯA CÓ]"
TRUONG_SO = {"subs", "subs_30_ngay_truoc", "sub_30_ngay_truoc", "view_30_ngay", "video_30_ngay", "view_tong", "so_video",
             "so_dai", "so_short", "hang_30_ngay_truoc"}
TRUONG_XEP_HANG = ("diem", "hang", "khoang_hang", "hang_tich_luy", "hang_da", "hang_theo_ngay_lap")
DUOC_GHI_DE_BOI_DINH_TINH = {"video_30_ngay"}   # đếm video 30 ngày từ vidIQ (gồm cả Shorts) thay cho đếm trong danh sách


# ---------- đọc bảng định tính ----------

def _kenh_dinh_tinh(thong_tin) -> dict[str, dict]:
    if isinstance(thong_tin, dict):
        out = {cid: dict(v or {}) for cid, v in thong_tin.items()}
    else:
        out = {}
        for v in thong_tin or []:
            if not v.get("id"):
                raise ValueError(f"kênh trong bảng định tính thiếu id: {v.get('ten') or v}")
            out[v["id"]] = dict(v)
    for cid, v in out.items():
        v["id"] = cid
        if "nhom" in v:
            v["nhom"] = dk.chuan_nhom(v["nhom"])
    return out


def doc_dinh_tinh(path: Path) -> dict:
    path = Path(path)
    if path.suffix.lower() == ".tsv":
        dong = []
        for r in csv.DictReader(path.open(encoding="utf-8-sig", newline=""), delimiter="\t"):
            v = {k.strip(): (x or "").strip() for k, x in r.items() if k and (x or "").strip()}
            for k in TRUONG_SO & v.keys():
                v[k] = dk.so(v[k])
            dong.append(v)
        return {"kenh": _kenh_dinh_tinh(dong)}
    dt = json.loads(path.read_text(encoding="utf-8-sig"))
    dt["kenh"] = _kenh_dinh_tinh(dt.get("kenh"))
    return dt


# ---------- kiểm tra số thật tự động ----------

def _so_phay(x: float, n: int = 2) -> str:
    return f"{x:.{n}f}".replace(".", ",")


def kiem_so_tu_dong(views: int, likes: int | None, comments: int | None, muc: str | None,
                    he_so: float | None) -> tuple[str, str]:
    """(trạng thái chuẩn, ghi chú). Không bao giờ trả 'dat': 'dat' cần đọc nội dung bình luận."""
    if muc == "chua_chin":
        return "chua_chin", "chưa chín (< 30 ngày tuổi): đo lại sau 2 tuần"
    kiem_ky = "CẦN KIỂM KỸ (hệ số ≥ 10): " if he_so is not None and he_so >= HE_SO_KIEM_KY else ""
    if likes is None or not views:
        return "so_bo", f"{kiem_ky}thiếu like hoặc view: chưa kiểm được; chưa đọc nội dung bình luận"
    if likes > views:
        return "nghi", f"{kiem_ky}like > view: nghi lỗi đơn vị"
    pct = likes / views * 100
    bl = f"bình luận {_so_phay(comments / views * 1000)}/1.000 view" if comments is not None else "không có số bình luận"
    if pct < LIKE_TOI_THIEU_PCT:
        return "nghi", f"{kiem_ky}like {_so_phay(pct)} % < 0,5 % (nghi view không thật); {bl}"
    return "so_bo", (f"{kiem_ky}like {_so_phay(pct)} %, {bl}; chưa đọc nội dung bình luận, "
                     "chưa đối chiếu sự kiện trùng")


# ---------- gộp ----------

def _doc_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8-sig"))


def _chuoi_co(co) -> str:
    if isinstance(co, str):
        return ", ".join(x.strip() for x in co.split(",") if x.strip())
    return ", ".join(co or [])


def gop(do_kenh_dir: Path, video_dir: Path, dinh_tinh: dict, xep_hang: Path | None = None, as_of: date | None = None,
        so_top_view: int = SO_TOP_VIEW, he_so_toi_thieu: float = HE_SO_TOI_THIEU) -> tuple[dict, list[str]]:
    canh_bao: list[str] = []
    if as_of is None:
        d = dk.doc_ngay(dinh_tinh.get("ngay_do"))
        as_of = d.date() if d else date.today()
    do_kenh = {}
    for p in sorted(Path(do_kenh_dir).glob("*.json")):
        d = _doc_json(p)
        if isinstance(d, dict) and "chi_so" in d:
            do_kenh[p.stem] = d
    rk = {}
    if xep_hang:
        for b in _doc_json(Path(xep_hang)).get("xep_hang", []):
            rk[b["kenh"]] = b
    dt_kenh = dinh_tinh.get("kenh") or {}
    thu_tu = list(do_kenh) + [c for c in dt_kenh if c not in do_kenh]

    kenh, ghi_de_chu_y = [], []
    for cid in thu_tu:
        k: dict = {"id": cid}
        bao_ve: set[str] = set()
        if cid in do_kenh:
            ci = dict(do_kenh[cid]["chi_so"])
            ci["co"] = list(ci.get("co") or [])
            ci.pop("ghi_de", None)
            b = rk.get(cid)
            for g in (b or {}).get("ghi_de") or []:       # áp lại ghi đè của xep-hang để số trong hồ sơ khớp bảng xếp hạng
                dk.ap_dung_ghi_de(ci, g["co"], g.get("ly_do") or "")
                ghi_de_chu_y.append({"loai": "co_du_lieu", "muc_do": "vừa", "noi_dung":
                                     f"Ghi đè bằng tay {g['co']} cho {dt_kenh.get(cid, {}).get('ten', cid)}: "
                                     f"{g.get('ly_do') or '(không ghi lý do)'}",
                                     "viec_can_lam": "Kiểm lại khi có số đo thật"})
            k.update({a: v for a, v in ci.items() if a != "co"})
            co = _chuoi_co(ci["co"])
            if b:
                k.update({a: b.get(a) for a in TRUONG_XEP_HANG})
                co = _chuoi_co(b.get("co")) or co
            elif rk:
                canh_bao.append(f"{cid}: có file đo nhưng không có trong --xep-hang (không có điểm/hạng)")
            k["co"] = co
            bao_ve = (set(ci) | set(TRUONG_XEP_HANG) | {"co", "id"}) - DUOC_GHI_DE_BOI_DINH_TINH
        if cid in dt_kenh:
            for khoa, gt in dt_kenh[cid].items():
                if khoa == "id":
                    continue
                if khoa in bao_ve:
                    canh_bao.append(f"{cid}: bảng định tính có trường '{khoa}' trùng số đo; giữ số đo, bỏ giá trị trong bảng")
                else:
                    k[khoa] = gt
        else:
            canh_bao.append(f"{cid}: có số đo nhưng chưa có phần định tính (ten, giu_loai, nhom, nguon_so…)")
            k.setdefault("ten", cid)
        if cid not in do_kenh and dt_kenh[cid].get("giu_loai") in ("Giữ", "giữ"):
            canh_bao.append(f"{cid}: kênh 'Giữ' nhưng chưa có file đo (do_kenh.py kenh --json)")
        kenh.append(k)

    video = []
    for cid, d in do_kenh.items():
        tsv = Path(video_dir) / f"{cid}.tsv"
        if not tsv.exists():
            canh_bao.append(f"{cid}: không có file video {tsv.name}; kênh này không có video trong hồ sơ")
            continue
        hsmap = {h["id"]: h for h in d.get("he_so", [])}
        dai = [v for v in dk.doc_video(tsv) if not v.is_short and v.published <= as_of]
        top = {v.id for v in sorted(dai, key=lambda v: -v.views)[:so_top_view]}
        chon = top | {i for i, h in hsmap.items() if h.get("he_so") is not None and h["he_so"] >= he_so_toi_thieu}
        for v in sorted((v for v in dai if v.id in chon), key=lambda v: -v.views):
            h = hsmap.get(v.id) or {}
            hs, muc = h.get("he_so"), h.get("muc")
            tuoi = h.get("tuoi_ngay")
            tuoi = max(1, tuoi if tuoi is not None else (as_of - v.published).days)
            st, ghi_chu = kiem_so_tu_dong(v.views, v.likes, v.comments, muc, hs)
            e = {"kenh": cid, "id": v.id, "link": f"https://youtu.be/{v.id}", "tieu_de": v.title,
                 "ngay_dang": v.published.isoformat(), "thoi_luong_s": v.duration_s, "views": v.views,
                 "view_moi_ngay": round(v.views / tuoi), "trung_vi_15_truoc": h.get("trung_vi_15_truoc"),
                 "he_so": round(hs, 2) if hs is not None else None,
                 "he_so_sau": round(h["he_so_sau"], 2) if h.get("he_so_sau") is not None else None,
                 "muc": muc, "la_top_view": v.id in top, "de_tai": v.title, "goc_tiep_can": KHUNG_CHUA_CO,
                 "tu_huyet": KHUNG_CHUA_CO, "kieu_mo": KHUNG_CHUA_CO, "anh_bia": KHUNG_CHUA_CO,
                 "dinh_phat_lai": KHUNG_CHUA_CO, "yeu_cau_binh_luan": KHUNG_CHUA_CO, "kiem_tra_so": st,
                 "ghi_chu": ghi_chu}
            if h.get("ly_do_khong_tinh") == "ngoai_cua_so":
                e["ghi_chu"] += "; ngoài cửa sổ liên tục: không có hệ số"
            tay = dict((dinh_tinh.get("video") or {}).get(v.id) or {})
            if "kiem_tra_so" in tay:
                ma = dk.trang_thai_kiem_so(tay["kiem_tra_so"])
                tay["kiem_tra_so"] = ma if ma else tay["kiem_tra_so"]
            if tay.get("ghi_chu"):
                tay["ghi_chu"] = f"{tay['ghi_chu']} | {e['ghi_chu']}"
            e.update(tay)
            video.append(e)

    ho_so = {"du_an": dinh_tinh.get("du_an", ""), "ngay_do": as_of.isoformat(),
             "ngay_moc_truoc": dinh_tinh.get("ngay_moc_truoc"), "phien_ban_cong_thuc": dk.PHIEN_BAN,
             "muc_tieu": dinh_tinh.get("muc_tieu") or {}, "model_link": dinh_tinh.get("model_link") or {},
             "kenh": kenh, "video": video, "doi_chung": dinh_tinh.get("doi_chung") or [],
             "nhan_ban": dinh_tinh.get("nhan_ban") or [], "theo_doi": dinh_tinh.get("theo_doi") or [],
             "chu_y": list(dinh_tinh.get("chu_y") or []) + ghi_de_chu_y}
    return ho_so, canh_bao


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--do-kenh", required=True)
    ap.add_argument("--video-dir", required=True)
    ap.add_argument("--dinh-tinh", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--xep-hang")
    ap.add_argument("--as-of")
    ap.add_argument("--so-top-view", type=int, default=SO_TOP_VIEW)
    ap.add_argument("--he-so-toi-thieu", type=float, default=HE_SO_TOI_THIEU)
    ns = ap.parse_args(argv)
    try:
        dt = doc_dinh_tinh(Path(ns.dinh_tinh))
    except ValueError as e:
        raise SystemExit(str(e)) from None
    as_of = dk.doc_ngay(ns.as_of).date() if ns.as_of and dk.doc_ngay(ns.as_of) else None
    hs, canh_bao = gop(Path(ns.do_kenh), Path(ns.video_dir), dt, Path(ns.xep_hang) if ns.xep_hang else None, as_of,
                       ns.so_top_view, ns.he_so_toi_thieu)
    out = Path(ns.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(hs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(hs['kenh'])} kênh; {len(hs['video'])} video; {len(canh_bao)} cảnh báo; ghi {out}")
    for c in canh_bao:
        print(f"CẢNH BÁO: {c}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
