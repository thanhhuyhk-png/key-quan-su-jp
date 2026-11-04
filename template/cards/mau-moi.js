// Năm mẫu thẻ «bằng chứng gốc» của P2, vẽ bằng hệ nhận diện lib/nhan-dien.js:
//   tai-lieu-dich | phim-panel | the-am-thanh | nhan-vat (bienThe: tach-nen | khung) | bieu-do (kieu: cot-doi | nguoi)
// Spec và lý do từng thông số: plans/261103-1756-he-nhan-dien-do-hoa/p2-spec.md.
// Quy ước: dữ liệu xấu thì NÉM LỖI tiếng Việt ở bước chuẩn bị (trước khung đầu tiên), không bao giờ cắt chữ hay méo hình trong im lặng.
// Luật cứng (lãnh tụ, nhãn âm thanh, nguồn) có máy chặn ở tools/luat_cung.py khi dựng trang; ở đây là lớp chặn thứ hai khi vẽ.
import { W, H, clamp, lerp, prog, ease, appear } from '../lib/common.js';
import { MAU, CO, LUOI, noiDungW, font, ngatDong } from '../lib/nhan-dien.js';
import { mocPhanTu, mocTuLoi } from '../lib/nhip-hien.js';
import { LOAI_P2, NHAN_AM_THANH as NHAN_AM, TRAN_ZOOM_LANH_TU as TRAN_ZOOM, TRAN_RAM_BYTE, kiemDuLieu, kiemThoiLuongGiong, kiemCatLanhTu, tinhKhungAnh, uocRam } from './luat-cung.js';

export const LOAI_MAU = LOAI_P2;
export const KIEU_NEN_MAU = { 'the-am-thanh': 'toi', 'nhan-vat': 'toi' };
export const NHAN_AM_THANH = NHAN_AM;
export const TRAN_ZOOM_LANH_TU = TRAN_ZOOM;
const MAX_KHUNG_PHIM = 150;           // số khung phim nạp sẵn tối đa; ngoài ra tổng byte giải mã ≤ TRAN_RAM_BYTE (đo từ kích thước thật)
const LO_KHUNG = 10;                 // nạp khung phim theo lô, không giải mã đồng thời cả trăm ảnh
const URL_LANH_TU = new URL('../data/lanh-tu.json', import.meta.url).href;

const loi = (S, m) => new Error(`[${S.type}] ${m}`);
const fmtNum = (v, dec = 0) => v.toFixed(dec).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, '.');
const namCua = (S) => S.nam ?? (/^\d{4}/.test(S.tag ?? '') ? S.tag.slice(0, 4) : null);
const soHopLe = (v) => typeof v === 'number' && Number.isFinite(v);

async function napAnh(S, src, ten) {
  if (!src || typeof src !== 'string') throw loi(S, `thiếu «${ten}» (đường dẫn ảnh)`);
  const im = new Image(); im.src = src;
  try { await im.decode(); } catch { throw loi(S, `không nạp được ảnh «${ten}»: ${src}`); }
  return im;
}
async function napJson(S, src, ten) {
  if (!src) throw loi(S, `thiếu «${ten}»`);
  let r;
  try { r = await fetch(src); } catch { throw loi(S, `không đọc được «${ten}»: ${src}`); }
  if (!r.ok) throw loi(S, `không đọc được «${ten}» (${r.status}): ${src}`);
  return r.json();
}

/** True nếu ảnh có điểm trong suốt (đọc ảnh thu nhỏ ≤ 512 px). Không đọc được điểm ảnh thì LỖI: nghi ngờ thì chặn. */
function coAlphaAnh(S, im, ten) {
  const k = Math.min(1, 512 / Math.max(im.width, im.height)), c = document.createElement('canvas');
  c.width = Math.max(1, Math.round(im.width * k)); c.height = Math.max(1, Math.round(im.height * k));
  const g = c.getContext('2d'); g.drawImage(im, 0, 0, c.width, c.height);
  let d;
  try { d = g.getImageData(0, 0, c.width, c.height).data; } catch { throw loi(S, `không kiểm được vùng trong suốt của «${ten}» (trình duyệt chặn đọc điểm ảnh): ảnh lãnh tụ không qua được kiểm`); }
  for (let i = 3; i < d.length; i += 4) if (d[i] < 255) return true;
  return false;
}

/** Danh sách từ có mốc [{text, start}] (giây) từ words.json của kit (`words[{text,start_ms}]`) hoặc mảng [{text,start}]. */
export function tuCoMoc(d) {
  if (Array.isArray(d)) return d.map((x) => ({ text: String(x.text ?? ''), start: x.start ?? x.start_ms / 1000 })).filter((x) => x.text.trim() && Number.isFinite(x.start));
  if (d && Array.isArray(d.words)) return d.words.filter((w) => !w.audio_event && String(w.text ?? '').trim() && Number.isFinite(w.start_ms)).map((w) => ({ text: w.text, start: w.start_ms / 1000 }));
  throw new Error('tệp lời không có mảng words');
}

/**
 * Mốc giây cho n phần tử. Thứ tự ưu tiên: S.loi = {tep: words.json, cum: [cụm đầu mỗi phần tử], offset} (mocTuLoi) → S.moc → S.nhip → mac.
 * Không tìm thấy cụm trong lời thì ném lỗi, không đoán.
 */
async function mocCuaThe(S, n, mac = []) {
  let S2 = S;
  if (S.loi) {
    const cum = S.loi.cum ?? [];
    if (cum.length !== n) throw loi(S, `loi.cum có ${cum.length} cụm nhưng thẻ có ${n} phần tử`);
    let tu;
    try { tu = tuCoMoc(await napJson(S, S.loi.tep, 'loi.tep')); } catch (e) { throw e.message.startsWith('[') ? e : loi(S, e.message); }
    const moc = mocTuLoi(tu, cum, S.loi.offset ?? 0);
    const sai = cum.filter((_, i) => moc[i] == null);
    if (sai.length) throw loi(S, `không tìm thấy trong lời: ${sai.map((c) => `«${c}»`).join(', ')}`);
    S2 = { ...S, moc };
  }
  const moc = mocPhanTu(S2, n, mac);
  if (moc.length !== n || !moc.every(soHopLe)) throw loi(S, 'mốc hiện không hợp lệ');
  return moc;
}

