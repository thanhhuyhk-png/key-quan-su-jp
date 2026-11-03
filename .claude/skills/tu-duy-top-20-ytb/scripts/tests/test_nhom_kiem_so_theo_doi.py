"""Test nhóm dạng danh sách, trạng thái kiểm tra số chuẩn, tab Theo dõi nhận kênh không xếp, mốc 0 ở tab thăng hạng."""
import json
import sys
from pathlib import Path

import openpyxl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import do_kenh as dk  # noqa: E402
import xuat_sheet as xs  # noqa: E402


def _hs(**them):
    kenh = [{"id": f"k{i}", "ten": f"Kênh {i}", "link": f"https://www.youtube.com/@k{i}", "subs": 1000 * (30 - i),
             "diem": 100 - i, "giu_loai": "Giữ", "nguon_so": "test", "ngay_video_dau": "2024-01-01"}
            for i in range(1, 25)]
    hs = {"du_an": "T", "ngay_do": "2026-10-22", "kenh": kenh, "video": [], "model_link": {"kenh": "k1"}}
    hs.update(them)
    return hs


def _xuat(tmp_path, hs):
    p = tmp_path / "hs.json"
    p.write_text(json.dumps(hs, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "t.xlsx"
    _, kiem = xs.xuat(p, out)
    return openpyxl.load_workbook(out), kiem


def _dong(ws, khoa_cot, gia_tri):
    hdr = [c.value for c in ws[xs.DONG_TIEU_DE]]
    j = hdr.index(khoa_cot)
    for r in ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1):
        if r[j].value == gia_tri:
            return r, hdr
    raise AssertionError(f"không thấy {gia_tri!r}")


# ---------- chuẩn hoá nhóm ----------

def test_chuan_nhom_nhan_chuoi_cu_danh_sach_va_nhan_hien_thi():
    assert dk.chuan_nhom("moi") == ["moi"]
    assert dk.chuan_nhom(["moi", "cung_nguon_luc"]) == ["moi", "cung_nguon_luc"]
    assert dk.chuan_nhom("Mới < 12 tháng · Cùng nguồn lực") == ["moi", "cung_nguon_luc"]
    assert dk.chuan_nhom("on_dinh, cung_nguon_luc") == ["on_dinh", "cung_nguon_luc"]
    assert dk.chuan_nhom(None) == [] and dk.chuan_nhom("") == []
    assert dk.chuan_nhom(["moi", "moi"]) == ["moi"]


def test_chuan_nhom_co_moi_tinh_tu_tuoi_video_dau():
    assert dk.chuan_nhom(["on_dinh"], tuoi_ngay=100) == ["moi", "on_dinh"]
    assert dk.chuan_nhom(["moi", "cung_nguon_luc"], tuoi_ngay=400) == ["cung_nguon_luc"]
    assert dk.chuan_nhom([], tuoi_ngay=364) == ["moi"] and dk.chuan_nhom([], tuoi_ngay=365) == []


def test_tab_top20_nhom_ghep_nhan_va_co_moi_tinh_tu_ngay_video_dau(tmp_path):
    hs = _hs()
    hs["kenh"][0].update({"nhom": ["on_dinh", "cung_nguon_luc"], "ngay_video_dau": "2026-09-04"})   # 48 ngày tuổi
    hs["kenh"][1].update({"nhom": "moi", "ngay_video_dau": "2023-01-01"})                          # nhóm tay sai
    wb, kiem = _xuat(tmp_path, hs)
    ws = wb[xs.TEN_TAB[1]]
    r, hdr = _dong(ws, "Tên kênh", "Kênh 1")
    assert r[hdr.index("Nhóm")].value == "Mới < 12 tháng · Ổn định ≥ 2 năm · Cùng nguồn lực"
    r2, _ = _dong(ws, "Tên kênh", "Kênh 2")
    assert "Mới" not in (r2[hdr.index("Nhóm")].value or "")
    assert any("Kênh 2" in k["noi_dung"] and "nhóm" in k["noi_dung"] and k["muc_do"] == "thấp" for k in kiem)


def test_nhom_chuoi_cu_van_chay_va_kiem_ho_so_thay_nhom_moi_trong_danh_sach(tmp_path):
    hs = _hs()
    for k in hs["kenh"]:
        k["ngay_video_dau"] = "2022-01-01"
    hs["kenh"][23].update({"nhom": ["moi"], "ngay_video_dau": "2026-08-01", "diem": 1})   # mới nhưng hạng 24 → ngoài TOP
    _, kiem = _xuat(tmp_path, hs)
    assert any("nhóm 'mới" in k["noi_dung"] for k in kiem)


def test_tai_sinh_gan_nhom_moi_bi_canh_bao(tmp_path):
    hs = _hs()
    hs["kenh"][0].update({"ngay_video_dau": "2026-09-04", "co": ["TAI_SINH"]})
    _, kiem = _xuat(tmp_path, hs)
    assert any("TAI_SINH" in k["noi_dung"] and "Kênh 1" in k["noi_dung"] and k["muc_do"] == "vừa" for k in kiem)


# ---------- kiểm tra số thật ----------

def test_trang_thai_kiem_so_chuan_va_chuoi_cu():
    for ma in ("chua_chin", "so_bo", "dat", "nghi"):
        assert dk.trang_thai_kiem_so(ma) == ma
    assert dk.trang_thai_kiem_so("Đạt (đã đọc 20 bình luận)") == "dat"
    assert dk.trang_thai_kiem_so("nghi ngờ (like thấp)") == "nghi"
    assert dk.trang_thai_kiem_so("sơ bộ: chưa đọc bình luận") == "so_bo"
    assert dk.trang_thai_kiem_so("chưa chín (< 30 ngày)") == "chua_chin"
    assert dk.trang_thai_kiem_so("loại") == "nghi" and dk.trang_thai_kiem_so("") is None and dk.trang_thai_kiem_so(None) is None


def _hs_video(trang_thai, he_so=6.0):
    hs = _hs()
    hs["video"] = [{"kenh": "k1", "id": "v1", "link": "https://youtu.be/v1", "tieu_de": "V", "ngay_dang": "2026-09-01",
                    "views": 1000, "he_so": he_so, "la_top_view": True, "kiem_tra_so": trang_thai}]
    return hs


@pytest.mark.parametrize("trang_thai,mau,hien", [
    ("dat", xs.XANH_LA, "đạt"), ("so_bo", xs.CAM_NHAT, "sơ bộ"), ("nghi", xs.DO_NHAT, "nghi ngờ"),
    ("chua_chin", xs.XAM, "chưa chín"), ("đạt, đã đọc bình luận", xs.XANH_LA, "đạt, đã đọc bình luận"),
    ("loại", xs.DO_NHAT, "loại")])
def test_to_mau_theo_trang_thai_kiem_so(tmp_path, trang_thai, mau, hien):
    wb, _ = _xuat(tmp_path, _hs_video(trang_thai))
    ws = wb[xs.TEN_TAB[5]]
    r, hdr = _dong(ws, "Tiêu đề", "V")
    j = hdr.index("Kiểm tra số thật")
    assert r[j].value == hien
    assert r[0].fill.fgColor.rgb == mau


def test_nghi_ngo_van_to_do_du_he_so_thap_nhung_dat_thi_khong_to(tmp_path):
    wb, _ = _xuat(tmp_path, _hs_video("nghi", he_so=3.5))
    r, _ = _dong(wb[xs.TEN_TAB[5]], "Tiêu đề", "V")
    assert r[0].fill.fgColor.rgb == xs.DO_NHAT
    wb2, _ = _xuat(tmp_path, _hs_video("dat", he_so=3.5))
    r2, _ = _dong(wb2[xs.TEN_TAB[5]], "Tiêu đề", "V")
    assert r2[0].fill.fgColor.rgb != xs.XANH_LA


# ---------- tab 9: Theo dõi nhận cả kênh không xếp ----------

def test_tab_theo_doi_co_ca_kenh_theo_doi_va_khong_du_chi_so_nhung_khong_co_kenh_loai(tmp_path):
    hs = _hs()
    hs["kenh"].append({"id": "kx", "ten": "Không đủ chỉ số", "giu_loai": "Giữ", "subs": 5, "nguon_so": "t"})   # không có điểm
    hs["kenh"].append({"id": "kt", "ten": "Đang theo dõi", "giu_loai": "Theo dõi", "subs": 7, "nguon_so": "t"})
    hs["kenh"].append({"id": "kl", "ten": "Bị loại", "giu_loai": "Loại", "subs": 9, "nguon_so": "t"})
    wb, _ = _xuat(tmp_path, hs)
    ws = wb[xs.TEN_TAB[9]]
    ten = {r[2] for r in ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1, values_only=True)}
    assert "Không đủ chỉ số" in ten and "Đang theo dõi" in ten and "Bị loại" not in ten
    assert "Kênh 1" in ten


