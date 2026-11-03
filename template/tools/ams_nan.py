"""Nắn các tờ bản đồ AMS lòng chảo Điện Biên Phủ vào hệ toạ độ của map3d và ghép thành một texture liền.

Logic nằm ở mô-đun này (import được để test); chạy bằng tools/nan-ban-do-ams.py (từ thư mục template/):
  python -I -X utf8 tools/nan-ban-do-ams.py [--no-warp] [--from-pdf-west <pdf>]
Phụ thuộc: numpy, opencv-python, scipy; thêm PyMuPDF chỉ khi dùng --from-pdf-west.
Hai tờ (đều là tài liệu quân sự Hoa Kỳ, công cộng; nguồn và giấy phép ở data/ams-nguon.md):
  5651 IV  Điện Biên Phủ, L7014, 1:50.000, 103°00'-103°15'E   data/ams-5651-4.jpg
  5551 I   Ban Thin Toc, L7015, 1:50.000, 102°45'-103°00'E    data/ams-5551-1.jpg  (kề phía Tây)
Đầu ra:
  data/ams-5651-4.georef.json        tham số nắn từng tờ: điểm khống chế, ma trận, sai số; khung texture
  data/ams-5651-4.texture.jpg        hai tờ đã nắn sang lưới Mercator WGS84, đúng UV map3d
  data/ams-5651-4.texture-mask.png   mặt nạ phủ (0 = ngoài các tờ, mép ngoài mờ dần, mép giữa hai tờ liền)

Mỗi tờ:
  1. Đo bốn đường khung tờ, dựng phép chiếu thô từ bốn góc (kinh vĩ độ qua Everest UTM).
  2. Tối ưu từng đường lưới UTM 1 km thành đường thẳng bám cả chiều dài ảnh; giao điểm là điểm khống chế.
  3. Khớp phép chiếu H (E, N) <-> pixel; báo RMS pixel và mét; kiểm độc lập bằng bốn góc khung tờ.
  4. Nắn ảnh qua Mercator ngang ngược, dịch tâm Indian 1960 -> WGS84, trừ sai lệch còn lại của bản đồ.
Không dùng số ngẫu nhiên: cùng đầu vào cho đúng cùng kết quả.
"""
import argparse
import json
import os
import sys

import cv2
import numpy as np

try:
    import scipy
    from scipy.ndimage import distance_transform_edt, map_coordinates
except ImportError as exc:  # pragma: no cover
    raise SystemExit('thiếu scipy: pip install scipy') from exc

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ams_georef as ag  # noqa: E402

DATA = os.path.join(HERE, '..', 'data')
OUT_JSON = os.path.join(DATA, 'ams-5651-4.georef.json')
OUT_TEX = os.path.join(DATA, 'ams-5651-4.texture.jpg')
OUT_MASK = os.path.join(DATA, 'ams-5651-4.texture-mask.png')

# Sai lệch còn lại của bản đồ so với thực địa (Đông, Bắc; mét), sau khi đã dịch tâm Indian 1960 -> WGS84.
# Đo bằng đối chiếu ảnh Sentinel-2 (đường băng, quốc lộ dọc lòng chảo) và đỉnh A1 (OSM) với ký hiệu ▲500.
SHEETS = [
    {'id': '5651-4', 'ten': 'Điện Biên Phủ', 'file': 'ams-5651-4.jpg', 'series': 'L7014', 'xuat_ban': 1966,
     'khung': {'west': 103.0, 'east': 103.25, 'south': 21.25, 'north': 21.5},
     'khung_px_goi_y': {'left': 136, 'right': 2388, 'top': 86, 'bottom': 2483},
     'lech_m': (35.0, 0.0), 'canh_chung': 'left'},
    {'id': '5551-1', 'ten': 'Ban Thin Toc', 'file': 'ams-5551-1.jpg', 'series': 'L7015', 'xuat_ban': 1968,
     'khung': {'west': 102.75, 'east': 103.0, 'south': 21.25, 'north': 21.5},
     'khung_px_goi_y': {'left': 202, 'right': 2451, 'top': 118, 'bottom': 2513},
     'lech_m': (35.0, 0.0), 'canh_chung': 'right'},
]
TEX_WEST_LIMIT = 102.90  # cắt texture ở kinh độ này: lòng chảo DEM bắt đầu 102.92, không cần phần xa hơn
TEX_LONG_SIDE = 4096
FEATHER_PX = 24.0   # độ mờ mép ngoài tờ (pixel ảnh gốc, 1 px = 11,5 m)
EDGE_CUT_PX = 5.0   # cắt sát khung tờ để không dính nét khung và nhãn mép
SEAM_CUT_PX = 3.0   # mép giữa hai tờ: bỏ nét khung và dải giấy trắng sát khung
SEAM_EXTEND_PX = 7.0  # mỗi tờ kéo dài thêm bằng cách nhân bản điểm ảnh sát mép, hai tờ hoà vào nhau trên dải này
PDF_DPI = 110       # độ phân giải ảnh của tờ 5651 IV đang có (2493 px cho 1627 pt)


