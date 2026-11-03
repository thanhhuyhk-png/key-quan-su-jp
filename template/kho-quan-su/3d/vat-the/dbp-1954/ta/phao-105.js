// 105 mm howitzer M2A1 (M101), US-made; 24 guns of Regiment 45 (NGUON.tsv: phao-105). 5.94 x 2.21 x 1.73 m,
// barrel 2.31 m with a plain muzzle; double shield (gun 14683's record); split trail on two wheels.
// Placed in caves dug into hillsides with only the muzzle showing (dien-bien-phu.md item 5).
// Paint is not sourced: muted olive, black tyres; no flag, emblem or numbers (those are museum paint).
// Item frame: +X is the towing direction (trail end, lunette); the muzzle points to -X in every state.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const RK = .52, TOC_KEO = .5, CHU_KY_BAN = 3.2;

  function tao(K, op) {
    const goc = H.nhom('phao-105'), diemCham = [], neo = {}, rnd = K.rng(op.hat || 1);
    const VL = 'son-ol', VLT = 'son-ol-toi';

    // ---- axle, bottom carriage, wheels -----------------------------------
    const be = H.nhom('be'); goc.add(be);
    const truc = H.mesh(H.truZ(.07, .07, 1.72, 16), VLT); truc.position.set(0, RK, 0); be.add(truc);
    const hopTruc = H.mesh(H.hop(.5, .3, .9, .04), VL); hopTruc.position.set(.12, RK + .12, 0); be.add(hopTruc);
    const banh = [];
    for (const z of [-1, 1]) {
      const w = H.banhPhao(RK, .25); w.position.set(0, RK, z * .98); be.add(w); banh.push(w);
      const cham = new T.Object3D(); cham.position.set(0, 0, z * .98); be.add(cham); cham.userData.laBanh = true; w.userData.cham = cham; diemCham.push(cham);
      const che = H.mesh(new T.TorusGeometry(RK + .05, .035, 4, 24, 150 * R).scale(1, 1, 2.6), VL); che.position.set(0, RK, z * .98); che.rotation.z = 15 * R; be.add(che);
    }
    neo.banhTrai = banh[1]; neo.banhPhai = banh[0];

    // ---- split trail: two box legs hinged at the carriage, joined at the lunette for travel ----
    const cang = [];
    for (const z of [-1, 1]) {
      const c = H.nhom('cang'); c.position.set(.3, RK + .02, z * .26); be.add(c);
      const dam = H.mesh(H.hop(3.5, .2, .16, .025), VL); dam.position.set(1.77, -.06, 0); dam.rotation.z = -4 * R; c.add(dam);
      const lop = []; for (let i = 0; i < 11; i++) lop.push([.4 + i * .3, .05 - i * .021, z * .085]);
      c.add(H.dinhTan(lop, .008, VLT, [0, 0, z]));
      // Spade at the trail end (folded up for travel, down into the ground for firing).
      const thuong = H.nhom('thuong'); thuong.position.set(3.47, -.18, 0); c.add(thuong);
      thuong.add(H.mesh(H.tam([[0, 0], [.08, 0], [.12, -.38], [-.06, -.38]], .32, .01), VLT));
      // The spade digs into the ground when firing, so it is neither a contact point nor counted in size checks.
      const ch = new T.Object3D(); ch.position.set(.03, -.4, 0); thuong.add(ch);
      thuong.children[0].userData.boQuaKhung = true;
      const tay = H.thanh([3.2, .1, 0], [3.2, .24, 0], .015, VLT); c.add(tay);
      cang.push({ c, z, thuong });
    }
    const vongMoc = H.mesh(new T.TorusGeometry(.07, .022, 8, 20), 'thep'); vongMoc.position.set(3.77, RK - .24, 0); vongMoc.rotation.x = 90 * R; be.add(vongMoc);
    const mocKeo = new T.Object3D(); mocKeo.position.set(3.83, RK - .24, 0); be.add(mocKeo); neo.mocKeo = mocKeo;

    // ---- cradle, recoil sleigh, equilibrators, shield ---------------------
    const tren = H.nhom('tren'); tren.position.set(.15, RK + .3, 0); be.add(tren);
    for (const z of [-1, 1]) {
      const tai = H.mesh(H.tam([[-.35, 0], [.45, 0], [.25, .32], [-.05, .38], [-.3, .2]], .05), VL); tai.position.set(0, 0, z * .2); tren.add(tai);
      const can = H.thanh([.35, .02, z * .32], [-.05, .5, z * .32], .055, VL); tren.add(can);
      const canTrong = H.thanh([.32, .05, z * .32], [.48, -.08, z * .32], .035, 'thep-mon'); tren.add(canTrong);
    }
    // Double shield: front and rear plates either side of the barrel, a top plate over the cradle.
    const lc = H.nhom('la-chan'); lc.position.set(-.42, 0, 0); tren.add(lc);
    for (const [dx, day] of [[0, .012], [.07, .01]]) for (const z of [-1, 1]) {
      const tam = H.mesh(H.tam([[0, -.15], [.74, -.15], [.79, .35], [.75, .78], [.22, .88], [0, .68]], day, .003), VL);
      tam.rotation.y = z > 0 ? -90 * R : 90 * R; tam.position.set(dx, 0, z * .2); tam.scale.set(1, 1, 1); lc.add(tam);
    }
    const nap = H.mesh(H.hop(.08, .03, .45, .01), VL); nap.position.set(.03, .76, 0); lc.add(nap);
    const ganLc = []; for (let i = 0; i < 6; i++) for (const z of [-1, 1]) ganLc.push([-.008, -.1 + i * .15, z * (.3 + (i % 3) * .18)]);
    lc.add(H.dinhTan(ganLc, .007, VLT, [-1, 0, 0]));
    // Sight and handwheels on the left.
    const ngam = H.nhom('ngam'); ngam.position.set(.25, .62, .38); tren.add(ngam);
    ngam.add(H.mesh(H.truX(.03, .03, .2, 12), 'thep'));
    ngam.add(H.thanh([0, -.03, 0], [0, -.3, -.05], .018, VLT));
    for (const [x, y] of [[.35, .2], [.1, .3]]) {
      const bl = H.mesh(new T.TorusGeometry(.1, .012, 6, 22), 'thep'); bl.position.set(x, y, .42); tren.add(bl);
      for (let i = 0; i < 3; i++) { const a = i / 3 * Math.PI * 2; bl.add(H.thanh([0, 0, 0], [Math.cos(a) * .1, Math.sin(a) * .1, 0], .006, 'thep')); }
    }

    // ---- elevating mass: barrel, breech, recoil cylinders (slides back on firing) ----
    const nang = H.nhom('nang'); nang.position.set(.05, .3, 0); tren.add(nang);
    const lui = H.nhom('lui'); nang.add(lui);
    const DAI = 2.31;
    lui.add(H.mesh(H.tien([[0, 0], [.072, 0], [.072, .35], [.062, .5], [.058, DAI], [0, DAI]], 20).rotateZ(90 * R), 'thep'));
    lui.add(H.mesh(H.hop(.3, .26, .28, .02), 'thep'));
    const khoa = H.mesh(H.hop(.08, .2, .22, .01), 'thep-mon'); khoa.position.set(.17, 0, 0); lui.add(khoa);
    // Chamber mouth (seen when the sliding breech block is open) and a round being rammed (close-ups only).
    const loNong = H.mesh(new T.CircleGeometry(.062, 24).rotateY(90 * R), 'den', { bong: false }); loNong.position.set(.152, 0, 0); lui.add(loNong);
    const dan = H.nhom('dan'); lui.add(dan);
    dan.add(H.mesh(H.truX(.056, .056, .37, 20).translate(.185, 0, 0), 'dong'));
    dan.add(H.mesh(H.tien([[0, 0], [.052, 0], [.052, .2], [.03, .33], [0, .4]], 20).rotateZ(90 * R), 'son-ol-toi'));
    const tayKhoa = H.thanh([.2, .08, .12], [.3, .2, .2], .012, 'thep-mon'); lui.add(tayKhoa);
    const xi = H.nhom('xi-lanh'); nang.add(xi);
    for (const y of [-.13, -.27]) { const c = H.mesh(H.truX(.07, .07, 1.25, 16), VL); c.position.set(-.55, y, 0); xi.add(c); }
    const ongDan = H.mesh(H.hop(1.35, .12, .2, .02), VL); ongDan.position.set(-.55, -.08, 0); xi.add(ongDan);
    const dauNong = new T.Object3D(); dauNong.position.set(-DAI - .02, 0, 0); lui.add(dauNong); neo.dauNong = dauNong;
    const lua = H.nhom('lua'); lua.position.copy(dauNong.position); lui.add(lua);
    const mLua = new T.MeshBasicMaterial({ color: 0xffd08a, transparent: true, opacity: .6, depthWrite: false });
    const non = new T.Mesh(H.tru(.0, .35, .9, 14).rotateZ(90 * R), mLua); non.position.x = -.45; lua.add(non);
    lua.add(new T.Mesh(new T.SphereGeometry(.24, 14, 10), new T.MeshBasicMaterial({ color: 0xfff0c4 })));
    const den = new T.PointLight(0xffb060, 0, 6, 1.8); lua.add(den);
    lua.traverse(o => { o.castShadow = false; o.userData.boQuaKhung = true; });

    // ---- cave emplacement dug into a hillside: a grassy earth dome open toward the muzzle, timber-framed mouth ----
    const ham = H.nhom('ham');
    const doiGeo = new T.SphereGeometry(1, 56, 22, 22 * R, 316 * R, 0, Math.PI / 2), dp = doiGeo.attributes.position;
    for (let i = 0; i < dp.count; i++) {
      const x = dp.getX(i), y = dp.getY(i), z = dp.getZ(i), n = 1 + .07 * Math.sin(x * 7 + z * 5) * Math.cos(y * 6 + x * 3) + .04 * Math.sin(z * 13 - x * 11);
      dp.setXYZ(i, x * 3.2 * n, y * 2.05 * n, z * 2.7 * n);
    }
    doiGeo.computeVertexNormals();
    const doi = H.mesh(doiGeo, K.vatLieu('dat').clone()); doi.material.side = T.DoubleSide; doi.position.set(1.35, 0, 0); ham.add(doi);
    const coDoi = H.mesh(new T.SphereGeometry(1, 40, 10, 22 * R, 316 * R, 0, .55).scale(3.25, 2.08, 2.75), 'co'); coDoi.position.set(1.35, .02, 0); ham.add(coDoi);
    for (const z of [-1, 1]) { const cot = H.mesh(H.tru(.1, .11, 1.55, 10), 'go-toi'); cot.position.set(-1.3, .77, z * .95); ham.add(cot); }
    const xa = H.mesh(H.truZ(.11, .11, 2.3, 10), 'go-toi'); xa.position.set(-1.3, 1.58, 0); ham.add(xa);
    for (let i = 0; i < 6; i++) { const g = H.mesh(H.truZ(.08, .08, 2.2 - i * .1, 8), 'go-toi'); g.position.set(-1.15 + i * .17, 1.68 + i * .04, 0); ham.add(g); }
    ham.traverse(o => { o.userData.boQuaKhung = true; });
    goc.add(ham);
    // ---- camouflage --------------------------------------------------------
    const la = [];
    for (const [cha, p, dai] of [[lc, [.0, .6, .5], 1.2], [lc, [.0, .6, -.5], 1.2], [lc, [0, 1.0, 0], 1.0], [be, [.5, 1.0, .6], 1.1], [be, [.5, 1.0, -.6], 1.1], [be, [1.6, .8, .2], 1.2], [be, [2.6, .7, -.2], 1.1], [lui, [-1.2, .05, 0], 1.0], [lui, [-.4, .05, 0], 1.0]]) {
      for (let k = 0; k < 3; k++) {
        const c = H.canhLa(rnd, dai * (.7 + rnd() * .5), 1.3);
        c.position.set(p[0] + (rnd() - .5) * .4, p[1] + (rnd() - .5) * .2, p[2] + (rnd() - .5) * .4);
        c.rotation.set((rnd() - .5) * 1.2, rnd() * 6.28, (rnd() - .3) * 1.2); cha.add(c); la.push(c);
      }
    }

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0, trienKhai = s !== 'keo';
      const quang = s === 'keo' ? (tt.tocDo === undefined ? TOC_KEO : tt.tocDo) * t : 0;
      // Towed trail first (+X), so the wheels turn the other way from the 37 mm.
      banh.forEach(w => { w.rotation.z = quang / RK; });
      cang.forEach(({ c, z, thuong }) => {
        c.rotation.y = trienKhai ? -z * 27 * R : z * 3.8 * R;
        thuong.rotation.z = trienKhai ? 0 : 80 * R;
      });
      vongMoc.visible = !trienKhai;
      nang.rotation.z = -(s === 'ban' ? 32 : s === 'trong-ham' ? 9 : s === 'nguy-trang' ? 14 : 0) * R;
      // Long recoil (about a metre) then a slow run-out; flash for the first instants.
      const pha = s === 'ban' ? (((t % CHU_KY_BAN) + CHU_KY_BAN) % CHU_KY_BAN) / CHU_KY_BAN : 1;
      lui.position.x = s === 'ban' ? (pha < .04 ? K.smooth(pha / .04) : 1 - K.smooth((pha - .04) / .4)) * 1.0 : 0;
      const sang = s === 'ban' && pha < .025;
      lua.visible = sang; den.intensity = sang ? 3 : 0;
      ham.visible = s === 'trong-ham';
      // Optional close-up controls: tt.khoa 0 = breech open .. 1 = closed (default), tt.napDan 0 = round behind
      // the breech .. 1 = fully home (default: no round shown).
      const kh = tt.khoa === undefined ? 1 : Math.min(1, Math.max(0, tt.khoa));
      khoa.position.z = (1 - kh) * .21; loNong.visible = kh < .98;
      dan.visible = tt.napDan !== undefined && tt.napDan < 1 && kh < .98;
      dan.position.x = .17 + (1 - Math.min(1, Math.max(0, tt.napDan || 0))) * .55 - .42;
      const phu = s === 'nguy-trang' ? 1 : (tt.nguyTrang || 0);
      la.forEach((c, i) => { c.visible = phu > 0 && i / la.length < phu; });
    }
    return { goc, capNhat, diemCham, neo, banKinhBanh: RK };
  }

  K.dangKy({
    ma: 'phao-105', ten: 'Lựu pháo 105 mm (M2A1)', phe: 'ta', thoiKy: 'dbp-1954',
    kichThuoc: { dai: 5.94, rong: 2.21, cao: 1.73 },
    trangThai: ['keo', 'ban', 'trong-ham', 'nguy-trang'],
    tao,
  });
})(typeof window !== 'undefined' ? window : globalThis);
