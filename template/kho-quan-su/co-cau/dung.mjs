#!/usr/bin/env node
// Dựng một cơ cấu (thư mục có main.js) bằng kit teardown rồi chụp ảnh soát hoặc xuất video.
//
//   node dung.mjs khoa-nong-105                  → bảng ảnh soát theo các mốc trong timeline.json
//   node dung.mjs khoa-nong-105 --video          → mp4 1920x1080 30 fps (--fps 60 nếu cần)
//   node dung.mjs khoa-nong-105 --still 9.4      → một khung PNG
//
// Kit đặt ở khoá teardown trong cau-hinh.toml ở gốc repo (hoặc biến TEARDOWN_DIR). Đầu ra: <thư mục chạy lệnh>/teardown-out/.
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
// Đọc khoá teardown trong cau-hinh.toml (gốc repo); không có thì báo rõ phải điền gì.
function teardownTrongCauHinh() {
  const f = path.resolve(HERE, '../../../cau-hinh.toml');
  if (!fs.existsSync(f)) return '';
  const m = fs.readFileSync(f, 'utf8').match(/^teardown\s*=\s*"([^"]*)"/m);
  return m ? m[1] : '';
}
const KIT = process.env.TEARDOWN_DIR || teardownTrongCauHinh();
if (!KIT) throw new Error('Chưa có đường dẫn kit teardown: điền khoá teardown trong cau-hinh.toml ở gốc repo.');
const FONTS = path.resolve(HERE, '../../fonts');
const [name, ...rest] = process.argv.slice(2);
if (!name) {
  console.error('dùng: node dung.mjs <tên-cơ-cấu> [--video [--fps 60]] [--still <giây>]');
  process.exit(1);
}
const dir = path.resolve(HERE, name);
if (!fs.existsSync(path.join(dir, 'main.js'))) throw new Error(`Không có ${dir}/main.js`);
if (!fs.existsSync(path.join(KIT, 'sims/build.mjs'))) throw new Error(`Không thấy kit teardown ở ${KIT}`);

const run = (args) => {
  const r = spawnSync(process.execPath, args, {stdio: 'inherit'});
  if (r.status !== 0) throw new Error(`Lệnh lỗi: node ${args.join(' ')}`);
};
run([path.join(KIT, 'sims/build.mjs'), dir]);
// Chữ tiếng Việt: kit chỉ nhúng font latin, style.css của cơ cấu đọc Be Vietnam Pro đặt cạnh trang.
const dist = path.resolve('teardown-out/dist');
for (const f of ['BeVietnamPro-SemiBold.ttf', 'BeVietnamPro-Regular.ttf']) fs.copyFileSync(path.join(FONTS, f), path.join(dist, f));

const opt = (k, d) => (rest.includes(`--${k}`) ? rest[rest.indexOf(`--${k}`) + 1] : d);
const cap = [path.join(KIT, 'sims/capture.mjs'), name, '--size', '1600x900', '--dpr', '1.2'];
if (rest.includes('--video')) run([...cap, '--fps', opt('fps', '30'), '--out', `teardown-out/${name}.mp4`]);
else if (rest.includes('--still')) run([...cap, '--still', opt('still'), '--out', `teardown-out/${name}-${opt('still')}.png`]);
else run([...cap, '--stills', 'beats', '--timeline', path.join(dir, 'timeline.json'), '--cols', '4', '--out', `teardown-out/${name}-soat.png`]);