/** Xếp chữ vào hộp: thử cỡ từ lớn xuống nhỏ, trả {size, lines}; không vừa thì lỗi. */
function xepChu(S, ctx, text, { maxW, maxH, from, to, wt = 600, fam = 'Oswald', lh = 1.2, style = '', ten }) {
  for (let size = from; size >= to; size -= 2) {
    ctx.font = font(wt, size, fam, style);
    const lines = ngatDong(ctx, text, maxW);
    if (lines.length * size * lh <= maxH && lines.every((l) => ctx.measureText(l).width <= maxW)) return { size, lines };
  }
  throw loi(S, `${ten} quá dài, không vừa khung ở cỡ chữ tối thiểu ${to}px: «${text.slice(0, 40)}…»`);
}

/** Số ký tự đã gõ của một đoạn dài `len` bắt đầu ở `bd`, gõ trong `dur` giây. */
const daGo = (t, bd, dur, len) => Math.floor(clamp((t - bd) / dur) * len + 1e-6);

/** Vẽ các dòng với `n` ký tự đầu (chữ gõ dần); các dòng bố cục theo cả đoạn nên chữ không nhảy dòng. Trả số ký tự còn lại. */
function veGo(ctx, lines, n, x, y, lh) {
  let left = n;
  lines.forEach((l, i) => {
    const k = Math.max(0, Math.min(l.length, left));
    if (k > 0) ctx.fillText(l.slice(0, k), x, y + i * lh);
    left -= l.length + 1;
  });
}

// ============================================================ chuẩn bị (async, sau khi font đã nạp)
export async function chuanBiMau(S, ctx, nd) {
  const y0 = nd.dauTheCao() + 44;
  const hC = LUOI.noiDungDuoi - y0;
  let names;
  try { const r = await fetch(URL_LANH_TU); if (!r.ok) throw new Error(String(r.status)); names = (await r.json()).ten; if (!Array.isArray(names)) throw new Error('thiếu mảng ten'); }
  catch (e) { throw loi(S, `không đọc được data/lanh-tu.json (${e.message}): không có danh sách tên thì không kiểm luật lãnh tụ`); }
  const sai = kiemDuLieu(S, names);
  if (sai.length) throw new Error(`LUẬT CỨNG: ${sai.join(' | ')}`);
  const R = { y0, hC };
  switch (S.type) {
    case 'tai-lieu-dich': return chuanBiTaiLieu(S, ctx, R);
    case 'phim-panel': return chuanBiPhim(S, ctx, R);
    case 'the-am-thanh': return chuanBiAmThanh(S, ctx, R);
    case 'nhan-vat': return chuanBiNhanVat(S, ctx, R);
    case 'bieu-do': return chuanBiBieuDo(S, ctx, R);
    default: throw loi(S, 'loại không thuộc P2');
  }
}

// ---------------------------------------------------------------- tai-lieu-dich
async function chuanBiTaiLieu(S, ctx, R) {
  const anh = await napAnh(S, S.anh, 'anh');
  const cau = S.cau;
  if (!Array.isArray(cau) || !cau.length) throw loi(S, '«cau» phải là mảng ít nhất một câu {goc, dich, vung}');
  if (cau.length > 6) throw loi(S, 'tối đa 6 câu mỗi thẻ (chia thẻ khác cho đoạn dài)');
  cau.forEach((c, i) => {
    if (!c.dich || typeof c.dich !== 'string') throw loi(S, `cau[${i}] thiếu «dich»`);
    const v = c.vung;
    if (!Array.isArray(v) || v.length !== 4 || !v.every(soHopLe) || v[0] < 0 || v[1] < 0 || v[2] <= 0 || v[3] <= 0 || v[0] + v[2] > 1.001 || v[1] + v[3] > 1.001) throw loi(S, `cau[${i}].vung phải là [x, y, rộng, cao] chuẩn hoá nằm trong trang`);
  });
  const moc = await mocCuaThe(S, cau.length, cau.map((c) => c.at));
  const vw = 760, vx = LUOI.le, px = vx + vw + 40, pw = W - LUOI.le - px;
  const g = { vx, vy: R.y0, vw, vh: R.hC, px, pw, pad: 40 };
  const inW = pw - 2 * g.pad;
  if (S.tenTL && S.tenTL.length > 42) throw loi(S, '«tenTL» tối đa 42 ký tự (nhãn BẢN DỊCH phải vừa bảng)');
  const bo = cau.map((c, i) => {
    const goc = c.goc ? xepChu(S, ctx, c.goc, { maxW: inW, maxH: 2 * 40 * 1.3, from: 40, to: 40, wt: 400, fam: 'Lora', lh: 1.3, style: 'italic', ten: `cau[${i}].goc` }) : { size: 40, lines: [] };
    const hGoc = goc.lines.length ? goc.lines.length * 40 * 1.3 + 20 : 0;
    const dich = xepChu(S, ctx, c.dich, { maxW: inW, maxH: R.hC - 30 - CO.nhanCao - 28 - hGoc - 28, from: 58, to: 44, wt: 600, ten: `cau[${i}].dich` });
    let tk = null;
    if (c.tuKhoa) {
      const pw_ = c.dich.split(' '), kw = c.tuKhoa.split(' ');
      const s = pw_.findIndex((_, j) => kw.every((w, k) => pw_[j + k] === w));
      if (s < 0) throw loi(S, `cau[${i}].tuKhoa «${c.tuKhoa}» không có trong «dich» (khớp theo từng từ, đúng dấu câu)`);
      tk = { s, n: kw.length };
    }
    return { goc, dich, hGoc, tk, len: c.dich.length };
  });
  // trạng thái nhìn (tâm, tỉ lệ) cho trang scan: nhìn toàn trang rồi lần lượt tới từng vùng câu
  const sc0 = Math.min(g.vw / anh.width, g.vh / anh.height) * 0.96;
  const nhin = cau.map((c) => {
    const [x, y, w, h] = c.vung, rw = Math.max(w, 0.5) * anh.width;
    const sc = clamp((g.vw * 0.88) / rw, sc0, 1.15);
    const lim = (c0, tong, nhin_) => (tong * sc <= nhin_ ? tong / 2 : clamp(c0, nhin_ / 2 / sc, tong - nhin_ / 2 / sc));
    return { cx: lim((x + w / 2) * anh.width, anh.width, g.vw), cy: lim((y + h / 2) * anh.height, anh.height, g.vh), sc };
  });
  return { ...R, g, anh, cau, moc, bo, nhin, nhin0: { cx: anh.width / 2, cy: anh.height / 2, sc: sc0 } };
}

