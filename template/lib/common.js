// Dùng chung cho mọi khối: thời gian, easing, nội suy keyframe, số ngẫu nhiên có seed, font, nhãn ngày, chú thích nguồn.
export const W = 1920, H = 1080;
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, k) => a + (b - a) * k;
export const prog = (t, a, d) => clamp((t - a) / d); // 0..1 trong khoảng [a, a+d]
export const ease = {
  linear: (x) => x,
  inOut: (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
  out: (x) => 1 - Math.pow(1 - x, 3),
  in: (x) => x * x * x,
  outBack: (x) => 1 + 2.70158 * Math.pow(x - 1, 3) + 1.70158 * Math.pow(x - 1, 2),
  sine: (x) => -(Math.cos(Math.PI * x) - 1) / 2,
  expoOut: (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x)),
  expoInOut: (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x < 0.5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2),
  backOut: (x) => { const c = 1.35; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); }, // vượt nhẹ ~6%
};

/**
 * Trạng thái xuất hiện/biến mất của một phần tử: a (độ mờ), s (tỉ lệ, vượt nhẹ rồi về 1), y (trượt lên, px).
 * Vào: ease-out nhanh, vượt có kiểm soát; ra: ease-in ngắn. from/to tính bằng giây.
 */
export function appear(t, from, { dur = 0.5, to = 1e9, out = 0.3, rise = 14, s0 = 0.86 } = {}) {
  const k = clamp((t - from) / dur);
  const o = clamp((t - to) / out);
  const a = ease.out(clamp(k / 0.6)) * (1 - ease.in(o));
  const s = lerp(s0, 1, ease.backOut(k)) * (1 - 0.04 * ease.in(o));
  return { a, s, y: (1 - ease.expoOut(k)) * rise + ease.in(o) * rise * 0.5 };
}
/** "Thắng" khi một con số dừng: phồng nhẹ rồi về (0 trước khi chạm). */
export function landPunch(t, at, dur = 0.35, amp = 0.07) {
  const k = clamp((t - at) / dur);
  return t < at ? 0 : amp * Math.sin(Math.PI * k) * (1 - k * 0.4);
}

/** Nội suy danh sách keyframe [{t, ...số}] với easing từng đoạn (k.ease, mặc định inOut). Trả object các trường số. */
export function keyframes(list, t) {
  if (t <= list[0].t) return { ...list[0] };
  const last = list[list.length - 1];
  if (t >= last.t) return { ...last };
  let i = 0;
  while (list[i + 1].t < t) i++;
  const a = list[i], b = list[i + 1];
  const k = (ease[b.ease || 'inOut'])((t - a.t) / (b.t - a.t));
  const o = {};
  for (const key of Object.keys(b)) {
    if (key === 't' || key === 'ease') continue;
    const va = a[key] ?? b[key], vb = b[key];
    if (typeof vb === 'number') {
      // góc: đi đường ngắn nhất
      if (key === 'heading') { let d = ((vb - va + 540) % 360) - 180; o[key] = va + d * k; }
      else o[key] = lerp(va, vb, k);
    } else o[key] = vb;
  }
  return o;
}

/** mulberry32: số ngẫu nhiên có seed (dựng lại y hệt mỗi lần render). */
export function rng(seed) {
  let a = seed >>> 0;
  return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
/** Nhiễu giá trị 1 chiều theo t (rung máy nhẹ). */
export function noise1(seed, x) {
  const i = Math.floor(x), f = x - i;
  const h = (n) => { const r = rng(seed * 7919 + n * 104729); return r() * 2 - 1; };
  const s = f * f * (3 - 2 * f);
  return lerp(h(i), h(i + 1), s);
}

export async function loadFonts() {
  const specs = ['700 40px Oswald', '500 40px Oswald', '400 40px Oswald', '400 20px BVP', '500 20px BVP', '600 20px BVP', '800 20px BVP',
    '400 20px Lora', '700 20px Lora', 'italic 400 20px Lora', '500 20px "Plex Mono"'];
  await Promise.all(specs.map((s) => document.fonts.load(s, 'Điện Biên Phủ ẮẰẲẴẶ ữ')));
  await document.fonts.ready;
}

/** Nhãn ngày góc trái trên kiểu CLD: hộp đen, chữ trắng in hoa. */
export function drawDateLabel(ctx, text, alpha = 1) {
  if (!text || alpha <= 0) return;
  // alpha dùng như tiến độ 0..1: vạch đỏ hiện, hộp quét sang phải, chữ hiện sau
  ctx.save();
  ctx.font = '600 42px Oswald';
  const tw = ctx.measureText(text).width;
  const k = ease.expoOut(clamp(alpha / 0.85));
  ctx.globalAlpha = clamp(alpha * 3);
  ctx.fillStyle = 'rgba(12,10,8,0.88)';
  ctx.fillRect(60, 52, (tw + 50) * k, 70);
  ctx.fillStyle = '#c93b2b';
  ctx.fillRect(60, 52, 8, 70);
  ctx.beginPath(); ctx.rect(60, 52, (tw + 50) * k, 70); ctx.clip();
  ctx.globalAlpha = clamp((alpha - 0.25) / 0.6);
  ctx.fillStyle = '#f3efe6';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 92 - (1 - k) * 16, 88);
  ctx.restore();
}

