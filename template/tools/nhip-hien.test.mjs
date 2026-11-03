// Test logic nhịp hiện: node --test tools/nhip-hien.test.mjs
// lib/nhip-hien.js là ES module không import gì, nạp bằng data URL để không phụ thuộc "type" của package.json.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const src = readFileSync(join(dirname(fileURLToPath(import.meta.url)), '..', 'lib', 'nhip-hien.js'), 'utf8');
const { chiaMoc, mocPhanTu, demNhip, kiemNhip, mocTuLoi, KHOANG_NHIP } = await import('data:text/javascript;base64,' + Buffer.from(src).toString('base64'));

test('chiaMoc: n <= 0 trả mảng rỗng', () => {
  assert.deepEqual(chiaMoc(0), []);
  assert.deepEqual(chiaMoc(-2), []);
});

test('chiaMoc: chia đều trong [from, to]', () => {
  assert.deepEqual(chiaMoc(3, { from: 1, to: 5 }), [1, 3, 5]);
  assert.deepEqual(chiaMoc(1, { from: 2, to: 9 }), [2]);
});

test('chiaMoc: bước cố định khi không có to', () => {
  assert.deepEqual(chiaMoc(3, { from: 1, buoc: 2 }), [1, 3, 5]);
});

test('chiaMoc: moc cho sẵn được giữ, thiếu thì kéo dài, giảm dần thì nâng lên', () => {
  assert.deepEqual(chiaMoc(4, { moc: [1, 2], buoc: 0.5 }), [1, 2, 2.5, 3]);
  assert.deepEqual(chiaMoc(3, { moc: [2, 1, 4] }), [2, 2, 4]);
  assert.deepEqual(chiaMoc(2, { moc: [1, 2, 3] }), [1, 2]);
  assert.deepEqual(chiaMoc(3, { moc: [1, NaN, 3] }), [1, 1, 3]);
});

test('mocPhanTu: ưu tiên moc > nhip > mốc riêng', () => {
  assert.deepEqual(mocPhanTu({ moc: [1, 2, 3], nhip: { from: 9 } }, 3, [7, 8, 9]), [1, 2, 3]);
  assert.deepEqual(mocPhanTu({ nhip: { from: 1, to: 3 } }, 3, [7, 8, 9]), [1, 2, 3]);
  assert.deepEqual(mocPhanTu({}, 3, [7, 8, 9]), [7, 8, 9]);
});

test('mocPhanTu: mốc riêng thiếu phần tử thì bù thêm', () => {
  const m = mocPhanTu({}, 3, [1, 2]);
  assert.equal(m.length, 3);
  assert.ok(m[2] > m[1]);
});

test('demNhip: gộp các mốc sát nhau thành một nhịp', () => {
  assert.equal(demNhip([1, 1.1, 1.2, 3, 5]), 3);
  assert.equal(demNhip([]), 0);
});

test('kiemNhip: cảnh báo khi dưới 3 hoặc trên 6 nhịp', () => {
  assert.equal(kiemNhip([1, 2]).ok, false);
  assert.match(kiemNhip([1, 2]).canhBao, /chỉ 2 nhịp/);
  assert.equal(kiemNhip([1, 2, 3, 4]).ok, true);
  assert.equal(kiemNhip([1, 2, 3, 4, 5, 6, 7]).ok, false);
});

test('mocTuLoi: tìm mốc cụm trong lời, bỏ dấu câu, theo thứ tự, có offset', () => {
  const tu = [
    { text: 'Lính', start: 10 }, { text: 'Pháp,', start: 10.4 }, { text: 'rồi', start: 11 },
    { text: 'Lê', start: 11.5 }, { text: 'dương.', start: 11.8 }, { text: 'Lính', start: 14 },
  ];
  assert.deepEqual(mocTuLoi(tu, ['lính pháp', 'lê dương', 'lính']), [10, 11.5, 14]);
  assert.deepEqual(mocTuLoi(tu, ['lê dương'], -10), [1.5]);
  assert.deepEqual(mocTuLoi(tu, ['không có']), [null]);
});

test('demNhip: chuỗi mốc dày kéo dài tách theo mốc đầu nhóm, không gộp thành một', () => {
  assert.equal(KHOANG_NHIP, 0.5);
  assert.equal(demNhip([0, 0.2, 0.4, 0.6, 0.8, 1.0]), 2);
  assert.equal(demNhip([0, 0.2, 0.4, 0.6, 0.8, 1.0], 0.25), 3);
  assert.equal(demNhip([0, 0.49, 0.5]), 2);
});

test('chiaMoc: mốc không phải số hoặc âm không sinh Infinity', () => {
  assert.deepEqual(chiaMoc(2, { moc: [NaN] }), [0, 0.9]);
  assert.deepEqual(chiaMoc(3, { moc: [-2, 1, NaN] }), [0, 1, 1]);
  assert.ok(chiaMoc(2, { moc: [NaN, NaN] }).every(Number.isFinite));
});
