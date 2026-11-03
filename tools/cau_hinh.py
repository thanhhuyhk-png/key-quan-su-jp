"""Đọc cấu hình máy: mọi đường dẫn riêng của từng máy nằm ở một chỗ.

- `cau-hinh.mau.toml` (lên Git): đủ mọi khoá, giá trị mẫu.
- `cau-hinh.toml` (không lên Git): bản của máy này, chỉ cần ghi khoá khác mẫu.

Dùng trong script:
    REPO = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
    sys.path.insert(0, str(REPO / "tools"))
    from cau_hinh import duong
    OUT = duong("output")
"""
from __future__ import annotations

import re
from pathlib import Path

MAU, RIENG = "cau-hinh.mau.toml", "cau-hinh.toml"
_DONG = re.compile(r'^([A-Za-z0-9_-]+)\s*=\s*"((?:[^"\\]|\\.)*)"\s*(?:#.*)?$')


def doc_toml(chu: str) -> dict[str, dict[str, str]]:
    """Đọc TOML phẳng: [nhóm] và khoá = "chuỗi". Đủ cho file cấu hình; Python 3.10 chưa có tomllib."""
    kq: dict[str, dict[str, str]] = {}
    nhom = kq.setdefault("", {})
    for so, dong in enumerate(chu.lstrip("\ufeff").splitlines(), 1):
        d = dong.strip()
        if not d or d.startswith("#"):
            continue
        m_nhom = re.match(r"^\[([^\]]+)\]\s*(?:#.*)?$", d)
        if m_nhom:
            nhom = kq.setdefault(m_nhom.group(1).strip(), {})
            continue
        m = _DONG.match(d)
        if not m:
            raise ValueError(f"dòng {so} không đọc được: {dong!r} (chỉ hỗ trợ khoá = \"chuỗi\")")
        nhom[m.group(1)] = m.group(2).replace('\\"', '"').replace("\\\\", "\\")
    return kq


def goc_repo(tu: str | Path) -> Path:
    """Thư mục gốc repo: thư mục cha gần nhất có cau-hinh.mau.toml."""
    for p in [Path(tu).resolve(), *Path(tu).resolve().parents]:
        if (p / MAU).exists():
            return p
    raise SystemExit(f"Không tìm thấy {MAU} ở {tu} hay thư mục cha nào.")


def doc(repo: Path | None = None) -> dict[str, dict[str, str]]:
    repo = repo or goc_repo(__file__)
    rieng = repo / RIENG
    if not rieng.exists():
        raise SystemExit(f"Thiếu {rieng}. Chép {MAU} thành {RIENG} rồi sửa đường dẫn cho máy này.")
    mau = doc_toml((repo / MAU).read_text(encoding="utf-8-sig"))
    for nhom, khoa in doc_toml(rieng.read_text(encoding="utf-8-sig")).items():
        mau.setdefault(nhom, {}).update(khoa)
    return mau


def duong(khoa: str, repo: Path | None = None, nhom: str = "duong_dan") -> Path:
    """Đường dẫn theo khoá trong [duong_dan]. Khoá không có hoặc để trống thì dừng và nói rõ phải sửa gì."""
    repo = repo or goc_repo(__file__)
    g = doc(repo).get(nhom, {})
    if khoa not in g:
        raise SystemExit(f"Khoá «{khoa}» không có trong [{nhom}] của {MAU}.")
    if not g[khoa]:
        raise SystemExit(f"Khoá «{khoa}» đang để trống. Điền đường dẫn vào [{nhom}] trong {repo / RIENG}.")
    return Path(g[khoa])
