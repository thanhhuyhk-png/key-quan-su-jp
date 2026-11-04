"""Cổng P0: kiểm đề tài đề xuất có trùng đề tài chủ kênh đã làm hoặc hội viên khác đã đăng ký không.

python -I tools/lichsu/kiem-de-tai.py "<đề tài>" [--goc "<góc kể>"] [--ngon-ngu vi] [--so-chung <csv/tsv>] [--cam <tsv>]
  --cam       sổ chủ đề cấm (mặc định kit/so-chu-de-cam.tsv): cột de_tai, tu_khoa (cách nhau ;), nam, trang_thai, ghi_chu.
              Từ khoá riêng (tên trận, địa danh, nhân vật) chặn bất kể năm; từ khoá chung chung đánh dấu ~ (vd ~củ chi)
              chỉ chặn khi đề xuất không có năm hoặc cùng năm với dòng sổ.
  --so-chung  tệp CSV/TSV xuất từ sổ đăng ký đề tài chung: cột đề tài, góc kể, ngôn ngữ, hội viên, ngày.
Chuẩn hoá bỏ dấu, chữ thường; khớp từ khoá nguyên cụm tiếng, kể cả khi viết liền hoặc dính (dienbienphu). Năm chỉ phân biệt với từ khoá chung chung (~).
Kết quả: CHẶN (trùng sổ cấm, hoặc cùng đề tài + ngôn ngữ + góc kể trong sổ chung), CẢNH BÁO (cùng đề tài + ngôn ngữ,
khác góc kể), ĐẠT. Luôn in số dòng đã so ở mỗi sổ; không truyền --so-chung thì in «sổ chung: chưa có, 0 dòng đã so»
(cố ý: sổ chung là Google Sheet làm ở bước sau) và vẫn so sổ cấm.
Mã thoát: 0 = ĐẠT hoặc CẢNH BÁO; 1 = CHẶN (chỉ mã này nghĩa là CHẶN); 2 = lỗi đầu vào (thiếu đối số, tệp thiếu hoặc không
đọc được hoặc sai mã hoá, sổ thiếu cột bắt buộc `de_tai` sau chuẩn hoá tiêu đề).
"""
import csv
import io
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
CAM_MAC_DINH = GOC / "kit" / "so-chu-de-cam.tsv"
NAM = re.compile(r"^(1\d{3}|20\d{2})$")
NGUONG_CUNG_GOC = 0.6


class LoiDauVao(Exception):
    """Tệp đầu vào thiếu, không đọc được hoặc sai cấu trúc: thoát mã 2."""


@dataclass
class KetQua:
    muc: str = "ĐẠT"
    dong_khop: list[str] = field(default_factory=list)


def chuan_hoa(chu: str) -> str:
    """Bỏ dấu, đ thành d, chữ thường, mọi ký tự không phải chữ hoặc số thành một dấu cách."""
    chu = unicodedata.normalize("NFD", chu.replace("đ", "d").replace("Đ", "D"))
    chu = "".join(c for c in chu if unicodedata.category(c) != "Mn").lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", chu).split())


def tieng(chu: str) -> list[str]:
    return chuan_hoa(chu).split()


def nam_trong(chu: str) -> set[str]:
    return {t for t in tieng(chu) if NAM.match(t)}


def bo_nam(tieng_chu: list[str]) -> list[str]:
    return [t for t in tieng_chu if not NAM.match(t)]


def chua_cum(tieng_chu: list[str], cum: list[str]) -> bool:
    """Cụm có nằm nguyên cụm tiếng trong chữ không; cũng tính cách viết liền hoặc dính một phần
    (dienbienphu, dien bienphu): chuỗi tiếng liền kề ghép lại phải bằng đúng cụm đã ghép, bắt đầu và kết thúc ở ranh giới tiếng."""
    dich = "".join(cum)
    if not dich:
        return False
    for dau in range(len(tieng_chu)):
        ghep = ""
        for tieng_ke in tieng_chu[dau:]:
            ghep += tieng_ke
            if ghep == dich:
                return True
            if len(ghep) >= len(dich):
                break
    return False


def cung_nam(nam_de_xuat: set[str], nam_dong: set[str]) -> bool:
    return not nam_de_xuat or not nam_dong or bool(nam_de_xuat & nam_dong)


def doc_bang(tep: Path, cot_bat_buoc: tuple[str, ...] = ()) -> list[dict]:
    try:
        chu = tep.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as e:
        raise LoiDauVao(f"không đọc được {tep} (cần UTF-8): {e}") from e
    dong_dau = chu.split("\n", 1)[0]
    dau = "\t" if dong_dau.count("\t") >= dong_dau.count(",") else ","
    doc = csv.DictReader(io.StringIO(chu, newline=""), delimiter=dau)
    cot = [chuan_hoa(k).replace(" ", "_") for k in (doc.fieldnames or []) if k]
    thieu = [c for c in cot_bat_buoc if c not in cot]
    if thieu:
        raise LoiDauVao(f"{tep} thiếu cột bắt buộc: {', '.join(thieu)} (các cột đang có: {', '.join(cot) or 'không có'})")
    return [{chuan_hoa(k).replace(" ", "_"): (v or "").strip() for k, v in r.items() if k} for r in doc]


def doc_cam(tep: Path = CAM_MAC_DINH) -> list[dict]:
    return [r for r in doc_bang(tep, ("de_tai",)) if r.get("de_tai")]


