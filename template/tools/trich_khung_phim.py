"""Trích khung hình từ phim tư liệu (tệp video) thành chuỗi JPG để thẻ phim-panel phát lại theo t.

  python -I -X utf8 tools/trich_khung_phim.py <video> --tu 12.5 --dai 4 --fps 12 --rong 1104 --out-dir <thư mục>/phim-xxx

Vì sao trích trước: hợp đồng render của máy dựng (kit/dung-trang.mjs) bắt renderFrame(t) thuần theo t và chụp từng khung độc lập, nên
thẻ không dùng thẻ <video> (không tua đúng khung được). Mỗi khung là một JPG; thẻ chọn khung theo (t - batDau) × fps.
Quy định: trích 3–5 s (tư liệu hạng B), tối đa 150 khung; phim tắt tiếng (script chỉ lấy hình). Ghi nguồn trong `source` của shot.
Cuối cùng in đoạn `phim: {...}` dán vào shot.
"""
import argparse
import importlib.util
import os
import subprocess
import sys

TOI_DA_KHUNG = 150
_spec = importlib.util.spec_from_file_location('luat_cung', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'luat_cung.py'))
luat_cung = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(luat_cung)   # dùng chung trần RAM với máy chặn


def lenh_ffmpeg(video, tu, dai, fps, rong, mau):
    """Lệnh ffmpeg trích khung: tua nhanh (-ss trước -i), scale giữ tỉ lệ, rộng chẵn, JPG chất lượng 4."""
    return ['ffmpeg', '-y', '-v', 'error', '-ss', str(tu), '-t', str(dai), '-i', video, '-an',
            '-vf', f'fps={fps},scale={rong}:-2:flags=lanczos', '-q:v', '4', mau]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('--tu', type=float, default=0.0, help='giây bắt đầu trong phim')
    ap.add_argument('--dai', type=float, required=True, help='số giây trích (3–5 s với tư liệu hạng B)')
    ap.add_argument('--fps', type=float, default=12.0)
    ap.add_argument('--rong', type=int, default=1104, help='bề rộng khung (mặc định đúng cửa sổ phim của thẻ)')
    ap.add_argument('--out-dir', required=True)
    a = ap.parse_args()
    n_du_kien = int(round(a.dai * a.fps))
    if not (0 < n_du_kien <= TOI_DA_KHUNG):
        raise SystemExit(f'LỖI: {n_du_kien} khung (tối đa {TOI_DA_KHUNG}): giảm --dai hoặc --fps')
    if not os.path.isfile(a.video):
        raise SystemExit(f'LỖI: không thấy video {a.video}')
    # trần RAM: thẻ nạp mọi khung vào bộ nhớ (rộng × cao × 4 byte mỗi khung); ước theo 16:9, đo lại theo khung thật sau khi trích
    uoc = luat_cung.uoc_ram(n_du_kien, a.rong, round(a.rong * 9 / 16))
    if uoc > luat_cung.TRAN_RAM_BYTE:
        raise SystemExit(f'CẢNH BÁO, dừng: {n_du_kien} khung rộng {a.rong} cần ≈ {uoc // 1048576} MB sau giải mã, vượt trần {luat_cung.TRAN_RAM_BYTE // 1048576} MB: giảm --rong, --fps hoặc --dai')
    os.makedirs(a.out_dir, exist_ok=True)
    for f in os.listdir(a.out_dir):
        if f.startswith('f') and f.endswith('.jpg'):
            os.remove(os.path.join(a.out_dir, f))
    r = subprocess.run(lenh_ffmpeg(a.video, a.tu, a.dai, a.fps, a.rong, os.path.join(a.out_dir, 'f%03d.jpg')), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode:
        raise SystemExit('LỖI ffmpeg:\n' + r.stdout.decode('utf-8', 'replace')[-500:])
    n = len([f for f in os.listdir(a.out_dir) if f.startswith('f') and f.endswith('.jpg')])
    if n == 0:
        raise SystemExit('LỖI: không trích được khung nào (--tu vượt độ dài phim?)')
    try:
        w, h = luat_cung.kich_thuoc(os.path.join(a.out_dir, 'f001.jpg'))
        if luat_cung.uoc_ram(n, w, h) > luat_cung.TRAN_RAM_BYTE:
            raise SystemExit(f'CẢNH BÁO: khung thật {w}×{h} × {n} khung ≈ {luat_cung.uoc_ram(n, w, h) // 1048576} MB, vượt trần {luat_cung.TRAN_RAM_BYTE // 1048576} MB: trích lại với --rong nhỏ hơn')
    except luat_cung.LoiNode as e:
        print(f'CẢNH BÁO: không đo được kích thước khung thật ({e})', file=sys.stderr)
    rel = a.out_dir.replace('\\', '/')
    print(f"{n} khung. Dán vào shot (đường dẫn tính từ trang cards/):\n  phim: {{ mau: '{rel}/f%03d.jpg', n: {n}, fps: {a.fps:g}, batDau: 0.3 }},")


if __name__ == '__main__':
    sys.exit(main())