// ---------------------------------------------------------------- phim-panel
async function chuanBiPhim(S, ctx, R) {
  const P = S.phim;
  if (!P || !P.mau) throw loi(S, '«phim» phải có {mau: "…/f%03d.jpg", n, fps} (khung trích sẵn bằng tools/trich_khung_phim.py)');
  if (!(P.n >= 1 && P.n <= MAX_KHUNG_PHIM)) throw loi(S, `phim.n = ${P.n}: nạp tối đa ${MAX_KHUNG_PHIM} khung (3–5 s ở 12–24 khung/s); trích ngắn hơn hoặc giảm fps`);
  if (!(P.fps > 0 && P.fps <= 30)) throw loi(S, 'phim.fps phải trong (0, 30]');
  const m = /%0(\d)d/.exec(P.mau);
  if (!m) throw loi(S, 'phim.mau phải chứa %0Nd, ví dụ f%03d.jpg');
  const dau = P.dau ?? 1;
  const ten = (i) => P.mau.replace(m[0], String(dau + i).padStart(+m[1], '0'));
  // nạp theo lô; đo byte giải mã từ kích thước thật, vượt trần thì dừng trước khi nạp tiếp
  const khung = [await napAnh(S, ten(0), 'phim khung 1')];
  let byte = uocRam(1, khung[0].width, khung[0].height);
  const ktra = (n) => { if (byte * (P.n / n) > TRAN_RAM_BYTE) throw loi(S, `${P.n} khung ${khung[0].width}×${khung[0].height} cần khoảng ${Math.round((byte * P.n) / n / 1048576)} MB sau giải mã, vượt trần ${Math.round(TRAN_RAM_BYTE / 1048576)} MB: trích lại với --rong nhỏ hơn hoặc ít khung hơn`); };
  ktra(1);
  for (let i = 1; i < P.n; i += LO_KHUNG) {
    const lo = await Promise.all(Array.from({ length: Math.min(LO_KHUNG, P.n - i) }, (_, j) => napAnh(S, ten(i + j), `phim khung ${i + j + 1}`)));
    for (const im of lo) { khung.push(im); byte += uocRam(1, im.width, im.height); }
    ktra(khung.length);
  }
  const so = S.so;
  if (!so || !soHopLe(so.value)) throw loi(S, '«so» phải có {value: số, unit, label}');
  const chip = S.chip ?? [];
  if (chip.length > 4) throw loi(S, 'tối đa 4 chip');
  const moc = await mocCuaThe(S, 1 + chip.length, [so.from, ...chip.map((c) => c.at)]);
  // khung phim 16:9 cùng trục với đầu thẻ; panel phải là 1/3 còn lại
  let fh = Math.min(621, 920 - R.y0), fw = Math.round((fh * 16) / 9);
  if (fh < 400) throw loi(S, 'đầu thẻ quá cao, không đủ chỗ cho khung phim (bỏ «title» hoặc rút ngắn)');
  const fx = LUOI.le, px = fx + fw + 48, pw = W - LUOI.le - px, pad = 32;
  ctx.save(); ctx.font = font(700, 96);
  const sizeSo = (() => { for (let s = 190; s >= 96; s -= 2) { ctx.font = font(700, s); if (ctx.measureText(fmtNum(so.value, so.dec ?? 0) + (so.suffix ?? '')).width <= pw - 2 * pad) return s; } throw loi(S, `số «${so.value}» quá dài cho panel (rộng ${pw - 2 * pad}px, cỡ tối thiểu 96px)`); })();
  ctx.font = font(500, CO.than, 'BVP');
  const nhanLines = so.label ? ngatDong(ctx, so.label, pw - 2 * pad) : [];
  ctx.font = font(600, 38); ctx.letterSpacing = '3px';
  const chipW = chip.map((c) => ctx.measureText(c.text).width + 40);
  ctx.restore();
  // chip xếp dòng
  const rows = []; let cur = [], cw = 0;
  chip.forEach((c, i) => { if (cw + chipW[i] > pw - 2 * pad && cur.length) { rows.push(cur); cur = []; cw = 0; } cur.push(i); cw += chipW[i] + 12; });
  if (cur.length) rows.push(cur);
  const cao = (S.panelNhan ? CO.nhanCao + 22 : 0) + sizeSo * 1.05 + (so.unit ? 74 : 0) + nhanLines.length * CO.than * 1.25 + 24 + rows.length * 74;
  if (cao > fh - 20) throw loi(S, `nội dung panel cao ${Math.round(cao)}px > ${fh - 20}px: bớt chip hoặc rút nhãn`);
  return { ...R, khung, P, fx, fy: R.y0, fw, fh, px, pw, pad, sizeSo, nhanLines, chipW, rows, moc };
}

// ---------------------------------------------------------------- the-am-thanh
async function chuanBiAmThanh(S, ctx, R) {
  const nhan = String(S.nhan ?? '').normalize('NFC').trim().toUpperCase();
  const anh = await napAnh(S, S.anh, 'anh');
  if (S.lanhTu === true && coAlphaAnh(S, anh, 'anh')) throw loi(S, 'ảnh lãnh tụ có vùng trong suốt (đã tách nền): dùng ảnh nguyên khung');
  const gi = S.giong;
  if (!gi || !gi.peaks) throw loi(S, '«giong.peaks» là JSON sóng âm tính từ tệp giọng thật (tools/song_am.py)');
  const pk = await napJson(S, gi.peaks, 'giong.peaks');
  if (!Array.isArray(pk.peaks) || pk.peaks.length < 10 || !(pk.dai > 0) || !pk.peaks.every(soHopLe)) throw loi(S, 'peaks.json hỏng (cần peaks[], dai > 0)');
  if (pk.peaks.reduce((m, v) => (v > m ? v : m), 0) < 0.05) throw loi(S, 'peaks.json phẳng: tệp giọng im lặng?');
  const sl = kiemThoiLuongGiong(S, pk.dai);
  if (sl.length) throw new Error(`LUẬT CỨNG: ${sl.join(' | ')}`);
  const ng = S.nguoi ?? {};
  if (!ng.ten || !ng.chucVu) throw loi(S, '«nguoi» cần {ten, chucVu}; chức vụ đúng thời điểm của lời nói');
  const pd = S.phuDe;
  if (!Array.isArray(pd) || !pd.length) throw loi(S, '«phuDe» phải là mảng {text} ít nhất một câu');
  const moc = await mocCuaThe(S, pd.length, pd.map((p) => p.at));
  const px = LUOI.le + 520 + 40, pw = W - LUOI.le - px;
  const hSub = 2 * 62, hFix = CO.nhanCao + 20 + 70 + 52 + (ng.boiCanh ? 50 : 0) + 16 + 20 + hSub;
  const hWave = Math.min(170, R.hC - hFix);
  if (hWave < 90) throw loi(S, 'đầu thẻ quá cao, không đủ chỗ cho sóng âm (bỏ «title»)');
  const sub = pd.map((p, i) => xepChu(S, ctx, p.text, { maxW: pw - 40, maxH: hSub, from: 48, to: 40, wt: 600, lh: 1.3, ten: `phuDe[${i}]` }));
  const nBar = Math.floor((pw - 40) / 8);
  const bars = Array.from({ length: nBar }, (_, i) => {
    const a = Math.floor((i * pk.peaks.length) / nBar), b = Math.max(a + 1, Math.floor(((i + 1) * pk.peaks.length) / nBar));
    let m = 0; for (let j = a; j < b; j++) if (pk.peaks[j] > m) m = pk.peaks[j];
    return m;
  });
  return { ...R, nhan, anh, pk, bars, nBar, moc, sub, px, pw, hWave, batDau: gi.batDau ?? 0.5, ng, pd };
}

