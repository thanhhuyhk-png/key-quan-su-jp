"""Chặn tái phạm: quét lời đọc, kịch bản, chữ trên hình theo sổ cách nói user đã sửa và chốt (kenh/cach-noi-da-chot.tsv).

Mỗi dòng sổ: mã, biểu thức cấm (regex), cách nói đúng, lý do, nguồn (lần user sửa), phạm vi (`tat-ca` mọi tệp;
`loi-doc` chỉ tệp lời đọc có "loi-doc" trong tên, vd luật xưng hô, vì thẻ tên trên hình viết "Tên · chức vụ").
Có chỗ nào khớp biểu thức cấm → in vị trí, cách nói đúng, rồi thoát mã 1. Chạy trước khi đọc giọng (dung-duong-giong.py tự gọi) và ở mọi cổng kịch bản.

python -I tools/lichsu/kiem-da-chot.py <tệp> [<tệp> ...]
"""
import csv
import re
import sys
from pathlib import Path

SO = Path(__file__).resolve().parents[2] / "kenh" / "cach-noi-da-chot.tsv"


def doc_so(so: Path = SO) -> list[dict]:
    with open(so, encoding="utf-8", newline="") as f:
        return [dict(r, re=re.compile(r["cam"])) for r in csv.DictReader(f, delimiter="\t") if r.get("cam")]


def ap_dung(luat: list[dict], tep: str) -> list[dict]:
    """Luật áp cho tệp này theo cột phạm vi."""
    return [r for r in luat if r.get("pham_vi", "tat-ca") != "loi-doc" or "loi-doc" in Path(tep).name]


def quet(van: str, luat: list[dict]) -> list[tuple[int, str, dict]]:
    """[(số dòng, đoạn khớp, dòng sổ)] cho mọi chỗ phạm trong văn bản."""
    return [(i, m.group(0), r) for i, dong in enumerate(van.splitlines(), 1) for r in luat for m in r["re"].finditer(dong)]


def main(tep: list[str]) -> int:
    luat, loi = doc_so(), 0
    for t in tep:
        for i, khop, r in quet(Path(t).read_text(encoding="utf-8"), ap_dung(luat, t)):
            print(f"CHẶN {t}:{i}: «{khop}» → dùng «{r['dung']}» ({r['ma']}: {r['ly_do']} · {r['nguon']})")
            loi += 1
    print(f"Sổ cách nói đã chốt: {len(luat)} luật, {loi} chỗ phạm trong {len(tep)} tệp.")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
