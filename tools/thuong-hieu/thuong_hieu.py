"""Máy dựng bộ nhận diện kênh từ một tệp cấu hình, hoàn toàn bằng code (không ảnh AI).

python -I -X utf8 tools/thuong-hieu/thuong_hieu.py --cau-hinh kenh/thuong-hieu/thuong-hieu.json --ra <thư mục ra>
Tuỳ chọn: --chrome <đường dẫn> (mặc định khoá `chrome` trong cau-hinh.toml), --font-dir <thư mục font>,
          --bo-qua-kiem-mau (chỉ dùng khi người dùng đã biết rủi ro trùng kênh mẫu).

Ra, với mỗi hướng bố cục <bc> (vach | tron | gach):
  <ra>/<bc>/svg/      logo-dung-*.svg, logo-ngang-*.svg (toi | sang | mot-mau-chu | mot-mau-nen), bieu-tuong.svg
  <ra>/<bc>/png/      cùng tên, nền trong; logo-anh-bia.png (cao 176 px, đặt cao 44 px trên ảnh bìa 1280x720)
  <ra>/<bc>/youtube/  anh-dai-dien-800.png, banner-2560x1440.jpg (nội dung trong vùng an toàn 1546x423), dau-kenh-150.png
  <ra>/soi.jpg        ảnh soi hướng đầu (hướng khác: soi-<bc>.jpg)
Chữ dựng bằng font OFL trong template/fonts rồi đổi sang path, nên SVG không phụ thuộc font cài trên máy xem.
Máy này không chứa logo hay chữ nào của kênh mẫu; bảng màu được kiểm bằng kiem-mau.py của skill goha-ho-so-kenh.
"""
from __future__ import annotations

import argparse
import colorsys
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
BO_CUC = ("vach", "tron", "gach")
BAN = ("toi", "sang", "mot-mau-chu", "mot-mau-nen")
AN_TOAN = (1546, 423)  # vùng an toàn banner YouTube
BANNER = (2560, 1440)
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
FONT_MAC_DINH = {"tieu_de": "Oswald-VF.ttf", "tieu_de_wght": 600, "noi_dung": "BeVietnamPro-Medium.ttf"}


class CauHinhLoi(ValueError):
    """Cấu hình thiếu hoặc sai; thông điệp nói rõ khoá nào và sửa gì."""


# ---------- cấu hình ----------

def tim_repo(tu: Path = HERE) -> Path:
    for p in [tu, *tu.parents]:
        if (p / "cau-hinh.mau.toml").exists():
            return p
    raise CauHinhLoi("Không thấy cau-hinh.mau.toml ở thư mục cha nào; chạy máy dựng trong repo kit.")


