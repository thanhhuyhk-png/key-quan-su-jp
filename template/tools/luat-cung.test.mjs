// Test lớp JS của máy chặn luật cứng (cards/luat-cung.js): chặn cả trang HTML viết tay khi mở. Chạy: node --test tools/luat-cung.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
// cards/luat-cung.js là ES module không import gì: nạp bằng data URL để không phụ thuộc "type" của package.json.
const src = readFileSync(new URL('../cards/luat-cung.js', import.meta.url), 'utf8');
const { chuanChu, timTenLanhTu, kiemDuLieu, kiemThoiLuongGiong, kiemCatLanhTu, uocRam, TRAN_RAM_BYTE } = await import('data:text/javascript;base64,' + Buffer.from(src).toString('base64'));

const names = JSON.parse(readFileSync(new URL('../data/lanh-tu.json', import.meta.url), 'utf8')).ten;
const nv = (o = {}) => ({ type: 'nhan-vat', source: 'x', ten: 'TRẦN VĂN MẪU', chucVu: 'x', bienThe: 'tach-nen', ...o });
const am = (o = {}) => ({ type: 'the-am-thanh', source: 'x', duration: 7, nhan: 'MÔ PHỎNG LẠI', nguoi: { ten: 'A', chucVu: 'B' }, giong: { tep: 'g.mp3', peaks: 'p.json', batDau: 0.5 }, ...o });
const co = (loi, ...chu) => loi.some((l) => chu.every((c) => l.includes(c)));

test('ba luật cứng và ca hợp lệ', () => {
  assert.ok(co(kiemDuLieu(nv({ lanhTu: true }), names), 'chỉ được «khung»'));
  assert.ok(co(kiemDuLieu(am({ nhan: undefined }), names), 'thiếu «nhan»'));
  assert.ok(co(kiemDuLieu(am({ lanhTu: true }), names), 'chỉ được «GHI ÂM GỐC»'));
  assert.deepEqual(kiemDuLieu(am(), names), []);
  assert.deepEqual(kiemDuLieu(am({ lanhTu: true, nhan: 'ghi âm gốc' }), names), []);
  assert.deepEqual(kiemDuLieu(nv({ bienThe: 'khung', lanhTu: true }), names), []);
});

test('lanhTu sai kiểu bị chặn', () => {
  for (const v of ['true', 1, null, 'yes', 0]) assert.ok(co(kiemDuLieu(nv({ lanhTu: v }), names), '«lanhTu» phải là true hoặc false'), String(v));
});

test('tên lãnh tụ ở mọi trường chữ, bí danh, Tố Hữu không bị chặn', () => {
  assert.ok(co(kiemDuLieu(nv({ ten: 'Nguyễn Ái Quốc' }), names), 'Nguyễn Ái Quốc'));
  assert.ok(co(kiemDuLieu(nv({ chiTiet: 'ảnh chụp Bác Hồ' }), names), 'chiTiet'));
  assert.ok(co(kiemDuLieu(am({ phuDe: [{ text: 'Võ Nguyên Giáp nói' }] }), names), 'phuDe[0].text'));
  assert.deepEqual(kiemDuLieu(nv({ ten: 'Tố Hữu' }), names), []);
  assert.deepEqual(kiemDuLieu(nv({ source: 'Hồ Chí Minh Toàn tập' }), names), []);
  assert.deepEqual(kiemDuLieu(nv({ ten: 'Nguyễn Văn Giáo' }), names), []);
  assert.equal(chuanChu('Nguyễn Đức'), ' nguyen duc ');
  assert.equal(timTenLanhTu({ a: { b: ['Hồ Chí Minh'] } }, names)[0].path, 'a.b[0]');
});

test('giong.tep, thời lượng giọng so với thẻ', () => {
  const s = am(); delete s.giong.tep;
  assert.ok(co(kiemDuLieu(s, names), 'giong.tep'));
  assert.deepEqual(kiemThoiLuongGiong(am(), 6.0), []);
  assert.ok(kiemThoiLuongGiong(am(), 20).length);
  assert.ok(kiemThoiLuongGiong(am(), 3).length);
});

test('zoomDen, phim.n, trần phóng cat, trần RAM', () => {
  for (const z of ['abc', null, 1.2, 0.9]) assert.ok(co(kiemDuLieu(nv({ bienThe: 'khung', zoomDen: z }), names), 'zoomDen'), String(z));
  const p = (n) => ({ type: 'phim-panel', source: 'x', phim: { mau: 'f%03d.jpg', n } });
  for (const n of [2.5, 0, '3', undefined]) assert.ok(co(kiemDuLieu(p(n), names), 'phim.n'), String(n));
  assert.deepEqual(kiemDuLieu(p(3), names), []);
  const lt = (cat) => nv({ bienThe: 'khung', lanhTu: true, cat });
  assert.ok(kiemCatLanhTu(lt([0.5, 0.5, 0.4]), 800, 1000).length);
  assert.deepEqual(kiemCatLanhTu(lt([0.5, 0.45, 0.9]), 800, 1000), []);
  assert.deepEqual(kiemCatLanhTu(nv({ bienThe: 'khung', lanhTu: false, cat: [0.5, 0.5, 0.2] }), 800, 1000), []);
  assert.ok(uocRam(150, 1104, 621) < TRAN_RAM_BYTE && TRAN_RAM_BYTE < uocRam(150, 1920, 1080));
});

test('loại không thuộc P2 không bị ảnh hưởng', () => {
  assert.deepEqual(kiemDuLieu({ type: 'so-lieu', lanhTu: 'true' }, names), []);
});
