// Kho3D: registry of 3D library items. Each item is one file calling Kho3D.dangKy({...}).
// Units are metres, +X is the item's forward, +Y up, +Z its left side. Everything is a pure function of t.
(function (g) {
  'use strict';
  const T = g.THREE;
  if (!T) throw new Error('Kho3D cần three.js (nạp vendor/three.min.js trước)');
  const K = { mon: {}, T };
  // Treat hex colours as sRGB (r149 defaults to legacy linear, which washes every flat colour out).
  if (T.ColorManagement) T.ColorManagement.legacyMode = false;

  // Deterministic RNG (mulberry32): random leaf placement, wear, crowd variety.
  K.rng = function (seed) {
    let a = (seed >>> 0) || 1;
    return function () {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  };

  K.dangKy = function (def) {
    if (!def || !def.ma) throw new Error('Món thiếu mã');
    if (!Array.isArray(def.trangThai) || def.trangThai.length < 3) throw new Error(def.ma + ': cần ít nhất 3 trạng thái');
    if (typeof def.tao !== 'function') throw new Error(def.ma + ': thiếu hàm tao()');
    if (K.mon[def.ma]) throw new Error('Trùng mã món ' + def.ma);
    K.mon[def.ma] = def;
  };

  K.danhSach = function () {
    return Object.values(K.mon).map(d => ({ ma: d.ma, ten: d.ten, phe: d.phe, trangThai: d.trangThai.slice() }));
  };

  // Build one instance. The item's tao() returns { goc, capNhat(tt), diemCham?: Object3D[], neo?: {ten: Object3D} }.
  K.tao = function (ma, tuyChon) {
    const def = K.mon[ma];
    if (!def) throw new Error('Không có món ' + ma);
    const opts = Object.assign({ hat: 1 }, tuyChon || {});
    const inst = def.tao(K, opts);
    if (!inst || !inst.goc || typeof inst.capNhat !== 'function') throw new Error(ma + ': tao() phải trả {goc, capNhat}');
    const khung = new T.Group();
    khung.name = ma;
    khung.add(K.hinh ? K.hinh.khongCat(inst.goc) : inst.goc);
    inst.khung = khung;
    inst.def = def;
    // Pose the item at time t, then drop it so its lowest contact point touches local ground (y = 0).
    inst.dat = function (tt) {
      const s = Object.assign({ trangThai: def.trangThai[0], t: 0 }, tt || {});
      if (def.trangThai.indexOf(s.trangThai) < 0) throw new Error(ma + ': không có trạng thái ' + s.trangThai);
      inst.goc.position.set(0, 0, 0);
      inst.capNhat(s);
      if (inst.diemCham && inst.diemCham.length && s.chamDat !== false) {
        khung.updateMatrixWorld(true);
        const p = new T.Vector3(), inv = new T.Matrix4().copy(khung.matrixWorld).invert();
        let lo = Infinity;
        for (const o of inst.diemCham) {
          if (!K.hien(o, khung)) continue;
          o.getWorldPosition(p).applyMatrix4(inv);
          lo = Math.min(lo, p.y);
        }
        if (Number.isFinite(lo)) inst.goc.position.y -= lo;
      }
      khung.updateMatrixWorld(true);
      return inst;
    };
    // World positions of named anchors (rope hooks, hands, muzzle) for scene composition.
    inst.neoThe = function (ten) {
      const o = inst.neo && inst.neo[ten];
      if (!o) throw new Error(ma + ': không có neo ' + ten);
      khung.updateMatrixWorld(true);
      return o.getWorldPosition(new T.Vector3());
    };
    return inst;
  };

  // Visible all the way up to (and including) root.
  K.hien = function (o, root) {
    for (let p = o; p; p = p.parent) { if (!p.visible) return false; if (p === root) return true; }
    return true;
  };

  // Size in metres of the item's visible meshes (for scale checks and framing).
  K.doKhung = function (obj) {
    obj.updateMatrixWorld(true);
    const box = new T.Box3();
    // Precise per-vertex bounds (a coarse box of a spinning wheel grows as it turns); hidden subtrees and
    // boQuaKhung meshes (berms, dug-in spades, muzzle flash) are skipped.
    const m = new T.Matrix4(), b = new T.Box3(), v = new T.Vector3();
    obj.traverse(o => {
      if (!o.isMesh || !K.hien(o, obj) || o.userData.boQuaKhung) return;
      if (!o.isInstancedMesh) {
        const pos = o.geometry.attributes.position;
        for (let i = 0; i < pos.count; i++) box.expandByPoint(v.fromBufferAttribute(pos, i).applyMatrix4(o.matrixWorld));
        return;
      }
      // Instanced: bound each copy (three r149 has no InstancedMesh.computeBoundingBox).
      if (!o.geometry.boundingBox) o.geometry.computeBoundingBox();
      for (let i = 0; i < o.count; i++) {
        o.getMatrixAt(i, m); m.premultiply(o.matrixWorld);
        box.union(b.copy(o.geometry.boundingBox).applyMatrix4(m));
      }
    });
    return box;
  };

  // Smooth interpolation helpers shared by poses.
  K.smooth = x => { x = Math.min(1, Math.max(0, x)); return x * x * (3 - 2 * x); };
  K.lerp = (a, b, p) => a + (b - a) * p;
  K.R = Math.PI / 180;

  g.Kho3D = K;
})(typeof window !== 'undefined' ? window : globalThis);
