"""Test máy chặn luật cứng (tools/luat_cung.py), nối vào build_shots.py và sóng âm (tools/song_am.py).
Nguyên tắc cần chứng minh: nghi ngờ thì chặn. Mỗi cách lách đã biết có một test.

Chạy: python -m pytest tools/test_luat_cung.py
"""
import hashlib
import importlib.util
import json
import os
import shutil

import numpy as np
import pytest
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def tai(ten, tep):
    spec = importlib.util.spec_from_file_location(ten, os.path.join(HERE, tep))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


luat = tai('luat_cung', 'luat_cung.py')
song_am = tai('song_am', 'song_am.py')
build = tai('build_shots', 'build_shots.py')
CO_NODE = shutil.which('node') is not None


@pytest.fixture()
def goc(tmp_path):
    """Thư mục khối giả: giọng + peaks khớp sha256 (6 s), PNG có alpha, JPG không alpha, ảnh lớn, khung phim."""
    (tmp_path / 'g.mp3').write_bytes(b'giong-that-gia-lap')
    sha = hashlib.sha256(b'giong-that-gia-lap').hexdigest()
    (tmp_path / 'p.json').write_text(json.dumps({'tep': 'g.mp3', 'sha256': sha, 'dai': 6.0, 'fps': 50, 'peaks': [0.1 * (i % 10) for i in range(300)]}), encoding='utf-8')
    rgba = Image.new('RGBA', (20, 20), (0, 0, 0, 0)); rgba.putpixel((5, 5), (255, 0, 0, 255)); rgba.save(tmp_path / 'nen.png')
    Image.new('RGB', (20, 20), (90, 90, 90)).save(tmp_path / 'anh.jpg')
    Image.new('RGB', (3000, 3000), (9, 9, 9)).save(tmp_path / 'lon.jpg')
    for i in (1, 2, 3):
        Image.new('RGB', (16, 9)).save(tmp_path / f'f{i:03d}.jpg')
    return str(tmp_path)


def am(**kw):
    s = {'type': 'the-am-thanh', 'source': 'nguồn', 'duration': 7, 'nhan': 'MÔ PHỎNG LẠI', 'anh': 'anh.jpg',
         'nguoi': {'ten': 'SĨ QUAN MẪU', 'chucVu': 'x'}, 'giong': {'tep': 'g.mp3', 'peaks': 'p.json', 'batDau': 0.5}}
    s.update(kw)
    return s


def nv(**kw):
    s = {'type': 'nhan-vat', 'source': 'nguồn', 'ten': 'TRẦN VĂN MẪU', 'chucVu': 'x', 'bienThe': 'tach-nen', 'anh': 'nen.png'}
    s.update(kw)
    return s


def phim(**kw):
    p = {'mau': 'f%03d.jpg', 'n': 3, 'fps': 12}
    p.update(kw)
    return {'type': 'phim-panel', 'source': 'x', 'phim': p}


def co(loi, *chu):
    return any(all(c in l for c in chu) for l in loi)


# ---- ba luật cứng bắt buộc + ca hợp lệ ----
def test_lanh_tu_dung_tach_nen_bi_chan(goc):
    assert co(luat.kiem_shot(nv(lanhTu=True), 's', goc), 'lãnh tụ', 'khung')


def test_the_am_thanh_thieu_nhan_bi_chan(goc):
    s = am(); del s['nhan']
    assert co(luat.kiem_shot(s, 's', goc), 'thiếu `nhan`')


def test_lanh_tu_nhan_khac_ghi_am_goc_bi_chan(goc):
    assert co(luat.kiem_shot(am(lanhTu=True, nhan='MÔ PHỎNG LẠI'), 's', goc), 'chỉ được «GHI ÂM GỐC»')


