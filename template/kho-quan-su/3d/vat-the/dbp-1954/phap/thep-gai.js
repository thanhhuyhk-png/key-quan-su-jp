// Concertina barbed wire around French strongpoints (NGUON.tsv: cu-diem; dien-bien-phu.md item 17: belts of wire
// several layers deep, mined). One coil 0.9 m high on U-pickets, along +X from x = 0. States: packed coil, coil
// unrolling over t (2 s to 10 m), and a belt with a breach blown through it (assault lanes at Him Lam).
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const BK = .45, VONG = 40, L0 = 1.2, DAI = 10, BUNG = 2;

  function cuon(rnd) {
    // Helix of VONG loops over L0 m (built packed, stretched along X by the state).
    const o = H.nhom('cuon'), diem = [];
    for (let i = 0; i <= VONG * 18; i++) { const a = i / 18 * Math.PI * 2, x = i / (VONG * 18) * L0; diem.push([x, BK + Math.sin(a) * BK * (1 + .04 * Math.sin(i * .7)), Math.cos(a) * BK]); }
    o.add(H.mesh(H.ong(diem, .0035, VONG * 36), 'thep-mon', { bong: true }));
    // Barbs: small crossed bars every few centimetres along the wire.
    const n = VONG * 9, gai = new T.InstancedMesh(H.hop(.05, .006, .006, .001), K.vatLieu('thep-mon'), n * 2), m = new T.Matrix4(), q = new T.Quaternion(), e = new T.Euler();
    for (let i = 0; i < n; i++) {
      const p = diem[Math.floor(i / n * (diem.length - 1))];
      for (let k = 0; k < 2; k++) { e.set(rnd() * 3, rnd() * 3, k * 1.57); q.setFromEuler(e); gai.setMatrixAt(i * 2 + k, m.compose(new T.Vector3(...p), q, new T.Vector3(1, 1, 1))); }
    }
    gai.castShadow = true; o.add(gai);
    return o;
  }
  function coc() {
    const o = H.nhom('coc');
    o.add(H.mesh(H.hop(.04, 1.15, .06, .006), 'thep')); o.children[0].position.y = .575;
    return o;
  }

  function tao(K, op) {
    const goc = H.nhom('thep-gai'), rnd = K.rng(op.hat || 1), cham = new T.Object3D(); goc.add(cham);
    const a = cuon(rnd), b = cuon(K.rng((op.hat || 1) + 7)); goc.add(a); goc.add(b);
    const cocs = []; for (let i = 0; i < 6; i++) { const c = coc(); goc.add(c); cocs.push(c); }

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0;
      const dai = s === 'cuon' ? L0 : s === 'bung' ? K.lerp(L0, DAI, K.smooth(t / BUNG)) : DAI;
      if (s !== 'dut') {
        a.visible = true; b.visible = false; b.position.set(0, 0, 0); b.rotation.set(0, 0, 0); b.scale.set(1, 1, 1);
        a.position.set(0, 0, 0); a.rotation.set(0, 0, 0); a.scale.set(dai / L0, 1, 1);
        cocs.forEach((c, i) => { c.visible = i < Math.max(1, Math.floor(dai / 2.2) + 1); c.position.set(i * 2.2, 0, 0); });
      } else {
        // Breach 1.6 m wide in the middle; cut ends sag to the ground and spring back towards the pickets.
        const nua = (DAI - 1.6) / 2;
        b.visible = true;
        a.scale.set(nua / L0, .82, 1); a.position.set(0, 0, 0); a.rotation.set(0, 0, -3 * R);
        b.scale.set(nua / L0, .82, 1); b.position.set(nua + 1.6, 0, 0); b.rotation.set(0, 0, 3 * R);
        cocs.forEach((c, i) => { c.visible = true; c.position.set(i < 3 ? i * 2.0 : nua + 1.6 + (i - 3) * 2.0 + .8, 0, 0); });
      }
      H.chamThap(goc, cham);
    }
    return { goc, capNhat, diemCham: [cham], neo: {} };
  }

  K.dangKy({ ma: 'thep-gai', ten: 'Dây thép gai cuộn (cứ điểm Pháp)', phe: 'phap', thoiKy: 'dbp-1954', kichThuoc: { dai: 10, cao: .9 }, trangThai: ['cuon', 'bung', 'dut'], tao });
})(typeof window !== 'undefined' ? window : globalThis);
