"""Quét chữ cho người xem (kịch bản, tiêu đề, mô tả, chữ trên hình) theo bộ lọc chính sách YouTube.

Danh sách mẫu ở tu-cam.tsv cạnh file này. Luật đầy đủ: kenh/bo-loc-chinh-sach-yt.md.

Dùng:
  python -I tools/loc-chinh-sach/quet.py <file> [<file> ...]               # kịch bản, lời đọc
  python -I tools/loc-chinh-sach/quet.py --tieu-de <file> [<file> ...]     # tiêu đề, chữ ảnh bìa, mô tả, thẻ
  python -I tools/loc-chinh-sach/quet.py -h | --help                      # in hướng dẫn này, mã thoát 0
  (--vi-tri metadata là tên khác của --tieu-de; --vi-tri than là quét như kịch bản.) File .srt: câu bắt đầu trong 30 s đầu xét gắt như tiêu đề.

Từ điển gộp hai nguồn (03/11/2026): mẫu riêng của kênh và từ điển bộ lọc YouTube dùng chung (nhóm yt_*).

Mã thoát: 0 = sạch hoặc chỉ có CẢNH BÁO; 1 = có lỗi CHẶN; 2 = lỗi cách dùng.
Lỗi CHẶN phải sửa trước khi làm giọng. CẢNH BÁO phải có người xem lại ngữ cảnh.
"""
from __future__ import annotations

import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DS_MAU = Path(__file__).with_name("tu-cam.tsv")
HOOK_GIAY = 30.0  # phụ đề: câu bắt đầu trước mốc này xét gắt như tiêu đề (đoạn mở quyết định người xem ở lại)
SRT_MOC = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->")


@dataclass(frozen=True)
class Mau:
    nhom: str
    muc_do: str
    pham_vi: str
    regex: re.Pattern[str]
    ly_do: str
    thay_bang: str


def doc_mau(duong_dan: Path) -> list[Mau]:
    ds = []
    with duong_dan.open(encoding="utf8", newline="") as f:
        for dong in csv.DictReader(f, delimiter="\t"):
            if dong["muc_do"] not in {"CHAN", "CANH"} or dong["pham_vi"] not in {"tat_ca", "tieu_de"}:
                raise ValueError(f"Dòng sai định dạng trong {duong_dan.name}: {dong}")
            ds.append(Mau(dong["nhom"], dong["muc_do"], dong["pham_vi"],
                          re.compile(dong["mau"], re.IGNORECASE), dong["ly_do"], dong["thay_bang"]))
    return ds


def dong_gat(dong: list[str], la_srt: bool) -> list[bool]:
    """Dòng nào của file .srt thuộc câu bắt đầu trước HOOK_GIAY."""
    gat, bat_dau = [], None
    for d in dong:
        m = SRT_MOC.match(d.strip())
        if m:
            h, p, s, ms = (int(x) for x in m.groups())
            bat_dau = h * 3600 + p * 60 + s + ms / 1000
        gat.append(la_srt and bat_dau is not None and bat_dau < HOOK_GIAY)
    return gat


def quet_file(duong_dan: Path, ds: list[Mau], la_tieu_de: bool) -> list[tuple[int, str, Mau, str]]:
    """Mỗi chỗ khớp (dòng, vị trí) chỉ báo một lần; mẫu CHAN thắng mẫu CANH."""
    ket_qua: dict[tuple[int, int, int], tuple[int, str, Mau, str]] = {}
    cac_dong = duong_dan.read_text(encoding="utf8").splitlines()
    gat = dong_gat(cac_dong, duong_dan.suffix.lower() == ".srt")
    for so_dong, dong in enumerate(cac_dong, start=1):
        for m in ds:
            if m.pham_vi == "tieu_de" and not (la_tieu_de or gat[so_dong - 1]):
                continue
            for k in m.regex.finditer(dong):
                khoa = (so_dong, k.start(), k.end())
                cu = ket_qua.get(khoa)
                if cu is None or (cu[2].muc_do == "CANH" and m.muc_do == "CHAN"):
                    ket_qua[khoa] = (so_dong, k.group(0), m, dong.strip())
    # chỗ khớp nằm gọn trong một chỗ khớp dài hơn cùng dòng, mức không thấp hơn, thì không báo lại («máu» trong «đẫm máu»)
    hang = {"CANH": 0, "CHAN": 1}
    giu = [k for k in ket_qua
           if not any(k2 != k and k2[0] == k[0] and k2[1] <= k[1] and k[2] <= k2[2]
                      and hang[ket_qua[k2][2].muc_do] >= hang[ket_qua[k][2].muc_do] for k2 in ket_qua)]
    return [ket_qua[k] for k in sorted(giu)]


def main(argv: list[str]) -> int:
    if any(a in ("-h", "--help") for a in argv):
        sys.stdout.reconfigure(encoding="utf-8")
        print(__doc__)
        return 0
    argv = [x for a in argv for x in (a.split("=", 1) if a.startswith("--vi-tri=") else [a])]
    if "--vi-tri" in argv:  # tên cũ của bộ lọc YouTube dùng chung: --vi-tri metadata|than
        i = argv.index("--vi-tri")
        vi_tri = argv[i + 1] if i + 1 < len(argv) else ""
        if vi_tri not in {"metadata", "than"}:
            print("--vi-tri chỉ nhận metadata hoặc than")
            return 2
        del argv[i:i + 2]
        if vi_tri == "metadata":
            argv.append("--tieu-de")
    la_tieu_de = "--tieu-de" in argv
    files = [Path(a) for a in argv if a != "--tieu-de"]
    if not files:
        print(__doc__)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    ds = doc_mau(DS_MAU)
    so_chan = so_canh = 0
    for f in files:
        if not f.is_file():
            print(f"KHÔNG THẤY FILE: {f}")
            return 2
        for so_dong, tu, m, dong in quet_file(f, ds, la_tieu_de):
            nhan = "CHẶN" if m.muc_do == "CHAN" else "CẢNH BÁO"
            so_chan += m.muc_do == "CHAN"
            so_canh += m.muc_do == "CANH"
            print(f"[{nhan}] {f.name}:{so_dong} «{tu}» ({m.nhom}) {m.ly_do}. Thay: {m.thay_bang}")
            print(f"    {dong[:160]}")
    loai = "tiêu đề, bìa, mô tả" if la_tieu_de else "kịch bản, lời đọc"
    print(f"\nTổng ({loai}): {so_chan} CHẶN, {so_canh} CẢNH BÁO.")
    return 1 if so_chan else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
