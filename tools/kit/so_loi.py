"""so-loi: so lời chuẩn với words.json (chép lời hoặc mốc chữ của giọng), ra tỉ lệ khớp và chỗ lệch.

Tỉ lệ = số token khớp / số token của LỜI CHUẨN; chữ nghe thừa không bị phạt. «Không đạt» vẫn thoát 0.
Chuẩn hoá tiếng Việt tự viết: thường hoá, NFC, dấu thanh về một kiểu, bỏ dấu câu và thẻ [..],
số/năm/ngày/thập phân/% thành chữ («.» là dấu nghìn, «,» là dấu thập phân), đơn vị km, kg, m.
"""
from __future__ import annotations

import argparse
import difflib
import json
import math
import re
import unicodedata
from pathlib import Path

from chung import LoiKit

CHU_SO = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
TEN_NHOM = ["", "nghìn", "triệu", "tỷ"]

# Dấu thanh về kiểu «dấu ở nguyên âm thứ hai» (hoà, thuý): hai kiểu cũ/mới thành một.
_THANH = {"òa": "oà", "óa": "oá", "ỏa": "oả", "õa": "oã", "ọa": "oạ",
          "òe": "oè", "óe": "oé", "ỏe": "oẻ", "õe": "oẽ", "ọe": "oẹ",
          "ùy": "uỳ", "úy": "uý", "ủy": "uỷ", "ũy": "uỹ", "ụy": "uỵ"}
_RE_THANH = re.compile("|".join(_THANH))

# Cách nói khác của cùng một chữ (số, vùng miền, chính tả) → một dạng.
_BIEN_THE = {"mốt": "một", "tư": "bốn", "lăm": "năm", "nhăm": "năm", "lẻ": "linh", "ngàn": "nghìn",
             "tỉ": "tỷ", "bẩy": "bảy", "tui": "tôi", "ổng": "ông", "hông": "không", "hổng": "không",
             "kilômét": "km", "kilomet": "km", "kilômet": "km", "kilôgam": "kg", "kilogam": "kg", "mét": "m"}
_CUM = [("ki lô mét", "km"), ("ki lô gam", "kg")]


def _doc_nhom(n: int, day_du: bool) -> list[str]:
    """Đọc một nhóm 3 chữ số (0..999). day_du: có nhóm lớn hơn, nên «không trăm», «linh» được đọc."""
    tram, chuc, dv = n // 100, n // 10 % 10, n % 10
    ra: list[str] = []
    if tram or day_du:
        ra += [CHU_SO[tram], "trăm"]
    if chuc > 1:
        ra += [CHU_SO[chuc], "mươi"]
    elif chuc == 1:
        ra.append("mười")
    elif dv and (tram or day_du):
        ra.append("linh")
    if dv:
        ra.append(CHU_SO[dv])
    return ra


def doc_so(s: str) -> str:
    """Chuỗi chữ số → chữ. Số có số 0 đầu hoặc quá 12 chữ số đọc từng số."""
    if (len(s) > 1 and s[0] == "0") or len(s) > 12:
        return " ".join(CHU_SO[int(c)] for c in s)
    nhom = []
    while s:
        nhom.append(int(s[-3:]))
        s = s[:-3]
    if not any(nhom):
        return "không"
    ra: list[str] = []
    for i in range(len(nhom) - 1, -1, -1):
        if nhom[i]:
            ra += _doc_nhom(nhom[i], i < len(nhom) - 1)
            if TEN_NHOM[i]:
                ra.append(TEN_NHOM[i])
    return " ".join(ra)


def _thap_phan(m: re.Match) -> str:
    phan = m.group(2)
    duoi = doc_so(phan) if (not phan.startswith("0") and len(phan) <= 2) else " ".join(CHU_SO[int(c)] for c in phan)
    return f" {doc_so(m.group(1))} phẩy {duoi} "


def chuan_hoa(chu: str, lang: str = "vi") -> list[str]:
    t = unicodedata.normalize("NFC", chu).lower()
    t = re.sub(r"\[[^\]]*\]", " ", t)
    if lang == "vi":
        t = re.sub(r"(?<![\d.,])(\d{1,2})[/.](\d{1,2})[/.](\d{4})(?![\d.,]?\d)", r"\1 tháng \2 năm \3", t)
        t = re.sub(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?![\d/])", r"\1 tháng \2", t)
        t = re.sub(r"km\s*(?:²|2(?!\d))", "km vuông", t)
        # tiếng Việt: «.» ngăn nghìn (phần nguyên không mở đầu bằng 0), «,» luôn là dấu thập phân
        t = re.sub(r"(?<![\d.,])[1-9]\d{0,2}(?:\.\d{3})+(?!\d)", lambda m: m.group().replace(".", ""), t)
        t = re.sub(r"(?<![\d.,])(\d+)[,.](\d+)(?!\d)", _thap_phan, t)
        t = t.replace("%", " phần trăm ")
        t = re.sub(r"\d+", lambda m: f" {doc_so(m.group())} ", t)
    t = re.sub(r"[\W_]+", " ", t).strip()
    if lang != "vi":
        return t.split()
    t = _RE_THANH.sub(lambda m: _THANH[m.group()], t)
    for cum, thay in _CUM:
        t = re.sub(rf"(?<!\S){cum}(?!\S)", thay, t)
    t = " ".join(_BIEN_THE.get(w, w) for w in t.split())
    return t.split()


