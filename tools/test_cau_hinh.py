"""Test hàm đọc cấu hình máy (tools/cau_hinh.py).

Chạy: python -m pytest tools/test_cau_hinh.py -q -p no:cacheprovider
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cau_hinh  # noqa: E402

MAU = '''# Mẫu
[duong_dan]
output = "D:/Mau/output"   # chú thích cuối dòng
chrome = "C:/Program Files/Google/Chrome/Application/chrome.exe"
teardown = ""
'''


def tao_repo(tmp_path: Path, rieng: str | None) -> Path:
    (tmp_path / "cau-hinh.mau.toml").write_text(MAU, encoding="utf-8")
    if rieng is not None:
        (tmp_path / "cau-hinh.toml").write_text(rieng, encoding="utf-8")
    return tmp_path


def test_doc_toml_phang_bo_chu_thich():
    d = cau_hinh.doc_toml(MAU)
    assert d["duong_dan"]["output"] == "D:/Mau/output"
    assert d["duong_dan"]["teardown"] == ""


def test_dau_thang_trong_chuoi_khong_bi_cat():
    d = cau_hinh.doc_toml('[a]\nx = "D:/kenh #1/ra"  # ghi chu\n')
    assert d["a"]["x"] == "D:/kenh #1/ra"


def test_file_rieng_de_len_mau(tmp_path):
    repo = tao_repo(tmp_path, '[duong_dan]\noutput = "E:/Toi/output"\n')
    assert cau_hinh.duong("output", repo) == Path("E:/Toi/output")
    assert cau_hinh.duong("chrome", repo) == Path("C:/Program Files/Google/Chrome/Application/chrome.exe")


def test_thieu_file_rieng_bao_cach_tao(tmp_path):
    repo = tao_repo(tmp_path, None)
    with pytest.raises(SystemExit, match="cau-hinh.mau.toml"):
        cau_hinh.duong("output", repo)


def test_khoa_rong_bao_ten_khoa(tmp_path):
    repo = tao_repo(tmp_path, '[duong_dan]\noutput = "E:/x"\n')
    with pytest.raises(SystemExit, match="teardown"):
        cau_hinh.duong("teardown", repo)


def test_khoa_khong_co_trong_mau(tmp_path):
    repo = tao_repo(tmp_path, '[duong_dan]\noutput = "E:/x"\n')
    with pytest.raises(SystemExit, match="khong-co"):
        cau_hinh.duong("khong-co", repo)


def test_tim_goc_repo_tu_thu_muc_con(tmp_path):
    repo = tao_repo(tmp_path, '[duong_dan]\noutput = "E:/x"\n')
    con = repo / "tap" / "EP001-x" / "san-xuat"
    con.mkdir(parents=True)
    assert cau_hinh.goc_repo(con / "dung.py") == repo


def test_file_co_bom_va_chu_thich_sau_nhom(tmp_path):
    repo = tao_repo(tmp_path, '\ufeff# lưu bằng Notepad\n[duong_dan]  # nhóm đường dẫn\noutput = "E:/x"\n')
    assert cau_hinh.duong("output", repo) == Path("E:/x")
