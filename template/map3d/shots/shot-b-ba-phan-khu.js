// Shot (b): 3 phân khu tô màu + nhãn, các cứ điểm chính
window.SHOT = {
  duration: 7,
  date: '1953 – 1954',
  camera: [
    { t: 0, lat: 21.374, lon: 103.010, dist: 19, heading: 10, pitch: 60, fov: 40 },
    { t: 7, lat: 21.377, lon: 103.009, dist: 17, heading: 4, pitch: 62, fov: 40, ease: 'sine' },
  ],
  zones: [
    { id: 'bac', from: 0.6, color: 'rgba(93,134,184,0.42)' },
    { id: 'trungtam', from: 1.6, color: 'rgba(93,134,184,0.42)' },
    { id: 'nam', from: 2.6, color: 'rgba(93,134,184,0.42)' },
  ],
  points: [
    { lat: 21.437, lon: 103.006, label: 'PHÂN KHU BẮC', side: 'dia-danh', noMarker: true, from: 0.9, size: 30, lift: 0 },
    { lat: 21.386, lon: 103.044, label: 'PHÂN KHU TRUNG TÂM', side: 'dia-danh', noMarker: true, from: 1.9, size: 30, lift: 0 },
    { lat: 21.337, lon: 103.040, label: 'PHÂN KHU NAM', side: 'dia-danh', noMarker: true, from: 2.9, size: 30, lift: 0 },
    { id: 'himlam', from: 3.6, noLabel: true }, { id: 'doclap', from: 3.7, noLabel: true }, { id: 'bankeo', from: 3.8, noLabel: true },
    { id: 'a1', from: 3.9, noLabel: true }, 
    { id: 'ham', from: 4.2, noLabel: true }, { id: 'sanbay', from: 4.3, noLabel: true }, { id: 'hongcum', from: 4.4, noLabel: true },
  ],
  titles: [{ text: '49 CỨ ĐIỂM', sub: 'chia thành ba phân khu', from: 4.6, x: 470, y: 520, size: 72 }],
};
