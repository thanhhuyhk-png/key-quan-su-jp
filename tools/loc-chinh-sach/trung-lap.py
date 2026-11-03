"""Cổng chống trùng: so lời đọc Goha với phụ đề đối thủ (và các tập Goha đã làm).

Dùng: python -I trung-lap.py <lời-đọc.txt> <nguồn so> [<nguồn so>...] [--bo-qua <file>] [--n 6] [--nguong 1.0]
  <nguồn so>: file .vtt/.srt/.txt/.md hoặc thư mục chứa các file đó.
  --bo-qua: file, mỗi dòng một câu nhận diện kênh, bỏ khỏi lời Goha trước khi so.
  --cum-chinh-thong: file cụm chính thống (tên văn kiện, khẩu hiệu, phương châm), mỗi dòng
     một cụm, loại khỏi cả hai phía. Mặc định: cum-chinh-thong.txt cạnh script.
Hai phép đo (plan quy trình, mục 4), cả hai đều đã bỏ cụm chính thống, con số (chữ số và
số viết bằng chữ cho giọng đọc) và từ chỉ ngày giờ:
  1. Tỉ lệ cụm n tiếng (mặc định 6) của Goha có trong nguồn so, bỏ thêm tên riêng
     (chữ viết hoa giữa câu trong lời Goha). Ngưỡng ≤ 1 %.
  2. Câu Goha có chuỗi ≥ 10 tiếng trùng nguyên văn (giữ tên riêng). Ngưỡng 0 câu.
Mã thoát 1 khi vượt một trong hai ngưỡng.
"""
import re
import sys
import unicodedata
from pathlib import Path

DUOI = {".vtt", ".srt", ".txt", ".md"}
MOC_GIO = re.compile(r"\d{1,2}:\d{2}(:\d{2})?[.,]\d{3}\s*-->")
THE = re.compile(r"<[^>]*>")
DAU_PHU_DE = ("WEBVTT", "Kind:", "Language:", "NOTE")
CAU_TRUNG_TOI_THIEU = 10
SO_VA_NGAY = set("không một hai ba bốn năm sáu bảy tám chín mười mươi mốt lăm tư trăm nghìn ngàn "
                 "triệu tỉ linh lẻ rưỡi ngày tháng giờ phút".split())
CUM_MAC_DINH = Path(__file__).with_name("cum-chinh-thong.txt")


def lam_sach_phu_de(chu: str) -> str:
    """Bỏ đầu tệp, mốc giờ, số thứ tự cue, thẻ <c>, và dòng lặp của phụ đề tự động."""
    giu: list[str] = []
    for dong in chu.splitlines():
        dong = THE.sub("", dong).strip()
        if not dong or dong.isdigit() or MOC_GIO.search(dong) or dong.startswith(DAU_PHU_DE):
            continue
        if dong in giu[-3:]:
            continue
        giu.append(dong)
    return "\n".join(giu)


def doc_nguon(tep: Path) -> str:
    chu = tep.read_text(encoding="utf-8", errors="replace")
    return lam_sach_phu_de(chu) if tep.suffix.lower() in {".vtt", ".srt"} else chu


def tach_tieng(chu: str) -> list[str]:
    chu = unicodedata.normalize("NFC", chu).lower()
    return re.sub(r"[^\w]+", " ", chu).replace("_", " ").split()


def ten_rieng(chu: str) -> set[str]:
    """Tiếng viết hoa không đứng đầu câu trong lời Goha (tên người, địa danh, đơn vị)."""
    ten: set[str] = set()
    for cau in re.split(r"(?<=[.!?…:])\s+|\n+", unicodedata.normalize("NFC", chu)):
        tu = re.findall(r"\w+", cau)
        ten.update(t.lower() for t in tu[1:] if t[0].isupper())
    return ten


def bo_cum(tieng: list[str], cac_cum: list[list[str]]) -> list[str]:
    """Bỏ mọi lần xuất hiện của các cụm chính thống (dài trước, ngắn sau)."""
    for c in sorted(cac_cum, key=len, reverse=True):
        n, kq, i = len(c), [], 0
        while i < len(tieng):
            if n and tieng[i:i + n] == c:
                i += n
            else:
                kq.append(tieng[i])
                i += 1
        tieng = kq
    return tieng


def la_so_ngay(t: str) -> bool:
    return t in SO_VA_NGAY or any(c.isdigit() for c in t)


def loc(tieng: list[str], ten: set[str]) -> list[str]:
    return [t for t in tieng if t not in ten and not la_so_ngay(t)]


