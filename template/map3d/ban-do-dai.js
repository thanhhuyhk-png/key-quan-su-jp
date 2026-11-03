// Bản đồ chuẩn đài (V3): địa hình lòng chảo SRTM + ảnh vệ tinh, cùng three.js r149 và hậu kỳ với kho 3D
// (template/kho-quan-su/3d/engine/hau-ky.js), nên màu, hạt, bloom khớp các cảnh 3D và phim Karmen.
// Trang nạp trước: vendor/three.min.js, engine/kho3d.js, engine/hau-ky.js; rồi window.SHOT; rồi module này.
// Khác map3d.js (v11, three 0.186 ES module): lớp phủ có khung riêng quanh vùng cảnh (S.khung, ~2 m/px) thay vì cả
// thung lũng (~18 m/px); mũi tên tiến công thuôn có đầu lớn, bóng đổ; lớp phát sáng
// (chớp nổ, cứ điểm nhấp sáng) cộng vào ảnh HDR để bloom bắt. Mọi thứ thuần theo t.
//
// SHOT: duration, camera [{t, lat, lon, dist km, heading, pitch, fov}], khung {north, south, west, east},
//   nhin (bộ màu hau-ky), phoi, date [{text, from, to}], zones [{id, from, color}],
//   zones [{id, from, dur, to, do (giây phân khu chuyển đỏ: thất thủ)}],
//   routes [{path | tên hào trong places.js, from, dur, width m, ease, lui (thời điểm mờ bớt), to (tắt), kieu: 'hao' | 'vong'}],
//   points [{id | lat/lon/label/side, from, to, hit, sang: [giây nhấp sáng], label: false | chuỗi, labelFrom}],
//   flashes [{id, at, count, every, len, size m}], callouts (template/lib/callout.js, giây của trang), credit.
//   Điểm có noMarker: chỉ nhãn (tên phân khu).
import { W, H, clamp, lerp, prog, ease, keyframes, appear, landPunch, loadFonts, drawDateLabel, drawCredit, mount } from '../lib/common.js';
import { callout } from '../lib/callout.js';
import { PLACES, ZONES, TRENCHES, CREDIT_MAP3D } from './places.js';

const THREE = window.THREE, K3 = window.Kho3D;
const S = window.SHOT;
const EXAG = S.exag ?? 1.8;
const BASE = 470; // độ cao đáy lòng chảo (m), mốc y = 0
const R = 6378137;
const MAU = { ta: '#d6291c', taToi: '#5c0c06', dich: '#3d72b8', trang: '#f3efe6' };
const lin = (hex) => new THREE.Color(hex).convertSRGBToLinear();

// ---------- địa lý (đơn vị thế giới: km) ----------
const mx = (lon) => (R * lon * Math.PI) / 180;
const my = (lat) => R * Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360));
let V, RG, KS, MX0, MY0;
const world = (lat, lon) => ({ x: ((mx(lon) - MX0) * KS) / 1000, z: (-(my(lat) - MY0) * KS) / 1000 });
function sampleGrid(g, lat, lon) {
  const fx = (mx(lon) - mx(g.west)) / (mx(g.east) - mx(g.west));
  const fy = (my(g.north) - my(lat)) / (my(g.north) - my(g.south));
  if (fx < 0 || fx > 1 || fy < 0 || fy > 1) return null;
  const x = fx * (g.cols - 1), y = fy * (g.rows - 1);
  const i = Math.floor(x), j = Math.floor(y), a = x - i, b = y - j;
  const v = (ii, jj) => g.dem[Math.min(g.rows - 1, jj) * g.cols + Math.min(g.cols - 1, ii)];
  return lerp(lerp(v(i, j), v(i + 1, j), a), lerp(v(i, j + 1), v(i + 1, j + 1), a), b);
}
const elev = (lat, lon) => sampleGrid(V, lat, lon) ?? sampleGrid(RG, lat, lon) ?? BASE;
const yOf = (e) => ((e - BASE) * EXAG) / 1000;
const v3 = (lat, lon, lift = 0) => { const p = world(lat, lon); return new THREE.Vector3(p.x, yOf(elev(lat, lon)) + lift, p.z); };
async function loadGrid(name) {
  const meta = await (await fetch(new URL(`../data/${name}_meta.json`, import.meta.url))).json();
  meta.dem = new Float32Array(await (await fetch(new URL(`../data/${name}_dem.bin`, import.meta.url))).arrayBuffer());
  return meta;
}