def test_ca_hop_le_khong_loi(goc):
    assert luat.kiem_shot(am(), 's', goc) == []
    assert luat.kiem_shot(am(lanhTu=True, nhan='ghi âm gốc', nguoi={'ten': 'LÃNH TỤ MẪU', 'chucVu': 'x'}), 's', goc) == []
    assert luat.kiem_shot(nv(), 's', goc) == []
    assert luat.kiem_shot(nv(bienThe='khung', lanhTu=True, anh='anh.jpg', zoomDen=1.04), 's', goc) == []
    assert luat.kiem_shot(phim(), 's', goc) == []


# ---- C1: không dò chữ trong văn bản; mọi shot được đánh giá ----
@pytest.mark.skipif(not CO_NODE, reason='cần node')
@pytest.mark.parametrize('viet_type', ["type: `nhan-vat`", "type: 'nhan' + '-vat'", "type: T", "type: ['nhan-vat'].join('')"])
def test_c1_type_viet_kieu_khac_van_bi_chan(tmp_path, monkeypatch, viet_type):
    (tmp_path / 'cards' / 'shots').mkdir(parents=True)
    (tmp_path / 'cards' / 'shots' / 'lach.js').write_text(
        f"const T = 'nhan' + '-vat';\nwindow.SHOT = {{ {viet_type}, bienThe: 'tach-nen', lanhTu: true, source: 'x', ten: 'A', chucVu: 'B', anh: 'a.png' }};\n", encoding='utf-8')
    monkeypatch.setattr(build, 'ROOT', str(tmp_path))
    with pytest.raises(SystemExit) as e:
        build.build('cards')
    assert 'LUẬT CỨNG' in str(e.value) and 'lach' in str(e.value) and 'khung' in str(e.value)


@pytest.mark.skipif(not CO_NODE, reason='cần node')
def test_c1_shot_khong_danh_gia_duoc_bi_chan(tmp_path, monkeypatch):
    (tmp_path / 'cards' / 'shots').mkdir(parents=True)
    (tmp_path / 'cards' / 'shots' / 'hong.js').write_text("window.SHOT = { type: nhan_vat_chua_khai };\n", encoding='utf-8')
    monkeypatch.setattr(build, 'ROOT', str(tmp_path))
    with pytest.raises(SystemExit) as e:
        build.build('cards')
    assert 'không đánh giá được' in str(e.value)


@pytest.mark.skipif(not CO_NODE, reason='cần node')
def test_trang_html_viet_tay_cung_bi_kiem(tmp_path, monkeypatch):
    (tmp_path / 'cards' / 'shots').mkdir(parents=True)
    (tmp_path / 'cards' / 'shots' / 'tot.js').write_text("window.SHOT = { type: 'so-lieu', duration: 3 };\n", encoding='utf-8')
    (tmp_path / 'cards' / 'tay.html').write_text(
        "<html><body><script>window.READY = false;\nwindow.SHOT = { type: 'the-am-thanh', source: 'x', ten: 'Hồ Chí Minh' };\n</script>"
        '<script type="module" src="cards.js"></script></body></html>', encoding='utf-8')
    monkeypatch.setattr(build, 'ROOT', str(tmp_path))
    with pytest.raises(SystemExit) as e:
        build.build('cards')
    assert 'tay.html' in str(e.value)


@pytest.mark.skipif(not CO_NODE, reason='cần node')
def test_moi_trang_cards_trong_repo_dat_luat():
    """Quét mọi cards/*.html thật của repo (kể cả sinh từ shot lẫn viết tay)."""
    cards = os.path.join(ROOT, 'cards')
    items = []
    loi = luat.kiem_khoi(items, cards)
    assert loi == [], loi


# ---- C2: cờ lanhTu sai kiểu ----
@pytest.mark.parametrize('gia_tri', ['true', 1, None, 'yes', 0])
def test_c2_lanh_tu_khong_phai_bool_bi_chan(goc, gia_tri):
    assert co(luat.kiem_shot(nv(lanhTu=gia_tri), 's', goc), '`lanhTu` phải là true hoặc false')
    assert co(luat.kiem_shot(am(lanhTu=gia_tri), 's', goc), '`lanhTu` phải là true hoặc false')


