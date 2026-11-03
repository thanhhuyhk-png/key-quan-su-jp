# LichSu-Studio — bộ khối dựng đồ hoạ phim tài liệu lịch sử

Bốn khối, mỗi khối là một engine `<khoi>/<khoi>.js` + các file cấu hình shot `<khoi>/shots/<ten>.js` (chỉ chứa `window.SHOT = {...}`).
Trang render được sinh ra từ cấu hình: `<khoi>/<ten>.html`. Theo hợp đồng của máy dựng `tools/kit/dung-trang.mjs` (SIZE 1920x1080, DURATION, renderFrame(t) thuần theo t, READY sau khi font + dữ liệu tải xong). Không dùng `Math.random`; mọi nhiễu đều có seed.

## Dùng nhanh

```bash
cd Du-an/LichSu-Studio/template
python tools/build_shots.py                 # sinh lại mọi trang shot từ shots/*.js (sau mỗi lần sửa cấu hình)
node ../tools/kit/dung-trang.mjs map3d/shot-c-keo-phao.html --stills 1,5,9.5 --out-dir <thư mục>   # soi
node ../tools/kit/dung-trang.mjs map3d/shot-c-keo-phao.html --out c.mp4 --fps 24                    # video
sh tools/render_stills.sh map3d <thư mục>   # soi mọi shot của một khối (mốc 1 s, giữa, gần cuối)
```

Shot mới: chép một file trong `shots/`, đổi tham số, chạy `build_shots.py`. Lower-third dựng nền trong suốt: `node ../tools/kit/dung-trang.mjs ... --transparent` (bỏ `previewBg`).
Tốc độ đo được: map3d ≈ 4,6 s máy cho 1 s video 24 fps (RTX 2080 Ti, gồm khởi động Chrome); khối 2D nhanh hơn.

## Thư mục

| Đường dẫn | Nội dung |
|---|---|
| `lib/common.js` | easing, `keyframes()`, `rng(seed)`, `noise1()`, nhãn ngày góc trái trên, chú thích nguồn góc phải dưới, `mount()` |
| `lib/nhan-dien.js`, `lib/nhan-dien-the.js`, `lib/nhip-hien.js`, `lib/goha-logo-ngang.png` | hệ nhận diện «bảng tác chiến» cho cards và overlay: màu, cỡ chữ, lưới, đầu thẻ, năm mờ, hộp từ khoá, nguồn + logo, nhịp hiện theo mốc lời (spec: `plans/261103-1756-he-nhan-dien-do-hoa/p1-spec.md`) |
| `cards/mau-moi.js` | năm mẫu thẻ «bằng chứng gốc» của P2 (`tai-lieu-dich`, `phim-panel`, `the-am-thanh`, `nhan-vat`, `bieu-do`); `tools/luat_cung.py` chặn vi phạm luật cứng khi dựng trang; spec `plans/261103-1756-he-nhan-dien-do-hoa/p2-spec.md` |
| `lib/troops.js` | biểu tượng bộ đội QĐND 1954 + lựu pháo 105 ly (vẽ bằng code) |
| `lib/fonts.css`, `fonts/` | font OFL: Oswald (tiêu đề, số), Be Vietnam Pro 400–800 (chữ thường), Lora (trích văn kiện), IBM Plex Mono (nhãn hồ sơ); giấy phép `fonts/OFL-*.txt` |
| `data/` | sinh bởi `tools/prep_data.py`: DEM + ảnh Sentinel-2 (valley z13, region z10), `borders.js` (Natural Earth), `ams-5651-4.jpg` |
| `node_modules/three` | three.js cài cục bộ (`npm install three`), không dùng CDN |

Chuẩn bị lại dữ liệu: `python tools/prep_data.py --map-dir <...>/assets/map --ne-dir <thư mục chứa ne_10m_admin_0_countries.geojson, ne_10m_minor_islands.geojson>`.

## Tham số chung (mọi khối)

