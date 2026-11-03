// Biểu tượng bộ đội Quân đội nhân dân Việt Nam 1954 và khẩu lựu pháo 105 ly — đồ hoạ minh họa vẽ bằng code
// (kiểu ký hiệu bản đồ, phẳng, không tả thực). Mũ nan có lưới + cành lá ngụy trang, quần áo xanh úa,
// dép cao su, súng trường đeo vai. Toạ độ: chân nhân vật tại (x, y), s = chiều cao hình (px).
import { rng, clamp } from './common.js';

const C = {
  ao: '#5f7342', quan: '#4c5c33', dep: '#26221c', da: '#a98462', mu: '#9c9566', muDam: '#6f6a45', la: '#3e6a2a', la2: '#557f33',
  sung: '#2b2119', vien: 'rgba(16,16,10,0.85)', phao: '#4a5734', phaoDam: '#323c22', lop: '#1b1b18', day: '#c9b98a',
};

function shadow(ctx, w) { ctx.fillStyle = 'rgba(0,0,0,0.32)'; ctx.beginPath(); ctx.ellipse(0, 0, w, w * 0.22, 0, 0, Math.PI * 2); ctx.fill(); }

function helmet(ctx, u, seed) {
  // mũ nan: chóp tròn + vành rộng, lưới đan, cành lá cắm
  ctx.fillStyle = C.mu; ctx.strokeStyle = C.vien; ctx.lineWidth = 1.2 * u;
  ctx.beginPath(); ctx.ellipse(0, -93 * u, 16 * u, 4 * u, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  ctx.beginPath(); ctx.ellipse(0, -94 * u, 11 * u, 10 * u, 0, Math.PI, Math.PI * 2); ctx.fill(); ctx.stroke();
  ctx.strokeStyle = C.muDam; ctx.lineWidth = 0.9 * u;
  for (let k = -2; k <= 2; k++) { ctx.beginPath(); ctx.moveTo(k * 4.5 * u - 4 * u, -94 * u); ctx.lineTo(k * 4.5 * u + 4 * u, -103 * u); ctx.stroke(); }
  const r = rng(seed);
  for (let k = 0; k < 4; k++) {
    const a = -Math.PI * (0.15 + 0.7 * r());
    const x = Math.cos(a) * 10 * u, y = -94 * u + Math.sin(a) * 9 * u;
    ctx.fillStyle = k % 2 ? C.la : C.la2;
    ctx.beginPath(); ctx.ellipse(x, y - 3 * u, 3.2 * u, 7 * u, a + Math.PI / 2 + (r() - 0.5), 0, Math.PI * 2); ctx.fill();
  }
}

/** Bộ đội. pose: 'walk' (đi, súng đeo vai) | 'pull' (nghiêng người kéo dây). facing 1 = đi sang phải. */
export function drawSoldier(ctx, x, y, s, { phase = 0, facing = 1, pose = 'walk', seed = 1, alpha = 1 } = {}) {
  const u = s / 105;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(x, y);
  shadow(ctx, 20 * u);
  ctx.scale(facing, 1);
  const lean = pose === 'pull' ? 0.38 : 0.04;
  ctx.rotate(lean);
  ctx.translate(0, -Math.abs(Math.sin(phase)) * 2 * u);
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const sw = Math.sin(phase) * (pose === 'pull' ? 0.45 : 0.38);
  // chân
  for (const k of [-1, 1]) {
    const a = sw * k;
    const fx = Math.sin(a) * 46 * u, fy = Math.cos(a) * 46 * u;
    ctx.strokeStyle = C.vien; ctx.lineWidth = 11 * u; ctx.beginPath(); ctx.moveTo(0, -48 * u); ctx.lineTo(fx, -48 * u + fy); ctx.stroke();
    ctx.strokeStyle = C.quan; ctx.lineWidth = 8.5 * u; ctx.beginPath(); ctx.moveTo(0, -48 * u); ctx.lineTo(fx, -48 * u + fy); ctx.stroke();
    ctx.fillStyle = C.dep; ctx.fillRect(fx - 3 * u, -48 * u + fy - 2 * u, 10 * u, 3.5 * u); // dép cao su
  }
  // súng trường đeo vai (sau lưng)
  if (pose === 'walk') {
    ctx.strokeStyle = C.sung; ctx.lineWidth = 3.6 * u;
    ctx.beginPath(); ctx.moveTo(-12 * u, -50 * u); ctx.lineTo(5 * u, -112 * u); ctx.stroke();
    ctx.lineWidth = 6 * u; ctx.beginPath(); ctx.moveTo(-12 * u, -50 * u); ctx.lineTo(-8 * u, -62 * u); ctx.stroke();
  }
  // thân áo
  ctx.fillStyle = C.ao; ctx.strokeStyle = C.vien; ctx.lineWidth = 1.4 * u;
  ctx.beginPath(); ctx.moveTo(-11 * u, -46 * u); ctx.lineTo(11 * u, -46 * u); ctx.lineTo(10 * u, -82 * u); ctx.lineTo(-10 * u, -82 * u); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#3b3322'; ctx.fillRect(-11 * u, -53 * u, 22 * u, 3.5 * u); // thắt lưng
  ctx.strokeStyle = '#3b3322'; ctx.lineWidth = 2 * u; ctx.beginPath(); ctx.moveTo(-9 * u, -80 * u); ctx.lineTo(9 * u, -54 * u); ctx.stroke(); // dây đeo
  // tay
  const hand = pose === 'pull' ? [24 * u, -66 * u] : [Math.sin(-sw) * 16 * u, -56 * u];
  ctx.strokeStyle = C.vien; ctx.lineWidth = 8.5 * u; ctx.beginPath(); ctx.moveTo(2 * u, -78 * u); ctx.lineTo(hand[0], hand[1]); ctx.stroke();
  ctx.strokeStyle = C.ao; ctx.lineWidth = 6.5 * u; ctx.beginPath(); ctx.moveTo(2 * u, -78 * u); ctx.lineTo(hand[0], hand[1]); ctx.stroke();
  ctx.fillStyle = C.da; ctx.beginPath(); ctx.arc(hand[0], hand[1], 3 * u, 0, Math.PI * 2); ctx.fill();
  // đầu (phẳng, không chi tiết mặt) + mũ nan
  ctx.fillStyle = C.da; ctx.strokeStyle = C.vien; ctx.lineWidth = 1.2 * u;
  ctx.beginPath(); ctx.arc(1 * u, -88 * u, 7.5 * u, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  helmet(ctx, u, seed);
  ctx.restore();
}

/** Vị trí tay (đầu dây) của người kéo trên màn hình. */
export function pullHand(x, y, s, facing) {
  const u = s / 105, a = 0.38, hx = 24 * u, hy = -66 * u;
  return [x + facing * (hx * Math.cos(a) - hy * Math.sin(a)), y + hx * Math.sin(a) + hy * Math.cos(a)];
}

/** Lựu pháo 105 ly: hai càng (kéo phía trước), bánh lớn, tấm chắn, nòng quay về sau. Trả toạ độ đầu càng (móc dây). */
export function drawHowitzer(ctx, x, y, s, { facing = 1, wheel = 0, alpha = 1 } = {}) {
  const u = s / 105, R = 23 * u;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(x, y);
  shadow(ctx, 60 * u);
  ctx.scale(facing, 1);
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const line = (pts, w, col) => {
    ctx.beginPath(); pts.forEach((p, i) => (i ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])));
    ctx.strokeStyle = C.vien; ctx.lineWidth = w + 2.5 * u; ctx.stroke();
    ctx.strokeStyle = col; ctx.lineWidth = w; ctx.stroke();
  };
  // hai càng chụm về phía trước
  line([[0, -R], [72 * u, -4 * u]], 6 * u, C.phaoDam);
  line([[6 * u, -R + 4 * u], [70 * u, -2 * u]], 5 * u, C.phao);
  // nòng + bộ hãm lùi, quay về sau
  line([[8 * u, -R - 9 * u], [-92 * u, -R - 26 * u]], 7.5 * u, C.phao);
  line([[4 * u, -R - 2 * u], [-52 * u, -R - 13 * u]], 9 * u, C.phaoDam);
  line([[-92 * u, -R - 26 * u], [-97 * u, -R - 27 * u]], 10 * u, C.phaoDam);
  // tấm chắn
  ctx.fillStyle = C.phao; ctx.strokeStyle = C.vien; ctx.lineWidth = 1.5 * u;
  ctx.beginPath(); ctx.moveTo(-4 * u, -R + 8 * u); ctx.lineTo(6 * u, -R + 8 * u); ctx.lineTo(1 * u, -R - 48 * u); ctx.lineTo(-9 * u, -R - 46 * u); ctx.closePath(); ctx.fill(); ctx.stroke();
  // bánh xe lớn
  ctx.fillStyle = C.lop; ctx.beginPath(); ctx.arc(0, -R, R, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = C.phao; ctx.beginPath(); ctx.arc(0, -R, R * 0.66, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = C.phaoDam; ctx.lineWidth = 2.2 * u;
  for (let k = 0; k < 6; k++) { const a = wheel + (k * Math.PI) / 3; ctx.beginPath(); ctx.moveTo(0, -R); ctx.lineTo(Math.cos(a) * R * 0.64, -R + Math.sin(a) * R * 0.64); ctx.stroke(); }
  ctx.fillStyle = C.phaoDam; ctx.beginPath(); ctx.arc(0, -R, 4 * u, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
  return [x + facing * 72 * u, y - 4 * u];
}

/**
 * Đặt một đội hình dọc đường đã chiếu lên màn hình.
 * path: {pts:[[x,y]...], len:[...]} (độ dài cộng dồn, px); head: độ dài (px) tới người đi đầu.
 * kind 'cannon': n người kéo dây phía trước + pháo + 2 người đẩy sau; kind 'file': hàng bộ đội đi.
 */
export function drawTroopGroup(ctx, path, head, t, { kind = 'file', count = 6, size = 34, gap = 30, seed = 3, alpha = 1 } = {}) {
  const total = path.len[path.len.length - 1];
  if (!(total > 0)) return;
  const at = (L) => {
    L = clamp(L, 0, total);
    let i = 1; while (i < path.len.length - 1 && path.len[i] < L) i++;
    const a = path.pts[i - 1], b = path.pts[i];
    const k = clamp((L - path.len[i - 1]) / Math.max(1e-6, path.len[i] - path.len[i - 1]));
    return { x: a[0] + (b[0] - a[0]) * k, y: a[1] + (b[1] - a[1]) * k, dx: b[0] - a[0] };
  };
  const items = [];
  const fade = (L) => clamp((L + gap) / gap) * alpha;
  if (kind === 'cannon') {
    const pullers = [];
    for (let i = 0; i < count; i++) pullers.push(head - i * gap * 0.8);
    const gunL = head - count * gap * 0.8 - gap * 1.1;
    const g = at(gunL), gf = g.dx >= 0 ? 1 : -1;
    items.push({ y: g.y, draw: () => {
      const hook = drawHowitzer(ctx, g.x, g.y, size * 0.95, { facing: gf, wheel: (-gunL / (size * 0.22)) * gf, alpha: fade(gunL) });
      // dây kéo: từ đầu càng qua tay từng người
      ctx.save(); ctx.globalAlpha *= fade(gunL); ctx.strokeStyle = C.day; ctx.lineWidth = Math.max(1.5, size * 0.04);
      ctx.beginPath(); ctx.moveTo(hook[0], hook[1]);
      for (let i = pullers.length - 1; i >= 0; i--) { const p = at(pullers[i]); const h = pullHand(p.x, p.y, size, p.dx >= 0 ? 1 : -1); ctx.lineTo(h[0], h[1]); }
      ctx.stroke(); ctx.restore();
    } });
    pullers.forEach((L, i) => { const p = at(L); items.push({ y: p.y - 0.01, draw: () => drawSoldier(ctx, p.x, p.y, size, { pose: 'pull', facing: p.dx >= 0 ? 1 : -1, phase: t * 6 + i * 1.3, seed: seed + i, alpha: fade(L) }) }); });
    for (let j = 0; j < 2; j++) { const L = gunL - gap * (1.0 + j * 0.7); const p = at(L); items.push({ y: p.y + 0.02, draw: () => drawSoldier(ctx, p.x, p.y, size, { pose: 'pull', facing: p.dx >= 0 ? 1 : -1, phase: t * 6 + j * 2.1, seed: seed + 20 + j, alpha: fade(L) }) }); }
  } else {
    for (let i = 0; i < count; i++) { const L = head - i * gap; const p = at(L); items.push({ y: p.y, draw: () => drawSoldier(ctx, p.x, p.y, size, { pose: 'walk', facing: p.dx >= 0 ? 1 : -1, phase: t * 7 + i * 1.7, seed: seed + i, alpha: fade(L) }) }); }
  }
  items.sort((a, b) => a.y - b.y).forEach((it) => it.draw());
}
