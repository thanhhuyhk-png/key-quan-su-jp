# Tiến độ tập 1 · Điện Biên Phủ 1954 (bản 15–17 phút)

Giờ thật từng phase (giờ máy, Asia/Bangkok).

| Phase | Bắt đầu | Xong | Thời gian | Ghi chú |
|---|---|---|---|---|
| P1 Nghiên cứu | 01/11 12:25 | 01/11 12:43 | 18 phút (3 sub-agent Sonnet song song, 8–12 phút mỗi agent) | sổ 71 dòng, 0 lỗi đối chiếu; sổ tài sản; công cụ lay-trang, kiem-so, trung-lap |
| P2 Kịch bản | 01/11 12:45 | 01/11 13:08 | 23 phút | v1 Sonnet 8 phút; Claude rà + 2 vòng sửa; Agy phản biện; cổng máy đạt |
| P2b Hook + phản biện kép + học Shu | 01/11 16:10 | 01/11 18:40 | 150 phút (gồm tải và phân tích 194 video) | user duyệt v3 lúc 16:06, dặn: phản biện thật kỹ, hook hấp dẫn, chuẩn phim QPVN |
| P1b Mở rộng sổ theo Shu | 01/11 18:22 | 01/11 19:23 | 61 phút (Sonnet hết hạn mức giữa chừng, Opus làm nốt nhóm E) | giọng thật 242 tiếng/phút → cần ~3.500 tiếng; thêm lời trích nhân chứng, hai phía, hôm nay |
| P2c Viết v4–v5 theo Shu + phản biện vòng hai | 01/11 19:25 | 01/11 20:15 | 50 phút (Opus viết v4 15 phút, Agy + Opus phản biện 10 phút, Opus biên tập v5 18 phút) | sổ 118 dòng; người viết Opus (Sonnet hết hạn mức đến 21:00) |
| P3 Phân cảnh | 01/11 20:32 | 01/11 20:48 | 16 phút (Opus; đọc tài liệu 8 phút, bảng 248 cảnh, máy kiểm + thử đột biến 6/6) | `san-xuat/phan-canh.md` ĐẠT `kiem-phan-canh.py`; 15:07 ước tính, 16,4 cảnh/phút; skill `goha-ls-phan-canh` |
| P4 Giọng | 01/11 20:49 | 01/11 21:02 | 13 phút (5 lượt TTS mỗi lượt 40–60 s; STT; soi chéo Deepgram; đọc lại 4 câu) | `giong-v1.wav` 15:18, STT ElevenLabs 98,1 %; `moc-cau.json`; phân cảnh đo lại ĐẠT; skill `goha-ls-giong` |
| P5 Dựng | 01/11 21:18 | 01/11 23:15 | 117 phút (máy dựng 7 lô, render nền song song; soi ảnh tĩnh 2–3 lượt mỗi lô) | 249 cảnh, 22.034 khung, 0 ô giữ chỗ; bản trộn −14 LUFS; skill `goha-ls-dung` |
| P6 QC | 01/11 23:15 | 02/11 00:16 | 61 phút (2 lượt STT bản trộn, 3 lượt ghép cuối) | STT bản trộn 95,8 % → nén tiếng động trong lời → 97,9 %; soi 24 khung bản đồ VN ĐẠT; deliver đẩy đỉnh +2,6 dBTP → ghép thẳng master giới hạn −2 dBTP |
| Duyệt v1 | 02/11 00:23 | | | user chê kém hơn Demo (hook nhạt, SFX 5/phút so với 89/phút, không khí thế); yêu cầu làm lại v2 ở chat mới, màu lịch sử, quân sự. Handoff `plans/handoffs/261102-0025-tap-1-dbp-lam-lai-v2.md` |
| v2 nghiên cứu Demo + dựng 3 phút đầu | 02/11 00:27 | 02/11 01:16 | 49 phút (đo Demo, intro, màu quân sự, 17 SFX mới, trộn, ghép, STT) | làm lại theo handoff 261102-0025: Demo làm sàn (hook trailer, SFX dày, nhạc to), màu lịch sử quân sự, dùng lại 3D Demo |
| Duyệt 3 phút đầu v2 | 02/11 01:17 | 02/11 01:32 | | user: "đã ổn hơn, hấp dẫn hơn"; dặn thêm sóng cảm xúc, khoảng thở ở mỗi bảng chữ (gõ máy chữ), không gen lại giọng |
| v2 sóng cảm xúc 3 phút đầu | 02/11 01:33 | 02/11 01:55 | 22 phút | 14 khoảng thở (25,5 s), 6 thẻ máy chữ, nhạc lên xuống; DỪNG chờ user xem `<output>\261102-dbp-v2\xem\dbp-v2-song-3phut.mp4` |
| v2 cả phim + P6 QC | 02/11 01:57 | 02/11 03:05 | 68 phút (45 khoảng thở, render lại 64 cảnh, 1 lượt STT, ghép 2 lần) | `<output>\261102-dbp-v2\final\dien-bien-phu-1954-v2.mp4` 17:13, −14,2 LUFS, đỉnh −1,9 dBTP, STT 97,9 %; DỪNG chờ user xem |
| Duyệt v2 cả phim | 02/11 09:00 | | | user chấm 7/10: màu nền phải xanh quân đội; phục hồi cảnh Dốc Chuối của Demo; bom đạn dày ở mốc tiến công; hậu kỳ nhà đài (Goha AVS, reverb, EQ, nén) |
| v3 lên 9 điểm + P6 QC | 02/11 09:40 | 02/11 11:45 | 125 phút (plan + phản biện Opus, màu A user chọn, đọc lại cụm 104–106, 9 SFX, 4 khoảng lặng mốc khí thế, chuỗi VST, render lại 40 cảnh, 2 lượt STT, ghép 3 lần) | `<output>\261102-dbp-v3\final\dien-bien-phu-1954-v3.mp4` 17:33, −14,2 LUFS, đỉnh −1,4 dBTP, STT 98,0 %; tự chấm 8,5; DỪNG chờ user xem |
| Duyệt v3 | 02/11 12:06 | | | user: "tương đối tốt, còn chút sạn"; phải hoàn hảo về nội dung; chưa render vội. Hai báo cáo soát (Opus độc lập, 5.765 bình luận); handoff `plans/handoffs/261102-1515-tap-1-dbp-v3-sua-noi-dung.md` |
| v4 sửa nội dung + P6 QC | 02/11 15:44 | 02/11 17:45 | 121 phút (2 sub-agent bình luận + tra nguồn 17 phút, sửa lời 19 câu + sổ + chữ, reviewer Opus, TTS 19 câu, dựng lại 92 cảnh 57 phút, dấu kênh logo mới 4 góc, 1 lượt STT, ghép 2 lần) | `<output>±102-dbp-v3inal\EP001-dien-bien-phu-1954.mp4` 17:48, −14,2 LUFS, đỉnh −1,4 dBTP, STT 98,05 %; DỪNG chờ user xem |
| Duyệt v4 | 02/11 18:48 | | | user: "Tổng duyệt ổn rồi"; tập 1 hoàn thiện; bản chốt ở `Final/`; nâng cấp QC; tiếp theo SEO & AEO |
