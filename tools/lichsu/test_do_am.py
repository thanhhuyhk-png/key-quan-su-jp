import importlib.util
import json
import wave
from pathlib import Path

import numpy as np
import pytest

_spec = importlib.util.spec_from_file_location("do_am", Path(__file__).with_name("do-am.py"))
da = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(da)

N = 600
CHUONG = [0, 180, 380]


def kl(kq, tu):
    return next(c["ket_luan"] for c in kq["chi_so"] if c["ten"].startswith(tu))


def phim(nhac_noi_db, nhac_khe_db, tat_o=(), kin=False):
    """Giọng nói 8 s rồi nghỉ 3 s; nhạc `nhac_noi_db` dB khi có lời, `nhac_khe_db` ở khe; `tat_o` = (bắt đầu, dài) nhạc tắt."""
    v = np.full(N, -90.0)
    m = np.full(N, nhac_noi_db)
    for i in range(10, N - 10):  # 10 s đầu và cuối không lời: hook và đuôi
        if (i - 10) % 11 < 8:
            v[i] = -15.0
        elif not kin:
            m[i] = nhac_khe_db
    m[:10] = nhac_khe_db
    for b, d in tat_o:
        m[b:b + d] = -80.0
    return v, m


def test_phim_dat_nhac_nho_dang_o_khe_va_tat_moi_chuong():
    v, m = phim(-37.0, -26.0, tat_o=[(75, 4), (270, 4), (500, 4)])
    kq = da.phan_tich(v, m, None, chuong=CHUONG)
    assert kl(kq, "Lời cao hơn nhạc (trung") == da.DAT
    assert kl(kq, "Nhạc ở khe") == da.DAT
    assert kl(kq, "Chương có nhạc tắt") == da.DAT
    assert kq["ket_luan"] != da.CHAN


def test_nhac_to_sat_loi_bi_chan_ca_ty_so_va_khe():
    v, m = phim(-23.0, -23.0, tat_o=[(75, 4), (270, 4), (500, 4)])
    kq = da.phan_tich(v, m, None, chuong=CHUONG)
    assert kl(kq, "Lời cao hơn nhạc (trung") == da.CHAN
    assert kl(kq, "Nhạc ở khe") == da.CHAN
    assert kq["ket_luan"] == da.CHAN


def test_khong_co_khoang_nghi_bi_chan_theo_chuong_va_doan_cang_dai():
    v, m = phim(-26.0, -26.0)
    kq = da.phan_tich(v, m, None, chuong=CHUONG)
    assert kl(kq, "Chương có nhạc tắt") == da.CHAN
    assert kl(kq, "Đoạn nhạc căng") == da.CHAN


def test_mok_chuong_gia_dinh_chi_canh_bao_khong_chan():
    v, m = phim(-37.0, -26.0)
    kq = da.phan_tich(v, m, None, chuong=None, do_dai_chuong=200)
    assert kl(kq, "Chương có nhạc tắt") == da.CANH_BAO
    assert kq["chuong_la_moc_that"] is False


def test_nhac_tat_trong_hook_khong_tinh_la_nghi_cua_chuong_dau():
    v, m = phim(-37.0, -26.0, tat_o=[(0, 6), (270, 4), (500, 4)])
    kq = da.phan_tich(v, m, None, chuong=CHUONG)
    assert kq["tat_trong_hook"] == [[0, 6]]
    assert kl(kq, "Chương có nhạc tắt") == da.CHAN


def test_nhac_tat_nhung_tieng_dong_con_chay_khong_tinh_la_nghi():
    v, m = phim(-37.0, -26.0, tat_o=[(75, 4), (270, 4), (500, 4)])
    s = np.full(N, -35.0)  # tiếng động chỉ thấp hơn lời 20 dB
    kq = da.phan_tich(v, m, s, chuong=CHUONG)
    assert kl(kq, "Chương có nhạc tắt") == da.CHAN
    assert kl(kq, "Tiếng động") == da.CANH_BAO


def test_loai_tru_cao_trao_co_y_khong_keo_so_do_xuong():
    v, m = phim(-37.0, -26.0, tat_o=[(75, 4), (270, 4), (500, 4)])
    m[300:400] = -17.0  # nhạc cùng bom đạn đè lời 100 s
    xau = da.phan_tich(v, m, None, chuong=CHUONG)
    tot = da.phan_tich(v, m, None, chuong=CHUONG, loai_tru=[(300, 400)])
    p10_xau = next(c["gia_tri"] for c in xau["chi_so"] if "10 %" in c["ten"])
    p10_tot = next(c["gia_tri"] for c in tot["chi_so"] if "10 %" in c["ten"])
    assert p10_tot > p10_xau


