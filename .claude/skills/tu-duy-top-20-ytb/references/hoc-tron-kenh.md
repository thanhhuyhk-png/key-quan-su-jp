# Học trọn một kênh (TOP 1 bắt buộc, TOP 2–5 nên làm)

Mục tiêu: trả lời «vì sao kênh này thắng, phần nào mình làm lại được với nguồn lực của mình». Học **lý do**, không chép câu chữ, giọng, bố cục, nhân vật.

## 1. Bộ số chuẩn (chạy `do_kenh.py kenh`)
Trung vị, trung vị ÷ sub, số video > 2×, phân tán, sub mỗi video, sub mỗi ngày (cả hai cách tính tuổi), hệ số vượt trội từng video, so với 2–3 kênh cùng nhóm. Đường tăng sub nếu có (các lần đo trước ở tab 9, hoặc vidIQ `channel_performance_trends`).

## 2. Video tốt và kém
- Xếp video theo **view chuẩn hoá tuổi** (view sau 7 hoặc 30 ngày, hoặc view mỗi ngày khi thiếu), lấy 20 % đầu và 20 % cuối.
- Với từng nhóm ghi: đề tài và tiền đề (premise), loại chuyện, tiêu đề (số chữ, có số, tên hay câu hỏi, kết quả hay bỏ lửng), ảnh bìa (mở ảnh: người, chữ, màu, vật), độ dài, ngày đăng và **tuần thứ mấy của kênh**, 2–3 câu đầu và giây nêu lời hứa.
- **Đối chứng nhóm với nhóm** (≥ 5 video vượt trội so với ≥ 5 video thường cùng kênh, cùng giai đoạn; ít hơn thì ghi n): so trên 6 biến — chủ đề con, tiêu đề, ảnh bìa, 30 giây mở, góc kể, độ dài và mốc đăng. Kết luận chỉ là **giả thuyết** (còn phân phối, thời điểm, độ nóng sự kiện); kiểm bằng nhiều nhóm và thử trên kênh mình trước khi làm theo.
- **Kiểm xem văn phong có quyết định không**: đo văn phong (độ dài câu trung vị, tốc độ, cách mở, cách kết) ở hai nhóm. Ở 5 kênh đã đo, văn phong của video hit và flop gần như giống hệt, nên hit đến từ tiền đề, tiêu đề, ảnh bìa (và mốc đăng ở kênh mới). Nếu kênh bạn đang học cho kết quả khác thì ghi lại, đó là phát hiện.

## 3. Cấu trúc theo % thời lượng
Trên 3–5 video có phụ đề, đánh dấu: mở (giây nêu lời hứa), gài luật hoặc bí ẩn, leo thang (bao nhiêu phút một bậc), cú lật, cao trào, dư âm (% cuối), lời mời bình luận. Đỉnh «được phát lại nhiều nhất» (`scripts/heatmap.py`): đỉnh rơi vào % nào, nội dung ở đó là gì (khớp với phụ đề). Heatmap là giá trị tương đối, không phải tỉ lệ giữ chân; video ít lượt xem lại thì không có.

## 4. Hình, giọng, chi phí
Người thật hay giọng máy (bằng chứng: bình luận, khoảng lặng tuyệt đối giữa câu), âm tiết mỗi phút, số cảnh mỗi phút (đếm 2 phút giữa rồi nhân đôi), nhạc, độ to. Ước giờ và tiền mỗi video, từ đó tính với nguồn lực của mình làm được mấy video mỗi tuần.

## 5. Bình luận
Theo `tieu-chi-va-cong-thuc.md` mục 6, cộng đếm nhóm cảm xúc (khóc, xúc động, sợ, cười, nhận ra mình, kể chuyện nhà mình) theo từng video. Tách loại chuyện (ví dụ chuyện ma kéo view, chuyện tình thân giữ người: like % và bình luận cao hơn, view thấp hơn).

## 6. Tuổi khán giả
Theo `do-tuoi-khan-gia.md`, ghi mức tin.

## 7. Bảng học
| Hạng mục | Làm theo (bằng chứng, n) | Không làm theo (lý do) | Thử có kiểm soát (giả thuyết, điều kiện dừng) |
|---|---|---|---|
Mỗi dòng ghi thị trường và nhóm tuổi của bằng chứng.

## 8. Giới hạn
Liệt kê: n của từng phép đo, phần chưa lấy được (phụ đề, bình luận, ảnh), giả định tự đặt, chi phí đã dùng.
