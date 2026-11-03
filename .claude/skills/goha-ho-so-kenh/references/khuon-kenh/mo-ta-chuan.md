# Chuẩn mô tả, thẻ, hashtag, ghi nguồn: <tên kênh> (khuôn trống)

> Khuôn do K2 chép thành `kenh/mo-ta-chuan.md`. P7 (`goha-ls-dang`) đọc tệp này để viết mô tả mọi tập. Điền từ 5–10 mô tả của video thắng trong sheet top 20 (đọc kỹ, chỉ ghi cái đo được); không chép chữ của kênh nào. Mô tả là chữ cho người xem nên đi theo luật ở `CLAUDE.md`: sub-agent viết, người phản biện khác rà, Claude rà dữ kiện theo sổ số liệu; quét bằng `quet.py --tieu-de` và `kiem-da-chot.py`, cả hai 0 lỗi.

## 1. Khuôn mô tả (thứ tự cố định, tối đa 4.800 ký tự)
| # | Khối | Quy cách | Học từ (n/10 video mẫu) |
|---|---|---|---|
| 1 | Cảnh mở | `<số ký tự; mở bằng mốc thời gian và địa điểm>` | `<n>` |
| 2 | Nút thắt | `<1–2 đoạn, kết bằng câu hỏi trùng ý tiêu đề>` | `<n>` |
| 3 | Khối nguồn tư liệu kể bằng lời | `<cách nêu loại tư liệu; nguồn trong nước đứng trước>` | `<n>` |
| 4 | Mốc chương | `0:00 <tên>`, `<số>` mốc, lấy từ bản dựng cuối | `<n>` |
| 5 | Xem thêm | `<từ tập 2: liên kết các tập trước>` | `<n>` |
| 6 | Nguồn và tư liệu | Mục 2 | `<n>` |
| 7 | Hashtag | Mục 3 | `<n>` |

## 2. Nguồn và tư liệu (ghi chi tiết, chính xác)
- Mỗi dòng: `<cơ quan giữ bản gốc, mã lưu trữ, tên tư liệu, năm>`; không ghi chung chung «theo internet».
- Câu ghi công bản đồ theo đúng giấy phép của từng nguồn: `<chép nguyên chữ mà giấy phép yêu cầu>`
- Ngân sách độ dài: `<số ký tự dành cho nguồn để cả mô tả ≤ 4.800>`

## 3. Hashtag (3 cái, dòng cuối)
| Đề tài | Ví dụ |
|---|---|
| `<nhóm đề tài 1>` | `<#...>` |

## 4. Thẻ (20–25 thẻ, tổng ≤ 480 ký tự, cách nhau «, », không ngoặc kép)
| Nhóm | Số thẻ | Ví dụ |
|---|---|---|
| Tên sự kiện, nhiều cách gọi | `<4–6>` | `<...>` |
| Địa danh, đơn vị | `<4–6>` | `<...>` |
| Nhân vật có trong phim | `<2–4>` | `<...>` |
| Tiếng Anh | `<3–4>` | `<...>` |
| Không dấu | `<1–2>` | `<...>` |
| Chung của ngách | `<2–3>` | `<...>` |
| Thương hiệu (đứng cuối) | 1 | `<tên kênh>` |

## 5. Mục khác khi tải lên
- `<danh mục, ngôn ngữ, khai báo nội dung tổng hợp, bình luận ghim: theo references/cong-quet-va-khai-bao.md của P7>`

## 6. Kiểm trước khi đăng (đạt hết mới đăng)
- [ ] Mô tả ≤ 4.800 ký tự; mốc chương lấy từ bản dựng cuối
- [ ] Mỗi dòng nguồn có dòng trong sổ tài sản; mỗi số có dòng trong sổ số liệu
- [ ] Hai lệnh quét 0 CHẶN; `kiem-da-chot.py` 0 chỗ phạm