def test_cu_nhan_chi_dem_tieng_vot_len_khong_dem_nen_on():
    s50 = np.full(2000, -50.0)
    s50[200:220] = -10.0  # nổ
    s50[600:620] = -10.0
    nen = np.full(2000, -12.0)  # ồn liên tục cao, không vọt
    assert len(da.cu_nhan(s50, -23.0)) == 2
    assert da.cu_nhan(nen, -23.0) == []


def test_doan_tim_cac_chuoi_dai_du():
    assert da.doan(np.array([1, 1, 0, 1, 1, 1, 0], bool), 3) == [(3, 3)]


def viet_wav(tep: Path, db: np.ndarray, sr: int = 8000, kenh: int = 1, sin: bool = False) -> None:
    """WAV 16 bit, mỗi giây một mức RMS `db` (sóng vuông cho RMS chính xác)."""
    if sin:  # sin 440 Hz, biên độ để RMS đúng mức db
        x = np.concatenate([10 ** (d / 20) * np.sqrt(2) * np.sin(2 * np.pi * 440 * np.arange(sr) / sr) for d in db])
    else:
        x = np.concatenate([np.where(np.arange(sr) % 2 == 0, 1, -1) * 10 ** (d / 20) for d in db])
    x = np.repeat(x, kenh)
    with wave.open(str(tep), "wb") as w:
        w.setnchannels(kenh)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def test_cli_chay_that_tren_wav_nhac_to_thoat_1_va_ghi_json(tmp_path, capsys):
    v, m = phim(-23.0, -23.0)
    viet_wav(tmp_path / "T-stem-giong.wav", np.maximum(v, -90))
    viet_wav(tmp_path / "T-stem-nhac.wav", m)
    ra = tmp_path / "ra.json"
    ma = da.main([str(tmp_path), "--ten", "T", "--chuong", "0,180,380", "--json", str(ra)])
    assert ma == 1
    out = capsys.readouterr().out
    assert "CHẶN" in out and "KẾT LUẬN: CHẶN" in out
    d = json.loads(ra.read_text(encoding="utf-8"))
    assert d["ket_luan"] == "CHẶN" and len(d["giong"]) == N


def test_cli_phim_dat_thoat_0(tmp_path):
    v, m = phim(-37.0, -26.0, tat_o=[(75, 4), (270, 4), (500, 4)])
    viet_wav(tmp_path / "T-stem-giong.wav", np.maximum(v, -90))
    viet_wav(tmp_path / "T-stem-nhac.wav", m)
    assert da.main([str(tmp_path), "--ten", "T", "--chuong", "0,180,380"]) == 0


def test_cli_chi_co_ban_tron_thoat_3_khong_ket_luan(tmp_path, capsys):
    viet_wav(tmp_path / "T-master.wav", np.full(60, -20.0))
    assert da.main([str(tmp_path), "--ten", "T"]) == 3
    assert "KHÔNG ĐO ĐƯỢC" in capsys.readouterr().out


def thoat(argv):
    with pytest.raises(SystemExit) as e:
        da.main(argv)
    return e.value.code


def test_loi_dau_vao_thoat_2_khong_trung_ma_chan_thu_muc_khong_co_stem(tmp_path, capsys):
    assert thoat([str(tmp_path)]) == 2
    assert "không xác định được tập" in capsys.readouterr().err


def test_loi_dau_vao_thoat_2_wav_hong(tmp_path):
    (tmp_path / "T-stem-giong.wav").write_text("không phải wav", encoding="utf-8")
    (tmp_path / "T-stem-nhac.wav").write_text("không phải wav", encoding="utf-8")
    assert thoat([str(tmp_path), "--ten", "T"]) == 2


def test_loi_dau_vao_thoat_2_chuong_sai_va_loai_tru_sai_va_do_dai_chuong_0(tmp_path):
    v, m = phim(-37.0, -26.0)
    viet_wav(tmp_path / "T-stem-giong.wav", np.maximum(v, -90))
    viet_wav(tmp_path / "T-stem-nhac.wav", m)
    goc = [str(tmp_path), "--ten", "T"]
    assert thoat(goc + ["--chuong", "a,b"]) == 2
    assert thoat(goc + ["--loai-tru", "x-y"]) == 2
    assert thoat(goc + ["--loai-tru", "650-600"]) == 2
    assert thoat(goc + ["--do-dai-chuong", "0"]) == 2


def test_tieng_dong_ngan_hon_khong_cat_ca_phim():
    v, m = phim(-37.0, -26.0, tat_o=[(75, 4), (270, 4), (500, 4)])
    kq = da.phan_tich(v, m, np.full(100, -50.0), chuong=CHUONG)
    assert kq["thoi_luong_s"] == N


def test_giong_va_nhac_lech_nhau_qua_2_giay_bao_loi():
    v, m = phim(-37.0, -26.0)
    with pytest.raises(ValueError, match="lệch"):
        da.phan_tich(v, m[:-5], None)


