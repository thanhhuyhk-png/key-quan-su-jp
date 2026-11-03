"""Test bộ lọc chính sách: chạy `python -m pytest tools/loc-chinh-sach -q`."""
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location("quet", Path(__file__).with_name("quet.py"))
quet = importlib.util.module_from_spec(_spec)
sys.modules["quet"] = quet  # dataclass cần module có trong sys.modules
_spec.loader.exec_module(quet)
DS = quet.doc_mau(quet.DS_MAU)


def _quet(tmp_path, noi_dung, la_tieu_de=False):
    f = tmp_path / "mau.txt"
    f.write_text(noi_dung, encoding="utf8")
    return [(tu.lower(), m.muc_do) for _, tu, m, _ in quet.quet_file(f, DS, la_tieu_de)]


def test_loi_doc_sach_khong_bao_gi(tmp_path):
    assert _quet(tmp_path, "Mười bảy giờ năm phút, ngày mười ba tháng ba, pháo ta bắn vào Him Lam.") == []


def test_chui_tuc_va_miet_thi_bi_chan(tmp_path):
    kq = _quet(tmp_path, "đm bọn khựa\nthằng nhật lùn")
    assert ("đm", "CHAN") in kq and ("khựa", "CHAN") in kq and ("nhật lùn", "CHAN") in kq


def test_tu_gay_soc_chi_chan_o_tieu_de(tmp_path):
    assert _quet(tmp_path, "Ảnh không che xác chết") == [("xác chết", "CANH")]
    kq = _quet(tmp_path, "Ảnh không che xác chết", la_tieu_de=True)
    assert ("không che", "CHAN") in kq and ("xác chết", "CHAN") in kq


def test_mot_cho_khop_chi_bao_mot_lan_va_lay_muc_nang(tmp_path):
    kq = _quet(tmp_path, "Trận đánh đẫm máu", la_tieu_de=True)
    assert kq == [("đẫm máu", "CHAN")]


def test_khong_bat_nham_tu_thuong(tmp_path):
    # "mọi người", "Pháp", "vãng lai" không được khớp mẫu "mọi rợ", "vãi"
    assert _quet(tmp_path, "Mọi người dân Pháp vãng lai ở Đông Dương") == []


def test_so_luong_tau_khong_bi_coi_la_miet_thi(tmp_path):
    assert _quet(tmp_path, "Ba tàu sân bay Mỹ không có ở bến; ba tàu chiến bị đánh chìm") == []
    assert ("ba tàu", "CHAN") in _quet(tmp_path, "bọn ba tàu")


def test_he_tu_va_luat_cung_la_canh_bao(tmp_path):
    kq = _quet(tmp_path, "quân ngụy và Trung Quốc")
    assert ("ngụy", "CANH") in kq and ("trung quốc", "CANH") in kq


def test_ma_thoat_1_khi_co_loi_chan(tmp_path):
    f = tmp_path / "x.txt"
    f.write_text("cách làm bom", encoding="utf8")
    assert quet.main([str(f)]) == 1
    f.write_text("trận Him Lam", encoding="utf8")
    assert quet.main([str(f)]) == 0


SRT = """1
00:00:02,000 --> 00:00:05,000
Ảnh không che những thi thể

2
00:00:40,000 --> 00:00:44,000
Ảnh không che những thi thể
"""


def test_srt_30_giay_dau_xet_gat_nhu_tieu_de(tmp_path):
    f = tmp_path / "loi.srt"
    f.write_text(SRT, encoding="utf8")
    kq = [(so_dong, tu.lower(), m.muc_do) for so_dong, tu, m, _ in quet.quet_file(f, DS, False)]
    # câu ở giây 2 (dòng 3) xét như tiêu đề: "không che" bị CHẶN; câu ở giây 40 (dòng 7) xét như lời đọc
    assert (3, "không che", "CHAN") in kq
    assert not any(d == 7 and muc == "CHAN" for d, _, muc in kq)


def test_vi_tri_metadata_la_ten_khac_cua_tieu_de(tmp_path):
    f = tmp_path / "td.txt"
    f.write_text("Trận đánh đẫm máu", encoding="utf8")
    assert quet.main([str(f), "--vi-tri", "metadata"]) == 1
    assert quet.main([str(f)]) == 0


def test_tu_dien_yt_gop_vao_bat_tu_metadata(tmp_path):
    # từ của bộ lọc YouTube chung (gộp 03/11/2026): "tra tấn" là CẢNH BÁO trong lời, CHẶN ở tiêu đề
    assert _quet(tmp_path, "tù binh bị tra tấn") == [("tra tấn", "CANH")]
    assert _quet(tmp_path, "tù binh bị tra tấn", la_tieu_de=True) == [("tra tấn", "CHAN")]


def test_khong_bat_nham_tu_tieng_anh_thuong(tmp_path):
    # «f*ck» trong từ điển gốc là chữ đã che; retard/rape chỉ khớp đúng từ; Gore, kms chỉ cảnh báo
    kq = _quet(tmp_path, "flashback fallback feedback fire retardant rapeseed", la_tieu_de=True)
    assert kq == []
    assert ("f*ck", "CHAN") in _quet(tmp_path, "what the f*ck", la_tieu_de=True)
    assert all(muc == "CANH" for _, muc in _quet(tmp_path, "Al Gore drove 120 kms", la_tieu_de=True))


def test_vi_tri_dang_co_dau_bang(tmp_path):
    f = tmp_path / "td.txt"
    f.write_text("Trận đánh đẫm máu", encoding="utf8")
    assert quet.main([str(f), "--vi-tri=metadata"]) == 1


def test_help_in_cach_dung_va_thoat_0(capsys):
    for co in ("--help", "-h"):
        assert quet.main([co]) == 0
        out = capsys.readouterr().out
        assert "--tieu-de" in out and "--vi-tri" in out and "KHÔNG THẤY FILE" not in out


def test_help_di_kem_tep_van_la_help(tmp_path, capsys):
    f = tmp_path / "a.txt"
    f.write_text("đm", encoding="utf8")
    assert quet.main([str(f), "--help"]) == 0
    assert "a.txt" not in capsys.readouterr().out


def test_khong_doi_so_van_ma_thoat_2():
    assert quet.main([]) == 2
