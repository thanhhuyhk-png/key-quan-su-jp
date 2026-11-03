"""Xuất hồ sơ "Tư duy Top 20" (JSON) thành bảng tính 12 tab theo mẫu bảng Top 20,
để tải lên Google Drive và chuyển thành Google Sheet.

Dùng:
  python xuat_sheet.py <ho-so-top20.json> --out <top20.xlsx> [--nghiem]
    --nghiem: dừng (mã 2) nếu kiểm tự động thấy lỗi mức cao (thiếu id/nguồn, cờ lỗi đơn vị trong TOP…).
Sau đó tải lên Drive (công cụ Google Drive create_file, contentMimeType
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, base64Content) để Drive tự chuyển thành Google Sheet.
Cấu trúc JSON: references/mau-google-sheet.md. Nhận cả tên trường của do_kenh.py (n_video, n_dai, n_short,
tuoi_tu_video_dau, sub_moi_ngay_video_dau…).
`nhom` nhận danh sách mã (chuỗi cũ vẫn được); `kiem_tra_so` nhận chua_chin | so_bo | dat | nghi (chuỗi cũ theo tiền tố).
Tab 9 nhận cả kênh Giữ chưa xếp và kênh Theo dõi. Hồ sơ gộp tự động: gop_ho_so.py.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import do_kenh as dk  # noqa: E402
from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

TEN_TAB = [
    "0. Tổng quan & Model Link",
    "1. TOP 20",
    "2. TOP 20 + video top",
    "3. Thăng hạng 30 ngày",
    "4. Khảo sát kênh",
    "5. Kho video vượt trội",
    "6. Cặp đối chứng",
    "7. Nhân bản đề tài",
    "8. Bám sát Model Link",
    "9. Theo dõi định kỳ",
    "10. Chú ý & phản biện",
    "11. Từ điển cột",
]
DONG_TIEU_DE = 3
SO_TOP = 20

XANH = "FF6AA84F"       # tiêu đề cột (như mẫu)
XANH_NHAT = "FFD9EAD3"  # dòng nhóm kênh
CAM = "FFFCE5CD"        # TOP 1–10 (như mẫu)
VANG = "FFFFD966"       # Model Link
DO_NHAT = "FFF4CCCC"    # cờ / giáng hạng
XANH_LA = "FFB6D7A8"    # thăng hạng / hệ số mạnh đã kiểm
CAM_NHAT = "FFFFF2CC"   # hệ số mạnh nhưng chưa kiểm số thật
XAM = "FFEFEFEF"
VIEN = Border(*(Side(style="thin", color="FFBFBFBF"),) * 4)

NHOM = dk.NHOM_NHAN
BI_DANH = {  # tên trường do_kenh.py → tên trường hồ sơ
    "so_video": "n_video", "so_dai": "n_dai", "so_short": "n_short", "tuoi_kenh_ngay": "tuoi_tu_video_dau",
    "sub_moi_ngay": "sub_moi_ngay_video_dau", "subs_30_ngay_truoc": "sub_30_ngay_truoc",
}

# (tiêu đề, khoá, ý nghĩa, cách tính/nguồn, kiểu)
COT_TOP20 = [
    ("Hạng", "hang", "Thứ hạng theo điểm hiệu suất trong các kênh 'Giữ' (đồng điểm đồng hạng)", "do_kenh.py xep-hang trên tập Giữ", "int"),
    ("Model Link", "_model", "★ = kênh mẫu hình số 1 để bám sát", "pha 6, user duyệt", "text"),
    ("Tên kênh", "ten", "Tên kênh", "trang kênh", "text"),
    ("Link kênh", "link", "Đường dẫn kênh", "trang kênh", "link"),
    ("Nhóm", "nhom", "Mới < 12 tháng / Ổn định ≥ 2 năm / Cùng nguồn lực (một kênh có thể thuộc nhiều nhóm); 'Mới' tính từ ngày video đầu", "bước phân nhóm", "text"),
    ("Ngách", "ngach", "Ngách / nhóm chủ đề", "xem 10 video", "text"),
    ("Định dạng hình–giọng", "dinh_dang", "Hình (người que, 2D, photoreal, audio…) + giọng", "xem video", "text"),
    ("Tuổi khán giả (mẫu bình luận)", "tuoi_khan_gia", "Nhóm tuổi chủ đạo trong mẫu bình luận, KHÔNG phải toàn bộ người xem", "references/do-tuoi-khan-gia.md", "text"),
    ("Mức tin tuổi", "tuoi_muc_tin", "Cao / Vừa / Thấp / Chưa xác định", "references/do-tuoi-khan-gia.md", "text"),
    ("Sub mốc trước", "subs_30_ngay_truoc", "Số sub ở mốc đo trước (~30 ngày)", "tab 9 lần trước hoặc vidIQ tăng 30 ngày", "int"),
    ("Sub hiện tại", "subs", "Số sub ở ngày đo", "trang kênh / API", "int"),
    ("Tăng 30 ngày", "_tang_sub", "Sub hiện tại − sub mốc trước", "tính", "int"),
    ("% tăng 30 ngày", "_pct_tang_hien", "% tăng DÙNG ĐỂ XẾP HẠNG (đã chặn trần 100 % khi kênh < 90 ngày; 'bỏ…' khi nền < 5.000 sub hoặc kênh lai Shorts); 'mốc 0' khi sub trước = 0, 'chưa có mốc' khi chưa có sub trước", "tính", "pct"),
    ("% tăng thô (chưa chặn trần/sàn)", "_pct_tang_tho", "Tăng 30 ngày ÷ sub mốc trước, chưa qua trần/sàn; chỉ để đối chiếu", "tính", "pct"),
    ("Số video", "so_video", "Tổng video công khai của kênh (không phải số lấy được)", "trang kênh / API", "int"),
    ("Video dài / Short", "_dai_short", "Số video dài / Shorts trong danh sách đã lấy", "do_kenh.py", "text"),
    ("Ngày video đầu", "ngay_video_dau", "Ngày đăng video đầu tiên còn công khai", "danh sách đủ / API", "text"),
    ("Tuổi kênh (ngày)", "tuoi_kenh_ngay", "Số ngày từ video đầu đến ngày đo", "tính", "int"),
    ("Sub/video", "sub_moi_video", "Sub ÷ tổng video (bỏ trống nếu sub lẫn Shorts)", "tính", "int"),
    ("Sub/ngày", "sub_moi_ngay", "Sub ÷ tuổi kênh (từ video đầu)", "tính", "int"),
    ("Trung vị view 20 video dài", "trung_vi_20_dai", "Trung vị view 20 video dài gần nhất đã đủ 30 ngày tuổi (lọc tuổi, chưa chuẩn hoá tuổi)", "do_kenh.py", "int"),
    ("N video đủ tính", "n_dai_dung_tinh", "Số video dùng để tính trung vị (< 10 = mẫu nhỏ)", "do_kenh.py", "int"),
    ("Trung vị ÷ sub", "trung_vi_chia_sub", ">50 % = được đề xuất cho người chưa đăng ký; <5 % = kênh yếu", "tiêu chí kênh", "pct"),
    ("Đà trung vị (10 mới ÷ 10 trước)", "da_trung_vi", ">1 = đang lên; <1 = đang xuống", "do_kenh.py", "float"),
    ("Video > 2× trung vị (/20)", "so_video_tren_2x", "Thông tin, không cộng điểm: nhiều video đột biến ≠ lặp lại được", "tiêu chí kênh", "int"),
    ("Phân tán (cao nhất ÷ trung vị)", "phan_tan", ">20 = phụ thuộc vài video đột biến", "tiêu chí kênh", "float"),
    ("Điểm hiệu suất", "diem", "Trung bình phân vị các tiêu chí có giá trị (0–100), tính trên tập Giữ", "references/tieu-chi-va-cong-thuc.md", "float"),
    ("Khoảng hạng 3 cách", "khoang_hang", "Hạng thấp–cao theo bộ tổng / tích luỹ / đà: hẹp = hạng vững", "do_kenh.py", "text"),
    ("Hạng 30 ngày trước", "hang_30_ngay_truoc", "Hạng ở lần đo trước (trống nếu chưa có lần đo)", "tab 9 lần trước", "int"),
    ("Thăng/giáng", "_delta_hang", "Hạng 30 ngày trước − hạng nay (dương = thăng)", "tính", "int"),
    ("Cờ dữ liệu", "co", "Cờ bẫy số liệu cần kiểm", "references/bay-so-lieu.md", "text"),
    ("Học gì", "hoc_gi", "Điều chép được, có bằng chứng", "học trọn", "text"),
    ("Không học", "khong_hoc_gi", "Điều không chép (khác tuổi, khác nguồn lực, rủi ro)", "học trọn", "text"),
    ("Chú ý", "chu_y", "Ghi chú như cột Chú ý của mẫu", "người phân tích", "text"),
    ("Nguồn số & ngày đo", "nguon_so", "Công cụ lấy số + ngày", "bắt buộc", "text"),
]
COT_KHAO_SAT = COT_TOP20[:2] + [("Giữ/Loại", "giu_loai", "Giữ / Loại / Theo dõi / Chưa lọc", "pha 3", "text"),
                                ("Lý do giữ/loại", "ly_do", "Lý do cụ thể, có số", "pha 3", "text")] + COT_TOP20[2:]
COT_VIDEO = [
    ("Kênh / STT", "_stt", "Dòng xanh nhạt = tiêu đề nhóm kênh; dòng dưới = STT video", "", "text"),
    ("Link video", "link", "Đường dẫn video", "API", "link"),
    ("Tiêu đề", "tieu_de", "Chép nguyên văn", "API", "text"),
    ("Ngày đăng", "ngay_dang", "Ngày đăng", "API", "text"),
    ("Thời lượng (phút)", "_phut", "Thời lượng", "API", "float"),
    ("View", "views", "Lượt xem ở ngày đo", "API (kiểm lỗi đơn vị)", "int"),
    ("View/ngày tuổi", "view_moi_ngay", "View ÷ số ngày từ khi đăng", "tính", "int"),
    ("Trung vị 15 video trước", "trung_vi_15_truoc", "Trung vị view 15 video dài đăng ngay trước", "do_kenh.py", "int"),
    ("Hệ số vượt trội", "he_so", "View ÷ trung vị 15 video trước", "bước hệ số vượt trội", "float"),
    ("Hệ số 5 video sau", "he_so_sau", "Trung vị đúng 5 video sau ÷ trung vị trước (giữ mức mới?)", "bước hệ số vượt trội", "float"),
    ("Mức", "muc", "<2 bình thường · 2–3 hơi cao · 3–5 đáng ghi · 5–10 mạnh · ≥10 kiểm kỹ · chưa chín (<30 ngày)", "do_kenh.py", "text"),
    ("Đề tài / premise", "de_tai", "Cụ thể, một cụm", "xem video", "text"),
    ("Góc tiếp cận", "goc_tiep_can", "Video trả lời câu hỏi nào", "xem video", "text"),
    ("Tử huyệt / nhu cầu", "tu_huyet", "Người xem muốn biết/cảm gì", "bình luận", "text"),
    ("Kiểu mở 30 giây", "kieu_mo", "1–2 câu đầu + nhãn kiểu mở + giây nêu lời hứa", "xem video", "text"),
    ("Ảnh bìa", "anh_bia", "Có người/chữ gì/màu chính/vật nổi bật ([CHƯA CÓ] nếu chưa mở ảnh)", "xem ảnh", "text"),
    ("Đỉnh phát lại", "dinh_phat_lai", "Mốc · % thời lượng của đỉnh 'Được phát lại nhiều nhất'", "heatmap.py", "text"),
    ("Yêu cầu trong bình luận", "yeu_cau_binh_luan", "Yêu cầu kèm số lần, ví dụ 'phần 2 (14)'", "bình luận", "text"),
    ("Kiểm tra số thật", "kiem_tra_so", "chua_chin (chưa chín) · so_bo (sơ bộ, chưa đọc bình luận) · dat (đã đọc bình luận và đối chiếu) · nghi (nghi ngờ, lý do ở Ghi chú)", "bước kiểm số thật", "text"),
    ("Ghi chú", "ghi_chu", "", "", "text"),
]
COT_THANG_HANG = [
    ("Hạng nay", "hang", "", "", "int"), ("Hạng 30 ngày trước", "hang_30_ngay_truoc", "", "", "int"),
    ("Thăng/giáng", "_delta_hang", "", "", "int"), ("Tên kênh", "ten", "", "", "text"),
    ("Link kênh", "link", "", "", "link"), ("Sub 30 ngày trước", "subs_30_ngay_truoc", "", "", "int"),
    ("Sub hiện tại", "subs", "", "", "int"), ("Sub tăng 30 ngày", "_tang_sub", "", "", "int"),
    ("% tăng", "_pct_tang_hien", "% tăng dùng để xếp hạng (đã qua trần/sàn); 'mốc 0' khi sub trước = 0; 'chưa có mốc' khi chưa có sub trước", "tính", "pct"),
    ("% tăng thô (chưa chặn trần/sàn)", "_pct_tang_tho", "Tăng 30 ngày ÷ sub mốc trước, chưa qua trần/sàn; chỉ để đối chiếu", "tính", "pct"),
    ("View 30 ngày", "view_30_ngay", "Lượt xem tăng trong 30 ngày; không có nguồn tự động, điền từ vidIQ channel_stats (trống nếu chưa có)", "vidIQ / lần đo trước", "int"),
    ("Video đăng 30 ngày", "video_30_ngay", "Số video mới trong 30 ngày", "danh sách video", "int"),
    ("Sub mới / video mới", "_sub_moi_video_moi", "Sub tăng 30 ngày ÷ video đăng 30 ngày", "tính", "int"),
    ("Trạng thái TOP 20", "_trang_thai", "Vào TOP mới / Rời TOP / Giữ TOP / Chưa có mốc trước", "tính", "text"),
    ("Nhận xét", "nhan_xet_thang_hang", "Vì sao lên/xuống (video nào kéo)", "người phân tích", "text"),
]
COT_DOI_CHUNG = [("Kênh", "kenh", "", "", "text"), ("Nhóm video vượt trội", "video_hit", "≥ 5 video nếu có", "", "text"),
                 ("Nhóm video thường (cùng giai đoạn)", "video_thuong", "≥ 5 video nếu có", "", "text"),
                 ("Khác chủ đề con?", "khac_chu_de", "", "", "text"), ("Khác tiêu đề?", "khac_tieu_de", "", "", "text"),
                 ("Khác ảnh bìa?", "khac_anh_bia", "", "", "text"), ("Khác mở 30 giây?", "khac_mo", "", "", "text"),
                 ("Khác góc kể?", "khac_goc", "", "", "text"), ("Khác độ dài / mốc đăng?", "khac_do_dai", "", "", "text"),
                 ("Giả thuyết nguyên nhân", "ket_luan", "Giả thuyết, KHÔNG phải nhân quả; thử trên kênh mình trước khi chép", "bước đối chứng", "text")]
DIEM_CO_HOI = [("Nhu cầu", "nhu_cau"), ("Bằng chứng nhiều kênh", "bang_chung"), ("Khoảng trống", "khoang_trong"),
               ("Hợp khán giả mục tiêu", "hop_khan_gia"), ("Chi phí làm được", "chi_phi"), ("Rủi ro thấp", "rui_ro")]
COT_NHAN_BAN = [("Video gốc", "video_goc", "", "", "text"), ("Nhu cầu đã chứng minh", "nhu_cau", "", "", "text"),
                ("Đổi nhân vật/sự kiện", "doi_nhan_vat", "", "", "text"), ("Đổi bối cảnh", "doi_boi_canh", "", "", "text"),
                ("Góc nhìn", "goc_nhin", "", "", "text"), ("Câu hỏi trung tâm", "cau_hoi_trung_tam", "", "", "text"),
                ("Nhu cầu gốc còn?", "con_nhu_cau", "", "", "text"), ("Đủ tư liệu?", "du_tu_lieu", "", "", "text"),
                ("Khác rõ bản gốc?", "khac_ro", "", "", "text")] + \
               [(f"Điểm: {t} (1–5)", f"_d_{k}", "", "bước điểm cơ hội", "int") for t, k in DIEM_CO_HOI] + \
               [("Tổng điểm cơ hội (/30)", "_tong_diem", "Tổng 6 mục; trống nếu có mục thiếu/ngoài 1–5", "bước điểm cơ hội", "int"),
                ("Kết luận điểm", "_ket_luan_diem", "> 22 thử ngay · 16–22 theo dõi · < 16 bỏ", "bước điểm cơ hội", "text"),
                ("Quyết định", "quyet_dinh", "", "user", "text")]
COT_THEO_DOI = [("Ngày", "ngay", "", "", "text"), ("Id kênh", "id_kenh", "Id ổn định để nối các kỳ", "", "text"),
                ("Kênh", "kenh", "", "", "text"), ("Hạng", "hang", "", "", "int"), ("Điểm", "diem", "", "", "float"),
                ("Sub", "subs", "", "", "int"), ("Tổng view", "view_tong", "", "", "int"),
                ("Số video", "so_video", "", "", "int"), ("Sub/video", "sub_moi_video", "", "", "int"),
                ("Trung vị 20 video dài", "trung_vi_20_dai", "", "", "int"),
                ("Trung vị ÷ sub", "trung_vi_chia_sub", "", "", "pct"),
                ("Phiên bản công thức", "phien_ban", "So hai kỳ chỉ khi cùng phiên bản", "do_kenh.PHIEN_BAN", "text"),
                ("Ghi chú", "ghi_chu", "", "", "text")]
COT_CHU_Y = [("Loại", "loai", "co_du_lieu / gioi_han / cau_hoi / phan_bien / kiem_tu_dong", "", "text"),
             ("Nội dung", "noi_dung", "", "", "text"), ("Mức độ", "muc_do", "cao / vừa / thấp", "", "text"),
             ("Việc cần làm", "viec_can_lam", "", "", "text")]


# ---------- chuẩn hoá đầu vào ----------

def _nfc(s) -> str:
    return unicodedata.normalize("NFC", str(s or "")).strip()


def _giu_loai(s) -> str:
    t = _nfc(s).casefold()
    return {"giữ": "Giữ", "loại": "Loại", "theo dõi": "Theo dõi"}.get(t, "Chưa lọc" if not t else _nfc(s))


def _so_thuc(x) -> float | None:
    if x is None or isinstance(x, bool):
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _tuoi_tu_video_dau(r: dict, ngay_do: date | None) -> int | None:
    dau = dk.doc_ngay(r.get("ngay_video_dau"))
    if dau is not None and ngay_do is not None:
        return (ngay_do - dau.date()).days
    t = _so_thuc(r.get("tuoi_kenh_ngay"))
    return int(t) if t is not None else None


def _chuan_kenh(k: dict, ngay_do: date | None = None) -> dict:
    r = dict(k)
    for dich, nguon in BI_DANH.items():
        if r.get(dich) is None and r.get(nguon) is not None:
            r[dich] = r[nguon]
    tuoi = _tuoi_tu_video_dau(r, ngay_do)
    tay = dk.chuan_nhom(r.get("nhom"))
    r["nhom_ds"] = dk.chuan_nhom(tay, tuoi)             # cờ 'moi' tính từ ngày video đầu, không tin nhãn tay
    r["_nhom_moi_lech"] = tuoi is not None and ("moi" in tay) != ("moi" in r["nhom_ds"])
    r["giu_loai"] = _giu_loai(r.get("giu_loai"))
    if isinstance(r.get("co"), (list, tuple)):
        r["co"] = ", ".join(map(str, r["co"]))
    h0 = r.get("hang_30_ngay_truoc")
    r["hang_30_ngay_truoc"] = int(h0) if isinstance(h0, (int, float)) and not isinstance(h0, bool) and h0 > 0 else None
    return r


def _xep_hang(kenh: list[dict]) -> None:
    """Hạng luôn tính lại từ điểm trong tập 'Giữ' (hạng cạnh tranh trên điểm làm tròn 1 chữ số)."""
    giu = [k for k in kenh if k["giu_loai"] == "Giữ" and _so_thuc(k.get("diem")) is not None]
    diem = {id(k): round(_so_thuc(k["diem"]), 1) for k in giu}
    for k in kenh:
        k["hang_dau_vao"] = k.get("hang")
        k["hang"] = (1 + sum(1 for v in diem.values() if v > diem[id(k)])) if id(k) in diem else None


def _moi_that(k: dict) -> bool:
    """Kênh 'mới' thật: nhóm mới và không phải kênh tái sinh (sub của kênh tái sinh có thể là lịch sử)."""
    return "moi" in k["nhom_ds"] and "TAI_SINH" not in str(k.get("co") or "")


def kiem_ho_so(hs: dict, kenh: list[dict], top: list[dict]) -> list[dict]:
    """Kiểm tự động trước khi xuất; trả mục cho tab 'Chú ý & phản biện'."""
    loi = []

    def them(noi_dung, muc="cao", viec=""):
        loi.append({"loai": "kiem_tu_dong", "noi_dung": noi_dung, "muc_do": muc, "viec_can_lam": viec})

    ids = [k.get("id") for k in kenh]
    if any(not i for i in ids):
        them(f"{sum(1 for i in ids if not i)} kênh thiếu id", viec="điền id kênh (UC…)")
    if len(set(i for i in ids if i)) < len([i for i in ids if i]):
        them("Có id kênh trùng", viec="gộp hoặc xoá dòng trùng")
    for k in top:
        if not k.get("nguon_so"):
            them(f"{k.get('ten')}: thiếu 'Nguồn số & ngày đo'", "vừa", "ghi công cụ + ngày")
        if "NGHI_LOI_DON_VI" in str(k.get("co") or ""):
            them(f"{k.get('ten')}: cờ NGHI_LOI_DON_VI trong TOP", viec="lấy lại số từ metadata đầy đủ")
        if not any(v.get("kenh") == k.get("id") and v.get("la_top_view") for v in hs.get("video", [])):
            them(f"{k.get('ten')}: chưa có video top", "vừa", "thu 5–10 video nhiều view nhất")
    if any(k["giu_loai"] == "Giữ" and _moi_that(k) for k in kenh) and not any(_moi_that(k) for k in top):
        them("Có kênh nhóm 'mới < 12 tháng' được giữ nhưng không vào TOP 20 — kiểm lại câu bắt buộc luật thép 3", "vừa")
    chua_loc = [k.get("ten") for k in kenh if k["giu_loai"] == "Chưa lọc"]
    if chua_loc:
        them(f"{len(chua_loc)} kênh chưa gắn Giữ/Loại", "vừa", "lọc ở pha 3")
    khong_diem = [k.get("ten") for k in kenh if k["giu_loai"] == "Giữ" and _so_thuc(k.get("diem")) is None]
    if khong_diem:
        them(f"{len(khong_diem)} kênh 'Giữ' không đủ chỉ số để xếp: {', '.join(map(str, khong_diem[:5]))}", "vừa")
    lech = [k.get("ten") for k in kenh if isinstance(k.get("hang_dau_vao"), int) and k["hang_dau_vao"] != k.get("hang")]
    if lech:
        them(f"Hạng trong hồ sơ khác hạng tính lại ở {len(lech)} kênh (đã dùng hạng tính lại)", "thấp")
    for k in kenh:
        if k.get("_nhom_moi_lech"):
            them(f"{k.get('ten')}: nhóm 'mới' ghi tay không khớp ngày video đầu; đã tính lại từ ngày video đầu",
                 "thấp")
        if "TAI_SINH" in str(k.get("co") or "") and "moi" in k.get("nhom_ds", []):
            them(f"{k.get('ten')}: cờ TAI_SINH nhưng vẫn ở nhóm 'mới' (video đầu < 12 tháng, ngày lập xa hơn 12 tháng): "
                 "sub có thể là lịch sử của kênh cũ", "vừa", "ghi rõ trong Chú ý; không dùng % tăng sub làm bằng chứng")
    ml = (hs.get("model_link") or {}).get("kenh")
    if not ml:
        them("Chưa chọn Model Link", "vừa")
    elif ml not in {k.get("id") for k in top}:
        them("Model Link không nằm trong TOP 20", viec="giải thích hoặc chọn lại")
    if len(top) < SO_TOP:
        them(f"TOP chỉ có {len(top)} kênh đáng tin (< 20) — giữ nguyên, không độn kênh yếu", "vừa")
    return loi


# ---------- tính cột dẫn xuất ----------

def _dan_xuat(k: dict, top_ids: set, top_truoc_ids: set, co_moc_truoc: bool, model_id: str | None) -> dict:
    r = dict(k)
    s, s0 = _so_thuc(k.get("subs")), _so_thuc(k.get("subs_30_ngay_truoc"))
    r["_tang_sub"] = int(s - s0) if s is not None and s0 is not None else None
    tho = (s - s0) / s0 if s is not None and s0 else None
    r["_pct_tang_tho"] = tho
    # hồ sơ do do_kenh.py gộp có pct_tang_sub_30 (đã qua trần 100 % và sàn nền); hồ sơ cũ không có thì dùng bản tính lại
    r["_pct_tang"] = _so_thuc(k.get("pct_tang_sub_30")) if "pct_tang_sub_30" in k else tho
    if r["_pct_tang"] is not None:
        r["_pct_tang_hien"] = r["_pct_tang"]
    elif s is not None and s0 == 0:
        r["_pct_tang_hien"] = "mốc 0 (sub trước = 0)"
    elif tho is not None:
        r["_pct_tang_hien"] = "bỏ khỏi xếp hạng (nền < 5.000 sub hoặc kênh lai Shorts)"
    else:
        r["_pct_tang_hien"] = "chưa có mốc"
    h, h0 = k.get("hang"), k.get("hang_30_ngay_truoc")
    r["_delta_hang"] = h0 - h if h is not None and h0 is not None else None
    dai, short = k.get("so_dai"), k.get("so_short")
    r["_dai_short"] = f"{dai if dai is not None else '?'} / {short if short is not None else '?'}" \
        if dai is not None or short is not None else None
    r["_model"] = "★ MODEL LINK" if model_id and k.get("id") == model_id else None
    v30 = _so_thuc(k.get("video_30_ngay"))
    r["_sub_moi_video_moi"] = round(r["_tang_sub"] / v30) if r["_tang_sub"] is not None and v30 else None
    trong, truoc = k.get("id") in top_ids, k.get("id") in top_truoc_ids
    if not co_moc_truoc:
        r["_trang_thai"] = "Chưa có mốc trước" if trong else "Ngoài TOP"
    else:
        r["_trang_thai"] = ("Vào TOP mới" if trong and not truoc else "Rời TOP" if truoc and not trong
                            else "Giữ TOP" if trong else "Ngoài TOP")
    r["nhom"] = " · ".join(NHOM.get(c, c) for c in k.get("nhom_ds", []))
    return r


# ---------- ghi ô ----------

def _gan(o, v):
    """Ghi giá trị an toàn: chuỗi bắt đầu = + - @ không thành công thức; bỏ ký tự điều khiển."""
    if isinstance(v, (list, tuple)):
        v = ", ".join(map(str, v))
    elif isinstance(v, dict):
        v = json.dumps(v, ensure_ascii=False)
    if isinstance(v, str):
        v = ILLEGAL_CHARACTERS_RE.sub("", v)
    o.value = v
    if isinstance(v, str) and v[:1] in ("=", "+", "-", "@"):
        o.data_type = "s"
    return o


def _khoa_pct_tang(r: dict) -> tuple:
    """Xếp theo % tăng giảm dần; kênh 'mốc 0' sau kênh có %, kênh 'chưa có mốc' cuối cùng."""
    p = r.get("_pct_tang")
    if p is not None:
        return (0, -p)
    return (1, 0) if str(r.get("_pct_tang_hien")).startswith(("mốc 0", "bỏ")) else (2, 0)


def _tieu_de(ws, tieu_de: str, phu: str, cot: list):
    _gan(ws.cell(1, 1), tieu_de).font = Font(bold=True, size=14)
    _gan(ws.cell(2, 1), phu).font = Font(italic=True, color="FF666666")
    for j, c in enumerate(cot, 1):
        o = _gan(ws.cell(DONG_TIEU_DE, j), c[0])
        o.font = Font(bold=True, color="FFFFFFFF")
        o.fill = PatternFill("solid", fgColor=XANH)
        o.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        o.border = VIEN
    ws.freeze_panes = ws.cell(DONG_TIEU_DE + 1, 3)
    ws.row_dimensions[DONG_TIEU_DE].height = 48


def _link_hop_le(v) -> bool:
    return isinstance(v, str) and re.match(r"https?://", v.strip()) is not None


def _ghi_dong(ws, i: int, cot: list, r: dict, to: str | None = None):
    for j, (_, khoa, _, _, kieu) in enumerate(cot, 1):
        v = r.get(khoa)
        o = _gan(ws.cell(i, j), v)
        o.border = VIEN
        o.alignment = Alignment(wrap_text=kieu == "text", vertical="top")
        if kieu == "int" and isinstance(v, (int, float)) and not isinstance(v, bool):
            o.number_format = "#,##0"
        elif kieu == "float" and isinstance(v, (int, float)):
            o.number_format = "#,##0.0"
        elif kieu == "pct" and isinstance(v, (int, float)):
            o.number_format = "0.0%"
        elif kieu == "link" and _link_hop_le(v):
            o.hyperlink = v.strip()
            o.font = Font(color="FF1155CC", underline="single")
        if to:
            o.fill = PatternFill("solid", fgColor=to)


RONG_CHU = {"hoc_gi", "khong_hoc_gi", "chu_y", "ly_do", "tieu_de", "noi_dung", "ket_luan", "kieu_mo",
            "nhan_xet_thang_hang", "y_nghia", "viec_can_lam", "de_tai", "goc_tiep_can", "tu_huyet", "anh_bia"}


def _rong_cot(ws, cot: list):
    for j, c in enumerate(cot, 1):
        ws.column_dimensions[get_column_letter(j)].width = \
            34 if c[1] in RONG_CHU else 28 if c[4] == "link" else 22 if c[4] == "text" else 13


def _bang(ws, tieu_de, phu, cot, rows, to_fn=None):
    _tieu_de(ws, tieu_de, phu, cot)
    for i, r in enumerate(rows, DONG_TIEU_DE + 1):
        _ghi_dong(ws, i, cot, r, to_fn(r) if to_fn else None)
    _rong_cot(ws, cot)
    if rows:
        ws.auto_filter.ref = f"A{DONG_TIEU_DE}:{get_column_letter(len(cot))}{DONG_TIEU_DE + len(rows)}"


def _fmt(v, kieu="") -> str:
    if v is None:
        return "–"
    if kieu == "pct" and isinstance(v, (int, float)):
        return f"{v:.1%}"
    if isinstance(v, bool):
        return "Có" if v else "Không"
    if isinstance(v, int):
        return f"{v:,}"
    if isinstance(v, float):
        return f"{v:,.1f}"
    return str(v)


def _kv(ws, dong: int, khoa: str, gia_tri, dam=False) -> int:
    _gan(ws.cell(dong, 1), khoa).font = Font(bold=True)
    gt = "\n".join(f"• {x}" for x in gia_tri) if isinstance(gia_tri, list) else gia_tri
    o = _gan(ws.cell(dong, 2), gt)
    o.alignment = Alignment(wrap_text=True, vertical="top")
    if dam:
        o.font = Font(bold=True)
    return dong + 1


# ---------- dựng sổ ----------

def xuat(path_json: Path, out: Path) -> tuple[Path, list[dict]]:
    hs = json.loads(Path(path_json).read_text(encoding="utf-8-sig"))
    ngay = hs.get("ngay_do", date.today().isoformat())
    ngay0 = hs.get("ngay_moc_truoc") or ""
    ml = hs.get("model_link") or {}
    model_id = ml.get("kenh")
    d_do = dk.doc_ngay(ngay)
    kenh_all = [_chuan_kenh(k, d_do.date() if d_do else None) for k in hs.get("kenh", [])]
    _xep_hang(kenh_all)
    giu = sorted([k for k in kenh_all if k["hang"] is not None], key=lambda k: (k["hang"], _nfc(k.get("ten"))))
    top = [k for k in giu if k["hang"] <= SO_TOP][:SO_TOP]
    top_ids = {k.get("id") for k in top}
    top_truoc_ids = {k.get("id") for k in kenh_all if (k.get("hang_30_ngay_truoc") or 99) <= SO_TOP}
    co_moc_truoc = bool(top_truoc_ids)
    dx = {k.get("id"): _dan_xuat(k, top_ids, top_truoc_ids, co_moc_truoc, model_id) for k in kenh_all}
    ten_kenh = {k.get("id"): k.get("ten") for k in kenh_all}
    kiem = kiem_ho_so(hs, kenh_all, top)
    chu_y = kiem + list(hs.get("chu_y", []))

    wb = Workbook()
    wb.remove(wb.active)
    ws = {t: wb.create_sheet(t) for t in TEN_TAB}

    # 1. TOP 20
    def to_top(r):
        return VANG if r.get("_model") else CAM if (r.get("hang") or 99) <= 10 else None
    _bang(ws[TEN_TAB[1]], f"TOP {len(top)} — {hs.get('du_an', '')}",
          f"Đo ngày {ngay}{' · mốc trước ' + ngay0 if ngay0 else ''} · hạng 1–10 tô cam, Model Link tô vàng · "
          f"nguồn từng dòng ở cột cuối · tuổi = mẫu bình luận", COT_TOP20, [dx[k.get("id")] for k in top], to_top)

    # 2. TOP 20 + video top
    w2 = ws[TEN_TAB[2]]
    _tieu_de(w2, "TOP 20 kèm video nhiều view nhất của từng kênh",
             "Mỗi kênh một dòng tiêu đề (bấm để mở kênh); video xếp theo view giảm dần; hệ số = view ÷ trung vị 15 "
             "video trước; xanh = hệ số ≥ 5 đã kiểm số thật, vàng nhạt = chưa kiểm", COT_VIDEO)
    dong = DONG_TIEU_DE + 1
    for k in top:
        la_ml = k.get("id") == model_id
        nhan = f"#{k['hang']} · {k.get('ten')} · {_fmt(k.get('subs'))} sub" + (" · ★ MODEL LINK" if la_ml else "")
        o = _gan(w2.cell(dong, 1), nhan)
        o.font = Font(bold=True, color="FF1155CC" if _link_hop_le(k.get("link")) else "FF000000")
        if _link_hop_le(k.get("link")):
            o.hyperlink = k["link"].strip()
        for j in range(1, len(COT_VIDEO) + 1):
            w2.cell(dong, j).fill = PatternFill("solid", fgColor=VANG if la_ml else XANH_NHAT)
            w2.cell(dong, j).border = VIEN
        w2.merge_cells(start_row=dong, start_column=1, end_row=dong, end_column=6)
        dong += 1
        vids = sorted([v for v in hs.get("video", []) if v.get("kenh") == k.get("id") and v.get("la_top_view")],
                      key=lambda v: -(_so_thuc(v.get("views")) or 0))
        if not vids:
            _gan(w2.cell(dong, 2), "CHƯA CÓ DỮ LIỆU VIDEO — thu thêm trước khi kết luận").font = Font(color="FFCC0000")
            dong += 1
        for stt, v in enumerate(vids, 1):
            tl = _so_thuc(v.get("thoi_luong_s"))
            r = dict(_nhan_kiem_so(v), _stt=stt, _phut=round(tl / 60, 1) if tl else None)
            _ghi_dong(w2, dong, COT_VIDEO, r, _to_video(v))
            dong += 1
    _rong_cot(w2, COT_VIDEO)

    # 3. Thăng hạng
    co_hang = [dx[k.get("id")] for k in kenh_all
               if k.get("hang") is not None or k.get("hang_30_ngay_truoc") is not None]
    if co_moc_truoc:
        co_hang.sort(key=lambda r: (r.get("_delta_hang") is None, -(r.get("_delta_hang") or 0)))
        phu3 = "Xếp theo mức thăng hạng; xanh = thăng, đỏ = giáng; 'Rời TOP' gồm cả kênh bị loại kỳ này"
    else:
        co_hang.sort(key=_khoa_pct_tang)
        phu3 = ("LẦN ĐO ĐẦU: chưa có hạng kỳ trước nên chưa có thăng/giáng; bảng xếp theo % tăng sub 30 ngày. "
                "'mốc 0' = kênh có sub trước bằng 0 (không tính được %), 'chưa có mốc' = chưa có sub kỳ trước. "
                "Lần đo sau lấy hạng từ tab 9.")

    def to_th(r):
        d = r.get("_delta_hang")
        return XANH_LA if d and d > 0 else DO_NHAT if (d and d < 0) or r.get("_trang_thai") == "Rời TOP" else None
    _bang(ws[TEN_TAB[3]], f"Báo cáo thăng hạng 30 ngày ({ngay0 or 'chưa có mốc'} → {ngay})", phu3,
          COT_THANG_HANG, co_hang, to_th)

    # 4. Khảo sát kênh
    ks = sorted((dx[k.get("id")] for k in kenh_all),
                key=lambda r: (r.get("hang") is None, r.get("hang") or 0, _nfc(r.get("ten"))))
    dem = {t: sum(1 for k in kenh_all if k["giu_loai"] == t) for t in ("Giữ", "Theo dõi", "Loại", "Chưa lọc")}
    _bang(ws[TEN_TAB[4]], f"Khảo sát {len(kenh_all)} kênh — giữ {dem['Giữ']} · theo dõi {dem['Theo dõi']} · "
          f"loại {dem['Loại']} · chưa lọc {dem['Chưa lọc']}",
          "Khảo sát rộng → đo → cổng lọc (hướng, khán giả, nguồn lực, ràng buộc) → xếp hạng trên tập Giữ; "
          "kênh loại tô xám", COT_KHAO_SAT, ks,
          lambda r: XAM if r.get("giu_loai") == "Loại" else VANG if r.get("_model") else None)
    dv = DataValidation(type="list", formula1='"Giữ,Loại,Theo dõi"', allow_blank=True)
    ws[TEN_TAB[4]].add_data_validation(dv)
    dv.add(f"C{DONG_TIEU_DE + 1}:C{DONG_TIEU_DE + max(1, len(ks))}")

    # 5. Kho video vượt trội
    vt = []
    for v in hs.get("video", []):
        if (_so_thuc(v.get("he_so")) or 0) >= 3:
            tl = _so_thuc(v.get("thoi_luong_s"))
            vt.append(dict(_nhan_kiem_so(v), _stt=ten_kenh.get(v.get("kenh"), v.get("kenh")),
                           _phut=round(tl / 60, 1) if tl else None))
    vt.sort(key=lambda v: -(_so_thuc(v.get("he_so")) or 0))
    _bang(ws[TEN_TAB[5]], f"Kho video vượt trội ({len(vt)} video, hệ số ≥ 3)",
          "Cột đầu = kênh; xếp theo hệ số; 'Kiểm tra số thật' bắt buộc trước khi dùng", COT_VIDEO, vt, _to_video)

    # 6. Cặp đối chứng
    _bang(ws[TEN_TAB[6]], "Đối chứng: nhóm video vượt trội vs nhóm video thường cùng kênh, cùng giai đoạn",
          "So trên cả chủ đề con, tiêu đề, ảnh bìa, mở 30 giây, góc kể, độ dài/mốc đăng; kết luận chỉ là giả thuyết",
          COT_DOI_CHUNG, [dict(d, kenh=ten_kenh.get(d.get("kenh"), d.get("kenh"))) for d in hs.get("doi_chung", [])])

    # 7. Nhân bản đề tài
    nb = []
    for n in hs.get("nhan_ban", []):
        r = dict(n)
        diem = n.get("diem") or {}
        vals = []
        for _, k in DIEM_CO_HOI:
            x = _so_thuc(diem.get(k))
            x = int(x) if x is not None and 1 <= x <= 5 and x == int(x) else None
            r[f"_d_{k}"] = x
            vals.append(x)
        tong = sum(vals) if all(x is not None for x in vals) else None
        r["_tong_diem"] = tong
        r["_ket_luan_diem"] = ("Thiếu/ngoài 1–5, chưa kết luận" if tong is None else "Thử ngay (> 22)" if tong > 22
                               else "Theo dõi (16–22)" if tong >= 16 else "Bỏ (< 16)")
        nb.append(r)
    _bang(ws[TEN_TAB[7]], "Nhân bản đề tài: giữ nhu cầu đã chứng minh, đổi phần còn lại",
          "Ba câu kiểm trước khi làm; câu 'Khác rõ bản gốc?' = không thì đổi thêm", COT_NHAN_BAN, nb,
          lambda r: XANH_LA if r["_tong_diem"] and r["_tong_diem"] > 22 else None)

    # 8. Bám sát Model Link
    w8 = ws[TEN_TAB[8]]
    mk = dx.get(model_id, {})
    _gan(w8.cell(1, 1), f"MODEL LINK: {mk.get('ten', '(chưa chọn)')}").font = Font(bold=True, size=14)
    w8.cell(1, 1).fill = PatternFill("solid", fgColor=VANG)
    d = 3
    d = _kv(w8, d, "Trạng thái", ml.get("trang_thai", "đề xuất, chờ user duyệt"), dam=True)
    d = _kv(w8, d, "Link", mk.get("link"))
    if _link_hop_le(mk.get("link")):
        w8.cell(d - 1, 2).hyperlink = mk["link"].strip()
    for nhan, khoa, kieu in [("Hạng / khoảng hạng 3 cách", "hang", ""), ("Điểm hiệu suất", "diem", ""),
                             ("Sub hiện tại", "subs", ""), ("Tăng 30 ngày", "_tang_sub", ""),
                             ("% tăng 30 ngày", "_pct_tang_hien", "pct"), ("Sub/video", "sub_moi_video", ""),
                             ("Trung vị view 20 video dài", "trung_vi_20_dai", ""),
                             ("Trung vị ÷ sub", "trung_vi_chia_sub", "pct"), ("Đà trung vị", "da_trung_vi", ""),
                             ("Định dạng", "dinh_dang", ""), ("Tuổi khán giả (mẫu bình luận)", "tuoi_khan_gia", ""),
                             ("Mức tin tuổi", "tuoi_muc_tin", "")]:
        gt = _fmt(mk.get(khoa), kieu)
        if khoa == "hang" and mk.get("khoang_hang"):
            gt = f"{gt} (khoảng {mk['khoang_hang']})"
        d = _kv(w8, d, nhan, gt)
    d = _kv(w8, d + 1, "Vì sao là TOP 1", ml.get("ly_do", []))
    d = _kv(w8, d, "Bám gì", ml.get("bam_gi", []))
    d = _kv(w8, d, "Không bám", ml.get("khong_bam", []))
    d = _kv(w8, d, "Theo dõi hằng tuần", ml.get("theo_doi_hang_tuan", []))
    d = _kv(w8, d, "Dừng bám khi", ml.get("dung_bam_khi", ["Sub/video hoặc trung vị view giảm 2 lần đo liên tiếp",
                                                          "Kênh đổi đề tài hoặc định dạng"]))
    w8.column_dimensions["A"].width = 30
    w8.column_dimensions["B"].width = 110

    # 9. Theo dõi định kỳ (dòng cũ trong hồ sơ + dòng kỳ này cho mọi kênh Giữ, kể cả kênh chưa xếp, và kênh Theo dõi)
    theo_doi = [dict(t, kenh=ten_kenh.get(t.get("kenh"), t.get("kenh")), id_kenh=t.get("id_kenh") or t.get("kenh"))
                for t in hs.get("theo_doi", [])]
    da_co = {(t.get("ngay"), t.get("id_kenh")) for t in theo_doi}
    dang_theo_doi = giu + [k for k in kenh_all if k["hang"] is None and k["giu_loai"] in ("Giữ", "Theo dõi")]
    for k in dang_theo_doi:
        if (ngay, k.get("id")) not in da_co:
            theo_doi.append({"ngay": ngay, "id_kenh": k.get("id"), "kenh": k.get("ten"), "hang": k.get("hang"),
                             "diem": _so_thuc(k.get("diem")), "subs": k.get("subs"), "view_tong": k.get("view_tong"),
                             "so_video": k.get("so_video"), "sub_moi_video": k.get("sub_moi_video"),
                             "trung_vi_20_dai": k.get("trung_vi_20_dai"),
                             "trung_vi_chia_sub": k.get("trung_vi_chia_sub"),
                             "phien_ban": k.get("phien_ban") or hs.get("phien_ban_cong_thuc")})
    _bang(ws[TEN_TAB[9]], "Theo dõi định kỳ — nguồn cho báo cáo thăng hạng kỳ sau",
          "Không sửa dòng cũ; mỗi kỳ một dòng mỗi kênh; chỉ so hai kỳ cùng phiên bản công thức", COT_THEO_DOI, theo_doi)

    # 10. Chú ý & phản biện
    _bang(ws[TEN_TAB[10]], "Những chú ý quan trọng & phản biện",
          "Dòng 'kiem_tu_dong' do script sinh; mục 'cao' phải xử lý trước khi dùng kết quả", COT_CHU_Y, chu_y,
          lambda r: DO_NHAT if _nfc(r.get("muc_do")).casefold() == "cao" else None)

    # 0. Tổng quan
    w0 = ws[TEN_TAB[0]]
    _gan(w0.cell(1, 1), f"TƯ DUY TOP 20 — {hs.get('du_an', '')}").font = Font(bold=True, size=16)
    mt = hs.get("muc_tieu") or {}
    d = 3
    d = _kv(w0, d, "Ngày đo / mốc trước", f"{ngay} / {ngay0 or 'chưa có (lần đo đầu)'}")
    d = _kv(w0, d, "Khán giả mục tiêu", mt.get("khan_gia"))
    d = _kv(w0, d, "Định dạng của mình", mt.get("dinh_dang"))
    d = _kv(w0, d, "Nguồn lực", mt.get("nguon_luc"))
    d = _kv(w0, d, "Ràng buộc", mt.get("rang_buoc", []))
    d = _kv(w0, d, "Khảo sát / giữ / TOP", f"{len(kenh_all)} kênh / {dem['Giữ']} giữ / {len(top)} vào TOP")
    d = _kv(w0, d, "MODEL LINK", f"{mk.get('ten', '(chưa chọn)')} — {ml.get('trang_thai', 'đề xuất')}", dam=True)
    w0.cell(d - 1, 2).fill = PatternFill("solid", fgColor=VANG)
    d = _kv(w0, d, "Vì sao", ml.get("ly_do", []))
    cao = [c.get("noi_dung") for c in chu_y if _nfc(c.get("muc_do")).casefold() == "cao"]
    d = _kv(w0, d, "Cảnh báo mức cao", cao or ["không"])
    if cao:
        w0.cell(d - 1, 2).fill = PatternFill("solid", fgColor=DO_NHAT)
    d = _kv(w0, d + 1, "Chú giải màu", ["Xanh đậm: tiêu đề cột", "Cam: hạng 1–10", "Vàng: Model Link",
                                       "Xanh lá: thăng hạng / hệ số ≥ 5 đã kiểm", "Vàng nhạt: hệ số ≥ 5 chưa kiểm",
                                       "Đỏ nhạt: giáng hạng / rời TOP / cảnh báo cao", "Xám: kênh bị loại"])
    d = _kv(w0, d, "Các tab", TEN_TAB[1:])
    w0.column_dimensions["A"].width = 26
    w0.column_dimensions["B"].width = 110

    # 11. Từ điển cột
    tu_dien = []
    for tab, cot in [(TEN_TAB[1], COT_TOP20), (TEN_TAB[2], COT_VIDEO), (TEN_TAB[3], COT_THANG_HANG),
                     (TEN_TAB[4], COT_KHAO_SAT[2:4]), (TEN_TAB[6], COT_DOI_CHUNG), (TEN_TAB[7], COT_NHAN_BAN),
                     (TEN_TAB[9], COT_THEO_DOI), (TEN_TAB[10], COT_CHU_Y)]:
        for c in cot:
            tu_dien.append({"tab": tab, "cot": c[0], "y_nghia": c[2], "cach_tinh": c[3]})
    _bang(ws[TEN_TAB[11]], "Từ điển cột", "Ý nghĩa và cách tính của từng cột",
          [("Tab", "tab", "", "", "text"), ("Cột", "cot", "", "", "text"),
           ("Ý nghĩa", "y_nghia", "", "", "text"), ("Cách tính / nguồn", "cach_tinh", "", "", "text")], tu_dien)
    ws[TEN_TAB[11]].column_dimensions["C"].width = 70
    ws[TEN_TAB[11]].column_dimensions["D"].width = 40

    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return out, kiem


def _to_video(v: dict) -> str | None:
    """Màu theo trạng thái kiểm tra số thật: nghi = đỏ (mọi hệ số); từ hệ số ≥ 5: đạt = xanh, chưa chín = xám,
    còn lại (sơ bộ, chưa kiểm, chuỗi cũ) = cam nhạt."""
    st = dk.trang_thai_kiem_so(v.get("kiem_tra_so"))
    if st == "nghi":
        return DO_NHAT
    if (_so_thuc(v.get("he_so")) or 0) < 5:
        return None
    return {"dat": XANH_LA, "chua_chin": XAM}.get(st, CAM_NHAT)


def _nhan_kiem_so(v: dict) -> dict:
    """Trạng thái chuẩn hiển thị bằng nhãn tiếng Việt; chuỗi cũ giữ nguyên."""
    ma = _nfc(v.get("kiem_tra_so")).casefold()
    return dict(v, kiem_tra_so=dk.NHAN_KIEM_TRA_SO[ma]) if ma in dk.NHAN_KIEM_TRA_SO else v


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ho_so")
    ap.add_argument("--out", required=True)
    ap.add_argument("--nghiem", action="store_true", help="dừng mã 2 nếu kiểm tự động có lỗi mức cao")
    ns = ap.parse_args(argv)
    out, kiem = xuat(Path(ns.ho_so), Path(ns.out))
    print(out)
    for k in kiem:
        print(f"[{k['muc_do']}] {k['noi_dung']}")
    if ns.nghiem and any(k["muc_do"] == "cao" for k in kiem):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