def test_loai_tru_phu_het_giay_co_loi_bao_loi_ro_va_main_thoat_2(tmp_path):
    v, m = phim(-37.0, -26.0)
    with pytest.raises(ValueError, match="loai-tru"):
        da.phan_tich(v, m, None, loai_tru=[(0, N)])
    viet_wav(tmp_path / "T-stem-giong.wav", np.maximum(v, -90))
    viet_wav(tmp_path / "T-stem-nhac.wav", m)
    assert da.main([str(tmp_path), "--ten", "T", "--loai-tru", f"0-{N}"]) == 2


def test_nhac_tat_o_duoi_sau_loi_cuoi_khong_tinh_la_nghi_cua_chuong_cuoi():
    v, m = phim(-37.0, -26.0, tat_o=[(75, 4), (270, 4)])
    m[N - 8:] = -80.0  # nhạc fade ra sau lời cuối
    kq = da.phan_tich(v, m, None, chuong=CHUONG)
    assert kq["tat_o_duoi"] == [[N - 8, 8]]
    assert kl(kq, "Chương có nhạc tắt") == da.CHAN


def test_nhac_dao_quanh_nguong_cang_khong_ngat_chuoi_nua():
    v = np.full(300, -15.0)
    m = np.where(np.arange(300) % 2 == 0, -29.0, -31.0)  # ngưỡng căng = −30
    assert da.lap_ho(np.array([1, 0, 1, 0, 0, 0, 1], bool), 2).tolist() == [1, 1, 1, 0, 0, 0, 1]
    assert kl(da.phan_tich(v, m, None), "Đoạn nhạc căng") == da.CHAN


def test_lra_loi_ffmpeg_co_ly_do_khong_im_lang(tmp_path):
    hong = tmp_path / "x.wav"
    hong.write_text("hỏng", encoding="utf-8")
    r = da.lra_tu([hong])
    assert "loi" in r and "LRA_LU" not in r
    v, m = phim(-37.0, -26.0)
    kq = da.phan_tich(v, m, None, lra=r)
    assert "ffmpeg" in next(c["chu_thich"] for c in kq["chi_so"] if c["ten"] == "LRA")


def test_doc_wav_stereo_44k1_ra_dung_muc_rms(tmp_path):
    viet_wav(tmp_path / "s.wav", np.full(5, -20.0), sr=44100, kenh=2, sin=True)
    db = da.rms_db(da.doc_wav(tmp_path / "s.wav"))
    assert len(db) == 5 and abs(float(db.mean()) + 17.0) < 0.5  # ffmpeg hạ stereo giống nhau lên mono +3 dB, mọi stem như nhau nên tỉ số không đổi


def test_doc_moc_chuong_tu_phan_canh_json_cong_lui_intro(tmp_path, capsys):
    pc = tmp_path / "pc.json"
    pc.write_text(json.dumps({"het": 100.0, "canh": [
        {"nguon": "karmen:1", "t0": 0}, {"nguon": "the:chuong/1", "t0": 10.0}, {"nguon": "the:chuong/2", "t0": 50.5}]}),
        encoding="utf-8")
    assert da.doc_moc_chuong(str(pc), None, 106.875) == pytest.approx([16.875, 57.375])
    assert da.doc_moc_chuong(str(pc), 2.0, 106.875) == pytest.approx([12.0, 52.5])
    pc.write_text(json.dumps({"canh": [{"nguon": "the:chuong/1", "t0": 10.0}]}), encoding="utf-8")
    assert da.doc_moc_chuong(str(pc), None, 106.875) == [10.0]
    assert "có thể lệch" in capsys.readouterr().err


def thoat_tim(thu):
    with pytest.raises(SystemExit) as e:
        da.tim_tep(thu, None, None)
    return e.value.code


def test_tim_tep_tu_doan_ten_tap_va_mau_rieng(tmp_path):
    for k in ("giong", "nhac", "tieng"):
        (tmp_path / f"EP9-stem-{k}.wav").write_bytes(b"")
    tep, ten = da.tim_tep(tmp_path, None, None)
    assert ten == "EP9" and set(tep) == {"giong", "nhac", "tieng"}
    (tmp_path / "EP8-tach-giong.wav").write_bytes(b"")
    assert thoat_tim(tmp_path) == 2
    (tmp_path / "A-giong.wav").write_bytes(b"")
    tep, ten = da.tim_tep(tmp_path, "A", "{ten}-{k}.wav")
    assert set(tep) == {"giong"}


def test_doc_loai_tru_doc_nhieu_doan():
    assert da.doc_loai_tru("600-650, 900.5-930") == [(600.0, 650.0), (900.5, 930.0)]
    assert da.doc_loai_tru(None) == []


def test_cli_chi_co_ban_tron_in_lra_va_i(tmp_path, capsys):
    viet_wav(tmp_path / "T-master.wav", np.full(30, -20.0))
    assert da.main([str(tmp_path), "--ten", "T"]) == 3
    assert "LRA" in capsys.readouterr().out
