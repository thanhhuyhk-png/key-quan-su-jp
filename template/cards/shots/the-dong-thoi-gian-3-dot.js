// Cảnh 15–17: 3 làn ĐỢT 1/2/3, sáng lần lượt
window.SHOT = {
  type: 'dong-thoi-gian', duration: 9,
  tag: '13/3 – 7/5/1954', kicker: 'CHIẾN DỊCH ĐIỆN BIÊN PHỦ', title: 'BA ĐỢT TẤN CÔNG',
  axis: { from: [10, 3, 1954], to: [10, 5, 1954], ticks: [
    { d: [13, 3, 1954], label: '13/3' }, { d: [30, 3, 1954], label: '30/3' }, { d: [15, 4, 1954], label: '15/4' }, { d: [1, 5, 1954], label: '1/5' }, { d: [7, 5, 1954], label: '7/5' } ] },
  lanes: [
    { name: 'ĐỢT 1', start: [13, 3, 1954], end: [17, 3, 1954], dates: '13–17/3', note: 'Him Lam · Độc Lập · Bản Kéo', activeFrom: 1.0, activeTo: 3.6 },
    { name: 'ĐỢT 2', start: [30, 3, 1954], end: [30, 4, 1954], open: true, dates: 'từ 30/3', note: 'Các cứ điểm phía Đông: C1, E, D, A1', activeFrom: 3.6, activeTo: 6.2, grow: 1.6 },
    { name: 'ĐỢT 3', start: [1, 5, 1954], end: [7, 5, 1954], dates: '1–7/5', note: 'Đồi A1 · 7/5 kết thúc', activeFrom: 6.2, activeTo: 99 },
  ],
  source: 'Nguồn: Báo Điện tử Chính phủ; Báo QĐND',
};
