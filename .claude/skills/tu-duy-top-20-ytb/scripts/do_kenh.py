"""Đo kênh YouTube theo chuẩn "Tư duy Top 20": trung vị video dài đủ tuổi, hệ số vượt trội,
hiệu suất chuẩn hoá theo tuổi kênh, đà hiện tại, cờ bẫy số liệu, xếp hạng có độ nhạy.

Dùng:
  python do_kenh.py kenh <danh-sach.tsv> --subs 38000 [--ngay-lap 2026-08-21] [--sub-30-ngay-truoc 12000]
        [--tong-video 22] [--ngay-video-dau 2026-09-04] [--as-of 2026-10-22] [--out ket-qua.md]
        [--meta <khoá>.meta.json]         # tong_flat, ngay_video_dau, cua_so_tu, so_hoi_vien từ thu_video.py (truyền tay ưu tiên hơn)
        [--cua-so-tu 2026-01-05]          # chỉ tính hệ số/trung vị cho video từ ngày này; ngoài cửa sổ: None kèm lý do
                                          # có cửa sổ mà thiếu --tong-video: bỏ sub/video, cờ THIEU_TONG_VIDEO_CHO_CUA_SO
        [--ty-trong-view-short 0.22]      # tỉ trọng view Shorts từ nguồn ngoài (0..1), ưu tiên hơn ước từ mẫu
        [--so-hoi-vien 14]                # số video hội viên không đọc được (thu_video.py ghi trong .meta.json)
  python do_kenh.py xep-hang <bang-kenh.tsv> [--as-of ...] [--out xep-hang.md] [--json xep-hang.json]
        [--ghi-de "<kênh>:<CỜ>[:lý do]" ...] [--do-nhay]
    bang-kenh.tsv: cột kenh, file, subs, và tuỳ chọn ngay_lap, sub_30_ngay_truoc, tong_video, ngay_video_dau,
    cua_so_tu, ty_trong_view_short, so_hoi_vien, meta (đường dẫn .meta.json cạnh bảng).

Danh sách video: TSV/CSV, nhận tên cột Việt hoặc Anh (xem COT). Chỉ dùng thư viện chuẩn.
Phiên bản công thức: PHIEN_BAN (ghi vào tab Theo dõi để so các kỳ đo).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import statistics
import sys
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

PHIEN_BAN = "2026-10-22.3"   # .3: trần 100 % và sàn nền cho % tăng sub, cửa sổ, tỉ trọng Shorts ngoài, độ nhạy (xem references/tieu-chi-va-cong-thuc.md mục 7)
SHORT_TOI_DA_S = 180          # YouTube Shorts tối đa 3 phút
TUOI_TOI_THIEU_NGAY = 30      # bỏ video chưa đủ 30 ngày khỏi trung vị (lọc tuổi tối thiểu, CHƯA phải chuẩn hoá tuổi)
SO_VIDEO_TRUNG_VI = 20        # 20 video dài gần nhất
KENH_TRE_NGAY = 90            # kênh trẻ hơn mức này dùng ngưỡng tuổi video thấp hơn
TUOI_TOI_THIEU_KENH_TRE = 14
MAU_TRUNG_VI_TOI_THIEU = 5    # dưới mức này không tính trung vị
MAU_TRUNG_VI_DU = 10          # dưới mức này gắn cờ MAU_TRUNG_VI_NHO
SO_VIDEO_TRUOC = 15           # hệ số = view / trung vị 15 video dài ngay trước
SO_VIDEO_SAU = 5
SO_VIDEO_TRUOC_TOI_THIEU = 5
MOC_CAT_PHO_BIEN = {30, 50, 60, 90, 100, 120, 150, 200, 250, 300, 500, 1000}
MUC_HE_SO = [  # (cận dưới, nhãn) — một nguồn duy nhất, xuat_sheet dùng lại
    (10.0, "can_kiem_ky"), (5.0, "manh"), (3.0, "dang_ghi"), (2.0, "hoi_cao"), (0.0, "binh_thuong")]
TRAN_PCT_TANG_KENH_TRE = 1.0  # kênh < KENH_TRE_NGAY ngày tuổi: % tăng sub 30 ngày tối đa 100 % khi xếp hạng
SAN_SUB_NEN_DA = 5_000        # sub 30 ngày trước dưới mức này: % tăng sub không dùng để xếp hạng (nền quá nhỏ)
NGUONG_TY_TRONG_SHORT = 0.2   # tỉ trọng view Shorts ≥ mức này: sub của kênh lai không dùng để xếp hạng
NGUONG_TAI_SINH_NGAY = 365    # ngày lập cách video đầu hơn mức này: kênh tái sinh
NGUONG_KENH_MOI_NGAY = 365    # nhóm "mới": tuổi tính từ video đầu
NGUONG_HANG_1_VUNG = 5 / 6    # hạng 1 ở ít nhất 5/6 cách tính mới coi là vững
CO_THEO_SUB = ("sub_moi_video", "trung_vi_chia_sub", "sub_moi_ngay_video_dau", "sub_moi_ngay_ngay_lap",
               "pct_tang_sub_30", "tang_sub_30")   # mọi chỉ số dựa trên sub: kênh lai Shorts không dùng để xếp hạng
CO_HOP_LE = (  # mọi cờ script gắn, cộng KHONG_DU_CHI_SO (xep_hang gắn); --ghi-de chỉ nhận cờ trong danh sách này
    "NGAY_TUONG_LAI", "TRUNG_VI_DUNG_VIDEO_TU_14_NGAY", "PHAN_TAN_CAO", "MAU_TRUNG_VI_NHO",
    "KHONG_DU_VIDEO_DAI_DU_30_NGAY", "KENH_QUA_MOI_DUOI_14_NGAY", "TAI_SINH", "DA_SUB_NEN_NHO",
    "PCT_TANG_BI_CHAN_100", "NHIEU_VIDEO_CUNG_NGAY", "NGHI_LOI_DON_VI", "THIEU_THOI_LUONG",
    "SHORT_UOC_THEO_THOI_LUONG", "NHIEU_SHORT", "SUB_LAN_SHORTS", "THIEU_TONG_VIDEO_CHO_CUA_SO",
    "DANH_SACH_CO_THE_BI_CAT", "DANH_SACH_THIEU_VIDEO", "IT_VIDEO", "DONG_BI_BO", "HOI_VIEN",
    "CO_VIDEO_DUOI_14_NGAY_DO_LAI_SAU_2_TUAN", "KHONG_DU_CHI_SO")
SO_CACH_TOI_THIEU = 3         # một cách tính chỉ hợp lệ trong độ nhạy khi xếp được ít nhất ngần này kênh
SO_CACH_HOP_LE_TOI_THIEU_DE_VUNG = 5  # dưới ngần này cách hợp lệ thì chưa đủ để gọi hạng 1 là vững
NHOM_NHAN = {"moi": "Mới < 12 tháng", "on_dinh": "Ổn định ≥ 2 năm", "cung_nguon_luc": "Cùng nguồn lực"}
KIEM_TRA_SO = ("chua_chin", "so_bo", "dat", "nghi")   # trạng thái chuẩn của "kiểm tra số thật"
NHAN_KIEM_TRA_SO = {"chua_chin": "chưa chín", "so_bo": "sơ bộ", "dat": "đạt", "nghi": "nghi ngờ"}
RONG = {"", "-", "–", "na", "n/a", "nan", "none", "null", "inf", "-inf", "#n/a"}

COT = {
    "id": ["id", "video_id", "videoid"],
    "title": ["tieu_de", "title", "ten"],
    "published": ["ngay_dang", "published", "publishedat", "upload_date", "timestamp_iso", "date", "ngay"],
    "duration_s": ["thoi_luong_s", "duration", "duration_s", "length_s", "thoi_luong"],
    "views": ["view", "views", "view_count", "luot_xem"],
    "likes": ["like", "likes", "like_count"],
    "comments": ["binh_luan", "comments", "comment_count"],
    "is_short": ["is_short", "short", "la_short"],
}


@dataclass
class Video:
    id: str
    title: str
    published: date
    views: int
    likes: int | None
    comments: int | None
    duration_s: int | None
    is_short_flag: bool | None = None
    published_dt: datetime | None = None

    @property
    def is_short(self) -> bool:
        """Cờ is_short (từ URL /shorts/ hoặc tab Shorts) là chuẩn; không có cờ thì ước bằng 0 < thời lượng ≤ 180 giây."""
        if self.is_short_flag is not None:
            return self.is_short_flag
        return self.duration_s is not None and 0 < self.duration_s <= SHORT_TOI_DA_S

    @property
    def short_la_uoc(self) -> bool:
        return self.is_short_flag is None

    @property
    def khoa_thu_tu(self):
        return (self.published_dt or datetime(self.published.year, self.published.month, self.published.day),
                self.id)


# ---------- đọc số, ngày ----------

def so(s) -> int | None:
    """Đọc số đếm kiểu Việt/Anh: '1.234.567', '809 N', '1,2 Tr', '1 triệu', '3.4K', '1.5M'.
    Trả None cho ô rỗng, nan, ô không đọc được, số âm."""
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return None if s != s or s < 0 else int(round(s))
    t = str(s).strip().lower().replace("\u00a0", " ")
    if t in RONG:
        return None
    nhan = 1
    for mau, he_so in ((r"tỷ|ty|b", 1_000_000_000), (r"triệu|trieu|tr|m", 1_000_000),
                       (r"nghìn|nghin|ngàn|ngan|n|k", 1_000)):
        m = re.fullmatch(rf"([0-9][0-9.,]*)\s*(?:{mau})\.?", t)
        if m:
            nhan, t = he_so, m.group(1)
            break
    t = t.replace(" ", "")
    try:
        if nhan > 1:
            v = float(t.replace(",", "."))
        elif re.fullmatch(r"[1-9]\d{0,2}([.,]\d{3})+", t):   # 1.234.567 hoặc 1,234,567
            v = float(re.sub(r"[.,]", "", t))
        else:
            v = float(t.replace(",", "."))                    # 1258.0 hoặc 1258,0
    except ValueError:
        return None
    if v != v or v < 0 or v == float("inf"):
        return None
    return int(round(v * nhan))


def thoi_luong(s) -> int | None:
    """Giây từ '1258', '20:58', '1:02:03', 'PT20M58S'."""
    if s is None:
        return None
    t = str(s).strip()
    m = re.fullmatch(r"(\d+):(\d{1,2})(?::(\d{1,2}))?", t)
    if m:
        a, b, c = m.groups()
        return int(a) * 3600 + int(b) * 60 + int(c) if c is not None else int(a) * 60 + int(b)
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", t, re.I)
    if m and any(m.groups()):
        h, mi, se = (int(x) if x else 0 for x in m.groups())
        return h * 3600 + mi * 60 + se
    return so(t)


def doc_ngay(s) -> datetime | None:
    """Nhận 2026-10-22, 2026-10-22T07:30:00Z, 20261022, 22/10/2026, 2026-9-3. Trả None nếu không đọc được."""
    if s is None:
        return None
    t = str(s).strip()
    if not t or t.lower() in RONG:
        return None
    try:
        if re.fullmatch(r"\d{8}", t):
            return datetime.strptime(t, "%Y%m%d")
        if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", t):
            return datetime.strptime(t, "%d/%m/%Y")
        m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", t)
        if m:
            return datetime(*map(int, m.groups()))
        return datetime.fromisoformat(t.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _ngay(s) -> date:
    d = doc_ngay(s)
    if d is None:
        raise ValueError(f"không đọc được ngày: {s!r}")
    return d.date()


def _bool(s) -> bool | None:
    if s is None or str(s).strip().lower() in RONG:
        return None
    return str(s).strip().lower() in {"1", "true", "yes", "co", "có", "x"}


def _doc_bang(text: str) -> list[dict]:
    if not text.strip():
        return []
    dong_dau = text.splitlines()[0]
    delim = "\t" if "\t" in dong_dau else ","
    return list(csv.DictReader(io.StringIO(text, newline=""), delimiter=delim))


def doc_video(path: Path, thong_ke: dict | None = None) -> list[Video]:
    """Đọc danh sách video. thong_ke (nếu truyền) được điền: tong_dong, bo_thieu_view_ngay, bo_trung_id."""
    rows = _doc_bang(Path(path).read_text(encoding="utf-8-sig"))
    tk = {"tong_dong": len(rows), "bo_thieu_view_ngay": 0, "bo_trung_id": 0}
    if not rows:
        if thong_ke is not None:
            thong_ke.update(tk)
        return []
    keys = {k.strip().lower(): k for k in rows[0].keys() if k is not None}

    def lay(row, ten):
        for alias in COT[ten]:
            if alias in keys:
                return row.get(keys[alias])
        return None

    theo_id: dict[str, Video] = {}
    khong_id: list[Video] = []
    for r in rows:
        views = so(lay(r, "views"))
        dt = doc_ngay(lay(r, "published"))
        if views is None or dt is None:
            tk["bo_thieu_view_ngay"] += 1
            continue
        co_gio = dt.hour or dt.minute or dt.second
        v = Video(id=str(lay(r, "id") or "").strip(), title=str(lay(r, "title") or ""), published=dt.date(),
                  views=views, likes=so(lay(r, "likes")), comments=so(lay(r, "comments")),
                  duration_s=thoi_luong(lay(r, "duration_s")), is_short_flag=_bool(lay(r, "is_short")),
                  published_dt=dt if co_gio else None)
        if not v.id:
            khong_id.append(v)
        elif v.id in theo_id:
            tk["bo_trung_id"] += 1
            if v.views > theo_id[v.id].views:
                theo_id[v.id] = v
        else:
            theo_id[v.id] = v
    if thong_ke is not None:
        thong_ke.update(tk)
    return list(theo_id.values()) + khong_id


# ---------- hệ số vượt trội ----------

def muc_he_so(h: float | None) -> str | None:
    if h is None:
        return None
    for can, nhan in MUC_HE_SO:
        if h >= can:
            return nhan
    return "binh_thuong"


def he_so_vuot_troi(videos: list[Video], as_of: date | None = None, cua_so_tu: date | None = None) -> list[dict]:
    """Hệ số = view ÷ trung vị 15 video dài đăng ngay trước (≥ 5 video mới tính).
    Hệ số sau = trung vị đúng 5 video đăng ngay sau ÷ trung vị trước (thiếu 5 thì không tính).
    Video < 30 ngày tuổi gắn mức 'chua_chin' (view chưa đủ thời gian).
    cua_so_tu: chỉ video đăng từ ngày này mới có hệ số và mới làm hàng xóm của nhau; video cũ hơn (lẻ tẻ, không có
    hàng xóm liền kề) trả he_so None, ly_do_khong_tinh 'ngoai_cua_so'."""
    dai = sorted([v for v in videos if not v.is_short], key=lambda v: v.khoa_thu_tu)
    trong = [v for v in dai if cua_so_tu is None or v.published >= cua_so_tu]
    vi_tri = {id(v): i for i, v in enumerate(trong)}
    ngay_dem: dict[date, int] = {}
    for v in dai:
        ngay_dem[v.published] = ngay_dem.get(v.published, 0) + 1
    out = []
    for v in dai:
        tuoi = (as_of - v.published).days if as_of else None
        hs = hs_sau = tv = None
        ly_do = None
        truoc: list[Video] = []
        sau: list[Video] = []
        if id(v) not in vi_tri:
            ly_do = "ngoai_cua_so"
        else:
            i = vi_tri[id(v)]
            truoc = trong[max(0, i - SO_VIDEO_TRUOC):i]
            sau = trong[i + 1:i + 1 + SO_VIDEO_SAU]
            if len(truoc) >= SO_VIDEO_TRUOC_TOI_THIEU:
                tv = statistics.median(x.views for x in truoc)
                hs = v.views / tv if tv else None
                if len(sau) == SO_VIDEO_SAU and tv:
                    hs_sau = statistics.median(x.views for x in sau) / tv
                if not tv:
                    ly_do = "trung_vi_truoc_bang_0"
            else:
                ly_do = "it_hon_5_video_truoc"
        muc = muc_he_so(hs)
        if tuoi is not None and tuoi < TUOI_TOI_THIEU_NGAY and hs is not None:
            muc = "chua_chin"
        out.append({"id": v.id, "title": v.title, "ngay": v.published.isoformat(), "tuoi_ngay": tuoi,
                    "views": v.views, "n_truoc": len(truoc), "trung_vi_15_truoc": tv, "he_so": hs,
                    "n_sau": len(sau), "he_so_sau": hs_sau, "muc": muc, "ly_do_khong_tinh": ly_do,
                    "cung_ngay": ngay_dem[v.published] > 1 and v.published_dt is None})
    return out


# ---------- chỉ số kênh ----------

def _bo_chi_so_sub(m: dict) -> None:
    """Kênh lai Shorts: sub có thể đến từ Shorts nên bỏ các chỉ số dựa trên sub khỏi xếp hạng (giữ bản thô *_tho)."""
    for k in CO_THEO_SUB:
        if m.get(k) is not None:
            m.setdefault(k + "_tho", m[k])   # không đè bản thô gốc (vd % tăng đã bị chặn trần)
            m[k] = None


def chi_so_kenh(videos: list[Video], subs: int | None, as_of: date, ngay_lap: date | None = None,
                tong_video: int | None = None, ngay_video_dau: date | None = None,
                sub_30_ngay_truoc: int | None = None, dong_bo: int = 0, cua_so_tu: date | None = None,
                ty_trong_view_short: float | None = None, so_hoi_vien: int = 0) -> dict:
    """cua_so_tu: chỉ video đăng từ ngày này được dùng (danh sách cố ý cắt thì không báo thiếu video).
    ty_trong_view_short: tỉ trọng view Shorts (0..1) từ nguồn ngoài, ưu tiên hơn ước từ mẫu Shorts đã lấy."""
    co: list[str] = []
    tuong_lai = [v for v in videos if v.published > as_of]
    if tuong_lai:
        co.append("NGAY_TUONG_LAI")
        videos = [v for v in videos if v.published <= as_of]
    dau_tam = ngay_video_dau or (min(v.published for v in videos) if videos else None)
    n_ngoai_cua_so = 0
    if cua_so_tu is not None:
        trong = [v for v in videos if v.published >= cua_so_tu]
        n_ngoai_cua_so, videos = len(videos) - len(trong), trong
    dai = sorted([v for v in videos if not v.is_short], key=lambda v: v.khoa_thu_tu, reverse=True)
    shorts = [v for v in videos if v.is_short]
    nguong_tuoi = TUOI_TOI_THIEU_NGAY
    if dau_tam and (as_of - dau_tam).days < KENH_TRE_NGAY:
        nguong_tuoi = TUOI_TOI_THIEU_KENH_TRE   # kênh < 90 ngày: hạ ngưỡng để không loại oan kênh mới đang lên
        co.append("TRUNG_VI_DUNG_VIDEO_TU_14_NGAY")
    du_tuoi = [v for v in dai if (as_of - v.published).days >= nguong_tuoi]
    mau = du_tuoi[:SO_VIDEO_TRUNG_VI]
    n_video = tong_video if tong_video is not None else len(videos)
    m: dict = {"n_video": n_video, "n_trong_danh_sach": len(videos), "n_dai": len(dai), "n_short": len(shorts),
               "n_dai_dung_tinh": len(mau), "nguong_tuoi_video": nguong_tuoi, "subs": subs, "dong_bo": dong_bo,
               "phien_ban": PHIEN_BAN, "cua_so_tu": cua_so_tu.isoformat() if cua_so_tu else None,
               "n_ngoai_cua_so": n_ngoai_cua_so, "so_hoi_vien": so_hoi_vien}

    for k in ("trung_vi_20_dai", "cao_nhat", "thap_nhat", "phan_tan", "so_video_tren_2x", "ty_le_tren_2x",
              "trung_vi_chia_sub", "ty_le_like_trung_vi", "da_trung_vi"):
        m[k] = None
    if len(mau) >= MAU_TRUNG_VI_TOI_THIEU:
        views = [v.views for v in mau]
        tv = statistics.median(views)
        m["trung_vi_20_dai"] = tv
        m["cao_nhat"], m["thap_nhat"] = max(views), min(views)
        m["phan_tan"] = max(views) / tv if tv else None
        m["so_video_tren_2x"] = sum(1 for x in views if x > 2 * tv)
        m["ty_le_tren_2x"] = m["so_video_tren_2x"] / len(views)
        m["trung_vi_chia_sub"] = tv / subs if subs else None
        likes = [v.likes / v.views for v in mau if v.likes is not None and v.views]
        m["ty_le_like_trung_vi"] = statistics.median(likes) if likes else None
        if m["phan_tan"] and m["phan_tan"] > 20:
            co.append("PHAN_TAN_CAO")
        if len(mau) < MAU_TRUNG_VI_DU:
            co.append("MAU_TRUNG_VI_NHO")
    else:
        co.append("KHONG_DU_VIDEO_DAI_DU_30_NGAY")
    if len(du_tuoi) >= 15:   # đà hiện tại: 10 video đủ tuổi gần nhất so 10 video trước đó
        moi, cu = du_tuoi[:10], du_tuoi[10:20]
        tv_cu = statistics.median(v.views for v in cu)
        m["da_trung_vi"] = statistics.median(v.views for v in moi) / tv_cu if tv_cu else None

    dau = dau_tam
    if dau:
        tuoi_vd = max(1, (as_of - dau).days)
        m["ngay_video_dau"] = dau.isoformat()
        m["tuoi_tu_video_dau"] = tuoi_vd
        tong_view = sum(v.views for v in videos)
        m["view_moi_ngay_video_dau"] = tong_view / tuoi_vd if tong_video is None and cua_so_tu is None else None
        m["sub_moi_ngay_video_dau"] = subs / tuoi_vd if subs is not None else None
        if tuoi_vd < 14:
            co.append("KENH_QUA_MOI_DUOI_14_NGAY")
    m["sub_moi_video"] = subs / n_video if subs is not None and n_video else None
    if cua_so_tu is not None and tong_video is None:
        m["sub_moi_video"] = None           # n_video mới là số video trong cửa sổ: chia sub cho nó thì thổi phồng
        co.append("THIEU_TONG_VIDEO_CHO_CUA_SO")
    if ngay_lap:
        tuoi_lap = max(1, (as_of - ngay_lap).days)
        m["tuoi_tu_ngay_lap"] = tuoi_lap
        m["sub_moi_ngay_ngay_lap"] = subs / tuoi_lap if subs is not None else None
        dau_chac = ngay_video_dau is not None or (
            cua_so_tu is None and len(videos) not in MOC_CAT_PHO_BIEN and (tong_video is None or tong_video <= len(videos)))
        if dau and dau_chac and (dau - ngay_lap).days > NGUONG_TAI_SINH_NGAY:
            co.append("TAI_SINH")   # lập từ lâu, video công khai mới đây: sub có thể là lịch sử, đừng coi là "mới"
    if sub_30_ngay_truoc is not None and subs is not None:
        m["subs_30_ngay_truoc"] = sub_30_ngay_truoc
        m["tang_sub_30"] = subs - sub_30_ngay_truoc
        pct = (subs - sub_30_ngay_truoc) / sub_30_ngay_truoc if sub_30_ngay_truoc else None
        if sub_30_ngay_truoc < SAN_SUB_NEN_DA:
            co.append("DA_SUB_NEN_NHO")
            m["pct_tang_sub_30_tho"] = pct
            pct = None
        elif pct is not None and m.get("tuoi_tu_video_dau") is not None and \
                m["tuoi_tu_video_dau"] < KENH_TRE_NGAY and pct > TRAN_PCT_TANG_KENH_TRE:
            co.append("PCT_TANG_BI_CHAN_100")
            m["pct_tang_sub_30_tho"] = pct
            pct = TRAN_PCT_TANG_KENH_TRE
        m["pct_tang_sub_30"] = pct
    m["video_30_ngay"] = sum(1 for v in videos if (as_of - v.published).days < 30)

    ty_mau = None
    if videos:
        dem_ngay: dict[date, int] = {}
        for v in videos:
            dem_ngay[v.published] = dem_ngay.get(v.published, 0) + 1
        if max(dem_ngay.values()) >= 5:
            co.append("NHIEU_VIDEO_CUNG_NGAY")
        if any(v.likes is not None and v.likes > v.views for v in videos):
            co.append("NGHI_LOI_DON_VI")
        elif subs and subs >= 10_000 and mau and max(v.views for v in mau) < 1_000:
            co.append("NGHI_LOI_DON_VI")
        if sum(1 for v in videos if v.duration_s is None and v.is_short_flag is None) > len(videos) / 2:
            co.append("THIEU_THOI_LUONG")
        if any(v.short_la_uoc for v in videos):
            co.append("SHORT_UOC_THEO_THOI_LUONG")
        if len(shorts) / len(videos) > 0.5:
            co.append("NHIEU_SHORT")
        tong_v = sum(v.views for v in videos)
        ty_mau = sum(v.views for v in shorts) / tong_v if tong_v else None
    if ty_trong_view_short is not None:
        m["ty_trong_view_short"], m["ty_trong_view_short_nguon"] = ty_trong_view_short, "ngoai"
        m["ty_trong_view_short_mau"] = ty_mau
    else:
        m["ty_trong_view_short"], m["ty_trong_view_short_nguon"] = ty_mau, "mau" if ty_mau is not None else None
    if m["ty_trong_view_short"] is not None and m["ty_trong_view_short"] >= NGUONG_TY_TRONG_SHORT:
        co.append("SUB_LAN_SHORTS")
        _bo_chi_so_sub(m)
    if tong_video is None and cua_so_tu is None and len(videos) in MOC_CAT_PHO_BIEN:
        co.append("DANH_SACH_CO_THE_BI_CAT")
    if tong_video is not None and cua_so_tu is None and tong_video > len(videos):
        co.append("DANH_SACH_THIEU_VIDEO")
    if n_video < 10:
        co.append("IT_VIDEO")
    if dong_bo:
        co.append("DONG_BI_BO")
    if so_hoi_vien:
        co.append("HOI_VIEN")   # video hội viên không đọc được: ngày video đầu có thể muộn hơn thực tế
    if dai and (as_of - dai[0].published).days < 14:
        co.append("CO_VIDEO_DUOI_14_NGAY_DO_LAI_SAU_2_TUAN")
    m["co"] = co
    return m


def phan_tich_ghi_de(cac_xau: list[str]) -> list[tuple[str, str, str]]:
    """'<kênh>:<CỜ>[:lý do]' thành (kênh, CỜ, lý do). Tên kênh không chứa dấu hai chấm; lý do thì được."""
    out = []
    for xau in cac_xau or []:
        kenh, _, con_lai = xau.partition(":")
        co, _, ly_do = con_lai.partition(":")
        kenh, co = kenh.strip(), co.strip().upper()
        if not kenh or not re.fullmatch(r"[A-Z][A-Z0-9_]+", co):
            raise ValueError(f"--ghi-de cần dạng '<kênh>:<CỜ>[:lý do]' (CỜ viết hoa, gạch dưới), nhận {xau!r}")
        if co not in CO_HOP_LE:
            raise ValueError(f"--ghi-de: cờ {co!r} không có trong danh sách hợp lệ ({', '.join(CO_HOP_LE)})")
        out.append((kenh, co, ly_do.strip()))
    return out


def ap_dung_ghi_de(m: dict, co: str, ly_do: str = "") -> None:
    """Ghi đè bằng tay có lý do: thêm cờ (SUB_LAN_SHORTS còn bỏ các chỉ số dựa trên sub) và ghi lý do vào m['ghi_de']."""
    co = co.strip().upper()
    if co not in m["co"]:
        m["co"].append(co)
    if co == "SUB_LAN_SHORTS":
        _bo_chi_so_sub(m)
    m.setdefault("ghi_de", []).append({"co": co, "ly_do": ly_do})


# ---------- nhóm kênh, kiểm tra số thật ----------

def chuan_nhom(nhom, tuoi_ngay: int | None = None) -> list[str]:
    """Nhóm kênh (chuỗi cũ, nhãn hiển thị hoặc danh sách) thành danh sách mã. Có tuoi_ngay (từ video đầu) thì cờ
    'moi' được tính lại: dưới 365 ngày thì có, ngược lại thì không."""
    if nhom is None:
        phan = []
    elif isinstance(nhom, (list, tuple, set)):
        phan = list(nhom)
    else:
        phan = re.split(r"[,;·|+]", str(nhom))
    nfc = lambda t: unicodedata.normalize("NFC", str(t)).strip()
    nguoc = {nfc(v).casefold(): k for k, v in NHOM_NHAN.items()}
    out: list[str] = []
    for x in phan:
        t = nfc(x)
        if not t:
            continue
        ma = t if t in NHOM_NHAN else nguoc.get(t.casefold(), t)
        if ma not in out:
            out.append(ma)
    if tuoi_ngay is not None:
        if tuoi_ngay < NGUONG_KENH_MOI_NGAY and "moi" not in out:
            out.insert(0, "moi")
        elif tuoi_ngay >= NGUONG_KENH_MOI_NGAY and "moi" in out:
            out.remove("moi")
    return out


def trang_thai_kiem_so(s) -> str | None:
    """Trạng thái chuẩn của 'kiểm tra số thật': chua_chin | so_bo | dat | nghi. Nhận cả chuỗi cũ khi nó BẮT ĐẦU bằng
    nguyên từ 'đạt', 'nghi' / 'nghi ngờ', 'sơ bộ', 'chưa chín' (không khớp 'nghiên cứu', 'đạtxx'); 'loại' cũ = nghi."""
    t = unicodedata.normalize("NFC", str(s or "")).strip().casefold()
    if not t:
        return None
    if t in KIEM_TRA_SO:
        return t
    for mau, ma in ((r"đạt", "dat"), (r"nghi(?: ngờ)?", "nghi"), (r"loại", "nghi"), (r"sơ bộ", "so_bo"),
                    (r"chưa chín", "chua_chin")):
        if re.match(mau + r"(?!\w)", t):
            return ma
    return None


# ---------- xếp hạng ----------

# Bộ tiêu chí (cao = tốt). "tich_luy" = hiệu suất từ đầu; "da" = đà hiện tại; "tong" = cả hai.
BO_TIEU_CHI = {
    "tich_luy": ["sub_moi_video", "trung_vi_20_dai", "trung_vi_chia_sub", "sub_moi_ngay_video_dau"],
    "da": ["pct_tang_sub_30", "da_trung_vi", "sub_moi_ngay_video_dau"],
}
BO_TIEU_CHI["tong"] = list(dict.fromkeys(BO_TIEU_CHI["tich_luy"] + BO_TIEU_CHI["da"]))
SO_TIEU_CHI_TOI_THIEU = 3


def _phan_vi(gia_tri: dict[str, float | None]) -> dict[str, float | None]:
    """Phân vị trung bình (mid-rank) 0–100; thiếu thì None (không bị tính 0)."""
    co_so = [v for v in gia_tri.values() if v is not None]
    n = len(co_so)
    out = {}
    for k, v in gia_tri.items():
        if v is None or n == 0:
            out[k] = None
        else:
            duoi = sum(1 for x in co_so if x < v)
            bang = sum(1 for x in co_so if x == v)
            out[k] = 100.0 * (duoi + 0.5 * bang) / n
    return out


def _diem(kenh: dict[str, dict], tieu_chi: list[str]) -> dict[str, tuple[float | None, int]]:
    pv = {t: _phan_vi({k: m.get(t) for k, m in kenh.items()}) for t in tieu_chi}
    out = {}
    for k in kenh:
        vals = [pv[t][k] for t in tieu_chi if pv[t][k] is not None]
        out[k] = (sum(vals) / len(vals) if len(vals) >= SO_TIEU_CHI_TOI_THIEU else None, len(vals))
    return out


def _hang(diem: dict[str, float | None]) -> dict[str, int | None]:
    """Hạng kiểu cạnh tranh trên điểm làm tròn 1 chữ số: 1, 2, 2, 4."""
    co = {k: round(v, 1) for k, v in diem.items() if v is not None}
    out = {}
    for k in diem:
        out[k] = None if k not in co else 1 + sum(1 for x in co.values() if x > co[k])
    return out


def xep_hang(kenh: dict[str, dict]) -> list[dict]:
    """Điểm = trung bình phân vị các tiêu chí CÓ giá trị (≥ 3 tiêu chí mới xếp).
    Tính 3 bộ (tổng / tích luỹ / đà) để thấy độ nhạy; 'hang' = bộ tổng.
    Thêm hạng theo ngày lập khi ≥ 80 % kênh có ngày lập."""
    if not kenh:
        return []
    bo = {ten: _diem(kenh, tc) for ten, tc in BO_TIEU_CHI.items()}
    hang = {ten: _hang({k: v[0] for k, v in d.items()}) for ten, d in bo.items()}
    co_lap = sum(1 for m in kenh.values() if m.get("sub_moi_ngay_ngay_lap") is not None)
    hang_lap = None
    if co_lap >= 0.8 * len(kenh):
        tc_lap = [t if t != "sub_moi_ngay_video_dau" else "sub_moi_ngay_ngay_lap" for t in BO_TIEU_CHI["tong"]]
        d_lap = _diem(kenh, tc_lap)
        hang_lap = _hang({k: v[0] for k, v in d_lap.items()})
    pv_spv = _phan_vi({k: m.get("sub_moi_video") for k, m in kenh.items()})
    tv_n = statistics.median(m["n_video"] for m in kenh.values())
    bang = []
    for k, m in kenh.items():
        diem, n_tc = bo["tong"][k]
        cac_hang = [h for h in (hang["tong"][k], hang["tich_luy"][k], hang["da"][k]) if h is not None]
        co = list(m["co"])
        if diem is None:
            co.append("KHONG_DU_CHI_SO")
        bang.append({
            "kenh": k, "diem": round(diem, 1) if diem is not None else None, "hang": hang["tong"][k],
            "n_tieu_chi": n_tc,
            "hang_tich_luy": hang["tich_luy"][k], "hang_da": hang["da"][k],
            "hang_theo_ngay_lap": hang_lap[k] if hang_lap else None,
            "khoang_hang": f"{min(cac_hang)}–{max(cac_hang)}" if cac_hang else None,
            "it_video_sub_nhieu": bool(pv_spv[k] is not None and pv_spv[k] >= 75 and m["n_video"] <= tv_n),
            **{t: m.get(t) for t in ["n_video", "subs", "sub_moi_video", "trung_vi_20_dai", "trung_vi_chia_sub",
                                      "ty_le_tren_2x", "phan_tan", "sub_moi_ngay_video_dau", "pct_tang_sub_30",
                                      "da_trung_vi", "tuoi_tu_video_dau", "n_dai_dung_tinh"]},
            "ghi_de": m.get("ghi_de"), "co": ",".join(co)})
    return sorted(bang, key=lambda b: (b["hang"] is None, b["hang"] or 0, b["kenh"]))


def _bien_the_do_nhay() -> list[tuple[str, list[str], object]]:
    tong = BO_TIEU_CHI["tong"]
    return [
        ("tổng (cách chính)", tong, None),
        ("tích luỹ", BO_TIEU_CHI["tich_luy"], None),
        ("đà", BO_TIEU_CHI["da"], None),
        ("tổng bỏ % tăng sub 30 ngày", [t for t in tong if t != "pct_tang_sub_30"], None),
        ("tổng, chỉ kênh ≥ 90 ngày tuổi",
         tong, lambda m: m.get("tuoi_tu_video_dau") is None or m["tuoi_tu_video_dau"] >= KENH_TRE_NGAY),
        ("chỉ trung vị tuyệt đối (trung vị, đà trung vị, trung vị ÷ sub)",
         ["trung_vi_20_dai", "da_trung_vi", "trung_vi_chia_sub"], None),
    ]


def do_nhay(kenh: dict[str, dict]) -> dict:
    """Chạy xếp hạng bằng nhiều cách tính và đếm kênh nào đứng hạng 1 ở bao nhiêu cách. Cách nào xếp được ít hơn
    SO_CACH_TOI_THIEU kênh (n_xep) thì hạng 1 ở đó vô nghĩa: không tính vào 'hạng 1 ở n/m' (m = số cách hợp lệ).
    'hang_1_vung' = kênh hạng 1 ở ít nhất 5/6 số cách hợp lệ (NGUONG_HANG_1_VUNG), và chỉ khi có ít nhất
    SO_CACH_HOP_LE_TOI_THIEU_DE_VUNG cách hợp lệ: chênh điểm lớn ở cách chính chưa chắc vững nếu đổi cách tính là mất ngôi."""
    bien_the, dem = [], {k: 0 for k in kenh}
    for ten, tieu_chi, loc in _bien_the_do_nhay():
        tap = {k: m for k, m in kenh.items() if loc is None or loc(m)}
        diem = _diem(tap, tieu_chi) if tap else {}
        hang = _hang({k: v[0] for k, v in diem.items()})
        n_xep = sum(1 for h in hang.values() if h is not None)
        hop_le = n_xep >= SO_CACH_TOI_THIEU
        dau = sorted(k for k, h in hang.items() if h == 1)
        if hop_le:
            for k in dau:
                dem[k] += 1
        bien_the.append({"ten": ten, "n_kenh": len(tap), "n_xep": n_xep, "hop_le": hop_le, "hang_1": dau})
    m_hop_le = sum(1 for b in bien_the if b["hop_le"])
    hang_1_o = dict(sorted(((k, c) for k, c in dem.items() if c), key=lambda kv: (-kv[1], kv[0])))
    du_cach = m_hop_le >= SO_CACH_HOP_LE_TOI_THIEU_DE_VUNG
    vung = sorted(k for k, c in hang_1_o.items() if du_cach and c / m_hop_le >= NGUONG_HANG_1_VUNG - 1e-9)
    return {"so_cach": len(bien_the), "so_cach_hop_le": m_hop_le, "bien_the": bien_the, "hang_1_o": hang_1_o,
            "hang_1_vung": vung}


# ---------- in ----------

def _fmt(x) -> str:
    if x is None:
        return "–"
    if isinstance(x, bool):
        return "Có" if x else "Không"
    if isinstance(x, float):
        return f"{x:,.2f}" if abs(x) < 100 else f"{x:,.0f}"
    if isinstance(x, int):
        return f"{x:,}"
    if isinstance(x, (list, tuple)):
        return ", ".join(map(str, x))
    return str(x).replace("|", "\\|").replace("\n", " ")


def _bang_md(rows: list[dict], cot: list[str]) -> str:
    out = ["| " + " | ".join(cot) + " |", "|" + "---|" * len(cot)]
    for r in rows:
        out.append("| " + " | ".join(_fmt(r.get(c)) for c in cot) + " |")
    return "\n".join(out)


def _utf8():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")


def ty_le(s) -> float:
    """Tỉ lệ 0..1 cho tham số dòng lệnh (nhận dấu phẩy thập phân)."""
    try:
        v = float(str(s).strip().replace(",", "."))
    except ValueError:
        raise argparse.ArgumentTypeError(f"không đọc được tỉ lệ: {s!r}") from None
    if not 0 <= v <= 1:
        raise argparse.ArgumentTypeError(f"tỉ lệ phải trong khoảng 0..1 (0,22 = 22 %), nhận {s!r}")
    return v


def _o(r: dict, ten: str) -> str:
    return (r.get(ten) or "").strip()


def doc_meta(path: Path) -> dict:
    """Đọc <kênh>.meta.json của thu_video.py: tổng video, ngày video đầu, cửa sổ, số hội viên. Meta ghi lỗi thu
    dữ liệu (thiếu video, tab lỗi) thì từ chối: số đo trên dữ liệu thiếu không dùng được."""
    d = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if d.get("loi"):
        raise SystemExit(f"{path}: thu dữ liệu chưa trọn vẹn ({d['loi']}); chạy lại thu_video.py rồi mới đo")
    return {"tong_video": d.get("tong_flat"), "ngay_video_dau": d.get("ngay_video_dau"),
            "cua_so_tu": d.get("cua_so_tu"), "so_hoi_vien": d.get("so_hoi_vien")}


def _uu_tien(truyen, meta: dict, khoa: str):
    """Giá trị truyền tay (dòng lệnh, cột bảng) ưu tiên hơn giá trị trong meta."""
    return truyen if truyen not in (None, "") else meta.get(khoa)


def _tim_kenh(kenh: dict[str, dict], ten: str) -> str:
    """Khớp tên kênh trong --ghi-de: đúng nguyên văn, hoặc không phân biệt hoa thường/dạng Unicode và duy nhất."""
    if ten in kenh:
        return ten
    chuan = lambda t: unicodedata.normalize("NFC", t).strip().casefold()
    khop = [k for k in kenh if chuan(k) == chuan(ten)]
    if len(khop) == 1:
        return khop[0]
    raise SystemExit(f"--ghi-de: không có kênh {ten!r} trong bảng (kênh có: {', '.join(list(kenh)[:8])}…)")


def main(argv=None) -> int:
    _utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="lenh", required=True)
    a = sub.add_parser("kenh")
    a.add_argument("file")
    a.add_argument("--subs", type=so, required=True)
    a.add_argument("--ngay-lap")
    a.add_argument("--sub-30-ngay-truoc", type=so)
    a.add_argument("--tong-video", type=so)
    a.add_argument("--ngay-video-dau")
    a.add_argument("--cua-so-tu", help="chỉ video đăng từ ngày này mới được đo và tính hệ số")
    a.add_argument("--ty-trong-view-short", type=ty_le,
                   help="tỉ trọng view Shorts 0..1 từ nguồn ngoài (vd vidIQ hoặc YouTube Data API, 30 ngày), ưu tiên hơn ước từ mẫu")
    a.add_argument("--so-hoi-vien", type=so, default=None, help="số video hội viên không đọc được")
    a.add_argument("--meta", help="<kênh>.meta.json của thu_video.py: lấy tong_flat, ngay_video_dau, cua_so_tu, so_hoi_vien "
                   "(tham số truyền tay ưu tiên hơn)")
    a.add_argument("--as-of", default=date.today().isoformat())
    a.add_argument("--out")
    a.add_argument("--json", help="ghi chỉ số + hệ số dạng JSON (để gộp vào hồ sơ Top 20)")
    b = sub.add_parser("xep-hang")
    b.add_argument("bang")
    b.add_argument("--as-of", default=date.today().isoformat())
    b.add_argument("--out")
    b.add_argument("--json", help="ghi bảng xếp hạng dạng JSON")
    b.add_argument("--ghi-de", action="append", default=[], metavar="KENH:CO[:LY_DO]",
                   help="ghi đè bằng tay có lý do, lặp được; vd 'Kênh A:SUB_LAN_SHORTS:nguồn ngoài báo 22 %% view là Shorts'")
    b.add_argument("--do-nhay", action="store_true", help="chạy 6 cách tính và in 'hạng 1 ở n/6 cách' cho từng kênh")
    ns = ap.parse_args(argv)
    as_of = _ngay(ns.as_of)

    if ns.lenh == "kenh":
        tk: dict = {}
        vids = doc_video(Path(ns.file), tk)
        ma = doc_meta(Path(ns.meta)) if ns.meta else {}
        cs, dau = _uu_tien(ns.cua_so_tu, ma, "cua_so_tu"), _uu_tien(ns.ngay_video_dau, ma, "ngay_video_dau")
        cua_so = _ngay(cs) if cs else None
        m = chi_so_kenh(vids, ns.subs, as_of, _ngay(ns.ngay_lap) if ns.ngay_lap else None,
                        tong_video=_uu_tien(ns.tong_video, ma, "tong_video"),
                        ngay_video_dau=_ngay(dau) if dau else None,
                        sub_30_ngay_truoc=ns.sub_30_ngay_truoc,
                        dong_bo=tk["bo_thieu_view_ngay"] + tk["bo_trung_id"], cua_so_tu=cua_so,
                        ty_trong_view_short=ns.ty_trong_view_short,
                        so_hoi_vien=_uu_tien(ns.so_hoi_vien, ma, "so_hoi_vien") or 0)
        hs = he_so_vuot_troi(vids, as_of, cua_so)
        md = [f"# Đo kênh: {Path(ns.file).name} (tính đến {as_of}, công thức {PHIEN_BAN})", "",
              f"Đọc {tk['tong_dong']} dòng; bỏ {tk['bo_thieu_view_ngay']} dòng thiếu view/ngày; "
              f"bỏ {tk['bo_trung_id']} dòng trùng id.", "",
              "## Chỉ số kênh", _bang_md([{"chi_so": k, "gia_tri": v} for k, v in m.items() if k != "co"],
                                        ["chi_so", "gia_tri"]),
              "", f"**Cờ:** {', '.join(m['co']) or 'không'}", "",
              "## Hệ số vượt trội (video dài, xếp theo ngày đăng)",
              _bang_md(hs, ["ngay", "tuoi_ngay", "id", "views", "n_truoc", "trung_vi_15_truoc", "he_so",
                            "n_sau", "he_so_sau", "muc", "ly_do_khong_tinh", "cung_ngay", "title"])]
        du_lieu_json = {"chi_so": m, "he_so": hs, "doc_file": tk}
    else:
        try:
            ghi_de = phan_tich_ghi_de(ns.ghi_de)
        except ValueError as e:
            raise SystemExit(str(e)) from None
        rows = _doc_bang(Path(ns.bang).read_text(encoding="utf-8-sig"))
        kenh = {}
        for r in rows:
            tk = {}
            vids = doc_video(Path(ns.bang).parent / r["file"], tk)
            try:
                ty_short = ty_le(r["ty_trong_view_short"]) if _o(r, "ty_trong_view_short") else None
            except argparse.ArgumentTypeError as e:
                raise SystemExit(f"{r['kenh']}: {e}") from None
            ma = doc_meta(Path(ns.bang).parent / _o(r, "meta")) if _o(r, "meta") else {}
            cs, dau = _uu_tien(_o(r, "cua_so_tu"), ma, "cua_so_tu"), _uu_tien(_o(r, "ngay_video_dau"), ma, "ngay_video_dau")
            kenh[r["kenh"]] = chi_so_kenh(
                vids, so(r.get("subs")), as_of, _ngay(r["ngay_lap"]) if _o(r, "ngay_lap") else None,
                tong_video=_uu_tien(so(r.get("tong_video")), ma, "tong_video"),
                ngay_video_dau=_ngay(dau) if dau else None,
                sub_30_ngay_truoc=so(r.get("sub_30_ngay_truoc")),
                dong_bo=tk["bo_thieu_view_ngay"] + tk["bo_trung_id"],
                cua_so_tu=_ngay(cs) if cs else None,
                ty_trong_view_short=ty_short, so_hoi_vien=_uu_tien(so(r.get("so_hoi_vien")), ma, "so_hoi_vien") or 0)
        da_ghi_de = []
        for ten, co, ly_do in ghi_de:
            k = _tim_kenh(kenh, ten)
            ap_dung_ghi_de(kenh[k], co, ly_do)
            da_ghi_de.append((k, co, ly_do))
        bang = xep_hang(kenh)
        md = [f"# Xếp hạng hiệu suất {len(bang)} kênh (tính đến {as_of}, công thức {PHIEN_BAN})", "",
              "Hạng = bộ tiêu chí tổng; khoảng hạng = min–max của 3 bộ (tổng, tích luỹ, đà). "
              "Kênh 'Không đủ chỉ số' không được xếp (không phải hạng cuối).", "",
              _bang_md(bang, ["hang", "kenh", "diem", "n_tieu_chi", "khoang_hang", "hang_tich_luy", "hang_da",
                              "hang_theo_ngay_lap", "it_video_sub_nhieu", "n_video", "subs", "sub_moi_video",
                              "trung_vi_20_dai", "trung_vi_chia_sub", "pct_tang_sub_30", "da_trung_vi",
                              "ty_le_tren_2x", "phan_tan", "sub_moi_ngay_video_dau", "n_dai_dung_tinh", "co"])]
        du_lieu_json = {"xep_hang": bang, "chi_so": kenh}
        if da_ghi_de:
            md += ["", "## Ghi đè bằng tay"] + [f"- {k}: {c}" + (f" — {ld}" if ld else "") for k, c, ld in da_ghi_de]
        if ns.do_nhay:
            dn = do_nhay(kenh)
            du_lieu_json["do_nhay"] = dn
            n = dn["so_cach"]
            md += ["", f"## Độ nhạy: {n} cách tính ({dn['so_cach_hop_le']} hợp lệ: xếp được ≥ {SO_CACH_TOI_THIEU} kênh)",
                   _bang_md([{"cach": b["ten"], "n_kenh": b["n_kenh"], "n_xep": b["n_xep"],
                              "hang_1": ", ".join(b["hang_1"]) if b["hop_le"] and b["hang_1"] else "–"}
                             for b in dn["bien_the"]], ["cach", "n_kenh", "n_xep", "hang_1"]), ""]
            mh = dn["so_cach_hop_le"]
            md += [f"- {k}: hạng 1 ở {c}/{mh} cách" + (" (vững)" if k in dn["hang_1_vung"] else "")
                   for k, c in dn["hang_1_o"].items()]
            if mh < SO_CACH_HOP_LE_TOI_THIEU_DE_VUNG:
                md.append(f"- Chỉ {mh} cách hợp lệ (< {SO_CACH_HOP_LE_TOI_THIEU_DE_VUNG}): chưa đủ cách tính để kết luận "
                          "hạng 1 vững; trình ≥ 2 ứng viên cho Model Link.")
            elif not dn["hang_1_vung"]:
                md.append(f"- Không kênh nào hạng 1 ở ≥ 5/6 số cách hợp lệ ({mh}): trình ≥ 2 ứng viên cho Model Link.")
    if ns.json:
        Path(ns.json).parent.mkdir(parents=True, exist_ok=True)
        Path(ns.json).write_text(json.dumps(du_lieu_json, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    out = "\n".join(md) + "\n"
    if ns.out:
        Path(ns.out).parent.mkdir(parents=True, exist_ok=True)
        Path(ns.out).write_text(out, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