// ---------- three.js + hậu kỳ ----------
const glCanvas = document.createElement('canvas'), ov = document.createElement('canvas');
ov.width = W; ov.height = H;
for (const c of [glCanvas, ov]) { c.style.position = 'absolute'; c.style.left = '0'; c.style.top = '0'; document.body.appendChild(c); }
const renderer = K3.mayVe(glCanvas, W, H);
renderer.shadowMap.enabled = false;
const hk = window.HAU_KY === false ? null : K3.hauKy(renderer, W, H);
const ctx = ov.getContext('2d');
const scene = new THREE.Scene();
const FOG = lin(S.fog ?? '#8c969a');
scene.background = FOG;
const camera = new THREE.PerspectiveCamera(40, W / H, 0.05, 900);
const SUN = (() => { const az = ((S.sunAz ?? 248) * Math.PI) / 180, el = ((S.sunEl ?? 24) * Math.PI) / 180; return new THREE.Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el)).normalize(); })();

// Địa hình: ảnh vệ tinh (giải mã sRGB → tuyến tính khi lấy mẫu), đổ bóng theo mặt trời, sương theo khoảng cách,
// lớp phủ màu (trộn alpha) và lớp phát sáng (cộng, nhân uSang) lấy theo toạ độ thế giới trong khung S.khung.
const VERT = `varying vec2 vUv; varying vec3 vN; varying vec3 vW;
void main(){ vUv = uv; vN = normal; vec4 w = modelMatrix * vec4(position,1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`;
const FRAG = `uniform sampler2D map, phu, sang; uniform float coPhu; uniform vec4 khung; uniform vec3 sun, fogC; uniform float fogD;
uniform vec4 hole; uniform float sat, dim, uSang;
varying vec2 vUv; varying vec3 vN; varying vec3 vW;
void main(){
  if (vW.x > hole.x && vW.x < hole.y && vW.z > hole.z && vW.z < hole.w) discard;
  vec3 c = texture2D(map, vUv).rgb;
  float l = dot(c, vec3(0.2126,0.7152,0.0722));
  c = mix(vec3(l), c, sat);
  float ndl = max(dot(normalize(vN), sun), 0.0);
  c *= clamp(1.0 + 1.4 * (ndl - sun.y), 0.42, 1.7);
  float lum = dot(c, vec3(0.333));
  c *= mix(vec3(0.84,0.92,1.06), vec3(1.10,1.02,0.86), smoothstep(0.02, 0.25, lum)); // bóng lạnh, sáng ấm
  c *= dim;
  if (coPhu > 0.5) {
    vec2 u = (vW.xz - khung.xy) / (khung.zw - khung.xy);
    if (u.x > 0.0 && u.x < 1.0 && u.y > 0.0 && u.y < 1.0) {
      u.y = 1.0 - u.y;
      vec4 o = texture2D(phu, u); c = mix(c, o.rgb, o.a);
      c += texture2D(sang, u).rgb * uSang;
    }
  }
  float d = length(vW - cameraPosition);
  c = mix(c, fogC, clamp(1.0 - exp(-pow(d * fogD, 1.6)), 0.0, 0.92));
  gl_FragColor = vec4(c, 1.0);
}`;
let KHUNG; // [x0, z0, x1, z1] km
const U = { phu: { value: null }, sang: { value: null }, khung: { value: new THREE.Vector4() }, uSang: { value: S.sangPhu ?? 1 } };
function terrainMesh(g, tex, coPhu, hole, drop) {
  const { rows, cols } = g;
  const pos = new Float32Array(rows * cols * 3), uv = new Float32Array(rows * cols * 2);
  const w0 = mx(g.west), w1 = mx(g.east), n0 = my(g.north), n1 = my(g.south);
  for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
    const k = j * cols + i;
    pos[k * 3] = ((lerp(w0, w1, i / (cols - 1)) - MX0) * KS) / 1000;
    pos[k * 3 + 1] = yOf(g.dem[k]) - drop;
    pos[k * 3 + 2] = (-(lerp(n0, n1, j / (rows - 1)) - MY0) * KS) / 1000;
    uv[k * 2] = i / (cols - 1); uv[k * 2 + 1] = 1 - j / (rows - 1);
  }
  const idx = new Uint32Array((rows - 1) * (cols - 1) * 6);
  let p = 0;
  for (let j = 0; j < rows - 1; j++) for (let i = 0; i < cols - 1; i++) {
    const a = j * cols + i, b = a + 1, c = a + cols, d = c + 1;
    idx.set([a, c, b, b, c, d], p); p += 6;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('uv', new THREE.BufferAttribute(uv, 2));
  geo.setIndex(new THREE.BufferAttribute(idx, 1));
  geo.computeVertexNormals();
  const mat = new THREE.ShaderMaterial({
    vertexShader: VERT, fragmentShader: FRAG,
    uniforms: { map: { value: tex }, phu: U.phu, sang: U.sang, khung: U.khung, uSang: U.uSang, coPhu: { value: coPhu ? 1 : 0 },
      sun: { value: SUN }, fogC: { value: FOG }, fogD: { value: S.fogDensity ?? 0.0075 }, hole: { value: hole },
      sat: { value: S.saturation ?? 0.55 }, dim: { value: S.exposure ?? 1 } },
  });
  return new THREE.Mesh(geo, mat);
}