# ---- C3: peaks gắn với tệp giọng và thời lượng ----
def test_c3_sha256_lech_bi_chan(goc):
    (open(os.path.join(goc, 'g.mp3'), 'wb')).write(b'giong-khac')
    assert co(luat.kiem_shot(am(), 's', goc), 'sha256')


def test_c3_thieu_giong_tep_hoac_tep_khong_co(goc):
    s = am(); s['giong'] = {'peaks': 'p.json'}
    assert co(luat.kiem_shot(s, 's', goc), 'thiếu `giong.tep`')
    assert co(luat.kiem_shot(am(giong={'tep': 'khong-co.mp3', 'peaks': 'p.json'}), 's', goc), 'giong.tep', 'không có trên đĩa')


@pytest.mark.parametrize('duration,ok', [(7, True), (6.6, True), (7.0, True), (7.2, False), (3, False), (20, False)])
def test_c3_giong_phai_phu_khoang_tieng_cua_the(goc, duration, ok):
    loi = luat.kiem_shot(am(duration=duration), 's', goc)
    assert (loi == []) == ok, loi
    if not ok:
        assert co(loi, 'lệch `duration`')


# ---- V1: danh sách tên dùng chung ----
def test_v1_bi_danh_va_moi_truong_chu(goc):
    assert co(luat.kiem_shot(nv(ten='Nguyễn Ái Quốc'), 's', goc), 'lãnh tụ', 'Nguyễn Ái Quốc')
    assert co(luat.kiem_shot(nv(chucVu='Chủ tịch Hồ Chí Minh'), 's', goc), '`chucVu`')
    assert co(luat.kiem_shot(am(phuDe=[{'text': 'x'}, {'text': 'Võ Nguyên Giáp nói'}]), 's', goc), 'phuDe[1].text')
    assert co(luat.kiem_shot(am(nguoi={'ten': 'A', 'chucVu': 'B', 'boiCanh': 'Bác Hồ gửi điện'}), 's', goc), 'boiCanh')


def test_v1_to_huu_khong_phai_lanh_tu_va_khop_tu_nguyen(goc):
    assert luat.kiem_shot(nv(ten='Tố Hữu', bienThe='tach-nen'), 's', goc) == []
    assert luat.kiem_shot(am(nguoi={'ten': 'Tố Hữu', 'chucVu': 'nhà thơ'}), 's', goc) == []
    assert luat.kiem_shot(nv(ten='Nguyễn Văn Giáo'), 's', goc) == []


def test_v1_source_duoc_nhac_ten_nhung_truong_khac_thi_khong(goc):
    assert luat.kiem_shot(nv(source='Hồ Chí Minh Toàn tập, tập 12'), 's', goc) == []


def test_v1_danh_sach_dung_chung_va_khong_co_to_huu():
    ten = luat.doc_ten_lanh_tu()
    assert 'Nguyễn Ái Quốc' in ten and not any('tố hữu' in t.lower() for t in ten)
    assert luat.chuan_chu('Nguyễn Đức') == ' nguyen duc '


# ---- V2: đóng khi nghi ngờ với ảnh ----
@pytest.mark.parametrize('anh', ['https://x/y.png', 'data:image/png;base64,AAAA', '/abs/a.png', 'C:/a.png', 'khong-co.png'])
def test_v2_anh_khong_hop_le_bi_chan(goc, anh):
    assert luat.kiem_shot(nv(bienThe='khung', lanhTu=True, anh=anh), 's', goc)
    assert luat.kiem_shot(am(lanhTu=True, nhan='GHI ÂM GỐC', anh=anh, nguoi={'ten': 'X', 'chucVu': 'y'}), 's', goc)


def test_v2_thieu_pillow_thi_loi_chu_khong_im_lang(goc, monkeypatch):
    monkeypatch.setattr(luat, '_pil', lambda: None)
    assert co(luat.kiem_shot(nv(bienThe='khung', lanhTu=True, anh='anh.jpg'), 's', goc), 'thiếu Pillow')
    assert co(luat.kiem_shot(am(lanhTu=True, nhan='GHI ÂM GỐC', nguoi={'ten': 'X', 'chucVu': 'y'}), 's', goc), 'thiếu Pillow')


