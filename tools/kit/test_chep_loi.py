"""Test lệnh chep-loi. KHÔNG gọi API thật: giong.gui_http bị thay bằng hàm giả.

Hình dạng phản hồi theo tài liệu:
- ElevenLabs Speech to Text (POST /v1/speech-to-text, multipart): {language_code, language_probability, text,
  words[{text,start,end,type: word|spacing|audio_event, speaker_id, logprob}]}.
- Deepgram pre-recorded (POST /v1/listen): {metadata, results{channels[{alternatives[{transcript, confidence,
  words[{word,start,end,confidence,punctuated_word}]}]}]}}; xác thực «Authorization: Token <khoá>».
Âm vào là sin 1 s sinh bằng ffmpeg trong tmp_path.
"""
import argparse
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chep_loi  # noqa: E402
import chung  # noqa: E402
import giong  # noqa: E402
from chung import LoiKit, chay_lenh  # noqa: E402


class Phan:
    def __init__(self, ma=200, du_lieu=None):
        self.status_code, self._d, self.headers = ma, du_lieu, {}
        self.text = json.dumps(du_lieu)

    def json(self):
        return self._d


SCRIBE = {"language_code": "vie", "language_probability": 0.99, "text": "Điện Biên Phủ (tiếng cười)", "words": [
    {"text": "Điện", "start": 0.10, "end": 0.40, "type": "word", "speaker_id": "speaker_0"},
    {"text": " ", "start": 0.40, "end": 0.42, "type": "spacing", "speaker_id": "speaker_0"},
    {"text": "Biên", "start": 0.42, "end": 0.70, "type": "word", "speaker_id": "speaker_0"},
    {"text": "Phủ", "start": 0.70, "end": 0.70, "type": "word", "speaker_id": "speaker_1"},
    {"text": "(tiếng cười)", "start": 0.90, "end": 1.20, "type": "audio_event", "speaker_id": "speaker_0"},
    {"text": "mất giờ", "start": None, "end": None, "type": "word"}]}

DEEPGRAM = {"metadata": {"duration": 1.0}, "results": {"channels": [{"alternatives": [
    {"transcript": "Điện Biên Phủ.", "confidence": 0.99, "words": [
        {"word": "điện", "start": 0.1, "end": 0.4, "confidence": 0.9, "punctuated_word": "Điện"},
        {"word": "biên", "start": 0.42, "end": 0.7, "confidence": 0.9, "punctuated_word": "Biên"},
        {"word": "phủ", "start": 0.7, "end": 1.0, "confidence": 0.9, "punctuated_word": "Phủ."}]}]}]}}


@pytest.fixture
def am(tmp_path):
    f = tmp_path / "giong-v1.wav"
    chay_lenh(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=1", "-ar", "48000", str(f)])
    return f


@pytest.fixture
def mang(monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "khoa-gia-el")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "khoa-gia-dg")

    class M:
        goi = []
        cho = Phan(200, SCRIBE)

    M.goi = []

    def gia(method, url, **kw):
        M.goi.append({"method": method, "url": url, **kw})
        return M.cho

    monkeypatch.setattr(giong, "gui_http", gia)
    return M


def chay(*tham_so):
    p = argparse.ArgumentParser()
    chep_loi.dang_ky(p)
    return chep_loi.chay(p.parse_args(list(tham_so)))


