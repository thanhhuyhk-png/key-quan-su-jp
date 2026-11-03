// Trench section (NGUON.tsv: chien-hao; dien-bien-phu.md item 8): every trench 1.7 m deep (over a 1.62 m soldier's
// head), infantry trench 0.5 m wide at the bottom, axial trench 1.2 m; dug at night, camouflaged as the digging went.
// The total length is disputed, so nothing here carries a number on screen.
// The item is an earth block along +X (length DAI) whose top is the ground surface at y = MAT; the trench floor is at
// y = MAT - 1.7. op.loai: 'bo-binh' (0.5 m floor, default) | 'truc' (1.2 m). States: being dug (the head advances
// with t), finished (fire step and parapets), camouflaged (branches laid along the lips).
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const DAI = 8, RONG = 4, MAT = 2.0, SAU = 1.7, TOC = 1.6;   // TOC: metres dug per second of t (time-lapse)

  function mat(day, bacBan) {
    // Cross-section in the YZ plane (as XY of an extruded plate), the trench notch open at the top.
    const d = day / 2, mieng = d + .28, nen = MAT - SAU;
    const p = [[-RONG / 2, 0], [RONG / 2, 0], [RONG / 2, MAT], [mieng, MAT]];
    if (bacBan) p.push([mieng - .04, nen + .55], [d + .1, nen + .55]);
    p.push([d, nen], [-d, nen], [-mieng, MAT], [-RONG / 2, MAT]);
    return p;
  }
  function khoi(diem, vl) {
    // Extrude the section along +X over 1 m (scaled to length by the state).
    const m = H.mesh(H.tam(diem, 1, .0).rotateY(-90 * R).translate(.5, 0, 0), vl);
    return m;
  }

  function tao(K, op) {
    const rnd = K.rng(op.hat || 1), day = op.loai === 'truc' ? 1.2 : .5;
    const goc = H.nhom('chien-hao'), cham = new T.Object3D(); goc.add(cham);
    const vlDat = K.vatLieu('dat');
    const dao = khoi(mat(day, true), vlDat); goc.add(dao);                                     // dug part
    const lien = khoi([[-RONG / 2, 0], [RONG / 2, 0], [RONG / 2, MAT], [-RONG / 2, MAT]], vlDat); goc.add(lien);   // undug ground ahead
    // Grass skin on the ground either side and parapets of thrown-out earth along both lips.
    const co = [], bo = [];
    for (const s of [-1, 1]) {
      const c = H.mesh(H.hop(1, .03, RONG / 2 - day / 2 - .3, .005), 'co'); c.position.set(.5, MAT + .015, s * (RONG / 2 + day / 2 + .3) / 2); goc.add(c); co.push(c);
      // Thrown-out spoil: a low lumpy ridge (vertex noise), not a smooth tube.
      const bg = new T.CylinderGeometry(.5, .5, 1, 14, 24, false, 0, Math.PI).rotateZ(90 * R).scale(1, .42, 1).translate(.5, 0, 0), bp = bg.attributes.position;
      for (let i = 0; i < bp.count; i++) { const x = bp.getX(i), y = bp.getY(i), z = bp.getZ(i); const n = 1 + .28 * Math.sin(x * 37 + z * 9 + s) * Math.sin(x * 13 - y * 7) + .12 * Math.sin(x * 91 + z * 23); bp.setY(i, y * n); bp.setZ(i, z * (1 + .15 * Math.sin(x * 29 + s))); }
      bg.computeVertexNormals();
      const b = H.mesh(bg, 'dat-do'); b.position.set(0, MAT, s * (day / 2 + .75)); goc.add(b); bo.push(b);
    }
    const coLien = H.mesh(H.hop(1, .03, RONG, .005), 'co'); coLien.position.set(.5, MAT + .015, 0); goc.add(coLien);
    // Camouflage branches laid across the lips.
    const la = [];
    for (let i = 0; i < 22; i++) { const c = H.canhLa(rnd, .9 + rnd() * .6, 1.1); c.position.set(.2 + rnd() * (DAI - .4), MAT + .05, (rnd() - .5) * (day + .9)); c.rotation.set((rnd() - .5) * .3, rnd() * 6.28, (rnd() - .5) * .2); goc.add(c); la.push(c); }
    const dauHao = new T.Object3D(); goc.add(dauHao);

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0;
      const dai = s === 'dang-dao' ? Math.min(DAI, Math.max(.3, TOC * t)) : DAI;
      dao.scale.set(dai, 1, 1); lien.position.x = dai; lien.scale.set(DAI - dai + 1e-3, 1, 1); lien.visible = dai < DAI;
      co.forEach(c => { c.scale.set(dai, 1, 1); c.position.x = dai / 2; });
      bo.forEach(b => { b.scale.set(dai, 1, 1); });
      coLien.scale.set(DAI - dai + 1e-3, 1, 1); coLien.position.x = dai + (DAI - dai) / 2; coLien.visible = dai < DAI;
      la.forEach(c => { c.visible = s === 'nguy-trang' && c.position.x < dai; });
      dauHao.position.set(dai, MAT - SAU, 0);
      H.chamThap(goc, cham);
    }
    return { goc, capNhat, diemCham: [cham], neo: { dauHao }, matDat: MAT, nenHao: MAT - SAU, rongDay: day };
  }

  K.dangKy({ ma: 'chien-hao', ten: 'Chiến hào (đoạn mặt cắt)', phe: 'ta', thoiKy: 'dbp-1954', kichThuoc: { dai: DAI, sau: SAU }, trangThai: ['dang-dao', 'xong', 'nguy-trang'], tao });
})(typeof window !== 'undefined' ? window : globalThis);