`duration` (s) · `date` (chuỗi hoặc `{text, from, to}`: nhãn ngày góc trái trên) · `credit`/`source` (chú thích nguồn góc phải dưới; mọi cảnh phải có) · `fadeIn`, `fadeOut` (s, về đen).
Easing trong keyframe: `ease: 'inOut' | 'out' | 'in' | 'sine' | 'linear' | 'outBack' | 'expoOut' | 'expoInOut' | 'backOut'` (áp cho đoạn đi TỚI keyframe đó).

Chuẩn chuyển động (bản sản xuất): mỗi phần tử xuất hiện riêng qua `appear()` trong `lib/common.js` — vào ease-out/expo, vượt nhẹ có kiểm soát (~6%), trượt lên vài px; ra ease-in ngắn. Ký hiệu bản đồ bật trước, đường dẫn mọc lên sau 80 ms, hộp nhãn bật sau 160 ms; nhãn mặc định vnmap so le 70 ms; tiêu đề hiện theo từng chữ (70 ms); vùng tô: viền vẽ dần rồi nền đậm dần; số đếm chạy expo-out rồi "thắng" (phồng nhẹ + vạch đỏ quét). Khi đặt `from` cho nhiều phần tử, giữ so le 40–120 ms và không để quá 1/3 số phần tử cùng chuyển động. Không in phụ đề lời đọc lên hình (phụ đề xuất SRT riêng).

## 1. map3d — địa hình lòng chảo 3D (three.js)

DEM phóng đại `exag` (mặc định 1.8), ảnh vệ tinh grade phim tài liệu (giảm bão hoà, bóng lạnh–sáng ấm, sương xa, vignette, hạt), nắng chiều nghiêng (`sunAz` 248°, `sunEl` 24°). Tinh chỉnh: `saturation`, `exposure`, `fogDensity`.
Địa danh, phân khu, tuyến kéo pháo, đường hào: `map3d/places.js` (OSM; mục `minh: true` tự ghi "vị trí minh họa").

| Tham số | Ý nghĩa |
|---|---|
| `camera: [{t, lat, lon, dist, heading, pitch, fov, ease}]` | máy quay quanh điểm nhìn: `dist` km, `heading` hướng nhìn (0 = nhìn về Bắc, 90 = Đông), `pitch` góc cúi (độ) |
| `points: [{id \| lat,lon,label,side, from, to, hit, sub, size, lift, dx, noLabel, noMarker}]` | chấm + nhãn hộp đen bám vị trí 3D. `side`: `dich` (ô vuông ký hiệu), `ta` (tam giác đỏ), `dia-danh`. `hit`: từ giây này ô đổi đỏ + dấu X |
| `zones: [{id: 'bac'\|'trungtam'\|'nam', from, dur, to, color}]` | vùng phân khu tô bán trong suốt, phủ bám địa hình |
| `routes: [{path, style, from, dur, ease, width, color, arrow, label, labelSub, labelAt, labelDy, troops}]` | đường vẽ dần bám địa hình. `path`: tên trong places.js (`keo-phao`, `hao-ngoai`, `hao-trong`, `hao-d1`, `hao-e2`, `hao-a1`) hoặc `[[lat,lon]...]`. `style`: `route` (nét đứt vàng + mũi tên), `attack` (mũi tên đỏ), `trench` (hào răng cưa). `width` mét |
| `troops: {kind: 'cannon'\|'file', count, size, gap, lag}` | (trong một route) bộ đội đi theo đầu đường đang vẽ, quay đúng hướng đi, nhịp bước. `cannon`: `count` người kéo dây + lựu pháo 105 ly + 2 người đẩy; `file`: hàng bộ đội đeo súng |
| `rings: [{id \| lat,lon, from, to, radius, color}]` | vòng sáng nhấp nháy bám địa hình |
| `flashes: [{id \| lat,lon, at, count, every, len, size, color}]` | chớp sáng pháo (`color` dạng `'rgba(255,90,40,A)'`) |
| `titles: [{text, sub, from, to, x, y, size}]` | chữ lớn giữa màn + gạch đỏ |

