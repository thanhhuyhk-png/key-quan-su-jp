// Khối overlay: lớp chữ nền TRONG SUỐT để phủ lên phim tư liệu (render --transparent rồi ghép bằng ffmpeg).
// SHOT: duration, date (nhãn ngày góc trái trên), credit (chú thích nguồn góc phải dưới),
//       texts: [{text, sub, from, to, x, y, size, color}] chữ lớn có nền tối mờ, bật so le theo từ.
import { W, H, clamp, prog, ease, appear, loadFonts, drawDateLabel, drawCredit, mount } from '../lib/common.js';
import { taoND, dangKyDo, MAU, CO, font, mauChu } from '../lib/nhan-dien.js';

const S = window.SHOT;
document.documentElement.style.background = 'transparent';
document.body.style.background = 'transparent';
const cv = document.createElement('canvas'); cv.width = W; cv.height = H; document.body.appendChild(cv);
const ctx = cv.getContext('2d');
// Mặc định vẽ theo hệ nhận diện lib/nhan-dien.js; SHOT.nhanDien = false giữ bản vẽ cũ.
const ND_ON = S.nhanDien !== false;
const nd = ND_ON ? taoND(ctx, S) : null;

function bigText(t, it) {
  const size = ND_ON ? Math.max(it.size ?? 96, 72) : it.size ?? 96, X = it.x ?? W / 2, y = it.y ?? H * 0.5, to = it.to ?? 1e9;
  if (t < it.from) return;
  ctx.save(); ctx.font = `700 ${size}px Oswald`; ctx.textBaseline = 'middle';
  const words = it.text.split(' '), sp = ctx.measureText(' ').width;
  const ws = words.map((w) => ctx.measureText(w).width), tw = ws.reduce((a, b) => a + b, 0) + sp * (words.length - 1);
  // dải tối mờ sau chữ để đọc được trên mọi nền phim
  const band = ease.expoOut(prog(t, it.from, 0.5)) * (1 - ease.in(prog(t, to, 0.3)));
  const g = ctx.createLinearGradient(0, y - size, 0, y + size * (it.sub ? 1.6 : 1));
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.5, `rgba(0,0,0,${(ND_ON ? 0.78 : 0.55) * band})`); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = g; ctx.fillRect(0, y - size, W, size * (it.sub ? 2.6 : 2));
  let x = X - tw / 2;
  words.forEach((w, i) => {
    const A = appear(t, it.from + i * 0.07, { dur: 0.5, to: to + i * 0.03, rise: size * 0.25, s0: 0.9 });
    if (A.a > 0) {
      ctx.save(); ctx.globalAlpha = A.a; ctx.translate(x + ws[i] / 2, y + A.y); ctx.scale(A.s, A.s);
      ctx.shadowColor = 'rgba(0,0,0,0.75)'; ctx.shadowBlur = 24; ctx.fillStyle = ND_ON ? mauChu(it.color) ?? MAU.kem : it.color ?? '#f3efe6'; ctx.fillText(w, -ws[i] / 2, 0); ctx.restore();
    }
    x += ws[i] + sp;
  });
  const u = ease.expoOut(prog(t, it.from + 0.25, 0.6)) * (1 - ease.in(prog(t, to, 0.3)));
  ctx.fillStyle = ND_ON ? MAU.vang : '#c93b2b'; ctx.fillRect(X - (tw / 2) * u, y + size * 0.6, tw * u, ND_ON ? 8 : 6);
  if (it.sub) {
    const A = appear(t, it.from + 0.3, { dur: 0.5, to, rise: 10 });
    ctx.globalAlpha = A.a; ctx.textAlign = 'center'; ctx.font = `500 ${ND_ON ? Math.max(CO.thanPhu, Math.round(size * 0.36)) : Math.round(size * 0.32)}px BVP`; ctx.fillStyle = ND_ON ? MAU.kem : 'rgba(243,239,230,0.92)';
    ctx.fillText(it.sub, X, y + size * 0.95 + A.y);
  }
  ctx.restore();
}


