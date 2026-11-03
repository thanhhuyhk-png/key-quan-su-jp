# Brief giao người viết P2b: hook và câu nối (sub-agent Sonnet), 01/11/2026

Bạn là người viết lời cho phim tài liệu YouTube 15–17 phút **Điện Biên Phủ 1954** của kênh Goha Studio. Kênh làm lịch sử và quân sự, khán giả nam 35–60 tuổi, bám sử chính thống Việt Nam. Kịch bản v3 đã được duyệt. Việc của bạn là làm cho **phần mở hấp dẫn hơn** và **câu mở, câu treo của từng chương sắc hơn**, theo chuẩn phim tài liệu của Truyền hình Quốc phòng Việt Nam (QPVN): lời trang trọng, chắc, thuật ngữ quân sự chuẩn (đại đoàn, trung đoàn, cứ điểm, phân khu, trận địa, giao thông hào), mỗi câu có một chi tiết cụ thể, không sáo rỗng, không giật gân. Làm việc và báo cáo bằng tiếng Việt. Thư mục: `<gốc repo kênh>` (múi giờ Asia/Bangkok).

## Được đọc (chỉ những file này)
1. `tap/EP001-dien-bien-phu-1954/ke-hoach/kich-ban-v3.md`: kịch bản đã duyệt, có mã sổ sau mỗi câu.
2. `tap/EP001-dien-bien-phu-1954/ke-hoach/loi-doc-v3.txt`: lời đọc thuần (số viết bằng chữ).
3. `tap/EP001-dien-bien-phu-1954/ke-hoach/so-so-lieu.csv`: nguồn sự thật DUY NHẤT. Đọc cột `stt`, `gia_tri`, `muc_dung`, `cach_noi`. Dòng `KHÔNG DÙNG` không được đưa lên; khi `cach_noi` có câu chữ cụ thể thì nói đúng như vậy.

**Không được đọc, không được tìm:** kịch bản, phụ đề, transcript, video của kênh khác; mọi file trong `kenh/nghien-cuu-top20/`, ổ `H:`, thư mục `tap/dien-bien-phu-mau/`. Không tra web. Thiếu dữ kiện thì ghi `[CẦN SỔ: …]`, không bịa.

## Việc 1: bốn phương án phần Mở
Viết **4 phương án** thay cho phần "Mở" của v3 (từ câu đầu đến hết lời hứa "ba quyết định"). Mỗi phương án dùng một **cơ chế hook** khác nhau (được chồng hai cơ chế):
- M1 Giấu thông tin: cho thấy một chi tiết lạ, chưa nói nó là gì ("Cái gì vậy?").
- M2 Khoe kết quả trước: mở bằng kết cục rồi quay lại ("Sao lại ra nông nỗi này?").
- M3 Lật kỳ vọng: một niềm tin chắc chắn bị lật ("Ủa?").
- M4 Khán giả biết trước: người xem biết điều mà nhân vật trong sử chưa biết ("Bao giờ họ nhận ra?").
- M5 Áp lực, leo thang: mục tiêu và hạn chót ("Có kịp không?").

Nguyên tắc chọn: chọn **câu hỏi** muốn người xem mang theo suốt 16 phút trước (phải dẫn đúng vào câu hỏi trung tâm: vì sao hai niềm tin của Bộ chỉ huy Pháp lại thành nguyên nhân thua), rồi mới chọn cơ chế và cách trình bày. Hook gieo gì thì phim phải gặt đúng cái đó (chỉ ra phim gặt ở chương nào).