**Nền bản đồ AMS (`nen`).** `nen: 've-tinh'` (mặc định, giữ nguyên mọi shot cũ) hoặc `nen: 'ams'` (giá trị khác báo lỗi): phủ bản đồ địa hình Mỹ AMS 1:50.000 (công cộng) lên địa hình 3D, đúng toạ độ, thay cho ảnh vệ tinh tối. Phủ hai tờ liền nhau, 5651 IV Điện Biên Phủ (103°00'-103°15'E) và 5551 I Ban Thin Toc (102°45'-103°00'E, tờ phía Tây), 21°15'-21°30'N, texture cắt từ 102,90°E; Bản Kéo, sân bay, Độc Lập, Hồng Cúm đều nằm trong vùng phủ. Ngoài vùng đó (Bắc, Nam, Đông xa) hiện ảnh vệ tinh nâng sáng. Nguồn, giấy phép: `data/ams-nguon.md`.

| Tham số (chỉ khi `nen: 'ams'`) | Ý nghĩa |
|---|---|
| `amsLook: {sat, relief, gain, mix, outside}` | `sat` bão hoà bản đồ (0,75), `relief` mức giữ khối núi bằng bóng đổ (0 = bản đồ phẳng rõ nhất, 1 = tối khối nhất; 0,85), `gain` độ sáng (0,8), `mix` mức phủ (1), `outside` độ sáng ảnh vệ tinh ngoài tờ (1,7) |
| `amsTint: [r, g, b]` | nhân màu cho giấy bản đồ, mặc định `[0.9, 0.96, 0.84]` (giấy ngả ô-liu, không be) |

Tạo lại dữ liệu nắn (cần `opencv-python`, `scipy`, `PyMuPDF` nếu đổi PDF): `python -I -X utf8 tools/nan-ban-do-ams.py` → `data/ams-5651-4.georef.json` (điểm khống chế từng tờ, ma trận, sai số), `ams-5651-4.texture.jpg` + `-mask.png` (hai tờ đã nắn và ghép, lưới Mercator WGS84, đúng UV map3d, 4096 px cạnh dài). Mép giữa hai tờ: cắt nét khung, kéo dài bằng nhân bản điểm ảnh sát mép và hoà trên khoảng 7 px; màu tờ phía Tây được kéo về màu tờ Điện Biên Phủ theo dải sát mép. Hàm toạ độ thuần và test: `tools/ams_georef.py`, `python -m pytest tools/test_ams_georef.py`. Chuỗi: lưới UTM 48 trên Everest → Mercator ngang ngược → dịch tâm Indian 1960 → WGS84 (198, 881, 317 m) → Mercator web. Sai số dư lưới 0,59 px = 6,8 m (tờ Tây 0,65 px = 7,5 m); còn lệch ~35 m về Đông so với thực địa (đo bằng ảnh vệ tinh, sau khi sửa lưới nắn), đã trừ trong `SHEETS[].lech_m` của `tools/ams_nan.py`. Texture dựng bằng `tools/ams_nan.py` (import được, test ở `tools/test_ams_georef.py`); `nan-ban-do-ams.py` chỉ là lối vào. Shot mẫu: `shot-h-ams-long-chao`. Nguồn ghi ở chú thích: `CREDIT_MAP3D_AMS` trong `places.js`.

Shot bản mẫu: `shot-a-toan-canh` (bay vào lòng chảo, nhãn ĐIỆN BIÊN PHỦ) · `shot-b-ba-phan-khu` · `shot-c-keo-phao` (15 KM, đội kéo pháo) · `shot-d-dot-1` (Him Lam, Độc Lập, Bản Kéo chớp đỏ, mũi tên + hàng bộ đội) · `shot-e-dot-2-hao` · `shot-f-dot-3-a1` · `shot-g-ket-ham` (7/5/1954 · 17:30) · `shot-h-ams-long-chao` (nền AMS, nhãn cứ điểm ở toạ độ thật).

