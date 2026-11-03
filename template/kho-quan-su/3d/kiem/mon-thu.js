// Test-only item: proves a new item needs one file and only public API (including its own material).
(function (g) {
  'use strict';
  const K = g.Kho3D, H = K.hinh;
  K.dangKyVatLieu('thu-do', ['#a03020', 'son', 1, .6, .1]);
  K.dangKy({
    ma: 'mon-thu', ten: 'Món thử', phe: 'thu', trangThai: ['a', 'b', 'c'],
    tao() {
      const goc = H.nhom('mon-thu'), hop = H.mesh(H.hop(.5, .5, .5, .02), 'thu-do'); hop.position.y = .5; goc.add(hop);
      const cham = new K.T.Object3D(); cham.position.y = .25; goc.add(cham);
      return { goc, diemCham: [cham], capNhat(tt) { hop.rotation.y = tt.trangThai === 'b' ? .5 : 0; hop.position.y = tt.trangThai === 'c' ? .8 : .5; cham.position.y = hop.position.y - .25; } };
    },
  });
})(typeof window !== 'undefined' ? window : globalThis);
