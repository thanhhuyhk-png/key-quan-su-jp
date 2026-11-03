// Khối archival: ảnh tư liệu Ken Burns + grade + hạt phim có seed + vignette + rung nhẹ + nhãn ngày + chú thích nguồn.
// Chế độ 2.5D parallax (SHOT.layers): tách ảnh thành lớp bằng polygon (toạ độ 0..1 theo ảnh), chỉ TÁCH lớp,
// không vẽ thêm nội dung; vùng lộ sau tiền cảnh bù bằng nền phóng nhẹ + làm mờ. Bụi/khói mỏng vẽ bằng code.
// SHOT.lanhTu = true (ảnh có lãnh tụ): bỏ mọi hiệu ứng, chỉ Ken Burns zoom rất chậm toàn ảnh.
import { W, H, clamp, lerp, prog, ease, keyframes, rng, noise1, loadFonts, drawDateLabel, drawCredit, mount } from '../lib/common.js';

const S = window.SHOT;
const LT = !!S.lanhTu;
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const ctx = cv.getContext('2d');
const GRADES = {
  'bw-am': 'grayscale(1) sepia(0.28) contrast(1.12) brightness(0.96)',
  'bw': 'grayscale(1) contrast(1.15) brightness(0.95)',
  'goc': 'saturate(0.85) contrast(1.05)',
  'phai-mau': 'saturate(0.55) sepia(0.2) contrast(1.05) brightness(0.97)',
};
let img;
const grain = [];
const layerCanvas = document.createElement('canvas'); layerCanvas.width = W; layerCanvas.height = H;
const lctx = layerCanvas.getContext('2d');
const maskCanvas = document.createElement('canvas'); maskCanvas.width = W; maskCanvas.height = H;
const mctx = maskCanvas.getContext('2d');

function makeGrain(seed) {
  for (let k = 0; k < 6; k++) {
    const c = document.createElement('canvas'); c.width = 640; c.height = 360;
    const g = c.getContext('2d'), im = g.createImageData(640, 360), r = rng(seed * 31 + k);
    for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (r() + r() + r() - 1.5) * 120; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
    g.putImageData(im, 0, 0); grain.push(c);
  }
}

/** Khung Ken Burns -> phép biến đổi ảnh->màn: X = ox + ix * sc. */
function frameTransform(t) {
  const def = [{ t: 0, x: 0.5, y: 0.5, zoom: 1.03 }, { t: S.duration, x: 0.5, y: 0.5, zoom: LT ? 1.06 : 1.15, ease: LT ? 'linear' : 'sine' }];
  const k = keyframes(S.move ?? def, t);
  const zoom = LT ? Math.min(k.zoom, 1.05) : k.zoom; // lãnh tụ: zoom rất chậm, trần 5 %
  if (LT || S.contain) {
    // trọn ảnh giữa khung (không cắt), phóng quanh tâm ảnh
    const sc = Math.min(W / img.width, (H - (S.containPad ?? (LT ? 150 : 0))) / img.height) * zoom;
    return { sc, ox: W / 2 - img.width * sc / 2, oy: H / 2 - img.height * sc / 2, contain: true };
  }
  const sc = Math.max(W / img.width, H / img.height) * zoom;
  const vw = W / sc, vh = H / sc;
  const sx = clamp(k.x * img.width - vw / 2, 0, img.width - vw), sy = clamp(k.y * img.height - vh / 2, 0, img.height - vh);
  return { sc, ox: -sx * sc, oy: -sy * sc };
}

/** Vẽ ảnh với phép biến đổi + lệch parallax (dx, dy, phóng s quanh tâm màn). */
function drawImageTf(g, tf, dx = 0, dy = 0, s = 1) {
  g.save();
  g.translate(W / 2 + dx, H / 2 + dy); g.scale(s, s); g.translate(-W / 2, -H / 2);
  g.drawImage(img, tf.ox, tf.oy, img.width * tf.sc, img.height * tf.sc);
  g.restore();
}
function polyPath(g, poly, tf, dx, dy, s) {
  g.beginPath();
  poly.forEach(([u, v], i) => {
    const x = (tf.ox + u * img.width * tf.sc - W / 2) * s + W / 2 + dx;
    const y = (tf.oy + v * img.height * tf.sc - H / 2) * s + H / 2 + dy;
    i ? g.lineTo(x, y) : g.moveTo(x, y);
  });
  g.closePath();
}

