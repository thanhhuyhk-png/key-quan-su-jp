"""Test phép biến đổi toạ độ bản đồ AMS bằng điểm đã biết.

Chạy từ thư mục template/:  python -m pytest tools/test_ams_georef.py -q
Giá trị chuẩn tm_forward, dịch tâm lấy từ PROJ 9 (EPSG:3148 Indian 1960 / UTM 48N; helmert 198, 881, 317),
đã đối chiếu tới milimét khi viết hàm.
"""
import json
import os
import sys

import numpy as np
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ams_georef as ag  # noqa: E402
import ams_nan  # noqa: E402

GEOREF = os.path.join(HERE, '..', 'data', 'ams-5651-4.georef.json')


@pytest.mark.parametrize('lat,lon,e,n', [
    (21.5, 103.0, 292840.242, 2378616.418),    # góc Tây Bắc khung tờ 5651 IV
    (21.25, 103.25, 318433.370, 2350629.167),  # góc Đông Nam
    (21.4, 103.1, 303066.790, 2367415.768),
])
def test_tm_forward_khop_proj_everest(lat, lon, e, n):
    ee, nn = ag.tm_forward(lat, lon)
    assert ee == pytest.approx(e, abs=0.005)
    assert nn == pytest.approx(n, abs=0.005)


def test_tm_forward_kinh_tuyen_giua_cho_E_500000():
    e, _ = ag.tm_forward(21.0, 105.0)
    assert e == pytest.approx(500000.0, abs=1e-6)


def test_tm_nguoc_la_nghich_dao_cua_tm_xuoi():
    lat = np.array([21.25, 21.39, 21.5])
    lon = np.array([103.0, 103.1, 103.25])
    la, lo = ag.tm_inverse(*ag.tm_forward(lat, lon))
    assert np.allclose(la, lat, atol=1e-9) and np.allclose(lo, lon, atol=1e-9)


def test_dich_tam_indian1960_sang_wgs84_khop_proj():
    lat, lon = ag.indian1960_to_wgs84(21.4, 103.1)
    assert lat == pytest.approx(21.40111060814, abs=1e-9)
    assert lon == pytest.approx(103.09621444267, abs=1e-9)


def test_dich_tam_khoang_400_met_ve_tay():
    lat0, lon0 = 21.4, 103.1
    lat, lon = ag.indian1960_to_wgs84(lat0, lon0)
    east_m = (lon - lon0) * np.pi / 180 * 6378137 * np.cos(np.radians(lat0))
    assert -420 < east_m < -370


def test_dich_tam_khu_hoi():
    lat, lon = ag.indian1960_to_wgs84(21.4, 103.1)
    la, lo = ag.wgs84_to_indian1960(lat, lon)
    assert float(la) == pytest.approx(21.4, abs=1e-7)
    assert float(lo) == pytest.approx(103.1, abs=1e-7)


def test_mercator_web_khu_hoi():
    assert float(ag.merc_inv_y(ag.merc_y(21.39))) == pytest.approx(21.39, abs=1e-9)
    assert float(ag.merc_inv_x(ag.merc_x(103.01))) == pytest.approx(103.01, abs=1e-9)


def test_homography_khoi_phuc_phep_bien_doi_da_biet():
    h_true = np.array([[1.2, 0.1, 30.0], [-0.05, 0.9, -12.0], [1e-5, -2e-5, 1.0]])
    src = np.array([[0, 0], [100, 0], [0, 100], [100, 100], [50, 20], [10, 80], [70, 60], [90, 30]], float)
    dst = ag.apply_homography(h_true, src)
    h = ag.fit_homography(src, dst)
    assert np.allclose(ag.apply_homography(h, src), dst, atol=1e-6)
    assert np.allclose(ag.apply_homography(h, [[33.0, 44.0]]), ag.apply_homography(h_true, [[33.0, 44.0]]), atol=1e-6)


def test_affine_khop_phep_tinh_tien_va_xoay():
    th = np.radians(0.85)
    a = np.array([[np.cos(th), -np.sin(th), 5.0], [np.sin(th), np.cos(th), -7.0]])
    src = np.array([[0, 0], [10, 0], [0, 10], [10, 10], [3, 7]], float)
    dst = src @ a[:, :2].T + a[:, 2]
    assert np.allclose(ag.apply_homography(ag.fit_affine(src, dst), src), dst, atol=1e-9)


