"""Test lệnh giong. KHÔNG gọi API thật: gui_http bị thay bằng hàm giả.

Hình dạng phản hồi theo tài liệu ElevenLabs «Create speech with timing»
(POST /v1/text-to-speech/{voice_id}/with-timestamps): JSON {audio_base64, alignment{characters,
character_start_times_seconds, character_end_times_seconds}, normalized_alignment{...}}.
Hình dạng lỗi: {"detail": {"status": "...", "message": "..."}}; 429 kèm tiêu đề Retry-After.
"""
import argparse
import base64
import json
import sys
import wave
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chung  # noqa: E402
import giong  # noqa: E402
from chung import LoiKit  # noqa: E402

KHOA_GIA = "khoa-gia-cho-test"


class Phan:
    def __init__(self, ma=200, du_lieu=None, tieu_de=None, chu=None):
        self.status_code = ma
        self._d = du_lieu
        self.headers = tieu_de or {}
        self.text = chu if chu is not None else json.dumps(du_lieu)

    def json(self):
        if self._d is None:
            raise ValueError("không phải json")
        return self._d


def canh(chu, moi_ky_tu=0.05):
    ks = list(chu)
    return {"characters": ks,
            "character_start_times_seconds": [round(i * moi_ky_tu, 3) for i in range(len(ks))],
            "character_end_times_seconds": [round((i + 1) * moi_ky_tu, 3) for i in range(len(ks))]}


def phan_thanh_cong(chu, so_mau=4800):
    pcm = b"\x01\x00" * so_mau
    return Phan(200, {"audio_base64": base64.b64encode(pcm).decode(), "alignment": canh(chu),
                      "normalized_alignment": canh(chu)})


@pytest.fixture
def mang(monkeypatch):
    """Thay gui_http; trả danh sách lượt gọi. Đặt hàng đợi phản hồi qua mang.cho."""
    monkeypatch.setenv("ELEVENLABS_API_KEY", KHOA_GIA)
    monkeypatch.setattr(giong.time, "sleep", lambda s: ngu.append(s))
    ngu.clear()

    class M:
        goi = []
        cho = []

    def gia(method, url, **kw):
        M.goi.append({"method": method, "url": url, **kw})
        return M.cho.pop(0) if len(M.cho) > 1 else M.cho[0]

    M.goi, M.cho = [], [phan_thanh_cong("[fast-paced] Chiến thắng")]
    monkeypatch.setattr(giong, "gui_http", gia)
    return M


ngu: list = []


def chay_giong(*tham_so):
    p = argparse.ArgumentParser()
    giong.dang_ky(p)
    return giong.chay(p.parse_args(list(tham_so)))


def test_url_header_va_body_toi_thieu(mang, tmp_path):
    chay_giong("[fast-paced] Chiến thắng", "--voice", "V1", "--out", str(tmp_path / "a.wav"))
    (g,) = mang.goi
    assert g["method"] == "POST"
    assert g["url"] == "https://api.elevenlabs.io/v1/text-to-speech/V1/with-timestamps?output_format=pcm_48000"
    assert g["headers"]["xi-api-key"] == KHOA_GIA
    assert g["json_body"] == {"text": "[fast-paced] Chiến thắng", "model_id": "eleven_v4", "language_code": "vi"}


def test_prev_next_va_voice_settings_chi_khi_co_co(mang, tmp_path):
    chay_giong("câu giữa", "--voice", "V1", "--out", str(tmp_path / "a.wav"), "--prev", "câu trước",
               "--next", "câu sau", "--stability", "0.4", "--similarity", "0.8", "--style", "0.1", "--speed", "1.1")
    body = mang.goi[0]["json_body"]
    assert body["previous_text"] == "câu trước" and body["next_text"] == "câu sau"
    assert body["voice_settings"] == {"stability": 0.4, "similarity_boost": 0.8, "style": 0.1, "speed": 1.1}


def test_wav_48k_mono_16bit_va_do_dai(mang, tmp_path):
    out = tmp_path / "a.wav"
    chay_giong("x", "--voice", "V1", "--out", str(out))
    with wave.open(str(out)) as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()) == (48000, 1, 2, 4800)


def test_moc_chu_cat_o_khoang_trang_va_the_la_mot_chu():
    w = giong.chu_tu_alignment(canh("[fast-paced] Chiến  thắng,"))
    assert [x["text"] for x in w] == ["[fast-paced]", "Chiến", "thắng,"]
    assert w[0] == {"text": "[fast-paced]", "start_ms": 0, "end_ms": 600}
    assert w[1]["start_ms"] == 650 and w[1]["end_ms"] == 900  # 13 ký tự đầu; "Chiến" = ký tự 13..17
    assert all(isinstance(x["start_ms"], int) and isinstance(x["end_ms"], int) for x in w)


def test_json_dung_luoc_do_bao_cao(mang, tmp_path, capsys):
    out = tmp_path / "a.wav"
    chay_giong("[fast-paced] Chiến thắng", "--voice", "V1", "--out", str(out), "--json")
    d = json.loads(capsys.readouterr().out)
    assert set(d) == {"adapter", "results"} and d["adapter"] == "elevenlabs"
    (kq,) = d["results"]
    assert kq["out"] == str(out.resolve()) and kq["sampleRate"] == 48000 and kq["voice"] == "V1"
    assert kq["duration"] == 0.1
    assert [x["text"] for x in kq["words"]] == ["[fast-paced]", "Chiến", "thắng"]