def test_scribe_gui_dung_url_header_truong_va_tep_mp3(mang, am, tmp_path):
    chay(str(am), "--out-dir", str(tmp_path / "stt"), "--lang", "vi")
    (g,) = mang.goi
    assert g["url"] == "https://api.elevenlabs.io/v1/speech-to-text"
    assert g["headers"]["xi-api-key"] == "khoa-gia-el"
    assert g["data"] == {"model_id": "scribe_v1", "language_code": "vi", "timestamps_granularity": "word",
                         "diarize": "true", "tag_audio_events": "true"}
    ten, noi_dung, loai = g["files"]["file"]
    assert ten.endswith(".mp3") and loai == "audio/mpeg" and noi_dung[:3] in (b"ID3", b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")


def test_scribe_ra_words_json_dung_luoc_do(mang, am, tmp_path):
    chay(str(am), "--out-dir", str(tmp_path / "stt"))
    d = json.loads((tmp_path / "stt" / "giong-v1.words.json").read_text(encoding="utf-8"))
    assert list(d)[:8] == ["source", "source_sha256", "audio_duration_ms", "provider", "model", "outcome",
                           "language", "warnings"]
    assert d["source"] == "giong-v1.wav" and d["provider"] == "elevenlabs" and d["outcome"] == "speech"
    assert d["language"] == "vi" and 900 <= d["audio_duration_ms"] <= 1100 and len(d["source_sha256"]) == 64
    w = d["words"]
    assert [x["text"] for x in w] == ["Điện", "Biên", "Phủ", "(tiếng cười)"]  # bỏ spacing và chữ không có mốc
    assert w[0] == {"id": "word_000001", "ordinal": 0, "text": "Điện", "start_ms": 100, "end_ms": 400,
                    "speaker": "1", "audio_event": False}
    assert w[2]["speaker"] == "2" and w[2]["end_ms"] == 900  # dài 0 → ≤ 200 ms nhưng không quá chữ kế (0,9 s)
    assert w[3]["audio_event"] is True and w[3]["id"] == "word_000004"


def test_txt_khong_co_audio_event(mang, am, tmp_path):
    chay(str(am), "--out-dir", str(tmp_path / "stt"))
    assert (tmp_path / "stt" / "giong-v1.txt").read_text(encoding="utf-8").strip() == "Điện Biên Phủ"


def test_deepgram_url_header_tham_so_va_du_lieu_nhi_phan(mang, am, tmp_path):
    mang.cho = Phan(200, DEEPGRAM)
    chay(str(am), "--out-dir", str(tmp_path / "stt"), "--adapter", "deepgram")
    (g,) = mang.goi
    assert g["url"] == "https://api.deepgram.com/v1/listen"
    assert g["headers"]["Authorization"] == "Token khoa-gia-dg" and "xi-api-key" not in g["headers"]
    assert g["params"] == {"model": "nova-2", "language": "vi", "smart_format": "true", "punctuate": "true"}
    assert isinstance(g["data"], bytes) and len(g["data"]) > 100
    d = json.loads((tmp_path / "stt" / "giong-v1.words.json").read_text(encoding="utf-8"))
    assert d["provider"] == "deepgram" and d["model"] == "nova-2"
    assert [x["text"] for x in d["words"]] == ["Điện", "Biên", "Phủ."]
    assert d["words"][1]["start_ms"] == 420 and d["words"][2]["speaker"] == ""


def test_words_json_dung_duoc_cho_so_loi(mang, am, tmp_path):
    import so_loi
    chay(str(am), "--out-dir", str(tmp_path / "stt"))
    du_lieu = json.loads((tmp_path / "stt" / "giong-v1.words.json").read_text(encoding="utf-8"))
    assert so_loi.so("Điện Biên Phủ", du_lieu, "vi", 0.97)["pass"] is True


def test_co_san_tep_ra_khong_force_thi_dung_truoc_khi_goi_api(mang, am, tmp_path):
    ra = tmp_path / "stt"
    ra.mkdir()
    (ra / "giong-v1.txt").write_text("cũ", encoding="utf-8")
    with pytest.raises(LoiKit, match="--force"):
        chay(str(am), "--out-dir", str(ra))
    assert mang.goi == []
    chay(str(am), "--out-dir", str(ra), "--force")
    assert len(mang.goi) == 1


def test_thieu_khoa_deepgram(monkeypatch, am, tmp_path):
    monkeypatch.delenv("DEEPGRAM_API_KEY", raising=False)
    monkeypatch.setattr(chung, "TEP_KHOA", tmp_path / "khong-co")
    monkeypatch.setattr(giong, "gui_http", lambda *a, **k: pytest.fail("không được gọi API"))
    with pytest.raises(LoiKit, match="DEEPGRAM_API_KEY"):
        chay(str(am), "--out-dir", str(tmp_path / "stt"), "--adapter", "deepgram")


def test_loi_api_dich_ra_cau_co_ma(mang, am, tmp_path):
    mang.cho = Phan(401, {"detail": {"status": "invalid_api_key", "message": "Invalid API key"}})
    with pytest.raises(LoiKit, match="401.*invalid_api_key"):
        chay(str(am), "--out-dir", str(tmp_path / "stt"))


def test_nguon_khong_ton_tai(mang, tmp_path):
    with pytest.raises(LoiKit, match="không thấy"):
        chay(str(tmp_path / "khong-co.wav"))
    assert mang.goi == []


class _ChuWhisper:
    def __init__(self, word, start, end):
        self.word, self.start, self.end = word, start, end


class _DoanWhisper:
    def __init__(self, words):
        self.words = words


def _whisper_gia(monkeypatch, ghi: dict):
    import types

    class WhisperModel:
        def __init__(self, ten, **kw):
            ghi["model"], ghi["kw"] = ten, kw

        def transcribe(self, duong, **kw):
            ghi["duong"], ghi["transcribe"] = duong, kw
            doan = [_DoanWhisper([_ChuWhisper(" Điện", 0.1, 0.4), _ChuWhisper(" Biên", 0.42, 0.7)]),
                    _DoanWhisper([_ChuWhisper(" Phủ.", 0.7, 0.7)])]
            return iter(doan), types.SimpleNamespace(language="vi")

    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=WhisperModel))


