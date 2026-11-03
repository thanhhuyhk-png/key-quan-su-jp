// Thẻ "máy chữ": chữ hiện từng ký tự như gõ phím (font IBM Plex Mono, đủ dấu tiếng Việt), con trỏ khối nhấp nháy,
// nhịp gõ người thật có seed, nghỉ sau dấu phẩy/chấm, mỗi ký tự "đóng" xuống lệch nhẹ ±1 px, mực đậm nhạt khác nhau.
// Cấu hình (SHOT.type = 'may-chu'):
//   blocks: [{text, size, maxW, x, y, color, start | gap, deadline, cps: [min, max], strike: true | highlight: 'cụm'|true}]
//   start: giây bắt đầu gõ (hoặc gap sau khối trước); deadline: giây phải gõ xong, số âm = tính từ cuối cảnh (nhịp tự co trong 14–20 ký tự/giây)
//   cite, citeGap: dòng nguồn mờ vào sau cùng (không gõ)
// Xuất window.TYPING = [{t, ch, kind: 'key'|'space'|'newline'|'end'}] (giây theo trang) để khớp tiếng gõ.
import { clamp, prog, ease, rng } from '../lib/common.js';

const FONT = (s) => `500 ${s}px "Plex Mono"`;

/** Lập lịch gõ + bố cục. Trả {blocks: [{chars, end, ...}], typing}. Thuần, có seed. */
export function planTyping(ctx, S) {
  const r = rng(S.seed ?? 29);
  const out = [], typing = [];
  let prevEnd = 0;
  for (const b of S.blocks) {
    const size = b.size ?? 64, maxW = b.maxW ?? 1500, x0 = b.x ?? 160;
    ctx.font = FONT(size);
    const cw = ctx.measureText('M').width, lh = size * 1.42;
    // bố cục theo từ, ngắt dòng ở dấu cách
    const chars = [];
    let x = 0, line = 0;
    const words = b.text.split(' ');
    words.forEach((w, wi) => {
      if (x > 0 && (x + w.length) * cw > maxW) { chars[chars.length - 1].kind = 'newline'; x = 0; line++; }
      for (const ch of w) { chars.push({ ch, kind: 'key', x: x0 + x * cw, line }); x++; }
      if (wi < words.length - 1) { chars.push({ ch: ' ', kind: 'space', x: x0 + x * cw, line }); x++; }
    });
    // nhịp: đơn vị thô (±35 %) + nghỉ sau dấu câu
    const units = chars.map(() => 1 + 0.35 * (2 * r() - 1));
    const pause = chars.map((c, i) => (i < chars.length - 1 && /[,.;:!?…]/.test(c.ch) ? (c.ch === ',' ? 0.15 : 0.17) + r() * (c.ch === ',' ? 0.05 : 0.08) : 0)); // nghỉ 0,15–0,25 s
    const start = b.start ?? prevEnd + (b.gap ?? 0.25);
    const U = units.reduce((a, v) => a + v, 0), P = pause.reduce((a, v) => a + v, 0);
    const [cmin, cmax] = b.cps ?? [14, 20];
    const deadline = b.deadline != null && b.deadline < 0 ? S.duration + b.deadline : b.deadline; // âm = tính từ cuối cảnh
    let cps = deadline ? U / Math.max(0.1, deadline - start - P) : 17;
    const want = cps;
    cps = clamp(cps, cmin, cmax);
    let t = start;
    chars.forEach((c, i) => {
      t += units[i] / cps;
      c.t = t; c.jx = (r() * 2 - 1); c.jy = (r() * 2 - 1); c.ink = 0.78 + r() * 0.22;
      typing.push({ t, ch: c.kind === 'newline' ? '\n' : c.ch, kind: c.kind });
      t += pause[i];
    });
    const end = chars[chars.length - 1].t;
    out.push({ ...b, size, cw, lh, chars, start, end, cps, wantCps: want, y0: b.y ?? 420, lines: line + 1 });
    prevEnd = end + (b.after ?? 0);
  }
  typing.push({ t: out[out.length - 1].end, ch: '', kind: 'end' });
  return { blocks: out, typing };
}

