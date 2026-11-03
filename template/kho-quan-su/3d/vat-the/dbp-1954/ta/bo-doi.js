// Main-force soldier, Dien Bien Phu 1954 (NGUON.tsv: bo-doi; dien-bien-phu.md item 1, checked against photos).
// Helmet: woven bamboo (open hexagonal weave), rounded crown flaring into the brim, dark strap, leaves tucked into
// the weave, as Tran Can's helmet in the Military History Museum and Karmen's colour footage at Dien Bien Phu.
// Variant mu 'boc-vai': cloth-covered with a net. Star on the helmet is OFF by default (one press caption only).
// Shirt worn outside the trousers with a belt, turn-down collar, two flap pockets, long sleeves; faded olive
// ("co ua"); cloth pack on two shoulder straps; rubber sandals. Default weapon K-50 (PPSh-41 pattern: wooden stock,
// perforated jacket, CURVED 35-round box magazine).
// Variants: sung 'k50' | 'k24' | 'khong'; ao 'so-mi' | 'tran-thu' (quilted, sleeved); mu 'nan' | 'boc-vai';
// saoMu; balo (default on); laLung (leaf bundle on the pack, as in assault photos); danSu; khongMat.
// Forbidden: pith or steel helmets of later periods, AK, folding-stock K-50M, drum magazines, rank insignia.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R, N = K.nguoi;

  // Closed lathe profile: outer surface from the crown down to the brim edge, then back up the inside.
  const MU_NGOAI = [[0, .268], [.05, .265], [.09, .25], [.118, .222], [.135, .19], [.15, .16], [.172, .132], [.192, .112]];
  const MU_TRONG = [[.186, .109], [.166, .127], [.145, .154], [.129, .182], [.111, .21], [.084, .236], [.045, .25], [0, .253]];
  function muNan(rnd, op) {
    const o = H.nhom('mu-nan');
    const bocVai = op.mu === 'boc-vai';
    o.add(H.mesh(H.tien(MU_NGOAI.concat(MU_TRONG), 40), bocVai ? 'vai-mu' : 'nan-tre'));
    // Rim binding and the inner head band.
    const vien = H.mesh(new T.TorusGeometry(.19, .0055, 5, 48).rotateX(90 * R), bocVai ? 'vai-mu' : 'tre'); vien.position.y = .111; o.add(vien);
    const dai = H.mesh(H.tru(.124, .124, .03, 32, 1, true), 'da-that'); dai.position.y = .16; o.add(dai);
    if (bocVai) {
      for (const [r, y] of [[.12, .21], [.142, .165]]) { const v = H.mesh(new T.TorusGeometry(r + .004, .0012, 4, 40).rotateX(90 * R), 'luoi'); v.position.y = y; o.add(v); }
      for (let i = 0; i < 10; i++) {
        const a = i / 10 * Math.PI * 2, d = MU_NGOAI.map(([r, y]) => [Math.cos(a) * (r + .003), y + .002, Math.sin(a) * (r + .003)]);
        o.add(H.mesh(H.ong(d, .0011, 16), 'luoi'));
      }
    }
    // Leaves tucked into the weave/net, standing out from the crown.
    for (let i = 0; i < 7; i++) {
      const c = H.canhLa(rnd, .14 + rnd() * .06, .6); c.scale.setScalar(.36);
      const a = i / 7 * Math.PI * 2 + rnd() * .5, k = 2 + Math.floor(rnd() * 3), p = MU_NGOAI[k];
      c.position.set(Math.cos(a) * p[0], p[1], Math.sin(a) * p[0]);
      c.rotation.set(0, -a, 55 * R + rnd() * .5); o.add(c);
    }
    if (op.saoMu) {
      const s = [];
      for (let i = 0; i < 10; i++) { const a = Math.PI / 2 + i * Math.PI / 5, r = i % 2 ? .009 : .022; s.push([Math.cos(a) * r, Math.sin(a) * r]); }
      const sao = H.mesh(H.tam(s, .003, 0), K.vatLieu('vai-mu', '#6c7c48'));
      sao.position.set(.14, .19, 0); sao.rotation.set(0, 90 * R, 0); sao.rotateX(-40 * R); o.add(sao);
    }
    // Chin strap.
    const quai = H.mesh(new T.TorusGeometry(.1, .003, 4, 24, Math.PI).rotateY(90 * R), 'da-that'); quai.position.set(.015, .14, 0); quai.rotation.z = Math.PI; o.add(quai);
    return o;
  }

  // Cloth pack with a flap, carried high on the back on two shoulder straps (straps visible in trench photos).
  function baLo(nguc, rnd, laLung) {
    const o = H.nhom('ba-lo'); nguc.add(o);
    const than = H.mesh(H.hop(.13, .32, .29, .04), 'ba-lo'); than.position.set(-.19, .04, 0); o.add(than);
    const nap = H.mesh(H.hop(.15, .1, .3, .03), 'ba-lo'); nap.position.set(-.185, .18, 0); nap.rotation.z = -.15; o.add(nap);
    for (const z of [-1, 1]) {
      o.add(H.mesh(H.ong([[-.15, .19, z * .085], [-.06, .245, z * .1], [.04, .24, z * .11], [.115, .16, z * .1], [.125, .04, z * .115], [.06, -.06, z * .16], [-.13, -.1, z * .11]], .009, 30), 'da-that'));
      const khoa = H.mesh(H.hop(.02, .03, .03, .004), 'thep-mon'); khoa.position.set(-.255, .15, z * .07); o.add(khoa);
    }
    if (laLung) for (let i = 0; i < 6; i++) {
      const c = H.canhLa(rnd, .5 + rnd() * .3, 1.2); c.position.set(-.26, -.05 + rnd() * .2, (rnd() - .5) * .2);
      c.rotation.set((rnd() - .5) * .8, (rnd() - .5) * .8, 70 * R + rnd() * .6); o.add(c);
    }
    return o;
  }

  // Weapons are built along +X from the butt (x = 0); marker objects give hand grips and the shoulder point.
  function k50() {
    const o = H.nhom('k50');
    o.add(H.mesh(H.tam([[0, -.06], [.02, .03], [.3, .025], [.38, .02], [.38, -.03], [.3, -.035], [.22, -.025], [.1, -.075], [.02, -.1]], .042, .006), 'go'));
    const than = H.mesh(H.hop(.22, .05, .04, .006), 'thep'); than.position.set(.46, .02, 0); o.add(than);
    const ong = H.mesh(H.truX(.024, .024, .3, 14), 'thep'); ong.position.set(.71, .022, 0); o.add(ong);
    for (let i = 0; i < 6; i++) for (const z of [-1, 1]) { const l = H.mesh(H.truZ(.006, .006, .005, 8), 'den'); l.position.set(.6 + i * .04, .025, z * .023); o.add(l); }
    const mieng = H.mesh(H.hop(.035, .045, .05, .005), 'thep'); mieng.position.set(.875, .025, 0); mieng.rotation.z = -.35; o.add(mieng);
    // Curved box magazine (arc of an annulus sector, extruded).
    const cung = [];
    for (let i = 0; i <= 8; i++) { const u = i / 8; cung.push([.4 + u * .055 + u * u * .05, -.005 - u * .2]); }
    for (let i = 8; i >= 0; i--) { const u = i / 8; cung.push([.448 + u * .055 + u * u * .05, -.005 - u * .19]); }
    const hop = H.mesh(H.tam(cung, .026, .003), 'thep'); o.add(hop);
    const coSo = H.mesh(new T.TorusGeometry(.022, .004, 4, 12, Math.PI), 'thep'); coSo.position.set(.37, -.01, 0); coSo.rotation.z = Math.PI; o.add(coSo);
    const ngam = H.mesh(H.hop(.02, .02, .01, .003), 'thep'); ngam.position.set(.4, .055, 0); o.add(ngam);
    const g = { vai: [.0, -.03, 0], tayCo: [.33, -.03, 0], tayTruoc: [.58, 0, 0] };
    return { o, g };
  }
  function k24() {
    const o = H.nhom('k24');
    o.add(H.mesh(H.tam([[0, -.07], [.02, .03], [.3, .02], [.85, .02], [.85, -.02], [.36, -.03], [.26, -.03], [.12, -.06], [.02, -.11]], .04, .006), 'go'));
    const nong = H.mesh(H.truX(.011, .013, .48, 10), 'thep'); nong.position.set(.95, .02, 0); o.add(nong);
    const khoa = H.mesh(H.truX(.017, .017, .16, 10), 'thep'); khoa.position.set(.38, .035, 0); o.add(khoa);
    const can = H.thanh([.42, .04, 0], [.42, .02, -.06], .006, 'thep'); o.add(can);
    const g = { vai: [.0, -.03, 0], tayCo: [.3, -.04, 0], tayTruoc: [.62, -.01, 0] };
    return { o, g };
  }

  function tao(K, op) {
    const danSu = !!op.danSu, khongMat = !!op.khongMat;
    const p = N.taoNguoi({ vlAo: danSu ? 'vai-dan' : op.ao === 'tran-thu' ? 'vai-tran-thu' : 'vai-quan', vlQuan: danSu ? 'vai-dan' : 'vai-quan', ao: danSu ? 'dan-su' : op.ao, khongMat, chan: op.chan });
    const rnd = K.rng(op.hat || 1), neo = {};
    if (!danSu) { p.dau.add(muNan(rnd, op)); if (op.balo !== false) baLo(p.nguc, rnd, op.laLung); }
    const loai = danSu ? 'khong' : (op.sung || 'k50');
    let sung = null;
    if (loai !== 'khong') {
      sung = loai === 'k24' ? k24() : k50();
      sung.diem = {};
      for (const [k, v] of Object.entries(sung.g)) { const m = new T.Object3D(); m.position.set(...v); sung.o.add(m); sung.diem[k] = m; }
      const day = H.mesh(H.ong([[0, -.06, .025], [.25, -.12, .03], [.55, -.05, .03]], .006, 12), 'da-that'); sung.o.add(day);
      sung.deo = H.nhom('deo'); p.nguc.add(sung.deo);
      // Slung across the back, muzzle up behind the right shoulder.
      sung.deo.position.set(op.balo === false ? -.16 : -.29, -.32, .1); sung.deo.rotation.set(-28 * R, 0, 74 * R);
      sung.deo.add(sung.o);
    }
    // Contact points: soles, plus the knees for kneeling.
    const diemCham = [];
    for (const ten of ['T', 'P']) {
      diemCham.push(p.chan[ten].gotM, p.chan[ten].muiM);
      const goiM = new T.Object3D(); goiM.position.set(.03, -.045, 0); p.chan[ten].goi.add(goiM); diemCham.push(goiM);
    }
    neo.tayT = p.tay.T.banTay; neo.tayP = p.tay.P.banTay; neo.dinhDau = p.dinhDau; neo.vaiT = p.tay.T.vai;

    function capNhat(tt) {
      const ten = tt.tuThe || tt.trangThai;
      if (!N.TU_THE[ten]) throw new Error('bo-doi: không có tư thế ' + ten);
      const pose = N.TU_THE[ten](tt.t || 0);
      // On a slope the whole figure is tilted with the ground by the scene; take that lean back off the torso.
      if (tt.doc) { pose.nghieng = (pose.nghieng || 0) - tt.doc * .85; pose.dauCui = (pose.dauCui || 0) - tt.doc * .3; }
      const ngam = ten === 'quy-ngam' && sung;
      N.apDung(p, pose, { tay: ngam ? null : tt.tay });
      if (sung) {
        if (ngam) {
          // Shouldered: butt at the right shoulder, barrel level, cheek on the stock; hands to the grips.
          if (sung.o.parent !== p.nguc) p.nguc.add(sung.o);
          const lean = (pose.nghieng || 0) * R;
          sung.o.position.set(.07, .17, -.13); sung.o.rotation.set(0, 4 * R, lean);
          p.goc.updateMatrixWorld(true);
          N.ikTay(p, 'P', sung.diem.tayCo.getWorldPosition(new T.Vector3()));
          N.ikTay(p, 'T', sung.diem.tayTruoc.getWorldPosition(new T.Vector3()));
          p.dau.rotation.x = -10 * R;
        } else if (ten === 'xung-phong') {
          // Carried for the assault: butt by the right hip, muzzle forward and up; hands on the grips.
          if (sung.o.parent !== p.nguc) p.nguc.add(sung.o);
          const lean = (pose.nghieng || 0) * R;
          sung.o.position.set(.02, -.3, -.14); sung.o.rotation.set(0, 8 * R, lean + 24 * R);
          p.goc.updateMatrixWorld(true);
          N.ikTay(p, 'P', sung.diem.tayCo.getWorldPosition(new T.Vector3()));
          N.ikTay(p, 'T', sung.diem.tayTruoc.getWorldPosition(new T.Vector3()));
        } else if (sung.o.parent !== sung.deo) { sung.deo.add(sung.o); sung.o.position.set(0, 0, 0); sung.o.rotation.set(0, 0, 0); }
      }
      p.goc.updateMatrixWorld(true);
    }
    return { goc: p.goc, capNhat, diemCham, neo, nguoi: p, tocDo: ten => (N.TU_THE[ten](0).tocDo || 0) };
  }

  K.dangKy({
    ma: 'bo-doi', ten: 'Bộ đội chủ lực', phe: 'ta', thoiKy: 'dbp-1954',
    kichThuoc: { cao: 1.62 },
    trangThai: ['dung', 'di', 'quy-ngam', 'keo-day', 'day', 'xung-phong'],
    tao,
  });
})(typeof window !== 'undefined' ? window : globalThis);
