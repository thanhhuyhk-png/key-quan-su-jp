// Hình khối khoá nòng, dựng bằng code từ G (kin.js). update(s) đặt tư thế theo trạng thái của khung.
import * as THREE from 'three';
import {G} from './kin.js';

export const COL = {
  olive: '#4b5233', oliveDark: '#3b4128', steel: '#3a3d38', brass: '#b08d3c', proj: '#59603c',
  cap: '#7c3426', accent: '#f0a830', floor: '#2a2d2b', bg: '#1d2022',
};
// Mặt cắt ngang trục nòng: bỏ nửa trên (y > hằng số). constant lớn = chưa cắt.
export const CLIP = new THREE.Plane(new THREE.Vector3(0, -1, 0), 2);

const std = (color, metal, rough) => new THREE.MeshStandardMaterial({color, metalness: metal, roughness: rough, envMapIntensity: 0.6});

// Mỗi chi tiết bị cắt có thêm một bản BackSide màu đỏ sẫm: nhìn qua mặt cắt thấy "lõi" thép thay cho lỗ rỗng.
function cutMesh(geo, mat, parent) {
  const m = new THREE.Mesh(geo, mat);
  mat.clippingPlanes = [CLIP];
  mat.clipShadows = true;
  m.castShadow = true;
  m.receiveShadow = true;
  const cap = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({color: COL.cap, side: THREE.BackSide, clippingPlanes: [CLIP]}));
  m.add(cap);
  parent.add(m);
  return m;
}
const box = (x0, x1, y0, y1, z0, z1) => {
  const g = new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0);
  g.translate((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2);
  return g;
};
// Tấm chữ nhật (y–z) có lỗ tròn ở tâm, đùn theo +x từ x0 tới x1.
function plateWithHole(x0, x1, hy, hz, r) {
  const s = new THREE.Shape();
  s.moveTo(-hz, -hy); s.lineTo(hz, -hy); s.lineTo(hz, hy); s.lineTo(-hz, hy); s.lineTo(-hz, -hy);
  const h = new THREE.Path();
  h.absarc(0, 0, r, 0, Math.PI * 2, true);
  s.holes.push(h);
  const g = new THREE.ExtrudeGeometry(s, {depth: x1 - x0, bevelEnabled: false, curveSegments: 48});
  g.rotateY(Math.PI / 2);
  g.translate(x0, 0, 0);
  return g;
}
// Lathe quanh trục x từ biên dạng [[bán kính, x], ...]
const latheX = (prof, seg = 64) => {
  const g = new THREE.LatheGeometry(prof.map(([r, x]) => new THREE.Vector2(r, x)), seg);
  g.rotateZ(-Math.PI / 2);
  return g;
};

