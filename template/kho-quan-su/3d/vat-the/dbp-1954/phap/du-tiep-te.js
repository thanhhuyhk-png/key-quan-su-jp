// Supply parachute with a load (NGUON.tsv: du; dien-bien-phu.md item 14): round canopies in many colours (General
// Giap's memoir: "thousands of brightly coloured parachutes"); colour is NOT tied to the cargo type (that table has no
// source). Load is a wooden crate. Canopy about 7 m across, rigging lines about 6 m.
// Item frame: crate bottom on y = 0, canopy above. States: opening (t), falling (sways with t), collapsed on the ground.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const MAU = ['#e8e4d8', '#3f6aa8', '#b8352f', '#d9782c', '#7a5a3a', '#c9b24a', '#5a7a4a'];
  const BK = 3.5, DAY = 6.2;

  function tao(K, op) {
    const rnd = K.rng(op.hat || 1), mau = op.mau || MAU[Math.floor(rnd() * MAU.length)];
    const goc = H.nhom('du'), cham = new T.Object3D(); goc.add(cham);
    const hom = H.mesh(H.hop(1.1, 1.0, 1.1, .03), 'go'); hom.position.y = .5; goc.add(hom);
    for (const y of [.15, .85]) { const dai = H.mesh(H.hop(1.14, .06, 1.14, .01), 'day'); dai.position.y = y; goc.add(dai); }
    // Canopy and rigging hang from one pivot at the crate top, so the sway swings the whole canopy.
    const treo = H.nhom('treo'); treo.position.y = 1.0; goc.add(treo);
    const tan = H.nhom('tan'); treo.add(tan);
    // Canopy: shallow dome with 16 scalloped gores; vent hole at the apex.
    const geo = new T.SphereGeometry(BK, 32, 10, 0, Math.PI * 2, .12, 1.25), p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i), a = Math.atan2(z, x), k = 1 - .05 * Math.pow(Math.abs(Math.cos(a * 8)), 2); p.setX(i, x * k); p.setZ(i, z * k); }
    geo.computeVertexNormals();
    const vl = K.vatLieu('vai-quan', mau).clone(); vl.side = T.DoubleSide;
    const vom = H.mesh(geo, vl); vom.scale.set(1, .6, 1); tan.add(vom);
    const mieng = BK * Math.sin(1.37), yMieng = BK * Math.cos(1.37) * .6;
    const day = [];
    for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2; day.push(H.thanh([0, 0, 0], [Math.cos(a) * mieng, DAY + yMieng, Math.sin(a) * mieng], .006, 'day')); }
    const nhomDay = H.nhom('day'); day.forEach(d => nhomDay.add(d)); treo.add(nhomDay);
    // Collapsed canopy: a flat crumpled sheet lying downwind of the crate.
    const xep = H.mesh(new T.CircleGeometry(BK * .8, 24).rotateX(-90 * R), vl, { bong: false }); xep.position.set(-BK * .9, .02, .3); goc.add(xep);
    const xp = xep.geometry.attributes.position; for (let i = 0; i < xp.count; i++) xp.setY(i, .02 + .12 * Math.abs(Math.sin(xp.getX(i) * 2.1 + xp.getZ(i) * 1.7)));
    xep.geometry.computeVertexNormals();

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0;
      const bung = s === 'mo' ? K.smooth(t / 1.4) : 1;
      tan.visible = s !== 'nam-dat'; nhomDay.visible = s !== 'nam-dat'; xep.visible = s === 'nam-dat';
      // Sway: canopy swings about the crate (pendulum, 3.2 s period, a few degrees).
      const lac = s === 'roi' ? 5 * Math.sin(t * 2 * Math.PI / 3.2) : 0;
      tan.position.set(0, DAY * (.55 + .45 * bung), 0);
      tan.scale.set(.25 + .75 * bung, .6 + .4 * bung, .25 + .75 * bung);
      nhomDay.scale.set(.25 + .75 * bung, .55 + .45 * bung, .25 + .75 * bung);
      treo.rotation.set(0, 0, lac * R);
      H.chamThap(goc, cham);
    }
    return { goc, capNhat, diemCham: [cham], neo: { hom } };
  }

  K.dangKy({ ma: 'du', ten: 'Dù tiếp tế', phe: 'phap', thoiKy: 'dbp-1954', kichThuoc: { rong: 7 }, trangThai: ['mo', 'roi', 'nam-dat'], tao });
})(typeof window !== 'undefined' ? window : globalThis);
