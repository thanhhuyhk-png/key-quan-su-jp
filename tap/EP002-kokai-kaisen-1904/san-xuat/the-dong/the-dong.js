// the-dong.js — thẻ số liệu động (chép từ EP001 日本海海戦; EP002 黄海海戦 dùng chung) (GSAP dùng làm thư viện easing; mọi khung là hàm thuần của t).
// Hợp đồng dung-trang.mjs: window.SIZE, window.DURATION, window.renderFrame(t), window.READY.
// Dữ liệu: window.SHOT = { kieu, duration, kicker, nguon, ... } (xem README trong thư mục này).
// 8 kiểu: dem-so, bong-tau, thanh-so-sanh, dong-ho, do-khoang-cach, so-sanh-toc-do, thuong-vong, moc-gio.
// Màu ngữ nghĩa: đỏ = Nhật/tiêu điểm, xám lạnh = Nga, kem = trung lập.
(() => {
  const S = window.SHOT;
  const NHAT = '#e0583f', DO = '#cc2222', NGA = '#9aa3ad', KEM = '#f0e8d8', KEMP = '#cfc8ba', NGUON = '#888278', TAT = '#2b2b2b';
  const MAU = { nhat: NHAT, nga: NGA, kem: KEM };
  const E = (n) => gsap.parseEase(n);
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const seg = (t, a, d, ease = 'power2.out') => (d <= 0 ? (t >= a ? 1 : 0) : E(ease)(clamp((t - a) / d)));
  const fmt = (n, dec = 0) => Number(n).toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec });
  const DUR = S.duration;
  const hold = Math.min(1.2, Math.max(0.6, DUR * 0.3));     // giữ tĩnh cuối thẻ
  const nhanh = DUR < 2.6 ? 0.8 : 1;                        // thẻ ngắn: rút gọn thời gian đếm
  window.SIZE = '1920x1080';
  window.DURATION = DUR;
  window.SFX_CUES = [];
  const cue = (t, tiep) => window.SFX_CUES.push({ t: Math.round(t * 100) / 100, tiep });

  // ---------- khung chung ----------
  const root = document.getElementById('root');
  const el = (tag, cls, parent = root, html = '') => { const e = document.createElement(tag); if (cls) e.className = cls; if (html) e.innerHTML = html; parent.appendChild(e); return e; };
  if (S.nen !== 'trong') { el('div', 'grid'); }
  ['tl', 'tr', 'bl', 'br'].forEach((c) => el('div', 'goc ' + c));
  const kicker = el('div', 'kicker', root, S.kicker || '黄海海戦 · 1904年8月10日');
  const rule = el('div', 'rule');
  const stage = el('div', 'stage');
  const nguon = el('div', 'nguon', root, S.nguon ? '出典: ' + S.nguon : '');
  const tag = S.nhan ? el('div', 'nhan-goc', root, S.nhan) : null;

  const vao = (t0 = 0) => { const k = seg(0, 0, 1); return k; };
  const chungUpdate = (t) => {
    const a = seg(t, 0.05, 0.45, 'power2.out');
    kicker.style.opacity = a; kicker.style.transform = `translateY(${(1 - a) * -14}px)`;
    rule.style.transform = `scaleX(${seg(t, 0.15, 0.55, 'expo.out')})`;
    nguon.style.opacity = seg(t, 0.7, 0.5) * 0.9;
    if (tag) tag.style.opacity = seg(t, 0.2, 0.4);
  };

  // ---------- odometer ----------
  // Mỗi chữ số là một cột 0..9,0 cuộn liên tục: v/10^k mod 10. Dừng đúng số nguyên khi v = giá trị.
  function odo(parent, value, { dec = 0, cls = '' } = {}) {
    const box = el('span', 'odo ' + cls, parent);
    const txt = fmt(value, dec);
    const cells = [], seps = [];
    for (let i = 0; i < txt.length; i++) {
      const ch = txt[i];
      if (/\d/.test(ch)) {
        const cell = el('span', 'dig', box);
        const col = el('span', 'col', cell);
        for (let d = 0; d <= 10; d++) el('span', 'n', col, String(d % 10));
        cells.push({ cell, col, pos: txt.length - 1 - i - (dec ? (i > txt.indexOf('.') ? 0 : 0) : 0), idx: i, ch });
      } else { const sp = el('span', 'sep', box, ch); seps.push({ sp, i }); }
    }
    const nd = txt.replace(/\D/g, '').length;
    let k = nd - 1;
    cells.forEach((c) => { c.k = k--; });
    seps.forEach((x) => { const r = cells.find((c) => c.idx > x.i); x.k = r ? r.k : 0; });
    return {
      box,
      set(v, blur = 0) {
        const vv = dec ? v * Math.pow(10, dec) : v;
        cells.forEach((c) => {
          c.cell.style.opacity = c.k === 0 || vv >= Math.pow(10, c.k) ? 1 : 0;
          // chữ số thấp nhất cuộn liên tục; chữ số cao chỉ nhích khi chữ số thấp hơn đi qua 9 → 0 (kiểu odometer cơ khí)
          let p;
          if (c.k === 0) p = vv % 10;
          else {
            const thap = (vv / Math.pow(10, c.k - 1)) % 10;
            p = Math.floor(vv / Math.pow(10, c.k)) % 10 + Math.min(1, Math.max(0, thap - 9));
          }
          c.col.style.transform = `translateY(${-(p) * 1.18}em)`;
        });
        seps.forEach((x) => { x.sp.style.opacity = vv >= Math.pow(10, x.k + 1) ? 1 : 0; });
        box.style.filter = blur > 0.2 ? `blur(${blur.toFixed(1)}px)` : 'none';
      },
    };
  }

  // ---------- bộ dựng theo kiểu ----------
  const K = {};

  // 1) đếm số (một hoặc nhiều hàng)
  K['dem-so'] = () => {
    const rows = (S.rows || [S]).map((r, i, a) => ({ ...r, i, n: a.length }));
    const objs = rows.map((r) => {
      const row = el('div', 'hang', stage);
      const color = MAU[r.mau || 'nhat'];
      if (r.truoc) el('span', 'tien', row, r.truoc);
      const o = odo(row, r.value, { dec: r.dec || 0 });
      if (r.dau) row.insertBefore(el('span', 'dau', null, r.dau), o.box);
      if (r.don_vi) el('span', 'donvi', row, r.don_vi);
      row.style.color = color; row.style.fontSize = (rows.length > 1 ? 150 : 230) + 'px';
      const thuoc = el('div', 'thuoc', stage);
      const fill = el('div', 'thuoc-fill', thuoc); fill.style.background = color;
      for (let i = 0; i < 21; i++) el('i', '', thuoc);
      return { r, row, o, thuoc, fill };
    });
    objs.forEach((x, i) => { cue(0.45 + i * 0.5, 'tich-bat-dau'); cue(0.45 + i * 0.5 + 1.1 * nhanh, 'cham-dich'); });
    return (t) => objs.forEach((x, i) => {
      const t0 = 0.45 + i * 0.5, d = 1.15 * nhanh;
      const p = seg(t, t0, d, 'expo.out');
      const v = x.r.value * p;
      const toc = (1 - p) * clamp((t - t0) / 0.15);
      x.o.set(p >= 0.999 ? x.r.value : v, toc * 5);
      const a = seg(t, t0 - 0.1, 0.3);
      x.row.style.opacity = a;
      const punch = t > t0 + d ? 0.07 * Math.sin(Math.PI * clamp((t - t0 - d) / 0.35)) : 0;
      x.row.style.transform = `translateY(${(1 - a) * 18}px) scale(${1 + punch})`;
      x.thuoc.style.opacity = a * 0.9;
      x.fill.style.width = (p * 100 * (x.r.ty_le || 1)) + '%';
    });
  };

  // 2) hình bóng tàu: tàu tắt dần theo số đếm
  const SHIP = [
    'M4 34 L22 34 L26 26 L40 26 L42 18 L50 18 L52 26 L64 26 L70 20 L74 20 L76 26 L100 26 L108 34 L116 34 L110 42 L10 42 Z',
    'M4 36 L30 36 L34 28 L46 28 L48 14 L52 14 L54 28 L70 28 L74 22 L82 22 L84 28 L104 28 L112 36 L116 36 L108 44 L8 44 Z',
    'M6 38 L38 38 L42 30 L58 30 L60 22 L66 22 L68 30 L88 30 L96 38 L110 38 L104 44 L10 44 Z',
  ];
  K['bong-tau'] = () => {
    const n = S.total, hang = Math.ceil(n / 7);
    const lbl = el('div', 'bt-cap', stage);
    const dem = el('div', 'hang bt-dem', lbl);
    const o = odo(dem, n); el('span', 'donvi', dem, S.don_vi || '隻'); el('span', 'tien2', dem, S.nhan_so || '沈没');
    dem.style.color = MAU[S.mau || 'nga'];
    const luoi = el('div', 'bt-luoi', stage);
    const ships = [];
    for (let i = 0; i < n; i++) {
      const c = el('div', 'tau', luoi);
      c.innerHTML = `<svg viewBox="0 0 120 56" width="150" height="70"><path d="${SHIP[(i * 7 + (i >> 2)) % 3]}" fill="currentColor"/><line class="gach" x1="6" y1="48" x2="114" y2="10" stroke="${DO}" stroke-width="5"/></svg>`;
      c.style.color = MAU[S.mau || 'nga'];
      ships.push(c);
    }
    let nhat = null;
    if (S.nhat) {
      nhat = el('div', 'bt-nhat', stage, `<span>${S.nhat.nhan}</span>`);
      for (let i = 0; i < S.nhat.so; i++) { const c = el('div', 'tau nho', nhat); c.innerHTML = `<svg viewBox="0 0 120 56" width="90" height="42"><path d="${SHIP[2]}" fill="${NHAT}"/></svg>`; }
    }
    cue(0.5, 'tich-bat-dau');
    return (t) => {
      const p = seg(t, 0.7, 1.5 * nhanh + n * 0.02, 'power1.inOut');
      const k = Math.floor(p * n + 1e-6);
      ships.forEach((c, i) => {
        const a = seg(t, 0.15 + i * 0.012, 0.3);
        c.style.opacity = i < k ? 0.28 : a;
        c.style.color = i < k ? TAT : MAU[S.mau || 'nga'];
        c.querySelector('.gach').style.opacity = i < k ? 1 : 0;
        c.style.transform = `translateY(${(1 - a) * 16}px)`;
      });
      o.set(p >= 0.999 ? n : p * n, (1 - p) * 3 * (t > 0.7 ? 1 : 0));
      dem.style.opacity = seg(t, 0.1, 0.4);
      if (nhat) nhat.style.opacity = seg(t, 1.6, 0.5);
    };
  };

  // 3) thanh so sánh (ô pháo)
  K['thanh-so-sanh'] = () => {
    const A = S.a, B = S.b, max = Math.max(A.so, B.so);
    const cols = max > 12 ? 10 : max;
    const mk = (d, mau) => {
      const hang = el('div', 'ss-hang', stage);
      el('div', 'ss-ten', hang, d.nhan);
      const cells = el('div', 'ss-o', hang);
      cells.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
      const list = [];
      for (let i = 0; i < d.so; i++) { const c = el('i', '', cells); c.style.setProperty('--c', mau); list.push(c); }
      const so = el('div', 'ss-so', hang, `${d.so}<small>${d.don_vi || '門'}</small>`);
      so.style.color = mau;
      return { hang, list, so, d };
    };
    const ra = mk(A, MAU[A.mau || 'nga']), rb = mk(B, MAU[B.mau || 'nhat']);
    const g = el('div', 'ss-ket', stage, S.ket || '');
    cue(0.5, 'tich-bat-dau'); cue(1.9, 'cham-dich');
    return (t) => {
      [ra, rb].forEach((r, j) => {
        const t0 = 0.5 + j * 0.45;
        r.hang.style.opacity = seg(t, t0 - 0.2, 0.3);
        const p = seg(t, t0, 0.9 * nhanh, 'power1.inOut');
        const k = Math.floor(p * r.d.so + 1e-6);
        r.list.forEach((c, i) => { c.style.opacity = i < k ? 1 : 0.14; c.style.transform = i === k - 1 && p < 1 ? 'scale(1.18)' : 'scale(1)'; });
        r.so.style.opacity = seg(t, t0 + 0.6, 0.3);
      });
      g.style.opacity = seg(t, 1.9, 0.4);
    };
  };

  // 4) đồng hồ mốc giờ
  K['dong-ho'] = () => {
    const [h, m] = S.gio.split(':').map(Number), [h0, m0] = (S.tu || `${h}:${m - 1 < 0 ? 59 : m - 1}`).split(':').map(Number);
    const phut = (hh, mm) => hh * 60 + mm;
    const tuP = phut(h0, m0), denP = phut(h, m);
    const wrap = el('div', 'dh', stage);
    const svg = el('div', 'dh-mat', wrap);
    let ticks = '';
    for (let i = 0; i < 60; i++) { const a = i * 6, l = i % 5 === 0 ? 22 : 10; ticks += `<line x1="0" y1="-${210 - l}" x2="0" y2="-210" transform="rotate(${a})" stroke="${i % 5 === 0 ? KEM : NGUON}" stroke-width="${i % 5 === 0 ? 5 : 2}"/>`; }
    svg.innerHTML = `<svg viewBox="-240 -240 480 480" width="440" height="440"><circle r="228" fill="none" stroke="${KEMP}" stroke-width="3" opacity=".5"/>${ticks}<line id="hh" x1="0" y1="0" x2="0" y2="-110" stroke="${KEM}" stroke-width="10" stroke-linecap="round"/><line id="mm" x1="0" y1="0" x2="0" y2="-176" stroke="${DO}" stroke-width="6" stroke-linecap="round"/><circle r="12" fill="${KEM}"/></svg>`;
    const dig = el('div', 'dh-dig', wrap);
    const hhE = svg.querySelector('#hh'), mmE = svg.querySelector('#mm');
    const sub = el('div', 'dh-sub', wrap, S.nhan_gio || '');
    cue(0.4, 'tich-chuyen'); cue(1.4, 'cham-dich');
    return (t) => {
      const p = seg(t, 0.4, 0.95 * nhanh, 'power3.inOut');
      const cur = tuP + (denP - tuP) * p;
      const ch = Math.floor(cur / 60) % 24, cm = Math.floor(cur % 60);
      mmE.setAttribute('transform', `rotate(${(cur % 60) * 6})`);
      hhE.setAttribute('transform', `rotate(${((cur / 60) % 12) * 30})`);
      dig.innerHTML = `${String(ch).padStart(2, '0')}<b>:</b>${String(cm).padStart(2, '0')}`;
      dig.style.color = p >= 0.999 ? KEM : KEMP;
      wrap.style.opacity = seg(t, 0.05, 0.4);
      sub.style.opacity = seg(t, 1.0, 0.45);
      sub.style.transform = `translateY(${(1 - seg(t, 1.0, 0.45)) * 14}px)`;
    };
  };

  // 5) đường đo khoảng cách (rangefinder)
  K['do-khoang-cach'] = () => {
    const wrap = el('div', 'rf', stage);
    wrap.innerHTML = `<div class="rf-gio">${S.gio || ''}</div>
      <svg class="rf-svg" viewBox="0 0 1500 220" width="1500" height="220">
        <g id="nga" transform="translate(120,150)"><path d="${SHIP[0]}" fill="${NGA}" transform="scale(1.9) translate(-60,-34)"/></g>
        <g id="nhat" transform="translate(1380,150)"><path d="${SHIP[2]}" fill="${NHAT}" transform="scale(1.9) translate(-60,-34)"/></g>
        <line id="th" x1="120" y1="40" x2="1380" y2="40" stroke="${KEM}" stroke-width="3"/>
        <line id="d1" x1="120" y1="22" x2="120" y2="58" stroke="${KEM}" stroke-width="4"/><line id="d2" x1="1380" y1="22" x2="1380" y2="58" stroke="${KEM}" stroke-width="4"/>
      </svg>`;
    const so = el('div', 'rf-so', wrap);
    const o = odo(so, S.den, {}); el('span', 'donvi', so, 'm');
    const info = el('div', 'dh-sub', wrap, S.nhan_gio || '');
    const nga = wrap.querySelector('#nga'), nhat = wrap.querySelector('#nhat'), th = wrap.querySelector('#th'), d1 = wrap.querySelector('#d1'), d2 = wrap.querySelector('#d2');
    const maxD = Math.max(S.tu, S.den);
    cue(0.5, 'tich-bat-dau'); cue(1.7, 'ping-khoa-tam');
    return (t) => {
      const p = seg(t, 0.5, 1.2 * nhanh, 'power3.out');
      const d = S.tu + (S.den - S.tu) * p;
      o.set(p >= 0.999 ? S.den : d, (1 - p) * 4);
      const half = 630 * (d / maxD) + 10; // nửa độ dài thước (px)
      const cx = 750;
      d1.setAttribute('x1', cx - half); d1.setAttribute('x2', cx - half); d2.setAttribute('x1', cx + half); d2.setAttribute('x2', cx + half);
      th.setAttribute('x1', cx - half); th.setAttribute('x2', cx + half);
      nga.setAttribute('transform', `translate(${cx - half},150)`); nhat.setAttribute('transform', `translate(${cx + half},150)`);
      wrap.style.opacity = seg(t, 0.05, 0.4);
      info.style.opacity = seg(t, 1.2, 0.45);
    };
  };

  // 6) so sánh tốc độ
  K['so-sanh-toc-do'] = () => {
    const A = S.a, B = S.b; // a = Nga (chậm), b = Nhật (nhanh)
    const wrap = el('div', 'tc', stage);
    const mk = (d, mau, y) => {
      const r = el('div', 'tc-hang', wrap);
      r.style.top = y + 'px';
      r.innerHTML = `<div class="tc-ten" style="color:${mau}">${d.nhan}</div><div class="tc-duong"><i></i><svg viewBox="0 0 120 56" width="170" height="80" class="tc-tau"><path d="${SHIP[0]}" fill="${mau}"/></svg></div><div class="tc-so" style="color:${mau}">${d.v}<small>ノット</small></div>`;
      return r;
    };
    const ra = mk(A, NGA, 40), rb = mk(B, NHAT, 220);
    const dif = el('div', 'tc-dif', wrap, `+${B.v - A.v}ノット <small>(+${Math.round(((B.v / A.v) - 1) * 100)}%)</small>`);
    cue(0.4, 'rexuoc-bat-dau'); cue(2.0, 'cham-dich');
    return (t) => {
      const p = seg(t, 0.4, 1.7 * nhanh, 'none');
      [[ra, A], [rb, B]].forEach(([r, d]) => {
        r.style.opacity = seg(t, 0.05, 0.35);
        r.querySelector('.tc-tau').style.transform = `translateX(${p * d.v * 38}px)`;
        r.querySelector('i').style.width = (p * d.v * 38 + 40) + 'px';
      });
      dif.style.opacity = seg(t, 1.9, 0.45);
      dif.style.transform = `translateY(${(1 - seg(t, 1.9, 0.45)) * 16}px) scale(${1 + 0.06 * Math.sin(Math.PI * clamp((t - 1.9) / 0.35))})`;
    };
  };

  // 7) thương vong: trang nghiêm, không đỏ chói, không nảy
  K['thuong-vong'] = () => {
    const rows = S.rows.map((r) => {
      const row = el('div', 'hang tv', stage);
      el('span', 'tien', row, r.nhan);
      const o = odo(row, r.value, { dec: 0 });
      el('span', 'donvi', row, r.don_vi || '名');
      if (r.them) el('span', 'them', row, r.them);
      row.style.color = r.mau === 'nga' ? '#b9c0c7' : KEM;
      return { row, o, r };
    });
    const dong = el('div', 'tv-ke', stage);
    cue(0.6, 'long-nhe');
    return (t) => {
      rows.forEach((x, i) => {
        const t0 = 0.6 + i * 0.7, d = 1.6 * nhanh;
        const p = seg(t, t0, d, 'sine.out');
        x.o.set(p >= 0.999 ? x.r.value : x.r.value * p, 0);
        const a = seg(t, t0 - 0.1, 0.5, 'sine.out');
        x.row.style.opacity = a;
        x.row.style.transform = `translateY(${(1 - a) * 10}px)`;
      });
      dong.style.transform = `scaleX(${seg(t, 0.3, 1.2, 'sine.inOut')})`;
    };
  };

  // 8) mốc giờ / tiêu đề: chữ trồi qua mặt nạ, đường kẻ đỏ vẽ từ giữa
  K['moc-gio'] = () => {
    const box = el('div', 'mg', stage);
    const l1 = el('div', 'mg-mask', box); const t1 = el('div', 'mg-t1', l1, S.dong1);
    const ke = el('div', 'mg-ke', box);
    const l2 = el('div', 'mg-mask', box); const t2 = el('div', 'mg-t2', l2, S.dong2 || '');
    const fit = (e, txt, mx) => { const n = Math.max([...String(txt)].length, 1); e.style.fontSize = Math.min(mx, Math.floor(1700 / n)) + 'px'; };
    fit(t1, S.dong1, 170); fit(t2, S.dong2 || '', 78);
    cue(0.3, 'dong-dau'); cue(0.9, 'am-ngan');
    return (t) => {
      const a = seg(t, 0.25, 0.8, 'expo.out');
      t1.style.transform = `translateY(${(1 - a) * 115}%)`;
      ke.style.transform = `scaleX(${seg(t, 0.55, 0.8, 'expo.inOut')})`;
      const b = seg(t, 0.8, 0.7, 'expo.out');
      t2.style.transform = `translateY(${(1 - b) * 115}%)`;
    };
  };

  const upd = K[S.kieu]();
  window.renderFrame = (t) => { chungUpdate(t); upd(t); return null; };
  const fontP = Promise.all(['700 80px NSJ', '400 40px NSJ'].map((f) => document.fonts.load(f, '日本海戦0123456789ノット隻門名'))).then(() => document.fonts.ready);
  fontP.then(() => { window.renderFrame(0); window.READY = true; });
})();
