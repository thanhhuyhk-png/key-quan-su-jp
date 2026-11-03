"""Biến đổi toạ độ cho bản đồ AMS (tờ 5651 IV, Điện Biên Phủ, 1:50.000, series L7014).

Hàm thuần, chỉ dùng numpy (nhận số hoặc mảng), không đọc tệp, không ngẫu nhiên. Chuỗi biến đổi:

  pixel ảnh  --(đồng dạng chiếu H)-->  UTM vùng 48 trên Everest (E, N, mét)
             --(Mercator ngang ngược)-->  vĩ độ, kinh độ trên hệ Indian 1960
             --(dịch tâm 3 tham số)-->  vĩ độ, kinh độ WGS84
             --(Mercator web)-->  toạ độ lưới địa hình map3d

Dữ kiện ghi ở mép tờ (đọc trên ảnh):
  Spheroid Everest, Grid 1.000 m UTM zone 48, Projection Transverse Mercator,
  Horizontal datum Indian Datum 1960, góc tờ 103°00'-103°15' E, 21°15'-21°30' N.
Elip Everest dùng cho Indian 1960 ở Việt Nam: a = 6377276.345, 1/f = 300.8017 (EPSG:7015).
Dịch tâm Indian 1960 -> WGS84 (Việt Nam đại lục): dX = 198, dY = 881, dZ = 317 m (NIMA TR8350.2, EPSG:4131).
"""
import numpy as np

WGS84 = (6378137.0, 298.257223563)
EVEREST_1937 = (6377276.345, 300.8017)
INDIAN1960_TO_WGS84 = (198.0, 881.0, 317.0)
UTM48 = {'lon0': 105.0, 'k0': 0.9996, 'fe': 500000.0, 'fn': 0.0}
R_MERC = 6378137.0


def _flat(ell):
    a, rf = ell
    return a, 1.0 / rf


# ---------- Mercator ngang (chuỗi Krüger bậc 4, sai số dưới 1 mm trong vùng UTM) ----------
def _series(n):
    a1 = n / 2 - 2 * n**2 / 3 + 5 * n**3 / 16 + 41 * n**4 / 180
    a2 = 13 * n**2 / 48 - 3 * n**3 / 5 + 557 * n**4 / 1440
    a3 = 61 * n**3 / 240 - 103 * n**4 / 140
    a4 = 49561 * n**4 / 161280
    b1 = n / 2 - 2 * n**2 / 3 + 37 * n**3 / 96 - n**4 / 360
    b2 = n**2 / 48 + n**3 / 15 - 437 * n**4 / 1440
    b3 = 17 * n**3 / 480 - 37 * n**4 / 840
    b4 = 4397 * n**4 / 161280
    return (a1, a2, a3, a4), (b1, b2, b3, b4)


def _consts(ell):
    a, f = _flat(ell)
    n = f / (2 - f)
    big_a = a / (1 + n) * (1 + n**2 / 4 + n**4 / 64)
    e = np.sqrt(f * (2 - f))
    return n, big_a, e, *_series(n)


def tm_forward(lat, lon, ell=EVEREST_1937, lon0=UTM48['lon0'], k0=UTM48['k0'], fe=UTM48['fe'], fn=UTM48['fn']):
    """(vĩ độ, kinh độ) độ -> (E, N) mét."""
    n, big_a, e, alpha, _ = _consts(ell)
    phi, dl = np.radians(lat), np.radians(np.asarray(lon, dtype=float) - lon0)
    t = np.sinh(np.arctanh(np.sin(phi)) - e * np.arctanh(e * np.sin(phi)))
    xi_p = np.arctan2(t, np.cos(dl))
    eta_p = np.arctanh(np.sin(dl) / np.sqrt(1 + t * t))
    xi, eta = xi_p, eta_p
    for j, aj in enumerate(alpha, start=1):
        xi = xi + aj * np.sin(2 * j * xi_p) * np.cosh(2 * j * eta_p)
        eta = eta + aj * np.cos(2 * j * xi_p) * np.sinh(2 * j * eta_p)
    return fe + k0 * big_a * eta, fn + k0 * big_a * xi


