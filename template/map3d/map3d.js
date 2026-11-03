// Khối map3d: địa hình lòng chảo 3D (three.js) + lớp phủ bám địa hình + nhãn chiếu từ 3D + biểu tượng bộ đội.
// Cấu hình: window.SHOT (xem README). Hàm renderFrame(t) thuần theo t.
import * as THREE from '../node_modules/three/build/three.module.js';
import { W, H, clamp, lerp, prog, ease, keyframes, rng, appear, landPunch, loadFonts, drawDateLabel, drawCredit, mount } from '../lib/common.js';
import { drawTroopGroup } from '../lib/troops.js';
import { PLACES, ZONES, ROUTE_KEO_PHAO, TRENCHES, CREDIT_MAP3D, CREDIT_MAP3D_AMS } from './places.js';

const S = window.SHOT;
const EXAG = S.exag ?? 1.8;
const BASE = 470; // độ cao đáy lòng chảo (m), làm mốc y = 0
const R = 6378137;
const COLORS = { ta: '#d8382a', dich: '#5d86b8', vang: '#e5a93b', trang: '#f3efe6' };
const NAMED_PATHS = { 'keo-phao': ROUTE_KEO_PHAO, ...TRENCHES };

// ---------- địa lý ----------
const mx = (lon) => (R * lon * Math.PI) / 180;
const my = (lat) => R * Math.log(Math.tan(Math.PI / 4 + (lat * Math.PI) / 360));
let V, RG, K, MX0, MY0; // meta valley/region, hệ số tỉ lệ, gốc
const world = (lat, lon) => ({ x: ((mx(lon) - MX0) * K) / 1000, z: (-(my(lat) - MY0) * K) / 1000 });

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
function v3(lat, lon, lift = 0) { const p = world(lat, lon); return new THREE.Vector3(p.x, yOf(elev(lat, lon)) + lift, p.z); }

async function loadGrid(name) {
  const meta = await (await fetch(`../data/${name}_meta.json`)).json();
  meta.dem = new Float32Array(await (await fetch(`../data/${name}_dem.bin`)).arrayBuffer());
  return meta;
}

// ---------- three.js ----------
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H);
renderer.outputColorSpace = THREE.SRGBColorSpace;
const glCanvas = renderer.domElement;
const ov = document.createElement('canvas'); ov.width = W; ov.height = H;
for (const c of [glCanvas, ov]) { c.style.position = 'absolute'; c.style.left = '0'; c.style.top = '0'; document.body.appendChild(c); }
const ctx = ov.getContext('2d');
const scene = new THREE.Scene();
const FOG = new THREE.Color(S.fog ?? '#8c969a');
scene.background = FOG;
const camera = new THREE.PerspectiveCamera(40, W / H, 0.05, 900);

const SUN = (() => { const az = ((S.sunAz ?? 248) * Math.PI) / 180, el = ((S.sunEl ?? 24) * Math.PI) / 180; return new THREE.Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), -Math.cos(az) * Math.cos(el)).normalize(); })();