// ---------- lớp phủ (canvas theo khung S.khung) ----------
const phu = document.createElement('canvas'), sang = document.createElement('canvas');
let pc, sc, phuTex, sangTex, MPX; // MPX: mét mỗi px lớp phủ
function px(lat, lon) {
  const p = world(lat, lon);
  return [((p.x - KHUNG[0]) / (KHUNG[2] - KHUNG[0])) * phu.width, ((p.z - KHUNG[1]) / (KHUNG[3] - KHUNG[1])) * phu.height];
}
function smoothPath(pts, n = 12) {
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
    for (let s = 0; s < n; s++) {
      const t = s / n, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map((d) => 0.5 * (2 * p1[d] + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2 + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3)));
    }
  }
  out.push(pts[pts.length - 1]);
  return out;
}
// Đường theo px lớp phủ, kèm độ dài tích luỹ.
function duongPx(pts) {
  const p = pts.map((q) => px(...q)), len = [0];
  for (let i = 1; i < p.length; i++) len.push(len[i - 1] + Math.hypot(p[i][0] - p[i - 1][0], p[i][1] - p[i - 1][1]));
  return { p, len, L: len[len.length - 1] };
}
// Điểm và hướng tại độ dài s trên đường.
function tai(d, s) {
  let i = 1;
  while (i < d.p.length - 1 && d.len[i] < s) i++;
  const a = d.p[i - 1], b = d.p[i], seg = d.len[i] - d.len[i - 1] || 1, k = clamp((s - d.len[i - 1]) / seg);
  const ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
  return [lerp(a[0], b[0], k), lerp(a[1], b[1], k), ang];
}
// Mũi tên tiến công kiểu bản đồ quân sự: thân thuôn (đuôi 45% → đủ bề rộng), đầu tam giác 2,3× bề rộng.
function hinhMuiTen(d, f, w) {
  const dau = Math.min(w * 2.1, d.L * f * 0.6), sDau = d.L * f, sThan = Math.max(0, sDau - dau);
  const trai = [], phai = [], n = Math.max(2, Math.ceil(sThan / 4));
  for (let i = 0; i <= n; i++) {
    const s = (sThan * i) / n, [x, y, a] = tai(d, s);
    const r = (w / 2) * lerp(0.6, 1, ease.out(clamp(s / Math.max(1, d.L * 0.7))));
    trai.push([x - Math.sin(a) * r, y + Math.cos(a) * r]); phai.push([x + Math.sin(a) * r, y - Math.cos(a) * r]);
  }
  const [cx, cy, ca] = tai(d, sThan), [tx, ty] = tai(d, sDau), rd = w * 1.15;
  return { than: [...trai, [cx - Math.sin(ca) * rd, cy + Math.cos(ca) * rd], [tx, ty], [cx + Math.sin(ca) * rd, cy - Math.cos(ca) * rd], ...phai.reverse()], dinh: [tx, ty, ca] };
}
const veDa = (g, pts) => { g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.closePath(); };

