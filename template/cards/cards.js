// Khối cards: thẻ chữ/số kiểu phim tài liệu (canvas 2D). SHOT.type chọn loại thẻ:
//   so-lieu | lich | dong-thoi-gian | van-kien | chuong | hook | lower-third | may-chu | hai-cot
//   và 5 mẫu P2 (cards/mau-moi.js): tai-lieu-dich | phim-panel | the-am-thanh | nhan-vat | bieu-do
// Mặc định vẽ bằng hệ nhận diện lib/nhan-dien.js + lib/nhan-dien-the.js; mã vẽ cũ ở dưới chỉ chạy khi SHOT.nhanDien === false.
import { W, H, clamp, lerp, prog, ease, rng, noise1, appear, landPunch, loadFonts, drawDateLabel, drawCredit, mount } from '../lib/common.js';

import { planTyping, drawTypewriter } from './typewriter.js';
import { taoND, dangKyDo } from '../lib/nhan-dien.js';
import { taoCacThe, KIEU_NEN, chuanBiMayChu } from '../lib/nhan-dien-the.js';
import { LOAI_MAU, chuanBiMau } from './mau-moi.js';

const S = window.SHOT;
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const ctx = cv.getContext('2d');
// Hệ nhận diện «bảng tác chiến» (lib/nhan-dien.js) là mặc định. SHOT.nhanDien = false giữ bản vẽ cũ bên dưới (shot cũ cần y nguyên).
const ND_ON = S.nhanDien !== false;
const nd = ND_ON ? taoND(ctx, S) : null;
const REF = { lowerBg: null, mc: null, mau: null };
const TYPES_ND = ND_ON ? taoCacThe(nd, ctx, S, REF) : null;
const C = { giay: '#d6c9a3', muc: '#1e1d1a', mucNhat: 'rgba(30,29,26,0.62)', do: '#c93b2b', vang: '#e5a93b', toi: '#120c07', kem: '#efe6d2' };
// Bảng màu lịch sử, quân sự (S.mau = 'quan-su', tập 1 v2): giấy bản đồ tác chiến ngả vàng, mực nâu đen, đỏ son ký hiệu ta,
// xanh mực ký hiệu địch, nâu đường đồng mức; thẻ tối màu vải quân phục sẫm. S.nen = 'trong': không vẽ nền (phủ lên hình động).
// S.mau = 'xanh-qd' (tập 1 v3, user chốt nền xanh quân đội): nền vải ô-liu quân phục có đường đồng mức bản đồ (S.nenQd = 'o-liu')
// hoặc vải rằn ri trầm (S.nenQd = 'ran-ri'); chữ kem, đỏ son sáng hơn để nổi trên lục; trang sổ là bảng sẫm đặt lên nền.
const XQ = S.mau === 'xanh-qd';
const QS = S.mau === 'quan-su' || XQ;
if (QS) Object.assign(C, { giay: '#cbb88c', muc: '#241d12', mucNhat: 'rgba(36,29,18,0.66)', do: '#a8271c', vang: '#c4922e', toi: '#15160f', kem: '#ebe2c8', dich: '#2c4766', dongMuc: '#8a6a43' });
if (XQ) Object.assign(C, { giay: '#2b3119', muc: '#ebe4c8', mucNhat: 'rgba(235,228,200,0.72)', do: '#dc5a3c', vang: '#dcae48', toi: '#141809', kem: '#ebe4c8', dich: '#9cb8d2', dongMuc: '#1e2312' });
const mucMo = (a) => (XQ ? `rgba(235,228,200,${a})` : `rgba(30,29,26,${a})`); // mực nhạt theo nền
const TRANG_SO = XQ ? 'rgba(14,17,7,0.58)' : 'rgba(245,238,220,0.55)';
const TRONG = S.nen === 'trong';

// ---------- nền ----------
function makeTexture(base, seed, { fibers = true, blotch = 0.08, grain = 18 } = {}) {
  const c = document.createElement('canvas'); c.width = W; c.height = H;
  const g = c.getContext('2d');
  g.fillStyle = base; g.fillRect(0, 0, W, H);
  const r = rng(seed);
  // vết loang tần số thấp
  const lo = document.createElement('canvas'); lo.width = 48; lo.height = 27;
  const lg = lo.getContext('2d'), li = lg.createImageData(48, 27);
  for (let i = 0; i < li.data.length; i += 4) { const v = r() * 255; li.data[i] = li.data[i + 1] = li.data[i + 2] = v; li.data[i + 3] = 255; }
  lg.putImageData(li, 0, 0);
  g.save(); g.globalAlpha = blotch; g.globalCompositeOperation = 'multiply'; g.imageSmoothingQuality = 'high'; g.drawImage(lo, 0, 0, W, H); g.restore();
  // sợi giấy
  if (fibers) {
    g.save(); g.globalAlpha = 0.06; g.strokeStyle = '#5a4a2c'; g.lineWidth = 1;
    for (let k = 0; k < 1400; k++) { const x = r() * W, y = r() * H, a = r() * Math.PI, l = 6 + r() * 26; g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke(); }
    g.restore();
  }
  // hạt mịn
  const im = g.getImageData(0, 0, W, H);
  for (let i = 0; i < im.data.length; i += 4) { const n = (r() - 0.5) * grain; im.data[i] += n; im.data[i + 1] += n; im.data[i + 2] += n; }
  g.putImageData(im, 0, 0);
  // vignette mép
  const vg = g.createRadialGradient(W / 2, H / 2, H * 0.5, W / 2, H / 2, H * 1.1);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(40,25,10,0.35)');
  g.fillStyle = vg; g.fillRect(0, 0, W, H);
  return c;
}
let BG;
const TRAN = 1.08; // nền bản đồ lớn hơn khung để trôi chậm

