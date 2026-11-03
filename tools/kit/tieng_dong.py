"""tieng-dong: tạo tiếng động ElevenLabs từ mô tả tiếng Anh, ghi .mp3/.wav và một dòng vào kit/ASSETS.tsv."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import giong as g
from chung import REPO, LoiKit, chay_lenh, ghi_nguyen_tu

ASSETS = REPO / "kit" / "ASSETS.tsv"
URL = f"{g.API}/v1/sound-generation"
GIAY_PHEP = "ElevenLabs — dùng thương mại theo gói trả phí"
# pcm_48000 của sound-generation là stereo 16-bit xen kẽ (đo thật 03/11/2026: xin 5 s nhận 960 000 byte).
KENH_PCM = 2


def do_dai_s(duong: Path) -> str:
    """Độ dài (giây, 2 số lẻ) đo bằng ffprobe; không đo được thì để trống."""
    try:
        r = chay_lenh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                       "default=nw=1:nk=1", str(duong)])
        return f"{float(r.stdout.decode().strip()):.2f}"
    except (LoiKit, ValueError):
        return ""


def duong_trong_kho(out: Path, tsv: Path) -> str:
    """Đường dẫn tương đối (dấu /) nếu tệp nằm dưới thư mục chứa ASSETS.tsv, không thì như người dùng đưa."""
    try:
        return out.resolve().relative_to(tsv.resolve().parent).as_posix()
    except ValueError:
        return str(out).replace("\\", "/")


def ghi_assets(tsv: Path, out: Path, mo_ta: str, nhom: str | None, dai: str, ngay: str) -> bool:
    """Thêm một dòng theo các cột sẵn có. Trả False nếu đã có dòng cùng tệp (không ghi trùng)."""
    chu = tsv.read_text(encoding="utf-8")
    dong = chu.splitlines()
    cot = dong[0].split("\t")
    tep = duong_trong_kho(out, tsv)
    if any(d.split("\t", 1)[0] == tep for d in dong[1:]):
        return False
    gia_tri = {"tep": tep, "nhom": nhom or out.resolve().parent.name,
               "mo_ta_prompt": " ".join(mo_ta.split()),
               "nguon_ngay": f"ElevenLabs SFX (kit tieng-dong), {ngay}", "giay_phep": GIAY_PHEP, "dai_s": dai}
    hang = "\t".join(gia_tri.get(c, "") for c in cot)
    with tsv.open("a", encoding="utf-8", newline="") as f:
        f.write(("" if chu.endswith("\n") else "\n") + hang + "\n")
    return True


def dang_ky(p: argparse.ArgumentParser) -> None:
    p.add_argument("mo_ta", metavar="mô_tả", help="mô tả tiếng động, tiếng Anh")
    p.add_argument("--out", required=True, help="tệp ra .mp3 hoặc .wav")
    p.add_argument("--duration", type=float, help="giây, 0.5 đến 30")
    p.add_argument("--influence", type=float, help="prompt_influence, 0 đến 1")
    p.add_argument("--loop", action="store_true")
    p.add_argument("--nhom", help="nhóm ghi vào ASSETS.tsv (mặc định: tên thư mục chứa tệp)")
    p.add_argument("--force", action="store_true", help="ghi đè tệp ra đã có")


def chay(a: argparse.Namespace) -> int:
    mo_ta = a.mo_ta.strip()
    if not mo_ta:
        raise LoiKit("thiếu mô tả tiếng động")
    out = Path(a.out)
    dinh_dang = {".mp3": "mp3_44100_128", ".wav": "pcm_48000"}.get(out.suffix.lower())
    if not dinh_dang:
        raise LoiKit("--out phải có đuôi .mp3 hoặc .wav")
    if a.duration is not None and not 0.5 <= a.duration <= 30:
        raise LoiKit("--duration phải trong khoảng 0.5 đến 30 giây")
    if a.influence is not None and not 0 <= a.influence <= 1:
        raise LoiKit("--influence phải trong khoảng 0 đến 1")
    if out.exists() and not a.force:
        raise LoiKit(f"{out} đã có; thêm --force để ghi đè")
    body: dict = {"text": mo_ta, "model_id": "eleven_text_to_sound_v2"}
    if a.duration is not None:
        body["duration_seconds"] = a.duration
    if a.influence is not None:
        body["prompt_influence"] = a.influence
    if a.loop:
        body["loop"] = True
    r = g.goi_api("POST", f"{URL}?output_format={dinh_dang}", ten="ElevenLabs (tiếng động)",
                  headers={**g.tieu_de_xi(), "content-type": "application/json"}, json_body=body, timeout=300)
    if not r.content:
        raise LoiKit("ElevenLabs trả về tệp rỗng")
    with ghi_nguyen_tu(out, ghi_de=True) as tam:
        if out.suffix.lower() == ".wav":
            g.ghi_wav(tam, r.content, g.TAN_SO, KENH_PCM)
        else:
            tam.write_bytes(r.content)
    dai = do_dai_s(out)
    print(f"✓ {out} ({dai or '?'} s)")
    if not ASSETS.exists():
        print(f"! không thấy {ASSETS}, bỏ qua ghi kho tài sản")
    elif ghi_assets(ASSETS, out, mo_ta, a.nhom, dai, datetime.now().strftime("%d/%m/%Y")):
        print(f"  đã ghi 1 dòng vào {ASSETS.name}")
    else:
        print(f"  {ASSETS.name} đã có dòng cho tệp này, không ghi trùng")
    return 0