def test_v2_the_am_thanh_lanh_tu_anh_co_alpha_bi_chan(goc):
    assert co(luat.kiem_shot(am(lanhTu=True, nhan='GHI ÂM GỐC', anh='nen.png', nguoi={'ten': 'X', 'chucVu': 'y'}), 's', goc), 'trong suốt')
    assert co(luat.kiem_shot(nv(bienThe='khung', lanhTu=True, anh='nen.png'), 's', goc), 'trong suốt')


def test_v2_tach_nen_voi_anh_khong_alpha_va_thieu_bien_the(goc):
    assert co(luat.kiem_shot(nv(anh='anh.jpg'), 's', goc), 'tach-nen', 'trong suốt')
    s = nv(); del s['bienThe']
    assert co(luat.kiem_shot(s, 's', goc), 'bienThe')


# ---- V5 + V4 phim ----
@pytest.mark.parametrize('n', [2.5, 0, -1, '3', True, None])
def test_v5_phim_n_phai_nguyen_duong(goc, n):
    assert co(luat.kiem_shot(phim(n=n), 's', goc), 'phim.n')


def test_v4_tran_ram_theo_kich_thuoc_that(goc):
    for i in (1, 50):   # khung 3000×3000: 50 khung ≈ 1,7 GB
        shutil.copy(os.path.join(goc, 'lon.jpg'), os.path.join(goc, f'g{i:03d}.jpg'))
    assert co(luat.kiem_shot(phim(mau='g%03d.jpg', n=50), 's', goc), 'vượt trần')
    assert luat.uoc_ram(150, 1104, 621) < luat.TRAN_RAM_BYTE < luat.uoc_ram(150, 1920, 1080)


def test_thieu_khung_phim_va_nguon(goc):
    assert co(luat.kiem_shot(phim(n=9), 's', goc), 'khung phim')
    s = nv(); del s['source']
    assert co(luat.kiem_shot(s, 's', goc), 'source')


# ---- T1, T4 ----
@pytest.mark.parametrize('z', ['abc', None, True, [1], 1.2, 0.9])
def test_t1_zoom_den_khong_hop_le_khong_nem_ngoai_le(goc, z):
    assert co(luat.kiem_shot(nv(bienThe='khung', lanhTu=True, anh='anh.jpg', zoomDen=z), 's', goc), 'zoomDen')


def test_t4_tran_phong_cat_anh_lanh_tu(goc):
    sai = luat.kiem_shot(nv(bienThe='khung', lanhTu=True, anh='anh.jpg', cat=[0.5, 0.5, 0.4]), 's', goc)
    assert co(sai, 'phóng quá 2 lần')
    assert luat.kiem_shot(nv(bienThe='khung', lanhTu=True, anh='anh.jpg', cat=[0.5, 0.5, 0.6]), 's', goc) == []


def test_shot_cu_khong_bi_anh_huong(goc):
    assert luat.kiem_shot({'type': 'so-lieu'}, 's', goc) == []


# ---- nối vào build_shots ----
@pytest.mark.skipif(not CO_NODE, reason='cần node')
def test_build_shots_dung_khi_vi_pham_va_khong_ghi_trang(tmp_path, monkeypatch):
    (tmp_path / 'cards' / 'shots').mkdir(parents=True)
    (tmp_path / 'cards' / 'shots' / 'xau.js').write_text("window.SHOT = { type: 'nhan-vat', bienThe: 'tach-nen', lanhTu: true, source: 'x', ten: 'A', chucVu: 'B', anh: 'a.png' };\n", encoding='utf-8')
    (tmp_path / 'cards' / 'shots' / 'tot.js').write_text("window.SHOT = { type: 'so-lieu', duration: 3 };\n", encoding='utf-8')
    monkeypatch.setattr(build, 'ROOT', str(tmp_path))
    with pytest.raises(SystemExit) as e:
        build.build('cards')
    assert 'LUẬT CỨNG' in str(e.value) and 'xau' in str(e.value)
    assert not (tmp_path / 'cards' / 'tot.html').exists()


