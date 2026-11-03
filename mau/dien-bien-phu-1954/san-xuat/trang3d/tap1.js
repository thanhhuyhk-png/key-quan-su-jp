// Tập 1 ĐBP: một cảnh 3D mỗi trang. window.CANH3D (sinh bởi dung-3d.py) chọn sân khấu của bản mẫu, cảnh mẫu mượn
// trạng thái vật thể (proto), mốc thời gian vật lý (te0, toc) và biến thể máy quay (xoay quanh điểm nhìn, đẩy/kéo, nâng).
// Thời gian cảnh mẫu tính theo bảng nhóm của bản mẫu (cat), nên mọi sự kiện vật lý giữ đúng như đã duyệt.
(function (C) {
  'use strict';
  const S = window.CANH3D, { tron, lerp } = C, T = window.THREE;
  C.nhomTrang(S.cat);
  const TAO = {
    sanBay: () => C.canhSanBay(), bauTroi: () => C.canhBauTroi(), tranDia: () => C.canhTranDia(),
    himLam: () => C.canhHimLam(), himLamDem: () => C.canhHimLam({ dem: true }), a1Dem: () => C.canhA1Dem(), a1Cat: () => C.canhA1Cat(),
    A: () => C.canhA(), B: () => C.canhB(), Cc: () => C.canhC(), D: () => C.canhDocChuoi(), F: () => C.canhF(),
  };
  const canh = TAO[S.san]();
  const nhin = S.nhin === 'dem' ? C.nhinDem(S.nhinThem || {}) : S.nhin === 'thu' ? C.nhinDem({ phoi: (S.phoi || .92) * 1.3, tuongPhan: 1, sang: 0, toi: [.03, .035, .045] }) : C.nhinPhim(Object.assign({}, C.NHIN_NGAY, S.nhinThem || {}));
  const ray = new T.Raycaster(), dat = new T.Plane(new T.Vector3(0, 1, 0), 0), v = new T.Vector3();

  // Biến thể máy: lấy máy của cảnh mẫu, tìm điểm nhìn (giao tia nhìn với mặt đất, hoặc 60 m phía trước), rồi
  // xoay quanh trục đứng qua điểm nhìn (độ), đổi khoảng cách (hệ số), nâng (m). Các đại lượng nội suy theo cảnh.
  function bienThe(cam, u) {
    const b = S.bien; if (!b) return cam;
    const k = tron(u), g = a => Array.isArray(a) ? lerp(a[0], a[1], k) : (a || 0);
    const huong = cam.getWorldDirection(new T.Vector3());
    ray.set(cam.position, huong); ray.far = 4000;
    ray.camera = cam;  // hạt (Sprite) cần máy để tính tia; vật không tính được thì bỏ qua
    let cham = null;
    const luoi = []; canh.scene.traverseVisible(o => { if (o.isMesh && !o.isInstancedMesh) luoi.push(o); });
    try { cham = ray.intersectObjects(luoi, false)[0] || null; } catch (e) { cham = null; }
    const q = cham ? cham.point.clone() : ray.ray.intersectPlane(dat, v) && v.distanceTo(cam.position) < 3000 ? v.clone() : cam.position.clone().addScaledVector(huong, 60);
    const r = cam.position.clone().sub(q), goc = g(b.xoay) * Math.PI / 180;
    r.applyAxisAngle(new T.Vector3(0, 1, 0), goc).multiplyScalar(b.keo ? g(b.keo) : 1);
    const p = q.clone().add(r); p.y = Math.max(q.y + 1.2, p.y + g(b.cao));
    if (b.fov) cam.fov = g(b.fov);
    C.nhin(cam, p, q); cam.updateProjectionMatrix();
    return cam;
  }

  function renderFrame(t) {
    const k = Math.floor(t * C.FPS + 1e-6), te = S.te0 + t * (S.toc || 1);
    const cam = bienThe(canh.ve(te - (S.goc ? C.batDau(S.goc) : 0), S.proto), t / S.d);
    const phu = { vien: S.vien ?? .5 };
    for (const [t0, a, dai] of S.chop || []) { const u = te - t0; if (u >= 0 && u < dai) phu.chop = Math.max(phu.chop || 0, a * (1 - u / dai)); }
    C.renderer.toneMappingExposure = S.phoi || .92;
    C.ve(canh.scene, cam, k + S.k0, nhin);
    C.lopPhu(k, phu);
    const den = (S.vao ? 1 - tron(t / S.vao) : 0) + (S.ra ? tron((t - S.d + S.ra) / S.ra) : 0);
    if (den > 0) C.lopPhu(k, { vien: 0, hat: 0, toi: Math.min(1, den) });
  }
  window.SIZE = C.W + 'x' + C.HH; window.DURATION = S.d; window.renderFrame = renderFrame;
  document.fonts.load('700 150px Oswald').then(() => { renderFrame(0); window.READY = true; });
})(window.BT);
