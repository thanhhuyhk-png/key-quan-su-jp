"""Test lệnh tieng-dong. KHÔNG gọi API thật: giong.gui_http bị thay bằng hàm giả.

Hình dạng theo tài liệu ElevenLabs «Sound generation» (POST /v1/sound-generation?output_format=...):
thân JSON {text, model_id, duration_seconds?, prompt_influence?, loop?}; phản hồi 200 là BYTE ÂM THANH thô
(mp3 hoặc PCM tuỳ output_format), không bọc json. Lỗi: {"detail": {...}}.
"""
import argparse
import json
import sys
import wave
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chung  # noqa: E402
import giong  # noqa: E402
import tieng_dong  # noqa: E402
from chung import LoiKit, chay_lenh  # noqa: E402

TIEU_DE = "tep\tnhom\tmo_ta_prompt\tnguon_ngay\tgiay_phep\tdai_s\tkiem_tra\tda_dung_o\n"
DONG_CU = "sfx/a/cu.mp3\ta\tmô tả cũ\tElevenLabs SFX (công cụ cũ), 25/10/2026\tgp\t8.05\tok\tĐBP\n"


class Phan:
    def __init__(self, ma=200, noi_dung=b"", du_lieu=None):
        self.status_code, self.content, self._d, self.headers = ma, noi_dung, du_lieu, {}
        self.text = json.dumps(du_lieu) if du_lieu is not None else ""

    def json(self):
        if self._d is None:
            raise ValueError("không phải json")
        return self._d


@pytest.fixture
def mp3_that(tmp_path):
    f = tmp_path / "mau.mp3"
    chay_lenh(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=300:duration=1", str(f)])
    return f.read_bytes()


@pytest.fixture
def kho(tmp_path, monkeypatch):
    """Kho tài sản giả = tmp_path/kit/ASSETS.tsv; thư mục kho là tmp_path/kit."""
    (tmp_path / "kit").mkdir()
    tsv = tmp_path / "kit" / "ASSETS.tsv"
    tsv.write_text(TIEU_DE + DONG_CU, encoding="utf-8")
    monkeypatch.setattr(tieng_dong, "ASSETS", tsv)
    return tsv


@pytest.fixture
def mang(monkeypatch, mp3_that):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "khoa-gia")

    class M:
        goi = []
        cho = Phan(200, mp3_that)

    M.goi = []

    def gia(method, url, **kw):
        M.goi.append({"method": method, "url": url, **kw})
        return M.cho

    monkeypatch.setattr(giong, "gui_http", gia)
    return M


def chay(*tham_so):
    p = argparse.ArgumentParser()
    tieng_dong.dang_ky(p)
    return tieng_dong.chay(p.parse_args(list(tham_so)))


def test_mp3_url_header_va_body_toi_thieu(mang, kho):
    out = kho.parent / "sfx" / "x" / "no.mp3"
    chay("a big explosion", "--out", str(out))
    (g,) = mang.goi
    assert g["url"] == "https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128"
    assert g["headers"]["xi-api-key"] == "khoa-gia"
    assert g["json_body"] == {"text": "a big explosion", "model_id": "eleven_text_to_sound_v2"}
    assert out.read_bytes() == mang.cho.content


def test_tuy_chon_duration_influence_loop(mang, kho):
    chay("rain", "--out", str(kho.parent / "m.mp3"), "--duration", "3.5", "--influence", "0.7", "--loop")
    assert mang.goi[0]["json_body"] == {"text": "rain", "model_id": "eleven_text_to_sound_v2",
                                        "duration_seconds": 3.5, "prompt_influence": 0.7, "loop": True}


def test_wav_pcm_48000_la_stereo_xen_ke_nen_giu_dung_do_dai(mang, kho):
    # Đo thật 03/11/2026: xin 5 s, nhận 960 000 byte; tự tương quan lệch 2 mẫu 0,999 > lệch 1 mẫu 0,889
    # → hai kênh xen kẽ. Ghi thành mono thì tệp dài gấp đôi, chậm và trầm một quãng tám.
    mang.cho = Phan(200, b"\x01\x00\x02\x00" * 48000)  # PCM stereo 1 s
    out = kho.parent / "sfx" / "n.wav"
    chay("click", "--out", str(out))
    assert mang.goi[0]["url"].endswith("output_format=pcm_48000")
    with wave.open(str(out)) as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()) == (48000, 2, 2, 48000)