const VERT = `
varying vec2 vUv; varying vec3 vN; varying vec3 vW;
void main(){ vUv = uv; vN = normal; vec4 w = modelMatrix * vec4(position,1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }`;
const FRAG = `
uniform sampler2D map; uniform sampler2D over; uniform float hasOver; uniform vec3 sun; uniform vec3 fogC; uniform float fogD;
uniform vec4 hole; uniform float sat; uniform float dim;
uniform sampler2D amsTex; uniform sampler2D amsMask; uniform vec4 amsRect; uniform float hasAms; uniform vec4 amsLook; uniform vec3 amsTint; uniform float amsOut;
varying vec2 vUv; varying vec3 vN; varying vec3 vW;
void main(){
  if (vW.x > hole.x && vW.x < hole.y && vW.z > hole.z && vW.z < hole.w) discard;
  vec3 c = texture2D(map, vUv).rgb;
  float l = dot(c, vec3(0.299,0.587,0.114));
  c = mix(vec3(l), c, sat);
  c = (c - 0.42) * 1.12 + 0.44;
  vec3 n = normalize(vN);
  float ndl = max(dot(n, sun), 0.0);
  float shade = clamp(1.05 + 1.3 * (ndl - sun.y), 0.5, 1.6);
  c *= shade;
  float lum = dot(c, vec3(0.333));
  c *= mix(vec3(0.86,0.93,1.04), vec3(1.12,1.02,0.84), smoothstep(0.08, 0.55, lum)); // bóng lạnh, sáng ấm
  c *= dim;
  if (hasAms > 0.5) {
    // nền AMS: bản đồ đã nắn phủ theo toạ độ thế giới (amsRect = xmin, xmax, zBắc, zNam); ngoài tờ giữ ảnh vệ tinh
    vec2 ua = vec2((vW.x - amsRect.x) / (amsRect.y - amsRect.x), 1.0 - (vW.z - amsRect.z) / (amsRect.w - amsRect.z));
    vec2 uc = clamp(ua, 0.0, 1.0);                    // lấy mẫu ngoài mọi nhánh để đạo hàm UV (mipmap) đồng nhất
    vec3 a = texture2D(amsTex, uc).rgb;
    float m = texture2D(amsMask, uc).r * step(0.0, ua.x) * step(ua.x, 1.0) * step(0.0, ua.y) * step(ua.y, 1.0);
    float la = dot(a, vec3(0.299,0.587,0.114));
    a = mix(vec3(la), a, amsLook.x) * amsTint;        // amsLook: x bão hoà, y giữ khối núi, z độ sáng
    a *= mix(1.0, shade, amsLook.y) * amsLook.z;
    c = mix(c * amsOut, a, m * amsLook.w);            // ngoài tờ: ảnh vệ tinh nâng sáng cho đỡ lệch với bản đồ
  }
  if (hasOver > 0.5) { vec4 o = texture2D(over, vUv); c = mix(c, o.rgb, o.a); }
  float d = length(vW - cameraPosition);
  float f = 1.0 - exp(-pow(d * fogD, 1.6));
  c = mix(c, fogC, clamp(f, 0.0, 0.92));
  gl_FragColor = vec4(c, 1.0);
  #include <colorspace_fragment>
}`;

function terrainMesh(g, tex, over, hole, drop, ams) {
  const { rows, cols } = g;
  const pos = new Float32Array(rows * cols * 3), uv = new Float32Array(rows * cols * 2);
  const w0 = mx(g.west), w1 = mx(g.east), n0 = my(g.north), n1 = my(g.south);
  for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
    const k = j * cols + i;
    pos[k * 3] = ((lerp(w0, w1, i / (cols - 1)) - MX0) * K) / 1000;
    pos[k * 3 + 1] = yOf(g.dem[k]) - drop;
    pos[k * 3 + 2] = (-(lerp(n0, n1, j / (rows - 1)) - MY0) * K) / 1000;
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
    uniforms: { map: { value: tex }, over: { value: over }, hasOver: { value: over ? 1 : 0 }, sun: { value: SUN }, fogC: { value: FOG }, fogD: { value: S.fogDensity ?? 0.0075 },
      hole: { value: hole }, sat: { value: S.saturation ?? 0.5 }, dim: { value: S.exposure ?? 1.15 },
      hasAms: { value: ams ? 1 : 0 }, amsTex: { value: ams?.tex ?? null }, amsMask: { value: ams?.mask ?? null }, amsRect: { value: ams?.rect ?? new THREE.Vector4() },
      amsLook: { value: ams?.look ?? new THREE.Vector4(1, 0, 1, 0) }, amsTint: { value: ams?.tint ?? new THREE.Vector3(1, 1, 1) }, amsOut: { value: ams?.out ?? 1 } },
  });
  return new THREE.Mesh(geo, mat);
}

// ---------- lớp phủ bám địa hình (canvas theo toạ độ ảnh valley) ----------
const drape = document.createElement('canvas');
let dctx, drapeTex;
const dpx = (lat, lon) => [((mx(lon) - mx(V.west)) / (mx(V.east) - mx(V.west))) * drape.width, ((my(V.north) - my(lat)) / (my(V.north) - my(V.south))) * drape.height];
const mPerPx = () => (((mx(V.east) - mx(V.west)) * K) / drape.width);