def doc_cau_hinh(duong: Path) -> dict:
    try:
        raw = json.loads(Path(duong).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        raise CauHinhLoi(f"Không thấy tệp cấu hình {duong}.") from None
    except json.JSONDecodeError as e:
        raise CauHinhLoi(f"Tệp cấu hình {duong} không phải JSON hợp lệ: {e}.") from None
    return kiem_cau_hinh(raw)


def nfc(v) -> str:
    """Chuỗi chuẩn NFC (dấu dựng sẵn) để font tìm đủ glyph."""
    return unicodedata.normalize("NFC", str(v or "").strip())


def kiem_cau_hinh(raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise CauHinhLoi("Cấu hình phải là một đối tượng JSON.")
    ten = nfc(raw.get("ten"))
    if not ten:
        raise CauHinhLoi("Thiếu khoá «ten» (tên kênh, chữ chính).")
    mau = raw.get("mau")
    if not isinstance(mau, dict):
        raise CauHinhLoi("Thiếu khoá «mau» gồm «nen», «chu», «nhan» (mã #rrggbb).")
    for vai in ("nen", "chu", "nhan"):
        v = mau.get(vai)
        if not v:
            raise CauHinhLoi(f"Thiếu màu «mau.{vai}».")
        if not HEX.match(str(v)):
            raise CauHinhLoi(f"Màu «mau.{vai}» = {v!r} không đúng dạng #rrggbb.")
    bo_cuc = raw.get("bo_cuc") or ["vach"]
    if isinstance(bo_cuc, str):
        bo_cuc = [bo_cuc]
    if not isinstance(bo_cuc, list) or not 1 <= len(bo_cuc) <= 3:
        raise CauHinhLoi("«bo_cuc» là danh sách 1 đến 3 hướng.")
    for b in bo_cuc:
        if b not in BO_CUC:
            raise CauHinhLoi(f"Hướng bố cục {b!r} không có; chọn trong {', '.join(BO_CUC)}.")
    if len(set(bo_cuc)) != len(bo_cuc):
        raise CauHinhLoi("«bo_cuc» có hướng trùng nhau.")
    handle = nfc(raw.get("handle"))
    if handle and not handle.startswith("@"):
        raise CauHinhLoi("«handle» phải bắt đầu bằng @.")
    font = {**FONT_MAC_DINH, **(raw.get("font") or {})}
    ten_viet_tat = nfc(raw.get("viet_tat")) or viet_tat(ten)
    return {
        "ten": ten,
        "chu_phu": nfc(raw.get("chu_phu")),
        "khau_hieu": nfc(raw.get("khau_hieu")),
        "handle": handle,
        "viet_tat": ten_viet_tat,
        "mau": {k: str(mau[k]).lower() for k in ("nen", "chu", "nhan")},
        "font": font,
        "bo_cuc": list(bo_cuc),
    }


def viet_tat(ten: str) -> str:
    """Chữ cái đầu của tối đa hai từ đầu: «Sử Thép» -> ST."""
    tu = [t for t in re.split(r"\s+", ten.strip()) if t]
    return "".join(t[0] for t in tu[:2]).upper() or ten[:1].upper()


def thieu_do_tuong_phan(cfg: dict) -> list[str]:
    """Lỗi tương phản: chữ trên nền ≥ 4,5:1, nhấn trên nền ≥ 3:1."""
    m = cfg["mau"]
    loi = []
    if tuong_phan(m["chu"], m["nen"]) < 4.5:
        loi.append(f"Chữ {m['chu']} trên nền {m['nen']} chỉ {tuong_phan(m['chu'], m['nen']):.1f}:1, cần ≥ 4,5:1.")
    if tuong_phan(m["nhan"], m["nen"]) < 3:
        loi.append(f"Nhấn {m['nhan']} trên nền {m['nen']} chỉ {tuong_phan(m['nhan'], m['nen']):.1f}:1, cần ≥ 3:1.")
    return loi


def sang_tuong_doi(h: str) -> float:
    def kenh(i: int) -> float:
        c = int(h[i:i + 2], 16) / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * kenh(1) + 0.7152 * kenh(3) + 0.0722 * kenh(5)


def tuong_phan(a: str, b: str) -> float:
    la, lb = sorted((sang_tuong_doi(a), sang_tuong_doi(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def nap_kiem_mau(repo: Path):
    tep = repo / ".claude/skills/goha-ho-so-kenh/scripts/kiem-mau.py"
    if not tep.exists():
        raise CauHinhLoi(f"Thiếu {tep}; không kiểm được màu có trùng kênh mẫu không.")
    spec = importlib.util.spec_from_file_location("kiem_mau_kenh_mau", tep)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mau_trung_kenh_mau(cfg: dict, repo: Path) -> list[str]:
    km = nap_kiem_mau(repo)
    ra = []
    for vai, m in cfg["mau"].items():
        for ten, ref in km.MAU_MAU.items():
            if km.gan(m, ref):
                ra.append(f"mau.{vai} = {m} gần {ten}")
    return ra


def ke_hoach_dau_ra(ra: Path, bc: str) -> dict[str, Path]:
    """Danh sách tệp đầu ra của một hướng, khoá = tên ngắn."""
    d = Path(ra) / bc
    kq = {}
    for kieu in ("dung", "ngang"):
        for ban in BAN:
            kq[f"svg/logo-{kieu}-{ban}"] = d / "svg" / f"logo-{kieu}-{ban}.svg"
            kq[f"png/logo-{kieu}-{ban}"] = d / "png" / f"logo-{kieu}-{ban}.png"
    kq["svg/bieu-tuong"] = d / "svg" / "bieu-tuong.svg"
    kq["png/bieu-tuong"] = d / "png" / "bieu-tuong.png"
    kq["png/logo-anh-bia"] = d / "png" / "logo-anh-bia.png"
    kq["youtube/anh-dai-dien"] = d / "youtube" / "anh-dai-dien-800.png"
    kq["youtube/banner"] = d / "youtube" / "banner-2560x1440.jpg"
    kq["youtube/dau-kenh"] = d / "youtube" / "dau-kenh-150.png"
    return kq


# ---------- chữ thành path ----------

class Font:
    def __init__(self, tep: Path, wght: float | None = None):
        from fontTools.ttLib import TTFont
        if not Path(tep).exists():
            raise CauHinhLoi(f"Không thấy font {tep}; chọn tệp có trong template/fonts.")
        self.f = TTFont(tep)
        loc = {"wght": float(wght)} if wght and "fvar" in self.f else None
        self.gs = self.f.getGlyphSet(location=loc) if loc else self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.cap = getattr(self.f["OS/2"], "sCapHeight", 0) or int(self.upm * 0.7)
        self.ten = Path(tep).name

    def glyph(self, c: str):
        ten = self.cmap.get(ord(c))
        if ten is None:
            raise CauHinhLoi(f"Font {self.ten} không có ký tự {c!r}; chọn font khác hoặc đổi chữ.")
        return self.gs[ten]

    def rong(self, chu: str, co: float, giang: float = 0.0) -> float:
        k = co / self.upm
        if not chu:
            return 0.0
        return sum(self.glyph(c).width * k for c in chu) + giang * co * (len(chu) - 1)

    def cao_hoa(self, co: float) -> float:
        return self.cap * co / self.upm

    def path(self, chu: str, co: float, x: float, y_day: float, giang: float = 0.0) -> str:
        from fontTools.pens.svgPathPen import SVGPathPen
        from fontTools.pens.transformPen import TransformPen
        k = co / self.upm
        d = []
        for c in chu:
            g = self.glyph(c)
            pen = SVGPathPen(self.gs)
            g.draw(TransformPen(pen, (k, 0, 0, -k, x, y_day)))
            cm = pen.getCommands()
            if cm:
                d.append(cm)
            x += g.width * k + giang * co
        return " ".join(d)


def nap_font(cfg: dict, font_dir: Path) -> tuple[Font, Font]:
    f = cfg["font"]
    return (Font(Path(font_dir) / f["tieu_de"], f.get("tieu_de_wght")),
            Font(Path(font_dir) / f["noi_dung"], f.get("noi_dung_wght")))


# ---------- dựng hình SVG ----------

def mau_ban(cfg: dict, ban: str) -> dict:
    """Màu chữ, nhấn, nền-dấu cho từng bản. Bản sáng dùng màu tối hơn trong cặp nền/chữ."""
    m = cfg["mau"]
    if ban == "toi":
        return {"chu": m["chu"], "nhan": m["nhan"], "phu": m["nhan"]}
    toi = min((m["nen"], m["chu"]), key=sang_tuong_doi)
    nhan_sang = m["nhan"] if tuong_phan(m["nhan"], "#ffffff") >= 3 else toi
    if ban == "sang":
        return {"chu": toi, "nhan": nhan_sang, "phu": nhan_sang}
    if ban == "mot-mau-chu":
        return {"chu": m["chu"], "nhan": m["chu"], "phu": m["chu"]}
    return {"chu": m["nen"], "nhan": m["nen"], "phu": m["nen"]}


def bieu_tuong(cfg: dict, tt: Font, bc: str, co: float, mau: dict, nen_tam: str | None = None) -> str:
    """Dấu chữ lồng (viết tắt) trong khung theo hướng; hộp co x co, gốc (0,0)."""
    c, n = mau["chu"], mau["nhan"]
    chu = cfg["viet_tat"]
    cs = co * 0.42
    while tt.rong(chu, cs, 0.02) > co * 0.62 and cs > 4:
        cs *= 0.95
    w = tt.rong(chu, cs, 0.02)
    cap = tt.cao_hoa(cs)
    x = (co - w) / 2
    y_day = co / 2 + cap / 2
    if bc == "gach":
        y_day -= co * 0.05
    fill = f'fill="{nen_tam}"' if nen_tam else 'fill="none"'
    s = []
    if bc == "tron":
        s.append(f'<circle cx="{co / 2:.1f}" cy="{co / 2:.1f}" r="{co * 0.465:.1f}" {fill} stroke="{n}" stroke-width="{co * 0.05:.1f}"/>')
    elif bc == "vach":
        s.append(f'<rect x="{co * 0.04:.1f}" y="{co * 0.04:.1f}" width="{co * 0.92:.1f}" height="{co * 0.92:.1f}" rx="{co * 0.06:.1f}" {fill} stroke="{n}" stroke-width="{co * 0.035:.1f}"/>')
        s.append(f'<rect x="{co * 0.04:.1f}" y="{co * 0.04:.1f}" width="{co * 0.11:.1f}" height="{co * 0.92:.1f}" rx="{co * 0.03:.1f}" fill="{n}"/>')
        x += co * 0.04
    else:  # gach
        if nen_tam:
            s.append(f'<rect x="0" y="0" width="{co}" height="{co}" rx="{co * 0.04:.1f}" fill="{nen_tam}"/>')
        s.append(f'<rect x="{co * 0.18:.1f}" y="{y_day + cap * 0.30:.1f}" width="{co * 0.64:.1f}" height="{co * 0.055:.1f}" fill="{n}"/>')
    s.append(f'<path fill="{c}" d="{tt.path(chu, cs, x, y_day, 0.02)}"/>')
    return "".join(s)


def khoi_chu(cfg: dict, tt: Font, nd: Font, bc: str, co: float, mau: dict, canh: str = "trai") -> tuple[str, float, float]:
    """Tên kênh + chữ phụ (+ gạch dưới với hướng gach). Gốc (0,0) góc trên-trái. Trả (svg, rộng, cao)."""
    ten = cfg["ten"].upper()
    giang_ten = 0.04
    w_ten = tt.rong(ten, co, giang_ten)
    cap = tt.cao_hoa(co)
    phu = cfg["chu_phu"].upper()
    cs = co * 0.34
    giang_phu = 0.32
    w_phu = nd.rong(phu, cs, giang_phu) if phu else 0
    w = max(w_ten, w_phu)
    x_ten = 0 if canh == "trai" else (w - w_ten) / 2
    y = cap
    s = [f'<path fill="{mau["chu"]}" d="{tt.path(ten, co, x_ten, y, giang_ten)}"/>']
    h = cap
    if bc == "gach":
        dày = max(co * 0.06, 2)
        s.append(f'<rect x="{x_ten:.1f}" y="{h + co * 0.16:.1f}" width="{w_ten:.1f}" height="{dày:.1f}" fill="{mau["nhan"]}"/>')
        h += co * 0.16 + dày
    if phu:
        gap = co * 0.28
        x_phu = 0 if canh == "trai" else (w - w_phu) / 2
        yb = h + gap + nd.cao_hoa(cs)
        s.append(f'<path fill="{mau["phu"]}" d="{nd.path(phu, cs, x_phu, yb, giang_phu)}"/>')
        h = yb
    return "".join(s), w, h


def logo(cfg: dict, tt: Font, nd: Font, bc: str, kieu: str, ban: str) -> tuple[str, float, float]:
    """Logo nền trong. Trả (svg, rộng, cao) theo đơn vị viewBox."""
    mau = mau_ban(cfg, ban)
    CO = 100.0
    mark = bieu_tuong(cfg, tt, bc, CO * 1.5, mau)
    chu, wc, hc = khoi_chu(cfg, tt, nd, bc, CO, mau, "trai" if kieu == "ngang" else "giua")
    pad = 20
    if kieu == "ngang":
        M = CO * 1.5
        gap = CO * 0.35
        H = max(M, hc)
        w = M + gap + wc
        thân = (f'<g transform="translate(0 {(H - M) / 2:.1f})">{mark}</g>'
                f'<g transform="translate({M + gap:.1f} {(H - hc) / 2:.1f})">{chu}</g>')
    else:
        M = CO * 1.5
        gap = CO * 0.3
        w = max(M, wc)
        H = M + gap + hc
        thân = (f'<g transform="translate({(w - M) / 2:.1f} 0)">{mark}</g>'
                f'<g transform="translate({(w - wc) / 2:.1f} {M + gap:.1f})">{chu}</g>')
    W, Hh = w + 2 * pad, H + 2 * pad
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {Hh:.0f}" width="{W:.0f}" height="{Hh:.0f}">'
           f'<title>{esc(cfg["ten"])}</title><g transform="translate({pad} {pad})">{thân}</g></svg>')
    return svg, W, Hh


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_bieu_tuong(cfg: dict, tt: Font, bc: str, ban: str = "toi", co: int = 512) -> str:
    mau = mau_ban(cfg, ban)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {co} {co}" width="{co}" height="{co}">'
            f'<title>{esc(cfg["ten"])}</title>{bieu_tuong(cfg, tt, bc, co, mau)}</svg>')


def svg_anh_dai_dien(cfg: dict, tt: Font, bc: str, co: int = 800) -> str:
    m = cfg["mau"]
    mau = {"chu": m["chu"], "nhan": m["nhan"], "phu": m["nhan"]}
    k = 0.76
    o = co * (1 - k) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {co} {co}" width="{co}" height="{co}">'
            f'<rect width="{co}" height="{co}" fill="{m["nen"]}"/>'
            f'<g transform="translate({o:.1f} {o:.1f})">{bieu_tuong(cfg, tt, bc, co * k, mau)}</g></svg>')


def svg_dau_kenh(cfg: dict, tt: Font, bc: str, co: int = 150) -> str:
    m = cfg["mau"]
    mau = {"chu": m["chu"], "nhan": m["nhan"], "phu": m["nhan"]}
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {co} {co}" width="{co}" height="{co}">'
            f'{bieu_tuong(cfg, tt, bc, co, mau, nen_tam=m["nen"])}</svg>')


def noi_dung_banner(cfg: dict, tt: Font, nd: Font, bc: str) -> tuple[str, float, float]:
    """Khối chữ giữa banner ở cỡ danh nghĩa (gốc 0,0). Trả (svg, rộng, cao)."""
    mau = {"chu": cfg["mau"]["chu"], "nhan": cfg["mau"]["nhan"], "phu": cfg["mau"]["nhan"]}
    CO = 100.0
    M = CO * 1.5
    mark = bieu_tuong(cfg, tt, bc, M, mau)
    chu, wc, hc = khoi_chu(cfg, tt, nd, bc, CO, mau, "trai")
    gap = CO * 0.35
    H1 = max(M, hc)
    W1 = M + gap + wc
    phan = [f'<g transform="translate(0 {(H1 - M) / 2:.1f})">{mark}</g>',
            f'<g transform="translate({M + gap:.1f} {(H1 - hc) / 2:.1f})">{chu}</g>']
    # chừa chỗ cho dấu tiếng Việt trên chữ hoa (Ử, É...) vượt quá chiều cao chữ hoa
    tren = CO * 0.30
    phan = [f'<g transform="translate(0 {tren:.1f})">{"".join(phan)}</g>']
    W, H = W1, H1 + tren
    dong = []
    if cfg["khau_hieu"]:
        dong.append((cfg["khau_hieu"], CO * 0.30, cfg["mau"]["chu"], 0.02))
    if cfg["handle"]:
        dong.append((cfg["handle"], CO * 0.26, cfg["mau"]["nhan"], 0.04))
    for txt, cs, mc, gi in dong:
        wt = nd.rong(txt, cs, gi)
        H += CO * 0.42 + nd.cao_hoa(cs)
        phan.append(f'<path fill="{mc}" d="{nd.path(txt, cs, 0, H, gi)}"/>')
        W = max(W, wt)
    # canh giữa theo chiều ngang
    giua = []
    giua.append(f'<g transform="translate({(W - W1) / 2:.1f} 0)">{phan[0]}</g>')
    for i, (txt, cs, mc, gi) in enumerate(dong):
        wt = nd.rong(txt, cs, gi)
        giua.append(f'<g transform="translate({(W - wt) / 2:.1f} 0)">{phan[1 + i]}</g>')
    return "".join(giua), W, H


def hinh_banner(cfg: dict, tt: Font, nd: Font, bc: str) -> tuple[str, tuple[float, float]]:
    """Banner 2560x1440; trả (svg, (rộng, cao) nội dung sau co giãn) để kiểm vùng an toàn."""
    m = cfg["mau"]
    ban, W, H = noi_dung_banner(cfg, tt, nd, bc)
    k = min(AN_TOAN[0] * 0.90 / W, AN_TOAN[1] * 0.90 / H)
    cx, cy = BANNER[0] / 2, BANNER[1] / 2
    rw, rh = W * k, H * k
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BANNER[0]} {BANNER[1]}" width="{BANNER[0]}" height="{BANNER[1]}">'
           f'<defs><pattern id="soc" width="64" height="64" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">'
           f'<rect width="3" height="64" fill="{m["nhan"]}" opacity="0.09"/></pattern>'
           f'<radialGradient id="sang" cx="50%" cy="50%" r="60%"><stop offset="0" stop-color="{m["chu"]}" stop-opacity="0.10"/>'
           f'<stop offset="1" stop-color="{m["chu"]}" stop-opacity="0"/></radialGradient></defs>'
           f'<rect width="{BANNER[0]}" height="{BANNER[1]}" fill="{m["nen"]}"/>'
           f'<rect width="{BANNER[0]}" height="{BANNER[1]}" fill="url(#soc)"/>'
           f'<rect width="{BANNER[0]}" height="{BANNER[1]}" fill="url(#sang)"/>'
           f'<g transform="translate({cx - rw / 2:.1f} {cy - rh / 2:.1f}) scale({k:.5f})">{ban}</g></svg>')
    return svg, (rw, rh)


