"""Nắn các tờ bản đồ AMS lòng chảo Điện Biên Phủ và ghép texture cho map3d.

Chạy từ thư mục template/:  python -I -X utf8 tools/nan-ban-do-ams.py [--no-warp] [--from-pdf-west <pdf>]
Toàn bộ logic ở ams_nan.py (import được để test); xem tài liệu đầu tệp đó.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ams_nan import main  # noqa: E402

if __name__ == '__main__':
    main()
