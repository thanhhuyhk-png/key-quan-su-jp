import importlib.util
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location("kiem_de_tai", Path(__file__).with_name("kiem-de-tai.py"))
kdt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kdt)

CAM = """de_tai\ttu_khoa\tnam\ttrang_thai\tghi_chu
Điện Biên Phủ\tđiện biên phủ; dien bien phu; dbp\t1954\tđã đăng\tmẫu
Hà Nội 12 ngày đêm\t12 ngày đêm; b-52 hà nội\t1972\tđã lên lịch\t
Trân Châu Cảng\ttrân châu cảng; pearl harbor\t1941\tđã lên lịch\t
"""

CAM_CHUNG = """de_tai	tu_khoa	nam	trang_thai	ghi_chu
Địa đạo Củ Chi	~củ chi	1968	đã lên lịch	
"""

SO_CHUNG = """Đề tài,Góc kể,Ngôn ngữ,Hội viên,Ngày
Midway 1942,Ba quyết định của đô đốc,vi,hv01,2026-11-01
Cuba 1962,Đồng hồ đếm ngược,en,hv02,2026-11-02
"""


def tep(tmp_path, ten, chu):
    p = tmp_path / ten
    p.write_text(chu, encoding="utf-8", newline="")
    return p


def test_chuan_hoa_bo_dau_va_chu_hoa():
    assert kdt.chuan_hoa("Điện Biên  Phủ, 1954!") == "dien bien phu 1954"
    assert kdt.chuan_hoa("B-52") == "b 52"


def test_chan_dbp_cac_cach_goi(tmp_path):
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM))
    for de in ("Điện Biên Phủ 1954", "dien bien phu", "Chiến dịch Điện Biên Phủ"):
        kq = kdt.kiem(de, cam)
        assert kq.muc == "CHẶN", de
        assert kq.dong_khop


def test_tu_khoa_rieng_chan_bat_ke_nam(tmp_path):
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM))
    for nam in ("1946", "1953", "1975"):
        assert kdt.kiem(f"Điện Biên Phủ {nam}", cam).muc == "CHẶN", nam


def test_tu_khoa_chung_chung_danh_dau_dau_nga_thi_phan_biet_theo_nam(tmp_path):
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM_CHUNG))
    assert kdt.kiem("Địa đạo Củ Chi 1968", cam).muc == "CHẶN"      # tên riêng của dòng, luôn chặn
    assert kdt.kiem("Củ Chi 1968", cam).muc == "CHẶN"              # cùng năm
    assert kdt.kiem("Củ Chi 1975", cam).muc == "ĐẠT"               # từ khoá chung, khác năm
    assert kdt.kiem("Củ Chi", cam).muc == "CHẶN"                   # không năm thì chặn


def test_ten_rieng_cua_dong_van_chan_du_tu_khoa_chung_khac_nam(tmp_path):
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM_CHUNG))
    assert kdt.kiem("Địa đạo Củ Chi 1975", cam).muc == "CHẶN"


def test_khong_khop_tu_con_trong_tu_khac(tmp_path):
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM))
    assert kdt.kiem("Trận Dbpxyz", cam).muc == "ĐẠT"


def test_dat_khi_khong_trung(tmp_path):
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM))
    kq = kdt.kiem("Trận Kohima 1944", cam)
    assert kq.muc == "ĐẠT" and not kq.dong_khop


def test_so_chung_cung_goc_chan(tmp_path):
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM))
    chung = kdt.doc_so_chung(tep(tmp_path, "chung.csv", SO_CHUNG))
    kq = kdt.kiem("Midway 1942", cam, chung, goc="Ba quyết định của đô đốc", ngon_ngu="vi")
    assert kq.muc == "CHẶN"


def test_so_chung_khac_goc_canh_bao(tmp_path):
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM))
    chung = kdt.doc_so_chung(tep(tmp_path, "chung.csv", SO_CHUNG))
    kq = kdt.kiem("Trận Midway", cam, chung, goc="Vật chứng còn lại", ngon_ngu="vi")
    assert kq.muc == "CẢNH BÁO"


def test_so_chung_khac_ngon_ngu_dat(tmp_path):
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM))
    chung = kdt.doc_so_chung(tep(tmp_path, "chung.csv", SO_CHUNG))
    assert kdt.kiem("Cuba 1962", cam, chung, goc="Đồng hồ đếm ngược", ngon_ngu="vi").muc == "ĐẠT"


