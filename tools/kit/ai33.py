"""Lệnh giong-ai33: đọc giọng qua ai33.pro (giọng clone của chính người dùng), dùng thay ElevenLabs khi chưa có khoá ElevenLabs.

Khoá: AI33_API_KEY trong .env (hoặc biến môi trường), đọc qua chung.khoa, không in giá trị.
Mặc định chỉ XEM TRƯỚC (không tốn credit): số ký tự, credit ước tính, số dư. Thêm --yes mới đọc thật.
  kit.py giong-ai33 --tim "GOHA"                       # tìm mã giọng theo tên (không tốn credit)
  kit.py giong-ai33 --voice clone_123 --text-file a.txt --out a.mp3        # xem trước
  kit.py giong-ai33 --voice clone_123 --text-file a.txt --out a.mp3 --yes  # đọc thật
Gọi API Text To Dialogue v3 với một người nói (A>; API đòi ≥ 2 speakers nên gửi cùng giọng 2 lần, B không dùng), chờ task, tải mp3 (và srt/json nếu có).
"""
from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path

from chung import LoiKit, ghi_nguyen_tu, khoa
from giong import goi_api, gui_http

API = "https://api.ai33.pro"
TEN_KHOA = "AI33_API_KEY"
CREDIT_MOI_KY_TU = 1.46  # đo 2026-11-06: 332 ký tự (1 giọng clone) tốn 486 credit
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"


def _tieu_de() -> dict:
    return {"xi-api-key": khoa(TEN_KHOA)}


def _multipart(truong: dict) -> tuple[bytes, str]:
    b = uuid.uuid4().hex
    phan = [f'--{b}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode("utf-8") for k, v in truong.items()]
    phan.append(f"--{b}--\r\n".encode())
    return b"".join(phan), f"multipart/form-data; boundary={b}"


def dang_ky(p: argparse.ArgumentParser) -> None:
    p.add_argument("text", nargs="?", help="lời cần đọc (hoặc --text-file)")
    p.add_argument("--text-file")
    p.add_argument("--voice", help="mã giọng ai33, vd clone_1234567")
    p.add_argument("--out", help="tệp .mp3 ra")
    p.add_argument("--speed", type=float, default=1.0)
    p.add_argument("--tim", help="tìm giọng theo tên, in tên và mã (không tốn credit)")
    p.add_argument("--yes", action="store_true", help="đọc thật (tốn credit)")
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--resume", help="tệp <tên>.ai33_task.json của lần gửi trước: chỉ chờ và tải, không tốn thêm credit")


def _tim(chu: str) -> int:
    r = goi_api("GET", f"{API}/v3/voices", ten="ai33", headers=_tieu_de(), params={"provider": "clone", "search": chu, "page_size": 50}, timeout=60)
    ds = (r.json() or {}).get("data", [])
    if not ds:
        print(f"Không thấy giọng nào khớp «{chu}». Mở ai33.pro, chép mã giọng clone (dạng clone_…) rồi dùng --voice.")
    for v in ds:
        print(f"{v.get('name', '')[:50]:<50} {v.get('voice_id')}  {v.get('provider', '')}")
    return 0


def chay(a: argparse.Namespace) -> int:
    if a.tim:
        return _tim(a.tim)
    if a.resume:
        tep = Path(a.resume)
        st = json.loads(tep.read_text(encoding="utf-8"))
        return _cho_va_tai(st["task_id"], tep.parent / (tep.name.replace(".ai33_task.json", "") + ".mp3"), a.timeout)
    if not a.voice or not a.out:
        raise LoiKit("cần --voice và --out (hoặc --tim)")
    loi = Path(a.text_file).read_text(encoding="utf-8").strip() if a.text_file else (a.text or "").strip()
    if not loi:
        raise LoiKit("chưa có lời để đọc")
    van_ban = "\n".join(f"A> {dong.strip()}" for dong in loi.splitlines() if dong.strip())
    uoc = round(len(van_ban) * CREDIT_MOI_KY_TU)
    tdj = dict(_tieu_de(), **{"Content-Type": "application/json"})
    so_du = (goi_api("GET", f"{API}/v1/credits", ten="ai33", headers=tdj, timeout=60).json() or {}).get("credits")
    print(f"Giọng {a.voice} · {len(van_ban)} ký tự · ước tính ~{uoc} credit · số dư {so_du}")
    if so_du is not None and so_du < uoc * 1.1:
        raise LoiKit("số dư không đủ")
    if not a.yes:
        print("CHƯA ĐỌC (xem trước). Thêm --yes để đọc thật.")
        return 0
    than, ct = _multipart({"text": van_ban, "speakers": json.dumps([{"voice_id": a.voice, "speed": a.speed}] * 2),
                           "delay": "0.3", "with_transcript": "true", "file_name": Path(a.out).stem})
    r = goi_api("POST", f"{API}/v3/text-to-speech/dialogue", ten="ai33",
                headers=dict(_tieu_de(), **{"Content-Type": ct}), data=than, timeout=120).json()
    tid = r.get("task_id")
    if not tid:
        raise LoiKit("ai33 không trả task_id: " + json.dumps(r, ensure_ascii=False)[:300])
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    (out.parent / f"{out.stem}.ai33_task.json").write_text(json.dumps({"task_id": tid, "voice": a.voice, "chars": len(van_ban)}), encoding="utf-8")
    print(f"Đã gửi task {tid[:8]}…, chờ…")
    return _cho_va_tai(tid, out, a.timeout)


def _cho_va_tai(tid: str, out: Path, het_gio: int) -> int:
    """Chờ task (không gửi lại lời) rồi tải mp3/srt/json. Lỗi 400 lúc đầu (task chưa vào CSDL) thì chờ tiếp tối đa 2 phút."""
    tdj = dict(_tieu_de(), **{"Content-Type": "application/json"})
    t0 = time.time()
    while True:
        r = gui_http("GET", f"{API}/v1/task/{tid}", headers=tdj, timeout=60)
        if r.status_code >= 400:
            if time.time() - t0 < 120:
                time.sleep(10)
                continue
            raise LoiKit(f"không đọc được task {tid}: {r.status_code}. Chạy lại: kit.py giong-ai33 --resume {out.parent / (out.stem + '.ai33_task.json')}")
        t = r.json()
        if t.get("status") == "done":
            break
        if t.get("status") == "error":
            raise LoiKit(f"task lỗi: {t.get('error_message')}")
        if time.time() - t0 > het_gio:
            raise LoiKit(f"quá {het_gio} giây chưa xong (task {tid}); không gửi lại để tránh tốn credit hai lần")
        time.sleep(5)
    m = t.get("metadata") or {}
    if not m.get("audio_url"):
        raise LoiKit("task xong nhưng không có audio_url")
    for khoa_url, duoi in (("audio_url", out.suffix or ".mp3"), ("srt_url", ".srt"), ("json_url", ".json")):
        if m.get(khoa_url):
            dich = out if khoa_url == "audio_url" else out.with_suffix(duoi)
            rr = gui_http("GET", m[khoa_url], headers={"User-Agent": UA}, timeout=300)
            if rr.status_code >= 400:
                raise LoiKit(f"tải {khoa_url} lỗi {rr.status_code}")
            with ghi_nguyen_tu(dich) as tam:
                tam.write_bytes(rr.content)
            print(f"  đã lưu {dich}")
    print(f"Xong. Tốn {t.get('credit_cost')} credit.")
    return 0
