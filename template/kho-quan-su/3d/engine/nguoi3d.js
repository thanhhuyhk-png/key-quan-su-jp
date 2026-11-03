// Shared 3D human: jointed skeleton, two-bone IK for arms and legs, semi-realistic body meshes, pose library.
// Height 1.62 m (main-force soldier, dien-bien-phu.md item 1). +X forward, +Y up, +Z the figure's left.
// Poses give hip height/lean plus foot and hand targets; knees and elbows are solved, so feet plant exactly
// and scenes can put hands on a rope, a handlebar pole or a gun grip.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const L = { dui: .40, cang: .40, coChan: .065, than: .46, co: .07, dau: .23, tayTren: .28, cangTay: .25, vai: .185, hong: .09 };
  const KHOP = .02;                              // hip joints sit 2 cm below the pelvis origin
  const CAO_HONG = L.dui + L.cang + L.coChan + KHOP;   // 0.885 m with straight legs

  // Tapered limb segment along -Y from the joint: radius r1 at the joint, r2 at the far end, rounded caps.
  function chi(r1, r2, dai, seg) {
    const p = [];
    for (let i = 0; i <= 6; i++) { const a = -Math.PI / 2 + i / 6 * Math.PI / 2; p.push([Math.cos(a) * r2, -dai + Math.sin(a) * r2 * .9]); }
    for (let i = 0; i <= 6; i++) { const a = i / 6 * Math.PI / 2; p.push([Math.cos(a) * r1, Math.sin(a) * r1 * .9]); }
    p.sort((a, b) => a[1] - b[1]);
    p[0][0] = 0; p[p.length - 1][0] = 0;
    return H.tien(p, seg || 18);
  }
  // Ellipsoid helper.
  function cau(rx, ry, rz) { return new T.SphereGeometry(1, 24, 16).scale(rx, ry, rz); }

  // Two-bone IK: a (root joint) -> b (mid joint) -> end at local (0,-lenB,0) of b. pole bends the joint toward it.
  const _v = new T.Vector3(), _q = new T.Quaternion(), _m = new T.Matrix4();
  function huongXuong(bone, dirWorld, poleWorld) {
    // Orient bone so its local -Y points along dirWorld and local +X leans toward poleWorld.
    const y = dirWorld.clone().negate().normalize();
    const x = poleWorld.clone().sub(y.clone().multiplyScalar(poleWorld.dot(y)));
    if (x.lengthSq() < 1e-8) x.set(1, 0, 0).sub(y.clone().multiplyScalar(y.x));
    x.normalize();
    const z = new T.Vector3().crossVectors(x, y).normalize();
    _m.makeBasis(x, y, z);
    const qWorld = new T.Quaternion().setFromRotationMatrix(_m);
    bone.parent.getWorldQuaternion(_q);
    bone.quaternion.copy(_q.invert().multiply(qWorld));
    bone.updateMatrixWorld(true);
  }
  function ik(a, b, lenA, lenB, dich, pole) {
    a.updateMatrixWorld(true);
    const pA = a.getWorldPosition(new T.Vector3());
    const d = dich.clone().sub(pA);
    const dist = Math.min(lenA + lenB - 1e-4, Math.max(Math.abs(lenA - lenB) + 1e-4, d.length()));
    const dh = d.normalize();
    const cosA = (lenA * lenA + dist * dist - lenB * lenB) / (2 * lenA * dist);
    const perp = pole.clone().sub(dh.clone().multiplyScalar(pole.dot(dh)));
    if (perp.lengthSq() < 1e-8) perp.set(1, 0, 0);
    perp.normalize();
    const goi = pA.clone().add(dh.clone().multiplyScalar(cosA * lenA)).add(perp.clone().multiplyScalar(Math.sqrt(Math.max(0, 1 - cosA * cosA)) * lenA));
    huongXuong(a, goi.clone().sub(pA), pole);
    const end = pA.clone().add(dh.clone().multiplyScalar(dist));
    huongXuong(b, end.clone().sub(goi), pole);
    return goi;
  }

  // Build skeleton + body. ao: 'so-mi' | 'tran-thu' | 'dan-su'; returns parts for outfit code to dress.
  function taoNguoi(op) {
    const vlAo = op.vlAo || 'vai-quan', vlQuan = op.vlQuan || vlAo, vlDa = op.khongMat ? 'da-toi' : 'da';
    const goc = H.nhom('nguoi');
    const hong = H.nhom('hong'); goc.add(hong);
    const than = H.nhom('than'); hong.add(than);
    const nguc = H.nhom('nguc'); nguc.position.y = L.than * .55; than.add(nguc);
    const co = H.nhom('co'); co.position.y = L.than * .45; nguc.add(co);
    const dau = H.nhom('dau'); dau.position.y = L.co; co.add(dau);
    const p = { goc, hong, than, nguc, co, dau, tay: {}, chan: {} };

    // Torso: lathe shells flattened front-to-back. Shirt worn outside the trousers with the belt over it
    // (archive photos; Viet Minh-issued shirt in the Musee de l'Armee): turn-down collar, two flap pockets.
    const dayAo = op.ao === 'tran-thu' ? 1.07 : 1, phang = .72;
    const vo = (prof, vl) => { const m = H.mesh(H.tien(prof.map(([r, y]) => [r * dayAo, y]), 28), vl); m.scale.x = phang; return m; };
    hong.add(H.mesh(cau(.125, .11, .16), vlQuan));
    than.add(vo([[.158, -.13], [.153, -.06], [.143, .04], [.147, .17], [.158, .3]], vlAo));
    nguc.add(vo([[.157, -.04], [.167, .05], [.172, .13], [.163, .185], [.125, .212], [.07, .222], [.0, .224]], vlAo));
    const that = H.mesh(new T.TorusGeometry(.146 * dayAo, .016, 6, 36).rotateX(90 * R), 'da-that'); that.scale.x = phang; that.position.y = .03; than.add(that);
    const khoa = H.mesh(H.hop(.01, .036, .046, .004), 'thep-mon'); khoa.position.set(.146 * dayAo * phang + .006, .03, 0); than.add(khoa);
    const xF = r => r * dayAo * phang + .004;
    if (op.ao === 'so-mi' || !op.ao) for (const z of [-1, 1]) {
      const tui = H.mesh(H.hop(.012, .1, .082, .006), vlAo); tui.position.set(xF(.168), .05, z * .075); tui.rotation.z = -.08; nguc.add(tui);
      const nap = H.mesh(H.hop(.016, .032, .088, .006), vlAo); nap.position.set(xF(.17) + .004, .105, z * .075); nap.rotation.z = -.1; nguc.add(nap);
      const cuc = H.mesh(new T.SphereGeometry(.0055, 6, 4), 'cuc'); cuc.position.set(xF(.17) + .012, .095, z * .075); nguc.add(cuc);
    }
    // Front placket buttons (five on the quilted jacket too).
    for (const [b, y, r] of [[nguc, .16, .165], [nguc, .08, .17], [nguc, .0, .162], [than, .2, .15], [than, .1, .146]]) {
      const c = H.mesh(new T.SphereGeometry(.0055, 6, 4), 'cuc'); c.position.set(xF(r) + .003, y, 0); b.add(c);
    }
    // Turn-down collar: a band round the neck and two lapel points on the chest.
    const coAo = H.mesh(new T.TorusGeometry(.062, .014, 6, 24, Math.PI * 1.5).rotateX(90 * R).rotateY(-135 * R), vlAo); coAo.scale.x = .9; coAo.position.y = .215; nguc.add(coAo);
    if (op.ao !== 'dan-su') for (const z of [-1, 1]) {
      const ve = H.mesh(H.tam([[0, 0], [.055, -.012], [.01, -.07]], .006, .002), vlAo);
      ve.position.set(.085, .205, z * .022); ve.rotation.set(0, z > 0 ? -70 * R : -110 * R, -30 * R); nguc.add(ve);
    }

    // Neck and head: no identifying features (simple nose, ears, closed eye line); short dark hair.
    co.add(H.mesh(H.tru(.043, .049, L.co + .03, 12).translate(0, L.co / 2, 0), vlDa));
    const so = H.mesh(cau(.092, .108, .086), vlDa); so.position.set(.0, .105, 0); dau.add(so);
    const ham = H.mesh(cau(.072, .058, .068), vlDa); ham.position.set(.032, .046, 0); dau.add(ham);
    const toc = H.mesh(cau(.096, .075, .089), 'toc'); toc.position.set(-.016, .148, 0); dau.add(toc);
    if (!op.khongMat) {
      // Low, rounded nose merged into the face (a cone read as a cartoon at mid distance).
      const mui = H.mesh(cau(.016, .026, .017), vlDa); mui.position.set(.088, .088, 0); mui.rotation.z = -.25; dau.add(mui);
      for (const z of [-1, 1]) {
        const tai = H.mesh(cau(.012, .027, .009), vlDa); tai.position.set(-.004, .095, z * .087); dau.add(tai);
        const mat = H.mesh(H.hop(.003, .003, .017, .001), 'den'); mat.position.set(.085, .112, z * .031); dau.add(mat);
        const may = H.mesh(H.hop(.004, .004, .024, .001), 'toc'); may.position.set(.087, .127, z * .032); dau.add(may);
      }
    }
    p.dinhDau = new T.Object3D(); p.dinhDau.position.set(0, .2, 0); dau.add(p.dinhDau);

    // Arms: loose sleeves to the wrist with a cuff, then hand (palm, finger block, thumb).
    for (const [ten, ben] of [['T', 1], ['P', -1]]) {
      const vai = H.nhom('vai' + ten); vai.position.set(0, .155, ben * L.vai); nguc.add(vai);
      vai.add(H.mesh(cau(.062 * dayAo, .06, .062 * dayAo), vlAo));
      const tren = H.nhom('tayTren' + ten); vai.add(tren);
      tren.add(H.mesh(chi(.057 * dayAo, .05 * dayAo, L.tayTren + .02), vlAo));
      const khuyu = H.nhom('cangTay' + ten); khuyu.position.y = -L.tayTren; tren.add(khuyu);
      khuyu.add(H.mesh(chi(.05 * dayAo, .044 * dayAo, L.cangTay * .86), vlAo));
      const mang = H.mesh(H.tru(.045 * dayAo, .046 * dayAo, .03, 14), vlAo); mang.position.y = -L.cangTay * .84; khuyu.add(mang);
      khuyu.add(H.mesh(chi(.032, .027, L.cangTay), vlDa));
      const banTay = H.nhom('banTay' + ten); banTay.position.y = -L.cangTay; khuyu.add(banTay);
      // Hand about 12% smaller than before (it read as a fist-sized blob): palm, finger block, thumb.
      const long = H.mesh(cau(.034, .04, .017), vlDa); long.position.y = -.032; banTay.add(long);
      const ngon = H.mesh(cau(.03, .027, .018), vlDa); ngon.position.set(.011, -.07, 0); ngon.rotation.z = .5; banTay.add(ngon);
      const cai = H.mesh(cau(.01, .023, .01), vlDa); cai.position.set(.023, -.027, ben * .011); cai.rotation.z = .6; banTay.add(cai);
      p.tay[ten] = { vai, tren, khuyu, banTay };
    }
    // Legs: hip -> thigh -> shin -> foot (sole flat at y = -coChan from the ankle).
    for (const [ten, ben] of [['T', 1], ['P', -1]]) {
      const khop = H.nhom('dui' + ten); khop.position.set(0, -.02, ben * L.hong); hong.add(khop);
      khop.add(H.mesh(chi(.088, .066, L.dui + .01), vlQuan));
      const goi = H.nhom('cangChan' + ten); goi.position.y = -L.dui; khop.add(goi);
      goi.add(H.mesh(chi(.066, .056, L.cang * .9), vlQuan));
      const gau = H.mesh(H.tru(.056, .058, .035, 14), vlQuan); gau.position.y = -L.cang * .88; goi.add(gau);
      const coChanDa = H.mesh(H.tru(.03, .033, .08, 10), vlDa); coChanDa.position.y = -L.cang + .03; goi.add(coChanDa);
      const ban = H.nhom('banChan' + ten); ban.position.y = -L.cang; goi.add(ban);
      const chanDa = H.mesh(cau(.12, .032, .045), vlDa); chanDa.position.set(.05, -.035, 0); ban.add(chanDa);
      const got = H.mesh(cau(.04, .035, .04), vlDa); got.position.set(-.035, -.03, 0); ban.add(got);
      if (op.chan !== 'tran') {
        const de = H.mesh(H.hop(.27, .016, .1, .006), 'cao-su-dep'); de.position.set(.045, -L.coChan + .008, 0); ban.add(de);
        // Two inner-tube straps crossing over the instep (arched over the foot so they stay visible).
        for (const [x, ry] of [[.1, 28], [.03, -28]]) { const q = H.mesh(new T.TorusGeometry(.05, .007, 5, 14, Math.PI), 'cao-su-dep'); q.position.set(x, -.055, 0); q.rotation.set(0, (90 + ry) * R, 0); ban.add(q); }
        const quaiGot = H.mesh(new T.TorusGeometry(.045, .006, 4, 16, Math.PI).rotateY(90 * R).rotateZ(90 * R), 'cao-su-dep'); quaiGot.position.set(-.045, -.03, 0); ban.add(quaiGot);
      }
      const gotM = new T.Object3D(); gotM.position.set(-.08, -L.coChan, 0); ban.add(gotM);
      const muiM = new T.Object3D(); muiM.position.set(.18, -L.coChan, 0); ban.add(muiM);
      p.chan[ten] = { khop, goi, ban, gotM, muiM };
    }
    return p;
  }

  // ---- pose library ---------------------------------------------------------
  // Each returns { hongY, hongX, nghieng (deg forward), dauCui, chan: {T:[x,y,z], P:[...]}, gocChan: {T,P} (deg toe-down),
  //                tay: {T,P} targets or null, vungTay: {T,P} FK swing (deg) when no target }
  function buocChan(u, dai, nang) {
    // Stance (u < .6): foot slides back from +dai/2 to -dai/2. Swing: arcs forward.
    if (u < .6) return [dai * (.5 - u / .6), 0];
    const w = (u - .6) / .4;
    return [-dai / 2 + dai * K.smooth(w), nang * Math.sin(Math.PI * w)];
  }
  const TU_THE = {
    dung: () => ({ hongY: CAO_HONG - .002, hongX: 0, nghieng: 2, dauCui: 0, chan: { T: [.02, 0, .1], P: [-.02, 0, -.1] }, gocChan: { T: 0, P: 0 }, vungTay: { T: [4, 8], P: [-2, 8] } }),
    di: (t) => {
      const chuKy = 1.1, dai = .66, u = ((t / chuKy) % 1 + 1) % 1;
      const fT = buocChan(u, dai, .1), fP = buocChan((u + .5) % 1, dai, .1);
      const reach = Math.max(Math.abs(fT[0]), Math.abs(fP[0]));
      const hongY = Math.min(CAO_HONG - .01, L.coChan + KHOP + Math.sqrt(Math.pow(L.dui + L.cang - .012, 2) - reach * reach)) + .01 * Math.cos(u * 4 * Math.PI);
      return { hongY, hongX: 0, nghieng: 5, dauCui: 2, chan: { T: [fT[0], fT[1], .09], P: [fP[0], fP[1], -.09] }, gocChan: { T: fT[1] > .01 ? -10 : 0, P: fP[1] > .01 ? -10 : 0 },
        vungTay: { T: [-fT[0] * 55, 18], P: [-fP[0] * 55, 18] }, tocDo: dai / (chuKy * .6) };
    },
    'keo-day': (t) => {
      const chuKy = 1.6, toc = .26, dai = toc * chuKy * .6, u = ((t / chuKy) % 1 + 1) % 1;
      const fT = buocChan(u, dai, .08), fP = buocChan((u + .5) % 1, dai, .08);
      fP[0] -= .12;
      const sau = Math.min(fT[0], fP[0]), truoc = Math.max(fT[0], fP[0]);
      const hongX = Math.min(truoc + .12, sau + .42);
      const reach = Math.max(Math.hypot(fT[0] - hongX, .1), Math.hypot(fP[0] - hongX, .1));
      const hongY = Math.min(CAO_HONG - .02, L.coChan + KHOP + Math.sqrt(Math.max(.04, Math.pow(L.dui + L.cang - .015, 2) - reach * reach)));
      return { hongY, hongX, nghieng: 32, dauCui: -18, chan: { T: [fT[0], fT[1], .1], P: [fP[0], fP[1], -.1] }, gocChan: { T: 0, P: 0 },
        tay: { T: [hongX + .42, hongY + .38, .08], P: [hongX + .3, hongY + .34, -.04] }, tocDo: toc };
    },
    day: (t) => {
      const chuKy = 1.6, toc = .26, dai = toc * chuKy * .6, u = ((t / chuKy) % 1 + 1) % 1;
      const fT = buocChan(u, dai, .07), fP = buocChan((u + .5) % 1, dai, .07);
      fP[0] -= .1;
      const sau = Math.min(fT[0], fP[0]), truoc = Math.max(fT[0], fP[0]);
      const hongX = Math.min(truoc + .14, sau + .5);
      const reach = Math.max(Math.hypot(fT[0] - hongX, .1), Math.hypot(fP[0] - hongX, .1));
      const hongY = Math.min(CAO_HONG - .03, L.coChan + KHOP + Math.sqrt(Math.max(.04, Math.pow(L.dui + L.cang - .015, 2) - reach * reach)));
      return { hongY, hongX, nghieng: 48, dauCui: -30, chan: { T: [fT[0], fT[1], .11], P: [fP[0], fP[1], -.11] }, gocChan: { T: 0, P: 0 },
        tay: { T: [hongX + .7, hongY + .32, .17], P: [hongX + .7, hongY + .32, -.17] }, tocDo: toc };
    },
    // Right knee down, sitting back on the tucked right heel, left foot forward. Lengths are consistent: hip joint
    // .34 m high, knee .055 m (on the ground) .281 m ahead, ankle .40 m back along the shin rising 15 degrees.
    'quy-ngam': () => ({ hongY: .36, hongX: 0, nghieng: 22, dauCui: 12, chan: { T: [.46, 0, .14], P: [-.105, .094, -.12] }, gocChan: { T: 0, P: 37 },
      cuoiGoi: { P: [.281, .055, -.12] } }),
    // Assault run: long fast strides, body leaning in, head up; the rifle is carried in both hands (bo-doi puts the
    // hands on it). Feet still overlap on the ground (no flight phase) so contact checks hold at any t.
    'xung-phong': (t) => {
      // Stance half the cycle (foot drives from under the hip to behind it), swing half with a high knee; the other
      // foot is half a cycle out, so one foot is always planted while the gait still reads as running.
      const chuKy = .66, dai = .7, hongX = .05, u = ((t / chuKy) % 1 + 1) % 1;
      const chan = v => v < .5 ? [dai * (.3 - 1.6 * v), 0] : (w => [dai * (-.5 + .8 * K.smooth(w)), .38 * Math.sin(Math.PI * w)])((v - .5) / .5);
      const fT = chan(u), fP = chan((u + .5) % 1);
      // Hip as high as both legs can still reach their targets (a lifted foot allows a higher hip).
      const toi = f => f[1] + L.coChan + KHOP + Math.sqrt(Math.max(.01, Math.pow(L.dui + L.cang - .03, 2) - Math.pow(f[0] - hongX, 2)));
      const hongY = Math.min(CAO_HONG - .05, toi(fT), toi(fP)) - .02 + .02 * Math.cos(u * 4 * Math.PI);
      return { hongY, hongX, nghieng: 24, dauCui: -12, chan: { T: [fT[0], fT[1], .1], P: [fP[0], fP[1], -.1] }, gocChan: { T: fT[1] > .01 ? -25 : 0, P: fP[1] > .01 ? -25 : 0 },
        vungTay: { T: [30, 70], P: [-10, 80] }, tocDo: 1.6 * dai / chuKy };
    },
    // Stooped shuffle, hands low (carrying a wheel chock beside a towed gun); small steps at the pull speed.
    cui: (t) => {
      const chuKy = 1.2, toc = .26, dai = toc * chuKy * .6, u = ((t / chuKy) % 1 + 1) % 1;
      const fT = buocChan(u, dai, .05), fP = buocChan((u + .5) % 1, dai, .05);
      return { hongY: .64, hongX: -.08, nghieng: 58, dauCui: -24, chan: { T: [fT[0] + .1, fT[1], .14], P: [fP[0] - .14, fP[1], -.14] }, gocChan: { T: 0, P: 0 },
        tay: { T: [.52, .22, .12], P: [.5, .2, -.08] }, tocDo: toc };
    },
  };

  // Reach a hand to a world point; elbows bend down, back and slightly out.
  function ikTay(p, ten, dich) {
    const a = p.tay[ten], ben = ten === 'T' ? 1 : -1, o = p.goc.localToWorld(new T.Vector3());
    const fwd = p.goc.localToWorld(new T.Vector3(1, 0, 0)).sub(o), ngang = p.goc.localToWorld(new T.Vector3(0, 0, ben)).sub(o);
    const pole = fwd.multiplyScalar(-1).add(new T.Vector3(0, -.6, 0)).add(ngang.multiplyScalar(.7));
    ik(a.tren, a.khuyu, L.tayTren, L.cangTay + .05, dich, pole);
    a.banTay.rotation.set(0, 0, 0);
  }

  // Apply a pose to a built person. extra.tay overrides hand targets with local points (item frame).
  function apDung(p, tuThe, extra) {
    const q = Object.assign({}, tuThe);
    p.goc.updateMatrixWorld(true);
    p.hong.position.set(q.hongX || 0, q.hongY, 0);
    p.hong.rotation.set(0, 0, 0);
    p.than.rotation.set(0, 0, -(q.nghieng || 0) * R * .55);
    p.nguc.rotation.set(0, 0, -(q.nghieng || 0) * R * .45);
    p.co.rotation.set(0, 0, (q.nghieng || 0) * R * .5);
    p.dau.rotation.set(0, 0, -(q.dauCui || 0) * R);
    p.goc.updateMatrixWorld(true);
    const W = v => p.goc.localToWorld(new T.Vector3(v[0], v[1], v[2]));
    const fwd = p.goc.localToWorld(new T.Vector3(1, 0, 0)).sub(p.goc.localToWorld(new T.Vector3()));
    // Legs: ankle target sits coChan above the sole point.
    for (const ten of ['T', 'P']) {
      const c = p.chan[ten], f = q.chan[ten];
      const pole = fwd.clone().add(new T.Vector3(0, .3, 0));
      let goiDich = null;
      if (q.cuoiGoi && q.cuoiGoi[ten]) goiDich = W(q.cuoiGoi[ten]);
      const ankle = W([f[0], f[1] + L.coChan, f[2]]);
      // Kneeling leg: the knee hint only chooses the bending plane; lengths stay exact.
      if (goiDich) ik(c.khop, c.goi, L.dui, L.cang, ankle, goiDich.clone().sub(c.khop.getWorldPosition(new T.Vector3())));
      else ik(c.khop, c.goi, L.dui, L.cang, ankle, pole);
      // Foot: level (or pitched toe-down) in the item frame.
      const pitch = ((q.gocChan && q.gocChan[ten]) || 0) * R;
      const qW = p.goc.getWorldQuaternion(new T.Quaternion()).multiply(new T.Quaternion().setFromEuler(new T.Euler(0, 0, -pitch)));
      c.goi.getWorldQuaternion(_q);
      c.ban.quaternion.copy(_q.invert().multiply(qW));
    }
    // Arms: IK to targets, else simple swing (deg forward, deg elbow bend).
    for (const ten of ['T', 'P']) {
      const a = p.tay[ten], ben = ten === 'T' ? 1 : -1;
      const dich = (extra && extra.tay && extra.tay[ten]) || (q.tay && q.tay[ten]);
      if (dich) ikTay(p, ten, dich.isVector3 ? dich : W(dich));
      else {
        const [vung, gap] = (q.vungTay && q.vungTay[ten]) || [0, 8];
        a.tren.rotation.set(ben * 6 * R, 0, vung * R);
        a.khuyu.rotation.set(0, 0, gap * R);
      }
    }
    p.goc.updateMatrixWorld(true);
  }

  K.nguoi = { L, CAO_HONG, taoNguoi, TU_THE, apDung, ik, ikTay, huongXuong, chi, cau };
})(typeof window !== 'undefined' ? window : globalThis);