// Hào vây lấn ('hao'): đường răng cưa đỏ viền tối; vòng vây ('vong'): nét đỏ đứt dày. Vẽ dần theo f.
function veHao(r, f, m) {
  const L = r.d.L * f, amp = m(r.amp ?? 25), buoc = amp * 1.6, pts = [];
  if (L < buoc) return;
  const vong = r.kieu === 'vong', b = vong ? 6 : buoc;
  for (let s = 0, lat = 1; s <= L; s += b, lat = -lat) { const [x, y, a] = tai(r.d, s), o = vong ? 0 : amp * lat; pts.push([x - Math.sin(a) * o, y + Math.cos(a) * o]); }
  pc.save(); pc.lineJoin = vong ? 'round' : 'miter'; if (vong) pc.setLineDash([m(420), m(220)]); pc.beginPath(); pts.forEach(([x, y], i) => (i ? pc.lineTo(x, y) : pc.moveTo(x, y)));
  pc.globalAlpha = 1 - 0.35 * ease.inOut(prog(r.t, r.lui ?? 1e9, 0.6));
  pc.strokeStyle = MAU.taToi; pc.lineWidth = m(r.width ?? 45) + m(16); pc.stroke();
  pc.strokeStyle = MAU.ta; pc.lineWidth = m(r.width ?? 45); pc.stroke(); pc.restore();
}
const resolvePt = (o) => (o.id ? { ...PLACES[o.id], ...o, label: o.label ?? PLACES[o.id].label } : o);
let routes = [];
function veLopPhu(t) {
  pc.clearRect(0, 0, phu.width, phu.height); sc.clearRect(0, 0, sang.width, sang.height);
  const m = (v) => v / MPX; // mét → px
  for (const z of S.zones || []) {
    const a = ease.out(prog(t, z.from ?? 0, z.dur ?? 0.8)) * (1 - prog(t, z.to ?? 1e9, 0.5));
    if (a <= 0) continue;
    const pts = smoothPath([...ZONES[z.id], ZONES[z.id][0]], 8).map((q) => px(...q));
    const kDo = z.do != null ? ease.inOut(prog(t, z.do, 0.6)) : 0;
    pc.save(); pc.globalAlpha = a; veDa(pc, pts);
    if (kDo < 1) { pc.globalAlpha = a * (1 - kDo); pc.fillStyle = z.color ?? 'rgba(61,114,184,0.30)'; pc.fill(); }
    if (kDo > 0) { pc.globalAlpha = a * kDo; pc.fillStyle = 'rgba(214,41,28,0.42)'; pc.fill(); }
    pc.globalAlpha = a;
    pc.setLineDash([m(70), m(40)]); pc.lineWidth = m(18); pc.strokeStyle = 'rgba(214,226,242,0.85)'; pc.stroke(); pc.restore();
  }
  for (const r of routes) {
    const f = ease[r.ease ?? 'inOut'](prog(t, r.from ?? 0, r.dur ?? 2));
    if (f <= 0.01) continue;
    r.t = t;
    if (r.kieu === 'hao' || r.kieu === 'vong') { veHao(r, f, m); continue; }
    const w = m(r.width ?? 300), mu = hinhMuiTen(r.d, f, w);
    const mo = (1 - 0.35 * ease.inOut(prog(t, r.lui ?? 1e9, 0.6))) * (1 - ease.inOut(prog(t, r.to ?? 1e9, 0.5))); // mờ bớt khi trận sau bắt đầu, tắt hẳn ở to
    if (mo <= 0) continue;
    // bóng đổ lên địa hình (lệch theo hướng nắng), viền tối, thân đỏ, sống sáng giữa thân
    pc.save(); pc.globalAlpha = 0.45 * mo; pc.filter = `blur(${m(30)}px)`; pc.translate(m(-45), m(30)); veDa(pc, mu.than); pc.fillStyle = '#000'; pc.fill(); pc.restore();
    pc.save(); pc.globalAlpha = mo; veDa(pc, mu.than); pc.lineJoin = 'round'; pc.lineWidth = m(26); pc.strokeStyle = MAU.taToi; pc.stroke();
    const [x0, y0] = r.d.p[0], [x1, y1] = mu.dinh, gr = pc.createLinearGradient(x0, y0, x1, y1);
    gr.addColorStop(0, 'rgba(176,28,18,0.82)'); gr.addColorStop(0.5, MAU.ta); gr.addColorStop(1, '#ec3a24');
    pc.fillStyle = gr; pc.fill();
    pc.clip(); pc.globalAlpha = 0.35 * mo; pc.lineWidth = w * 0.22; pc.lineCap = 'round'; pc.strokeStyle = '#ff9a7a';
    pc.beginPath(); const sMax = r.d.L * f - w * 2.1; for (let s = 0; s <= sMax; s += 4) { const [x, y] = tai(r.d, s); s ? pc.lineTo(x, y) : pc.moveTo(x, y); } pc.stroke();
    pc.restore();
  }
  // cứ điểm nhấp sáng: vầng sáng trên đất + vòng lan, mỗi nhịp 0,5 s
  for (const o of S.points || []) {
    const p = resolvePt(o);
    for (const t0 of o.sang || []) {
      const u = t - t0; if (u < 0 || u > 1.6) continue;
      const [x, y] = px(p.lat, p.lon), nh = Math.pow(Math.max(0, Math.sin((u / 0.5) * Math.PI)), 2) * (1 - u / 1.6);
      const g = sc.createRadialGradient(x, y, 0, x, y, m(160));
      g.addColorStop(0, `rgba(255,190,110,${0.4 * nh})`); g.addColorStop(1, 'rgba(255,150,60,0)');
      sc.fillStyle = g; sc.beginPath(); sc.arc(x, y, m(160), 0, Math.PI * 2); sc.fill();
      const ph = (u % 0.5) / 0.5;
      pc.save(); pc.globalAlpha = (1 - ph) * (1 - u / 1.6); pc.strokeStyle = '#ffe7a8'; pc.lineWidth = m(20);
      pc.beginPath(); pc.arc(x, y, m(90 + 260 * ph), 0, Math.PI * 2); pc.stroke(); pc.restore();
    }
  }
  // chớp nổ: lõi trắng, quầng cam, tắt nhanh (vào lớp phát sáng để bloom bắt)
  for (const fl of S.flashes || []) {
    const p = resolvePt(fl), [x, y] = px(p.lat, p.lon);
    for (let n = 0; n < (fl.count ?? 1); n++) {
      const k = (t - fl.at - n * (fl.every ?? 0.3)) / (fl.len ?? 0.5);
      if (k < 0 || k > 1) continue;
      const a = Math.pow(1 - k, 2), rr = m(fl.size ?? 120) * (0.4 + 0.8 * k), ox = m(60) * Math.sin(n * 2.4), oy = m(60) * Math.cos(n * 1.7);
      const g = sc.createRadialGradient(x + ox, y + oy, 0, x + ox, y + oy, rr);
      g.addColorStop(0, `rgba(255,250,230,${a})`); g.addColorStop(0.3, `rgba(255,140,50,${a * 0.8})`); g.addColorStop(1, 'rgba(255,80,20,0)');
      sc.fillStyle = g; sc.beginPath(); sc.arc(x + ox, y + oy, rr, 0, Math.PI * 2); sc.fill();
    }
  }
  phuTex.needsUpdate = true; sangTex.needsUpdate = true;
}

