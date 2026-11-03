"""Test master/ghép: đọc kết quả ebur128, số học gain, và chạy thật với âm/hình tự sinh bằng ffmpeg."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import am_cuoi  # noqa: E402
from chung import LoiKit  # noqa: E402

TOM_TAT = """
[Parsed_ebur128_0 @ 000001] Summary:

  Integrated loudness:
    I:         -23.4 LUFS
    Threshold: -33.5 LUFS

  Loudness range:
    LRA:         5.1 LU

  True peak:
    Peak:       -1.2 dBFS
"""


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def test_doc_ebur128_lay_I_va_dinh():
    r = am_cuoi.doc_ebur128(TOM_TAT)
    assert r == {"I": -23.4, "dinh": -1.2}


def test_doc_ebur128_chi_lay_sau_summary():
    chu = "I:  -5.0 LUFS\nPeak: -0.1 dBFS\n" + TOM_TAT
    assert am_cuoi.doc_ebur128(chu)["I"] == -23.4


def test_doc_ebur128_cam_hoan_toan_la_vo_cung():
    chu = "Summary:\n  I:  -inf LUFS\n  Peak:  -inf dBFS\n"
    r = am_cuoi.doc_ebur128(chu)
    assert r["I"] == float("-inf") and r["dinh"] == float("-inf")


def test_doc_ebur128_khong_co_tom_tat_thi_loi():
    with pytest.raises(LoiKit):
        am_cuoi.doc_ebur128("không có gì")


def test_gain_toi_dich_va_tran_limiter():
    assert am_cuoi.gain_toi_dich(-20.0, -14.0) == 6.0
    assert am_cuoi.tran_limiter(-3.0) == pytest.approx(0.7079, abs=1e-4)
    assert am_cuoi.tran_limiter(0.0) == 1.0


def test_tran_limiter_ngoai_mien_thi_loi():
    with pytest.raises(LoiKit):
        am_cuoi.tran_limiter(-30.0)  # alimiter chỉ nhận 0,0625..1
    with pytest.raises(LoiKit):
        am_cuoi.tran_limiter(1.0)


def test_lenh_ghep_copy_hinh_va_ma_hoa_am():
    lenh = am_cuoi.lenh_ghep("v.mp4", "a.wav", "r.mp4", "aac_mf")
    assert lenh[lenh.index("-c:v") + 1] == "copy"
    assert lenh[lenh.index("-c:a") + 1] == "aac_mf"
    assert lenh[lenh.index("-b:a") + 1] == "256k"


@pytest.fixture
def am_sine(tmp_path):
    p = tmp_path / "mix.wav"
    ffmpeg("-f", "lavfi", "-i", "sine=f=440:d=6:sample_rate=48000", "-af", "volume=-20dB", "-ac", "2", str(p))
    return p


def args_master(am, ra, lufs=-14.0, tp=-3.0, force=False, json_=False):
    return argparse.Namespace(am=str(am), ra=str(ra), lufs=lufs, tp=tp, force=force, json=json_)


def test_master_dua_ve_lufs_dich_va_ton_trong_tran(am_sine, tmp_path, capsys):
    ra = tmp_path / "master.wav"
    assert am_cuoi.chay_master(args_master(am_sine, ra, json_=True)) == 0
    kq = json.loads(capsys.readouterr().out)
    assert abs(kq["I"] - (-14.0)) < 0.3
    assert kq["dinh"] <= -3.0 + 0.2
    assert ra.exists()


def test_master_tran_thap_bi_chan_dinh(am_sine, tmp_path, capsys):
    ra = tmp_path / "master.wav"
    am_cuoi.chay_master(args_master(am_sine, ra, tp=-18.0, json_=True))
    kq = json.loads(capsys.readouterr().out)
    assert kq["dinh"] <= -18.0 + 0.3
    assert kq["I"] < -14.5  # bị chặn nên không tới đích; lệnh báo thật, không giả


def test_master_khong_ghi_de_khi_thieu_force(am_sine, tmp_path):
    ra = tmp_path / "master.wav"
    ra.write_bytes(b"x")
    with pytest.raises(LoiKit):
        am_cuoi.chay_master(args_master(am_sine, ra))


def test_ghep_giu_hinh_va_do_lai_tren_mp4(am_sine, tmp_path, capsys):
    hinh = tmp_path / "v.mp4"
    ffmpeg("-f", "lavfi", "-i", "testsrc=s=320x180:r=24:d=6", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", str(hinh))
    master = tmp_path / "master.wav"
    am_cuoi.chay_master(args_master(am_sine, master))
    capsys.readouterr()
    ra = tmp_path / "final.mp4"
    a = argparse.Namespace(hinh=str(hinh), am=str(master), ra=ra, force=False, json=True)
    a.ra = str(ra)
    assert am_cuoi.chay_ghep(a) == 0
    kq = json.loads(capsys.readouterr().out)
    assert kq["ma_hoa_am"] in ("aac_mf", "aac")
    assert abs(kq["I"] - (-14.0)) < 0.5
    assert kq["dinh"] < -1.0
    pr = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name", "-of", "csv=p=0", str(ra)], capture_output=True, text=True)
    assert "h264" in pr.stdout
