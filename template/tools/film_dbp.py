"""Dựng HÌNH bản mẫu "Chiến dịch Điện Biên Phủ 1954" theo plans/261025-1950-dien-bien-phu-thu/edl-v1.md.

  python tools/film_dbp.py write              # sinh cấu hình cảnh <khoi>/shots/dbp/*.js + trang HTML
  python tools/film_dbp.py render [S05 ...]   # render từng cảnh -> render/scenes/S##.mp4 (bỏ qua cảnh đã có, --force để làm lại)
  python tools/film_dbp.py assemble           # ghép -> render/picture-v1.mp4 (không âm thanh), kiểm mốc, xuất sheet

Mỗi cảnh = cấu hình shot gốc của thư viện + Object.assign(window.SHOT, {chỉnh riêng}).
fit = thời lượng cảnh (co/giãn đều mọi keyframe), tail = 8 khung giữ thêm cho cảnh có hoà sang cảnh sau.
"""
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.normpath(os.path.join(T, '..', '..', '..', 'output', '261025-dien-bien-phu-mau'))
REN = os.path.join(OUT, 'render')
SCN = os.path.join(REN, 'scenes')
FILM = os.path.join(OUT, 'assets', 'film', 'viet-nam-tren-duong-thang-loi-karmen-1955.mp4')
PHOTO = '../../../../output/261025-dien-bien-phu-mau/assets/photo/'  # tương đối từ template/archival
FPS = 24
TAIL_F = 8
FADE_TO_BLACK = 152.5
KARMEN = 'Tư liệu phim «Việt Nam» (R. Karmen, 1955)'
RED = '#c93b2b'
# Xử lý phim Karmen: cắt khung 4:3 phủ 16:9, giảm bão hoà 30 %, tăng tương phản, hạt, vignette (dùng chung cho mọi tập).
KARMEN_CAT = 'crop=1440:810:240:135'
KARMEN_MAU = 'eq=saturation=0.7:contrast=1.12:brightness=-0.015,noise=alls=9:allf=t:all_seed=7,vignette=angle=0.75'


def F(s):
    return round(s * FPS)


def ph(name):
    return PHOTO + name


def _l29_plus_1():
    # "TRI ÂN…" vào khi lời L29 bắt đầu + 1 s, tính theo giây trong cảnh S33
    plan = next((x.split('=', 1)[1] for x in sys.argv if x.startswith('--voice-plan=')), os.path.join(OUT, 'audio', 'voice7', 'plan.json'))
    tim = next((x.split('=', 1)[1] for x in sys.argv if x.startswith('--timing=')), None)
    if not (tim and os.path.exists(plan)):
        return 1.2  # mốc edl-v1 (picture-v4)
    with open(plan, encoding='utf-8') as fh:
        l29 = next(x for x in json.load(fh) if x['id'] == 'L29')
    with open(tim, encoding='utf-8') as fh:
        s33 = next(x for x in json.load(fh) if x['scene'] == 'S33')
    return round(l29['speech_start'] + 1.0 - s33['start_s'], 3)


L29_PLUS_1 = _l29_plus_1()