// ---------------------------------------------------------------- nhan-vat
async function chuanBiNhanVat(S, ctx, R) {
  const bt = S.bienThe;
  if (!['tach-nen', 'khung'].includes(bt)) throw loi(S, `«bienThe» bắt buộc là «tach-nen» hoặc «khung» (nhận: «${bt ?? ''}»)`);
  const anh = await napAnh(S, S.anh, 'anh');
  if (S.lanhTu === true && coAlphaAnh(S, anh, 'anh')) throw loi(S, 'ảnh lãnh tụ có vùng trong suốt (đã tách nền): dùng ảnh nguyên khung');
  const sc = kiemCatLanhTu(S, anh.width, anh.height);
  if (sc.length) throw new Error(`LUẬT CỨNG: ${sc.join(' | ')}`);
  if (!S.ten || !S.chucVu) throw loi(S, 'cần «ten» và «chucVu» (chức vụ đúng thời điểm)');
  const tx = LUOI.le, tw = 900;
  let ten = null;
  for (const s of [104, 96, 88, 80, 72, 64]) { ctx.font = font(700, s); if (ctx.measureText(S.ten).width <= tw) { ten = { size: s, lines: [S.ten] }; break; } }
  if (!ten) { ctx.font = font(700, 64); const l = ngatDong(ctx, S.ten, tw); if (l.length > 2) throw loi(S, `«ten» quá dài (${S.ten.length} ký tự)`); ten = { size: 64, lines: l }; }
  const moc = await mocCuaThe(S, 3, [S.from, undefined, undefined].map((v, i) => (v ?? 0.3) + i * 0.6));
  const det = S.chiTiet ? xepChu(S, ctx, S.chiTiet, { maxW: tw, maxH: 3 * 44 * 1.3, from: 44, to: 40, wt: 500, fam: 'BVP', lh: 1.3, ten: 'chiTiet' }) : { size: 44, lines: [] };
  const R2 = { ...R, anh, bt, ten, det, moc, tx, tw };
  if (bt === 'khung') {
    const zd = S.zoomDen ?? 1.04;
    // Tính cả viền ngoài 30 px để khung không lấn vùng chữ tx..tx+tw.
    const maxW = W - LUOI.le - 40 - (tx + tw) - 30;
    const k = tinhKhungAnh(S, anh.width, anh.height, maxW, Math.min(R.hC - 40, 640));
    Object.assign(R2, k, { fx: W - LUOI.le - k.fw - 40, fy: R.y0 + (R.hC - k.fh) / 2, zd });
  } else {
    const hmax = R.hC + 30;
    const sc = Math.min(hmax / anh.height, 820 / anh.width);
    Object.assign(R2, { iw: anh.width * sc, ih: anh.height * sc });
  }
  return R2;
}

// ---------------------------------------------------------------- bieu-do
async function chuanBiBieuDo(S, ctx, R) {
  const kieu = S.kieu;
  if (!['cot-doi', 'nguoi'].includes(kieu)) throw loi(S, `«kieu» bắt buộc là «cot-doi» hoặc «nguoi» (nhận: «${kieu ?? ''}»)`);
  if (kieu === 'cot-doi') {
    const hang = S.hang;
    if (!Array.isArray(hang) || !hang.length || hang.length > 3) throw loi(S, '«hang» là mảng 1–3 hàng {nhan, ta, dich}');
    hang.forEach((h, i) => { if (!h.nhan || !soHopLe(h.ta) || !soHopLe(h.dich) || h.ta < 0 || h.dich < 0 || (h.ta === 0 && h.dich === 0)) throw loi(S, `hang[${i}] cần nhan và hai giá trị số ≥ 0, không cùng bằng 0`); });
    const moc = await mocCuaThe(S, hang.length, hang.map((h) => h.at));
    return { ...R, hang, moc };
  }
  const nhom = S.nhom;
  if (!Array.isArray(nhom) || !nhom.length || nhom.length > 2) throw loi(S, '«nhom» là mảng 1–2 nhóm {ten, soLuong}');
  const moi = S.moi ?? 1;
  if (!(moi >= 1) || !Number.isInteger(moi)) throw loi(S, '«moi» (số người mỗi hình) phải là số nguyên ≥ 1');
  const bo = nhom.map((n, i) => {
    if (!n.ten || !soHopLe(n.soLuong) || n.soLuong <= 0) throw loi(S, `nhom[${i}] cần ten và soLuong > 0`);
    const so = Math.ceil(n.soLuong / moi);
    if (so > 80) throw loi(S, `nhom[${i}] cần ${so} hình (> 80): tăng «moi»`);
    return { so, day: n.soLuong / moi };
  });
  const moc = await mocCuaThe(S, nhom.length, nhom.map((n) => n.at));
  return { ...R, nhom, moi, bo, moc };
}

