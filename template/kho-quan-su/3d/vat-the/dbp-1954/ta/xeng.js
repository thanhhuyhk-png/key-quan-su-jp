// Long-handled digging spade (dien-bien-phu.md item 8: "mỗi người cuốc, xẻng"), for close shots of trench digging
// without hands in frame. Blade 0.22 × 0.28 m, wooden shaft 1.2 m. A small earth heap is part of the item so the
// buried blade tip never goes below ground. States: lying, stuck in the ground, throwing a spadeful (t, 1.4 s cycle).
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const CHU_KY = 1.4;

  function tao(K, op) {
    const rnd = K.rng(op.hat || 1), goc = H.nhom('xeng'), cham = new T.Object3D(); goc.add(cham);
    const ui = H.mesh(new T.SphereGeometry(.5, 20, 8, 0, Math.PI * 2, 0, Math.PI / 2).scale(1, .45, .8), 'dat-do'); goc.add(ui);
    const xeng = H.nhom('xeng-cam'); goc.add(xeng);
    // Blade: slightly dished plate, point down along -Y; shaft up along +Y from the socket.
    const lg = H.tam([[-.11, .28], [.11, .28], [.11, .06], [0, -.02], [-.11, .06]], .006, .002), lp = lg.attributes.position;
    for (let i = 0; i < lp.count; i++) lp.setZ(i, lp.getZ(i) + .04 * Math.pow(lp.getX(i) / .11, 2));
    lg.computeVertexNormals();
    const luoi = H.mesh(lg, 'thep'); xeng.add(luoi);
    xeng.add(H.thanh([0, .26, .02], [0, .4, .02], .022, 'thep'));
    xeng.add(H.thanh([0, .38, .02], [0, 1.5, .02], .018, 'go'));
    // Spadeful of earth riding on the blade, then flying off as clods.
    const nam = H.mesh(new T.DodecahedronGeometry(.1, 1).scale(1, .55, .8), 'dat-do'); nam.position.set(0, .16, .07); xeng.add(nam);
    const n = 9, cuc = new T.InstancedMesh(new T.DodecahedronGeometry(.045, 0), K.vatLieu('dat-do'), n), v = [];
    for (let i = 0; i < n; i++) v.push([(rnd() - .3) * 1.4, 2.2 + rnd() * 1.2, (rnd() - .5) * .8]);
    cuc.castShadow = true; goc.add(cuc); cuc.userData.boQuaKhung = true;

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0, m = new T.Matrix4();
      nam.visible = false; cuc.visible = false; ui.visible = s !== 'nam';
      if (s === 'nam') { xeng.position.set(-.7, .025, 0); xeng.rotation.set(0, 0, 90 * R); xeng.rotation.x = 90 * R; }
      else if (s === 'cam-dat') { xeng.position.set(0, .05, 0); xeng.rotation.set(0, 0, -14 * R); }
      else {
        // Cut (down into the heap), lever back, lift and throw forward; a pure function of the cycle phase.
        const u = ((t / CHU_KY) % 1 + 1) % 1;
        const cat = u < .3 ? K.smooth(u / .3) : 1, nang = u < .3 ? 0 : K.smooth((u - .3) / .4), nem = u < .7 ? 0 : K.smooth((u - .7) / .15);
        xeng.position.set(-.1 + nang * .25, .05 + (1 - cat) * .3 + nang * .7, 0);
        xeng.rotation.set(0, 0, (-14 + nang * -40 + nem * 70) * R);
        nam.visible = u > .3 && u < .78;
        const tt0 = u >= .76 ? (u - .76) * CHU_KY : -1;
        cuc.visible = tt0 >= 0;
        const p0 = new T.Vector3(.35, .95, 0);
        for (let i = 0; i < n; i++) {
          const p = p0.clone().add(new T.Vector3(v[i][0] * tt0, v[i][1] * tt0 - 4.9 * tt0 * tt0, v[i][2] * tt0));
          p.y = Math.max(.03, p.y);
          cuc.setMatrixAt(i, m.compose(p, new T.Quaternion().setFromEuler(new T.Euler(i, tt0 * 6, i * 2)), new T.Vector3(1, 1, 1)));
        }
        cuc.instanceMatrix.needsUpdate = true;
      }
      H.chamThap(goc, cham);
    }
    return { goc, capNhat, diemCham: [cham], neo: {} };
  }

  K.dangKy({ ma: 'xeng', ten: 'Xẻng đào hào', phe: 'ta', thoiKy: 'dbp-1954', kichThuoc: { dai: 1.5 }, trangThai: ['nam', 'cam-dat', 'hat-dat'], tao });
})(typeof window !== 'undefined' ? window : globalThis);
