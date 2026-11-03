// Khoá nòng lựu pháo 105 mm M2A1 (M101): số đo và một vòng bắn là hàm thuần của t. Không có three.js ở đây.
// Trục: +x về phía miệng nòng, +y lên trên, +z sang phải pháo (nhìn từ sau ra). Đơn vị mét.
//
// Có nguồn (TM 9-1325, 1944; en.wikipedia.org/wiki/M101_howitzer):
//   cỡ nòng 105 mm, dài nòng 2,31 m (L/22), khoá chêm trượt ngang (horizontal sliding wedge, tay quay),
//   cò kiểu gõ, kéo liên tục, tự lên cò bằng dây (continuous pull), giật lùi thuỷ khí hằng định 42 in.
//   Đạn 105 x 372 mm R.
// ƯỚC LƯỢNG theo tỷ lệ ảnh, chưa đối chiếu bản vẽ: kích thước vòng khoá, khối chêm, hành trình chêm,
//   tay quay, đầu đạn, đường kính vỏ đạn. Trước khi lên phim phải đo lại trên hình TM 9-1325 và ghi NGUON.tsv.

export const G = {
  // có nguồn
  bore: 0.105,
  tubeLen: 2.31,
  recoil: 42 * 0.0254, // 1,067 m
  caseLen: 0.372,
  // ước lượng
  face: -0.12, // mặt trước khối chêm = đáy buồng đạn
  ringFront: 0.05,
  ringRear: -0.30,
  wedgeDepth: 0.15, // theo x
  wedgeHalfY: 0.12,
  wedgeHalfZ: 0.09,
  ringHalfY: 0.17,
  ringHalfZ: 0.15,
  chamberR: 0.062,
  caseR: 0.059,
  rimR: 0.066,
  projLen: 0.40,
  travel: 0.165, // chêm trượt sang phải tới khi mép trái qua khỏi vành vỏ đạn
  leverLen: 0.32,
  leverSwing: (105 * Math.PI) / 180,
};
G.muzzle = G.face + G.tubeLen;

// Nhịp phim (giây). timeline.json chép lại đúng các mốc này.
export const T = {
  cut: 2.0, open: 3.4, ram: 5.0, close: 7.0, pull: 8.4, fire: 9.0, runout: 9.6,
  reopen: 12.0, extract: 12.7, uncut: 14.6, end: 17.0,
};
// Giật lùi thật chỉ ~0,1 s; phim chiếu chậm để đọc được.
export const SLOW = 4;

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const sm = (x) => {
  const u = clamp01(x);
  return u * u * u * (u * (u * 6 - 15) + 10);
};
const span = (t, a, d) => sm((t - a) / d);
const outExpo = (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * clamp01(x)));

// Một đầu vào (t) suy ra mọi tư thế: khoá, đạn, kim hoả, giật lùi, vỏ đạn.
export function stateAt(t) {
  const open = span(t, T.open, 1.0) - span(t, T.close, 0.9) + span(t, T.reopen, 0.8);
  const ram = span(t, T.ram, 1.5); // 0: đạn sau khoá 0,95 m .. 1: vào buồng
  const pin = span(t, T.pull, 0.25) - span(t, T.fire + 0.4, 0.3);
  const fired = t >= T.fire;
  // giật lùi: lùi hết 1,067 m rất nhanh, rồi đẩy trở về (chậm SLOW lần)
  const back = outExpo((t - T.fire) / (0.12 * SLOW));
  const ret = span(t, T.runout, 2.0);
  const recoil = fired ? G.recoil * back * (1 - ret) : 0;
  // đầu đạn rời vỏ, chạy hết nòng
  const projX = fired ? Math.min(3.2, ((t - T.fire) / (0.35 * SLOW / 4)) ** 2 * 0.6) : 0;
  const glow = fired ? Math.exp(-(t - T.fire) / 0.35) : 0;
  // vỏ đạn bị hất ra sau khi khoá mở gần hết
  const ex = clamp01((t - T.extract) / 0.7);
  const caseX = -1.0 * outExpo(ex);
  const caseY = -0.24 * Math.min(1, ex * ex * 1.6); // rơi tới sàn (y sàn −0,36, bán kính vỏ 0,06 + 0,06)
  const cut = span(t, T.cut, 1.0) - span(t, T.uncut, 1.0);
  // phần đang làm việc (để tô màu nhấn)
  let work = '';
  if (t >= T.open && t < T.open + 1.0) work = 'wedge';
  else if (t >= T.ram && t < T.ram + 1.5) work = 'round';
  else if (t >= T.close && t < T.close + 0.9) work = 'wedge';
  else if (t >= T.pull && t < T.fire + 0.4) work = 'pin';
  else if (t >= T.fire && t < T.runout + 2.0) work = 'recoil';
  else if (t >= T.reopen && t < T.extract + 0.7) work = 'case';
  return {open, ram, pin, recoil, projX, glow, caseX, caseY, ex, cut, fired, work,
    wedgeZ: open * G.travel, lever: open * G.leverSwing};
}

export const CAPTIONS = [
  [0, 'Lựu pháo 105 mm M2A1', 'Khoá nòng chêm trượt ngang'],
  [T.cut, 'Cắt dọc nòng', 'Buồng đạn, khối chêm, kim hoả'],
  [T.open, 'Mở khoá nòng', 'Khối chêm trượt sang phải'],
  [T.ram, 'Nạp đạn', 'Đạn 105 × 372 mm R'],
  [T.close, 'Đóng khoá nòng', ''],
  [T.pull, 'Giật dây cò', 'Kim hoả đập hạt lửa'],
  [T.fire, 'Bắn', 'Giật lùi 1,07 m · quay chậm'],
  [T.runout, 'Nòng trở về', 'Hãm lùi thuỷ khí'],
  [T.reopen, 'Mở khoá, hất vỏ đạn', ''],
];
export const captionAt = (t) => CAPTIONS.filter((c) => c[0] <= t).pop();
