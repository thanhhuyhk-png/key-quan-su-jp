// Shot (f): đợt 3 — zoom đồi A1, vòng sáng, chớp nổ khối bộc phá
window.SHOT = {
  duration: 8,
  date: '6/5/1954 · 20:30',
  camera: [
    { t: 0, lat: 21.386, lon: 103.015, dist: 7, heading: 300, pitch: 45, fov: 40 },
    { t: 5, lat: 21.383, lon: 103.0177, dist: 3.4, heading: 285, pitch: 38, fov: 38 },
    { t: 8, lat: 21.383, lon: 103.0177, dist: 3.1, heading: 280, pitch: 37, fov: 38, ease: 'out' },
  ],
  rings: [{ id: 'a1', from: 1.5, radius: 320 }],
  points: [{ id: 'a1', from: 0.4, size: 34, sub: '960 KG BỘC PHÁ' }],
  flashes: [{ id: 'a1', at: 6.2, count: 1, len: 1.4, size: 520, color: 'rgba(255,150,60,A)' }],
};
