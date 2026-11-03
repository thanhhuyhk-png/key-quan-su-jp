"""Phần dùng chung của kit: lỗi có hướng dẫn, đọc khoá API (không in), gọi ffmpeg, ghi tệp nguyên tử."""
from __future__ import annotations

import math
import os
import subprocess
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

class LoiKit(Exception):
    """Lỗi có câu hướng dẫn cho người dùng (không kèm khoá, không kèm vết ngăn xếp)."""


REPO = next((p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists()), None)
if REPO is None:
    raise LoiKit("không tìm thấy gốc repo (thư mục có cau-hinh.mau.toml) phía trên tools/kit. "
                 "Chạy kit từ bản chép đầy đủ của repo Goha Lịch Sử, đừng chép riêng thư mục tools/kit.")
TEP_KHOA = REPO / ".env"  # không lên Git (.gitignore); mẫu: khoa-api.mau


def json_an_toan(x):
    """Đổi inf/nan (vd LUFS của bản lặng = -inf) thành None để json.dumps ra JSON hợp lệ, không có -Infinity/NaN."""
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    if isinstance(x, dict):
        return {k: json_an_toan(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [json_an_toan(v) for v in x]
    return x


def doc_tep_khoa(chu: str) -> dict[str, str]:
    """Đọc các dòng TEN=giá trị (bỏ dòng trống, dòng #, ngoặc kép bao ngoài, BOM)."""
    ra: dict[str, str] = {}
    for dong in chu.lstrip("﻿").splitlines():
        dong = dong.strip()
        if not dong or dong.startswith("#") or "=" not in dong:
            continue
        ten, gia_tri = dong.split("=", 1)
        gia_tri = gia_tri.strip()
        if len(gia_tri) >= 2 and gia_tri[0] == gia_tri[-1] and gia_tri[0] in "\"'":
            gia_tri = gia_tri[1:-1]
        ra[ten.strip().removeprefix("export ").strip()] = gia_tri
    return ra


def khoa(ten: str, tep: Path | None = None) -> str:
    """Giá trị khoá API: biến môi trường trước, rồi tệp khoá ở gốc repo. Thiếu thì dừng, nói rõ cách thêm."""
    gia_tri = os.environ.get(ten, "").strip()
    if not gia_tri:
        tep = tep or TEP_KHOA
        if tep.exists():
            gia_tri = doc_tep_khoa(tep.read_text(encoding="utf-8")).get(ten, "").strip()
    if not gia_tri:
        raise LoiKit(f"thiếu khoá {ten}. Thêm dòng «{ten}=<khoá của bạn>» vào {TEP_KHOA.name} ở gốc repo "
                     f"(chép từ khoa-api.mau), hoặc đặt biến môi trường {ten}.")
    return gia_tri


def co_khoa(ten: str, tep: Path | None = None) -> bool:
    """Có khoá hay không (không trả giá trị)."""
    try:
        khoa(ten, tep)
        return True
    except LoiKit:
        return False


def chay_lenh(lenh: list[str], *, dau_vao: bytes | None = None, cwd: Path | str | None = None) -> subprocess.CompletedProcess:
    """Chạy lệnh ngoài (ffmpeg, ffprobe) bằng danh sách đối số, không qua shell. Hỏng thì LoiKit kèm 12 dòng cuối."""
    if lenh and Path(lenh[0]).stem.lower() == "ffmpeg" and "-nostdin" not in lenh and dau_vao is None:
        lenh = [lenh[0], "-nostdin", *lenh[1:]]
    try:
        r = subprocess.run(lenh, input=dau_vao, capture_output=True, cwd=cwd)
    except FileNotFoundError as e:
        raise LoiKit(f"không tìm thấy {lenh[0]}. Cài bằng: winget install Gyan.FFmpeg (rồi mở lại cửa sổ lệnh)") from e
    if r.returncode != 0:
        duoi = "\n".join(r.stderr.decode("utf-8", "replace").strip().splitlines()[-12:])
        raise LoiKit(f"{Path(lenh[0]).name} thoát mã {r.returncode}:\n{duoi}")
    return r


@contextmanager
def ghi_nguyen_tu(dich: Path, ghi_de: bool = True) -> Iterator[Path]:
    """Cho đường dẫn tạm cạnh đích (giữ đuôi tệp); xong thì đổi tên sang đích. Lỗi thì xoá tệp tạm."""
    dich = Path(dich)
    if dich.exists() and not ghi_de:
        raise LoiKit(f"{dich} đã có; thêm --force để ghi đè")
    dich.parent.mkdir(parents=True, exist_ok=True)
    tam = dich.with_name(f"{dich.stem}.part{dich.suffix}")
    try:
        yield tam
        os.replace(tam, dich)
    finally:
        if tam.exists():
            tam.unlink()