def test_dong_assets_dung_cot_duong_dan_tuong_doi_va_do_dai(mang, kho):
    out = kho.parent / "sfx" / "chien-truong" / "no-lon.mp3"
    chay("a big\texplosion\nwith echo", "--out", str(out))
    dong = kho.read_text(encoding="utf-8").splitlines()
    assert len(dong) == 3
    c = dict(zip(TIEU_DE.strip().split("\t"), dong[2].split("\t")))
    assert c["tep"] == "sfx/chien-truong/no-lon.mp3" and c["nhom"] == "chien-truong"
    assert c["mo_ta_prompt"] == "a big explosion with echo"
    assert c["nguon_ngay"].startswith("ElevenLabs SFX (kit tieng-dong), ") and c["nguon_ngay"][-10:].count("/") == 2
    assert c["giay_phep"] == "ElevenLabs — dùng thương mại theo gói trả phí"
    assert 0.9 <= float(c["dai_s"]) <= 1.2 and c["kiem_tra"] == "" and c["da_dung_o"] == ""
    assert len(dong[2].split("\t")) == 8
    assert dong[1] == DONG_CU.strip()  # dòng cũ nguyên vẹn


def test_nhom_tu_chon(mang, kho):
    chay("x", "--out", str(kho.parent / "sfx" / "q" / "x.mp3"), "--nhom", "khong-khi")
    assert kho.read_text(encoding="utf-8").splitlines()[2].split("\t")[1] == "khong-khi"


def test_tep_ngoai_kho_giu_duong_dan_nguoi_dung_dua(mang, kho, tmp_path):
    ngoai = tmp_path / "ngoai" / "x.mp3"
    chay("x", "--out", str(ngoai))
    tep = kho.read_text(encoding="utf-8").splitlines()[2].split("\t")[0]
    assert tep == str(ngoai).replace("\\", "/")


def test_khong_ghi_trung_dong_cung_tep(mang, kho):
    out = kho.parent / "sfx" / "x.mp3"
    chay("x", "--out", str(out))
    chay("x", "--out", str(out), "--force")
    assert len(kho.read_text(encoding="utf-8").splitlines()) == 3
    assert len(mang.goi) == 2  # vẫn gọi API lần hai vì có --force


def test_dong_cuoi_khong_co_xuong_dong_van_ghi_dung(mang, kho):
    kho.write_text(TIEU_DE + DONG_CU.rstrip("\n"), encoding="utf-8")
    chay("x", "--out", str(kho.parent / "x.mp3"))
    assert len(kho.read_text(encoding="utf-8").splitlines()) == 3


def test_dinh_dang_va_tham_so_sai_khong_goi_api(mang, kho):
    for loi in (["--out", str(kho.parent / "x.ogg")],
                ["--out", str(kho.parent / "x.mp3"), "--duration", "31"],
                ["--out", str(kho.parent / "x.mp3"), "--duration", "0.1"],
                ["--out", str(kho.parent / "x.mp3"), "--influence", "1.5"]):
        with pytest.raises(LoiKit):
            chay("x", *loi)
    assert mang.goi == []


def test_tep_co_san_can_force(mang, kho):
    out = kho.parent / "x.mp3"
    out.write_bytes(b"cu")
    with pytest.raises(LoiKit, match="--force"):
        chay("x", "--out", str(out))
    assert mang.goi == [] and out.read_bytes() == b"cu"


def test_loi_api_khong_ghi_tep_va_khong_ghi_assets(mang, kho):
    mang.cho = Phan(401, du_lieu={"detail": {"status": "quota_exceeded", "message": "hết credit"}})
    out = kho.parent / "x.mp3"
    with pytest.raises(LoiKit, match="401.*quota_exceeded"):
        chay("x", "--out", str(out))
    assert not out.exists() and len(kho.read_text(encoding="utf-8").splitlines()) == 2


def test_thieu_khoa(monkeypatch, kho):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.setattr(chung, "TEP_KHOA", kho.parent / "khong-co")
    monkeypatch.setattr(giong, "gui_http", lambda *a, **k: pytest.fail("không được gọi API"))
    with pytest.raises(LoiKit, match="ELEVENLABS_API_KEY"):
        chay("x", "--out", str(kho.parent / "x.mp3"))
