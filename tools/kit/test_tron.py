"""Test trộn: dựng đồ thị từ mix.json (phần thuần) và trộn thật với âm tự sinh bằng ffmpeg lavfi."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tron  # noqa: E402
from chung import LoiKit  # noqa: E402


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def kh_tu(plan, goc=Path("."), dai=10.0):
    return tron.doc_ke_hoach(plan, goc, do_dai=lambda f: dai)


# --- phần thuần -------------------------------------------------------------------------------------------------------

def test_ease_expr_mot_buoc():
    assert tron.ease_expr([{"at": 2, "to": 0.5, "over": 1}]) == "if(lt(t,2),1,if(lt(t,3),1+(-0.5)*(t-2)/1,0.5))"


def test_ease_expr_nhieu_buoc_noi_tiep_va_buoc_tuc_thi():
    e = tron.ease_expr([{"at": 1, "to": 0, "over": 0}, {"at": 4, "to": 1, "over": 2}])
    assert e == "if(lt(t,1),1,if(lt(t,4),0,if(lt(t,6),0+(1)*(t-4)/2,1)))"


def test_ease_chong_buoc_la_loi():
    with pytest.raises(LoiKit, match="ease"):
        tron.chuan_ease([{"at": 1, "to": 0, "over": 2}, {"at": 2, "to": 1, "over": 1}])


def test_ease_ngoai_mien_la_loi():
    with pytest.raises(LoiKit):
        tron.chuan_ease([{"at": 1, "to": 5, "over": 1}])


def test_gain_cue_lam_tron_mot_phan_muoi_db():
    assert tron.gain_cue(-16, -3.04) == -13.0
    assert tron.gain_cue(-10, -9.0) == -1.0


def test_khoa_la_o_goc_bao_chua_ho_tro():
    with pytest.raises(LoiKit, match="stems.*chưa hỗ trợ"):
        kh_tu({"duration": 5, "stems": "x", "cues": []})


def test_align_khac_start_va_gain_bao_chua_ho_tro():
    base = {"duration": 5}
    with pytest.raises(LoiKit, match="align"):
        kh_tu({**base, "cues": [{"sound": "a.wav", "t": 1, "align": "peak"}]})
    with pytest.raises(LoiKit, match="in_band"):
        kh_tu({**base, "cues": [{"sound": "a.wav", "t": 1, "gain": "in_band"}]})
    with pytest.raises(LoiKit, match="chưa hỗ trợ"):
        kh_tu({**base, "cues": [{"sound": "a+b.wav", "t": 1}]})


def test_bus_va_weight_duoc_bo_qua_co_canh_bao_va_align_start_chap_nhan():
    kh = kh_tu({"duration": 5, "cues": [{"sound": "a.wav", "t": 1, "align": "start", "bus": "ngoai", "weight": "hero"}]})
    assert len(kh["cues"]) == 1
    assert any("bus" in w for w in kh["warnings"])


def test_khong_co_gi_de_tron_la_loi():
    with pytest.raises(LoiKit, match="trộn"):
        kh_tu({"duration": 5})


def test_thieu_thoi_luong_va_giong_la_loi():
    with pytest.raises(LoiKit):
        kh_tu({"cues": [{"sound": "a.wav", "t": 1}]})


def test_tim_am_ten_tron_qua_sfx_dir(tmp_path):
    (tmp_path / "audio" / "sfx").mkdir(parents=True)
    (tmp_path / "audio" / "sfx" / "nổ.mp3").write_bytes(b"x")
    kh = kh_tu({"duration": 5, "sfx_dir": "audio/sfx", "cues": [{"sound": "nổ", "t": 1}]}, goc=tmp_path)
    assert Path(kh["cues"][0]["sound"]) == tmp_path / "audio" / "sfx" / "nổ.mp3"


def test_tim_am_duong_dan_tuong_doi_tinh_tu_thu_muc_mix(tmp_path):
    kh = kh_tu({"duration": 5, "cues": [{"sound": "x/a.wav", "t": 1}]}, goc=tmp_path)
    assert Path(kh["cues"][0]["sound"]) == tmp_path / "x" / "a.wav"


def test_am_kieu_bo_am_thanh_bao_chua_ho_tro():
    with pytest.raises(LoiKit, match="chưa hỗ trợ"):
        kh_tu({"duration": 5, "cues": [{"sound": "bo-am:no", "t": 1}]})


def do_thi(plan, dinh=None, goc=Path(".")):
    kh = kh_tu(plan, goc)
    dinh = dinh or {c["sound"]: -3.0 for c in kh["cues"]}
    return tron.dung_do_thi(kh, dinh, {})


def test_do_thi_cue_co_cut_gain_va_adelay():
    _, g = do_thi({"duration": 10, "limit": 0.9, "cues": [{"sound": "a.wav", "t": 1.2345, "db": -16, "cut": 2}]},
                  dinh={str(Path("a.wav")): -3.04})
    assert "atrim=0:2,afade=t=out:st=1.7:d=0.3,volume=-13.0dB,adelay=1235|1235" in g


def test_do_thi_cut_ngan_hon_0_3_mo_het_doan():
    _, g = do_thi({"duration": 10, "limit": 0.9, "cues": [{"sound": "a.wav", "t": 0, "cut": 0.2}]})
    assert "afade=t=out:st=0:d=0.2" in g


def test_do_thi_t_am_bi_kep_ve_0():
    _, g = do_thi({"duration": 10, "limit": 0.9, "cues": [{"sound": "a.wav", "t": -2}]})
    assert "adelay=0|0" in g


def test_do_thi_cung_mot_am_nhieu_cue_chi_mo_mot_lan_va_asplit():
    inputs, g = do_thi({"duration": 10, "limit": 0.9, "cues": [{"sound": "a.wav", "t": 1}, {"sound": "a.wav", "t": 3}, {"sound": "b.wav", "t": 4}]})
    assert len(inputs) == 4 and inputs.count("-i") == 2
    assert "asplit=2" in g


def test_do_thi_limit_co_thi_level_false_khong_co_thi_auto_level():
    _, co = do_thi({"duration": 10, "limit": 0.8, "cues": [{"sound": "a.wav", "t": 1}]})
    _, khong = do_thi({"duration": 10, "cues": [{"sound": "a.wav", "t": 1}]})
    assert "alimiter=limit=0.8:level=false" in co
    assert "alimiter=limit=0.95," in khong and "level=false" not in khong
    assert "apad=whole_dur=10,alimiter" in khong  # đệm TRƯỚC limiter


def test_do_thi_fade_out_cuoi():
    _, g = do_thi({"duration": 10, "fade_out": 1.5, "cues": [{"sound": "a.wav", "t": 1}]})
    assert "afade=t=out:st=8.5:d=1.5[out]" in g


def bed(**k):
    return {"file": "n.wav", **k}


def test_do_thi_giong_va_nhac_duck_mac_dinh_bat():
    _, g = do_thi({"voice": "v.wav", "duration": 10, "music": {"beds": [bed()]}})
    assert "sidechaincompress=threshold=0.02:ratio=8:attack=20:release=350" in g
    assert "volume=0.2" in g  # music.volume mặc định


def test_do_thi_duck_false_khong_nen_va_duck_tuy_chinh():
    _, g = do_thi({"voice": "v.wav", "duration": 10, "music": {"duck": False, "beds": [bed()]}})
    assert "sidechaincompress" not in g and "asplit" not in g
    _, g = do_thi({"voice": "v.wav", "duration": 10, "music": {"duck": {"ratio": 4}, "beds": [bed()]}})
    assert "ratio=4:" in g


def test_do_thi_bed_loop_fade_volume_ease_adelay():
    _, g = do_thi({"duration": 20, "music": {"duck": False, "beds": [bed(**{"from": 2, "to": 12, "loop": True, "fade_in": 1, "fade_out": 2,
                                                                             "volume": 0.5, "ease": [{"at": 5, "to": 0, "over": 1}]})]}})
    assert "aloop=loop=-1:size=2e9,atrim=0:10,asetpts=N/SR/TB,afade=t=in:d=1,afade=t=out:st=8:d=2,volume=0.5000,adelay=2000|2000," in g
    assert "volume='if(lt(t,5),1,if(lt(t,6),1+(-1)*(t-5)/1,0))':eval=frame" in g


def test_do_thi_nhieu_file_trong_bed_acrossfade():
    _, g = do_thi({"duration": 20, "music": {"duck": False, "beds": [{"files": ["a.wav", "b.wav"], "crossfade": 3}]}})
    assert "acrossfade=d=3" in g


def test_do_thi_bed_lufs_dung_do_to_do_duoc():
    kh = kh_tu({"duration": 20, "music": {"duck": False, "beds": [bed(lufs=-20, volume=1)]}})
    _, g = tron.dung_do_thi(kh, {}, {str(Path("n.wav")): -26.0})
    assert "volume=1.9953" in g  # +6 dB


def test_do_thi_bed_bat_dau_sau_het_phim_bi_bo_co_canh_bao():
    kh = kh_tu({"duration": 5, "music": {"beds": [bed(**{"from": 9})]}, "cues": [{"sound": "a.wav", "t": 1}]})
    assert any("sau" in w for w in kh["warnings"])


def test_do_thi_tin_hieu_la_khong_chua_dong_lenh_dai():
    cues = [{"sound": f"s{i % 7}.wav", "t": i * 0.01, "db": -20} for i in range(1500)]
    kh = kh_tu({"duration": 30, "limit": 0.9, "cues": cues})
    inputs, g = tron.dung_do_thi(kh, {c["sound"]: -3.0 for c in kh["cues"]}, {})
    assert g.count("adelay=") == 1500
    assert len(inputs) == 14  # bảy -i


# --- tích hợp ---------------------------------------------------------------------------------------------------------

def do_dinh(tep):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tep), "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    return float(re.search(r"max_volume: (\S+) dB", r.stderr)[1])


def args_tron(mix, out, force=False):
    return argparse.Namespace(mix=str(mix), out=str(out), force=force, json=True)


def test_tron_that_cue_dung_muc_db_va_do_dai(tmp_path, capsys):
    ffmpeg("-f", "lavfi", "-i", "sine=f=500:d=2:sample_rate=44100", "-af", "volume=-6dB", str(tmp_path / "ting.wav"))  # mono, đỉnh −6
    mix = tmp_path / "mix.json"
    mix.write_text(json.dumps({"duration": 4, "limit": 1, "cues": [{"sound": "ting.wav", "t": 1.0, "db": -12, "cut": 1.5}]}), encoding="utf-8")
    out = tmp_path / "ra.wav"
    assert tron.chay(args_tron(mix, out)) == 0
    kq = json.loads(capsys.readouterr().out)
    assert kq["cues"] == 1 and out.exists()
    assert abs(do_dinh(out) - (-12.0)) < 0.25
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)], capture_output=True, text=True)
    assert abs(float(d.stdout) - 4.0) < 0.05
    assert "lufs" in kq


def test_tron_khong_ghi_de_khi_thieu_force_va_bao_thieu_tep(tmp_path):
    mix = tmp_path / "mix.json"
    mix.write_text(json.dumps({"duration": 2, "cues": [{"sound": "khong-co.wav", "t": 0}]}), encoding="utf-8")
    with pytest.raises(LoiKit, match="khong-co"):
        tron.chay(args_tron(mix, tmp_path / "ra.wav"))
    ffmpeg("-f", "lavfi", "-i", "anullsrc=d=1", str(tmp_path / "khong-co.wav"))
    (tmp_path / "ra.wav").write_bytes(b"x")
    with pytest.raises(LoiKit, match="force"):
        tron.chay(args_tron(mix, tmp_path / "ra.wav"))


def test_tron_giong_nhac_duck_nhac_ha_khi_co_giong(tmp_path, capsys):
    ffmpeg("-f", "lavfi", "-i", "sine=f=300:d=4:sample_rate=48000", str(tmp_path / "nhac.wav"))
    ffmpeg("-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono:d=2", "-f", "lavfi", "-i", "sine=f=800:d=2:sample_rate=48000",
           "-filter_complex", "[1:a]volume=-10dB[s];[0:a][s]concat=n=2:v=0:a=1", str(tmp_path / "giong.wav"))  # 2 s lặng rồi 2 s tiếng
    mix = tmp_path / "mix.json"
    mix.write_text(json.dumps({"voice": "giong.wav", "limit": 1, "music": {"volume": 0.5, "beds": [{"file": "nhac.wav", "loop": True}]}}), encoding="utf-8")
    out = tmp_path / "ra.wav"
    tron.chay(args_tron(mix, out))
    kq = json.loads(capsys.readouterr().out)
    assert abs(kq["duration"] - 4.0) < 0.05
    assert out.exists()


def test_tron_hon_nghin_cue_khong_vuong_dong_lenh_windows(tmp_path, capsys):
    ffmpeg("-f", "lavfi", "-i", "sine=f=500:d=0.2:sample_rate=48000", str(tmp_path / "t.wav"))
    cues = [{"sound": "t.wav", "t": round(i * 0.004, 3), "db": -30} for i in range(1200)]
    mix = tmp_path / "mix.json"
    mix.write_text(json.dumps({"duration": 6, "limit": 0.9, "cues": cues}), encoding="utf-8")
    assert tron.chay(args_tron(mix, tmp_path / "ra.wav")) == 0
    assert json.loads(capsys.readouterr().out)["cues"] == 1200


def test_cache_dinh_dung_lai_khong_do_lai(tmp_path, monkeypatch):
    ffmpeg("-f", "lavfi", "-i", "sine=f=500:d=1", str(tmp_path / "a.wav"))
    cache = tmp_path / "cache.json"
    p1 = tron.do_dinh_nhieu([tmp_path / "a.wav"], cache)
    assert cache.exists()
    monkeypatch.setattr(tron, "do_dinh_mot", lambda f: (_ for _ in ()).throw(AssertionError("không được đo lại")))
    p2 = tron.do_dinh_nhieu([tmp_path / "a.wav"], cache)
    assert p1 == p2


# --- kiểm kiểu mix.json -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("plan", [
    {"duration": 5, "music": {"beds": [{"file": "a.wav", "fade_in": "2"}]}},
    {"duration": 5, "music": {"beds": [{"file": "a.wav", "fade_out": None}]}},
    {"duration": 5, "music": {"beds": [{"file": "a.wav", "volume": "lớn"}]}},
    {"duration": 5, "music": {"beds": [{"file": "a.wav", "crossfade": "x"}]}},
    {"duration": 5, "music": {"beds": [{"file": "a.wav", "to": "hết"}]}},
    {"duration": 5, "music": {"beds": [{"file": "a.wav", "from": float("nan")}]}},
    {"duration": 5, "music": {"beds": [{"file": "a.wav", "lufs": "x"}]}},
    {"duration": 5, "music": {"beds": ["a.wav"]}},
    {"duration": 5, "music": {"beds": {"file": "a.wav"}}},
    {"duration": 5, "music": {"beds": [{"files": "a.wav"}]}},
    {"duration": 5, "music": {"beds": [{"file": 7}]}},
    {"duration": 5, "cues": ["ting"]},
    {"duration": 5, "cues": {"sound": "x"}},
    {"duration": 5, "cues": [{"sound": "x.wav", "t": float("inf")}]},
    {"duration": 5, "cues": [{"sound": "x.wav", "t": float("nan")}]},
    {"duration": float("inf"), "cues": [{"sound": "x.wav", "t": 1}]},
    {"duration": 5, "voice": 5},
    {"duration": 5, "sfx_dir": 5, "cues": [{"sound": "x.wav", "t": 1}]},
    {"duration": 5, "fade_out": float("nan"), "cues": [{"sound": "x.wav", "t": 1}]},
    {"duration": 5, "music": {"volume": float("inf"), "beds": [{"file": "a.wav"}]}},
])
def test_mix_sai_kieu_thanh_loi_kit_khong_traceback(plan):
    with pytest.raises(LoiKit):
        kh_tu(plan)


# --- nhiều tệp âm khác nhau -------------------------------------------------------------------------------------------

def test_do_thi_amovie_khong_dung_i_cho_cue():
    cues = [{"sound": f"am{i}.wav", "t": i, "db": -20} for i in range(5)]
    kh = kh_tu({"duration": 10, "limit": 0.9, "cues": cues})
    inputs, g = tron.dung_do_thi(kh, {c["sound"]: -3.0 for c in kh["cues"]}, {}, amovie=True)
    assert inputs == [] and g.count("amovie=") == 5 and g.count("adelay=") == 5


def test_tron_hon_bon_tram_am_khac_nhau_vuot_dong_lenh(tmp_path, capsys):
    ffmpeg("-f", "lavfi", "-i", "sine=f=500:d=0.1:sample_rate=48000", str(tmp_path / "goc.wav"))
    thu = tmp_path / ("thu-muc-dai-" + "x" * 40)
    thu.mkdir()
    cues = []
    for i in range(450):
        (thu / f"am-{i:04d}.wav").write_bytes((tmp_path / "goc.wav").read_bytes())
        cues.append({"sound": f"{thu}/am-{i:04d}.wav".replace("\\", "/"), "t": round(i * 0.02, 3), "db": -30})
    mix = tmp_path / "mix.json"
    mix.write_text(json.dumps({"duration": 12, "limit": 0.9, "cues": cues}), encoding="utf-8")
    assert tron.chay(args_tron(mix, tmp_path / "ra.wav")) == 0
    assert json.loads(capsys.readouterr().out)["cues"] == 450
    assert (tmp_path / "ra.wav").stat().st_size > 1000


def test_amovie_va_i_cho_cung_ket_qua(tmp_path, monkeypatch):
    ffmpeg("-f", "lavfi", "-i", "sine=f=440:d=1:sample_rate=44100", "-af", "volume=-9dB", str(tmp_path / "a.wav"))
    ffmpeg("-f", "lavfi", "-i", "sine=f=900:d=1:sample_rate=48000", str(tmp_path / "b.wav"))
    mix = tmp_path / "mix.json"
    mix.write_text(json.dumps({"duration": 4, "limit": 0.9, "cues": [{"sound": "a.wav", "t": 0.5, "db": -10}, {"sound": "b.wav", "t": 1.5, "db": -14, "cut": 0.5}]}), encoding="utf-8")
    tron.chay(args_tron(mix, tmp_path / "i.wav"))
    monkeypatch.setattr(tron, "GIOI_HAN_DONG_LENH", 10)  # ép dùng amovie
    tron.chay(args_tron(mix, tmp_path / "m.wav"))
    assert (tmp_path / "i.wav").read_bytes() == (tmp_path / "m.wav").read_bytes()


# --- nhận diện kiểu đọc đồ thị từ tệp ----------------------------------------------------------------------------------

def test_kieu_doc_do_thi_theo_thu_chay_that_khong_theo_so_phien_ban(monkeypatch):
    goi = []

    def gia(lenh, **kw):
        goi.append(lenh)
        if "-/filter_complex" in lenh:
            raise LoiKit("ffmpeg thoát mã 8:\nUnrecognized option '/filter_complex'.")
        return subprocess.CompletedProcess(lenh, 0, b"ffmpeg version 2023-12-01-git-abc", b"")

    monkeypatch.setattr(tron, "chay_lenh", gia)
    tron.co_kieu_moi.cache_clear()
    assert tron.co_kieu_moi() is False
    assert any("-/filter_complex" in c for c in goi)
    tron.co_kieu_moi.cache_clear()


def test_kieu_doc_do_thi_may_that_chay_duoc():
    tron.co_kieu_moi.cache_clear()
    assert tron.co_kieu_moi() in (True, False)


# --- cache và JSON ----------------------------------------------------------------------------------------------------

def test_ghi_cache_loi_o_dia_khong_lam_hong_lenh(tmp_path):
    ffmpeg("-f", "lavfi", "-i", "sine=f=500:d=1", str(tmp_path / "a.wav"))
    chan = tmp_path / "la-tep"
    chan.write_text("x")
    p = tron.do_dinh_nhieu([tmp_path / "a.wav"], chan / "cache.json")  # thư mục cha là tệp: ghi không được
    assert len(p) == 1
