# Kiểm P1 · EP002 黄海海戦 1904

Tập chưa có kịch bản khung, nên «dòng [SỔ]» lấy từ mục «Dữ kiện cần tra trước» của `brief.md`.

## Kiểm sổ (2026-11-13)
- Lệnh: `python -I tools/lichsu/kiem-so.py tap/EP002-kokai-kaisen-1904/ke-hoach/so-so-lieu.csv "E:/Goha-JP/output/261113-kokai-kaisen-1904/nguon-tho"`
- Kết quả: 47 dòng, **Tổng dòng lỗi: 0** (A7b là MỘT NGUỒN, đã để KHÔNG DÙNG).
- Mức dùng: DÙNG 31 · NÓI TRÒN 6 · ĐỐI CHIẾU 2 · KHÔNG DÙNG 8.

## Bảng phủ brief → mã dòng
| Dữ kiện trong brief | Mã dòng | Phủ |
|---|---|---|
| Mốc giờ: xuất cảng | B1, B1b | có (nói tròn «早朝») |
| Mốc giờ: giao chiến lần 1 | B2, B2b, B3, B3b | có |
| Mốc giờ: giao chiến lần 2 | B5 | có |
| Mốc giờ: phát pháo trúng cầu chỉ huy | B6a, B6b | có (nói tròn «午後6時40分ごろ») |
| Mốc giờ: mặt trời lặn | B8a | có (MỘT NGUỒN, ghi rõ) |
| Thành phần hai hạm đội | A5a, A5b, A5c, A6a, A6b, A6c, A7a | có |
| Tốc độ, cự ly | B2, B4, B5 | có (số nước ngoài, ĐỐI CHIẾU) |
| Ai chết vì phát pháo, vì sao tan đội hình | B6a, B6b, B7 | có |
| Số phận từng tàu Nga sau trận | C1, C2, C3, C4, C5, C5b | có |
| Thiệt hại 三笠, thương vong hai bên | B9a, B9b, C6a, C6b | có (tổng thương vong KHÔNG DÙNG) |
| Quân hàm 東郷 | A4 | có (大将, thăng 6/6/1904) |
| Quân hàm ヴィトゲフト | A3a, A3b | có (少将, 司令長官代理) |
| Mối nối 蔚山沖, 日本海海戦 | C9, C9b, C9c | có (C9b chỉ ĐỐI CHIẾU, nói «といわれる») |
| Thêm: lệnh phá vây | A2 | có |
| Thêm: bối cảnh vây 旅順 | A8, A9 | có |
| Thêm: số phận hạm đội ở 旅順 sau đó | C7, C7b, C8, C8b | có |

Phủ 100 % các dữ kiện trong brief.

## Việc còn treo trước P2
- Nguồn gần như toàn Wikipedia JA/EN (được tính chính thống theo `luat-noi-dung.md` mục 7). Chưa có JACAR, 『明治三十七八年海戦史』, Corbett bản chữ. Luận điểm C9b (bài học sang 日本海海戦) và A9 (東郷 thận trọng vì hạm đội Baltic) đang nói dạng «とされる / といわれる».
- B7: quân hàm của ウフトムスキー chưa có dòng sổ riêng; kiểm trước khi viết lời.
- Cách viết tên đã chốt tạm: ヴィトゲフト, ディアナ. Khi người dùng duyệt thì ghi vào `kenh/cach-noi-da-chot.tsv`.
- Bản đồ đoạn tàu ディアナ chạy tới サイゴン: áp luật cứng của kit (Hoàng Sa, Trường Sa thuộc Việt Nam, ghi «Biển Đông», cấm đường lưỡi bò).

## P2 (2026-11-13, 06:58–07:50)

Quy trình: brief người viết (`brief-viet-p2.md`, khối luật C so máy = True) → Sonnet viết v1 (4 phương án mở) → Claude rà sổ + phản biện kép vòng 1 (Agy `gemini-4-argon-high --sandbox` + Opus ngữ cảnh mới, thư mục cách ly) → biên tập v2 (D1–D24) → phản biện kép vòng 2 → biên tập v3 (E1–E27, script `sua-v3.py` có assert cho cả kịch bản và lời đọc).

