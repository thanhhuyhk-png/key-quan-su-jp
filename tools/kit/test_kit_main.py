"""Test cổng vào kit.py: không cần requests cho lệnh không cần mạng, mã hoá stdout, lỗi hệ thống thành câu hướng dẫn."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))
import kit  # noqa: E402
import tron  # noqa: E402


def chay_kit(*tham_so, env_them=None, truoc=""):
    env = {**os.environ, **(env_them or {})}
    ma = f"{truoc}import sys; sys.path.insert(0, {str(KIT)!r}); import kit; sys.exit(kit.main({list(tham_so)!r}))"
    return subprocess.run([sys.executable, "-c", ma], capture_output=True, env=env)


def test_lenh_khong_can_mang_chay_duoc_khi_thieu_requests():
    r = chay_kit("kiem", "-h", truoc="sys = __import__('sys'); sys.modules['requests'] = None\n")
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    assert "kiem" in r.stdout.decode("utf-8", "replace")


def test_lenh_goi_mang_thieu_requests_bao_cach_cai(monkeypatch):
    import giong
    monkeypatch.setitem(sys.modules, "requests", None)
    with pytest.raises(giong.LoiKit, match=r"pip install -r requirements\.txt"):
        giong.gui_http("GET", "http://127.0.0.1:9/x", headers={})


def test_stdout_cp1252_van_in_duoc_dau_tich(tmp_path):
    (tmp_path / "loi.txt").write_text("một hai", encoding="utf-8")
    (tmp_path / "w.json").write_text(json.dumps({"words": [{"text": "một", "start_ms": 0, "end_ms": 1},
                                                           {"text": "hai", "start_ms": 1, "end_ms": 2}]}), encoding="utf-8")
    r = chay_kit("so-loi", "--text", str(tmp_path / "loi.txt"), "--words", str(tmp_path / "w.json"),
                 env_them={"PYTHONIOENCODING": "cp1252:strict", "PYTHONUTF8": "0"})
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    assert "✓".encode("utf-8") in r.stdout


@pytest.mark.parametrize("loi", [PermissionError(13, "Permission denied"), ValueError("xấu"), TypeError("kiểu"), KeyError("k")])
def test_loi_he_thong_thanh_cau_huong_dan_khong_traceback(monkeypatch, capsys, loi):
    def hong(a):
        raise loi
    monkeypatch.setattr(tron, "chay", hong)
    assert kit.main(["tron", "x.json", "--out", "y.wav"]) == 1
    err = capsys.readouterr().err
    assert err.startswith("Lỗi") and "Traceback" not in err