# (id, đầu, cuối, khối, shot gốc trong <khoi>/shots/ hoặc None, chỉnh riêng, phụ)
# phụ: {'tail': True} hoà sang cảnh sau; {'karmen': 'mm:ss.s'} trích phim (đầu cảnh đã dò bằng scdet, có thể lệch mốc EDL ±5 s theo moc-canh.md); {'overlay': (khoi, gốc, chỉnh)} lớp chữ trong suốt
SCENES = [
    ('S01', 0.0, 2.2, 'cards', 'the-hook-13-3', {
        'duration': 2.2, 'y': 500,
        'glows': [{'at': 0.1, 'len': 0.6, 'x': 1500, 'y': 980}, {'at': 0.9, 'len': 0.5, 'x': 420, 'y': 1000}, {'at': 1.6, 'len': 0.6, 'x': 1200, 'y': 1020}],
        'lines': [{'text': '13/3/1954', 'at': 0.25, 'size': 160, 'shake': 14, 'flash': 0.35},
                  {'text': 'HIM LAM · ĐIỆN BIÊN PHỦ', 'at': 1.0, 'size': 66, 'color': RED, 'shake': 8, 'flash': 0.2, 'spacing': 10}]}, {}),
    ('S02', 2.2, 6.1, 'archival', 'anh-luu-phao-105-parallax', {
        'fit': 3.9, 'date': '13/3/1954 · khoảng 17:00', 'fadeIn': 0,
        'credit': 'Đơn vị lựu pháo 105 ly chuẩn bị ra chiến trường Điện Biên Phủ · Ảnh: TTLTQG III / TTXVN'}, {}),
    ('S03', 6.1, 9.8, None, None, {}, {'karmen': '43:07.5', 'shake': True}),
    ('S04', 9.8, 14.3, 'map3d', 'shot-a-toan-canh', {
        'fit': 4.5, 'fadeIn': 0,
        'titles': [{'text': '49 CỨ ĐIỂM', 'from': 5.2, 'y': 790, 'size': 76},
                   {'text': '16.200 QUÂN · LÚC ĐÔNG NHẤT', 'from': 5.6, 'y': 885, 'size': 50}]}, {'tail': True}),
    ('S05', 14.3, 17.9, 'map3d', 'shot-c-keo-phao', {
        'duration': 3.6,
        'camera': [{'t': 0, 'lat': 21.476, 'lon': 103.097, 'dist': 13.2, 'heading': 317, 'pitch': 50, 'fov': 42},
                   {'t': 3.6, 'lat': 21.468, 'lon': 103.088, 'dist': 12.4, 'heading': 320, 'pitch': 48, 'fov': 42, 'ease': 'sine'}],
        'routes': [{'path': 'keo-phao', 'style': 'route', 'from': 0.1, 'dur': 3.1, 'ease': 'inOut', 'width': 60,
                    'label': '15 KM', 'labelSub': 'hướng kéo pháo (minh họa)', 'labelAt': 0.3, 'labelDy': -110, 'labelFrom': 0.8, 'labelSize': 44,
                    'troops': {'kind': 'cannon', 'count': 6, 'size': 64, 'gap': 44, 'lag': 0}}],
        'points': [{'id': 'h6', 'from': 0.15, 'size': 28, 'dx': -150}]}, {}),
    ('S06', 17.9, 21.2, None, None, {}, {'karmen': '40:46.53', 'texts': [{'text': 'HƠN 261.000 DÂN CÔNG', 'from': 0.35, 'y': 860, 'size': 84}]}),
    ('S07', 21.2, 24.8, 'archival', None, {
        'duration': 3.6, 'image': ph('quan-phap-ra-hang-cau-muong-thanh-01.jpg'), 'grade': 'bw-am', 'seed': 11, 'shake': 0.8, 'flicker': 0.02,
        'move': [{'t': 0, 'x': 0.5, 'y': 0.5, 'zoom': 1.04}, {'t': 3.6, 'x': 0.52, 'y': 0.48, 'zoom': 1.12, 'ease': 'sine'}],
        'date': '7/5/1954', 'credit': 'Quân Pháp ra hàng trên cầu Mường Thanh · Ảnh: TTLTQG III / TTXVN'}, {}),
    ('S08', 24.8, 27.4, 'cards', 'the-hook-13-3', {
        'duration': 2.6, 'y': 600, 'glows': [],
        'lines': [{'text': 'VÌ SAO?', 'at': 0.12, 'size': 230, 'color': RED, 'shake': 18, 'flash': 0.45, 'spacing': 6}]}, {}),
    ('S09', 27.4, 28.6, 'cards', 'the-chuong-1', {'duration': 1.2, 'hit': 0.06, 'fadeOut': 0}, {'tail': True}),
    ('S10', 28.6, 33.4, 'map3d', 'shot-b-ba-phan-khu', {'fit': 4.8}, {}),
    ('S11', 33.4, 37.7, 'cards', None, {
        'type': 'so-lieu', 'duration': 4.3, 'layout': 'row', 'title': '5 ĐẠI ĐOÀN CHỦ LỰC',
        'items': [{'value': v, 'count': False, 'from': 0.5 + i * 0.12, 'size': 170} for i, v in enumerate([308, 312, 316, 304, 351])],
        'source': 'Nguồn: Báo Nhân Dân; Báo QĐND'}, {}),
    ('S12', 37.7, 46.2, 'archival', None, {
        'duration': 8.5, 'image': ph('giap-xem-ban-do-01.jpg'), 'lanhTu': True, 'grade': 'goc',
        'move': [{'t': 0, 'x': 0.5, 'y': 0.5, 'zoom': 1.0}, {'t': 8.5, 'x': 0.5, 'y': 0.5, 'zoom': 1.06, 'ease': 'linear'}],
        'credit': 'Đại tướng Võ Nguyên Giáp và các chiến sĩ xem bản đồ trước khi mở màn Chiến dịch, 1954 · Ảnh: TTLTQG III'}, {}),
    ('S13', 46.2, 50.8, 'cards', None, {
        'type': 'may-chu', 'duration': 4.6, 'seed': 13,
        'kicker': 'CUỐI THÁNG 1/1954 · BỘ CHỈ HUY CHIẾN DỊCH', 'title': 'ĐỔI PHƯƠNG CHÂM TÁC CHIẾN',
        'blocks': [{'text': 'ĐÁNH NHANH, THẮNG NHANH', 'size': 96, 'y': 480, 'maxW': 1600, 'start': 0.2, 'deadline': 1.45, 'strike': True, 'dimAfter': 0.5, 'after': 0.45},
                   {'text': 'ĐÁNH CHẮC, TIẾN CHẮC', 'size': 96, 'y': 650, 'maxW': 1600, 'gap': 0, 'deadline': -1.25, 'highlight': True}],
        'source': 'Nguồn: Báo QĐND; Báo Nhân Dân'}, {'typing': True, 'manual': True}),
    ('S14', 50.8, 54.6, 'archival', 'anh-keo-phao-parallax', {
        'fit': 3.8, 'fadeIn': 0, 'date': 'THÁNG 1/1954 · KÉO PHÁO',
        'credit': 'Bộ đội kéo pháo vào mặt trận Điện Biên Phủ (ảnh minh họa) · Ảnh: TTLTQG III / TTXVN'}, {}),
    ('S15', 54.6, 57.8, 'cards', 'the-lich-1-2-1954', {'fit': 3.2}, {}),
    ('S16', 57.8, 61.0, None, None, {}, {'karmen': '41:32.4'}),
    ('S17', 61.0, 66.4, 'archival', None, {
        'duration': 5.4, 'image': ph('phao-cao-xa-ban-01.jpg'), 'contain': True, 'containPad': 260, 'grade': 'bw', 'exposure': 0.85, 'vignette': 0.5, 'seed': 13, 'flicker': 0.02, 'grain': 0.1,
        'move': [{'t': 0, 'x': 0.5, 'y': 0.5, 'zoom': 1.0}, {'t': 5.4, 'x': 0.5, 'y': 0.5, 'zoom': 1.05, 'ease': 'linear'}],
        'credit': 'Các khẩu pháo đã sẵn sàng chiến đấu, 1954 (ảnh minh họa) · Ảnh: TTLTQG III · Tên, chức danh: Báo QĐND; Báo Nhân Dân'},
     {'overlay': ('cards', 'lower-third-to-vinh-dien', {'duration': 5.4, 'from': 0.5, 'y': 800, 'previewBg': None, 'source': None})}),
    ('S18', 66.4, 73.3, 'cards', 'the-so-lieu-hau-phuong', {'duration': 6.9, 'items': [
        {'value': 261453, 'from': 0.15, 'dur': 0.6, 'unit': 'DÂN CÔNG', 'label': 'phục vụ chiến dịch'},
        {'value': 20991, 'from': 0.3, 'dur': 0.6, 'unit': 'XE ĐẠP THỒ', 'label': 'phục vụ chiến dịch'},
        {'value': 23000, 'from': 0.45, 'dur': 0.55, 'prefix': 'HƠN', 'unit': 'TẤN GẠO', 'label': 'nhân dân đóng góp'}]}, {}),
    ('S19', 73.3, 74.3, 'cards', 'the-chuong-1', {'duration': 1.0, 'hit': 0.05, 'fadeOut': 0, 'number': 2, 'title': 'BA ĐỢT TIẾN CÔNG'}, {}),
    ('S20', 74.3, 80.7, 'map3d', 'shot-d-dot-1', {'fit': 6.4}, {}),
    ('S21', 80.7, 87.9, 'map3d', 'shot-e-dot-2-hao', {'fit': 7.2}, {}),
    ('S22', 87.9, 92.4, 'map3d', 'shot-f-dot-3-a1', {'fit': 4.5,
        'date': [{'text': 'ĐỢT 3 · 1–7/5/1954', 'from': 0.2, 'to': 5.0}, {'text': '20:30 · 6/5/1954 · ĐỒI A1', 'from': 5.4}],
        'flashes': [{'id': 'a1', 'at': 7.3, 'count': 1, 'len': 1.4, 'size': 520, 'color': 'rgba(255,150,60,A)'}]}, {}),
    ('S23', 92.4, 96.6, 'archival', None, {
        'duration': 4.2, 'image': ph('tan-cong-doi-a1-01.jpg'), 'grade': 'bw-am', 'seed': 17, 'shake': 1.5, 'flicker': 0.03,
        'move': [{'t': 0, 'x': 0.5, 'y': 0.45, 'zoom': 1.06}, {'t': 4.2, 'x': 0.48, 'y': 0.42, 'zoom': 1.14, 'ease': 'sine'}],
        'drift': {'x': 30, 'y': 4, 'zoom': 0.04}, 'bgDepth': 0.1, 'bgBlur': 1.5,
        'layers': [
            {'name': 'bo-doi', 'depth': 0.55, 'feather': 8, 'poly': [[0.2, 0.48], [0.2, 0.33], [0.26, 0.22], [0.3, 0.2], [0.38, 0.2], [0.41, 0.33], [0.5, 0.12], [0.52, 0.08], [0.57, 0.08], [0.6, 0.18], [0.66, 0.18], [0.67, 0.35], [0.5, 0.42], [0.3, 0.46]]},
            {'name': 'dat-da', 'depth': 1.0, 'feather': 5, 'poly': [[0, 0.44], [0.2, 0.46], [0.35, 0.42], [0.5, 0.4], [0.6, 0.36], [0.75, 0.37], [0.9, 0.38], [1, 0.36], [1, 1], [0, 1]]}],
        'dust': {'count': 60, 'opacity': 0.3, 'smoke': 0.7, 'seed': 31},
        'flashes': [{'at': 0.2, 'len': 0.6, 'strength': 0.9}],
        'credit': 'Trận đánh đồi A1 · ảnh tư liệu 1954, chụp lại sau trận · Ảnh: TTLTQG III / TTXVN'}, {}),
    ('S24', 96.6, 99.9, 'cards', 'the-hook-13-3', {
        'duration': 3.3, 'y': 560, 'glows': [{'at': 0.1, 'len': 0.8, 'x': 960, 'y': 1000}],
        'lines': [{'text': '7/5/1954 · 17:30', 'at': 0.2, 'size': 160, 'shake': 12, 'flash': 0.35}]}, {}),
    ('S25', 99.9, 106.1, 'map3d', 'shot-g-ket-ham', {
        'fit': 6.2, 'titles': [], 'fadeOut': 0,
        'credit': 'Địa hình: AWS Terrain Tiles (SRTM, công cộng) · Ảnh vệ tinh: Sentinel-2 cloudless 2016 (EOX, CC BY 4.0) · Vị trí: OpenStreetMap (ODbL) · Tên, chức danh: Báo QĐND; Báo Nhân Dân'},
     {'overlay': ('cards', 'lower-third-to-vinh-dien', {'duration': 6.2, 'from': 1.2, 'y': 800, 'previewBg': None, 'source': None,
                                                         'name': 'TẠ QUỐC LUẬT', 'role': 'ĐẠI ĐỘI TRƯỞNG', 'detail': 'Đại đội 360'})}),
    ('S26', 106.1, 110.5, 'archival', None, {
        'duration': 4.4, 'image': ph('co-quyet-chien-quyet-thang-noc-ham-01.jpg'), 'grade': 'bw-am', 'seed': 19, 'flicker': 0.02,
        'move': [{'t': 0, 'x': 0.55, 'y': 0.48, 'zoom': 1.05}, {'t': 4.4, 'x': 0.55, 'y': 0.46, 'zoom': 1.11, 'ease': 'sine'}],
        'drift': {'x': 18, 'y': 0, 'zoom': 0.025}, 'bgDepth': 0.1, 'bgBlur': 1.2,
        'layers': [
            {'name': 'ham-co', 'depth': 0.5, 'feather': 5, 'poly': [[0, 0.52], [0.3, 0.53], [0.4, 0.46], [0.42, 0.45], [0.49, 0.44], [0.55, 0.41], [0.56, 0.3], [0.58, 0.27], [0.62, 0.28], [0.68, 0.31], [0.68, 0.42], [0.6, 0.42], [0.58, 0.48], [0.73, 0.49], [0.75, 0.5], [0.85, 0.5], [0.93, 0.57], [1, 0.57], [1, 1], [0, 1]]},
            {'name': 'tien-canh', 'depth': 1.0, 'feather': 6, 'poly': [[0, 0.72], [0.3, 0.71], [0.5, 0.74], [0.7, 0.72], [1, 0.73], [1, 1], [0, 1]]}],
        'dust': {'count': 30, 'opacity': 0.22, 'smoke': 0.3, 'seed': 41},
        'credit': 'Lá cờ «Quyết chiến, Quyết thắng» trên nóc hầm De Castries · ảnh tư liệu 1954, chụp lại sau trận · Ảnh: TTLTQG III / TTXVN'}, {}),
    ('S27', 110.5, 116.0, 'cards', None, {
        'type': 'so-lieu', 'duration': 5.5, 'layout': 'row',
        'items': [{'value': 16000, 'prefix': 'HƠN', 'from': 0.12, 'dur': 0.6, 'size': 200, 'label': 'địch bị tiêu diệt và bắt sống'},
                  {'value': 62, 'from': 0.3, 'dur': 0.5, 'size': 200, 'label': 'máy bay bị bắn rơi, phá hủy'}],
        'source': 'Nguồn: Báo Điện tử Chính phủ; Báo QĐND'}, {}),
    ('S28', 116.0, 121.8, 'archival', None, {
        'duration': 5.8, 'image': ph('bac-ho-gan-huy-hieu-hoang-dang-vinh-01.jpg'), 'lanhTu': True, 'grade': 'goc',
        'move': [{'t': 0, 'x': 0.5, 'y': 0.5, 'zoom': 1.0}, {'t': 5.8, 'x': 0.5, 'y': 0.5, 'zoom': 1.05, 'ease': 'linear'}],
        'credit': 'Chủ tịch Hồ Chí Minh gắn Huy hiệu Chiến sĩ Điện Biên cho chiến sĩ Hoàng Đăng Vinh · Ảnh: TTLTQG III'}, {}),
    ('S29', 121.8, 129.0, 'cards', None, {
        'type': 'may-chu', 'duration': 7.2, 'seed': 29,
        'kicker': 'THƯ KHEN · 8/5/1954', 'title': 'GỬI BỘ ĐỘI, DÂN CÔNG, THANH NIÊN XUNG PHONG VÀ ĐỒNG BÀO TÂY BẮC',
        'blocks': [{'text': '“Thắng lợi tuy lớn nhưng mới là bắt đầu. Chúng ta không nên vì thắng mà kiêu, không nên chủ quan khinh địch.”',
                    'size': 56, 'y': 400, 'maxW': 1560, 'start': 0.05, 'deadline': -1.25, 'highlight': 'mới là bắt đầu.'}],
        'cite': '— Hồ Chí Minh, Thư khen ngày 8/5/1954 · Hồ Chí Minh Toàn tập; dẫn theo Báo QĐND', 'citeGap': 0.2,
        'source': 'Nguồn: Hồ Chí Minh Toàn tập; dẫn theo Báo QĐND'}, {'typing': True, 'manual': True}),
    ('S30', 129.0, 137.6, 'vnmap', 'vn-b-toan-canh-ket', {'fit': 8.6, 'fadeIn': 0,
        'titles': [{'text': 'HIỆP ĐỊNH GIƠ-NE-VƠ', 'sub': 'Công nhận độc lập, chủ quyền, thống nhất và toàn vẹn lãnh thổ', 'from': 1.5, 'x': 96, 'y': 800, 'size': 66, 'subMaxW': 760}]}, {}),
    ('S31', 137.6, 141.6, None, None, {}, {'karmen': '45:13.9'}),
    ('S32', 141.6, 144.2, 'archival', None, {
        'duration': 2.6, 'image': ph('bo-doi-ho-reo-xac-may-bay-01.jpg'), 'grade': 'bw-am', 'seed': 23, 'flicker': 0.02, 'shake': 0.8,
        'move': [{'t': 0, 'x': 0.5, 'y': 0.5, 'zoom': 1.03}, {'t': 2.6, 'x': 0.5, 'y': 0.48, 'zoom': 1.1, 'ease': 'sine'}],
        'credit': 'Bộ đội chiến sĩ hò reo trên xác máy bay địch bị pháo binh ta bắn rơi, tháng 5/1954 · Ảnh: TTLTQG III'}, {}),
    ('S33', 144.2, 155.0, 'cards', 'the-hook-13-3', {
        'duration': 10.8, 'glows': [], 'fadeOut': 2.5,
        'source': 'Nguồn: Báo QĐND',
        'lines': [{'text': 'ĐIỆN BIÊN PHỦ', 'at': 0.0, 'to': 0.85, 'y': 450, 'size': 150, 'shake': 0, 'flash': 0, 'spacing': 8},
                  {'text': '13/3 – 7/5/1954 · 56 NGÀY ĐÊM', 'at': 0.08, 'to': 0.85, 'y': 600, 'size': 62, 'color': RED, 'shake': 0, 'flash': 0, 'spacing': 6},
                  {'text': 'TRI ÂN CÁC THẾ HỆ CHA ANH', 'at': L29_PLUS_1, 'y': 540, 'size': 96, 'shake': 0, 'flash': 0, 'spacing': 6}]}, {'manual': True}),
]
XFADE_AFTER = {'S04', 'S09'}
OLD = {sc[0]: (sc[1], sc[2]) for sc in SCENES}  # mốc theo edl-v1 (thời lượng gốc của cấu hình)
# Mốc mới chỉ dùng khi chỉ định rõ: --timing=<file json [{scene, start_s, end_s, frames}]>
TIMING = next((x.split('=', 1)[1] for x in sys.argv if x.startswith('--timing=')), None)
if TIMING:
    with open(TIMING, encoding='utf-8') as fh:
        _new = {r['scene']: r for r in json.load(fh)}
    SCENES = [(sc[0], _new[sc[0]]['start_s'], _new[sc[0]]['end_s'], *sc[3:]) for sc in SCENES]
    for sc in SCENES:
        r = _new[sc[0]]
        assert F(sc[2]) - F(sc[1]) == r['frames'], (sc[0], F(sc[2]) - F(sc[1]), r['frames'])
