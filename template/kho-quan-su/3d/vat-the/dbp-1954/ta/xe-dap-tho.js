// Pack bicycle of the porter corps (NGUON.tsv: xe-dap-tho). French-made roadsters (Peugeot, Lincoln; the Vina in
// the national museum has a horizontal top tube). Field modifications: frame reinforced with wood and iron, rear rack;
// a ~1 m bamboo pole lashed to the left handlebar for steering ("tay ngai"); a bamboo pole lashed to the seat post
// rising ~0.5 m above the saddle; two three-legged wooden stools (one to rest the bike, one to chock a wheel downhill).
// Rice sacks hang either side. No brand lettering; nobody rides a loaded bike. Thong Nhat bikes did not exist yet.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const RK = .355;

  function ghe() {
    const o = H.nhom('ghe-ba-chan');
    o.add(H.mesh(H.tru(.13, .13, .03, 3).rotateY(30 * R).translate(0, .38, 0), 'go'));
    for (let i = 0; i < 3; i++) {
      const a = i / 3 * Math.PI * 2;
      o.add(H.thanh([Math.cos(a) * .07, .37, Math.sin(a) * .07], [Math.cos(a) * .15, 0, Math.sin(a) * .15], .016, 'go-toi'));
    }
    return o;
  }
  // Burlap rice sack: a bulging body with a gathered, tied neck.
  function bao(dai, cao, day, rnd) {
    const o = H.nhom('bao-gao');
    const geo = new T.SphereGeometry(1, 28, 18), p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) {
      let x = p.getX(i), y = p.getY(i), z = p.getZ(i);
      const phinh = 1 + .08 * Math.sin(x * 5 + rnd()) * Math.cos(y * 4);
      p.setXYZ(i, x * dai / 2 * phinh, y * cao / 2 * (y < 0 ? .92 : 1), z * day / 2 * (1 - .25 * Math.max(0, y)));
    }
    geo.computeVertexNormals();
    o.add(H.mesh(geo, 'bao'));
    const co = H.mesh(H.tien([[.0, 0], [.04, 0], [.025, .05], [.045, .1], [0, .11]], 12), 'bao'); co.position.set(-dai * .42, cao * .28, 0); co.rotation.z = 50 * R; o.add(co);
    const buoc = H.mesh(new T.TorusGeometry(.03, .006, 5, 14).rotateX(90 * R), 'day'); buoc.position.set(-dai * .42 - .03, cao * .28 + .03, 0); buoc.rotation.z = 50 * R; o.add(buoc);
    return o;
  }
  // Rope lashing: several turns around a point on a pole (axis dir).
  function buoc(diem, truc, r, vong) {
    const o = H.nhom('day-buoc');
    for (let i = 0; i < (vong || 5); i++) {
      const v = H.mesh(new T.TorusGeometry(r, .0045, 5, 16), 'day');
      v.position.set(diem[0] + truc[0] * i * .011, diem[1] + truc[1] * i * .011, diem[2] + truc[2] * i * .011);
      v.quaternion.setFromUnitVectors(new T.Vector3(0, 0, 1), new T.Vector3(...truc).normalize());
      o.add(v);
    }
    return o;
  }
  function tre(a, b, r, vl) {
    const o = H.nhom('tre');
    o.add(H.thanh(a, b, r, vl || 'tre'));
    const va = new T.Vector3(...a), vb = new T.Vector3(...b), n = Math.floor(va.distanceTo(vb) / .28);
    for (let i = 1; i <= n; i++) {
      const p = va.clone().lerp(vb, i / (n + 1)), m = H.mesh(new T.TorusGeometry(r * 1.02, r * .18, 5, 14), 'go');
      m.position.copy(p); m.quaternion.setFromUnitVectors(new T.Vector3(0, 0, 1), vb.clone().sub(va).normalize()); o.add(m);
    }
    return o;
  }

  function tao(K, op) {
    const goc = H.nhom('xe-dap-tho'), rnd = K.rng(op.hat || 1), neo = {}, diemCham = [];
    const xe = H.nhom('xe'); goc.add(xe);
    const P = { truc: [-.56, RK, 0], giua: [-.04, .29, 0], yen: [-.2, .84, 0], coTren: [.4, .86, 0], coDuoi: [.45, .72, 0], trucTruoc: [.56, RK, 0] };
    const ong = (a, b, r) => xe.add(H.thanh(a, b, r || .016, 'son-lx'));
    for (const z of [-1, 1]) {
      ong([P.giua[0], P.giua[1], z * .03], [P.truc[0], P.truc[1], z * .055], .011);
      ong([P.yen[0] + .02, P.yen[1] - .05, z * .02], [P.truc[0], P.truc[1], z * .055], .01);
      ong([P.coDuoi[0] + .01, P.coDuoi[1], z * .03], [P.trucTruoc[0], P.trucTruoc[1], z * .05], .012);
    }
    ong(P.giua, [P.yen[0] + .015, P.yen[1] - .02, 0], .017);
    ong([P.yen[0] + .02, P.yen[1] - .04, 0], [P.coTren[0], P.coTren[1] - .03, 0], .017);
    ong(P.giua, P.coDuoi, .019);
    ong(P.coDuoi, [P.coTren[0] - .01, P.coTren[1] + .03, 0], .022);
    // Handlebar with stem, grips.
    const ghiDong = H.nhom('ghi-dong'); ghiDong.position.set(P.coTren[0] - .02, P.coTren[1] + .1, 0); xe.add(ghiDong);
    ghiDong.add(H.thanh([0, -.1, 0], [0, 0, 0], .013, 'thep-mon'));
    ghiDong.add(H.mesh(H.ong([[-.12, .03, -.29], [-.03, .02, -.18], [.02, 0, 0], [-.03, .02, .18], [-.12, .03, .29]], .011, 24), 'thep-mon'));
    for (const z of [-1, 1]) { const tn = H.mesh(H.truZ(.016, .016, .1, 10).rotateY(-20 * R * z), 'cao-su'); tn.position.set(-.11, .03, z * .26); ghiDong.add(tn); }
    // Saddle on its post, with rails and springs.
    const yen = H.mesh(H.tam([[-.11, 0], [-.1, .035], [.0, .04], [.14, .02], [.16, .005], [.14, -.01], [-.1, -.012]], .16, .01), 'da-that');
    yen.position.set(P.yen[0] - .02, P.yen[1] + .1, 0); yen.scale.z = 1; xe.add(yen);
    xe.add(H.thanh([P.yen[0] + .005, P.yen[1] - .03, 0], [P.yen[0] - .01, P.yen[1] + .09, 0], .012, 'thep-mon'));
    // Wheels, crank, chain, pedals, mudguards.
    const banhSau = H.banhXeDap(RK); banhSau.position.set(...P.truc); xe.add(banhSau);
    const banhTruoc = H.banhXeDap(RK); banhTruoc.position.set(...P.trucTruoc); xe.add(banhTruoc);
    for (const w of [banhSau, banhTruoc]) { const m = new T.Object3D(); m.position.set(0, -RK, 0); m.userData.laBanh = true; xe.add(m); m.position.set(w.position.x, 0, 0); diemCham.push(m); }
    const dia = H.mesh(new T.TorusGeometry(.09, .008, 6, 32), 'thep-mon'); dia.position.set(P.giua[0], P.giua[1], .06); xe.add(dia);
    const dua = H.nhom('dui-dia'); dua.position.set(P.giua[0], P.giua[1], 0); xe.add(dua);
    for (const z of [-1, 1]) {
      const tay = H.mesh(H.hop(.17, .02, .012, .004), 'thep-mon'); tay.position.set(.075 * z, 0, z * .075); dua.add(tay);
      const ban = H.mesh(H.hop(.1, .025, .07, .006), 'cao-su'); ban.position.set(.16 * z, 0, z * .12); dua.add(ban);
    }
    xe.add(H.mesh(H.ong([[P.giua[0], P.giua[1] + .09, .06], [(P.giua[0] + P.truc[0]) / 2, P.truc[1] + .055, .058], [P.truc[0] + .02, P.truc[1] + .04, .056], [P.truc[0] - .035, P.truc[1], .056], [P.truc[0] + .02, P.truc[1] - .04, .056], [(P.giua[0] + P.truc[0]) / 2, P.giua[1] - .02, .058], [P.giua[0], P.giua[1] - .09, .06]], .0045, 40), 'den'));
    for (const [w, s, e] of [[P.truc, 10, 175], [P.trucTruoc, 15, 150]]) {
      const ve = H.mesh(new T.TorusGeometry(RK + .03, .028, 4, 30, (e - s) * R).scale(1, 1, .6), 'son-lx-toi');
      ve.position.set(w[0], w[1], 0); ve.rotation.z = s * R; xe.add(ve);
    }
    // Rear rack (ba ga) and reinforcement: wood battens lashed along the frame.
    const baGa = H.mesh(H.hop(.46, .02, .2, .005), 'thep'); baGa.position.set(P.truc[0] + .05, .74, 0); xe.add(baGa);
    for (const z of [-1, 1]) xe.add(H.thanh([P.truc[0] + .2, .73, z * .09], [P.truc[0], P.truc[1], z * .06], .007, 'thep'));
    xe.add(H.thanh([P.yen[0], .75, 0], [P.truc[0] + .27, .74, 0], .008, 'thep'));
    const nep1 = H.mesh(H.hop(.52, .035, .025, .006), 'go'); nep1.position.set(.1, .84, .03); nep1.rotation.z = 2 * R; xe.add(nep1);
    const nep2 = H.mesh(H.hop(.5, .035, .025, .006), 'go'); nep2.position.set(.2, .51, .035); nep2.rotation.z = 38 * R; xe.add(nep2);
    xe.add(buoc([-.06, .84, .02], [1, .035, 0], .03, 5)); xe.add(buoc([.3, .855, .02], [1, .035, 0], .03, 5));
    xe.add(buoc([.13, .45, .03], [.79, .62, 0], .032, 4));
    // Bamboo steering pole on the left grip, running back along the load; bamboo pole on the seat post.
    const goTay = [P.coTren[0] - .14, P.coTren[1] + .13, .27], cuoiTay = [-.52, 1.0, .5];
    xe.add(tre(goTay, cuoiTay, .022));
    xe.add(buoc([goTay[0] + .01, goTay[1], goTay[2]], [-.93, .14, .23], .026, 6));
    const tayNgai = new T.Object3D(); tayNgai.position.set(...cuoiTay); xe.add(tayNgai); neo.tayNgai = tayNgai;
    const goYen = [P.yen[0] + .02, .55, -.03], dinhYen = [P.yen[0] - .08, P.yen[1] + .1 + .5, -.03];
    xe.add(tre(goYen, dinhYen, .024));
    xe.add(buoc([P.yen[0] + .015, .68, -.03], [-.15, 1, 0], .03, 5));
    const treYen = new T.Object3D(); treYen.position.set(...dinhYen); xe.add(treYen); neo.treYen = treYen;
    const dayTruoc = new T.Object3D(); dayTruoc.position.set(P.coTren[0] + .03, P.coTren[1] + .08, 0); xe.add(dayTruoc); neo.dayTruoc = dayTruoc;
    xe.add(buoc([P.coTren[0], P.coTren[1] + .03, 0], [0, 1, 0], .03, 3));
    // Load: rice sacks either side of the frame, one across the rack; stools lashed on top.
    const tai = H.nhom('tai'); xe.add(tai);
    for (const z of [-1, 1]) {
      const b1 = bao(.62, .42, .2, rnd); b1.position.set(-.1, .55, z * .18); b1.rotation.set(z * 8 * R, 0, -4 * R); tai.add(b1);
      const b2 = bao(.5, .36, .18, rnd); b2.position.set(-.5, .6, z * .17); b2.rotation.set(z * 10 * R, 0, 6 * R); tai.add(b2);
    }
    const b3 = bao(.5, .22, .34, rnd); b3.position.set(-.38, .88, 0); b3.rotation.y = 90 * R; tai.add(b3);
    for (const z of [-1, 1]) tai.add(H.mesh(H.ong([[-.1, .86, z * .02], [-.12, .8, z * .2], [-.1, .45, z * .28]], .006, 14), 'day'));
    const gheNghi = ghe(), gheChen = ghe();
    // Spare stool carried upside down on the rack load.
    const gheTren = ghe(); gheTren.position.set(-.42, 1.4, 0); gheTren.rotation.set(Math.PI, 0, 0); tai.add(gheTren);
    gheNghi.position.set(-.08, 0, .24); goc.add(gheNghi);
    gheChen.position.set(P.trucTruoc[0] + RK + .14, 0, 0); goc.add(gheChen);
    for (const gh of [gheNghi, gheChen]) { const m = new T.Object3D(); gh.add(m); m.userData.ghe = gh; diemCham.push(m); }

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0;
      const toc = s === 'dat' ? .8 : s === 'len-doc' ? .35 : s === 'xuong-doc' ? .3 : 0;
      const quang = toc * t;
      banhSau.rotation.z = banhTruoc.rotation.z = -quang / RK;
      dua.rotation.z = -quang / RK * .45;
      gheNghi.visible = s === 'nghi';
      gheChen.visible = s === 'xuong-doc';
      gheTren.visible = s !== 'nghi';
      // Resting: the bike leans a few degrees onto the stool under the top tube.
      xe.rotation.x = s === 'nghi' ? 7 * R : 0;
      diemCham.forEach(o => { if (o.userData.ghe) o.visible = o.userData.ghe.visible; });
    }
    return { goc, capNhat, diemCham, neo, banKinhBanh: RK };
  }

  K.dangKy({
    ma: 'xe-dap-tho', ten: 'Xe đạp thồ', phe: 'ta', thoiKy: 'dbp-1954',
    kichThuoc: { dai: 1.85, banh: .71 },
    trangThai: ['dat', 'len-doc', 'xuong-doc', 'nghi'],
    tao,
  });
})(typeof window !== 'undefined' ? window : globalThis);