// Giấy bản đồ tác chiến: nền ngả vàng, đường đồng mức nâu, lưới toạ độ xanh mực, nếp gấp, vết ố.
function makeMapPaper(seed) {
  const w = Math.round(W * TRAN), h = Math.round(H * TRAN);
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d');
  const base = makeTexture(C.giay, seed, { blotch: 0.1, grain: 14 });
  g.drawImage(base, 0, 0, w, h);
  // trường độ cao giả (tổng vài tần số) → đường đồng mức
  const r = rng(seed + 7), gw = 64, gh = 36, f = new Float32Array(gw * gh);
  for (let k = 0; k < 3; k++) {
    const cx = r() * gw, cy = r() * gh, rr = 6 + r() * 10;
    for (let y = 0; y < gh; y++) for (let x = 0; x < gw; x++) f[y * gw + x] += Math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * rr * rr)) * (0.6 + r());
  }
  for (let i = 0; i < f.length; i++) f[i] += r() * 0.05;
  const val = (x, y) => { // nội suy song tuyến
    const fx = x / w * (gw - 1), fy = y / h * (gh - 1), x0 = Math.floor(fx), y0 = Math.floor(fy), x1 = Math.min(gw - 1, x0 + 1), y1 = Math.min(gh - 1, y0 + 1), u = fx - x0, v = fy - y0;
    return (f[y0 * gw + x0] * (1 - u) + f[y0 * gw + x1] * u) * (1 - v) + (f[y1 * gw + x0] * (1 - u) + f[y1 * gw + x1] * u) * v;
  };
  const im = g.getImageData(0, 0, w, h), d = im.data, lv = new Float32Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) lv[y * w + x] = Math.floor(val(x, y) * 9);
  for (let y = 0; y < h - 1; y++) for (let x = 0; x < w - 1; x++) {
    const i = y * w + x;
    if (lv[i] !== lv[i + 1] || lv[i] !== lv[i + w]) { const k = i * 4, a = lv[i] % 4 === 0 ? 0.75 : 0.5; d[k] += (138 - d[k]) * a; d[k + 1] += (106 - d[k + 1]) * a; d[k + 2] += (67 - d[k + 2]) * a; }
  }
  g.putImageData(im, 0, 0);
  // lưới toạ độ và số kinh vĩ ở mép
  g.save(); g.strokeStyle = 'rgba(44,71,102,0.20)'; g.lineWidth = 1.2; g.font = '500 15px "Plex Mono"'; g.fillStyle = 'rgba(44,71,102,0.45)';
  for (let x = 40, k = 0; x < w; x += 172, k++) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); g.fillText(`103°${String(k * 4).padStart(2, '0')}'`, x + 4, 22); }
  for (let y = 60, k = 0; y < h; y += 172, k++) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); g.fillText(`21°${String(30 - k * 4).padStart(2, '0')}'`, 6, y - 5); }
  g.restore();
  // nếp gấp: một dọc, một ngang (vệt sáng cạnh vệt tối)
  for (const [x0, y0, x1, y1] of [[w * 0.5, 0, w * 0.5, h], [0, h * 0.52, w, h * 0.52]]) {
    g.save(); g.lineWidth = 3; g.strokeStyle = 'rgba(70,50,25,0.18)'; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke();
    g.translate(x0 === x1 ? 3 : 0, y0 === y1 ? 3 : 0); g.strokeStyle = 'rgba(255,248,225,0.22)'; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke(); g.restore();
  }
  // vết ố
  for (let k = 0; k < 5; k++) {
    const x = r() * w, y = r() * h, rr = 120 + r() * 260, gr = g.createRadialGradient(x, y, 0, x, y, rr);
    gr.addColorStop(0, 'rgba(110,75,35,0.10)'); gr.addColorStop(1, 'rgba(110,75,35,0)');
    g.fillStyle = gr; g.fillRect(x - rr, y - rr, rr * 2, rr * 2);
  }
  return c;
}

// Trường nhiễu giá trị (lưới thưa gw×gh, nội suy song tuyến) để vẽ đốm rằn ri và đường đồng mức.
function truongNhieu(r, gw, gh, w, h) {
  const f = new Float32Array(gw * gh);
  for (let i = 0; i < f.length; i++) f[i] = r();
  return (x, y) => {
    const fx = x / w * (gw - 1), fy = y / h * (gh - 1), x0 = Math.floor(fx), y0 = Math.floor(fy), x1 = Math.min(gw - 1, x0 + 1), y1 = Math.min(gh - 1, y0 + 1);
    const u = (fx - x0) ** 2 * (3 - 2 * (fx - x0)), v = (fy - y0) ** 2 * (3 - 2 * (fy - y0));
    return (f[y0 * gw + x0] * (1 - u) + f[y0 * gw + x1] * u) * (1 - v) + (f[y1 * gw + x0] * (1 - u) + f[y1 * gw + x1] * u) * v;
  };
}

