# QA và QC cho video

**QA** là phòng ngừa: làm cho lỗi ít xảy ra. **QC** là kiểm tra: bắt lỗi trước khi giao. Cần cả hai, và không để một bên che bên kia.

## QA (trước và trong khi làm)

- Tiêu chí "xong" viết trước, ba loại:
  - **Đo được** (máy kiểm): độ dài, kích thước, fps, âm lượng, không khung đen, chữ khớp lời.
  - **Cảm nhận được** (mắt tai người hoặc reviewer): mở đầu giữ chân không, nhịp, chữ đọc kịp không, hợp thương hiệu không.
  - **Ràng buộc** (không thoả hiệp): bản quyền, quyền hình ảnh, số liệu đúng nguồn, không hứa quá.
- Thử rẻ trước, cổng trước bước tốn tiền (xem nguyên tắc 3 ở SKILL.md).
- Mỗi tiêu chí phải *kiểm được*. Nếu không nghĩ ra cách kiểm thì viết lại tiêu chí cho cụ thể hơn, hoặc đánh dấu "chỉ người kiểm được".
- Quy tắc học từ lỗi cũ (trong `CLAUDE.md`) được đọc lại đầu mỗi việc.

## QC: thang bốn bậc, rẻ đến đắt

Đi lần lượt. Bậc rẻ bắt được nhiều lỗi nhất, nên làm trước.

1. **Tự động (máy đo).** Chạy các lệnh trong [video-checks.md](video-checks.md). Kết quả là số liệu, không phải ý kiến.
2. **Soi ảnh khung và transcript (phần "mắt").** Xem ảnh tổng hợp các khung, phóng to khung có chữ tiếng Việt (dấu, cắt chữ, tràn khung), đối chiếu transcript với kịch bản. Model làm việc này trên *ảnh và chữ*; nó không xem được video chạy và **không nghe được tiếng**. Phần tiếng (giọng có tự nhiên không, nhạc đè giọng ở đâu) chỉ có số liệu từ bậc 1; nghe là việc của người ở bậc 4. Ghi rõ điều này trong báo cáo.
   - **Quy tắc lấy mẫu khung** để lỗi một khung không lọt: khung ở mỗi mốc cắt (lấy bằng cách phát hiện cảnh của ffmpeg, xem video-checks.md), 2 giây đầu và 2 giây cuối, mọi cảnh có chữ, và ít nhất một khung mỗi 5–8 giây. Số khung mặc định của công cụ thường quá thưa cho video dài, hãy đặt lại theo độ dài.
3. **Reviewer độc lập.** Một subagent ngữ cảnh mới, chỉ đọc. Nó nhận: *yêu cầu gốc của người dùng nguyên văn, brief, tiêu chí*, và các file bằng chứng (ảnh khung, ảnh tổng hợp, transcript, kịch bản, kết quả JSON của lệnh kiểm, sổ tài sản). **Không nhận video để "xem"**, vì nó cũng không xem hay nghe được. Không nhận lý lẽ của người làm. Mẫu prompt ở cuối file này.
4. **Người duyệt.** Phần cảm tính, phần tiếng, và quyết định đăng. Tôi trình bản cuối kèm bảng check và danh sách lỗi còn lại, người đồng ý thì mới coi là xong.

Mức Nhanh làm bậc 1–2, người đang xem trong chat là bậc 4 (bậc 3 bỏ vì mức không yêu cầu). Mức Chuẩn cần cả bốn. Mức Sản xuất làm theo từng giai đoạn.

## Kiểm ràng buộc (bản quyền, quyền hình ảnh, số liệu)

