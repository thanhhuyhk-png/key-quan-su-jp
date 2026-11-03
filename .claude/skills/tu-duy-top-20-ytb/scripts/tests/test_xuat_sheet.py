"""Test cho xuat_sheet.py: hồ sơ JSON → XLSX 12 tab theo mẫu Top 20 (tải lên Google Drive thành Google Sheet)."""
import json
import sys
from pathlib import Path

import openpyxl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import xuat_sheet as xs  # noqa: E402


def ho_so():
    kenh = []
    for i in range(1, 26):
        kenh.append({
            "id": f"k{i}", "ten": f"Kênh {i}", "link": f"https://www.youtube.com/@k{i}",
            "nhom": "moi" if i % 3 == 0 else "on_dinh", "ngach": "kể chuyện", "dinh_dang": "người que",
            "tuoi_khan_gia": "18–34", "tuoi_muc_tin": "Vừa",
            "subs": 100_000 - i * 1000, "subs_30_ngay_truoc": 90_000 - i * 900,
            "so_video": 50 + i, "trung_vi_20_dai": 200_000 - i * 5000, "sub_moi_video": 1000 - i,
            "diem": 100 - i, "hang_30_ngay_truoc": (i % 25) + 1,
            "giu_loai": "Giữ" if i <= 20 else "Loại", "ly_do": "test", "co": "",
        })
    video = []
    for i in range(1, 4):
        for j in range(1, 6):
            video.append({"kenh": f"k{i}", "id": f"v{i}{j}", "link": f"https://youtu.be/v{i}{j}",
                          "tieu_de": f"Video {i}.{j}", "ngay_dang": "2026-09-01", "thoi_luong_s": 1300,
                          "views": 10_000 * (6 - j), "he_so": 6 - j, "la_top_view": True})
    return {
        "du_an": "Thử", "ngay_do": "2026-10-22", "ngay_moc_truoc": "2026-09-22",
        "muc_tieu": {"khan_gia": "18–34", "dinh_dang": "người que", "nguon_luc": "1 người + AI",
                     "rang_buoc": ["né chiến tranh"]},
        "model_link": {"kenh": "k1", "ly_do": ["sub/video cao nhất"], "bam_gi": ["nhịp đăng"],
                       "khong_bam": ["đề tài ma"], "theo_doi_hang_tuan": ["sub, view"], "trang_thai": "đề xuất"},
        "kenh": kenh, "video": video,
        "doi_chung": [{"kenh": "k1", "video_hit": "v11", "video_thuong": "v15", "ket_luan": "tiêu đề"}],
        "nhan_ban": [{"video_goc": "v11", "nhu_cau": "x",
                      "diem": {"nhu_cau": 5, "bang_chung": 4, "khoang_trong": 4, "hop_khan_gia": 5,
                               "chi_phi": 3, "rui_ro": 4}}],
        "theo_doi": [{"ngay": "2026-10-22", "kenh": "k1", "subs": 99000}],
        "chu_y": [{"loai": "gioi_han", "noi_dung": "thiếu CTR", "muc_do": "cao"}],
    }


@pytest.fixture
def wb(tmp_path):
    p = tmp_path / "hs.json"
    p.write_text(json.dumps(ho_so(), ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "top20.xlsx"
    xs.xuat(p, out)
    return openpyxl.load_workbook(out)


def test_du_12_tab_dung_thu_tu(wb):
    assert wb.sheetnames == xs.TEN_TAB
    assert len(wb.sheetnames) == 12


def test_tab_top20_chi_20_kenh_giu_xep_theo_diem_va_danh_dau_model_link(wb):
    ws = wb[xs.TEN_TAB[1]]
    hdr = [c.value for c in ws[xs.DONG_TIEU_DE]]
    assert hdr[0] == "Hạng" and "Model Link" in hdr and "Tên kênh" in hdr
    rows = list(ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1, values_only=True))
    rows = [r for r in rows if r[0] is not None]
    assert len(rows) == 20
    assert rows[0][hdr.index("Tên kênh")] == "Kênh 1"
    assert rows[0][hdr.index("Model Link")] == "★ MODEL LINK"
    # top 10 tô màu khác 11–20
    c1 = ws.cell(xs.DONG_TIEU_DE + 1, 1).fill.fgColor.rgb
    c11 = ws.cell(xs.DONG_TIEU_DE + 11, 1).fill.fgColor.rgb
    assert c1 != c11


def test_link_la_hyperlink(wb):
    ws = wb[xs.TEN_TAB[1]]
    hdr = [c.value for c in ws[xs.DONG_TIEU_DE]]
    cell = ws.cell(xs.DONG_TIEU_DE + 1, hdr.index("Link kênh") + 1)
    assert cell.hyperlink is not None and "youtube.com" in cell.hyperlink.target


def test_tab_video_top_gom_theo_kenh_co_dong_tieu_de_kenh(wb):
    ws = wb[xs.TEN_TAB[2]]
    vals = [r[0] for r in ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1, values_only=True)]
    assert any(isinstance(v, str) and v.startswith("#1 · Kênh 1") for v in vals)
    assert any(isinstance(v, str) and v.startswith("#2 · Kênh 2") for v in vals)


def test_tab_thang_hang_tinh_dung_chenh_hang_va_tang_sub(wb):
    ws = wb[xs.TEN_TAB[3]]
    hdr = [c.value for c in ws[xs.DONG_TIEU_DE]]
    rows = [r for r in ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1, values_only=True) if r[0] is not None]
    by = {r[hdr.index("Tên kênh")]: r for r in rows}
    r1 = by["Kênh 1"]
    assert r1[hdr.index("Hạng nay")] == 1
    assert r1[hdr.index("Hạng 30 ngày trước")] == 2
    assert r1[hdr.index("Thăng/giáng")] == 1
    assert r1[hdr.index("Sub tăng 30 ngày")] == 99_000 - 89_100


def test_tab_nhan_ban_tinh_tong_diem_co_hoi_va_ket_luan(wb):
    ws = wb[xs.TEN_TAB[7]]
    hdr = [c.value for c in ws[xs.DONG_TIEU_DE]]
    r = next(ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1, values_only=True))
    assert r[hdr.index("Tổng điểm cơ hội (/30)")] == 25
    assert r[hdr.index("Kết luận điểm")] == "Thử ngay (> 22)"


def test_tu_dien_cot_giai_thich_moi_cot_tab_top20(wb):
    ws = wb[xs.TEN_TAB[11]]
    cot_da_giai_thich = {r[1] for r in ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1, values_only=True)}
    for c in xs.COT_TOP20:
        assert c[0] in cot_da_giai_thich, c[0]