VER = next((a.split('=')[1] for a in sys.argv if a.startswith('--ver=')), 'v2')  # hoà 8 khung sang cảnh kế


def scene_file(block, sid):
    return os.path.join(T, block, 'shots', 'dbp', f'{sid.lower()}.js')


def page(block, sid):
    return os.path.join(T, block, f'dbp-{sid.lower()}.html')


def write_js(path, base, over, comment):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    src = ''
    if base:
        with open(base, encoding='utf-8') as fh:
            src = fh.read().strip() + '\n'
    else:
        src = 'window.SHOT = {};\n'
    over = {k: v for k, v in over.items()}
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(f'// {comment}\n' + src + 'Object.assign(window.SHOT, ' + json.dumps(over, ensure_ascii=False, indent=1) + ');\n')


def cmd_write():
    for sid, a, b, block, base, over, extra in SCENES:
        dur = (F(b) - F(a)) / FPS
        oa, ob = OLD[sid]
        odur = (F(ob) - F(oa)) / FPS
        note = f'Phim mẫu ĐBP {sid} {a:.3f}–{b:.3f} s (mốc theo giọng mới; cấu hình gốc dài {odur:.3f} s)'
        if block:
            o = dict(over)
            if 'fit' in o:
                o['fit'] = dur                     # co/giãn đều keyframe của shot gốc
            elif extra.get('manual'):
                o['duration'] = dur                # cảnh tự đặt mốc theo thời lượng mới (gõ máy chữ, S33)
            elif 'duration' in o:
                o['duration'] = odur               # mốc trong cấu hình viết theo thời lượng cũ...
                o['fit'] = dur                     # ...dời theo cùng tỉ lệ cảnh
            if extra.get('tail'):
                o['tail'] = TAIL_F / FPS
            write_js(scene_file(block, sid), os.path.join(T, block, 'shots', base + '.js') if base else None, o, note)
        if extra.get('karmen') or extra.get('overlay'):
            if extra.get('overlay'):
                ob, obase, oo = extra['overlay']
            else:
                ob, obase, oo = 'overlay', None, {'credit': KARMEN, 'texts': extra.get('texts', [])}
            oo = dict(oo, duration=dur)
            write_js(os.path.join(T, ob, 'shots', 'dbp', f'{sid.lower()}-lop-chu.js'), os.path.join(T, ob, 'shots', obase + '.js') if obase else None, oo, note + ' — lớp chữ trong suốt')
    subprocess.run([sys.executable, os.path.join(T, 'tools', 'build_shots.py')], check=True, stdout=subprocess.DEVNULL)
    print('đã sinh', len(SCENES), 'cảnh')


