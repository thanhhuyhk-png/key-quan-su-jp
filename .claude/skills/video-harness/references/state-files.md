# File trạng thái

Chỉ tạo khi mức Chuẩn hoặc Sản xuất. Đặt trong `plans/<ngày>-<slug>/` của dự án (theo quy ước thư mục của dự án). Mức Nhanh không cần file. Mỗi file ngắn: nếu không ai đọc lại thì không viết.

## brief.md (Chuẩn và Sản xuất)

```
# <tên video>
Mức: Chuẩn | Sản xuất  (vì: ...)
Mục tiêu: người xem làm hoặc cảm thấy gì sau khi xem
Người xem / nơi đăng / định dạng: ...
Yêu cầu gốc của người dùng (nguyên văn): "..."
Giới hạn: chi tối đa ... (bước trả phí trong ngưỡng này được làm tiếp, vượt thì hỏi), hạn chót ..., độ dài ...
Nguồn và tài sản được dùng: ... (kèm sổ tài sản và sổ số liệu: nguồn, giấy phép, quyền)
Tiêu chí "xong":
  Đo được:        - ...
  Cảm nhận được:  - ...
  Ràng buộc:      - ...
Cổng người duyệt: ở các điểm nào (kịch bản? storyboard? bản cuối?)
```

## checks.md (kèm sổ lỗi)

```
| Yêu cầu | Kết quả (pass/fail/unresolved) | Bằng chứng (lệnh, số liệu, khung, mốc giờ) |

Sổ lỗi:
| # | Mức | Mô tả | Nguyên nhân | Cách sửa | Trạng thái | Quy tắc đã thêm? |
```

Bằng chứng thiếu thì ghi `unresolved`, đừng để trống.

## progress.md (Sản xuất, hoặc khi chuyển chat)

```
Đang ở: giai đoạn / lát nào
Đã xong (kèm đường dẫn file đã lưu): ...
Quyết định đã chốt của người: ...
Đang treo / rủi ro / lỗi mở: ...
Bước tiếp theo cụ thể: ...
File cần đọc trước: brief.md, checks.md, CLAUDE.md
```

Khi tiếp tục ở phiên mới: đọc ba file trên trước, rồi làm tiếp từ bước ghi trong "bước tiếp theo". Chuyển chat đúng lúc dừng an toàn, tức là vừa xong một giai đoạn và không có lệnh nào chạy dở.

## Quy tắc học được

Ghi vào `CLAUDE.md` của dự án (xem "Khi lỗi" ở SKILL.md để biết khi nào đáng ghi). Mỗi quy tắc một dòng, có lý do: `- Khi <tình huống>, làm <cách>, vì <lỗi đã gặp>.` Xem lại định kỳ và gỡ quy tắc không còn đúng.