### Cổng máy trên bản trình duyệt v3
| Cổng | Kết quả |
|---|---|
| `rieng/tools/quet-ja.py kich-ban-v3.md loi-doc-v3.txt` | 0 CHẶN, 1 CẢNH BÁO (chữ «đường lưỡi bò» trong dòng `Hình:` là câu CẤM của luật kit, giữ) |
| `tools/loc-chinh-sach/quet.py` (từ điển Việt/Anh) | 0 CHẶN (không có giá trị với tiếng Nhật, xem ghi đè) |
| `trung-lap.py` so với 23 phụ đề đối thủ cùng đề tài + 35 phụ đề Shu + lời đọc EP001 v3 + tập mẫu | v1 0,00 % · v2 0,00 % · v3 0,00 % (0/828), 0 câu ≥ 10 tiếng. Kiểm tra cổng còn sống: so v1 với chính nó → KHÔNG ĐẠT |
| `kiem-da-chot.py` | 0 chỗ phạm (sổ cách nói đang 0 luật) |
| Mã sổ trong kịch bản | 40 mã, tất cả tồn tại, 0 mã KHÔNG DÙNG |
| `kiem-so.py` toàn sổ (48 dòng, thêm B7b) | 0 lỗi |
| Số ký tự lời đọc | v1 7.961 · v2 7.734 · v3 **7.123** (≈ 21:47 ở 327 ký tự/phút đo ở EP001) |
| Câu hỏi trung tâm | 18 s (1,4 %) |
| Cao trào (phát pháo 午後6時40分ごろ) | 12:54 (59,2 %) |

### Hook (7 tiêu chí /35)
- v1 (M3): Opus 26, Gemini 25 → viết lại.
- v2: Opus 27, Gemini 32 → dùng bản viết lại của Opus (dự kiến 34) ở v3.

### Phản biện: nhận và bác
Nhận (đã sửa): logic «逃げ切り = tới 日没» sai vì hạm đội Nga vẫn tới hoàng hôn → định nghĩa lại là giữ đội hình và hướng đi; «前を通り過ぎ» trái B3 (後尾); chi tiết vượt cach_noi (A8 Tsesarevich 艦橋, A3b 後任, A6a 梨羽, B3 hướng rẽ, B9b 午後6時前, C7b 修復, C2 抑留 tới hết chiến tranh); B4 Poltava dựng thành đoạn khẳng định → gộp một câu ĐỐI CHIẾU; nhắc lại hai số cự ly nước ngoài và suy «半分以下»; 「あと7時間半」 suy từ gia_tri 12:30 trong khi lời nói 正午すぎ; 結 tự mâu thuẫn; văn phong lẫn 常体; câu định nghĩa sơ đẳng; câu bù độ dài lặp; 上村 gọi trống → 第2艦隊; thứ tự 蔚山 (14/8) trước ノヴィーク (20/8); nhãn Hoàng Sa, Trường Sa (Việt Nam), Biển Đông trên bản đồ サイゴン; bỏ bản đồ Viễn Đông cổ ở hook.
Bác:
- Opus, Gemini: ảnh `ndl-yalu-1904-fleet-gun.jpg` «có thể là trận Áp Lục 1894». Claude mở ảnh: thiết giáp hạm thời 1904, cùng người chụp 芦野海軍教授 với ảnh 8/10, nhan đề NDL ghi «10TH AUGUST 1904». Giữ.
- Gemini: 「1時間20分ほど」 là độ chính xác giả. 18:37–18:40 → 20:02 = 1:22–1:25, nói «ほど» là đúng; giữ ở hook và 第5章, bỏ hai chỗ lặp.

### Sổ đã chỉnh trong P2
- Thêm B7b (ウフトムスキー 次席指揮官 少将, JA + EN, kiem-so ĐẠT).
- cach_noi C7 thêm «二度砲撃戦の機会…薄暮に至り見失った» (có trong trích nguồn 2); B4 gộp tốc độ + ポルタヴァ thành một câu ĐỐI CHIẾU; B6a gia_tri sửa khớp cach_noi (午後6時40分ごろ).

### Còn mở cho người dùng
- Độ dài 21:47 thấp hơn mục tiêu brief 24–27 phút (vẫn trong 20–30 phút của hồ sơ kênh).
- B8a (日没 午後8時ごろ) vẫn MỘT NGUỒN.

