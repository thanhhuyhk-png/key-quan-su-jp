"""Khuôn kênh của kit phải qua máy quét như K2 bước 10 yêu cầu: `quet.py --tieu-de <tệp>` ra 0 CHẶN."""
import importlib.util
import sys
from pathlib import Path

import pytest

_GOC = Path(__file__).resolve().parents[2]
_KHUON = _GOC / ".claude" / "skills" / "goha-ho-so-kenh" / "references" / "khuon-kenh"

_spec = importlib.util.spec_from_file_location("quet_khuon", Path(__file__).with_name("quet.py"))
quet = importlib.util.module_from_spec(_spec)
sys.modules["quet_khuon"] = quet  # dataclass cần module có trong sys.modules
_spec.loader.exec_module(quet)
DS = quet.doc_mau(quet.DS_MAU)
CAC_KHUON = sorted(_KHUON.glob("*.md"))


def test_thu_muc_khuon_co_du_tep():
    assert len(CAC_KHUON) >= 6, f"khuôn kênh thiếu tệp ở {_KHUON}"


@pytest.mark.parametrize("tep", CAC_KHUON, ids=lambda p: p.name)
def test_khuon_kenh_sach_o_che_do_tieu_de(tep):
    kq = [(so_dong, tu, m.muc_do) for so_dong, tu, m, _ in quet.quet_file(tep, DS, True)]
    assert kq == [], f"{tep.name} còn chữ bị máy quét bắt: {kq}"
