// Khối vnmap: bản đồ chính trị phẳng Đông Dương – Biển Đông (canvas 2D, Web Mercator) + bay máy.
// Luật cứng: Hoàng Sa, Trường Sa thuộc Việt Nam (cùng màu, có nhãn), ghi "BIỂN ĐÔNG"; không vẽ ranh giới biển nào.
import { W, H, clamp, lerp, prog, ease, keyframes, rng, appear, loadFonts, drawDateLabel, drawCredit, mount } from '../lib/common.js';
import { BORDERS } from '../data/borders.js';
import { callout } from '../lib/callout.js';

const S = window.SHOT;
const CREDIT = 'Bản đồ: Natural Earth (phạm vi công cộng) · Ảnh vệ tinh: Sentinel-2 cloudless 2016 (EOX, CC BY 4.0) · Hoàng Sa, Trường Sa thuộc Việt Nam';
const COL = { bien: '#0c263d', bien2: '#123552', vn: '#9a2d23', vnVien: '#e0826c', lang: '#2c2a26', langVien: '#5d5850', chu: '#f3efe6' };
// Bảng màu lịch sử, quân sự (S.mau = 'quan-su', tập 1 v2): bản đồ tham mưu in giấy — biển xám lam nhạt, Việt Nam màu đất son,
// nước khác màu giấy, chữ mực; phủ vân giấy và lưới toạ độ. Hoàng Sa, Trường Sa vẫn cùng màu Việt Nam.
const QS = S.mau === 'quan-su';
if (QS) Object.assign(COL, { bien: '#76898a', bien2: '#93a49f', vn: '#b4613f', vnVien: '#6e2414', lang: '#c4b58f', langVien: '#6d6450', chu: '#f3ead2',
                             muc: '#231d12', mucNhat: '#4a4232', bienChu: 'rgba(32,52,70,0.85)', diem: '#8f1f14' });
let giay = null;
function makeGiay() {
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d'), r = rng(77);
  g.fillStyle = '#ffffff'; g.fillRect(0, 0, W, H);
  const lo = document.createElement('canvas'); lo.width = 48; lo.height = 27;
  const lg = lo.getContext('2d'), li = lg.createImageData(48, 27);
  for (let i = 0; i < li.data.length; i += 4) { const v = 200 + r() * 55; li.data[i] = v; li.data[i + 1] = v * 0.97; li.data[i + 2] = v * 0.88; li.data[i + 3] = 255; }
  lg.putImageData(li, 0, 0); g.imageSmoothingQuality = 'high'; g.drawImage(lo, 0, 0, W, H);
  const im = g.getImageData(0, 0, W, H);
  for (let i = 0; i < im.data.length; i += 4) { const n = (r() - 0.5) * 22; im.data[i] += n; im.data[i + 1] += n; im.data[i + 2] += n; }
  g.putImageData(im, 0, 0);
  g.strokeStyle = 'rgba(70,60,40,0.35)'; g.lineWidth = 1;
  for (let x = 60; x < W; x += 160) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, H); g.stroke(); }
  for (let y = 40; y < H; y += 160) { g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); }
  return c;
}
const DEFAULT_LABELS = [
  { text: 'VIỆT NAM', lon: 105.2, lat: 21.75, kind: 'vn' },
  { text: 'LÀO', lon: 102.9, lat: 19.6, kind: 'nuoc' },
  { text: 'CAMPUCHIA', lon: 104.9, lat: 12.8, kind: 'nuoc' },
  { text: 'THÁI LAN', lon: 101.0, lat: 15.6, kind: 'nuoc' },
  { text: 'TRUNG QUỐC', lon: 108.5, lat: 24.0, kind: 'nuoc' },
  { text: 'BIỂN ĐÔNG', lon: 113.4, lat: 14.2, kind: 'bien', static: true },
  { text: 'QUẦN ĐẢO HOÀNG SA', lon: 111.95, lat: 17.45, kind: 'dao', static: true },
  { text: 'QUẦN ĐẢO TRƯỜNG SA', lon: 114.2, lat: 11.55, kind: 'dao', static: true },
  { text: 'VỊNH BẮC BỘ', lon: 107.9, lat: 19.75, kind: 'bien-nho' },
];

const RAD = Math.PI / 180;
const my = (lat) => Math.log(Math.tan(Math.PI / 4 + (lat * RAD) / 2)) / RAD; // độ "mercator"
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const ctx = cv.getContext('2d');
let sat, satMeta, cam;
const P = (lon, lat) => [W / 2 + (lon - cam.lon) * cam.zoom, H / 2 - (my(lat) - my(cam.lat)) * cam.zoom];

