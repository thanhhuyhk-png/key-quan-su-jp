# Giao việc cho sub-agent

## Khi nào giao

- Giao phần cơ học nhiều vòng: dự đoán từ 3 vòng tra cứu trở lên, hoặc đầu ra thô dài hơn khoảng 2 nghìn token (tải, gỡ băng, quét, đếm, tìm tệp). Sub-agent trả báo cáo ngắn kèm đường dẫn bản thô; phiên chính tự mở bản thô nào cần cho quyết định.
- Biết đích danh tệp thì tra thẳng, đừng giao: mỗi sub-agent tốn một lượng ngữ cảnh khởi động.
- Chạy song song chỉ khi mỗi sub-agent sở hữu tệp riêng. Hai sub-agent cùng sửa một tệp, một cấu hình chung, hay một chuỗi đánh số tuần tự là công thức hỏng việc.
- Bậc model theo vai: xem `luat-van-hanh.md` mục 2.

## Mẫu brief

Brief là thứ duy nhất sub-agent biết. Không chuyển cả hội thoại; tóm tắt đúng các quyết định cần cho việc này và chỉ đường dẫn tệp cụ thể thay vì «tự tìm quanh repo» (trừ khi chính việc là đi tìm).

```
## Việc
<một đoạn: làm gì, để phục vụ điều gì>

## Được đọc
- <đường dẫn tệp hoặc thư mục>

## Được sửa hoặc tạo (chỉ những chỗ này)
- <đường dẫn>

## Tiêu chí xong (đo được)
- <vd: lệnh X chạy ra 0 lỗi; tệp Y có đủ 12 dòng; mọi số liệu có nguồn>

## Ràng buộc
- <vùng cấm, không đọc khoá hay cookies, không chạy bước tốn tiền, không commit, cờ phạm vi nếu có>
- <quyết định chủ kênh đã chốt, để sub-agent khỏi hỏi lại>

## Nơi ghi báo cáo
plans/reports/<tên-việc>-<ngày>.md  (ngắn: tệp đã làm, bằng chứng từng tiêu chí, chỗ nghi ngờ)

## Kết thúc báo cáo bằng
Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
Summary: một hoặc hai câu
Concerns/Blockers: nếu có
```

Nếu chủ kênh đặt một cờ phạm vi (ví dụ chỉ làm phần tối thiểu), phải ghi cờ đó vào brief; sub-agent không thấy cờ sẽ mặc định làm đủ phạm vi.

## Nhận kết quả

- Đọc dòng `Status` trước. `BLOCKED` hoặc `NEEDS_CONTEXT`: đổi ngữ cảnh, phạm vi hoặc cách tiếp cận; không gửi lại đúng brief cũ.
- Đối chiếu từng tiêu chí xong với bằng chứng trong báo cáo, không tin lời «đã xong».
- Người viết không tự chấm bài của mình: việc quan trọng thì cho một sub-agent khác, ngữ cảnh mới, chỉ đọc, kiểm lại.
- Hợp nhất kết quả, quyết định gộp và hỏi chủ kênh là việc của phiên chính.