def test_lech_con_lai_dich_diem_ve_dong_dung_so_met():
    lat, lon = 21.39, 103.02
    la, lo = ag._offset_deg(lat, (58.0, 0.0))
    assert float(la) == 0.0
    assert float(lo) * np.pi / 180 * 6378137 * np.cos(np.radians(lat)) == pytest.approx(58.0, abs=1e-6)


@pytest.fixture(scope='module')
def tong():
    with open(GEOREF, encoding='utf-8') as fh:
        return json.load(fh)


@pytest.fixture(scope='module', params=[0, 1], ids=['5651-4', '5551-1'])
def geo(request, tong):
    return tong['cac_to'][request.param]


@pytest.mark.skipif(not os.path.exists(GEOREF), reason='chưa chạy nan-ban-do-ams.py')
class TestTepNan:
    def test_du_diem_khong_che_va_sai_so_nho(self, geo):
        assert geo['so_diem_khong_che'] >= 8
        assert geo['sai_so_du']['rms_pixel'] < 1.0
        assert geo['sai_so_du']['rms_met'] < 12

    def test_diem_luoi_ve_dung_pixel_da_do(self, geo):
        h = np.array(geo['ma_tran_utm_sang_pixel'])
        for e, n, px, py, _ in geo['diem_khong_che']['hang'][::53]:
            q = ag.apply_homography(h, [[e, n]])[0]
            assert np.hypot(q[0] - px, q[1] - py) < 1.5

    def test_khung_to_doc_lap_lech_duoi_2_pixel_ruoi(self, geo):
        assert all(c['lech_px'] < 2.5 for c in geo['kiem_doc_lap_khung_to'])

    def test_pixel_va_wgs84_khu_hoi(self, geo):
        h_en2px = np.array(geo['ma_tran_utm_sang_pixel'])
        h_px2en = np.array(geo['ma_tran_pixel_sang_utm'])
        off = tuple(geo['tai_lieu']['sai_lech_con_lai_dong_bac_m'])
        pts = np.array([[500.0, 700.0], [1200.0, 1500.0], [2000.0, 2300.0]])
        lat, lon = ag.pixel_to_wgs84(h_px2en, pts, offset_m=off)
        px, py = ag.wgs84_to_pixel(h_en2px, lat, lon, offset_m=off)
        assert np.allclose(np.c_[px, py], pts, atol=0.01)

    def test_hai_to_ke_nhau_o_kinh_tuyen_103(self, tong):
        tay, dong = tong['cac_to'][1]['tai_lieu']['khung_to_indian1960'], tong['cac_to'][0]['tai_lieu']['khung_to_indian1960']
        assert tay['east'] == dong['west'] == 103.0
        assert tay['south'] == dong['south'] and tay['north'] == dong['north']

    def test_khung_phu_chua_long_chao_va_phia_tay(self, tong):
        t = tong['texture']
        assert t['west'] <= 102.92 and t['east'] > 103.2
        assert t['south'] < 21.335 and t['north'] > 21.42   # Hồng Cúm đến Độc Lập
        assert max(t['rong'], t['cao']) <= 4096


# ---------- chuỗi pixel -> WGS84 và dựng texture ----------
def test_pixel_sang_wgs84_khop_proj_khong_tron_vong():
    """Cho pixel = (E, N) bằng phép đồng nhất nên kết quả phải là chuỗi UTM Everest -> Indian 1960 -> WGS84 của PROJ."""
    ident = np.eye(3)
    lat, lon = ag.pixel_to_wgs84(ident, [[300000.0, 2365000.0], [310500.0, 2360250.0]])
    assert lat[0] == pytest.approx(21.378957670540334, abs=1e-8)
    assert lon[0] == pytest.approx(103.06692964708691, abs=1e-8)
    assert lat[1] == pytest.approx(21.337198363746616, abs=1e-8)
    assert lon[1] == pytest.approx(103.16869654254438, abs=1e-8)


