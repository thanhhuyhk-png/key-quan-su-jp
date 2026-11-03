// Các loại thẻ của khối cards vẽ theo hệ nhận diện «bảng tác chiến» (lib/nhan-dien.js).
// Cùng tên `type` và cùng tham số với bản cũ; thêm: S.nam (năm mờ), S.moc / S.nhip (mốc hiện theo lời, xem lib/nhip-hien.js),
// S.logo = false (tắt logo), S.nhanDien = false (dùng bản vẽ cũ của cards.js).
import { W, H, lerp, prog, ease, rng, noise1, appear, landPunch } from './common.js';
import { MAU, CO, LUOI, noiDungW, font, ngatDong, mauChu } from './nhan-dien.js';
import { mocPhanTu } from './nhip-hien.js';
import { drawTypewriter } from '../cards/typewriter.js';
import { taoCacTheMau, KIEU_NEN_MAU } from '../cards/mau-moi.js';

const fmtNum = (v, dec = 0) => v.toFixed(dec).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, '.');
const namCua = (S) => S.nam ?? (/^\d{4}/.test(S.tag ?? '') ? S.tag.slice(0, 4) : S.year ? String(S.year) : null);

/** Kiểu nền theo loại thẻ: thẻ chữ dài dùng olive sâu hơn. */
export const KIEU_NEN = { 'van-kien': 'toi', chuong: 'toi', 'may-chu': 'toi', hook: 'toi', ...KIEU_NEN_MAU };

/** Bản S cho thẻ máy chữ: sàn cỡ chữ, màu đọc được trên olive. */
export function chuanBiMayChu(S) {
  return { ...S, blocks: S.blocks.map((b) => ({ ...b, size: Math.max(b.size ?? 64, 46), color: mauChu(b.color) })) };
}
export const mauMayChu = (nd) => ({ kem: MAU.kem, do: MAU.gach, muc: MAU.than, hop: MAU.vang, con: MAU.kem, cite: MAU.kemPhu, citeSize: 40, inkMin: 0.94, gach: (x, y, w, h) => nd.gach(x, y, w, h) });