// ---------- lớp 2D trên màn hình ----------
function project(p3) {
  const v = p3.clone().project(camera);
  return { x: (v.x * 0.5 + 0.5) * W, y: (-v.y * 0.5 + 0.5) * H, ok: v.z < 1 && v.z > -1 };
}
function nhan(x, y, text, { size = 30, alpha = 1, scale = 1, accent = MAU.ta } = {}) {
  ctx.save(); ctx.globalAlpha = alpha;
  ctx.translate(x, y); ctx.scale(scale, scale); ctx.translate(-x, -y);
  ctx.font = `600 ${size}px Oswald`; ctx.letterSpacing = '2px';
  const bw = ctx.measureText(text).width + size * 0.9, bh = size * 1.45;
  const bx = clamp(x - bw / 2, 20, W - bw - 20), by = y - bh;
  ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 14; ctx.fillStyle = 'rgba(10,9,8,0.88)'; ctx.fillRect(bx, by, bw, bh);
  ctx.shadowBlur = 0; ctx.fillStyle = accent; ctx.fillRect(bx, by, 6, bh);
  ctx.fillStyle = MAU.trang; ctx.textBaseline = 'middle'; ctx.textAlign = 'center'; ctx.fillText(text, bx + bw / 2 + 3, by + bh * 0.53);
  ctx.restore();
}
// Ký hiệu cứ điểm địch: ô vuông xanh viền trắng; bị tiêu diệt / bức hàng: đỏ có dấu X.
function kyHieu(x, y, alpha, hit, scale) {
  ctx.save(); ctx.globalAlpha = alpha; ctx.translate(x, y); ctx.scale(scale, scale);
  ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 8;
  ctx.fillStyle = hit ? MAU.ta : MAU.dich; ctx.fillRect(-11, -11, 22, 22);
  ctx.shadowBlur = 0; ctx.strokeStyle = MAU.trang; ctx.lineWidth = 3; ctx.strokeRect(-11, -11, 22, 22);
  if (hit) { ctx.lineWidth = 3.5; ctx.beginPath(); ctx.moveTo(-6, -6); ctx.lineTo(6, 6); ctx.moveTo(6, -6); ctx.lineTo(-6, 6); ctx.stroke(); }
  ctx.restore();
}

