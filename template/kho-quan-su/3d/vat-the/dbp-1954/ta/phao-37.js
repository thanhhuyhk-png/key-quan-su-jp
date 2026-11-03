// 37 mm automatic AA gun M1939 (61-K) on the 4-wheel ZU-7 carriage, Soviet-made (NGUON.tsv: phao-37).
// Museum piece 510681: 6.20 x 1.78 x 2.50 m, green; shields beside the breech in front of the layers' seats.
// Travel: upper mount turned 180 deg, barrel locked at the tail. Firing: 4 jacks down, wheels lifted.
// Drawn with black tyres (white sidewalls on the exhibit are display paint). No markings, numbers or text.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const RK = .45, TOC_KEO = .6, CHU_KY_BAN = .35;

  function tao(K, op) {
    const goc = H.nhom('phao-37'), diemCham = [], neo = {};
    const rnd = K.rng(op.hat || 1);

    // ---- carriage frame -------------------------------------------------
    const khung = H.nhom('khung'); goc.add(khung);
    const dam = H.mesh(H.hop(3.0, .24, .42, .02), 'son-lx'); dam.position.set(-.05, .64, 0); khung.add(dam);
    const san = H.mesh(H.hop(2.1, .035, 1.08, .008), 'son-lx'); san.position.set(-.1, .775, 0); khung.add(san);
    for (const z of [-1, 1]) {
      const be = H.mesh(H.hop(2.1, .09, .05, .01), 'son-lx-toi'); be.position.set(-.1, .72, z * .52); khung.add(be);
    }
    const dinh = [];
    for (let i = 0; i < 15; i++) for (const z of [-1, 1]) dinh.push([-1.12 + i * .145, .795, z * .5]);
    khung.add(H.dinhTan(dinh.map(p => [p[0], p[1], p[2]]), .008, 'thep', [0, 1, 0]));
    // Axles and suspension arms.
    for (const x of [-1.05, 1.05]) {
      const truc = H.mesh(H.truZ(.045, .045, 1.48, 14), 'thep'); truc.position.set(x, RK, 0); khung.add(truc);
      for (const z of [-1, 1]) { const tay = H.thanh([x * .78, .6, z * .22], [x, RK + .02, z * .6], .04, 'son-lx-toi'); khung.add(tay); }
    }
    // Tow bar (A-frame) to the towing eye at the front.
    const MOC_X = 3.05;
    for (const z of [-1, 1]) khung.add(H.thanh([1.42, .62, z * .2], [MOC_X - .12, .56, 0], .045, 'son-lx'));
    const vongMoc = H.mesh(new T.TorusGeometry(.055, .018, 8, 20), 'thep'); vongMoc.position.set(MOC_X, .56, 0); vongMoc.rotation.x = 90 * R; khung.add(vongMoc);
    const mocKeo = new T.Object3D(); mocKeo.position.set(MOC_X + .04, .56, 0); khung.add(mocKeo); neo.mocKeo = mocKeo;
    // Travel lock post at the tail (barrel clamp).
    const giaKhoa = H.nhom('gia-khoa'); giaKhoa.position.set(-1.62, .6, 0); khung.add(giaKhoa);
    for (const z of [-1, 1]) giaKhoa.add(H.thanh([.08, 0, z * .2], [0, .8, z * .06], .03, 'son-lx'));
    const kep = H.mesh(H.hop(.12, .08, .2, .015), 'son-lx-toi'); kep.position.set(0, .84, 0); giaKhoa.add(kep);

    // ---- wheels (suspended from the frame) --------------------------------
    const banh = [];
    for (const x of [-1.05, 1.05]) for (const z of [-1, 1]) {
      const w = H.banhPhao(RK, .2); w.position.set(x, RK, z * .79); khung.add(w); banh.push(w);
      // Contact sits on the frame under the axle (a child of the spinning wheel would turn with it).
      const cham = new T.Object3D(); cham.position.set(x, 0, z * .79); khung.add(cham); cham.userData.laBanh = true; w.userData.cham = cham; diemCham.push(cham);
    }
    neo.banhSau = banh[0]; neo.banhTruoc = banh[2];

    // ---- jacks: 2 on frame ends, 2 on folding side outriggers ---------------
    const kich = [];
    function taoKich(cha, x, y, z) {
      const o = H.nhom('kich'); o.position.set(x, y, z); cha.add(o);
      const ong = H.mesh(H.tru(.04, .04, .22, 12), 'son-lx-toi'); ong.position.y = -.08; o.add(ong);
      const vit = H.mesh(H.tru(.022, .022, .6, 10), 'thep-mon'); o.add(vit);
      const de = H.mesh(H.tru(.12, .14, .035, 20), 'son-lx-toi'); o.add(de);
      const cham = new T.Object3D(); cham.position.y = -.018; de.add(cham); diemCham.push(cham);
      kich.push({ vit, de, cham });
      return o;
    }
    taoKich(khung, 1.48, .56, 0); taoKich(khung, -1.5, .56, 0);
    const cang = [];
    for (const z of [-1, 1]) {
      const c = H.nhom('cang'); c.position.set(0, .62, z * .23); khung.add(c);
      const thanh = H.mesh(H.hop(1.55, .1, .1, .015), 'son-lx'); thanh.position.set(.78, 0, 0); c.add(thanh);
      taoKich(c, 1.55, -.06, 0);
      cang.push({ c, z });
    }

    // ---- upper mount (turns 180 deg for travel) ---------------------------
    const be = H.nhom('be-tren'); be.position.set(0, .8, 0); khung.add(be);
    be.add(H.mesh(H.tien([[0, 0], [.56, 0], [.56, .06], [.5, .09], [0, .09]], 40), 'son-lx-toi'));
    const sanBe = H.mesh(H.hop(1.3, .03, 1.2, .01), 'son-lx'); sanBe.position.set(-.05, .1, 0); be.add(sanBe);
    for (const z of [-1, 1]) {
      const tai = H.mesh(H.tam([[-.32, 0], [.32, 0], [.24, .62], [.04, .7], [-.18, .55]], .04), 'son-lx'); tai.position.set(.08, .1, z * .17); be.add(tai);
    }
    // Shields: tall steel slabs either side of the cradle, ahead of the seats (exhibit 510681).
    for (const z of [-1, 1]) {
      const kh = H.mesh(H.tam([[-.05, 0], [.58, 0], [.58, .86], [.4, 1.18], [-.02, 1.18], [-.05, .9]], .014, .004), 'son-lx');
      kh.position.set(-.02, .12, z * .36); be.add(kh);
      const gan = []; for (let i = 0; i < 6; i++) gan.push([.0 + i * .1, .14 + .06, z * (.36 + .008)]);
      for (let i = 0; i < 5; i++) gan.push([.57, .3 + i * .17, z * (.36 + .008)]);
      be.add(H.dinhTan(gan, .007, 'thep', [0, 0, z]));
    }
    // Seats, handwheels, sight.
    for (const z of [-1, 1]) {
      const cot = H.mesh(H.tru(.025, .03, .42, 10), 'son-lx-toi'); cot.position.set(-.55, .33, z * .48); be.add(cot);
      const ghe = H.mesh(H.hop(.24, .04, .22, .015), 'thep'); ghe.position.set(-.55, .56, z * .48); be.add(ghe);
      const tua = H.mesh(H.hop(.04, .2, .2, .012), 'thep'); tua.position.set(-.68, .68, z * .48); be.add(tua);
      const banhLai = H.mesh(new T.TorusGeometry(.11, .012, 8, 28), 'thep'); banhLai.position.set(-.26, .72, z * .44); banhLai.rotation.y = 90 * R; be.add(banhLai);
      for (let i = 0; i < 3; i++) { const a = i / 3 * Math.PI * 2; banhLai.add(H.thanh([0, 0, 0], [Math.cos(a) * .11, Math.sin(a) * .11, 0], .006, 'thep')); }
      const tayQ = H.mesh(H.tru(.012, .012, .07, 8), 'go-toi'); tayQ.position.set(-.26, .83, z * .4); be.add(tayQ);
      const de = H.mesh(H.hop(.18, .02, .1, .006), 'son-lx-toi'); de.position.set(-.3, .2, z * .5); be.add(de);
    }
    const ngam = H.nhom('ngam'); ngam.position.set(-.18, 1.08, .3); be.add(ngam);
    ngam.add(H.mesh(H.hop(.22, .12, .1, .015), 'son-lx-toi'));
    const ongNgam = H.mesh(H.truX(.022, .022, .22, 12), 'thep'); ongNgam.position.set(-.08, .08, 0); ngam.add(ongNgam);
    ngam.add(H.thanh([0, -.06, 0], [.12, -.36, -.12], .015, 'son-lx-toi'));

    // ---- elevating mass: receiver, barrel, recuperator, clip --------------
    const trucNang = H.nhom('truc-nang'); trucNang.position.set(.15, .72, 0); be.add(trucNang);
    const lui = H.nhom('lui'); trucNang.add(lui);
    const hop = H.mesh(H.hop(1.1, .26, .2, .02), 'son-lx'); hop.position.set(-.3, .02, 0); lui.add(hop);
    const nap = H.mesh(H.hop(.7, .05, .16, .01), 'son-lx-toi'); nap.position.set(-.35, .17, 0); lui.add(nap);
    for (let i = 0; i < 5; i++) { const s = H.mesh(H.hop(.02, .2, .21, .004), 'son-lx-toi'); s.position.set(-.75 + i * .12, .02, 0); lui.add(s); }
    // Clip guide and a 5-round clip standing in it (brass cases, steel-grey projectiles).
    const kepDan = H.nhom('kep-dan'); lui.add(kepDan);
    const ray = H.mesh(H.hop(.26, .16, .05, .008), 'thep'); ray.position.set(-.18, .25, 0); lui.add(ray);
    for (let i = 0; i < 5; i++) {
      const vo = H.mesh(H.tru(.021, .021, .24, 12), 'dong'); vo.position.set(-.28 + i * .05, .38, 0); kepDan.add(vo);
      const dan = H.mesh(H.tien([[0, 0], [.019, 0], [.019, .03], [.012, .075], [0, .09]], 12), 'thep'); dan.position.set(-.28 + i * .05, .5, 0); kepDan.add(dan);
    }
    const khoaNong = H.mesh(H.truX(.07, .07, .22, 16), 'son-lx-toi'); khoaNong.position.set(.32, .0, 0); lui.add(khoaNong);
    const DAI_NONG = 2.35;
    const nong = H.mesh(H.tien([[0, 0], [.05, 0], [.05, .5], [.043, .6], [.043, DAI_NONG], [0, DAI_NONG]], 16).rotateZ(-90 * R), 'thep');
    nong.position.set(.4, 0, 0); lui.add(nong);
    const loaGiam = H.mesh(H.tien([[.038, 0], [.05, 0], [.075, .17], [.07, .19], [.03, .19]], 18).rotateZ(-90 * R), 'thep');
    loaGiam.position.set(.4 + DAI_NONG, 0, 0); lui.add(loaGiam);
    for (let i = 0; i < 4; i++) { const v = H.mesh(H.truX(.056, .056, .04, 16), 'son-lx-toi'); v.position.set(.48 + i * .13, 0, 0); lui.add(v); }
    const loXo = H.mesh(H.truX(.06, .06, 1.0, 16), 'son-lx'); loXo.position.set(.4, -.13, 0); trucNang.add(loXo);
    const dauNong = new T.Object3D(); dauNong.position.set(.4 + DAI_NONG + .2, 0, 0); lui.add(dauNong); neo.dauNong = dauNong;
    // Muzzle flash: emissive cone + star, and a short-lived light.
    const lua = H.nhom('lua'); lua.position.copy(dauNong.position); lui.add(lua);
    const mLua = new T.MeshBasicMaterial({ color: 0xffd38a, transparent: true, opacity: .9, depthWrite: false });
    const non = new T.Mesh(H.tru(.0, .16, .5, 12).rotateZ(-90 * R), mLua); non.position.x = .25; lua.add(non);
    const sao = new T.Mesh(new T.SphereGeometry(.12, 12, 8), new T.MeshBasicMaterial({ color: 0xfff1c8 })); lua.add(sao);
    const den = new T.PointLight(0xffb560, 0, 9, 1.6); lua.add(den);
    lua.traverse(o => { o.castShadow = false; o.userData.boQuaKhung = true; });

    // ---- extras by state: wheel chocks, earth emplacement, camouflage -------
    const chen = H.nhom('chen');
    for (const x of [-1.05, 1.05]) for (const z of [-1, 1]) {
      const g = H.mesh(H.tam([[0, 0], [.32, 0], [.32, .05], [.06, .2], [0, .2]], .2, .006), 'go'); g.position.set(x - RK - .3, 0, z * .79); chen.add(g);
    }
    goc.add(chen);
    const u = H.nhom('u-dat');
    u.add(H.mesh(H.tien([[2.55, 0], [2.7, .5], [2.85, .66], [3.05, .6], [3.4, 0]], 64), 'dat-do'));
    const coU = new T.InstancedMesh(new T.ConeGeometry(.04, .22, 4), K.vatLieuLa(2), 160), m4 = new T.Matrix4();
    for (let i = 0; i < 160; i++) { const a = rnd() * 6.28, r = 2.75 + rnd() * .45; m4.compose(new T.Vector3(Math.cos(a) * r, .64 - Math.abs(r - 2.9) * 1.4 + .04, Math.sin(a) * r), new T.Quaternion().setFromEuler(new T.Euler(rnd() * .5, 0, rnd() * .5)), new T.Vector3(1, .6 + rnd(), 1)); coU.setMatrixAt(i, m4); }
    u.add(coU); u.traverse(o => { o.userData.boQuaKhung = true; });
    goc.add(u);
    const la = H.nhom('nguy-trang');
    const ganLa = [[be, [.25, .9, .36], 1.1], [be, [.25, .9, -.36], 1.1], [be, [.3, 1.25, 0], 1.0], [be, [-.5, .9, .2], .9], [be, [-.4, .7, -.45], .9],
      [khung, [.6, .82, .5], 1.2], [khung, [-.7, .82, -.5], 1.2], [khung, [1.2, .7, -.3], 1.0], [khung, [-1.3, .8, .3], 1.0], [khung, [0, .82, 0], 1.3]];
    const laNong = [];
    for (const [cha, p, dai] of ganLa) for (let k = 0; k < 3; k++) {
      const c = H.canhLa(rnd, dai * (.7 + rnd() * .5), 1.3); c.position.set(p[0] + (rnd() - .5) * .3, p[1] + (rnd() - .5) * .2, p[2] + (rnd() - .5) * .3);
      c.rotation.set((rnd() - .5) * 1.2, rnd() * 6.28, (rnd() - .3) * 1.4); c.userData.cha = cha; la.add(c);
    }
    for (let k = 0; k < 6; k++) { const c = H.canhLa(rnd, .8 + rnd() * .4, 1.2); c.position.set(.6 + k * .32, .05, (rnd() - .5) * .1); c.rotation.set(rnd() * 6.28, (rnd() - .5) * .6, (rnd() - .5) * .5); laNong.push(c); lui.add(c); }
    // Branches attach to the moving parts so they ride with the mount and frame.
    la.children.slice().forEach(c => c.userData.cha.add(c));
    const tatCaLa = laNong.concat(be.children.filter(c => c.name === 'canh-la'), khung.children.filter(c => c.name === 'canh-la'));

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0, trienKhai = s === 'ban' || s === 'u-dat' || s === 'nguy-trang';
      // Upper mount: travel turns it to the rear with the barrel level in the lock.
      be.rotation.y = trienKhai ? 0 : Math.PI;
      trucNang.rotation.z = trienKhai ? (s === 'ban' ? 55 : s === 'u-dat' ? 62 : 48) * R : -1.5 * R;
      giaKhoa.visible = true; kep.position.y = .84;
      // Wheels roll with distance when towed; lift off the ground when deployed.
      const quang = s === 'keo' ? (tt.tocDo === undefined ? TOC_KEO : tt.tocDo) * t : 0;
      banh.forEach(w => { w.rotation.z = -quang / RK; w.position.y = RK + (trienKhai ? .1 : 0); w.userData.cham.position.y = w.position.y - RK; });
      // Jacks and outriggers.
      kich.forEach(k => { const h = trienKhai ? .56 : .26; k.vit.position.y = -h / 2; k.vit.scale.y = h / .6; k.de.position.y = -h; });
      cang.forEach(({ c, z }) => { c.rotation.y = trienKhai ? -z * 90 * R : 0; });
      diemCham.forEach(o => { o.visible = trienKhai ? !o.userData.laBanh : true; });
      // Firing cycle: fast recoil, slower run-out; flash for the first 50 ms of each round.
      const pha = s === 'ban' ? (((t % CHU_KY_BAN) + CHU_KY_BAN) % CHU_KY_BAN) / CHU_KY_BAN : 1;
      lui.position.x = s === 'ban' ? -.17 * (pha < .15 ? K.smooth(pha / .15) : 1 - K.smooth((pha - .15) / .6)) : 0;
      const sang = s === 'ban' && pha < .14;
      lua.visible = sang; den.intensity = sang ? 6 : 0;
      chen.visible = s === 'chen-banh';
      kepDan.visible = trienKhai;
      u.visible = s === 'u-dat';
      const phu = s === 'nguy-trang' ? 1 : (tt.nguyTrang || 0);
      tatCaLa.forEach((c, i) => { c.visible = phu > 0 && (i / tatCaLa.length) < phu; });
    }

    return { goc, capNhat, diemCham, neo, quangDuong: tt => (tt.trangThai === 'keo' ? TOC_KEO * (tt.t || 0) : 0), banKinhBanh: RK };
  }

  K.dangKy({
    ma: 'phao-37', ten: 'Pháo cao xạ 37 mm (61-K)', phe: 'ta', thoiKy: 'dbp-1954',
    kichThuoc: { dai: 6.2, rong: 1.78, cao: 2.5 },
    trangThai: ['keo', 'chen-banh', 'ban', 'u-dat', 'nguy-trang'],
    tao,
  });
})(typeof window !== 'undefined' ? window : globalThis);
