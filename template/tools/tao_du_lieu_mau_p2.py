"""Sinh dữ liệu MẪU cho 5 mẫu thẻ P2 vào template/data/mau-p2/ (dữ liệu giả, có nhãn «MẪU», không phải tư liệu lịch sử).

  python -I -X utf8 tools/tao_du_lieu_mau_p2.py [--giong <tệp giọng .wav/.mp3 có sẵn>]

Tạo:
  trang-mau.jpg            trang văn bản giả (scan giả có nhiễu) cho tai-lieu-dich
  nguoi-nen-mau.png        hình người đen xám nền trong suốt cho nhan-vat tach-nen
  nguoi-khung-mau.jpg      ảnh chân dung giả (không có alpha) cho nhan-vat khung
  phim-mau/f001.jpg ...    khung hình trích từ một đoạn phim giả (ffmpeg) cho phim-panel
  giong-mau.mp3 + .peaks.json   giọng (6 s) và sóng âm tính trước cho the-am-thanh

Mọi hình đều vẽ bằng code (Pillow, ffmpeg), có seed cố định nên chạy lại ra đúng bản cũ. Cần Pillow, numpy, ffmpeg.
Giọng: nếu không có --giong thì tự tạo tiếng nói giả (sin điều biên theo âm tiết) bằng ffmpeg, không cần tệp ngoài.
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'data', 'mau-p2')
FONTS = os.path.join(ROOT, 'fonts')

NOI_DUNG = [
    ['Báo cáo mẫu số 00 gửi bộ phận thử bố cục.', 'Mọi dòng chữ trên trang này đều là chữ giả,', 'chỉ dùng để thử cách tô câu và cách dịch.'],
    ['Câu mẫu thứ nhất nằm ở đoạn đầu của trang giấy.', 'Câu mẫu thứ hai nằm ở giữa trang, dài hơn một chút.', 'Câu mẫu thứ ba nằm ở cuối trang và ngắn.'],
    ['Không có số liệu lịch sử nào trong trang này.', 'Khi dùng thật phải thay bằng trang scan thật,', 'có nguồn và có dòng trong sổ số liệu.'],
]


def tep(*p):
    d = os.path.join(OUT, *p)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    return d


def font_lora(size):
    f = ImageFont.truetype(os.path.join(FONTS, 'Lora-VF.ttf'), size)
    try:
        f.set_variation_by_axes([500])
    except Exception:
        pass
    return f


def trang_mau():
    """Trang 1000×1414: giấy xám ngả, chữ mực đen, vài dòng, dấu nghiêng «MẪU» mờ. In ra vùng tô (x, y, w, h chuẩn hoá) của vài câu."""
    w, h = 1000, 1414
    rng = np.random.default_rng(20261103)
    nen = np.full((h, w, 3), (218, 214, 198), dtype=np.float32)
    nen += rng.normal(0, 5.0, (h, w, 1)).astype(np.float32)           # hạt
    yy = np.linspace(-1, 1, h)[:, None, None]
    xx = np.linspace(-1, 1, w)[None, :, None]
    nen -= (xx ** 2 + yy ** 2) * 16                                     # mép tối nhẹ như scan
    im = Image.fromarray(np.clip(nen, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(im)
    muc = (38, 36, 32)
    dr.text((90, 90), 'TÀI LIỆU MẪU', font=font_lora(54), fill=muc)
    dr.text((90, 160), 'KHÔNG PHẢI TƯ LIỆU LỊCH SỬ', font=font_lora(30), fill=(90, 86, 76))
    dr.line([(90, 215), (910, 215)], fill=(90, 86, 76), width=3)
    f = font_lora(37)
    y = 270
    vung = []
    for dd, doan in enumerate(NOI_DUNG):
        for dong in doan:
            dr.text((90, y), dong, font=f, fill=muc)
            wd = dr.textlength(dong, font=f)
            vung.append((90 / w, (y - 4) / h, wd / w, 52 / h))
            y += 58
        y += 40
    # dấu «MẪU» nghiêng, mờ
    stamp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.text((170, 1040), 'MẪU', font=font_lora(260), fill=(140, 40, 30, 70))
    stamp = stamp.rotate(18, resample=Image.BICUBIC, center=(w / 2, 1100))
    im = Image.alpha_composite(im.convert('RGBA'), stamp).convert('RGB')
    im = im.filter(ImageFilter.GaussianBlur(0.6))
    im.save(tep('trang-mau.jpg'), quality=82)
    return vung


def hinh_nguoi(w, h, nen_rgba, ao, da):
    """Hình bán thân đơn giản: đầu elip + vai. ao/da là màu."""
    im = Image.new('RGBA', (w, h), nen_rgba)
    dr = ImageDraw.Draw(im)
    cx = w // 2
    dr.ellipse([cx - w * 0.17, h * 0.07, cx + w * 0.17, h * 0.07 + w * 0.40], fill=da)
    dr.rounded_rectangle([cx - w * 0.07, h * 0.07 + w * 0.36, cx + w * 0.07, h * 0.07 + w * 0.50], radius=10, fill=da)
    dr.polygon([(cx - w * 0.07, h * 0.07 + w * 0.46), (cx + w * 0.07, h * 0.07 + w * 0.46), (w * 0.98, h * 0.60), (w * 0.98, h), (w * 0.02, h), (w * 0.02, h * 0.60)], fill=ao)
    return im


def nguoi_nen():
    """PNG nền trong suốt, mép mềm (alpha liên tục), tỉ lệ đứng 700×900."""
    im = hinh_nguoi(700, 900, (0, 0, 0, 0), (74, 86, 64, 255), (176, 148, 122, 255))
    a = im.getchannel('A').filter(ImageFilter.GaussianBlur(1.4))
    im.putalpha(a)
    dr = ImageDraw.Draw(im)
    dr.text((350, 640), 'ẢNH MẪU', font=font_lora(48), fill=(244, 238, 218, 235), anchor='mm')
    im.save(tep('nguoi-nen-mau.png'), optimize=True)


def nguoi_khung():
    """JPG chân dung giả 800×1000, nền xám chuyển sắc, không có alpha."""
    w, h = 800, 1000
    g = np.linspace(120, 70, h, dtype=np.float32)[:, None, None] * np.ones((1, w, 3), dtype=np.float32)
    nen = Image.fromarray(g.astype(np.uint8))
    nguoi = hinh_nguoi(w, h, (0, 0, 0, 0), (58, 66, 52, 255), (176, 148, 122, 255))
    nen = Image.alpha_composite(nen.convert('RGBA'), nguoi).convert('RGB')
    dr = ImageDraw.Draw(nen)
    dr.text((w // 2, 700), 'ẢNH MẪU', font=font_lora(56), fill=(244, 238, 218), anchor='mm')
    nen.save(tep('nguoi-khung-mau.jpg'), quality=85)


def chay(cmd):
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode:
        raise SystemExit(f'{cmd[0]} lỗi:\n' + r.stdout.decode('utf-8', 'replace')[-800:])


def phim_mau():
    """3 giây phim giả 12 khung/s (36 khung 768×432): hạt, mây trôi, khối sáng đi ngang. Chỉ để thử, nhãn «PHIM MẪU» in trong hình."""
    d = tep('phim-mau', 'x')
    d = os.path.dirname(d)
    for f in os.listdir(d):
        os.remove(os.path.join(d, f))
    vf = ("gradients=s=768x432:d=3:r=12:speed=0.03:c0=0x2a2a28:c1=0xb4b4a8:c2=0x5a5a54:nb_colors=3:seed=7,format=gray,"
          "noise=alls=22:allf=t,drawbox=x='-120+t*300':y=190:w=120:h=90:color=white@0.55:t=fill,"
          "drawtext=fontfile='" + os.path.join(FONTS, 'BeVietnamPro-SemiBold.ttf').replace('\\', '/').replace(':', '\\:') + "':text='PHIM MẪU':fontcolor=white@0.8:fontsize=44:x=24:y=24,"
          "vignette=PI/5,format=yuvj420p")
    chay(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', vf, '-q:v', '5', os.path.join(d, 'f%03d.jpg')])
    return len(os.listdir(d))


def giong(nguon):
    """Giọng 6 s mono 16 kHz mp3 + peaks. Có `nguon` thì cắt 6 s từ đó; không thì tạo tiếng nói giả."""
    mp3 = tep('giong-mau.mp3')
    if nguon:
        chay(['ffmpeg', '-y', '-v', 'error', '-ss', '20', '-t', '6', '-i', nguon, '-ac', '1', '-ar', '16000', '-b:a', '48k', mp3])
    else:
        # tiếng nói giả: sóng 140 Hz và 2,8 kHz điều biên theo nhịp âm tiết ~4 Hz, nghỉ ở giây thứ 3
        expr = "aevalsrc='(0.5*sin(2*PI*140*t)+0.25*sin(2*PI*2800*t))*pow(abs(sin(PI*4*t)),0.7)*(1-between(t,2.9,3.4))':s=16000:d=6"
        chay(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', expr, '-ac', '1', '-b:a', '48k', mp3])
    chay([sys.executable, '-I', '-X', 'utf8', os.path.join(HERE, 'song_am.py'), mp3, '--out', tep('giong-mau.peaks.json')])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--giong', help='tệp giọng có sẵn (cắt 6 s từ giây 20)')
    a = ap.parse_args()
    vung = trang_mau()
    print('vùng các dòng chữ trên trang (x, y, w, h chuẩn hoá):')
    for i, v in enumerate(vung):
        print(f'  dòng {i}: [{v[0]:.3f}, {v[1]:.3f}, {v[2]:.3f}, {v[3]:.3f}]')
    nguoi_nen()
    nguoi_khung()
    print('số khung phim:', phim_mau())
    giong(a.giong)


if __name__ == '__main__':
    main()
