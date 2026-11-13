# -*- coding: utf-8 -*-
"""
quet-ja.py — Quét chính sách YouTube cho chữ TIẾNG NHẬT (kịch bản, lời đọc, tiêu đề, mô tả, chữ trên hình).
Bản riêng bổ sung cho `tools/loc-chinh-sach/quet.py`: quet.py của kit chỉ có từ điển tiếng Việt/Anh
(0 ký tự tiếng Nhật), nên với lời đọc tiếng Nhật nó luôn báo «0 CHẶN» dù có chữ cấm.

Cách làm: nạp nguyên mô-đun quet.py của kit (không sửa), gộp từ điển của kit với
`rieng/tools/tu-cam-ja.tsv` (cùng định dạng), rồi chạy đúng hàm main của kit.

Dùng (giống quet.py):
  python -I -X utf8 rieng/tools/quet-ja.py <file> [<file> ...]            # kịch bản, lời đọc, bảng phân cảnh
  python -I -X utf8 rieng/tools/quet-ja.py --tieu-de <file> [<file> ...]  # tiêu đề, chữ bìa, mô tả, thẻ
Mã thoát: 0 = sạch hoặc chỉ CẢNH BÁO; 1 = có CHẶN; 2 = lỗi cách dùng.
Thêm từ: sửa tu-cam-ja.tsv (cột nhom, muc_do CHAN|CANH, pham_vi tat_ca|tieu_de, mau = regex, ly_do, thay_bang).
Lưu ý: regex tiếng Nhật không dùng (?<!\\w): kana và kanji đều là \\w, nên ranh giới từ kiểu Latin làm hỏng mẫu.
"""
import importlib.util
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
QUET = GOC / "tools" / "loc-chinh-sach" / "quet.py"
DS_JA = Path(__file__).with_name("tu-cam-ja.tsv")


def nap_quet():
    spec = importlib.util.spec_from_file_location("quet_kit", QUET)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["quet_kit"] = mod
    spec.loader.exec_module(mod)
    return mod


def main(argv):
    q = nap_quet()
    doc_goc = q.doc_mau
    q.doc_mau = lambda p: doc_goc(p) + doc_goc(DS_JA)   # main của kit tra tên này trong mô-đun
    return q.main(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
