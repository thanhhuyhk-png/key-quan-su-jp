// Luật cứng của kênh cho các mẫu P2, phần thuần dữ liệu (không DOM, test được bằng node). Bản Python song song: tools/luat_cung.py.
// Cả hai đọc chung data/lanh-tu.json. Nguyên tắc: NGHI NGỜ THÌ BÁO LỖI, không cho qua.
export const LOAI_P2 = ['tai-lieu-dich', 'phim-panel', 'the-am-thanh', 'nhan-vat', 'bieu-do'];
export const NHAN_AM_THANH = ['MÔ PHỎNG LẠI', 'GHI ÂM GỐC'];
export const TRAN_ZOOM_LANH_TU = 1.08;       // ảnh lãnh tụ chỉ phóng đều rất chậm, trần 8 %
export const TI_LE_KHUNG_MIN = 0.6;         // giới hạn rộng/cao của khung theo từng ảnh
export const TI_LE_KHUNG_MAX = 1.6;
export const TRAN_PHONG_CAT = 2;             // ảnh lãnh tụ: vùng cắt ≥ 1/2 cạnh ảnh (phóng ≤ 2 lần), không cắt sát mặt
export const TRAN_RAM_BYTE = 450 * 1024 * 1024; // tổng byte khung phim sau giải mã
const BO_QUA = ['source', 'credit'];         // nguồn có thể nhắc tên lãnh tụ (tên sách, báo) nên không quét

const isNum = (v) => typeof v === 'number' && Number.isFinite(v);

/** Chuỗi không dấu, chữ thường, chỉ chữ số/chữ cái, bọc bằng khoảng trắng để so khớp từ nguyên. */
export function chuanChu(s) {
  const t = String(s ?? '').normalize('NFD').replace(/\p{M}/gu, '').toLowerCase().replace(/đ/g, 'd').replace(/[^a-z0-9]+/g, ' ').trim();
  return ` ${t} `;
}
export const chuanNhan = (s) => String(s ?? '').normalize('NFC').trim().toUpperCase();

/** Duyệt mọi trường chữ của shot (đệ quy), trả [{path, ten}] khi gặp tên trong danh sách. */
export function timTenLanhTu(obj, names, path = '') {
  const ds = names.map((n) => [n, chuanChu(n)]);
  const out = [];
  const di = (v, p) => {
    if (typeof v === 'string') { const c = chuanChu(v); for (const [n, k] of ds) if (c.includes(k)) out.push({ path: p, ten: n }); }
    else if (Array.isArray(v)) v.forEach((x, i) => di(x, `${p}[${i}]`));
    else if (v && typeof v === 'object') for (const [k, x] of Object.entries(v)) if (!(p === '' && BO_QUA.includes(k))) di(x, p ? `${p}.${k}` : k);
  };
  di(obj, path);
  return out;
}

/** Số byte bitmap của n khung rộng w, cao h (RGBA). */
export const uocRam = (n, w, h) => n * w * h * 4;

/** Tỉ lệ khai tay phải hợp lệ; tỉ lệ ảnh tự suy được kẹp vào khoảng cho phép. */
export function tiLeKhung(S, w, h) {
  if ('tiLe' in S) {
    if (!isNum(S.tiLe) || S.tiLe < TI_LE_KHUNG_MIN || S.tiLe > TI_LE_KHUNG_MAX) throw new Error('[nhan-vat] «tiLe» phải là số dương hữu hạn trong [' + TI_LE_KHUNG_MIN + '; ' + TI_LE_KHUNG_MAX + ']');
    return S.tiLe;
  }
  return Math.max(TI_LE_KHUNG_MIN, Math.min(TI_LE_KHUNG_MAX, w / h));
}

/** Vùng cắt chuẩn hoá theo ảnh w×h, cat = [tâmX, tâmY, rộng], tỉ lệ khung rộng/cao. */
export function vungCat(cat, w, h, tiLe = tiLeKhung({}, w, h)) {
  const cw = cat[2] * w, ch = cw / tiLe;
  return { rong: cw / w, cao: ch / h };
}

/** Tính khung và vùng cắt không kéo giãn ảnh; thiếu cat thì lấy vùng lớn nhất vừa ảnh. */
export function tinhKhungAnh(S, w, h, maxW, maxH) {
  const tiLe = tiLeKhung(S, w, h);
  const cat = 'cat' in S ? S.cat : [0.5, 0.5, Math.min(1, tiLe * h / w)];
  if (!(Array.isArray(cat) && cat.length === 3 && cat.every(isNum))) throw new Error('[nhan-vat] «cat» là [tâmX, tâmY, rộng] toàn số');
  const cw = cat[2] * w, ch = cw / tiLe, cx = cat[0] * w, cy = cat[1] * h;
  if (cw <= 0 || cx - cw / 2 < -0.5 || cx + cw / 2 > w + 0.5 || cy - ch / 2 < -0.5 || cy + ch / 2 > h + 0.5) throw new Error('[nhan-vat] «cat» vượt ra ngoài ảnh (tỉ lệ khung ' + tiLe + ' không vừa); giảm «rộng» hoặc dời tâm. Không kéo giãn ảnh để lấp');
  const fh = Math.min(maxH, maxW / tiLe), fw = fh * tiLe;
  return { tiLe, fw, fh, cw, ch, cx, cy };
}

