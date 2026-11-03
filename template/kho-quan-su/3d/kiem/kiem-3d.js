// Automated checks for the 3D library (run: node kiem/kiem-3d.js). Loads three.js and the engine in a VM
// without WebGL; geometry, poses, contacts, sizes and the review scene are computed without rendering.
// Checks measure the drawn geometry independently of the engine's own contact logic.
'use strict';
const vm = require('node:vm'), fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const ENGINE = ['vendor/three.min.js', 'engine/kho3d.js', 'engine/vat-lieu.js', 'engine/hinh.js', 'engine/san-khau.js', 'engine/nguoi3d.js'];
// Every item file under vat-the/ is picked up automatically (adding an item needs no change here).
const quet = d => fs.readdirSync(path.join(root, d), { withFileTypes: true }).flatMap(e => e.isDirectory() ? quet(path.join(d, e.name)) : e.name.endsWith('.js') ? [path.join(d, e.name)] : []);
const MON = quet('vat-the');

// Minimal canvas stand-in so texture painters really run (any 2D call is accepted and counted).
let lenhVe = 0;
const ctx2d = new Proxy({}, { get: (o, k) => (k in o ? o[k] : () => { lenhVe++; }), set: (o, k, v) => { o[k] = v; return true; } });
const document = { createElement: () => ({ width: 0, height: 0, getContext: () => ctx2d, style: {} }) };
const ctx = vm.createContext({ console, Math, Date, setTimeout, Float32Array, Uint16Array, Uint32Array, Int32Array, Uint8Array, Int8Array, Int16Array, Uint8ClampedArray, Float64Array, ArrayBuffer, DataView, Map, Set, WeakMap, Promise, Symbol, JSON, Object, Array, Number, String, Boolean, Error, TypeError, RangeError, Proxy, document });
ctx.globalThis = ctx; ctx.self = ctx;
const load = f => vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx, { filename: f });
ENGINE.forEach(load); MON.forEach(load);
const K = ctx.Kho3D, T = ctx.THREE, N = K.nguoi;
const rows = []; let fail = 0;
function check(name, fn) {
  try { const d = fn(); rows.push(`ĐẠT | ${name} | ${d || ''}`); }
  catch (e) { fail++; rows.push(`KHÔNG ĐẠT | ${name} | ${e.message}`); }
}
const assert = (c, m) => { if (!c) throw new Error(m); };
const TIMES = [-.4, 0, .13, .37, .8, 1.2, 2.5, 3.3];
const W = o => o.getWorldPosition(new T.Vector3());
const ds = () => K.danhSach().filter(d => d.ma !== 'mon-thu');

check('Đăng ký, số trạng thái, mã không trùng', () => {
  const by = Object.fromEntries(ds().map(d => [d.ma, d.trangThai.length]));
  for (const [ma, n] of Object.entries({ 'bo-doi': 6, 'phao-37': 5, 'xe-dap-tho': 4, 'phao-105': 4, 'dan-cong': 3, c47: 4, 'ham-vom': 3, 'lo-cot': 3, 'thep-gai': 3, du: 3, 'chien-hao': 3, xeng: 3, 'doi-a1': 3, 'vu-no': 3 })) assert(by[ma] >= n, `${ma}: ${by[ma]} trạng thái`);
  let trung = false; try { K.dangKy(K.mon['bo-doi']); } catch (e) { trung = true; }
  assert(trung, 'đăng ký trùng mã không báo lỗi');
  return `${Object.keys(by).length} món: ` + Object.entries(by).map(([k, v]) => `${k} ${v}`).join(', ');
});

check('Vật liệu và vân bề mặt: mọi hàm vẽ chạy được', () => {
  const truoc = lenhVe;
  for (const ten of K.dsVatLieu()) K.vatLieu(ten);
  assert(lenhVe - truoc > 1000, 'hàm vẽ vân gần như không chạy');
  return `${K.dsVatLieu().length} vật liệu, ${lenhVe - truoc} lệnh vẽ`;
});

