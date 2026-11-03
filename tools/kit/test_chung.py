"""Test phần dùng chung: đọc tệp khoá, thiếu khoá, ghi nguyên tử."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import LoiKit, co_khoa, doc_tep_khoa, ghi_nguyen_tu, khoa  # noqa: E402


def test_doc_tep_khoa_bo_chu_thich_ngoac_va_bom():
    chu = '\ufeff# chú thích\nA_KEY="gia tri"\n\nexport B_KEY=b\nhong\n'
    assert doc_tep_khoa(chu) == {"A_KEY": "gia tri", "B_KEY": "b"}


def test_khoa_uu_tien_bien_moi_truong(tmp_path, monkeypatch):
    tep = tmp_path / "k"
    tep.write_text("X_KEY=tu-tep\n", encoding="utf-8")
    monkeypatch.setenv("X_KEY", "tu-moi-truong")
    assert khoa("X_KEY", tep) == "tu-moi-truong"


def test_khoa_doc_tu_tep_khi_khong_co_bien(tmp_path, monkeypatch):
    tep = tmp_path / "k"
    tep.write_text("X_KEY=tu-tep\n", encoding="utf-8")
    monkeypatch.delenv("X_KEY", raising=False)
    assert khoa("X_KEY", tep) == "tu-tep"


def test_thieu_khoa_bao_cach_them_ma_khong_lo_gia_tri(tmp_path, monkeypatch):
    monkeypatch.delenv("Y_KEY", raising=False)
    with pytest.raises(LoiKit, match="thiếu khoá Y_KEY"):
        khoa("Y_KEY", tmp_path / "khong-co")
    assert co_khoa("Y_KEY", tmp_path / "khong-co") is False


def test_ghi_nguyen_tu_doi_ten_khi_xong_va_don_tep_tam_khi_loi(tmp_path):
    dich = tmp_path / "ra.txt"
    with ghi_nguyen_tu(dich) as tam:
        tam.write_text("1", encoding="utf-8")
    assert dich.read_text(encoding="utf-8") == "1"
    with pytest.raises(RuntimeError):
        with ghi_nguyen_tu(dich) as tam:
            tam.write_text("2", encoding="utf-8")
            raise RuntimeError
    assert dich.read_text(encoding="utf-8") == "1" and not tam.exists()
    with pytest.raises(LoiKit, match="--force"):
        with ghi_nguyen_tu(dich, ghi_de=False):
            pass


def test_json_an_toan_doi_vo_cuc_va_nan_thanh_null():
    import json
    from chung import json_an_toan
    d = {"a": float("-inf"), "b": [1.5, float("nan"), float("inf")], "c": {"d": "x"}}
    assert json_an_toan(d) == {"a": None, "b": [1.5, None, None], "c": {"d": "x"}}
    json.loads(json.dumps(json_an_toan(d), allow_nan=False))  # không còn -Infinity/NaN


def test_import_chung_ngoai_repo_bao_loi_ro(tmp_path):
    import subprocess
    lon = tmp_path / "a" / "b"
    lon.mkdir(parents=True)
    (lon / "chung.py").write_text((Path(__file__).resolve().parent / "chung.py").read_text(encoding="utf-8"), encoding="utf-8")
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", "-c", f"import sys; sys.path.insert(0, {str(lon)!r}); import chung"], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode != 0
    assert "cau-hinh.mau.toml" in r.stderr and "StopIteration" not in r.stderr