// ============================================================ vẽ
export function taoCacTheMau(nd, ctx, S, ref) {
  const cuoi = (t, o) => nd.chan(t, o);
  const dauTrang = (t) => { nd.nen(t); nd.namMo(t, namCua(S)); nd.dauThe(t); };
  /** Tem «MẪU»: thẻ dùng dữ liệu giả tự nhận là mẫu ở góc phải trên, để không ai đăng nhầm. */
  function tem(t) {
    if (!S.mau) return;
    ctx.save(); ctx.font = font(600, CO.nhan); ctx.letterSpacing = '3px';
    const txt = 'MẪU · DỮ LIỆU GIẢ', w = ctx.measureText(txt).width + 40; ctx.restore();
    nd.nhan(txt, W - LUOI.le - w, 72, { kieu: 'do', a: ease.out(prog(t, 0.1, 0.3)) });
  }
  const R = () => ref.mau;

  // ---------- tai-lieu-dich ----------
  function taiLieu(t) {
    const { g, anh, cau, moc, bo, nhin, nhin0, y0, hC } = R();
    dauTrang(t); nd.ghiNhip(moc);
    // khung trang scan
    const a = ease.out(prog(t, 0.15, 0.5));
    nd.bang(g.vx, g.vy, g.vw, g.vh, { a });
    let v = nhin0;
    nhin.forEach((n, i) => {
      const k = ease.inOut(prog(t, moc[i] - 0.15, 0.9));
      v = { cx: lerp(v.cx, n.cx, k), cy: lerp(v.cy, n.cy, k), sc: Math.exp(lerp(Math.log(v.sc), Math.log(n.sc), k)) };
    });
    ctx.save(); ctx.globalAlpha = a; ctx.beginPath(); ctx.rect(g.vx + 8, g.vy + 8, g.vw - 16, g.vh - 16); ctx.clip();
    ctx.translate(g.vx + g.vw / 2, g.vy + g.vh / 2); ctx.scale(v.sc, v.sc); ctx.translate(-v.cx, -v.cy);
    ctx.drawImage(anh, 0, 0);
    const ic = moc.reduce((m, mm, i) => (t >= mm ? i : m), -1);
    ctx.globalCompositeOperation = 'multiply';
    cau.forEach((c, i) => {
      const k = ease.inOut(prog(t, moc[i] + 0.1, 0.7)); if (k <= 0) return;
      const [x, y, w, h] = c.vung;
      ctx.fillStyle = MAU.vang; ctx.globalAlpha = a * (i === ic ? 0.9 : 0.4);
      ctx.fillRect(x * anh.width, y * anh.height, w * anh.width * k, h * anh.height);
    });
    ctx.restore();
    // bảng bản dịch
    const A = appear(t, 0.2, { dur: 0.5, rise: 0, s0: 1 });
    nd.bang(g.px, y0, g.pw, hC, { a: A.a, gay: MAU.vang });
    nd.nhan(`BẢN DỊCH${S.tenTL ? ' · ' + S.tenTL : ''}`, g.px + g.pad, y0 + 30, { a: A.a });
    const xin = g.px + g.pad + 10, yTop = y0 + 30 + CO.nhanCao + 28;
    const ve = (i, alpha) => {
      const b = bo[i], c = cau[i], age = t - moc[i];
      const dur = clamp(b.len / 32, 0.5, Math.max(0.5, (moc[i + 1] ?? moc[i] + 3.5) - moc[i] - 0.2));
      const n = daGo(t, moc[i] + 0.12, dur, b.len), xong = n >= b.len;
      ctx.save(); ctx.globalAlpha = alpha * ease.out(prog(age, 0, 0.25)); ctx.textBaseline = 'alphabetic';
      let y = yTop;
      if (b.goc.lines.length) {
        ctx.font = font(400, 40, 'Lora', 'italic'); ctx.fillStyle = MAU.kemPhu;
        b.goc.lines.forEach((l, j) => ctx.fillText(l, xin, y + 40 + j * 52));
        y += b.hGoc;
      }
      const sz = b.dich.size, lh = sz * 1.2, base = y + sz;
      ctx.font = font(600, sz);
      // hộp từ khoá quét sau khi gõ xong, từng từ chuyển sang chữ than khi hộp phủ hết từ đó
      const ws = []; let off = 0;
      b.dich.lines.forEach((l, li) => {
        let x = xin; const sp = ctx.measureText(' ').width;
        l.split(' ').forEach((w, wi) => { const ww = ctx.measureText(w).width; ws.push({ w, x, y: base + li * lh, ww, ch: off, last: false }); x += ww + sp; off += w.length + 1; });
        ws[ws.length - 1].last = true;
      });
      const kk = b.tk ? ease.inOut(prog(t, moc[i] + 0.12 + dur + 0.1, 0.5)) : 0;
      let tong = 0, cum = 0;
      if (b.tk) for (let j = b.tk.s; j < b.tk.s + b.tk.n; j++) tong += ws[j].ww;
      ws.forEach((p, j) => {
        let cov = 0;
        if (b.tk && j >= b.tk.s && j < b.tk.s + b.tk.n) { cov = clamp((kk * tong - cum) / p.ww); cum += p.ww; }
        if (cov > 0) nd.hopTuKhoa(p.x - 8, p.y - sz * 1.0, p.ww + 16, sz * 1.3, cov);
      });
      ws.forEach((p, j) => {
        const k = Math.max(0, Math.min(p.w.length, n - p.ch)); if (k <= 0) return;
        const inTk = b.tk && j >= b.tk.s && j < b.tk.s + b.tk.n;
        let cov = 0; if (inTk) { let c0 = 0; for (let q = b.tk.s; q < j; q++) c0 += ws[q].ww; cov = clamp((kk * tong - c0) / p.ww); }
        ctx.font = font(600, sz); ctx.fillStyle = cov >= 1 ? MAU.than : MAU.kem; ctx.fillText(p.w.slice(0, k), p.x, p.y);
      });
      if (!xong && alpha > 0.5 && Math.floor(t * 3) % 2 === 0) { const last = ws.filter((p) => n > p.ch).pop(); if (last) { const k = Math.min(last.w.length, n - last.ch); ctx.font = font(600, sz); ctx.fillStyle = MAU.vang; ctx.fillRect(last.x + ctx.measureText(last.w.slice(0, k)).width + 6, last.y - sz * 0.8, 6, sz * 0.9); } }
      ctx.restore();
    };
    if (ic >= 0) {
      if (ic > 0 && t - moc[ic] < 0.2) ve(ic - 1, 1 - prog(t - moc[ic], 0, 0.2));
      ve(ic, 1);
    }
    tem(t); cuoi(t);
  }

  // ---------- phim-panel ----------
  function phimPanel(t) {
    const { khung, P, fx, fy, fw, fh, px, pw, pad, sizeSo, nhanLines, chipW, rows, moc } = R();
    dauTrang(t); nd.ghiNhip(moc);
    const a = ease.out(prog(t, 0.1, 0.5));
    // khung phim: chỉ phát lại khung đã trích (renderFrame thuần theo t); trước giờ bắt đầu giữ khung đầu, hết phim giữ khung cuối
    const bd = P.batDau ?? 0.3, idx0 = (t - bd) * P.fps;
    const idx = P.lap ? ((Math.floor(idx0) % P.n) + P.n) % P.n : clamp(Math.floor(idx0), 0, P.n - 1);
    const im = khung[idx];
    ctx.save(); ctx.globalAlpha = a;
    ctx.fillStyle = MAU.khung; ctx.fillRect(fx, fy, fw, fh);
    const fit = P.fit === 'phu' ? Math.max(fw / im.width, fh / im.height) : Math.min(fw / im.width, fh / im.height);
    ctx.beginPath(); ctx.rect(fx, fy, fw, fh); ctx.clip();
    ctx.drawImage(im, fx + (fw - im.width * fit) / 2, fy + (fh - im.height * fit) / 2, im.width * fit, im.height * fit);
    ctx.restore();
    ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = 'rgba(217,211,182,0.55)'; ctx.lineWidth = 3; ctx.strokeRect(fx - 1.5, fy - 1.5, fw + 3, fh + 3); ctx.restore();
    // panel số
    nd.bang(px, fy, pw, fh, { a, gay: MAU.do });
    const so = S.so; let y = fy + 26;
    const x = px + pad + 10;
    if (S.panelNhan) { nd.nhan(S.panelNhan, x, y, { a }); y += CO.nhanCao + 22; }
    const A = appear(t, moc[0], { dur: 0.5, rise: 24, s0: 0.94 });
    if (A.a > 0) {
      const dur = so.count === false ? 0.12 : so.dur ?? 1.4;
      const v = lerp(so.start ?? 0, so.value, ease.expoOut(prog(t, moc[0], dur)));
      const txt = fmtNum(t >= moc[0] + dur * 0.92 ? so.value : Math.round(v), so.dec ?? 0) + (so.suffix ?? '');
      ctx.save(); ctx.globalAlpha = A.a; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
      ctx.font = font(700, sizeSo); ctx.fillStyle = MAU.kem; const base = y + sizeSo * 0.92 + A.y; ctx.fillText(txt, x, base);
      const u = ease.expoOut(prog(t, moc[0] + dur * 0.92, 0.45)); ctx.fillStyle = MAU.do; ctx.fillRect(x, base + 14, ctx.measureText(txt).width * u, 8);
      y += sizeSo * 1.05;
      if (so.unit) { ctx.font = font(600, CO.than - 4); ctx.fillStyle = MAU.vang; ctx.fillText(so.unit, x, y + 50); y += 74; }
      ctx.font = font(500, CO.than, 'BVP'); ctx.fillStyle = MAU.kem;
      nhanLines.forEach((l, j) => ctx.fillText(l, x, y + 30 + j * CO.than * 1.25));
      y += nhanLines.length * CO.than * 1.25 + 24;
      ctx.restore();
    } else y += sizeSo * 1.05 + (so.unit ? 74 : 0) + nhanLines.length * CO.than * 1.25 + 24;
    rows.forEach((r, ri) => { let cx = x; r.forEach((i) => { const C = appear(t, moc[1 + i], { dur: 0.4, rise: 14, s0: 0.92 }); if (C.a > 0) nd.nhan(S.chip[i].text, cx, y + ri * 74 + C.y, { kieu: S.chip[i].kieu ?? 'vien', size: 38, a: C.a, k: ease.expoOut(prog(t, moc[1 + i], 0.35)) }); cx += chipW[i] + 12; }); });
    tem(t); cuoi(t);
  }

  // ---------- the-am-thanh ----------
  function amThanh(t) {
    const { anh, pk, bars, nBar, moc, sub, px, pw, hWave, batDau, ng, y0, hC, nhan } = R();
    dauTrang(t); nd.ghiNhip(moc);
    const a = ease.out(prog(t, 0.1, 0.5));
    // ảnh người nói: cắt phủ khung, chỉ phóng đều chậm (không rung, không méo, không tách nền)
    const fx = LUOI.le, fw = 520, fh = hC;
    nd.bang(fx, y0, fw, fh, { a });
    const z = Math.min(TRAN_ZOOM_LANH_TU, 1 + 0.04 * prog(t, 0, S.duration)), cov = Math.max((fw - 16) / anh.width, (fh - 16) / anh.height) * z;
    const [nx, ny] = S.anhNeo ?? [0.5, 0.35];
    ctx.save(); ctx.globalAlpha = a; ctx.beginPath(); ctx.rect(fx + 8, y0 + 8, fw - 16, fh - 16); ctx.clip();
    const iw = anh.width * cov, ih = anh.height * cov;
    ctx.drawImage(anh, fx + 8 - (iw - (fw - 16)) * nx, y0 + 8 - (ih - (fh - 16)) * ny, iw, ih);
    ctx.restore();
    // nhãn: có mặt suốt thời gian thẻ, không tắt
    const gi = nhan === 'GHI ÂM GỐC' ? 'dac' : 'do';
    const X = px + 20; let y = y0;
    nd.nhan(nhan, X, y, { kieu: gi, a: appear(t, 0.05, { dur: 0.3, rise: 0, s0: 1 }).a }); y += CO.nhanCao + 20;
    const B = appear(t, 0.2, { dur: 0.5, rise: 14, s0: 1 });
    ctx.save(); ctx.globalAlpha = B.a; ctx.textBaseline = 'alphabetic';
    ctx.font = font(700, 64); ctx.fillStyle = MAU.kem; ctx.fillText(ng.ten, X, y + 56 + B.y);
    ctx.font = font(500, CO.thanPhu + 4, 'BVP'); ctx.fillStyle = MAU.vang; ctx.fillText(ng.chucVu, X, y + 70 + 46 + B.y);
    if (ng.boiCanh) { ctx.font = font(500, 40, 'BVP'); ctx.fillStyle = MAU.kemPhu; ctx.fillText(ng.boiCanh, X, y + 70 + 52 + 46 + B.y); }
    ctx.restore();
    y += 70 + 52 + (ng.boiCanh ? 50 : 0) + 16;
    // sóng âm từ peaks của tệp giọng thật; đầu đọc đỏ chạy theo t
    const wx = px, ww = pw, wy = y;
    nd.bang(wx, wy, ww, hWave, { a });
    const tr = clamp((t - batDau) / pk.dai), mid = wy + hWave / 2, bw = 5, step = (ww - 40) / nBar;
    ctx.save(); ctx.globalAlpha = a;
    bars.forEach((v, i) => {
      const hh = Math.max(4, v * (hWave - 36)), x = wx + 20 + i * step, r = ease.out(prog(t, 0.2 + (i / nBar) * 0.35, 0.3));
      ctx.fillStyle = i / nBar < tr ? MAU.kem : 'rgba(217,211,182,0.38)'; ctx.fillRect(x, mid - (hh * r) / 2, bw, hh * r);
    });
    const hx = wx + 20 + tr * (ww - 40);
    ctx.fillStyle = MAU.do; ctx.fillRect(hx - 3, wy + 8, 6, hWave - 16);
    ctx.beginPath(); ctx.moveTo(hx - 11, wy + 2); ctx.lineTo(hx + 11, wy + 2); ctx.lineTo(hx, wy + 18); ctx.closePath(); ctx.fill();
    ctx.restore();
    // phụ đề: câu đang đọc
    const ic = moc.reduce((m, mm, i) => (t >= mm ? i : m), -1);
    if (ic >= 0) {
      const s = sub[ic], C = appear(t, moc[ic], { dur: 0.35, rise: 12, s0: 1 });
      ctx.save(); ctx.globalAlpha = C.a; ctx.textBaseline = 'alphabetic'; ctx.font = font(600, s.size); ctx.fillStyle = MAU.kem;
      s.lines.forEach((l, j) => ctx.fillText(l, X, wy + hWave + 20 + s.size + j * s.size * 1.3 + C.y));
      ctx.restore();
    }
    tem(t); cuoi(t);
  }

  // ---------- nhan-vat ----------
  function nhanVat(t) {
    const Rr = R(); const { anh, bt, ten, det, moc, tx, tw, y0, hC } = Rr;
    dauTrang(t); nd.ghiNhip(moc);
    // khối chữ bên trái
    const bang = appear(t, 0.1, { dur: 0.5, rise: 0, s0: 1 });
    nd.bang(tx - 20, y0, tw + 40, hC, { a: bang.a, gay: MAU.vang });
    let y = y0 + 36;
    const n = daGo(t, moc[0], 0.9, S.ten.length);
    ctx.save(); ctx.textBaseline = 'alphabetic'; ctx.font = font(700, ten.size); ctx.fillStyle = MAU.kem;
    const ga = ease.out(prog(t, moc[0], 0.2));
    ctx.globalAlpha = bang.a * ga;
    veGo(ctx, ten.lines, n, tx + 22, y + ten.size * 0.95, ten.size * 1.08);
    ctx.restore();
    y += ten.lines.length * ten.size * 1.08 + 30;
    const C = appear(t, moc[1], { dur: 0.4, rise: 12, s0: 1 });
    if (C.a > 0) nd.nhan(S.chucVu, tx + 22, y + C.y, { a: C.a, k: ease.expoOut(prog(t, moc[1], 0.4)) });
    y += CO.nhanCao + 26;
    const D = appear(t, moc[2], { dur: 0.45, rise: 12, s0: 1 });
    if (D.a > 0 && det.lines.length) { ctx.save(); ctx.globalAlpha = D.a; ctx.font = font(500, det.size, 'BVP'); ctx.fillStyle = MAU.kem; ctx.textBaseline = 'alphabetic'; det.lines.forEach((l, j) => ctx.fillText(l, tx + 22, y + det.size + j * det.size * 1.3 + D.y)); ctx.restore(); }
    // ảnh bên phải
    const ia = ease.out(prog(t, 0.2, 0.6));
    if (bt === 'tach-nen') {
      const { iw, ih } = Rr, z = 1 + 0.03 * prog(t, 0, S.duration), cx = W - LUOI.le - 40 - iw / 2, base = y0 + hC + 12;
      ctx.save(); ctx.globalAlpha = ia * 0.5;
      const g = ctx.createRadialGradient(cx, base - ih * 0.45, 20, cx, base - ih * 0.45, ih * 0.75); g.addColorStop(0, 'rgba(244,238,218,0.20)'); g.addColorStop(1, 'rgba(244,238,218,0)');
      ctx.fillStyle = g; ctx.fillRect(cx - ih, base - ih * 1.3, ih * 2, ih * 1.5); ctx.restore();
      ctx.save(); ctx.globalAlpha = ia * 0.5; ctx.fillStyle = 'rgba(8,10,4,0.7)'; ctx.beginPath(); ctx.ellipse(cx, base, iw * 0.46, 14, 0, 0, Math.PI * 2); ctx.fill(); ctx.restore();
      ctx.save(); ctx.globalAlpha = ia; ctx.translate(cx, base); ctx.scale(z, z); ctx.drawImage(anh, -iw / 2, -ih, iw, ih); ctx.restore();
    } else {
      // khung trang trọng: ảnh cắt vuông vắn đúng tỉ lệ khung, chỉ phóng đều chậm; không hiệu ứng nào khác lên mặt
      const { fw, fh, fx, fy, cw, ch, cx, cy, zd } = Rr, z = lerp(1, zd, prog(t, 0, S.duration)), sw = cw / z, sh = ch / z;
      ctx.save(); ctx.globalAlpha = ia;
      ctx.fillStyle = MAU.vang; ctx.fillRect(fx - 30, fy - 30, fw + 60, fh + 60);
      ctx.fillStyle = MAU.nenToi; ctx.fillRect(fx - 24, fy - 24, fw + 48, fh + 48);
      ctx.strokeStyle = 'rgba(244,238,218,0.6)'; ctx.lineWidth = 2; ctx.strokeRect(fx - 11, fy - 11, fw + 22, fh + 22);
      ctx.drawImage(anh, cx - sw / 2, cy - sh / 2, sw, sh, fx, fy, fw, fh);
      ctx.restore();
    }
    tem(t); cuoi(t);
  }

  // ---------- bieu-do ----------
  function bieuDo(t) {
    const Rr = R(); const { y0, hC, moc } = Rr;
    dauTrang(t); nd.ghiNhip(moc);
    const bot = LUOI.noiDungDuoi;
    if (S.kieu === 'cot-doi') cotDoi(t, Rr, y0, bot); else nguoi(t, Rr, y0, bot);
    tem(t); cuoi(t);
  }
  function cotDoi(t, { hang, moc }, y0, bot) {
    const cx = W / 2, half = noiDungW / 2, soW = 210, barMax = half - soW - 24, bank = ease.out(prog(t, 0.15, 0.5));
    nd.bang(LUOI.le, y0, noiDungW, bot - y0, { a: bank });
    const tenTa = S.tenTa ?? 'QUÂN TA', tenDich = S.tenDich ?? 'ĐỐI PHƯƠNG';
    ctx.save(); ctx.font = font(600, CO.nhan); ctx.letterSpacing = '3px';
    const wTa = ctx.measureText(tenTa).width + 40, wDich = ctx.measureText(tenDich).width + 40; ctx.restore();
    nd.nhan(tenTa, cx - 30 - wTa, y0 + 22, { kieu: 'do', a: bank });
    nd.nhan(tenDich, cx + 30, y0 + 22, { kieu: 'vien', a: bank });
    const top = y0 + 22 + CO.nhanCao + 20, rowH = (bot - top - 16) / hang.length;
    const chung = S.thang === 'chung' ? Math.max(...hang.flatMap((h) => [h.ta, h.dich])) : null;
    hang.forEach((h, i) => {
      const A = appear(t, moc[i], { dur: 0.4, rise: 12, s0: 1 });
      if (A.a <= 0) return;
      const m = chung ?? Math.max(h.ta, h.dich), dur = 1.3, k = ease.expoOut(prog(t, moc[i] + 0.1, dur));
      const y = top + i * rowH, bh = Math.min(84, rowH * 0.46);
      ctx.save(); ctx.globalAlpha = A.a; ctx.textBaseline = 'alphabetic';
      ctx.font = font(600, CO.thanPhu + 2, 'BVP'); ctx.textAlign = 'center'; ctx.fillStyle = MAU.kem; ctx.fillText(h.nhan, cx, y + 40 + A.y);
      const by = y + 56 + A.y, lw = (barMax * h.ta) / m * k, rw = (barMax * h.dich) / m * k;
      ctx.fillStyle = MAU.do; ctx.fillRect(cx - 12 - lw, by, lw, bh);
      ctx.fillStyle = MAU.xanhDich; ctx.fillRect(cx + 12, by, rw, bh);
      ctx.fillStyle = 'rgba(244,238,218,0.55)'; ctx.fillRect(cx - 2, by - 6, 4, bh + 12);
      const fs = Math.max(56, Math.min(72, bh * 0.9));
      ctx.font = font(700, fs); ctx.fillStyle = MAU.kem;
      ctx.textAlign = 'right'; ctx.fillText(fmtNum(Math.round(h.ta * k), h.dec ?? 0), cx - 12 - Math.max(lw, 0) - 18 + (lw < 1 ? 0 : 0), by + bh / 2 + fs * 0.36);
      ctx.textAlign = 'left'; ctx.fillText(fmtNum(Math.round(h.dich * k), h.dec ?? 0), cx + 12 + rw + 18, by + bh / 2 + fs * 0.36);
      ctx.restore();
    });
  }
  function nguoi(t, { nhom, moi, bo, moc }, y0, bot) {
    const n = nhom.length, gap = 24, ph = (bot - y0 - gap * (n - 1)) / n, bank = ease.out(prog(t, 0.15, 0.5));
    nhom.forEach((g, gi) => {
      const y = y0 + gi * (ph + gap), x = LUOI.le, leftW = 520, ta = (g.mau ?? (gi === 0 ? 'ta' : 'dich')) === 'ta';
      const A = appear(t, moc[gi], { dur: 0.4, rise: 12, s0: 1 });
      nd.bang(x, y, noiDungW, ph, { a: bank, gay: ta ? MAU.do : MAU.xanhDich });
      if (A.a <= 0) return;
      const dur = Math.min(2.4, bo[gi].so * 0.045 + 0.4), k = prog(t, moc[gi] + 0.15, dur);
      ctx.save(); ctx.globalAlpha = A.a; ctx.textBaseline = 'alphabetic';
      ctx.font = font(600, CO.thanPhu + 2, 'BVP'); ctx.fillStyle = ta ? MAU.doChu : MAU.xanhDich; ctx.fillText(g.ten, x + 40, y + 62 + A.y);
      let fs = 150; ctx.font = font(700, fs);
      const val = Math.round(g.soLuong * ease.out(k)), txt = fmtNum(g.soLuong >= 0 ? val : 0, 0);
      const full = fmtNum(g.soLuong, 0);
      while (ctx.measureText(full).width > leftW - 60 && fs > 96) { fs -= 4; ctx.font = font(700, fs); }
      ctx.fillStyle = MAU.kem; ctx.fillText(txt, x + 40, y + 70 + fs * 0.95 + A.y);
      if (g.donVi) { ctx.font = font(600, CO.than - 4); ctx.fillStyle = MAU.vang; ctx.fillText(g.donVi, x + 40, y + 70 + fs * 0.95 + 56 + A.y); }
      ctx.restore();
      // lưới hình người: chọn số hàng cho hình lớn nhất
      const total = bo[gi].so, ax = x + leftW + 20, aw = noiDungW - leftW - 60, ay = y + 24, ah = ph - 48 - (moi > 1 ? 54 : 0);
      let best = { s: 0, cols: total, rows: 1 };
      for (let r = 1; r <= 8; r++) { const cols = Math.ceil(total / r), s = Math.min(aw / cols, ah / r); if (s > best.s) best = { s, cols, rows: r }; }
      const s = best.s;
      for (let i = 0; i < total; i++) {
        const shown = clamp(k * total - i), col = i % best.cols, row = Math.floor(i / best.cols), cx = ax + col * s + s / 2, cy = ay + row * s + s / 2;
        veNguoi(cx, cy, s * 0.82, ta ? MAU.do : MAU.xanhDich, A.a, shown, i === total - 1 ? bo[gi].day - (total - 1) : 1);
      }
      if (moi > 1) nd.nhan(`1 HÌNH = ${fmtNum(moi)} ${S.donVi ?? 'NGƯỜI'}`, ax, y + ph - 20 - CO.nhanCao, { kieu: 'vien', a: A.a });
    });
  }
  /** Hình người ký hiệu (đầu tròn + thân), vẽ bằng code, không tả thực. `phan` = phần hình được lấp (hình cuối có thể lẻ). */
  function veNguoi(cx, cy, s, mau, a, hien, phan) {
    if (hien <= 0) return;
    ctx.save(); ctx.globalAlpha = a * hien; ctx.translate(cx, cy + (1 - ease.out(hien)) * 10);
    const dung = (fill) => {
      ctx.fillStyle = fill; ctx.beginPath(); ctx.arc(0, -s * 0.3, s * 0.15, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.moveTo(-s * 0.2, s * 0.42); ctx.lineTo(-s * 0.2, -s * 0.06); ctx.quadraticCurveTo(0, -s * 0.16, s * 0.2, -s * 0.06); ctx.lineTo(s * 0.2, s * 0.42); ctx.closePath(); ctx.fill();
    };
    if (phan < 0.999) { dung('rgba(244,238,218,0.22)'); ctx.beginPath(); ctx.rect(-s / 2, -s / 2, s * phan, s); ctx.clip(); }
    dung(mau); ctx.restore();
  }

  return { 'tai-lieu-dich': taiLieu, 'phim-panel': phimPanel, 'the-am-thanh': amThanh, 'nhan-vat': nhanVat, 'bieu-do': bieuDo };
}
