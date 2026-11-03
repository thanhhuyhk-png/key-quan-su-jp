"""Test so lời: chuẩn hoá tiếng Việt, căn token, tỉ lệ khớp, báo cáo chữ và json."""
import argparse
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import so_loi  # noqa: E402
from chung import LoiKit  # noqa: E402


def t(chu, lang="vi"):
    return so_loi.chuan_hoa(chu, lang)


def tu(*chu):
    """Tệp words.json giả: mỗi chữ cách nhau 0,5 s."""
    return {"language": "vi", "words": [
        {"id": f"word_{i:06d}", "ordinal": i, "text": w, "start_ms": i * 500, "end_ms": i * 500 + 400,
         "speaker": "1", "audio_event": False} for i, w in enumerate(chu)]}


def goi(tmp_path, loi, words, *kem):
    tl = tmp_path / "loi-chuan.txt"
    tl.write_text(loi, encoding="utf-8")
    tw = tmp_path / "w.json"
    tw.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    p = argparse.ArgumentParser()
    so_loi.dang_ky(p)
    return p.parse_args(["--text", str(tl), "--words", str(tw), *kem])


# ---------- chuẩn hoá ----------

def test_ten_rieng_thuong_hoa_bo_dau_cau():
    assert t("Điện Biên Phủ,") == ["điện", "biên", "phủ"]


def test_the_ngoac_vuong_bi_bo():
    assert t("[fast-paced] Chiến thắng!") == ["chiến", "thắng"]


def test_gach_noi_thanh_cach_ten_phap():
    assert t("Đờ Cát-xtơ-ri") == ["đờ", "cát", "xtơ", "ri"]


def test_ngay_thang_nam():
    # đọc: bảy tháng năm năm một nghìn chín trăm năm mươi bốn
    assert t("7/5/1954") == "bảy tháng năm năm một nghìn chín trăm năm mươi bốn".split()


def test_ngay_thang_khong_nam():
    assert t("12/9") == "mười hai tháng chín".split()


def test_nam_khong_tram():
    assert t("2025") == "hai nghìn không trăm hai mươi năm".split()
    assert t("1005") == "một nghìn không trăm linh năm".split()


def test_so_nho_va_lon():
    assert t("0") == ["không"]
    assert t("10") == ["mười"]
    assert t("15") == ["mười", "năm"]
    assert t("21") == ["hai", "mươi", "một"]
    assert t("105") == "một trăm linh năm".split()
    assert t("1000000") == ["một", "triệu"]
    assert t("2.000") == ["hai", "nghìn"]
    assert t("1.954") == "một nghìn chín trăm năm mươi bốn".split()
    assert t("1.000.000") == ["một", "triệu"]


def test_so_thap_phan_va_don_vi():
    assert t("1,5 km") == ["một", "phẩy", "năm", "km"]
    assert t("50%") == "năm mươi phần trăm".split()
    assert t("4 km²") == ["bốn", "km", "vuông"]
    assert t("4 km2") == ["bốn", "km", "vuông"]


def test_ki_lo_met_ve_km():
    assert t("ki-lô-mét") == ["km"]
    assert t("kilômét") == ["km"]
    assert t("năm ki lô mét") == ["năm", "km"]


def test_dau_thanh_kieu_cu_moi_nhu_nhau():
    assert t("hoà bình") == t("hòa bình")
    assert t("thuỷ điện") == t("thủy điện")
    assert t("uỷ ban") == t("ủy ban")
    assert t("khoẻ") == t("khỏe")
    assert t("quý") == ["quý"]  # không đụng chữ đã đúng


def test_bien_the_so_va_vung_mien():
    assert t("hai mươi mốt") == t("21")
    assert t("hai mươi tư") == t("24")
    assert t("mười lăm") == t("15")
    assert t("ngàn") == t("nghìn")
    assert t("tỉ") == t("tỷ")


def test_ngon_ngu_khac_khong_doi_so():
    assert t("In 1954, Hanoi", "en") == ["in", "1954", "hanoi"]


# ---------- so khớp ----------

def test_khop_hoan_toan_voi_so_va_dau():
    ref = "Ngày 7/5/1954, Điện Biên Phủ thất thủ."
    hyp = tu("Ngày", "bảy", "tháng", "năm", "năm", "1954", "điện", "biên", "phủ", "thất", "thủ")
    kq = so_loi.so(ref, hyp, "vi", 0.97)
    assert kq["match"] == 1.0 and kq["pass"] is True and kq["issues"] == []


def test_thieu_tu_la_loi_thua_tu_khong_phat():
    ref = "một hai ba bốn năm sáu bảy tám chín mười"
    hyp = tu("một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười", "thừa", "thêm")
    assert so_loi.so(ref, hyp, "vi", 0.97)["match"] == 1.0
    hyp2 = tu("một", "hai", "ba", "bốn", "sáu", "bảy", "tám", "chín", "mười")
    kq = so_loi.so(ref, hyp2, "vi", 0.97)
    assert kq["match"] == 0.9 and kq["pass"] is False and kq["scriptWords"] == 10 and kq["heardWords"] == 9
    assert kq["issues"][0]["expected"] == "năm" and kq["issues"][0]["heard"] == ""
    assert kq["issues"][0]["start_ms"] is None