// Nền xanh quân đội: vải ô-liu quân phục (sợi đan mịn) hoặc rằn ri bốn màu trầm; đường đồng mức bản đồ tác chiến in sẫm,
// lưới toạ độ khaki mờ, mép tối. Chữ kem đặt trên nền này.
function makeQuanPhuc(seed, ranRi) {
  const w = Math.round(W * TRAN), h = Math.round(H * TRAN);
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d');
  g.drawImage(makeTexture('#3a4126', seed, { fibers: false, blotch: 0.2, grain: 10 }), 0, 0, w, h);
  const r = rng(seed + 11), im = g.getImageData(0, 0, w, h), d = im.data;
  const lop = ranRi ? [[[44, 50, 30], 0.50, 9, 6], [[78, 64, 42], 0.60, 11, 7], [[96, 98, 66], 0.66, 8, 5]].map(([mau, nguong, gw, gh]) =>
    [mau, nguong, truongNhieu(r, gw * 2, gh * 2, w, h), truongNhieu(r, gw * 6, gh * 6, w, h)]) : [];
  const cao = truongNhieu(rng(seed + 7), 9, 6, w, h), cao2 = truongNhieu(rng(seed + 9), 22, 13, w, h);
  const lv = new Int16Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x, k = i * 4;
    for (const [mau, nguong, f1, f2] of lop) {
      if (f1(x, y) * 0.8 + f2(x, y) * 0.2 > nguong) { d[k] = d[k] * 0.25 + mau[0] * 0.75; d[k + 1] = d[k + 1] * 0.25 + mau[1] * 0.75; d[k + 2] = d[k + 2] * 0.25 + mau[2] * 0.75; }
    }
    if (((x + y) & 3) === 0) { d[k] *= 0.93; d[k + 1] *= 0.93; d[k + 2] *= 0.93; } // sợi vải đan chéo
    lv[i] = Math.floor((cao(x, y) * 0.8 + cao2(x, y) * 0.2) * 14);
  }
  for (let y = 0; y < h - 1; y++) for (let x = 0; x < w - 1; x++) {
    const i = y * w + x;
    if (lv[i] !== lv[i + 1] || lv[i] !== lv[i + w]) { const k = i * 4, a = lv[i] % 5 === 0 ? 0.55 : 0.32; d[k] *= 1 - a; d[k + 1] *= 1 - a * 0.9; d[k + 2] *= 1 - a; }
  }
  g.putImageData(im, 0, 0);
  g.save(); g.strokeStyle = 'rgba(214,204,160,0.10)'; g.lineWidth = 1.2; g.font = '500 15px "Plex Mono"'; g.fillStyle = 'rgba(214,204,160,0.32)';
  for (let x = 40, k = 0; x < w; x += 172, k++) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); g.fillText(`103°${String(k * 4).padStart(2, '0')}'`, x + 4, 22); }
  for (let y = 60, k = 0; y < h; y += 172, k++) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); g.fillText(`21°${String(30 - k * 4).padStart(2, '0')}'`, 6, y - 5); }
  g.restore();
  const vg = g.createRadialGradient(w / 2, h / 2, h * 0.35, w / 2, h / 2, h * 0.95);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(6,8,2,0.55)');
  g.fillStyle = vg; g.fillRect(0, 0, w, h);
  return c;
}

// Vẽ nền mỗi khung: trong suốt (+ lớp tối nhẹ cho chữ đọc được), giấy bản đồ trôi chậm, hoặc nền cũ.
function nen(t) {
  if (TRONG) {
    ctx.clearRect(0, 0, W, H);
    const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.15, W / 2, H / 2, H * 0.95);
    vg.addColorStop(0, `rgba(12,12,8,${S.toi ?? 0.5})`); vg.addColorStop(1, `rgba(8,8,5,${Math.min(1, (S.toi ?? 0.5) + 0.3)})`);
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
    return;
  }
  if (BG.width > W) {
    const k = clamp(t / Math.max(1, S.duration), 0, 1), dx = (BG.width - W) * (0.15 + 0.7 * k), dy = (BG.height - H) * (0.6 - 0.3 * k);
    ctx.drawImage(BG, -dx, -dy);
    return;
  }
  ctx.drawImage(BG, 0, 0);
}

// ---------- tiện ích chữ ----------
const font = (w, s, fam = 'Oswald', style = '') => `${style} ${w} ${s}px ${fam}`.trim();
function fmtNum(v, dec = 0) { return v.toFixed(dec).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }
function wrap(text, maxW) {
  const words = text.split(' '), lines = []; let cur = '';
  for (const w of words) { const n = cur ? cur + ' ' + w : w; if (ctx.measureText(n).width > maxW && cur) { lines.push(cur); cur = w; } else cur = n; }
  if (cur) lines.push(cur);
  return lines;
}
function header(t, a = 1) {
  // tiêu đề thẻ kiểu hồ sơ: tag đen nhỏ + tiêu đề in hoa + đường kẻ
  if (!S.title) return;
  // tag -> kicker -> tiêu đề -> đường kẻ, so le 80 ms
  const T1 = appear(t, 0.05, { dur: 0.45, rise: 0 }), T2 = appear(t, 0.13, { dur: 0.45, rise: 0 }), T3 = appear(t, 0.2, { dur: 0.6, rise: 18, s0: 1 });
  ctx.save(); ctx.globalAlpha = T1.a * a;
  let x = 120;
  if (S.tag) { ctx.font = font(500, 18, '"Plex Mono"'); const tw = ctx.measureText(S.tag).width; ctx.fillStyle = C.muc; ctx.fillRect(x, 92, tw + 20, 30); ctx.fillStyle = C.giay; ctx.textBaseline = 'middle'; ctx.fillText(S.tag, x + 10, 108); x += tw + 36; }
  ctx.globalAlpha = T2.a * a;
  if (S.kicker) { ctx.font = font(500, 18, '"Plex Mono"'); ctx.fillStyle = C.mucNhat; ctx.textBaseline = 'middle'; ctx.fillText(S.kicker, x, 108); }
  ctx.globalAlpha = T3.a * a;
  ctx.save(); ctx.beginPath(); ctx.rect(100, 120, W, 82); ctx.clip();
  ctx.font = font(700, 54); ctx.fillStyle = C.muc; ctx.textBaseline = 'alphabetic'; ctx.fillText(S.title, 120, 190 + T3.y * 3); ctx.restore();
  ctx.fillStyle = C.muc; ctx.fillRect(120, 214, (W - 240) * ease.expoOut(prog(t, 0.3, 1.1)), 2);
  ctx.fillStyle = C.do; ctx.fillRect(120, 210, 70 * ease.expoOut(prog(t, 0.25, 0.5)), 6);
  ctx.restore();
}
function source(t, dark = !XQ) { drawCredit(ctx, S.source, 1, dark); }