Ràng buộc đo được cho mỗi phương án:
- Câu đầu tiên vào thẳng biến cố, không chào, không giới thiệu kênh, không "Chào mừng", không "Hôm nay chúng ta".
- Trong 15 giây đầu (khoảng 40 tiếng lời đọc đầu tiên) có ngày, giờ hoặc nơi cụ thể.
- Câu hỏi trung tâm xuất hiện trước tiếng thứ 125 của lời đọc (≈ 45 giây ở 170 tiếng/phút).
- Toàn phần Mở 170–240 tiếng lời đọc (đếm trên bản số viết bằng chữ).
- Giữ lời hứa "ba quyết định, một của Pháp, hai của ta" và ẩn dụ "cái bẫy tự giăng".
- Mọi dữ kiện có mã sổ sau câu. Chất liệu mạnh có sẵn trong sổ (gợi ý, không bắt buộc): lời hứa của Trung tá Pi-rốt về pháo binh và số viên đạn pháo Pháp bắn mà không khống chế được pháo ta (A6a, A6b); "pháo đài bất khả xâm phạm" (A4c); 17 giờ 30 phút 7/5 tướng Đờ Cát-xtơ bị bắt (B9b, M15); 27/3 lần cuối máy bay Pháp hạ cánh (B5a); đường kéo pháo bằng tay (M10); Tô Vĩnh Diện (M11); dân công, xe đạp thồ, gạo (M9); ngày 26/1 đổi cách đánh, kéo pháo ra (M5). Cái chết của Pi-rốt (A6c) là KHÔNG DÙNG.
- Không dùng góc của kênh khác: "sai lầm không nằm ở thung lũng"; "cuộc đấu trí giữa Đại tướng và Na-va" làm trục; "đêm đảo ngược kế hoạch", "cãi Bộ Chính trị"; ẩn dụ "cối xay thịt". Tránh cụm sáo: "đồng loạt khai hỏa", "mưa bom bão đạn", "thần tốc", "huyền thoại", "chấn động", "lá cờ được cắm trên nóc hầm".

Mỗi phương án trình bày đúng mẫu:
```
### Phương án H<n> · cơ chế M<x>(+M<y>) · câu hỏi cài vào đầu người xem: "…"
Kịch bản (mỗi câu một gạch đầu dòng, mã sổ sau câu; sau mỗi đoạn có dòng "Hình:" và "Chữ trên hình:")
Lời đọc thuần (số viết bằng chữ, mỗi câu một dòng)
Đo: tổng tiếng = …; câu hỏi trung tâm bắt đầu ở tiếng thứ …; ngày/giờ/nơi đầu tiên ở tiếng thứ …
Gặt ở: chương … (câu nào)
```
Đếm tiếng bằng máy (vd `python -I -c` tách theo khoảng trắng trên lời đọc thuần), không ước lượng.

## Việc 2: câu mở và câu treo của từng chương
Với Chương 1–6 và phần Kết của v3: đề xuất câu mở (câu hỏi nhỏ) và câu treo cuối chương **mới** nếu câu hiện có yếu (chung chung, lặp ý, không tạo câu hỏi kế tiếp), theo mẫu:
```
Chương n · câu mở | cũ: "…" | mới: "…" | lý do (một dòng)
Chương n · câu treo | cũ: "…" | mới: "…" | lý do
```
Câu nào đã tốt thì ghi "giữ" và lý do. Không đổi dữ kiện, không thêm dữ kiện ngoài sổ. Mỗi câu mới phải khác về câu chữ so với chính v3 ở chỗ khác (không lặp ý trong phim).

## Luật cứng của dự án
- Lời Chủ tịch Hồ Chí Minh và Đại tướng Võ Nguyên Giáp: **không đưa vào lời đọc**; chỉ ghi `[CHỮ TRÊN HÌNH: "<nguyên văn từ sổ>" · nguồn]`. Lời người thật khác (sĩ quan Pháp, chiến sĩ, hồi ký) giọng dẫn được kể lại nếu nói rõ ai nói và nguồn.
- Phân biệt thực dân, quân viễn chinh, Bộ chỉ huy Pháp với nhân dân Pháp; không nêu Trung Quốc.
- Hy sinh: một câu nêu việc làm, không tả thương tích.
- Ngôi thứ ba, giọng kể điềm tĩnh, chắc; không xưng nhà sử học.

