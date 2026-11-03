"""Kiểm bảng màu kênh có khác cặp màu kênh mẫu (nền ô-liu #3a4126, nhấn vàng đồng #e2b04a) không.

python -I -X utf8 kiem-mau.py <nen> <nhan> [<mau khac> ...]
Ví dụ: python -I -X utf8 kiem-mau.py "#0f2742" "#ff7a3c"

Mỗi màu đưa vào được so với cả hai màu kênh mẫu. Gần = lệch sắc độ dưới 35 độ (với màu đủ bão hoà)
và lệch độ sáng dưới 0,25. Mã thoát 0 = ĐẠT, 1 = có màu gần kênh mẫu, 2 = sai cách dùng.
"""
import colorsys
import re
import sys

MAU_MAU = {"ô-liu #3a4126": "#3a4126", "vàng đồng #e2b04a": "#e2b04a"}
LECH_SAC_DO = 35.0
LECH_SANG = 0.25
BAO_HOA_TOI_THIEU = 0.15


def hls(h: str) -> tuple[float, float, float]:
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return colorsys.rgb_to_hls(r, g, b)


def gan(a: str, b: str) -> bool:
    ha, la, sa = hls(a)
    hb, lb, sb = hls(b)
    if abs(la - lb) >= LECH_SANG:
        return False
    if sa < BAO_HOA_TOI_THIEU or sb < BAO_HOA_TOI_THIEU:
        return False  # màu xám, không có sắc độ để so
    d = abs(ha - hb)
    return min(d, 1 - d) * 360 < LECH_SAC_DO


def main() -> int:
    mau = sys.argv[1:]
    if len(mau) < 2 or not all(re.fullmatch(r"#[0-9a-fA-F]{6}", m) for m in mau):
        print("Cách dùng: kiem-mau.py <nền #rrggbb> <nhấn #rrggbb> [màu khác ...]")
        return 2
    xau = 0
    for m in mau:
        for ten, ref in MAU_MAU.items():
            if gan(m.lower(), ref):
                print(f"GẦN KÊNH MẪU: {m} gần {ten}")
                xau += 1
    print("ĐẠT" if not xau else "ĐỔI MÀU RỒI KIỂM LẠI")
    return 1 if xau else 0


if __name__ == "__main__":
    sys.exit(main())