const BIEN = { 'bo-doi': [{}, { khongMat: true }, { sung: 'k24', ao: 'tran-thu' }, { danSu: true }, { mu: 'boc-vai', laLung: true, saoMu: true }], 'dan-cong': [{}, { nu: true }, { nu: true, nonLa: true, chan: 'dep' }] };
check('Mọi trạng thái × thời điểm (cả t âm) × biến thể: hữu hạn và chạm đất bằng hình thật', () => {
  let n = 0, xau = 0;
  for (const d of ds()) for (const b of (BIEN[d.ma] || [{}])) {
    const inst = K.tao(d.ma, b);
    const cacTuThe = d.ma === 'bo-doi' ? d.trangThai.map(s => [s]).concat([['dung', 'cui']]) : d.trangThai.map(s => [s]);
    for (const [s, tu] of cacTuThe) for (const t of TIMES) {
      inst.dat({ trangThai: s, tuThe: tu, t });
      const box = K.doKhung(inst.khung);
      assert([box.min.x, box.min.y, box.min.z, box.max.x, box.max.y, box.max.z].every(Number.isFinite), `${d.ma}/${tu || s}/${t} không hữu hạn`);
      // Lowest drawn point must sit on the ground: neither floating nor sunk (tread blocks may dip 2 cm).
      assert(box.min.y > -.025 && box.min.y < .012, `${d.ma}/${tu || s}/${t}: hình thấp nhất ở ${box.min.y.toFixed(3)} m`);
      xau = Math.max(xau, Math.abs(box.min.y)); n++;
    }
  }
  return `${n} lượt; lệch đất lớn nhất ${(xau * 100).toFixed(1)} cm`;
});

check('Kích thước mét thật', () => {
  const size = (ma, s, b) => K.doKhung(K.tao(ma, b).dat({ trangThai: s }).khung).getSize(new T.Vector3());
  const nguoi = size('bo-doi', 'dung'), p37 = size('phao-37', 'keo'), p105 = size('phao-105', 'keo'), xe = size('xe-dap-tho', 'dat');
  assert(nguoi.y >= 1.62 && nguoi.y <= 1.8, 'người cao ' + nguoi.y.toFixed(2));
  assert(Math.abs(p37.x - 6.2) <= .3 && Math.abs(p37.z - 1.78) <= .1 && p37.y >= 2.0 && p37.y <= 2.6, `37 mm ${p37.x.toFixed(2)} × ${p37.z.toFixed(2)} × ${p37.y.toFixed(2)}`);
  assert(Math.abs(p105.x - 5.94) <= .3 && Math.abs(p105.z - 2.21) <= .12 && Math.abs(p105.y - 1.73) <= .15, `105 mm ${p105.x.toFixed(2)} × ${p105.z.toFixed(2)} × ${p105.y.toFixed(2)}`);
  assert(xe.x >= 1.6 && xe.x <= 2.2, 'xe dài ' + xe.x.toFixed(2));
  return `người ${nguoi.y.toFixed(2)}; 37 mm ${p37.x.toFixed(2)}×${p37.z.toFixed(2)}×${p37.y.toFixed(2)}; 105 mm ${p105.x.toFixed(2)}×${p105.z.toFixed(2)}×${p105.y.toFixed(2)}; xe ${xe.x.toFixed(2)} m`;
});

check('Không chữ trên món', () => {
  for (const d of ds()) K.tao(d.ma).khung.traverse(o => assert(!o.isSprite && !(o.geometry && o.geometry.type === 'TextGeometry'), d.ma + ' có chữ'));
  const src = MON.map(f => fs.readFileSync(path.join(root, f), 'utf8')).join();
  assert(!/fillText|strokeText|TextGeometry/.test(src), 'mã món có lệnh vẽ chữ');
  return 'quét cây cảnh và mã nguồn';
});

check('Thuần theo t: một instance qua trạng thái xáo trộn, khung bị dời/xoay, vẫn khớp instance mới', () => {
  let n = 0;
  const sig = i => { const inv = new T.Matrix4().copy(i.khung.matrixWorld).invert(), a = []; i.khung.traverse(o => a.push(new T.Matrix4().multiplyMatrices(inv, o.matrixWorld).elements.map(v => (Math.abs(v) < 5e-5 ? 0 : v).toFixed(4)).join())); return a.join('|'); };
  for (const d of ds()) {
    const cu = K.tao(d.ma, { hat: 3 }), thu = d.trangThai.slice().reverse().concat(d.trangThai);
    cu.khung.position.set(5, 1, -2); cu.khung.rotation.set(0, .7, .2);
    for (const s of thu) cu.dat({ trangThai: s, t: 1.9 });
    for (const s of d.trangThai) {
      cu.dat({ trangThai: s, t: .77 });
      const moi = K.tao(d.ma, { hat: 3 }); moi.khung.position.copy(cu.khung.position); moi.khung.rotation.copy(cu.khung.rotation);
      moi.dat({ trangThai: s, t: .77 });
      assert(sig(cu) === sig(moi), `${d.ma}/${s} phụ thuộc lịch sử gọi`); n++;
    }
  }
  const src = ENGINE.slice(1).concat(MON).map(f => fs.readFileSync(path.join(root, f), 'utf8')).join();
  assert(!/Math\.random|Date\.now|new Date|requestAnimationFrame/.test(src), 'có random / Date / RAF');
  return n + ' trạng thái';
});

