# Kiểm tra tập 1 · Điện Biên Phủ 1954

## P1 Nghiên cứu (01/11/2026)

Sổ: `so-so-lieu.csv`, 71 dòng = 19 dòng sổ mẫu (mã M) + 23 dòng phía Pháp (mã A) + 29 dòng phía ta (mã B). Hai dòng sổ mẫu M13, M21 (đồi A1, nguồn cổng Sở VHTTDL Điện Biên lỗi chứng chỉ SSL) đã thay bằng B8a1–B8b2 với nguồn mới.
Cột `muc_dung` (DÙNG / TÙY / ĐỐI CHIẾU / KHÔNG DÙNG) và `cach_noi` do Claude chốt; người viết P2 phải theo.

Đối chiếu nguyên văn: `python -I tools/lichsu/kiem-so.py tap/EP001-dien-bien-phu-1954/ke-hoach/so-so-lieu.csv <output>/261101-dien-bien-phu-1954/nguon-tho` → **0 dòng lỗi**; 68 dòng đủ hai nguồn, 3 dòng một nguồn (A8a kích thước lòng chảo, B8a3 kiểm số 960 kg, B9a số tù binh), cả ba có cách nói thận trọng.

### Độ phủ [SỔ] của kịch bản khung
| Chỗ [SỔ] trong khung | Dòng sổ |
|---|---|
| Mở: giờ nổ súng, số khẩu pháo vào Him Lam | M12, B2f ("hàng chục khẩu", không nói 40) |
| Mở: 49 cứ điểm, 16.200 quân; 7/5 sụp đổ | M6, M7, M15 |
| Ch.1: nhảy dù 20/11/1953; mục tiêu kế hoạch Navarre | A2a, A2b, A1a–A1e |
| Ch.2: số cứ điểm, quân, sân bay, pháo, xe tăng | M6, M7, A4a, A4b, A4c, A4d |
| Ch.3: ngày đổi cách đánh | M5, M10, M11 |
| Ch.4: mốc ba đợt; chiều dài giao thông hào | M2–M4, B3a–B3c; B4a (không nêu số, nói "hàng trăm ki-lô-mét") |
| Ch.5: khối bộc phá; giờ chiếm A1 | B8a1, B8a2, B5a–B5c, B6, B7a |
| Ch.6: số chính thống; số Pháp ghi đối chiếu | M16, B7b, B9a, M9; A7a (ĐỐI CHIẾU) |
| Kết: 17 giờ 30 phút 7/5, cờ trên nóc hầm; Giơ-ne-vơ 21/7 | M15, B9b, M19 |

Phủ 100 % chỗ [SỔ]. Niềm tin của Pháp (luận điểm trung tâm): A5, A6a, A6b.

### Quyết định nội dung đã chốt ở P1
- Lời Chủ tịch Hồ Chí Minh, Đại tướng Võ Nguyên Giáp: chỉ hiện chữ nguyên văn trên hình kèm nguồn; giọng dẫn AI không đọc nguyên văn (luật cứng cấm AI "đọc lại" với lãnh tụ).
- Không nhắc cái chết của Piroth (A6c); không nói 960 kg (chỉ có trong chú thích ảnh), nói "gần một tấn"; không nêu số sơn pháo 75 mm, tổng chiều dài hào, số sĩ quan bị bắt; "hàng chục khẩu pháo" thay cho "40 khẩu".
- Bế Văn Đàn (M14) không đưa vào vì hy sinh trước chiến dịch.

## P2 Kịch bản (01/11/2026)

Bản trình duyệt: **`kich-ban-v3.md`**, lời đọc **`loi-doc-v3.txt`** (2.582 tiếng, ≈ 15,2 phút đọc, ≈ 16 phút cả khoảng lặng). v1 do sub-agent Sonnet viết theo `brief-viet-p2.md` (khối luật mục C chép nguyên văn, máy xác nhận). v2, v3 do Claude sửa sau cổng máy và phản biện.

### Cổng máy
| Cổng | v1 | v3 |
|---|---|---|
| `quet.py` (bộ lọc chính sách) | 0 CHẶN, 0 CẢNH BÁO | 0 CHẶN, 0 CẢNH BÁO |
| `trung-lap.py` cụm 6 tiếng (16 phụ đề ĐBP + 9 CLD + bản mẫu Goha) | **1,73 %, 2 câu ≥ 10 tiếng: KHÔNG ĐẠT** | **0,18 %, 0 câu: ĐẠT** (3 cụm còn lại là công thức kết quả "bắn rơi hoặc phá hủy") |
| Mã sổ | 61 mã | 61 mã, 0 mã lạ, 0 mã KHÔNG DÙNG |
| Lời lãnh tụ trong lời đọc | 0 | 0 (chỉ ở chữ trên hình) |

Danh sách cụm chính thống thêm 5 dòng (câu trích có ngoặc trong nguồn, chức danh, người nhận thư khen). Đo minh bạch: v3 với danh sách cũ vẫn ĐẠT (0,61 %, 0 câu), tức phần viết lại tự qua cổng.

### Claude sửa v1 → v2 (rà sổ + chống trùng)
Viết lại câu trùng cách kể ("dây tời đứt, khẩu pháo nặng hơn hai tấn bắt đầu trôi xuống dốc" gần như chép câu trích báo; "lấy thân mình lấp lỗ châu mai"; "khối bộc phá gần một tấn nổ trên đồi"; "địch đã tăng cường lực lượng"; câu thư khen; câu chức danh). Bỏ câu ngoài sổ ("nhiều đơn vị chưa kịp hoàn lại sức"), sửa "không hề có tên Điện Biên Phủ" thành "lúc đầu nằm ngoài kế hoạch" [A3a], sửa câu pháo đi qua đường kéo pháo. Rút phần mở để lời hứa vào giây 46.