## P3 (2026-11-13, 14:04–14:12)

- Máy: `san-xuat/lap-phan-canh.py` (sinh bảng từ thẻ ý đồ theo câu + bể hình theo chương, chép cách làm EP001 JP) và `san-xuat/kiem-phan-canh.py` (chép từ EP001 JP, sửa: lời `loi-doc-v3.txt`, 327 ký tự/phút, 9 chương, 9 mã bản đồ code, luật bản đồ Việt Nam bật cho bản đồ tới サイゴン, nhãn «AI生成» bắt buộc lại theo `luat-noi-dung.md` mục 5, chú thích ngày chụp của ảnh được miễn «Nguồn:»).
- Kết quả: **ĐẠT** — 297 cảnh, 21:48 (ước tính, chưa có giọng), 13,6 cảnh/phút; mọi chương ≥ 12 cảnh/phút và có cận đặc tả; mở 21 cảnh/phút.
- Kiểu: ảnh 97 · clip AI 45 · bản đồ code 111 · thẻ 44. Ảnh/clip khác nhau **84** (ảnh 66, clip 18) — trên chuẩn Peleliu 61. Mỗi ảnh/clip ≤ 3 lần, cách ≥ 60 s; không quá 4 cảnh liền không hình thật; A? dài nhất 4,4 s.
- Thử đột biến 7/7 bắt: bản đồ サイゴン thiếu Hoàng Sa; ảnh cấm (bản đồ Viễn Đông cổ); thẻ số không nguồn; clip thiếu nhãn AI生成; 5 cảnh liền không hình thật; ảnh dùng 5 lần; ảnh A? 14,7 s.
- Không dùng (CAM): 2 bản đồ Viễn Đông cổ của EP001 (có thể chứa Biển Đông sai luật), ảnh NDL «đuổi tàu buôn», ảnh người sống sót リューリク (chưa soi thương tích), 初瀬, ảnh 東郷 A? của EP001 (trùng vai).
- Sửa lời trước P3: câu 300 「旅順艦隊を失ったあと、日本が…」 → 「旅順艦隊が力を失ったあと、連合艦隊が…」 (lỗi Opus đã chỉ ở vòng 1, sót ở v3), sửa cả kịch bản và lời đọc bằng assert.

### Rủi ro, việc cho P4–P5
- Mốc là ước tính 327 ký tự/phút; sau P4 ghi `moc-cau.json` rồi chạy lại `lap-phan-canh.py` + máy kiểm (như EP001 v2).
- 18 clip AI dùng lại từ EP001 (cảnh chung: biển, khói, đèn pha, hạm đội nhìn xa). Hai tập cùng kênh dùng lại clip → rủi ro «nội dung lặp» thấp nhưng có; P5 có thể thay bằng clip mới (tốn credit Flow, hỏi trước).
- Bản đồ code chiếm 37 % số cảnh; 9 mã cần dựng ở P5 (`tai-san-can-dung.md`), trong đó `churitsu` phải theo luật cứng Hoàng Sa, Trường Sa, Biển Đông.
- Ảnh A? (`VIT`, `TOGOP`, `NOVS`) vẫn chờ đối chiếu bản gốc; chưa rõ thì P5 thay bằng thẻ chữ.
- Nhãn trên clip: đã chốt «イラスト» nhỏ (xem dòng quyết định bên dưới).
- **Quyết định nhãn AI (13/11 chiều):** chủ kênh chọn «bỏ nhãn như EP001». `CLAUDE.md` của kit (mục luật cứng, «không tự nới», `rieng/ghi-de.md` không nới được) bắt hình minh hoạ của kênh ngách khác phải «ghi chữ minh hoạ trên hình». Nên EP002 bỏ chữ «AI生成» nhưng giữ một nhãn nhỏ «イラスト» góc dưới trái trên 45 cảnh clip; máy kiểm chấp nhận «イラスト» hoặc «AI生成». Vẫn khai «altered or synthetic content» ở YouTube Studio khi đăng. EP001 bản final đã bỏ hết nhãn: cần chủ kênh xem lại trước khi tải lên.