/** Vẽ khung t. */
export function drawTypewriter(ctx, S, plan, t, C) {
  const last = plan.blocks[plan.blocks.length - 1];
  plan.blocks.forEach((b, bi) => {
    const yOf = (line) => b.y0 + line * b.lh;
    // tô vàng phía sau cụm (sau khi gõ xong)
    if (b.highlight) {
      const k = ease.inOut(prog(t, b.end + 0.15, 0.45));
      if (k > 0) {
        const txt = b.text; const ph = b.highlight === true ? txt : b.highlight;
        const s = txt.indexOf(ph);
        if (s >= 0) {
          const sel = b.chars.filter((c, i) => i >= s && i < s + ph.length && c.kind !== 'newline');
          const rows = {}; sel.forEach((c) => { (rows[c.line] ??= []).push(c); });
          let left = sel.length * k;
          for (const line of Object.keys(rows)) {
            const rc = rows[line], n = Math.min(rc.length, left); if (n <= 0) break;
            ctx.fillStyle = C.hop ?? 'rgba(229,169,59,0.92)';
            ctx.fillRect(rc[0].x - 8, yOf(+line) - b.size * 1.0, n * b.cw + 16, b.size * 1.28);
            left -= n;
          }
        }
      }
    }
    ctx.font = FONT(b.size); ctx.textBaseline = 'alphabetic';
    const hlOn = b.highlight && t > b.end + 0.35;
    const hs = b.highlight ? b.text.indexOf(b.highlight === true ? b.text : b.highlight) : -1;
    const hl = b.highlight === true ? b.text.length : (b.highlight || '').length;
    const dim = b.dimAfter != null ? 1 - 0.5 * ease.out(prog(t, b.end + b.dimAfter, 0.5)) : 1;
    b.chars.forEach((c, i) => {
      if (t < c.t || c.kind !== 'key') return;
      const age = t - c.t;
      const strikeIn = 1 - clamp(age / 0.06); // khung đầu "đóng" mạnh, lún 1 px
      ctx.globalAlpha = Math.max(c.ink, C.inkMin ?? 0) * dim;
      const inHl = hlOn && i >= hs && i < hs + hl;
      ctx.fillStyle = inHl ? C.muc : b.color ?? C.kem;
      ctx.fillText(c.ch, c.x + c.jx, yOf(c.line) + c.jy + strikeIn * 1.5);
    });
    ctx.globalAlpha = 1;
    // gạch đỏ cụm cũ
    if (b.strike) {
      const k = ease.inOut(prog(t, b.end + 0.15, 0.35));
      if (k > 0) {
        const rows = {}; b.chars.forEach((c) => { if (c.kind !== 'newline') (rows[c.line] ??= []).push(c); });
        for (const line of Object.keys(rows)) {
          const rc = rows[line];
          if (C.gach) C.gach(rc[0].x - 6, yOf(+line) - b.size * 0.36, (rc.length * b.cw + 12) * k, Math.max(6, b.size * 0.09));
          else { ctx.fillStyle = C.do; ctx.fillRect(rc[0].x - 6, yOf(+line) - b.size * 0.36, (rc.length * b.cw + 12) * k, Math.max(6, b.size * 0.09)); }
        }
      }
    }
    // con trỏ khối: đặc khi đang gõ, nhấp nháy 2 Hz khi chờ; chỉ ở khối đang hoạt động
    const active = t >= b.start - 0.3 && (bi === plan.blocks.length - 1 ? true : t < plan.blocks[bi + 1].start);
    if (active && !(S.cursorOffAfter != null && t > last.end + S.cursorOffAfter)) {
      const typed = b.chars.filter((c) => c.t <= t);
      const lc = typed.length ? typed[typed.length - 1] : null;
      const cx = lc ? lc.x + b.cw * (lc.kind === 'newline' ? 0 : 1) : b.chars[0].x;
      const cl = lc ? (lc.kind === 'newline' ? lc.line + 1 : lc.line) : 0;
      const cxx = lc && lc.kind === 'newline' ? b.x ?? 160 : cx;
      const typing = lc && t - lc.t < 0.35 && t < b.end + 0.05;
      if (typing || Math.floor((t - b.start) * 2) % 2 === 0) {
        ctx.fillStyle = C.con ?? 'rgba(239,230,210,0.85)';
        ctx.fillRect(cxx + 4, yOf(cl) - b.size * 0.8, b.cw * 0.6, b.size * 0.95);
      }
    }
  });
  if (S.cite) {
    const a = ease.out(prog(t, last.end + (S.citeGap ?? 0.35), 0.6));
    ctx.save(); ctx.globalAlpha = a; ctx.font = `500 ${C.citeSize ?? 30}px BVP`; ctx.fillStyle = C.cite ?? 'rgba(239,230,210,0.85)';
    ctx.fillText(S.cite, last.x ?? 160, last.y0 + last.lines * last.lh + 30 + (1 - a) * 8); ctx.restore();
  }
}