def pdf_to_jpg(pdf, out):
    try:
        import fitz
    except ImportError as exc:
        raise SystemExit('thiếu PyMuPDF để đọc PDF: pip install pymupdf') from exc
    pix = fitz.open(pdf)[0].get_pixmap(dpi=PDF_DPI, alpha=False)
    pix.save(out + '.png')
    img = cv2.imread(out + '.png')
    os.remove(out + '.png')
    cv2.imwrite(out, img, [cv2.IMWRITE_JPEG_QUALITY, 88])


def darkness(img):
    """Độ tối của nét: nét lưới đen có max(R,G,B) thấp. Chuẩn hoá về 0-1."""
    return (np.clip(150 - img.max(axis=2).astype(np.float32), 0, None) / 100).astype(np.float32)


def fit_line(dark, p0, p1, search=6.0, slope=0.003):
    """Tối ưu đoạn thẳng gần p0-p1 (toạ độ pixel (x, y), gần thẳng đứng hoặc nằm ngang) cực đại tổng độ tối.
    Trả hàm toạ độ: với đường dọc x = a*y + b, với đường ngang y = a*x + b, và điểm/px."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    vertical = abs(p1[1] - p0[1]) > abs(p1[0] - p0[0])
    k = 1 if vertical else 0           # trục chạy dọc đường
    lo, hi = sorted((p0[k], p1[k]))
    margin = 0.03 * (hi - lo)
    t = np.arange(lo + margin, hi - margin, 1.0)
    s0 = (p1[1 - k] - p0[1 - k]) / (p1[k] - p0[k])
    base = p0[1 - k] + s0 * (t - p0[k])
    mid = t.mean()

    def score(off, sl):
        p = base + off + sl * (t - mid)
        co = np.vstack([t, p]) if vertical else np.vstack([p, t])
        return float(map_coordinates(dark, co, order=1).sum())

    cands = [(o, s) for o in np.arange(-search, search + 0.01, 0.5) for s in np.arange(-slope, slope + 1e-9, 0.001)]
    off, sl = max(cands, key=lambda c: score(*c))
    for so, ss in ((0.25, 0.0004), (0.1, 0.0001), (0.04, 0.00004)):
        cands = [(off + i * so, sl + j * ss) for i in range(-2, 3) for j in range(-2, 3)]
        off, sl = max(cands, key=lambda c: score(*c))
    a = s0 + sl
    # p(t) = base + off + sl*(t-mid) = p0[1-k] + s0*(t-p0[k]) + off + sl*(t-mid) = a*t + b
    b = p0[1 - k] - s0 * p0[k] + off - sl * mid
    return a, b, vertical, score(off, sl) / len(t)


def intersect(v, h):
    """Giao điểm đường dọc x = a*y + b với đường ngang y = c*x + d."""
    a, b = v[0], v[1]
    c, d = h[0], h[1]
    x = (a * d + b) / (1 - a * c)
    return np.array([x, c * x + d])


def find_neatline(dark, hint):
    """Bốn góc khung tờ đo trên ảnh gốc: TL, TR, BR, BL."""
    h, w = dark.shape
    L, R, T, B = hint['left'], hint['right'], hint['top'], hint['bottom']
    left = fit_line(dark, (L, T + 80), (L, B - 80), search=8, slope=0.02)
    right = fit_line(dark, (R, T + 80), (R, B - 80), search=8, slope=0.02)
    top = fit_line(dark, (L + 80, T), (R - 80, T), search=8, slope=0.02)
    bot = fit_line(dark, (L + 80, B), (R - 80, B), search=8, slope=0.02)
    return {'TL': intersect(left, top), 'TR': intersect(right, top), 'BR': intersect(right, bot), 'BL': intersect(left, bot)}


def corners_en(khung):
    pts = {'TL': (khung['north'], khung['west']), 'TR': (khung['north'], khung['east']),
           'BR': (khung['south'], khung['east']), 'BL': (khung['south'], khung['west'])}
    return {k: tuple(float(v) for v in ag.tm_forward(la, lo)) for k, (la, lo) in pts.items()}


def find_grid(dark, nl, corners):
    """Giao điểm lưới 1 km: trả mảng (E, N, px, py) và danh sách đường điểm thấp."""
    order = ('TL', 'TR', 'BR', 'BL')
    h0 = ag.fit_homography([corners[k] for k in order], [nl[k] for k in order])
    es = [c[0] for c in corners.values()]
    ns = [c[1] for c in corners.values()]
    e_lines = range(int(np.ceil(min(es) / 1000)), int(np.floor(max(es) / 1000)) + 1)
    n_lines = range(int(np.ceil(min(ns) / 1000)), int(np.floor(max(ns) / 1000)) + 1)
    nlo, nhi = min(ns) + 4000.0, max(ns) - 4000.0
    elo, ehi = min(es) + 4000.0, max(es) - 4000.0
    vert, hori, weak = {}, {}, []
    for e in e_lines:
        p = ag.apply_homography(h0, [[e * 1000.0, nlo], [e * 1000.0, nhi]])
        a, b, _, sc = fit_line(dark, p[0], p[1])
        if sc < 0.2:
            weak.append(f'E{e}')   # đường bị nhãn, sông, nét khác che: bỏ khỏi khớp
        else:
            vert[e] = (a, b)
    for n in n_lines:
        p = ag.apply_homography(h0, [[elo, n * 1000.0], [ehi, n * 1000.0]])
        a, b, _, sc = fit_line(dark, p[0], p[1])
        if sc < 0.2:
            weak.append(f'N{n}')
        else:
            hori[n] = (a, b)
    pts = [(e * 1000.0, n * 1000.0, *intersect(v, hz)) for e, v in vert.items() for n, hz in hori.items()]
    return np.array(pts), weak, (e_lines, n_lines)


def sheet_georef(spec, img):
    dark = darkness(img)
    nl = find_neatline(dark, spec['khung_px_goi_y'])
    corners = corners_en(spec['khung'])
    pts, weak, (e_lines, n_lines) = find_grid(dark, nl, corners)
    en, px = pts[:, :2], pts[:, 2:]
    h_en2px = ag.fit_homography(en, px)
    h_px2en = ag.fit_homography(px, en)
    res_px = np.hypot(*(ag.apply_homography(h_en2px, en) - px).T)
    res_m = np.hypot(*(ag.apply_homography(h_px2en, px) - en).T)
    res_aff = np.hypot(*(ag.apply_homography(ag.fit_affine(en, px), en) - px).T)
    mpp = float(np.hypot(*(h_px2en[:2, :2] @ [1, 0])))
    check = []
    for k in ('TL', 'TR', 'BL', 'BR'):
        pred = ag.apply_homography(h_en2px, [corners[k]])[0]
        d = float(np.hypot(*(pred - nl[k])))
        check.append({'goc': k, 'E': round(corners[k][0], 1), 'N': round(corners[k][1], 1), 'px_do': [round(float(v), 1) for v in nl[k]],
                      'px_du_doan': [round(float(v), 1) for v in pred], 'lech_px': round(d, 2), 'lech_m': round(d * mpp, 1)})
    return {
        'id': spec['id'], 'ten': spec['ten'],
        'tai_lieu': {
            'tep_anh': spec['file'], 'kich_thuoc_anh': [img.shape[1], img.shape[0]],
            'to': f"AMS series {spec['series']}, tờ {spec['id'].replace('-', ' ')} {spec['ten'].upper()}, 1:50.000, xuất bản {spec['xuat_ban']}",
            'luoi': f"UTM vùng 48 (CM 105°E, k0 0,9996, FE 500000), lưới 1.000 m, nhãn E {e_lines[0]}-{e_lines[-1]}, N {n_lines[0]}-{n_lines[-1]}",
            'elip': 'Everest 1830 (hiệu chỉnh 1937): a = 6377276.345, 1/f = 300.8017',
            'datum_to': 'Indian Datum 1960', 'khung_to_indian1960': spec['khung'],
            'dich_tam_indian1960_sang_wgs84_m': list(ag.INDIAN1960_TO_WGS84),
            'sai_lech_con_lai_dong_bac_m': list(spec['lech_m']),
        },
        'm_tren_pixel': round(mpp, 3),
        'so_diem_khong_che': int(len(pts)),
        'mo_hinh': 'phép chiếu H (8 tham số) từ (E, N) UTM sang pixel và ngược lại',
        'sai_so_du': {
            'rms_pixel': round(float(np.sqrt((res_px ** 2).mean())), 3), 'rms_met': round(float(np.sqrt((res_m ** 2).mean())), 2),
            'max_pixel': round(float(res_px.max()), 3), 'max_met': round(float(res_m.max()), 2),
            'rms_pixel_neu_chi_affine': round(float(np.sqrt((res_aff ** 2).mean())), 3),
        },
        'kiem_doc_lap_khung_to': check,
        'duong_luoi_yeu': weak,
        'ma_tran_utm_sang_pixel': h_en2px.tolist(),
        'ma_tran_pixel_sang_utm': h_px2en.tolist(),
        'khung_to_px': {k: [round(float(v), 2) for v in nl[k]] for k in ('TL', 'TR', 'BR', 'BL')},
        'diem_khong_che': {'cot': ['E_m', 'N_m', 'px', 'py', 'du_pixel'],
                           'hang': [[int(e), int(n), round(float(x), 2), round(float(y), 2), round(float(r), 2)] for (e, n, x, y), r in zip(pts, res_px)]},
    }


def texture_rect(geos):
    """Hình chữ nhật WGS84 bao hai tờ (cắt ở TEX_WEST_LIMIT), kèm lề, theo vị trí thực địa."""
    lats, lons = [], []
    for g in geos:
        k = g['tai_lieu']['khung_to_indian1960']
        off = g['tai_lieu']['sai_lech_con_lai_dong_bac_m']
        for la, lo in ((k['north'], k['west']), (k['north'], k['east']), (k['south'], k['west']), (k['south'], k['east'])):
            a, b = ag.indian1960_to_wgs84(la, lo)
            da, db = ag._offset_deg(la, off)
            lats.append(float(a - da)); lons.append(float(b - db))
    pad = 0.0004
    return {'west': round(max(min(lons) - pad, TEX_WEST_LIMIT), 5), 'east': round(max(lons) + pad, 5),
            'south': round(min(lats) - pad, 5), 'north': round(max(lats) + pad, 5)}


def edge_alpha(shape, quad, shared):
    """Mặt nạ trong toạ độ ảnh gốc + vùng ảnh hợp lệ. 0 ngoài khung tờ, mép ngoài mờ dần.
    Mép chung với tờ kề: alpha dốc từ 0 đến 1 trên SEAM_EXTEND_PX tính từ SEAM_CUT_PX - SEAM_EXTEND_PX, nên mỗi tờ lấn sang
    dải đã cắt (điểm ảnh ở đó được nhân bản từ sát mép trong) và hai tờ hoà vào nhau, không để khe."""
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    names = ('top', 'right', 'bottom', 'left')   # TL->TR, TR->BR, BR->BL, BL->TL
    pts = [quad[k] for k in ('TL', 'TR', 'BR', 'BL')]
    alpha = np.ones((h, w), np.float32)
    valid = np.ones((h, w), bool)
    for i, name in enumerate(names):
        p, q = np.array(pts[i], np.float32), np.array(pts[(i + 1) % 4], np.float32)
        e = q - p
        d = (e[0] * (yy - p[1]) - e[1] * (xx - p[0])) / float(np.hypot(*e))
        if name == shared:
            a = np.clip((d - (SEAM_CUT_PX - SEAM_EXTEND_PX)) / SEAM_EXTEND_PX, 0, 1)
            valid &= d >= SEAM_CUT_PX
        else:
            a = np.clip((d - EDGE_CUT_PX) / FEATHER_PX, 0, 1)
            a = a * a * (3 - 2 * a)
        alpha = np.minimum(alpha, a)
    return alpha, valid


def fill_outside(img, valid):
    """Thay điểm ảnh ngoài vùng hợp lệ bằng điểm hợp lệ gần nhất (bỏ nét khung, giấy trắng và chữ mép)."""
    _, (iy, ix) = distance_transform_edt(~valid, return_indices=True)
    return img[iy, ix]


SEAM_STRIP_PX = 450  # dải sát mép chung dùng để so màu hai tờ (cùng cảnh quan ở hai bên mép)


def lab_stats(img, alpha, quad, side):
    """Trung bình, độ lệch chuẩn màu Lab trong dải SEAM_STRIP_PX sát mép chung (side: 'left' hay 'right')."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    xx = np.arange(img.shape[1], dtype=np.float32)[None, :]
    if side == 'left':
        x0 = min(quad['TL'][0], quad['BL'][0])
        band = (xx > x0) & (xx < x0 + SEAM_STRIP_PX)
    else:
        x1 = max(quad['TR'][0], quad['BR'][0])
        band = (xx < x1) & (xx > x1 - SEAM_STRIP_PX)
    sel = (alpha > 0.99) & band
    v = lab[sel]
    return v.mean(0), v.std(0)