/** Kiểm dữ liệu shot P2. Trả list lỗi (rỗng = đạt). names = data/lanh-tu.json .ten. */
export function kiemDuLieu(S, names) {
  const loi = [];
  const t = S.type;
  if (!LOAI_P2.includes(t)) return loi;
  const pre = `[${t}]`;
  if (!(S.source || S.credit)) loi.push(`${pre} thiếu «source» (nguồn góc phải dưới là bắt buộc)`);
  if ('lanhTu' in S && typeof S.lanhTu !== 'boolean') loi.push(`${pre} «lanhTu» phải là true hoặc false (nhận: ${JSON.stringify(S.lanhTu)}): cờ sai kiểu làm luật lãnh tụ bị bỏ qua`);
  const lanhTu = S.lanhTu === true;
  if ((t === 'nhan-vat' || t === 'the-am-thanh') && !lanhTu) {
    for (const h of timTenLanhTu(S, names)) loi.push(`${pre} «${h.path}» nhắc tên lãnh tụ «${h.ten}» mà shot không khai lanhTu: true`);
  }
  if (t === 'nhan-vat') {
    const bt = S.bienThe;
    if (!['tach-nen', 'khung'].includes(bt)) loi.push(`${pre} «bienThe» bắt buộc là «tach-nen» hoặc «khung» (nhận: ${JSON.stringify(bt)})`);
    if (lanhTu && bt !== 'khung') loi.push(`${pre} lãnh tụ dùng biến thể ${JSON.stringify(bt)}: chỉ được «khung», cấm tách nền, sửa ảnh lãnh tụ`);
    if ('zoomDen' in S) {
      if (!isNum(S.zoomDen)) loi.push(`${pre} «zoomDen» phải là số (nhận: ${JSON.stringify(S.zoomDen)})`);
      else if (S.zoomDen < 1 || S.zoomDen > TRAN_ZOOM_LANH_TU) loi.push(`${pre} «zoomDen» ${S.zoomDen} ngoài [1; ${TRAN_ZOOM_LANH_TU}]: ảnh chỉ được phóng đều rất chậm`);
    }
    if (bt === 'khung' && 'tiLe' in S) {
      try { tiLeKhung(S); } catch (e) { loi.push(e.message); }
    }
    if ((lanhTu || bt === 'khung') && 'cat' in S && !(Array.isArray(S.cat) && S.cat.length === 3 && S.cat.every(isNum))) loi.push(`${pre} «cat» là [tâmX, tâmY, rộng] toàn số`);
  }
  if (t === 'the-am-thanh') {
    if (S.nhan === undefined || S.nhan === null || S.nhan === '') loi.push(`${pre} thiếu «nhan»: bắt buộc «MÔ PHỎNG LẠI» hoặc «GHI ÂM GỐC»`);
    else if (!NHAN_AM_THANH.includes(chuanNhan(S.nhan))) loi.push(`${pre} «nhan» ${JSON.stringify(S.nhan)} không hợp lệ: chỉ «MÔ PHỎNG LẠI» hoặc «GHI ÂM GỐC»`);
    else if (lanhTu && chuanNhan(S.nhan) !== 'GHI ÂM GỐC') loi.push(`${pre} lãnh tụ có «nhan» ${JSON.stringify(S.nhan)}: chỉ được «GHI ÂM GỐC», cấm dựng giọng lãnh tụ`);
    const g = S.giong ?? {};
    if (!g.tep) loi.push(`${pre} thiếu «giong.tep» (tệp giọng thật mà peaks được tính từ đó)`);
    if (!g.peaks) loi.push(`${pre} thiếu «giong.peaks» (JSON sóng âm từ tools/song_am.py)`);
    if ('batDau' in g && !(isNum(g.batDau) && g.batDau >= 0)) loi.push(`${pre} «giong.batDau» phải là số ≥ 0`);
  }
  if (t === 'phim-panel') {
    const p = S.phim ?? {};
    if (!Number.isInteger(p.n) || p.n < 1) loi.push(`${pre} «phim.n» phải là số nguyên dương (nhận: ${JSON.stringify(p.n)})`);
    if ('dau' in p && !(Number.isInteger(p.dau) && p.dau >= 0)) loi.push(`${pre} «phim.dau» phải là số nguyên ≥ 0`);
  }
  return loi;
}

/** Giọng thật phải phủ khoảng tiếng của thẻ: batDau + dai lệch duration quá 0,5 s thì sóng lệch tiếng. */
export function kiemThoiLuongGiong(S, dai) {
  const bd = S.giong?.batDau ?? 0.5, d = S.duration;
  if (!isNum(d)) return ['[the-am-thanh] thiếu «duration» số'];
  if (Math.abs(bd + dai - d) > 0.5 + 1e-9) return [`[the-am-thanh] giọng dài ${dai} s bắt đầu ${bd} s kết thúc ${(bd + dai).toFixed(2)} s, lệch «duration» ${d} s quá 0,5 s: sóng và đầu đọc sẽ lệch tiếng`];
  return [];
}

/** Trần phóng cắt ảnh lãnh tụ: vùng cắt phải ≥ 1/TRAN_PHONG_CAT cạnh ảnh theo cả hai chiều. */
export function kiemCatLanhTu(S, w, h) {
  if (S.lanhTu !== true || S.bienThe !== 'khung') return [];
  let k;
  try { k = tinhKhungAnh(S, w, h, w, h); } catch (e) { return [e.message]; }
  const v = vungCat([0.5, 0.5, k.cw / w], w, h, k.tiLe), min = 1 / TRAN_PHONG_CAT;
  if (v.rong < min - 1e-9 || v.cao < min - 1e-9) return [`[nhan-vat] «cat» cắt ảnh lãnh tụ phóng quá ${TRAN_PHONG_CAT} lần (vùng cắt ${(v.rong * 100).toFixed(0)}% × ${(v.cao * 100).toFixed(0)}% ảnh, cần ≥ ${min * 100}% mỗi chiều): không cắt sát mặt`];
  return [];
}