## P4 Giọng (2026-11-13, 15:01–16:00)

- Giọng: ElevenLabs `eleven_v4`, voice `tu1x0Bmib6kmsrXy16CZ`, `ja`, không thẻ đầu bài; 2 lượt (câu 1–164: 4.170 ký tự, câu 165–303: 3.559 ký tự) rồi nối. Tệp ở `E:/Goha-JP/output/261113-kokai-kaisen-1904/giong/`: bản cuối `giong-v2.wav` (+ `.mp3` 96k để chép lời), các bản cũ `giong-v1.wav`, `giong-v2a/v2b.wav` giữ để lùi.
- **Lỗi lặp lại của eleven_v4 (như EP001): giọng nuốt cả đoạn giữa lượt.** Mốc của kit sụp về 0 ở ~20 câu cuối mỗi lượt; so lời với STT Deepgram: 0,895, thiếu hẳn **câu 82–104 (458 ký tự)** và **câu 254–269 (324 ký tự)**; đầu câu 82 chỉ còn «日本の強み», đầu câu 105 chỉ còn «あ» (mất «旅順艦隊は»).
- Vá bằng đọc lại có ngữ cảnh (`--prev/--next`): khối 82–104 (518 ký tự), 254–269 (462), 105 (25), và 151–152 (60, vì chép lời toàn bài lần đó bỏ sót, xem dưới). Cắt chỗ hỏng ở chỗ lặng nhất của khe, đệm 0,35 s, chèn khối đọc lại: `san-xuat/ghep-giong-v2.py`, `ghep-giong-v3.py`, `ghep-giong-v4.py`. Mỗi khối đọc lại tự chép lời kiểm: khoi-1 0,977 · khoi-2 0,941 (toàn đồng âm: 租借→咀嚼, 青島→沈, 蔚山→うざん) · khoi-3 0,972 · khoi-4 đủ chữ.
- **STT Deepgram thỉnh thoảng bỏ từ dù âm thanh đủ:** câu 151 «追う側には、ためらう理由があったとされます» lúc có lúc mất giữa các lần chép toàn bài; chép riêng đoạn 17 s quanh nó thì đủ. Vì vậy chỗ «thiếu» chỉ được coi là thật khi cửa sổ cắt âm thanh quanh đó ngắn bất thường (khối 1: 2,4 s, khối 2: 0,3 s) hoặc chép riêng đoạn vẫn thiếu.
- Bản cuối: **23:07 (1.387,15 s)**, −18,0 LUFS, LRA 2,8, đỉnh mẫu −1,5 dBFS. Độ to từng câu: lệch chuẩn 0,75 dB; câu 105 (đọc lại) to hơn trung vị 1,7 dB, câu 47, 71, 199, 223 nhỏ hơn 2,6–4,0 dB (câu rất ngắn). Chưa chỉnh.
- So lời `so-loi-ja.py` trên bản cuối: **0,966** (ngưỡng 0,97, EP001 v2 đạt 0,970): 133 chỗ lệch, gần hết là đồng âm hoặc cách viết (東郷→統合, 隊形→体型, 針路→進路, 蔚山→うざん, ゔぃ→び, あと→後), không còn đoạn thiếu ≥ 12 ký tự. **Chưa ai nghe**; dưới ngưỡng 0,97 nên cần nghe tai.
- `moc-cau.json` dựng bằng `rieng/tools/moc-cau-ja.py` trên STT bản cuối: 303 câu, 96,2 % ký tự khớp giờ thật, không mốc lùi. Câu 151 không có mốc khớp (STT bỏ), nội suy giữa câu 150 và 152.
- P3 chạy lại trên mốc thật: **315 cảnh, 23:07, 13,6 cảnh/phút, 84 ảnh/clip khác nhau, máy kiểm ĐẠT** (bản ước tính cũ ở `ke-hoach/nhap/phan-canh-uoc-tinh.md`).
- Chi phí: ElevenLabs ≈ 8.200–8.800 credit (đọc chính 7.127 ký tự + dòng trống; đọc lại 1.065 ký tự). Deepgram: 4 lần chép toàn bài (v1, v2a, v2c, v2d) + 6 đoạn nhỏ ≈ 0,43 USD (vượt 0,11 USD ước: tôi chép lại sau mỗi lần vá để chứng minh). Số dư thật chưa kiểm.

