// Geometry helpers shared by all items. Sizes in metres. Every mesh casts and receives shadows by default.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, R = K.R;
  const H = {};

  H.mesh = function (geo, vl, opts) {
    const m = new T.Mesh(geo, typeof vl === 'string' ? K.vatLieu(vl) : vl);
    m.castShadow = !(opts && opts.bong === false);
    m.receiveShadow = true;
    return m;
  };
  H.nhom = function (ten) { const o = new T.Group(); if (ten) o.name = ten; return o; };
  H.dat = function (o, x, y, z, rx, ry, rz) { o.position.set(x || 0, y || 0, z || 0); o.rotation.set((rx || 0) * R, (ry || 0) * R, (rz || 0) * R); return o; };

  function hinhChuNhatBo(w, h, r) {
    const s = new T.Shape(), x = -w / 2, y = -h / 2;
    r = Math.min(r, w / 2, h / 2);
    s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
    s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r);
    s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
    return s;
  }
  // Rounded box w (x) × h (y) × d (z), centred. b = edge bevel.
  H.hop = function (w, h, d, b) {
    b = Math.min(b === undefined ? .01 : b, d / 2.2, w / 3, h / 3);
    const geo = new T.ExtrudeGeometry(hinhChuNhatBo(w - 2 * b, h - 2 * b, b), { depth: Math.max(.0005, d - 2 * b), bevelEnabled: true, bevelThickness: b, bevelSize: b, bevelSegments: 2, curveSegments: 4 });
    geo.translate(0, 0, -(d - 2 * b) / 2);
    return geo;
  };
  // Extruded plate from a 2D outline in the XY plane, thickness along Z, centred.
  H.tam = function (diem, day, b) {
    const s = new T.Shape(diem.map(p => new T.Vector2(p[0], p[1])));
    b = b === undefined ? Math.min(.006, day / 3) : b;
    const geo = new T.ExtrudeGeometry(s, { depth: Math.max(.0005, day - 2 * b), bevelEnabled: b > 0, bevelThickness: b, bevelSize: b, bevelSegments: 1 });
    geo.translate(0, 0, -(day - 2 * b) / 2);
    return geo;
  };
  // Cylinder along Y (r top, r bottom), or along X / Z with H.truX / H.truZ.
  H.tru = (r1, r2, h, seg) => new T.CylinderGeometry(r1, r2, h, seg || 20);
  H.truX = (r1, r2, h, seg) => H.tru(r1, r2, h, seg).rotateZ(-90 * R);
  H.truZ = (r1, r2, h, seg) => H.tru(r1, r2, h, seg).rotateX(90 * R);
  // Tube along a smooth curve through points [[x,y,z],...].
  H.ong = function (diem, r, seg, kin) {
    const c = new T.CatmullRomCurve3(diem.map(p => new T.Vector3(p[0], p[1], p[2])), !!kin, 'centripetal');
    return new T.TubeGeometry(c, seg || Math.max(8, diem.length * 8), r, 10, !!kin);
  };
  // Straight rod between two points.
  H.thanh = function (a, b, r, vl) {
    const va = new T.Vector3(...a), vb = new T.Vector3(...b), len = va.distanceTo(vb);
    const m = H.mesh(H.tru(r, r, len, 10), vl);
    m.position.copy(va).add(vb).multiplyScalar(.5);
    m.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), vb.clone().sub(va).normalize());
    return m;
  };
  // Lathe around Y from a profile [[radius, y], ...].
  H.tien = (profile, seg) => new T.LatheGeometry(profile.map(p => new T.Vector2(p[0], p[1])), seg || 32);

  // Instanced rivets (small domes) at local positions, all facing +n.
  H.dinhTan = function (diem, r, vl, n) {
    const geo = new T.SphereGeometry(r, 8, 4, 0, Math.PI * 2, 0, Math.PI / 2);
    const im = new T.InstancedMesh(geo, K.vatLieu(vl || 'thep'), diem.length);
    const q = new T.Quaternion().setFromUnitVectors(new T.Vector3(0, 1, 0), new T.Vector3(...(n || [0, 0, 1])).normalize());
    const m = new T.Matrix4();
    diem.forEach((p, i) => { m.compose(new T.Vector3(...p), q, new T.Vector3(1, 1, 1)); im.setMatrixAt(i, m); });
    im.castShadow = true; im.receiveShadow = true;
    return im;
  };

  // Gun-carriage road wheel: tyre with tread blocks, steel disc with lightening holes, hub. Axis along Z.
  H.banhPhao = function (rk, rong) {
    const o = H.nhom('banh');
    const rt = rk * .66;
    const prof = [[rt, -rong / 2], [rk - .025, -rong / 2], [rk, -rong / 2 + .03], [rk, rong / 2 - .03], [rk - .025, rong / 2], [rt, rong / 2]];
    const lop = H.mesh(H.tien(prof, 48).rotateX(90 * R), 'cao-su');
    o.add(lop);
    const n = 30, gai = new T.InstancedMesh(H.hop(.055, .022, rong * .86, .006), K.vatLieu('cao-su'), n), m = new T.Matrix4();
    for (let i = 0; i < n; i++) {
      const a = i / n * Math.PI * 2;
      m.compose(new T.Vector3(Math.cos(a) * (rk + .006), Math.sin(a) * (rk + .006), 0), new T.Quaternion().setFromAxisAngle(new T.Vector3(0, 0, 1), a + Math.PI / 2), new T.Vector3(1, 1, 1));
      gai.setMatrixAt(i, m);
    }
    gai.castShadow = true; o.add(gai);
    const dia = H.mesh(H.tien([[0, -rong * .28], [rt * .98, -rong * .28], [rt + .005, -rong * .2], [rt + .005, rong * .2], [rt * .98, rong * .28], [0, rong * .28]], 40).rotateX(90 * R), 'son-lx');
    o.add(dia);
    for (let i = 0; i < 6; i++) {
      const a = i / 6 * Math.PI * 2, lo = H.mesh(H.truZ(rt * .16, rt * .16, rong * .6, 16), 'den');
      lo.position.set(Math.cos(a) * rt * .58, Math.sin(a) * rt * .58, 0); o.add(lo);
    }
    const truc = H.mesh(H.tien([[0, -rong * .5], [rt * .3, -rong * .5], [rt * .26, -rong * .32], [rt * .3, rong * .32], [rt * .22, rong * .5], [0, rong * .5]], 24).rotateX(90 * R), 'thep');
    o.add(truc);
    const bulong = [];
    for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2; bulong.push([Math.cos(a) * rt * .2, Math.sin(a) * rt * .2, rong * .5]); }
    o.add(H.dinhTan(bulong, .012, 'thep-mon'));
    return o;
  };

  // Bicycle wheel (28 inch class): tyre, rim, 36 spokes, hub. Axis along Z.
  H.banhXeDap = function (rk) {
    const o = H.nhom('banh-xe-dap');
    o.add(H.mesh(new T.TorusGeometry(rk - .018, .018, 10, 64), 'cao-su'));
    o.add(H.mesh(new T.TorusGeometry(rk - .04, .009, 6, 64), 'thep-mon'));
    o.add(H.mesh(H.truZ(.022, .022, .1, 14), 'thep-mon'));
    const n = 36, nan = new T.InstancedMesh(H.tru(.0013, .0013, 1, 4), K.vatLieu('thep-mon'), n), m = new T.Matrix4();
    for (let i = 0; i < n; i++) {
      const a = i / n * Math.PI * 2, side = i % 2 ? .035 : -.035, lech = (i % 4 < 2 ? 1 : -1) * .3;
      const p0 = new T.Vector3(Math.cos(a + lech) * .02, Math.sin(a + lech) * .02, side);
      const p1 = new T.Vector3(Math.cos(a) * (rk - .045), Math.sin(a) * (rk - .045), 0);
      const d = p1.clone().sub(p0), len = d.length();
      m.compose(p0.clone().add(p1).multiplyScalar(.5), new T.Quaternion().setFromUnitVectors(new T.Vector3(0, 1, 0), d.normalize()), new T.Vector3(1, len, 1));
      nan.setMatrixAt(i, m);
    }
    nan.castShadow = true; o.add(nan);
    return o;
  };

  // Lanceolate leaf in the XY plane, slightly cupped, tip along +X.
  let laGeo = null;
  function geoLa() {
    if (laGeo) return laGeo;
    const s = new T.Shape();
    s.moveTo(0, 0); s.quadraticCurveTo(.05, .028, .13, 0); s.quadraticCurveTo(.05, -.028, 0, 0);
    laGeo = new T.ShapeGeometry(s, 6);
    const p = laGeo.attributes.position;
    for (let i = 0; i < p.count; i++) p.setZ(i, Math.abs(p.getY(i)) * .6 - p.getX(i) * p.getX(i) * .8);
    laGeo.computeVertexNormals();
    return laGeo;
  }
  // A leafy cut branch: twig along +X of length dai, leaves in clusters. Used for camouflage.
  H.canhLa = function (rnd, dai, matDo) {
    const o = H.nhom('canh-la');
    const cong = .08 + rnd() * .12, diem = [[0, 0, 0], [dai * .5, cong, (rnd() - .5) * .1], [dai, cong * .6 - .05, (rnd() - .5) * .15]];
    o.add(H.mesh(H.ong(diem, .008, 12), 'go-toi'));
    const n = Math.round(dai * 60 * (matDo || 1));
    const c = new T.CatmullRomCurve3(diem.map(p => new T.Vector3(...p)));
    const im = new T.InstancedMesh(geoLa(), K.vatLieuLa('chung'), n), mau = [0, 1, 2, 3].map(i => K.vatLieuLa(i).color);
    const m = new T.Matrix4(), q = new T.Quaternion(), e = new T.Euler();
    for (let i = 0; i < n; i++) {
      const u = .15 + .85 * rnd(), p = c.getPoint(u);
      p.add(new T.Vector3((rnd() - .5) * .08, (rnd() - .5) * .08, (rnd() - .5) * .08));
      e.set(rnd() * 6.28, rnd() * 6.28, rnd() * 6.28); q.setFromEuler(e);
      const s = .7 + rnd() * .7, k = Math.floor(rnd() * 4);
      m.compose(p, q, new T.Vector3(s, s, s)); im.setMatrixAt(i, m); im.setColorAt(i, mau[k]);
    }
    im.castShadow = true; im.receiveShadow = true; o.add(im);
    return o;
  };


  // Forest strip: trunks, dark canopy cores and crossed leaf cards (alpha leaf texture), all instanced.
  // cay: [{x, y, z, h}] ground positions and heights. Reusable by any scene.
  H.rung = function (cay, rnd) {
    const o = H.nhom('rung'), m = new T.Matrix4(), q = new T.Quaternion(), e = new T.Euler();
    const than = new T.InstancedMesh(H.tien([[.11, 0], [.08, .4], [.06, 1], [0, 1]], 8), K.vatLieu('go-toi'), cay.length);
    const nCum = 5, nThe = 4;
    const loi = new T.InstancedMesh(new T.IcosahedronGeometry(1, 2), new T.MeshStandardMaterial({ color: new T.Color('#1d2c17'), roughness: 1 }), cay.length * nCum);
    const the = new T.InstancedMesh(new T.PlaneGeometry(2, 2), K.vatLieu('la-tan'), cay.length * nCum * nThe);
    let a = 0, b = 0;
    cay.forEach((c, i) => {
      m.compose(new T.Vector3(c.x, c.y, c.z), q.identity(), new T.Vector3(1, c.h, 1)); than.setMatrixAt(i, m);
      for (let k = 0; k < nCum; k++) {
        const r = (.35 + rnd() * .35) * (c.h / 3), p = new T.Vector3(c.x + (rnd() - .5) * c.h * .35, c.y + c.h * (.85 + rnd() * .35), c.z + (rnd() - .5) * c.h * .35);
        m.compose(p, q.identity(), new T.Vector3(r * .55, r * .48, r * .55)); loi.setMatrixAt(a++, m);
        for (let j = 0; j < nThe; j++) {
          e.set(rnd() * Math.PI, rnd() * Math.PI, rnd() * Math.PI); q.setFromEuler(e);
          m.compose(p, q, new T.Vector3(r * 1.25, r * 1.25, 1)); the.setMatrixAt(b++, m);
        }
      }
    });
    [than, loi, the].forEach(x => { x.castShadow = true; x.receiveShadow = true; x.frustumCulled = false; o.add(x); });
    return o;
  };

  // ---- Soft billboard particles for fire and smoke ------------------------------------------------------------
  // Each particle is a camera-facing quad (oriented in onBeforeRender, so poses stay a pure function of t) with a
  // soft procedural texture: 'lua' a hot core with a soft edge (drawn additively), 'khoi' a lumpy puff.
  const texHat = {};
  function vanHat(kieu) {
    if (texHat[kieu] !== undefined) return texHat[kieu];
    if (typeof document === 'undefined') return (texHat[kieu] = null);
    const s = 128, c = document.createElement('canvas'); c.width = c.height = s;
    const x = c.getContext('2d'), rnd = K.rng(kieu === 'lua' ? 11 : 23);
    const dom = (cx, cy, r, a) => { const gr = x.createRadialGradient(cx, cy, 0, cx, cy, r); if (!gr) return; gr.addColorStop(0, `rgba(255,255,255,${a})`); gr.addColorStop(1, 'rgba(255,255,255,0)'); x.fillStyle = gr; x.beginPath(); x.arc(cx, cy, r, 0, 7); x.fill(); };
    if (kieu === 'lua') { dom(64, 64, 62, 1); dom(64, 70, 34, .9); }
    else {
      // Billowing puff: broad lobes plus many small ones (ragged edge); lit from above (lower part darker); grain.
      for (let i = 0; i < 26; i++) { const a = rnd() * 6.28, d = rnd() * 30; dom(64 + Math.cos(a) * d, 64 + Math.sin(a) * d, 18 + rnd() * 26, .32 + rnd() * .3); }
      for (let i = 0; i < 70; i++) { const a = rnd() * 6.28, d = 20 + rnd() * 26; dom(64 + Math.cos(a) * d, 64 + Math.sin(a) * d, 5 + rnd() * 10, .25 + rnd() * .3); }
      x.globalCompositeOperation = 'source-atop';
      const gr = x.createLinearGradient(0, 10, 0, 118);
      if (gr) { gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(1, 'rgba(70,70,70,.65)'); x.fillStyle = gr; x.fillRect(0, 0, s, s); }
      for (let i = 0; i < 900; i++) { x.fillStyle = rnd() < .5 ? 'rgba(0,0,0,.18)' : 'rgba(255,255,255,.12)'; x.fillRect(rnd() * s, rnd() * s, 2, 2); }
      x.globalCompositeOperation = 'source-over';
    }
    const tex = new T.CanvasTexture(c); tex.encoding = T.sRGBEncoding;
    return (texHat[kieu] = tex);
  }
  const _q = new T.Quaternion();
  H.hat = function (n, kieu, mau) {
    const nhom = H.nhom('hat-' + kieu), ds = [];
    for (let i = 0; i < n; i++) {
      const m = new T.Mesh(new T.PlaneGeometry(1, 1), new T.MeshBasicMaterial({ map: vanHat(kieu), color: new T.Color(mau), transparent: true, depthWrite: false, opacity: 0, blending: kieu === 'lua' ? T.AdditiveBlending : T.NormalBlending }));
      m.castShadow = false; m.receiveShadow = false; m.userData.boQuaKhung = true; m.frustumCulled = false;
      // Face the camera without touching the pose: undo the parent rotation, then take the camera's.
      m.onBeforeRender = (r, sc, cam) => { m.parent.getWorldQuaternion(_q).invert(); m.quaternion.copy(_q).multiply(cam.quaternion); m.updateMatrixWorld(); };
      nhom.add(m); ds.push(m);
    }
    return { nhom, ds };
  };
  // A fire made of rising, shrinking flame particles: flicker is a pure function of t. o: {r, cao, toc, n}.
  H.lua = function (rnd, o) {
    const op = Object.assign({ r: .5, cao: 1.6, toc: 1.3, n: 16, khoi: 6 }, o);
    const l = H.hat(op.n, 'lua', '#ffb347'), k = H.hat(op.khoi, 'khoi', '#2a2420'), nhom = H.nhom('lua');
    nhom.add(k.nhom); nhom.add(l.nhom);
    const seed = l.ds.map(() => [rnd(), (rnd() - .5) * 2, (rnd() - .5) * 2, rnd()]), seedK = k.ds.map(() => [rnd(), (rnd() - .5) * 2, (rnd() - .5) * 2]);
    const cVang = new T.Color('#ffd27a'), cDo = new T.Color('#e0481c');
    nhom.userData.capNhat = function (t, cuong) {
      const c = cuong === undefined ? 1 : cuong;
      l.ds.forEach((m, i) => {
        const [ph, dx, dz, k2] = seed[i], u = ((t * op.toc * (.8 + k2 * .5) + ph) % 1 + 1) % 1;
        m.position.set(dx * op.r * (1 - u * .6), u * op.cao * c, dz * op.r * (1 - u * .6));
        const sc = op.r * (1.5 - u) * (.8 + k2 * .5) * c; m.scale.set(sc, sc * 1.5, 1);
        m.material.color.copy(cVang).lerp(cDo, u); m.material.opacity = c * Math.sin(Math.PI * Math.min(1, u * 1.15)) * .9;
      });
      k.ds.forEach((m, i) => {
        const [ph, dx, dz] = seedK[i], u = ((t * op.toc * .45 + ph) % 1 + 1) % 1;
        m.position.set(dx * op.r + u * op.r, op.cao * c * (.8 + u * 2.2), dz * op.r);
        const sc = op.r * (1.2 + u * 2.4) * c; m.scale.set(sc, sc, 1); m.material.opacity = c * .55 * Math.sin(Math.PI * u);
      });
    };
    return nhom;
  };

  // Sandbags: one instanced pillow per entry [x, y, z, rotY, rotZ?, rotX?] (deg); y is the bag's bottom (centre when rotX).
  // Bag 0.56 × 0.17 × 0.32 m (filled jute sack), small per-bag squash and shade so walls do not look tiled.
  let baoGeo = null;
  H.baoCat = function (ds, rnd) {
    if (!baoGeo) {
      baoGeo = H.hop(.56, .17, .32, .07);
      const p = baoGeo.attributes.position;
      for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i); p.setY(i, p.getY(i) * (1 - .35 * Math.pow(Math.abs(x) / .28, 4)) * (1 - .25 * Math.pow(Math.abs(z) / .16, 4))); }
      baoGeo.computeVertexNormals();
    }
    const im = new T.InstancedMesh(baoGeo, K.vatLieu('bao'), Math.max(1, ds.length)), m = new T.Matrix4(), c = new T.Color();
    ds.forEach((d, i) => {
      const s = .92 + rnd() * .16;
      m.compose(new T.Vector3(d[0], d[1] + (d[5] === undefined ? .085 * s : 0), d[2]), new T.Quaternion().setFromEuler(new T.Euler((d[5] || 0) * R, (d[3] || 0) * R + (rnd() - .5) * .12, (d[4] || 0) * R + (rnd() - .5) * .06)), new T.Vector3(s, s * (.85 + rnd() * .3), s));
      im.setMatrixAt(i, m); im.setColorAt(i, c.setScalar(.78 + rnd() * .3));
    });
    im.count = ds.length;
    im.castShadow = true; im.receiveShadow = true;
    return im;
  };

  // Lowest drawn point of a posed item, in the item root's frame (the root sits at the origin, unrotated, while
  // posing). Meshes marked boQuaKhung (spinning props, fire, smoke) are skipped, like K.doKhung. For items with no
  // natural feet (aircraft, air bursts, parachutes) so the library's ground-contact rule still holds.
  H.chamThap = function (goc, cham) {
    goc.updateMatrixWorld(true);
    const inv = new T.Matrix4().copy(goc.matrixWorld).invert(), m = new T.Matrix4(), v = new T.Vector3(), b = new T.Box3();
    let lo = Infinity;
    goc.traverse(o => {
      if (!o.isMesh || !K.hien(o, goc) || o.userData.boQuaKhung) return;
      if (o.isInstancedMesh) {
        if (!o.geometry.boundingBox) o.geometry.computeBoundingBox();
        for (let i = 0; i < o.count; i++) { o.getMatrixAt(i, m); m.premultiply(o.matrixWorld).premultiply(inv); lo = Math.min(lo, b.copy(o.geometry.boundingBox).applyMatrix4(m).min.y); }
        return;
      }
      m.multiplyMatrices(inv, o.matrixWorld);
      const p = o.geometry.attributes.position;
      for (let i = 0; i < p.count; i++) lo = Math.min(lo, v.fromBufferAttribute(p, i).applyMatrix4(m).y);
    });
    cham.position.set(0, Number.isFinite(lo) ? lo : 0, 0);
  };

  // r149 frustum-culls an InstancedMesh by its source geometry only; copies spread over metres would pop out.
  const _instanced = T.InstancedMesh;
  H.khongCat = function (root) { root.traverse(o => { if (o instanceof _instanced) o.frustumCulled = false; }); return root; };

  K.hinh = H;
})(typeof window !== 'undefined' ? window : globalThis);
