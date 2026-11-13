# -*- coding: utf-8 -*-
"""soat-sao.py <mã...> — xuất tờ khung (4 khung/clip, 960x540) để soi sao, cờ, huy hiệu trên clip AI trước khi dùng."""
import subprocess, sys, os
from PIL import Image
M = 'E:/Goha-JP/output/261113-kokai-kaisen-1904/muse/'
T = 'C:/Users/admin/AppData/Local/Temp/soat/'
os.makedirs(T, exist_ok=True)
for c in sys.argv[1:]:
    f = M + c + '.mp4'
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout)
    sh = Image.new('RGB', (1920, 1080))
    for i, t in enumerate((0.3, d * 0.35, d * 0.65, d - 0.3)):
        o = f'{T}{c}_{i}.png'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{t:.2f}', '-i', f, '-frames:v', '1', o])
        sh.paste(Image.open(o).convert('RGB').resize((960, 540)), ((i % 2) * 960, (i // 2) * 540))
    sh.save(f'{T}{c}.jpg', quality=90)
    print(c, round(d, 2), 's ->', f'{T}{c}.jpg')