check('Bánh lăn đúng quãng đường', () => {
  const i = K.tao('phao-37'); i.dat({ trangThai: 'keo', t: 2 });
  const goc = -i.neo.banhSau.rotation.z, mong = .6 * 2 / .45;
  assert(Math.abs(goc - mong) / mong < .01, `37 mm: ${goc} ≠ ${mong}`);
  return 'sai số < 1%';
});

check('Người: IK chân tới đích ±5 mm; đứng thẳng; quỳ đúng; luôn có chân đỡ', () => {
  let saiMax = 0;
  for (const ma of ['bo-doi', 'dan-cong']) {
    const i = K.tao(ma), p = i.nguoi;
    const cac = ma === 'bo-doi' ? [['dung'], ['di'], ['quy-ngam'], ['keo-day'], ['day'], ['xung-phong'], ['dung', 'cui']] : [['ganh'], ['leo-doc'], ['nghi']];
    for (const [s, tu] of cac) for (let k = 0; k < 16; k++) {
      const t = k * .11;
      i.dat({ trangThai: s, tuThe: tu, t });
      if (ma === 'bo-doi') {
        const dich = N.TU_THE[tu || s](t).chan;
        for (const ten of ['T', 'P']) {
          const muc = i.goc.localToWorld(new T.Vector3(dich[ten][0], dich[ten][1] + N.L.coChan, dich[ten][2]));
          const sai = W(p.chan[ten].ban).distanceTo(muc); saiMax = Math.max(saiMax, sai);
          assert(sai < .005, `${tu || s} t=${t.toFixed(2)}: mắt cá ${ten} lệch đích ${(sai * 100).toFixed(1)} cm`);
        }
      }
      const de = Math.min(...['T', 'P'].flatMap(ten => [W(p.chan[ten].gotM).y, W(p.chan[ten].muiM).y]));
      if ((tu || s) !== 'quy-ngam') assert(de < .012, `${ma}/${tu || s} t=${t.toFixed(2)}: không chân nào chạm đất (${de.toFixed(3)})`);
    }
  }
  const i = K.tao('bo-doi'), p = i.nguoi;
  i.dat({ trangThai: 'dung' });
  const g = W(p.chan.T.goi), h = W(p.chan.T.khop), c = W(p.chan.T.ban);
  assert(g.distanceTo(h) + g.distanceTo(c) - h.distanceTo(c) < .01, 'đứng còn khuỵu gối');
  i.dat({ trangThai: 'quy-ngam' });
  const goiSau = W(p.chan.P.goi).y, deTruoc = Math.min(W(p.chan.T.gotM).y, W(p.chan.T.muiM).y), dinh = W(p.dinhDau).y;
  assert(goiSau < .09, 'gối sau cao ' + goiSau.toFixed(3));
  assert(deTruoc < .012, 'chân trước lơ lửng ' + deTruoc.toFixed(3));
  assert(dinh > 1.0 && dinh < 1.3, 'đỉnh đầu khi quỳ ' + dinh.toFixed(2));
  for (const s of ['keo-day', 'day']) for (let k = 0; k < 16; k++) {
    i.dat({ trangThai: s, t: k * .1 });
    assert(Math.max(W(p.chan.T.ban).x, W(p.chan.P.ban).x) - W(p.hong).x > -.16, `${s}: hông vượt chân trước quá 0,16 m`);
  }
  return `mắt cá lệch tối đa ${(saiMax * 1000).toFixed(1)} mm; quỳ: gối sau ${goiSau.toFixed(3)} m, chân trước ${deTruoc.toFixed(3)} m, đỉnh đầu ${dinh.toFixed(2)} m`;
});

check('Cảnh Dốc Chuối: dựng được, thuần theo t, tay người kéo nằm trên dây', () => {
  load('the/canh-doc-chuoi.js');
  const c = K.canhDocChuoi(null);
  let tot = 0, nguoi = 0;
  for (const t of [3, .5, 2.2, 0, 5.8]) {
    c.ve(t, 16 / 9);
    const day = [], keo = [];
    c.scene.traverse(o => { if (o.isMesh && o.geometry.type === 'TubeGeometry' && o.geometry.parameters.path.curves) day.push(o.geometry.parameters.path.curves); if (o.name === 'bo-doi') keo.push(o); });
    assert(day.length === 2, 'phải có 2 dây, thấy ' + day.length);
    const kc = q => Math.min(...day.flat().map(s => new T.Line3(s.v1, s.v2).closestPointToPoint(q, true, new T.Vector3()).distanceTo(q)));
    nguoi = keo.length; tot = 0;
    for (const k of keo) { const tay = []; k.traverse(o => { if (o.name === 'banTayT' || o.name === 'banTayP') tay.push(o.localToWorld(new T.Vector3(0, -.05, 0))); }); if (tay.every(q => kc(q) < .04)) tot++; }
    assert(tot >= 12, `t=${t}: chỉ ${tot}/${nguoi} người có cả hai tay trên dây`);
  }
  return `${tot}/${nguoi} người bám dây (người chèn gỗ cầm khúc gỗ)`;
});