Ràng buộc là loại tiêu chí dễ lọt nhất, vì không có công cụ đo một phát. Cách làm:
- **Sổ tài sản**: mỗi ảnh, nhạc, giọng, phông, clip dùng trong video ghi một dòng: nguồn, giấy phép hoặc điều kiện dùng, người tạo (nếu AI thì ghi công cụ). Ảnh Wikimedia tải kèm trang nguồn thì chép giấy phép từ trang đó; còn lại phải ghi tay. Ảnh tạo bằng AI, nhạc tạo bằng công cụ AI, ảnh stock đều ghi nguồn tương ứng.
- **Sổ số liệu**: mỗi con số, trích dẫn, tên riêng trong kịch bản ghi nguồn. Không có nguồn thì ghi `unresolved` và báo người duyệt, không tự đoán.
- Người thật, thương hiệu của bên thứ ba, giọng nhân bản: ghi rõ đã có quyền chưa. Chưa rõ thì đó là S1.
- Reviewer đối chiếu hai sổ này với kịch bản và ảnh khung; thiếu dòng nào thì báo `unresolved`.

## Mức độ lỗi

| Mức | Nghĩa | Hành động |
|---|---|---|
| S1 | Chặn giao: sai sự thật, vi phạm bản quyền, lỗi hình/tiếng nặng, sai tiêu chí cứng | Sửa, kiểm lại, rồi mới giao |
| S2 | Nên sửa: ảnh hưởng chất lượng nhưng vẫn xem được | Sửa nếu rẻ, không thì ghi lại và báo người duyệt |
| S3 | Ghi nhận: chi tiết nhỏ | Ghi vào sổ, không chặn |

Người duyệt có quyền chấp nhận S2 và S3 còn lại. S1 thì không giao khi chưa xử lý, trừ khi người ra quyết định rõ ràng và biết hậu quả.

## Giao: cổng cuối

Báo cáo giao gồm: trạng thái (pass, pass có điều kiện, chưa xong), bảng check (yêu cầu, kết quả, bằng chứng), lỗi còn lại theo mức, phần máy chưa xác nhận được và cần người xem. Không có "xong" nếu thiếu bằng chứng cho tiêu chí đo được.

## Mẫu prompt reviewer độc lập

```
Bạn là reviewer chất lượng video, ngữ cảnh mới. Chỉ đọc, không sửa file.
Bạn KHÔNG xem được video chạy và KHÔNG nghe được tiếng. Chỉ kết luận từ các file dưới đây.
Yêu cầu gốc của người dùng (nguyên văn): <dán nguyên văn>
Brief và tiêu chí: <đường dẫn brief.md>
Bằng chứng: <ảnh khung, ảnh tổng hợp, transcript, kịch bản, kết quả JSON của lệnh kiểm, sổ tài sản, sổ số liệu>
Việc cần làm:
 1. Đối chiếu từng tiêu chí: tiêu chí | pass/fail/unresolved | bằng chứng (tên file, mốc giờ, số liệu).
 2. So tiêu chí trong brief với yêu cầu gốc: nêu tiêu chí nào bị thiếu hoặc bị thu hẹp.
 3. Kiểm sổ tài sản và sổ số liệu: dòng nào thiếu nguồn hoặc quyền thì báo unresolved.
 4. Ngoài tiêu chí, nêu tối đa 5 vấn đề brief chưa lường, theo mức S1/S2/S3.
Không khen chung chung. Không đủ bằng chứng thì ghi unresolved. Phần tiếng và nhịp cảm xúc: ghi "cần người nghe/xem".
Kết thúc bằng: Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
```

Chọn model cho reviewer theo bậc model ở `huong-dan/dieu-phoi/luat-van-hanh.md`. Việc đọc ảnh và phán đoán thường cần mức vừa trở lên, không dùng mức rẻ nhất cho phần phán đoán thị giác.

## Kiểm tra chính bộ kiểm tra

Cuối mỗi việc Chuẩn hoặc Sản xuất, hỏi: *có lỗi nào người duyệt tìm ra mà bộ check của mình bỏ sót không?* Nếu có, thêm check hoặc quy tắc tương ứng vào `CLAUDE.md` của dự án. Khung chỉ tốt lên khi có người (hoặc tôi) nhớ làm bước này, nên đưa nó vào checklist hoàn tất.