def test_dung_normalized_alignment_khi_alignment_rong(mang, tmp_path):
    mang.cho[0] = Phan(200, {"audio_base64": base64.b64encode(b"\0\0").decode(), "alignment": None,
                             "normalized_alignment": canh("xin chào")})
    out = tmp_path / "a.wav"
    chay_giong("x", "--voice", "V1", "--out", str(out), "--json")
    assert out.exists()


def test_text_file_duoc_cat_khoang_trang(mang, tmp_path):
    f = tmp_path / "loi.txt"
    f.write_text("\n  Xin chào  \n", encoding="utf-8")
    chay_giong("--text-file", str(f), "--voice", "V1", "--out", str(tmp_path / "a.wav"))
    assert mang.goi[0]["json_body"]["text"] == "Xin chào"


def test_vua_text_vua_file_la_loi(mang, tmp_path):
    f = tmp_path / "loi.txt"
    f.write_text("a", encoding="utf-8")
    with pytest.raises(LoiKit):
        chay_giong("b", "--text-file", str(f), "--voice", "V1", "--out", str(tmp_path / "a.wav"))
    assert mang.goi == []


def test_qua_tran_ky_tu_bao_loi_ro_va_khong_goi_api(mang, tmp_path):
    with pytest.raises(LoiKit, match="5000"):
        chay_giong("a" * 5001, "--voice", "V1", "--out", str(tmp_path / "a.wav"))
    assert mang.goi == []
    chay_giong("a" * 5000, "--voice", "V1", "--out", str(tmp_path / "a.wav"))  # đúng trần vẫn được


def test_tep_ra_co_san_can_force(mang, tmp_path):
    out = tmp_path / "a.wav"
    out.write_bytes(b"cu")
    with pytest.raises(LoiKit, match="--force"):
        chay_giong("x", "--voice", "V1", "--out", str(out))
    assert mang.goi == []
    chay_giong("x", "--voice", "V1", "--out", str(out), "--force")
    assert out.read_bytes()[:4] == b"RIFF"


def test_thu_lai_429_theo_retry_after(mang, tmp_path):
    mang.cho[:] = [Phan(429, {"detail": {"status": "too_many_concurrent_requests", "message": "bận"}}, {"Retry-After": "2"}),
                   Phan(429, {"detail": {"message": "bận"}}, {"Retry-After": "0.2"}),
                   phan_thanh_cong("x")]
    chay_giong("x", "--voice", "V1", "--out", str(tmp_path / "a.wav"))
    assert len(mang.goi) == 3 and ngu == [2, 1]  # làm tròn lên, tối thiểu 1 s


def test_thu_lai_429_khong_co_header_cho_15_30_45_roi_bo(mang, tmp_path):
    mang.cho[:] = [Phan(429, {"detail": {"message": "bận"}})]
    with pytest.raises(LoiKit, match="429"):
        chay_giong("x", "--voice", "V1", "--out", str(tmp_path / "a.wav"))
    assert len(mang.goi) == 4 and ngu == [15, 30, 45]


def test_5xx_cung_duoc_thu_lai(mang, tmp_path):
    mang.cho[:] = [Phan(503, None, chu="Service Unavailable"), phan_thanh_cong("x")]
    chay_giong("x", "--voice", "V1", "--out", str(tmp_path / "a.wav"))
    assert len(mang.goi) == 2 and ngu == [15]


def test_cho_qua_120_giay_thi_bo_ngay(mang, tmp_path):
    mang.cho[:] = [Phan(429, {"detail": {"message": "hết hạn mức ngày"}}, {"Retry-After": "300"})]
    with pytest.raises(LoiKit, match="429"):
        chay_giong("x", "--voice", "V1", "--out", str(tmp_path / "a.wav"))
    assert len(mang.goi) == 1 and ngu == []


def test_loi_api_in_ma_va_thong_diep_khong_lo_khoa(mang, tmp_path):
    mang.cho[:] = [Phan(401, {"detail": {"status": "quota_exceeded", "message": "You have 0 credits left"}})]
    with pytest.raises(LoiKit) as e:
        chay_giong("x", "--voice", "V1", "--out", str(tmp_path / "a.wav"))
    s = str(e.value)
    assert "401" in s and "quota_exceeded" in s and "0 credits" in s and KHOA_GIA not in s
    assert len(mang.goi) == 1  # 4xx khác 429 không thử lại


def test_loi_422_dang_danh_sach(mang, tmp_path):
    mang.cho[:] = [Phan(422, {"detail": [{"loc": ["body", "text"], "msg": "field required", "type": "missing"}]})]
    with pytest.raises(LoiKit, match="field required"):
        chay_giong("x", "--voice", "V1", "--out", str(tmp_path / "a.wav"))


def test_thieu_khoa_bao_loi_va_khong_goi_api(monkeypatch, tmp_path):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.setattr(chung, "TEP_KHOA", tmp_path / "khong-co")
    goi = []
    monkeypatch.setattr(giong, "gui_http", lambda *a, **k: goi.append(1))
    with pytest.raises(LoiKit, match="ELEVENLABS_API_KEY"):
        chay_giong("x", "--voice", "V1", "--out", str(tmp_path / "a.wav"))
    assert goi == []


def test_ma_giong_duoc_ma_hoa_trong_url(mang, tmp_path):
    chay_giong("x", "--voice", "a/b?c=1#d", "--out", str(tmp_path / "a.wav"))
    url = mang.goi[0]["url"]
    assert url == "https://api.elevenlabs.io/v1/text-to-speech/a%2Fb%3Fc%3D1%23d/with-timestamps?output_format=pcm_48000"