function drawParallax(t, tf, filter) {
  // camera trôi: lệch theo tiến độ shot (sine), lớp sâu hơn lệch ít hơn
  const p = ease.sine(prog(t, 0, S.duration)) - 0.5;
  const dr = S.drift ?? { x: 28, y: 0, zoom: 0.035 };
  const off = (d) => ({ dx: -dr.x * d * p * 2, dy: -dr.y * d * p * 2, s: 1 + dr.zoom * d * (p + 0.5) });
  // nền: cả ảnh, phóng nhẹ + mờ để che vùng lộ sau các lớp trước
  const b = off(S.bgDepth ?? 0.15);
  ctx.save(); ctx.filter = `${filter} blur(${S.bgBlur ?? 3}px)`;
  drawImageTf(ctx, tf, b.dx, b.dy, b.s * 1.02);
  ctx.restore();
  for (const L of S.layers) {
    const o = off(L.depth);
    lctx.clearRect(0, 0, W, H);
    lctx.save(); lctx.filter = filter; drawImageTf(lctx, tf, o.dx, o.dy, o.s); lctx.restore();
    // mặt nạ mềm mép
    mctx.clearRect(0, 0, W, H);
    mctx.save(); mctx.filter = `blur(${L.feather ?? 3}px)`; mctx.fillStyle = '#fff';
    polyPath(mctx, L.poly, tf, o.dx, o.dy, o.s); mctx.fill(); mctx.restore();
    lctx.save(); lctx.globalCompositeOperation = 'destination-in'; lctx.drawImage(maskCanvas, 0, 0); lctx.restore();
    // L.shadow (px, tuỳ chọn): bóng mờ sau lớp để tách khối; chỉ bật khi mép lớp không nằm trên vùng trơn (trời)
    ctx.save(); if (L.shadow) { ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = L.shadow; } ctx.drawImage(layerCanvas, 0, 0); ctx.restore();
  }
}

function drawDust(t) {
  // bụi lơ lửng + khói mỏng: hạt có seed, vị trí là hàm của t
  const d = S.dust; if (!d) return;
  const r = rng(d.seed ?? 77);
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  for (let i = 0; i < (d.count ?? 70); i++) {
    const x0 = r() * W, y0 = r() * H, sp = 8 + r() * 26, sz = 1 + r() * 2.6, ph = r() * 6.28;
    const x = (x0 + t * sp * (d.wind ?? 1) + noise1(i + 5, t * 0.4 + ph) * 30 + W) % W;
    const y = (y0 - t * sp * 0.35 + noise1(i + 9, t * 0.3 + ph) * 20 + H) % H;
    ctx.globalAlpha = (d.opacity ?? 0.35) * (0.4 + 0.6 * (0.5 + 0.5 * Math.sin(t * 1.3 + ph)));
    ctx.fillStyle = '#efe6d2'; ctx.beginPath(); ctx.arc(x, y, sz, 0, Math.PI * 2); ctx.fill();
  }
  ctx.restore();
  if (d.smoke) {
    const rs = rng((d.seed ?? 77) + 1);
    ctx.save(); ctx.globalCompositeOperation = 'screen';
    for (let i = 0; i < 6; i++) {
      const bx = rs() * W, by = H * (0.45 + rs() * 0.5), R = 260 + rs() * 320, sp = 10 + rs() * 18;
      const x = bx + t * sp + noise1(40 + i, t * 0.25) * 60, y = by - t * 6;
      const g = ctx.createRadialGradient(x, y, 0, x, y, R);
      g.addColorStop(0, `rgba(220,214,200,${d.smoke * 0.18})`); g.addColorStop(1, 'rgba(220,214,200,0)');
      ctx.fillStyle = g; ctx.fillRect(x - R, y - R, R * 2, R * 2);
    }
    ctx.restore();
  }
}

