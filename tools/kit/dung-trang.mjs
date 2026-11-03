#!/usr/bin/env node
// dung-trang.mjs — biến trang HTML (hợp đồng template/lib/common.js: window.SIZE, DURATION, renderFrame(t), READY)
// thành mp4, mov trong suốt, ảnh tĩnh hoặc JSON. Thay bước dựng trang của CLI cũ, chạy được trên máy hội viên.
// Chỉ cần Node >= 22 (WebSocket toàn cục), Chrome/Edge và ffmpeg. Không gói npm ngoài.
//
//   node tools/kit/dung-trang.mjs <trang.html> --out x.mp4 --fps 24 [--force]
//   node tools/kit/dung-trang.mjs <trang.html> --out x.mov --transparent [--force]
//   node tools/kit/dung-trang.mjs <trang.html> --stills 0.5,1.2 --out-dir d [--transparent]
//   node tools/kit/dung-trang.mjs <trang.html> --data TYPING --out x.json
//   node tools/kit/dung-trang.mjs --kiem-webgl [--phan-mem] [--chrome đường\dẫn]
// stdout chỉ in đường dẫn kết quả (hoặc JSON khi --json); tiến độ và lỗi ra stderr.

import { spawn, spawnSync } from 'node:child_process';
import {
  existsSync, readFileSync, writeFileSync, mkdirSync, mkdtempSync, readdirSync,
  rmSync, renameSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname, resolve, basename, extname, parse as parsePath } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { setTimeout as sleep } from 'node:timers/promises';
import { once } from 'node:events';

const READY_MS = Number(process.env.GOHA_READY_MS) || 30000;
const CDP_MS = 60000;

// ---------------------------------------------------------------- phần thuần

export function parseArgs(argv) {
  const a = {
    page: null, out: null, fps: 30, force: false, transparent: false, stills: null, outDir: null,
    data: null, json: false, kiemWebgl: false, phanMem: false, chrome: null, help: false, from: 0, to: null,
  };
  const needVal = (i, flag) => {
    if (i + 1 >= argv.length) throw new Error(`Cờ ${flag} cần một giá trị.`);
    return argv[i + 1];
  };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i];
    switch (k) {
      case '--out': a.out = needVal(i++, k); break;
      case '--out-dir': a.outDir = needVal(i++, k); break;
      case '--fps': {
        const v = Number(needVal(i++, k));
        if (!Number.isFinite(v) || v < 1 || v > 120) throw new Error('--fps phải từ 1 đến 120.');
        a.fps = v; break;
      }
      case '--stills': {
        const parts = needVal(i++, k).split(',').map((s) => s.trim());
        const nums = parts.map(Number);
        if (!parts.length || parts.some((s) => s === '') || nums.some((n) => !Number.isFinite(n) || n < 0)) {
          throw new Error('--stills cần danh sách giây không âm, cách nhau dấu phẩy (vd 0.5,1.2).');
        }
        a.stills = nums; break;
      }
      case '--data': {
        const v = needVal(i++, k);
        if (!/^[A-Za-z_$][\w$]*$/.test(v)) throw new Error(`--data: tên biến "${v}" không hợp lệ.`);
        a.data = v; break;
      }
      case '--from': case '--to': {
        const v = Number(needVal(i++, k));
        if (!Number.isFinite(v) || v < 0) throw new Error(`${k} phải là số giây không âm.`);
        a[k.slice(2)] = v; break;
      }
      case '--chrome': a.chrome = needVal(i++, k); break;
      case '--force': a.force = true; break;
      case '--transparent': a.transparent = true; break;
      case '--json': a.json = true; break;
      case '--kiem-webgl': a.kiemWebgl = true; break;
      case '--phan-mem': a.phanMem = true; break;
      case '--help': case '-h': a.help = true; break;
      default:
        if (k.startsWith('--')) throw new Error(`Cờ không biết/không hỗ trợ: ${k}`);
        if (a.page !== null) throw new Error(`Chỉ nhận một trang, thừa: ${k}`);
        a.page = k;
    }
  }
  if (a.stills && a.data) throw new Error('--stills và --data không dùng cùng lúc, chọn một.');
  if ((a.from || a.to !== null) && (a.stills || a.data)) throw new Error('--from/--to chỉ dùng khi dựng video (--out).');
  if (!a.page && !a.kiemWebgl && !a.help) throw new Error('Thiếu đường dẫn trang HTML.');
  return a;
}