function smoothPath(pts, n = 12) {
  // Catmull-Rom trên [lat, lon]
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
function withLength(pts) {
  const len = [0];
  for (let i = 1; i < pts.length; i++) { const a = world(...pts[i - 1]), b = world(...pts[i]); len.push(len[i - 1] + Math.hypot(b.x - a.x, b.z - a.z)); }
  return { pts, len };
}
function cut(path, f) {
  const L = f * path.len[path.len.length - 1];
  const out = [path.pts[0]];
  for (let i = 1; i < path.pts.length; i++) {
    if (path.len[i] <= L) { out.push(path.pts[i]); continue; }
    const k = (L - path.len[i - 1]) / (path.len[i] - path.len[i - 1]);
    const a = path.pts[i - 1], b = path.pts[i];
    out.push([lerp(a[0], b[0], k), lerp(a[1], b[1], k)]);
    break;
  }
  return out;
}
function strokePx(pts, width, color, { dash = null, glow = 0, alpha = 1 } = {}) {
  if (pts.length < 2) return;
  dctx.save();
  dctx.globalAlpha = alpha;
  dctx.lineCap = 'round'; dctx.lineJoin = 'round';
  dctx.beginPath();
  pts.forEach((p, i) => { const [x, y] = dpx(...p); i ? dctx.lineTo(x, y) : dctx.moveTo(x, y); });
  if (glow) { dctx.shadowColor = color; dctx.shadowBlur = glow; }
  dctx.strokeStyle = 'rgba(10,8,6,0.55)'; dctx.lineWidth = width + 3; if (dash) dctx.setLineDash(dash); dctx.stroke();
  dctx.strokeStyle = color; dctx.lineWidth = width; dctx.stroke();
  dctx.restore();
}
function arrowHead(pts, size, color, alpha = 1) {
  if (pts.length < 2) return;
  const [x1, y1] = dpx(...pts[pts.length - 1]);
  let j = pts.length - 2, x0, y0;
  do { [x0, y0] = dpx(...pts[j]); j--; } while (j >= 0 && Math.hypot(x1 - x0, y1 - y0) < size * 0.6);
  const a = Math.atan2(y1 - y0, x1 - x0);
  dctx.save(); dctx.globalAlpha = alpha; dctx.fillStyle = color; dctx.strokeStyle = 'rgba(10,8,6,0.6)'; dctx.lineWidth = 2;
  dctx.beginPath(); dctx.moveTo(x1 + Math.cos(a) * size * 0.5, y1 + Math.sin(a) * size * 0.5);
  dctx.lineTo(x1 + Math.cos(a + 2.5) * size, y1 + Math.sin(a + 2.5) * size);
  dctx.lineTo(x1 + Math.cos(a - 2.5) * size, y1 + Math.sin(a - 2.5) * size);
  dctx.closePath(); dctx.stroke(); dctx.fill(); dctx.restore();
}
function zigzag(pts, amp) {
  // hào giao thông: đường gấp khúc răng cưa theo toạ độ ảnh
  const px = pts.map((p) => dpx(...p));
  const out = [];
  let acc = 0, flip = 1;
  for (let i = 1; i < px.length; i++) {
    const [x0, y0] = px[i - 1], [x1, y1] = px[i];
    const L = Math.hypot(x1 - x0, y1 - y0); if (L < 1e-6) continue;
    const nx = -(y1 - y0) / L, ny = (x1 - x0) / L;
    for (let s = 0; s < L; s += 1) { acc += 1; if (acc >= amp * 1.6) { acc = 0; flip = -flip; out.push([x0 + ((x1 - x0) * s) / L + nx * amp * flip, y0 + ((y1 - y0) * s) / L + ny * amp * flip]); } }
  }
  out.push(px[px.length - 1]);
  return out;
}

const resolvePt = (o) => (o.id ? { ...PLACES[o.id], ...o } : o);
const resolvePath = (r) => (typeof r.path === 'string' ? NAMED_PATHS[r.path] : r.path);

let routes = [];
function drawDrape(t) {
  const m = mPerPx();
  dctx.clearRect(0, 0, drape.width, drape.height);
  for (const z of S.zones || []) {
    // vùng: viền nét đứt vẽ dần (expo), nền tô đậm dần theo sau
    const f0 = z.from ?? 0, d = z.dur ?? 0.9;
    const out = 1 - ease.in(prog(t, z.to ?? 1e9, 0.5));
    const kLine = ease.expoOut(prog(t, f0, d));
    const kFill = ease.out(prog(t, f0 + d * 0.35, d));
    if (kLine <= 0 || out <= 0) continue;
    const pts = smoothPath([...ZONES[z.id], ZONES[z.id][0]], 8);
    dctx.save(); dctx.globalAlpha = kFill * out; dctx.beginPath();
    pts.forEach((p, i) => { const [x, y] = dpx(...p); i ? dctx.lineTo(x, y) : dctx.moveTo(x, y); });
    dctx.closePath(); dctx.fillStyle = z.color ?? 'rgba(93,134,184,0.38)'; dctx.fill(); dctx.restore();
    const part = pts.slice(0, Math.max(2, Math.ceil(pts.length * kLine)));
    dctx.save(); dctx.globalAlpha = out; dctx.beginPath();
    part.forEach((p, i) => { const [x, y] = dpx(...p); i ? dctx.lineTo(x, y) : dctx.moveTo(x, y); });
    dctx.setLineDash([14, 8]); dctx.lineWidth = 3; dctx.strokeStyle = z.stroke ?? 'rgba(220,232,245,0.9)'; dctx.stroke(); dctx.restore();
  }
  for (const r of routes) {
    const f = ease[r.ease ?? 'inOut'](prog(t, r.from ?? 0, r.dur ?? 3));
    const a = 1 - prog(t, r.to ?? 1e9, 0.6);
    if (f <= 0 || a <= 0) continue;
    const pts = cut(r.path, f);
    const w = (r.width ?? (r.style === 'attack' ? 140 : 70)) / m;
    if (r.style === 'trench') {
      const zz = zigzag(pts, (r.amp ?? 22) / m);
      dctx.save(); dctx.globalAlpha = a; dctx.lineJoin = 'miter'; dctx.beginPath(); zz.forEach((p, i) => (i ? dctx.lineTo(...p) : dctx.moveTo(...p)));
      dctx.strokeStyle = 'rgba(30,18,10,0.8)'; dctx.lineWidth = w + 3; dctx.stroke(); dctx.strokeStyle = r.color ?? '#b8582e'; dctx.lineWidth = w; dctx.stroke(); dctx.restore();
    } else {
      const color = r.color ?? (r.style === 'attack' ? COLORS.ta : COLORS.vang);
      strokePx(pts, w, color, { dash: r.dash ?? (r.style === 'route' ? [w * 2.2, w * 1.2] : null), glow: r.glow ?? 5, alpha: a });
      if (r.arrow !== false) arrowHead(pts, w * (r.style === 'attack' ? 3.2 : 4.5), color, a);
    }
  }
  for (const g of S.rings || []) {
    const p = resolvePt(g);
    const a = ease.out(prog(t, g.from ?? 0, 0.5)) * (1 - prog(t, g.to ?? 1e9, 0.5));
    if (a <= 0) continue;
    const [x, y] = dpx(p.lat, p.lon), rad = (g.radius ?? 260) / m;
    for (let k = 0; k < 3; k++) {
      const ph = ((t - (g.from ?? 0)) * 0.7 + k / 3) % 1;
      dctx.save(); dctx.globalAlpha = a * (1 - ph); dctx.strokeStyle = g.color ?? COLORS.vang; dctx.lineWidth = Math.max(2, 18 / m); dctx.shadowColor = g.color ?? COLORS.vang; dctx.shadowBlur = 3;
      dctx.beginPath(); dctx.arc(x, y, rad * (0.4 + ph), 0, Math.PI * 2); dctx.stroke(); dctx.restore();
    }
    dctx.save(); dctx.globalAlpha = a; dctx.strokeStyle = g.color ?? COLORS.vang; dctx.lineWidth = Math.max(2.5, 24 / m); dctx.beginPath(); dctx.arc(x, y, rad * 0.4, 0, Math.PI * 2); dctx.stroke(); dctx.restore();
  }
  drapeTex.needsUpdate = true;
}

// ---------- 2D phủ trên màn hình ----------
function project(p3) {
  const v = p3.clone().project(camera);
  return { x: (v.x * 0.5 + 0.5) * W, y: (-v.y * 0.5 + 0.5) * H, ok: v.z < 1 && v.z > -1 };
}
function labelBox(x, y, text, { size = 24, alpha = 1, scale = 1, bg = 'rgba(10,9,8,0.9)', fg = '#f3efe6', sub = null, accent = null } = {}) {
  ctx.save(); ctx.globalAlpha = alpha;
  ctx.translate(x, y); ctx.scale(scale, scale); ctx.translate(-x, -y); // phóng từ chân nhãn
  ctx.font = `600 ${size}px Oswald`;
  const tw = ctx.measureText(text).width;
  let sw = 0; if (sub) { ctx.font = `400 ${Math.round(size * 0.62)}px BVP`; sw = ctx.measureText(sub).width; }
  const bw = Math.max(tw, sw) + size * 0.9, bh = size * 1.5 + (sub ? size * 0.85 : 0);
  let bx = clamp(x - bw / 2, 20, W - bw - 20), by = y - bh;
  ctx.fillStyle = bg; ctx.fillRect(bx, by, bw, bh);
  if (accent) { ctx.fillStyle = accent; ctx.fillRect(bx, by, 5, bh); }
  ctx.fillStyle = fg; ctx.textBaseline = 'middle'; ctx.textAlign = 'center';
  ctx.font = `600 ${size}px Oswald`; ctx.fillText(text, bx + bw / 2, by + size * 0.78);
  if (sub) { ctx.font = `400 ${Math.round(size * 0.62)}px BVP`; ctx.fillStyle = 'rgba(243,239,230,0.8)'; ctx.fillText(sub, bx + bw / 2, by + size * 1.72); }
  ctx.restore();
}
function marker(x, y, side, alpha, hit, scale = 1) {
  ctx.save(); ctx.globalAlpha = alpha;
  ctx.translate(x, y); ctx.scale(scale, scale); ctx.translate(-x, -y);
  if (side === 'dich') {
    ctx.fillStyle = hit ? COLORS.ta : COLORS.dich; ctx.strokeStyle = '#f3efe6'; ctx.lineWidth = 2.5;
    ctx.fillRect(x - 8, y - 8, 16, 16); ctx.strokeRect(x - 8, y - 8, 16, 16);
    if (hit) { ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x - 6, y - 6); ctx.lineTo(x + 6, y + 6); ctx.moveTo(x + 6, y - 6); ctx.lineTo(x - 6, y + 6); ctx.stroke(); }
  } else if (side === 'ta') {
    ctx.fillStyle = COLORS.ta; ctx.strokeStyle = '#f3efe6'; ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.moveTo(x, y - 11); ctx.lineTo(x + 10, y + 7); ctx.lineTo(x - 10, y + 7); ctx.closePath(); ctx.fill(); ctx.stroke();
  } else {
    ctx.fillStyle = '#f3efe6'; ctx.beginPath(); ctx.arc(x, y, 6, 0, Math.PI * 2); ctx.fill();
  }
  ctx.restore();
}
function flash(x, y, k, color, size) {
  // chớp sáng pháo: lõi trắng + quầng màu, tắt nhanh
  const a = Math.pow(1 - k, 2);
  const r = size * (0.4 + k * 1.2);
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, `rgba(255,248,225,${a})`); g.addColorStop(0.25, color.replace('A', String(a * 0.9))); g.addColorStop(1, color.replace('A', '0'));
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill(); ctx.restore();
}