def tm_inverse(easting, northing, ell=EVEREST_1937, lon0=UTM48['lon0'], k0=UTM48['k0'], fe=UTM48['fe'], fn=UTM48['fn']):
    """(E, N) mét -> (vĩ độ, kinh độ) độ."""
    n, big_a, e, _, beta = _consts(ell)
    xi = (np.asarray(northing, dtype=float) - fn) / (k0 * big_a)
    eta = (np.asarray(easting, dtype=float) - fe) / (k0 * big_a)
    xi_p, eta_p = xi, eta
    for j, bj in enumerate(beta, start=1):
        xi_p = xi_p - bj * np.sin(2 * j * xi) * np.cosh(2 * j * eta)
        eta_p = eta_p - bj * np.cos(2 * j * xi) * np.sinh(2 * j * eta)
    chi = np.arcsin(np.sin(xi_p) / np.cosh(eta_p))
    # vĩ độ từ vĩ độ conformal: lặp điểm bất động (hội tụ rất nhanh)
    phi = chi
    for _ in range(6):
        phi = np.arcsin(np.tanh(np.arctanh(np.sin(chi)) + e * np.arctanh(e * np.sin(phi))))
    lon = lon0 + np.degrees(np.arctan2(np.sinh(eta_p), np.cos(xi_p)))
    return np.degrees(phi), lon


# ---------- đổi hệ toạ độ trắc địa (dịch tâm 3 tham số) ----------
def geodetic_to_ecef(lat, lon, h, ell):
    a, f = _flat(ell)
    e2 = f * (2 - f)
    phi, lam = np.radians(lat), np.radians(lon)
    nu = a / np.sqrt(1 - e2 * np.sin(phi) ** 2)
    return ((nu + h) * np.cos(phi) * np.cos(lam), (nu + h) * np.cos(phi) * np.sin(lam), (nu * (1 - e2) + h) * np.sin(phi))


def ecef_to_geodetic(x, y, z, ell):
    a, f = _flat(ell)
    e2 = f * (2 - f)
    lam = np.arctan2(y, x)
    p = np.hypot(x, y)
    phi = np.arctan2(z, p * (1 - e2))
    for _ in range(8):
        nu = a / np.sqrt(1 - e2 * np.sin(phi) ** 2)
        h = p / np.cos(phi) - nu
        phi = np.arctan2(z, p * (1 - e2 * nu / (nu + h)))
    return np.degrees(phi), np.degrees(lam)


def indian1960_to_wgs84(lat, lon, h=0.0, shift=INDIAN1960_TO_WGS84):
    x, y, z = geodetic_to_ecef(lat, lon, h, EVEREST_1937)
    return ecef_to_geodetic(x + shift[0], y + shift[1], z + shift[2], WGS84)


def wgs84_to_indian1960(lat, lon, h=0.0, shift=INDIAN1960_TO_WGS84):
    x, y, z = geodetic_to_ecef(lat, lon, h, WGS84)
    return ecef_to_geodetic(x - shift[0], y - shift[1], z - shift[2], EVEREST_1937)


# ---------- Mercator web (cùng hệ với map3d.js: mx, my) ----------
def merc_x(lon):
    return R_MERC * np.radians(lon)


def merc_y(lat):
    return R_MERC * np.log(np.tan(np.pi / 4 + np.radians(lat) / 2))


def merc_inv_y(y):
    return np.degrees(2 * np.arctan(np.exp(np.asarray(y, dtype=float) / R_MERC)) - np.pi / 2)


def merc_inv_x(x):
    return np.degrees(np.asarray(x, dtype=float) / R_MERC)


