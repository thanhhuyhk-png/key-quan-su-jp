// Shot (g): kết — camera về hầm chỉ huy, nhãn 7/5/1954 · 17:30
window.SHOT = {
  duration: 8,
  date: '7/5/1954',
  fadeOut: 0.5,
  camera: [
    { t: 0, lat: 21.390, lon: 103.020, dist: 6, heading: 200, pitch: 48, fov: 40 },
    { t: 6, lat: 21.3849, lon: 103.0107, dist: 2.4, heading: 230, pitch: 40, fov: 38 },
    { t: 8, lat: 21.3849, lon: 103.0107, dist: 2.2, heading: 234, pitch: 39, fov: 38, ease: 'out' },
  ],
  rings: [{ id: 'ham', from: 3.5, radius: 200, color: '#d8382a' }],
  points: [{ id: 'ham', from: 1.0, size: 30 }],
  titles: [{ text: '7/5/1954 · 17:30', from: 3.8, y: 900, size: 96 }],
};
