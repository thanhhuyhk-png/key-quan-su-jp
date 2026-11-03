# Hồ sơ kênh: <tên kênh>

- Trạng thái: `<nháp | đã duyệt (ngày)>` (K2 chỉ đổi thành «đã duyệt» ở bước 11, sau khi năm tệp `kenh/*.md` xong; bộ định tuyến đọc dòng này)

> Mẫu trống. Chép thành `ho-so-kenh/ho-so.md`, thay mọi `<...>`, xoá dòng chú thích bắt đầu bằng «Ghi chú:». Skill khác đọc đúng tên mục dưới đây, đừng đổi tên mục.

## 1. Kênh
- Tên kênh: `<tên>` · handle: `<@handle hoặc "chưa có">` (kiểm bằng cách tra thử trên YouTube; tên trùng kênh lớn thì đổi)
- Ngách: `<một câu: đề tài + góc kể>`
- Ngôn ngữ, thị trường: `<vd tiếng Anh, Mỹ-Anh-Úc>`
- Khán giả: `<giới, tuổi chính, mối quan tâm>`
- Độ dài tập: `<vd 12–20 phút, mục tiêu 15–17>` · nhịp đăng: `<số tập mỗi tuần>`
- Mức chạy: `<Đầy đủ | Tiết kiệm | Miễn phí>` (lấy từ báo cáo K1)
- Ghi chú: ngôn ngữ quyết định giọng, bộ lọc chữ, nguồn tư liệu và cách đặt tiêu đề.

## 2. Mẫu để bám
- Model Link: `<tên kênh, @handle>` · lý do chọn: `<2 dòng, có số>`
- Điều học: `<cấu trúc, độ dài, nhịp>` · Điều cố ý làm khác: `<...>`
- Sheet top 20: `<link Google Sheet đã Tạo bản sao của bạn>` · ngày đo: `<ngày/tháng/năm>`

## 3. Giọng người dẫn
- Nhà cung cấp: `<ElevenLabs | VieNeu | Kokoro | khác>`
- `voice_id`: `<mã>` (**phải khác `3VnrjnYrskPMDsapTr8X`**) · tên giọng: `<tên>`
- Model: `<vd eleven_v4>` · ngôn ngữ (`language_code`): `<vi | en | ...>`
- Thẻ đầu bài: `<vd [fast-paced] hoặc "không dùng">`
- Cách đọc: `<đọc cả bài một lần rồi cắt câu | từng đoạn ≤ ... ký tự>`
- Quy tắc sửa một câu: `<vd đọc lại câu trước–câu đó–câu sau trong một lần gọi rồi cắt lấy câu giữa>`
- Ghi chú: model nào bỏ qua `speed` thì ghi rõ, và không tăng tốc bằng xử lý sau nếu giọng bị méo.
- Chi phí đã báo và người dùng đã đồng ý: `<ngày, số ký tự>`

## 4. Thương hiệu
- Bảng màu (hex, vai): nền `<#......>` · nhấn `<#......>` · chữ chính `<#......>` · chữ phụ `<#......>` · thẻ cảnh báo `<#......>`
- Kết quả lệnh kiểm màu khác kênh mẫu: `<ĐẠT, ngày>`
- Font tiêu đề: `<tên, giấy phép OFL hoặc tương đương>` · font nội dung: `<tên>` (phải có dấu tiếng Việt nếu kênh tiếng Việt)
- Tagline: `<...>`
- Tệp, tính từ gốc repo, trong thư mục hướng đã chọn `kenh/thuong-hieu/<hướng: vach | tron | gach>/`: logo `svg/` và `png/` (cùng bộ, nền trong) · logo ảnh bìa `png/logo-anh-bia.png` · ảnh đại diện, banner, dấu kênh trong phim `youtube/` (`anh-dai-dien-800.png`, `banner-2560x1440.jpg`, `dau-kenh-150.png`)
- Cấm riêng của thương hiệu: `<vd không đặt logo lên nền cùng màu>`

## 5. Luật nội dung
- Luật riêng của ngách: `ho-so-kenh/luat-noi-dung.md`
- Bộ lọc chính sách YouTube: `kenh/bo-loc-chinh-sach-yt.md`, máy quét `tools/loc-chinh-sach/quet.py`
- Tệp kênh dùng cho P2, P7, P8: `kenh/khung-kenh.md`, `kenh/lich-noi-dung.md`, `kenh/thumbnail-chuan.md`, `kenh/mo-ta-chuan.md`, `kenh/seo-kenh.md`; sổ tay văn phong `kenh/hoc-shu/so-tay-van-phong.md` (do bước Shu của P2 tạo)
- Sổ cách nói đã chốt: `kenh/cach-noi-da-chot.tsv` (máy kiểm `tools/lichsu/kiem-da-chot.py`)

## 6. Công cụ thay thế đang dùng
- `<chỗ nào đang dùng bản thay thế so với mức Đầy đủ, vd giọng VieNeu thay ElevenLabs; nhạc Pixabay thay Suno>`
- Nếu đang ở mức Đầy đủ: ghi «không có».

## 7. Nhật ký thay đổi hồ sơ
- `<ngày>`: tạo hồ sơ; người dùng duyệt ngách, Model Link, thương hiệu.
