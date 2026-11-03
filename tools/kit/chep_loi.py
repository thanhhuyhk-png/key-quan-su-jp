"""chep-loi: chép lời từ âm thanh/video bằng ElevenLabs Scribe, Deepgram hoặc Whisper chạy trên máy, ra <tên>.words.json và <tên>.txt.

Ba adapter quy về CÙNG lược đồ words.json (phong bì + words[{id, ordinal, text, start_ms, end_ms,
speaker, audio_event}]) để so-loi và các script dựng đọc như nhau. ElevenLabs, Deepgram trả phí theo từng lần gọi;
Whisper (thư viện faster-whisper) miễn phí, không cần khoá, nhưng chậm trên CPU (mức chạy Miễn phí).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

import giong as g
from chung import LoiKit, chay_lenh, khoa

URL_SCRIBE = f"{g.API}/v1/speech-to-text"
URL_DEEPGRAM = "https://api.deepgram.com/v1/listen"


def trich_mp3(nguon: Path, dich: Path) -> int:
    """Trích âm mono 16 kHz mp3; trả độ dài (ms) đo trên tệp mp3."""
    chay_lenh(["ffmpeg", "-y", "-i", str(nguon), "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000",
               "-b:a", "64k", "-f", "mp3", str(dich)])
    r = chay_lenh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1",
                   str(dich)])
    try:
        return round(float(r.stdout.decode().strip()) * 1000)
    except ValueError as e:
        raise LoiKit(f"không đo được độ dài âm của {nguon.name}") from e


def _sua_thoi_gian(ds: list[dict], dai_ms: int) -> list[dict]:
    """Kẹp vào [0, độ dài]; chữ dài 0 thì cho ≤ 200 ms nhưng không quá chữ kế."""
    for i, w in enumerate(ds):
        w["start_ms"] = max(0, min(w["start_ms"], dai_ms))
        w["end_ms"] = max(w["start_ms"], min(w["end_ms"], dai_ms))
        if w["end_ms"] == w["start_ms"]:
            ke = ds[i + 1]["start_ms"] if i + 1 < len(ds) else dai_ms
            w["end_ms"] = min(w["start_ms"] + 200, max(ke, w["start_ms"]))
    return ds


def tu_scribe(d: dict, dai_ms: int) -> list[dict]:
    """Phản hồi Scribe: words[{text,start,end,type: word|spacing|audio_event, speaker_id}]."""
    ra = []
    for w in d.get("words", []):
        loai = w.get("type", "word")
        if loai == "spacing" or w.get("start") is None or w.get("end") is None:
            continue
        su_kien = loai == "audio_event"
        chu = str(w.get("text", "")).strip()
        if su_kien and not chu.startswith("("):
            chu = f"({chu.strip('()[]')})"
        sp = str(w.get("speaker_id") or "")
        so_sp = sp.rsplit("_", 1)[-1]
        ra.append({"text": chu, "start_ms": round(w["start"] * 1000), "end_ms": round(w["end"] * 1000),
                   "speaker": str(int(so_sp) + 1) if so_sp.isdigit() else "", "audio_event": su_kien})
    return _sua_thoi_gian(ra, dai_ms)


def tu_deepgram(d: dict, dai_ms: int) -> list[dict]:
    """Phản hồi Deepgram: results.channels[0].alternatives[0].words[{word,start,end,punctuated_word,speaker?}]."""
    try:
        ds = d["results"]["channels"][0]["alternatives"][0].get("words", [])
    except (KeyError, IndexError, TypeError) as e:
        raise LoiKit("Deepgram trả dữ liệu không đúng dạng (thiếu results.channels[0].alternatives[0])") from e
    ra = [{"text": w.get("punctuated_word") or w["word"], "start_ms": round(w["start"] * 1000),
           "end_ms": round(w["end"] * 1000),
           "speaker": str(w["speaker"] + 1) if isinstance(w.get("speaker"), int) else "", "audio_event": False}
          for w in ds]
    return _sua_thoi_gian(ra, dai_ms)


def tu_whisper(doan, dai_ms: int) -> list[dict]:
    """Kết quả faster-whisper (word_timestamps=True): các đoạn có .words[{word, start, end}], chữ có khoảng trắng đầu."""
    ra = [{"text": w.word.strip(), "start_ms": round(w.start * 1000), "end_ms": round(w.end * 1000), "speaker": "",
           "audio_event": False} for d in doan for w in (d.words or []) if w.word.strip()]
    return _sua_thoi_gian(ra, dai_ms)


def chep_whisper(mp3: Path, model: str, lang: str, dai_ms: int) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise LoiKit("adapter whisper cần thư viện faster-whisper: python -m pip install faster-whisper "
                     "(lần đầu tự tải model, cỡ vài trăm MB)") from e
    ngon_ngu = None if lang in ("auto", "") else lang
    try:
        doan, _ = WhisperModel(model, device="auto", compute_type="default").transcribe(
            str(mp3), language=ngon_ngu, word_timestamps=True, vad_filter=False)
        doan = list(doan)  # faster-whisper chép lười: lỗi thật nổ ở đây
    except Exception as e:
        raise LoiKit(f"whisper lỗi khi tải model «{model}» hoặc chép lời: {e}") from e
    return tu_whisper(doan, dai_ms)


def viet_words_json(duong: Path, nguon: Path, mp3_sha: str, dai_ms: int, nha: str, model: str, lang: str,
                    ds: list[dict]) -> None:
    for i, w in enumerate(ds):
        w.update(id=f"word_{i + 1:06d}", ordinal=i)
    dau = {"source": nguon.name, "source_sha256": mp3_sha, "audio_duration_ms": dai_ms, "provider": nha,
           "model": model, "outcome": "speech" if any(not w["audio_event"] for w in ds) else "no_recognized_speech",
           "language": lang, "warnings": []}
    khoa_w = ["id", "ordinal", "text", "start_ms", "end_ms", "speaker", "audio_event"]
    dong = [json.dumps({k: w[k] for k in khoa_w}, ensure_ascii=False) for w in ds]
    than = json.dumps(dau, ensure_ascii=False, indent=2)[:-2]  # bỏ "\n}" để nối mục words
    sau = ",\n  \"words\": [\n    " + ",\n    ".join(dong) + "\n  ]\n}\n" if dong else ",\n  \"words\": []\n}\n"
    with g.ghi_nguyen_tu(duong, ghi_de=True) as tam:
        tam.write_text(than + sau, encoding="utf-8")


def dang_ky(p: argparse.ArgumentParser) -> None:
    p.add_argument("nguon", help="tệp âm thanh hoặc video")
    p.add_argument("--out-dir", default="transcript", help="thư mục ra (mặc định transcript/)")
    p.add_argument("--adapter", choices=["elevenlabs", "deepgram", "whisper"], default="elevenlabs")
    p.add_argument("--lang", default="vi")
    p.add_argument("--model", help="mặc định scribe_v1 (ElevenLabs), nova-2 (Deepgram), medium (Whisper)")
    p.add_argument("--force", action="store_true", help="ghi đè tệp ra đã có")


def chep_api(a: argparse.Namespace, model: str, am: bytes, dai_ms: int, timeout: float) -> list[dict]:
    """Adapter qua API (ElevenLabs hoặc Deepgram)."""
    if a.adapter == "elevenlabs":
        r = g.goi_api("POST", URL_SCRIBE, ten="ElevenLabs (chép lời)", headers=g.tieu_de_xi(),
                      data={"model_id": model, "language_code": a.lang, "timestamps_granularity": "word",
                            "diarize": "true", "tag_audio_events": "true"},
                      files={"file": ("am.mp3", am, "audio/mpeg")}, timeout=timeout)
        return tu_scribe(_json(r, "ElevenLabs"), dai_ms)
    r = g.goi_api("POST", URL_DEEPGRAM, ten="Deepgram", timeout=timeout,
                  headers={"Authorization": f"Token {khoa('DEEPGRAM_API_KEY')}", "Content-Type": "audio/mpeg"},
                  params={"model": model, "language": a.lang, "smart_format": "true", "punctuate": "true"},
                  data=am)
    return tu_deepgram(_json(r, "Deepgram"), dai_ms)


def chay(a: argparse.Namespace) -> int:
    nguon = Path(a.nguon)
    if not nguon.is_file():
        raise LoiKit(f"không thấy tệp {nguon}")
    ra = Path(a.out_dir)
    f_words, f_txt = ra / f"{nguon.stem}.words.json", ra / f"{nguon.stem}.txt"
    if not a.force:
        for f in (f_words, f_txt):
            if f.exists():
                raise LoiKit(f"{f} đã có; thêm --force để ghi đè (chưa gọi API, chưa tốn phí)")
    ten_khoa = {"elevenlabs": "ELEVENLABS_API_KEY", "deepgram": "DEEPGRAM_API_KEY"}.get(a.adapter)
    if ten_khoa:
        khoa(ten_khoa)  # thiếu khoá thì dừng trước khi tách âm
    model = a.model or {"elevenlabs": "scribe_v1", "deepgram": "nova-2", "whisper": "medium"}[a.adapter]
    with tempfile.TemporaryDirectory() as tmp:
        mp3 = Path(tmp) / "am.mp3"
        dai_ms = trich_mp3(nguon, mp3)
        am = mp3.read_bytes()
        ds = chep_whisper(mp3, model, a.lang, dai_ms) if a.adapter == "whisper" else None
    sha = hashlib.sha256(am).hexdigest()
    timeout = max(600, 2 * dai_ms / 1000)
    if ds is None:
        ds = chep_api(a, model, am, dai_ms, timeout)
    ra.mkdir(parents=True, exist_ok=True)
    viet_words_json(f_words, nguon, sha, dai_ms, a.adapter, model, a.lang, ds)
    with g.ghi_nguyen_tu(f_txt, ghi_de=True) as tam:
        tam.write_text(" ".join(w["text"] for w in ds if not w["audio_event"]) + "\n", encoding="utf-8")
    print(f"✓ {len(ds)} chữ → {f_words}")
    return 0


def _json(r, ten: str) -> dict:
    try:
        return r.json()
    except ValueError as e:
        raise LoiKit(f"{ten} trả dữ liệu không phải json") from e