# ---------- phép chiếu H giữa hai mặt phẳng ----------
def fit_homography(src, dst):
    """Khớp H (3x3) sao cho dst ~ H(src) bằng DLT chuẩn hoá. src, dst: mảng (n, 2), n >= 4."""
    src, dst = np.asarray(src, float), np.asarray(dst, float)

    def norm(p):
        c = p.mean(axis=0)
        s = np.sqrt(2) / np.mean(np.hypot(*(p - c).T))
        return np.array([[s, 0, -s * c[0]], [0, s, -s * c[1]], [0, 0, 1]])

    ts, td = norm(src), norm(dst)
    ps = (ts @ np.c_[src, np.ones(len(src))].T).T
    pd = (td @ np.c_[dst, np.ones(len(dst))].T).T
    rows = []
    for (x, y, _), (u, v, _) in zip(ps, pd):
        rows.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u])
        rows.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])
    h = np.linalg.svd(np.array(rows))[2][-1].reshape(3, 3)
    h = np.linalg.inv(td) @ h @ ts
    return h / h[2, 2]


def apply_homography(h, pts):
    pts = np.asarray(pts, float)
    q = np.c_[pts, np.ones(len(pts))] @ np.asarray(h).T
    return q[:, :2] / q[:, 2:3]


def fit_affine(src, dst):
    """Khớp affine 2x3 bằng bình phương tối thiểu, trả ma trận 3x3 (dòng cuối 0 0 1)."""
    src, dst = np.asarray(src, float), np.asarray(dst, float)
    a = np.c_[src, np.ones(len(src))]
    sol = np.linalg.lstsq(a, dst, rcond=None)[0]
    return np.vstack([sol.T, [0, 0, 1]])


# ---------- chuỗi hoàn chỉnh ----------
def _offset_deg(lat, offset_m):
    """Đổi vectơ lệch (Đông, Bắc) mét sang độ kinh, độ vĩ tại vĩ độ lat (xấp xỉ cầu, đủ cho vài trăm mét)."""
    de, dn = offset_m
    return np.degrees(dn / R_MERC) + 0.0 * np.asarray(lat, float), np.degrees(de / (R_MERC * np.cos(np.radians(lat))))


def pixel_to_wgs84(h_pix_to_utm, px, shift=INDIAN1960_TO_WGS84, offset_m=(0.0, 0.0)):
    """Toạ độ pixel (n, 2) -> (lat, lon) WGS84 (hai mảng).
    offset_m = (Đông, Bắc) mét: sai lệch còn lại của bản đồ so với thực địa (AMS - thực địa), trừ đi ở đây."""
    en = apply_homography(h_pix_to_utm, px)
    lat_i, lon_i = tm_inverse(en[:, 0], en[:, 1])
    lat, lon = indian1960_to_wgs84(lat_i, lon_i, 0.0, shift)
    dlat, dlon = _offset_deg(lat, offset_m)
    return lat - dlat, lon - dlon


def wgs84_to_pixel(h_utm_to_pix, lat, lon, shift=INDIAN1960_TO_WGS84, offset_m=(0.0, 0.0)):
    """(lat, lon) WGS84 thực địa -> pixel ảnh AMS. Nhận số hoặc mảng cùng kích thước.
    Điểm thực địa nằm ở chỗ lệch offset_m trên bản đồ nên lấy mẫu tại (thực địa + offset)."""
    lat, lon = np.asarray(lat, float), np.asarray(lon, float)
    dlat, dlon = _offset_deg(lat, offset_m)
    lat_i, lon_i = wgs84_to_indian1960(lat + dlat, lon + dlon, 0.0, shift)
    e, n = tm_forward(lat_i, lon_i)
    pts = np.c_[np.ravel(e), np.ravel(n)]
    out = apply_homography(h_utm_to_pix, pts)
    return out[:, 0].reshape(np.shape(e)), out[:, 1].reshape(np.shape(e))
