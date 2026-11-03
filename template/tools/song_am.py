"""Tính trước sóng âm (peaks) từ tệp giọng THẬT để thẻ the-am-thanh vẽ; trình duyệt không giải mã âm.

  python -I -X utf8 tools/song_am.py <tệp âm thanh> --out <peaks.json> [--fps 50]

Giải mã bằng ffmpeg ra mono 16 kHz, chia cửa sổ 1/fps giây, lấy biên độ tuyệt đối lớn nhất mỗi cửa sổ, chuẩn hoá theo phân vị 99,5
của các cửa sổ (một tiếng nổ lẻ không làm phẳng cả sóng), kẹp 0..1, làm tròn 3 chữ số.
JSON ra: {"tep", "sha256", "dai" (giây), "fps", "peaks": [...]}. `sha256` là của tệp nguồn để QC đối chiếu đúng tệp giọng.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys

import numpy as np

SR = 16000


class LoiAm(Exception):
    pass


def tinh_peaks(mau, sr=SR, fps=50):
    """mau: mảng int16 (hoặc số thực -1..1). Trả (peaks list[float 0..1], độ dài giây)."""
    x = np.abs(np.asarray(mau, dtype=np.float64))
    if x.size == 0:
        raise LoiAm('tệp âm không có mẫu nào')
    if x.max() > 1.5:
        x = x / 32768.0
    cua = max(1, int(round(sr / fps)))
    n = int(np.ceil(x.size / cua))
    x = np.pad(x, (0, n * cua - x.size))
    p = x.reshape(n, cua).max(axis=1)
    chuan = float(np.percentile(p, 99.5))
    if chuan <= 1e-6:
        raise LoiAm('tệp âm im lặng (không có biên độ)')
    return [round(float(v), 3) for v in np.clip(p / chuan, 0, 1)], len(mau) / sr


def sha256_tep(duong):
    """sha256 băm theo khối 1 MB (tệp giọng có thể rất lớn)."""
    h = hashlib.sha256()
    with open(duong, 'rb') as fh:
        for khoi in iter(lambda: fh.read(1 << 20), b''):
            h.update(khoi)
    return h.hexdigest()


def giai_ma(duong):
    try:
        r = subprocess.run(['ffmpeg', '-v', 'error', '-i', duong, '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError as e:
        raise LoiAm('không tìm thấy ffmpeg trong PATH (cần để giải mã tệp giọng)') from e
    if r.returncode:
        raise LoiAm(f'ffmpeg không đọc được {duong}: ' + r.stderr.decode('utf-8', 'replace')[-300:])
    return np.frombuffer(r.stdout, dtype=np.int16)


def viet_peaks(nguon, out, fps=50):
    mau = giai_ma(nguon)
    peaks, dai = tinh_peaks(mau, SR, fps)
    sha = sha256_tep(nguon)
    d = {'tep': os.path.basename(nguon), 'sha256': sha, 'dai': round(dai, 3), 'fps': fps, 'peaks': peaks}
    with open(out, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(d, fh, ensure_ascii=False, separators=(',', ':'))
        fh.write('\n')
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nguon')
    ap.add_argument('--out', required=True)
    ap.add_argument('--fps', type=int, default=50)
    a = ap.parse_args()
    try:
        d = viet_peaks(a.nguon, a.out, a.fps)
    except LoiAm as e:
        raise SystemExit(f'LỖI: {e}')
    print(f'{a.out}: {len(d["peaks"])} cửa sổ, {d["dai"]} s, từ {d["tep"]}')


if __name__ == '__main__':
    main()
