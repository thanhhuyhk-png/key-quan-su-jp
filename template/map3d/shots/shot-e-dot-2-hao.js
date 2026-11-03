// Shot (e): đợt 2 — hào vây lấn vẽ dần, siết quanh các đồi phía Đông
window.SHOT = {
  duration: 9,
  date: 'TỪ 30/3/1954',
  credit: 'Địa hình: AWS Terrain Tiles (SRTM, công cộng) · Ảnh vệ tinh: Sentinel-2 cloudless 2016 (EOX, CC BY 4.0) · Vị trí cứ điểm: OpenStreetMap (ODbL) · Đường hào: minh họa',
  camera: [
    { t: 0, lat: 21.389, lon: 103.018, dist: 9.5, heading: 290, pitch: 52, fov: 40 },
    { t: 9, lat: 21.389, lon: 103.016, dist: 7.4, heading: 279, pitch: 49, fov: 40, ease: 'sine' },
  ],
  zones: [{ id: 'trungtam', from: 0, color: 'rgba(93,134,184,0.26)' }],
  routes: [
    { path: 'hao-ngoai', style: 'trench', from: 0.4, dur: 3.2, width: 45 },
    { path: 'hao-trong', style: 'trench', from: 3.0, dur: 3.0, width: 45 },
    { path: 'hao-e2', style: 'trench', from: 5.4, dur: 2.0, width: 40 },
    { path: 'hao-d1', style: 'trench', from: 5.7, dur: 2.0, width: 40 },
    { path: 'hao-a1', style: 'trench', from: 6.0, dur: 2.0, width: 40 },
  ],
  points: [{ id: 'a1', from: 0.5 }],
};
