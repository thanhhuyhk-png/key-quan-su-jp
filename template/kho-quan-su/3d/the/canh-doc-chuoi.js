// Review scene (not a library item): night, a diorama slope like Doc Chuoi; a 37 mm gun hauled uphill on two
// long ropes, six soldiers per rope, a man with a wheel chock at the rear wheel. No lamps (hauled in the dark,
// dien-bien-phu.md item 4). Nobody is identifiable. Built only from library items and engine helpers.
(function (g) {
  'use strict';
  const K = g.Kho3D, T = K.T, H = K.hinh, R = K.R;

  K.canhDocChuoi = function (renderer) {
    const scene = K.canh(renderer, 'dem', 13);
    const DOC = 13, V = .26;
    const sb = K.saBan({ dai: 20, rong: 7.5, day: 1.8, doc: DOC, hat: 11, nhap: .035 });
    scene.add(sb.nhom);
    const rnd = K.rng(29);
    // Jungle along the far edge (camera works from the open near side).
    const cay = [];
    for (let i = 0; i < 46; i++) { const x = -9.6 + (i / 46) * 19.2 + rnd() * .3, z = 2.4 + rnd() * 1.2; cay.push({ x, y: sb.doCao(x, z), z, h: 1.8 + rnd() * 1.8 }); }
    scene.add(H.rung(cay, rnd));

    // Actors.
    const phao = K.tao('phao-37', { hat: 4 }); scene.add(phao.khung);
    const hang = [];
    for (const ben of [1, -1]) for (let i = 0; i < 6; i++) {
      const p = K.tao('bo-doi', { hat: 40 + i + (ben > 0 ? 0 : 10), sung: i % 3 === 1 ? 'k50' : 'khong' });
      scene.add(p.khung); hang.push({ p, ben, i });
    }
    const chen = K.tao('bo-doi', { hat: 77, sung: 'khong' }); scene.add(chen.khung);
    const go = H.mesh(H.tam([[0, 0], [.3, 0], [.3, .05], [.06, .18], [0, .18]], .18, .006), 'go'); scene.add(go);
    const day = [null, null];
    const datLenDoc = (inst, x, z) => { inst.khung.position.set(x, sb.doCao(x, z), z); inst.khung.rotation.set(0, 0, DOC * R); };

    const cam = new T.PerspectiveCamera(34, 16 / 9, .1, 200);
    function ve(t, aspect) {
      const gx = -4.6 + V * t;
      datLenDoc(phao, gx, 0);
      phao.dat({ trangThai: 'keo', t, tocDo: V });
      const moc = phao.neoThe('mocKeo');
      // Each rope: from the towing eye, splitting to its side, then taut through the hands of its row.
      const diemDay = { 1: [moc.clone()], '-1': [moc.clone()] };
      for (const ben of [1, -1]) {
        const tach = new T.Vector3(moc.x + 1.3 * Math.cos(DOC * R), 0, ben * .72);
        tach.y = sb.doCao(tach.x, tach.z) + .85; diemDay[ben].push(tach);
      }
      for (const h of hang) {
        const x = gx + 5.3 + h.i * 1.0, z = h.ben * 1.0;
        datLenDoc(h.p, x, z);
        // Each man grips where his arms reach in the pulling pose; the taut rope runs through both palms.
        h.p.dat({ trangThai: 'keo-day', t: t + h.i * .27 + (h.ben > 0 ? 0 : .5), doc: DOC });
        const long = ten => h.p.neo['tay' + ten].localToWorld(new T.Vector3(0, -.05, 0));
        diemDay[h.ben].push(long('P'), long('T'));
      }
      for (const ben of [1, -1]) {
        const cuoi = diemDay[ben][diemDay[ben].length - 1].clone(); cuoi.x += .9; cuoi.y = sb.doCao(cuoi.x, cuoi.z) + .25; diemDay[ben].push(cuoi);
        const path = new T.CurvePath();
        for (let i = 1; i < diemDay[ben].length; i++) path.add(new T.LineCurve3(diemDay[ben][i - 1], diemDay[ben][i]));
        const idx = ben > 0 ? 0 : 1;
        if (day[idx]) { scene.remove(day[idx]); day[idx].geometry.dispose(); }
        day[idx] = H.mesh(new T.TubeGeometry(path, 160, .012, 6, false), 'day'); scene.add(day[idx]);
      }
      // Chock man: stooped behind the rear wheel on the outer side, block held low against the tyre.
      const banhSau = phao.neoThe('banhSau');
      datLenDoc(chen, banhSau.x - .95, -1.25);
      chen.dat({ trangThai: 'dung', tuThe: 'cui', t, doc: DOC });
      const a = chen.neoThe('tayT'), b = chen.neoThe('tayP');
      go.position.copy(a).lerp(b, .5); go.position.y -= .08; go.rotation.set(0, 0, DOC * R);
      // Camera drifts around the column.
      const tam = new T.Vector3(gx + 4.2, sb.doCao(gx + 4.2, 0) + .4, 0);
      K.quayQuanh(cam, tam, 14.5, 8, 238 + t * 6);
      cam.aspect = aspect; cam.updateProjectionMatrix();
    }
    return { scene, cam, ve };
  };
})(typeof window !== 'undefined' ? window : globalThis);
