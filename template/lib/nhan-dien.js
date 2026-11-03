// Hệ nhận diện đồ hoạ Goha Studio: «bảng tác chiến». Dùng chung cho cards, overlay và các mẫu sau này (P2).
// Thông số và lý do: plans/261103-1756-he-nhan-dien-do-hoa/p1-spec.md.
// Mọi vẽ là canvas 2D, không Math.random (nhiễu có seed theo hợp đồng reelcrew render).
//
//   const nd = taoND(ctx, S);       // S = window.SHOT
//   await nd.chuanBi({ kieu: 'sang' | 'toi', seed, nen: true, logo: true });   // dựng nền, nạp logo (gọi trước mount)
//   nd.batDau(); nd.nen(t); nd.dauThe(t, {...}); ...; nd.ghiNhip([mốc hiện từng phần tử]); nd.chan(t);
//   dangKyDo(nd, S);                // window.CHU_DO: dữ liệu cho tools/do-tuong-phan.py
import { W, H, clamp, prog, ease, rng, appear } from './common.js';
import { demNhip, kiemNhip } from './nhip-hien.js';

// ---------- màu ----------
export const MAU = {
  nen: '#303A22',        // olive than, nền chính của thẻ
  nenToi: '#232A18',     // olive than sâu hơn: văn kiện, chương, máy chữ
  camo: ['#27301B', '#394629', '#2F3A21'], // ba tông rằn ri, lệch nền không quá ±8 % sáng
  kem: '#F4EEDA',       // chữ chính
  kemPhu: '#D9D3B6',    // chữ phụ, nguồn
  vang: '#F2C230',      // nhấn: nhãn hộp, từ khoá, vạch đậm
  do: '#FF5A3F',        // đỏ son (cùng họ đỏ logo #dc5a3c, sáng hơn): vạch, thanh, số lớn; ≥ 3:1 với nền olive kể cả mảng rằn ri sáng
  doHop: '#C62A1E',     // đỏ đậm làm nền hộp có chữ kem (4,9:1)
  doChu: '#FF8466',     // đỏ cho chữ nhỏ (≥ 4,5:1 trên nền olive)
  than: '#14180D',      // chữ đặt trên hộp vàng
  gach: '#E5432F',      // gạch xoá chữ cũ: ≥ 3:1 với chữ kem để chữ bị gạch vẫn đọc được
  ve: 'rgba(244,238,218,0.55)', // vạch mảnh dưới tiêu đề
  xanhDich: '#A9C4DC',  // ký hiệu, chữ phía đối phương (khi cần)
};
// Màu cũ trong shot EP001 → màu mới đọc được trên nền olive (chữ đỏ son #c93b2b chỉ 2,3:1).
const DOI_MAU = {
  '#c93b2b': MAU.doChu, '#a8271c': MAU.doChu, '#dc5a3c': MAU.doChu, '#d8312a': MAU.doChu,
  '#e5a93b': MAU.vang, '#dcae48': MAU.vang, '#c4922e': MAU.vang,
  '#9cb8d2': MAU.xanhDich, '#2c4766': MAU.xanhDich,
};
export const mauChu = (c) => (c ? DOI_MAU[String(c).toLowerCase()] ?? c : c);

// ---------- cỡ chữ (px ở khung 1920×1080) ----------
export const CO = {
  so: 220, soNho: 150,        // số lớn
  tieuDe: 84, tieuDeNho: 64,  // Oswald 700
  nhan: 34,                   // nhãn hộp (Oswald 600, in hoa, giãn 3 px)
  nhanCao: 62,                // chiều cao hộp nhãn: đủ chứa dấu mũ trên và dấu nặng dưới của chữ Việt in hoa
  than: 48, thanPhu: 40,      // chữ thường BVP
  nguon: 30,                  // nguồn góc phải dưới
  tenNguoi: 64,               // thẻ tên
  toiThieu: 38,               // sàn của chữ thông tin; nguon là ngoại lệ (30) vì là chữ phụ
};
// ---------- lưới, lề, vùng an toàn ----------
export const LUOI = {
  le: 96, tren: 72, duoi: 64,
  noiDungTren: 300, noiDungDuoi: 900, // vùng nội dung: giữa đầu thẻ và hàng chân
  logoCao: 48,
  // Shorts 9:16 cắt giữa từ 16:9: giữ ý chính (số, tên) trong cột này nếu muốn còn nguyên khi cắt
  shortsX0: 656, shortsX1: 1264,
};
export const noiDungW = W - 2 * LUOI.le;