// ---------- (i) thẻ số liệu ----------
function soLieu(t) {
  nen(t); header(t);
  const items = S.items || [];
  const mode = S.layout ?? (items.length > 1 ? 'row' : 'single');
  items.forEach((it, i) => {
    const A = appear(t, it.from, { dur: 0.5, to: it.to ?? 1e9, rise: 30, s0: 0.92 }), a = A.a;
    if (a <= 0) return;
    const dur = it.count === false ? 0.12 : it.dur ?? 1.6;
    const k = ease.expoOut(prog(t, it.from, dur));
    const v = lerp(it.start ?? 0, it.value, k);
    const landed = it.count === false || t >= it.from + dur * 0.92;
    const txt = fmtNum(landed ? it.value : Math.round(v), it.dec ?? 0) + (it.suffix ?? '');
    const punch = landPunch(t, it.from + dur * 0.92, 0.35, 0.06);
    let cx, cy, size;
    if (mode === 'single' || mode === 'replace') { cx = W / 2; cy = 560; size = it.size ?? 230; }
    else { const n = items.length; cx = 120 + ((W - 240) / n) * (i + 0.5); cy = 560; size = it.size ?? (n === 3 ? 140 : 190); }
    ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center';
    ctx.save(); ctx.translate(cx, cy + A.y); ctx.scale(A.s + punch, A.s + punch);
    ctx.font = font(700, size); ctx.fillStyle = C.muc; ctx.fillText(txt, 0, 0); ctx.restore();
    // vạch đỏ quét dưới số khi số chạm đích
    const u = ease.expoOut(prog(t, it.from + dur * 0.92, 0.45));
    if (u > 0) { ctx.font = font(700, size); const tw = ctx.measureText(txt).width; ctx.fillStyle = C.do; ctx.fillRect(cx - tw / 2, cy + size * 0.05, tw * u, 5); }
    if (it.prefix) { ctx.font = font(600, size * 0.24); ctx.fillStyle = C.muc; ctx.fillText(it.prefix, cx, cy - size * 0.98); }
    const U = appear(t, it.from + 0.25, { dur: 0.5, to: it.to ?? 1e9, rise: 12 });
    ctx.globalAlpha = a * U.a;
    if (it.unit) { ctx.font = font(600, size * 0.26); ctx.fillStyle = C.do; ctx.fillText(it.unit, cx, cy + size * 0.42 + U.y); }
    const Lb = appear(t, it.from + 0.4, { dur: 0.5, to: it.to ?? 1e9, rise: 12 });
    ctx.globalAlpha = a * Lb.a;
    ctx.font = font(500, 30, 'BVP'); ctx.fillStyle = C.muc;
    const lines = (ctx.font = font(500, 30, 'BVP'), wrap(it.label ?? '', mode === 'row' ? (W - 240) / items.length - 60 : 1100));
    lines.forEach((l, j) => ctx.fillText(l, cx, cy + size * (it.unit ? 0.68 : 0.4) + 40 * j));
    ctx.restore();
  });
  source(t);
}

