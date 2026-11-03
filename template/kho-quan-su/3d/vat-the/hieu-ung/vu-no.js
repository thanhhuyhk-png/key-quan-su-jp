// Explosion effects, all a pure function of t (seconds after detonation; nothing shows before 0):
//   'dat'     ground burst of a shell: flash, an earth-and-smoke column about 8 m high that forms in ~0.2 s, a dust
//             skirt along the ground, ballistic clods;
//   'cao-xa'  anti-aircraft burst in the air: flash then a black puff that spreads and drifts;
//   'boc-pha' the big charge under hill A1: an earth-and-fire column about 40 m high, heavy smoke.
// op.co scales the whole effect. Particles are soft camera-facing quads (H.hat) and skip size checks; a scorch disc
// (or a tiny core in the air) keeps ground contact.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;
  const KIEU = {
    dat:      { lua: 18, khoi: 46, vay: 26, dat: 40, cao: 8, toa: 3.2, song: 3.0, lanh: .45, mauKhoi: '#4f4538', den: 30 },
    'cao-xa': { lua: 10, khoi: 18, vay: 0, dat: 0, cao: 1.6, toa: 2.4, song: 3.4, lanh: .3, mauKhoi: '#1b1a19', den: 14 },
    'boc-pha':{ lua: 44, khoi: 90, vay: 40, dat: 150, cao: 40, toa: 12, song: 6, lanh: 1.6, mauKhoi: '#3e352c', den: 160 },
  };

  function tao(K, op) {
    const rnd = K.rng(op.hat || 1), co = op.co || 1;
    const goc = H.nhom('vu-no'), cham = new T.Object3D(); goc.add(cham);
    // Scorched ground: a soft-edged dark stain (the soft particle texture laid flat), not a crisp hole.
    const nen = H.mesh(new T.CircleGeometry(1, 32).rotateX(-90 * R), new T.MeshBasicMaterial({ color: 0x1a1612, transparent: true, opacity: .8, depthWrite: false, map: H.hat(1, 'lua', '#000').ds[0].material.map }), { bong: false });
    nen.position.y = .002; goc.add(nen);
    const tam = new T.Mesh(new T.SphereGeometry(.02, 6, 4), new T.MeshBasicMaterial({ color: 0x000000 })); tam.position.y = .02; goc.add(tam);
    const bo = {};
    const sv = n => Array.from({ length: n }, () => { const a = rnd() * 6.283, r = Math.pow(rnd(), .7); return [Math.cos(a) * r, rnd(), Math.sin(a) * r, rnd()]; });
    for (const [ten, k] of Object.entries(KIEU)) {
      const o = H.nhom(ten); goc.add(o);
      const lua = H.hat(k.lua, 'lua', '#ffb24a'), khoi = H.hat(k.khoi, 'khoi', k.mauKhoi), vay = H.hat(k.vay, 'khoi', '#6b5a44');
      [khoi, vay, lua].forEach(x => o.add(x.nhom));
      let dat = null;
      if (k.dat) { dat = new T.InstancedMesh(new T.DodecahedronGeometry(1, 0), K.vatLieu('dat-do'), k.dat); dat.castShadow = false; dat.frustumCulled = false; dat.userData.boQuaKhung = true; o.add(dat); }
      const den = new T.PointLight(0xffa850, 0, k.cao * 8 * co, 1.6); den.position.y = k.cao * .25 * co; o.add(den);
      bo[ten] = { o, k, lua, khoi, vay, dat, den, vLua: sv(k.lua), vKhoi: sv(k.khoi), vVay: sv(k.vay), vDat: sv(k.dat) };
    }
    const cLua = new T.Color('#ffe2a0'), cLua2 = new T.Color('#e8501c'), cSang = new T.Color('#d88a4a');

    function capNhat(tt) {
      const s = tt.trangThai, t = tt.t || 0, m = new T.Matrix4(), q = new T.Quaternion(), e = new T.Euler();
      nen.visible = s !== 'cao-xa'; tam.visible = s === 'cao-xa';
      nen.scale.setScalar(t > 0 ? KIEU[s].toa * .9 * co * K.smooth(t / .15) : .01);
      for (const [ten, b] of Object.entries(bo)) {
        const on = ten === s && t > 0, k = b.k;
        b.o.visible = on;
        if (!on) {
          // Reset the idle kinds so the pose never depends on earlier calls.
          b.den.intensity = 0;
          [b.lua, b.khoi, b.vay].forEach(x => x.ds.forEach(p => { p.position.set(0, 0, 0); p.scale.set(1, 1, 1); }));
          if (b.dat) { for (let i = 0; i < b.dat.count; i++) b.dat.setMatrixAt(i, m.identity()); b.dat.instanceMatrix.needsUpdate = true; }
          continue;
        }
        // Flash: fireball swells in ~0.15 s, climbs a little, cools from yellow to red and dies.
        const sl = Math.max(0, 1 - t / k.lanh);
        b.den.intensity = k.den * sl * sl;
        b.lua.ds.forEach((p, i) => {
          const v = b.vLua[i], r = k.toa * co * (.25 + .8 * K.smooth(t / .15)) * (.3 + .7 * v[3]);
          p.position.set(v[0] * r, (ten === 'cao-xa' ? 0 : k.cao * co * .22 * v[1] * K.smooth(t / .3)) + r * .35, v[2] * r);
          const sc = co * k.toa * (.55 + .5 * v[3]) * (.6 + .6 * K.smooth(t / .12)); p.scale.set(sc, sc, 1);
          p.material.color.copy(cLua).lerp(cLua2, Math.min(1, t / k.lanh)); p.material.opacity = Math.min(1, sl * 1.6) * (.6 + .4 * v[3]);
        });
        // Column: each puff shoots to its height (exponential ease, column forms almost at once), then drifts,
        // grows and fades. Early puffs are lit by the flash.
        const tat = 1 - K.smooth((t / k.song - .35) / .65);
        b.khoi.ds.forEach((p, i) => {
          const v = b.vKhoi[i], u = Math.max(0, t - v[3] * .12);
          const cot = ten === 'cao-xa' ? 0 : k.cao * co * Math.pow(v[1], .8) * (1 - Math.exp(-u / (ten === 'boc-pha' ? .45 : .16)));
          // Cone that widens with height (a dirty 'cauliflower'), still spreading as it drifts.
          const lan = k.toa * co * (.2 + 1.15 * v[1]) * (.45 + .85 * K.smooth(u / k.song)) * Math.hypot(v[0], v[2]);
          const a = Math.atan2(v[2], v[0]);
          p.position.set(Math.cos(a) * lan + u * .5 * co, cot + u * .35 * co + (ten === 'cao-xa' ? (v[1] - .5) * k.toa * co : k.toa * co * .25), Math.sin(a) * lan);
          const sc = co * k.toa * (.6 + .5 * v[3]) * (.5 + 1.3 * K.smooth(u / k.song)) * (ten === 'cao-xa' ? 1 : .9 + v[1] * .5); p.scale.set(sc, sc, 1);
          p.material.color.set(k.mauKhoi).lerp(cSang, sl * .7 * (1 - v[1] * .5)); p.material.opacity = .82 * tat * K.smooth(u / .08);
        });
        // Dust skirt racing out along the ground.
        b.vay.ds.forEach((p, i) => {
          const v = b.vVay[i], a = Math.atan2(v[2], v[0]), d = k.toa * co * (.6 + 2.6 * (1 - Math.exp(-t / .35))) * (.7 + .3 * v[3]);
          p.position.set(Math.cos(a) * d, k.toa * co * .2 + t * .2, Math.sin(a) * d);
          const sc = co * k.toa * (.9 + 1.0 * K.smooth(t / k.song)) * (.8 + .4 * v[3]); p.scale.set(sc * 1.6, sc * .8, 1);
          p.material.opacity = .55 * tat * K.smooth(t / .1);
        });
        // Earth: ballistic clods (g = 9.8), resting where they land.
        if (b.dat) {
          b.vDat.forEach((v, i) => {
            const u = Math.max(0, t - v[3] * .04), v0 = Math.sqrt(2 * 9.8 * k.cao * co) * (.35 + .65 * v[1]);
            const bay = Math.min(u, 2 * v0 / 9.8), ngang = k.toa * co * (.6 + 1.6 * v[3]) / 1.2;
            const y = Math.max(.05, v0 * bay - 4.9 * bay * bay);
            const sc = co * (ten === 'boc-pha' ? .4 : .1) * (.4 + v[3]);
            e.set(u * 5 + i, u * 3, i);
            b.dat.setMatrixAt(i, m.compose(new T.Vector3(v[0] * ngang * bay, y, v[2] * ngang * bay), q.setFromEuler(e), new T.Vector3(sc, sc, sc)));
          });
          b.dat.instanceMatrix.needsUpdate = true;
        }
      }
      H.chamThap(goc, cham);
    }
    return { goc, capNhat, diemCham: [cham], neo: {} };
  }

  K.dangKy({ ma: 'vu-no', ten: 'Vụ nổ (nổ đất, cao xạ, bộc phá)', phe: 'chung', thoiKy: 'chung', trangThai: ['dat', 'cao-xa', 'boc-pha'], tao });
})(typeof window !== 'undefined' ? window : globalThis);