# ---------- tab 3 / tab 1: mốc 0 ----------

def test_moc_0_hien_ro_thay_vi_trong_va_chua_co_moc(tmp_path):
    hs = _hs()
    hs["kenh"][0].update({"subs": 38_000, "subs_30_ngay_truoc": 0})
    hs["kenh"][1].update({"subs": 1000, "subs_30_ngay_truoc": 500})
    wb, _ = _xuat(tmp_path, hs)
    for tab, khoa in ((xs.TEN_TAB[3], "% tăng"), (xs.TEN_TAB[1], "% tăng 30 ngày")):
        ws = wb[tab]
        r0, hdr = _dong(ws, "Tên kênh", "Kênh 1")
        r1, _ = _dong(ws, "Tên kênh", "Kênh 2")
        r2, _ = _dong(ws, "Tên kênh", "Kênh 3")
        assert str(r0[hdr.index(khoa)].value).startswith("mốc 0")
        assert r1[hdr.index(khoa)].value == pytest.approx(1.0)
        assert r2[hdr.index(khoa)].value == "chưa có mốc"
    ws3 = wb[xs.TEN_TAB[3]]
    ten = [r[3] for r in ws3.iter_rows(min_row=xs.DONG_TIEU_DE + 1, values_only=True)]
    assert ten.index("Kênh 2") < ten.index("Kênh 1") < ten.index("Kênh 3")     # có % → mốc 0 → chưa có mốc
