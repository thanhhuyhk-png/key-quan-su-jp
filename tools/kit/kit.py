"""Bộ lệnh dựng phim của kit Goha (thay CLI ngoài): giọng, chép lời, so lời, trộn, master, ghép, kiểm, tiếng động.

Chạy: python -I -X utf8 tools/kit/kit.py <lệnh> [đối số]   (xem: kit.py <lệnh> -h)

Mỗi lệnh là một mô-đun cùng thư mục, có hai hàm:
    dang_ky(p: argparse.ArgumentParser) -> None   # khai đối số
    chay(a: argparse.Namespace) -> int            # mã thoát: 0 xong (kể cả «không đạt» khi kiểm), 1 lỗi thật
Khoá API đọc qua chung.py (biến môi trường hoặc tệp khoá ở gốc repo), không bao giờ in giá trị.
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from chung import LoiKit  # noqa: E402
except Exception as e:  # chung.py báo thẳng khi chạy ngoài repo: in câu hướng dẫn, không vết ngăn xếp
    sys.exit(f"Lỗi: {e}")

# tên lệnh → (mô-đun, mô tả ngắn)
LENH = {
    "giong": ("giong", "Đọc giọng ElevenLabs, ra WAV 48 kHz và mốc từng chữ"),
    "giong-ai33": ("ai33", "Đọc giọng clone qua ai33.pro (thay ElevenLabs), mặc định chỉ xem trước"),
    "tu-lieu": ("tu_lieu", "Tìm ảnh lưu trữ qua API NARA, DVIDS, Smithsonian, Pexels (miễn phí)"),
    "chep-loi": ("chep_loi", "Chép lời (ElevenLabs Scribe hoặc Deepgram), ra <tên>.words.json"),
    "so-loi": ("so_loi", "So lời chuẩn với words.json, tỉ lệ khớp và chỗ lệch"),
    "tron": ("tron", "Trộn âm theo mix.json (giọng, nhạc, tiếng động)"),
    "master": ("am_cuoi", "Master tăng mức cố định tới LUFS đích + chặn đỉnh"),
    "ghep": ("am_cuoi", "Ghép hình với âm master, đo lại độ to trên file ra"),
    "kiem": ("kiem", "Kiểm file video cuối: độ to, đỉnh, cỡ, fps, khung đen, đứng hình, lặng"),
    "tieng-dong": ("tieng_dong", "Tạo tiếng động ElevenLabs, ghi kho tài sản"),
    "tieng-ai33": ("am_ai33", "Tạo tiếng động ElevenLabs SFX qua ai33.pro, mặc định chỉ xem trước"),
    "nhac-ai33": ("am_ai33", "Tạo nhạc nền Suno qua ai33.pro (2 bản mỗi lần), mặc định chỉ xem trước"),
}


def _utf8_stdio() -> None:
    """Luồng ra bằng UTF-8: stdout chuyển hướng trên Windows mặc định là mã trang ANSI và chết ở «✓» SAU khi API đã tính tiền."""
    for luong in (sys.stdout, sys.stderr):
        if hasattr(luong, "reconfigure"):
            luong.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    ap = argparse.ArgumentParser(prog="kit.py", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="lenh", required=True, metavar="<lệnh>")
    for ten, (mo_dun, mo_ta) in LENH.items():
        p = sub.add_parser(ten, help=mo_ta, description=mo_ta)
        m = importlib.import_module(mo_dun)
        dk = getattr(m, f"dang_ky_{ten.replace('-', '_')}", None) or m.dang_ky
        dk(p)
        p.set_defaults(_mo_dun=m, _ten=ten)
    a = ap.parse_args(argv)
    chay = getattr(a._mo_dun, f"chay_{a._ten.replace('-', '_')}", None) or a._mo_dun.chay
    try:
        return int(chay(a) or 0)
    except LoiKit as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 1
    except OSError as e:
        print(f"Lỗi hệ thống: {e.strerror or e}" + (f" ({e.filename})" if e.filename else "")
              + ". Kiểm tra ổ đĩa còn chỗ, tệp không đang mở ở chương trình khác, quyền ghi thư mục.", file=sys.stderr)
        return 1
    except (ValueError, TypeError, KeyError) as e:
        print(f"Lỗi: dữ liệu đầu vào không đúng dạng ({type(e).__name__}: {e}). Kiểm tra lại tệp json/đối số vừa đưa.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
