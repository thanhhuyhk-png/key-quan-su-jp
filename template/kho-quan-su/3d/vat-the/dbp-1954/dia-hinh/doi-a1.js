// Hill A1 (Éliane 2) with the sapping tunnel, for cut-away shots (so-so-lieu.csv rows 13 and 21). Sourced and drawn:
// tunnel dug from the night of 20/4/1954 for 15 days and nights, reaching right under the enemy's strongpoint bunker;
// a charge of 960 kg (nearly one tonne) in packets stacked at the tunnel end; fired 20:30 on 6/5/1954. NOT drawn as a
// claim: tunnel length (sources say 47, 49 or 82 m), entrance position, packet count. Tunnel bore ~0.9 m (one source)
// is drawn as "one man crawling". Hill about 30 m high (one source) at a believable scale; shape is illustrative.
// op.catLop (default true): only the far half (z <= 0) is built and the cut face at z = 0 shows soil strata, tunnel
// and bunker. States: tunnel only, charge in place, detonation (t from 0: glow, heave, crater).
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const DAI = 150, SAU = 90, NEN = 2, CAO = 30;
  const DINH = [6, 0], HAM_Y = NEN + CAO - 3.2, CUOI = [4, HAM_Y - 3.5], CUA = [-22, 0];

  const goc0 = (x, z) => NEN + CAO * Math.exp(-(Math.pow((x - DINH[0]) / 34, 2) + Math.pow((z - DINH[1]) / 28, 2)) * 1.15) + .6 * Math.sin(x * .21 + z * .17) * Math.cos(z * .13);
  // Detonation: heave the crown above the charge, then leave a crater (t in seconds after firing).
  function caoDo(x, z, no, t) {
    let y = goc0(x, z);
    if (!no || t <= 0) return y;
    const d = Math.hypot(x - CUOI[0], z), k = Math.exp(-Math.pow(d / 11, 2));
    const phong = 7 * K.smooth(t / .35) * (1 - K.smooth((t - .45) / .6)), ho = 5.5 * K.smooth((t - .4) / .8);
    return y + (phong - ho) * k;
  }
  const yCua = () => goc0(CUA[0], 0) - .2;

  function tao(K, op) {
    const catLop = op.catLop !== false, rnd = K.rng(op.hat || 1);
    const goc = H.nhom('doi-a1'), cham = new T.Object3D(); goc.add(cham);
    // Ground surface: bare shelled earth (hills were cleared), darker scars, sparse dry grass.
    const sz = catLop ? SAU / 2 : SAU, mat = new T.PlaneGeometry(DAI, sz, 150, catLop ? 45 : 90).rotateX(-90 * R).translate(0, 0, catLop ? -sz / 2 : 0);
    // Shell craters scattered at random (seeded), denser on the crown that was fought over.
    const ho = Array.from({ length: 220 }, () => { const x = (rnd() - .5) * DAI * .9, z = catLop ? -rnd() * sz : (rnd() - .5) * sz; return [x, z, 1 + rnd() * 2.5 * (1 + 2 * Math.exp(-Math.pow((x - DINH[0]) / 30, 2)))]; });
    // Relief carried by the mesh and by the exported caoDo: crater bowls with a raised lip, two-scale roughness.
    const gho = (x, z) => {
      let y = .35 * Math.sin(x * .9 + z * .4) * Math.cos(z * .8 - x * .3) + .18 * Math.sin(x * 2.3 - z * 1.7);
      for (const [hx, hz, hr] of ho) { const d = Math.hypot(x - hx, z - hz) / hr; if (d < 1.4) y += d < 1 ? -.35 * hr * (1 - d * d) : .1 * hr * Math.sin((d - 1) / .4 * Math.PI); }
      return y;
    };
    // Red-brown laterite (the soil of the Dien Bien Phu hills), darker in craters, a little grass low down.
    const mp = mat.attributes.position, mau = [], c1 = new T.Color('#5a3f2a'), c2 = new T.Color('#6f4e33'), c3 = new T.Color('#465230'), c4 = new T.Color('#2e231b');
    const ghoV = new Float32Array(mp.count); for (let i = 0; i < mp.count; i++) ghoV[i] = gho(mp.getX(i), mp.getZ(i));
    for (let i = 0; i < mp.count; i++) {
      const x = mp.getX(i), z = mp.getZ(i), n = .5 + .5 * Math.sin(x * .37 + z * .53) * Math.cos(x * .11 - z * .29);
      let hoDan = 0; for (const [hx, hz, hr] of ho) { const d = Math.hypot(x - hx, z - hz); if (d < hr) hoDan = Math.max(hoDan, 1 - d / hr); }
      const c = c1.clone().lerp(c2, n * .6).lerp(c3, Math.max(0, .45 - goc0(x, z) / CAO) * .7).lerp(c4, Math.min(1, hoDan * .9));
      mau.push(c.r, c.g, c.b);
    }
    mat.setAttribute('color', new T.Float32BufferAttribute(mau, 3));
    const be = H.mesh(mat, new T.MeshStandardMaterial({ vertexColors: true, roughness: .98 }), { bong: false }); goc.add(be);
    // Cut face at z = 0: strata bands under the surface line.
    const tang = ['#7a5f3e', '#8f7048', '#a3855c', '#7b5d3f', '#94785a', '#665038'];
    const cot = 150, hang = 30, mc = new T.BufferGeometry();
    { const pos = [], col = [], idx = [];
      for (let i = 0; i <= cot; i++) for (let j = 0; j <= hang; j++) {
        const x = -DAI / 2 + i / cot * DAI, top = goc0(x, 0), y = top * (1 - j / hang);
        pos.push(x, y, 0);
        const d = top - y + Math.sin(x * .4) * .6, band = Math.min(tang.length - 1, Math.floor(d / 4.2)), cc = new T.Color(tang[band]).multiplyScalar(.9 + .14 * Math.sin(x * 3 + j));
        col.push(cc.r, cc.g, cc.b);
      }
      for (let i = 0; i < cot; i++) for (let j = 0; j < hang; j++) { const a = i * (hang + 1) + j, b = a + hang + 1; idx.push(a, a + 1, b, b, a + 1, b + 1); }
      mc.setAttribute('position', new T.Float32BufferAttribute(pos, 3)); mc.setAttribute('color', new T.Float32BufferAttribute(col, 3)); mc.setIndex(idx); mc.computeVertexNormals(); }
    const matCat = H.mesh(mc, new T.MeshStandardMaterial({ vertexColors: true, roughness: 1, side: T.DoubleSide }), { bong: false });
    matCat.visible = catLop; goc.add(matCat);
    // Tunnel on the cut face: a dark bore from the entrance on the near hillside to just under the bunker, with
    // timber frames; its line climbs gently into the hill.
    const ham = H.nhom('duong-ham'); ham.visible = catLop; goc.add(ham);
    const a = new T.Vector3(CUA[0], yCua(), .02), b = new T.Vector3(CUOI[0], CUOI[1], .02), dai = a.distanceTo(b);
    const long = H.mesh(H.hop(dai, .9, .04, .01), 'den', { bong: false }); long.position.copy(a).add(b).multiplyScalar(.5); long.rotation.z = Math.atan2(b.y - a.y, b.x - a.x); ham.add(long);
    for (let s = .6; s < dai; s += 1.4) {
      const p = a.clone().lerp(b, s / dai), khung = H.nhom(); khung.position.copy(p); khung.rotation.z = long.rotation.z; ham.add(khung);
      for (const dy of [-.48, .48]) { const go = H.mesh(H.hop(.1, .07, .05, .01), 'go'); go.position.y = dy; khung.add(go); }
      for (const dx of [-.05]) { const go = H.mesh(H.hop(.07, .96, .05, .01), 'go'); go.position.x = dx; khung.add(go); }
    }
    // Strongpoint bunker on the crown (cut through), roof of logs and earth: a dark chamber in the cut face.
    const hcThu = H.nhom('ham-co-thu'); hcThu.visible = catLop; goc.add(hcThu);
    const phong = H.mesh(H.hop(9, 2.6, .05, .02), 'den', { bong: false }); phong.position.set(CUOI[0], HAM_Y + 1.3, .03); hcThu.add(phong);
    for (let i = 0; i < 10; i++) { const go = H.mesh(H.hop(.2, .2, .06, .02), 'go-toi'); go.position.set(CUOI[0] - 4.5 + i * 1, HAM_Y + 2.7, .05); hcThu.add(go); }
    // Charge: packets stacked at the tunnel end (count not shown as a number).
    const khoi = H.nhom('khoi-boc-pha'); khoi.position.set(CUOI[0] + .2, CUOI[1] - .35, .06); khoi.rotation.z = long.rotation.z; goc.add(khoi);
    const goi = []; for (let x = 0; x < 6; x++) for (let y = 0; y < 3; y++) goi.push([-x * .26, y * .2, 0]);
    const g2 = new T.InstancedMesh(H.hop(.24, .18, .04, .02), K.vatLieu('vai-quan', '#4b4a32'), goi.length), m = new T.Matrix4();
    goi.forEach((p, i) => g2.setMatrixAt(i, m.compose(new T.Vector3(p[0], p[1] + .09, 0), new T.Quaternion(), new T.Vector3(1, 1, 1))));
    khoi.add(g2);
    // Detonation glow inside the hill (unlit, fades), and a light.
    // Soft additive glow quad facing the camera (H.hat), so it reads as light through the cut face, not a solid ball.
    const qh = H.hat(3, 'lua', '#ffa040'), quang = qh.nhom; quang.position.set(CUOI[0], CUOI[1], .5); goc.add(quang);
    const den = new T.PointLight(0xffa050, 0, 80, 1.5); den.position.set(CUOI[0], CUOI[1] + 4, 6); goc.add(den);
    const neo = { cuaHam: new T.Object3D(), cuoiHam: new T.Object3D(), dinh: new T.Object3D() };
    neo.cuaHam.position.copy(a); neo.cuoiHam.position.copy(b); neo.dinh.position.set(CUOI[0], goc0(CUOI[0], 0), 0);
    Object.values(neo).forEach(o => goc.add(o));

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0, no = s === 'no';
      for (let i = 0; i < mp.count; i++) mp.setY(i, caoDo(mp.getX(i), mp.getZ(i), no, t) + ghoV[i]);
      mp.needsUpdate = true; mat.computeVertexNormals();
      const cp = mc.attributes.position;
      for (let i = 0; i <= cot; i++) { const x = -DAI / 2 + i / cot * DAI, top = caoDo(x, 0, no, t) + gho(x, 0); for (let j = 0; j <= hang; j++) cp.setY(i * (hang + 1) + j, top * (1 - j / hang)); }
      cp.needsUpdate = true; mc.computeVertexNormals();
      khoi.visible = s === 'boc-pha' || (no && t <= 0);
      const sang = no && t > 0 ? Math.max(0, 1 - K.smooth((t - .25) / .9)) : 0;
      quang.visible = sang > 0;
      qh.ds.forEach((p, i) => { const sc = (4 + 14 * K.smooth(t / .3)) * (1 - i * .25); p.scale.set(sc, sc, 1); p.position.set(0, i * .8, 0); p.material.opacity = sang * (.9 - i * .2); });
      den.intensity = 60 * sang;
      hcThu.visible = catLop && !(no && t > .4);
      H.chamThap(goc, cham);
    }
    return { goc, capNhat, diemCham: [cham], neo, caoDo: (x, z, tt) => caoDo(x, z, tt && tt.trangThai === 'no', tt ? tt.t || 0 : 0) + gho(x, z) };
  }

  K.dangKy({ ma: 'doi-a1', ten: 'Đồi A1 cắt lớp (đường hầm, khối bộc phá)', phe: 'ta', thoiKy: 'dbp-1954', kichThuoc: { dai: DAI, cao: NEN + CAO }, trangThai: ['ham', 'boc-pha', 'no'], tao });
})(typeof window !== 'undefined' ? window : globalThis);
