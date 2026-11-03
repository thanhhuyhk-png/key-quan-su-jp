# Tập 1 · Điện Biên Phủ 1954: phân cảnh (P3, 01/11/2026)

Nguồn sự thật duy nhất cho hình của tập. Lời: `ke-hoach/loi-doc-v5.txt` (223 câu). Chuẩn: `template/chuan-dao-dien.md`, luật cứng ở `CLAUDE.md`. Tư liệu ảnh (hạng, ghi nguồn): `anh.tsv`. Máy kiểm: `python -I kiem-phan-canh.py` (đọc bảng dưới, ghi `phan-canh.json`, `tai-san-can-dung.md` và mục Tóm tắt; thoát mã 1 nếu trượt luật).

## Cách đọc
- **Neo**: cảnh bắt đầu ở câu `N` (đếm câu có chữ trong lời đọc), `N:k` (từ chữ thứ k của câu, đếm từ 0), hoặc tên khoảng lặng. Cảnh kéo tới neo của cảnh sau. Chưa có giọng nên giây là ước tính (242 tiếng/phút + khoảng lặng); sau P4 máy thay bằng mốc chữ thật từ STT, rồi đo lại mọi trần thời lượng.
- **Nguồn hình**: `anh:<tệp>` ảnh tư liệu (archival, Ken Burns hoặc tách lớp 2.5D) · `karmen:<mm:ss>` phim «Việt Nam» (Karmen 1955, hạng B, ≤ 5 s, tắt tiếng gốc) · `3d:<cảnh mẫu>` dựng lại cảnh 3D đã có của bản mẫu (`tap/dien-bien-phu-mau/san-xuat/ban-full/phan-canh.json`, `ban-thu-3d/phan-canh.md`), khớp lại thời lượng · `3d-moi:<sân khấu>` cảnh 3D mới trên sân khấu và kho có sẵn · `map3d:<tên>` địa hình lòng chảo (không chạm biển) · `vnmap:<tên>` bản đồ chính trị (luôn có Hoàng Sa, Trường Sa, "Biển Đông") · `the:<kiểu>/<tên>` thẻ chữ, số (`template/cards`) · `can-tim:<tên>` tư liệu chưa có, kèm phương án thay.
- **Cỡ / góc**: `dac-ta, can, trung, toan, toan-xa, ban-do, the, anh, phim` / `thap, ngang, cao, tren-xuong, chech, cat-lop, phang`.
- **Chữ trên hình**: mọi thẻ có số phải ghi "Nguồn:". Ghi nguồn góc phải dưới do máy sinh: ảnh, phim lấy từ `anh.tsv`; đồ họa ghi "Đồ họa minh họa" kèm nguồn số liệu của thẻ.

## Khoảng lặng có tên
| Tên | Sau | Giây | Dùng |
|---|---|---|---|
| P1 | 24 | 6 | nhạc + tiêu đề phim |
| P2 | 93 | 4 | lời Chủ tịch Hồ Chí Minh chỉ ở chữ trên hình |
| A1 | 176 | 2.5 | tiếng nổ bộc phá A1 (tiếng lớn vào lặng); tách tại ranh câu khi đặt giọng |
| P3 | 211 | 4 | thư khen 8/5/1954 chỉ ở chữ trên hình |
| GN | P3 | 3 | ảnh văn bản Hiệp định Giơ-ne-vơ, thẻ ngày, nhạc |
| KT | 223 | 6 | thẻ câu hỏi bình luận cuối phim, hàng mộ, tắt nhạc |
| T1 | 1 | 1.5 | khoảng thở: 195 tấn đếm xong (cảnh trước giữ hình, lời ngừng) |
| T2 | 3 | 1.5 | khoảng thở: 6 TẤN (cảnh trước giữ hình, lời ngừng) |
| T3 | 8 | 1.0 | khoảng thở: niềm tin thứ nhất gõ xong (cảnh trước giữ hình, lời ngừng) |
| T4 | 11 | 3.0 | khoảng thở: gõ lời hứa ba phát (cảnh trước giữ hình, lời ngừng) |
| T5 | 15 | 3.0 | khoảng thở: gõ xong câu hỏi lớn (cảnh trước giữ hình, lời ngừng) |
| T6 | 17 | 1.0 | khoảng thở: hai cuốn sổ mở (cảnh trước giữ hình, lời ngừng) |
| T7 | 18 | 2.0 | khoảng thở: gõ xong ba điều quay lại (cảnh trước giữ hình, lời ngừng) |
| T8 | 22 | 2.0 | khoảng thở: hai cột sổ ghi xong (cảnh trước giữ hình, lời ngừng) |
| T9 | 25 | 1.5 | khoảng thở: gạch Điện Biên Phủ khỏi kế hoạch (cảnh trước giữ hình, lời ngừng) |
| U1 | 26 | 1.5 | khoảng thở: khoanh ngày 24/7 (cảnh trước giữ hình, lời ngừng) |
| U2 | 27 | 2.0 | khoảng thở: thanh 18 tháng (cảnh trước giữ hình, lời ngừng) |
| U3 | 29 | 1.5 | khoảng thở: bản đồ dừng ở Điện Biên Phủ (cảnh trước giữ hình, lời ngừng) |
| U4 | 33 | 1.5 | khoảng thở: hai đợt nhảy dù (cảnh trước giữ hình, lời ngừng) |
| U5 | 39 | 2.0 | khoảng thở: gõ xong 'nhọt hút độc' (cảnh trước giữ hình, lời ngừng) |
| V1 | 41 | 1.5 | khoảng thở: khoanh lịch 3/12 (cảnh trước giữ hình, lời ngừng) |
| V2 | 46 | 2.0 | khoảng thở: gõ xong lời ông Trần Quốc Hanh (cảnh trước giữ hình, lời ngừng) |
| V3 | 49 | 3.0 | khoảng thở: đáy chương 1: bẫy đã chọn, máy hạ vào lòng chảo (cảnh trước giữ hình, lời ngừng) |
| V4 | 55 | 1.5 | khoảng thở: số 11.800 đếm xong (cảnh trước giữ hình, lời ngừng) |
| V5 | 56 | 1.5 | khoảng thở: ba số hỏa lực (cảnh trước giữ hình, lời ngừng) |
| V6 | 58 | 2.0 | khoảng thở: gõ xong niềm tin của Pi-rốt (cảnh trước giữ hình, lời ngừng) |
| V7 | 67 | 1.5 | khoảng thở: trang 24/12 (cảnh trước giữ hình, lời ngừng) |
| V8 | 69 | 2.0 | khoảng thở: gõ xong '100%' (cảnh trước giữ hình, lời ngừng) |
| V9 | 70 | 1.0 | khoảng thở: gạch '100%' (cảnh trước giữ hình, lời ngừng) |
| W1 | 72 | 3.0 | khoảng thở: đáy chương 2: hai trang, nói một đằng viết một nẻo (cảnh trước giữ hình, lời ngừng) |
| W2 | 76 | 1.5 | khoảng thở: đường qua núi phía bên kia (cảnh trước giữ hình, lời ngừng) |
| W3 | 80 | 1.5 | khoảng thở: hai số kéo pháo (cảnh trước giữ hình, lời ngừng) |
| W4 | 89 | 2.0 | khoảng thở: bốn số pháo ta (cảnh trước giữ hình, lời ngừng) |
| W5 | 92 | 1.5 | khoảng thở: giờ bắn không đến (cảnh trước giữ hình, lời ngừng) |
| W6 | 95 | 2.0 | khoảng thở: đổi phương châm (cảnh trước giữ hình, lời ngừng) |
| W7 | 101 | 1.5 | khoảng thở: gõ xong 'như sét đánh ngang tai' (cảnh trước giữ hình, lời ngừng) |
| W8 | 105 | 2.741 | khoảng thở: lặng sau "Ông anh dũng hy sinh", trời sao (cảnh trước giữ hình, lời ngừng) |
| WA | 105:17 | 0.5 | khe giữa dòng: gió vực sau "một bên vực sâu" (v3) |
| WB | 105:22 | 1.0 | khe giữa dòng: dây tời đứt, tao dây quất (v3) |
| WC | 105:33 | 1.0 | khe giữa dòng: pháo trôi, bánh nghiến sỏi (v3) |
| WD | 105:44 | 1.0 | khe giữa dòng: bánh pháo khựng lại, sỏi lăn xuống vực; tiếng của khẩu pháo, không tiếng va vào người (v3) |
| W9 | 106 | 1.0 | khoảng thở: khoanh lịch 5/2 (cảnh trước giữ hình, lời ngừng) |
| X1 | 112 | 2.5 | khoảng thở: đáy chương 3, lặng căng chờ: câu hỏi đúng hay sai (cảnh trước giữ hình, lời ngừng) |
| X2 | 116 | 1.5 | khoảng thở: 3 PHÁT (cảnh trước giữ hình, lời ngừng) |
| X3 | 125 | 2.0 | khoảng thở: gõ xong lời Pi-rốt (cảnh trước giữ hình, lời ngừng) |
| X4 | 128 | 1.5 | khoảng thở: 3 PHÁT vỡ (cảnh trước giữ hình, lời ngừng) |
| X5 | 130 | 2.0 | khoảng thở: niềm tin thứ nhất: SAI (cảnh trước giữ hình, lời ngừng) |
| X6 | 133 | 1.5 | khoảng thở: hai số tăng viện (cảnh trước giữ hình, lời ngừng) |
| X7 | 137 | 1.0 | khoảng thở: thanh ba đợt (cảnh trước giữ hình, lời ngừng) |
| X8 | 149 | 3.0 | khoảng thở: đáy chương 4: người trong hào vẫn đào (cảnh trước giữ hình, lời ngừng) |
| X9 | 153 | 2.0 | khoảng thở: 6 TẤN (cảnh trước giữ hình, lời ngừng) |
| Y1 | 155 | 2.0 | khoảng thở: cần 200, thu 100 (cảnh trước giữ hình, lời ngừng) |
| Y2 | 157 | 1.5 | khoảng thở: gõ xong 'giữ yên bầu trời' (cảnh trước giữ hình, lời ngừng) |
| Y3 | 163 | 2.5 | khoảng thở: gõ xong câu hỏi đào hầm (cảnh trước giữ hình, lời ngừng) |
| Y4 | 167 | 1.5 | khoảng thở: ba điều phải giải quyết (cảnh trước giữ hình, lời ngừng) |
| Y5 | 172 | 1.5 | khoảng thở: thanh ba đợt, đợt 3 (cảnh trước giữ hình, lời ngừng) |
| Y6 | 175 | 3.0 | khoảng thở: đáy chương 5: lặng trong lòng hầm trước tiếng nổ (cảnh trước giữ hình, lời ngừng) |
| Y7 | 184 | 2.0 | khoảng thở: niềm tin thứ hai còn dấu hỏi (cảnh trước giữ hình, lời ngừng) |
| Y8 | 185 | 1.0 | khoảng thở: con đường tiếp tế sau dãy núi (cảnh trước giữ hình, lời ngừng) |
| Y9 | 187 | 1.0 | khoảng thở: cột số thứ nhất (cảnh trước giữ hình, lời ngừng) |
| Z1 | 190 | 1.0 | khoảng thở: cột số thứ hai (cảnh trước giữ hình, lời ngừng) |
| Z2 | 193 | 1.5 | khoảng thở: số 40.000 (cảnh trước giữ hình, lời ngừng) |
| Z3 | 198 | 1.5 | khoảng thở: số xe thồ (cảnh trước giữ hình, lời ngừng) |
| Z4 | 201 | 2.0 | khoảng thở: hai cột đủ số (cảnh trước giữ hình, lời ngừng) |
| Z5 | 204 | 3.5 | khoảng thở: đáy chương 6: lặng tưởng nhớ người hy sinh (cảnh trước giữ hình, lời ngừng) |
| Z6 | 205 | 2.0 | khoảng thở: hai niềm tin: SAI (cảnh trước giữ hình, lời ngừng) |
| Z7 | 210 | 1.0 | khoảng thở: lá cờ trên nóc hầm (cảnh trước giữ hình, lời ngừng) |
| Z8 | 216 | 1.5 | khoảng thở: 3 PHÁT lần cuối (cảnh trước giữ hình, lời ngừng) |
| ZA | 121 | 1.5 | khoảng thở (v4): lặng sau Phan Đình Giót lấp lỗ châu mai (cảnh trước giữ hình, lời ngừng) |
| ZB | 189 | 1.0 | khoảng thở (v4): hai số chính thức của trận đánh (cảnh trước giữ hình, lời ngừng) |
| ZC | 200 | 1.0 | khoảng thở (v4): ba số sức người (cảnh trước giữ hình, lời ngừng) |
| Z9 | 222 | 2.0 | khoảng thở: ba số nghĩa trang A1 (cảnh trước giữ hình, lời ngừng) |
| H1 | 114 | 3.5 | mốc khí thế (v3): loạt pháo mở màn bắn vào Him Lam: pháo bắn đi, đạn rít, nổ dồn xa vọng núi, rung trầm, đất rơi |
| H2 | X7 | 2.0 | mốc khí thế (v3): đợt 2 mở màn: pháo loạt, súng máy, hô xung phong xa |
| H3 | 174 | 1.5 | mốc khí thế (v3): loạt hỏa tiễn H6 rít qua đầu, nổ dày |
| H4 | 178 | 1.75 | mốc khí thế (v3), một cụm với A1, đỉnh thấp hơn A1: toàn mặt trận tiến công: pháo mọi hướng, súng máy, hô xung phong vang lòng chảo |

