"""giong: đọc giọng ElevenLabs (có mốc thời gian), ra WAV 48 kHz mono 16-bit và mốc từng chữ.

Cũng chứa lớp gửi HTTP dùng chung của chep_loi và tieng_dong: gui_http (một lượt gửi, chỗ để test thay)
và goi_api (thử lại 429/5xx, dịch lỗi API ra câu có mã và thông điệp, không bao giờ in tiêu đề/khoá).
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import time
import wave
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from chung import LoiKit, ghi_nguyen_tu, khoa

API = "https://api.elevenlabs.io"
MAX_KY_TU = 5000
SO_LAN_THU_LAI = 3
CHO_MAC_DINH = (15, 30, 45)  # giây, khi API không gửi Retry-After
CHO_TOI_DA = 120
TAN_SO = 48000


# ---------- HTTP dùng chung ----------

def gui_http(method: str, url: str, *, headers: dict, json_body: dict | None = None, data=None,
             files=None, params=None, timeout: float = 300):
    """Một lượt gửi, trả requests.Response. Test thay hàm này bằng hàm giả. requests nạp tại đây để các lệnh
    không cần mạng (kiem, tron, master, ghep, -h) chạy được khi máy chưa cài requests."""
    try:
        import requests
    except ImportError as e:
        raise LoiKit("thiếu thư viện requests. Cài bằng: python -m pip install -r requirements.txt") from e
    try:
        return requests.request(method, url, headers=headers, json=json_body, data=data, files=files,
                                params=params, timeout=timeout)
    except requests.RequestException as e:
        raise LoiKit(f"không gọi được {url.split('?')[0]}: {type(e).__name__} (kiểm tra mạng, thử lại; "
                     f"nếu tệp lớn thì có thể máy chủ đã nhận và tính phí)") from e


def thong_diep_loi(r) -> str:
    """Lấy câu lỗi của API từ thân phản hồi (ElevenLabs: detail.message hoặc detail[].msg; Deepgram: err_msg)."""
    try:
        d = r.json()
    except ValueError:
        return (r.text or "").strip()[:300] or "(không có thân lỗi)"
    if isinstance(d, dict):
        ct = d.get("detail", d.get("err_msg", d.get("message", d)))
        if isinstance(ct, dict):
            ma = ct.get("status") or ct.get("code")
            return f"{ma}: {ct.get('message', '')}".strip(": ") if ma or ct.get("message") else json.dumps(ct, ensure_ascii=False)[:300]
        if isinstance(ct, list):
            return "; ".join(str(x.get("msg", x)) if isinstance(x, dict) else str(x) for x in ct)[:300]
        return str(ct)[:300]
    return str(d)[:300]


def _cho_bao_lau(r, lan: int) -> float:
    ra = r.headers.get("Retry-After") if getattr(r, "headers", None) else None
    try:
        if ra is not None:
            return max(1, math.ceil(float(ra)))
    except ValueError:
        pass
    return CHO_MAC_DINH[min(lan, len(CHO_MAC_DINH) - 1)]


def goi_api(method: str, url: str, *, ten: str, **kw):
    """Gửi, thử lại 429/5xx tối đa 3 lần (theo Retry-After hoặc 15/30/45 s, chờ >120 s thì bỏ). Lỗi → LoiKit."""
    for lan in range(SO_LAN_THU_LAI + 1):
        r = gui_http(method, url, **kw)
        if r.status_code < 400:
            return r
        co_the_thu = r.status_code == 429 or r.status_code >= 500
        if co_the_thu and lan < SO_LAN_THU_LAI:
            cho = _cho_bao_lau(r, lan)
            if cho > CHO_TOI_DA:
                raise LoiKit(f"{ten} trả {r.status_code}: {thong_diep_loi(r)} (phải chờ {cho:g} s; "
                             "có thể hết hạn mức, thử lại sau)")
            time.sleep(cho)
            continue
        goi_y = ""
        if r.status_code == 401:
            goi_y = " (khoá sai hoặc hết credit)"
        elif r.status_code == 404:
            goi_y = " (kiểm tra mã giọng/đường dẫn)"
        raise LoiKit(f"{ten} trả {r.status_code}: {thong_diep_loi(r)}{goi_y}")
    raise LoiKit(f"{ten}: hết lượt thử lại")  # không tới được; giữ cho kiểu trả về


def tieu_de_xi(ten_khoa: str = "ELEVENLABS_API_KEY") -> dict:
    return {"xi-api-key": khoa(ten_khoa)}


def ghi_wav(duong: Path, pcm: bytes, tan_so: int = TAN_SO, so_kenh: int = 1) -> None:
    with wave.open(str(duong), "wb") as w:
        w.setnchannels(so_kenh)
        w.setsampwidth(2)
        w.setframerate(tan_so)
        w.writeframes(pcm)


# ---------- giọng ----------

def chu_tu_alignment(al: dict | None) -> list[dict]:
    """Mốc ký tự → mốc từng chữ; cắt ở khoảng trắng, dấu câu dính chữ, thẻ [..] cũng là một «chữ»."""
    if not al:
        return []
    ky_tu = al.get("characters") or []
    bat = al.get("character_start_times_seconds") or []
    ket = al.get("character_end_times_seconds") or []
    ra, cur = [], None
    for i, c in enumerate(ky_tu):
        if c.isspace():
            cur = None
            continue
        if cur is None:
            cur = {"text": "", "start_ms": round(bat[i] * 1000), "end_ms": 0}
            ra.append(cur)
        cur["text"] += c
        cur["end_ms"] = round(ket[i] * 1000)
    return ra


def dung_body(text: str, model: str, lang: str | None, prev: str | None, nxt: str | None,
              cai_dat: dict) -> dict:
    body: dict = {"text": text, "model_id": model}
    if lang:
        body["language_code"] = lang
    if prev:
        body["previous_text"] = prev
    if nxt:
        body["next_text"] = nxt
    if cai_dat:
        body["voice_settings"] = cai_dat
    return body


def dang_ky(p: argparse.ArgumentParser) -> None:
    p.add_argument("text", nargs="?", help="lời cần đọc (hoặc dùng --text-file)")
    p.add_argument("--text-file", help="tệp lời (UTF-8, cắt khoảng trắng đầu cuối)")
    p.add_argument("--voice", required=True, help="mã giọng ElevenLabs")
    p.add_argument("--model", default="eleven_v4")
    p.add_argument("--lang", default="vi", help="language_code, mặc định vi")
    p.add_argument("--out", help="tệp .wav ra (mặc định ./giong-<ngày giờ>.wav)")
    p.add_argument("--json", action="store_true", help="in kết quả json (lược đồ results[].words[] mà cat-cau.py, dung-duong-giong.py đọc)")
    p.add_argument("--prev", help="previous_text: câu liền trước, để giữ giọng điệu liền mạch")
    p.add_argument("--next", help="next_text: câu liền sau")
    p.add_argument("--stability", type=float)
    p.add_argument("--similarity", type=float, help="similarity_boost")
    p.add_argument("--style", type=float)
    p.add_argument("--speed", type=float)
    p.add_argument("--force", action="store_true", help="ghi đè tệp ra đã có")


def _lay_loi(a: argparse.Namespace) -> str:
    if a.text and a.text_file:
        raise LoiKit("đưa lời bằng đối số HOẶC --text-file, không cả hai")
    if a.text_file:
        try:
            chu = Path(a.text_file).read_text(encoding="utf-8-sig").strip()
        except OSError as e:
            raise LoiKit(f"không đọc được {a.text_file}: {e.strerror}") from e
    else:
        chu = (a.text or "").strip()
    if not chu:
        raise LoiKit("thiếu lời cần đọc (đối số hoặc --text-file)")
    if len(chu) > MAX_KY_TU:
        raise LoiKit(f"lời dài {len(chu)} ký tự, quá trần {MAX_KY_TU}. Chia lượt ở ranh chương rồi đọc từng lượt.")
    return chu


def chay(a: argparse.Namespace) -> int:
    chu = _lay_loi(a)
    out = Path(a.out) if a.out else Path(f"giong-{datetime.now():%Y%m%d-%H%M%S}.wav")
    if out.suffix.lower() != ".wav":
        raise LoiKit("--out phải có đuôi .wav")
    if out.exists() and not a.force:
        raise LoiKit(f"{out} đã có; thêm --force để ghi đè")
    cai_dat = {k: v for k, v in (("stability", a.stability), ("similarity_boost", a.similarity),
                                 ("style", a.style), ("speed", a.speed)) if v is not None}
    body = dung_body(chu, a.model, a.lang, a.prev, a.next, cai_dat)
    headers = {**tieu_de_xi(), "content-type": "application/json"}
    ma_giong = quote(a.voice, safe="")
    url = f"{API}/v1/text-to-speech/{ma_giong}/with-timestamps?output_format=pcm_48000"
    r = goi_api("POST", url, ten="ElevenLabs (giọng)", headers=headers, json_body=body, timeout=300)
    try:
        d = r.json()
        pcm = base64.b64decode(d["audio_base64"])
    except (ValueError, KeyError, TypeError) as e:
        raise LoiKit("ElevenLabs trả dữ liệu không đúng dạng (thiếu audio_base64)") from e
    chu_moc = chu_tu_alignment(d.get("alignment") or d.get("normalized_alignment"))
    with ghi_nguyen_tu(out, ghi_de=True) as tam:
        ghi_wav(tam, pcm)
    kq = {"out": str(out.resolve()), "duration": round(len(pcm) / 2 / TAN_SO, 3), "sampleRate": TAN_SO,
          "voice": a.voice}
    if chu_moc:
        kq["words"] = chu_moc
    if a.json:
        print(json.dumps({"adapter": "elevenlabs", "results": [kq]}, ensure_ascii=False, indent=2))
    else:
        print(f"✓ {kq['out']} ({kq['duration']} s, {len(chu_moc)} chữ)")
    return 0
