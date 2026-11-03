// Douglas C-47 Dakota, French Air Force transport groups at Dien Bien Phu (dien-bien-phu.md item 13).
// Type data: length 19.43 m, span 28.96 m, height 5.16 m at rest (tail-dragger, nose up about 11.5 degrees);
// cargo door on the LEFT rear fuselage, no tail ramp. Paint is not sourced: drawn muted silver-grey with the
// generic French roundel (blue centre, white, red outer) and three-stripe rudder flash (blue forward); no serials or unit codes (the file's decision).
// Item frame: +X is the nose, +Z the left wing, origin under the airframe. Banking and diving are the scene's job.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  K.dangKyVatLieu('nhom-c47', ['#9ba1a2', 'nhom', 2, .42, .55]);
  K.dangKyVatLieu('nhom-chay', ['#2b2724', 'hat', 2, .9, .25]);
  K.dangKyVatLieu('kinh-c47', ['#1d2328', 'hat', 1, .15, .6]);
  K.dangKyVatLieu('co-xanh', ['#1f3b78', 'son', 1, .55, .1]);
  K.dangKyVatLieu('co-trang', ['#d8d8d2', 'son', 1, .55, .1]);
  K.dangKyVatLieu('co-do', ['#a3252a', 'son', 1, .55, .1]);

  // Fuselage radius along x (lathe profile) and the upswept tail cone centreline.
  const PROF = [[-9.72, 0], [-9.6, .12], [-8.6, .36], [-7.0, .63], [-5.2, .9], [-3.0, 1.12], [-1.0, 1.22], [1.5, 1.24], [4.0, 1.22], [6.0, 1.15], [7.4, 1.0], [8.5, .78], [9.25, .5], [9.6, .22], [9.72, 0]];
  const rThan = x => { for (let i = 1; i < PROF.length; i++) if (x <= PROF[i][0]) { const [a, ra] = PROF[i - 1], [b, rb] = PROF[i]; return ra + (rb - ra) * (x - a) / (b - a); } return 0; };
  const vong = x => .013 * Math.pow(Math.max(0, -x - 2), 2);
  const CANH_Y = -.72, DONG_CO_Z = 3.3, DONG_CO_Y = -.55;
  // Gear chosen so the rest attitude matches the type: main wheels under the wing leading edge, tail wheel
  // strut 0.55 m, ground angle about 11.6 degrees, prop tips about 1 m clear, fin top 5.16 m.
  const BANH_X = 2.3, CHAN = 1.68, DUOI_X = -8.35, DUOI_CHAN = .7;
  const DAT_DUOI = vong(DUOI_X) - .3 - DUOI_CHAN + .05 - .23, DAT_CHINH = DONG_CO_Y - CHAN - .61;
  const GOC_DAT = Math.atan2(DAT_DUOI - DAT_CHINH, BANH_X - DUOI_X + .12) / R;

  // Skin panels: the fuselage lathe maps U round and V along (two tiles); the wing and tail plates map metres, so they
  // take their own copy of the texture at about 7 m a tile.
  let vlTam = null;
  function nhomTam() {
    if (vlTam) return vlTam;
    const g = K.vatLieu('nhom-c47');
    if (!g.map) return (vlTam = g);
    vlTam = g.clone(); vlTam.map = g.map.clone(); vlTam.map.repeat.set(.14, .14); vlTam.map.needsUpdate = true; vlTam.bumpMap = vlTam.map;
    return vlTam;
  }

  // Plan-form plate in the XZ plane (outline [x, z] points), thickness tapering with |z|, centred on y = 0.
  function tamNgang(diem, day, vatLieu, ham) {
    const geo = H.tam(diem.map(([x, z]) => [x, z]), day, .02).rotateX(90 * R);
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i); p.setY(i, ham(x, z, p.getY(i))); }
    geo.computeVertexNormals();
    return H.mesh(geo, vatLieu);
  }
  function nuaCanh(s) {
    const LE = z => 3.0 - Math.max(0, z - 4.2) * Math.tan(15.5 * R), TE = z => -1.4 - (z - 1.1) * .004;
    const d = [];
    for (let z = 1.1; z <= 14.0001; z += .7) d.push([LE(z), s * z]);
    for (let k = 1; k <= 6; k++) { const a = k / 7 * Math.PI; d.push([K.lerp(LE(14), TE(14.48), .5) + Math.cos(a) * (LE(14) - TE(14.48)) / 2, s * (14 + Math.sin(a) * .48)]); }
    for (let z = 14.0; z >= 1.0999; z -= .7) d.push([TE(z), s * z]);
    return tamNgang(d, .56, nhomTam(), (x, z, y) => {
      const az = Math.abs(z), u = Math.min(1, Math.max(0, (LE(Math.min(az, 14)) - x) / Math.max(.5, LE(Math.min(az, 14)) - TE(az))));
      const day = (1 - .62 * (az - 1.1) / 13.4) * (.3 + .7 * Math.pow(Math.sin(Math.PI * Math.min(1, u * 1.25 + .05)), .55));
      return y * day + CANH_Y + Math.max(0, az - 4.2) * Math.tan(6 * R);
    });
  }
  function canhQuat(rnd) {
    const o = H.nhom('canh-quat');
    o.add(H.mesh(H.tien([[0, -.25], [.3, -.2], [.26, .15], [.12, .38], [0, .45]], 20).rotateZ(-90 * R), 'thep'));
    for (let i = 0; i < 3; i++) {
      const la = H.mesh(H.tam([[.18, -.06], [1.75, -.09], [1.78, 0], [1.7, .1], [.18, .09]], .03, .006), 'den');
      const k = H.nhom(); k.rotation.x = i * 120 * R;
      la.rotation.set(18 * R, 0, 90 * R); la.position.x = .05; k.add(la); o.add(k);
      la.userData.boQuaKhung = true;
    }
    // Faint blur disc so a spinning prop reads at 24 fps.
    const mo = new T.Mesh(new T.CircleGeometry(1.76, 40).rotateY(90 * R), new T.MeshBasicMaterial({ color: 0x2a2a2a, transparent: true, opacity: .12, depthWrite: false, side: T.DoubleSide }));
    mo.userData.boQuaKhung = true; mo.castShadow = false; o.add(mo); o.userData.mo = mo;
    return o;
  }
  function cocarde(r) {
    const o = H.nhom('cocarde');
    // French cocarde: blue centre, white ring, red outer ring (reversed it would be the British roundel).
    [[r, 'co-do'], [r * .66, 'co-trang'], [r * .33, 'co-xanh']].forEach(([rr, vl], i) => { const m = H.mesh(new T.CircleGeometry(rr, 40), vl, { bong: false }); m.position.z = i * .004; o.add(m); });
    return o;
  }

  function tao(K, op) {
    const goc = H.nhom('c47'), may = H.nhom('may'), rnd = K.rng(op.hat || 1), neo = {};
    goc.add(may);
    const cham = new T.Object3D(); goc.add(cham);

    // ---- fuselage ------------------------------------------------------------
    const thanGeo = H.tien(PROF.map(([x, r]) => [r, x]), 36).rotateZ(-90 * R).scale(1, 1.07, 1);
    const tp = thanGeo.attributes.position; for (let i = 0; i < tp.count; i++) tp.setY(i, tp.getY(i) + vong(tp.getX(i)));
    thanGeo.computeVertexNormals();
    const than = H.mesh(thanGeo, 'nhom-c47'); may.add(than);
    const tren = (x, y, ben) => [x, y + vong(x), ben * Math.sqrt(Math.max(0, Math.pow(rThan(x) * 1.0, 2) - y * y))];
    // Cockpit glazing, cabin windows, left rear cargo door (outline only), all as thin dark plates on the skin.
    const kinh = (x, y, ben, w, h, quay) => { const [px, py, pz] = tren(x, y, ben); const m = H.mesh(H.hop(w, h, .03, .008), 'kinh-c47', { bong: false }); m.position.set(px, py, pz); m.rotation.set(0, 0, 0); m.lookAt(px, py + (quay || 0), pz + ben * 3); return m; };
    for (const ben of [-1, 1]) {
      for (const [x, y] of [[8.15, .52], [7.75, .62], [7.35, .66]]) may.add(kinh(x, y, ben, .36, .26, .4));
      for (let i = 0; i < 7; i++) may.add(kinh(-3.6 + i * .95, .3, ben, .32, .3));
    }
    const cua = H.mesh(H.hop(1.5, 1.55, .025, .01), K.vatLieu('nhom-c47', '#7e8485'), { bong: false });
    { const [px, py, pz] = tren(-5.3, -.05, 1); cua.position.set(px, py, pz); cua.lookAt(px, py, pz + 3); may.add(cua); }
    const cuaNeo = new T.Object3D(); cuaNeo.position.copy(cua.position); may.add(cuaNeo); neo.cuaHang = cuaNeo;

    // ---- wings, nacelles, props ------------------------------------------------
    const canhT = nuaCanh(1), canhP = nuaCanh(-1); may.add(canhT); may.add(canhP);
    const quat = [], lua = [], dongCo = [];
    for (const s of [1, -1]) {
      const n = H.nhom('dong-co'); n.position.set(0, DONG_CO_Y, s * DONG_CO_Z); may.add(n); dongCo.push(n);
      n.add(H.mesh(H.tien([[0, -5.0], [.66, -4.95], [.73, -4.4], [.72, -3.2], [.6, -1.6], [.42, -.2], [.18, .9], [0, 1.0]], 28).rotateZ(90 * R), 'nhom-c47'));
      const cowl = H.mesh(new T.TorusGeometry(.68, .06, 8, 28).rotateY(90 * R), 'den'); cowl.position.x = 4.98; n.add(cowl);
      const q = canhQuat(rnd); q.position.x = 5.12; n.add(q); quat.push(q);
      const f = H.nhom('lua'); f.position.set(1.2, .55, 0); n.add(f); lua.push(f);
      const ngon = H.lua(rnd, { r: .45, cao: 1.6, toc: 2.2, n: 14, khoi: 6 }); ngon.rotation.z = 62 * R; f.add(ngon); f.userData.ngon = ngon;
      const den = new T.PointLight(0xff9a40, 0, 14, 1.6); f.add(den); f.userData.den = den;
      f.traverse(o => { o.castShadow = false; o.userData.boQuaKhung = true; });
      const nl = new T.Object3D(); nl.position.copy(f.position); n.add(nl); neo[s > 0 ? 'dongCoT' : 'dongCoP'] = nl;
    }
    // Main gear under each nacelle: two struts, wheel; and a short tail wheel.
    const banh = [], chan = [];
    for (const s of [1, -1]) {
      const c = H.nhom('cang-chinh'); c.position.set(BANH_X, DONG_CO_Y, s * DONG_CO_Z); may.add(c); chan.push(c);
      const thanh = H.nhom('thanh-cang'); c.add(thanh); c.userData.thanh = thanh;
      for (const dz of [-.22, .22]) thanh.add(H.thanh([0, -.2, dz], [0, -CHAN, dz * .4], .055, 'thep'));
      const b = H.nhom('banh'); b.position.set(0, -CHAN, 0); c.add(b); banh.push(b);
      b.add(H.mesh(new T.TorusGeometry(.44, .17, 12, 32), 'cao-su'));
      b.add(H.mesh(H.truZ(.3, .3, .24, 20), 'thep-mon'));
    }
    const duoiBanh = H.nhom('banh-duoi'); duoiBanh.position.set(DUOI_X, vong(DUOI_X) - .3, 0); may.add(duoiBanh);
    duoiBanh.add(H.thanh([0, .25, 0], [-.12, -DUOI_CHAN + .05, 0], .045, 'thep'));
    const bd = H.mesh(new T.TorusGeometry(.16, .07, 8, 20), 'cao-su'); bd.position.set(-.12, -DUOI_CHAN + .05, 0); duoiBanh.add(bd);

    // ---- tail: fin with tricolour rudder flash, tailplane ----------------------------------------------
    const yDuoi = vong(-8.2);
    const fin = H.mesh(H.tam([[-5.6, 0], [-8.1, 3.5], [-9.05, 3.7], [-9.62, 3.25], [-9.7, .1]], .18, .02), nhomTam());
    fin.position.set(0, yDuoi + .55, 0); may.add(fin);
    const dauChay = [];  // markings on parts that burn on the wreck
    [['co-xanh', -9.0], ['co-trang', -9.3], ['co-do', -9.6]].forEach(([vl, x]) => {
      for (const s of [1, -1]) { const m = H.mesh(H.hop(.3, 2.3, .01, .002), vl, { bong: false }); m.position.set(x, yDuoi + .55 + 1.5, s * .095); may.add(m); dauChay.push(m); }
    });
    for (const s of [1, -1]) may.add(tamNgang([[-7.5, 0], [-8.2, s * 4.0], [-8.75, s * 4.25], [-9.55, s * 3.9], [-9.7, 0]].map(([x, z]) => [x, z]), .2, nhomTam(), (x, z, y) => y * (1 - .5 * Math.abs(z) / 4.3) + yDuoi + .45));
    // Roundels: wing tops near the tips, fuselage sides behind the wing.
    for (const s of [1, -1]) {
      const c = cocarde(.75); c.rotation.x = -90 * R; c.position.set(-.1, CANH_Y + .16 + (11.5 - 4.2) * Math.tan(6 * R), s * 11.5); may.add(c);
      if (s < 0) canhP.userData.cocarde = c;
      const f = cocarde(.6); const [px, py, pz] = tren(-2.6, .15, s); f.position.set(px, py, pz + s * .02); f.rotation.y = s > 0 ? 0 : Math.PI; may.add(f); dauChay.push(f);
    }

    // Outer right wing panel as its own part so the wreck can lose it.
    may.traverse(o => { if (o.isMesh) o.userData.vlGoc = o.material; });
    than.userData.chay = true; canhP.userData.chay = true; fin.userData.chay = true;

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0;
      const dat = s === 'ha-canh' || s === 'xac', gear = s === 'ha-canh';
      may.position.set(0, 0, 0); may.rotation.set(0, 0, dat ? GOC_DAT * R : 0);
      if (s === 'xac') { may.rotation.set(-4 * R, 0, 1.5 * R); }
      // Retracted, the C-47's main wheels stay half out under the nacelles; the struts fold away.
      chan.forEach(c => { c.visible = s !== 'xac'; c.userData.thanh.visible = gear; c.position.y = DONG_CO_Y + (gear ? 0 : CHAN - .37); });
      banh.forEach(b => { b.rotation.z = gear ? -(tt.tocDo || 0) * t / .61 : 0; });
      duoiBanh.visible = s !== 'xac';
      // Props: about 4 turns a second on screen (stylised), slow windmill on the hit engine, bent and still on the wreck.
      quat.forEach((q, i) => {
        const hong = (s === 'trung-dan' && i === 1) || s === 'xac';
        q.rotation.x = hong ? (s === 'xac' ? 25 * R : t * 2.2) : t * 2 * Math.PI * 4.3;
        q.userData.mo.visible = !hong;
      });
      // Fire: right engine when hit; small residual fires on the wreck. Flicker is a pure function of t.
      lua.forEach((f, i) => {
        const chay = (s === 'trung-dan' && i === 1) || (s === 'xac' && i === 1);
        f.visible = chay;
        const k = 1 + .18 * Math.sin(t * 23 + i) + .12 * Math.sin(t * 37.3);
        f.userData.ngon.userData.capNhat(t, s === 'xac' ? .6 : 1); f.userData.den.intensity = chay ? 4 * k : 0;
      });
      // Wreck: belly on the ground, charred skin on the rear and right side, outer right wing gone.
      may.traverse(o => { if (o.isMesh && o.userData.vlGoc && !o.userData.boQuaKhung) o.material = (s === 'xac' && (o.userData.chay || (o.parent && o.parent.userData && o.parent.userData.chay))) ? K.vatLieu('nhom-chay') : o.userData.vlGoc; });
      canhP.scale.set(1, 1, s === 'xac' ? .55 : 1); canhP.userData.cocarde.visible = s !== 'xac';
      dauChay.forEach(m => { m.visible = s !== 'xac'; });
      H.chamThap(goc, cham);
    }
    return { goc, capNhat, diemCham: [cham], neo };
  }

  K.dangKy({
    ma: 'c47', ten: 'Máy bay vận tải C-47 Dakota', phe: 'phap', thoiKy: 'dbp-1954',
    kichThuoc: { dai: 19.43, rong: 28.96, cao: 5.16 },
    trangThai: ['bay', 'ha-canh', 'trung-dan', 'xac'],
    tao,
  });
})(typeof window !== 'undefined' ? window : globalThis);