def test_so_chung_tsv_va_khong_goc(tmp_path):
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM))
    chung = kdt.doc_so_chung(tep(tmp_path, "chung.tsv", SO_CHUNG.replace(",", "\t")))
    assert kdt.kiem("Midway 1942", cam, chung, ngon_ngu="vi").muc == "CẢNH BÁO"


def test_main_ma_thoat(tmp_path, capsys):
    cam = tep(tmp_path, "cam.tsv", CAM)
    assert kdt.main(["Điện Biên Phủ 1954", "--cam", str(cam)]) == 1
    assert "CHẶN" in capsys.readouterr().out
    assert kdt.main(["Kohima 1944", "--cam", str(cam)]) == 0
    assert kdt.main([]) == 2


def test_so_that_cua_repo_chan_dbp():
    assert kdt.main(["Điện Biên Phủ 1954"]) == 1
    assert kdt.main(["dien bien phu"]) == 1


# --- đầu vào hỏng: mã thoát 2, không ĐẠT giả ---

def chay_main(capsys, *doi):
    ma = kdt.main(list(doi))
    out = capsys.readouterr()
    return ma, out.out, out.err


def test_so_chung_sai_ten_cot_dung_voi_ma_2(tmp_path, capsys):
    cam = tep(tmp_path, "cam.tsv", CAM)
    chung = tep(tmp_path, "chung.csv", "Chủ đề,Góc kể,Ngôn ngữ\nRach Gam Xoai Mut,x,vi\n")
    ma, out, err = chay_main(capsys, "Rạch Gầm Xoài Mút", "--cam", str(cam), "--so-chung", str(chung))
    assert ma == 2
    assert "chung.csv" in err and "de_tai" in err
    assert "ĐẠT" not in out


def test_so_cam_thieu_cot_dung_voi_ma_2(tmp_path, capsys):
    cam = tep(tmp_path, "cam.tsv", "ten\tnam\nX\t1954\n")
    ma, _, err = chay_main(capsys, "Midway", "--cam", str(cam))
    assert ma == 2 and "cam.tsv" in err and "de_tai" in err


def test_tep_thieu_ma_2_khong_traceback(tmp_path, capsys):
    cam = tep(tmp_path, "cam.tsv", CAM)
    ma, _, err = chay_main(capsys, "Midway", "--cam", str(cam), "--so-chung", str(tmp_path / "khong-co.csv"))
    assert ma == 2 and "khong-co.csv" in err


def test_tep_sai_ma_hoa_ma_2(tmp_path, capsys):
    cam = tep(tmp_path, "cam.tsv", CAM)
    chung = tmp_path / "u16.csv"
    chung.write_bytes("Đề tài,Góc kể\nMidway,x\n".encode("utf-16"))
    ma, _, err = chay_main(capsys, "Midway", "--cam", str(cam), "--so-chung", str(chung))
    assert ma == 2 and "u16.csv" in err


def test_in_so_dong_da_so(tmp_path, capsys):
    cam = tep(tmp_path, "cam.tsv", CAM)
    chung = tep(tmp_path, "chung.csv", SO_CHUNG)
    ma, out, _ = chay_main(capsys, "Waterloo 1815", "--cam", str(cam), "--so-chung", str(chung))
    assert ma == 0
    assert "sổ cấm: 3 dòng đã so" in out and "sổ chung: 2 dòng đã so" in out


def test_khong_so_chung_in_ro_chua_co(tmp_path, capsys):
    cam = tep(tmp_path, "cam.tsv", CAM)
    ma, out, _ = chay_main(capsys, "Điện Biên Phủ 1954", "--cam", str(cam))
    assert ma == 1  # vẫn so sổ cấm
    assert "sổ chung: chưa có, 0 dòng đã so" in out


def test_o_nhieu_dong_trong_ngoac_kep_khong_vo_dong(tmp_path):
    chung = tep(tmp_path, "chung.csv", 'Đề tài,Góc kể,Ngôn ngữ\nMidway 1942,"dòng 1\u2028dòng 2\ndòng 3",vi\n')
    dong = kdt.doc_so_chung(chung)
    assert len(dong) == 1 and "dòng 3" in dong[0]["goc_ke"]


