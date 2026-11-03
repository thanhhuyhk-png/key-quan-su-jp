# Brief tập: <tiêu đề làm việc>

Mẫu cho `tap/EPxxx-<slug>/ke-hoach/brief.md`. Điền hết; ô chưa biết ghi «chưa rõ», không bỏ trống. Người dùng đã duyệt đề tài mới được ghi.

## Đề tài
- **Đề tài:** 
- **Năm, địa điểm:** 
- **Ngôn ngữ, thị trường:** 
- **Góc kể (khác biệt so với video cùng đề tài):** 
- **Cấu trúc kể:** (đồng hồ đếm ngược / bàn cờ hai kế hoạch / người dẫn đường / ba quyết định / vật chứng; khác cấu trúc tập liền trước)
- **Câu hỏi trung tâm của tập:** 
- **Độ dài mục tiêu:** (từ `ho-so-kenh/ho-so.md`)

## Vì sao chọn
| Cột | Điểm 0–5 | Bằng chứng |
|---|---|---|
| Nhu cầu | | |
| Cạnh tranh | | |
| Tư liệu sẵn có | | |
| Rủi ro chính sách | | |

Video mẫu trong sheet top 20 (tiêu đề, kênh, view, link): 

## Kiểm trùng
- Lệnh: `python -I -X utf8 tools/lichsu/kiem-de-tai.py "<đề tài>" --goc "<góc kể>" --ngon-ngu <mã>`
- Kết quả: ĐẠT / CẢNH BÁO (ghi dòng khớp) — ngày kiểm: 
- Đã đăng ký vào sổ chung: có / chưa (người dùng tự điền)

## Giao cho P1
- **Dữ kiện cần tra trước:** (con số, ngày, tên, quân hàm hay chức vụ của nhân vật chính)
- **Nguồn chính thống đã biết:** 
- **Tư liệu hình đã biết (hạng A/B/C):** 
- **Bản đồ, đồ hoạ code cần dựng:** 
- **Điểm nhạy cảm riêng của đề tài** (đối chiếu `ho-so-kenh/luat-noi-dung.md`): 
- **Việc không làm:** 

---

# Mẫu `progress.md`

Tạo cùng lúc với `brief.md`, ở `tap/EPxxx-<slug>/ke-hoach/progress.md` (ví dụ `tap/EP001-<slug>/ke-hoach/progress.md`). Bộ định tuyến của `CLAUDE.md` đọc tệp này khi người dùng chọn «làm tiếp tập dở», nên mỗi phase xong phải cập nhật dòng của nó. Giờ ghi theo giờ máy thật (`date`).

```
# Tiến độ tập <số> · <tiêu đề làm việc>

Đang ở: P0 xong, chờ P1
Bước tiếp theo: chạy P1 `goha-ls-nghien-cuu` với brief.md

| Phase | Trạng thái | Ngày | Cổng đã duyệt | Ghi chú |
|---|---|---|---|---|
| P0 Chọn đề tài | xong | <dd/mm> | người dùng duyệt đề tài <dd/mm> | kiểm trùng: ĐẠT |
| P1 Nghiên cứu | chưa | | | |
| P2 Kịch bản | chưa | | | |
| P3 Phân cảnh | chưa | | | |
| P4 Giọng | chưa | | | |
| P5 Dựng | chưa | | | |
| P6 QC | chưa | | | |
| P7 Đăng | chưa | | | |
| P8 Shorts | chưa | | | |
```
