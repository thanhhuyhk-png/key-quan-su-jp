# Cổng quét, khai báo nội dung tổng hợp, cài đặt tải lên

## Brief cho sub-agent viết chữ
Mỗi prompt giao việc viết chữ cho người xem (tiêu đề, mô tả, thẻ, chữ bìa, bình luận ghim, dịch) gồm:
1. Việc và tệp được ghi (một tệp nháp trong `tap/<tập>/ke-hoach/`).
2. Tệp được đọc: sổ số liệu, kịch bản chốt, sổ tài sản, mốc chương, `kenh/mo-ta-chuan.md`, `kenh/thumbnail-chuan.md`, `kenh/cach-noi-da-chot.tsv`, `ho-so-kenh/ho-so.md`, `ho-so-kenh/luat-noi-dung.md`.
3. **Nguyên khối mục C** của `kenh/bo-loc-chinh-sach-yt.md` (mở tệp, chép từ dòng «BỘ LỌC CHÍNH SÁCH YOUTUBE» đến hết khối), không rút gọn.
4. Luật cứng sử Việt từ `CLAUDE.md` (lãnh tụ, bản đồ Biển Đông, không ảnh AI, hệ từ, xưng hô có chức vụ khi ấy).
5. «Dữ kiện chỉ lấy từ sổ số liệu và kịch bản; không thêm số, ngày, tên đơn vị nào ngoài đó.»
6. Kết báo cáo bằng danh sách chỗ có từ thuộc dòng 2–5 của khối luật và lý do giữ, xác nhận tiêu đề và bìa sạch.

Người phản biện nhận cùng khối luật. Claude rà tay dữ kiện theo sổ trước khi chạy máy.

## Cổng máy (mỗi lần sửa chữ chạy lại)
| Lệnh | Đạt khi |
|---|---|
| `python -I tools/loc-chinh-sach/quet.py --tieu-de Final/EPxxx-postpack.md` | mã thoát 0, 0 CHẶN |
| `python -I tools/loc-chinh-sach/quet.py --vi-tri metadata Final/EPxxx-postpack.md` | như trên |
| `python -I tools/loc-chinh-sach/quet.py Final/*.srt` | 0 CHẶN |
| `python -I -X utf8 tools/lichsu/kiem-da-chot.py Final/EPxxx-postpack.md` | 0 chỗ phạm |
Mỗi CẢNH BÁO có người xem ngữ cảnh; giữ thì ghi lý do vào `checks.md` của tập. Chữ trên bìa cũng đưa vào postpack (khối Thumbnail) để máy quét thấy.

## Khai báo «Altered or synthetic content» (nội dung tổng hợp)
YouTube hỏi lúc tải lên. Khai **trung thực**; khai sai hỏng điểm tin cậy kênh.
- **Có:** có cảnh, ảnh, âm thanh do máy tạo hoặc sửa mà trông/nghe như thật (người thật nói điều họ không nói, sự kiện thật vẽ lại trông như quay thật, giọng giả một người cụ thể).
- **Không:** đồ hoạ minh hoạ ghi rõ «minh hoạ» trên hình, bản đồ, giọng người dẫn tổng hợp không giả người thật, nhạc nền không lời. Chủ kênh quyết ở mục này; ghi lý do một dòng vào postpack (tập mẫu: chọn Không, vì 3D và bản đồ đều ghi «minh hoạ», giọng dẫn không giả người thật).
- Hình hay giọng mô phỏng người thật (nhất là lãnh tụ Việt Nam) là việc luật cứng cấm làm; nếu phim có thì sai từ khâu trước, quay lại sửa, không chọn «Không» để qua.
- Dù khai Không, mô tả vẫn ghi: nhạc AI nêu nhà cung cấp, giọng dẫn AI nêu nhà cung cấp, cảnh dựng lại ghi rõ.

## Cài đặt khi tải lên (ghi vào postpack)
- Danh mục: Giáo dục (theo `kenh/seo-kenh.md`; đánh giá lại sau vài tập).
- Ngôn ngữ video, tiêu đề, mô tả: ngôn ngữ chính của kênh (`ho-so.md`).
- Phụ đề: từng tệp `.srt` kèm ngôn ngữ.
- Màn hình cuối và thẻ: trỏ tập cùng loạt; chưa có tập khác thì để trống.
- Bảng tự đánh giá quảng cáo: trả lời trung thực. Mục AI/tổng hợp: như trên.
- Thẻ mặc định kênh chỉ vài thẻ chung; 20–25 thẻ riêng của tập đã nằm ở khối Thẻ.

## DỪNG
Trình user: đường dẫn postpack, ba bìa (mở cỡ thật và cỡ điện thoại), tiêu đề chính và bản thử, các CẢNH BÁO còn giữ. Không tải lên, không đặt lịch đăng khi user chưa duyệt.