## Khối luật bộ lọc chính sách (chép nguyên văn từ `kenh/bo-loc-chinh-sach-yt.md` mục C)
```text
BỘ LỌC CHÍNH SÁCH YOUTUBE: BẮT BUỘC (Goha Studio, kênh tài liệu lịch sử, quân sự)
Mục tiêu: video đủ điều kiện quảng cáo đầy đủ (biểu tượng xanh). Vi phạm bất kỳ dòng nào dưới đây thì viết lại.
1. Không chửi tục, kể cả từ nhẹ, kể cả viết tắt hoặc che chữ (đm, vl, "C.H.Ế.T"…).
2. Không từ miệt thị dân tộc, vùng miền, phe phái (khựa, chệt, ba tàu, nhật lùn, mọi rợ, gook, parky, 3 que, bò đỏ, dư luận viên…). Không "thằng/bọn/lũ" đi với tên một dân tộc. Dùng "thực dân Pháp", "quân viễn chinh", "quân xâm lược", không dùng "bọn Tây".
3. Hệ từ: "kháng chiến chống Mỹ, cứu nước"; "chính quyền Sài Gòn", "quân đội Sài Gòn". "Ngụy", "Việt cộng", "VNCH" chỉ được nằm trong câu trích có nguồn. Không viết "Chiến tranh Việt Nam" trong lời, tiêu đề, mô tả (chỉ được trong thẻ). Không nêu "Trung Quốc"; thời cổ trung đại gọi tên triều đại (Nam Hán, Tống, Nguyên Mông, Minh, Thanh).
4. Bạo lực: kể kết quả, con số có nguồn, ý nghĩa quân sự. KHÔNG tả vết thương, máu, xác, cách giết, cảnh hành quyết. Thảm kịch nêu trong 1 câu trung tính có nguồn, không khai thác cảm xúc ghê rợn.
5. Tiêu đề, chữ ảnh bìa, 2 dòng đầu mô tả: cấm các chữ máu me, đẫm máu, chặt đầu, xác chết, thi thể, tàn sát, thảm sát, kinh hoàng, rùng rợn, "không che", "không kiểm duyệt", "uncensored", 18+. Cấm giật tít kiểu "tái mặt", "câm nín", "sốc", "chấn động". Dùng câu hỏi "Vì sao…?", "Toàn cảnh…", nghịch lý, và PHẢI trả lời được trong phim.
6. Không nội dung tình dục; xâm hại tình dục, tự sát chỉ được nhắc một câu, không mô tả.
7. Quốc xã, Khmer Đỏ, IS…: kể trung tính có ngữ cảnh, không khen, không tôn vinh, không trích khẩu hiệu tuyên truyền mà không có lời bình.
8. Vũ khí: được giải thích vai trò, cấu tạo, cách dùng trong trận; cấm hướng dẫn chế tạo, độ chế, chế bom, chất nổ.
9. Không phủ nhận thảm kịch; không đề tài chiến sự đang diễn ra; không dùng từ khoá thời sự để kéo view.
10. Người dẫn kể ngôi thứ ba, không xưng là nhà sử học, chuyên gia; không giả lời người thật; lời trích ghi rõ ai nói, nguồn.
11. Mỗi tập phải có câu hỏi trung tâm, chương và chi tiết riêng; không dùng đoạn văn mẫu lặp giữa các tập (chính sách "nội dung không chân thực").
Cuối bài, tự liệt kê: (a) mọi chỗ có từ thuộc dòng 2–5 và lý do giữ lại (chỉ được giữ khi là câu trích có nguồn); (b) xác nhận tiêu đề, bìa sạch theo dòng 5.
```

## Đầu ra
Ghi toàn bộ vào `tap/EP001-dien-bien-phu-1954/ke-hoach/hook-p2b.md` (tạo mới). Không sửa file nào khác. Cuối file, làm phần tự liệt kê theo yêu cầu cuối khối luật bộ lọc.
Trả lời ngắn: đường dẫn file, bảng 4 phương án (cơ chế, tổng tiếng, vị trí câu hỏi trung tâm), số câu chương đề xuất đổi, rồi
`Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT` kèm tên model thật.