export function parseSize(v) {
  let w; let h;
  if (typeof v === 'string') {
    const m = /^\s*(\d+)\s*[x×]\s*(\d+)\s*$/i.exec(v);
    if (!m) throw new Error(`window.SIZE "${v}" không đúng dạng WxH.`);
    [w, h] = [Number(m[1]), Number(m[2])];
  } else if (Array.isArray(v) && v.length === 2) {
    [w, h] = v.map(Number);
  } else if (v && typeof v === 'object') {
    [w, h] = [Number(v.width), Number(v.height)];
  } else throw new Error('window.SIZE thiếu hoặc sai dạng (cần "WxH").');
  if (!Number.isInteger(w) || !Number.isInteger(h)) throw new Error('window.SIZE phải là số nguyên.');
  if (w < 16 || h < 16) throw new Error(`window.SIZE ${w}x${h}: cạnh nhỏ nhất là 16.`);
  if (w % 2 || h % 2) throw new Error(`window.SIZE ${w}x${h}: hai cạnh phải chẵn (x264/ProRes).`);
  return [w, h];
}

// TOML phẳng: [nhóm] rồi khoá = "chuỗi". Chịu BOM, chú thích #, nháy đơn/đôi.
export function readToml(text) {
  const out = {};
  let cur = out;
  for (const raw of text.replace(/^\uFEFF/, '').split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith('#')) continue;
    const sec = /^\[([^\]]+)\]\s*(#.*)?$/.exec(line);
    if (sec) { cur = out[sec[1].trim()] ??= {}; continue; }
    const kv = /^([A-Za-z0-9_.-]+)\s*=\s*(.*)$/.exec(line);
    if (!kv) continue;
    const rest = kv[2];
    let val;
    const q = rest[0];
    if (q === '"' || q === "'") {
      let s = '';
      let j = 1;
      for (; j < rest.length && rest[j] !== q; j++) {
        if (q === '"' && rest[j] === '\\' && j + 1 < rest.length) {
          const n = rest[++j];
          s += n === 'n' ? '\n' : n === 't' ? '\t' : (n === '\\' || n === '"') ? n : '\\' + n; // thoát lạ (đường dẫn Windows): giữ cả dấu \
        } else s += rest[j];
      }
      val = s;
    } else val = rest.replace(/\s+#.*$/, '').trim();
    cur[kv[1]] = val;
  }
  return out;
}

/** Đối số ffmpeg ghép các still thành một ảnh soi ngang (mỗi ảnh rộng 640), như sheet.jpg của bản cũ. */
/** Khúc khung cần dựng: từ round(from·fps) tới trước round(min(to, thời lượng)·fps); khung f ở giây f/fps. */
export function frameRange(duration, fps, from = 0, to = null) {
  const end = Math.min(to ?? duration, duration);
  if (!(end > from)) throw new Error(`Không có gì để dựng trong khúc ${from}–${end} s (trang dài ${duration} s).`);
  return { first: Math.round(from * fps), last: Math.round(end * fps) };
}

export function sheetArgs(files, out) {
  const scaled = files.map((_, i) => `[${i}:v]scale=640:-2[${files.length > 1 ? `s${i}` : 'v'}]`);
  const stack = files.length > 1 ? `;${files.map((_, i) => `[s${i}]`).join('')}hstack=inputs=${files.length}[v]` : '';
  return ['-y', '-v', 'error', ...files.flatMap((f) => ['-i', f]),
    '-filter_complex', scaled.join(';') + stack, '-map', '[v]', '-frames:v', '1', '-q:v', '3', out];
}

