"""Test kiểm: đọc kết quả ffmpeg (phần thuần) và chạy thật trên video tự sinh bằng lavfi."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kiem  # noqa: E402
from chung import LoiKit  # noqa: E402

YC = {"lufs": -14.0, "size": "1920x1080", "fps": 24.0, "freeze_min": 2.0, "silence_min": 2.0}


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def do_mau(**k):
    do = {"duration": 100.0, "video": {"width": 1920, "height": 1080, "fps": 24.0, "duration": 100.0},
          "audio": {"duration": 100.0}, "lufs": -14.0, "true_peak": -2.0, "black": [], "frozen": [], "flashes": [], "silences": []}
    do.update(k)
    return do


def ids(do, yc=YC):
    return [(f["id"], f["level"]) for f in kiem.phan_xu(do, yc)]


# --- phần thuần -------------------------------------------------------------------------------------------------------

def test_moc_dinh_dang_phut_giay():
    assert kiem.moc(0) == "0:00.0"
    assert kiem.moc(83.26) == "1:23.3"
    assert kiem.moc(913.0) == "15:13.0"


def test_doc_black_freeze_silence():
    err = ("[blackdetect @ 0x1] black_start:0 black_end:1.5 black_duration:1.5\n"
           "[freezedetect @ 0x2] lavfi.freezedetect.freeze_start: 2.5\n[freezedetect @ 0x2] lavfi.freezedetect.freeze_duration: 3\n"
           "[freezedetect @ 0x2] lavfi.freezedetect.freeze_end: 5.5\n[freezedetect @ 0x2] lavfi.freezedetect.freeze_start: 9\n"
           "[silencedetect @ 0x3] silence_start: 10.2\n[silencedetect @ 0x3] silence_end: 14.1 | silence_duration: 3.9\n"
           "[silencedetect @ 0x3] silence_start: 20\n")
    assert kiem.doc_black(err) == [{"start": 0.0, "end": 1.5, "duration": 1.5}]
    fz = kiem.doc_freeze(err, 12.0)
    assert fz[0] == {"start": 2.5, "end": 5.5, "duration": 3.0}
    assert fz[1] == {"start": 9.0, "end": 12.0, "duration": 3.0}  # đứng hình tới hết file
    sl = kiem.doc_silence(err, 22.0)
    assert sl[0] == {"start": 10.2, "end": 14.1, "duration": 3.9}
    assert sl[1]["end"] == 22.0


def test_doc_yavg_ghep_pts_time():
    out = "frame:0    pts:0       pts_time:0\nlavfi.signalstats.YAVG=16.0\nframe:1    pts:1       pts_time:0.0416667\nlavfi.signalstats.YAVG=235.5\n"
    assert kiem.doc_yavg(out) == [(0.0, 16.0), (0.0416667, 235.5)]


def y(*vals):
    return [(i / 24, float(v)) for i, v in enumerate(vals)]


def test_chop_mot_khung_sang_giua_hai_khung_toi():
    c = kiem.tim_chop(y(100, 100, 100, 240, 100, 100))
    assert len(c) == 1 and c[0]["frames"] == 1 and c[0]["kind"] == "sáng"


def test_chop_hai_khung_van_la_chop_ba_khung_thi_khong():
    assert len(kiem.tim_chop(y(100, 100, 240, 240, 100, 100))) == 1
    assert kiem.tim_chop(y(100, 100, 240, 240, 240, 100, 100)) == []


def test_doi_canh_mot_lan_khong_phai_chop():
    assert kiem.tim_chop(y(100, 100, 100, 240, 240, 240)) == []


def test_probe_xoay_90_doi_chieu_va_bo_luong_bia():
    pj = {"format": {"duration": "10.0"}, "streams": [
        {"codec_type": "video", "codec_name": "mjpeg", "width": 500, "height": 500, "r_frame_rate": "25/1", "disposition": {"attached_pic": 1}},
        {"codec_type": "video", "codec_name": "h264", "width": 1080, "height": 1920, "r_frame_rate": "30000/1001", "side_data_list": [{"rotation": -90}]},
        {"codec_type": "audio", "codec_name": "aac", "duration": "9.9"}]}
    t = kiem.phan_tich_probe(pj)
    assert (t["video"]["width"], t["video"]["height"]) == (1920, 1080)
    assert t["video"]["fps"] == pytest.approx(29.97, abs=0.01)
    assert t["audio"]["duration"] == 9.9


def test_phan_xu_sach_la_ready():
    assert ids(do_mau()) == []
    assert kiem.ket_luan([]) == "ready"


def test_phan_xu_do_to_va_dinh():
    assert ids(do_mau(lufs=-17.0)) == [("loudness", "warn")]
    assert ids(do_mau(lufs=-14.0 + 1.5)) == []  # đúng ngưỡng chưa báo
    assert ids(do_mau(true_peak=-0.5)) == [("peak", "warn")]
    assert ids(do_mau(true_peak=-1.0)) == []


def test_phan_xu_im_lang_hoan_toan_la_loi():
    assert ("silent_sound", "fail") in ids(do_mau(lufs=-70.0))
    assert ("silent_sound", "fail") in ids(do_mau(lufs=float("-inf")))
    assert kiem.ket_luan(kiem.phan_xu(do_mau(lufs=-70.0), YC)) == "not_ready"


def test_phan_xu_khung_den_bo_qua_doan_ngan_sat_dau_cuoi():
    assert ids(do_mau(black=[{"start": 0.0, "end": 0.5, "duration": 0.5}])) == []
    assert ids(do_mau(black=[{"start": 99.6, "end": 100.0, "duration": 0.4}])) == []
    assert ids(do_mau(black=[{"start": 40.0, "end": 40.5, "duration": 0.5}])) == [("black", "warn")]
    assert ids(do_mau(black=[{"start": 0.0, "end": 1.5, "duration": 1.5}])) == [("black", "warn")]


def test_phan_xu_gan_het_la_den_la_loi():
    assert ("all_black", "fail") in ids(do_mau(black=[{"start": 0.0, "end": 95.0, "duration": 95.0}]))


def test_phan_xu_lang_giua_phim_bo_dau_cuoi():
    assert ids(do_mau(silences=[{"start": 0.0, "end": 3.0, "duration": 3.0}])) == []
    assert ids(do_mau(silences=[{"start": 97.0, "end": 100.0, "duration": 3.0}])) == []
    assert ids(do_mau(silences=[{"start": 50.0, "end": 53.0, "duration": 3.0}])) == [("silence", "warn")]


def test_phan_xu_do_dai_hinh_am_lech():
    do = do_mau(audio={"duration": 98.0})
    assert ids(do) == [("sound_short", "warn")]
    assert ids(do_mau(video={"width": 1920, "height": 1080, "fps": 24.0, "duration": 98.0})) == [("picture_short", "warn")]


def test_phan_xu_size_va_fps_la_loi():
    v = {"width": 1280, "height": 720, "fps": 30.0, "duration": 100.0}
    assert set(ids(do_mau(video=v))) == {("size", "fail"), ("fps", "fail")}
    assert ids(do_mau(video={**v, "width": 1920, "height": 1080, "fps": 24.04})) == []


def test_phan_xu_thieu_hinh_va_thieu_am():
    assert ("no_picture", "fail") in ids(do_mau(video=None))
    assert ids(do_mau(audio=None, lufs=None, true_peak=None)) == [("no_sound", "warn")]


def test_dinh_dang_khuon_chu_cho_soi_qc():
    do = do_mau(black=[{"start": 72.3, "end": 74.0, "duration": 1.7}])
    f = kiem.phan_xu(do, YC)
    chu = kiem.dinh_dang("v.mp4", kiem.ket_luan(f), do, f)
    dong = chu.splitlines()
    assert dong[0].startswith("! 1 ")
    assert dong[1].strip().startswith("1920×1080 24 fps · 100.0 s · -14.0 LUFS")
    assert dong[2].startswith("! khung đen 1:12.3")
    f_loi = kiem.phan_xu(do_mau(lufs=-70.0), YC)
    assert kiem.dinh_dang("v.mp4", "not_ready", do_mau(lufs=-70.0), f_loi).splitlines()[0].startswith("✗")


# --- soi-qc đọc được cả ! và ✗ ----------------------------------------------------------------------------------------

def nap_soi_qc():
    import importlib.util
    goc = Path(__file__).resolve().parents[2]
    # repo chủ kit: tap/EP001-…; kit hội viên: mau/dien-bien-phu-1954
    p = next(q for q in (goc / "tap" / "EP001-dien-bien-phu-1954" / "san-xuat" / "soi-qc.py",
                         goc / "mau" / "dien-bien-phu-1954" / "san-xuat" / "soi-qc.py") if q.exists())
    sys.path.insert(0, str(p.parent))
    spec = importlib.util.spec_from_file_location("soi_qc", p)
    m = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)
    except SystemExit as e:  # script tập mẫu đọc cau-hinh.toml lúc nạp (có sau K1)
        pytest.skip(f"chưa có cau-hinh.toml: {e}")
    return m


def test_soi_qc_tra_ca_dong_loi_va_canh_bao(tmp_path):
    soi = nap_soi_qc()
    check = tmp_path / "check.txt"
    check.write_text("! 2 điều cần xem: v.mp4\n  1920×1080 24 fps\n! khung đen 1:12.3–1:14.0 (1.7 s)  → soi\n✗ cỡ hình sai 2:00.0  → x\n", encoding="utf-8")
    pc = {"canh": [{"id": "C1", "t0": 0.0, "t1": 100.0, "nguon": "n", "hinh": "h"}, {"id": "C2", "t0": 100.0, "t1": 300.0, "nguon": "n", "hinh": "h"}]}
    ra = tmp_path / "ra.md"
    assert soi.tra_canh(check, pc, ra) == 2


# --- tích hợp ---------------------------------------------------------------------------------------------------------

def args_kiem(f, **k):
    d = dict(video=str(f), lufs=-14.0, size=None, fps=None, freeze_min=2.0, silence_min=2.0, json=True)
    d.update(k)
    return argparse.Namespace(**d)


def kiem_json(f, capsys, **k):
    assert kiem.chay(args_kiem(f, **k)) == 0
    return json.loads(capsys.readouterr().out)


def test_kiem_that_video_hop_le(tmp_path, capsys):
    f = tmp_path / "ok.mp4"
    ffmpeg("-f", "lavfi", "-i", "testsrc=s=320x180:r=24:d=4", "-f", "lavfi", "-i", "sine=f=440:d=4:sample_rate=48000", "-af", "volume=-12dB",
           "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", str(f))
    kq = kiem_json(f, capsys, size="320x180", fps=24.0)
    assert kq["streams"]["video"]["width"] == 320
    assert kq["measured"]["lufs"] is not None and kq["measured"]["true_peak"] < 0
    assert not [x for x in kq["findings"] if x["level"] == "fail"]


def test_kiem_that_bat_khung_den_dung_hinh_va_lang(tmp_path, capsys):
    f = tmp_path / "xau.mp4"
    ffmpeg("-f", "lavfi", "-i", "color=c=black:s=320x180:r=24:d=3", "-f", "lavfi", "-i", "color=c=red:s=320x180:r=24:d=4",
           "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo:d=7",
           "-filter_complex", "[0][1]concat=n=2:v=1:a=0[v]", "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-preset", "ultrafast",
           "-pix_fmt", "yuv420p", "-c:a", "aac", str(f))
    kq = kiem_json(f, capsys, size="640x360")
    ids_ = {x["id"] for x in kq["findings"]}
    assert {"black", "frozen", "silent_sound", "size"} <= ids_ or {"all_black", "frozen", "silent_sound", "size"} <= ids_
    assert kq["verdict"] == "not_ready"


def test_kiem_that_bat_khung_chop(tmp_path, capsys):
    f = tmp_path / "chop.mp4"
    ffmpeg("-f", "lavfi", "-i", "color=c=0x606060:s=320x180:r=24:d=1", "-f", "lavfi", "-i", "color=c=white:s=320x180:r=24:d=1",
           "-f", "lavfi", "-i", "color=c=0x606060:s=320x180:r=24:d=1",
           "-filter_complex", "[1]trim=end_frame=1,setpts=PTS-STARTPTS[w];[0][w][2]concat=n=3:v=1:a=0[v]", "-map", "[v]",
           "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-qp", "0", str(f))
    kq = kiem_json(f, capsys)
    assert any(x["id"] == "flash" for x in kq["findings"])
    assert kq["streams"]["audio"] is None


def test_kiem_chu_in_ra_doc_duoc_va_khong_co_file_la_loi(tmp_path, capsys):
    with pytest.raises(LoiKit):
        kiem.chay(args_kiem(tmp_path / "khong-co.mp4"))
    f = tmp_path / "a.mp4"
    ffmpeg("-f", "lavfi", "-i", "testsrc=s=320x180:r=24:d=2", "-f", "lavfi", "-i", "sine=d=2", "-c:v", "libx264", "-preset", "ultrafast",
           "-pix_fmt", "yuv420p", "-c:a", "aac", str(f))
    kiem.chay(args_kiem(f, json=False))
    chu = capsys.readouterr().out
    assert re.match(r"^(✓|!|✗) ", chu)