**Hình bộ đội là biểu tượng minh họa** (đồ hoạ ký hiệu bản đồ vẽ bằng code, không phải ảnh, không tả thực người): mũ nan có lưới và cành lá ngụy trang, quần áo xanh úa, dép cao su, súng trường đeo vai; lựu pháo 105 ly hai càng, bánh lớn, kéo bằng dây. Phía Pháp chỉ dùng ký hiệu ô vuông. Chú thích nguồn của shot có hình bộ đội/mũi tên/hào phải ghi "minh họa".

## 2. vnmap — bản đồ chính trị phẳng Đông Dương – Biển Đông

Việt Nam đỏ trầm, láng giềng tối, biển xanh đen. **Hoàng Sa, Trường Sa luôn tô màu Việt Nam, có nhãn; ghi "BIỂN ĐÔNG"; không vẽ bất kỳ ranh giới biển nào.** Dữ liệu Natural Earth gán quần đảo cho nước khác: `prep_data.py` loại mọi mảnh đất nước khác trong hai hộp quần đảo và gán đảo cho Việt Nam.

| Tham số | Ý nghĩa |
|---|---|
| `camera: [{t, lon, lat, zoom, ease}]` | `zoom` = px trên 1 độ kinh (52 ≈ cả Đông Dương + Biển Đông, 330 ≈ Tây Bắc, 2500 ≈ lòng chảo). Nội suy theo log, bay đều |
| `labels: [{text, lon, lat, kind, from, to}]` | thêm nhãn (`kind`: `vn`, `nuoc`, `bien`, `bien-nho`, `dao`). Nhãn mặc định (Việt Nam, Lào, Campuchia, Thái Lan, Trung Quốc, Biển Đông, hai quần đảo, Vịnh Bắc Bộ) tắt bằng `defaultLabels: false` — **không tắt khi khung có Biển Đông** |
| `markers: [{lon, lat, label, from, to, size, dx, dy}]` | chấm vàng nhấp nháy + nhãn |
| `satellite: {from, dur}` | hiện dần ảnh Sentinel-2 vùng Tây Bắc (để hoà hình sang map3d) |
| `titles: [{text, sub, from, x, y, size, align}]` | chữ lớn |

Shot: `vn-a-bay-xuong-dbp` (toàn cảnh → Tây Bắc → Điện Biên Phủ → ảnh vệ tinh; nối `map3d/shot-a-toan-canh` bằng hoà hình), `vn-b-toan-canh-ket` (cảnh kết, Hiệp định Giơ-ne-vơ).

## 3. cards — thẻ chữ, số (`type`)

| `type` | Tham số riêng |
|---|---|
| `so-lieu` | giấy kraft. `tag`, `kicker`, `title` (đầu thẻ kiểu hồ sơ). `items: [{value, from, dur, unit, label, prefix, suffix, dec, size}]` 1–3 số đếm chạy lần lượt; `layout: 'row'` (cạnh nhau) hoặc `'single'` |
| `lich` | `month`, `year`, `day` (khoanh đỏ vẽ dần lúc `circleAt`), `note`, `noteSub` |
| `dong-thoi-gian` | `axis: {from:[d,m,y], to, ticks:[{d, label}]}`, `lanes: [{name, start, end, dates, note, activeFrom, activeTo, grow, open}]` (`open: true` = không chốt ngày kết thúc, thanh mờ dần) |
| `van-kien` | nền nâu tối. `kicker`, `title`, `y`, `blocks: [{text, from, perWord, size, font: 'serif', maxW, color, dimAt, marks: [{phrase, type: 'strike'\|'highlight', at, dur}]}]`, `cite`, `citeAt`. Trích lãnh tụ: chữ nguyên văn, không giọng đọc |
| `chuong` | `number`, `title`, `kicker`, `hit` (giây đập: phóng to → về, chớp trắng) |
| `hook` | nền đen. `lines: [{text, at, size, color, shake, flash, spacing}]`, `glows: [{at, len, x, y}]` (vết sáng chớp xa) |
| `lower-third` | `name`, `role`, `detail`, `from`, `to`, `y`; `previewBg` chỉ để soi (bỏ khi render `--transparent`) |