def chuan_tieng(chu: str, cac_cum: list[list[str]]) -> list[str]:
    """Tách tiếng, bỏ cụm chính thống và con số, ngày giờ (giữ tên riêng)."""
    return [t for t in bo_cum(tach_tieng(chu), cac_cum) if not la_so_ngay(t)]


def cum(tieng: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(tieng[i:i + n]) for i in range(len(tieng) - n + 1)}


def dem_trung(tieng: list[str], cum_nguon: set[tuple[str, ...]], n: int) -> tuple[int, int]:
    cac_cum = [tuple(tieng[i:i + n]) for i in range(len(tieng) - n + 1)]
    return sum(c in cum_nguon for c in cac_cum), len(cac_cum)


def tach_cau(chu: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<=[.!?…])\s+|\n+", chu) if c.strip()]


def cau_trung_dai(chu: str, cum_nguon: set[tuple[str, ...]], n: int = CAU_TRUNG_TOI_THIEU,
                  cac_cum: list[list[str]] | None = None) -> list[str]:
    return [cau for cau in tach_cau(chu) if cum(chuan_tieng(cau, cac_cum or []), n) & cum_nguon]


def bo_cau(chu: str, cau_bo: list[str]) -> str:
    bo = {" ".join(tach_tieng(c)) for c in cau_bo if c.strip()}
    return " ".join(c for c in tach_cau(chu) if " ".join(tach_tieng(c)) not in bo)


def liet_ke_nguon(duong_dan: list[str]) -> list[Path]:
    tep: list[Path] = []
    for d in map(Path, duong_dan):
        tep += sorted(p for p in d.rglob("*") if p.suffix.lower() in DUOI) if d.is_dir() else [d]
    return tep


def doc_doi(doi: list[str]) -> tuple[list[str], dict[str, str]]:
    vi_tri, co, i = [], {}, 0
    while i < len(doi):
        if doi[i].startswith("--"):
            co[doi[i][2:]] = doi[i + 1]
            i += 2
        else:
            vi_tri.append(doi[i])
            i += 1
    return vi_tri, co


def main(doi: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    vi_tri, co = doc_doi(doi)
    if len(vi_tri) < 2:
        print(__doc__)
        return 2
    n, nguong = int(co.get("n", 6)), float(co.get("nguong", 1.0))
    tep_cum = Path(co.get("cum-chinh-thong", CUM_MAC_DINH))
    cac_cum = [tach_tieng(d) for d in tep_cum.read_text(encoding="utf-8").splitlines()
               if d.strip() and not d.startswith("#")] if tep_cum.exists() else []
    loi = Path(vi_tri[0]).read_text(encoding="utf-8")
    if "bo-qua" in co:
        loi = bo_cau(loi, Path(co["bo-qua"]).read_text(encoding="utf-8").splitlines())
    ten = ten_rieng(loi)
    goha = loc(bo_cum(tach_tieng(loi), cac_cum), ten)
    tong_cum, tong_cau = set(), set()
    for tep in liet_ke_nguon(vi_tri[1:]):
        chu = doc_nguon(tep)
        cum_tep = cum(loc(bo_cum(tach_tieng(chu), cac_cum), ten), n)
        so, tong = dem_trung(goha, cum_tep, n)
        print(f"{so / max(tong, 1) * 100:5.2f} %  ({so}/{tong})  {tep.name}")
        tong_cum |= cum_tep
        tong_cau |= cum(chuan_tieng(chu, cac_cum), CAU_TRUNG_TOI_THIEU)
    so, tong = dem_trung(goha, tong_cum, n)
    cau_trung = cau_trung_dai(loi, tong_cau, CAU_TRUNG_TOI_THIEU, cac_cum)
    ty_le = so / max(tong, 1) * 100
    print(f"GỘP: {ty_le:.2f} % cụm {n} tiếng trùng ({so}/{tong}); ngưỡng ≤ {nguong} %")
    for c in sorted({" ".join(goha[i:i + n]) for i in range(len(goha) - n + 1)
                     if tuple(goha[i:i + n]) in tong_cum})[:40]:
        print(f"  cụm: {c}")
    print(f"Câu trùng nguyên văn ≥ {CAU_TRUNG_TOI_THIEU} tiếng: {len(cau_trung)}")
    for cau in cau_trung:
        print(f"  - {cau}")
    dat = ty_le <= nguong and not cau_trung
    print("ĐẠT" if dat else "KHÔNG ĐẠT")
    return 0 if dat else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