export const font = (w, s, fam = 'Oswald', style = '') => `${style} ${w} ${s}px ${fam}`.trim();

/** Ngắt dòng theo bề rộng với font hiện tại của ctx. */
export function ngatDong(ctx, text, maxW) {
  const lines = []; let cur = '';
  for (const w of String(text).split(' ')) { const n = cur ? cur + ' ' + w : w; if (ctx.measureText(n).width > maxW && cur) { lines.push(cur); cur = w; } else cur = n; }
  if (cur) lines.push(cur);
  return lines;
}

// ---------- nền ----------
// Trường nhiễu giá trị (lưới thưa, nội suy trơn) dùng cho rằn ri và đường đồng mức.
function truongNhieu(r, gw, gh, w, h) {
  const f = new Float32Array(gw * gh);
  for (let i = 0; i < f.length; i++) f[i] = r();
  return (x, y) => {
    const fx = (x / w) * (gw - 1), fy = (y / h) * (gh - 1), x0 = Math.floor(fx), y0 = Math.floor(fy), x1 = Math.min(gw - 1, x0 + 1), y1 = Math.min(gh - 1, y0 + 1);
    const u = (fx - x0) ** 2 * (3 - 2 * (fx - x0)), v = (fy - y0) ** 2 * (3 - 2 * (fy - y0));
    return (f[y0 * gw + x0] * (1 - u) + f[y0 * gw + x1] * u) * (1 - v) + (f[y1 * gw + x0] * (1 - u) + f[y1 * gw + x1] * u) * v;
  };
}
const hex2rgb = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));

/** Nền «bảng tác chiến»: olive than, rằn ri tông gần nền, đường đồng mức sáng mờ, lưới toạ độ, mép tối nhẹ. Có seed. */
export function dungNen(seed, kieu = 'sang', tran = 1.08) {
  const w = Math.round(W * tran), h = Math.round(H * tran);
  const hw = w >> 1, hh = h >> 1; // tính ở nửa độ phân giải rồi phóng: mép rằn ri mềm tự nhiên
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d');
  g.fillStyle = kieu === 'toi' ? MAU.nenToi : MAU.nen; g.fillRect(0, 0, w, h);
  const r = rng(seed * 31 + 7);
  const lop = (kieu === 'toi' ? 0.5 : 1);
  const m = document.createElement('canvas'); m.width = hw; m.height = hh;
  const mg = m.getContext('2d'), im = mg.createImageData(hw, hh), d = im.data;
  const nguong = [0.52, 0.6, 0.66];
  const tru = MAU.camo.map((_, i) => [truongNhieu(r, 14 + i * 3, 8 + i * 2, hw, hh), truongNhieu(r, 40, 24, hw, hh)]);
  const cao = truongNhieu(rng(seed + 3), 9, 6, hw, hh), cao2 = truongNhieu(rng(seed + 5), 22, 13, hw, hh);
  const lv = new Int16Array(hw * hh);
  const cols = MAU.camo.map(hex2rgb);
  for (let y = 0; y < hh; y++) for (let x = 0; x < hw; x++) {
    const i = y * hw + x, k = i * 4;
    for (let L = 0; L < 3; L++) {
      const [f1, f2] = tru[L];
      if (f1(x, y) * 0.8 + f2(x, y) * 0.2 > nguong[L]) { d[k] = cols[L][0]; d[k + 1] = cols[L][1]; d[k + 2] = cols[L][2]; d[k + 3] = 255 * lop; }
    }
    lv[i] = Math.floor((cao(x, y) * 0.8 + cao2(x, y) * 0.2) * 14);
  }
  mg.putImageData(im, 0, 0);
  g.imageSmoothingQuality = 'high'; g.drawImage(m, 0, 0, w, h);
  // đường đồng mức (sáng mờ): bản đồ tác chiến in lên vải
  const l = document.createElement('canvas'); l.width = hw; l.height = hh;
  const lg = l.getContext('2d'), li = lg.createImageData(hw, hh), ld = li.data;
  for (let y = 0; y < hh - 1; y++) for (let x = 0; x < hw - 1; x++) {
    const i = y * hw + x;
    if (lv[i] !== lv[i + 1] || lv[i] !== lv[i + hw]) { const k = i * 4, dam = lv[i] % 5 === 0; ld[k] = 214; ld[k + 1] = 204; ld[k + 2] = 160; ld[k + 3] = dam ? 38 : 20; }
  }
  lg.putImageData(li, 0, 0);
  g.drawImage(l, 0, 0, w, h);
  // lưới toạ độ mảnh
  g.save(); g.strokeStyle = 'rgba(214,204,160,0.07)'; g.lineWidth = 1.5;
  for (let x = 40; x < w; x += 172) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); }
  for (let y = 60; y < h; y += 172) { g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
  g.restore();
  const vg = g.createRadialGradient(w / 2, h / 2, h * 0.45, w / 2, h / 2, h * 1.0);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(6,8,2,0.38)');
  g.fillStyle = vg; g.fillRect(0, 0, w, h);
  return c;
}

