"""Lệnh tu-lieu: tìm ảnh, phim lưu trữ qua API NARA, DVIDS, Smithsonian Open Access, Pexels, Internet Archive,
Library of Congress, Wikimedia Commons (miễn phí, không tốn credit; ba nguồn sau không cần khoá, thêm 07/11/2026).

Khoá đọc qua chung.khoa từ .env (NARA_API_KEY, DVIDS_API_KEY, SMITHSONIAN_API_KEY, PEXELS_API_KEY), không in giá trị.
  kit.py tu-lieu "Peleliu 1944" --nguon nara,dvids,si --so 10
  kit.py tu-lieu "Peleliu airfield" --nguon nara --tai D:/Goha/output/<tập>/assets-moi
  kit.py tu-lieu "Peleliu 1944" --nguon ia,loc,commons --so 10   (ia: phim, bản tin; loc: ảnh, bản đồ; commons: ảnh đã lọc)
In bảng TSV: nguon, ma, tieu_de, trang, tep, giay_phep_goi_y. Giấy phép chỉ là gợi ý theo nguồn; P1 vẫn phải ghi hạng A/A?/B/C.
Pexels là ảnh stock hiện đại: chỉ dùng làm nền, vân, cảnh vật; không dùng làm tư liệu lịch sử.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from chung import LoiKit, co_khoa, ghi_nguyen_tu, khoa
from giong import goi_api, gui_http

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"
KHOA = {"nara": "NARA_API_KEY", "dvids": "DVIDS_API_KEY", "si": "SMITHSONIAN_API_KEY", "pexels": "PEXELS_API_KEY",
        "ia": None, "loc": None, "commons": None}  # None: nguồn mở, không cần khoá
UA_MO = "GohaKit-tu-lieu/1.0 (archival research script)"


def _nara(q: str, so: int, chi_anh: bool = False) -> list[dict]:
    tham = {"q": q, "limit": so, "availableOnline": "true"}
    if chi_anh:
        tham["typeOfMaterials"] = "Photographs and other Graphic Materials"
    r = goi_api("GET", "https://catalog.archives.gov/api/v2/records/search", ten="NARA",
                headers={"x-api-key": khoa(KHOA["nara"]), "Content-Type": "application/json"},
                params=tham, timeout=60).json()
    ra = []
    for h in ((r.get("body") or {}).get("hits") or {}).get("hits", []):
        rec = (h.get("_source") or {}).get("record") or {}
        na = rec.get("naId")
        so_dt = rec.get("digitalObjects") or []
        tep = next((d.get("objectUrl") for d in so_dt if str(d.get("objectType", "")).lower().startswith(("image", "jpg", "tif")) or
                    str(d.get("objectUrl", "")).lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff"))), "")
        loai = ",".join(sorted({str(d.get("objectType", "")) for d in so_dt}))[:40]
        ra.append({"nguon": "NARA", "ma": f"NAID {na}", "tieu_de": rec.get("title", ""), "trang": f"https://catalog.archives.gov/id/{na}",
                   "tep": tep, "giay_phep": f"chính phủ Mỹ, thường phạm vi công cộng (kiểm «Use restriction»); {loai}"})
    return ra


def _dvids(q: str, so: int, chi_anh: bool = True) -> list[dict]:
    r = goi_api("GET", "https://api.dvidshub.net/search", ten="DVIDS", headers={},
                params={"api_key": khoa(KHOA["dvids"]), "q": q, "type": "image", "max_results": so}, timeout=60).json()
    return [{"nguon": "DVIDS", "ma": str(x.get("id", "")), "tieu_de": x.get("title", ""), "trang": x.get("url", ""),
             "tep": x.get("thumbnail", "") if isinstance(x.get("thumbnail"), str) else (x.get("thumbnail") or {}).get("url", ""),
             "giay_phep": "DVIDS: ảnh quân đội Mỹ, thường phạm vi công cộng (kiểm ghi chú trên trang)"} for x in r.get("results", [])]


def _si(q: str, so: int, chi_anh: bool = False) -> list[dict]:
    r = goi_api("GET", "https://api.si.edu/openaccess/api/v1.0/search", ten="Smithsonian", headers={},
                params={"api_key": khoa(KHOA["si"]), "q": f"{q} AND online_media_type:Images" if chi_anh else q, "rows": so}, timeout=60).json()
    ra = []
    for x in (r.get("response") or {}).get("rows", []):
        dn = ((x.get("content") or {}).get("descriptiveNonRepeating") or {})
        media = ((dn.get("online_media") or {}).get("media") or [])
        m = next((m for m in media if m.get("type") == "Images"), media[0] if media else {})
        quyen = ((m.get("usage") or {}).get("access") or "").strip()
        ra.append({"nguon": "Smithsonian", "ma": dn.get("record_ID", x.get("id", "")), "tieu_de": x.get("title", ""),
                   "trang": dn.get("record_link", ""), "tep": m.get("content", ""),
                   "giay_phep": "CC0 (Open Access)" if quyen == "CC0" else f"không phải CC0 ({quyen or 'chưa rõ'}): hạng B"})
    return ra


def _pexels(q: str, so: int, chi_anh: bool = True) -> list[dict]:
    r = goi_api("GET", "https://api.pexels.com/v1/search", ten="Pexels", headers={"Authorization": khoa(KHOA["pexels"])},
                params={"query": q, "per_page": so}, timeout=60).json()
    return [{"nguon": "Pexels", "ma": str(x.get("id", "")), "tieu_de": x.get("alt", ""), "trang": x.get("url", ""),
             "tep": (x.get("src") or {}).get("large2x", ""), "giay_phep": f"Pexels License, ảnh hiện đại của {x.get('photographer', '?')}: chỉ làm nền"}
            for x in r.get("photos", [])]


def _ia(q: str, so: int, chi_anh: bool = False) -> list[dict]:
    """Internet Archive: phim (bản tin, phim quân đội), ảnh. Quyền theo từng mục: licenseurl/rights; không có thì phải kiểm trang."""
    loai = "mediatype:(image)" if chi_anh else "mediatype:(movies OR image)"
    r = goi_api("GET", "https://archive.org/advancedsearch.php", ten="Internet Archive", headers={"User-Agent": UA_MO},
                params={"q": f"({q}) AND {loai}", "fl[]": ["identifier", "title", "mediatype", "licenseurl", "rights", "year"],
                        "rows": so, "output": "json"}, timeout=60).json()
    ra = []
    for x in (r.get("response") or {}).get("docs", []):
        lic = x.get("licenseurl") or ""
        quyen = x.get("rights") or ""
        quyen = " ".join(quyen) if isinstance(quyen, list) else quyen
        goi_y = ("phạm vi công cộng (licenseurl)" if "publicdomain" in lic else f"giấy phép {lic}" if lic
                 else f"chưa rõ quyền ({quyen[:60] or 'không ghi'}): kiểm nguồn gốc phim")
        ra.append({"nguon": "Internet Archive", "ma": x.get("identifier", ""), "tieu_de": f"{x.get('title', '')} [{x.get('mediatype', '')} {x.get('year', '')}]",
                   "trang": f"https://archive.org/details/{x.get('identifier', '')}", "tep": "", "giay_phep": goi_y})
    return ra


def _loc(q: str, so: int, chi_anh: bool = False) -> list[dict]:
    """Library of Congress: ảnh, bản đồ, báo. Quyền theo rights_advisory của từng mục."""
    r = goi_api("GET", "https://www.loc.gov/photos/" if chi_anh else "https://www.loc.gov/search/", ten="Library of Congress",
                headers={"User-Agent": UA_MO}, params={"q": q, "fo": "json", "c": so}, timeout=60).json()
    ra = []
    for x in (r.get("results") or [])[:so]:
        anh = x.get("image_url") or []
        quyen = x.get("rights_advisory") or x.get("rights") or ""
        quyen = " ".join(quyen) if isinstance(quyen, list) else str(quyen)
        ra.append({"nguon": "LOC", "ma": str(x.get("id", "")).rstrip("/").split("/")[-1], "tieu_de": x.get("title", ""),
                   "trang": x.get("id", ""), "tep": (anh[-1] if anh else "").split("#")[0],
                   "giay_phep": f"LOC: {quyen[:80] or 'kiểm Rights Advisory trên trang'}"})
    return ra


def _commons(q: str, so: int, chi_anh: bool = True) -> list[dict]:
    """Wikimedia Commons: tệp ảnh, phim; giấy phép lấy từ extmetadata (LicenseShortName)."""
    r = goi_api("GET", "https://commons.wikimedia.org/w/api.php", ten="Wikimedia Commons", headers={"User-Agent": UA_MO},
                params={"action": "query", "generator": "search", "gsrsearch": q, "gsrnamespace": 6, "gsrlimit": so,
                        "prop": "imageinfo", "iiprop": "url|extmetadata", "format": "json"}, timeout=60).json()
    ra = []
    for x in ((r.get("query") or {}).get("pages") or {}).values():
        ii = (x.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata") or {}
        lic = (md.get("LicenseShortName") or {}).get("value", "")
        ra.append({"nguon": "Commons", "ma": x.get("title", "").replace("File:", ""), "tieu_de": x.get("title", ""),
                   "trang": ii.get("descriptionurl", ""), "tep": ii.get("url", ""),
                   "giay_phep": f"Commons: {lic or 'chưa rõ'}" + (" (kiểm tác giả, nguồn gốc)" if lic else "")})
    return ra


HAM = {"nara": _nara, "dvids": _dvids, "si": _si, "pexels": _pexels, "ia": _ia, "loc": _loc, "commons": _commons}


def dang_ky(p: argparse.ArgumentParser) -> None:
    p.add_argument("q", nargs="?", help="từ khoá tìm (tiếng Anh)")
    p.add_argument("--nguon", default="nara,dvids,si", help="danh sách: nara,dvids,si,pexels,ia,loc,commons")
    p.add_argument("--so", type=int, default=10, help="số kết quả mỗi nguồn")
    p.add_argument("--tai", help="thư mục tải ảnh về (thư mục mới riêng, ví dụ <output>/<tập>/assets-moi)")
    p.add_argument("--chi-anh", action="store_true", help="NARA, Smithsonian: chỉ lấy ảnh (bỏ phim, sách)")
    p.add_argument("--kiem-khoa", action="store_true", help="chỉ báo khoá nào có/thiếu (không in giá trị)")


def _ten_tep(d: dict) -> str:
    duoi = Path(d["tep"].split("?")[0]).suffix.lower() or ".jpg"
    goc = re.sub(r"[^a-z0-9]+", "-", f"{d['nguon']}-{d['ma']}-{d['tieu_de'][:40]}".lower()).strip("-")
    return goc + (duoi if duoi in (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp") else ".jpg")


def chay(a: argparse.Namespace) -> int:
    ds = [n.strip() for n in a.nguon.split(",") if n.strip()]
    sai = [n for n in ds if n not in HAM]
    if sai:
        raise LoiKit(f"nguồn không biết: {', '.join(sai)} (dùng: {', '.join(HAM)})")
    if a.kiem_khoa:
        for n in HAM:
            print(f"{n}\t{KHOA[n] or '-'}\t{'không cần khoá' if KHOA[n] is None else 'có' if co_khoa(KHOA[n]) else 'thiếu'}")
        return 0
    if not a.q:
        raise LoiKit("cần từ khoá tìm")
    print("nguon\tma\ttieu_de\ttrang\ttep\tgiay_phep_goi_y")
    tat_ca = []
    for n in ds:
        if KHOA[n] is not None and not co_khoa(KHOA[n]):
            print(f"# {n}: thiếu khoá {KHOA[n]} trong .env, bỏ qua")
            continue
        try:
            kq = HAM[n](a.q, a.so, a.chi_anh)
        except LoiKit as e:
            print(f"# {n}: lỗi {e}")
            continue
        for d in kq:
            print("\t".join(str(d[k]).replace("\t", " ").replace("\n", " ") for k in ("nguon", "ma", "tieu_de", "trang", "tep", "giay_phep")))
        tat_ca += kq
    if a.tai:
        thu_muc = Path(a.tai)
        thu_muc.mkdir(parents=True, exist_ok=True)
        for d in tat_ca:
            if not d["tep"]:
                continue
            r = gui_http("GET", d["tep"], headers={"User-Agent": UA}, timeout=300)
            if r.status_code >= 400 or not str(r.headers.get("Content-Type", "image")).startswith("image"):
                print(f"# không tải được {d['ma']} ({r.status_code})")
                continue
            dich = thu_muc / _ten_tep(d)
            with ghi_nguyen_tu(dich) as tam:
                tam.write_bytes(r.content)
            print(f"# đã tải {dich.name}")
    return 0