check('Lô 2: số đo, phù hiệu, hào, đường hầm A1, vụ nổ', () => {
  const size = (ma, st, b) => K.doKhung(K.tao(ma, b).dat({ trangThai: st, t: .5 }).khung).getSize(new T.Vector3());
  // C-47 type data: 19.43 m long, 28.96 m span, 5.16 m high at rest on its tail wheel.
  const c = size('c47', 'ha-canh');
  assert(Math.abs(c.x - 19.43) <= .5 && Math.abs(c.z - 28.96) <= .3 && Math.abs(c.y - 5.16) <= .25, `C-47 ${c.x.toFixed(2)} × ${c.z.toFixed(2)} × ${c.y.toFixed(2)}`);
  // French cocarde: blue centre, white, red outer (reversed is the British roundel).
  const vong = []; K.tao('c47').khung.traverse(o => { if (o.name === 'cocarde') vong.push(o.children.map(m => [m.geometry.parameters.radius, m.material.name]).sort((a, b) => a[0] - b[0]).map(x => x[1]).join(',')); });
  assert(vong.length >= 4 && vong.every(v => v === 'co-xanh,co-trang,co-do'), 'thứ tự màu cocarde: ' + vong[0]);
  // Trench: 1.7 m deep, infantry floor 0.5 m, axial 1.2 m.
  for (const [loai, rong] of [['bo-binh', .5], ['truc', 1.2]]) { const h = K.tao('chien-hao', { loai }); assert(Math.abs(h.matDat - h.nenHao - 1.7) < .001 && h.rongDay === rong, `hào ${loai}: sâu ${(h.matDat - h.nenHao).toFixed(2)}, đáy ${h.rongDay}`); }
  // Hill A1: the tunnel climbs into the hill and ends under the crown bunker, inside the hill.
  const a1 = K.tao('doi-a1').dat({ trangThai: 'boc-pha' }), cuoi = a1.neo.cuoiHam.position, cua = a1.neo.cuaHam.position, dinh = a1.neo.dinh.position;
  assert(cuoi.y > cua.y && Math.abs(cuoi.x - dinh.x) < .01 && dinh.y - cuoi.y > 3 && dinh.y - cuoi.y < 10, `hầm: cửa ${cua.y.toFixed(1)} m, cuối ${cuoi.y.toFixed(1)} m, đỉnh ${dinh.y.toFixed(1)} m`);
  // Explosions show nothing before detonation, then light up.
  for (const st of ['dat', 'cao-xa', 'boc-pha']) {
    const i = K.tao('vu-no'); let thay = 0;
    i.dat({ trangThai: st, t: -.1 }); i.khung.traverse(o => { if (o.userData.boQuaKhung && K.hien(o, i.khung) && o.isMesh && (!o.material.opacity || o.material.opacity > .01)) thay++; });
    assert(thay === 0, `${st}: ${thay} hạt hiện trước t = 0`);
    i.dat({ trangThai: st, t: .2 }); let sang = 0; i.khung.traverse(o => { if (o.isMesh && K.hien(o, i.khung) && o.material.opacity > .1 && o.userData.boQuaKhung) sang++; });
    assert(sang > 5, `${st}: chỉ ${sang} hạt hiện lúc 0,2 s`);
  }
  return `C-47 ${c.x.toFixed(2)}×${c.z.toFixed(2)}×${c.y.toFixed(2)} m; cocarde xanh-trắng-đỏ (${vong.length}); hào sâu 1,7 m; hầm A1 dưới đỉnh ${(dinh.y - cuoi.y).toFixed(1)} m; nổ tắt trước 0`;
});

check('Thêm món bằng một file qua API công khai (cả vật liệu riêng)', () => {
  load('kiem/mon-thu.js');
  const i = K.tao('mon-thu');
  for (const s of K.mon['mon-thu'].trangThai) { i.dat({ trangThai: s, t: .5 }); assert(Math.abs(K.doKhung(i.khung).min.y) < .002, 'món thử không chạm đất ở ' + s); }
  return 'món thử 3 trạng thái, vật liệu riêng đăng ký từ file món';
});

console.log('KIỂM KHO 3D');
rows.forEach((r, i) => console.log(`${i + 1}. ${r}`));
console.log(`KẾT QUẢ: ${rows.length - fail}/${rows.length} ĐẠT`);
process.exitCode = fail ? 1 : 0;