export function buildGun() {
  const root = new THREE.Group();
  const recoiling = new THREE.Group(); // nòng, vòng khoá, chêm, tay quay, đạn: lùi cùng nhau
  root.add(recoiling);
  const mOlive = std(COL.olive, 0.35, 0.55);
  const mDark = std(COL.oliveDark, 0.35, 0.6);
  const mSteel = std(COL.steel, 0.6, 0.45);

  // Nòng: rỗng, buồng đạn r 0,062 tới hết vỏ đạn, côn vào lòng nòng 105 mm, đầu nòng hơi loe.
  const F = G.face, br = G.bore / 2, cr = G.chamberR;
  const tube = latheX([
    [cr, G.ringFront], [0.105, G.ringFront], [0.1, F + 0.7], [0.085, F + 1.3], [0.08, G.muzzle - 0.07],
    [0.088, G.muzzle - 0.06], [0.088, G.muzzle], [br, G.muzzle], [br, F + G.caseLen + 0.06],
    [cr, F + G.caseLen], [cr, G.ringFront],
  ]);
  cutMesh(tube, mOlive, recoiling);

  // Vòng khoá: khối trước có lỗ buồng đạn, tấm trên/dưới, vách trái, tấm sau có lỗ nạp. Bên phải để trống cho chêm ra.
  const ringMat = std(COL.oliveDark, 0.4, 0.5);
  const wx0 = F - G.wedgeDepth, hy = G.ringHalfY, hz = G.ringHalfZ;
  cutMesh(plateWithHole(F, G.ringFront, hy, hz, cr), ringMat, recoiling);
  cutMesh(plateWithHole(G.ringRear, wx0, G.wedgeHalfY, hz, G.rimR + 0.004), ringMat, recoiling);
  cutMesh(box(G.ringRear, F, G.wedgeHalfY, hy, -hz, hz), ringMat, recoiling);
  cutMesh(box(G.ringRear, F, -hy, -G.wedgeHalfY, -hz, hz), ringMat, recoiling);
  cutMesh(box(wx0, F, -G.wedgeHalfY, G.wedgeHalfY, -hz, -G.wedgeHalfZ), ringMat, recoiling);

  // Khối chêm và kim hoả (con của chêm).
  const wedgeMat = std(COL.steel, 0.6, 0.45);
  const wedge = cutMesh(box(wx0, F, -G.wedgeHalfY + 0.003, G.wedgeHalfY - 0.003, -G.wedgeHalfZ, G.wedgeHalfZ), wedgeMat, recoiling);
  const pinMat = std('#8d8f86', 0.8, 0.3);
  const pinGeo = new THREE.CylinderGeometry(0.009, 0.009, 0.11, 20);
  pinGeo.rotateZ(Math.PI / 2);
  pinGeo.translate(F - 0.065, 0, 0);
  const pin = new THREE.Mesh(pinGeo, pinMat);
  wedge.add(pin);

  // Tay quay mở khoá: trục đứng trên tấm trên, cánh tay quay quanh y.
  const lever = new THREE.Group();
  lever.position.set(F - 0.09, hy, hz - 0.03);
  const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.05, 24), mSteel);
  hub.position.y = 0.025;
  const armGeo = new THREE.BoxGeometry(G.leverLen, 0.025, 0.035);
  armGeo.translate(-G.leverLen / 2, 0.04, 0);
  const arm = new THREE.Mesh(armGeo, mSteel);
  const knob = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.1, 16), std('#2b2b27', 0.1, 0.8));
  knob.position.set(-G.leverLen, 0.09, 0);
  lever.add(hub, arm, knob);
  for (const o of [hub, arm, knob]) o.castShadow = true;
  recoiling.add(lever);

  // Máng nòng (đứng yên) và ống hãm lùi (lùi theo nòng).
  const cradle = new THREE.Group();
  root.add(cradle);
  cutMesh(box(-0.05, 1.55, -0.34, -0.31, -0.16, 0.16), mDark, cradle);
  for (const z of [-0.16, 0.16]) cutMesh(box(-0.05, 1.55, -0.34, -0.14, z - 0.012, z + 0.012), mDark, cradle);
  for (const z of [-0.07, 0.07]) {
    const g = new THREE.CylinderGeometry(0.05, 0.05, 1.45, 32);
    g.rotateZ(Math.PI / 2);
    g.translate(G.ringRear + 0.725 + 0.05, -0.225, z);
    cutMesh(g, mOlive, recoiling);
  }

  // Viên đạn: vỏ đồng có gờ, đầu đạn hình búp. Vỏ và đầu đạn tách nhau khi bắn.
  const round = new THREE.Group();
  recoiling.add(round);
  const caseG = new THREE.Group();
  round.add(caseG);
  const brass = std(COL.brass, 0.8, 0.42);
  brass.envMapIntensity = 0.3;
  brass.emissive = new THREE.Color(COL.accent);
  brass.emissiveIntensity = 0;
  const caseGeo = latheX([[0.0, 0], [G.rimR, 0], [G.rimR, 0.012], [G.caseR, 0.016], [G.caseR - 0.003, G.caseLen - 0.02], [br + 0.002, G.caseLen], [0.0, G.caseLen]]);
  const caseMesh = new THREE.Mesh(caseGeo, brass);
  caseMesh.castShadow = true;
  caseG.add(caseMesh);
  const projG = new THREE.Group();
  round.add(projG);
  const pl = G.projLen;
  const projGeo = latheX([[0.0, -0.08], [br - 0.004, -0.08], [br, 0.0], [br, 0.15], [br * 0.93, 0.21], [br * 0.7, 0.29], [br * 0.38, 0.36], [0.01, pl - 0.08 + 0.0], [0.0, pl - 0.08]]);
  projGeo.translate(G.caseLen, 0, 0);
  const projMesh = new THREE.Mesh(projGeo, std(COL.proj, 0.3, 0.55));
  projMesh.castShadow = true;
  projG.add(projMesh);

  // Thước giật lùi: vạch màu nhấn trên thành máng, dài đúng quãng nòng đã lùi.
  const ruler = new THREE.Mesh(new THREE.BoxGeometry(1, 0.012, 0.004), new THREE.MeshBasicMaterial({color: COL.accent}));
  ruler.position.set(0, -0.17, 0.175);
  root.add(ruler);
  const ticks = new THREE.Group();
  for (let i = 0; i <= 10; i++) {
    const tk = new THREE.Mesh(new THREE.BoxGeometry(0.004, i % 5 ? 0.025 : 0.045, 0.003), new THREE.MeshBasicMaterial({color: '#d9d4c3'}));
    tk.position.set(G.ringRear - i * 0.1, -0.15, 0.177);
    ticks.add(tk);
  }
  const end = new THREE.Mesh(new THREE.BoxGeometry(0.006, 0.06, 0.003), new THREE.MeshBasicMaterial({color: COL.accent}));
  end.position.set(G.ringRear - G.recoil, -0.15, 0.178);
  ticks.add(end);
  root.add(ticks);

  const glowMats = {wedge: wedgeMat, pin: pinMat, round: brass};
  for (const m of [wedgeMat, pinMat]) m.emissive = new THREE.Color(COL.accent);

  const anchors = {
    wedge: new THREE.Vector3(), lever: new THREE.Vector3(), chamber: new THREE.Vector3(), ring: new THREE.Vector3(),
  };

  function update(s, t) {
    recoiling.position.x = -s.recoil;
    wedge.position.z = s.wedgeZ;
    lever.rotation.y = s.lever;
    pin.position.x = 0.012 * s.pin;
    // đạn: sau khoá 0,95 m rồi đẩy vào buồng; hiện từ lúc nạp
    round.visible = t >= 4.6 || s.fired;
    round.position.x = F - 0.95 * (1 - s.ram);
    projG.position.x = s.projX;
    projG.visible = s.projX < 3.0;
    caseG.position.set(s.caseX, s.caseY, s.ex * 0.18);
    caseG.rotation.y = -s.ex * 0.7;
    caseG.rotation.z = Math.sin(s.ex * Math.PI) * 0.45;
    brass.emissiveIntensity = 0.9 * s.glow;
    // màu nhấn cho phần đang làm việc
    const pulse = 0.35 + 0.15 * Math.sin(t * 7);
    wedgeMat.emissiveIntensity = s.work === 'wedge' ? pulse : 0;
    pinMat.emissiveIntensity = s.work === 'pin' ? 1.2 * pulse : 0;
    if (s.work === 'round') brass.emissiveIntensity = Math.max(brass.emissiveIntensity, pulse * 0.5);
    ruler.visible = s.recoil > 0.003;
    ruler.scale.x = Math.max(0.001, s.recoil);
    ruler.position.x = G.ringRear - s.recoil / 2;
    ticks.visible = s.work === 'recoil';
    CLIP.constant = 0.6 * (1 - s.cut) + 0.0005;
    // điểm neo cho nhãn
    root.updateMatrixWorld(true);
    anchors.wedge.set(wx0 + 0.02, 0.0, s.wedgeZ + G.wedgeHalfZ).applyMatrix4(recoiling.matrixWorld);
    anchors.lever.set(-G.leverLen, 0.09, 0).applyMatrix4(lever.matrixWorld);
    anchors.chamber.set(F + 0.2, 0.0, -0.04).applyMatrix4(recoiling.matrixWorld);
    anchors.ring.set(G.ringRear, -0.15, 0.18).applyMatrix4(recoiling.matrixWorld);
  }
  return {root, update, anchors, glowMats};
}