# --- sổ cấm thật của kit: tên riêng quanh trận Điện Biên Phủ ---

SO_THAT = Path(__file__).resolve().parents[2] / "kit" / "so-chu-de-cam.tsv"


@pytest.mark.parametrize("de", [
    "Điện Biên Phủ 1953", "Him Lam", "Đồi A1", "Đồi C1", "Mường Thanh", "Kéo pháo vào Điện Biên", "De Castries",
    "Đờ Cát", "Chiến dịch Trần Đình", "Castor 1953", "Hồng Cúm", "Bản Kéo", "Cứ điểm Độc Lập", "Kế hoạch Navarre",
    "Điện Biên 1954", "Chiến dịch Điện Biên", "Dien Bien",
])
def test_so_that_chan_ten_rieng_dien_bien_phu(de):
    assert kdt.kiem(de, kdt.doc_cam(SO_THAT)).muc == "CHẶN", de


@pytest.mark.parametrize("de", ["Kohima 1944", "Tuyên ngôn Độc lập 1945", "Củ Chi 1975", "Tổng tiến công mùa xuân 1972"])
def test_so_that_khong_chan_nham(de):
    assert kdt.kiem(de, kdt.doc_cam(SO_THAT)).muc == "ĐẠT", de


@pytest.mark.parametrize("de", [
    "Dienbienphu 1954", "DIENBIENPHU", "Điệnbiênphủ", "Dien bienphu 1954", "dienbien phu", "Trận Dienbien",
    "Himlam", "Decastries", "Muongthanh 1954", "Kếhoạchnavarre",
])
def test_so_that_chan_cach_viet_lien_khong_dau_cach(de):
    assert kdt.kiem(de, kdt.doc_cam(SO_THAT)).muc == "CHẶN", de


@pytest.mark.parametrize("de", ["Trận Vạn Tường 1965", "Trận Núi Thành 1965", "Van Tuong 1965", "Vantuong", "Dienbienxyz"])
def test_so_that_viet_lien_khong_chan_nham_de_tai_khac(de):
    assert kdt.kiem(de, kdt.doc_cam(SO_THAT)).muc == "ĐẠT", de


def test_viet_lien_chi_khop_o_ranh_gioi_tieng(tmp_path):
    """Ghép các tiếng liền kề phải trùng đúng từ khoá, không khớp một đoạn nằm giữa chữ."""
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM))
    assert kdt.kiem("Trận Dienbienphuxyz", cam).muc == "ĐẠT"
    assert kdt.kiem("Trận Xdienbienphu", cam).muc == "ĐẠT"


def test_so_that_dong_nao_co_nam_va_tu_khoa_rieng_van_chan_khac_nam():
    cam = kdt.doc_cam(SO_THAT)
    for r in cam:
        nam = r.get("nam", "").split(";")[0]
        if not nam:
            continue
        sai_nam = str(int(nam) - 7)
        assert kdt.kiem(f"{r['de_tai']} {sai_nam}", cam).muc == "CHẶN", r["de_tai"]


def test_help_in_huong_dan_ma_0(capsys):
    for co in ("--help", "-h"):
        assert kdt.main([co]) == 0
        out = capsys.readouterr().out
        assert "Mã thoát" in out and "đã so" not in out.splitlines()[0]


SO_FORM = """Dấu thời gian\tĐề tài\tGóc kể\tNgôn ngữ\tHội viên
04/11/2026 20:15:00\tMidway 1942\tBa quyết định của đô đốc\tvi\tKênh A
"""


@pytest.mark.parametrize("cot_ngay", ["Dấu thời gian", "Timestamp"])
def test_so_tai_tu_google_form_doc_cot_thoi_gian_lam_ngay(tmp_path, cot_ngay):
    chung = kdt.doc_so_chung(tep(tmp_path, "form.tsv", SO_FORM.replace("Dấu thời gian", cot_ngay)))
    assert chung[0]["ngay"] == "04/11/2026 20:15:00"
    cam = kdt.doc_cam(tep(tmp_path, "cam.tsv", CAM))
    kq = kdt.kiem("Midway 1942", cam, chung, goc="Ba quyết định của đô đốc", ngon_ngu="vi")
    assert kq.muc == "CHẶN"
    assert any("Kênh A | 04/11/2026" in d for d in kq.dong_khop)