export function stillName(t, png) {
  return `still-${t.toFixed(2).padStart(7, '0')}s.${png ? 'png' : 'jpg'}`;
}

export function ffmpegArgs({ fps, transparent, out }) {
  const head = ['-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps)];
  const tags = ['-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-color_range', 'tv'];
  if (transparent) {
    return [...head, '-c:v', 'png', '-i', '-',
      '-vf', 'scale=in_color_matrix=bt601:out_color_matrix=bt709:out_range=tv:flags=bicubic+accurate_rnd+full_chroma_int,format=yuva444p10le,setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv',
      '-c:v', 'prores_ks', '-profile:v', '4444', '-pix_fmt', 'yuva444p10le', ...tags, '-r', String(fps), out];
  }
  return [...head, '-c:v', 'mjpeg', '-i', '-',
    '-vf', 'scale=in_range=pc:in_color_matrix=bt601:out_range=tv:out_color_matrix=bt709:flags=bicubic+accurate_rnd+full_chroma_int,format=yuv420p,setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', ...tags,
    '-movflags', '+faststart', '-r', String(fps), out];
}

// Gốc repo = thư mục cha gần nhất có cau-hinh.mau.toml.
export function findRepoRoot(start) {
  let d = resolve(start);
  for (;;) {
    if (existsSync(join(d, 'cau-hinh.mau.toml'))) return d;
    const up = dirname(d);
    if (up === d) return null;
    d = up;
  }
}

const HANG_CHROME = [
  ['Google', 'Chrome', 'chrome.exe'],
  ['Microsoft', 'Edge', 'msedge.exe'],
  ['BraveSoftware', 'Brave-Browser', 'brave.exe'],
  ['Chromium', null, 'chrome.exe'],
];

export function resolveChrome({ flag, env = process.env, root, exists = existsSync } = {}) {
  if (flag) return flag;
  if (env.GOHA_CHROME) return env.GOHA_CHROME;
  if (root) {
    const f = join(root, 'cau-hinh.toml');
    if (exists(f)) {
      try {
        const c = readToml(readFileSync(f, 'utf8')).duong_dan?.chrome;
        if (c && exists(c)) return c;
      } catch { /* bỏ qua, dò tiếp */ }
    }
  }
  const roots = [env.ProgramFiles, env['ProgramFiles(x86)'], env.LOCALAPPDATA].filter(Boolean);
  for (const r of roots) {
    for (const [hang, sp, exe] of HANG_CHROME) {
      const p = [r, hang, sp, 'Application', exe].filter(Boolean).join('/');
      if (exists(p)) return p;
    }
  }
  throw new Error('Không tìm thấy Chrome hoặc Edge. Cài Chrome, rồi chỉ đường dẫn bằng một trong ba cách: '
    + 'cờ --chrome, biến môi trường GOHA_CHROME, hoặc khoá chrome trong [duong_dan] của cau-hinh.toml.');
}

// ---------------------------------------------------------------- Chrome + CDP

const log = (s) => process.stderr.write(s);

function killTree(child) {
  if (!child || child.exitCode !== null || !child.pid) return;
  if (process.platform === 'win32') spawnSync('taskkill', ['/pid', String(child.pid), '/T', '/F'], { stdio: 'ignore', windowsHide: true });
  else child.kill('SIGKILL');
}

async function rmRetry(dir) {
  for (let i = 0; i < 8; i++) {
    try { rmSync(dir, { recursive: true, force: true }); return; } catch { await sleep(250); }
  }
}

class Session {
  constructor() {
    this.pageErrors = []; this.consoleErrors = []; this.failed = []; this.pending = new Map();
    this.waiters = []; this.id = 0; this.reqUrl = new Map();
  }

  async launch({ chromePath, width, height, phanMem }) {
    this.profile = mkdtempSync(join(tmpdir(), 'goha-chrome-'));
    const flags = [
      '--headless=new', '--remote-debugging-port=0', `--user-data-dir=${this.profile}`,
      '--no-first-run', '--no-default-browser-check', '--hide-scrollbars', '--allow-file-access-from-files',
      '--autoplay-policy=no-user-gesture-required', '--disable-background-timer-throttling',
      '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows',
      '--disable-features=CalculateNativeWinOcclusion', '--disable-ipc-flooding-protection',
      '--force-device-scale-factor=1', `--window-size=${Math.max(width, 400)},${Math.max(height, 400)}`,
    ];
    if (process.platform === 'linux') flags.push('--disable-dev-shm-usage');
    if (phanMem) flags.push('--use-angle=swiftshader', '--enable-unsafe-swiftshader');
    flags.push('about:blank');
    this.child = spawn(chromePath, flags, {
      stdio: 'ignore', windowsHide: true,
      env: { ...process.env, TMP: this.profile, TEMP: this.profile },
    });
    this.exited = false;
    this.child.on('exit', () => { this.exited = true; this.failAll(new Error('Chrome đã thoát giữa chừng.')); });
    this.child.on('error', (e) => { // ENOENT, EACCES: Node không phát 'exit', nên đánh dấu đã chết để vòng chờ dừng ngay
      this.exited = true;
      this.launchError = new Error(`Không chạy được Chrome (${chromePath}): ${e.message}`);
      this.failAll(this.launchError);
    });

    const portFile = join(this.profile, 'DevToolsActivePort');
    let port = null;
    for (let i = 0; i < 600 && !port; i++) {
      if (this.launchError) throw this.launchError;
      if (this.exited) throw new Error('Chrome thoát ngay khi khởi động. Thử --phan-mem hoặc kiểm đường dẫn Chrome.');
      if (existsSync(portFile)) {
        const l = readFileSync(portFile, 'utf8').split(/\r?\n/)[0].trim();
        if (/^\d+$/.test(l)) port = l;
      }
      if (!port) await sleep(100);
    }
    if (!port) throw new Error('Chrome không mở cổng điều khiển trong 60 s.');
    let wsUrl = null;
    for (let i = 0; i < 100 && !wsUrl; i++) {
      try {
        const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
        wsUrl = list.find((x) => x.type === 'page')?.webSocketDebuggerUrl;
      } catch { /* chưa sẵn sàng */ }
      if (!wsUrl) await sleep(100);
    }
    if (!wsUrl) throw new Error('Không lấy được tab trang từ Chrome.');
    this.ws = new WebSocket(wsUrl);
    await new Promise((ok, no) => { this.ws.onopen = ok; this.ws.onerror = () => no(new Error('Không nối được CDP.')); });
    this.ws.onmessage = (ev) => this.onMessage(JSON.parse(ev.data));
    this.ws.onclose = () => this.failAll(new Error('Chrome đã đóng kết nối.'));
    await this.send('Page.enable');
    await this.send('Runtime.enable');
    await this.send('Network.enable');
  }

  failAll(err) {
    for (const p of this.pending.values()) { clearTimeout(p.timer); p.no(err); }
    this.pending.clear();
  }

  onMessage(m) {
    if (m.id) {
      const p = this.pending.get(m.id);
      if (!p) return;
      this.pending.delete(m.id); clearTimeout(p.timer);
      if (m.error) p.no(new Error(`CDP ${p.method}: ${m.error.message}`)); else p.ok(m.result);
      return;
    }
    const q = m.params || {};
    switch (m.method) {
      case 'Runtime.exceptionThrown': {
        const d = q.exceptionDetails || {};
        this.pageErrors.push(d.exception?.description || d.text || 'ngoại lệ không rõ');
        break;
      }
      case 'Runtime.consoleAPICalled':
        if (q.type === 'error') this.consoleErrors.push((q.args || []).map((x) => x.value ?? x.description ?? '').join(' '));
        break;
      case 'Network.requestWillBeSent': this.reqUrl.set(q.requestId, q.request.url); break;
      case 'Network.responseReceived':
        if (q.response.status >= 400) this.failed.push(`HTTP ${q.response.status}: ${q.response.url}`);
        break;
      case 'Network.loadingFailed':
        if (!q.canceled) this.failed.push(`${q.errorText}: ${this.reqUrl.get(q.requestId) || '(url không rõ)'}`);
        break;
      default: break;
    }
    this.waiters = this.waiters.filter((w) => (w.method === m.method ? (w.ok(q), false) : true));
  }

  send(method, params = {}) {
    return new Promise((ok, no) => {
      if (this.exited) return no(new Error('Chrome đã thoát.'));
      const id = ++this.id;
      const timer = setTimeout(() => { this.pending.delete(id); no(new Error(`Chrome không trả lời lệnh ${method} sau 60 s.`)); }, CDP_MS);
      this.pending.set(id, { ok, no, timer, method });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  waitEvent(method, ms) {
    return new Promise((ok) => {
      const t = setTimeout(() => ok(null), ms);
      this.waiters.push({ method, ok: (q) => { clearTimeout(t); ok(q); } });
    });
  }

  async evalJs(expression, awaitPromise = true) {
    const r = await this.send('Runtime.evaluate', { expression, awaitPromise, returnByValue: true });
    if (r.exceptionDetails) {
      const d = r.exceptionDetails;
      throw new Error(d.exception?.description || d.exception?.value || d.text || 'lỗi JavaScript');
    }
    return r.result?.value;
  }

  async setViewport(w, h, transparent) {
    await this.send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: 1, mobile: false });
    if (transparent) await this.send('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 0 } });
  }

  async close() {
    try { this.ws?.close(); } catch { /* đã đóng */ }
    killTree(this.child);
    if (this.profile) await rmRetry(this.profile);
  }

  report() {
    const cut = (arr) => [...new Set(arr)].slice(0, 5).map((s) => `    - ${String(s).split('\n')[0].slice(0, 300)}`).join('\n');
    const parts = [];
    if (this.failed.length) parts.push(`  Tài nguyên tải hỏng:\n${cut(this.failed)}`);
    if (this.pageErrors.length) parts.push(`  Ngoại lệ trong trang:\n${cut(this.pageErrors)}`);
    if (this.consoleErrors.length) parts.push(`  console.error:\n${cut(this.consoleErrors)}`);
    return parts.join('\n');
  }
}

// Mở trang, chờ load (tối đa 30 s, hết hạn thì đi tiếp), rồi chờ READY.
async function openPage(s, url) {
  s.pageErrors.length = 0; s.consoleErrors.length = 0; s.failed.length = 0;
  const loaded = s.waitEvent('Page.loadEventFired', 30000);
  const nav = await s.send('Page.navigate', { url });
  if (nav.errorText) throw new Error(`Không mở được trang: ${nav.errorText}`);
  await loaded;
  const deadline = Date.now() + READY_MS;
  for (;;) {
    let ready = false;
    try {
      ready = await s.evalJs('window.READY === undefined ? document.readyState === "complete" : window.READY === true', false);
    } catch { /* trang đang chuyển cảnh */ }
    if (ready) break;
    if (Date.now() > deadline) {
      const rep = s.report();
      throw new Error(`Trang không READY sau ${Math.round(READY_MS / 1000)} s.${rep ? `\n${rep}` : '\n  Không thấy lỗi nào được báo; kiểm window.READY trong trang.'}`);
    }
    await sleep(100);
  }
  if (s.pageErrors.length) throw new Error(`Trang báo lỗi khi tải:\n${s.report()}`);
}

async function pageInfo(s) {
  return s.evalJs(`({
    size: window.SIZE ?? (window.TIMELINE && window.TIMELINE.size) ?? null,
    duration: window.DURATION ?? window.DUR ?? (window.TIMELINE && (window.TIMELINE.total ?? window.TIMELINE.duration)) ?? null,
    hasFrame: typeof window.renderFrame === "function"
  })`, false);
}

// Vẽ khung tại t (renderFrame, 2 lượt rAF) rồi chụp. Trả Buffer.
async function captureAt(s, t, fmt, frameNo) {
  const where = frameNo === null ? `giây ${t}` : `khung ${frameNo} (giây ${t})`;
  let ret;
  try {
    ret = await s.evalJs(`(async()=>{const v=await window.renderFrame(${t});return typeof v==="string"&&v.startsWith("data:image/")?v:null})()`);
  } catch (e) {
    throw new Error(`renderFrame lỗi ở ${where}: ${e.message}`);
  }
  if (ret) return Buffer.from(ret.slice(ret.indexOf(',') + 1), 'base64');
  try {
    await s.evalJs('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r(0))))');
  } catch (e) { throw new Error(`Lỗi khi chờ vẽ ở ${where}: ${e.message}`); }
  if (s.pageErrors.length || s.consoleErrors.length) {
    throw new Error(`Trang báo lỗi ở ${where}:\n${s.report()}`);
  }
  const shot = await s.send('Page.captureScreenshot', {
    format: fmt, ...(fmt === 'jpeg' ? { quality: 92 } : {}), fromSurface: true, captureBeyondViewport: false,
  });
  if (!shot.data) throw new Error(`Chrome không trả ảnh ở ${where}.`);
  return Buffer.from(shot.data, 'base64');
}

// Mở trang, đọc SIZE/DURATION, đặt khung nhìn đúng cỡ và nạp lại nếu cỡ khác.
async function prepare(s, url, { needSize, transparent }) {
  await s.setViewport(1920, 1080, transparent);
  await openPage(s, url);
  const info = await pageInfo(s);
  if (!info.hasFrame) throw new Error('Trang thiếu hàm window.renderFrame(t).');
  let size = [1920, 1080];
  if (needSize) {
    size = parseSize(info.size);
    if (size[0] !== 1920 || size[1] !== 1080) {
      await s.setViewport(size[0], size[1], transparent);
      await openPage(s, url);
    }
  }
  return { size, duration: Number(info.duration) };
}

// ---------------------------------------------------------------- các chế độ

async function modeVideo(s, a, url) {
  const ext = a.transparent ? '.mov' : '.mp4';
  const dest = resolve(a.out ?? join(dirname(resolve(a.page)), parsePath(a.page).name + ext));
  if (extname(dest).toLowerCase() !== ext) {
    throw new Error(`Đuôi tệp ra phải là ${ext}${a.transparent ? ' khi dùng --transparent' : ' (dùng --transparent cho .mov)'}.`);
  }
  if (existsSync(dest) && !a.force) throw new Error(`${dest} đã có. Thêm --force để ghi đè.`);
  mkdirSync(dirname(dest), { recursive: true });

  const { size, duration } = await prepare(s, url, { needSize: true, transparent: a.transparent });
  if (!(duration > 0)) throw new Error('Trang thiếu window.DURATION (giây, > 0).');
  const { first, last } = frameRange(duration, a.fps, a.from, a.to);
  const total = last - first;
  if (total < 1) throw new Error('Thời lượng quá ngắn so với fps: không đủ một khung.');
  const fmt = a.transparent ? 'png' : 'jpeg';
  await captureAt(s, 0, 'jpeg', 0); // chụp bỏ: lần đầu hay đen

  const tmp = join(dirname(dest), `${parsePath(dest).name}.tmp-${process.pid}${ext}`);
  const ff = spawn(process.env.GOHA_FFMPEG || 'ffmpeg', ffmpegArgs({ fps: a.fps, transparent: a.transparent, out: tmp }), {
    stdio: ['pipe', 'ignore', 'pipe'], windowsHide: true,
  });
  let ffErr = '';
  ff.stderr.on('data', (d) => { ffErr = (ffErr + d).slice(-1500); });
  let ffDead = false;
  const ffDone = new Promise((ok) => ff.on('close', (code) => { ffDead = true; ok(code); }));
  ff.on('error', (e) => { ffErr = `Không chạy được ffmpeg: ${e.message}`; });
  ff.stdin.on('error', () => { /* ffmpeg thoát sớm, báo ở dưới */ });
  s.ffmpeg = ff;

  const t0 = Date.now();
  let lastLog = 0;
  try {
    for (let k = 0; k < total; k++) {
      const f = first + k;
      if (ffDead) throw new Error(`ffmpeg thoát giữa chừng ở khung ${f}:\n${ffErr.slice(-600)}`);
      const t = Math.round((f / a.fps) * 1e6) / 1e6;
      const buf = await captureAt(s, t, fmt, f);
      if (!ff.stdin.write(buf)) await once(ff.stdin, 'drain').catch(() => {});
      if (Date.now() - lastLog > 1000) {
        lastLog = Date.now();
        const fps = ((k + 1) / ((Date.now() - t0) / 1000)).toFixed(1);
        log(`\r  khung ${k + 1}/${total} (${fps} khung/giây)   `);
      }
    }
    ff.stdin.end();
    const code = await ffDone;
    if (code !== 0) throw new Error(`ffmpeg lỗi (mã ${code}):\n${ffErr.slice(-600)}`);
    renameSync(tmp, dest);
  } catch (e) {
    try { ff.stdin.destroy(); } catch { /* đã đóng */ }
    killTree(ff);
    await sleep(200);
    rmSync(tmp, { force: true });
    throw e;
  }
  const secs = (Date.now() - t0) / 1000;
  log(`\r  xong ${total} khung ${size[0]}x${size[1]} trong ${secs.toFixed(1)} s (${(total / secs).toFixed(1)} khung/giây)\n`);
  return { out: dest, frames: total, width: size[0], height: size[1], fps: a.fps, seconds: secs, framesPerSecond: total / secs };
}

async function modeStills(s, a, url) {
  const dir = resolve(a.outDir ?? join(dirname(resolve(a.page)), 'stills'));
  const { duration } = await prepare(s, url, { needSize: true, transparent: a.transparent });
  const over = a.stills.filter((t) => duration > 0 && t > duration);
  if (over.length) throw new Error(`Mốc ${over.join(', ')} vượt thời lượng trang (${duration} s).`);
  mkdirSync(dir, { recursive: true });
  for (const f of readdirSync(dir)) if (/^still-\d{4}\.\d\ds\.(jpg|png)$/.test(f)) rmSync(join(dir, f), { force: true });
  await captureAt(s, a.stills[0], 'jpeg', null); // chụp bỏ
  const files = [];
  for (const t of a.stills) {
    const buf = await captureAt(s, t, a.transparent ? 'png' : 'jpeg', null);
    const f = join(dir, stillName(t, a.transparent));
    writeFileSync(f, buf);
    files.push(f);
  }
  const sheet = join(dir, 'sheet.jpg');
  const r = spawnSync(process.env.GOHA_FFMPEG || 'ffmpeg', sheetArgs(files, sheet), { encoding: 'utf8', windowsHide: true });
  if (r.status !== 0) throw new Error(`Không ghép được sheet.jpg: ${(r.stderr || r.error?.message || '').trim().split(/\r?\n/).slice(-3).join(' ')}`);
  return { files, sheet };
}

async function modeData(s, a, url) {
  if (!a.out) throw new Error('--data cần --out <tệp.json>.');
  const dest = resolve(a.out);
  if (existsSync(dest) && !a.force) throw new Error(`${dest} đã có. Thêm --force để ghi đè.`);
  await prepare(s, url, { needSize: false, transparent: false });
  const json = await s.evalJs(`JSON.stringify(window[${JSON.stringify(a.data)}] ?? null)`, false);
  if (json === 'null') throw new Error(`Trang không có biến window.${a.data} (hoặc rỗng) sau READY.`);
  mkdirSync(dirname(dest), { recursive: true });
  writeFileSync(dest, JSON.stringify(JSON.parse(json), null, 1));
  return { out: dest };
}

async function modeWebgl(s, a) {
  await s.setViewport(400, 400, false);
  const r = await s.evalJs(`(() => {
    const c = document.createElement("canvas");
    const gl = c.getContext("webgl2") || c.getContext("webgl");
    if (!gl) return { webgl: false };
    const x = gl.getExtension("WEBGL_debug_renderer_info");
    return { webgl: true, version: gl.getParameter(gl.VERSION),
      renderer: x ? gl.getParameter(x.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
      vendor: x ? gl.getParameter(x.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR) };
  })()`, false);
  r.loai = !r.webgl ? 'khong-co' : /swiftshader|llvmpipe|software|basic render/i.test(r.renderer) ? 'phan-mem' : 'gpu';
  r.phanMemBat = a.phanMem;
  return r;
}

// ---------------------------------------------------------------- main

const HELP = `Dùng: node dung-trang.mjs <trang.html> --out x.mp4 [--fps 30] [--from s] [--to s] [--force] [--transparent]
       node dung-trang.mjs <trang.html> --stills 0.5,1.2 [--out-dir d] [--transparent]
       node dung-trang.mjs <trang.html> --data TEN --out x.json [--force]
       node dung-trang.mjs --kiem-webgl [--phan-mem]
Chung: --chrome <exe> · --json (stdout là JSON) · --phan-mem (WebGL bằng SwiftShader, máy không GPU)`;

/** Node 22 trở lên mới có WebSocket toàn cục; Node cũ chạy Chrome xong mới vỡ, nên kiểm trước. */
export function kiemNode(coWebSocket = typeof WebSocket !== 'undefined', ver = process.versions.node) {
  if (!coWebSocket) {
    throw new Error(`Cần Node 22 trở lên (đang là ${ver}). Cập nhật: winget upgrade OpenJS.NodeJS.LTS`);
  }
}

async function main() {
  const a = parseArgs(process.argv.slice(2));
  if (a.help) { console.log(HELP); return 0; }
  kiemNode();
  if (a.stills && a.out) throw new Error('--stills ghi vào một thư mục: dùng --out-dir <thư mục>, không dùng --out.');
  const here = dirname(fileURLToPath(import.meta.url));
  const root = findRepoRoot(here) || findRepoRoot(process.cwd());
  const chromePath = resolveChrome({ flag: a.chrome, root });
  if (a.page && !a.kiemWebgl && !existsSync(a.page)) throw new Error(`Không thấy trang: ${a.page}`);

  const s = new Session();
  const onSig = () => { killTree(s.ffmpeg); s.close().finally(() => process.exit(130)); };
  process.on('SIGINT', onSig); process.on('SIGTERM', onSig);
  try {
    await s.launch({ chromePath, width: 1920, height: 1080, phanMem: a.phanMem });
    if (a.kiemWebgl) {
      const r = await modeWebgl(s, a);
      const line = `WebGL: ${r.loai}${r.renderer ? ` · ${r.renderer}` : ''}${r.version ? ` · ${r.version}` : ''}`;
      if (a.json) console.log(JSON.stringify(r)); else console.log(line);
      log(`${line}\n`);
      return r.webgl ? 0 : 2;
    }
    const url = pathToFileURL(resolve(a.page)).href + '?render=1';
    const res = a.stills ? await modeStills(s, a, url) : a.data ? await modeData(s, a, url) : await modeVideo(s, a, url);
    if (a.json) console.log(JSON.stringify(res));
    else for (const p of res.files ?? [res.out]) console.log(p);
    return 0;
  } finally {
    await s.close();
  }
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().then((c) => process.exit(c), (e) => { log(`\nLỖI: ${e.message}\n`); process.exit(1); });
}
