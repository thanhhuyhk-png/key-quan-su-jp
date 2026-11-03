# Chuẩn đạo diễn cho phim sử dựng bằng code

Rút từ bản thử 60 giây v2 Điện Biên Phủ (30/10/2026, mẫu: `tap/dien-bien-phu-mau/san-xuat/ban-thu-3d/`) và phương pháp của Baptiste Kelano ("đo, đừng chép"). Áp cho mọi tập có đồ hoạ 3D, bản đồ, thẻ chữ. Luật cứng sử ở `README.md` vẫn đứng trên chuẩn này.

## 1. Thứ tự làm
1. **Mốc chữ trước, hình sau.** Lấy mốc từng chữ của đường giọng đã chốt (Deepgram trên đường giọng riêng). Mọi cú cắt, mọi sự kiện hình gắn vào một chữ hoặc một khoảng lặng có tên.
2. **Phân cảnh là dữ liệu.** Mỗi cảnh một dòng: khung đầu–cuối (24 fps), lời, cỡ và góc máy, ý đồ, tiếng. Viết trước khi dựng, sửa khi đổi ý. Mẫu: `ban-thu-3d/phan-canh.md`.
3. **Kiểm dữ kiện chi phối hình** trước khi chọn ánh sáng: pha trăng đêm đó (Điện Biên Phủ 1/2/1954 trăng 4%: không vẽ trăng), giờ, mùa, thời tiết có nguồn hay không. Không có nguồn thì không phô ra.
4. **Storyboard ảnh tĩnh mọi cảnh** (`node tools/kit/dung-trang.mjs <trang.html> --stills <giây,...>`), soi như người xem, liệt kê lỗi, sửa rồi mới render video. Mỗi lỗi sửa tối đa 3 lần; hết 3 lần thì đổi cách hoặc chấp nhận có ghi chú.
5. Render, trộn, `deliver`, `check`, đo lại đỉnh thật, soi khung thành phẩm ở mọi điểm nhấn.

## 2. Hình
- Hai cảnh liền nhau không cùng cỡ và góc. Đoạn hành động khoảng 25–35 cú cắt mỗi phút; đoạn tưởng niệm giữ lâu.
- Mỗi đoạn có ít nhất một cận đặc tả chủ thể vật lý (dây, nan hoa, bánh xe). Không quay cận thứ mà kho vẽ còn yếu (bàn tay, mặt): đổi sang cách khác nói cùng ý.
- Ánh sáng có nguồn: trăng, sao, mặt trời thấp, lửa có thật. Không đèn ở nơi lịch sử không có đèn. Ánh sáng mang nghĩa tôn vinh là lớp phủ toàn khung nhẹ, không phải nguồn sáng trong cảnh.
- Vùng tối đủ sâu để chỗ sáng rực lên, nhưng mỗi khung phải đọc được chủ thể trong một giây.
- **Hình bám lời theo nấc:** lời nói "đứt" thì hình có dấu hiệu đứt; sự kiện lớn nhất đặt ở khoảng lặng ngay sau câu.
- Chậm hình bằng co giãn đồng hồ vật lý (`coGian`), không bằng đổi tốc độ video, để chuyển động liên tục qua mọi cú cắt.

## 3. Người thật, anh hùng, lãnh tụ
- Anh hùng có thật: bóng sẫm không mặt, không chân dung; khoảnh khắc hy sinh cắt trước lúc chạm, sau đó không vẽ lại người; máy rời đi (lên trời, ra xa). Tên và đơn vị hiện bằng thẻ chữ đúng nguồn.
- Lãnh tụ: không dựng 3D, không AI; chỉ ảnh thật quốc gia nguyên gốc có ghi nguồn.

## 4. Âm thanh
- Tiếng lớn (đứt, nổ, va) vào khoảng lặng giữa câu; tiếng nhỏ, giòn được nằm trong chữ. Đo: đỉnh tiếng nhấn cao hơn nền 15–20 dB.
- Mỗi phản ứng một tiếng (bước chân, dây căng, gỗ, bánh, xích). Tiếng nền đúng chỗ (dế rừng đêm, gió núi).
- Nhạc lùi khi có khoảnh khắc thiêng (hạ còn ~25%), trở lại trước câu mới.
- Mọi tiếng mới kiểm bằng Earshot (`match`/`rank`) trước khi dùng; ghi vào `kit/ASSETS.tsv` kèm mô tả, giấy phép, kết quả Earshot. Tiếng kho BDE chỉ dùng bản thử (giấy phép chưa rõ).
- Kiểm lời bằng STT trên **bản trộn** (không chỉ trên giọng riêng).

## 5. Lời
- Sửa một câu: đọc lại câu trước–câu đó–câu sau trong một lần gọi, cắt câu giữa ở đáy năng lượng, gọt −60 dB chừa đuôi 0,2 s, cân mức theo câu cũ cùng vị trí.
