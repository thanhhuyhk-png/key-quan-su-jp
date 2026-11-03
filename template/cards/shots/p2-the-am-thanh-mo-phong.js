// MẪU P2: thẻ âm thanh nhãn «MÔ PHỎNG LẠI» (người không phải lãnh tụ). Sóng âm vẽ từ giong-mau.peaks.json (tính trước từ giong-mau.mp3 bằng tools/song_am.py).
window.SHOT = {
  type: 'the-am-thanh', duration: 7, seed: 23, mau: true, nam: 'MẪU',
  kicker: 'ÂM THANH',
  nhan: 'MÔ PHỎNG LẠI',
  anh: '../data/mau-p2/nguoi-khung-mau.jpg', anhNeo: [0.5, 0.3],
  nguoi: { ten: 'NGUYỄN VĂN MẪU', chucVu: 'Sĩ quan mẫu, chỉ huy sở chỉ huy', boiCanh: 'Điện báo mẫu · ngày 00/00' },
  giong: { tep: '../data/mau-p2/giong-mau.mp3', peaks: '../data/mau-p2/giong-mau.peaks.json', batDau: 0.5 },
  phuDe: [{ text: 'Câu phụ đề mẫu thứ nhất, hiện lúc giọng bắt đầu.' }, { text: 'Câu thứ hai thay câu thứ nhất khi giọng sang ý khác.' }, { text: 'Câu cuối, giữ đến hết thẻ.' }],
  moc: [0.6, 2.4, 4.4],
  source: 'MẪU · giọng và ảnh giả, không phải tư liệu lịch sử',
};
