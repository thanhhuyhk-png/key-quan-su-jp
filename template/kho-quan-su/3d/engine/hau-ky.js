// Post-processing for the 3D pages. three.js r149 (UMD) ships no EffectComposer as a plain script, so the passes are
// written here. The scene renders into a linear HDR target with depth; then, each optional:
//   bong  contact shading from depth (creases, feet on ground, wheels in mud)
//   dof   depth of field by distance, or a tilt-shift band for diorama shots
//   bloom lights above a threshold spill into a soft glow (fire, blasts, muzzle flashes)
// and a final pass: exposure + ACES (the same curve the renderer used before, so a neutral look matches the old
// output), film softness, grade in display space (saturation, contrast, brightness, black and white tint), grain and
// a cos^4 vignette. The grade mirrors ffmpeg's eq/noise/vignette used on the archive film so 3D cuts against it.
// Every pass is a pure function of its inputs and the frame index (grain is hashed from it): frames render alone.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T;

  const VS = 'varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }';
  // Window depth -> distance from the camera (perspective cameras only).
  const SAU = `uniform sampler2D tSau; uniform float uGan, uXa;
    float sau(vec2 uv) { float d = texture2D(tSau, uv).x; return uGan * uXa / (uXa - d * (uXa - uGan)); }`;
  // Per-pixel rotation for sample patterns (interleaved gradient noise): fixed per pixel, no frame dependence.
  const IGN = 'float ign(vec2 p) { return fract(52.9829189 * fract(dot(p, vec2(.06711056, .00583715)))); }';

  // Contact shading: view-space hemisphere test against 12 neighbours within uBan metres, normal from derivatives.
  const FS_BONG = `uniform sampler2D tMau; uniform vec2 uKich, uTan; uniform float uBan, uManh; varying vec2 vUv; ${SAU} ${IGN}
    vec3 viTri(vec2 uv) { float z = sau(uv); return vec3((uv * 2. - 1.) * uTan * z, -z); }
    void main() {
      vec4 c = texture2D(tMau, vUv); vec3 p = viTri(vUv);
      vec3 n = normalize(cross(dFdx(p), dFdy(p)));
      float r = uBan / (-p.z * uTan.y) * .5, a0 = ign(gl_FragCoord.xy) * 6.2832, occ = 0.;
      for (int i = 0; i < 12; i++) {
        float t = (float(i) + .5) / 12., a = a0 + float(i) * 2.39996;
        vec2 o = vec2(cos(a), sin(a)) * r * sqrt(t) * vec2(uKich.y / uKich.x, 1.);
        vec3 v = viTri(vUv + o) - p; float l = length(v);
        occ += max(0., dot(n, v / max(l, 1e-4)) - .15) * (1. - smoothstep(uBan * .5, uBan * 1.5, l));
      }
      gl_FragColor = vec4(c.rgb * (1. - uManh * clamp(occ / 12. * 2., 0., 1.)), 1.);
    }`;

  // Depth of field: gather over a golden-angle disc sized by the centre's blur; sharp samples do not smear outwards.
  const FS_DOF = `uniform sampler2D tMau; uniform vec2 uKich; uniform float uTieuCu, uKhau, uMax, uTilt, uTiltY, uTiltRong;
    varying vec2 vUv; ${SAU}
    float coc(vec2 uv) {
      if (uTilt > .5) return uMax * smoothstep(uTiltRong, uTiltRong + .3, abs(uv.y - uTiltY));
      float z = sau(uv); return min(uMax, uKhau * abs(z - uTieuCu) / z);
    }
    void main() {
      float c0 = coc(vUv); vec3 s = texture2D(tMau, vUv).rgb; float w = 1.;
      if (c0 > .5) for (int i = 0; i < 48; i++) {
        float t = (float(i) + .5) / 48., r = sqrt(t) * c0, a = float(i) * 2.39996;
        vec2 uv = vUv + vec2(cos(a), sin(a)) * r / uKich;
        float k = smoothstep(r * .5 - 1., r * .5 + 1., coc(uv));
        s += texture2D(tMau, uv).rgb * k; w += k;
      }
      gl_FragColor = vec4(s / w, 1.);
    }`;

  // Bloom: thresholded half-size copy, a chain of smaller copies, each blurred (9-tap separable Gaussian).
  const FS_SANG = `uniform sampler2D tMau; uniform vec2 uKich; uniform float uPhoi, uNguong, uMem; varying vec2 vUv;
    void main() {
      vec2 d = .5 / uKich;
      vec3 c = (texture2D(tMau, vUv + vec2(-d.x, -d.y)).rgb + texture2D(tMau, vUv + vec2(d.x, -d.y)).rgb
              + texture2D(tMau, vUv + vec2(-d.x, d.y)).rgb + texture2D(tMau, vUv + vec2(d.x, d.y)).rgb) * .25 * uPhoi;
      float l = max(c.r, max(c.g, c.b));
      gl_FragColor = vec4(c * smoothstep(uNguong, uNguong + uMem, l), 1.);
    }`;
  const FS_XUONG = `uniform sampler2D tMau; uniform vec2 uKich; varying vec2 vUv;
    void main() {
      vec2 d = .5 / uKich;
      gl_FragColor = vec4((texture2D(tMau, vUv + vec2(-d.x, -d.y)).rgb + texture2D(tMau, vUv + vec2(d.x, -d.y)).rgb
                         + texture2D(tMau, vUv + vec2(-d.x, d.y)).rgb + texture2D(tMau, vUv + vec2(d.x, d.y)).rgb) * .25, 1.);
    }`;
  const FS_MO = `uniform sampler2D tMau; uniform vec2 uKich, uHuong; varying vec2 vUv;
    void main() {
      vec2 d = uHuong / uKich;
      vec3 c = texture2D(tMau, vUv).rgb * .227027
             + (texture2D(tMau, vUv + d * 1.384615).rgb + texture2D(tMau, vUv - d * 1.384615).rgb) * .316216
             + (texture2D(tMau, vUv + d * 3.230769).rgb + texture2D(tMau, vUv - d * 3.230769).rgb) * .070270;
      gl_FragColor = vec4(c, 1.);
    }`;

  const MUC = 5;
  const FS_CUOI = `uniform sampler2D tMau, tB0, tB1, tB2, tB3, tB4; uniform vec2 uKich;
    uniform float uPhoi, uBloom, uMem, uBao, uTuongPhan, uSang, uHat, uVien, uKhung;
    uniform vec3 uToi, uTrang; varying vec2 vUv;
    vec3 rrt(vec3 v) { vec3 a = v * (v + .0245786) - .000090537; vec3 b = v * (.983729 * v + .4329510) + .238081; return a / b; }
    vec3 aces(vec3 c) {
      const mat3 vao = mat3(vec3(.59719, .07600, .02840), vec3(.35458, .90834, .13383), vec3(.04823, .01566, .83777));
      const mat3 ra = mat3(vec3(1.60475, -.10208, -.00327), vec3(-.53108, 1.10813, -.07276), vec3(-.07367, -.00605, 1.07602));
      return clamp(ra * rrt(vao * (c / .6)), 0., 1.);
    }
    vec3 srgb(vec3 c) { return mix(pow(c, vec3(1. / 2.4)) * 1.055 - .055, c * 12.92, vec3(lessThanEqual(c, vec3(.0031308)))); }
    float hash(vec2 p) { vec3 q = fract(vec3(p.xyx) * .1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
    void main() {
      vec2 d = 1. / uKich;
      vec3 c = texture2D(tMau, vUv).rgb;
      if (uMem > 0.) {
        vec3 n = (texture2D(tMau, vUv + vec2(d.x, 0.)).rgb + texture2D(tMau, vUv - vec2(d.x, 0.)).rgb
                + texture2D(tMau, vUv + vec2(0., d.y)).rgb + texture2D(tMau, vUv - vec2(0., d.y)).rgb) * .25;
        c = mix(c, n, uMem);
      }
      c = c * uPhoi + uBloom * (texture2D(tB0, vUv).rgb * .3 + texture2D(tB1, vUv).rgb * .25 + texture2D(tB2, vUv).rgb * .2
                              + texture2D(tB3, vUv).rgb * .15 + texture2D(tB4, vUv).rgb * .1);
      c = srgb(aces(c));
      float l = dot(c, vec3(.2126, .7152, .0722));
      c = mix(vec3(l), c, uBao);
      c = (c - .5) * uTuongPhan + .5 + uSang;
      c = uToi + c * (uTrang - uToi);
      c += (hash(gl_FragCoord.xy + mod(uKhung, 97.) * vec2(37.1, 91.7)) - .5) * 2. * uHat;
      if (uVien > 0.) {
        vec2 q = (vUv - .5) * vec2(uKich.x / uKich.y, 1.);
        float dn = length(q) / length(vec2(uKich.x / uKich.y, 1.) * .5), k = cos(uVien * min(dn, 1.));
        c *= k * k * k * k;
      }
      gl_FragColor = vec4(clamp(c, 0., 1.), 1.);
    }`;

  // Neutral look: same image as rendering straight to the canvas (exposure + ACES + sRGB), nothing added.
  K.HAU_KY_TRUNG_TINH = {
    bong: null,                    // { ban: radius in m, manh: 0..1 }
    dof: null,                     // { tieuCu: m, khau: px per unit defocus, max: px } or { tilt: true, y: 0..1 from bottom, rong, max }
    bloom: null,                   // { nguong: linear level, mem: soft knee, manh }
    mem: 0, bao: 1, tuongPhan: 1, sang: 0, toi: [0, 0, 0], trang: [1, 1, 1], hat: 0, vien: 0,
  };

  K.hauKy = function (renderer, w, h) {
    const rt = (ww, hh, o) => new T.WebGLRenderTarget(ww, hh, Object.assign({ type: T.HalfFloatType, depthBuffer: false,
      minFilter: T.LinearFilter, magFilter: T.LinearFilter }, o));
    const goc = rt(w, h, { depthBuffer: true, samples: 4, depthTexture: new T.DepthTexture(w, h) });
    const rtBong = rt(w, h), rtDof = rt(w, h), xuong = [], tam = [];
    for (let i = 0; i < MUC; i++) { const ww = Math.max(1, w >> (i + 1)), hh = Math.max(1, h >> (i + 1)); xuong.push(rt(ww, hh)); tam.push(rt(ww, hh)); }

    const camQ = new T.OrthographicCamera(-1, 1, 1, -1, 0, 1), sQ = new T.Scene();
    const quad = new T.Mesh(new T.PlaneGeometry(2, 2)); quad.frustumCulled = false; sQ.add(quad);
    const vl = (fs, ten) => new T.ShaderMaterial({ vertexShader: VS, fragmentShader: fs, depthTest: false, depthWrite: false, toneMapped: false,
      uniforms: Object.fromEntries(ten.map(k => [k, { value: null }])) });
    const SAU_U = ['tSau', 'uGan', 'uXa'];
    const M = {
      bong: vl(FS_BONG, ['tMau', 'uKich', 'uTan', 'uBan', 'uManh', ...SAU_U]),
      dof: vl(FS_DOF, ['tMau', 'uKich', 'uTieuCu', 'uKhau', 'uMax', 'uTilt', 'uTiltY', 'uTiltRong', ...SAU_U]),
      sang: vl(FS_SANG, ['tMau', 'uKich', 'uPhoi', 'uNguong', 'uMem']),
      xuong: vl(FS_XUONG, ['tMau', 'uKich']),
      mo: vl(FS_MO, ['tMau', 'uKich', 'uHuong']),
      cuoi: vl(FS_CUOI, ['tMau', 'tB0', 'tB1', 'tB2', 'tB3', 'tB4', 'uKich', 'uPhoi', 'uBloom', 'uMem', 'uBao', 'uTuongPhan', 'uSang',
        'uHat', 'uVien', 'uKhung', 'uToi', 'uTrang']),
    };
    M.bong.extensions.derivatives = true;
    function chay(mat, u, dich) {
      for (const k in u) mat.uniforms[k].value = u[k];
      quad.material = mat; renderer.setRenderTarget(dich); renderer.render(sQ, camQ);
    }
    const kich = r => new T.Vector2(r.width, r.height);
    const den = rt(1, 1);   // stands in for bloom levels when bloom is off (cleared to black once)
    renderer.setRenderTarget(den); renderer.setClearColor(0x000000, 1); renderer.clear(); renderer.setRenderTarget(null);

    // Draw one frame. o: look (see HAU_KY_TRUNG_TINH), phoi: exposure, k: frame index (grain only).
    function ve(scene, cam, k, o) {
      o = Object.assign({}, K.HAU_KY_TRUNG_TINH, o);
      const tm = renderer.toneMapping; renderer.toneMapping = T.NoToneMapping;
      renderer.setRenderTarget(goc); renderer.render(scene, cam);
      renderer.toneMapping = tm;
      const sauU = { tSau: goc.depthTexture, uGan: cam.near, uXa: cam.far };
      let nguon = goc.texture;
      if (o.bong) {
        const ty = Math.tan(cam.fov * Math.PI / 360);
        chay(M.bong, Object.assign({ tMau: nguon, uKich: kich(goc), uTan: new T.Vector2(ty * cam.aspect, ty), uBan: o.bong.ban, uManh: o.bong.manh }, sauU), rtBong);
        nguon = rtBong.texture;
      }
      if (o.dof) {
        const f = o.dof;
        chay(M.dof, Object.assign({ tMau: nguon, uKich: kich(goc), uTieuCu: f.tieuCu || 10, uKhau: f.khau || 0, uMax: f.max || 8,
          uTilt: f.tilt ? 1 : 0, uTiltY: f.y === undefined ? .5 : f.y, uTiltRong: f.rong === undefined ? .12 : f.rong }, sauU), rtDof);
        nguon = rtDof.texture;
      }
      const bl = [];
      if (o.bloom) {
        chay(M.sang, { tMau: nguon, uKich: kich(goc), uPhoi: o.phoi, uNguong: o.bloom.nguong, uMem: o.bloom.mem || .5 }, xuong[0]);
        for (let i = 0; i < MUC; i++) {
          if (i > 0) chay(M.xuong, { tMau: xuong[i - 1].texture, uKich: kich(xuong[i - 1]) }, xuong[i]);
          chay(M.mo, { tMau: xuong[i].texture, uKich: kich(xuong[i]), uHuong: new T.Vector2(1, 0) }, tam[i]);
          chay(M.mo, { tMau: tam[i].texture, uKich: kich(tam[i]), uHuong: new T.Vector2(0, 1) }, xuong[i]);
          bl.push(xuong[i].texture);
        }
      } else for (let i = 0; i < MUC; i++) bl.push(den.texture);
      chay(M.cuoi, { tMau: nguon, tB0: bl[0], tB1: bl[1], tB2: bl[2], tB3: bl[3], tB4: bl[4], uKich: kich(goc), uPhoi: o.phoi,
        uBloom: o.bloom ? o.bloom.manh : 0, uMem: o.mem, uBao: o.bao, uTuongPhan: o.tuongPhan, uSang: o.sang, uHat: o.hat, uVien: o.vien,
        uKhung: k || 0, uToi: new T.Vector3(...o.toi), uTrang: new T.Vector3(...o.trang) }, null);
    }
    return { ve };
  };
})(typeof window !== 'undefined' ? window : globalThis);