/** Nạp ảnh và chờ giải mã. */
async function nap(src) { const im = new Image(); im.src = src; await im.decode(); return im; }

// ---------- bộ vẽ ----------
export function taoND(ctx, S) {
  const log = []; // chữ đã vẽ trong khung hiện tại (cho máy đo tương phản)
  const nhipMoc = []; // mốc hiện của các phần tử nội dung trong thẻ (cho số nhịp hiện)
  const gachLog = []; // gạch xoá đã vẽ trong khung hiện tại: máy đo bỏ vùng gạch khỏi nền của chữ và kiểm gạch/chữ riêng
  // Bọc fillText đúng một lần trên mỗi ctx: gọi taoND lần nữa không bọc chồng (log không nhân đôi).
  const goc = ctx.__fillTextGoc ?? (ctx.__fillTextGoc = ctx.fillText.bind(ctx));
  let vai = 'noi-dung'; // vai chữ đang vẽ: 'noi-dung' (sàn 38 px) | 'nhan' (nhãn hộp, chức danh) | 'nguon' (sàn 30 px)
  ctx.fillText = (text, x, y, maxW) => {
    ghi(String(text), x, y);
    if (!window.ND_AN_CHU) goc(text, x, y, maxW); // ND_AN_CHU: máy đo dựng cùng khung không chữ để lấy nền thật
  };
  function ghi(text, x, y) {
    const m = /(\d+(?:\.\d+)?)px/.exec(ctx.font); if (!m) return;
    const tf = ctx.getTransform(), sc = Math.hypot(tf.a, tf.b), size = parseFloat(m[1]) * sc;
    const tm = ctx.measureText(text), p = tf.transformPoint({ x, y });
    // ô chữ khít theo số đo thật của chuỗi (không theo ước lượng cỡ chữ): máy đo không lẫn vạch dưới chữ vào nền
    log.push({ text, size, x0: p.x - tm.actualBoundingBoxLeft * sc, x1: p.x + tm.actualBoundingBoxRight * sc,
      y0: p.y - tm.actualBoundingBoxAscent * sc, y1: p.y + tm.actualBoundingBoxDescent * sc,
      fill: typeof ctx.fillStyle === 'string' ? ctx.fillStyle : null, a: ctx.globalAlpha, vai });
  }
  let BG = null, LOGO = null;
  const TRONG = S.nen === 'trong';
  const nd = {
    S, log, TRONG, nhipMoc, gachLog,
    /** nen: false cho loại thẻ không gọi nd.nen (hook, thẻ tên, overlay): khỏi dựng nền rằn ri. */
    async chuanBi({ kieu = 'sang', seed = S.seed ?? 5, logo = true, nen = true } = {}) {
      if (!TRONG && nen) BG = dungNen(seed, kieu);
      if (logo) LOGO = await nap(new URL('./goha-logo-ngang.png', import.meta.url).href);
    },
    batDau() { log.length = 0; nhipMoc.length = 0; gachLog.length = 0; },
    /** Khai mốc hiện (giây) của các phần tử nội dung của thẻ; đầu thẻ, năm mờ, nguồn không tính. */
    ghiNhip(mocs) { for (const m of mocs) if (Number.isFinite(m)) nhipMoc.push(m); },

    /** Nền: vải olive trôi chậm, hoặc lớp tối nhẹ trong suốt khi phủ lên phim (S.nen = 'trong'). */
    nen(t) {
      if (TRONG) {
        ctx.clearRect(0, 0, W, H);
        const a = S.toi ?? 0.4;
        const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.2, W / 2, H / 2, H);
        vg.addColorStop(0, `rgba(14,17,8,${a})`); vg.addColorStop(1, `rgba(8,10,4,${Math.min(1, a + 0.3)})`);
        ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
        return;
      }
      const k = clamp(t / Math.max(1, S.duration)), dx = (BG.width - W) * (0.15 + 0.7 * k), dy = (BG.height - H) * (0.6 - 0.3 * k);
      ctx.drawImage(BG, -dx, -dy);
    },
    /** Tấm tối dưới khối chữ khi phủ lên phim (không làm gì trên nền olive). */
    tam(x, y, w, h, a = 1) {
      if (!TRONG || a <= 0) return;
      ctx.save(); ctx.globalAlpha = a;
      const g = ctx.createLinearGradient(0, y, 0, y + h);
      g.addColorStop(0, 'rgba(8,10,4,0)'); g.addColorStop(0.18, 'rgba(8,10,4,0.76)'); g.addColorStop(0.82, 'rgba(8,10,4,0.76)'); g.addColorStop(1, 'rgba(8,10,4,0)');
      ctx.fillStyle = g; ctx.fillRect(x, y, w, h); ctx.restore();
    },
    /** Bảng sẫm đặt lên nền (trang sổ, ô thông tin): viền mảnh, nền olive rất tối mờ để chữ đọc được trên rằn ri. */
    bang(x, y, w, h, { a = 1, gay = null } = {}) {
      ctx.save(); ctx.globalAlpha = a;
      ctx.fillStyle = TRONG ? 'rgba(8,10,4,0.78)' : 'rgba(12,15,7,0.62)'; ctx.fillRect(x, y, w, h);
      ctx.strokeStyle = 'rgba(217,211,182,0.35)'; ctx.lineWidth = 2; ctx.strokeRect(x + 1, y + 1, w - 2, h - 2);
      if (gay) { ctx.fillStyle = gay; ctx.fillRect(x, y, 10, h); }
      ctx.restore();
    },
    /** Năm mờ cỡ lớn làm nền (chữ 4 số hoặc mốc ngắn). */
    namMo(t, text, { x = W - LUOI.le + 20, y = 880, a = 0.085 } = {}) {
      if (!text) return;
      const A = appear(t, 0.15, { dur: 0.9, rise: 0, s0: 1 });
      ctx.save(); ctx.globalAlpha = A.a * a; ctx.font = font(700, text.length > 4 ? 380 : 560); ctx.textAlign = 'right'; ctx.fillStyle = MAU.kem;
      ctx.fillText(text, x, y); ctx.restore();
    },
    /** Nhãn hộp: chữ in hoa trong hộp. kieu 'dac' (vàng đặc) | 'vien' (viền vàng) | 'do' (đỏ, chữ kem). Trả bề rộng. */
    nhan(text, x, y, { kieu = 'dac', cao = CO.nhanCao, size = CO.nhan, a = 1, k = 1 } = {}) {
      ctx.save(); ctx.font = font(600, size); ctx.letterSpacing = '3px'; ctx.textBaseline = 'alphabetic';
      // hộp và chữ canh theo số đo mực của chuỗi mẫu có dấu cao nhất và thấp nhất, nên dấu không thò ra ngoài hộp
      const ref = ctx.measureText('ÂỆỒỮỌĐ'), asc = ref.actualBoundingBoxAscent, des = ref.actualBoundingBoxDescent;
      cao = Math.max(cao, Math.ceil(asc + des) + 16);
      const w = ctx.measureText(text).width + 40;
      ctx.globalAlpha = a; ctx.beginPath(); ctx.rect(x, y, w * k, cao); ctx.clip();
      if (kieu === 'vien') { ctx.strokeStyle = MAU.vang; ctx.lineWidth = 3; ctx.strokeRect(x + 1.5, y + 1.5, w - 3, cao - 3); }
      else { ctx.fillStyle = kieu === 'do' ? MAU.doHop : MAU.vang; ctx.fillRect(x, y, w, cao); }
      ctx.fillStyle = kieu === 'vien' ? MAU.vang : kieu === 'do' ? MAU.kem : MAU.than;
      vai = 'nhan'; ctx.fillText(text, x + 20, y + (cao + asc - des) / 2); vai = 'noi-dung'; ctx.restore();
      return w;
    },
    /** Vạch: mảnh suốt bề rộng + đoạn đậm ở đầu. k = tiến độ 0..1. */
    vach(x, y, w, k, { dam = 220, mauDam = MAU.vang } = {}) {
      ctx.fillStyle = MAU.ve; ctx.fillRect(x, y + 2, w * k, 3);
      ctx.fillStyle = mauDam; ctx.fillRect(x, y - 2, dam * Math.min(1, k * 1.6), 9);
    },
    /**
     * Đầu thẻ: [tag viền] [kicker/nhãn đặc] → tiêu đề Oswald → vạch có đoạn đậm. Trả y đáy (đặt nội dung từ đó + 40).
     * o: {nhan, tag, tieuDe}; mặc định lấy từ S.kicker, S.tag, S.title.
     */
    dauThe(t, o = {}) { return nd.dauTheVe(t, o, true); },
    /** Đáy đầu thẻ mà không vẽ (để đặt tấm tối hay nội dung trước khi vẽ). */
    dauTheCao(o = {}) { return nd.dauTheVe(0, o, false); },
    dauTheVe(t, o, ve) {
      const nhan = o.nhan ?? S.kicker, tag = o.tag ?? S.tag, tieuDe = o.tieuDe ?? S.title;
      if (!nhan && !tag && !tieuDe) return LUOI.tren;
      const A1 = appear(t, 0.05, { dur: 0.45, rise: 0, s0: 1 }), A2 = appear(t, 0.14, { dur: 0.5, rise: 16, s0: 1 });
      let x = LUOI.le;
      if (ve && tag && nhan) x += nd.nhan(tag, x, LUOI.tren, { kieu: 'vien', a: A1.a }) + 14;
      if (ve && (nhan || tag)) nd.nhan(nhan ?? tag, x, LUOI.tren, { a: A1.a * ease.out(prog(t, 0.05, 0.4)), k: ease.expoOut(prog(t, 0.05, 0.5)) });
      let yDay = LUOI.tren + CO.nhanCao;
      if (tieuDe) {
        let size = CO.tieuDe, lines;
        ctx.save(); ctx.font = font(700, size);
        while (ctx.measureText(tieuDe).width > noiDungW && size > CO.tieuDeNho) { size -= 4; ctx.font = font(700, size); }
        lines = ngatDong(ctx, tieuDe, noiDungW);
        if (lines.length > 1) { size = CO.tieuDeNho; ctx.font = font(700, size); lines = ngatDong(ctx, tieuDe, noiDungW); }
        const base = yDay + 28 + size * 0.95;
        if (ve) {
          ctx.globalAlpha = A2.a; ctx.fillStyle = MAU.kem; ctx.textBaseline = 'alphabetic';
          lines.forEach((l, i) => ctx.fillText(l, LUOI.le, base + i * size * 1.08 + A2.y));
        }
        ctx.restore();
        yDay = base + (lines.length - 1) * size * 1.08 + 26;
      }
      if (ve) { ctx.save(); ctx.globalAlpha = A1.a; nd.vach(LUOI.le, yDay, noiDungW, ease.expoOut(prog(t, 0.3, 1.0))); ctx.restore(); }
      return yDay + 9;
    },
    /** Nhãn ngày: cards có đầu thẻ → góc phải (trái đã có nhãn); không có đầu thẻ hoặc overlay → góc trái trên. */
    nhanNgay(text, a, { phai = false } = {}) {
      if (!text || a <= 0) return;
      ctx.save(); ctx.font = font(600, 42); ctx.letterSpacing = '1px';
      const w = ctx.measureText(text).width + 56, k = ease.expoOut(clamp(a / 0.85)), x = phai ? W - LUOI.le - w : LUOI.le, y = phai ? 110 : LUOI.tren;
      ctx.globalAlpha = clamp(a * 3); ctx.beginPath(); ctx.rect(x, y, w * k, 64); ctx.clip();
      ctx.fillStyle = 'rgba(12,15,7,0.9)'; ctx.fillRect(x, y, w, 64);
      ctx.fillStyle = MAU.do; ctx.fillRect(x, y, 8, 64);
      ctx.globalAlpha = clamp((a - 0.25) / 0.6); ctx.fillStyle = MAU.kem; ctx.textBaseline = 'middle';
      ctx.fillText(text, x + 30, y + 33); ctx.restore();
    },
    /** Gạch xoá chữ cũ (đỏ MAU.gach). Ghi lại để máy đo xử lý riêng; mọi gạch xoá của thẻ phải đi qua hàm này. */
    gach(x, y, w, h) {
      ctx.save(); ctx.fillStyle = MAU.gach; ctx.fillRect(x, y, w, h);
      const tf = ctx.getTransform(), p0 = tf.transformPoint({ x, y }), p1 = tf.transformPoint({ x: x + w, y: y + h });
      gachLog.push({ x0: Math.min(p0.x, p1.x), y0: Math.min(p0.y, p1.y), x1: Math.max(p0.x, p1.x), y1: Math.max(p0.y, p1.y), fill: MAU.gach, a: ctx.globalAlpha });
      ctx.restore();
    },
    /** Hộp từ khoá: mảng vàng sau cụm chữ (chữ vẽ đè lên bằng MAU.than). k = tiến độ quét 0..1. */
    hopTuKhoa(x, y, w, h, k = 1) {
      if (k <= 0) return;
      ctx.fillStyle = MAU.vang; ctx.fillRect(x, y, w * k, h);
    },
    /** Nguồn (góc phải dưới) + logo (góc trái dưới). Mọi cảnh phải có nguồn. */
    chan(t, { logo = !TRONG && S.logo !== false, a = 1, scrim = false } = {}) {
      const text = S.source ?? S.credit;
      const A = appear(t, 0.35, { dur: 0.6, rise: 0, s0: 1 }).a * a;
      if (TRONG || scrim) {
        const g = ctx.createLinearGradient(0, H - 230, 0, H); g.addColorStop(0, 'rgba(8,10,4,0)'); g.addColorStop(0.55, 'rgba(8,10,4,0.55)'); g.addColorStop(1, 'rgba(8,10,4,0.9)');
        ctx.save(); ctx.globalAlpha = A; ctx.fillStyle = g; ctx.fillRect(0, H - 230, W, 230); ctx.restore();
      }
      if (text) {
        ctx.save(); ctx.globalAlpha = A; ctx.font = font(500, CO.nguon, 'BVP'); ctx.textAlign = 'right'; ctx.fillStyle = MAU.kemPhu; ctx.textBaseline = 'alphabetic';
        const maxW = logo ? 1380 : 1650, lines = ngatDong(ctx, text, maxW), lh = CO.nguon * 1.25;
        let y = H - LUOI.duoi - (lines.length - 1) * lh;
        vai = 'nguon';
        for (const l of lines) { ctx.fillText(l, W - LUOI.le, y); y += lh; }
        vai = 'noi-dung';
        ctx.restore();
      }
      if (logo && LOGO) {
        const h = LUOI.logoCao, w = (h * LOGO.width) / LOGO.height;
        ctx.save(); ctx.globalAlpha = 0.92 * A; ctx.drawImage(LOGO, LUOI.le, H - LUOI.duoi - h + 8, w, h); ctx.restore();
      }
    },
    /**
     * Thẻ tên người (góc trái dưới): vạch đỏ đứng, chức danh, tên Oswald, chi tiết. Dùng cho lower-third và overlay.
     * it: {name, role, detail, from, to, y, size}. Trả không gì.
     */
    theTen(t, it, hetCanh) {
      const from = it.from ?? 0.3, to = it.to ?? hetCanh - 0.5;
      const a = ease.out(prog(t, from, 0.45)) * (1 - prog(t, to, 0.4)), k = ease.out(prog(t, from, 0.6));
      if (a <= 0) return;
      const size = Math.max(it.size ?? CO.tenNguoi, 56), x = LUOI.le, yDay = it.y ?? 900;
      ctx.save(); ctx.font = font(700, size);
      const ten = ngatDong(ctx, it.name, 1500);
      ctx.font = font(500, CO.thanPhu, 'BVP');
      const det = it.detail ? ngatDong(ctx, it.detail, 1500) : [];
      const roleH = it.role ? 70 : 0, h = roleH + ten.length * size * 1.1 + det.length * 52 + 26;
      const top = yDay - h;
      ctx.restore();
      ctx.save(); ctx.globalAlpha = a;
      const g = ctx.createLinearGradient(0, top - 90, 0, H); g.addColorStop(0, 'rgba(8,10,4,0)'); g.addColorStop(0.35, 'rgba(8,10,4,0.62)'); g.addColorStop(1, 'rgba(8,10,4,0.78)');
      ctx.fillStyle = g; ctx.fillRect(0, top - 90, 1560, H - top + 90);
      ctx.fillStyle = MAU.do; ctx.fillRect(x, top, 9, h * k);
      let yy = top + 8;
      if (it.role) { nd.nhan(it.role, x + 32, yy, { cao: 58, size: 30, a: 1, k }); yy += 70; }
      ctx.font = font(700, size); ctx.fillStyle = MAU.kem; ctx.textBaseline = 'alphabetic';
      for (const l of ten) { yy += size * 0.92; ctx.fillText(l, x + 32 - (1 - k) * 40, yy); yy += size * 0.18; }
      ctx.font = font(500, CO.thanPhu, 'BVP'); ctx.fillStyle = MAU.kemPhu;
      for (const l of det) { yy += 46; ctx.fillText(l, x + 34, yy); yy += 6; }
      ctx.restore();
    },
  };
  return nd;
}

