// MẪU P2: thẻ nhân vật, biến thể khung (LÃNH TỤ). Ảnh thật cắt khung vuông vắn, viền trang trọng, không tách nền, không hiệu ứng lên mặt;
// chỉ phóng đều rất chậm (zoomDen ≤ 1,08). `cat` = [tâmX, tâmY, rộng] chuẩn hoá; chiều cao suy ra từ khung, không kéo giãn.
window.SHOT = {
  type: 'nhan-vat', bienThe: 'khung', lanhTu: true, duration: 6, seed: 26, mau: true, nam: 'MẪU',
  kicker: 'NHÂN VẬT', title: 'NGƯỜI ĐỨNG ĐẦU',
  anh: '../data/mau-p2/nguoi-khung-mau.jpg', cat: [0.5, 0.45, 0.9], zoomDen: 1.04,
  ten: 'LÃNH TỤ MẪU', chucVu: 'CHỨC VỤ MẪU', chiTiet: 'Chức vụ đúng thời điểm trong tập, một dòng giải thích ngắn',
  moc: [0.4, 1.4, 2.1],
  source: 'MẪU · ảnh giả vẽ bằng code, không phải tư liệu lịch sử',
};
