# Dựng Shorts (lệnh đã chạy thật ở tập mẫu)

Hai script của tập mẫu nằm ở `san-xuat/` của tập mẫu nằm ở `mau/dien-bien-phu-1954/` (ở repo của chủ kit là `tap/EP001-dien-bien-phu-1954/`): `shorts.py` (cắt, ghép, dựng khung, cháy phụ đề, trộn, master) và `ve-bia-shorts.py` (bìa 9:16). Khuôn HTML khung dọc: `template/shorts-doc.html`. Tập mới KHÔNG có sẵn hai script này: **bước đầu tiên là chép chúng sang `tap/<EPxxx-slug>/san-xuat/`**, rồi sửa bảng dữ liệu đầu tệp theo tập mới, không sửa logic trừ khi có lý do.

## Cái phải sửa khi chép sang tập mới
- Hằng đường dẫn đầu `shorts.py`: `FINAL` (thư mục `Final/` của tập), `V4`/`SRT` (tên video và `.vi.srt` của tập), `MASTER` và `GIONG` (bản master và stem giọng trong `<output>/<ngày>-<tập>/am/`), `RA` (thư mục ra tạm ở `<output>`). Đừng ghi đường dẫn máy cứng: dùng `duong("output")` từ `tools/cau_hinh.py` như bản mẫu.
- Bảng `SHORTS`: mỗi mã `Snn` gồm `h1`, `h2` (hai dòng chữ dải trên) và `doan` (danh sách đoạn; mỗi đoạn là các số khối `.vi.srt` liền nhau, ví dụ `[110, 111]`).
- Bảng `CHU_SO`: câu có số đọc bằng chữ thì ghi tay bản chữ số (đối chiếu sổ số liệu), không chuyển tự động.
- Hằng `FPS=24`, `NOI=0.2` (kéo mỗi đoạn thêm 0,2 s vào khoảng lặng rồi crossfade), `KET=1.8` (thẻ kết), `LUFS=-14`.
- Bảng `KHUNG` trong `ve-bia-shorts.py`: mã Shorts → (Shorts lấy khung, giây, ghi chú khung). Chỉ lấy khung ảnh hoặc phim tư liệu thật.

## Lệnh
```
python -I -X utf8 tap/<tập>/san-xuat/shorts.py S1 --kieu doc|vuong|ca-hai
python -I -X utf8 tap/<tập>/san-xuat/ve-bia-shorts.py
```
`--kieu ca-hai` (mặc định) dựng cả dọc 1080×1920 và vuông 1080×1080. Ra `<output>/<ngày>-shorts/<S>-<kiểu>.mp4`; chép bản chọn vào `Final/shorts/EPxxx-Snn-<slug>/EPxxx-Snn.mp4`. Bìa ra thẳng `Final/shorts/EPxxx-Snn-<slug>/EPxxx-Snn-bia.jpg`.

## Nguyên tắc dựng (đã chạy)
- **Hình giữ trọn khung 16:9** của phim đặt giữa nền dọc (khung 1080×608 ở y = 592–1200), nên nhãn góc, dòng nguồn và Hoàng Sa, Trường Sa trên bản đồ còn nguyên. Ảnh lãnh tụ chỉ được thu phóng, không cắt xén (và tránh dùng đoạn có lãnh tụ).
- **Nền** theo hồ sơ kênh (màu, thẻ địa danh · tháng/năm, câu hỏi chữ vàng cùng kiểu chữ ảnh bìa). Đáy ~420 px chừa cho nút và tiêu đề Shorts; lề phải chừa 120 px.
- **Phụ đề cháy** ngay dưới khung, ≤ 2 dòng, lấy nguyên câu từ `.vi.srt`.
- **Âm:** giọng và tiếng động cắt cùng đoạn với hình từ stem; nhạc nối bằng crossfade ~0,4 s; chuẩn về −14 LUFS, chặn đỉnh; đo ebur128 trên mp4.
- **Thẻ kết** `KET` giây: giữ khung giữa câu cuối (khung cuối đoạn có thể đã chuyển cảnh tối), tối đi, chữ «Xem trọn phim … ở liên kết phía trên», không giọng. Liên kết thật gắn bằng mục «Video liên quan» của Shorts trong Studio.
- Không đọc giọng mới, không sinh hình mới: không tốn tiền giọng, nhạc, ảnh.

## Bìa 9:16
Nền dọc của Shorts + một khung tư liệu thật lấy từ chính video Shorts. Trích khung ra ảnh trước rồi mới ghép (ghép thẳng nền với video đã tua có lúc ra ô đen). Shorts toàn đồ hoạ 3D không có khung tư liệu thì mượn một khung phim thật của Shorts khác cùng tập. Không ảnh AI, không ảnh lãnh tụ. Quét chữ bìa bằng `quet.py --tieu-de`.

## Việc đặt tên và nộp
- Thư mục `Final/shorts/EPxxx-Snn-<slug>/`: `EPxxx-Snn.mp4`, `EPxxx-Snn-bia.jpg`, `EPxxx-Snn-seo.md`. Slug không dấu, ngắn, nói đúng nội dung.
- `Final/shorts/EPxxx-shorts-cach-dang.md`: cùng một tệp mp4 cho cả 3 nền tảng (1080×1920, 24 fps, −14 LUFS); YouTube: tải bìa lên mục ảnh thu nhỏ, «Video liên quan» chọn phim dài, danh mục Giáo dục, mục nội dung tổng hợp theo cách khai của phim dài; TikTok: bìa làm ảnh bìa, liên kết phim dài ở trang cá nhân; Facebook: liên kết phim dài dán vào bình luận đầu; nhãn AI trên TikTok, Facebook do chủ kênh quyết khi đăng; thứ tự đăng gợi ý và mỗi ngày một video.