## Bảng phân cảnh
<!-- BANG -->
| # | Neo | Nguồn hình | Cỡ / góc | Hình | Chữ trên hình | Âm |
|---|---|---|---|---|---|---|
| MO01 | 1 | karmen:44:38.90 | trung/ngang | Hòm hàng tiếp tế của phía Pháp xếp chồng ở Điện Biên Phủ. | Nhãn ngày "9/4/1954 · Nguồn: Báo QĐND" | gỗ hòm va, gió |
| MO02 | 1:13 | demo:BD8 | toan/tren-xuong | Nhìn chéo từ trên sân bay Mường Thanh: dù tiếp tế nhiều màu rơi, nhiều dù lệch về phía ta; nhánh hào ta bò tới đường băng (3D Demo đã duyệt). | | động cơ C-47 trầm, tán dù bật |
| MO03 | 1:23 | the:so-lieu/195-tan | the/phang | Số đếm chạy 0 → 195 trên nền vải ô-liu quân phục. | "195 tấn hàng thả xuống · 9/4/1954 · Nguồn: Báo QĐND" | số chạy tích tắc |
| MO04 | 2 | karmen:44:42.10 | dac-ta/ngang | Đặc tả hàng thùng phuy tiếp tế, máy lia ngang. | | kim loại thùng va khẽ |
| MO05 | 3 | the:hook/6-tan | the/phang | Chữ "6 TẤN" trắng lớn trên nền đen, rung nhẹ khi hiện. | "6 tấn · Nguồn: Báo QĐND" | một nhịp trống trầm, rồi im |
| MO06 | 4 | karmen:44:36.64 | trung/cao | Đống đạn pháo tiếp tế của phía Pháp, máy lia chậm. | | kim loại va khẽ, gió |
| MO07 | 5 | anh:toan-canh-canh-dong-dien-bien-ttxvn-1953 | anh/phang | Cánh đồng Điện Biên năm 1953, Ken Burns chậm sang phải. | Nhãn "1953" | nhạc nền vào |
| MO08 | 6 | map3d:shot-a-toan-canh | ban-do/cao | Bay vào lòng chảo, cánh đồng sáng lên giữa vành núi; không chạm biển. | "lòng chảo rộng nhất Tây Bắc · căn cứ không-bộ · tiếp tế bằng máy bay · Nguồn: Báo Nhân Dân" | gió núi |
| MO09 | 7 | karmen:43:56.30 | trung/thap | Hầm vòm tôn và hòm gỗ của phía Pháp sau hàng thép gai. | | thép gai, gió |
| MO10 | 8 | the:may-chu/niem-tin | the/phang | Hai thẻ niềm tin hiện lần lượt (thẻ 1 ở câu 8, thẻ 2 ở câu 9). | "Bộ chỉ huy Pháp tin: ta không đưa được pháo lớn tới · Nguồn: Báo Nhân Dân" / "Bộ chỉ huy Pháp tin: ta không nuôi nổi một lực lượng lớn đánh lâu ở xa hậu phương · Nguồn: Báo Nhân Dân" | giấy lật |
| MO11 | 9:11 | karmen:41:13.50 | toan/cao | Con đường đất đỏ uốn qua rừng núi Tây Bắc. | | gió núi, bánh xe xa |
| MO12 | 10 | karmen:44:45.00 | toan/ngang | Dãy lựu pháo của phía Pháp ở Điện Biên Phủ, nòng chĩa lên. | Thẻ tên "Trung tá Pi-rốt · chỉ huy pháo binh, chỉ huy phó tập đoàn cứ điểm · Nguồn: TTXVN" (không có ảnh) | kim loại khẽ |
| MO13 | 10:12 | karmen:44:48.90 | can/thap | Cận khẩu lựu pháo của phía Pháp, càng pháo và bánh xe. |  | nòng thép ù |
| MO13b | 10:25 | anh:chuyen-dan-vao-ham-phao-01 | anh/chech | Bộ đội ta chuyển đạn vào hầm pháo, Ken Burns chậm. | | đạn va gỗ khẽ |
| MO14 | 11 | the:may-chu/3-phat | the/phang | Chữ "3 PHÁT" trắng lớn trên nền đen. | "3 phát · Nguồn: TTXVN" | ba tiếng gõ khô |
| MO15 | 12 | karmen:44:24.30 | toan/ngang | Xác máy bay của phía Pháp nằm trên sân bay Mường Thanh, cánh quạt gãy. | "cuối tháng 3/1954 · máy bay Pháp không còn hạ cánh được · Nguồn: Báo Nhân Dân" | gió, kim loại kẽo kẹt |
| MO16 | 13 | anh:phao-cao-xa-ban-01 | anh/chech | Pháo cao xạ ta bắn, Ken Burns đẩy vào nòng. | | cao xạ xa |
| MO17 | 14 | anh:quan-phap-ra-hang-cau-muong-thanh-01 | anh/phang | Quân Pháp ra hàng trên cầu Mường Thanh, phóng chậm. | "7/5/1954 · Nguồn: Báo QĐND" | nhạc lùi |
| MO18 | 15 | the:may-chu/cau-hoi | the/phang | Câu hỏi trên nền tối, bản đồ lòng chảo mờ phía sau. | "Vì sao Bộ chỉ huy Pháp chọn Điện Biên Phủ, rồi thua ở chính nơi đó?" · "56 ngày đêm · 13/3 – 7/5/1954 · Nguồn: Báo QĐND" | im, một nốt đàn trầm |
| MO19 | 16 | anh:tren-noc-ham-de-castries-01 | anh/thap | Bộ đội trên nóc hầm Đờ Cát-xtơ-ri, phóng chậm. | | nhạc trở lại |
| MO20 | 17 | the:hai-so/mo | the/phang | Hai cuốn sổ đồ họa mở ra hai bên khung, trang trống. | Trái "phía Pháp tin / ghi" · phải "quân và dân ta làm" | sổ mở |
| MO21 | 18 | map3d:ba-quyet-dinh | ban-do/cao | Lòng chảo từ cao; đường trời (nét đứt) và hai thẻ niềm tin hiện trên bản đồ. | | gió |
| MO22 | 18:11 | the:may-chu/quay-lai | the/phang | Hai thẻ niềm tin và nhãn "đường trời" lật ngược, quay mũi về phía Pháp. | "Nguồn: Báo Nhân Dân" | giấy lật |
| MO23 | 19 | map3d:ba-quyet-dinh | ban-do/tren-xuong | Mũi tên ① quanh tập đoàn cứ điểm, các cứ điểm mọc gai. | "① Bộ chỉ huy Pháp: con nhím sống nhờ cầu hàng không · Nguồn: Báo Nhân Dân" | |
| MO24 | 20 | map3d:ba-quyet-dinh | ban-do/chech | Mũi tên ② từ trận địa trên núi lùi ra rồi đặt lại vòng trận địa mới. | "② Ta: đánh chắc, tiến chắc · 26/1/1954 · Nguồn: Báo QĐND" | |
| MO25 | 21 | map3d:ba-quyet-dinh | ban-do/cao | Mũi tên ③: hào đỏ siết vào, cắt đôi đường băng. | "③ Ta: từ đợt hai, siết hào, cắt đôi sân bay · Nguồn: Báo Chính phủ, TTXVN" | |
| MO26 | 22 | the:hai-so/doi-chieu | the/phang | Hai cuốn sổ: trang trái hiện dòng "tin", trang phải hiện dòng "làm". | | bút viết |
| MO27 | 23 | demo:MM2> | toan/chech | Chiều 13/3: từ cạnh miệng hầm pháo ta nhìn ra lòng chảo khô, vành núi trong hơi sương (3D Demo đã duyệt, giữ khung cuối khi hết cảnh mẫu). | "13/3/1954 · Nguồn: Báo QĐND" | lá nguỵ trang, gió, dế xa |
| MO28 | 24 | map3d:shot-a-toan-canh | ban-do/cao | Máy rút cao khỏi lòng chảo, vành núi khép quanh như miệng bẫy. | | nhạc dâng |
| MO29 | 24:10 | karmen:43:12.20 | toan-xa/ngang | Cánh đồng lòng chảo, khói nổ bốc trên dãy đồi xa. | | nhạc dâng, nổ xa âm ỉ |
| MO30 | P1 | the:tieu-de/phim | the/phang | Tiêu đề phim trên nền tối. | "ĐIỆN BIÊN PHỦ 1954" | nhạc tiêu đề |
| C1-01 | 25 | the:chuong/1 | the/phang | Thẻ chương 1. | "Lòng chảo" | đập chương |
| C1-02 | 25:10 | vnmap:dong-duong | ban-do/cao | Đông Dương và Biển Đông, khung rộng có Hoàng Sa, Trường Sa, "Biển Đông", "Vịnh Bắc Bộ"; Điện Biên Phủ còn mờ. | Thẻ tên "Na-va · Tổng chỉ huy quân đội viễn chinh Pháp · 5/1953 · Nguồn: Báo QĐND" (không có ảnh) | nhạc nền |
| C1-03 | 25:25 | the:may-chu/ke-hoach-na-va | the/phang | Tờ hồ sơ kế hoạch gõ chữ, không có dòng nào ghi Điện Biên Phủ. | "Kế hoạch Na-va" | máy chữ |
| C1-04 | 26 | the:lich/24-7-1953 | the/phang | Lịch 24/7/1953, khoanh đỏ. | "24/7/1953 · kế hoạch Na-va được thông qua · Nguồn: Báo Nhân Dân" | bút khoanh |
| C1-05 | 27 | the:dong-thoi-gian/18-thang | the/phang | Thanh thời gian khoảng 18 tháng từ 7/1953. | "khoảng 18 tháng · 'kết thúc chiến tranh trong danh dự' · Nguồn: Báo QĐND" | |
| C1-06 | 28 | vnmap:dong-duong | ban-do/cao | Khung rộng có Hoàng Sa, Trường Sa, "Biển Đông"; các khối tiểu đoàn cơ động (ô vuông) rải khắp đồng bằng và Trung Lào. | "84 tiểu đoàn cơ động · theo Thượng tướng Hoàng Minh Thảo · Nguồn: Báo Nhân Dân" | |
| C1-07 | 29 | vnmap:vn-a-bay-xuong-dbp | ban-do/tren-xuong | Bay từ khung rộng (có Hoàng Sa, Trường Sa, "Biển Đông") về Tây Bắc; Điện Biên Phủ sáng lên. | | nhạc chuyển |
| C1-08 | 30 | vnmap:tay-bac | ban-do/cao | Tây Bắc, khung dừng ở kinh độ ≤ 105,5° Đông, không chạm biển; mũi tên đỏ của ta hướng lên Tây Bắc. | | |
| C1-09 | 31 | anh:operation-castor-05782 | anh/phang | Ảnh hành quân Cát-to, phóng chậm. | "20/11/1953 · hành quân Cát-to (Hải Ly) · Nguồn: Báo Nhân Dân" | động cơ máy bay xa |
| C1-10 | 32 | 3d-moi:bau-troi | toan-xa/thap | Từ xa: đoàn C-47 thả dù xuống lòng chảo, tán dù như chấm trắng, không thấy người. | "6 tiểu đoàn dù · khoảng 4.500 quân · Nguồn: Báo Nhân Dân" | động cơ, gió |
| C1-11 | 33 | the:dong-thoi-gian/castor | the/phang | Hai thanh: ba tiểu đoàn ngày đầu, ba tiểu đoàn những ngày kế tiếp. | "20/11/1953 · Nguồn: Báo Nhân Dân" | |
| C1-12 | 34 | map3d:long-chao-loi-the | ban-do/cao | Lòng chảo từ cao, ba ghim số hiện lần lượt ở câu 35–37. | | |
| C1-13 | 35 | map3d:long-chao-loi-the | ban-do/tren-xuong | Nhìn thẳng xuống, thước đo dài 18 km, rộng 6–8 km. | "dài khoảng 18 km · rộng 6–8 km · Nguồn: Báo Nhân Dân" | |
| C1-14 | 36 | vnmap:tay-bac | ban-do/cao | Tây Bắc và Thượng Lào, không chạm biển; mũi tên che chở về phía Thượng Lào. | | |
| C1-15 | 37 | demo:TN1> | toan/cao | C-47 hạ cánh xuống sân bay Mường Thanh, bụi đỏ cuộn; rồi hầm vòm bao cát, thép gai bung (3D Demo TN1–TN2 đã duyệt, giữ khung cuối). | | động cơ hạ cánh, thép gai |
| C1-16 | 38 | the:may-chu/nhot-hut-doc | the/phang | Trích "nhọt hút độc" bằng chữ Lora, tô vàng cụm từ. | "'nhọt hút độc' · tướng Cô-nhi · Nguồn: Báo Nhân Dân" | |
| C1-17 | 40 | map3d:y-do-phap | ban-do/cao | Mũi tên đỏ bị hút vào lòng chảo, vòng khép quanh (nhãn "ý đồ của Bộ chỉ huy Pháp · minh họa"). | | |
| C1-18 | 41 | the:lich/3-12-1953 | the/phang | Lịch 3/12/1953. | "3/12/1953 · Na-va ra chỉ thị giao chiến · Nguồn: Báo Nhân Dân" | |
| C1-19 | 42 | anh:bac-ho-bo-chinh-tri-quyet-dinh-mo-chien-dich-01 | anh/phang | Ảnh lãnh tụ nguyên gốc, lanhTu: chỉ phóng rất chậm toàn ảnh, không đè chữ; thẻ đặt trên nền riêng cạnh ảnh. | "6/12/1953 · Bộ Chính trị quyết định mở chiến dịch · Nguồn: TTXVN" | nhạc trang nghiêm |
| C1-20 | 43 | map3d:long-chao-loi-the | ban-do/cao | Lòng chảo từ cao, hai mốc 3/12 và 6/12 hai bên. | "3/12 · 6/12/1953 · Nguồn: Báo Nhân Dân, TTXVN" | |
| C1-21 | 44 | 3d-moi:rung-nua | toan/ngang | Hàng bộ đội đi trong rừng nứa đêm, bóng không mặt, ánh sao lọt qua tán. | | lá nứa, bước chân |
| C1-22 | 45 | 3d-moi:rung-nua | dac-ta/thap | Đặc tả dép cao su bước trên lá nứa khô. | Thẻ tên "ông Trần Quốc Hanh · cán sự chính trị Tiểu đoàn 418, Đại đoàn 304 · Nguồn: Báo QĐND" | lá khô |
| C1-23 | 46 | the:van-kien/tran-quoc-hanh | the/phang | Lời trích hiện từng dòng. | "Ở Phú Thọ hơn tháng trời trong rừng nứa, bộ đội không được tiếp xúc với dân, không được tập luyện vì sợ lộ." · ông Trần Quốc Hanh · Nguồn: Báo QĐND | |
| C1-24 | 47:2 | karmen:40:44 | phim/ngang | Người đi gùi trên đường núi, áo dân thường. | | |
| C1-25 | 48 | map3d:long-chao-loi-the | ban-do/thap | Máy hạ dần vào lòng chảo Mường Thanh, chiều sang sáng. | | nhạc chuyển |
| C2-01 | 50 | the:chuong/2 | the/phang | Thẻ chương 2. | "Con nhím" | đập chương |
| C2-02 | 50:4 | 3d:TN2 | dac-ta/ngang | Cuộn thép gai bung căng trước máy, bao cát đập xuống chồng lớp trên nóc hầm. | | thép gai, bao cát |
| C2-03 | 51 | 3d-moi:ham-phap | toan/cao | Từ cao: cụm cứ điểm bao cát, hào, lô cốt giữa cánh đồng. | "① Bộ chỉ huy Pháp: con nhím · Nguồn: Báo Nhân Dân" | |
| C2-04 | 52 | 3d-moi:ham-phap | dac-ta/ngang | Đặc tả lỗ châu mai lô cốt, tối bên trong. | | gió qua khe |
| C2-05 | 53 | map3d:shot-b-ba-phan-khu | ban-do/cao | Ba phân khu sáng lần lượt đúng lúc đọc tên. | "49 cứ điểm · 3 phân khu: Bắc · Trung tâm · Nam (Hồng Cúm) · Nguồn: Báo QĐND" | |
| C2-06 | 54 | anh:castries-karnow-1954 | anh/phang | Ảnh Đờ Cát-xtơ-ri, phóng chậm. | "Đại tá Đờ Cát-xtơ-ri · về sau thăng Thiếu tướng · Nguồn: Báo QĐND" | |
| C2-07 | 55 | the:so-lieu/11800 | the/phang | Số chạy 11.800. | "khoảng 11.800 quân lúc mở màn · Nguồn: Báo Nhân Dân" | |
| C2-08 | 56 | 3d-moi:ham-phap | trung/thap | Hầm vòm bao cát của phía Pháp nhìn ngang, thép gai phía trước. | | |
| C2-09 | 56:12 | the:so-lieu/hoa-luc-phap | the/phang | Ba số chạy lần lượt. | "24 pháo 105 mm · 4 pháo 155 mm · 10 xe tăng · Nguồn: Báo Nhân Dân" | |
| C2-10 | 57 | 3d-moi:ham-phap | trung/chech | Hầm vòm bao cát nhìn từ phía sau, C-47 trên trời. | Thẻ tên "Trung tá Pi-rốt · Nguồn: TTXVN" | |
| C2-11 | 58 | the:niem-tin/pi-rot | the/phang | Thẻ niềm tin của Pi-rốt. | "Pi-rốt tin: ta chỉ có pháo nhỏ và súng cối · Nguồn: TTXVN" | |
| C2-12 | 59 | karmen:40:53.4 | phim/chech | Vách núi đá, người phá đá mở đường (phim Karmen, mô phỏng lại). | | đá vỡ, gió |
| C2-13 | 60 | map3d:con-nhim | ban-do/cao | Các cứ điểm trên bản đồ mọc gai như lưng con nhím. | "con nhím = căn cứ không-bộ · Nguồn: Báo Nhân Dân" | |
| C2-14 | 61 | 3d-moi:san-bay | dac-ta/thap | Đặc tả kiện hàng dù nằm trên đất cạnh đường băng. | | |
| C2-15 | 62 | vnmap:cau-hang-khong | ban-do/cao | Hà Nội → Điện Biên Phủ, đường bay vẽ dần; khung rộng có Hoàng Sa, Trường Sa, "Biển Đông", "Vịnh Bắc Bộ". | "cách Hà Nội hàng trăm km · Nguồn: Báo Nhân Dân" / "cầu hàng không từ 11/1953 · Nguồn: Báo Nhân Dân" | động cơ xa |
| C2-16 | 64 | 3d-moi:bau-troi | toan-xa/ngang | Máy bay vận tải trên cao trên sân bay Mường Thanh, dù tiếp tế rơi. | "khoảng 200 tấn/ngày · vài chục chuyến · Nguồn: Báo Nhân Dân" | động cơ |
| C2-17 | 65 | map3d:hai-san-bay | ban-do/cao | Hai sân bay Mường Thanh, Hồng Cúm sáng lên. | "2 sân bay: Mường Thanh, Hồng Cúm · Nguồn: Tư liệu văn kiện Đảng Cộng sản Việt Nam" | |
| C2-18 | 66 | anh:bearcat-muong-thanh-ecpad-1954 | anh/phang | Máy bay Bearcat ở Mường Thanh, phóng chậm. | | |
| C2-19 | 67 | anh:operation-castor-cogny-castries-05781 | anh/thap | Tướng Cô-nhi và Đại tá Đờ Cát-xtơ-ri ở Điện Biên Phủ (1953). | Nhãn "1953" | |
| C2-20 | 67:11 | the:hai-trang/24-12 | the/phang | Trang trái "nói với binh lính" hiện từng dòng. | "24/12/1953 · Na-va: trận đánh chỉ có thể thuận lợi cho phía Pháp · Nguồn: Báo Nhân Dân" | bút viết |
| C2-21 | 68 | the:hai-trang/1-1 | the/phang | Trang phải "thư riêng" mở ra. | "1/1/1954 · thư riêng · Nguồn: Báo Nhân Dân" | giấy |
| C2-22 | 69 | the:van-kien/thu-na-va | the/phang | Lời trích gõ chữ, "100%" tô vàng. | "Trước đây hai tuần, tôi đánh giá khả năng đó là 100%…" · Na-va, thư riêng 1/1/1954 · Nguồn: Báo Nhân Dân (trích tài liệu Pháp) | máy chữ |
| C2-23 | 70 | the:van-kien/thu-na-va | the/phang | Cùng thẻ: gạch ngang "100%". | | gạch bút |
| C2-24 | 71 | the:hai-trang/doi-chieu | the/phang | Hai trang cạnh nhau; trang trái mờ ở câu 72. | | |
| C2-25 | 73 | map3d:con-nhim | ban-do/chech | Con nhím trên bản đồ, hai thẻ niềm tin sáng phía trên. | "Nguồn: Báo Nhân Dân" | |
| C2-26 | 74 | 3d-moi:ham-phap | dac-ta/thap | Đặc tả bao cát và thép gai lô cốt từ dưới lên. | | |
| C2-27 | 75 | 3d-moi:ham-phap | trung/ngang | Từ trong lô cốt nhìn qua lỗ châu mai ra vành núi. | | gió qua khe |
| C2-28 | 76 | karmen:40:46.55 | phim/cao | Đoàn người gùi hàng nối nhau leo dốc núi, rồi người phá đá mở đường (phim Karmen, mô phỏng lại). | | bước chân, nhạc chuyển |
| C3-01 | 77 | the:chuong/3 | the/phang | Thẻ chương 3. | "Đổi cách đánh" | đập chương |
| C3-02 | 77:6 | map3d:shot-c-keo-phao | ban-do/cao | Đường kéo pháo bắt đầu vẽ từ Nà Nhạn. | "16/1/1954 · Nà Nhạn · Nguồn: Báo QĐND" | |
| C3-03 | 78 | anh:keo-phao-01 | anh/thap | Bộ đội kéo pháo, tách lớp 2.5D. | | dây căng |
| C3-04 | 79 | 3d:T-A1 | dac-ta/thap | Dây kéo căng, bàn chân bám đất dốc. | Thẻ tên "ông Phạm Đức Cư · chiến sĩ Tiểu đoàn 394, Trung đoàn cao xạ 367 · Nguồn: Báo QĐND" | dây kẽo kẹt |
| C3-05 | 80 | the:so-lieu/keo-phao | the/phang | Hai số chạy. | "mỗi khẩu 2,4 tấn · 80–100 người kéo · Nguồn: Báo QĐND" | |
| C3-06 | 81 | map3d:shot-c-keo-phao | ban-do/chech | Đường kéo pháo vẽ hết, nhãn 15 KM, đỉnh Pu Pha Sông. | "15 km · rộng 3 m · đỉnh Pu Pha Sông 1.150 m · Nguồn: Báo QĐND" | |
| C3-07 | 82 | 3d-moi:keo-phao | dac-ta/cao | Đặc tả lớp cành lá nguỵ trang phủ lên mặt đường mới mở. | | lá nguỵ trang |
| C3-08 | 83 | anh:keo-phao-02 | anh/phang | Kéo pháo qua đèo dốc, phóng chậm. | "cơm ăn ngay tại chỗ, ăn xong lao vào việc · Nguồn: Báo QĐND" | |
| C3-09 | 84 | karmen:41:30 | phim/ngang | Bộ đội nguỵ trang kéo khẩu pháo qua rừng. | Thẻ tên "ông Nguyễn Quang Thuận · chiến sĩ Đại đội 815, Tiểu đoàn 383 · Nguồn: Báo QĐND" | |
| C3-10 | 84:20 | 3d:thu-A2 | toan/thap | Toàn cảnh thấp ngang dốc, đội kéo pháo, trăng sau đồi. | Chữ "Hai… ba… nào" đúng lúc đọc · Nguồn: Báo QĐND | tiếng hô (không lời), dây |
| C3-11 | 85 | 3d-moi:keo-phao | dac-ta/ngang | Đặc tả bánh pháo nhích lên trên dốc, chèn gỗ đặt theo. | | gỗ nghiến |
| C3-12 | 86 | 3d-moi:keo-phao | toan-xa/cao | Toàn cảnh trời sao, đội kéo nhỏ trên sống núi. | "16/1 – 25/1/1954 · gần 10 đêm · Nguồn: Báo QĐND" | dế rừng đêm |
| C3-13 | 87 | map3d:nam-dai-doan | ban-do/cao | Năm khối đại đoàn hiện quanh lòng chảo. | "5 đại đoàn: 308 · 312 · 316 · 304 · 351 (công pháo) · Nguồn: Báo Nhân Dân" | |
| C3-14 | 88 | the:so-lieu/phao-ta | the/phang | Số 200 chạy, rồi ba số con ở câu 89. | "hơn 200 khẩu pháo và cối · Nguồn: Báo QĐND" / "24 lựu pháo 105 mm · 16 cối 120 mm · 24 cao xạ 37 mm · Nguồn: Báo QĐND" | |
| C3-15 | 90 | anh:luu-phao-105-bao-tang-ha-noi-01 | anh/thap | Lựu pháo 105 ở bảo tàng, máy dọc nòng (không nêu số hiệu). | | |
| C3-16 | 90:13 | 3d-moi:keo-phao | toan/chech | Khẩu 105 của ta trên sườn núi tháng 1, nòng hướng lòng chảo. | | |
| C3-17 | 91 | 3d:MM1 | trung/thap | Ụ pháo nguỵ trang, khẩu 105 nòng chỉ xuống lòng chảo, khẩu đội chờ ở xa; đổi nhãn thành 25/1/1954. | "25/1/1954 · phần lớn pháo đã vào trận địa · Nguồn: Báo Nhân Dân" | lá xào xạc |
| C3-18 | 92 | the:hook/gio-ban | the/phang | Đồng hồ đếm lùi dừng lại, kim đứng. | | tích tắc rồi tắt |
| C3-19 | 93 | map3d:long-chao-dem | ban-do/cao | Bản đồ lòng chảo tối, phóng rất chậm. | Thẻ tên "Đại tướng Võ Nguyên Giáp · Chỉ huy trưởng kiêm Bí thư Đảng ủy Mặt trận · Nguồn: Báo Nhân Dân" (chữ, không ảnh) | nhạc lùi |
| C3-20 | 93:22 | the:van-kien/loi-dan-dat | the/phang | Nền chữ tối chuẩn bị lời dặn (khung giấy hiện). | | |
| C3-21 | P2 | the:van-kien/loi-dan | the/phang | Lời Chủ tịch Hồ Chí Minh hiện chữ nguyên văn, không giọng đọc. | "Trận này rất quan trọng, phải đánh cho thắng. Chắc thắng mới đánh, không chắc thắng, không đánh" · lời Chủ tịch Hồ Chí Minh giao nhiệm vụ cho Đại tướng Võ Nguyên Giáp · Nguồn: Báo Nhân Dân | lặng, nhạc ~25 % |
| C3-22 | 94 | the:van-kien/phuong-cham | the/phang | Thẻ phương châm gõ chữ: "đánh nhanh, thắng nhanh" gạch bỏ, "đánh chắc, tiến chắc" hiện ra. | "26/1/1954 · đánh nhanh, thắng nhanh → đánh chắc, tiến chắc · Nguồn: Báo QĐND" | máy chữ |
| C3-23 | 96 | map3d:cu-diem-day | ban-do/tren-xuong | Phân khu Trung tâm: cứ điểm và công sự dày lên so với lúc lập kế hoạch. | | |
| C3-24 | 98 | 3d-moi:keo-phao | trung/cao | Khẩu pháo dừng giữa dốc, phủ lá, đội kéo ngồi chờ. | | gió |
| C3-25 | 99 | 3d-moi:him-lam | toan/ngang | Đồi Him Lam tháng 1: thép gai dày, lô cốt bao cát kín. | | |
| C3-26 | 100 | 3d:T-C1 | trung/thap | Trước miệng hầm tối, dây căng dần. | "đêm 26/1/1954 · Nguồn: Báo QĐND" | gỗ khung hầm |
| C3-27 | 101 | the:van-kien/set-danh | the/phang | Lời trích. | "như sét đánh ngang tai" · ông Nguyễn Quang Thuận · Nguồn: Báo QĐND | |
| C3-28 | 102 | 3d:T-C2 | trung/chech | Nòng ló khỏi hầm, đội kéo quay đầu. | | bánh lăn đất |
| C3-29 | 103 | karmen:41:40 | phim/thap | Cận bánh xe pháo lăn trên đất rừng. | | |
| C3-30 | 104 | 3d-moi:keo-phao | toan/chech | Pháo xuống dốc trong đêm, dây ghìm phía sau. | | dây ghìm |
| C3-31 | 105 | 3d:T-D1 | toan/cao | Sa bàn Dốc Chuối: đường xẻ vách núi, vực một bên, đêm không trăng. Soát khung: khẩu pháo phải là cao xạ. | "1/2/1954 · Dốc Chuối · Nguồn: Báo QĐND" | gió vực, dây căng kẽo kẹt |
| C3-31b | 105:18 | demo:T-D2> | dac-ta/ngang | Đặc tả dây tời bện căng, các tao dây tách rồi đứt; nối sang khẩu cao xạ bắt đầu trôi (3D Demo đã duyệt). | | dây đứt (WB) |
| C3-31c | 105:23 | 3d:T-D3 | trung/thap | Khẩu cao xạ 37 trôi xuống dốc trong đêm, càng pháo lao dốc (cảnh mẫu bản thử, co đồng hồ cho khớp lời). | | pháo trôi, bánh nghiến sỏi (WC) |
| C3-31d | 105:34 | demo:T-E1> | toan/ngang | Đội kéo phía sau; một bóng người lao tới chèn bánh pháo (không thấy mặt, không cảnh thương tích); cắt sang đặc tả bánh xe khựng lại (3D Demo đã duyệt). | | bánh pháo khựng (WD) |
| C3-32 | 105:45 | 3d:T-E4 | toan/thap | Pháo dừng bên mép vực, máy nâng chậm lên trời sao; không thấy người, không cảnh thương tích. | "Anh hùng Tô Vĩnh Diện · Khẩu đội trưởng, Đại đội 827 · 1/2/1954 · Nguồn: Báo QĐND" | nhạc ~25 %, gió |
| C3-33 | 106 | the:lich/5-2-1954 | the/phang | Lịch 5/2/1954, ghi mồng 3 Tết Giáp Ngọ. | "kéo pháo ra: đêm 26/1 – sáng 5/2/1954 (mồng 3 Tết Giáp Ngọ) · Nguồn: Báo QĐND" | |
| C3-34 | 107 | map3d:tran-dia-moi | ban-do/cao | Vòng trận địa mới quanh lòng chảo vẽ dần. | | |
| C3-35 | 108 | 3d-moi:tran-dia | trung/chech | Hầm pháo của ta trên sườn núi, nòng ló ra khỏi mái đất nguỵ trang. | "pháo đặt từng khẩu trong hầm · Nguồn: TTXVN" | |
| C3-36 | 109 | map3d:tran-dia-moi | ban-do/tren-xuong | Hai vòng: sơn pháo gần, lựu pháo xa; ở câu 110 thêm chấm đỏ là trận địa giả. | "trận địa giả · Nguồn: TTXVN" | |
| C3-37 | 111 | anh:luu-phao-105-san-sang-01 | anh/chech | Lựu pháo sẵn sàng trong trận địa, phóng chậm. | | |
| C3-37b | 111:6 | 3d-moi:ham-phap | toan/thap | Hầm vòm và thép gai phía Pháp nhỏ giữa cánh đồng, nhìn từ cao trong sương. | | nòng quay rít |
| C3-38 | 112 | the:cau-hoi/dung-sai | the/phang | Câu hỏi trên nền tối. | "Quyết định ấy đúng hay sai?" | im |
| C3-39 | 113 | 3d-moi:him-lam | toan-xa/ngang | Đồi Him Lam chiều 13/3 dưới nắng xiên, trăng ban ngày phía đông. | "13/3/1954 · Nguồn: Báo QĐND" | gió, nhạc hụt nhịp |
| C4-01 | 114 | the:chuong/4 | the/phang | Thẻ chương 4, đập ở "giờ". | "Pháo nổ, hào siết" · "13/3/1954 · 17 giờ 5 phút · Him Lam · Nguồn: Báo QĐND" | đập chương |
| C4-02 | 114:10 | karmen:43:07.6 | phim/ngang | Lựu pháo bắn trong rừng, khói đầu nòng. | "hàng chục khẩu pháo · Nguồn: Báo QĐND" | pháo nổ trong khoảng giữa câu |
| C4-02b | H1 | karmen:43:19.6 | phim/thap | Pháo ta khai hỏa (bóng pháo thủ ngược sáng, chớp đầu nòng), khói nổ trùm sườn đồi (phim Karmen, mô phỏng lại). | | tổ hợp H1 |
| C4-03 | 115 | map3d:shot-d-dot-1 | ban-do/cao | Him Lam chớp đỏ; các chấm trận địa quanh sườn núi chớp sáng. | | nổ xa |
| C4-04 | 116 | the:hook/3-phat | the/phang | "3 PHÁT" hiện lại, rung. | "Nguồn: TTXVN" | |
| C4-05 | 117 | 3d-moi:ham-phap | trung/ngang | Lửa cháy trên đồi Độc Lập trong đêm, nhìn chéo. | | pháo bắn |
| C4-06 | 118 | map3d:tran-dia-gia | ban-do/cao | Chấm trận địa thật và giả cùng chớp lửa. | | |
| C4-07 | 119 | 3d-moi:tran-dia | toan-xa/thap | Đạn nổ trên sườn đồi trống, không có pháo. | "phần lớn đạn pháo Pháp rơi vào trận địa nghi binh · Nguồn: TTXVN" | nổ đất |
| C4-08 | 120 | 3d-moi:tran-dia | dac-ta/ngang | Mái hầm gỗ đất của ta rung, đất rơi lả tả, khói. | | đất rơi |
| C4-09 | 121 | karmen:43:16.2 | phim/ngang | Bộ binh xung phong qua cỏ cao, khói đạn. | | |
| C4-10 | 121:14 | 3d-moi:him-lam | toan-xa/cao | Lô cốt Him Lam nhả lửa trong đêm từ xa; chớp tắt, máy nâng lên trời; không người. | "Anh hùng Phan Đình Giót · Tiểu đội phó, Đại đội 58 · 13/3/1954 · Nguồn: Báo QĐND" | súng máy dứt, lặng |
| C4-11 | 122 | map3d:shot-d-dot-1 | ban-do/tren-xuong | Him Lam đổi màu, mũi tên tới Độc Lập. | "Him Lam: 23 giờ 30 phút 13/3 · Nguồn: Báo Nhân Dân" | |
| C4-12 | 122:11 | 3d:BD3 | toan-xa/cao | Đồi Độc Lập đơn độc trong đêm, chớp nổ trên đỉnh. | "Độc Lập: 6 giờ 30 phút 15/3 · Nguồn: Báo QĐND" | nổ xa |
| C4-13 | 123 | map3d:shot-d-dot-1 | ban-do/cao | Bản Kéo nhấp sáng, phân khu Bắc mở. | "Bản Kéo: 17/3 · Đợt 1 · 13/3 – 17/3/1954 · Nguồn: Báo Chính phủ" | |
| C4-14 | 125 | the:van-kien/thua-so-phao | the/phang | Lời trích của Pi-rốt. | "Tôi có thừa số pháo cần thiết" · Trung tá Pi-rốt · Nguồn: Báo QĐND | |
| C4-15 | 126 | karmen:43:30.7 | phim/ngang | Đạn pháo nổ dồn trên cánh đồng, cột khói nối nhau (phim Karmen, mô phỏng lại). | "khoảng 6.000 viên pháo Pháp bắn quanh Him Lam · Nguồn: TTXVN" | pháo dồn |
| C4-16 | 127 | anh:chuyen-dan-vao-ham-phao-01 | anh/thap | Chuyển đạn vào hầm pháo, phóng chậm. | | |
| C4-17 | 128 | the:hook/3-phat-vo | the/phang | "3 PHÁT" vỡ ra thành mảnh. | "Nguồn: TTXVN" | vỡ khô |
| C4-18 | 129 | anh:luu-phao-105-bao-tang-ha-noi-01 | anh/chech | Lựu pháo 105 ở bảo tàng, đường máy khác C3-15 (bản 02 là tấm bảng chú thích, không dùng). | | |
| C4-19 | 130 | the:niem-tin/1-sai | the/phang | Thẻ niềm tin 1 bị gạch, đóng dấu "sai". | "niềm tin 1: sai · Nguồn: Báo Nhân Dân" | dấu đóng |
| C4-20 | 131 | map3d:trinh-sat | ban-do/cao | Vệt bay trinh sát quét trên lòng chảo, trận địa ta không hiện. | | máy bay xa |
| C4-21 | 132 | anh:cao-xa-37mm-bao-tang-ha-noi-01 | anh/thap | Pháo cao xạ 37 mm ở bảo tàng. | | |
| C4-22 | 132:16 | 3d:MB1 | dac-ta/ngang | Động cơ C-47, khói đạn cao xạ nổ quanh, lửa bùng. | "Trung đoàn 367 · 14 máy bay (hết đợt 1) · Nguồn: Báo Nhân Dân" | cao xạ, động cơ hụt |
| C4-23 | 133 | the:so-lieu/tang-vien | the/phang | Hai số. | "sau 13/3: tăng viện khoảng 4.000 quân · Nguồn: Báo Nhân Dân" / "lúc đông nhất: 16.200 quân · Nguồn: Báo QĐND" | |
| C4-24 | 134 | 3d-moi:san-bay | trung/thap | C-47 chạm đất giữa đường băng đầy hố đạn, khói quanh. | "27/3/1954 · lần cuối máy bay Pháp hạ cánh · Nguồn: Báo Nhân Dân" | động cơ hạ cánh |
| C4-25 | 135 | karmen:44:29.25 | phim/ngang | Xác máy bay tiêm kích của phía Pháp nằm trên sân bay Mường Thanh (góc khác MO15). | | |
| C4-26 | 135:13 | map3d:hai-san-bay | ban-do/tren-xuong | Đường băng Mường Thanh bị gạch chéo. | | |
| C4-27 | 136 | 3d-moi:bau-troi | dac-ta/thap | Đặc tả tán dù tiếp tế lơ lửng, dây căng. | | gió |
| C4-28 | 137 | the:dong-thoi-gian/3-dot | the/phang | Thanh ba đợt, đợt 2 sáng. | "Đợt 2 · 30/3 – cuối tháng 4/1954 · Nguồn: Báo Chính phủ" | |
| C4-28b | H2 | karmen:43:39.3 | phim/thap | Bộ đội tiến qua cỏ cao trong khói đạn (phim Karmen, mô phỏng lại). | | tổ hợp H2 |
| C4-29 | 138 | map3d:shot-e-dot-2-hao | ban-do/cao | Hào vây lấn vẽ dần quanh khu trung tâm. | "đánh các điểm cao phía Đông, vây lấn, khống chế sân bay · Nguồn: Báo Chính phủ" | |
| C4-30 | 139 | 3d:BD8 | toan/tren-xuong | Các nhánh hào ta bò dần tới đường băng; xác C-47 trên đường băng. | "③ Ta: siết hào, cắt đôi sân bay · Nguồn: TTXVN" | đất lạo xạo |
| C4-31 | 140 | map3d:shot-e-dot-2-hao | ban-do/chech | C1, E, D, A1 sáng đúng lúc đọc tên. | "C1 · E · D · A1 · Nguồn: Báo QĐND" | |
| C4-32 | 141 | karmen:43:44.6 | phim/thap | Bộ đội vượt hào, thép gai, tiến lên sườn đồi trong khói (phim Karmen, mô phỏng lại). | | nổ xa |
| C4-33 | 142 | anh:tan-cong-doi-c1-01 | anh/phang | Tiến công đồi C1, phóng chậm. | | |
| C4-34 | 143 | 3d-moi:bau-troi | toan-xa/thap | Đồi A1 lỗ chỗ hố đạn dưới ánh pháo sáng trong đêm. | "đầu tháng 4/1954 · 1 tiểu đoàn dù nhảy trong 3 đêm · Nguồn: TTXVN" | động cơ đêm |
| C4-35 | 144 | anh:giao-thong-hao-bo-doi-sinh-hoat-1954 | anh/phang | Bộ đội sinh hoạt trong giao thông hào. | | |
| C4-36 | 145 | 3d-moi:chien-hao | trung/cat-lop | Nhìn xuống các nhánh hào ta bò dần tới sân bay (kho chưa có mặt cắt hào có thước). | "hào sâu 1,7 m · đáy hào trục 1,2 m · Nguồn: TTXVN" | |
| C4-37 | 146 | map3d:mang-hao | ban-do/cao | Mạng hào lan khắp phân khu Trung tâm. | "mạng hào dài 'hàng trăm ki-lô-mét' · Nguồn: Báo QĐND" | |
| C4-38 | 147 | 3d:BD7 | dac-ta/thap | Nhánh hào ta cắt về phía đường băng, nhìn chéo từ trên. | | xẻng đất |
| C4-39 | 148 | 3d-moi:chien-hao | trung/thap | Nhánh hào ta trên đồng trống cạnh đường băng (kho chưa có mưa). | "đầu tháng 4/1954 · mưa nhiều ngày · Nguồn: Báo QĐND" | mưa |
| C4-40 | 149 | anh:giao-thong-hao-him-lam-ttltqg3-thumb | anh/phang | Ảnh nhỏ đặt trong khung giấy, phóng chậm. | | mưa nhỏ dần |
| C4-41 | 150 | map3d:mang-hao | ban-do/tren-xuong | Hào siết thêm, vùng tập đoàn cứ điểm thu hẹp. | | |
| C4-42 | 151 | 3d-moi:ham-phap | dac-ta/ngang | Cuộn thép gai đứt, khe phá mở. | | thép bật |
| C4-43 | 152 | 3d-moi:bau-troi | toan-xa/thap | Từ dưới lên: dù tiếp tế lơ lửng trên lòng chảo. | | gió, nhạc chuyển |
| C5-01 | 153 | the:chuong/5 | the/phang | Thẻ chương 5. | "Lấy đi bầu trời" | đập chương |
| C5-02 | 153:6 | 3d-moi:bau-troi | toan-xa/cao | C-47 thả dù từ trên cao, nhìn từ trên máy bay xuống (góc khác MO01–MO02). | "9/4/1954 · thả 195 tấn · Nguồn: Báo QĐND" | |
| C5-03 | 153:21 | the:hook/6-tan | the/phang | "6 TẤN" hiện lại. | "thu 6 tấn · Nguồn: Báo QĐND" | trống trầm |
| C5-04 | 154 | the:so-lieu/can-thu | the/phang | Hai cột: cần 200, thu 100. | "cần khoảng 200 tấn đạn dược/ngày · cao nhất thu khoảng 100 tấn · Nguồn: TTXVN" | |
| C5-05 | 156 | 3d-moi:bau-troi | toan-xa/cao | Dù dạt qua vòng hào, rơi về phía trận địa ta. | | gió |
| C5-06 | 157 | 3d-moi:tran-dia | trung/thap | Dãy ụ pháo nguỵ trang trên sườn đồi, nòng nâng (kho chưa có ụ cao xạ 37). | Thẻ tên "ông Trần Xuân Kình · chiến sĩ Trung đoàn cao xạ 367 · Nguồn: Báo Nhân Dân" | |
| C5-07 | 157:15 | 3d-moi:bau-troi | toan-xa/ngang | Khói đạn cao xạ nổ đen trên trời. | | cao xạ |
| C5-08 | 157:27 | the:van-kien/giu-yen-bau-troi | the/phang | Lời trích. | "giữ yên bầu trời" · ông Trần Xuân Kình, chiến sĩ Trung đoàn cao xạ 367 · Nguồn: Báo Nhân Dân | |
| C5-09 | 158 | 3d-moi:bau-troi | toan-xa/thap | C-47 giữa khói đạn cao xạ, động cơ bốc cháy. | | động cơ gầm |
| C5-10 | 158:14 | 3d-moi:bau-troi | toan/cao | Dù rơi ra ngoài vòng trận địa. | | |
| C5-11 | 159 | 3d-moi:chien-hao | toan/tren-xuong | Đầu hào tiến dần theo thời gian. | | xẻng đất |
| C5-12 | 160 | map3d:hao-cat-san-bay | ban-do/cao | Hai nhánh hào gặp nhau giữa đường băng. | "16/4/1954 · hào cắt đôi sân bay · Nguồn: TTXVN" | |
| C5-13 | 161 | 3d:BD9 | toan/thap | Bóng đồi A1 đen trên nền trời, chớp pháo xa sau đồi; không vẽ trăng. | "từ đêm 20/4/1954 · Nguồn: TTXVN" | dế, nổ rất xa |
| C5-14 | 162 | 3d:BD10 | trung/cat-lop | Mặt cắt đồi A1: đường hầm hẹp xiên vào lòng đồi. | "A1 · Đại đội công binh 83, Trung đoàn 151 · Nguồn: TTXVN" | đất cào |
| C5-15 | 163 | the:cau-hoi/dao-ham | the/phang | Câu hỏi trên nền tối. | "Làm sao đào sâu vào chân một cứ điểm mà đối phương không hay biết?" | |
| C5-16 | 164 | anh:tan-cong-doi-a1-01 | anh/phang | Ảnh đồi A1, phóng chậm. | Thẻ tên "Đại tá Nguyễn Bội Giong · phái viên Bộ Tổng tư lệnh trong chiến dịch · Nguồn: Báo QĐND" | |
| C5-16b | 164:22 | demo:BD10 | trung/cat-lop | Mặt cắt đồi A1: đường hầm hẹp xiên vào lòng đồi (3D Demo đã duyệt; tách khỏi ảnh C5-16 cho ảnh hạng A? không quá 5 s). | | đất cào khẽ |
| C5-17 | 165 | the:ba-viec/a1 | the/phang | Ba dòng đánh dấu lần lượt ở câu 165, 166, 167. | "không để lộ · đổ đất kín, giữ hướng · không để người đào ngạt · Đại tá Nguyễn Bội Giong · Nguồn: Báo QĐND" | bút đánh dấu |
| C5-18 | 168 | 3d-moi:a1-cat | dac-ta/ngang | Lòng hầm A1 hẹp, khối gói thuốc nổ cuối hầm (kho chưa có la bàn, đèn pin). | Chữ "như con đom đóm" · Nguồn: Báo QĐND | đất rơi khẽ |
| C5-19 | 169 | 3d-moi:a1-cat | trung/ngang | Mặt cắt đồi A1, đường hầm xiên vào lòng đồi, góc khác. | | quạt nan |
| C5-20 | 170 | 3d-moi:san-bay | toan/cao | Đường băng hố đạn, hào cắt ngang, xác C-47. | "28/4/1954 · sân bay hoàn toàn bị vô hiệu hóa · Nguồn: Báo Nhân Dân" | |
| C5-21 | 171 | map3d:shot-f-dot-3-a1 | ban-do/cao | A1 và C1 nhấp sáng, chưa đổi màu. | | |
| C5-22 | 172 | the:dong-thoi-gian/3-dot | the/phang | Thanh ba đợt, đợt 3 sáng. | "Đợt 3 · 1/5 – 7/5/1954 · Nguồn: Báo Nhân Dân" | |
| C5-23 | 173 | 3d-moi:bau-troi | trung/thap | Dù rơi xuống cạnh hào ta. | "giai đoạn cuối: khoảng 1/3 số dù rơi vào trận địa ta · Nguồn: Báo Nhân Dân, TTXVN" | dù chạm đất |
| C5-24 | 174 | map3d:hoa-tien | ban-do/cao | Vệt hỏa tiễn vạch trên phân khu Trung tâm trong đêm. | "hỏa tiễn H6 · đợt 3 · Nguồn: Báo QĐND" | rít |
| C5-24b | H3 | demo:BD9+6 | toan/thap | Bóng đồi A1 đen trên nền trời đêm, chớp pháo và hỏa tiễn nổ sau đồi (3D Demo đã duyệt). | | tổ hợp H3 |
| C5-25 | 175 | 3d:BD11 | dac-ta/ngang | Máy trượt dọc lòng hầm tới cuối: khối gói thuốc nổ sát vách. | "khoảng 15 ngày đêm · Nguồn: Báo Nhân Dân" | |
| C5-26 | 176 | the:lich/6-5-1954 | the/phang | Đồng hồ 20:30 trên nền tối. | "6/5/1954 · 20 giờ 30 phút · gần 1 tấn bộc phá · Nguồn: Báo QĐND" | tích tắc |
| C5-27 | 176:11 | 3d:BD12 | toan/cat-lop | Mặt cắt đồi: ánh đỏ bùng trong lòng đồi, đỉnh phồng lên (chậm bằng coGian). | | lửa bén |
| C5-28 | A1 | demo:BD13 | toan-xa/thap | Cột đất lửa bùng từ đỉnh A1, sóng chấn, máy giật. | | NỔ LỚN trong khoảng lặng A1 |
| C5-29 | 177 | 3d-moi:a1-dem | toan-xa/ngang | Cột khói sau nổ, bụi lắng trên đồi đêm. | "Anh hùng Nguyễn Văn Bạch · Tiểu đội trưởng, Đại đội công binh 83 · Nguồn: TTXVN" | đất rơi |
| C5-30 | 178 | karmen:43:36 | phim/thap | Bộ đội xung phong, cột nổ trắng trên đồi. | | súng, hô |
| C5-30b | H4 | karmen:43:10.35 | phim/ngang | Pháo ta khai hỏa ngược sáng rồi một lô cốt nổ tung, mảnh văng (phim Karmen, mô phỏng lại). | | tổ hợp H4 |
| C5-31 | 179 | 3d-moi:a1-dem | toan-xa/cao | Cột khói và lửa còn cháy trên đỉnh A1 sau tiếng nổ, máy lùi xa. | "rạng sáng 7/5/1954 · làm chủ đồi A1 · Nguồn: Báo QĐND" | gió sớm |
| C5-32 | 180 | map3d:shot-g-ket-ham | ban-do/cao | Mũi tên tổng công kích từ mọi hướng vào phân khu Trung tâm. | "7/5/1954 · tổng công kích · Nguồn: Báo Nhân Dân" | |
| C5-33 | 181 | map3d:ba-quyet-dinh | ban-do/tren-xuong | Ba mũi tên ①②③ hiện lại. | | |
| C5-34 | 182 | 3d-moi:tran-dia | dac-ta/ngang | Đặc tả nòng 105 của ta trong hầm (không phải loạt 13/3). | | |
| C5-35 | 183 | 3d:MB2 | toan-xa/thap | C-47 kéo vệt khói đổ xuống sau dãy núi, cắt trước lúc chạm đất. | | |
| C5-36 | 184 | the:niem-tin/2-hoi | the/phang | Thẻ 1 gạch "sai", thẻ 2 còn dấu hỏi. | "niềm tin 2 · ? · Nguồn: Báo Nhân Dân" | |
| C5-37 | 185 | karmen:41:07.2 | phim/cao | Con đường đất trên núi: dân công, xe, cờ đỏ (phim Karmen, mô phỏng lại). | | bước chân, nhạc chuyển |
| C6-01 | 186 | the:chuong/6 | the/phang | Thẻ chương 6. | "Hai loại con số" | đập chương |
| C6-02 | 186:6 | karmen:45:31 | phim/cao | Hàng binh trên cánh đồng. | | |
| C6-03 | 187 | the:hai-cot/trai | the/phang | Hai cột số, cột trái sáng. | | |
| C6-04 | 188 | anh:hang-binh-phap-01 | anh/phang | Hàng binh Pháp, phóng chậm. | "16.200 · tiêu diệt và bắt sống · Nguồn: Báo Chính phủ" | |
| C6-05 | 189 | anh:may-bay-bi-ban-ha-01 | anh/chech | Máy bay bị bắn hạ, phóng chậm. | "62 máy bay bị bắn rơi, phá hủy · Nguồn: Báo Chính phủ" | |
| C6-06 | 190 | the:hai-cot/phai | the/phang | Cột phải sáng, còn trống. | | |
| C6-07 | 191 | vnmap:tay-bac | ban-do/cao | Tây Bắc xa xôi, không chạm biển; hai khối nhỏ "2 sư đoàn" mờ. | "Bộ chỉ huy Pháp tin: ta không tập trung được quá 2 sư đoàn · Nguồn: Báo Nhân Dân" | |
| C6-08 | 192 | map3d:nam-dai-doan | ban-do/cao | Năm khối đại đoàn hiện quanh lòng chảo. | "5 đại đoàn · Nguồn: Báo Nhân Dân" | |
| C6-09 | 193 | the:so-lieu/40000 | the/phang | Số chạy 40.000. | "khoảng 40.000 quân chủ lực (khoảng 55.000 kể cả tuyến hai) · Nguồn: Báo Nhân Dân" | |
| C6-10 | 194 | 3d:T-F2 | toan/cao | Đoàn xe thồ uốn theo đường núi, mặt trời thấp. | | bánh xe, bước chân |
| C6-11 | 195 | 3d:T-F1 | dac-ta/ngang | Đặc tả nan hoa quay, bao gạo căng. | | nan xe đạp |
| C6-12 | 196 | anh:xe-tho-dan-cong-01 | anh/phang | Xe thồ dân công, phóng chậm. | "lúc đầu 80–100 kg/xe · Nguồn: Báo Nhân Dân" | |
| C6-13 | 197 | 3d-moi:hau-phuong | dac-ta/cao | Đặc tả đoạn tre buộc vào ghi-đông (tay ngai), tay lái nghiêng. | "tay ngai: đoạn tre khoảng 1 m buộc vào ghi-đông · Nguồn: Báo QĐND" | dây buộc |
| C6-14 | 198 | the:so-lieu/xe-tho | the/phang | Số chạy 80–100 → 200–300 kg. | "sau cải tiến 200–300 kg · Nguồn: Báo Nhân Dân" | |
| C6-15 | 199 | anh:xe-dap-tho-dan-cong-ttltqg3-a4 | anh/phang | Ảnh xe đạp thồ, phóng chậm. | "ông Ma Văn Thắng · dân công Phú Thọ · có chuyến hơn 3 tạ · Nguồn: Báo Nhân Dân" | |
| C6-16 | 200 | karmen:41:01 | phim/cao | Đoàn dân công cờ đỏ trên đèo. | "hơn 260.000 dân công hỏa tuyến · Nguồn: Báo Chính phủ" | |
| C6-17 | 200:14 | 3d:T-F3 | toan/thap | Xe nặng gạo lướt sát máy, bụi trong nắng. | "gần 21.000 xe đạp thồ · hơn 23.000 tấn gạo · Nguồn: Báo Chính phủ" | hành khúc dâng |
| C6-18 | 201 | the:hai-cot/du | the/phang | Cột phải điền đủ bộ ba số. | "Nguồn: Báo Chính phủ" | |
| C6-19 | 202 | map3d:hai-duong | ban-do/cao | Đường bay tiếp tế mờ dần, đường xe thồ trên núi sáng lên (câu 203). | | |
| C6-20 | 204 | 3d-moi:a1-dem | toan-xa/ngang | Đồi trơ trong sương sớm, tĩnh, không người. | "4.020 cán bộ, chiến sĩ hy sinh · 792 mất tích, 9.118 bị thương · Nguồn: VTV" | nhạc ~25 % |
| C6-21 | 205 | the:niem-tin/2-sai | the/phang | Hai thẻ niềm tin cùng gạch "sai". | "Nguồn: Báo Nhân Dân" | dấu đóng |
| KT-01 | 206 | map3d:shot-g-ket-ham | ban-do/tren-xuong | Máy hạ xuống hầm chỉ huy giữa phân khu Trung tâm. | "17 giờ 30 phút · 7/5/1954 · Nguồn: Báo Nhân Dân" | |
| KT-02 | 206:21 | anh:danh-chiem-cau-muong-thanh-01 | anh/phang | Đánh chiếm cầu Mường Thanh, phóng chậm. | "tổ xung kích Đại đội 360, Tiểu đoàn 130, Trung đoàn 209, Đại đoàn 312 · Đại đội trưởng Tạ Quốc Luật · Nguồn: Báo Nhân Dân" | |
| KT-03 | 207 | 3d-moi:ham-phap | trung/thap | Hầm vòm bao cát chỉ huy nhìn từ bên hông. | Chữ "Giơ tay lên!" đúng lúc đọc · lời kể của Anh hùng Tạ Quốc Luật · Nguồn: Báo Nhân Dân | |
| KT-04 | 208 | anh:de-castries-ra-hang-01 | anh/phang | Đờ Cát-xtơ-ri ra hàng, phóng chậm. | "Đờ Cát-xtơ-ri bị bắt cùng toàn bộ Bộ Tham mưu · Nguồn: TTXVN" | |
| KT-05 | 209 | 3d-moi:ham-phap | dac-ta/ngang | Đặc tả bao cát nóc hầm chỉ huy (kho chưa có điện thoại dã chiến). | | chuông điện thoại tắt |
| KT-06 | 209:10 | karmen:45:41 | phim/ngang | Hàng dài hàng binh. | | |
| KT-07 | 210 | anh:co-quyet-chien-quyet-thang-noc-ham-01 | anh/thap | Lá cờ trên nóc hầm, phóng chậm; không làm 3D lá cờ. | | nhạc dâng |
| KT-08 | 211 | the:lich/8-5-1954 | the/phang | Lịch 8/5/1954. | "8/5/1954 · thư khen của Chủ tịch Hồ Chí Minh · Nguồn: Báo QĐND" | |
| KT-09 | 211:15 | karmen:45:15 | phim/ngang | Dân bản chào đón bộ đội. | | |
| KT-10 | P3 | the:van-kien/thu-khen | the/phang | Lời Chủ tịch Hồ Chí Minh hiện chữ nguyên văn, không giọng đọc. | "Thắng lợi tuy lớn nhưng mới là bắt đầu. Chúng ta không nên vì thắng mà kiêu, không nên chủ quan khinh địch." · thư ngày 8/5/1954 của Chủ tịch Hồ Chí Minh · Nguồn: Báo QĐND | lặng, nhạc ~25 % |
| KT-11 | GN | anh:geneve-hiep-dinh-1954-ban-chup-luu-tru-phap | anh/phang | Văn bản Hiệp định Giơ-ne-vơ, phóng chậm. | "8/5/1954 · Hội nghị Giơ-ne-vơ bắt đầu bàn về Đông Dương · Nguồn: Báo Chính phủ" | nhạc trở lại |
| KT-12 | 212 | map3d:ba-quyet-dinh | ban-do/cao | Mũi tên ① hiện lại. | "① Bộ chỉ huy Pháp · Nguồn: Báo Nhân Dân" | |
| KT-13 | 213 | 3d-moi:keo-phao | toan-xa/thap | Hàng người kéo pháo lên đỉnh dốc dưới trời sao (góc mới). | "② Ta · Nguồn: Báo QĐND" | |
| KT-14 | 214 | map3d:hao-cat-san-bay | ban-do/tren-xuong | Hào siết, đường băng cắt đôi. | "③ Ta · Nguồn: Báo Chính phủ, TTXVN" | |
| KT-15 | 215 | karmen:45:05 | phim/cao | Bộ đội cầm cờ Quyết chiến Quyết thắng trên xe tăng thu được. | | hành khúc |
| KT-16 | 215:11 | vnmap:toan-quoc | ban-do/cao | Việt Nam toàn khung với Hoàng Sa, Trường Sa, "Biển Đông"; máy lùi rất chậm. | | hành khúc |
| KT-17 | 216 | the:hook/3-phat-mo | the/phang | "3 PHÁT" hiện lần cuối rồi mờ. | "Nguồn: TTXVN" | |
| KT-18 | 217 | map3d:shot-c-keo-phao | ban-do/cao | Đường kéo pháo 15 km sáng dần từ Nà Nhạn qua Pu Pha Sông. | "15 km · Nguồn: Báo QĐND" | |
| KT-19 | 218 | 3d-moi:keo-phao | toan/thap | Dừng ở khẩu pháo trên dốc, giữ lâu. | | dây căng, rồi lặng |
| KT-20 | 219 | anh:ham-de-castries-2022 | anh/phang | Hầm Đờ Cát-xtơ-ri hôm nay. | "hầm chỉ huy: dài 20 m · rộng 8 m · giữ nguyên cấu trúc · Nguồn: Báo Nhân Dân" | gió |
| KT-21 | 220 | 3d-moi:a1-hom-nay | toan-xa/cao | Đồi trong sương nhìn từ cao, không người. | | chim, gió |
| KT-22 | 221 | can-tim:nghia-trang-a1 | anh/phang | Ảnh Nghĩa trang liệt sĩ quốc gia A1 có giấy phép (Commons); chưa có thì thẻ số trên nền tối. | "Nghĩa trang liệt sĩ quốc gia A1 · 645 mộ · Nguồn: Báo Văn hóa, TTXVN" | |
| KT-23 | 222 | the:so-lieu/645 | the/phang | Ba số: 645 / 10 / 39. | "645 mộ · 10 mộ đủ thông tin · 39 mộ có một phần thông tin · báo cáo 8/2026 · Nguồn: Báo Văn hóa, TTXVN" | |
| KT-24 | 223 | can-tim:hang-mo-a1 | anh/thap | Hàng mộ, không chữ chồng lên; chưa có ảnh thì chữ "596" trắng nhỏ trên nền đen. | "596 mộ chưa có thông tin · Nguồn: Báo Văn hóa, TTXVN" | nhạc tắt dần |
| KT-25 | KT | the:cau-hoi/binh-luan | the/phang | Thẻ câu hỏi bình luận cuối phim. | "Theo bạn, quyết định nào trong ba quyết định ấy là quan trọng nhất?" | lặng |
<!-- /BANG -->

## Tóm tắt
<!-- TOM -->
- **258 cảnh, 1061 s (17:41), 14.6 cảnh/phút** (mốc chữ thật).
- Theo kiểu: karmen 29, demo 8, the 64, anh 30, map3d 43, vnmap 8, 3d-moi 53, 3d 21, can-tim 2.
- Tư liệu thật (ảnh + phim): 59 cảnh, 194 s; hạng B/A? dài nhất 4.9 s.

| Chương | Cảnh | Giây | Cảnh/phút | Đặc tả |
|---|---|---|---|---|
| Mở | 31 | 117 | 15.9 | 1 |
| Ch1 Lòng chảo | 25 | 128 | 11.7 | 1 |
| Ch2 Con nhím | 28 | 119 | 14.1 | 4 |
| Ch3 Đổi cách đánh | 43 | 177 | 14.6 | 4 |
| Ch4 Pháo nổ, hào siết | 45 | 158 | 17.1 | 5 |
| Ch5 Lấy đi bầu trời | 40 | 159 | 15.1 | 3 |
| Ch6 Hai loại con số | 21 | 92 | 13.8 | 2 |
| Kết | 25 | 112 | 13.4 | 1 |
<!-- /TOM -->