### Phản biện Agy (`agy-phan-bien-v2.md`, gemini-4-argon-high, thư mục cách ly) → v3
Nhận và sửa: thẻ "8/5 Hội nghị Giơ-ne-vơ khai mạc" sai (8/5 là ngày bắt đầu bàn Đông Dương) [M19]; trục thời gian chương 5 đảo qua lại, đã xếp 27/3 → 16/4 → 20/4 → 28/4 → 1/5 → 6/5 → 7/5; 200–300 tấn là của hai sân bay [A4a]; "một đường băng" mâu thuẫn; bỏ giờ "8 giờ" lệch nguồn [B7a]; 52 máy bay ghi "tính cả chiến dịch" [B7b]; bỏ danh sách tổ xung kích thiếu người [M15]; "Giơ tay lên!" ghi rõ là lời trích hồi ký Tạ Quốc Luật (đã soi chữ thô Báo Nhân Dân); bỏ câu Navarre trùng nghĩa [A4c]; gộp đoạn Tô Vĩnh Diện còn 2 câu; bản đồ ghi "Biển Đông"; ảnh Castor có De Castries chuyển khỏi ngày 20/11; nhãn Karmen "tắt tiếng gốc, có cảnh dựng lại"; "Bộ chỉ huy Pháp" ở các câu niềm tin; câu treo cuối chương 5; đổi tên chương 4.
Bác bỏ (có bằng chứng): "lời đọc chỉ 1.400 tiếng, hụt nửa thời lượng" — Agy đếm trên kịch bản ghi số bằng chữ số; `loi-doc-v3.txt` đo được 2.582 tiếng. "Thay mọi chữ 'Pháp' trống không" — sử chính thống vẫn dùng "Pháp", "quân Pháp" khi kể tác chiến; đã nêu rõ "quân viễn chinh", "Bộ chỉ huy Pháp" ở các câu then chốt. "Tách số tù binh khỏi phim" — B9a do Claude chốt DÙNG, nay nói "theo Báo Chính phủ".

### Còn để user quyết ở cổng duyệt
- Cao trào: chương 4 (trận mở màn, lời hứa của Pi-rốt thất bại) bắt đầu ở 54 %, chương 5 ở 68 %, A1 ở 79 %. Khung cũ đặt cao trào ở chương 5; Claude giữ như vậy vì trận Him Lam là đỉnh hành động, chương 5 là đỉnh luận điểm.

## P2b–P2c Hook, học Shu, viết lại theo khuôn (01/11/2026, sau khi user duyệt v3 lúc 16:06)

User dặn: phản biện thật kỹ, hook hấp dẫn, chất lượng như phim QPVN; bước 1 là Shu (học video triệu view và Model Link). Bản chốt: **`kich-ban-v5.md`, `loi-doc-v5.txt`** (3.555 tiếng, khoảng 15 phút ở giọng thật 242 tiếng/phút).

### Phát hiện làm đổi độ dài
Giọng chốt Tung Dang đo trên bản mẫu: 242 tiếng/phút (444 tiếng / 110 s), không phải 170 (170 là tốc độ của CLD). v3 2.582 tiếng thực ra chỉ khoảng 11 phút → v4, v5 kéo lên khoảng 3.550 tiếng; sổ mở rộng 71 → 118 dòng (nhóm D hai phía, cầu hàng không; nhóm E nhân chứng, hôm nay), `kiem-so.py` 0 lỗi.

### Hook: 4 vòng chấm (thang 7 tiêu chí, /35)
| Bản | Agy | Opus |
|---|---|---|
| H0 (mở v3, loạt pháo 13/3) | 27 | 26 |
| H1 lời hứa ba phát | 31 | 28 |
| H4 pháo ta vào trước, Pháp chưa biết | 30 | 29 |
| Mở v4 (H4 ghép H1, theo Shu) | 29 | 26 |
| Mở v5 (cảnh 9/4: thả 195 tấn, thu 6 tấn; câu hỏi đúng chữ tiêu đề B) | chưa chấm | Opus tự chấm 32 |

### Cổng máy v5
| Cổng | Kết quả |
|---|---|
| `quet.py` kịch bản + lời đọc; `--tieu-de` (tiêu đề, bìa, 2 dòng đầu mô tả) | 0 CHẶN, 0 CẢNH BÁO |
| `trung-lap.py` (16 phụ đề ĐBP, 9 CLD, 185 phụ đề kho học Shu, 112 bóc băng Deepgram, bản mẫu Goha) | **0,65 %, 0 câu: ĐẠT**. Với danh sách cụm cũ: 0,73 % và đúng 1 câu là công thức "dưới sự lãnh đạo của Đảng và Chủ tịch Hồ Chí Minh" (sổ M20) → thêm vào `cum-chinh-thong.txt`. v4 lần đầu 0,85 %: Claude viết lại 7 câu cách kể (0,36 %). |
| Mã sổ | 88 mã, 0 mã lạ, 0 KHÔNG DÙNG/ĐỐI CHIẾU |
| Mốc | câu hỏi trung tâm 0:49 (5,5 %); lời hứa ba phát vỡ 55,6 %; điểm hoả A1 77,6 %; 6 câu hỏi tu từ (khoảng 2,5 phút một câu); 11 lời trích có tên người nói; câu cuối 8 tiếng |

### Phản biện vòng hai (`agy-phan-bien-v4.md`, `opus-phan-bien-v4.md`) → v5 (`brief-bien-tap-v5.md`, 12 quyết định)
Nhận: sân bay 200–300 tấn là của hai sân bay [A4a]; "ba phân khu" (không "ba cụm") [M6]; bỏ "Nhưng" sau lời dặn "chắc thắng" (quyết định 26/1 làm đúng lời dặn [M5]); tách nguồn A6b (QĐND / TTXVN); trục thời gian Ch4–5 không giật lùi; "mồng"; logic quyết định thứ ba so với mốc 27/3 [B5a]; "ngày 7/5" tổng công kích (không "chiều"); câu lãnh đạo của Đảng [M20]; chủ thể ta ở các điểm cao phía Đông [M3]; phiên âm "Xê Một", "Hát Sáu"; số mộ đủ 10 / 39 / 596 [E7]. Bác: Agy đòi đưa lại bộ ba số pháo vào lời (giữ, nhưng gọn); "đánh đi đánh lại" các điểm cao (sổ không có, viết theo M3/M4).

### Còn treo
- E9 (hơn 4.000 hy sinh, theo VTV) và B2d (24 pháo cao xạ) cần đối chiếu sách "Điện Biên Phủ: Sự kiện – Con số" (Nxb QĐND 2024) trước khi làm giọng.
- Phần Mở v5 dài 391 tiếng (khoảng 1:37, 11 %), dài hơn khuôn 60–90 s; giữ vì mạnh nhất qua chấm điểm, có thể gọt khi dựng.
- Ảnh "A?" (gồm ảnh lãnh tụ) chưa khoá nguồn: tối đa 3–5 s hoặc thay nền chữ ở P3.

## P3 Phân cảnh (01/11/2026)