# ---------- chụp bằng Chrome ----------

CHROME_HET_GIO_GIAY = 60


def chrome_chup(chrome: str, svg: str, w: int, h: int, ra: Path, nen_trong: bool = True) -> None:
    """Chụp SVG thành ảnh bằng Chrome headless với hồ sơ tạm riêng; lỗi thì ném CauHinhLoi kèm đuôi stderr."""
    from PIL import Image
    ra = Path(ra)
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as t:
        p = Path(t) / "x.html"
        p.write_text('<html><body style="margin:0;background:transparent">' + svg + "</body></html>", encoding="utf-8")
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
               "--no-first-run", "--no-default-browser-check", f"--user-data-dir={Path(t) / 'ho-so'}",
               "--default-background-color=00000000", f"--window-size={w},{h}", "--virtual-time-budget=10000",
               f"--screenshot={ra}", p.as_uri()]
        try:
            kq = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=CHROME_HET_GIO_GIAY)
        except subprocess.TimeoutExpired:
            raise CauHinhLoi(f"Chrome chạy quá {CHROME_HET_GIO_GIAY} giây khi chụp {ra.name}; đã dừng. "
                             "Đóng các cửa sổ Chrome treo rồi chạy lại.") from None
        except OSError as e:
            raise CauHinhLoi(f"Không chạy được Chrome {chrome}: {e}") from None
    duoi = " | ".join((kq.stderr or "").strip().splitlines()[-5:])
    if kq.returncode != 0:
        raise CauHinhLoi(f"Chrome lỗi (mã {kq.returncode}) khi chụp {ra.name}: {duoi or 'không có thông báo'}")
    if not ra.exists() or ra.stat().st_size == 0:
        raise CauHinhLoi(f"Chrome không tạo ra ảnh {ra.name}. {duoi}".strip())
    im = Image.open(ra).convert("RGBA")
    if im.size != (w, h):
        im = im.crop((0, 0, w, h))
    im.save(ra)


