// Internal review board: each cell is its own lit scene on a display plinth; the camera frames the item from its
// measured size and orbits slowly with t so the video shows every side. ?nhom= picks a subset while iterating.
const K = Kho3D, T = THREE;
const NHOM = window.NHOM_3D || 'tat-ca';
const BO = {
  phao: { size: [2400, 1600], cot: 3, o: [
    ['phao-37', 'keo', 'ngay', 35], ['phao-37', 'chen-banh', 'ngay', 150], ['phao-37', 'ban', 'ngay', 40],
    ['phao-37', 'u-dat', 'ngay', 210], ['phao-37', 'nguy-trang', 'ngay', 30], ['phao-37', 'keo', 'dem', 60]] },
  nguoi: { size: [2400, 1600], cot: 4, o: [
    ['bo-doi', 'dung', 'ngay', 30], ['bo-doi', 'di', 'ngay', 80], ['bo-doi', 'quy-ngam', 'ngay', 60], ['bo-doi', 'keo-day', 'ngay', 80],
    ['bo-doi', 'day', 'ngay', 70], ['bo-doi', 'dung', 'ngay', 200, { ao: 'tran-thu', sung: 'k24' }], ['bo-doi', 'di', 'dem', 70], ['bo-doi', 'keo-day', 'dem', 75, { khongMat: true }]] },
  p105: { size: [2400, 1600], cot: 2, o: [
    ['phao-105', 'keo', 'ngay', 35], ['phao-105', 'ban', 'ngay', 210], ['phao-105', 'trong-ham', 'ngay', 200], ['phao-105', 'nguy-trang', 'ngay', 40]] },
  dc: { size: [2400, 1600], cot: 3, o: [
    ['dan-cong', 'ganh', 'ngay', 60], ['dan-cong', 'leo-doc', 'ngay', 80], ['dan-cong', 'nghi', 'ngay', 40],
    ['dan-cong', 'ganh', 'ngay', 70, { nu: true }], ['dan-cong', 'ganh', 'ngay', 120, { nu: true, nonLa: true }], ['dan-cong', 'ganh', 'dem', 70, { nu: true }]] },
  // Batch 2 (Dien Bien Phu full episode). 6th field: fixed camera radius for items whose particles skip the size box.
  lo2: { size: [3200, 2400], cot: 4, o: [
    ['c47', 'bay', 'ngay', 30], ['c47', 'ha-canh', 'ngay', 210], ['c47', 'trung-dan', 'chieu', 140], ['c47', 'xac', 'chieu', 60],
    ['ham-vom', 'nguyen', 'ngay', 30], ['ham-vom', 'gia-co', 'ngay', 50], ['ham-vom', 'sap', 'chieu', 40], ['lo-cot', 'nguyen', 'ngay', 30],
    ['lo-cot', 'chay', 'dem', 30], ['lo-cot', 'sap', 'ngay', 210], ['thep-gai', 'bung', 'ngay', 70], ['thep-gai', 'dut', 'ngay', 80],
    ['du', 'mo', 'ngay', 30], ['du', 'roi', 'ngay', 60], ['du', 'nam-dat', 'ngay', 40], ['du', 'roi', 'chieu', 60, { mau: '#b8352f' }]] },
  lo2ta: { size: [3200, 2400], cot: 4, o: [
    ['chien-hao', 'dang-dao', 'ngay', 50], ['chien-hao', 'xong', 'ngay', 20], ['chien-hao', 'nguy-trang', 'dem', 30], ['chien-hao', 'xong', 'ngay', 0, { loai: 'truc' }],
    ['xeng', 'cam-dat', 'ngay', 70], ['xeng', 'hat-dat', 'ngay', 80], ['bo-doi', 'xung-phong', 'ngay', 80, { sung: 'k24' }], ['bo-doi', 'xung-phong', 'dem', 100, { khongMat: true }],
    ['doi-a1', 'ham', 'ngay', 90], ['doi-a1', 'boc-pha', 'chieu', 70], ['doi-a1', 'no', 'chieu', 90], ['doi-a1', 'ham', 'chieu', 30, { catLop: false }],
    ['vu-no', 'dat', 'chieu', 30, null, 14], ['vu-no', 'cao-xa', 'ngay', 30, null, 9], ['vu-no', 'boc-pha', 'chieu', 30, null, 55]] },
  // Bản Full V3, bước 4: the items on screen in the Dien Bien Phu episode, raised from diorama to near-real.
  v3: { size: [3200, 1600], cot: 4, dai: 40, o: [
    ['c47', 'bay', 'ngay', 30], ['c47', 'bay', 'ngay', 200], ['c47', 'trung-dan', 'ngay', 140], ['phao-105', 'keo', 'ngay', 35],
    ['phao-105', 'ban', 'ngay', 210], ['bo-doi', 'keo-day', 'ngay', 80], ['bo-doi', 'xung-phong', 'ngay', 80, { sung: 'k24' }], ['dan-cong', 'ganh', 'ngay', 60]] },
  xe: { size: [2400, 1600], cot: 2, o: [
    ['xe-dap-tho', 'dat', 'ngay', 70], ['xe-dap-tho', 'len-doc', 'ngay', 120], ['xe-dap-tho', 'xuong-doc', 'ngay', 250], ['xe-dap-tho', 'nghi', 'ngay', 300]] },
};
const tatCa = { size: [3200, 3200], cot: 6, o: [].concat(BO.nguoi.o.slice(0, 6), [['bo-doi', 'keo-day', 'dem', 75, { khongMat: true }], ['bo-doi', 'di', 'ngay', 60, { mu: 'boc-vai', laLung: true }]], BO.phao.o, BO.p105.o, BO.xe.o, BO.dc.o.slice(0, 3)), canh: true };
const B = NHOM === 'tat-ca' ? tatCa : NHOM === 'canh' ? { size: [1920, 1080], cot: 1, o: [], canh: true, chiCanh: true } : BO[NHOM];
const [W, Hh] = B.size;
const gl = document.getElementById('gl'), chu = document.getElementById('chu');
chu.width = W; chu.height = Hh; const cx = chu.getContext('2d');
const renderer = K.mayVe(gl, W, Hh);
renderer.setScissorTest(true);
const lop = B.chiCanh ? 0 : Math.ceil(B.o.length / B.cot);
const canhH = B.chiCanh ? Hh : B.canh ? Math.round(Hh * .36) : 0;
const oW = Math.floor(W / B.cot), oH = lop ? Math.floor((Hh - canhH) / lop) : 0;
const o = B.o.map(([ma, tt, kieu, goc, bienThe, banKinh], i) => {
  const kt = K.mon[ma].kichThuoc || {}, scene = K.canh(renderer, kieu, ma.startsWith('phao') ? 6 : Math.max(2.5, (Math.max(kt.dai || 0, kt.rong || 0)) * .6));
  const inst = K.tao(ma, Object.assign({ hat: 7 + i }, bienThe || {}));
  scene.add(inst.khung);
  inst.dat({ trangThai: tt, t: 0 });
  const box = K.doKhung(inst.khung), size = box.getSize(new T.Vector3()), r = ma === 'phao-37' ? 3.6 : Math.max(size.x, size.z) * .62 + .3;
  const de = K.deTron(r, kieu); scene.add(de);
  const cam = new T.PerspectiveCamera(30, oW / oH, .05, 3000);
  return { ma, tt, kieu, goc, scene, inst, cam, box, bienThe, banKinh, x: (i % B.cot) * oW, y: Math.floor(i / B.cot) * oH };
});
const canh = B.canh ? K.canhDocChuoi(renderer) : null;
function nhan(text, x, y, s, mau, w) { cx.font = (w || 300) + ' ' + s + 'px BeVN'; cx.fillStyle = mau; cx.fillText(text, x, y); }
function renderFrame(t) {
  cx.clearRect(0, 0, W, Hh);
  for (const c of o) {
    c.inst.dat({ trangThai: c.tt, t, khongMat: c.bienThe && c.bienThe.khongMat });
    const box = K.doKhung(c.inst.khung), size = box.getSize(new T.Vector3()), tam = box.getCenter(new T.Vector3());
    if (c.banKinh) tam.y += c.banKinh * .45;
    const r = c.banKinh || Math.max(size.x, size.y, size.z) * .62;
    const xa = r / Math.sin(15 * Math.PI / 180) * .95;
    K.quayQuanh(c.cam, tam, xa * .92, xa * .32, c.goc + t * 9);
    c.cam.aspect = oW / oH; c.cam.updateProjectionMatrix();
    const y = Hh - c.y - oH;
    renderer.setViewport(c.x, y, oW, oH); renderer.setScissor(c.x + 2, y + 2, oW - 4, oH - 4);
    renderer.render(c.scene, c.cam);
    nhan(({ 'bo-doi': 'BỘ ĐỘI', 'phao-37': 'PHÁO 37 MM', 'phao-105': 'LỰU PHÁO 105 MM', 'xe-dap-tho': 'XE THỒ', 'dan-cong': 'DÂN CÔNG' }[c.ma] || K.mon[c.ma].ten.toUpperCase()) + ' · ' + c.tt + (c.kieu === 'dem' ? ' · đêm' : '') + (c.bienThe ? ' · ' + Object.entries(c.bienThe).map(([k, v]) => v === true ? ({ khongMat: 'không mặt', danSu: 'dân sự' }[k] || k) : v).join(' ') : ''), c.x + 22, c.y + 38, 22, c.kieu === 'dem' ? '#c9d6e4' : '#2a2f33', 700);
  }
  if (canh) {
    const y0 = Hh - canhH;
    renderer.setViewport(0, 0, W, canhH); renderer.setScissor(0, 0, W, canhH);
    canh.ve(t, W / canhH);
    renderer.render(canh.scene, canh.cam);
    nhan('DỐC CHUỐI · ĐÊM · KÉO PHÁO 37 MM LÊN DỐC (sa bàn)', 28, y0 + 44, 26, '#d7e2ee', 700);
  }
}
window.SIZE = W + 'x' + Hh; window.DURATION = B.dai || 6; window.renderFrame = renderFrame; window.READY = false;
Promise.all([document.fonts.load('700 22px BeVN'), document.fonts.load('300 22px BeVN')]).then(() => {
  renderFrame(0); window.READY = true;
});
