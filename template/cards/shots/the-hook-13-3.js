// Cảnh 1: hook nền đen, ngày giờ hiện từng dòng, rung nhẹ + chớp
window.SHOT = {
  type: 'hook', duration: 3.5, y: 500,
  glows: [{ at: 0.2, len: 0.6, x: 1500, y: 980 }, { at: 1.3, len: 0.5, x: 400, y: 1000 }, { at: 2.6, len: 0.8, x: 1200, y: 1020 }],
  lines: [
    { text: '13/3/1954 · 17:05', at: 0.4, size: 150, shake: 14, flash: 0.35 },
    { text: 'HIM LAM · ĐIỆN BIÊN', at: 1.6, size: 70, color: '#c93b2b', shake: 8, flash: 0.2, spacing: 10 },
  ],
};
