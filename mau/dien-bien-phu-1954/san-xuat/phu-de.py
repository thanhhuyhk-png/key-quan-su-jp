"""Phụ đề tiếng Việt (.srt) theo mốc chữ thật của đường giọng (moc-cau.json), lùi theo intro.

Mỗi câu một dòng; câu dài hơn 90 ký tự tách ở dấu câu (. ? ! ; ,) gần giữa nhất, không có dấu thì ở chữ gần giữa. Dòng bắt đầu ở chữ đầu, kết thúc ngay trước
chữ đầu của dòng sau (tối đa +0,6 s sau chữ cuối), nên tắt trong khoảng thở, khoảng lặng.

python -I -X utf8 phu-de.py --ra <tệp .srt>
"""
import argparse
import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))
import intro  # noqa: E402

TOI_DA = 90


def tach(tu: list[str]) -> list[tuple[int, int]]:
    """Chia chỉ số chữ [a, b) của một câu thành các dòng ≤ TOI_DA ký tự, cắt sau chữ có dấu câu gần giữa nhất."""
    if len(" ".join(tu)) <= TOI_DA:
        return [(0, len(tu))]
    giua = len(" ".join(tu)) / 2
    cho = [k for k, w in enumerate(tu[:-1]) if w[-1] in ".?!;,"] or list(range(len(tu) - 1))  # không có dấu: tách ở chữ gần giữa
    k = min(cho, key=lambda k: abs(len(" ".join(tu[:k + 1])) - giua)) + 1
    return [(a, b) for a, b in tach(tu[:k])] + [(a + k, b + k) for a, b in tach(tu[k:])]


def gio(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra", required=True)
    o = ap.parse_args()
    moc = json.loads((GOC / "moc-cau.json").read_text(encoding="utf-8"))
    loi = [l.strip() for l in (GOC.parent / "ke-hoach" / "loi-doc-v5.txt").read_text(encoding="utf-8").split("\n") if l.strip()]
    dong = []
    for cau, t in zip(loi, moc["cau"]):
        tu = cau.split()
        assert len(tu) == len(t), (cau[:40], len(tu), len(t))
        dong += [(t[a], t[b - 1], " ".join(tu[a:b])) for a, b in tach(tu)]
    ra = []
    for i, (a, cuoi, chu) in enumerate(dong):
        b = min(cuoi + 0.6 + 0.06 * len(chu.split()[-1]), dong[i + 1][0] - 0.04) if i + 1 < len(dong) else cuoi + 0.8
        ra.append(f"{i + 1}\n{gio(a + intro.INTRO_GIAY)} --> {gio(b + intro.INTRO_GIAY)}\n{chu}\n")
    Path(o.ra).write_text("\n".join(ra), encoding="utf-8")
    print(f"{len(ra)} dòng, dài nhất {max(len(c) for *_, c in dong)} ký tự → {o.ra}")


if __name__ == "__main__":
    main()
