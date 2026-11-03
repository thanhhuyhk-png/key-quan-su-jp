// Test cho dung-trang.mjs. Chạy: node --test tools/kit/
// Phần thuần (đối số, TOML, tên still, lệnh ffmpeg, dò Chrome) + một test tích hợp dựng trang thử tự sinh.
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, readdirSync, existsSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { execFileSync, spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import {
  parseArgs, readToml, stillName, ffmpegArgs, findRepoRoot, resolveChrome, parseSize, sheetArgs, frameRange, kiemNode,
} from './dung-trang.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const SCRIPT = join(HERE, 'dung-trang.mjs');

// ---------- phần thuần ----------

test('parseArgs: dựng mp4', () => {
  const a = parseArgs(['trang.html', '--out', 'x.mp4', '--fps', '24', '--force']);
  assert.equal(a.page, 'trang.html');
  assert.equal(a.out, 'x.mp4');
  assert.equal(a.fps, 24);
  assert.equal(a.force, true);
  assert.equal(a.transparent, false);
  assert.equal(a.stills, null);
});

test('parseArgs: mặc định fps 30, đường dẫn có dấu cách và tiếng Việt', () => {
  const a = parseArgs(['tập 1/a b.html']);
  assert.equal(a.fps, 30);
  assert.equal(a.page, 'tập 1/a b.html');
});

test('parseArgs: stills, data, trong suốt, chrome, phần mềm', () => {
  const s = parseArgs(['t.html', '--stills', '0.5,1.2', '--out-dir', 'd', '--transparent']);
  assert.deepEqual(s.stills, [0.5, 1.2]);
  assert.equal(s.outDir, 'd');
  assert.equal(s.transparent, true);
  const d = parseArgs(['t.html', '--data', 'TYPING', '--out', 'x.json', '--json']);
  assert.equal(d.data, 'TYPING');
  assert.equal(d.json, true);
  const c = parseArgs(['t.html', '--chrome', 'C:/c.exe', '--phan-mem', '--kiem-webgl']);
  assert.equal(c.chrome, 'C:/c.exe');
  assert.equal(c.phanMem, true);
  assert.equal(c.kiemWebgl, true);
});

test('parseArgs: lỗi đối số', () => {
  assert.throws(() => parseArgs([]), /trang/i);
  assert.throws(() => parseArgs(['t.html', '--fps', '0']), /fps/);
  assert.throws(() => parseArgs(['t.html', '--fps', '999']), /fps/);
  assert.throws(() => parseArgs(['t.html', '--stills', 'a,b']), /stills/);
  assert.throws(() => parseArgs(['t.html', '--stills', '-1']), /stills/);
  assert.throws(() => parseArgs(['t.html', '--data', '1bad']), /data/);
  assert.throws(() => parseArgs(['t.html', '--stills', '1', '--data', 'X']), /cùng lúc|một/);
  assert.throws(() => parseArgs(['t.html', '--khong-co']), /không biết|không hỗ trợ/i);
});

test('parseArgs: --kiem-webgl không cần trang', () => {
  const a = parseArgs(['--kiem-webgl']);
  assert.equal(a.kiemWebgl, true);
  assert.equal(a.page, null);
});

test('parseSize: chuỗi, mảng, đối tượng; lẻ hoặc nhỏ là lỗi', () => {
  assert.deepEqual(parseSize('1920x1080'), [1920, 1080]);
  assert.deepEqual(parseSize([320, 180]), [320, 180]);
  assert.deepEqual(parseSize({ width: 640, height: 360 }), [640, 360]);
  assert.throws(() => parseSize('1921x1080'), /chẵn/);
  assert.throws(() => parseSize('8x8'), /16/);
  assert.throws(() => parseSize('abc'), /SIZE/);
});

test('readToml: BOM, chú thích, nhóm, nháy đơn/đôi', () => {
  const t = readToml('\uFEFF# chú thích\n[duong_dan]\noutput = "D:/x y"  # ghi chú\nchrome = \'C:/c d/chrome.exe\'\n\n[khac]\nchrome = "sai"\n');
  assert.equal(t.duong_dan.output, 'D:/x y');
  assert.equal(t.duong_dan.chrome, 'C:/c d/chrome.exe');
  assert.equal(t.khac.chrome, 'sai');
});

test('readToml: dấu # trong chuỗi không phải chú thích', () => {
  const t = readToml('[duong_dan]\nchrome = "C:/a#b/chrome.exe"\n');
  assert.equal(t.duong_dan.chrome, 'C:/a#b/chrome.exe');
});

test('stillName: đúng mẫu ReelCrew', () => {
  assert.equal(stillName(0.5, false), 'still-0000.50s.jpg');
  assert.equal(stillName(1.2, false), 'still-0001.20s.jpg');
  assert.equal(stillName(12, true), 'still-0012.00s.png');
  assert.equal(stillName(123.456, false), 'still-0123.46s.jpg');
});

test('parseArgs + frameRange: --from/--to dựng một khúc như bản cũ (khung round(from·fps) … trước round(to·fps))', () => {
  const a = parseArgs(['p.html', '--out', 'x.mp4', '--fps', '24', '--from', '1.5', '--to', '3']);
  assert.equal(a.from, 1.5); assert.equal(a.to, 3);
  assert.deepEqual(frameRange(10, 24, 1.5, 3), { first: 36, last: 72 });
  assert.deepEqual(frameRange(10, 24, 0, null), { first: 0, last: 240 });
  assert.deepEqual(frameRange(2, 24, 1, 9), { first: 24, last: 48 }, 'to vượt thời lượng thì cắt về cuối trang');
  assert.throws(() => frameRange(2, 24, 2, 3), /khúc/);
  assert.throws(() => parseArgs(['p.html', '--from', '-1']), /--from/);
  assert.throws(() => parseArgs(['p.html', '--stills', '1', '--from', '1']), /--from/);
});

test('sheetArgs: ghép các still thành một dải ngang rộng 640 mỗi ảnh', () => {
  const a = sheetArgs(['a.jpg', 'b.jpg', 'c.png'], 'd/sheet.jpg');
  assert.deepEqual(a.slice(0, 2), ['-y', '-v']);
  assert.deepEqual(a.filter((x, i) => a[i - 1] === '-i'), ['a.jpg', 'b.jpg', 'c.png']);
  const f = a[a.indexOf('-filter_complex') + 1];
  assert.match(f, /\[0:v\]scale=640:-2\[s0\]/);
  assert.match(f, /\[s0\]\[s1\]\[s2\]hstack=inputs=3\[v\]/);
  assert.equal(a.at(-1), 'd/sheet.jpg');
  const mot = sheetArgs(['a.jpg'], 's.jpg');
  assert.match(mot[mot.indexOf('-filter_complex') + 1], /\[0:v\]scale=640:-2\[v\]$/);
});

test('ffmpegArgs: mp4 gắn bt709, x264 crf 18, faststart', () => {
  const a = ffmpegArgs({ fps: 24, transparent: false, out: 'o.mp4' }).join(' ');
  assert.match(a, /-f image2pipe/);
  assert.match(a, /-framerate 24/);
  assert.match(a, /-c:v mjpeg/);
  assert.match(a, /out_color_matrix=bt709/);
  assert.match(a, /-c:v libx264 -preset medium -crf 18/);
  assert.match(a, /-pix_fmt yuv420p/);
  assert.match(a, /-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv/);
  assert.match(a, /-movflags \+faststart/);
  assert.ok(a.endsWith('o.mp4'));
});

test('ffmpegArgs: mov prores 4444 alpha từ png', () => {
  const a = ffmpegArgs({ fps: 30, transparent: true, out: 'o.mov' }).join(' ');
  assert.match(a, /-c:v png/);
  assert.match(a, /-c:v prores_ks -profile:v 4444/);
  assert.match(a, /-pix_fmt yuva444p10le/);
  assert.doesNotMatch(a, /libx264/);
});

test('findRepoRoot: đi lên tới thư mục có cau-hinh.mau.toml', () => {
  const root = mkdtempSync(join(tmpdir(), 'goha-root-'));
  try {
    writeFileSync(join(root, 'cau-hinh.mau.toml'), '');
    mkdirSync(join(root, 'a', 'b'), { recursive: true });
    assert.equal(findRepoRoot(join(root, 'a', 'b')), root);
    assert.equal(findRepoRoot(join(tmpdir(), 'khong-co-goc-nao-ca-' + Date.now())), null);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test('resolveChrome: thứ tự cờ > biến môi trường > toml > dò', () => {
  const root = mkdtempSync(join(tmpdir(), 'goha-chrome-'));
  try {
    writeFileSync(join(root, 'cau-hinh.mau.toml'), '');
    writeFileSync(join(root, 'cau-hinh.toml'), '\uFEFF[duong_dan]\nchrome = "T:/toml.exe"\n');
    const all = () => true;
    assert.equal(resolveChrome({ flag: 'F:/flag.exe', env: { GOHA_CHROME: 'E:/env.exe' }, root, exists: all }), 'F:/flag.exe');
    assert.equal(resolveChrome({ env: { GOHA_CHROME: 'E:/env.exe' }, root, exists: all }), 'E:/env.exe');
    assert.equal(resolveChrome({ env: {}, root, exists: all }), 'T:/toml.exe');
    // toml trỏ tệp không tồn tại -> rơi xuống dò theo ProgramFiles
    const found = resolveChrome({
      env: { ProgramFiles: 'P:/PF' }, root,
      exists: (p) => p === 'P:/PF/Google/Chrome/Application/chrome.exe',
    });
    assert.equal(found, 'P:/PF/Google/Chrome/Application/chrome.exe');
    assert.throws(() => resolveChrome({ env: {}, root, exists: () => false }), /GOHA_CHROME|cau-hinh/);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

// ---------- tích hợp (cần Chrome + ffmpeg + ffprobe thật) ----------

function probe(file, entries) {
  const out = execFileSync('ffprobe', ['-v', 'error', '-count_frames', '-select_streams', 'v:0',
    '-show_entries', `stream=${entries}`, '-of', 'json', file], { encoding: 'utf8' });
  return JSON.parse(out).streams[0];
}

const PAGE = `<!doctype html><meta charset="utf-8"><title>thử</title>
<body style="margin:0;background:transparent"><canvas id="c" width="320" height="180"></canvas>
<script>
window.READY = false;
window.SIZE = '320x180';
window.DURATION = 0.5;
window.TYPING = [{ at: 0.1, ch: 'a' }];
const ctx = document.getElementById('c').getContext('2d');
window.renderFrame = async (t) => {
  ctx.clearRect(0, 0, 320, 180);
  if (!window.__opaque) { /* nền trong suốt */ } else { ctx.fillStyle = '#204060'; ctx.fillRect(0, 0, 320, 180); }
  ctx.fillStyle = '#ff0000';
  ctx.fillRect(100 + Math.round(t * 100), 60, 60, 60);
};
window.READY = true;
</script>`;

function chay(args, opts = {}) {
  return spawnSync(process.execPath, [SCRIPT, ...args], { encoding: 'utf8', timeout: 120000, ...opts });
}

test('tích hợp: mp4 + mov + stills + data từ trang thử', async (t) => {
  const dir = mkdtempSync(join(tmpdir(), 'goha trang thử '));
  try {
    const chk = chay(['--kiem-webgl']);
    if (/không tìm thấy Chrome/i.test(chk.stderr)) { t.skip('máy không có Chrome'); return; }

    const page = join(dir, 'trang thử.html');
    writeFileSync(page, PAGE.replace('window.READY = true;', 'window.__opaque = true; window.READY = true;'));
    const pageAlpha = join(dir, 'alpha.html');
    writeFileSync(pageAlpha, PAGE);

    // mp4
    const mp4 = join(dir, 'ra.mp4');
    const r1 = chay([page, '--out', mp4, '--fps', '24']);
    assert.equal(r1.status, 0, r1.stderr);
    assert.equal(r1.stdout.trim(), mp4);
    const v = probe(mp4, 'codec_name,width,height,r_frame_rate,pix_fmt,nb_read_frames,color_space,color_primaries,color_transfer,color_range');
    assert.equal(v.codec_name, 'h264');
    assert.equal(v.width, 320); assert.equal(v.height, 180);
    assert.equal(v.r_frame_rate, '24/1');
    assert.equal(v.pix_fmt, 'yuv420p');
    assert.equal(v.nb_read_frames, '12');
    assert.equal(v.color_space, 'bt709'); assert.equal(v.color_primaries, 'bt709');
    assert.equal(v.color_transfer, 'bt709'); assert.equal(v.color_range, 'tv');

    // không --force thì không đè
    const r2 = chay([page, '--out', mp4, '--fps', '24']);
    assert.notEqual(r2.status, 0);
    assert.match(r2.stderr, /force/);
    const r3 = chay([page, '--out', mp4, '--fps', '24', '--force']);
    assert.equal(r3.status, 0, r3.stderr);
    assert.deepEqual(readdirSync(dir).filter((f) => f.includes('.tmp-') || f.startsWith('.render')), []);

    // mov trong suốt
    const mov = join(dir, 'ra.mov');
    const r4 = chay([pageAlpha, '--out', mov, '--fps', '24', '--transparent']);
    assert.equal(r4.status, 0, r4.stderr);
    const m = probe(mov, 'codec_name,pix_fmt,width,height,nb_read_frames');
    assert.equal(m.codec_name, 'prores');
    assert.match(m.pix_fmt, /^yuva444p1[02]le$/); // giải mã ProRes 4444 có thể báo 12 bit
    assert.equal(m.nb_read_frames, '12');
    const alpha = execFileSync('ffmpeg', ['-v', 'error', '-i', mov, '-vf', 'alphaextract,format=gray', '-frames:v', '1', '-f', 'rawvideo', '-'], { maxBuffer: 1 << 24 });
    assert.equal(alpha.length, 320 * 180);
    assert.equal(alpha[0], 0, 'góc phải trong suốt');
    assert.equal(alpha[90 * 320 + 130], 255, 'hình đỏ phải đặc');

    // stills jpg (nền đặc) và png (trong suốt)
    const sd = join(dir, 'st');
    const r5 = chay([page, '--stills', '0.1,0.3', '--out-dir', sd]);
    assert.equal(r5.status, 0, r5.stderr);
    assert.deepEqual(readdirSync(sd).sort(), ['sheet.jpg', 'still-0000.10s.jpg', 'still-0000.30s.jpg']);
    assert.deepEqual([...readFileSync(join(sd, 'still-0000.10s.jpg')).subarray(0, 2)], [0xff, 0xd8]);
    const sp = join(dir, 'sp');
    const r6 = chay([pageAlpha, '--stills', '0.2', '--out-dir', sp, '--transparent']);
    assert.equal(r6.status, 0, r6.stderr);
    assert.deepEqual(readdirSync(sp).sort(), ['sheet.jpg', 'still-0000.20s.png']);
    assert.equal(readFileSync(join(sp, 'still-0000.20s.png')).subarray(1, 4).toString(), 'PNG');
    // mốc vượt thời lượng
    const r7 = chay([page, '--stills', '9', '--out-dir', sd]);
    assert.notEqual(r7.status, 0);

    // data
    const js = join(dir, 'd.json');
    const r8 = chay([page, '--data', 'TYPING', '--out', js]);
    assert.equal(r8.status, 0, r8.stderr);
    assert.deepEqual(JSON.parse(readFileSync(js, 'utf8')), [{ at: 0.1, ch: 'a' }]);
    const r9 = chay([page, '--data', 'KHONG_CO', '--out', join(dir, 'e.json')]);
    assert.notEqual(r9.status, 0);
    assert.match(r9.stderr, /KHONG_CO/);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('tích hợp: báo rõ tệp hỏng khi trang không READY, và lỗi khung', async (t) => {
  const dir = mkdtempSync(join(tmpdir(), 'goha loi '));
  try {
    const chk = chay(['--kiem-webgl']);
    if (/không tìm thấy Chrome/i.test(chk.stderr)) { t.skip('máy không có Chrome'); return; }
    // ảnh thiếu + ngoại lệ trong renderFrame ở t > 0.2
    const page = join(dir, 'hong.html');
    writeFileSync(page, `<!doctype html><body><img src="khong-co.png">
<script>
window.SIZE='320x180'; window.DURATION=0.5;
window.renderFrame = (t) => { if (t > 0.2) throw new Error('vo roi'); };
window.READY = true;
</script>`);
    const r = chay([page, '--out', join(dir, 'x.mp4'), '--fps', '10', '--force']);
    assert.notEqual(r.status, 0);
    assert.match(r.stderr, /vo roi/);
    assert.match(r.stderr, /khung \d+/);
    assert.equal(existsSync(join(dir, 'x.mp4')), false);

    const page2 = join(dir, 'chua-san-sang.html');
    writeFileSync(page2, `<!doctype html><body><img src="anh-thieu.png"><script>
window.SIZE='320x180'; window.DURATION=1; window.renderFrame=()=>{}; window.READY=false;</script>`);
    const r2 = chay([page2, '--out', join(dir, 'y.mp4'), '--force'], { env: { ...process.env, GOHA_READY_MS: '1500' } });
    assert.notEqual(r2.status, 0);
    assert.match(r2.stderr, /anh-thieu\.png/);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

// ---------- sửa theo soát lại ----------

test('Chrome sai đường dẫn: báo ngay nguyên nhân thật, không treo', () => {
  const t0 = Date.now();
  const r = spawnSync(process.execPath, [SCRIPT, '--kiem-webgl', '--chrome', join(tmpdir(), 'khong-co-chrome', 'chrome.exe')],
    { encoding: 'utf8', timeout: 30000 });
  assert.notEqual(r.status, 0);
  assert.match(r.stderr, /Không chạy được Chrome/);
  assert.ok(Date.now() - t0 < 8000, `mất ${Date.now() - t0} ms`);
});

test('readToml: dấu \\ lạ trong chuỗi nháy kép được giữ nguyên (đường dẫn Windows)', () => {
  const t = readToml('[duong_dan]\nchrome = "C:\\Program Files\\Google\\chrome.exe"\nghi = "a\\nb"\n');
  assert.equal(t.duong_dan.chrome, 'C:\\Program Files\\Google\\chrome.exe');
  assert.equal(t.duong_dan.ghi, 'a\nb');
});

test('--stills cùng --out: báo lỗi chỉ sang --out-dir', () => {
  const dir = mkdtempSync(join(tmpdir(), 'goha stills '));
  try {
    const page = join(dir, 't.html');
    writeFileSync(page, '<!doctype html><body>x');
    const r = spawnSync(process.execPath, [SCRIPT, page, '--stills', '0.5', '--out', join(dir, 'a.png')], { encoding: 'utf8', timeout: 30000 });
    assert.notEqual(r.status, 0);
    assert.match(r.stderr, /--out-dir/);
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test('kiemNode: thiếu WebSocket toàn cục thì báo cần Node 22', () => {
  assert.throws(() => kiemNode(false, '20.11.0'), /Node 22/);
  assert.doesNotThrow(() => kiemNode(true, '22.1.0'));
});
