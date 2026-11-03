// Địa danh lòng chảo Điện Biên Phủ. Toạ độ từ OpenStreetMap (ODbL); minh: true = vị trí minh họa.
// side: 'ta' | 'dich' | 'dia-danh' (quyết định ký hiệu).
export const PLACES = {
  dbp: { lat: 21.388, lon: 103.012, label: 'ĐIỆN BIÊN PHỦ', side: 'dia-danh' },
  a1: { lat: 21.383, lon: 103.0177, label: 'ĐỒI A1', side: 'dich' },
  ham: { lat: 21.3849, lon: 103.0107, label: 'HẦM CHỈ HUY ĐỜ CÁT-XTƠ-RI', side: 'dich' },
  himlam: { lat: 21.4047, lon: 103.024, label: 'ĐỒI HIM LAM', side: 'dich' },
  doclap: { lat: 21.4213, lon: 103.0066, label: 'ĐỒI ĐỘC LẬP', side: 'dich' },
  d1: { lat: 21.3924, lon: 103.0166, label: 'ĐỒI D1', side: 'dich' },
  e2: { lat: 21.3957, lon: 103.0164, label: 'ĐỒI E2', side: 'dich' },
  h6: { lat: 21.43, lon: 103.052, label: 'TRẬN ĐỊA PHÁO TA', sub: '(minh họa)', side: 'ta' },
  sanbay: { lat: 21.397, lon: 103.008, label: 'SÂN BAY MƯỜNG THANH', side: 'dich' },
  bankeo: { lat: 21.405, lon: 102.993, label: 'BẢN KÉO', side: 'dich', minh: true },
  hongcum: { lat: 21.335, lon: 103.004, label: 'HỒNG CÚM', side: 'dich', minh: true },
};

// Ba phân khu (đường bao minh họa, [lat, lon]).
export const ZONES = {
  bac: [[21.431, 103.000], [21.428, 103.016], [21.414, 103.034], [21.4025, 103.032], [21.4015, 103.000], [21.403, 102.984], [21.414, 102.982]],
  trungtam: [[21.3985, 103.000], [21.3985, 103.026], [21.389, 103.027], [21.374, 103.022], [21.370, 103.005], [21.376, 102.995], [21.390, 102.993]],
  nam: [[21.347, 102.993], [21.348, 103.016], [21.337, 103.021], [21.325, 103.012], [21.326, 102.994]],
};

// Hướng kéo pháo vào trận địa H6 (minh họa, từ phía Đông Bắc).
export const ROUTE_KEO_PHAO = [[21.520, 103.140], [21.512, 103.128], [21.503, 103.124], [21.494, 103.110], [21.486, 103.106], [21.474, 103.094], [21.466, 103.085], [21.455, 103.077], [21.447, 103.064], [21.437, 103.059], [21.430, 103.052]];

export const CREDIT_MAP3D = 'Địa hình: AWS Terrain Tiles (SRTM, công cộng) · Ảnh vệ tinh: Sentinel-2 cloudless 2016 (EOX, CC BY 4.0) · Vị trí cứ điểm: OpenStreetMap (ODbL), một số vị trí minh họa';

export const CREDIT_MAP3D_AMS = 'Bản đồ: AMS series L7014 tờ 5651 IV và L7015 tờ 5551 I, 1:50.000 (tài liệu chính phủ Hoa Kỳ, công cộng) · Địa hình: AWS Terrain Tiles (SRTM, công cộng) · Vị trí cứ điểm: OpenStreetMap (ODbL), một số vị trí minh họa';

// Hào vây lấn (minh họa): hai vòng cung siết dần phía Đông khu trung tâm + các hào tiến sát D1, E2, A1.
function arc(lat0, lon0, rKm, fromDeg, toDeg, n = 24) {
  const pts = [];
  for (let i = 0; i <= n; i++) {
    const b = ((fromDeg + ((toDeg - fromDeg) * i) / n) * Math.PI) / 180;
    pts.push([lat0 + (Math.cos(b) * rKm) / 110.6, lon0 + (Math.sin(b) * rKm) / 103.6]);
  }
  return pts;
}
const C0 = [21.389, 103.012];
export const TRENCHES = {
  'hao-ngoai': arc(...C0, 2.6, -25, 200),
  'hao-trong': arc(...C0, 1.75, -5, 175),
  'hao-d1': [[21.3935, 103.0345], [21.3930, 103.0285], [21.3926, 103.0215], [21.3924, 103.0175]],
  'hao-e2': [[21.4010, 103.0330], [21.3990, 103.0270], [21.3968, 103.0205], [21.3958, 103.0172]],
  'hao-a1': [[21.3770, 103.0330], [21.3795, 103.0280], [21.3815, 103.0225], [21.3828, 103.0186]],
};