def doc_chu_nghe(du_lieu: dict) -> list[dict]:
    """Danh sách chữ từ words.json của chép-lời (`words`) hoặc json của lệnh giọng (`results[0].words`)."""
    if "words" in du_lieu:
        return du_lieu["words"]
    try:
        return du_lieu["results"][0]["words"]
    except (KeyError, IndexError, TypeError) as e:
        raise LoiKit("tệp words không có mục «words» (hay results[0].words)") from e


def so(loi: str, du_lieu: dict, lang: str, nguong: float) -> dict:
    ref = chuan_hoa(loi, lang)
    hyp: list[str] = []
    chu_cua: list[dict] = []  # token nghe được → chữ gốc (để lấy thời gian)
    for w in doc_chu_nghe(du_lieu):
        if w.get("audio_event"):
            continue
        for tok in chuan_hoa(str(w.get("text", "")), lang):
            hyp.append(tok)
            chu_cua.append(w)
    sm = difflib.SequenceMatcher(None, ref, hyp, autojunk=False)
    khop = sum(b.size for b in sm.get_matching_blocks())
    ti_le = khop / len(ref) if ref else 1.0
    loi_lech = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        bat, ket = (chu_cua[j1].get("start_ms"), chu_cua[j2 - 1].get("end_ms")) if j2 > j1 else (None, None)
        loi_lech.append({"expected": " ".join(ref[i1:i2]), "heard": " ".join(hyp[j1:j2]),
                         "start_ms": bat, "end_ms": ket,
                         "_gan_ms": (chu_cua[j1 - 1].get("end_ms") if j1 > 0 else 0)})
    return {"match": round(ti_le, 4), "scriptWords": len(ref), "heardWords": len(hyp), "issues": loi_lech,
            "min": nguong, "pass": ti_le >= nguong, "language": lang, "_ti_le": ti_le}


def _dong_ho(ms: int | float) -> str:
    giay = ms / 1000
    return f"{int(giay // 60)}:{giay % 60:04.1f}"


def dang_ky(p: argparse.ArgumentParser) -> None:
    p.add_argument("--text", required=True, help="tệp lời chuẩn (.txt)")
    p.add_argument("--words", required=True, help="words.json của chep-loi (hoặc json của giong)")
    p.add_argument("--lang", help="mặc định: ngôn ngữ ghi trong words.json, không có thì vi")
    p.add_argument("--min", type=float, default=0.97, help="ngưỡng đạt (0..1, hoặc phần trăm), mặc định 0.97")
    p.add_argument("--json", action="store_true", help="in json thay cho chữ")


def _doc_tep(duong: str) -> str:
    try:
        return Path(duong).read_text(encoding="utf-8-sig")
    except OSError as e:
        raise LoiKit(f"không đọc được {duong}: {e.strerror}") from e


def chay(a: argparse.Namespace) -> int:
    loi = _doc_tep(a.text)
    try:
        du_lieu = json.loads(_doc_tep(a.words))
    except json.JSONDecodeError as e:
        raise LoiKit(f"{a.words} không phải json hợp lệ: {e}") from e
    lang = a.lang or du_lieu.get("language") or "vi"
    nguong = a.min / 100 if a.min > 1 else a.min
    kq = so(loi, du_lieu, lang, nguong)
    ti_le = kq.pop("_ti_le")
    for x in kq["issues"]:
        x["_gan"] = x.pop("_gan_ms")
    if a.json:
        ra = {**kq, "issues": [{k: v for k, v in x.items() if k != "_gan"} for x in kq["issues"]]}
        print(json.dumps(ra, ensure_ascii=False, indent=2))
        return 0
    pct = math.floor(ti_le * 1000) / 10
    ng = f"{nguong * 100:g}%"
    print(f"✓ {pct:.1f}% (≥ {ng})" if kq["pass"] else f"✗ {pct:.1f}% (< {ng}) · {len(kq['issues'])} chỗ lệch")
    for x in kq["issues"][:50]:
        co_gio = x["start_ms"] is not None
        gio = _dong_ho(x["start_ms"] if co_gio else x["_gan"])
        print(f"  {'' if co_gio else '~'}{gio}  chuẩn «{x['expected']}» / nghe «{x['heard']}»")
    return 0