function ring(r) {
  ctx.beginPath();
  r.forEach(([lon, lat], i) => { const [x, y] = P(lon, lat); i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
  ctx.closePath();
}
function inView(r) {
  // loại nhanh vòng ngoài khung
  let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
  for (let i = 0; i < r.length; i += 4) { const [x, y] = P(r[i][0], r[i][1]); x0 = Math.min(x0, x); x1 = Math.max(x1, x); y0 = Math.min(y0, y); y1 = Math.max(y1, y); }
  return x1 > -400 && x0 < W + 400 && y1 > -400 && y0 < H + 400;
}

function drawMap(t, polyAlpha) {
  const g = ctx.createRadialGradient(W * 0.6, H * 0.5, 100, W * 0.5, H * 0.5, W * 0.8);
  g.addColorStop(0, COL.bien2); g.addColorStop(1, COL.bien);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  // ảnh vệ tinh vùng Tây Bắc khi bay sát
  const sa = S.satellite ? ease.inOut(prog(t, S.satellite.from, S.satellite.dur ?? 1.5)) : 0;
  if (sa > 0) {
    const [x0, y0] = P(satMeta.west, satMeta.north), [x1, y1] = P(satMeta.east, satMeta.south);
    ctx.save(); ctx.globalAlpha = sa; ctx.filter = 'saturate(0.55) brightness(0.95) contrast(1.05)';
    ctx.drawImage(sat, x0, y0, x1 - x0, y1 - y0); ctx.restore();
  }
  const fillA = polyAlpha * (1 - sa * 0.85);
  ctx.lineJoin = 'round';
  ctx.save(); ctx.globalAlpha = fillA;
  for (const o of BORDERS.other) { if (!inView(o.r)) continue; ring(o.r); ctx.fillStyle = COL.lang; ctx.fill(); }
  for (const r of BORDERS.vn) { if (!inView(r)) continue; ring(r); ctx.fillStyle = COL.vn; ctx.fill(); }
  ctx.restore();
  // đường biên (giữ mờ khi có ảnh vệ tinh)
  ctx.save(); ctx.globalAlpha = polyAlpha * (1 - sa * 0.4); ctx.lineWidth = 1.3;
  for (const o of BORDERS.other) { if (!inView(o.r)) continue; ring(o.r); ctx.strokeStyle = COL.langVien; ctx.stroke(); }
  ctx.lineWidth = 2; ctx.strokeStyle = COL.vnVien;
  for (const r of BORDERS.vn) { if (!inView(r)) continue; ring(r); ctx.stroke(); }
  ctx.restore();
  // Hoàng Sa, Trường Sa: từng đảo tô màu Việt Nam, tối thiểu một chấm để luôn nhìn thấy
  ctx.save(); ctx.globalAlpha = polyAlpha;
  for (const key of ['hoang_sa', 'truong_sa']) {
    for (const r of BORDERS.islands[key]) {
      ring(r); ctx.fillStyle = COL.vn; ctx.fill(); ctx.strokeStyle = COL.vnVien; ctx.lineWidth = 1; ctx.stroke();
      const c = r.reduce((a, p) => [a[0] + p[0] / r.length, a[1] + p[1] / r.length], [0, 0]);
      const [x, y] = P(c[0], c[1]);
      ctx.beginPath(); ctx.arc(x, y, clamp(cam.zoom / 20, 3.3, 6), 0, Math.PI * 2); ctx.fillStyle = QS ? COL.diem : COL.vn; ctx.fill(); ctx.lineWidth = 1.5; ctx.strokeStyle = QS ? '#f3ead2' : '#f0b2a2'; ctx.stroke();
    }
  }
  ctx.restore();
}

function label(text, x, y, kind, a, sc = 1) {
  const z = cam.zoom;
  const base = { vn: 34, nuoc: 26, bien: 34, 'bien-nho': 20, dao: 18, tp: 22 }[kind] ?? 24;
  const size = Math.round(base * clamp(Math.pow(z / 60, 0.35), 0.85, 1.5));
  ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.translate(x, y); ctx.scale(sc, sc); ctx.translate(-x, -y);
  if (kind === 'bien' || kind === 'bien-nho') {
    ctx.font = `italic 500 ${size}px Lora`; ctx.fillStyle = QS ? COL.bienChu : 'rgba(170,200,225,0.85)';
    ctx.letterSpacing = `${Math.round(size * 0.25)}px`;
    ctx.fillText(text, x, y);
  } else if (kind === 'dao') {
    ctx.font = `600 ${size}px Oswald`; ctx.letterSpacing = '1px';
    const tw = ctx.measureText(text).width;
    ctx.fillStyle = QS ? 'rgba(36,29,18,0.85)' : 'rgba(10,9,8,0.82)'; ctx.fillRect(x - tw / 2 - 8, y - size * 0.7, tw + 16, size * 1.4);
    ctx.fillStyle = COL.chu; ctx.fillText(text, x, y);
  } else {
    ctx.font = `${kind === 'vn' ? 700 : 500} ${size}px Oswald`; ctx.letterSpacing = `${Math.round(size * 0.12)}px`;
    ctx.shadowColor = QS && kind !== 'vn' ? 'rgba(0,0,0,0)' : 'rgba(0,0,0,0.6)'; ctx.shadowBlur = 8;
    ctx.fillStyle = kind === 'vn' ? COL.chu : QS ? COL.mucNhat : 'rgba(210,204,190,0.8)';
    ctx.fillText(text, x, y);
  }
  ctx.restore();
}

// Quốc gia nhấp sáng khi lời đọc tên (S.nhap [{nuoc: 'vn' | tên Natural Earth, at}]): loé rồi giữ viền sáng.
// 'vn' gồm cả Hoàng Sa, Trường Sa.
function nhap(t) {
  for (const n of S.nhap || []) {
    const u = t - n.at; if (u < 0) continue;
    const a = 0.6 * Math.exp(-u / 0.35) * clamp(u / 0.08) + 0.3 * clamp(u / 0.15);
    const vong = n.nuoc === 'vn' ? [...BORDERS.vn, ...BORDERS.islands.hoang_sa, ...BORDERS.islands.truong_sa]
      : BORDERS.other.filter((o) => o.n === n.nuoc).map((o) => o.r);
    ctx.save(); ctx.lineJoin = 'round';
    for (const r of vong) {
      if (!inView(r)) continue;
      ring(r); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = `rgba(255,200,140,${a * 0.35})`; ctx.fill();
      ctx.globalCompositeOperation = 'source-over'; ctx.shadowColor = '#ffcf7a'; ctx.shadowBlur = 16 * a;
      ctx.strokeStyle = `rgba(255,214,140,${Math.min(1, a * 1.6)})`; ctx.lineWidth = 2.5; ctx.stroke(); ctx.shadowBlur = 0;
    }
    ctx.restore();
  }
}

function marker(m, t) {
  const A = appear(t, m.from ?? 0, { dur: 0.5, to: m.to ?? 1e9, s0: 0.3 }), a = A.a;
  if (a <= 0) return;
  const [x, y] = P(m.lon, m.lat);
  ctx.save(); ctx.globalAlpha = a;
  ctx.translate(x, y); ctx.scale(A.s, A.s); ctx.translate(-x, -y);
  const ph = ((t - (m.from ?? 0)) * 0.8) % 1;
  ctx.strokeStyle = '#e5a93b'; ctx.lineWidth = 3; ctx.globalAlpha = a * (1 - ph);
  ctx.beginPath(); ctx.arc(x, y, 10 + ph * 34, 0, Math.PI * 2); ctx.stroke();
  ctx.globalAlpha = a; ctx.fillStyle = m.color ?? '#e5a93b'; ctx.strokeStyle = '#111'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(x, y, 8, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  if (m.label) {
    ctx.font = `600 ${m.size ?? 30}px Oswald`;
    const tw = ctx.measureText(m.label).width, s = m.size ?? 30;
    const lx = x + (m.dx ?? 22), ly = y + (m.dy ?? -s);
    ctx.fillStyle = 'rgba(10,9,8,0.9)'; ctx.fillRect(lx, ly - s * 0.75, tw + s * 0.8, s * 1.5);
    ctx.fillStyle = COL.chu; ctx.textBaseline = 'middle'; ctx.fillText(m.label, lx + s * 0.4, ly);
  }
  ctx.restore();
}

const grain = [];
function makeGrain() {
  for (let k = 0; k < 4; k++) {
    const c = document.createElement('canvas'); c.width = 480; c.height = 270;
    const g = c.getContext('2d'), im = g.createImageData(480, 270), r = rng(301 + k);
    for (let i = 0; i < im.data.length; i += 4) { const v = r() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
    g.putImageData(im, 0, 0); grain.push(c);
  }
}

function renderFrame(t) {
  t = clamp(t, 0, S.duration);
  // zoom nội suy theo log để tốc độ bay đều
  const k = keyframes(S.camera.map((c) => ({ ...c, lz: Math.log(c.zoom) })), t);
  cam = { lon: k.lon, lat: k.lat, zoom: Math.exp(k.lz) };
  drawMap(t, 1);
  nhap(t);
  const labels = [...(S.defaultLabels === false ? [] : DEFAULT_LABELS), ...(S.labels || [])];
  const sa = S.satellite ? prog(t, S.satellite.from, S.satellite.dur ?? 1.5) : 0;
  labels.forEach((l, i) => {
    // nhãn mặc định bật ra so le 70 ms
    // nhãn chủ quyền (Hoàng Sa, Trường Sa, Biển Đông) có mặt ngay từ khung đầu, không animate
    const A = l.static ? { a: 1, s: 1, y: 0 } : appear(t, l.from ?? 0.25 + i * 0.07, { dur: 0.55, to: l.to ?? 1e9, rise: 8, s0: 0.9 });
    const a = A.a * (1 - sa);
    if (a <= 0) return;
    const [x, y] = P(l.lon, l.lat);
    if (x < -300 || x > W + 300 || y < -100 || y > H + 100) return;
    label(l.text, x, y + A.y, l.kind ?? 'nuoc', a, A.s);
  });
  for (const m of S.markers || []) marker(m, t);
  for (const ti of S.titles || []) {
    const a = ease.out(prog(t, ti.from, 0.6)) * (1 - prog(t, ti.to ?? 1e9, 0.5));
    if (a <= 0) continue;
    ctx.save(); ctx.globalAlpha = a; ctx.textAlign = ti.align ?? 'left'; ctx.textBaseline = 'alphabetic';
    ctx.shadowColor = 'rgba(0,0,0,0.7)'; ctx.shadowBlur = 24;
    ctx.font = `700 ${ti.size ?? 84}px Oswald`; ctx.fillStyle = COL.chu; ctx.fillText(ti.text, ti.x ?? 96, ti.y ?? 900);
    if (ti.sub) {
      // dòng phụ xuống dòng trong bề rộng subMaxW để không lấn sang chú thích nguồn góc phải dưới
      const fs = Math.round((ti.size ?? 84) * 0.36);
      ctx.font = `500 ${fs}px BVP`; ctx.fillStyle = 'rgba(243,239,230,0.9)';
      const lines = []; let cur = '';
      for (const w of ti.sub.split(' ')) { const n = cur ? cur + ' ' + w : w; if (ctx.measureText(n).width > (ti.subMaxW ?? 820) && cur) { lines.push(cur); cur = w; } else cur = n; }
      if (cur) lines.push(cur);
      lines.forEach((l, i) => ctx.fillText(l, ti.x ?? 96, (ti.y ?? 900) + (ti.size ?? 84) * 0.62 + i * fs * 1.3));
    }
    ctx.restore();
  }
  if (QS) { ctx.save(); ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(giay, 0, 0); ctx.restore(); }
  // vignette + hạt
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.05);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.globalAlpha = 0.05; ctx.globalCompositeOperation = 'overlay'; ctx.drawImage(grain[Math.floor(t * 24) % 4], 0, 0, W, H); ctx.restore();
  const d = typeof S.date === 'string' ? { text: S.date } : S.date;
  if (d) drawDateLabel(ctx, d.text, ease.out(prog(t, d.from ?? 0.2, 0.5)) * (1 - prog(t, d.to ?? 1e9, 0.4)));
  for (const c of S.callouts || []) callout(ctx, t, c);
  drawCredit(ctx, S.credit ?? CREDIT, 1);
  const fi = S.fadeIn ?? 0, fo = S.fadeOut ?? 0;
  const black = Math.max(fi ? 1 - prog(t, 0, fi) : 0, fo ? prog(t, S.duration - fo, fo) : 0);
  if (black > 0) { ctx.fillStyle = `rgba(0,0,0,${black})`; ctx.fillRect(0, 0, W, H); }
}

async function init() {
  satMeta = await (await fetch(new URL('../data/region_meta.json', import.meta.url))).json();
  sat = new Image(); sat.src = new URL('../data/region_s2.jpg', import.meta.url).href; await sat.decode();
  makeGrain();
  if (QS) giay = makeGiay();
  await loadFonts();
  mount(S.duration, renderFrame);
}
init();
