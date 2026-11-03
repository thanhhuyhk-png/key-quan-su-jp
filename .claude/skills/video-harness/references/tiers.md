# Chọn mức kiểm soát

Mức là công cụ để cân thời gian với rủi ro. Chọn bằng cách hỏi, không bằng cách đếm. Mỗi mức là **gói mặc định**: được thêm hoặc bớt từng cổng lẻ nếu ghi lý do. Ví dụ clip 10 giây cho khách có thể là "Chuẩn, thêm kiểm bản quyền, bỏ storyboard". Phim 5 phút xem nội bộ có thể là "Nhanh".

## Các câu hỏi quyết định

- **Ai sẽ xem?** Chỉ bạn, hay khán giả, hay khách, hay thương hiệu của người khác?
- **Làm lại có rẻ không?** Tốn bao nhiêu credit (giọng, ảnh, nhạc), bao lâu render? "Đáng kể" nghĩa là vượt mức chi tối đa ghi trong `brief.md`; chưa ghi thì coi mọi bước trả phí là đáng hỏi.
- **Đăng rồi có rút lại được không?** Đăng công khai, gửi khách, chạy quảng cáo thì khó rút.
- **Có nội dung nhạy cảm không?** Người thật, thương hiệu, số liệu, y tế, tài chính, pháp lý.
- **Loại video này đã làm thành công chưa?** Lần đầu với một gói hay phong cách thì rủi ro cao hơn.
- **Có kéo dài qua nhiều phiên hoặc nhiều tập không?** Thì cần trạng thái ghi ra file.

## Ba mức

### Nhanh
Hợp: thử nghiệm, dùng nội bộ, làm lại rẻ, gần như không tốn credit.
- Brief một câu trong chat.
- Một check chính: `python tools/kit/kit.py kiem <video>` (kích thước, độ dài, âm lượng, khung đứng) và soi ảnh tổng hợp các khung. **Phần tiếng chưa có ai nghe**: model không nghe được, nên người đang xem trong chat nghe và là cổng duyệt.
- Không file trạng thái, không reviewer riêng.
- Vẫn bắt buộc: hỏi trước khi đăng, và hỏi trước mọi bước trả phí nếu brief chưa ghi mức chi tối đa.

### Chuẩn
Hợp: video thật sẽ đăng, một phiên, chi phí vừa.
- Brief ngắn (khoảng một nửa trang) và tiêu chí ba loại (đo được, cảm nhận được, ràng buộc) trong một file `brief.md`.
- Thử rẻ trước: mẫu giọng ngắn, một cảnh, rồi mới cả video.
- QC tự động + soi bằng mắt/tai.
- Một lượt **reviewer độc lập** trước khi giao.
- Người duyệt bản cuối.

### Sản xuất
Hợp: phim tài liệu dài, loạt nhiều tập, video cho khách hoặc thương hiệu, chi phí đáng kể, nhiều phiên.
- Mọi thứ của mức Chuẩn, thêm:
- Duyệt **kịch bản và storyboard** trước khi tốn credit tạo ảnh và giọng.
- **Mẫu đại diện**: làm một tập hoặc một cảnh điển hình, duyệt xong mới làm hàng loạt.
- QC theo từng giai đoạn (lát), không dồn đến cuối.
- Sổ lỗi có mức độ; `progress.md` để chuyển chat.
- Reviewer độc lập sau mỗi giai đoạn lớn.

## Dấu hiệu nâng mức giữa chừng

- Ước lượng chi phí lớn hơn dự kiến, hoặc render một lần quá lâu.
- Lỗi mức S1 xuất hiện, hoặc một lỗi qua ba lần sửa chưa hết.
- Người xem hoá ra là khách hoặc công chúng, chứ không phải nội bộ.
- Việc kéo sang phiên thứ hai.
- Phát hiện vấn đề bản quyền hoặc quyền hình ảnh.

## Hạ mức

Được phép khi có lý do: ví dụ lát này chỉ là thử nghiệm bỏ đi, hoặc lỗi này đã có quy tắc chặn sẵn. Ghi lý do một dòng. Không hạ mức chỉ vì mệt hoặc vội, vì đó đúng lúc lỗi lọt qua.