Mọi thẻ: `source` (chú thích nguồn), `seed` (vân giấy).

**Hệ nhận diện (mặc định cho mọi `type` và cho overlay).** Nền olive than có rằn ri tông gần nền, đầu thẻ nhãn hộp vàng + tiêu đề Oswald + vạch có đoạn đậm, năm mờ làm nền (`nam`, hoặc 4 số đầu của `tag`), bảng sẫm cho chữ dày, nguồn góc phải dưới, logo Goha góc trái dưới (`logo: false` để tắt), chữ nội dung ≥ 40 px. Thêm tham số:

| Tham số | Ý nghĩa |
|---|---|
| `moc: [giây, ...]` | mốc hiện từng phần tử (`items`, `lanes`, `blocks`, các dòng của `hai-cot`) theo mốc lời; ưu tiên hơn `from` riêng |
| `nhip: {from, to, buoc}` | chia đều mốc hiện các phần tử |
| `nam` | năm mờ nền (mặc định lấy từ `tag` hoặc `year`) |
| `nhanDien: false` | vẽ bằng mã cũ trong `cards.js` (dựng lại shot cũ y nguyên) |

Màu đỏ son cũ trong shot (`#c93b2b` …) tự đổi sang màu đọc được trên nền olive. Mẫu mốc lời: `cards/shots/nd-mau-so-lieu-theo-loi.js`.

**Năm mẫu «bằng chứng gốc» (P2).** Cùng hệ nhận diện, cùng `moc` / `nhip` / `loi`; mọi mẫu bắt buộc có `source`; dữ liệu giả đặt `mau: true` (thẻ tự đóng tem «MẪU · DỮ LIỆU GIẢ»). Dữ liệu xấu thì trang không dựng được và báo lỗi tiếng Việt (không cắt chữ, không kéo giãn ảnh). Shot mẫu `cards/shots/p2-*.js`, dữ liệu mẫu `data/mau-p2/` (sinh bằng `tools/tao_du_lieu_mau_p2.py`).

| `type` | Tham số riêng |
|---|---|
| `tai-lieu-dich` | `anh` (trang scan), `kicker`, `title`, `tenTL` (tên tài liệu ở nhãn BẢN DỊCH), `cau: [{goc, dich, vung: [x, y, rộng, cao] chuẩn hoá trên trang, tuKhoa}]`, `moc: [giây]` hoặc `loi: {tep: words.json của kit, cum: [cụm đầu mỗi câu], offset}` |
| `phim-panel` | `phim: {mau: '…/f%03d.jpg', n, fps, batDau, dau, lap, fit: 'vua'\|'phu'}` (khung trích sẵn bằng `tools/trich_khung_phim.py <video> --tu --dai --fps --out-dir`; tối đa 150 khung, không dùng thẻ `<video>`), `so: {value, unit, label, dec, suffix, prefix}`, `panelNhan`, `chip: [{text, kieu}]` (≤ 4), `moc` (số, rồi từng chip) |
| `the-am-thanh` | `nhan` **bắt buộc**: «MÔ PHỎNG LẠI» hoặc «GHI ÂM GỐC»; `anh`, `anhNeo`, `nguoi: {ten, chucVu, boiCanh}`, `giong: {tep: '<giọng thật>', peaks: '….peaks.json', batDau}` (giọng + `duration` phải khớp trong 0,5 s) (tạo bằng `tools/song_am.py <giọng> --out …`: tính trước từ tệp giọng thật), `phuDe: [{text}]`, `moc`/`loi`, `lanhTu` |
| `nhan-vat` | `bienThe` **bắt buộc**: `tach-nen` (PNG đã tách nền, người không phải lãnh tụ) hoặc `khung` (ảnh cắt khung vuông vắn 4:5 `cat: [tâmX, tâmY, rộng]`, viền trang trọng, chỉ phóng đều `zoomDen` ≤ 1,08); `anh`, `ten`, `chucVu` (đúng thời điểm), `chiTiet`, `lanhTu`, `moc` (tên, chức danh, chi tiết) |
| `bieu-do` | `kieu`: `cot-doi` (`hang: [{nhan, ta, dich}]` ≤ 3, `tenTa`, `tenDich`, `thang: 'chung'`) hoặc `nguoi` (`nhom: [{ten, soLuong, mau, donVi}]` ≤ 2, `moi` = người mỗi hình ≤ 80 hình, `donVi`); `moc` |

