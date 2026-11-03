import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("kiem_da_chot", Path(__file__).with_name("kiem-da-chot.py"))
kdc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kdc)
# Sổ mẫu riêng của test (bản chụp sổ của chủ kit): test không phụ thuộc kenh/cach-noi-da-chot.tsv,
# vốn trống ở kit hội viên và đổi theo từng kênh.
SO_TEST = Path(__file__).with_name("test-so-cach-noi.tsv")
LUAT = kdc.doc_so(SO_TEST)


def test_chan_cau_sai_cu_tvd():
    loi = kdc.quet("Pháo không lao xuống vực. Anh hy sinh.", LUAT)
    assert [r["ma"] for _, _, r in loi] == ["tvd-ong"]


def test_cho_qua_cau_da_chot():
    assert kdc.quet("Pháo không lao xuống vực. Ông anh dũng hy sinh.", LUAT) == []


def test_bao_dung_so_dong():
    loi = kdc.quet("dòng một\nanh hy sinh khi chèn bánh pháo", LUAT)
    assert loi[0][0] == 2


def test_so_that_cua_kenh_doc_duoc():
    kdc.doc_so()


def test_main_tra_ma_1_khi_pham(tmp_path, monkeypatch):
    monkeypatch.setattr(kdc, "doc_so", lambda: LUAT)
    f = tmp_path / "loi.txt"
    f.write_text("Anh hy sinh.", encoding="utf-8")
    assert kdc.main([str(f)]) == 1
    f.write_text("Ông anh dũng hy sinh.", encoding="utf-8")
    assert kdc.main([str(f)]) == 0


def test_chan_ten_viet_nam_goi_tron_trong_loi_doc():
    loi = kdc.quet("Theo lệnh của Võ Nguyên Giáp, pháo kéo ra.", kdc.ap_dung(LUAT, "loi-doc-v5.txt"))
    assert any(r["ma"].startswith("xung-ho-") for _, _, r in loi)


def test_cho_qua_ten_co_quan_ham_hoac_ong():
    van = ("Đại tướng Võ Nguyên Giáp nhận lệnh. Khẩu đội trưởng Tô Vĩnh Diện lao mình. Tiểu đội phó Phan Đình Giót. "
           "Đại tá Nguyễn Bội Giong, khi ấy là phái viên Bộ Tổng tư lệnh, kể. Chủ tịch Hồ Chí Minh viết thư.")
    assert kdc.quet(van, kdc.ap_dung(LUAT, "loi-doc-v5.txt")) == []


def test_luat_xung_ho_khong_ap_cho_the_ten_tren_hinh():
    assert kdc.quet("| \"Tô Vĩnh Diện · Khẩu đội trưởng\" |", kdc.ap_dung(LUAT, "phan-canh.md")) == []


def test_chan_quan_ham_ve_sau_khong_noi_thoi_diem():
    # năm 1954 chưa phong quân hàm: «Đại tá» về sau phải kèm «khi ấy/lúc đó là <chức vụ>» (user chốt 02/11/2026)
    loi = kdc.quet("Theo Đại tá Nguyễn Bội Giong trên Báo Quân đội nhân dân.", kdc.ap_dung(LUAT, "loi-doc-v5.txt"))
    assert any(r["ma"] == "quan-ham-thoi-diem-giong" for _, _, r in loi)
    dung = kdc.quet("Ông Nguyễn Bội Giong, lúc đó là phái viên Bộ Tổng tư lệnh, kể.", kdc.ap_dung(LUAT, "loi-doc-v5.txt"))
    assert dung == []
