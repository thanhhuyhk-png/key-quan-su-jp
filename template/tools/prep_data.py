"""Chuẩn bị dữ liệu cho các khối: DEM + ảnh vệ tinh (map3d), biên giới (vnmap), ảnh AMS (archival).

Chạy một lần:  python tools/prep_data.py --map-dir <...>/assets/map --ne-dir <thư mục Natural Earth geojson>
Ghi vào template/data/.
"""
import argparse, json, math, os, shutil
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')

# Hộp quần đảo Hoàng Sa, Trường Sa (độ). Mọi mảnh đất của nước khác trong hộp bị loại; đảo trong hộp tô màu Việt Nam.
PARACEL = (110.5, 15.3, 113.5, 17.5)
SPRATLY = (111.0, 6.5, 116.3, 12.0)
BBOX = (88.0, -3.0, 128.0, 30.0)


def in_box(x, y, b):
    return b[0] <= x <= b[2] and b[1] <= y <= b[3]


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = np.array(pts[0]), np.array(pts[-1])
    ab = b - a
    n = np.hypot(*ab)
    p = np.array(pts)
    if n == 0:
        d = np.hypot(*(p - a).T)
    else:
        d = np.abs(ab[0] * (p[:, 1] - a[1]) - ab[1] * (p[:, 0] - a[0])) / n
    i = int(np.argmax(d))
    if d[i] > eps:
        return rdp(pts[: i + 1], eps)[:-1] + rdp(pts[i:], eps)
    return [pts[0], pts[-1]]


def polys(g):
    return g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]


def prep_dem(src, name, step):
    meta = json.load(open(os.path.join(src, f'meta_{name}.json'), encoding='utf-8'))
    dem = np.load(os.path.join(src, f'dem_{name}.npy'))
    dem = np.clip(dem, 0, None)
    h, w = dem.shape
    # Trung bình khối step x step để giảm lưới
    dem = dem[: h - h % step, : w - w % step].reshape(h // step, step, w // step, step).mean(axis=(1, 3)).astype('<f4')
    out = 'valley' if name == 'z13' else 'region'
    dem.tofile(os.path.join(DATA, f'{out}_dem.bin'))
    meta.update({'rows': dem.shape[0], 'cols': dem.shape[1]})
    json.dump(meta, open(os.path.join(DATA, f'{out}_meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    im = Image.open(os.path.join(src, f's2_{name}.jpg')).convert('RGB')
    im.save(os.path.join(DATA, f'{out}_s2.jpg'), quality=92)
    print(out, dem.shape, im.size)


def prep_borders(ne):
    d = json.load(open(os.path.join(ne, 'ne_10m_admin_0_countries.geojson'), encoding='utf-8'))
    out = {'vn': [], 'islands': {'hoang_sa': [], 'truong_sa': []}, 'other': []}
    for f in d['features']:
        name = f['properties']['ADMIN']
        for poly in polys(f['geometry']):
            ring = poly[0]
            cx = sum(c[0] for c in ring) / len(ring)
            cy = sum(c[1] for c in ring) / len(ring)
            if not in_box(cx, cy, BBOX):
                continue
            if in_box(cx, cy, PARACEL) or in_box(cx, cy, SPRATLY):
                # Đảo trong hai quần đảo: thuộc Việt Nam (dữ liệu nguồn gán nước khác thì gán lại)
                key = 'hoang_sa' if in_box(cx, cy, PARACEL) else 'truong_sa'
                out['islands'][key].append([[round(x, 4), round(y, 4)] for x, y in ring])
                continue
            simp = rdp([tuple(c) for c in ring], 0.012)
            if len(simp) < 4:
                continue
            simp = [[round(x, 3), round(y, 3)] for x, y in simp]
            if name == 'Vietnam':
                out['vn'].append(simp)
            else:
                out['other'].append({'n': name, 'r': simp})
    m = json.load(open(os.path.join(ne, 'ne_10m_minor_islands.geojson'), encoding='utf-8'))
    for f in m['features']:
        for poly in polys(f['geometry']):
            ring = poly[0]
            cx = sum(c[0] for c in ring) / len(ring)
            cy = sum(c[1] for c in ring) / len(ring)
            for key, box in (('hoang_sa', PARACEL), ('truong_sa', SPRATLY)):
                if in_box(cx, cy, box):
                    out['islands'][key].append([[round(x, 4), round(y, 4)] for x, y in ring])
    with open(os.path.join(DATA, 'borders.js'), 'w', encoding='utf-8') as fh:
        fh.write('// Natural Earth 10m (phạm vi công cộng), đã giản lược. Hoàng Sa, Trường Sa gán Việt Nam.\n')
        fh.write('export const BORDERS = ' + json.dumps(out, separators=(',', ':')) + ';\n')
    print('borders vn', len(out['vn']), 'other', len(out['other']), 'HS', len(out['islands']['hoang_sa']), 'TS', len(out['islands']['truong_sa']))


def prep_ams(src):
    Image.MAX_IMAGE_PIXELS = None
    im = Image.open(os.path.join(src, 'ams-5651-4.png')).convert('RGB')
    im.thumbnail((3200, 3200))
    im.save(os.path.join(DATA, 'ams-5651-4.jpg'), quality=88)
    print('ams', im.size)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--map-dir', required=True)
    ap.add_argument('--ne-dir', required=True)
    a = ap.parse_args()
    os.makedirs(DATA, exist_ok=True)
    prep_dem(os.path.join(a.map_dir, 'valley'), 'z13', 4)
    prep_dem(os.path.join(a.map_dir, 'region'), 'z10', 4)
    prep_borders(a.ne_dir)
    prep_ams(a.map_dir)