def test_whisper_chay_tren_may_khong_can_khoa_ra_cung_luoc_do(monkeypatch, am, tmp_path):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("DEEPGRAM_API_KEY", raising=False)
    ghi = {}
    _whisper_gia(monkeypatch, ghi)
    chay(str(am), "--out-dir", str(tmp_path / "stt"), "--adapter", "whisper")
    assert ghi["model"] == "medium"
    assert ghi["transcribe"]["language"] == "vi" and ghi["transcribe"]["word_timestamps"] is True
    d = json.loads((tmp_path / "stt" / "giong-v1.words.json").read_text(encoding="utf-8"))
    assert d["provider"] == "whisper" and d["model"] == "medium"
    assert [w["text"] for w in d["words"]] == ["Điện", "Biên", "Phủ."]
    assert d["words"][0]["start_ms"] == 100 and d["words"][2]["end_ms"] > d["words"][2]["start_ms"]
    assert (tmp_path / "stt" / "giong-v1.txt").read_text(encoding="utf-8").strip() == "Điện Biên Phủ."


def test_whisper_thieu_thu_vien_bao_cach_cai(monkeypatch, am, tmp_path):
    monkeypatch.setitem(sys.modules, "faster_whisper", None)
    with pytest.raises(LoiKit, match="pip install faster-whisper"):
        chay(str(am), "--out-dir", str(tmp_path / "stt"), "--adapter", "whisper")


def test_whisper_lang_auto_truyen_none(monkeypatch, am, tmp_path):
    ghi = {}
    _whisper_gia(monkeypatch, ghi)
    chay(str(am), "--out-dir", str(tmp_path / "stt"), "--adapter", "whisper", "--lang", "auto")
    assert ghi["transcribe"]["language"] is None


def test_whisper_loi_tao_model_thanh_loikit(monkeypatch, am, tmp_path):
    import types

    class WhisperModel:
        def __init__(self, *a, **kw):
            raise OSError("không tải được model (mất mạng)")

    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=WhisperModel))
    with pytest.raises(LoiKit, match="mất mạng"):
        chay(str(am), "--out-dir", str(tmp_path / "stt"), "--adapter", "whisper")


def test_whisper_loi_khi_chep_thanh_loikit(monkeypatch, am, tmp_path):
    import types

    class WhisperModel:
        def __init__(self, *a, **kw):
            pass

        def transcribe(self, *a, **kw):
            def sinh():
                raise RuntimeError("hết bộ nhớ")
                yield
            return sinh(), None

    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=WhisperModel))
    with pytest.raises(LoiKit, match="hết bộ nhớ"):
        chay(str(am), "--out-dir", str(tmp_path / "stt"), "--adapter", "whisper")