def run(args):
    r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise SystemExit(f'Lỗi: {" ".join(args)}\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}')
    return r.stdout


DUNG_TRANG = ['node', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools', 'kit', 'dung-trang.mjs')]


def dung_trang(*a):
    """Dựng trang HTML (mp4, mov trong suốt, --data) bằng tools/kit/dung-trang.mjs."""
    return run([*DUNG_TRANG, *a])


def tc(s):
    m, sec = s.split(':')
    return int(m) * 60 + float(sec)


def frames_of(path):
    out = run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', path])
    return int(out.strip().split(',')[0])


def cmd_render(only, force):
    os.makedirs(SCN, exist_ok=True)
    for sid, a, b, block, base, over, extra in SCENES:
        if only and sid not in only:
            continue
        out = os.path.join(SCN, f'{sid}.mp4')
        if os.path.exists(out) and not force:
            continue
        n = F(b) - F(a) + (TAIL_F if extra.get('tail') else 0)
        lay = None
        if extra.get('karmen') or extra.get('overlay'):
            ob = extra['overlay'][0] if extra.get('overlay') else 'overlay'
            lay = os.path.join(SCN, f'{sid}-lop-chu.mov')
            dung_trang(os.path.join(T, ob, f'dbp-{sid.lower()}-lop-chu.html'), '--out', lay, '--fps', '24', '--transparent', '--force')
        if extra.get('karmen'):
            shake = "crop=w=iw-40:h=ih-24:x='20+7*sin(t*41)':y='12+4*sin(t*53)',scale=1920:1080," if extra.get('shake') else ''
            vf = (f"[0:v]fps=24,{KARMEN_CAT},scale=1920:1080:flags=lanczos,setsar=1,{shake}{KARMEN_MAU}[b];"
                  f"[1:v]format=rgba[o];[b][o]overlay=0:0,format=yuv420p[v]")
            run(['ffmpeg', '-y', '-v', 'error', '-ss', str(tc(extra['karmen'])), '-i', FILM, '-i', lay, '-filter_complex', vf,
                 '-map', '[v]', '-an', '-frames:v', str(n), '-r', '24', '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', out])
        else:
            base_mp4 = out if not lay else os.path.join(SCN, f'{sid}-nen.mp4')
            dung_trang(page(block, sid), '--out', base_mp4, '--fps', '24', '--force')
            if lay:
                run(['ffmpeg', '-y', '-v', 'error', '-i', base_mp4, '-i', lay, '-filter_complex', '[1:v]format=rgba[o];[0:v][o]overlay=0:0,format=yuv420p[v]',
                     '-map', '[v]', '-an', '-r', '24', '-c:v', 'libx264', '-crf', '15', out])
        got = frames_of(out)
        print(f'{sid}: {got} khung (cần {n}){"" if got >= n else "  THIẾU!"}', flush=True)


def cmd_assemble():
    # Hai bước để ít tốn bộ nhớ: (1) chuẩn hoá từng đoạn đúng số khung (cặp hoà cảnh ghép thành một đoạn),
    # (2) nối bằng concat demuxer rồi mã hoá một lần.
    seg_dir = os.path.join(SCN, 'seg')
    os.makedirs(seg_dir, exist_ok=True)
    enc = ['-an', '-r', '24', '-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-pix_fmt', 'yuv420p']
    norm = lambda k, n: f'[{k}:v]fps=24,setsar=1,format=yuv420p,trim=end_frame={n},setpts=PTS-STARTPTS'
    segs, i = [], 0
    while i < len(SCENES):
        sid, a, b, *_rest = SCENES[i]
        n = F(b) - F(a) + (TAIL_F if _rest[-1].get('tail') else 0)
        out = os.path.join(seg_dir, f'{sid}.mp4')
        if sid in XFADE_AFTER:
            sid2, a2, b2, *_r2 = SCENES[i + 1]
            n2 = F(b2) - F(a2)
            off = (F(b) - F(a)) / FPS
            g = f'{norm(0, n)}[a];{norm(1, n2)}[b];[a][b]xfade=transition=fade:duration={TAIL_F / FPS:.6f}:offset={off:.6f}[v]'
            run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(SCN, f'{sid}.mp4'), '-i', os.path.join(SCN, f'{sid2}.mp4'),
                 '-filter_complex', g, '-map', '[v]', *enc, out])
            i += 2
        else:
            run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(SCN, f'{sid}.mp4'), '-filter_complex', norm(0, n) + '[v]',
                 '-map', '[v]', *enc, out])
            i += 1
        segs.append(out)
    lst = os.path.join(seg_dir, 'list.txt')
    with open(lst, 'w', encoding='utf-8') as fh:
        fh.write(''.join(f"file '{x.replace(os.sep, '/')}'\n" for x in segs))
    out = os.path.join(REN, f'picture-{VER}.mp4')  # mờ về đen từ 152,5 s nằm trong trang S33 (fadeOut)
    run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-an', '-r', '24',
         '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out])
    check(out)
    sheet(out)