export function taoCacThe(nd, ctx, S, ref = {}) {
  const cuoi = (t, o) => nd.chan(t, o);
  const MC = mauMayChu(nd);
  // Phần mở đầu chung: nền, năm mờ, đầu thẻ. Trả y nơi nội dung bắt đầu.
  const mo = (t, o = {}) => { nd.nen(t); nd.namMo(t, o.nam ?? namCua(S)); return nd.dauThe(t, o) + 44; };

  // ---------- số liệu ----------
  function soLieu(t) {
    const y0 = mo(t);
    const items = S.items || [], n = items.length;
    const mode = S.layout ?? (n > 1 ? 'row' : 'single');
    const moc = mocPhanTu(S, n, items.map((i) => i.from));
    nd.ghiNhip(moc);
    const top = y0, bot = LUOI.noiDungDuoi;
    items.forEach((it, i) => {
      const from = moc[i];
      const A = appear(t, from, { dur: 0.5, to: it.to ?? 1e9, rise: 30, s0: 0.92 }); if (A.a <= 0) return;
      const dur = it.count === false ? 0.12 : it.dur ?? 1.6;
      const v = lerp(it.start ?? 0, it.value, ease.expoOut(prog(t, from, dur)));
      const landed = it.count === false || t >= from + dur * 0.92;
      const txt = fmtNum(landed ? it.value : Math.round(v), it.dec ?? 0) + (it.suffix ?? '');
      const punch = landPunch(t, from + dur * 0.92, 0.35, 0.06);
      const colW = (noiDungW) / (mode === 'row' ? n : 1);
      const size = Math.max(it.size ?? (mode === 'row' ? (n >= 3 ? CO.soNho : 190) : CO.so), 140);
      const cx = mode === 'row' ? LUOI.le + colW * (i + 0.5) : W / 2;
      const cy = top + (bot - top) * 0.5 + size * 0.2;
      if (mode === 'row') nd.bang(LUOI.le + colW * i + 14, top - 10, colW - 28, bot - top + 10, { a: A.a });
      ctx.save(); ctx.globalAlpha = A.a; ctx.textAlign = 'center';
      ctx.save(); ctx.translate(cx, cy + A.y); ctx.scale(A.s + punch, A.s + punch);
      ctx.font = font(700, size); ctx.fillStyle = MAU.kem; ctx.fillText(txt, 0, 0); ctx.restore();
      const u = ease.expoOut(prog(t, from + dur * 0.92, 0.45));
      if (u > 0) { ctx.font = font(700, size); const tw = ctx.measureText(txt).width; ctx.fillStyle = MAU.do; ctx.fillRect(cx - tw / 2, cy + size * 0.07, tw * u, 8); }
      if (it.prefix) { ctx.font = font(600, Math.max(CO.thanPhu, size * 0.26)); ctx.fillStyle = MAU.vang; ctx.fillText(it.prefix, cx, cy - size * 0.92); }
      const U = appear(t, from + 0.25, { dur: 0.5, to: it.to ?? 1e9, rise: 12 });
      ctx.globalAlpha = A.a * U.a;
      const us = Math.max(CO.than, size * 0.28);
      let yy = cy + size * 0.07 + 70;
      if (it.unit) { yy = cy + size * 0.07 + 30 + us * 0.95; ctx.font = font(600, us); ctx.fillStyle = MAU.vang; ctx.fillText(it.unit, cx, yy + U.y); yy += us + 14; }
      const Lb = appear(t, from + 0.4, { dur: 0.5, to: it.to ?? 1e9, rise: 12 });
      ctx.globalAlpha = A.a * Lb.a; ctx.font = font(500, CO.than, 'BVP'); ctx.fillStyle = MAU.kem;
      ngatDong(ctx, it.label ?? '', mode === 'row' ? colW - 70 : 1200).forEach((l, j) => ctx.fillText(l, cx, yy + 6 + j * CO.than * 1.2));
      ctx.restore();
    });
    cuoi(t);
  }

  // ---------- lịch ----------
  function lich(t) {
    const y0 = mo(t, { nam: String(S.year) });
    const { month, year, day } = S;
    nd.ghiNhip([0.3, S.circleAt ?? 1.4, ...(S.note ? [(S.circleAt ?? 1.4) + 0.7] : [])]);
    const first = new Date(Date.UTC(year, month - 1, 1)).getUTCDay(), days = new Date(Date.UTC(year, month, 0)).getUTCDate();
    const off = (first + 6) % 7, rows = Math.ceil((off + days) / 7);
    const cw = 130, top = y0 + 6, headH = 130;
    const ch = Math.min(96, (LUOI.noiDungDuoi - top - headH) / rows);
    const wCal = cw * 7, x0 = S.note ? LUOI.le + 20 : (W - wCal) / 2;
    const a = ease.out(prog(t, 0.3, 0.6));
    nd.bang(x0 - 24, top, wCal + 48, headH + ch * rows + 20, { a });
    ctx.save(); ctx.globalAlpha = a; ctx.textBaseline = 'alphabetic';
    ctx.font = font(700, 54); ctx.fillStyle = MAU.vang; ctx.fillText(`THÁNG ${month} · ${year}`, x0, top + 62);
    ctx.font = font(500, CO.toiThieu); ctx.textAlign = 'center'; ctx.fillStyle = MAU.kemPhu;
    ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'].forEach((h, i) => ctx.fillText(h, x0 + cw * i + cw / 2, top + 114));
    ctx.fillStyle = MAU.ve; ctx.fillRect(x0, top + 126, wCal, 3);
    ctx.textBaseline = 'middle';
    let cx = 0, cy = 0;
    for (let d = 1; d <= days; d++) {
      const idx = off + d - 1, col = idx % 7, row = Math.floor(idx / 7);
      const x = x0 + cw * col + cw / 2, y = top + headH + ch * row + ch / 2 + 4;
      ctx.globalAlpha = a * ease.out(prog(t, 0.35 + d * 0.012, 0.3));
      ctx.font = font(d === day ? 700 : 500, d === day ? 58 : 50); ctx.fillStyle = d === day ? MAU.vang : MAU.kem;
      ctx.fillText(String(d), x, y);
      if (d === day) { cx = x; cy = y; }
    }
    ctx.restore();
    const circleAt = S.circleAt ?? 1.4, k = ease.inOut(prog(t, circleAt, 0.8));
    if (k > 0) {
      ctx.save(); ctx.strokeStyle = MAU.do; ctx.lineWidth = 8; ctx.lineCap = 'round'; ctx.beginPath();
      const r = rng(7);
      for (let s = 0; s <= 80 * k; s++) { const ang = -2.2 + (s / 80) * Math.PI * 2.15, rr = 54 + Math.sin(s * 0.3) * 1.5 + r() * 1.2; const x = cx + Math.cos(ang) * rr * 1.1, y = cy + Math.sin(ang) * rr * 0.92; s ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
      ctx.stroke(); ctx.restore();
    }
    if (S.note) {
      const nx = x0 + wCal + 70, na = ease.out(prog(t, circleAt + 0.7, 0.5)), maxW = W - LUOI.le - nx;
      ctx.save(); ctx.globalAlpha = na; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
      ctx.font = font(700, 60); ctx.fillStyle = MAU.vang;
      const ls = ngatDong(ctx, S.note, maxW); let yy = cy - 20;
      ls.forEach((l) => { ctx.fillText(l, nx, yy); yy += 68; });
      if (S.noteSub) { ctx.font = font(500, CO.than, 'BVP'); ctx.fillStyle = MAU.kem; ngatDong(ctx, S.noteSub, maxW).forEach((l) => { ctx.fillText(l, nx, yy + 8); yy += 56; }); }
      ctx.restore();
    }
    cuoi(t);
  }

  // ---------- dòng thời gian ----------
  const dayNo = ([d, m, y]) => Date.UTC(y, m - 1, d) / 86400000;
  function dongThoiGian(t) {
    const y0 = mo(t);
    const A = dayNo(S.axis.from), B = dayNo(S.axis.to), lanes = S.lanes;
    const x0 = 420, x1 = W - LUOI.le - 40, X = (d) => lerp(x0, x1, (dayNo(d) - A) / (B - A));
    const moc = mocPhanTu(S, lanes.length, lanes.map((l, i) => l.activeFrom ?? 0.8 + i * 0.4));
    nd.ghiNhip(moc);
    const top = y0 + 90, gap = Math.min(200, (945 - top - 70) / Math.max(1, lanes.length));
    nd.bang(LUOI.le, y0 - 20, noiDungW, 945 - y0 + 20, { a: ease.out(prog(t, 0.25, 0.5)) });
    const ay = top + gap * lanes.length - 20;
    ctx.save(); ctx.globalAlpha = ease.out(prog(t, 0.3, 0.5));
    ctx.fillStyle = MAU.kemPhu; ctx.fillRect(x0, ay, x1 - x0, 3);
    ctx.font = font(500, CO.toiThieu); ctx.textAlign = 'center';
    for (const tk of S.axis.ticks || []) { const x = X(tk.d); ctx.fillRect(x, ay - 10, 3, 20); ctx.fillText(tk.label, x, ay + 52); }
    ctx.restore();
    lanes.forEach((ln, i) => {
      const y = top + gap * i, from = moc[i];
      const on = t >= from && t < (ln.activeTo ?? 1e9);
      const la = ease.out(prog(t, 0.4 + i * 0.15, 0.5));
      ctx.save(); ctx.globalAlpha = la; ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
      ctx.font = font(700, 50); ctx.fillStyle = on ? MAU.vang : MAU.kem; ctx.fillText(ln.name, LUOI.le + 30, y);
      ctx.fillStyle = 'rgba(244,238,218,0.22)'; ctx.fillRect(x0, y - 2, x1 - x0, 4);
      const k = ease.inOut(prog(t, from, ln.grow ?? 1.0)), xs = X(ln.start), xe = X(ln.end), col = on ? MAU.do : MAU.kem;
      if (ln.open) { const gr = ctx.createLinearGradient(xs, 0, xe, 0); gr.addColorStop(0, col); gr.addColorStop(0.7, col); gr.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = gr; } else ctx.fillStyle = col;
      ctx.fillRect(xs, y - 10, Math.max(0, (xe - xs) * k), 20);
      ctx.fillStyle = col; ctx.beginPath(); ctx.arc(xs, y, 15, 0, Math.PI * 2); ctx.fill();
      if (k > 0.98 && !ln.open) { ctx.beginPath(); ctx.arc(xe, y, 15, 0, Math.PI * 2); ctx.fill(); }
      ctx.globalAlpha *= ease.out(prog(t, from + 0.4, 0.5)); ctx.textBaseline = 'alphabetic';
      const txt = (s, f, c, yy) => { ctx.font = f; ctx.fillStyle = c; const w = ctx.measureText(s).width; ctx.fillText(s, Math.min(xs, W - LUOI.le - 40 - w), yy); };
      txt(ln.dates ?? '', font(600, CO.thanPhu + 2, 'BVP'), MAU.vang, y - 30);
      if (ln.note) txt(ln.note, font(500, CO.toiThieu + 2, 'BVP'), MAU.kem, y + 62);
      ctx.restore();
    });
    cuoi(t);
  }

  // ---------- văn kiện ----------
  const findPhrase = (words, phrase) => { const p = phrase.split(' '); for (let i = 0; i + p.length <= words.length; i++) if (p.every((w, j) => words[i + j] === w)) return i; return -1; };
  function drawSpan(ps, k, fn) {
    const rows = []; for (const p of ps) { const r = rows.find((q) => q.y === p.y); if (r) r.x1 = p.x + p.ww; else rows.push({ y: p.y, x0: p.x, x1: p.x + p.ww }); }
    let left = rows.reduce((s, r) => s + r.x1 - r.x0, 0) * k;
    for (const r of rows) { const w = Math.min(r.x1 - r.x0, left); if (w <= 0) break; fn(r.y, r.x0, w); left -= w; }
  }
  // Hộp vàng quét qua cụm từ trái sang phải (theo bề rộng, qua từng dòng): từ đổi sang chữ than khi hộp đã phủ hết từ đó;
  // từ chưa phủ vẫn là chữ kem trên nền olive, nên chữ không bao giờ chìm trong lúc hộp quét.
  function daQuet(words, pos, m, i, t) {
    const s0 = findPhrase(words, m.phrase), n = m.phrase.split(' ').length;
    if (s0 < 0 || i < s0 || i >= s0 + n) return false;
    const rows = []; for (const p of pos.slice(s0, s0 + n)) { const r = rows.find((q) => q.y === p.y); if (r) r.x1 = p.x + p.ww; else rows.push({ y: p.y, x0: p.x, x1: p.x + p.ww }); }
    const total = rows.reduce((a, r) => a + r.x1 - r.x0, 0), p = pos[i], ri = rows.findIndex((q) => q.y === p.y);
    const den = rows.slice(0, ri).reduce((a, r) => a + r.x1 - r.x0, 0) + (p.x + p.ww - rows[ri].x0);
    return ease.inOut(prog(t, m.at, m.dur ?? 0.6)) * total >= den - 0.5;
  }
  function vanKien(t) {
    nd.nen(t);
    const yH = nd.dauTheCao();
    // bố cục trước, vẽ sau (cần chiều cao khối để đặt tấm tối khi phủ lên phim)
    let y = Math.max(S.y ?? 0, yH + 80);
    const X0 = 120;
    const moc = mocPhanTu(S, S.blocks.length, S.blocks.map((b) => b.from));
    const bl = S.blocks.map((b, bi) => {
      const size = Math.max(b.size ?? 64, 52), fam = b.font === 'serif' ? 'Lora' : 'Oswald', weight = b.font === 'serif' ? 500 : 700;
      ctx.font = font(weight, size, fam, b.italic ? 'italic' : '');
      const lines = ngatDong(ctx, b.text, Math.min(b.maxW ?? 1560, W - 2 * X0)), words = b.text.split(' ');
      const pos = []; lines.forEach((l, li) => { let x = X0; for (const w of l.split(' ')) { const ww = ctx.measureText(w).width; pos.push({ w, x, y: y + li * size * 1.42, ww }); x += ww + ctx.measureText(' ').width; } });
      const o = { b, size, fam, weight, words, pos, from: moc[bi] }; y += lines.length * size * 1.42 + (b.gap ?? 60); return o;
    });
    const yCite = Math.min(y + 10, 880);
    nd.ghiNhip([...bl.map((o) => o.from), ...bl.flatMap((o) => (o.b.marks || []).map((m) => m.at)), ...(S.cite ? [S.citeAt ?? 1] : [])]);
    nd.tam(0, 20, W, Math.min(960, yCite + 120) - 20, ease.out(prog(t, 0.1, 0.5)));
    nd.namMo(t, namCua(S)); nd.dauThe(t);
    for (const { b, size, fam, weight, words, pos, from } of bl) {
      const per = b.perWord ?? 0.12;
      for (const m of b.marks || []) {
        if (m.type !== 'highlight') continue;
        const idx = findPhrase(words, m.phrase); if (idx < 0) continue;
        const k = ease.inOut(prog(t, m.at, m.dur ?? 0.6)); if (k <= 0) continue;
        drawSpan(pos.slice(idx, idx + m.phrase.split(' ').length), k, (yy, x, w) => { nd.hopTuKhoa(x - 8, yy - size * 1.15, w + 16, size * 1.4); });
      }
      pos.forEach((p, i) => {
        const a = ease.out(prog(t, from + i * per, 0.35)); if (a <= 0) return;
        const hl = (b.marks || []).some((m) => m.type === 'highlight' && daQuet(words, pos, m, i, t));
        ctx.save(); ctx.globalAlpha = a * (b.dimAt != null ? 1 - 0.45 * ease.out(prog(t, b.dimAt, 0.5)) : 1);
        ctx.font = font(weight, size, fam, b.italic ? 'italic' : ''); ctx.fillStyle = hl ? MAU.than : mauChu(b.color) ?? MAU.kem; ctx.textBaseline = 'alphabetic';
        ctx.fillText(p.w, p.x, p.y + (1 - a) * 12); ctx.restore();
      });
      for (const m of b.marks || []) {
        if (m.type !== 'strike') continue;
        const idx = findPhrase(words, m.phrase); if (idx < 0) continue;
        const k = ease.inOut(prog(t, m.at, m.dur ?? 0.5));
        if (k > 0) drawSpan(pos.slice(idx, idx + m.phrase.split(' ').length), k, (yy, x, w) => nd.gach(x - 6, yy - size * 0.36, w + 12, Math.max(8, size * 0.1)));
      }
    }
    if (S.cite) {
      ctx.save(); ctx.globalAlpha = ease.out(prog(t, S.citeAt ?? 1, 0.6)); ctx.font = font(500, CO.thanPhu, 'BVP'); ctx.fillStyle = MAU.kemPhu;
      ctx.fillText(S.cite, X0, yCite); ctx.restore();
    }
    cuoi(t);
  }

  // ---------- chương ----------
  function chuong(t) {
    const hit = S.hit ?? 0.15, k = prog(t, hit, 0.45);
    nd.ghiNhip([hit]);
    const sc = t < hit ? 1.25 : lerp(1.12, 1, ease.out(k)) * (1 + 0.012 * prog(t, hit, S.duration));
    nd.nen(t); nd.tam(0, 190, W, 700);
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(sc, sc); ctx.translate(-W / 2, -H / 2);
    ctx.globalAlpha = t < hit ? 0 : 1; ctx.textAlign = 'center';
    ctx.font = font(700, 300); ctx.fillStyle = MAU.do; ctx.fillText(String(S.number), W / 2, 560);
    const kk = S.kicker ?? `CHƯƠNG ${S.number}`; ctx.font = font(600, CO.nhan); ctx.letterSpacing = '3px';
    const kw = ctx.measureText(kk).width + 40; ctx.letterSpacing = '0px';
    ctx.save(); ctx.textAlign = 'left'; nd.nhan(kk, W / 2 - kw / 2, 210, {}); ctx.restore();
    ctx.font = font(700, 110); ctx.fillStyle = MAU.kem;
    ngatDong(ctx, S.title, 1600).forEach((l, i) => ctx.fillText(l, W / 2, 700 + i * 112));
    const lw = 320 * ease.out(prog(t, hit + 0.1, 0.5)); ctx.fillStyle = MAU.vang; ctx.fillRect(W / 2 - lw / 2, 770 + (ngatDong(ctx, S.title, 1600).length - 1) * 112, lw, 10);
    ctx.restore();
    const fl = 1 - prog(t, hit, 0.25);
    if (t >= hit && fl > 0) { ctx.fillStyle = `rgba(255,245,225,${fl * 0.7})`; ctx.fillRect(0, 0, W, H); }
    cuoi(t);
  }

  // ---------- hook ----------
  function hook(t) {
    if (S.nen === 'trong') nd.nen(t); else { ctx.fillStyle = '#0F1309'; ctx.fillRect(0, 0, W, H); }
    for (const f of S.glows || []) {
      const k = (t - f.at) / (f.len ?? 0.7); if (k < 0 || k > 1) continue;
      const g = ctx.createRadialGradient(f.x ?? W * 0.7, f.y ?? H * 0.8, 0, f.x ?? W * 0.7, f.y ?? H * 0.8, 520);
      g.addColorStop(0, `rgba(255,170,90,${0.5 * (1 - k)})`); g.addColorStop(1, 'rgba(255,120,60,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    }
    // tấm tối sau cụm chữ khi phủ lên phim, để chữ đọc được trên mọi nền
    { let yy = S.y ?? 470, a = 1e9, b = -1e9;
      for (const l of S.lines) { const sz = Math.max(l.size ?? 120, 84), y = l.y ?? yy; a = Math.min(a, y - sz); b = Math.max(b, y + sz * 0.35); yy += sz * 1.25; }
      nd.tam(0, a - 90, W, b - a + 180); }
    nd.ghiNhip(S.lines.map((l) => l.at));
    let shake = 0, flash = 0;
    for (const l of S.lines) { const k = prog(t, l.at, 0.35); if (t >= l.at && k < 1) { shake = Math.max(shake, (1 - k) * (l.shake ?? 10)); flash = Math.max(flash, (1 - prog(t, l.at, 0.18)) * (l.flash ?? 0.5)); } }
    ctx.save(); ctx.translate(noise1(11, t * 30) * shake, noise1(23, t * 30) * shake); ctx.textAlign = 'center';
    let y = S.y ?? 470;
    for (const l of S.lines) {
      const size = Math.max(l.size ?? 120, 84), yy = l.y ?? y;
      const a = t >= l.at ? ease.out(prog(t, l.at, 0.12)) : 0, out = 1 - prog(t, l.to ?? 1e9, 0.4);
      if (a * out > 0) {
        ctx.save(); ctx.globalAlpha = a * out;
        const sc = lerp(1.08, 1, ease.out(prog(t, l.at, 0.4))) * (1 + 0.01 * prog(t, l.at, 6));
        ctx.translate(W / 2, yy); ctx.scale(sc, sc); ctx.font = font(l.weight ?? 700, size); ctx.fillStyle = mauChu(l.color) ?? MAU.kem;
        ctx.letterSpacing = `${l.spacing ?? 4}px`; ctx.fillText(l.text, 0, 0); ctx.restore();
      }
      y += size * 1.25;
    }
    ctx.restore();
    if (flash > 0) { ctx.fillStyle = `rgba(255,248,235,${flash})`; ctx.fillRect(0, 0, W, H); }
    const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.3, W / 2, H / 2, H); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.55)');
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
    cuoi(t, { logo: false });
  }

  // ---------- thẻ tên ----------
  function lowerThird(t) {
    ctx.clearRect(0, 0, W, H);
    nd.ghiNhip([S.from ?? 0.3]);
    if (ref.lowerBg) { ctx.drawImage(ref.lowerBg, 0, 0, W, H); ctx.fillStyle = 'rgba(0,0,0,0.35)'; ctx.fillRect(0, 0, W, H); }
    nd.theTen(t, { name: S.name, role: S.role, detail: S.detail, from: S.from, to: S.to ?? S.duration - 0.6, y: S.y ?? 920, size: S.size }, S.duration);
    cuoi(t, { logo: false, scrim: true, a: ease.out(prog(t, S.from ?? 0.3, 0.5)) * (1 - prog(t, S.to ?? S.duration - 0.6, 0.5)) });
  }

  // ---------- máy chữ ----------
  function mayChu(t) {
    nd.nen(t); nd.tam(0, 20, W, 940); nd.namMo(t, namCua(S));
    if (S.title || S.kicker) nd.dauThe(t);
    nd.ghiNhip(ref.mc.plan.blocks.map((b) => b.start));
    drawTypewriter(ctx, ref.mc.S, ref.mc.plan, t, MC);
    cuoi(t);
  }

  // ---------- hai cột đối chiếu ----------
  function haiCot(t) {
    const y0 = mo(t) - 10, cols = S.cols || [], gap = 60, cw = cols.length === 1 ? Math.min(1100, noiDungW) : (noiDungW - gap) / 2, bot = LUOI.noiDungDuoi;
    const xDau = cols.length === 1 ? (W - cw) / 2 : LUOI.le;
    const tatCa = cols.flatMap((c) => (c.lines || []).map((l) => l.at ?? 0));
    const moc = mocPhanTu(S, tatCa.length, tatCa); let mi = 0;
    nd.ghiNhip([...cols.map((c, i) => c.from ?? 0.2 + i * 0.15), ...moc]);
    cols.forEach((col, i) => {
      const x = xDau + i * (cw + gap), from = col.from ?? 0.2 + i * 0.15;
      const A = appear(t, from, { dur: 0.6, rise: 24, s0: 0.97 }), dim = col.dimAt != null ? 1 - 0.55 * ease.out(prog(t, col.dimAt, 0.5)) : 1;
      const ta = col.mau === 'ta';
      if (A.a > 0) {
        ctx.save(); ctx.globalAlpha = A.a * dim; ctx.translate(0, A.y);
        nd.bang(x, y0, cw, bot - y0, { gay: ta ? MAU.do : MAU.vang });
        ctx.textBaseline = 'alphabetic'; ctx.textAlign = 'left';
        if (col.sub) { ctx.font = font(600, CO.toiThieu); ctx.fillStyle = MAU.vang; ctx.fillText(col.sub, x + 46, y0 + 62); }
        ctx.font = font(700, 64); ctx.fillStyle = ta ? MAU.do : MAU.kem; ctx.fillText(col.title ?? '', x + 46, y0 + 140);
        nd.vach(x + 46, y0 + 164, (cw - 92) * ease.expoOut(prog(t, from + 0.2, 0.8)), 1, { dam: 140 });
        ctx.restore();
      }
      let y = y0 + 250;
      for (const l of col.lines || []) {
        const at = moc[mi++], size = Math.max(l.size ?? 44, 44);
        ctx.font = font(l.weight ?? 600, size, l.font === 'serif' ? 'Lora' : 'BVP');
        const rows = ngatDong(ctx, l.text, cw - 100), la = ease.out(prog(t, at, 0.4));
        if (la > 0 && A.a > 0) {
          ctx.save(); ctx.globalAlpha = la * dim; ctx.fillStyle = mauChu(l.color) ?? MAU.kem; ctx.textBaseline = 'alphabetic';
          rows.forEach((r, j) => ctx.fillText(r, x + 46, y + j * size * 1.3 + (1 - la) * 10));
          if (l.strike != null) { const k = ease.inOut(prog(t, l.strike, 0.5)), w = Math.max(...rows.map((r) => ctx.measureText(r).width)); if (k > 0) nd.gach(x + 40, y - size * 0.36, (w + 12) * k, Math.max(7, size * 0.1)); }
          ctx.restore();
        }
        y += rows.length * size * 1.3 + (l.gap ?? 34);
      }
    });
    cuoi(t);
  }

  return { 'hai-cot': haiCot, 'may-chu': mayChu, 'so-lieu': soLieu, lich, 'dong-thoi-gian': dongThoiGian, 'van-kien': vanKien, chuong, hook, 'lower-third': lowerThird, ...taoCacTheMau(nd, ctx, S, ref) };
}
