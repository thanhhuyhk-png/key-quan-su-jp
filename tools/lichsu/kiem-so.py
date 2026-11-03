"""Đối chiếu câu trích nguyên văn trong sổ số liệu với chữ thô của đúng trang nguồn.

Dùng: python -I kiem-so.py <so-so-lieu.csv> <thư mục chữ thô> [--chi-loi]
Thư mục chữ thô chứa các file .txt do lay-trang.py tạo (dòng đầu "URL: ...").
Mỗi dòng sổ có tối đa hai cặp (nguon_N_url, trich_nguyen_van_N). Một cặp đạt khi mọi
mảnh của câu trích (tách ở "…" hoặc "...") nằm trong chữ của trang, sau khi chuẩn hoá
hoa thường, gạch ngang và bỏ hẳn khoảng trắng, dấu ngoặc (chữ và số phải đúng thứ tự).
Kết quả: OK · KHÔNG KHỚP · THIẾU TRANG (chưa tải) · TRỐNG (thiếu url hoặc câu trích).
Mã thoát 1 khi có KHÔNG KHỚP, THIẾU TRANG, hoặc dòng không có nguồn nào.
Dòng chỉ có một nguồn đạt thì báo MỘT NGUỒN (cảnh báo, không chặn).
"""
import csv
import re
import sys
import unicodedata
from pathlib import Path

DOI_KY_TU = str.maketrans({"“": '"', "”": '"', "„": '"', "«": '"', "»": '"',
                           "‘": "'", "’": "'", "–": "-", "—": "-", " ": " "})
MANH_TOI_THIEU = 8


def chuan_hoa(chu: str) -> str:
    chu = unicodedata.normalize("NFC", chu).translate(DOI_KY_TU).lower()
    return re.sub(r"\s+", " ", chu).strip()


def chuan_url(url: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", url.strip()).rstrip("/")


def nap_trang(thu_muc: Path) -> dict[str, str]:
    trang = {}
    for tep in thu_muc.rglob("*.txt"):
        dong_dau, _, than = tep.read_text(encoding="utf-8").partition("\n")
        if dong_dau.startswith("URL: "):
            trang[chuan_url(dong_dau[5:])] = khoa_so(chuan_hoa(than))
    return trang


def khoa_so(chu: str) -> str:
    """Bỏ khoảng trắng và dấu ngoặc: báo khác nhau chỉ vì cách đặt ngoặc thì không tính lệch."""
    return re.sub(r"[\s\"']", "", chu)


def manh_trich(trich: str) -> list[str]:
    tho = re.split(r"[\[(]?\s*(?:…|\.\.\.)\s*[\])]?", chuan_hoa(trich))
    manh = [khoa_so(m).strip(".,;:") for m in tho]
    return [m for m in manh if len(m) >= MANH_TOI_THIEU]


def kiem_cap(url: str, trich: str, trang: dict[str, str]) -> str:
    if not url.strip() or not trich.strip():
        return "TRỐNG"
    chu = trang.get(chuan_url(url))
    if chu is None:
        return "THIẾU TRANG"
    manh = manh_trich(trich)
    if manh and all(m in chu for m in manh):
        return "OK"
    return "KHÔNG KHỚP"


def kiem_dong(dong: dict[str, str], trang: dict[str, str]) -> tuple[list[str], bool]:
    kq = [kiem_cap(dong.get(f"nguon_{i}_url", ""), dong.get(f"trich_nguyen_van_{i}", ""), trang)
          for i in (1, 2)]
    loi = any(k in ("KHÔNG KHỚP", "THIẾU TRANG") for k in kq) or "OK" not in kq
    return kq, loi


def main(doi: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    co = [a for a in doi if a.startswith("--")]
    vi_tri = [a for a in doi if not a.startswith("--")]
    if len(vi_tri) != 2:
        print(__doc__)
        return 2
    trang = nap_trang(Path(vi_tri[1]))
    so_loi = 0
    with open(vi_tri[0], encoding="utf-8-sig", newline="") as f:
        for dong in csv.DictReader(f):
            kq, loi = kiem_dong(dong, trang)
            so_loi += loi
            nhan = "LỖI" if loi else ("MỘT NGUỒN" if kq.count("OK") == 1 else "ĐẠT")
            if loi or "--chi-loi" not in co:
                print(f"[{nhan}] {dong.get('stt', '?')} · {dong.get('du_kien', '')[:60]} · "
                      f"nguồn 1: {kq[0]} · nguồn 2: {kq[1]}")
    print(f"Tổng dòng lỗi: {so_loi}")
    return 1 if so_loi else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