function renderFrame(t) {
  t = clamp(t, 0, S.duration);
  const c = keyframes(S.camera, t);
  const tgt = v3(c.lat, c.lon);
  const h = (c.heading * Math.PI) / 180, p = (c.pitch * Math.PI) / 180;
  camera.position.copy(tgt).addScaledVector(new THREE.Vector3(Math.sin(h), 0, -Math.cos(h)), -Math.cos(p) * c.dist).add(new THREE.Vector3(0, Math.sin(p) * c.dist, 0));
  camera.fov = c.fov ?? 40; camera.updateProjectionMatrix(); camera.lookAt(tgt); camera.updateMatrixWorld();
  veLopPhu(t);
  const k = Math.round(t * 24);
  if (hk) hk.ve(scene, camera, k + (S.khungDau ?? 0), Object.assign({ phoi: S.phoi ?? 1 }, S.nhin));
  else { renderer.setRenderTarget(null); renderer.render(scene, camera); }

  ctx.clearRect(0, 0, W, H);
  for (const o of S.points || []) {
    const p = resolvePt(o), f0 = o.from ?? 0, to = o.to ?? 1e9;
    const mk = appear(t, f0, { dur: 0.45, to, s0: 0.2 });
    if (mk.a <= 0) continue;
    const q = project(v3(p.lat, p.lon, 0.02));
    if (!q.ok || q.x < -40 || q.x > W + 40 || q.y < -40 || q.y > H + 40) continue;
    const hit = o.hit != null && t >= o.hit;
    const nhip = (o.sang || []).reduce((s, t0) => s + landPunch(t, t0, 0.5, 0.35) + landPunch(t, t0 + 0.5, 0.5, 0.25), 0);
    if (!o.noMarker) kyHieu(q.x, q.y, mk.a, hit, mk.s + nhip + (o.hit != null ? landPunch(t, o.hit, 0.35, 0.5) : 0));
    if (o.label === false) continue;
    const lf = o.labelFrom ?? f0, lift = o.lift ?? 64;
    const g = ease.expoOut(prog(t, lf, 0.3)) * (1 - ease.in(prog(t, to, 0.3)));
    if (g > 0 && lift > 20 && !o.noMarker) { ctx.save(); ctx.globalAlpha = mk.a; ctx.strokeStyle = 'rgba(243,239,230,0.9)'; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(q.x, q.y - 14); ctx.lineTo(q.x, q.y - 14 - (lift - 18) * g); ctx.stroke(); ctx.restore(); }
    const L = appear(t, lf + 0.12, { dur: 0.5, to, rise: 10 });
    if (L.a > 0) nhan(q.x + (o.dx ?? 0), q.y - lift + L.y, o.label ?? p.label, { size: o.size ?? 34, alpha: L.a, scale: L.s });
  }
  for (const d of [].concat(S.date || [])) {
    if (t >= (d.from ?? 0) - 0.01) drawDateLabel(ctx, d.text, ease.out(prog(t, d.from ?? 0.2, 0.5)) * (1 - prog(t, d.to ?? 1e9, 0.3)));
  }
  for (const c of S.callouts || []) callout(ctx, t, c);
  drawCredit(ctx, S.credit ?? CREDIT_MAP3D, 1);
}