/** Chú thích nguồn góc phải dưới (nhỏ, có nền mờ để đọc được trên mọi nền). */
export function drawCredit(ctx, text, alpha = 1, dark = false) {
  if (!text || alpha <= 0) return;
  ctx.save();
  ctx.globalAlpha = alpha;
  const FS = 26, LH = 34; // >= 22 px ở 1080p
  ctx.font = `500 ${FS}px BVP`;
  ctx.textAlign = 'right';
  ctx.textBaseline = 'alphabetic';
  const maxW = 1500;
  // tự xuống dòng khi dài
  const words = text.split(' ');
  const lines = [];
  let cur = '';
  for (const w of words) { const n = cur ? cur + ' ' + w : w; if (ctx.measureText(n).width > maxW && cur) { lines.push(cur); cur = w; } else cur = n; }
  if (cur) lines.push(cur);
  let y = H - 30 - (lines.length - 1) * LH;
  if (!dark) {
    // dải gradient tối sau góc phải dưới để đọc được trên nền sáng
    const top = y - FS - 30, wMax = Math.max(...lines.map((l) => ctx.measureText(l).width));
    const rx = wMax / 2 + 320, ry = H - top + 60, cx = 1856 - wMax / 2;
    ctx.save(); ctx.translate(cx, H + 20); ctx.scale(rx, ry);
    const g = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);
    g.addColorStop(0, 'rgba(0,0,0,0.72)'); g.addColorStop(0.6, 'rgba(0,0,0,0.5)'); g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, 1, 0, Math.PI * 2); ctx.fill(); ctx.restore();
  }
  for (const l of lines) {
    if (!dark) { ctx.fillStyle = 'rgba(0,0,0,0.6)'; ctx.fillText(l, 1856 + 1.5, y + 1.5); }
    ctx.fillStyle = dark ? 'rgba(30,29,26,0.85)' : 'rgba(244,240,230,0.95)';
    ctx.fillText(l, 1856, y);
    y += LH;
  }
  ctx.restore();
}

/** Lắp hợp đồng dựng trang (tools/kit/dung-trang.mjs): SIZE, DURATION, renderFrame(t), READY. */
export function mount(duration, renderFrame) {
  // SHOT.fit = thời lượng dựng thật (s): mọi keyframe co/giãn đều theo tỉ lệ, chuyển động giữ trọn.
  // SHOT.tail = giây giữ thêm ở cuối (khung cuối đứng yên) để hoà sang cảnh sau.
  const S = window.SHOT || {};
  const base = renderFrame;
  let rf = base, dur = duration;
  if (S.fit) {
    const k = duration / S.fit;
    rf = (t) => base(Math.min(t * k, duration));
    dur = S.fit;
  }
  if (S.tail) { const inner = rf, end = dur; rf = (t) => inner(Math.min(t, end)); dur += S.tail; }
  window.SIZE = `${W}x${H}`;
  window.DURATION = dur;
  window.renderFrame = rf;
  renderFrame = rf;
  const q = new URLSearchParams(location.search);
  renderFrame(q.has('t') ? Number(q.get('t')) : 0);
  window.READY = true;
}