function renderFrame(t) {
  t = clamp(t, 0, S.duration);
  const tf = frameTransform(t);
  const fl = !LT && S.flicker ? 1 + noise1(13, t * 24) * S.flicker : 1;
  const filter = LT ? (S.grade === 'goc' || !S.grade ? 'none' : GRADES[S.grade]) : `${GRADES[S.grade ?? 'bw-am']} brightness(${fl * (S.exposure ?? 1)})`;
  const sh = LT ? 0 : S.shake ?? 0;
  ctx.fillStyle = tf.contain ? '#0b0a08' : '#000'; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.translate(noise1(5, t * 9) * sh, noise1(9, t * 9) * sh);
  if (!LT && !tf.contain && S.layers && S.layers.length) drawParallax(t, tf, filter);
  else { ctx.save(); ctx.filter = filter; drawImageTf(ctx, tf, 0, 0, 1 + (sh && !tf.contain ? 0.01 : 0)); ctx.restore(); }
  if (tf.contain) { ctx.strokeStyle = 'rgba(0,0,0,0.85)'; ctx.lineWidth = 1; ctx.strokeRect(tf.ox - 0.5, tf.oy - 0.5, img.width * tf.sc + 1, img.height * tf.sc + 1); }
  ctx.restore();
  if (!LT) drawDust(t);
  if (!LT) {
    // hạt phim: ô nhiễu đổi theo khung (24 fps), lệch có seed
    const f = Math.floor(t * 24), r = rng((S.seed ?? 1) * 1000 + f);
    ctx.save(); ctx.globalAlpha = S.grain ?? 0.16; ctx.globalCompositeOperation = 'overlay';
    ctx.drawImage(grain[f % grain.length], -r() * 200, -r() * 120, W + 400, H + 240);
    ctx.restore();
    if (S.scratches !== false) {
      ctx.save(); ctx.strokeStyle = 'rgba(235,228,210,0.18)'; ctx.lineWidth = 1.2;
      for (let i = 0; i < 2; i++) if (r() < 0.35) { const x = r() * W; ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x + (r() - 0.5) * 6, H); ctx.stroke(); }
      ctx.restore();
    }
  }
  if (!LT) {
    const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.38, W / 2, H / 2, H * 1.0);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, `rgba(0,0,0,${S.vignette ?? 0.7})`);
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  }
  const d = typeof S.date === 'string' ? { text: S.date } : S.date;
  if (d) drawDateLabel(ctx, d.text, ease.out(prog(t, d.from ?? 0.3, 0.5)) * (1 - prog(t, d.to ?? 1e9, 0.4)));
  drawCredit(ctx, S.credit, 1); // chú thích nguồn có từ khung đầu, không animate
  for (const f of LT ? [] : S.flashes || []) {
    // chớp trắng (vd bộc phá): bật tức thì, tắt theo ease-out
    const k = (t - f.at) / (f.len ?? 0.5);
    if (k >= 0 && k <= 1) { ctx.fillStyle = `rgba(255,250,240,${(f.strength ?? 0.85) * Math.pow(1 - k, 2)})`; ctx.fillRect(0, 0, W, H); }
  }
  const fi = S.fadeIn ?? 0, fo = S.fadeOut ?? 0;
  const black = Math.max(fi ? 1 - prog(t, 0, fi) : 0, fo ? prog(t, S.duration - fo, fo) : 0);
  if (black > 0) { ctx.fillStyle = `rgba(0,0,0,${black})`; ctx.fillRect(0, 0, W, H); }
}

async function init() {
  img = new Image(); img.src = S.image; await img.decode();
  makeGrain(S.seed ?? 1);
  await loadFonts();
  mount(S.duration, renderFrame);
}
init();