def check(path):
    total = frames_of(path)
    want = F(SCENES[-1][2])
    print(f'\nTổng: {total} khung = {total / FPS:.3f} s (cần {want} khung) -> {"ĐẠT" if abs(total - want) <= 1 else "LỆCH"}')
    print('| Cảnh | Mốc EDL (s) | Khung đầu thực | Mốc thực (s) | Lệch (khung) | Khung | Kết quả |')
    print('|---|---|---|---|---|---|---|')
    pos = 0
    for sid, a, b, *_ in SCENES:
        start = pos
        n = F(b) - F(a)
        got = frames_of(os.path.join(SCN, f'{sid}.mp4'))
        need = n + (TAIL_F if _[-1].get('tail') else 0)
        ok = abs(start - F(a)) <= 1 and got >= need
        print(f'| {sid} | {a:.1f} | {start} | {start / FPS:.3f} | {start - F(a)} | {n} | {"đạt" if ok else "LỖI"} |')
        pos += n


def sheet(path):
    cols, w, h = 6, 320, 180
    rows = (len(SCENES) + cols - 1) // cols
    g = Image.new('RGB', (cols * w, rows * (h + 26)), (12, 12, 12))
    d = ImageDraw.Draw(g)
    try:
        fnt = ImageFont.truetype(os.path.join(T, 'fonts', 'BeVietnamPro-SemiBold.ttf'), 18)
    except OSError:
        fnt = ImageFont.load_default()
    tmp = os.path.join(SCN, '_mid.png')
    for i, (sid, a, b, *_) in enumerate(SCENES):
        mid = (F(a) + F(b)) // 2
        run(['ffmpeg', '-y', '-v', 'error', '-i', path, '-vf', f'select=eq(n\\,{mid}),scale={w}:{h}', '-frames:v', '1', tmp])
        x, y = (i % cols) * w, (i // cols) * (h + 26)
        g.paste(Image.open(tmp).convert('RGB'), (x, y + 26))
        d.text((x + 6, y + 3), f'{sid}  {a:.1f}–{b:.1f} s', fill=(240, 230, 210), font=fnt)
    os.remove(tmp)
    out = os.path.join(REN, f'picture-{VER}-sheet.jpg')
    g.save(out, quality=88)
    print('sheet:', out)


def cmd_typing():
    # Mốc gõ phím tuyệt đối trên timeline phim: ký tự hiện ở khung đầu tiên có n/24 >= t (khớp khung thật)
    import math
    for sid, a, b, block, base, over, extra in SCENES:
        if not extra.get('typing'):
            continue
        tmp = os.path.join(SCN, f'{sid}-typing-raw.json')
        dung_trang(page(block, sid), '--data', 'TYPING', '--out', tmp, '--force')
        with open(tmp, encoding='utf-8') as fh:
            raw = json.load(fh)
        raw = raw.get('data', raw) if isinstance(raw, dict) else raw
        info = []
        for e in raw:
            n = math.ceil(e['t'] * FPS - 1e-6)
            info.append({'t': round((F(a) + n) / FPS, 4), 'ch': e['ch'], 'kind': e['kind']})
        out = os.path.join(REN, f'typing-{sid}.json')
        with open(out, 'w', encoding='utf-8') as fh:
            json.dump(info, fh, ensure_ascii=False, indent=1)
        keys = [e for e in info if e['kind'] == 'key']
        dur = keys[-1]['t'] - keys[0]['t']
        print(f'{sid}: {len(keys)} phím, gõ {keys[0]["t"]:.3f}–{keys[-1]["t"]:.3f} s (tuyệt đối), '
              f'{(len(info) - 1) / max(dur, 1e-6):.1f} ký tự/giây trung bình, xong trước cuối cảnh {b - keys[-1]["t"]:.2f} s -> {out}')


if __name__ == '__main__':
    c = sys.argv[1] if len(sys.argv) > 1 else ''
    rest = [x for x in sys.argv[2:] if not x.startswith('--')]
    if c == 'write':
        cmd_write()
    elif c == 'render':
        cmd_render(set(rest), '--force' in sys.argv)
    elif c == 'typing':
        cmd_typing()
    elif c == 'assemble':
        cmd_assemble()
    else:
        print(__doc__)
