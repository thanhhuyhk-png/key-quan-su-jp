# Dựng thương hiệu kênh bằng code

Mọi hình làm bằng code (SVG, Chrome headless), không dùng ảnh AI. Máy dựng CHUNG nằm ở `tools/thuong-hieu/thuong_hieu.py`: đọc một tệp cấu hình của kênh bạn, tự dựng logo, ảnh đại diện, banner, dấu kênh và ảnh soi. Chữ dựng từ font OFL trong `template/fonts/` rồi đổi thành path. Máy không chứa logo hay chữ của kênh mẫu, nên không cần chép hay sửa tay. Chrome hay Edge lấy từ khoá `chrome` trong `cau-hinh.toml`; cần `fontTools`, `Pillow` (đã nằm trong `requirements.txt` của kit).

Không chép máy dựng ở `kenh/thuong-hieu/ma-nguon/` của kênh mẫu (nếu repo có): nó ghi cứng màu, chữ và nét logo của kênh mẫu.

## Quy trình
1. Chốt tên kênh, chữ phụ (vd `History`, có thể để trống), khẩu hiệu, handle `@...`, bảng màu (mục dưới), font.
2. Chép `tools/thuong-hieu/vi-du.json` thành `kenh/thuong-hieu/thuong-hieu.json` rồi sửa. Khoá:
   - `ten` (bắt buộc), `chu_phu`, `khau_hieu`, `handle` (bắt đầu bằng `@`), `viet_tat` (chữ lồng trong dấu; bỏ trống thì lấy chữ đầu của hai từ đầu tên).
   - `mau`: `nen`, `chu`, `nhan` (cả ba bắt buộc, dạng `#rrggbb`).
   - `font`: `tieu_de` (tên tệp trong `template/fonts/`), `tieu_de_wght` (với font biến thiên, vd 600), `noi_dung`. Bỏ trống thì dùng Oswald 600 và Be Vietnam Pro Medium.
   - `bo_cuc`: 1 đến 3 hướng trong `vach` (khung vuông có vạch bên), `tron` (vòng tròn), `gach` (gạch dưới). Ba hướng cho ba bản để so; chọn một.
3. Chạy (máy dựng tự kiểm màu trước, trùng họ màu kênh mẫu thì dừng, mã thoát 3; tương phản kém mã 4; thiếu khoá mã 2):
   `python -I -X utf8 tools/thuong-hieu/thuong_hieu.py --cau-hinh kenh/thuong-hieu/thuong-hieu.json --ra kenh/thuong-hieu/ra`
   Tuỳ chọn: `--chrome <đường dẫn>`, `--font-dir <thư mục font>`.
4. Đầu ra, mỗi hướng `<bc>` một thư mục: `svg/` (logo dọc, ngang; bản `toi`, `sang`, `mot-mau-chu`, `mot-mau-nen`; `bieu-tuong.svg`), `png/` (cùng bộ, nền trong; `logo-anh-bia.png`), `youtube/` (`anh-dai-dien-800.png`, `banner-2560x1440.jpg` có nội dung trong vùng an toàn 1546×423, `dau-kenh-150.png`). Cạnh đó có `soi.jpg` (hướng đầu) và `soi-<bc>.jpg` (hướng khác).
5. Soi `soi.jpg` cỡ thật: banner với khung đỏ nét đứt là vùng an toàn, ảnh đại diện 400, 98 và 40 px, dấu kênh mờ 58 % trên khung phim, logo trên nền tối và sáng. Soi chữ tràn, dấu tiếng Việt bị cắt, chữ khó đọc. Sửa JSON rồi chạy lại tới khi sạch.
6. Chọn một hướng: sửa `bo_cuc` trong `thuong-hieu.json` chỉ còn hướng đó rồi chạy lại lệnh bước 3. Lần chạy cuối cũng ghi `kenh/thuong-hieu/nhan-dien-kenh.js`: màu thẻ chữ, lớp chữ suy từ `nen`, `chu`, `nhan` và đường dẫn logo ngang nền tối của hướng đó; `template/lib/nhan-dien.js` đọc tệp này khi dựng. Tệp này **bắt buộc** trước P5: kit thiếu nó thì mọi thẻ chữ báo lỗi, để kênh bạn không mang màu kênh mẫu. Giữ nguyên thư mục `--ra` (tệp trỏ tới logo trong đó), commit cả hai vào repo kênh. Đổi màu, đổi logo: sửa `thuong-hieu.json` rồi chạy lại máy, không sửa tay `nhan-dien-kenh.js`. Xoá các hướng không chọn ở lần chạy trước nếu còn.

