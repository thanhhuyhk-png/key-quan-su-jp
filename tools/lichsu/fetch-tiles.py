"""Tải và ghép ô bản đồ cho một vùng: địa hình (AWS Terrarium, công cộng) và ảnh vệ tinh Sentinel-2 cloudless 2016 (EOX, CC BY 4.0).

Dùng: python fetch-tiles.py <thư mục ra> --bbox lat_min lon_min lat_max lon_max --zoom 13 [--layers dem,s2]
Ra: dem_z{z}.png (độ cao mét, uint16 + offset ghi trong meta), dem_z{z}.npy, s2_z{z}.jpg, meta_z{z}.json (bbox Web Mercator chính xác của ảnh ghép).
"""
import argparse, io, json, math, os, time, urllib.request
import numpy as np
from PIL import Image

URL = {"dem": "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
       "s2": "https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg"}


def deg2tile(lat: float, lon: float, z: int) -> tuple[float, float]:
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def tile2deg(x: float, y: float, z: int) -> tuple[float, float]:
    n = 2 ** z
    lon = x / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lat, lon


def get(url: str) -> bytes:
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Goha-LichSu/1.0"})
            return urllib.request.urlopen(req, timeout=30).read()
        except Exception as e:  # mạng chập chờn: thử lại có giãn cách
            if i == 3:
                raise RuntimeError(f"tải lỗi {url}: {e}")
            time.sleep(2 * (i + 1))
    return b""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--bbox", type=float, nargs=4, required=True)
    ap.add_argument("--zoom", type=int, default=13); ap.add_argument("--layers", default="dem,s2")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    la0, lo0, la1, lo1 = a.bbox; z = a.zoom
    x0, y1 = deg2tile(la0, lo0, z); x1, y0 = deg2tile(la1, lo1, z)
    tx = range(int(x0), int(x1) + 1); ty = range(int(y0), int(y1) + 1)
    for layer in a.layers.split(","):
        size = 256 if layer == "dem" else 256
        canvas = Image.new("RGB", (len(tx) * size, len(ty) * size))
        for i, x in enumerate(tx):
            for j, y in enumerate(ty):
                im = Image.open(io.BytesIO(get(URL[layer].format(z=z, x=x, y=y)))).convert("RGB")
                canvas.paste(im.resize((size, size)), (i * size, j * size))
        if layer == "dem":
            arr = np.asarray(canvas).astype(np.float32)
            h = arr[..., 0] * 256 + arr[..., 1] + arr[..., 2] / 256 - 32768
            np.save(os.path.join(a.out, f"dem_z{z}.npy"), h.astype(np.float32))
            print("dem", h.shape, "min", float(h.min()), "max", float(h.max()))
        else:
            canvas.save(os.path.join(a.out, f"s2_z{z}.jpg"), quality=92)
            print("s2", canvas.size)
    north, west = tile2deg(tx[0], ty[0], z); south, east = tile2deg(tx[-1] + 1, ty[-1] + 1, z)
    json.dump({"zoom": z, "north": north, "south": south, "west": west, "east": east,
               "tiles_x": [tx[0], tx[-1]], "tiles_y": [ty[0], ty[-1]],
               "credit": "Địa hình: AWS Terrain Tiles (Mapzen/SRTM, công cộng); Ảnh vệ tinh: Sentinel-2 cloudless 2016 (EOX IT Services, CC BY 4.0; Contains modified Copernicus Sentinel data 2016)"},
              open(os.path.join(a.out, f"meta_z{z}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
