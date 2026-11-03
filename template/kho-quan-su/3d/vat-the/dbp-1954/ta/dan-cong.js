// Front-line civilian porter (NGUON.tsv: dan-cong, decision VE TRUNG TINH). No sourced clothing pattern, so plain
// dark civilian clothes. Sourced details only: women wore head scarves (wartime report re-published by Nhan Dan);
// carrying pole with two woven bamboo baskets (bo nan, Thanh Hoa museum reconstruction); a conical hat used to keep
// rain off the rice (Ms La Thi Nhai's hat, Dien Bien Phu exhibition 2024) as a variant. Walked in single file at night.
// Variants: nu (woman: head scarf), nonLa (conical hat), chan 'tran' (default barefoot) | 'dep'.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R, N = K.nguoi;

  function boNan(rnd) {
    const o = H.nhom('bo-nan');
    o.add(H.mesh(H.tien([[0, 0], [.16, 0], [.19, .04], [.2, .3], [.21, .32], [.19, .32], [.185, .05], [.15, .015], [0, .015]], 28), 'tre'));
    const vanh = H.mesh(new T.TorusGeometry(.205, .012, 6, 28).rotateX(90 * R), 'go'); vanh.position.y = .32; o.add(vanh);
    for (const y of [.1, .2]) { const d = H.mesh(new T.TorusGeometry(.199, .006, 4, 28).rotateX(90 * R), 'go'); d.position.y = y; o.add(d); }
    const gao = H.mesh(new T.SphereGeometry(.19, 18, 10, 0, Math.PI * 2, 0, Math.PI / 2).scale(1, .45, 1), 'bao'); gao.position.y = .3; o.add(gao);
    // Four ropes from the rim up to the pole hook.
    for (let i = 0; i < 4; i++) { const a = i / 4 * Math.PI * 2 + .4; o.add(H.thanh([Math.cos(a) * .2, .32, Math.sin(a) * .2], [0, .95, 0], .004, 'day')); }
    const cham = new T.Object3D(); o.add(cham); o.userData.cham = cham;
    return o;
  }
  function nonLa() {
    const o = H.nhom('non-la');
    o.add(H.mesh(H.tien([[0, .36], [.215, .12], [.222, .115], [.0, .3]], 32), 'tre'));
    for (let i = 1; i < 6; i++) { const v = H.mesh(new T.TorusGeometry(.215 * i / 6, .002, 3, 28).rotateX(90 * R), 'go'); v.position.y = .36 - .24 * i / 6; o.add(v); }
    return o;
  }
  function khan() {
    const o = H.nhom('khan');
    const vo = H.mesh(new T.SphereGeometry(1, 24, 14, 0, Math.PI * 2, 0, Math.PI * .62).scale(.1, .12, .095), 'vai-dan'); vo.position.set(-.008, .105, 0); o.add(vo);
    const mo = H.mesh(H.tam([[0, 0], [.07, .02], [0, .05]], .16, .01), 'vai-dan'); mo.position.set(.06, .19, 0); mo.rotation.y = 0; o.add(mo);
    const duoi = H.mesh(H.tam([[0, 0], [-.09, -.06], [-.02, -.1]], .05, .008), 'vai-dan'); duoi.position.set(-.08, .1, 0); o.add(duoi);
    return o;
  }

  function tao(K, op) {
    const p = N.taoNguoi({ vlAo: 'vai-dan', vlQuan: 'vai-den', ao: 'dan-su', chan: op.chan || 'tran' });
    const rnd = K.rng(op.hat || 1), goc = p.goc, neo = {};
    if (op.nonLa) p.dau.add(nonLa()); else if (op.nu) p.dau.add(khan());
    // Carrying pole along the walking direction on the right shoulder, sagging under the load.
    const don = H.nhom('don-ganh'); goc.add(don);
    don.add(H.mesh(H.ong([[-.78, -.03, 0], [-.4, .0, 0], [0, .015, 0], [.4, .0, 0], [.78, -.03, 0]], .02, 24), 'tre'));
    const bo = [boNan(rnd), boNan(rnd)];
    bo.forEach((b, i) => { b.position.set(i ? .76 : -.76, -.98, 0); don.add(b); });
    const diemCham = [];
    for (const ten of ['T', 'P']) diemCham.push(p.chan[ten].gotM, p.chan[ten].muiM);
    bo.forEach(b => diemCham.push(b.userData.cham));
    neo.donTruoc = new T.Object3D(); neo.donTruoc.position.set(.78, -.03, 0); don.add(neo.donTruoc);

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0, nghi = s === 'nghi';
      const pose = nghi ? N.TU_THE.dung(t) : N.TU_THE.di(s === 'leo-doc' ? t * .62 : t * .82);
      pose.nghieng = (pose.nghieng || 0) + (s === 'leo-doc' ? 16 : 6) - (tt.doc || 0) * .85;
      N.apDung(p, pose, null);
      // Pole on the right shoulder; on rest the baskets stand on the ground and the pole stays across the shoulder.
      goc.updateMatrixWorld(true);
      const vai = goc.worldToLocal(p.tay.P.vai.getWorldPosition(new T.Vector3()));
      const lac = nghi ? 0 : Math.sin(t * 2 * Math.PI / .55) * 3.5;
      don.position.set(vai.x, vai.y + .07, vai.z + .02);
      don.rotation.set(0, 0, (nghi ? 0 : -(pose.nghieng || 0) * .25) * R);
      bo.forEach((b, i) => {
        b.rotation.set(0, 0, (lac + (pose.nghieng || 0) * .25) * R);
        b.position.y = nghi ? -vai.y - .07 : -.98;
        b.userData.cham.visible = nghi;
      });
      goc.updateMatrixWorld(true);
      N.ikTay(p, 'P', neo.donTruoc.getWorldPosition(new T.Vector3()).add(new T.Vector3(0, 0, 0)).lerp(don.getWorldPosition(new T.Vector3()), .55));
      if (nghi) N.ikTay(p, 'T', don.localToWorld(new T.Vector3(-.3, .0, .0)));
      goc.updateMatrixWorld(true);
    }
    return { goc, capNhat, diemCham, neo, nguoi: p };
  }

  K.dangKy({
    ma: 'dan-cong', ten: 'Dân công hoả tuyến', phe: 'ta', thoiKy: 'dbp-1954',
    kichThuoc: { cao: 1.6 },
    trangThai: ['ganh', 'leo-doc', 'nghi'],
    tao,
  });
})(typeof window !== 'undefined' ? window : globalThis);
