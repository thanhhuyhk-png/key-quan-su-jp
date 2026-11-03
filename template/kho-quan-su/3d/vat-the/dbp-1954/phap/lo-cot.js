// French field blockhouse (NGUON.tsv: cu-diem; dien-bien-phu.md item 17): timber frame and sandbags, half dug in,
// a narrow firing slit, roof of logs under sandbags; hills around it cleared to bare earth. Generic, no markings.
// Item frame: +X is the firing slit side; base on y = 0. States: intact, burning (after the opening barrage), wrecked.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const W = 3.2, CAO = 1.7;

  function tao(K, op) {
    const goc = H.nhom('lo-cot'), rnd = K.rng(op.hat || 1), cham = new T.Object3D(); goc.add(cham);
    const than = H.nhom('than'); goc.add(than);
    // Four sandbag walls, bond offset per course; a gap in the front wall makes the slit.
    const bao = [];
    for (let h = 0; h < 10; h++) {
      const y = h * .17, lech = (h % 2) * .28;
      for (let x = -W / 2 + .1 + lech; x <= W / 2; x += .56) { bao.push([x, y, W / 2, 0]); bao.push([x, y, -W / 2, 0]); }
      for (let z = -W / 2 + .3 + lech; z <= W / 2 - .2; z += .56) {
        bao.push([-W / 2, y, z, 90]);
        if (!(h >= 6 && h <= 7 && Math.abs(z) < 1.0)) bao.push([W / 2, y, z, 90]);
      }
    }
    than.add(H.baoCat(bao, rnd));
    const khe = H.mesh(H.hop(.1, .3, 1.7, .01), 'den'); khe.position.set(W / 2 - .02, 1.15, 0); than.add(khe);
    // Roof: logs across, then a layer of bags.
    const mai = H.nhom('mai'); mai.position.y = CAO; than.add(mai);
    for (let i = 0; i < 12; i++) { const go = H.mesh(H.truZ(.12, .12, W + .6, 8), 'go-toi'); go.position.set(-W / 2 - .1 + i * .3, .1, 0); go.rotation.y = (rnd() - .5) * .08; mai.add(go); }
    const baoMai = []; for (let x = -W / 2; x <= W / 2; x += .58) for (let z = -W / 2 + .1; z <= W / 2; z += .34) baoMai.push([x, .22, z, 0]);
    mai.add(H.baoCat(baoMai, rnd));
    // Earth heaped around the lower half (the dug-in part).
    const dg = new T.CylinderGeometry(W * .7, W * .98, .8, 28, 3, true), dp = dg.attributes.position;
    for (let i = 0; i < dp.count; i++) { const x = dp.getX(i), z = dp.getZ(i), k = 1 + .08 * Math.sin(Math.atan2(z, x) * 5 + 1.3) + .05 * Math.sin(Math.atan2(z, x) * 11); dp.setX(i, x * k); dp.setZ(i, z * k); }
    dg.computeVertexNormals();
    const dat = H.mesh(dg, 'dat'); dat.position.y = .4; dat.material = dat.material.clone(); dat.material.side = T.DoubleSide; goc.add(dat);
    // Fire inside the slit and on the roof (pure function of t).
    const lua = H.nhom('lua'); goc.add(lua);
    const ngon = H.lua(rnd, { r: 1.0, cao: 2.4, n: 22, khoi: 10 }); ngon.position.y = CAO + .35; lua.add(ngon);
    const mSang = new T.MeshBasicMaterial({ color: 0xffb35a, transparent: true, opacity: .9, depthWrite: false, blending: T.AdditiveBlending });
    const sang = new T.Mesh(H.hop(.12, .25, 1.5, .01), mSang); sang.position.set(W / 2 + .02, 1.15, 0); lua.add(sang);
    const den = new T.PointLight(0xff9a40, 0, 16, 1.6); den.position.set(0, CAO + 1, 0); lua.add(den);
    lua.traverse(o => { o.castShadow = false; o.userData.boQuaKhung = true; });

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0;
      lua.visible = s === 'chay';
      ngon.userData.capNhat(t, 1); mSang.opacity = .75 + .2 * Math.sin(t * 17);
      den.intensity = s === 'chay' ? 5 * (1 + .2 * Math.sin(t * 23)) : 0;
      // Wrecked: roof caved in on one side, front wall slumped.
      mai.rotation.set(s === 'sap' ? 14 * R : 0, 0, s === 'sap' ? -9 * R : 0); mai.position.y = s === 'sap' ? CAO - .55 : CAO;
      than.scale.set(1, s === 'sap' ? .8 : 1, 1);
      H.chamThap(goc, cham);
    }
    return { goc, capNhat, diemCham: [cham], neo: {} };
  }

  K.dangKy({ ma: 'lo-cot', ten: 'Lô cốt bao cát (cứ điểm Pháp)', phe: 'phap', thoiKy: 'dbp-1954', kichThuoc: { dai: 3.8, rong: 3.8 }, trangThai: ['nguyen', 'chay', 'sap'], tao });
})(typeof window !== 'undefined' ? window : globalThis);