**Máy chặn luật cứng (nghi ngờ thì chặn):** `python tools/build_shots.py` đánh giá mọi tệp shot của khối và mọi trang HTML còn lại của `cards/` (kể cả viết tay) bằng node, rồi dừng và báo lỗi khi: `nhan-vat` có `lanhTu: true` mà không phải biến thể `khung` (hoặc ảnh lãnh tụ đã tách nền); `the-am-thanh` thiếu `nhan` hoặc `nhan` ngoài hai nhãn; `the-am-thanh` có `lanhTu: true` mà `nhan` khác «GHI ÂM GỐC»; `lanhTu` không phải bool; tên trong `data/lanh-tu.json` (danh sách dùng chung, chưa đủ, ai gặp tên thì thêm; Tố Hữu không thuộc) xuất hiện ở bất kỳ trường chữ nào mà quên `lanhTu`; `giong.tep` thiếu hoặc sha256 lệch peaks, giọng lệch `duration` quá 0,5 s; `anh`/tệp là URL, `data:` hay thiếu trên đĩa; thiếu `source`; `phim.n` không nguyên dương hoặc khung phim vượt 450 MB; `cat` ảnh lãnh tụ phóng quá 2 lần. Lớp JS `cards/luat-cung.js` kiểm lại cùng luật khi trang chạy nên HTML viết tay cũng không READY nếu vi phạm. Test: `python -m pytest tools/test_luat_cung.py`, `node --test tools/luat-cung.test.mjs`. Soi 3 mốc: `python -I -X utf8 tools/soi-nhan-dien.py p2 <thư mục>`.

Kiểm (cần `reelcrew`, numpy, Pillow: `pip install -r requirements.txt`): `python -I -X utf8 tools/do-tuong-phan.py <thư mục ra>` đo tương phản (WCAG) trên ảnh soi có chữ và không chữ, chữ nhỏ nhất và số nhịp hiện; ngưỡng ở spec P1 (thoát mã 1 nếu có trang không ĐẠT hoặc LỖI); `python -m pytest tools/test_do_tuong_phan.py` test máy đo; `tools/soi-nhan-dien.py` chụp 3 mốc, ghép ảnh trước/sau, chụp khói mọi trang; `node --test tools/nhip-hien.test.mjs` test logic nhịp hiện.

## 4. archival — ảnh tư liệu

`image` (đường dẫn tương đối từ `archival/`), `move: [{t, x, y, zoom, ease}]` (Ken Burns; `x, y` tâm 0–1 theo ảnh, `zoom` 1 = phủ kín khung), `grade: 'bw-am' | 'bw' | 'goc' | 'phai-mau'`, `grain` (0–0.3), `seed`, `shake` (px), `flicker`, `vignette`, `scratches: false`, `date`, `credit`.

