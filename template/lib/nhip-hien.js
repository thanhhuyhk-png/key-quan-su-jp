// Nhịp hiện của thẻ: logic thuần (không DOM, không canvas) để test được bằng node.
// Một thẻ được dựng dần theo lời: mỗi phần tử có một mốc giây hiện. Mốc lấy theo thứ tự ưu tiên:
//   1. SHOT.moc = [giây, ...]            mảng mốc cho từng phần tử, theo thứ tự phần tử của loại thẻ
//   2. SHOT.nhip = {from, to, buoc}      tự chia đều các phần tử trong [from, to] (hoặc cách nhau `buoc` giây)
//   3. mốc riêng của từng phần tử (from, at…) khai trong shot, như trước nay
// Mọi hàm ở đây thuần theo đầu vào, không dùng số ngẫu nhiên.

/** Khoảng tối thiểu (giây) giữa hai nhịp: phần tử hiện cách mốc đầu của nhóm chưa tới khoảng này thì cùng một nhịp. */
export const KHOANG_NHIP = 0.5;

/** Chuẩn hoá một mảng mốc: không âm, không giảm dần; giá trị không phải số lấy mốc liền trước (đầu mảng lấy 0). */
function tangDan(arr) {
  const out = [];
  let prev = 0;
  for (const v of arr) {
    prev = Math.max(prev, Number.isFinite(v) ? Math.max(0, v) : prev);
    out.push(prev);
  }
  return out;
}

/**
 * Chia mốc cho n phần tử.
 * @param {number} n số phần tử
 * @param {{moc?: number[], from?: number, to?: number, buoc?: number}} o
 *   moc: mốc cho sẵn (ngắn hơn n thì kéo dài thêm `buoc` giây mỗi phần tử)
 *   from, to: chia đều trong khoảng; buoc: khoảng cách cố định (mặc định 0,9 s)
 * @returns {number[]} n mốc không giảm
 */
export function chiaMoc(n, { moc, from = 0.5, to, buoc = 0.9 } = {}) {
  if (!(n > 0)) return [];
  if (Array.isArray(moc) && moc.length) {
    const base = tangDan(moc.slice(0, n));
    while (base.length < n) base.push(base[base.length - 1] + buoc);
    return base;
  }
  if (to != null && n > 1) return Array.from({ length: n }, (_, i) => from + ((to - from) * i) / (n - 1));
  return Array.from({ length: n }, (_, i) => from + i * buoc);
}

/**
 * Mốc hiện của n phần tử trong một shot.
 * @param {object} S SHOT
 * @param {number} n số phần tử của loại thẻ
 * @param {number[]} [mac] mốc riêng khai trong shot (dùng khi shot không có moc và nhip)
 */
export function mocPhanTu(S, n, mac = []) {
  if (Array.isArray(S.moc) && S.moc.length) return chiaMoc(n, { moc: S.moc });
  if (S.nhip && typeof S.nhip === 'object') return chiaMoc(n, S.nhip);
  const ok = mac.length >= n && mac.slice(0, n).every(Number.isFinite);
  return ok ? mac.slice(0, n) : chiaMoc(n, { moc: mac.filter(Number.isFinite) });
}

/**
 * Số nhịp hiện: sắp mốc tăng dần; một nhịp là nhóm mốc bắt đầu từ mốc đầu của nhóm và gồm mọi mốc cách nó chưa tới `gap`
 * giây (mặc định KHOANG_NHIP). Tính từ mốc đầu nhóm, không từ mốc liền trước, nên chuỗi mốc dày kéo dài vẫn tách thành nhiều nhịp.
 */
export function demNhip(mocs, gap = KHOANG_NHIP) {
  const s = mocs.filter(Number.isFinite).sort((a, b) => a - b);
  let n = 0, dau = -Infinity;
  for (const v of s) { if (v - dau >= gap) { n++; dau = v; } }
  return n;
}

/** Thẻ giữ lâu cần 3–6 nhịp hiện; trả cảnh báo dạng chữ nếu lệch. */
export function kiemNhip(mocs, { min = 3, max = 6, gap = KHOANG_NHIP } = {}) {
  const nhip = demNhip(mocs, gap);
  const canhBao = nhip < min ? `chỉ ${nhip} nhịp hiện (cần ≥ ${min})` : nhip > max ? `${nhip} nhịp hiện (nên ≤ ${max})` : null;
  return { nhip, ok: !canhBao, canhBao };
}

const chuan = (w) => String(w).toLowerCase().normalize('NFC').replace(/[^\p{L}\p{N}]+/gu, '');

/**
 * Tìm mốc giây của cụm từ trong danh sách từ có mốc của giọng đọc. (Chưa có thẻ nào gọi; để dành cho P2 dựng `moc` từ moc-cau.json.)
 * @param {{text: string, start: number}[]} tu từ của lời đọc, theo thứ tự (vd từ moc-cau.json / STT)
 * @param {string[]} cum các cụm cần tìm, theo thứ tự xuất hiện trong lời
 * @param {number} [offset] giây cộng thêm (đổi từ giờ tập sang giờ thẻ: truyền -giờBắtĐầuThẻ)
 * @returns {(number|null)[]} mốc từng cụm, null nếu không tìm thấy
 */
export function mocTuLoi(tu, cum, offset = 0) {
  const ws = tu.map((x) => chuan(x.text));
  let cursor = 0;
  return cum.map((c) => {
    const p = String(c).split(/\s+/).map(chuan).filter(Boolean);
    if (!p.length) return null;
    for (let i = cursor; i + p.length <= ws.length; i++) {
      if (p.every((w, j) => ws[i + j] === w)) { cursor = i + p.length; return tu[i].start + offset; }
    }
    return null;
  });
}
