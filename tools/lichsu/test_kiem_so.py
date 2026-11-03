import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("kiem_so", Path(__file__).with_name("kiem-so.py"))
ks = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ks)

TRANG = {"qdnd.vn/bai-1": ks.khoa_so(ks.chuan_hoa(
    "Ngày 13-3-1954, Chiến dịch Điện Biên Phủ bắt đầu. Trải qua “ba đợt” chiến đấu "
    "liên tục trong 56 ngày đêm, quân ta tiêu diệt và bắt sống 16.200 tên địch."))}


def test_trich_dung_nguyen_van_thi_ok():
    assert ks.kiem_cap("https://www.qdnd.vn/bai-1/", "Chiến dịch Điện Biên Phủ bắt đầu", TRANG) == "OK"


def test_trich_co_dau_ba_cham_va_ngoac_cong_van_khop():
    trich = 'Trải qua "ba đợt" chiến đấu … bắt sống 16.200 tên địch'
    assert ks.kiem_cap("http://qdnd.vn/bai-1", trich, TRANG) == "OK"


def test_trich_bi_sua_so_thi_khong_khop():
    assert ks.kiem_cap("https://qdnd.vn/bai-1", "bắt sống 16.000 tên địch", TRANG) == "KHÔNG KHỚP"


def test_chua_tai_trang_thi_thieu_trang():
    assert ks.kiem_cap("https://nhandan.vn/x", "bất kỳ câu nào dài", TRANG) == "THIẾU TRANG"


def test_dong_khong_co_nguon_dat_thi_loi_va_mot_nguon_thi_khong_loi():
    dong = {"nguon_1_url": "https://qdnd.vn/bai-1", "trich_nguyen_van_1": "56 ngày đêm, quân ta",
            "nguon_2_url": "", "trich_nguyen_van_2": ""}
    assert ks.kiem_dong(dong, TRANG) == (["OK", "TRỐNG"], False)
    assert ks.kiem_dong({"nguon_1_url": "", "trich_nguyen_van_1": ""}, TRANG)[1] is True


def test_nap_trang_doc_url_dong_dau(tmp_path):
    (tmp_path / "a.txt").write_text("URL: https://qdnd.vn/bai-2\nNội dung  có\nhai dòng", encoding="utf-8")
    assert ks.nap_trang(tmp_path) == {"qdnd.vn/bai-2": "nộidungcóhaidòng"}


def test_trich_co_ngoac_vuong_ba_cham_va_khoang_trang_sat_ngoac():
    trich = 'Trải qua “ ba đợt ” chiến đấu [...] tiêu diệt và bắt sống 16.200 tên địch'
    assert ks.kiem_cap("https://qdnd.vn/bai-1", trich, TRANG) == "OK"
