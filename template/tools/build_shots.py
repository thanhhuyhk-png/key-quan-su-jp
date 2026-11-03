"""Sinh trang HTML cho từng shot: <khoi>/shots/<ten>.js  ->  <khoi>/<ten>.html

Mỗi file shots/<ten>.js chỉ chứa  window.SHOT = { ... };  (cấu hình của shot).
Trang sinh ra nạp font chung, gắn SHOT rồi nạp engine <khoi>/<khoi>.js.
Chạy:  python tools/build_shots.py            (mọi khối)
       python tools/build_shots.py map3d      (một khối)
"""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location('luat_cung', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'luat_cung.py'))
luat_cung = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(luat_cung)
BLOCKS = ['map3d', 'vnmap', 'cards', 'archival', 'overlay']
PAGE = """<!doctype html><html lang="vi"><head><meta charset="utf-8"><link rel="stylesheet" href="../lib/fonts.css"></head><body>
<!-- Sinh tự động từ shots/{name}.js bằng tools/build_shots.py. Sửa file .js rồi chạy lại, đừng sửa trang này. -->
<script>window.READY = false;
{shot}
</script>
<script type="module" src="{block}.js"></script>
</body></html>
"""


def build(block):
    src = os.path.join(ROOT, block, 'shots')
    if not os.path.isdir(src):
        return []
    made = []
    items = []
    for fn in sorted(os.listdir(src)):
        p = os.path.join(src, fn)
        if os.path.isdir(p):
            items += [(os.path.join(p, f), f'{fn}-{f[:-3]}') for f in sorted(os.listdir(p)) if f.endswith('.js')]
        elif fn.endswith('.js'):
            items.append((p, fn[:-3]))
    # luật cứng của kênh (tools/luat_cung.py): có lỗi thì báo hết rồi dừng, chưa ghi trang nào của khối này
    try:
        loi = luat_cung.kiem_khoi([(p, f'{block}/{n}') for p, n in items], os.path.join(ROOT, block))
    except luat_cung.LoiNode as e:
        raise SystemExit(f'{block}: {e}')
    if loi:
        raise SystemExit('LUẬT CỨNG, dừng dựng trang:\n  - ' + '\n  - '.join(loi))
    for path, name in items:
        fn = os.path.relpath(path, src)
        with open(path, encoding='utf-8') as fh:
            shot = fh.read().strip()
        if 'window.SHOT' not in shot:
            raise SystemExit(f'{block}/shots/{fn}: thiếu "window.SHOT = {{...}}"')
        out = os.path.join(ROOT, block, name + '.html')
        with open(out, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(PAGE.format(name=name, shot=shot, block=block))
        made.append(out)
    return made


if __name__ == '__main__':
    blocks = sys.argv[1:] or BLOCKS
    for b in blocks:
        for p in build(b):
            print(os.path.relpath(p, ROOT))