def _to_vuong_nho():
    """Một tờ giả: khung 103.00-103.01E, 21.40-21.41N, ảnh 400x400 pixel, lưới biết trước, nội dung là một chấm đen."""
    khung = {'west': 103.0, 'east': 103.01, 'south': 21.40, 'north': 21.41}
    corners = ams_nan.corners_en(khung)
    px = {'TL': (10.0, 10.0), 'TR': (390.0, 10.0), 'BR': (390.0, 390.0), 'BL': (10.0, 390.0)}
    order = ('TL', 'TR', 'BR', 'BL')
    h_en2px = ag.fit_homography([corners[k] for k in order], [px[k] for k in order])
    geo = {'tai_lieu': {'khung_to_indian1960': khung, 'sai_lech_con_lai_dong_bac_m': [0.0, 0.0]},
           'ma_tran_utm_sang_pixel': h_en2px.tolist(), 'ma_tran_pixel_sang_utm': np.linalg.inv(h_en2px).tolist(),
           'khung_to_px': {k: list(v) for k, v in px.items()}}
    spec = {'lech_m': (0.0, 0.0), 'canh_chung': 'none'}
    return geo, spec, h_en2px


def test_texture_maps_dung_tai_tam_diem_anh_dich():
    geo, spec, h = _to_vuong_nho()
    rect = {'west': 103.0, 'east': 103.01, 'south': 21.40, 'north': 21.41}
    rect, tw, th = ams_nan.grid_size(rect, 512)
    mx, my = ams_nan.texture_maps(h, rect, tw, th, (58.0, 0.0))
    x0, x1 = ag.merc_x(rect['west']), ag.merc_x(rect['east'])
    y0, y1 = ag.merc_y(rect['south']), ag.merc_y(rect['north'])
    worst = 0.0
    for j in range(0, th, 37):
        for i in range(0, tw, 41):
            lon = ag.merc_inv_x(x0 + (i + 0.5) / tw * (x1 - x0))
            lat = ag.merc_inv_y(y1 - (j + 0.5) / th * (y1 - y0))
            px, py = ag.wgs84_to_pixel(h, lat, lon, offset_m=(58.0, 0.0))
            worst = max(worst, abs(float(px) - mx[j, i]), abs(float(py) - my[j, i]))
    assert worst < 0.05   # pixel nguồn


def test_warp_dat_cham_dung_cho_duoi_nua_pixel():
    geo, spec, h = _to_vuong_nho()
    img = np.full((400, 400, 3), 255, np.uint8)
    cx, cy = 200, 150
    yy, xx = np.mgrid[0:400, 0:400]
    img[(xx - cx) ** 2 + (yy - cy) ** 2 <= 9] = 0
    tex, mask, rect, (tw, th) = ams_nan.warp([img], [geo], [spec], long_side=512)
    # vị trí thực địa của chấm, rồi pixel texture mong đợi (chỉ số, tâm điểm ảnh = i + 0,5)
    lat, lon = ag.pixel_to_wgs84(np.array(geo['ma_tran_pixel_sang_utm']), [[cx, cy]])
    x0, x1 = ag.merc_x(rect['west']), ag.merc_x(rect['east'])
    y0, y1 = ag.merc_y(rect['south']), ag.merc_y(rect['north'])
    ex = (float(ag.merc_x(lon[0])) - x0) / (x1 - x0) * tw - 0.5
    ey = (y1 - float(ag.merc_y(lat[0]))) / (y1 - y0) * th - 0.5
    dark = (255 - tex.astype(np.float32).mean(axis=2))
    ys, xs = np.nonzero((dark > 60) & (mask > 200))
    w = dark[ys, xs]
    gx, gy = (xs * w).sum() / w.sum(), (ys * w).sum() / w.sum()
    assert abs(gx - ex) < 0.5 and abs(gy - ey) < 0.5
    assert mask[int(round(ey)), int(round(ex))] == 255


def test_grid_size_boi_so_16_va_diem_anh_vuong():
    rect, tw, th = ams_nan.grid_size({'west': 102.9, 'east': 103.246, 'south': 21.2507, 'north': 21.5015}, 4096)
    assert tw % 16 == 0 and th % 16 == 0 and tw == 4096
    px_x = (ag.merc_x(rect['east']) - ag.merc_x(rect['west'])) / tw
    px_y = (ag.merc_y(rect['north']) - ag.merc_y(rect['south'])) / th
    assert px_y == pytest.approx(px_x, rel=2e-4)
