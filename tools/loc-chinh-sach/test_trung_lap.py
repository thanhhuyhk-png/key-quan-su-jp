import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("trung_lap", Path(__file__).with_name("trung-lap.py"))
tl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tl)

VTT = """WEBVTT
Kind: captions
Language: vi

00:00:01.000 --> 00:00:03.000 align:start position:0%
chiều<00:00:01.500><c> ngày</c> 13 tháng 3

00:00:03.000 --> 00:00:05.000
chiều ngày 13 tháng 3
pháo của ta bắn vào him lam
"""


def test_doc_vtt_bo_moc_gio_the_va_dong_lap():
    assert tl.lam_sach_phu_de(VTT) == "chiều ngày 13 tháng 3\npháo của ta bắn vào him lam"


def test_tach_tieng_bo_dau_cau_va_hoa_thuong():
    assert tl.tach_tieng("Chiều 13/3, pháo bắn!") == ["chiều", "13", "3", "pháo", "bắn"]


def test_ten_rieng_lay_chu_hoa_khong_dau_cau():
    ten = tl.ten_rieng("Pháo bắn vào Him Lam. Quân Pháp ở Mường Thanh rút.")
    assert {"him", "lam", "mường", "thanh", "pháp"} <= ten
    assert "pháo" not in ten  # chữ hoa đầu câu không tính là tên riêng


def test_loc_bo_so_va_ten_rieng():
    assert tl.loc(["chiều", "13", "pháo", "him", "lam"], {"him", "lam"}) == ["chiều", "pháo"]


def test_loc_bo_so_viet_bang_chu_va_tu_chi_ngay_gio():
    tieng = tl.tach_tieng("ngày hai mươi mốt tháng bảy bốn mươi khẩu pháo khai hỏa")
    assert tl.loc(tieng, set()) == ["khẩu", "pháo", "khai", "hỏa"]


def test_bo_cum_chinh_thong_ca_hai_phia():
    cum = [tl.tach_tieng("Quyết chiến, Quyết thắng")]
    tieng = tl.tach_tieng("lá cờ Quyết chiến Quyết thắng tung bay")
    assert tl.bo_cum(tieng, cum) == ["lá", "cờ", "tung", "bay"]


def test_ty_le_trung_cum_sau_tieng():
    goha = "một hai ba bốn năm sáu bảy tám".split()
    ref = tl.cum(goha[:7], 6)  # hai cụm đầu của goha có trong nguồn
    so_trung, tong = tl.dem_trung(goha, ref, 6)
    assert (so_trung, tong) == (2, 3)


def test_cau_trung_nguyen_van_tu_muoi_tieng():
    ref = tl.cum(tl.tach_tieng("hôm ấy cả thung lũng rung lên dưới làn đạn pháo của quân ta"), 10)
    loi = "Mở đầu. Hôm ấy cả thung lũng rung lên dưới làn đạn pháo của quân ta. Câu khác hẳn."
    cau = tl.cau_trung_dai(loi, ref, 10)
    assert len(cau) == 1 and cau[0].startswith("Hôm ấy")


def test_bo_qua_cau_nhan_dien_kenh():
    loi = "Đây là Goha Studio. Pháo bắn vào Him Lam."
    assert tl.bo_cau(loi, ["Đây là Goha Studio."]) == "Pháo bắn vào Him Lam."


def test_cau_chi_trung_vi_cum_chinh_thong_thi_khong_bi_bat():
    cum = [tl.tach_tieng("độc lập, chủ quyền, thống nhất và toàn vẹn lãnh thổ")]
    nguon = "hiệp định công nhận độc lập chủ quyền thống nhất và toàn vẹn lãnh thổ của ba nước"
    ref = tl.cum(tl.chuan_tieng(nguon, cum), 10)
    loi = "Hiệp định công nhận độc lập, chủ quyền, thống nhất và toàn vẹn lãnh thổ của ba nước."
    assert tl.cau_trung_dai(loi, ref, 10, cum) == []
