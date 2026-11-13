// tam-tu-lieu.js — "tấm tư liệu" (evidence plane) cho bản đồ 3D: ảnh thật đứng trong không gian bản đồ,
// có cọc ghim xuống điểm neo và nón chiếu, nối liền cảnh ảnh với cảnh bản đồ thay cho cú cắt thô.
//   mode 'lui': cảnh mở bằng ảnh đầy khung (khớp cảnh ảnh trước), máy lùi ra để lộ bản đồ quanh điểm neo.
//   mode 'vao': cảnh chạy bản đồ như cũ, cuối cảnh máy bay vào tấm ảnh tới đầy khung (khớp cảnh ảnh sau).
// Chỉ đổi đường máy và thêm vật thể; cú máy gốc, tàu, nhãn giữ nguyên. Chữ trên tấm = chú thích đã có ở cảnh ảnh.
export async function lapTam(o) {
  const { THREE, sc, cam, W, H, cfg, tam } = o;
  const camf0 = o.camf, upd = o.upd;
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  const io = (x) => { x = clamp(x); return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };

  // ảnh: tông cũ giống Ken Burns (dung-p5: hue s=0.22, contrast 1.08, hơi tối)
  const img = await new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = tam.anh; });
  const cv = document.createElement('canvas'); const MAXW = 2048, sc0 = Math.min(1, MAXW / img.width);
  cv.width = Math.round(img.width * sc0); cv.height = Math.round(img.height * sc0);
  const g = cv.getContext('2d'); g.filter = 'saturate(0.22) contrast(1.08) brightness(0.96)'; g.drawImage(img, 0, 0, cv.width, cv.height);
  g.filter = 'none';                                            // viền tối như vignette=PI/4.5 của cảnh ảnh
  const rg = g.createRadialGradient(cv.width / 2, cv.height / 2, Math.hypot(cv.width, cv.height) * 0.22, cv.width / 2, cv.height / 2, Math.hypot(cv.width, cv.height) * 0.5);
  rg.addColorStop(0, 'rgba(0,0,0,0)'); rg.addColorStop(1, 'rgba(0,0,0,0.42)'); g.fillStyle = rg; g.fillRect(0, 0, cv.width, cv.height);
  const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const asp = cv.width / cv.height;

  // tư thế cuối của cú máy gốc → cỡ và hướng tấm
  const SD = o.SD, K0 = o.K0, K1 = o.K1;
  const tMoc = tam.mode === 'lui' ? SD : 0, kMoc = tam.mode === 'lui' ? K1 : K0;
  upd(tMoc, kMoc); camf0(tMoc, kMoc); cam.updateMatrixWorld();
  const neo = tam.neo();                                   // Vector3 điểm neo (cảng, tàu)
  const pRef = cam.position.clone(), qRef = cam.quaternion.clone();
  const dRef = pRef.distanceTo(neo);
  const hT = dRef * (tam.co || 0.26), wT = hT * asp;        // chiều cao tấm theo khoảng cách máy
  const nang = hT * (tam.nang || 0.3);                        // tấm nổi trên điểm neo
  // dời thẻ khỏi chữ trên màn: keo = kéo về điểm máy nhìn (0..1), lech = tiến về phía máy (bội số chiều cao thẻ)
  const fw = new THREE.Vector3(0, 0, -1).applyQuaternion(qRef);
  const tgt = fw.y < -1e-4 ? pRef.clone().add(fw.clone().multiplyScalar(-pRef.y / fw.y)) : neo.clone();
  tgt.setY(neo.y);
  const NHO0 = tam.nho || 0.42;
  const datThe = (lech, keo) => {                               // vị trí + hướng thẻ cho một cặp tham số
    const chan = neo.clone().lerp(tgt, keo);
    chan.add(pRef.clone().sub(chan).setY(0).normalize().multiplyScalar(hT * lech));
    const day = chan.clone().add(new THREE.Vector3(0, nang, 0));  // mép dưới tấm
    const C = day.clone().add(new THREE.Vector3(0, hT / 2, 0));
    // tấm quay mặt về phía máy (xoay quanh trục đứng, nghiêng ngửa nhẹ theo máy)
    const toCam = pRef.clone().sub(C);
    return { day, yaw: Math.atan2(toCam.x, toCam.z), pitch: Math.atan2(toCam.y, Math.hypot(toCam.x, toCam.z)) * 0.55 };
  };
  // khung thẻ (cỡ nhỏ) chiếu lên màn ở tư thế máy tham chiếu: phải tránh tiêu đề, đồng hồ (trên 340 px), dòng nguồn (dưới 950 px)
  const hop = (d) => {
    const g0 = new THREE.Object3D(); g0.position.copy(d.day); g0.rotation.set(-d.pitch, d.yaw, 0, 'YXZ'); g0.scale.setScalar(NHO0); g0.updateMatrixWorld(true);
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9;
    for (const [x, y] of [[-1, 0], [1, 0], [1, 1], [-1, 1]]) {
      const v = g0.localToWorld(new THREE.Vector3(x * wT / 2, y * hT, 0)).project(cam);
      const px = (v.x * 0.5 + 0.5) * W, py = (1 - (v.y * 0.5 + 0.5)) * H;
      x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py); }
    return { x0, x1, y0, y1: y1 + 70 };                          // + nhãn dưới thẻ
  };
  // điểm không được che (nhãn Hoàng Sa, Trường Sa, Biển Đông: luật cứng của kit), đo ở tư thế tham chiếu
  const tranh = (tam.tranh || []).map((q) => { const v = q.clone().project(cam); return v.z < 1 ? [(v.x * 0.5 + 0.5) * W, (1 - (v.y * 0.5 + 0.5)) * H] : null; }).filter(Boolean);
  const cheNhan = (b) => tranh.some(([x, y]) => x > b.x0 - 170 && x < b.x1 + 170 && y > b.y0 - 60 && y < b.y1 + 30);
  const ok = (b) => b.y0 >= 340 && b.y1 <= 950 && b.x0 >= 120 && b.x1 <= W - 120 && !cheNhan(b);
  let chon = null;
  if (tam.lech !== undefined || tam.keo !== undefined) chon = datThe(tam.lech || 0, tam.keo || 0);
  else {
    let tot = null, diem = 1e9;
    for (const keo of [0, 0.25, 0.5, 0.75]) for (let lech = 0; lech <= 4.01; lech += 0.25) {
      const d = datThe(lech, keo), b = hop(d);
      if (ok(b)) { chon = d; break; }
      const pen = (cheNhan(b) ? 5000 : 0) + Math.max(0, 340 - b.y0) + Math.max(0, b.y1 - 950) + Math.max(0, 120 - b.x0) + Math.max(0, b.x1 - W + 120) + lech * 5 + keo * 40;
      if (pen < diem) { diem = pen; tot = d; }
    }
    if (!chon) chon = tot;
  }
  const { day, yaw, pitch } = chon;
  const grp = new THREE.Group(); grp.position.copy(day); grp.rotation.set(-pitch, yaw, 0, 'YXZ'); sc.add(grp);
  const matA = new THREE.MeshBasicMaterial({ map: tex, transparent: true, fog: false, depthTest: false, toneMapped: false });
  const pl = new THREE.Mesh(new THREE.PlaneGeometry(wT, hT), matA); pl.position.y = hT / 2; pl.renderOrder = 30; grp.add(pl);
  const vienM = new THREE.LineBasicMaterial({ color: 0xcc2222, transparent: true, fog: false, depthTest: false });
  const vien = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints([[-1, -1], [1, -1], [1, 1], [-1, 1]].map(([x, y]) => new THREE.Vector3(x * wT / 2 * 1.015, hT / 2 + y * hT / 2 * 1.02, 0.0001))), vienM);
  vien.renderOrder = 31; grp.add(vien);
  // cọc ghim + vòng ở điểm neo
  const cocM = new THREE.LineBasicMaterial({ color: 0xcc2222, transparent: true, fog: false, depthTest: false });
  const coc = new THREE.Line(new THREE.BufferGeometry().setFromPoints([day, neo.clone().setY(neo.y + 0.001)]), cocM); coc.renderOrder = 29; sc.add(coc);
  const vongM = new THREE.MeshBasicMaterial({ color: 0xcc2222, transparent: true, fog: false, depthTest: false, side: THREE.DoubleSide });
  const vong = new THREE.Mesh(new THREE.RingGeometry(0.8, 1, 48), vongM); vong.rotation.x = -Math.PI / 2; vong.position.copy(neo).setY(neo.y + 0.004); vong.scale.setScalar(hT * 0.09); vong.renderOrder = 29; sc.add(vong);
  // nón chiếu: từ điểm neo lên bốn góc tấm (ảnh "mọc" từ hiện trường); tính lại mỗi khung vì tấm co giãn
  const GOC4 = [[-1, 0], [1, 0], [1, 1], [-1, 1]];
  const gocW = () => GOC4.map(([x, y]) => grp.localToWorld(new THREE.Vector3(x * wT / 2, y * hT, 0)));
  const nonM = new THREE.MeshBasicMaterial({ color: 0xcc2222, transparent: true, opacity: 0.08, fog: false, depthTest: false, depthWrite: false, side: THREE.DoubleSide, blending: THREE.AdditiveBlending });
  const nonG = new THREE.BufferGeometry(); nonG.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(36), 3));
  const non = new THREE.Mesh(nonG, nonM); non.renderOrder = 28; non.frustumCulled = false; sc.add(non);
  const canhM = new THREE.LineBasicMaterial({ color: 0xcc2222, transparent: true, opacity: 0.55, fog: false, depthTest: false });
  const canhG = new THREE.BufferGeometry(); canhG.setAttribute('position', new THREE.Float32BufferAttribute(new Float32Array(24), 3));
  const canh = new THREE.LineSegments(canhG, canhM); canh.renderOrder = 28; canh.frustumCulled = false; sc.add(canh);
  const capNon = () => {
    grp.updateMatrixWorld(true); const g4 = gocW(), n0 = neo, P = nonG.attributes.position, L = canhG.attributes.position;
    for (let i = 0; i < 4; i++) { const a = g4[i], b = g4[(i + 1) % 4];
      P.setXYZ(i * 3, n0.x, n0.y, n0.z); P.setXYZ(i * 3 + 1, a.x, a.y, a.z); P.setXYZ(i * 3 + 2, b.x, b.y, b.z);
      L.setXYZ(i * 2, n0.x, n0.y, n0.z); L.setXYZ(i * 2 + 1, a.x, a.y, a.z); }
    P.needsUpdate = true; L.needsUpdate = true; };

  // nhãn HTML dưới tấm: chú thích của cảnh ảnh + nguồn
  const nh = document.createElement('div');
  nh.style.cssText = 'position:absolute;transform:translate(-50%,0);white-space:nowrap;text-align:center;color:#f0e8d8;font-weight:700;font-size:28px;text-shadow:0 2px 10px #000,0 0 3px #000;pointer-events:none';
  nh.innerHTML = `${tam.chu || ''}<div style="font-weight:400;font-size:20px;color:#cfc8ba">${tam.nguon || ''}</div>`;
  document.body.appendChild(nh);

  // tư thế máy khi tấm đầy khung (cover, giống khung Ken Burns ≈ zoom 1.08)
  const fov = THREE.MathUtils.degToRad(cam.fov), aspC = W / H;
  const dPhu = (asp > aspC ? (hT / 2) / Math.tan(fov / 2) : (wT / 2) / (Math.tan(fov / 2) * aspC)) * 0.93;
  grp.updateMatrixWorld(true); const pTam = grp.localToWorld(new THREE.Vector3(0, hT / 2, dPhu));
  const qTam = grp.quaternion.clone();
  const TP = Math.min(SD * 0.72, tam.tp || 2.6);              // thời lượng cú lùi / cú bay vào

  const setA = (a, aKhung) => {
    matA.opacity = a; vienM.opacity = a * aKhung; cocM.opacity = a * aKhung; vongM.opacity = 0.9 * a * aKhung;
    nonM.opacity = 0.08 * a * aKhung; canhM.opacity = 0.55 * a * aKhung;
  };
  let hudA = 1;
  const camf = (t, k) => {
    camf0(t, k); const pO = cam.position.clone(), qO = cam.quaternion.clone();
    let u;                                                     // 0 = ở tấm, 1 = cú máy gốc
    if (tam.mode === 'lui') u = io(t / TP); else u = 1 - io((t - (SD - TP)) / TP);
    cam.position.copy(pTam.clone().lerp(pO, u)); cam.quaternion.copy(qTam.clone().slerp(qO, u));
    // tấm co lại thành thẻ tư liệu nhỏ ghim tại điểm neo (lùi) / lớn dần trước khi bay vào (vào); thẻ ở lại suốt cảnh
    const NHO = tam.nho || 0.42;
    const s = tam.mode === 'lui' ? lerp(1, NHO, io((t - TP * 0.5) / (TP * 0.7))) : lerp(NHO, 1, io((t - (SD - TP)) / (TP * 0.55)));
    grp.scale.setScalar(s); capNon();
    const a = tam.mode === 'lui' ? 1 : clamp((t - Math.max(0, SD - TP - 1.0)) / 0.5);
    setA(a, clamp(u * 3));
    hudA = clamp((u - 0.6) / 0.35);                            // khung chữ bản đồ chỉ hiện khi đã ra bản đồ
    cam.updateMatrixWorld();
    const v = grp.position.clone().project(cam);
    nh.style.left = ((v.x * 0.5 + 0.5) * W) + 'px'; nh.style.top = ((1 - (v.y * 0.5 + 0.5)) * H + 14) + 'px';
    nh.style.opacity = (v.z < 1 && Math.abs(v.x) < 0.9 && v.y > -0.85) ? a * clamp((u - 0.55) / 0.3) : 0;
  };
  return { camf, hud: () => hudA };
}