def match_colour(img, own, ref):
    """Kéo màu tờ phía Tây (in mực xanh nhạt hơn) về tờ Điện Biên Phủ: chuẩn hoá trung bình, độ lệch chuẩn trong Lab theo dải sát mép."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    out = (lab - own[0]) / (own[1] + 1e-6) * ref[1] + ref[0]
    return cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)


def grid_size(rect, long_side):
    """Kích thước texture (rộng, cao) bội số của 16, điểm ảnh vuông theo Mercator; kéo cạnh Nam ra cho vừa số hàng.
    Trả (rect đã chỉnh, tw, th). Giả định khung rộng hơn cao."""
    x0, x1 = ag.merc_x(rect['west']), ag.merc_x(rect['east'])
    y0, y1 = ag.merc_y(rect['south']), ag.merc_y(rect['north'])
    tw = int(round(long_side / 16)) * 16
    pix = (x1 - x0) / tw
    th = int(np.ceil((y1 - y0) / pix / 16)) * 16
    south = round(float(ag.merc_inv_y(y1 - th * pix)), 5)
    return {**rect, 'south': south}, tw, th


def texture_maps(h_en2px, rect, tw, th, offset_m, step=16):
    """Bản đồ nắn cho cv2.remap: với điểm ảnh đích (i, j), toạ độ pixel nguồn tại TÂM điểm ảnh ((i + 0,5), (j + 0,5)).
    Tính trên lưới thô đặt đúng tâm ô thô, thêm một ô viền để nội suy không bị kẹp ở mép, rồi phóng bằng cv2.resize
    (cùng quy ước tâm điểm ảnh nên không lệch)."""
    x0, x1 = ag.merc_x(rect['west']), ag.merc_x(rect['east'])
    y0, y1 = ag.merc_y(rect['south']), ag.merc_y(rect['north'])
    gx = (np.arange(-1, tw // step + 1) + 0.5) * step
    gy = (np.arange(-1, th // step + 1) + 0.5) * step
    xx, yy = np.meshgrid(gx, gy)
    lon = ag.merc_inv_x(x0 + (xx / tw) * (x1 - x0))
    lat = ag.merc_inv_y(y1 - (yy / th) * (y1 - y0))
    px, py = ag.wgs84_to_pixel(h_en2px, lat, lon, offset_m=offset_m)
    size = (tw + 2 * step, th + 2 * step)
    out = []
    for m in (px, py):
        big = cv2.resize(m.astype(np.float32), size, interpolation=cv2.INTER_LINEAR)
        out.append(np.ascontiguousarray(big[step:step + th, step:step + tw]))
    return out


def warp(imgs, geos, specs, long_side=TEX_LONG_SIDE):
    rect, tw, th = grid_size(texture_rect(geos), long_side)
    masks = [edge_alpha(i.shape[:2], g['khung_to_px'], s['canh_chung']) for i, g, s in zip(imgs, geos, specs)]
    alphas = [m[0] for m in masks]
    imgs = [fill_outside(i, m[1]) for i, m in zip(imgs, masks)]
    ref = lab_stats(imgs[0], alphas[0], geos[0]['khung_to_px'], 'left')
    layers = []
    for k, (img, g, s, al) in enumerate(zip(imgs, geos, specs, alphas)):
        if k > 0:
            img = match_colour(img, lab_stats(img, al, g['khung_to_px'], 'right'), ref)
        mx, my = texture_maps(np.array(g['ma_tran_utm_sang_pixel']), rect, tw, th, s['lech_m'])
        rgb = cv2.remap(img, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
        a = cv2.remap(al, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        layers.append((rgb.astype(np.float32), np.clip(a, 0, 1)))
    wsum = sum(a for _, a in layers)
    tex = sum(c * a[..., None] for c, a in layers) / np.maximum(wsum, 1e-6)[..., None]
    mask = 1 - np.prod([1 - a for _, a in layers], axis=0)
    tex8 = np.clip(tex, 0, 255).astype(np.uint8)
    return tex8, (np.clip(mask, 0, 1) * 255).round().astype(np.uint8), rect, (tw, th)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--no-warp', action='store_true', help='chỉ ghi tệp nắn, không dựng ảnh nắn')
    ap.add_argument('--from-pdf-west', metavar='PDF', help='đổi PDF tờ 5551 I (Ban Thin Toc) thành data/ams-5551-1.jpg trước khi nắn')
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    if a.from_pdf_west:
        pdf_to_jpg(a.from_pdf_west, os.path.join(DATA, SHEETS[1]['file']))
    imgs, geos = [], []
    for s in SHEETS:
        img = cv2.imread(os.path.join(DATA, s['file']))
        if img is None:
            raise SystemExit(f"không đọc được {s['file']} (tờ phía Tây: chạy với --from-pdf-west, xem data/ams-nguon.md)")
        g = sheet_georef(s, img)
        imgs.append(img)
        geos.append(g)
        e = g['sai_so_du']
        print(f"tờ {s['id']}: điểm khống chế {g['so_diem_khong_che']}, RMS {e['rms_pixel']} px = {e['rms_met']} m (max {e['max_pixel']} px), affine {e['rms_pixel_neu_chi_affine']} px, {g['m_tren_pixel']} m/px")
        print('  góc khung lệch (px):', {c['goc']: c['lech_px'] for c in g['kiem_doc_lap_khung_to']}, 'đường yếu:', g['duong_luoi_yeu'] or 'không')
    out = {'phan_mem': {'python': sys.version.split()[0], 'numpy': np.__version__, 'opencv': cv2.__version__, 'scipy': scipy.__version__},
           'cac_to': geos}
    if a.no_warp:
        # giữ khung texture của lần dựng trước (loadAms đọc khoá này)
        if os.path.exists(OUT_JSON):
            with open(OUT_JSON, encoding='utf-8') as fh:
                old = json.load(fh)
            if 'texture' in old:
                out['texture'] = old['texture']
    else:
        tex, mask, rect, (tw, th) = warp(imgs, geos, SHEETS)
        cv2.imwrite(OUT_TEX, tex, [cv2.IMWRITE_JPEG_QUALITY, 90])
        cv2.imwrite(OUT_MASK, mask)
        out['texture'] = {'tep': os.path.basename(OUT_TEX), 'mat_na': os.path.basename(OUT_MASK), 'rong': tw, 'cao': th,
                          'luoi': 'cột tuyến tính theo kinh độ, hàng theo Mercator y (cùng hệ với mx, my trong map3d.js)', **rect,
                          'cac_to': [f"{s['id'].replace('-', ' ')} {s['ten']}" for s in SHEETS]}
    with open(OUT_JSON, 'w', encoding='utf-8', newline='') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write('\n')


if __name__ == '__main__':
    main()
