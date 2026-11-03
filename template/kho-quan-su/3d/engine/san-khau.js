// Stage: renderer, lighting presets (day studio, late afternoon, moonlit night), diorama blocks, camera helpers.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;

  K.mayVe = function (canvas, w, h) {
    const r = new T.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
    r.setPixelRatio(1); r.setSize(w, h, false);
    r.outputEncoding = T.sRGBEncoding;
    r.toneMapping = T.ACESFilmicToneMapping; r.toneMappingExposure = .92;
    r.shadowMap.enabled = true; r.shadowMap.type = T.PCFSoftShadowMap;
    return r;
  };

  // Soft gradient sky baked into an environment map so metal and paint pick up believable reflections.
  const envCache = {};
  function moiTruong(renderer, tren, duoi) {
    const key = tren + duoi;
    if (envCache[key]) return envCache[key];
    const s = new T.Scene(), geo = new T.SphereGeometry(10, 32, 16), c = [], a = new T.Color(tren), b = new T.Color(duoi);
    const p = geo.attributes.position;
    for (let i = 0; i < p.count; i++) { const k = K.smooth((p.getY(i) / 10 + .3) / 1.1); const col = b.clone().lerp(a, k); c.push(col.r, col.g, col.b); }
    geo.setAttribute('color', new T.Float32BufferAttribute(c, 3));
    s.add(new T.Mesh(geo, new T.MeshBasicMaterial({ vertexColors: true, side: T.BackSide })));
    const pm = new T.PMREMGenerator(renderer);
    envCache[key] = pm.fromScene(s, .04).texture;
    pm.dispose();
    return envCache[key];
  }

  const KIEU = {
    ngay:  { nen: '#d7dee5', troi: '#e6edf4', dat: '#6f6553', hemi: .42, chinh: ['#fff0d8', 1.45, [-4, 8, 5]], phu: ['#cfe0ff', .3, [5, 3, -4]], suong: null },
    chieu: { nen: '#d3c4ad', troi: '#f0dcbb', dat: '#5b4c3a', hemi: .38, chinh: ['#ffcf94', 1.6, [-7, 3.2, 3]], phu: ['#9fb8e0', .28, [5, 4, -4]], suong: null },
    dem:   { nen: '#0b121c', troi: '#4a6386', dat: '#101317', hemi: .55, chinh: ['#a9c2e8', 1.35, [3, 9, -4]], phu: ['#5f80b4', .55, [-6, 3, 5]], suong: ['#0e1722', .034] },
  };

  // A lit scene in one of the presets. bongRong = half-size of the shadow camera (m).
  K.canh = function (renderer, kieu, bongRong) {
    const k = KIEU[kieu || 'ngay'];
    if (!k) throw new Error('Không có kiểu ánh sáng ' + kieu);
    const s = new T.Scene();
    s.background = new T.Color(k.nen);
    s.environment = renderer ? moiTruong(renderer, k.troi, k.dat) : null;
    if (k.suong) s.fog = new T.FogExp2(new T.Color(k.suong[0]), k.suong[1]);
    s.add(new T.HemisphereLight(new T.Color(k.troi), new T.Color(k.dat), k.hemi));
    const sun = new T.DirectionalLight(new T.Color(k.chinh[0]), k.chinh[1]);
    sun.position.set(...k.chinh[2]); sun.castShadow = true;
    const r = bongRong || 5;
    Object.assign(sun.shadow.camera, { left: -r, right: r, top: r, bottom: -r, near: .5, far: 40 });
    const ms = r > 4 ? 2048 : 1024; sun.shadow.mapSize.set(ms, ms); sun.shadow.bias = -.0004; sun.shadow.normalBias = .02; sun.shadow.radius = 3;
    s.add(sun); s.add(sun.target);
    const fill = new T.DirectionalLight(new T.Color(k.phu[0]), k.phu[1]);
    fill.position.set(...k.phu[2]); s.add(fill);
    s.userData = { kieu, troi: sun };
    return s;
  };

  // Round display plinth: soil puck with a grass top, for single-item turntables.
  K.deTron = function (r, kieu) {
    const o = H.nhom('de-tron');
    const dat = H.mesh(H.tru(r, r * 1.02, .18, 64), 'dat'); dat.position.y = -.09; o.add(dat);
    const mat = H.mesh(new T.CircleGeometry(r * .995, 72).rotateX(-90 * R), kieu === 'dem' ? 'dat' : 'co'); mat.position.y = .001; o.add(mat);
    const vien = H.mesh(H.tru(r * 1.04, r * 1.06, .05, 64), new T.MeshStandardMaterial({ color: 0x9fb0bd, roughness: .25, metalness: .1, transparent: true, opacity: .55 }));
    vien.position.y = -.205; o.add(vien);
    return o;
  };

  // Diorama block (sa bàn): terrain top with a slope along +X, cut-away sides showing soil strata, glass plinth.
  // Returns { nhom, doCao(x, z) } so items can stand on the surface.
  K.saBan = function (op) {
    const o = Object.assign({ dai: 14, rong: 6, day: 1.6, doc: 12, hat: 3, nhap: .08 }, op);
    const rnd = K.rng(o.hat), tanD = Math.tan(o.doc * R);
    const sx = 140, sz = 60;
    const nhieu = (x, z) => o.nhap * (Math.sin(x * 1.3 + 1.7) * Math.cos(z * 1.1) * .6 + Math.sin(x * 3.1 + z * 2.3) * .25 + Math.sin(x * 7.7 - z * 5.1) * .08);
    const doCao = (x, z) => x * tanD + nhieu(x, z);
    const nhom = H.nhom('sa-ban');
    // Top surface with vertex colours: grass, worn dirt track along the centre.
    const top = new T.PlaneGeometry(o.dai, o.rong, sx, sz).rotateX(-90 * R);
    const p = top.attributes.position, col = [], cGrass = new T.Color('#5d6a39'), cDry = new T.Color('#7b7446'), cDirt = new T.Color('#7a6142');
    for (let i = 0; i < p.count; i++) {
      const x = p.getX(i), z = p.getZ(i);
      p.setY(i, doCao(x, z));
      const track = Math.exp(-Math.pow(z / (o.rong * .16), 2)), n = .5 + .5 * Math.sin(x * 2.1 + z * 3.7) * Math.cos(z * 1.3 - x);
      const c = cGrass.clone().lerp(cDry, n * .5).lerp(cDirt, K.smooth(track * 1.15));
      col.push(c.r, c.g, c.b);
    }
    top.setAttribute('color', new T.Float32BufferAttribute(col, 3));
    top.computeVertexNormals();
    const mTop = H.mesh(top, new T.MeshStandardMaterial({ vertexColors: true, roughness: .97 }), { bong: false });
    nhom.add(mTop);
    // Side walls: soil strata bands with wavy boundaries.
    const tang = ['#6f5a3c', '#8a6a44', '#a5845a', '#7a5c3e', '#9b7d57', '#5e4a33'];
    function vach(diemTren) {
      const n = diemTren.length, cols = 18, pos = [], c = [], idx = [];
      for (let i = 0; i < n; i++) {
        const [x, y, z] = diemTren[i];
        for (let j = 0; j <= cols; j++) {
          const v = j / cols, yy = K.lerp(y, -o.day, v);
          pos.push(x, yy, z);
          const d = (y - yy) + Math.sin(x * 2.3 + z * 1.7) * .05;
          const band = Math.min(tang.length - 1, Math.floor(d / .27));
          const cc = new T.Color(tang[band]).multiplyScalar(.92 + .16 * Math.sin(x * 9 + j));
          c.push(cc.r, cc.g, cc.b);
        }
      }
      for (let i = 0; i < n - 1; i++) for (let j = 0; j < cols; j++) {
        const a = i * (cols + 1) + j, b = a + cols + 1;
        idx.push(a, b, a + 1, b, b + 1, a + 1);
      }
      const geo = new T.BufferGeometry();
      geo.setAttribute('position', new T.Float32BufferAttribute(pos, 3));
      geo.setAttribute('color', new T.Float32BufferAttribute(c, 3));
      geo.setIndex(idx); geo.computeVertexNormals();
      const m = H.mesh(geo, new T.MeshStandardMaterial({ vertexColors: true, roughness: 1, side: T.DoubleSide }), { bong: false });
      nhom.add(m);
    }
    const X = o.dai / 2, Z = o.rong / 2, edge = (fx, fz, n) => Array.from({ length: n + 1 }, (_, i) => { const [x, z] = [fx(i / n), fz(i / n)]; return [x, doCao(x, z), z]; });
    vach(edge(u => -X + u * o.dai, () => Z, sx));
    vach(edge(u => X - u * o.dai, () => -Z, sx));
    vach(edge(() => X, u => Z - u * o.rong, sz));
    vach(edge(() => -X, u => -Z + u * o.rong, sz));
    const day = H.mesh(H.hop(o.dai, .02, o.rong, .002), 'dat'); day.position.y = -o.day; nhom.add(day);
    const de = H.mesh(H.hop(o.dai + .5, .14, o.rong + .5, .04), new T.MeshStandardMaterial({ color: 0xaebfcc, roughness: .18, metalness: .05, transparent: true, opacity: .6 }));
    de.position.y = -o.day - .08; nhom.add(de);
    // Scattered stones and grass tufts for scale cues.
    const da = new T.InstancedMesh(new T.DodecahedronGeometry(.06, 0), K.vatLieu('dat-do'), 90), m4 = new T.Matrix4();
    for (let i = 0; i < 90; i++) {
      const x = (rnd() - .5) * o.dai * .96, z = (rnd() - .5) * o.rong * .96, s = .4 + rnd() * 1.4;
      m4.compose(new T.Vector3(x, doCao(x, z) + .01, z), new T.Quaternion().setFromEuler(new T.Euler(rnd() * 3, rnd() * 3, rnd() * 3)), new T.Vector3(s, s * .6, s));
      da.setMatrixAt(i, m4);
    }
    da.castShadow = true; da.receiveShadow = true; nhom.add(da);
    H.khongCat(nhom);
    return { nhom, doCao, doc: o.doc };
  };

  // Camera orbiting a target: góc (deg around Y), cao (height above target), xa (distance).
  K.quayQuanh = function (cam, tam, xa, cao, goc) {
    const a = goc * R;
    cam.position.set(tam.x + Math.cos(a) * xa, tam.y + cao, tam.z + Math.sin(a) * xa);
    cam.lookAt(tam);
  };
})(typeof window !== 'undefined' ? window : globalThis);