Bảng `san-xuat/phan-canh.md` (nguồn sự thật, neo theo câu/chữ của `loi-doc-v5.txt`), tư liệu `san-xuat/anh.tsv`, máy sinh `phan-canh.json`, `tai-san-can-dung.md`.
- `python -I kiem-phan-canh.py` → **ĐẠT**: 248 cảnh, ước 15:07 (242 tiếng/phút + 6 khoảng lặng có tên: P1 6 s, P2 4 s, A1 2,5 s, P3 4 s, GN 3 s, KT 6 s), 16,4 cảnh/phút; mọi chương ≥ 14,5 cảnh/phút và có cận đặc tả.
- Theo kiểu: 3D mới 66, 3D bản mẫu 24, thẻ 64, map3d 43, vnmap 8, ảnh 29, Karmen 12, cần tìm 2 (ảnh nghĩa trang A1, hàng mộ; có phương án thay bằng thẻ trên nền tối).
- Thử đột biến 6/6 bắt đúng lý do: lãnh tụ dựng 3D, vnmap thiếu Hoàng Sa, ảnh cấm (bìa Time), Karmen > 5 s, số không nguồn, lời lãnh tụ trùng lời đọc.
- Quyết định hình: không dùng ảnh lãnh tụ A? (Đại tướng xem bản đồ, duyệt cao xạ): câu 93 là bản đồ tối + thẻ chữ chức danh; ảnh A duy nhất (Bác Hồ và Bộ Chính trị, gốc TTLTQG III) ở câu 42, chế độ `lanhTu`. Loạt mở màn 13/3 dùng Karmen 43:05 + bản đồ chớp sáng, không 3D pháo 105 của ta. Phan Đình Giót: lô cốt nhả lửa từ xa rồi tắt, máy nâng lên trời, không người. Tô Vĩnh Diện: sa bàn Dốc Chuối và pháo dừng bên vực (cảnh 3D bản mẫu T-D1, T-E4), P5 phải soát khẩu pháo là cao xạ.
- Ảnh Castor có Cô-nhi, Đờ Cát-xtơ-ri chỉ ghi năm 1953 (không gắn ngày). Ảnh A? và B chạy ≤ 4,7 s (ước tính); đo lại sau P4.
- Còn treo: E9 (hơn 4.000 hy sinh, VTV) và B2d (24 cao xạ) một nguồn; tìm ảnh nghĩa trang A1 có giấy phép (Commons) ở P5.

## P4 Giọng (01/11/2026)

- Đối chiếu trước khi làm giọng: B2d (24 cao xạ 37 mm) thêm VOV.VN 06/05/2020 và Tạp chí Con số & Sự kiện, nay ba nguồn khớp; E9 (hơn 4.000 hy sinh) khớp 4.020 ở VTV, Tạp chí Con số & Sự kiện và Wikipedia (dẫn hồ sơ quân y). Chưa có sách «Điện Biên Phủ: Sự kiện – Con số»; lời giữ "hơn 4.000". Ghi ở cột `ghi_chu_chenh_lech`; `kiem-so.py` 0 lỗi.
- Tung Dang `3VnrjnYrskPMDsapTr8X`, `eleven_v4`, `[fast-paced]`. Reelcrew giới hạn `eleven_v4` 5.000 ký tự mỗi lượt (bảng `MAX_CHARS` không có v4, rơi về trần v3), nên chia 5 lượt ở ranh chương: Mở+Ch1, Ch2+Ch3, Ch4, Ch5, Ch6+Kết. Mỗi lượt cân về −18 LUFS, cắt câu bằng `cat-cau.py` (mốc chữ của chính TTS), nối theo lời, chèn 6 khoảng lặng có tên (`san-xuat/dung-duong-giong.py`).
- **Chi phí ElevenLabs:** TTS 16.280 ký tự (5 lượt) + 2.758 ký tự (4 câu đọc lại, mỗi lần đọc kèm câu trước, câu sau) ≈ 19.000 ký tự; STT khoảng 15,3 phút + 1 đoạn 12 s. Deepgram (soi chéo) 8 đoạn ngắn.
- STT ElevenLabs trên đường giọng: **98,1 %** (ngưỡng 97 %), 46 chỗ lệch. Phần lớn là cách viết (mùng/mồng, Navarre, Piroth, De Castries, "c" cho "xê", "im lặng" ở khoảng lặng). 7 chỗ nghi đọc sai soi chéo bằng Deepgram nova-2: cả hai cùng nghe sai ở câu 5 ("chính" → "chiến"), 105 ("chèn" → "tràn/che"), 197 ("tay ngai" → "nhai"), 213 ("dám" → "dán/rán") → đọc lại; bản mới Deepgram nghe đúng 105, 197, 213; câu 5 ElevenLabs nghe đúng "chính" (Deepgram "chín", vần -inh giọng Bắc). Đạt: "Pu Pha Sông", "Nà Nhạn", "Giong" (Deepgram "Dong", gi/d giọng Bắc).
- Đường giọng `<output>±101-dien-bien-phu-1954\giong\giong-v1.wav`: **15:18,1**, −18,0 LUFS, đỉnh −1,2 dBFS; độ to từng câu lệch chuẩn 0,6 dB, các câu thay nằm trong ±0,7 dB so với câu bên cạnh.
- Phân cảnh đo lại trên mốc chữ thật (`san-xuat/moc-cau.json`): ĐẠT sau hai sửa (C1-24 Karmen vào từ chữ thứ 2 câu 47 vì dài 5,04 s; C3-37 ảnh A? 5,6 s tách thêm C3-37b 3D). 249 cảnh, 16,2 cảnh/phút.

## P5 Dựng (01/11/2026, 21:18–23:15)

Máy dựng theo lô trong `san-xuat/` (chi tiết: skill `goha-ls-dung`): `dung-the.py` 64 thẻ + 2 thẻ thay ảnh nghĩa trang, `dung-tu-lieu.py` 29 ảnh + 12 Karmen, `dung-ban-do.py` 43 map3d + 8 vnmap, `dung-3d.py` + `trang3d/tap1.js` 90 cảnh 3D, `dung-lop-chu.py` 133 lớp chữ, `ghep-hinh.py`, `dung-am.py`. Mọi lô: số khung từng cảnh khớp (0 dòng LỆCH); ghép 22.034 khung đúng tổng.
- Soi ảnh tĩnh và sửa: ghi nguồn thẻ chữ; lời Bác ngắt dòng; nhãn bản đồ đè nhau; `template/node_modules` thiếu (cài lại three); 3D co đồng hồ vật lý khi cảnh dài hơn cảnh mẫu; điểm nhìn biến thể máy bằng raycast lưới; cảnh mẫu BD7 hỏng ở kho hiện tại (thay 4 cảnh hào bằng góc sân bay BD8); cảnh đêm tăng phơi sáng; cảnh dãy núi đổi sang sân khấu Him Lam (không lộ ô cờ); C4-18 ảnh bảng chú thích hiện vật (lộ số hiệu) → thay ảnh khẩu pháo.
- Bảng phân cảnh sửa cột Hình 28 cảnh 3D cho đúng cái hiện lên; **nợ chất lượng kho 3D** (ghi trong ngoặc ở bảng): cửa khoang C-47, ụ pháo Pháp, la bàn và đèn pin trong hầm, điện thoại dã chiến, mưa trong hào, ụ cao xạ 37, mặt cắt hào có thước; 7 cảnh đồi trong sương gần giống nhau.
- Đã soát: Dốc Chuối dùng mô hình `phao-37` (đúng cao xạ 37). Ảnh lãnh tụ duy nhất (Bác Hồ, Bộ Chính trị, TTLTQG III) chế độ `lanhTu`; lời lãnh tụ chỉ ở thẻ chữ trong khoảng lặng.
- Âm: 9 lớp nền (8 bản nhạc kho Suno theo chương + gió núi), 78 tiếng động kho (không gen mới, 0 đồng); nổ bộc phá A1 trong khoảng lặng A1; nhạc ~−33 dB ở hai khoảng lặng lời Bác.

