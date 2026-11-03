// Phim mẫu: khoá nòng lựu pháo 105 mm M2A1, một vòng nạp – bắn – giật lùi – hất vỏ. render(t) là hàm thuần của t.
import * as THREE from 'three';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';
import {runSim} from 'teardown-kit/runtime.js';
import {createStage} from 'teardown-kit/stage3d.js';
import {keyed} from 'teardown-kit/util.js';
import {buildGun, COL} from './gun.js';
import {captionAt, stateAt, T} from './kin.js';

const DEFAULTS = {duration: T.end, fps: 60, theme: 'dark', hud: {enabled: false}, director: {enabled: false}, watermark: ''};

// Góc máy theo thời gian: [t, [vị trí x,y,z, đích x,y,z]]
const CAM = [
  [0, [-1.45, 0.7, 1.35, 0.3, -0.08, 0]],
  [T.cut, [-0.95, 1.2, 0.7, 0.0, -0.1, 0.03]],
  [T.open, [-0.85, 1.05, 0.72, -0.08, -0.1, 0.07]],
  [T.ram, [-1.2, 1.0, 0.95, -0.25, -0.1, 0.03]],
  [T.close, [-0.85, 1.05, 0.7, -0.05, -0.1, 0.05]],
  [T.fire - 0.3, [-1.0, 1.75, 2.15, 0.15, -0.2, 0]],
  [T.runout + 1.6, [-1.0, 1.75, 2.15, 0.15, -0.2, 0]],
  [T.reopen, [-1.5, 0.85, 1.15, -0.4, -0.15, 0.05]],
  [T.uncut, [-1.6, 0.8, 1.4, -0.1, -0.12, 0.05]],
  [T.end, [-1.5, 0.65, 1.55, 0.25, -0.1, 0]],
];

function buildOverlay(app) {
  const el = document.createElement('div');
  el.className = 'ov';
  el.innerHTML = `
    <div class="cap"><div class="c1"></div><div class="c2"></div></div>
    <div class="read">
      <div class="row"><span>KHOÁ NÒNG</span><b class="r-open"></b></div>
      <div class="bar"><i class="b-open"></i></div>
      <div class="row"><span>GIẬT LÙI</span><b class="r-rec"></b></div>
      <div class="bar"><i class="b-rec"></i></div>
    </div>
    <svg class="lead"></svg>
    <div class="tag t-wedge">Khối chêm</div>
    <div class="tag t-lever">Tay mở khoá</div>
    <div class="tag t-chamber">Buồng đạn</div>
    <div class="src">Số đo: TM 9-1325 (1944) · chi tiết khoá nòng là mô phỏng</div>`;
  app.appendChild(el);
  const q = (s) => el.querySelector(s);
  return {el, q};
}

runSim(DEFAULTS, async ({canvas, hud, capture}) => {
  const st = createStage(canvas, hud, {bg: COL.bg, fov: 30, capture, bloom: {strength: 0.35, radius: 0.4, threshold: 0.85}, exposure: 1.05});
  const {renderer, scene, camera} = st;
  renderer.localClippingEnabled = true;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const pm = new THREE.PMREMGenerator(renderer);
  scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.55;
  scene.fog = new THREE.Fog(COL.bg, 4, 9);

  scene.add(new THREE.HemisphereLight('#c9d3dc', '#2a241c', 0.5));
  const key = new THREE.DirectionalLight('#ffe2bf', 2.4);
  key.position.set(-2.5, 4.0, 2.2);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, {left: -2.5, right: 2.5, top: 2.5, bottom: -2.5, near: 0.5, far: 12});
  key.shadow.bias = -0.0004;
  scene.add(key);
  const rim = new THREE.DirectionalLight('#9fb6d8', 0.9);
  rim.position.set(2.5, 1.5, -2.5);
  scene.add(rim);

  const floor = new THREE.Mesh(new THREE.CircleGeometry(30, 64), new THREE.MeshStandardMaterial({color: COL.floor, roughness: 0.95}));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.36;
  floor.receiveShadow = true;
  scene.add(floor);

  const gun = buildGun();
  scene.add(gun.root);
  const ov = buildOverlay(document.getElementById('app'));
  const lead = ov.q('.lead');
  const tags = {wedge: ov.q('.t-wedge'), lever: ov.q('.t-lever'), chamber: ov.q('.t-chamber')};

  const place = (name, anchor, show, dx, dy) => {
    const tag = tags[name];
    const p = st.project(anchor);
    tag.style.opacity = show;
    tag.style.transform = `translate(${p.x + dx}px, ${p.y + dy}px)`;
    return show > 0.01 ? `<line x1="${p.x}" y1="${p.y}" x2="${p.x + dx}" y2="${p.y + dy + 14}" opacity="${show}"/><circle cx="${p.x}" cy="${p.y}" r="3.5" opacity="${show}"/>` : '';
  };
  const win = (t, a, b) => Math.min(1, Math.max(0, Math.min((t - a) / 0.3, (b - t) / 0.3)));

  return {
    render(t) {
      const s = stateAt(t);
      const c = keyed(CAM, t);
      camera.position.set(c[0], c[1], c[2]);
      camera.lookAt(c[3], c[4], c[5]);
      gun.update(s, t);
      st.render();

      const cap = captionAt(t);
      ov.q('.c1').textContent = cap[1];
      ov.q('.c2').textContent = cap[2];
      ov.q('.cap').style.opacity = cap[0] === 0 ? 1 : Math.min(1, (t - cap[0]) / 0.35 + 0.15); // khung 0 là thumbnail
      ov.q('.r-open').textContent = s.open > 0.98 ? 'MỞ' : s.open < 0.02 ? 'ĐÓNG' : `${Math.round(s.open * 100)} %`;
      ov.q('.b-open').style.width = `${s.open * 100}%`;
      ov.q('.r-rec').textContent = `${s.recoil.toFixed(2).replace('.', ',')} m`;
      ov.q('.b-rec').style.width = `${(s.recoil / 1.067) * 100}%`;
      lead.innerHTML =
        place('wedge', gun.anchors.wedge, win(t, T.cut + 0.6, T.ram), 70, -90) +
        place('lever', gun.anchors.lever, win(t, T.open + 0.3, T.ram), 60, -70) +
        place('chamber', gun.anchors.chamber, win(t, T.ram + 0.4, T.pull), -40, -120);
      return {};
    },
    resize() {
      st.resize();
    },
  };
});