const grain = [];
function makeGrain() {
  for (let k = 0; k < 4; k++) {
    const c = document.createElement('canvas'); c.width = 480; c.height = 270;
    const g = c.getContext('2d'), im = g.createImageData(480, 270), r = rng(101 + k);
    for (let i = 0; i < im.data.length; i += 4) { const v = r() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
    g.putImageData(im, 0, 0); grain.push(c);
  }
}
function finish(t) {
  // vignette + hạt phim nhẹ + fade đầu/cuối
  const vg = ctx.createRadialGradient(W / 2, H / 2, H * 0.42, W / 2, H / 2, H * 1.02);
  vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.62)');
  ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.globalAlpha = 0.05; ctx.globalCompositeOperation = 'overlay'; ctx.drawImage(grain[Math.floor(t * 24) % 4], 0, 0, W, H); ctx.restore();
}

function renderFrame(t) {
  t = clamp(t, 0, S.duration);
  const c = keyframes(S.camera, t);
  const tgt = v3(c.lat, c.lon);
  const h = (c.heading * Math.PI) / 180, p = (c.pitch * Math.PI) / 180;
  const fwd = new THREE.Vector3(Math.sin(h), 0, -Math.cos(h));
  camera.position.copy(tgt).addScaledVector(fwd, -Math.cos(p) * c.dist).add(new THREE.Vector3(0, Math.sin(p) * c.dist, 0));
  camera.fov = c.fov ?? 40; camera.updateProjectionMatrix();
  camera.lookAt(tgt);
  camera.updateMatrixWorld();
  drawDrape(t);
  renderer.render(scene, camera);

  ctx.clearRect(0, 0, W, H);
  // bộ đội đi dọc đường (theo đầu đường đang vẽ)
  for (const r of routes) {
    if (!r.troops) continue;
    const tr = r.troops;
    const f = ease[r.ease ?? 'inOut'](prog(t, r.from ?? 0, r.dur ?? 3));
    const a = ease.out(prog(t, (r.from ?? 0) + 0.2, 0.6)) * (1 - prog(t, r.to ?? 1e9, 0.6));
    if (a <= 0) continue;
    const sp = { pts: [], len: [0] };
    let head = 0;
    const tip = f * r.path.len[r.path.len.length - 1];
    for (let i = 0; i < r.path.pts.length; i++) {
      const q = project(v3(...r.path.pts[i], 0.01));
      if (i) sp.len.push(sp.len[i - 1] + Math.hypot(q.x - sp.pts[i - 1][0], q.y - sp.pts[i - 1][1]));
      sp.pts.push([q.x, q.y]);
      if (r.path.len[i] <= tip) head = sp.len[i] + (i + 1 < r.path.pts.length ? 0 : 0);
    }
    // nội suy đầu đội hình trong đoạn đang vẽ
    const i1 = r.path.len.findIndex((L) => L > tip);
    if (i1 > 0) { const k = (tip - r.path.len[i1 - 1]) / (r.path.len[i1] - r.path.len[i1 - 1]); head = lerp(sp.len[i1 - 1], sp.len[i1], k); }
    drawTroopGroup(ctx, sp, head - (tr.lag ?? 10), t, { ...tr, alpha: a });
  }
  // nhãn trên đường (vd "15 KM")
  for (const r of routes) {
    if (!r.label) continue;
    const L = appear(t, r.labelFrom ?? (r.from ?? 0) + (r.dur ?? 3) * 0.6, { dur: 0.55, to: r.to ?? 1e9, rise: 16 });
    if (L.a <= 0) continue;
    const i = Math.round((r.labelAt ?? 0.5) * (r.path.pts.length - 1));
    const q = project(v3(...r.path.pts[i], 0.05));
    if (q.ok) labelBox(q.x + (r.labelDx ?? 0), q.y - 30 + (r.labelDy ?? 0) + L.y, r.label, { size: r.labelSize ?? 34, alpha: L.a, scale: L.s, accent: COLORS.vang, sub: r.labelSub });
  }
  // điểm + nhãn: ký hiệu bật ra trước, đường dẫn mọc lên, hộp nhãn bật sau (so le 80–160 ms)
  for (const o of S.points || []) {
    const p = resolvePt(o);
    const f0 = o.from ?? 0, to = o.to ?? 1e9;
    const m = appear(t, f0, { dur: 0.45, to, s0: 0.2 });
    if (m.a <= 0) continue;
    const q = project(v3(p.lat, p.lon, 0.02));
    if (!q.ok || q.x < -40 || q.x > W + 40 || q.y < -40 || q.y > H + 40) continue;
    const hit = o.hit != null && t >= o.hit;
    const punch = o.hit != null ? landPunch(t, o.hit, 0.35, 0.6) : 0;
    if (!o.noMarker) marker(q.x, q.y, p.side, m.a, hit, m.s + punch);
    if (o.noLabel) continue;
    const lift = o.lift ?? 52;
    const g = ease.expoOut(prog(t, f0 + 0.08, 0.3)) * (1 - ease.in(prog(t, to, 0.3)));
    if (lift > 20 && g > 0) { ctx.save(); ctx.globalAlpha = m.a; ctx.strokeStyle = 'rgba(243,239,230,0.9)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(q.x, q.y - 10); ctx.lineTo(q.x, q.y - 10 - (lift - 14) * g); ctx.stroke(); ctx.restore(); }
    const L = appear(t, f0 + (lift > 20 ? 0.16 : 0), { dur: 0.5, to, rise: 10 });
    if (L.a > 0) labelBox(q.x + (o.dx ?? 0), q.y - lift + L.y, o.label ?? p.label, { size: o.size ?? (p.side === 'dia-danh' ? 40 : 24), alpha: L.a, scale: L.s, sub: o.sub ?? p.sub ?? (p.minh ? 'vị trí minh họa' : null), accent: hit ? COLORS.ta : p.side === 'ta' ? COLORS.ta : null });
  }
  // chớp sáng
  for (const fl of S.flashes || []) {
    const p = resolvePt(fl);
    for (let n = 0; n < (fl.count ?? 1); n++) {
      const k = (t - fl.at - n * (fl.every ?? 0.35)) / (fl.len ?? 0.6);
      if (k < 0 || k > 1) continue;
      const q = project(v3(p.lat, p.lon, 0.03));
      if (q.ok) flash(q.x, q.y, k, fl.color ?? 'rgba(255,90,40,A)', fl.size ?? 120);
    }
  }
  // tiêu đề lớn: từng chữ bật lên so le 70 ms, gạch đỏ quét sau
  for (const ti of S.titles || []) {
    const size = ti.size ?? 110, y = ti.y ?? H * 0.5, X = ti.x ?? W / 2, to = ti.to ?? 1e9;
    if (t < ti.from) continue;
    ctx.save(); ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
    ctx.font = `700 ${size}px Oswald`;
    const words = ti.text.split(' '), sp = ctx.measureText(' ').width;
    const ws = words.map((w) => ctx.measureText(w).width), tw = ws.reduce((a, b) => a + b, 0) + sp * (words.length - 1);
    let x = X - tw / 2;
    words.forEach((w, i) => {
      const A = appear(t, ti.from + i * 0.07, { dur: 0.55, to: to + i * 0.03, rise: size * 0.28, s0: 0.9 });
      if (A.a > 0) {
        ctx.save(); ctx.globalAlpha = A.a; ctx.translate(x + ws[i] / 2, y + A.y); ctx.scale(A.s, A.s);
        ctx.shadowColor = 'rgba(0,0,0,0.7)'; ctx.shadowBlur = 30; ctx.fillStyle = '#f3efe6'; ctx.fillText(w, -ws[i] / 2, 0); ctx.restore();
      }
      x += ws[i] + sp;
    });
    const u = ease.expoOut(prog(t, ti.from + 0.25, 0.7)) * (1 - ease.in(prog(t, to, 0.3)));
    ctx.fillStyle = COLORS.ta; ctx.fillRect(X - (tw / 2) * u, y + size * 0.62, tw * u, 6);
    if (ti.sub) {
      const A = appear(t, ti.from + 0.35, { dur: 0.5, to, rise: 10 });
      ctx.globalAlpha = A.a; ctx.textAlign = 'center'; ctx.font = `500 ${Math.round(size * 0.3)}px BVP`; ctx.fillStyle = 'rgba(243,239,230,0.9)'; ctx.shadowColor = 'rgba(0,0,0,0.8)'; ctx.shadowBlur = 12; ctx.fillText(ti.sub, X, y + size * 0.95 + A.y);
    }
    ctx.restore();
  }
  finish(t);
  for (const d of [].concat(S.date || []).map((x) => (typeof x === 'string' ? { text: x } : x))) {
    if (t >= (d.from ?? 0) - 0.01) drawDateLabel(ctx, d.text, ease.out(prog(t, d.from ?? 0.2, 0.5)) * (1 - prog(t, d.to ?? 1e9, 0.3)));
  }
  drawCredit(ctx, S.credit ?? (S.nen === 'ams' ? CREDIT_MAP3D_AMS : CREDIT_MAP3D), 1);
  const fi = S.fadeIn ?? 0, fo = S.fadeOut ?? 0;
  const black = Math.max(fi ? 1 - prog(t, 0, fi) : 0, fo ? prog(t, S.duration - fo, fo) : 0);
  if (black > 0) { ctx.fillStyle = `rgba(0,0,0,${black})`; ctx.fillRect(0, 0, W, H); }
}

// Nền AMS: tờ 5651 IV đã nắn sang lưới Mercator WGS84 (tools/nan-ban-do-ams.py), khung phủ ghi trong ams-5651-4.georef.json.
async function loadAms(loader) {
  let geo, tex, mask;
  try {
    const res = await fetch('../data/ams-5651-4.georef.json');
    if (!res.ok) throw new Error(`georef HTTP ${res.status}`);
    geo = await res.json();
    if (!geo.texture) throw new Error('georef thiếu khoá texture: chạy tools/nan-ban-do-ams.py (không dùng --no-warp lần đầu)');
    [tex, mask] = await Promise.all([loader.loadAsync(`../data/${geo.texture.tep}`), loader.loadAsync(`../data/${geo.texture.mat_na}`)]);
  } catch (e) {
    console.error(`map3d: không nạp được nền AMS cho shot nen:'ams' (${e.message})`);
    throw e;
  }
  const T = geo.texture;
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
  mask.anisotropy = renderer.capabilities.getMaxAnisotropy();
  const nw = world(T.north, T.west), se = world(T.south, T.east);
  const look = S.amsLook ?? {};
  const t = S.amsTint ?? [0.9, 0.96, 0.84];
  return { tex, mask, rect: new THREE.Vector4(nw.x, se.x, nw.z, se.z),
    look: new THREE.Vector4(look.sat ?? 0.75, look.relief ?? 0.85, look.gain ?? 0.8, look.mix ?? 1), tint: new THREE.Vector3(...t), out: look.outside ?? 1.7 };
}

async function init() {
  [V, RG] = await Promise.all([loadGrid('valley'), loadGrid('region')]);
  const latC = (V.north + V.south) / 2, lonC = (V.west + V.east) / 2;
  K = Math.cos((latC * Math.PI) / 180); MX0 = mx(lonC); MY0 = my(latC);
  const loader = new THREE.TextureLoader();
  const [tv, tr] = await Promise.all([loader.loadAsync('../data/valley_s2.jpg'), loader.loadAsync('../data/region_s2.jpg')]);
  for (const tx of [tv, tr]) { tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = renderer.capabilities.getMaxAnisotropy(); }
  drape.width = 1536; drape.height = 2304; dctx = drape.getContext('2d');
  drapeTex = new THREE.CanvasTexture(drape); drapeTex.colorSpace = THREE.SRGBColorSpace; drapeTex.anisotropy = renderer.capabilities.getMaxAnisotropy();
  const a = world(V.north, V.west), b = world(V.south, V.east);
  const inset = 0.05;
  if (S.nen !== undefined && S.nen !== 've-tinh' && S.nen !== 'ams') throw new Error(`map3d: nen '${S.nen}' không hợp lệ, chỉ nhận 've-tinh' hoặc 'ams'`);
  const ams = S.nen === 'ams' ? await loadAms(loader) : null;
  scene.add(terrainMesh(V, tv, drapeTex, new THREE.Vector4(1e9, -1e9, 0, 0), 0, ams));
  scene.add(terrainMesh(RG, tr, null, new THREE.Vector4(a.x + inset, b.x - inset, a.z + inset, b.z - inset), 0.004, ams));
  routes = (S.routes || []).map((r) => ({ ...r, path: withLength(smoothPath(resolvePath(r), r.style === 'trench' ? 6 : 10)) }));
  if (S.nen === 'ams') window.MAP3D_PROJECT = (lat, lon) => project(v3(lat, lon, 0.02)); // cho máy đo độ lệch nhãn
  makeGrain();
  await loadFonts();
  mount(S.duration, renderFrame);
}
init();