def svg_doi_cao(svg: str, cao: int) -> tuple[str, int]:
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)" width="[\d.]+" height="[\d.]+"', svg)
    w0, h0 = float(m.group(1)), float(m.group(2))
    w = round(w0 * cao / h0)
    return svg.replace(f'width="{w0:.0f}" height="{h0:.0f}"', f'width="{w}" height="{cao}"', 1), w


def cat_sat(p: Path, pad: int) -> None:
    from PIL import Image
    im = Image.open(p).convert("RGBA")
    box = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    im = im.crop(box)
    nen = Image.new("RGBA", (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0))
    nen.alpha_composite(im, (pad, pad))
    nen.save(p)


def dung_mot_huong(cfg: dict, tt: Font, nd: Font, bc: str, ra: Path, chrome: str) -> dict:
    from PIL import Image
    kh = ke_hoach_dau_ra(ra, bc)
    for p in kh.values():
        p.parent.mkdir(parents=True, exist_ok=True)
    for kieu, cao in (("dung", 600), ("ngang", 400)):
        for ban in BAN:
            svg, _, _ = logo(cfg, tt, nd, bc, kieu, ban)
            kh[f"svg/logo-{kieu}-{ban}"].write_text(svg, encoding="utf-8", newline="")
            s2, w = svg_doi_cao(svg, cao)
            chrome_chup(chrome, s2, w, cao, kh[f"png/logo-{kieu}-{ban}"])
    sv = svg_bieu_tuong(cfg, tt, bc)
    kh["svg/bieu-tuong"].write_text(sv, encoding="utf-8", newline="")
    chrome_chup(chrome, sv, 512, 512, kh["png/bieu-tuong"])
    svg, _, _ = logo(cfg, tt, nd, bc, "ngang", "toi")
    s2, w = svg_doi_cao(svg, 176)
    chrome_chup(chrome, s2, w, 176, kh["png/logo-anh-bia"])
    cat_sat(kh["png/logo-anh-bia"], 8)
    chrome_chup(chrome, svg_anh_dai_dien(cfg, tt, bc), 800, 800, kh["youtube/anh-dai-dien"])
    chrome_chup(chrome, svg_dau_kenh(cfg, tt, bc), 150, 150, kh["youtube/dau-kenh"])
    banner, _ = hinh_banner(cfg, tt, nd, bc)
    tam = kh["youtube/banner"].with_suffix(".tam.png")
    try:
        chrome_chup(chrome, banner, *BANNER, tam)
        Image.open(tam).convert("RGB").save(kh["youtube/banner"], quality=92)
    finally:
        tam.unlink(missing_ok=True)
    return kh