def test_thay_chu_co_thoi_gian_cua_chu_nghe_duoc():
    kq = so_loi.so("một hai ba", tu("một", "hay", "ba"), "vi", 0.97)
    (loi,) = kq["issues"]
    assert (loi["expected"], loi["heard"], loi["start_ms"], loi["end_ms"]) == ("hai", "hay", 500, 900)


def test_audio_event_bi_bo():
    w = tu("một", "(tiếng cười)", "hai")
    w["words"][1]["audio_event"] = True
    kq = so_loi.so("một hai", w, "vi", 0.97)
    assert kq["heardWords"] == 2 and kq["match"] == 1.0


def test_doc_duoc_json_cua_giong():
    # lược đồ `kit.py giong --json`: results[0].words
    d = {"adapter": "elevenlabs", "results": [{"words": [{"text": "một", "start_ms": 0, "end_ms": 10}]}]}
    assert so_loi.doc_chu_nghe(d)[0]["text"] == "một"


def test_ngưỡng_bang_dung_van_dat():
    kq = so_loi.so("a b", tu("a", "b"), "vi", 1.0)
    assert kq["pass"] is True


# ---------- dòng lệnh ----------

def test_cli_dat_in_dau_tich_va_thoat_0(tmp_path, capsys):
    a = goi(tmp_path, "[fast-paced] Chào các bạn", tu("chào", "các", "bạn"))
    assert so_loi.chay(a) == 0
    ra = capsys.readouterr().out
    assert ra.startswith("✓ 100.0% (≥ 97%)")


def test_cli_khong_dat_van_thoat_0_va_liet_ke_cho_lech(tmp_path, capsys):
    loi = " ".join(["từ"] * 9 + ["đúng"])
    a = goi(tmp_path, loi, tu(*(["từ"] * 9 + ["sai"])))
    assert so_loi.chay(a) == 0
    d = capsys.readouterr().out.splitlines()
    assert d[0].startswith("✗ 90.0%")
    assert "0:04.5" in d[1] and "chuẩn «đúng» / nghe «sai»" in d[1]


def test_cli_json_dung_luoc_do(tmp_path, capsys):
    a = goi(tmp_path, "một hai", tu("một", "hai"), "--json", "--min", "0.9")
    so_loi.chay(a)
    d = json.loads(capsys.readouterr().out)
    assert set(d) == {"match", "scriptWords", "heardWords", "issues", "min", "pass", "language"}
    assert d["pass"] is True and d["min"] == 0.9 and d["language"] == "vi"


def test_cli_mac_dinh_tieng_viet_khi_words_khong_ghi_ngon_ngu(tmp_path, capsys):
    w = tu("năm", "mươi")
    del w["language"]
    a = goi(tmp_path, "50", w, "--json")
    so_loi.chay(a)
    d = json.loads(capsys.readouterr().out)
    assert d["language"] == "vi" and d["match"] == 1.0


def test_cli_thieu_tep_bao_loi(tmp_path):
    a = argparse.Namespace(text=str(tmp_path / "khong-co.txt"), words=str(tmp_path / "w.json"),
                           lang=None, min=0.97, json=False)
    with pytest.raises(LoiKit):
        so_loi.chay(a)


def test_dau_phay_luon_la_thap_phan_kieu_viet():
    assert t("0,125 km") == "không phẩy một hai năm km".split()
    assert t("3,142") == "ba phẩy một bốn hai".split()
    assert t("2,000") == "hai phẩy không không không".split()
    assert t("1.954,5") == "một nghìn chín trăm năm mươi bốn phẩy năm".split()
    assert t("0.125") == "không phẩy một hai năm".split()


def test_ngay_viet_bang_dau_cham():
    assert t("7.5.1954") == "bảy tháng năm năm một nghìn chín trăm năm mươi bốn".split()


def test_json_giong_doc_duoc_nhu_cho_dung_duong_giong():
    # tap/EP001.../dung-duong-giong.py đọc json["results"][0]["words"], mỗi chữ có text/start_ms/end_ms
    import giong
    chu = giong.chu_tu_alignment({"characters": list("a b"), "character_start_times_seconds": [0, 0.1, 0.2],
                                  "character_end_times_seconds": [0.1, 0.2, 0.3]})
    d = {"adapter": "elevenlabs", "results": [{"words": chu}]}
    w = d["results"][0]["words"]
    assert [x["text"] for x in w] == ["a", "b"] and all("start_ms" in x and "end_ms" in x for x in w)
    assert so_loi.doc_chu_nghe(d) == w