### Việc người dùng phải làm
Nghe `giong-v2.wav` (bản cuối, 23:07): các tên ツェサレーヴィチ, レトヴィザン, ペレスヴェート, ヴィトゲフト, ウフトムスキー, 蔚山沖, 膠州湾, 出羽重遠; năm tháng viết chữ Hán (千九百四年…); các mối ghép theo mốc chữ: khối 1 từ 6:16 (câu 82) tới 8:12 (câu 106), câu 151–152 quanh 11:35–11:47, khối 2 từ 18:44 (câu 254) tới 20:22 (câu 270).

## P5 Lô 0 (2026-11-13, 15:30–15:45): trailer 10 s + 開幕 S001–S024

- Máy dựng: chép từ EP001 JP rồi chỉnh (`san-xuat/dung-p5.py`, `dung-3d.py`, `ban-do-3d/ban-do-3d.html`, `dung-the-dong.py` + `the-dong/`, `intro.py`, `trailer-am.py`, `lo0-xem.py`). Mới viết cho EP002: 10 cú máy bản đồ 3D (koukai, ryojun, ryojun12, kosen1, tsuigeki, kosen2, senkai, sanran, churitsu, ulsan; trục bắc lên, đồng hồ + thanh mặt trời tới 日没 ở các cảnh trong ngày, đất Natural Earth `world-land.json`, tàu Meshy dùng lại), 44 thẻ số động (`CARDS` trong `dung-the-dong.py`), cửa sổ k của cảnh bản đồ chạy tuần tự theo thời gian phim.
- Lô 0: 24/24 cảnh đúng số khung (1.506 khung = 62,75 s); trailer 10 s (240 khung) + âm tổng hợp `trailer-am.wav`; bản xem `preview/lo0-xem-v1.mp4` (72,8 s, giọng v2 + nhạc `suno-ch3-1` của EP001 hạ khi có giọng, −15,4 LUFS; CHƯA có tiếng động).
- Bản đồ `churitsu` (luật cứng): soi bằng mắt, có «Hoàng Sa (Việt Nam)», «Trường Sa (Việt Nam)», «Biển Đông», không đường lưỡi bò, không nhãn 南シナ海.
- **SOÁT SAO TRÊN CLIP AI (khung phóng to, 17 clip × 3 khung):** `V07b` có SAO TRẮNG trên thân tàu (ở EP001 vẫn dùng làm `V07B`), `V08` gốc có sao (EP001 đã thay bằng `V08b`, sạch), `V13` có sao (EP001 đã loại). EP002: bỏ V07B và V13, `V08` trỏ tới `V08b.mp4`; 15 clip còn lại không thấy sao (soi ở độ phân giải 960 px, sao nhỏ có thể sót). Bảng phân cảnh dựng lại: 315 cảnh, 82 ảnh/clip khác nhau (66 ảnh + 16 clip), máy kiểm ĐẠT.
- **EP001 (đã ra bản final) còn dùng V07b ở 3 cảnh: S145, S165, S209 (khoảng 1:54, 2:15, 2:55 trên phim, chưa tính trailer)** → có sao trắng trên thân tàu. Cần thay trước khi đăng.
- Quyết định Meshy (chủ kênh giao tự đánh giá, 13/11): dùng lại 4 mô hình tàu Meshy của EP001 (thiết giáp, tuần dương, phóng lôi, chuyên dụng), không tạo thêm. Lý do: bản đồ 概略 chỉ cần hình bóng theo loại tàu và đã đọc được ở khung hình; chỗ yếu là bờ biển (dữ liệu Natural Earth làm tròn 0,1°), Meshy không sửa được phần đó. Sẽ tạo thêm (≈ 5 credit mỗi mô hình) chỉ khi xem cả phim thấy cần, ví dụ pháo 28cm cho cảnh tháng 12.
- Còn treo: ảnh hạng A? (ヴィトゲフト, 東郷 1904, ノヴィーク) chưa đối chiếu bản gốc; 20 ảnh sau Lô 0 chưa dựng; mua nhạc/SFX/clip Flow chờ bạn gật Lô 0.