## P6 QC (01/11/2026, từ 23:15)

- STT ElevenLabs trên bản trộn v1: 95,8 % (TRƯỢT): bốn thẻ trích lời có tiếng máy chữ, dây kéo pháo −20 dB dài tới 6 s lấp lời (STT trả "đọc lại"). Sửa `dung-am.py`: tiếng động trong lời ≤ −30 dB, máy chữ ≤ 2 s → **97,9 %** (giọng riêng 98,1 %). Deepgram soi chéo "chèn", "mười bảy giờ năm phút", "hai mươi giờ ba mươi phút": nghe đủ. **Chi phí:** STT ElevenLabs 2 lượt × 15,3 phút.
- Soi khung bản đồ: 8 cảnh vnmap × 3 khung: Hoàng Sa, Trường Sa, "Biển Đông" ở mọi khung chạm biển; khung Tây Bắc không chạm biển; không đường lưỡi bò. ĐẠT.
- `reelcrew deliver` đẩy đỉnh thật lên **+2,6 dBTP** (đúng lỗi đã ghi ở hồ sơ dự án) → bỏ deliver, ghép thẳng master `loudnorm I=-14 TP=-2 + alimiter 0,7` vào hình.
- `reelcrew check`: các cảnh "hình đen" 0,13–0,33 s là khung đầu thẻ nền đen (chữ hiện sau 0,05–0,3 s, cố ý); "hình đứng yên" là thẻ, ảnh (cố ý); một khung chớp sáng đầu cảnh 3D C1-22 → bỏ khung đầu mọi cảnh 3D khi ghép.
- Ghép thẳng master `loudnorm I=-14 TP=-2 + alimiter` vẫn −0,8 dBTP sau AAC → thử trên AAC: TP −3 cho −14,4 LUFS, đỉnh −1,6. **File cuối: −14,4 LUFS, đỉnh thật −2,0 dBTP** (ebur128 trên `final/dien-bien-phu-1954-v1.mp4`, 22.034 khung, 2,2 GB).
- Khung lỗi 3D: sửa bằng đo độ sáng từng khung (khung lệch > 20 so với hai khung kề, ở mép so hai khung cùng phía) và `freezeframes`; tập 1 có 2 khung (C1-22 khung 1, C5-06 khung cuối); bỏ qua cảnh có nổ, chớp, lửa (C5-28 là chớp bộc phá).
- `reelcrew check` lần cuối: còn 2 "khung tối" và 13 "hình đen" 0,13–0,92 s, đều là khung đầu/cuối thẻ nền đen (chữ hiện sau 0,05–0,3 s; "3 PHÁT" mờ dần ở Kết); "hình đứng yên" ở thẻ, ảnh. Chấp nhận.
- Phụ đề `final/dien-bien-phu-1954-v1.vi.srt`: 285 dòng theo mốc chữ thật, câu dài tách ở dấu phẩy, dài nhất 90 ký tự.
- **DỪNG: chờ user xem bản cuối** (`<output>±101-dien-bien-phu-1954inal\dien-bien-phu-1954-v1.mp4`). Sau khi duyệt: chép về `tap/EP001-dien-bien-phu-1954/Final/`, làm P7 (ảnh bìa A/B, postpack).

## v2: làm lại theo sàn bản Demo, 3 phút đầu (02/11/2026, 00:27–01:16)

