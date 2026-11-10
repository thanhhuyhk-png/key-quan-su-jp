"""Lệnh nhac-ai33 và tieng-ai33: nhạc nền (Suno) và tiếng động (ElevenLabs SFX) qua ai33.pro.

Thêm theo yêu cầu của người dùng (07/11/2026, P5 EP001: «ai33 Suno + SFX», được viết thêm lệnh vào kit; mỗi lần sinh báo credit trước).
Khoá: AI33_API_KEY (chung.khoa, không in giá trị). Mặc định chỉ XEM TRƯỚC (không tốn credit): in việc sẽ gọi, credit ước tính, số dư.
Thêm --yes mới gọi thật. Mỗi lần gửi ghi <tên>.ai33_task.json cạnh tệp ra; --resume <tệp đó> chỉ chờ và tải, không tốn thêm.

  kit.py tieng-ai33 --text "LVT engine idling, waves" --giay 4 --out lvt.mp3            # xem trước: 4 s × 60 = 240 credit
  kit.py tieng-ai33 --text "..." --giay 4 --out lvt.mp3 --yes                            # tạo thật
  kit.py nhac-ai33 --mo-ta "dark cinematic war documentary underscore, low strings" --out c1.mp3          # xem trước
  kit.py nhac-ai33 --mo-ta "..." --out c1.mp3 --yes        # Suno trả 2 bản: c1-1.mp3, c1-2.mp3

Giá (trang API ai33.pro, đọc 07/11/2026): tiếng động 60 credit mỗi giây khai (làm tròn lên, tối thiểu 60), để tự động thì 300;
Suno: tài liệu chỉ có ví dụ credit_cost 3600 mỗi task, giá thật in sau khi xong.
Giấy phép: ghi nguồn, giấy phép từng tệp vào kit/ASSETS.tsv; nhạc Suno qua bên thứ ba thì quyền thương mại phụ thuộc gói Suno của ai33, cần người dùng xác nhận.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from ai33 import API, UA, _tieu_de
from chung import LoiKit, ghi_nguyen_tu
from giong import goi_api, gui_http

SFX_MOI_GIAY, SFX_TU_DONG, SUNO_UOC = 60, 300, 3600


def _chung(p: argparse.ArgumentParser) -> None:
    p.add_argument("--out", required=False, help="tệp .mp3 ra")
    p.add_argument("--yes", action="store_true", help="gọi thật (tốn credit)")
    p.add_argument("--timeout", type=int, default=900)
    p.add_argument("--resume", help="tệp <tên>.ai33_task.json của lần gửi trước: chỉ chờ và tải")


def dang_ky_tieng_ai33(p: argparse.ArgumentParser) -> None:
    p.add_argument("--text", help="mô tả tiếng (≤ 450 ký tự, tiếng Anh)")
    p.add_argument("--giay", type=float, default=None, help="độ dài 0,5–30 s (bỏ trống = tự động, 300 credit)")
    p.add_argument("--loop", action="store_true")
    p.add_argument("--anh-huong", type=float, default=0.3, help="prompt_influence 0–1")
    _chung(p)


def dang_ky_nhac_ai33(p: argparse.ArgumentParser) -> None:
    p.add_argument("--mo-ta", help="mô tả nhạc cho Suno (1–500 ký tự)")
    p.add_argument("--co-loi", action="store_true", help="có lời hát (mặc định không lời)")
    _chung(p)


def _so_du() -> float | None:
    tdj = dict(_tieu_de(), **{"Content-Type": "application/json"})
    return (goi_api("GET", f"{API}/v1/credits", ten="ai33", headers=tdj, timeout=60).json() or {}).get("credits")


def _gui(duong: str, than: dict, out: Path, uoc: int, mo_ta: str, yes: bool, timeout: int) -> int:
    so_du = _so_du()
    print(f"{mo_ta} · ước tính ~{uoc} credit · số dư {so_du}")
    if so_du is not None and so_du < uoc * 1.1:
        raise LoiKit("số dư không đủ")
    if not yes:
        print("CHƯA GỌI (xem trước). Thêm --yes để tạo thật.")
        return 0
    r = goi_api("POST", f"{API}{duong}", ten="ai33", headers=dict(_tieu_de(), **{"Content-Type": "application/json"}),
                data=json.dumps(than).encode("utf-8"), timeout=120).json()
    tid = r.get("task_id")
    if not tid:
        raise LoiKit("ai33 không trả task_id: " + json.dumps(r, ensure_ascii=False)[:300])
    out.parent.mkdir(parents=True, exist_ok=True)
    (out.parent / f"{out.stem}.ai33_task.json").write_text(json.dumps({"task_id": tid, "duong": duong, "than": than}, ensure_ascii=False), encoding="utf-8")
    print(f"Đã gửi task {tid[:8]}…, chờ…")
    return _cho_va_tai(tid, out, timeout)


def _tai(url: str, dich: Path) -> None:
    rr = gui_http("GET", url, headers={"User-Agent": UA}, timeout=300)
    if rr.status_code >= 400:
        raise LoiKit(f"tải {url[:60]} lỗi {rr.status_code}")
    with ghi_nguyen_tu(dich) as tam:
        tam.write_bytes(rr.content)
    print(f"  đã lưu {dich}")


def _cho_va_tai(tid: str, out: Path, het_gio: int) -> int:
    tdj = dict(_tieu_de(), **{"Content-Type": "application/json"})
    t0 = time.time()
    while True:
        r = gui_http("GET", f"{API}/v1/task/{tid}", headers=tdj, timeout=60)
        if r.status_code >= 400:
            if time.time() - t0 < 120:
                time.sleep(10)
                continue
            raise LoiKit(f"không đọc được task {tid}: {r.status_code}")
        t = r.json()
        if t.get("status") == "done":
            break
        if t.get("status") == "error":
            raise LoiKit(f"task lỗi: {t.get('error_message')}")
        if time.time() - t0 > het_gio:
            raise LoiKit(f"quá {het_gio} giây chưa xong (task {tid}); không gửi lại. Chạy lại với --resume")
        time.sleep(5)
    m = t.get("metadata") or {}
    urls = m.get("all_audio_urls") or [u for u in (m.get("output_uri"), m.get("audio_url"), t.get("output_uri")) if u][:1]
    if not urls:
        raise LoiKit("task xong nhưng không có đường tải")
    if len(urls) == 1:
        _tai(urls[0], out)
    else:
        for i, u in enumerate(urls, 1):
            _tai(u, out.with_name(f"{out.stem}-{i}{out.suffix or '.mp3'}"))
    print(f"Xong. Tốn {t.get('credit_cost')} credit.")
    return 0


def _resume(a: argparse.Namespace) -> int:
    tep = Path(a.resume)
    st = json.loads(tep.read_text(encoding="utf-8"))
    return _cho_va_tai(st["task_id"], tep.parent / (tep.name.replace(".ai33_task.json", "") + ".mp3"), a.timeout)


def chay_tieng_ai33(a: argparse.Namespace) -> int:
    if a.resume:
        return _resume(a)
    if not a.text or not a.out:
        raise LoiKit("cần --text và --out")
    if len(a.text) > 450:
        raise LoiKit("mô tả quá 450 ký tự")
    if a.giay is not None and not 0.5 <= a.giay <= 30:
        raise LoiKit("--giay phải trong 0,5–30")
    uoc = SFX_TU_DONG if a.giay is None else max(60, math.ceil(a.giay) * SFX_MOI_GIAY)
    than = {"text": a.text, "duration_seconds": a.giay, "prompt_influence": a.anh_huong, "loop": a.loop, "model_id": "eleven_text_to_sound_v3"}
    return _gui("/v1/task/sound-effect", than, Path(a.out), uoc, f"Tiếng động «{a.text[:60]}» · {a.giay or 'tự động'} s", a.yes, a.timeout)


def chay_nhac_ai33(a: argparse.Namespace) -> int:
    if a.resume:
        return _resume(a)
    if not a.mo_ta or not a.out:
        raise LoiKit("cần --mo-ta và --out")
    if not 1 <= len(a.mo_ta) <= 500:
        raise LoiKit("mô tả 1–500 ký tự")
    than = {"create_mode": "simple", "gpt_description_prompt": a.mo_ta, "make_instrumental": not a.co_loi}
    return _gui("/v1s/task/music-generation", than, Path(a.out), SUNO_UOC,
                f"Nhạc Suno «{a.mo_ta[:60]}» ({'có lời' if a.co_loi else 'không lời'}; giá thật in sau khi xong)", a.yes, a.timeout)


dang_ky = dang_ky_tieng_ai33
chay = chay_tieng_ai33