COT_NGAY_CUA_FORM = ("dau_thoi_gian", "timestamp")


def doc_so_chung(tep: Path) -> list[dict]:
    """Sổ chung tải từ Sheet nhận câu trả lời Google Form: cột thời gian của Form dùng làm cột ngày."""
    ra = []
    for r in doc_bang(tep, ("de_tai",)):
        if not r.get("de_tai"):
            continue
        if not r.get("ngay"):
            r["ngay"] = next((r[k] for k in COT_NGAY_CUA_FORM if r.get(k)), "")
        ra.append(r)
    return ra


def tu_khoa_cua(r: dict) -> list[tuple[str, bool]]:
    """(từ khoá, chung chung?) của một dòng sổ cấm; từ khoá có tiền tố ~ là chung chung, chỉ chặn khi cùng năm."""
    ra = [(r["de_tai"], False)]
    for k in r.get("tu_khoa", "").split(";"):
        k = k.strip()
        if k:
            ra.append((k.lstrip("~").strip(), k.startswith("~")))
    return ra


def khop_cam(de_tai: str, cam: list[dict]) -> list[str]:
    t, nam = tieng(de_tai), nam_trong(de_tai)
    kq = []
    for r in cam:
        cung = cung_nam(nam, nam_trong(r.get("nam", "")))
        if any(chua_cum(t, tieng(k)) and (cung or not chung) for k, chung in tu_khoa_cua(r)):
            kq.append(f"{r['de_tai']} ({r.get('nam') or 'không năm'}, {r.get('trang_thai', '')})")
    return kq


def cung_goc(a: str, b: str) -> bool:
    ta, tb = set(tieng(a)), set(tieng(b))
    if not ta and not tb:
        return True
    return bool(ta and tb) and len(ta & tb) / len(ta | tb) >= NGUONG_CUNG_GOC


def khop_chung(de_tai: str, goc: str, ngon_ngu: str, chung: list[dict]) -> tuple[list[str], list[str]]:
    """(dòng cùng đề tài + ngôn ngữ + góc: CHẶN, dòng cùng đề tài + ngôn ngữ khác góc: CẢNH BÁO)."""
    t, nam = bo_nam(tieng(de_tai)), nam_trong(de_tai)
    chan, canh_bao = [], []
    for r in chung:
        tr = bo_nam(tieng(r["de_tai"]))
        if not cung_nam(nam, nam_trong(r["de_tai"])):
            continue
        if not (chua_cum(t, tr) or (len(t) >= 2 and chua_cum(tr, t))):
            continue
        if ngon_ngu and r.get("ngon_ngu") and chuan_hoa(r["ngon_ngu"]) != chuan_hoa(ngon_ngu):
            continue
        mo_ta = (f"{r['de_tai']} | góc: {r.get('goc_ke') or '(chưa ghi)'} | {r.get('ngon_ngu', '')} | "
                 f"{r.get('hoi_vien', '')} | {r.get('ngay', '')}")
        (chan if cung_goc(goc, r.get("goc_ke", "")) else canh_bao).append(mo_ta)
    return chan, canh_bao


def kiem(de_tai: str, cam: list[dict], chung: list[dict] | None = None,
         goc: str = "", ngon_ngu: str = "") -> KetQua:
    trung_cam = khop_cam(de_tai, cam)
    if trung_cam:
        return KetQua("CHẶN", [f"sổ chủ đề cấm: {d}" for d in trung_cam])
    chan, canh_bao = khop_chung(de_tai, goc, ngon_ngu, chung or [])
    if chan:
        return KetQua("CHẶN", [f"sổ chung: {d}" for d in chan])
    if canh_bao:
        return KetQua("CẢNH BÁO", [f"sổ chung: {d}" for d in canh_bao])
    return KetQua()


def doc_doi(doi: list[str]) -> tuple[list[str], dict[str, str]]:
    vi_tri, co, i = [], {}, 0
    while i < len(doi):
        if doi[i].startswith("--") and i + 1 < len(doi):
            co[doi[i][2:]] = doi[i + 1]
            i += 2
        else:
            vi_tri.append(doi[i])
            i += 1
    return vi_tri, co


def main(doi: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if any(d in ("-h", "--help") for d in doi):
        print(__doc__)
        return 0
    vi_tri, co = doc_doi(doi)
    if not vi_tri:
        print(__doc__)
        return 2
    try:
        cam = doc_cam(Path(co.get("cam", CAM_MAC_DINH)))
        chung = doc_so_chung(Path(co["so-chung"])) if "so-chung" in co else None
    except LoiDauVao as e:
        print(f"Lỗi đầu vào: {e}", file=sys.stderr)
        return 2
    kq = kiem(" ".join(vi_tri), cam, chung, co.get("goc", ""), co.get("ngon-ngu", ""))
    print(f"{kq.muc}: {' '.join(vi_tri)}")
    print(f"  (sổ cấm: {len(cam)} dòng đã so; "
          + (f"sổ chung: {len(chung)} dòng đã so)" if chung is not None else "sổ chung: chưa có, 0 dòng đã so)"))
    for d in kq.dong_khop:
        print(f"  - {d}")
    if kq.muc == "CHẶN":
        print("Chọn đề tài hoặc góc kể khác rồi chạy lại.")
    elif kq.muc == "CẢNH BÁO":
        print("Cùng đề tài, khác góc kể: chỉ đi tiếp nếu góc của bạn thật sự khác và người dùng đã duyệt.")
    return 1 if kq.muc == "CHẶN" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