async function init() {
  [V, RG] = await Promise.all([loadGrid('valley'), loadGrid('region')]);
  const latC = (V.north + V.south) / 2, lonC = (V.west + V.east) / 2;
  KS = Math.cos((latC * Math.PI) / 180); MX0 = mx(lonC); MY0 = my(latC);
  const loader = new THREE.TextureLoader();
  const [tv, tr] = await Promise.all([loader.loadAsync(new URL('../data/valley_s2.jpg', import.meta.url).href), loader.loadAsync(new URL('../data/region_s2.jpg', import.meta.url).href)]);
  for (const tx of [tv, tr]) { tx.encoding = THREE.sRGBEncoding; tx.anisotropy = renderer.capabilities.getMaxAnisotropy(); }
  // khung lớp phủ: S.khung (mặc định quanh lòng chảo), canvas tối đa 4096 px cạnh dài
  const kh = S.khung ?? { north: 21.45, south: 21.32, west: 102.95, east: 103.08 };
  const a = world(kh.north, kh.west), b = world(kh.south, kh.east);
  KHUNG = [a.x, a.z, b.x, b.z];
  const rw = KHUNG[2] - KHUNG[0], rh = KHUNG[3] - KHUNG[1], sc0 = 4096 / Math.max(rw, rh);
  phu.width = sang.width = Math.round(rw * sc0); phu.height = sang.height = Math.round(rh * sc0);
  MPX = (rw * 1000) / phu.width;
  pc = phu.getContext('2d'); sc = sang.getContext('2d');
  phuTex = new THREE.CanvasTexture(phu); phuTex.encoding = THREE.sRGBEncoding; phuTex.anisotropy = renderer.capabilities.getMaxAnisotropy();
  sangTex = new THREE.CanvasTexture(sang); sangTex.encoding = THREE.sRGBEncoding;
  U.phu.value = phuTex; U.sang.value = sangTex; U.khung.value.set(...KHUNG);
  const va = world(V.north, V.west), vb = world(V.south, V.east), inset = 0.05;
  scene.add(terrainMesh(V, tv, true, new THREE.Vector4(1e9, -1e9, 0, 0), 0));
  scene.add(terrainMesh(RG, tr, false, new THREE.Vector4(va.x + inset, vb.x - inset, va.z + inset, vb.z - inset), 0.004));
  routes = (S.routes || []).map((r) => ({ ...r, d: duongPx(smoothPath(typeof r.path === 'string' ? TRENCHES[r.path] : r.path, r.kieu === 'hao' ? 6 : 10)) }));
  await loadFonts();
  mount(S.duration, renderFrame);
}
init();