# ---------- ảnh soi ----------

def _font_soi(cfg: dict, font_dir: Path, co: int):
    """Font nội dung theo cấu hình; thiếu thì thử BeVietnamPro-Medium, rồi font mặc định của Pillow."""
    from PIL import ImageFont
    for ten in (cfg["font"]["noi_dung"], "BeVietnamPro-Medium.ttf"):
        try:
            return ImageFont.truetype(str(font_dir / ten), co)
        except OSError:
            continue
    return ImageFont.load_default(co)


def ghep_soi(cfg: dict, kh: dict, font_dir: Path, dich: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont
    W = 1920
    nen_sheet = (28, 28, 30)
    ft = _font_soi(cfg, Path(font_dir), 22)
    banner = Image.open(kh["youtube/banner"]).convert("RGB").resize((W, 1080), Image.LANCZOS)
    d = ImageDraw.Draw(banner)
    sw, sh = AN_TOAN[0] * 0.75, AN_TOAN[1] * 0.75
    box = ((W - sw) / 2, (1080 - sh) / 2, (W + sw) / 2, (1080 + sh) / 2)
    for i in range(0, int(sw), 24):  # khung vùng an toàn nét đứt
        d.line([(box[0] + i, box[1]), (min(box[0] + i + 12, box[2]), box[1])], fill=(255, 60, 60), width=2)
        d.line([(box[0] + i, box[3]), (min(box[0] + i + 12, box[2]), box[3])], fill=(255, 60, 60), width=2)
    for i in range(0, int(sh), 24):
        d.line([(box[0], box[1] + i), (box[0], min(box[1] + i + 12, box[3]))], fill=(255, 60, 60), width=2)
        d.line([(box[2], box[1] + i), (box[2], min(box[1] + i + 12, box[3]))], fill=(255, 60, 60), width=2)
    # nền xem trước: cột đại diện, dấu kênh, logo hai nền
    hang = Image.new("RGB", (W, 520), nen_sheet)
    dh = ImageDraw.Draw(hang)
    m = cfg["mau"]
    ava = Image.open(kh["youtube/anh-dai-dien"]).convert("RGB")
    x = 30
    for co in (400, 98, 40):
        a = ava.resize((co, co), Image.LANCZOS)
        mask = Image.new("L", (co * 4, co * 4), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, co * 4 - 1, co * 4 - 1], fill=255)
        hang.paste(a, (x, 30), mask.resize((co, co), Image.LANCZOS))
        dh.text((x, 440), f"{co}px", font=ft, fill=(210, 210, 210))
        x += co + 30
    khung = Image.new("RGB", (480, 270), (92, 100, 96))
    kd = ImageDraw.Draw(khung)
    for i in range(0, 480, 40):
        kd.line([(i, 0), (i - 100, 270)], fill=(108, 116, 112), width=10)
    dau = Image.open(kh["youtube/dau-kenh"]).convert("RGBA")
    dau.putalpha(dau.getchannel("A").point(lambda a: int(a * 0.58)))
    khung.paste(dau, (480 - 150 - 16, 270 - 150 - 16), dau)
    hang.paste(khung, (x + 20, 30))
    dh.text((x + 20, 310), "dấu kênh 150px, mờ 58% trên khung phim", font=ft, fill=(210, 210, 210))
    x2 = x + 20 + 480 + 40
    toi_cao = 0
    for ban, nen in (("toi", m["nen"]), ("sang", "#f4f4f2")):
        lg = Image.open(kh[f"png/logo-ngang-{ban}"]).convert("RGBA")
        w2 = 640 if x2 + 640 <= W else W - x2 - 10
        if w2 < 200:
            x2, w2 = 30, 640
        r = lg.resize((w2, round(lg.height * w2 / lg.width)), Image.LANCZOS)
        y = 30 if ban == "toi" else 30 + 20 + toi_cao
        blk = Image.new("RGB", (w2 + 20, r.height + 20), nen)
        blk.paste(r, (10, 10), r)
        hang.paste(blk, (x2, y))
        toi_cao = blk.height
    # ghép: banner trên cùng, hàng dưới
    sheet = Image.new("RGB", (W, 1080 + 520), nen_sheet)
    sheet.paste(banner, (0, 0))
    sheet.paste(hang, (0, 1080))
    dich.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(dich, quality=90)