/**
 * Khai báo window.CHU_DO (getter): máy đo tools/do-tuong-phan.py đọc bằng `reelcrew render <trang> --data CHU_DO`.
 * Trả {mau: [{t, chu: [...]}], nhip: {mocs, n, ok, canhBao}}.
 *  - mau: chữ đã vẽ ở các mốc soi (1 s, giữa shot, 95 %; kẹp ra ngoài đoạn mờ vào/ra đen). Mỗi chữ có cỡ, màu, ô chữ, độ mờ `a`,
 *    vai, và `buon` (đứng yên: cùng ô, cùng độ mờ ở 0,1 s sau); chữ đang chuyển động không `buon`.
 *  - nhip: mốc hiện của các phần tử nội dung do từng loại thẻ khai (nd.ghiNhip), đếm bằng demNhip (lib/nhip-hien.js).
 */
export function dangKyDo(nd, S, mocSoi) {
  Object.defineProperty(window, 'CHU_DO', {
    configurable: true,
    get() {
      const d = S.duration, rf = window.renderFrame;
      const lo = (S.fadeIn ?? 0) + 0.02, hi = d - (S.fadeOut ?? 0) - 0.02;
      const ts = mocSoi ?? [1, Math.round(d * 50) / 100, Math.round(d * 95) / 100].map((t) => Math.round(Math.min(hi, Math.max(lo, t)) * 100) / 100);
      const chup = (t) => { nd.batDau(); rf(t); return { chu: nd.log.map((e) => ({ ...e })), gach: nd.gachLog.map((g) => ({ ...g })) }; };
      const mau = ts.map((t) => {
        const { chu, gach } = chup(t), sau = chup(t + 0.1 <= d ? t + 0.1 : t - 0.1).chu;
        for (const e of chu) e.buon = sau.some((f) => f.text === e.text && Math.abs(f.x0 - e.x0) <= 1.5 && Math.abs(f.y0 - e.y0) <= 1.5 && Math.abs(f.a - e.a) <= 0.02);
        return { t, chu, gach };
      });
      nd.batDau(); rf(0);
      const mocs = [...nd.nhipMoc];
      return { mau, nhip: { mocs, n: demNhip(mocs), ...kiemNhip(mocs) } };
    },
  });
}