// Thẻ góc dưới trái (tên người, đơn vị, số liệu ngắn): thes: [{name, role, detail, from, to}]
function wrapW(text, maxW) {
  const out = []; let cur = '';
  for (const w of text.split(' ')) { const n = cur ? cur + ' ' + w : w; if (ctx.measureText(n).width > maxW && cur) { out.push(cur); cur = w; } else cur = n; }
  if (cur) out.push(cur); return out;
}
function the(t, it, i) {
  const from = it.from ?? 0.3, to = it.to ?? S.duration - 0.35;
  const a = ease.out(prog(t, from, 0.45)) * (1 - prog(t, to, 0.35)), k = ease.out(prog(t, from, 0.6));
  if (a <= 0) return;
  const x = 110, y = (it.y ?? 880);
  ctx.save(); ctx.globalAlpha = a;
  ctx.font = `700 ${it.size ?? 54}px Oswald`;
  const nameLines = wrapW(it.name, 1500);
  ctx.font = '500 26px BVP';
  const det = it.detail ? wrapW(it.detail, 1300) : [];
  const h = nameLines.length * (it.size ?? 54) * 1.12 + det.length * 34 + (it.role ? 34 : 0) + 40;
  const g = ctx.createLinearGradient(0, y - h - 60, 0, H); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(0.45, 'rgba(0,0,0,0.5)'); g.addColorStop(1, 'rgba(0,0,0,0.62)');
  ctx.fillStyle = g; ctx.fillRect(0, y - h - 60, 1500, H - y + h + 60);
  ctx.fillStyle = '#c93b2b'; ctx.fillRect(x, y - h, 7, h * k);
  let yy = y - h + 30;
  if (it.role) { ctx.font = '500 22px "Plex Mono"'; ctx.fillStyle = 'rgba(239,230,210,0.85)'; ctx.fillText(it.role, x + 28, yy); yy += 34; }
  ctx.font = `700 ${it.size ?? 54}px Oswald`; ctx.fillStyle = '#ffffff';
  for (const l of nameLines) { yy += (it.size ?? 54); ctx.fillText(l, x + 26 - (1 - k) * 40, yy - 8); yy += (it.size ?? 54) * 0.12; }
  ctx.font = '500 26px BVP'; ctx.fillStyle = 'rgba(239,230,210,0.92)';
  for (const l of det) { yy += 34; ctx.fillText(l, x + 28, yy); }
  ctx.restore();
}

function renderFrame(t) {
  t = clamp(t, 0, S.duration);
  ctx.clearRect(0, 0, W, H);
  const d = typeof S.date === 'string' ? { text: S.date } : S.date;
  if (ND_ON) {
    nd.batDau();
    nd.ghiNhip([...(S.texts || []).map((it) => it.from), ...(S.thes || []).map((it) => it.from ?? 0.3), ...(d ? [d.from ?? 0.2] : [])]);
    for (const it of S.texts || []) bigText(t, it);
    (S.thes || []).forEach((it) => nd.theTen(t, { ...it, y: it.y ?? 920 }, S.duration));
    if (d) nd.nhanNgay(d.text, ease.out(prog(t, d.from ?? 0.2, 0.5)) * (1 - prog(t, d.to ?? 1e9, 0.4)));
    nd.chan(t, { logo: S.logo === true, scrim: !!S.credit });
    return;
  }
  for (const it of S.texts || []) bigText(t, it);
  (S.thes || []).forEach((it, i) => the(t, it, i));
  if (d) drawDateLabel(ctx, d.text, ease.out(prog(t, d.from ?? 0.2, 0.5)) * (1 - prog(t, d.to ?? 1e9, 0.4)));
  drawCredit(ctx, S.credit, 1);
}

async function init() {
  await loadFonts();
  if (ND_ON) await nd.chuanBi({ logo: S.logo === true, nen: false });
  mount(S.duration, renderFrame);
  if (ND_ON) dangKyDo(nd, S);
}
init();
