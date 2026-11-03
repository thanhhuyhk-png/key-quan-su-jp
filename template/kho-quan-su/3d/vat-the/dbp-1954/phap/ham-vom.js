// French dugout with an arched roof (NGUON.tsv: cu-diem; dien-bien-phu.md item 17). De Castries' command post was
// 20 × 8 m, about 2 m deep, roofed with curved steel sheet under many layers of sandbags and heavy timber; only the
// blast wall at the entrance was concrete. This is a generic smaller dugout of the same build: 6 × 4.4 m, steel arch,
// timber layer, sandbags, sandbag entrance with a dark door. No flag, sign or lettering.
// Item frame: +X is the entrance side; base on y = 0 (the scene sinks it into the ground as needed).
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const DAI = 6, BK = 2.0, VAO = 1.6;   // length, arch radius, how long the reinforcing layer takes to land (s)

  function tao(K, op) {
    const goc = H.nhom('ham-vom'), rnd = K.rng(op.hat || 1), cham = new T.Object3D(); goc.add(cham);
    const vom = H.nhom('vom'); goc.add(vom);
    // Corrugated steel arch (seen at the open ends) and the earth/timber mass over it.
    const ton = H.mesh(new T.CylinderGeometry(BK, BK, DAI, 40, 1, true, 0, Math.PI).rotateZ(90 * R), K.vatLieu('thep', '#4a4b45'));
    ton.material = ton.material.clone(); ton.material.side = T.DoubleSide; vom.add(ton);
    for (let i = 0; i < 9; i++) { const go = H.mesh(H.truX(.13, .13, DAI + .4, 8), 'go-toi'); const a = (20 + i * 17.5) * R; go.position.set(0, Math.sin(a) * (BK + .18), Math.cos(a) * (BK + .18)); go.rotation.x = (rnd() - .5) * .1; vom.add(go); }
    // Two layers of sandbags following the arch, bags laid across the slope.
    const bao = [];
    for (const [lop, r0] of [[0, BK + .42], [1, BK + .62]]) {
      for (let i = 0; i <= 12; i++) {
        const a = (8 + i * 13.7) * R;
        for (let x = -DAI / 2 + .18 + lop * .16; x < DAI / 2; x += .33) bao.push([x, Math.sin(a) * r0, Math.cos(a) * r0, 90, 0, 90 - a / R]);
      }
    }
    vom.add(H.baoCat(bao, rnd));
    // Earth berm piled against both long sides.
    for (const s of [-1, 1]) { const be = H.mesh(new T.CylinderGeometry(1.3, 1.3, DAI + .6, 18, 1, false, 0, Math.PI).rotateZ(90 * R).scale(1, .95, 1), 'dat'); be.position.set(0, 0, s * (BK + .55)); vom.add(be); }
    // Entrance: sandbag blast wall in front of a dark door; closed back wall.
    const cua = H.mesh(H.hop(.08, 1.7, 1.0, .02), 'den'); cua.position.set(DAI / 2 + .02, .85, 0); vom.add(cua);
    const tuong = [];
    for (let h = 0; h < 9; h++) for (const z of [-1.9, -1.4, 1.4, 1.9]) tuong.push([DAI / 2 + .25, h * .17, z + (h % 2) * .12, 90]);
    for (let h = 0; h < 11; h++) for (let z = -1.7; z <= 1.71; z += .58) tuong.push([-DAI / 2 - .2, h * .17, z + (h % 2) * .2, 90]);
    vom.add(H.baoCat(tuong, rnd));
    // Reinforcing layer (state gia-co): bags drop one after another onto the crown, then stay.
    const them = [], hThem = [];
    for (let i = 0; i < 18; i++) { const x = -DAI / 2 + .4 + (i % 9) * .62, z = (Math.floor(i / 9) - .5) * .7; them.push([x, 0, z, 90]); hThem.push(BK + .78); }
    const lopThem = H.baoCat(them, rnd); goc.add(lopThem);
    const goc0 = []; const m = new T.Matrix4(); for (let i = 0; i < them.length; i++) { lopThem.getMatrixAt(i, m); goc0.push(m.clone()); }

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0;
      // Collapsed: arch flattened and tilted, bags slumped (shelling).
      vom.scale.set(1, s === 'sap' ? .55 : 1, 1); vom.rotation.set(s === 'sap' ? 6 * R : 0, 0, s === 'sap' ? -3 * R : 0);
      lopThem.visible = s === 'gia-co';
      if (s === 'gia-co') {
        const p = new T.Vector3(), q = new T.Quaternion(), sc = new T.Vector3();
        for (let i = 0; i < them.length; i++) {
          const u = K.smooth((t - i * VAO / them.length) / .35), roi = 1 - u;
          goc0[i].decompose(p, q, sc); p.y += hThem[i] + roi * roi * 2.5;
          lopThem.setMatrixAt(i, m.compose(p, q, sc));
        }
        lopThem.instanceMatrix.needsUpdate = true;
      }
      H.chamThap(goc, cham);
    }
    return { goc, capNhat, diemCham: [cham], neo: {} };
  }

  K.dangKy({ ma: 'ham-vom', ten: 'Hầm vòm bao cát (cứ điểm Pháp)', phe: 'phap', thoiKy: 'dbp-1954', kichThuoc: { dai: 6.9, rong: 5.6 }, trangThai: ['nguyen', 'gia-co', 'sap'], tao });
})(typeof window !== 'undefined' ? window : globalThis);
