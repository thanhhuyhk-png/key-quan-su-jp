# Thumbnail A/B/C cho Test & Compare

Chuẩn nhận diện của kênh: `kenh/thumbnail-chuan.md` (nền, bảng màu, font, vùng an toàn, logo; màu và logo lấy từ `ho-so-kenh/ho-so.md`). Skill này chỉ nói cách làm 3 bản.

## Luật không đổi (kênh sử Việt)
- **Nền chỉ là ảnh, phim tư liệu thật hoặc đồ hoạ code.** Không ảnh AI. Ảnh phải đủ quyền dùng và có dòng trong sổ tài sản; ảnh chưa xin phép thì không dùng.
- **Không ảnh lãnh tụ Việt Nam** trên bìa (bìa phải cắt, hạ màu, chồng chữ, mà luật cứng cấm sửa ảnh lãnh tụ).
- Không máu, xác, vết thương, tù binh hay tướng địch ra hàng ghép chữ mỉa mai; không cờ chính quyền Sài Gòn; không biểu tượng Quốc xã làm trọng tâm.
- Chữ trên bìa quét bằng `quet.py --tieu-de`: không «không che», «uncensored», chữ máu me, giật tít.

## Chữ bìa: 3–5 chữ, mở vòng lặp
- Người xem đọc trong 1 giây phải tự hỏi «sao lại thế?». Dùng nghịch lý hoặc cặp số đối lập có trong sổ số liệu; ưu tiên **dạng câu hỏi**: dòng 1 nêu sự việc có thật, dòng 2 là câu hỏi ngắn không tự lộ đáp án.
- Mỗi chữ đúng nghĩa đen theo sổ. Chọn từ hỏi không gợi sai sự thật.
- Câu mơ hồ hoặc khẳng định đóng bị loại. Chữ bìa không lặp tiêu đề.
- Có thẻ ngày/địa danh ở thẻ màu nổi theo chuẩn kênh (mọi tập).

## Ba bản
| Bản | Khác nhau ở | Dùng để thử |
|---|---|---|
| A (chính) | Chữ nghịch lý + chủ thể hành động (ảnh/phim tư liệu mạnh nhất tập) | Bản mặc định |
| B | Cùng chủ thể, chữ câu hỏi khác góc (hỏi về cái bị giấu, cái chưa biết) | Khác góc tò mò |
| C | Chủ thể khác (cảnh khác của tập), chữ cặp số đối lập | Khác hình, khác chữ |

Đừng đổi cùng lúc cả chữ lẫn bố cục giữa A và B, kẻo số đo không chỉ ra yếu tố nào thắng. Mỗi bản ghi lại: tệp, chữ hai dòng, ảnh nền (mã sổ tài sản), vì sao chọn.

## Dựng
- Khuôn HTML bìa của kênh (tập mẫu: `template/thumbnail-dbp.html`) nhận ảnh, chữ, thẻ; chụp bằng Chrome/Edge headless (`chrome` trong `cau-hinh.toml`). Tập mẫu có `mau/dien-bien-phu-1954/san-xuat/ve-thumbnail.py` (ở repo chủ kit là `tap/EP001-dien-bien-phu-1954/san-xuat/`); tập mới KHÔNG có sẵn, chép nó sang `tap/<EPxxx-slug>/san-xuat/` rồi sửa bảng dữ liệu đầu tệp. Script có: bảng `BAN` khai ba bản (ảnh, chữ, thẻ) và ra `Final/EPxxx-thumbnail-a/b/c.jpg` cùng bản soi cỡ điện thoại ở `<output>`. Tập mới chép script, đổi bảng `BAN` và đường ảnh.
- Thông số: 1280×720, JPG ≤ 2 MB.
- **Soi trước khi trình:** xuất bản 168×94, chữ vẫn đọc được; chữ và thẻ cách mép trái ≥ 110 px, mép phải dưới chừa chỗ cho số thời lượng; logo đúng góc theo chuẩn kênh.

## Test & Compare
Tải ba bìa lên mục Test & Compare của Studio khi đăng. Sau 7–14 ngày ghi bản thắng và số đo vào `kenh/lich-noi-dung.md`; tập sau học từ bản thắng (kiểu chữ, chủ thể), không bắt chước tuyệt đối từ một lần thử.