// ---------- (ii) lịch tháng ----------
function lich(t) {
  nen(t); header(t);
  const { month, year, day } = S;
  const first = new Date(Date.UTC(year, month - 1, 1)).getUTCDay(); // 0 = CN
  const days = new Date(Date.UTC(year, month, 0)).getUTCDate();
  const x0 = S.note ? 330 : 560, y0 = 330, cw = 120, ch = 92; // có chú thích: lịch dịch trái để chữ không tràn mép
  const a = ease.out(prog(t, 0.3, 0.6));
  ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = font(600, 34); ctx.fillStyle = C.muc; ctx.textAlign = 'left'; ctx.fillText(`THÁNG ${month} · ${year}`, x0, y0 - 70); ctx.textAlign = 'center';
  const heads = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'];
  ctx.font = font(500, 20, '"Plex Mono"'); ctx.fillStyle = C.mucNhat;
  heads.forEach((h, i) => ctx.fillText(h, x0 + cw * i + cw / 2, y0));
  ctx.fillStyle = C.muc; ctx.fillRect(x0, y0 + 24, cw * 7, 2);
  const off = (first + 6) % 7; // Thứ Hai đầu tuần
  let cx = 0, cy = 0;
  for (let d = 1; d <= days; d++) {
    const idx = off + d - 1, col = idx % 7, row = Math.floor(idx / 7);
    const x = x0 + cw * col + cw / 2, y = y0 + 70 + ch * row;
    const da = ease.out(prog(t, 0.35 + d * 0.012, 0.3));
    ctx.globalAlpha = a * da; ctx.font = font(d === day ? 700 : 400, 38); ctx.fillStyle = d === day ? C.muc : mucMo(0.75);
    ctx.fillText(String(d), x, y);
    if (d === day) { cx = x; cy = y; }
  }
  ctx.restore();
  // vòng tròn đỏ vẽ dần như bút
  const k = ease.inOut(prog(t, S.circleAt ?? 1.4, 0.8));
  if (k > 0) {
    ctx.save(); ctx.strokeStyle = C.do; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath();
    const r = rng(7);
    for (let s = 0; s <= 80 * k; s++) { const ang = -2.2 + (s / 80) * Math.PI * 2.15, rr = 46 + Math.sin(s * 0.3) * 1.5 + r() * 1.2; const x = cx + Math.cos(ang) * rr * 1.08, y = cy + Math.sin(ang) * rr * 0.92; s ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
    ctx.stroke(); ctx.restore();
  }
  if (S.note) {
    const na = ease.out(prog(t, (S.circleAt ?? 1.4) + 0.7, 0.5));
    ctx.save(); ctx.globalAlpha = na; ctx.font = font(600, 40); ctx.fillStyle = C.do; ctx.textAlign = 'left'; ctx.fillText(S.note, x0 + cw * 7 + 50, cy + 12);
    if (S.noteSub) { ctx.font = font(500, 26, 'BVP'); ctx.fillStyle = C.muc; ctx.fillText(S.noteSub, x0 + cw * 7 + 50, cy + 56); }
    ctx.restore();
  }
  source(t);
}

// ---------- (iii) dòng thời gian 3 làn ----------
const dayNo = ([d, m, y]) => Date.UTC(y, m - 1, d) / 86400000;
function dongThoiGian(t) {
  nen(t); header(t);
  const A = dayNo(S.axis.from), B = dayNo(S.axis.to);
  const x0 = 360, x1 = W - 160, X = (d) => lerp(x0, x1, (dayNo(d) - A) / (B - A));
  const lanes = S.lanes;
  const top = 330, gap = 190;
  // trục tháng
  ctx.save(); ctx.globalAlpha = ease.out(prog(t, 0.3, 0.5));
  const ay = top + gap * lanes.length - 40;
  ctx.fillStyle = C.muc; ctx.fillRect(x0, ay, x1 - x0, 2);
  ctx.font = font(500, 20, '"Plex Mono"'); ctx.fillStyle = C.mucNhat; ctx.textAlign = 'center';
  for (const tk of S.axis.ticks || []) { const x = X(tk.d); ctx.fillRect(x, ay - 8, 2, 16); ctx.fillText(tk.label, x, ay + 34); }
  ctx.restore();
  lanes.forEach((ln, i) => {
    const y = top + gap * i;
    const on = t >= (ln.activeFrom ?? 1e9) && t < (ln.activeTo ?? 1e9);
    const la = ease.out(prog(t, 0.4 + i * 0.15, 0.5));
    ctx.save(); ctx.globalAlpha = la * (on || ln.activeFrom == null || t < ln.activeFrom ? 1 : 0.55);
    ctx.font = font(700, 40); ctx.fillStyle = on ? C.do : C.muc; ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
    ctx.fillText(ln.name, 120, y);
    ctx.fillStyle = mucMo(0.25); ctx.fillRect(x0, y - 2, x1 - x0, 4);
    const k = ease.inOut(prog(t, ln.activeFrom ?? 0.8 + i * 0.4, ln.grow ?? 1.0));
    const xs = X(ln.start), xe = X(ln.end);
    const col = on ? C.do : C.muc;
    if (ln.open) { const gr = ctx.createLinearGradient(xs, 0, xe, 0); gr.addColorStop(0, col); gr.addColorStop(0.7, col); gr.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = gr; } else ctx.fillStyle = col;
    ctx.fillRect(xs, y - 7, Math.max(0, (xe - xs) * k), 14);
    ctx.fillStyle = col; ctx.beginPath(); ctx.arc(xs, y, 11, 0, Math.PI * 2); ctx.fill();
    if (k > 0.98 && !ln.open) { ctx.beginPath(); ctx.arc(xe, y, 11, 0, Math.PI * 2); ctx.fill(); }
    const ta = ease.out(prog(t, (ln.activeFrom ?? 0.8 + i * 0.4) + 0.4, 0.5));
    ctx.globalAlpha *= ta; ctx.font = font(600, 30, 'BVP'); ctx.fillStyle = C.muc; ctx.textBaseline = 'alphabetic';
    ctx.fillText(ln.dates ?? '', xs, y - 26);
    if (ln.note) { ctx.font = font(500, 28, 'BVP'); ctx.fillStyle = mucMo(0.85); ctx.fillText(ln.note, xs, y + 48); }
    ctx.restore();
  });
  source(t);
}

// ---------- (iv) văn kiện nền tối ----------
function vanKien(t) {
  nen(t);
  if (S.title || S.kicker) {
    ctx.save(); ctx.globalAlpha = ease.out(prog(t, 0.1, 0.5));
    ctx.font = font(500, 22, '"Plex Mono"'); ctx.fillStyle = 'rgba(239,230,210,0.7)'; ctx.fillText(S.kicker ?? '', 160, 150);
    ctx.font = font(700, 46); ctx.fillStyle = C.kem; ctx.fillText(S.title, 160, 212);
    ctx.fillStyle = C.do; ctx.fillRect(160, 232, 80, 5);
    ctx.restore();
  }
  let y = S.y ?? 380;
  for (const b of S.blocks) {
    const size = b.size ?? 64;
    const fam = b.font === 'serif' ? 'Lora' : 'Oswald';
    const weight = b.font === 'serif' ? 500 : 700;
    ctx.font = font(weight, size, fam, b.italic ? 'italic' : '');
    const lines = wrap(b.text, b.maxW ?? 1500);
    const words = b.text.split(' ');
    const per = b.perWord ?? 0.12;
    // vị trí từng từ
    let wi = 0; const pos = [];
    lines.forEach((l, li) => { let x = 160; for (const w of l.split(' ')) { const ww = ctx.measureText(w).width; pos.push({ w, x, y: y + li * size * 1.35, ww }); x += ww + ctx.measureText(' ').width; wi++; } });
    // đánh dấu cụm (tô vàng phía sau chữ)
    for (const m of b.marks || []) {
      const idx = findPhrase(words, m.phrase); if (idx < 0) continue;
      const k = ease.inOut(prog(t, m.at, m.dur ?? 0.6));
      if (k <= 0 || m.type !== 'highlight') continue;
      drawSpan(pos.slice(idx, idx + m.phrase.split(' ').length), size, k, (p, x, w) => { ctx.fillStyle = 'rgba(229,169,59,0.92)'; ctx.fillRect(x - 8, p.y - size * 1.04, w + 16, size * 1.3); });
    }
    pos.forEach((p, i) => {
      const a = ease.out(prog(t, b.from + i * per, 0.35));
      if (a <= 0) return;
      const hl = (b.marks || []).some((m) => m.type === 'highlight' && t >= m.at + (m.dur ?? 0.6) * 0.5 && inPhrase(words, m.phrase, i));
      ctx.save(); ctx.globalAlpha = a * (b.dimAt != null ? 1 - 0.55 * ease.out(prog(t, b.dimAt, 0.5)) : 1);
      ctx.font = font(weight, size, fam, b.italic ? 'italic' : '');
      ctx.fillStyle = hl ? C.muc : b.color ?? C.kem; ctx.textBaseline = 'alphabetic';
      ctx.fillText(p.w, p.x, p.y + (1 - a) * 12);
      ctx.restore();
    });
    for (const m of b.marks || []) {
      const idx = findPhrase(words, m.phrase); if (idx < 0 || m.type !== 'strike') continue;
      const k = ease.inOut(prog(t, m.at, m.dur ?? 0.5));
      if (k > 0) drawSpan(pos.slice(idx, idx + m.phrase.split(' ').length), size, k, (p, x, w) => { ctx.fillStyle = C.do; ctx.fillRect(x - 6, p.y - size * 0.36, w + 12, Math.max(6, size * 0.09)); });
    }
    y += lines.length * size * 1.35 + (b.gap ?? 60);
  }
  if (S.cite) {
    const a = ease.out(prog(t, S.citeAt ?? 1, 0.6));
    ctx.save(); ctx.globalAlpha = a; ctx.font = font(500, 28, 'BVP'); ctx.fillStyle = 'rgba(239,230,210,0.8)'; ctx.fillText(S.cite, 160, Math.min(y + 10, 930)); ctx.restore();
  }
  drawCredit(ctx, S.source, 1);
}
function findPhrase(words, phrase) {
  const p = phrase.split(' ');
  for (let i = 0; i + p.length <= words.length; i++) if (p.every((w, j) => words[i + j] === w)) return i;
  return -1;
}
function inPhrase(words, phrase, i) { const s = findPhrase(words, phrase); return s >= 0 && i >= s && i < s + phrase.split(' ').length; }
function drawSpan(ps, size, k, fn) {
  // vẽ một dải đi qua các từ theo tỉ lệ k (gộp theo dòng)
  const rows = []; for (const p of ps) { const r = rows.find((q) => q.y === p.y); if (r) { r.x1 = p.x + p.ww; } else rows.push({ y: p.y, x0: p.x, x1: p.x + p.ww }); }
  const total = rows.reduce((s, r) => s + r.x1 - r.x0, 0); let left = total * k;
  for (const r of rows) { const w = Math.min(r.x1 - r.x0, left); if (w <= 0) break; fn({ y: r.y }, r.x0, w); left -= w; }
}

// ---------- (v) thẻ chương ----------
function chuong(t) {
  const hit = S.hit ?? 0.15;
  const k = prog(t, hit, 0.45);
  const sc = t < hit ? 1.25 : lerp(1.12, 1, ease.out(k)) * (1 + 0.012 * prog(t, hit, S.duration));
  nen(t);
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(sc, sc); ctx.translate(-W / 2, -H / 2);
  const a = t < hit ? 0 : 1;
  ctx.globalAlpha = a; ctx.textAlign = 'center';
  ctx.font = font(700, 260); ctx.fillStyle = C.do; ctx.fillText(String(S.number), W / 2, 560);
  ctx.font = font(500, 26, '"Plex Mono"'); ctx.fillStyle = 'rgba(239,230,210,0.7)'; ctx.fillText(S.kicker ?? `CHƯƠNG ${S.number}`, W / 2, 300);
  ctx.font = font(700, 96); ctx.fillStyle = C.kem; ctx.fillText(S.title, W / 2, 720);
  ctx.fillStyle = C.do; const lw = 260 * ease.out(prog(t, hit + 0.1, 0.5)); ctx.fillRect(W / 2 - lw / 2, 760, lw, 6);
  ctx.restore();
  const fl = 1 - prog(t, hit, 0.25);
  if (t >= hit && fl > 0) { ctx.fillStyle = `rgba(255,245,225,${fl * 0.85})`; ctx.fillRect(0, 0, W, H); }
  drawCredit(ctx, S.source, 1);
}

// ---------- (vi) hook nền đen ----------
function hook(t) {
  if (TRONG) nen(t); else { ctx.fillStyle = QS ? C.toi : '#050403'; ctx.fillRect(0, 0, W, H); }
  // chớp sáng xa (vết sáng chân trời)
  for (const f of S.glows || []) {
    const k = (t - f.at) / (f.len ?? 0.7); if (k < 0 || k > 1) continue;
    const g = ctx.createRadialGradient(f.x ?? W * 0.7, f.y ?? H * 0.8, 0, f.x ?? W * 0.7, f.y ?? H * 0.8, 520);
    g.addColorStop(0, `rgba(255,170,90,${0.5 * (1 - k)})`); g.addColorStop(1, 'rgba(255,120,60,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  let shake = 0; let flash = 0;
  for (const l of S.lines) { const k = prog(t, l.at, 0.35); if (t >= l.at && k < 1) { shake = Math.max(shake, (1 - k) * (l.shake ?? 10)); flash = Math.max(flash, (1 - prog(t, l.at, 0.18)) * (l.flash ?? 0.5)); } }
  const dx = noise1(11, t * 30) * shake, dy = noise1(23, t * 30) * shake;
  ctx.save(); ctx.translate(dx, dy); ctx.textAlign = 'center';
  let y = S.y ?? 470;
  for (const l of S.lines) {
    const size = l.size ?? 120;
    const yy = l.y ?? y;
    const a = t >= l.at ? ease.out(prog(t, l.at, 0.12)) : 0;
    const out = 1 - prog(t, l.to ?? 1e9, 0.4);
    if (a * out > 0) {
      ctx.save(); ctx.globalAlpha = a * out;
      const sc = lerp(1.08, 1, ease.out(prog(t, l.at, 0.4))) * (1 + 0.01 * prog(t, l.at, 6));
      ctx.translate(W / 2, yy); ctx.scale(sc, sc);
      ctx.font = font(l.weight ?? 700, size); ctx.fillStyle = l.color ?? C.kem;
      ctx.letterSpacing = `${l.spacing ?? 4}px`; ctx.fillText(l.text, 0, 0);
      ctx.restore();
    }
    y += size * 1.25;
  }
  ctx.restore();
  if (flash > 0) { ctx.fillStyle = `rgba(255,248,235,${flash})`; ctx.fillRect(0, 0, W, H); }
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.7)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  drawCredit(ctx, S.source, 1);
}

// ---------- (vii) lower-third ----------
let lowerBg = null;
function lowerThird(t) {
  ctx.clearRect(0, 0, W, H);
  if (lowerBg) { ctx.drawImage(lowerBg, 0, 0, W, H); ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(0, 0, W, H); }
  const a = ease.out(prog(t, S.from ?? 0.3, 0.5)) * (1 - prog(t, S.to ?? S.duration - 0.6, 0.5));
  const k = ease.out(prog(t, S.from ?? 0.3, 0.7));
  const x = 110, y = S.y ?? 860;
  ctx.save(); ctx.globalAlpha = a;
  const g = ctx.createLinearGradient(0, y - 160, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.55)');
  ctx.fillStyle = g; ctx.fillRect(0, y - 160, 1300, H - y + 160);
  ctx.fillStyle = C.do; ctx.fillRect(x, y - 96, 7, 150 * k);
  ctx.font = font(500, 22, '"Plex Mono"'); ctx.fillStyle = 'rgba(239,230,210,0.85)'; ctx.fillText(S.role ?? '', x + 28, y - 66);
  ctx.save(); ctx.beginPath(); ctx.rect(x + 20, y - 60, 1700, 90); ctx.clip();
  ctx.font = font(700, 70); ctx.fillStyle = '#ffffff'; ctx.fillText(S.name, x + 26 - (1 - k) * 60, y + 10); ctx.restore();
  if (S.detail) { ctx.font = font(500, 26, 'BVP'); ctx.fillStyle = 'rgba(239,230,210,0.9)'; const lines = wrap(S.detail, 1300); lines.forEach((l, i) => ctx.fillText(l, x + 28, y + 54 + i * 34)); }
  ctx.restore();
  drawCredit(ctx, S.source, a);
}

// ---------- (viii) máy chữ: trích dẫn gõ từng ký tự ----------
let PLAN = null;
function mayChu(t) {
  nen(t);
  if (S.title) {
    ctx.save(); ctx.globalAlpha = ease.out(prog(t, 0.05, 0.5));
    ctx.font = font(500, 22, '"Plex Mono"'); ctx.fillStyle = 'rgba(239,230,210,0.7)'; ctx.fillText(S.kicker ?? '', 160, 150);
    ctx.font = font(700, 46); ctx.fillStyle = C.kem; ctx.fillText(S.title, 160, 212);
    ctx.fillStyle = C.do; ctx.fillRect(160, 232, 80 * ease.expoOut(prog(t, 0.15, 0.5)), 5);
    ctx.restore();
  }
  drawTypewriter(ctx, S, PLAN, t, C);
  drawCredit(ctx, S.source, 1);
}

// ---------- (ix) hai cột đối chiếu trên giấy (hai cuốn sổ, hai trang thư, hai loại con số) ----------
// cols: [{title, sub, from, dimAt, lines: [{text, at, size, color, strike}]}, {…}]
function haiCot(t) {
  nen(t); header(t);
  const top = S.title ? 300 : 200, gap = 80, cw = (W - 240 - gap) / 2;
  (S.cols || []).forEach((col, i) => {
    const x = 120 + i * (cw + gap);
    const A = appear(t, col.from ?? 0.2 + i * 0.15, { dur: 0.6, rise: 24, s0: 0.97 });
    const dim = col.dimAt != null ? 1 - 0.6 * ease.out(prog(t, col.dimAt, 0.5)) : 1;
    if (A.a <= 0) return;
    ctx.save(); ctx.globalAlpha = A.a * dim; ctx.translate(0, A.y);
    // trang: nền sáng hơn giấy, viền mực, gáy đỏ
    ctx.fillStyle = TRANG_SO; ctx.fillRect(x, top, cw, H - top - 150);
    ctx.strokeStyle = C.muc; ctx.lineWidth = 2; ctx.strokeRect(x, top, cw, H - top - 150);
    ctx.fillStyle = col.mau === 'ta' ? C.do : C.muc; ctx.fillRect(x, top, 10, H - top - 150);
    ctx.font = font(500, 22, '"Plex Mono"'); ctx.fillStyle = C.mucNhat; ctx.textBaseline = 'alphabetic';
    if (col.sub) ctx.fillText(col.sub, x + 44, top + 52);
    ctx.font = font(700, 50); ctx.fillStyle = col.mau === 'ta' ? C.do : C.muc; ctx.fillText(col.title ?? '', x + 44, top + 114);
    ctx.fillStyle = C.muc; ctx.fillRect(x + 44, top + 136, (cw - 88) * ease.expoOut(prog(t, (col.from ?? 0.2) + 0.2, 0.8)), 2);
    let y = top + 210;
    for (const l of col.lines || []) {
      const size = l.size ?? 40;
      ctx.font = font(l.weight ?? 600, size, l.font === 'serif' ? 'Lora' : 'BVP');
      const rows = wrap(l.text, cw - 100);
      const la = ease.out(prog(t, l.at ?? 0, 0.4));
      if (la > 0) {
        ctx.save(); ctx.globalAlpha *= la; ctx.fillStyle = l.color ?? C.muc;
        rows.forEach((r, j) => ctx.fillText(r, x + 44, y + j * size * 1.3 + (1 - la) * 10));
        if (l.strike != null) {
          const k = ease.inOut(prog(t, l.strike, 0.5));
          const w = Math.max(...rows.map((r) => ctx.measureText(r).width));
          if (k > 0) { ctx.fillStyle = C.do; ctx.fillRect(x + 38, y - size * 0.36, (w + 12) * k, Math.max(5, size * 0.09)); }
        }
        ctx.restore();
      }
      y += rows.length * size * 1.3 + (l.gap ?? 34);
    }
    ctx.restore();
  });
  source(t);
}

const TYPES = { 'hai-cot': haiCot, 'may-chu': mayChu, 'so-lieu': soLieu, lich, 'dong-thoi-gian': dongThoiGian, 'van-kien': vanKien, chuong, hook, 'lower-third': lowerThird };
function renderFrame(t) {
  t = clamp(t, 0, S.duration);
  const d = typeof S.date === 'string' ? { text: S.date } : S.date;
  if (ND_ON) {
    nd.batDau();
    TYPES_ND[S.type](t);
    if (d) nd.nhanNgay(d.text, ease.out(prog(t, d.from ?? 0.2, 0.5)), { phai: !!(S.title || S.kicker) });
  } else {
    TYPES[S.type](t);
    if (d) drawDateLabel(ctx, d.text, ease.out(prog(t, d.from ?? 0.2, 0.5)));
  }
  const fi = S.fadeIn ?? 0, fo = S.fadeOut ?? 0;
  const black = Math.max(fi ? 1 - prog(t, 0, fi) : 0, fo ? prog(t, S.duration - fo, fo) : 0);
  if (black > 0) { ctx.fillStyle = `rgba(0,0,0,${black})`; ctx.fillRect(0, 0, W, H); }
}

async function init() {
  if (LOAI_MAU.includes(S.type) && !ND_ON) throw new Error(`SHOT.type ${S.type} chỉ có trong hệ nhận diện (bỏ nhanDien:false)`);
  if (!TYPES[S.type] && !LOAI_MAU.includes(S.type)) throw new Error(`SHOT.type không hợp lệ: ${S.type}`);
  const dark = ['van-kien', 'chuong', 'may-chu'].includes(S.type);
  if (ND_ON) await nd.chuanBi({ kieu: KIEU_NEN[S.type] ?? 'sang', seed: S.seed ?? 5, nen: !['hook', 'lower-third'].includes(S.type) });
  else if (S.type !== 'hook' && S.type !== 'lower-third' && !TRONG) BG = XQ && !dark ? makeQuanPhuc(S.seed ?? 5, S.nenQd === 'ran-ri')
    : QS && !dark ? makeMapPaper(S.seed ?? 5)
    : makeTexture(dark ? (XQ ? '#1d2213' : QS ? '#1c1e16' : '#2a1c12') : C.giay, S.seed ?? 5, dark ? { fibers: false, blotch: 0.18, grain: 10 } : {});
  if (TRONG) { document.documentElement.style.background = 'transparent'; document.body.style.background = 'transparent'; }
  if (S.type === 'lower-third') { document.documentElement.style.background = 'transparent'; document.body.style.background = 'transparent'; }
  if (S.type === 'lower-third' && S.previewBg) { lowerBg = new Image(); lowerBg.src = S.previewBg; await lowerBg.decode(); REF.lowerBg = lowerBg; }
  await loadFonts();
  if (LOAI_MAU.includes(S.type)) REF.mau = await chuanBiMau(S, ctx, nd);
  if (S.type === 'may-chu' && ND_ON) { const SND = chuanBiMayChu(S); PLAN = planTyping(ctx, SND); REF.mc = { S: SND, plan: PLAN }; window.TYPING = PLAN.typing; window.TYPING_INFO = PLAN.blocks.map((b) => ({ start: b.start, end: b.end, cps: b.cps, wantCps: b.wantCps })); }
  else if (S.type === 'may-chu') { PLAN = planTyping(ctx, S); window.TYPING = PLAN.typing; window.TYPING_INFO = PLAN.blocks.map((b) => ({ start: b.start, end: b.end, cps: b.cps, wantCps: b.wantCps })); }
  mount(S.duration, renderFrame);
  if (ND_ON) dangKyDo(nd, S);
}
// Lỗi chuẩn bị (dữ liệu xấu, luật cứng) báo rõ ở console và window.LOI_THE; READY không bật nên bộ dựng dừng, không treo mà không nói gì.
init().catch((e) => { window.LOI_THE = String(e && e.message ? e.message : e); console.error(window.LOI_THE); throw e; });