@pytest.mark.skipif(not CO_NODE, reason='cần node')
def test_build_shots_dung_duoc_khi_hop_le(tmp_path, monkeypatch):
    (tmp_path / 'cards' / 'shots').mkdir(parents=True)
    Image.new('RGB', (8, 10)).save(tmp_path / 'cards' / 'a.jpg')
    (tmp_path / 'cards' / 'shots' / 'tot.js').write_text("window.SHOT = { type: 'nhan-vat', bienThe: 'khung', lanhTu: true, source: 'x', ten: 'A', chucVu: 'B', anh: 'a.jpg' };\n", encoding='utf-8')
    monkeypatch.setattr(build, 'ROOT', str(tmp_path))
    assert len(build.build('cards')) == 1
    assert (tmp_path / 'cards' / 'tot.html').exists()


# ---- sóng âm ----
def test_peaks_theo_cua_so_va_chuan_hoa():
    sr, fps = 16000, 50
    x = np.zeros(sr * 2, dtype=np.int16)
    x[sr // 2: sr] = 12000
    x[sr: sr + 800] = 3000
    p, dai = song_am.tinh_peaks(x, sr, fps)
    assert len(p) == 100 and dai == pytest.approx(2.0)
    assert max(p) == 1.0 and p[30] == 1.0 and p[0] == 0.0
    assert 0 < p[50] < 1.0


def test_peaks_im_lang_hoac_rong_bao_loi():
    with pytest.raises(song_am.LoiAm):
        song_am.tinh_peaks(np.zeros(16000, dtype=np.int16))
    with pytest.raises(song_am.LoiAm):
        song_am.tinh_peaks(np.array([], dtype=np.int16))


def test_t2_thieu_ffmpeg_bao_loi_ro_va_sha_theo_khoi(tmp_path, monkeypatch):
    def khong_co(*a, **k):
        raise FileNotFoundError('ffmpeg')
    monkeypatch.setattr(song_am.subprocess, 'run', khong_co)
    with pytest.raises(song_am.LoiAm, match='ffmpeg'):
        song_am.giai_ma('x.wav')
    f = tmp_path / 'a.bin'; f.write_bytes(os.urandom(3 * (1 << 20) + 17))
    assert song_am.sha256_tep(str(f)) == hashlib.sha256(f.read_bytes()).hexdigest() == luat.sha256_tep(str(f))


# Khung lấy tỉ lệ ảnh thật bằng Pillow; JS và Python cùng hợp đồng vùng cắt.
@pytest.mark.parametrize('w,h,ratio', [(600, 800, .75), (900, 600, 1.5), (600, 600, 1), (300, 900, .6), (1800, 600, 1.6)])
def test_khung_theo_ti_le_anh(goc, w, h, ratio):
    Image.new('RGB', (w, h)).save(os.path.join(goc, 'ti-le.jpg'))
    s = nv(bienThe='khung', lanhTu=True, anh='ti-le.jpg')
    assert luat.ti_le_khung(s, w, h) == ratio
    assert luat.kiem_shot(s, 's', goc) == []


@pytest.mark.parametrize('ratio', [.6, .8, 1, 1.6])
def test_khung_ti_le_khai_tay_hop_le(goc, ratio):
    s = nv(bienThe='khung', lanhTu=True, anh='anh.jpg', tiLe=ratio)
    assert luat.ti_le_khung(s, 20, 20) == ratio
    assert luat.kiem_shot(s, 's', goc) == []


@pytest.mark.parametrize('ratio', [2, -1, 0, '1', None, True, float('nan'), float('inf')])
def test_khung_ti_le_khai_tay_sai_bi_chan(goc, ratio):
    assert co(luat.kiem_shot(nv(bienThe='khung', anh='anh.jpg', tiLe=ratio), 's', goc), 'tiLe')


def test_cat_vuot_anh_theo_ti_le_moi(goc):
    Image.new('RGB', (900, 600)).save(os.path.join(goc, 'ngang.jpg'))
    s = nv(bienThe='khung', lanhTu=True, anh='ngang.jpg', tiLe=1.5, cat=[.7, .5, .6])
    assert luat.kiem_shot(s, 's', goc) == []
    s['cat'] = [.9, .5, .6]
    assert co(luat.kiem_shot(s, 's', goc), 'vượt', '1.5')
    s['cat'] = [.5, .5, .8]
    assert luat.kiem_shot(s, 's', goc) == []
    s['tiLe'] = 1
    assert co(luat.kiem_shot(s, 's', goc), 'vượt', '1')
    s['tiLe'] = 1.5
    s['cat'] = [.5, .5, .4]
    assert co(luat.kiem_shot(s, 's', goc), 'phóng quá 2 lần')


@pytest.mark.skipif(not CO_NODE, reason='cần node')
def test_js_python_cung_vung_cat():
    cases = [[[.5, .5, .6], 900, 600, 1.5], [[.5, .5, .8], 600, 800, .75], [[.5, .5, 1], 600, 600, 1], [[.5, .5, .6], 300, 900, .6], [[.5, .5, 1], 900, 600]]
    script = "const fs=require('node:fs');(async()=>{const src=fs.readFileSync('cards/luat-cung.js','utf8');const m=await import('data:text/javascript;base64,'+Buffer.from(src).toString('base64'));const cases=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(cases.map(c=>m.vungCat(...c))));})()"
    r = luat.subprocess.run(['node', '-e', script], input=json.dumps(cases), text=True, capture_output=True, cwd=ROOT, check=True)
    for case, js in zip(cases, json.loads(r.stdout)):
        assert luat.vung_cat(*case) == pytest.approx(js)


def test_kich_thuoc_theo_exif_xoay(goc):
    # JPEG chụp dọc lưu 400×300 kèm Orientation=6: trình duyệt xoay thành 300×400 trước khi vẽ.
    im = Image.new('RGB', (400, 300)); ex = im.getexif(); ex[0x0112] = 6
    duong = os.path.join(goc, 'xoay.jpg'); im.save(duong, exif=ex)
    assert luat.kich_thuoc(duong) == (300, 400)
    s = nv(bienThe='khung', lanhTu=True, anh='xoay.jpg')
    assert luat.tinh_khung_anh(s, *luat.kich_thuoc(duong))['tiLe'] == .75


@pytest.mark.skipif(not CO_NODE, reason='cần node')
def test_js_python_cung_tinh_khung_anh():
    # Cùng đầu vào thì cùng khung, cùng vùng cắt, hoặc cùng báo vượt ảnh.
    cases = [({}, 900, 600), ({}, 300, 900), ({}, 4000, 1000), ({'cat': [.5, .45, .9]}, 800, 1000),
             ({'tiLe': 1.5, 'cat': [.9, .5, .6]}, 900, 600), ({'tiLe': 1, 'cat': [.5, .5, .8]}, 900, 600), ({'tiLe': .6}, 900, 600)]
    script = ("const fs=require('node:fs');(async()=>{const src=fs.readFileSync('cards/luat-cung.js','utf8');"
              "const m=await import('data:text/javascript;base64,'+Buffer.from(src).toString('base64'));"
              "const cases=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(cases.map(([s,w,h])=>"
              "{try{return m.tinhKhungAnh(s,w,h,w,h)}catch(e){return 'LOI'}})));})()")
    r = luat.subprocess.run(['node', '-e', script], input=json.dumps(cases), text=True, capture_output=True, cwd=ROOT, check=True)
    for (s, w, h), js in zip(cases, json.loads(r.stdout)):
        try:
            py = luat.tinh_khung_anh(s, w, h, w, h)
        except ValueError:
            py = 'LOI'
        if js == 'LOI' or py == 'LOI':
            assert js == py, (s, w, h)
        else:
            assert py == pytest.approx(js), (s, w, h)