Muốn dáng khác hẳn các hướng có sẵn thì báo người dùng, không sửa tay SVG ra rồi bỏ máy dựng; thêm hướng mới vào `bieu_tuong()` trong `tools/thuong-hieu/thuong_hieu.py` kèm test.

## Bảng màu
Cần: nền, nhấn (màu chữ chính ảnh bìa), chữ phụ, một màu cảnh báo/thẻ. Trên nền tối, chữ chính phải đạt tương phản ≥ 4,5:1; ảnh đại diện đọc được ở 98 px và 40 px.

**Phải khác kênh mẫu** (nền ô-liu `#3a4126`, nhấn vàng đồng `#e2b04a`). Lệnh kiểm, in ĐẠT hoặc liệt kê màu gần kênh mẫu (mã thoát 0 là đạt):
`python -I -X utf8 .claude/skills/goha-ho-so-kenh/scripts/kiem-mau.py "<nền>" "<nhấn>" ["<màu khác>" ...]`
Màu bị coi là gần khi lệch sắc độ dưới 35 độ và độ sáng dưới 0,25 so với một trong hai màu kênh mẫu. Cam, vàng nghệ, lục sẫm đều dễ bị bắt. Nên chọn họ màu khác hẳn: navy với kem, than với đỏ gạch, xám đá với lam nhạt. Màu gần mà người dùng vẫn muốn giữ thì báo người dùng rủi ro, không tự bỏ qua lệnh kiểm.

Đừng dùng màu vàng chanh sáng nếu Model Link dùng màu đó (tránh chép kênh mẫu của chính bạn).

## Font
Chọn font có giấy phép OFL, có dấu tiếng Việt nếu kênh tiếng Việt. Tiêu đề một font đậm; nội dung một font dễ đọc. Chép tệp (kèm giấy phép OFL) vào `template/fonts/` của kit, ghi tên vào hồ sơ và vào `font` của `thuong-hieu.json`; font phải có đủ dấu tiếng Việt, thiếu ký tự thì máy dựng báo rõ ký tự nào. Kênh mẫu dùng Oswald 600 và Be Vietnam Pro; bạn có thể dùng lại (OFL) nhưng khác kiểu bố cục là đủ, không bắt buộc đổi font.

## Quy cách tối thiểu
- Ảnh đại diện 800×800, chủ thể chiếm khoảng ba phần tư, không thêm chữ nhỏ.
- Banner 2560×1440, nội dung nằm trong vùng an toàn 1546×423 ở giữa.
- Khoảng trống quanh logo ít nhất bằng chiều cao chữ nhỏ nhất của logo.
- Logo trên ảnh bìa cao ≤ 7 % chiều cao ảnh, đặt trong vùng an toàn (YouTube Studio cắt mép).
- Dấu kênh trong phim: ô nhỏ, độ mờ khoảng 58 %, ẩn ở tiêu đề, ảnh, lời nhân vật quan trọng.
- Cấm: kéo méo, xoay, viền phát sáng, đổi màu tuỳ tiện; ghép logo với biểu tượng nhà nước, quân hiệu, cờ; làm logo bằng ảnh AI.

## Cổng duyệt
Trình người dùng: ảnh đại diện, banner, logo nền tối và nền sáng, ảnh đại diện thu nhỏ 98 px và 40 px, bảng màu và kết quả lệnh kiểm. Người dùng gật thì ghi đường dẫn vào mục 4 của `ho-so.md`.
