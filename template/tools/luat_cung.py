"""Máy chặn luật cứng của kênh cho các shot cards P2 (CLAUDE.md «Luật cứng»). build_shots.py gọi trước khi sinh trang; có lỗi thì dừng.
Bản JS song song (chạy khi trang mở, chặn cả trang HTML viết tay): cards/luat-cung.js. Cả hai đọc chung data/lanh-tu.json.

NGUYÊN TẮC: NGHI NGỜ THÌ BÁO LỖI, không cho qua. Shot được đánh giá bằng node (mọi tệp shot trong khối, và các trang HTML còn lại của khối cards),
rồi mới lọc theo `type` đã tính xong; không dò chữ trong văn bản.

Chặn (mỗi dòng là một lỗi, kèm tên shot):
  1. nhan-vat `lanhTu: true` mà biến thể không phải `khung`; ảnh lãnh tụ có vùng trong suốt (đã tách nền); `zoomDen` ngoài [1; 1,08] hay không phải số;
     `cat` cắt ảnh lãnh tụ phóng quá 2 lần (vùng cắt < 1/2 cạnh ảnh).
  2. the-am-thanh thiếu `nhan`, hoặc `nhan` không phải «MÔ PHỎNG LẠI» / «GHI ÂM GỐC».
  3. the-am-thanh `lanhTu: true` mà `nhan` khác «GHI ÂM GỐC»; ảnh có vùng trong suốt.
  4. `lanhTu` có mặt mà không phải bool (`'true'`, `1`, `null` làm luật bị bỏ qua nên bị chặn).
  5. tên trong data/lanh-tu.json xuất hiện ở BẤT KỲ trường chữ nào (trừ source, credit) của nhan-vat hay the-am-thanh mà không khai `lanhTu: true`.
  6. the-am-thanh: thiếu `giong.tep` hay `giong.peaks`; tệp giọng không có trên đĩa; sha256 của tệp khác sha256 ghi trong peaks; `giong.batDau + dai`
     lệch `duration` quá 0,5 s.
  7. năm loại P2 thiếu `source`; nhan-vat thiếu/sai `bienThe`; `tach-nen` dùng ảnh không có alpha; phim.n không phải số nguyên dương;
     tổng byte khung phim sau giải mã vượt trần 450 MB.
  8. `anh` là URL, `data:`, đường dẫn tuyệt đối; `anh` hay tệp khai mà không có trên đĩa; thiếu Pillow khi cần kiểm ảnh.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DUONG_LANH_TU = os.path.join(os.path.dirname(HERE), 'data', 'lanh-tu.json')
NHAN_AM_THANH = ('MÔ PHỎNG LẠI', 'GHI ÂM GỐC')
TRAN_ZOOM_LANH_TU = 1.08
TI_LE_KHUNG_MIN = 0.6                  # giới hạn rộng/cao của khung theo từng ảnh
TI_LE_KHUNG_MAX = 1.6
TRAN_PHONG_CAT = 2                     # ảnh lãnh tụ: vùng cắt ≥ 1/2 cạnh ảnh
TRAN_RAM_BYTE = 450 * 1024 * 1024      # tổng byte khung phim sau giải mã
LECH_GIONG_TOI_DA = 0.5                # giây
LOAI_P2 = ('tai-lieu-dich', 'phim-panel', 'the-am-thanh', 'nhan-vat', 'bieu-do')
BO_QUA = ('source', 'credit')          # nguồn có thể nhắc tên lãnh tụ (tên sách, báo) nên không quét


class LoiNode(Exception):
    """Không đọc được shot bằng node, hoặc thiếu dữ liệu dùng chung."""


def doc_ten_lanh_tu(duong=DUONG_LANH_TU):
    try:
        d = json.load(open(duong, encoding='utf-8'))
        ten = d['ten']
        assert isinstance(ten, list) and ten and all(isinstance(t, str) for t in ten)
        return ten
    except (OSError, ValueError, KeyError, AssertionError) as e:
        raise LoiNode(f'không đọc được danh sách lãnh tụ {duong} ({type(e).__name__}): không có danh sách thì không kiểm luật') from e


def chuan_chu(s):
    """Không dấu, chữ thường, chỉ chữ/số, bọc khoảng trắng để so khớp từ nguyên (cùng thuật toán cards/luat-cung.js)."""
    s = unicodedata.normalize('NFD', str(s if s is not None else ''))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn').lower().replace('đ', 'd')
    return ' ' + re.sub(r'[^a-z0-9]+', ' ', s).strip() + ' '


def tim_ten_lanh_tu(obj, ten, path=''):
    """Duyệt đệ quy mọi chuỗi trong shot; trả [(đường dẫn, tên)] khi gặp tên lãnh tụ. Bỏ qua source/credit ở gốc."""
    ds = [(n, chuan_chu(n)) for n in ten]
    out = []

    def di(v, p):
        if isinstance(v, str):
            c = chuan_chu(v)
            out.extend((p, n) for n, k in ds if k in c)
        elif isinstance(v, list):
            for i, x in enumerate(v):
                di(x, f'{p}[{i}]')
        elif isinstance(v, dict):
            for k, x in v.items():
                if not (p == '' and k in BO_QUA):
                    di(x, f'{p}.{k}' if p else k)
    di(obj, path)
    return out


def chuan_nhan(s):
    return unicodedata.normalize('NFC', str(s or '')).strip().upper()


def la_so(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v and abs(v) != float('inf')


def uoc_ram(n, w, h):
    return n * w * h * 4


def ti_le_khung(shot, w=None, h=None):
    """Tỉ lệ khai tay phải hợp lệ; tỉ lệ ảnh tự suy được kẹp như bản JS."""
    if 'tiLe' in shot:
        r = shot['tiLe']
        if not la_so(r) or not TI_LE_KHUNG_MIN <= r <= TI_LE_KHUNG_MAX:
            raise ValueError(f'«tiLe» phải là số dương hữu hạn trong [{TI_LE_KHUNG_MIN}; {TI_LE_KHUNG_MAX}]')
        return r
    return max(TI_LE_KHUNG_MIN, min(TI_LE_KHUNG_MAX, w / h))


def vung_cat(cat, w, h, ti_le=None):
    """Vùng cắt chuẩn hoá theo ảnh, cùng đầu vào/kết quả cards/luat-cung.js."""
    if ti_le is None:
        ti_le = ti_le_khung({}, w, h)
    cw = cat[2] * w
    return {'rong': cw / w, 'cao': cw / ti_le / h}


def tinh_khung_anh(shot, w, h, max_w=None, max_h=None):
    """Khung và vùng cắt không kéo giãn ảnh, cùng hợp đồng tinhKhungAnh của cards/luat-cung.js.
    Vùng cắt vượt ảnh thì ValueError. max_w, max_h mặc định là kích thước ảnh."""
    max_w, max_h = (w if max_w is None else max_w), (h if max_h is None else max_h)
    ti_le = ti_le_khung(shot, w, h)
    cat = shot['cat'] if 'cat' in shot else [0.5, 0.5, min(1, ti_le * h / w)]
    if not (isinstance(cat, list) and len(cat) == 3 and all(la_so(x) for x in cat)):
        raise ValueError('«cat» là [tâmX, tâmY, rộng] toàn số')
    cw = cat[2] * w; ch = cw / ti_le; cx = cat[0] * w; cy = cat[1] * h
    if cw <= 0 or cx - cw / 2 < -0.5 or cx + cw / 2 > w + 0.5 or cy - ch / 2 < -0.5 or cy + ch / 2 > h + 0.5:
        raise ValueError(f'«cat» vượt ra ngoài ảnh (tỉ lệ khung {ti_le:g} không vừa); giảm «rộng» hoặc dời tâm. Không kéo giãn ảnh để lấp')
    fh = min(max_h, max_w / ti_le)
    return {'tiLe': ti_le, 'fw': fh * ti_le, 'fh': fh, 'cw': cw, 'ch': ch, 'cx': cx, 'cy': cy}


def sha256_tep(duong):
    h = hashlib.sha256()
    with open(duong, 'rb') as fh:
        for khoi in iter(lambda: fh.read(1 << 20), b''):
            h.update(khoi)
    return h.hexdigest()


def _pil():
    try:
        from PIL import Image
        return Image
    except ImportError:
        return None


def _duong(goc, rel):
    """(đường dẫn thật, None) nếu rel là đường dẫn tương đối hợp lệ; (None, lý do) nếu không."""
    if not isinstance(rel, str) or not rel:
        return None, 'không phải đường dẫn'
    if re.match(r'^[A-Za-z][A-Za-z0-9+.\-]*:', rel) or rel.startswith(('/', '\\')):
        return None, 'là URL, data: hay đường dẫn tuyệt đối; chỉ cho đường dẫn tương đối trong repo'
    p = os.path.normpath(os.path.join(goc, rel))
    return (p, None) if os.path.isfile(p) else (None, 'không có trên đĩa')


def co_alpha(duong):
    """True nếu ảnh có điểm trong suốt. Ném LoiNode khi thiếu Pillow hoặc ảnh không đọc được (đóng khi nghi ngờ)."""
    Image = _pil()
    if Image is None:
        raise LoiNode('thiếu Pillow (pip install pillow): không kiểm được vùng trong suốt của ảnh')
    try:
        with Image.open(duong) as im:
            if im.mode in ('RGBA', 'LA', 'PA') or 'transparency' in im.info:
                return im.convert('RGBA').getchannel('A').getextrema()[0] < 255
            return False
    except OSError as e:
        raise LoiNode(f'không đọc được ảnh {duong}: {e}') from e


def kich_thuoc(duong):
    Image = _pil()
    if Image is None:
        raise LoiNode('thiếu Pillow (pip install pillow): không đo được kích thước ảnh')
    try:
        with Image.open(duong) as im:
            w, h = im.size
            # Trình duyệt xoay ảnh theo EXIF Orientation trước khi vẽ: 5–8 là xoay 90°.
            return (h, w) if im.getexif().get(0x0112) in (5, 6, 7, 8) else (w, h)
    except OSError as e:
        raise LoiNode(f'không đọc được ảnh {duong}: {e}') from e


def _anh(loi, pre, goc, rel, ten='anh'):
    p, ly_do = _duong(goc, rel)
    if p is None:
        loi.append(f'{pre}: `{ten}` {rel!r} {ly_do}')
    return p


def _lam(loi, pre, ham, *a):
    """Chạy một kiểm cần Pillow/đọc ảnh; LoiNode thành một dòng lỗi (không im lặng)."""
    try:
        return ham(*a)
    except LoiNode as e:
        loi.append(f'{pre}: {e}')
        return None


def kiem_shot(shot, ten, goc, ten_lanh_tu=None):
    """Kiểm một shot (dict từ window.SHOT). goc = thư mục chứa trang HTML (đường dẫn trong shot tính từ đó). Trả list lỗi (rỗng = đạt)."""
    loi = []
    t = shot.get('type')
    if t not in LOAI_P2:
        return loi
    pre = f'{ten} [{t}]'
    names = ten_lanh_tu if ten_lanh_tu is not None else doc_ten_lanh_tu()
    if not (shot.get('source') or shot.get('credit')):
        loi.append(f'{pre}: thiếu «source» (nguồn góc phải dưới là bắt buộc)')
    if 'lanhTu' in shot and not isinstance(shot['lanhTu'], bool):
        loi.append(f'{pre}: `lanhTu` phải là true hoặc false (nhận: {shot["lanhTu"]!r}): cờ sai kiểu làm luật lãnh tụ bị bỏ qua')
    lanh_tu = shot.get('lanhTu') is True
    if t in ('nhan-vat', 'the-am-thanh') and not lanh_tu:
        for p, n in tim_ten_lanh_tu(shot, names):
            loi.append(f'{pre}: `{p}` nhắc tên lãnh tụ «{n}» mà shot không khai `lanhTu: true`')
    if t == 'nhan-vat':
        _nhan_vat(shot, pre, goc, lanh_tu, loi)
    elif t == 'the-am-thanh':
        _am_thanh(shot, pre, goc, lanh_tu, loi)
    elif t == 'tai-lieu-dich':
        if shot.get('anh') is not None:
            _anh(loi, pre, goc, shot['anh'])
        else:
            loi.append(f'{pre}: thiếu `anh` (trang scan)')
    elif t == 'phim-panel':
        _phim(shot, pre, goc, loi)
    return loi


def _nhan_vat(shot, pre, goc, lanh_tu, loi):
    bt = shot.get('bienThe')
    if bt not in ('tach-nen', 'khung'):
        loi.append(f'{pre}: `bienThe` bắt buộc là «tach-nen» hoặc «khung» (nhận: {bt!r})')
    if lanh_tu and bt != 'khung':
        loi.append(f'{pre}: lãnh tụ (`lanhTu: true`) dùng biến thể {bt!r}: chỉ được «khung», cấm tách nền, sửa ảnh lãnh tụ')
    if 'zoomDen' in shot:
        z = shot['zoomDen']
        if not la_so(z):
            loi.append(f'{pre}: `zoomDen` phải là số (nhận: {z!r})')
        elif z < 1 or z > TRAN_ZOOM_LANH_TU:
            loi.append(f'{pre}: `zoomDen` {z} ngoài [1; {TRAN_ZOOM_LANH_TU}]: ảnh chỉ được phóng đều rất chậm')
    ti_le_hop_le = True
    if bt == 'khung' and 'tiLe' in shot:
        try:
            ti_le_khung(shot)
        except ValueError as e:
            loi.append(f'{pre}: {e}')
            ti_le_hop_le = False
    cat = shot.get('cat')
    cat_hop_le = True
    if (lanh_tu or bt == 'khung') and 'cat' in shot and not (isinstance(cat, list) and len(cat) == 3 and all(la_so(c) for c in cat)):
        loi.append(f'{pre}: `cat` là [tâmX, tâmY, rộng] toàn số')
        cat_hop_le = False
    if shot.get('anh') is None:
        loi.append(f'{pre}: thiếu `anh`')
        return
    p = _anh(loi, pre, goc, shot['anh'])
    if p is None:
        return
    a = _lam(loi, pre, co_alpha, p)
    if lanh_tu and a:
        loi.append(f'{pre}: ảnh lãnh tụ «{shot["anh"]}» có vùng trong suốt (đã tách nền): dùng ảnh nguyên khung')
    if bt == 'tach-nen' and a is False:
        loi.append(f'{pre}: «{shot["anh"]}» không có vùng trong suốt: biến thể tach-nen cần PNG đã tách nền sẵn')
    if bt == 'khung' and ti_le_hop_le and cat_hop_le:
        kt = _lam(loi, pre, kich_thuoc, p)
        if kt:
            w, h = kt
            try:
                k = tinh_khung_anh(shot, w, h)
            except ValueError as e:
                loi.append(f'{pre}: {e}'); k = None
            v = vung_cat([0.5, 0.5, k['cw'] / w], w, h, k['tiLe']) if k else None
            toi_thieu = 1 / TRAN_PHONG_CAT
            if v and lanh_tu and (v['rong'] < toi_thieu - 1e-9 or v['cao'] < toi_thieu - 1e-9):
                rong, cao = v['rong'], v['cao']
                loi.append(f'{pre}: «cat» cắt ảnh lãnh tụ phóng quá {TRAN_PHONG_CAT} lần (vùng cắt {rong:.0%} × {cao:.0%} ảnh, cần ≥ {toi_thieu:.0%} mỗi chiều): không cắt sát mặt')


def _am_thanh(shot, pre, goc, lanh_tu, loi):
    nhan = shot.get('nhan')
    if nhan in (None, ''):
        loi.append(f'{pre}: thiếu `nhan`: bắt buộc «MÔ PHỎNG LẠI» hoặc «GHI ÂM GỐC»')
    elif chuan_nhan(nhan) not in NHAN_AM_THANH:
        loi.append(f'{pre}: `nhan` {nhan!r} không hợp lệ: chỉ «MÔ PHỎNG LẠI» hoặc «GHI ÂM GỐC»')
    elif lanh_tu and chuan_nhan(nhan) != 'GHI ÂM GỐC':
        loi.append(f'{pre}: lãnh tụ (`lanhTu: true`) có `nhan` {nhan!r}: chỉ được «GHI ÂM GỐC», cấm dựng giọng lãnh tụ')
    if shot.get('anh') is None:
        loi.append(f'{pre}: thiếu `anh` (ảnh người nói)')
    else:
        p = _anh(loi, pre, goc, shot['anh'])
        if p is not None and lanh_tu and _lam(loi, pre, co_alpha, p):
            loi.append(f'{pre}: ảnh lãnh tụ «{shot["anh"]}» có vùng trong suốt (đã tách nền): dùng ảnh nguyên khung')
    g = shot.get('giong') if isinstance(shot.get('giong'), dict) else {}
    if not g.get('tep'):
        loi.append(f'{pre}: thiếu `giong.tep` (tệp giọng thật mà peaks được tính từ đó)')
    if not g.get('peaks'):
        loi.append(f'{pre}: thiếu `giong.peaks` (JSON sóng âm tính từ tệp giọng thật bằng tools/song_am.py)')
        return
    if 'batDau' in g and not (la_so(g['batDau']) and g['batDau'] >= 0):
        loi.append(f'{pre}: `giong.batDau` phải là số ≥ 0')
        return
    pp = _anh(loi, pre, goc, g['peaks'], 'giong.peaks')
    tp = _anh(loi, pre, goc, g['tep'], 'giong.tep') if g.get('tep') else None
    if pp is None:
        return
    try:
        d = json.load(open(pp, encoding='utf-8'))
        ok = isinstance(d.get('peaks'), list) and len(d['peaks']) >= 10 and la_so(d.get('dai')) and d['dai'] > 0 and isinstance(d.get('sha256'), str) and d['sha256']
    except (OSError, ValueError, AttributeError):
        ok = False
    if not ok:
        loi.append(f'{pre}: peaks «{g["peaks"]}» thiếu hoặc hỏng peaks[], dai, sha256 (tạo bằng tools/song_am.py từ tệp giọng thật)')
        return
    if tp is not None and sha256_tep(tp) != d['sha256']:
        loi.append(f'{pre}: sha256 của «{g["tep"]}» khác sha256 trong «{g["peaks"]}»: peaks không phải của tệp giọng này (tạo lại bằng tools/song_am.py)')
    dur = shot.get('duration')
    if not la_so(dur):
        loi.append(f'{pre}: thiếu `duration` số')
    elif abs(g.get('batDau', 0.5) + d['dai'] - dur) > LECH_GIONG_TOI_DA + 1e-9:
        loi.append(f'{pre}: giọng dài {d["dai"]} s từ {g.get("batDau", 0.5)} s, lệch `duration` {dur} s quá {LECH_GIONG_TOI_DA} s: sóng và đầu đọc sẽ lệch tiếng')


def _phim(shot, pre, goc, loi):
    p = shot.get('phim') if isinstance(shot.get('phim'), dict) else {}
    n, dau = p.get('n'), p.get('dau', 1)
    if not (isinstance(n, int) and not isinstance(n, bool) and n >= 1):
        loi.append(f'{pre}: `phim.n` phải là số nguyên dương (nhận: {n!r})')
        return
    if not (isinstance(dau, int) and not isinstance(dau, bool) and dau >= 0):
        loi.append(f'{pre}: `phim.dau` phải là số nguyên ≥ 0')
        return
    m = re.search(r'%0(\d)d', str(p.get('mau', '')))
    if not m:
        loi.append(f'{pre}: `phim.mau` phải chứa %0Nd, ví dụ f%03d.jpg')
        return
    dau_tien = None
    for i in (0, n - 1):
        f = p['mau'].replace(m.group(0), str(dau + i).zfill(int(m.group(1))))
        q = _anh(loi, pre, goc, f, 'khung phim')
        if q is None:
            return
        dau_tien = dau_tien or q
    kt = _lam(loi, pre, kich_thuoc, dau_tien)
    if kt and uoc_ram(n, *kt) > TRAN_RAM_BYTE:
        loi.append(f'{pre}: {n} khung {kt[0]}×{kt[1]} cần ≈ {uoc_ram(n, *kt) // 1048576} MB sau giải mã, vượt trần {TRAN_RAM_BYTE // 1048576} MB: trích lại với --rong nhỏ hơn hoặc ít khung hơn')


# Đọc window.SHOT của nhiều tệp trong một lần gọi node: .js là literal JS; .html lấy các <script> không có src.
_NODE = ("const fs=require('fs');const ds=JSON.parse(fs.readFileSync(0,'utf8'));const out={};"
         "for(const p of ds){try{let c=fs.readFileSync(p,'utf8');"
         "if(p.endsWith('.html'))c=[...c.matchAll(/<script(?![^>]*\\bsrc=)[^>]*>([\\s\\S]*?)<\\/script>/g)].map(m=>m[1]).join('\\n');"
         "const w={};new Function('window',c)(w);out[p]=w.SHOT===undefined?null:w.SHOT;}catch(e){out[p]={__loi:String(e)};}}"
         "process.stdout.write(JSON.stringify(out));")


def doc_shots(duong_dan):
    node = shutil.which('node')
    if not node:
        raise LoiNode('không tìm thấy node trong PATH (cần để đọc shot khi kiểm luật cứng)')
    r = subprocess.run([node, '-e', _NODE], input=json.dumps(duong_dan).encode('utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode:
        raise LoiNode('node lỗi: ' + r.stderr.decode('utf-8', 'replace')[-300:])
    return json.loads(r.stdout.decode('utf-8'))


def kiem_khoi(items, goc):
    """items: [(đường dẫn tệp shot, tên)]; goc: thư mục khối chứa trang HTML. Trả list lỗi.
    Đánh giá MỌI tệp shot bằng node rồi lọc theo type đã tính; khối cards còn quét các trang HTML không sinh từ shot (viết tay, tồn đọng)."""
    cand = [(p, ten, False) for p, ten in items]
    if os.path.basename(os.path.normpath(goc)) == 'cards' and os.path.isdir(goc):
        sinh = {ten.split('/', 1)[-1] for _, ten in items}
        cand += [(os.path.join(goc, f), f'cards/{f}', True) for f in sorted(os.listdir(goc))
                 if f.endswith('.html') and not f.endswith('.__an-chu.html') and f[:-5] not in sinh]
    if not cand:
        return []
    names = doc_ten_lanh_tu()
    kq = doc_shots([p for p, _, _ in cand])
    loi = []
    for p, ten, la_html in cand:
        s = kq.get(p)
        if isinstance(s, dict) and '__loi' in s:
            loi.append(f'{ten}: không đánh giá được {"trang HTML" if la_html else "shot"} (đóng khi nghi ngờ): {s["__loi"]}')
        elif s is None:
            if not la_html:
                loi.append(f'{ten}: không có window.SHOT')
        elif isinstance(s, dict):
            loi += kiem_shot(s, ten, goc, names)
        else:
            loi.append(f'{ten}: window.SHOT không phải object')
    return loi