User chê v1 kém hơn Demo (hook nhạt, SFX mờ, không khí thế). Plan `plans/261102-0026-tap-1-dbp-v2/plan.md`.
- **Intro trailer** `san-xuat/intro.py`: 6,875 s (165 khung) trước lời; HK1–HK4 Demo nguyên hình, tiếng; 9 cú cắt đúng phách nhạc hook (C-47 trúng đạn, cột nổ, pháo nhả khói, vượt hào xung phong, bộc phá A1, Độc Lập đêm, tiến qua khói nổ, nổ trên đồi xa); chữ "ĐIỆN BIÊN PHỦ · 13/3 – 7/5/1954" đứng yên; 6,36 s cắt hết tiếng (đo −180 dB), CẠCH, lời vào khi nhạc dâng lại. Mọi mốc lùi 165 khung.
- **Hình**: 12 cảnh yếu thay bằng phim Karmen chưa dùng (hòm hàng, thùng phuy, đạn pháo tiếp tế, hầm vòm thép gai, đường đèo đất đỏ, pháo Pháp, xác máy bay, cánh đồng nổ khói; mỗi đoạn ≤ 5 s, ghi "mô phỏng lại") và 3D Demo đã duyệt (nguồn mới `demo:<mã>[>]`, `dung-demo.py`); MO13 tách MO13b (ảnh chuyển đạn vào hầm pháo, vì đoạn Karmen > 5 s). Ảnh màu Cát-to vẫn khoá (nghi tô màu) nên C1-10 giữ 3D cũ (nợ).
- **Màu lịch sử, quân sự** (`mau: 'quan-su'`): thẻ sáng trên giấy bản đồ tác chiến (đường đồng mức, lưới toạ độ, nếp gấp, trôi chậm); 9 thẻ tối phủ trong suốt lên 3D Demo làm tối, mờ, đẩy máy (`NEN_SAU`); vnmap kiểu bản đồ tham mưu in giấy (Việt Nam đất son; Hoàng Sa, Trường Sa, "Biển Đông" giữ nguyên).
- **Âm** `dung-am.py` viết lại: 286 tiếng / 3 phút = **91 tiếng/phút** sau intro (Demo 89, v1 5); mỗi cú cắt một tiếng theo loại cảnh, gõ phím từng chữ trên thẻ và nhãn, lớp nền chiến trường xa + gió núi, nhạc hook vol 1,3 liền từ intro, đập trầm ở thẻ số, tiêu đề, chương. Tiếng lớn chỉ trong khe lặng đo được: hơn nền ngay trước +5…+24 dB (RMS). Câu 14 không có khe → đập nhỏ, ngắn.
- **SFX mới (chi phí ElevenLabs)**: 16 tiếng, ~35 s âm thanh (`<output>\261102-dbp-v2\am\sfx\`), + 1 tiếng vụt synth miễn phí. Earshot: 14 strong; "chien-truong-xa", "xac-may-bay" weak (nghe ra nổ xa, kim loại cạo; dùng làm nền); bản "vut-tram" ra tiếng đập → đổi vai thành `cham-cat`. Ghi `<thư mục công cụ cũ>\Du-an\LichSu-Studio\kit\ASSETS.tsv`.
- **Đo bản 3 phút** `<output>\261102-dbp-v2\xem\dbp-v2-3phut-dau.mp4` (4.320 khung, 1080p24): −14,2 LUFS, đỉnh −2,0 dBFS sau AAC, LRA 4,7. Cú cắt thật 60 (12 intro + 48 cảnh) = 20/phút; máy dò `scene>0.3` thấy 54 (v1 39; Demo 48 trong 2:34). **STT ElevenLabs bản trộn 98,2 %** (ngưỡng 97 %; v1 97,9 %), 17 khác biệt chỉ là cách viết tên riêng và nhãn hiệu ứng. `kiem-phan-canh.py` ĐẠT.
- Sửa kèm: đoạn render trình duyệt mang cờ dải màu đầy đủ (yuvj420p) trộn với phim dải TV → ghép cuối mã hoá lại về TV một lần.
- **DỪNG**: chờ user so 3 phút đầu với Demo; đạt mới làm cả phim.

## v2: sóng cảm xúc, 3 phút đầu (02/11/2026, 01:33–01:55)

User xem bản 3 phút: "đã ổn hơn, hấp dẫn hơn"; giọng hùng hồn, nhanh nên cần chỗ nghỉ, sóng cảm xúc; mỗi lần có bảng chữ, bảng thông tin thì gõ chữ làm điểm nghỉ; không gen lại giọng.
- **Giọng** `giong-v2.wav` (15:50, từ các câu đã cắt của v1, không gọi ElevenLabs): 14 khoảng thở T1–T9, U1–U5 sau câu 1, 3, 8, 11, 15, 17, 18, 22, 25, 26, 27, 29, 33, 39 (1–3 s, tổng 25,5 s, số nguyên khung). `moc-cau.json`, khe lặng đo lại `am/khe-lang-v2.txt`. `kiem-phan-canh.py`: khoảng thở T*/U* được giữ hình bởi cảnh trước; ĐẠT; đúng 14 cảnh đổi số khung (13 bảng chữ + bản đồ C1-07).
- **Thẻ máy chữ**: MO10, MO14 (lời hứa Pi-rốt, tô "3 phát"; bỏ thẻ trùng ở MO13), MO18 (câu hỏi lớn), MO22, C1-03 (gạch Điện Biên Phủ), C1-16 ("nhọt hút độc") gõ xong trong khoảng thở; hạn chót neo `@T4-0.6` (mới trong `dung-the.py`). Tiếng gõ từng ký tự theo lịch gõ chép từ `typewriter.js` (cùng seed), chỉ thành tiếng trong khoảng thở, trộn sẵn một tệp mỗi thẻ (`reelcrew mix` vỡ ENAMETOOLONG khi > ~300 cue).
- **Nhạc**: hook hạ mỏng trong mỗi khoảng thở rồi trở lại, đáy gần lặng ở câu hỏi lớn (T5), dâng vào tiêu đề; Chương 1 nhạc tài liệu êm, dâng nhẹ ở Cát-to; đoạn lắng (câu 25–30, 34–37) tiếng nhỏ 6 dB, không gõ nhãn.
- **Bản xem** `<output>\261102-dbp-v2\xem\dbp-v2-song-3phut.mp4` (3:26, 4.944 khung, cùng nội dung bản 3 phút trước): −14,2 LUFS, đỉnh −2,2 dBFS. STT ElevenLabs bản trộn **98,2 %** (24 khác biệt: tên riêng viết kiểu Pháp, nhãn "im lồng tiếng" ở khoảng thở). Chi phí: 2 lượt STT × 3,4 phút.
- **DỪNG**: chờ user xem bản có sóng; đạt thì làm cả phim (handoff `plans/handoffs/261102-0155-tap-1-dbp-v2-ca-phim.md`).


## v2: cả phim theo sóng cảm xúc + P6 QC (02/11/2026, 01:57–03:05)

User giao làm luôn khi bản 3 phút có sóng đạt (ô nhận xét trong prompt để trống, hiểu là đạt). Không gọi lại TTS.
- **Khoảng thở cả phim**: 45 dòng mới V1–V9, W1–W9, X1–X9, Y1–Y9, Z1–Z9 (1–3,5 s, bội 0,5 s, tổng 85,5 s) ở mọi bảng chữ, bảng số từ câu 41; đáy mỗi chương: V3 (Ch1, 3 s), W1 (Ch2, 3 s), X1 (Ch3, câu hỏi đúng hay sai, 3 s), X8 (Ch4, người trong hào vẫn đào, 3 s), Y6 (Ch5, lặng trong lòng hầm trước tiếng nổ A1, 3 s), Z5 (Ch6, người hy sinh, 3,5 s). `giong-v2.wav` 17:06,1 (nối lại câu đã cắt). `kiem-phan-canh.py` nhận tiền tố T…Z; ĐẠT (KT-07 ảnh A? vượt 5 s → Z7 hạ 1 s). 52 cảnh đổi số khung, render lại đúng các cảnh đó.
- **Thẻ**: 6 thẻ lời trích chuyển `may-chu` gõ xong trong khoảng thở (C1-23, C2-11, C3-27, C4-14, C5-08, C5-17); 24 thẻ tối mới phủ lên hình động (`NEN_SAU`), trừ lời Bác (C3-20, C3-21, KT-10) và đoạn tưởng niệm (KT-22, KT-24, KT-25). Soi bản đồ bắt được 3 vnmap (C2-15, C6-07, KT-16) và 7 thẻ (C2-21, C3-20, C3-21, C5-26, KT-08, KT-10, KT-25) còn màu v1 (đỏ trên navy, giấy kraft) → render lại màu quân sự.
- **Hình thay**: C2-12, C2-28, C5-37 (đồi sương lặp) → Karmen phá đá mở đường, đoàn gùi hàng leo dốc, đường tiếp tế có cờ đỏ; C4-15, C4-32 (ba cảnh "đồi cam chớp trắng" gần giống nhau) → Karmen đạn nổ dồn, vượt hào thép gai; C5-28 → 3D Demo BD13. Sửa Karmen trùng hoặc sai: C4-02 cũ (43:05) lộ 2,4 s cảnh người chỉ huy trước cú cắt 2587,4 → 43:07,6 (pháo nhả khói); C4-09 trùng MO29 → 43:16,2; C4-25 trùng MO15 và lộ 0,3 s xe tăng → 44:29,25 (xác máy bay tiêm kích). Mọi đoạn kiểm cú cắt bằng máy dò `scene>0,25`, ≤ 5 s, ghi "mô phỏng lại".
- **Âm**: nhạc mỗi chương một bản theo sóng (tài liệu → battle-2 nhỏ → hành khúc kéo pháo → battle-1 → battle-2 tắt hẳn ở đáy trước A1 → hành khúc 2 → requiem), hạ mỏng ở mỗi khoảng thở, đáy hạ sâu (`DAY`); nền chiến trường ở Ch4–Ch5; 20 tiếng nhấn mới trong khe lặng đo lại (`khe-lang-v2.txt`, 172 khe) ở các câu then chốt (pháo 13/3, "Chiến dịch Điện Biên Phủ bắt đầu", tổng công kích, "Giơ tay lên!"…), bộc phá A1 có rung trầm + nổ gần. 1.014 tiếng động, **58/phút** sau intro (đoạn lắng thưa có chủ ý; phút căng 76–96). `reelcrew mix` vỡ khi > 300 cue → trộn sẵn tiếng động một lớp (`tron_tieng`), reelcrew mix chỉ trộn giọng + nhạc.
- **Ghép**: bỏ khung đầu đen 0,17 s của cảnh 3D (trang chưa kịp sáng) bằng khung sáng đầu tiên (`den_dau` ở `ghep-hinh.py`); bỏ lớp chữ thừa ở KT-22, KT-24 (lộ dòng nội bộ "chờ tư liệu có giấy phép" đè ghi nguồn).

### P6 QC (file `<output>\261102-dbp-v2\final\dien-bien-phu-1954-v2.mp4`, 24.791 khung, 17:13)
- STT ElevenLabs bản trộn cả phim: **97,9 %** (ngưỡng 97 %); 133 khác biệt gần hết là nhãn tiếng nền và tên riêng viết kiểu Pháp; chỉ 3 chỗ khác chữ thật: "làm"/"là", "sông"/"xông", "rừng Nà Nhạn" → Deepgram soi chéo nghe đủ câu ("tà nhạn", lệch phụ âm). **Chi phí:** STT ElevenLabs 1 lượt × 17,1 phút.
- Độ to file cuối (ebur128): **−14,2 LUFS, đỉnh thật −1,9 dBTP**, LRA 4,2.
- Soi 8 vnmap × 3 khung trên file cuối: Hoàng Sa, Trường Sa, "Biển Đông" ở mọi khung chạm biển; khung Tây Bắc không chạm biển; không đường lưỡi bò. ĐẠT (sau khi render lại 3 bản đồ màu quân sự).
- `reelcrew check`: còn 3 "hình đen" (C5-15 0,13 s khung đầu thẻ nền tối, KT-22 0,92 s mở đoạn tưởng niệm, KT-25 0,13 s) cố ý; 2 "hình đứng yên" (C1-22 dép trên lá, C4-07 sa bàn đồi nổ) là cảnh máy đứng. Chấp nhận.
- Phụ đề `final/dien-bien-phu-1954-v2.vi.srt`: 285 dòng theo mốc chữ mới (lùi intro 6,875 s), tắt trong khoảng thở, dài nhất 90 ký tự.
- **Nợ chất lượng**: còn nhiều cảnh 3D "sa bàn trên đồng cỏ phẳng" ở Ch2–Ch5 (hầm vòm bao cát C2-03…C2-27, KT-03, KT-05; nhánh hào C4-36, C4-39, C5-11; dù C4-27, C4-43, C5-05, C5-10, C5-23; đồi cam chớp C4-05, C4-07); kho Karmen chưa dùng và 3D Demo không đủ đoạn dài, đúng nghĩa để thay hết. C1-10 vẫn 3D cũ (ảnh màu Cát-to khoá). C6-20 (đáy hy sinh) giữ đồi sương có chủ ý.
- **DỪNG**: chờ user xem bản cả phim.

## v3: từ 7 lên 9 điểm, hậu kỳ nhà đài (02/11/2026, 09:40–11:45)

Plan `plans/261102-0940-tap-1-dbp-v3/plan.md`; phản biện Opus ngữ cảnh mới `phan-bien.md` (nhận gần hết).
- **Màu nền (user chọn A lúc 09:58):** vải ô-liu quân phục + đồng mức mờ, chữ kem, đỏ son sáng (`cards.js` `mau: 'xanh-qd'`, `makeQuanPhuc`); 27 thẻ sáng (số liệu, lịch, dòng thời gian, hai cột) render lại. Sửa kèm: số ngày, nhãn phụ dùng màu mực cứng (chìm trên nền sẫm) → `mucMo()`; chú thích thẻ lịch tràn mép phải (có từ v2) → lịch dịch trái khi có chú thích.
- **Dốc Chuối phục hồi:** câu 105 thành 6 câu ngắn trên cùng dòng, mọi chữ theo [M11] (sửa `cach_noi` của sổ, ghi chú luật bạo lực ở `kich-ban-v5.md`); `quet.py` 0 CHẶN. Đọc lại cụm 104–106 bằng ElevenLabs (3 lượt, chọn lượt 1: ngắt câu rõ; Deepgram nghe đủ cả 3); ranh câu lệch < 1 dB. Khe giữa dòng WA–WD (`105:k`): dây đứt, pháo trôi, bánh pháo khựng (tiếng của khẩu pháo, không tiếng va vào người), W8 lặng 3 s trời sao. Hình: chuỗi Demo T-D2 (dây tách, đứt) → 3D T-D3 (pháo trôi) → Demo T-E1…E3 (lao mình chèn bánh, bánh khựng) → T-E4; nhạc chỉ còn 40 % cả cảnh.
- **Mốc khí thế (khoảng lặng có tên, có cảnh riêng):** H1 sau câu 114 (3,5 s, Karmen 43:19,6 pháo khai hỏa → bộ binh xông lên), H2 sau X7 (2 s, Karmen 43:39,3), H3 sau câu 174 (1,5 s, 3D Demo BD9+6), H4 sau câu 178 (1,75 s, Karmen 43:10,35 pháo + lô cốt nổ; một cụm với A1, nhỏ hơn A1). X1 3 → 2,5 s; W9, X7 → 1 s; Z7 giữ 1 s (ảnh cờ hạng A? trần 5 s), nhạc hành khúc dâng ở câu 210, requiem vào sau cờ; nền chiến trường chạy dưới câu 179–180 rồi cắt phụt ở câu 181. Mỗi mốc 4–8 lớp; rung máy tắt dần đúng cú nổ (`ghep-hinh.py` `RUNG`). Soi khung loại đoạn Karmen 43:48 (là tù binh Pháp, cờ Pháp ở 43:49,5).
- **Hậu kỳ âm bằng plugin thật** (`hau-ky-am.py`, pedalboard của Goha AVS): giọng Pro-Q 3 → Pro-DS 3,5 dB → Pro-C 2 Vocal; nhạc khoét 2,5 kHz + duck sidechain −8 dB; tiếng chia bus không gian (thung lũng Valhalla Room 3,2 s, hầm 0,7 s, giao diện phòng nhỏ), đuôi vang duck −9 dB dưới lời; Pro-C 2 Bus → Pro-L 2. Đo: plugin trễ 1 mẫu, 0 khung giọng bị câm. 9 SFX ElevenLabs mới (pháo loạt gần, nổ dồn xa, đạn rít, đất rơi, súng máy gần, hô xung phong xa, hỏa tiễn, cờ bay, reo thắng); Deepgram xác nhận tiếng hô và tiếng reo không thành chữ.
- **Độ nhấn (RMS 400 ms so với lời 3 s trước):** H1 +9,9 dB, H2 +9,4, H3 +7,6, H4 +8,8, A1 +10,5 (lớn nhất phim); Dốc Chuối WB +7,2, WC +8,3, WD +5,4. Chưa đạt mục tiêu +12 dB của plan: trần đỉnh −3,5 dBTP (để qua AAC) ở −14 LUFS là giới hạn vật lý.
- **Sửa nhờ STT:** tiếng nhấn ở khe sau câu 23, 141, 180 tràn 0,5 s vào câu sau (có từ v2) → `gon()` cắt gọn trong khe.

### P6 QC (file `<output>\261102-dbp-v3\final\dien-bien-phu-1954-v3.mp4`, 25.280 khung, 17:33, 2,5 GB)
- STT ElevenLabs bản trộn: **98,0 %** (v2 97,9 %), khác biệt còn lại chỉ ở cách viết tên riêng, nhãn tiếng nền, thanh điệu (chèn/chen: đo lớp tại chữ, giọng cao hơn nhạc 8 dB, không tiếng động). Sau đó chỉ hạ nhạc ở Dốc Chuối; Deepgram đoạn 30 s nghe đủ "chèn bánh pháo". **Chi phí:** STT ElevenLabs 2 lượt × 17,5 phút; TTS khoảng 1.180 ký tự; SFX 9 tiếng khoảng 32 s; Deepgram vài đoạn ngắn.
- Độ to file cuối (ebur128): **−14,2 LUFS, đỉnh thật −1,4 dBTP**, LRA 3,6 (v2 4,2: limiter ép nhiều hơn để giữ cú nổ). Bộ `aac` của ffmpeg vọt đỉnh +0,8…+1,9 dBTP → mã hoá `aac_mf` 256k, trần Pro-L 2 −3,5.
- Bản đồ: 8 vnmap × 3 khung: Hoàng Sa, Trường Sa, "Biển Đông" ở mọi khung chạm biển; Tây Bắc không chạm biển; không đường lưỡi bò. ĐẠT.
- `reelcrew check`: 2 "hình đen" 0,13 s (khung đầu thẻ nền tối C5-15, đầu đoạn tưởng niệm KT-24) và 2 "hình đứng yên" (C1-22 dép trên lá, C4-06/C4-07 sa bàn) như v2, cố ý. Đã sửa: 0,25 s đen đầu H3 (khung đệm đen của video nhóm Demo → `BD9+6`).
- Bỏ hạt phim tổng hợp: lượt mã hoá cuối có `noise` làm file 9,4 GB (71 Mbps).
- Phụ đề `final/dien-bien-phu-1954-v3.vi.srt` (`san-xuat/phu-de.py`, mới): 288 dòng, dài nhất 90 ký tự.
- **Tự chấm:** 8,5/10. Dốc Chuối, các mốc tiến công, màu nền đạt ý. Còn kéo điểm: (1) cảnh 3D "sa bàn đồng cỏ phẳng" ở Ch4–Ch5 (11:20–11:40, C4-36…C5-23) vẫn còn, kho Karmen chưa dùng đã cạn đoạn đúng nghĩa; (2) LRA thấp, độ nhấn +8…+10 dB.
- **DỪNG:** chờ user xem bản v3.

### Sửa sau khi user xem v3 (02/11/2026 12:06–12:35)
- User: bản v3 "tương đối tốt, còn chút sạn"; câu Tô Vĩnh Diện quay về lỗi cũ «anh hy sinh» trong khi Demo v11 (26/10) đã sửa thành «Ông anh dũng hy sinh.» (gọi «ông», không «anh»). Nhận lỗi phát âm nhỏ («chèn») và nợ cảnh sa bàn 3D là chấp nhận được.
- Sửa: đọc lại đuôi cụm (ElevenLabs 3 lượt × khoảng 200 ký tự, chọn lượt 2), ghép "Ông anh dũng hy sinh." vào bản đọc đã duyệt sau "vực." (cân theo cùng câu "Pháo không lao xuống vực.", bù −3,2 dB); W8 3,013 → 2,741 s để mọi mốc sau giữ nguyên; render lại 4 cảnh lệch 1 khung do làm tròn (C4-04, C4-05, C5-13, C5-14). File cuối −14,2 LUFS, đỉnh −1,4 dBTP, 25.280 khung; Deepgram 50 s quanh Dốc Chuối nghe đủ "lao mình chèn bánh pháo… Ông anh dũng hy sinh.".
- Chặn tái phạm: sổ `kenh/cach-noi-da-chot.tsv` + máy kiểm `tools/lichsu/kiem-da-chot.py` (test), `dung-duong-giong.py` tự gọi; thêm luật xưng hô nhân vật phía Việt Nam (phản ánh khán giả CLD Studio: «chỉ đọc chức danh bên Mỹ, Việt Nam đọc trống không»). Lời tập 1: 0 chỗ phạm.
- Đang làm: nghiên cứu toàn bộ bình luận video Điện Biên Phủ nhiều view (sub-agent), đối chiếu lời tập 1 trước khi đăng.

## v4: sửa nội dung theo hai báo cáo soát, dấu kênh logo mới 4 góc (02/11/2026, 15:44–17:45)

Handoff `plans/handoffs/261102-1515-tap-1-dbp-v3-sua-noi-dung.md`. Bình luận: đọc trọn 1.676/1.676 bình luận dài hơn 105 ký tự và phân loại 280 bình luận không chữ (0 tiêu cực), báo cáo `plans/reports/binh-luan-261102-1222-dien-bien-phu.md` mục 8; không có đính chính mới về quân hàm, chức vụ.
- **Tra nguồn** (`plans/reports/nguon-261102-1550-du-kien-dbp.md`, tự mở lại QĐND và Nhân Dân để kiểm): ông Phạm Đức Cư, Nguyễn Quang Thuận, Trần Xuân Kình chỉ có nguồn gọi «chiến sĩ» năm 1954 → lời và thẻ gọi «chiến sĩ»; ông Nguyễn Bội Giong năm 1954 là phái viên Bộ Tổng tư lệnh, chưa có quân hàm (phong lần đầu theo Nghị định 306-TTg năm 1958) → «Đại tá Nguyễn Bội Giong, khi ấy là phái viên…»; ông Tạ Quốc Luật là Anh hùng LLVTND (QĐND 2014, Tuổi Trẻ: truy tặng 2004) → sổ M15a; ngày Đờ Cát-xtơ-ri lên Thiếu tướng mâu thuẫn (23/4 hay 16/4) → không nêu ngày; Cô-nhi, Na-va giữ «tướng»; 10.130 là số thương binh đã điều trị, khác phạm vi 9.118 bị thương; giờ nổ súng giữ 17 giờ 5 phút; H6 có tham gia (Nhân Dân, QĐND).
- **Lời (19 câu):** 10 (Thông tấn xã Việt Nam), 25, 34, 45, 65, 67, 79, 84, 89, 125, 156, 157, 158, 164, 183, 188 («quân địch»), 204 (đủ 4.020 hy sinh, 792 mất tích, 9.118 bị thương theo VTV), 216 («mà không bị tiêu diệt»), 219. Cổng: `quet.py` 0 CHẶN 0 CẢNH BÁO; `kiem-da-chot.py` 0 chỗ phạm; `kiem-so.py` 0 dòng lỗi; chống trùng 0,43 %, 0 câu. Reviewer Opus ngữ cảnh mới: 18/18 câu ĐẠT (`plans/reports/soat-lai-261102-tap-1-v4-cau-sua.md`), nhận thêm câu 158 («thả dù chệch ra ngoài trận địa của phía Pháp») và đồng bộ sổ M16, E9, A4a.
- **Chữ trên hình:** C5-03 «TRONG 195 TẤN»; C4-02 bỏ «cỡ 75–120 ly»; nguồn C6-06, C2-24, C3-18, C1-03; C2-06 nguồn Báo QĐND; C4-23 «SAU 13/3/1954»; «Anh hùng» trên thẻ Tô Vĩnh Diện, Phan Đình Giót, Nguyễn Văn Bạch; thẻ tên ba chiến sĩ và ông Giong; thẻ tổn thất C6-20; C2-17 bỏ «200–300 tấn»; C2-22 «100% (…)»; C1-11, C3-22 theo gợi ý soát.
- **Giọng:** ElevenLabs đọc lại 19 câu (mỗi câu kèm câu trước và sau), **5.432 ký tự**; Deepgram nghe đủ cả 19 câu giữa. Đệm lặng < 1 khung để mỗi câu lệch bản cũ đúng bội số khung (`sua/dem-khung.json`); ba khoảng thở mới ZA (sau Phan Đình Giót), ZB (sau 62 máy bay), ZC (sau ba số sức người). Giọng 17:41.
- **Dựng:** 92 cảnh dựng lại (27 thẻ, 17 tư liệu, 14 bản đồ, 25 cảnh 3D, 1 Demo, 43 lớp chữ), 0 lệch khung; C5-16 tách thành ảnh 4,5 s + C5-16b (Demo BD10) để ảnh hạng A? không quá 5 s. Sửa lỗi cũ trong `ghep-hinh.py`: `freezeframes` cần hai đầu vào; luật mới thay đoạn đầu cảnh 3D nhấp nháy nhiều khung (C1-22, C4-05).
- **Dấu kênh:** logo mới «GOHA STUDIO» (phiên nhận diện, `cc0fb6c`), 229×50, linh hoạt 4 góc: 26 lần đổi góc trên 249 cảnh, chỉ ở cú cắt, mờ vào 0,4 s, tránh thẻ tên, nhãn ngày, tiêu đề thẻ, ghi nguồn; ẩn ở intro, MO30, ảnh và lời lãnh tụ (C1-19, C3-20, C3-21, KT-10), tưởng niệm KT-22…KT-25. Khung Full HD mỗi lần đổi góc: `<output>±102-dbp-v3\soi\dau-4-goc-v4\`.

### P6 QC (file `<output>±102-dbp-v3inal\EP001-dien-bien-phu-1954.mp4`, 25.635 khung, 17:48, 2,6 GB)
- STT ElevenLabs bản trộn: **98,05 %** (v3 98,0 %). Chỗ lệch là cách viết (tên Pháp kiểu Latin, mồng/mùng, «xê» → «c»), nhãn tiếng nền, thanh điệu (chèn/chen, Kình/Kinh). «ở phía bên kia» (câu 76, không đổi) STT ghi «nhạc nền»; Deepgram trên đoạn cắt từ đầu câu nghe đủ → đạt.
- Độ to file cuối (ebur128): **−14,2 LUFS, đỉnh thật −1,4 dBTP**, LRA 3,5.
- Bản đồ: 8 vnmap × 3 khung: Hoàng Sa, Trường Sa, «Biển Đông» ở mọi khung chạm biển; Tây Bắc không chạm biển; không đường lưỡi bò. ĐẠT (`final/soi-ban-do-v4.jpg`).
- `reelcrew check`: 2 «hình đen» 0,13 s (khung đầu thẻ nền tối C5-15, đầu KT-24) và 1 «đứng yên» 4,1 s (sa bàn C4-06), như v3, cố ý. Tờ 64 mốc `final/to-khung-64-v4.jpg`.
- Phụ đề `final/EP001-dien-bien-phu-1954.vi.srt`: 294 dòng, dài nhất 90 ký tự.
- **Chi phí:** TTS ElevenLabs 5.432 ký tự; STT ElevenLabs 1 lượt × 17,8 phút; Deepgram 21 đoạn ngắn.
- **DỪNG:** chờ user xem bản v4.

### Duyệt v4 (02/11/2026 18:48)
- User: "Tổng duyệt ổn rồi"; tập 1 coi như hoàn thiện, chuyển sang SEO & AEO. Bản chốt chuyển về `tap/EP001-dien-bien-phu-1954/Final/` (video, phụ đề, `EP001-do-cuoi-v4.txt`, `EP001-check-v4.txt`, `EP001-check-v4.md`).
- User chốt cách gọi: đúng theo thời điểm sự kiện, «hoặc nói lúc đó ông là…»; câu 164 giữ «Đại tá Nguyễn Bội Giong, khi ấy là phái viên Bộ Tổng tư lệnh». Luật máy `quan-ham-thoi-diem-giong` (sổ cách nói, 27 luật; test 15/15).
- Nâng cấp QC: skill `goha-ls-qc` thêm cổng A (QC nội dung trước khi đọc giọng, render) và `san-xuat/soi-qc.py` (tờ bản đồ, tờ 64 mốc, tra cảnh báo `reelcrew check` về mã cảnh, hậu tố phiên bản).