**2.5D parallax** (chỉ TÁCH lớp, không vẽ thêm nội dung, không AI):
`layers: [{name, depth, poly: [[x,y]...], feather, shadow}]` — polygon toạ độ 0–1 theo ảnh gốc, vẽ tay theo ảnh (mở ảnh có lưới 10% để đọc toạ độ). Lớp sau trong danh sách nằm trên. `depth` 0 (xa) … 1+ (gần). Nền = cả ảnh phóng nhẹ + mờ `bgBlur` (px) để che vùng lộ sau tiền cảnh, lệch theo `bgDepth`. `drift: {x, y, zoom}` = biên độ camera trôi cả shot (px, tỉ lệ). `shadow` (px) chỉ bật khi mép lớp không nằm trên vùng trơn như trời. `dust: {count, opacity, smoke, seed, wind}` = bụi lơ lửng + khói mỏng vẽ bằng code.

**Ảnh có lãnh tụ** (Chủ tịch Hồ Chí Minh, Đại tướng Võ Nguyên Giáp, lãnh đạo khác): đặt `lanhTu: true` — engine bỏ tách lớp, rung, nhấp nháy, hạt, xước, bụi; giữ màu gốc (`grade: 'goc'`); chỉ Ken Burns zoom rất chậm toàn ảnh (trần 8%).

Shot: `anh-ams-ban-do` (bản đồ AMS L7014 tờ 5651-IV), `anh-keo-phao-parallax` (3 lớp), `anh-luu-phao-105-parallax` (trời / dàn pháo + người / cỏ), `anh-lanh-tu-ken-burns` (chế độ lãnh tụ).

## Luật cứng (soi trên still trước khi giao)

1. Khung có Việt Nam/Biển Đông: Hoàng Sa + Trường Sa cùng màu Việt Nam, có nhãn, có "BIỂN ĐÔNG"; không đường lưỡi bò hay ranh giới biển; không nền/tile/dữ liệu nguồn Trung Quốc; không cờ VNCH.
2. Không ảnh AI, không tạo hình người tả thực; hình bộ đội chỉ là biểu tượng minh họa.
3. Mọi cảnh có chú thích nguồn góc phải dưới.
4. Chữ Việt đủ dấu: chỉ dùng font trong `fonts/`.

## 5. overlay — lớp chữ trong suốt phủ lên phim tư liệu

Vẽ theo hệ nhận diện (chữ lớn ≥ 72 px, thẻ tên, nhãn ngày, nguồn có dải tối; `nhanDien: false` giữ bản cũ; `logo: true` để thêm logo).

`duration`, `date`, `credit`, `texts: [{text, sub, from, to, x, y, size, color}]`. Render `--transparent` (ProRes 4444) rồi ghép bằng ffmpeg `overlay`. Lower-third (`cards`, `type: 'lower-third'`, `previewBg: null`) cũng phủ theo cách này.

## Co giãn shot theo EDL

Mọi khối nhận `fit` (thời lượng dựng thật, s): mọi keyframe co/giãn đều, chuyển động giữ trọn; `tail` (s): giữ khung cuối thêm để hoà sang cảnh sau. Shot con của một phim: `<khoi>/shots/<nhom>/<ten>.js` sinh `<khoi>/<nhom>-<ten>.html`.

## Phim mẫu Điện Biên Phủ

`python tools/film_dbp.py write | render [S##...] [--force] | assemble` — bảng 33 cảnh theo `plans/261025-1950-dien-bien-phu-thu/edl-v1.md`; cảnh = shot gốc + chỉnh riêng (`<khoi>/shots/dbp/s##.js`). Ra `output/261025-dien-bien-phu-mau/render/scenes/S##.mp4`, `picture-v1.mp4` (không âm thanh, 24 fps), `picture-v1-sheet.jpg`; in bảng mốc từng cảnh. Phim Karmen: trích theo mốc đã dò cắt cảnh, bỏ tiếng, cắt khung 4:3 phủ 16:9, giảm bão hoà 30 %, tăng tương phản, hạt, vignette, lớp chữ phủ.