# ---------- chạy ----------

def chay(args: argparse.Namespace) -> int:
    repo = tim_repo()
    cfg = doc_cau_hinh(Path(args.cau_hinh))
    loi = thieu_do_tuong_phan(cfg)
    if loi:
        print("Màu chưa đạt tương phản:\n  " + "\n  ".join(loi))
        return 4
    if not args.bo_qua_kiem_mau:
        trung = mau_trung_kenh_mau(cfg, repo)
        if trung:
            print("DỪNG: màu trùng họ màu kênh mẫu (ô-liu, vàng đồng):\n  " + "\n  ".join(trung)
                  + "\nĐổi màu rồi chạy lại.")
            return 3
    chrome = args.chrome
    if not chrome:
        sys.path.insert(0, str(repo / "tools"))
        from cau_hinh import duong
        chrome = str(duong("chrome"))
    font_dir = Path(args.font_dir) if args.font_dir else repo / "template/fonts"
    tt, nd = nap_font(cfg, font_dir)
    ra = Path(args.ra)
    for i, bc in enumerate(cfg["bo_cuc"]):
        kh = dung_mot_huong(cfg, tt, nd, bc, ra, chrome)
        soi = ra / ("soi.jpg" if i == 0 else f"soi-{bc}.jpg")
        ghep_soi(cfg, kh, font_dir, soi)
        print(f"[{bc}] xong, ảnh soi: {soi}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Dựng bộ nhận diện kênh từ tệp cấu hình.")
    ap.add_argument("--cau-hinh", required=True, help="Tệp JSON thương hiệu của kênh")
    ap.add_argument("--ra", required=True, help="Thư mục ra")
    ap.add_argument("--chrome", help="Đường dẫn Chrome/Edge (mặc định: khoá chrome trong cau-hinh.toml)")
    ap.add_argument("--font-dir", help="Thư mục font (mặc định: template/fonts)")
    ap.add_argument("--bo-qua-kiem-mau", action="store_true", help="Bỏ qua kiểm trùng màu kênh mẫu")
    args = ap.parse_args(argv)
    try:
        return chay(args)
    except CauHinhLoi as e:
        print(f"LỖI: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
