// Callout kiểu bản tin quân sự (QPVN): thanh đỏ mọc lên, dòng lớn (số đếm lên rồi dừng đúng chữ, hoặc chữ), nhãn in
// hoa trượt vào, có thể thêm dòng nguồn; mọi thứ cùng ra. Góc trái dưới, trong vùng an toàn. Dùng chung cho lớp chữ
// trên phim, bản đồ và thẻ số liệu để cả tập một họ.
// c: { tu, den (giây), so | chu, truoc, sau, tren (dòng nhỏ trên), nhan, nguon, y, mau (màu dòng lớn) }
import { ease } from './common.js';

const kep = (x) => Math.min(1, Math.max(0, x));
const so = (n) => Math.round(n).toLocaleString('vi-VN');
export const CALLOUT_FONTS = ['800 104px BVP', '600 40px BVP', '500 24px BVP', '600 30px BVP'];

export function callout(cx, t, c) {
  const k = t - c.tu, ra = 1 - ease.in(kep((t - c.den) / 0.35));
  if (k < 0 || ra <= 0) return;
  const x = c.x ?? 118, y = c.y ?? 770;
  cx.save(); cx.globalAlpha = ra;
  const dinh = c.tren ? y - 46 : y - 4; // thanh đỏ ôm cả dòng nhỏ phía trên
  cx.fillStyle = '#c93b2b'; cx.fillRect(x - 28, dinh, 10, (y + 164 - dinh) * ease.expoOut(kep(k / 0.35)));
  cx.shadowColor = 'rgba(0,0,0,.7)'; cx.shadowBlur = 22; cx.textBaseline = 'top'; cx.letterSpacing = '1px';
  if (c.tren) {
    cx.globalAlpha = ra * ease.out(kep(k / 0.25)); cx.font = '600 30px BVP'; cx.fillStyle = '#f5f1e8'; cx.letterSpacing = '3px';
    cx.fillText(c.tren, x + 4, y - 42); cx.letterSpacing = '1px';
  }
  const a1 = ease.out(kep(k / 0.25)), lon = c.chu ?? so(c.so * ease.out(kep((k - 0.05) / 0.4)));
  cx.globalAlpha = ra * a1; cx.font = '800 104px BVP'; cx.fillStyle = c.mau ?? '#e03a2e';
  cx.fillText(`${c.truoc || ''}${lon}${c.sau || ''}`, x + 30 * (1 - ease.expoOut(kep(k / 0.45))), y);
  if (c.nhan) {
    const a2 = ease.out(kep((k - 0.2) / 0.3));
    cx.globalAlpha = ra * a2; cx.font = '600 40px BVP'; cx.fillStyle = '#f5f1e8'; cx.letterSpacing = '2px';
    cx.fillText(c.nhan, x + 4 + 24 * (1 - ease.expoOut(kep((k - 0.2) / 0.45))), y + 120);
  }
  if (c.nguon) { cx.font = '500 24px BVP'; cx.fillStyle = 'rgba(245,241,232,.82)'; cx.letterSpacing = '0px'; cx.fillText(c.nguon, x + 4, y + 172); }
  cx.restore();
}
