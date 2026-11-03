// Material library: PBR materials with small procedural canvas textures (deterministic).
// Colours are drawing estimates (no source gives paint codes); see docs/tri-thuc/khi-tai-quan-su/dien-bien-phu.md.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T;
  const coCanvas = typeof document !== 'undefined';
  const cache = {};

  function hexRgb(h) { const n = parseInt(h.slice(1), 16); return [n >> 16 & 255, n >> 8 & 255, n & 255]; }

  // Paint a 256px texture with a painter(ctx, rnd, size); returns a repeating sRGB CanvasTexture.
  function vanBeMat(seed, mau, painter, lap) {
    if (!coCanvas) return null;
    const s = 256, c = document.createElement('canvas');
    c.width = c.height = s;
    const x = c.getContext('2d'), rnd = K.rng(seed);
    x.fillStyle = mau; x.fillRect(0, 0, s, s);
    painter(x, rnd, s, hexRgb(mau));
    const tex = new T.CanvasTexture(c);
    tex.wrapS = tex.wrapT = T.RepeatWrapping;
    tex.repeat.set(lap || 1, lap || 1);
    tex.encoding = T.sRGBEncoding;
    tex.anisotropy = 4;
    return tex;
  }
  const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`;
  const toi = (c, k) => c.map(v => Math.max(0, Math.round(v * k)));

  const VE = {
    // Worn military paint: soft dirt blotches, dust speckle, a few darker streaks.
    son(x, r, s, c) {
      for (let i = 0; i < 70; i++) { x.fillStyle = rgba(toi(c, .78 + r() * .12), .18); x.beginPath(); x.ellipse(r() * s, r() * s, 8 + r() * 40, 6 + r() * 26, r() * 3, 0, 7); x.fill(); }
      for (let i = 0; i < 1600; i++) { x.fillStyle = r() < .5 ? 'rgba(0,0,0,.08)' : 'rgba(255,240,210,.06)'; x.fillRect(r() * s, r() * s, 1.5, 1.5); }
      for (let i = 0; i < 10; i++) { x.strokeStyle = rgba(toi(c, .7), .16); x.lineWidth = 1 + r() * 2; const px = r() * s; x.beginPath(); x.moveTo(px, r() * s * .4); x.lineTo(px + r() * 6 - 3, s * (.5 + r() * .5)); x.stroke(); }
    },
    // Plain-weave cloth: a faint 1 px weave (stronger lines read as ribbed knit on a figure), soft creases running
    // along the limb (V), faded and soiled patches.
    vai(x, r, s, c) {
      for (let y = 0; y < s; y += 2) { x.fillStyle = rgba(toi(c, .9), .1); x.fillRect(0, y, s, 1); }
      for (let xx = 0; xx < s; xx += 2) { x.fillStyle = rgba(toi(c, 1.08), .07); x.fillRect(xx, 0, 1, s); }
      for (let i = 0; i < 34; i++) {
        const px = r() * s, w = 3 + r() * 9, gr = x.createLinearGradient(px - w, 0, px + w, 0);
        if (!gr) break;
        gr.addColorStop(0, rgba(c, 0)); gr.addColorStop(.5, rgba(toi(c, r() < .5 ? .72 : 1.18), .22)); gr.addColorStop(1, rgba(c, 0));
        x.fillStyle = gr; x.fillRect(px - w, r() * s * .5, 2 * w, s * (.3 + r() * .5));
      }
      for (let i = 0; i < 40; i++) { x.fillStyle = rgba(toi(c, .8 + r() * .35), .12); x.beginPath(); x.ellipse(r() * s, r() * s, 10 + r() * 30, 8 + r() * 20, r() * 3, 0, 7); x.fill(); }
    },
    // Coarse burlap sack weave.
    bao(x, r, s, c) {
      for (let y = 0; y < s; y += 6) for (let xx = 0; xx < s; xx += 6) { x.fillStyle = rgba(toi(c, .75 + r() * .4), .55); x.fillRect(xx + ((y / 6) % 2) * 3, y, 4, 4); }
      for (let i = 0; i < 300; i++) { x.strokeStyle = rgba(toi(c, 1.2), .25); x.beginPath(); const a = r() * s, b = r() * s; x.moveTo(a, b); x.lineTo(a + r() * 10 - 5, b + r() * 10 - 5); x.stroke(); }
    },
    // Wood grain along U.
    go(x, r, s, c) {
      for (let i = 0; i < 46; i++) { x.strokeStyle = rgba(toi(c, .62 + r() * .5), .45); x.lineWidth = .6 + r() * 2.2; const y0 = r() * s; x.beginPath(); x.moveTo(0, y0); for (let xx = 0; xx <= s; xx += 16) x.lineTo(xx, y0 + Math.sin(xx * .03 + i) * 3 + r() * 2); x.stroke(); }
    },
    // Bamboo culm: fine longitudinal fibres.
    tre(x, r, s, c) {
      for (let i = 0; i < 90; i++) { x.strokeStyle = rgba(toi(c, .78 + r() * .4), .35); x.lineWidth = .5 + r(); const y0 = r() * s; x.beginPath(); x.moveTo(0, y0); x.lineTo(s, y0 + r() * 2 - 1); x.stroke(); }
    },
    // Quilted winter vest (áo trấn thủ): diamond stitching over cloth.
    tranThu(x, r, s, c) {
      VE.vai(x, r, s, c);
      x.strokeStyle = rgba(toi(c, .62), .7); x.lineWidth = 2;
      for (let i = -s; i < 2 * s; i += 32) { x.beginPath(); x.moveTo(i, 0); x.lineTo(i + s, s); x.stroke(); x.beginPath(); x.moveTo(i, s); x.lineTo(i + s, 0); x.stroke(); }
    },
    // Open hexagonal bamboo weave (long mot): three families of strips at 60 degrees; holes stay transparent.
    dan(x, r, s, c) {
      x.clearRect(0, 0, s, s);
      const buoc = s / 4;
      for (const goc of [0, 60, 120]) {
        x.save(); x.translate(s / 2, s / 2); x.rotate(goc * Math.PI / 180);
        for (let i = -6; i <= 6; i++) {
          x.fillStyle = rgba(toi(c, .82 + r() * .3), 1); x.fillRect(-s, i * buoc - 5, 2 * s, 10);
          x.fillStyle = rgba(toi(c, .6), .5); x.fillRect(-s, i * buoc + 4, 2 * s, 1.5);
        }
        x.restore();
      }
    },
    // Leaf cluster card: many small leaves on transparent ground, darker towards the middle.
    tanLa(x, r, s, c) {
      x.clearRect(0, 0, s, s);
      for (let i = 0; i < 420; i++) {
        const a = r() * Math.PI * 2, d = Math.sqrt(r()) * s * .46, px = s / 2 + Math.cos(a) * d, py = s / 2 + Math.sin(a) * d;
        x.save(); x.translate(px, py); x.rotate(r() * Math.PI * 2);
        x.fillStyle = rgba(toi(c, .55 + r() * .75 - d / s * .3), 1);
        x.beginPath(); x.ellipse(0, 0, 9 + r() * 7, 3.5 + r() * 2, 0, 0, Math.PI * 2); x.fill();
        x.restore();
      }
    },
    // Natural-metal aircraft skin: rows of panels of slightly different tone with staggered joints, fine seams and
    // faint rivet lines (seen close on MB1, so kept subtle: a strong grid read as squared paper), a few streaks.
    nhom(x, r, s, c) {
      const ny = 8, h = s / ny;
      x.fillStyle = rgba(toi(c, .5), .32);
      for (let j = 0; j < ny; j++) {
        let px = -r() * 40;
        while (px < s) {
          const w = 40 + r() * 60;
          x.save(); x.fillStyle = rgba(toi(c, .95 + r() * .1), .5); x.fillRect(px, j * h, w, h); x.restore();
          x.fillRect(px, j * h, .8, h);
          for (let y = j * h + 3; y < (j + 1) * h; y += 6) { x.save(); x.fillStyle = rgba(toi(c, 1.15), .3); x.fillRect(px + 2, y, 1, 1); x.restore(); }
          px += w;
        }
        x.fillRect(0, j * h, s, .8);
      }
      for (let i = 0; i < 26; i++) { x.fillStyle = rgba(toi(c, .75), .05 + r() * .06); x.fillRect(r() * s, r() * s, 2 + r() * 3, 20 + r() * 60); }
    },
    // Fine grain for rubber, skin, soil.
    hat(x, r, s, c) {
      for (let i = 0; i < 2600; i++) { x.fillStyle = rgba(toi(c, .7 + r() * .6), .25); x.fillRect(r() * s, r() * s, 1 + r() * 2, 1 + r() * 2); }
    },
  };

  // name: [hex, painter, repeat, roughness, metalness]
  const BANG = {
    'son-lx':    ['#4a5730', 'son', 2, .62, .25],
    'son-lx-toi':['#38422a', 'son', 2, .7, .2],
    'son-ol':    ['#4e5735', 'son', 2, .62, .25],
    'son-ol-toi':['#3a4128', 'son', 2, .7, .2],
    'thep':      ['#3b3d39', 'son', 2, .45, .65],
    'thep-mon':  ['#77776f', 'hat', 2, .38, .8],
    'cao-su':    ['#1e1e1c', 'hat', 3, .93, 0],
    'go':        ['#6d5032', 'go', 1, .82, 0],
    'go-toi':    ['#58402a', 'go', 1, .85, 0],
    'vai-quan':  ['#76765a', 'vai', 3, .96, 0],
    'nan-tre':   ['#c8b37e', 'dan', 8, .7, 0, { alphaTest: .45, side: 2 }],
    'ba-lo':     ['#6e6b4f', 'vai', 2, .97, 0],
    'vai-mu':    ['#4a5a31', 'vai', 3, .96, 0],
    'vai-dan':   ['#45392d', 'vai', 3, .97, 0],
    'vai-den':   ['#26231f', 'vai', 3, .97, 0],
    'luoi':      ['#5a6340', 'hat', 2, .95, 0],
    'la-tan':    ['#3f5c2b', 'tanLa', 1, .85, 0, { alphaTest: .4, side: 2 }],
    'bao':       ['#8d7a55', 'bao', 3, .97, 0],
    'tre':       ['#b9a262', 'tre', 1, .6, 0],
    'day':       ['#9d8e66', 'bao', 4, .95, 0],
    'da':        ['#7a5641', 'hat', 1, .72, 0],
    'da-toi':    ['#2e2a26', 'hat', 1, .8, 0],
    'da-that':   ['#4a3524', 'hat', 2, .7, 0],
    'cuc':       ['#3a3a2c', 'hat', 1, .5, 0],
    'toc':       ['#1a1714', 'hat', 2, .85, 0],
    'vai-tran-thu': ['#7a6a46', 'tranThu', 2, .97, 0],
    'cao-su-dep':['#2a2622', 'hat', 2, .9, 0],
    'dat':       ['#6a563a', 'hat', 4, .98, 0],
    'dat-do':    ['#7d5a3a', 'hat', 4, .98, 0],
    'co':        ['#56633a', 'hat', 12, .98, 0],
    'den':       ['#151513', 'hat', 1, .6, .3],
    'dong':      ['#a07a3a', 'hat', 1, .35, .85],
  };

  // Surface relief: the painted texture doubles as a bump map (weave, grain, panel seams catch the light).
  const NOI = { son: .012, vai: .01, bao: .04, go: .03, tre: .015, tranThu: .035, hat: .015, nhom: .006 };

  // Items can add materials from their own file: spec = [hex, painter, repeat, roughness, metalness, extra].
  K.dangKyVatLieu = function (ten, spec) {
    if (BANG[ten]) throw new Error('Trùng vật liệu ' + ten);
    if (!VE[spec[1]]) throw new Error('Không có kiểu vân ' + spec[1]);
    BANG[ten] = spec;
  };
  K.dsVatLieu = () => Object.keys(BANG);

  K.vatLieu = function (ten, mauRieng) {
    const key = ten + (mauRieng || '');
    if (cache[key]) return cache[key];
    const b = BANG[ten];
    if (!b) throw new Error('Không có vật liệu ' + ten);
    const mau = mauRieng || b[0];
    let seed = 7; for (const ch of key) seed = (seed * 31 + ch.charCodeAt(0)) >>> 0;
    const map = vanBeMat(seed, mau, VE[b[1]], b[2]);
    const noi = map && NOI[b[1]] ? { bumpMap: map, bumpScale: NOI[b[1]] } : {};
    const m = new T.MeshStandardMaterial(Object.assign({ color: map ? 0xffffff : new T.Color(mau), map, roughness: b[3], metalness: b[4] }, noi, b[5] || {}));
    m.name = key;
    cache[key] = m;
    return m;
  };

  // Leaf material: double-sided, three greens chosen by index.
  const LA = ['#3e5a28', '#55703a', '#6f7f3c', '#4a6230'];
  K.vatLieuLa = function (i) {
    const key = i === 'chung' ? 'la-chung' : 'la' + (i % LA.length);
    if (!cache[key]) cache[key] = new T.MeshStandardMaterial({ color: i === 'chung' ? 0xffffff : new T.Color(LA[i % LA.length]), roughness: .8, side: T.DoubleSide });
    return cache[key];
  };
})(typeof window !== 'undefined' ? window : globalThis);
