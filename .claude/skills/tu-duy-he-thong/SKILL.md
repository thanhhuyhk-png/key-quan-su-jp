---
name: tu-duy-he-thong
description: >-
  Quy trình «tư duy hệ thống» trước khi sửa hoặc thêm tính năng: khảo sát bằng 3 câu hỏi (sự thật nằm
  ở đâu, lỗi báo về đâu, xoá đi thì hỏng gì) → vẽ mô hình → spec → plan → CHỦ KÊNH DUYỆT → mới làm →
  vòng phản hồi có điều kiện dừng → phép thử xoá và reviewer ngữ cảnh mới → ghi trí nhớ gọn. Dùng
  TRƯỚC mọi việc không mô tả được trong một câu: vá bug, đổi nhà cung cấp, thêm công cụ, tái cấu
  trúc, tính năng mới, đổi quy trình sản xuất. Kích hoạt khi nghe «tư duy hệ thống», «lên mô hình
  tổng thể», «plan trước khi làm», «làm đúng trình tự».
---

# Tư duy hệ thống: khảo sát, mô hình, spec, plan, duyệt, làm

Ý tưởng theo video của Ngô Phùng Khánh, ghép với cách làm việc của Claude Code.

Điểm xuất phát: mã chỉ là cái bóng của «lý thuyết» trong đầu người làm. AI tạo ra bóng rất nhanh, nhưng chỉ đáng tin khi người cầm lái hiểu nó vừa làm gì. Người cầm nhịp là chủ kênh và Claude, không phải agent chạy việc.

Việc mô tả được trong một câu (đổi chữ, sửa lỗi chính tả) thì bỏ qua skill này.

## Bước 1. Khảo sát, CHƯA sửa gì

Claude đóng vai người khảo sát, không phải thợ. Dùng Grep, Glob, đọc tệp, hoặc sub-agent `Explore` (xem `huong-dan/dieu-phoi/khong-co-ak-kit.md`). **Cấm sửa hay ghi tệp làm việc ở bước này.** Trả lời ba câu, kèm tệp:dòng:

1. **Sự thật nằm ở đâu?** Liệt kê MỌI nơi đang giữ cùng một dữ liệu (cấu hình, cài đặt đã lưu, tệp dự án, dịch vụ ngoài). Từ hai nơi cùng «làm chủ» trở lên là lỗi đang chờ nổ.
2. **Lỗi báo về đâu?** Khi hỏng, chỗ nào hiện lỗi (log, giao diện, thông báo, hay im lặng)? Chỗ nào nuốt lỗi, âm thầm rơi về giá trị mặc định là chỗ «giả vờ chạy».
3. **Xoá hay đổi cái này thì hỏng gì?** Vùng ảnh hưởng: mọi nơi gọi hoặc đọc, test đang khoá, dữ liệu cũ của người dùng.

Nếu là bug, kèm **bằng chứng thật** (log, kết quả chạy, số liệu đo): test xanh chưa chắc là đúng. Ghi vào `plans/<plan>/01-khao-sat.md`.

## Bước 2. Vẽ mô hình (không vẽ được nghĩa là chưa hiểu)

`plans/<plan>/02-mo-hinh.md`: sơ đồ mermaid gồm hộp và mũi tên luồng dữ liệu; đánh dấu ★ nơi lưu trạng thái, ⚠ chỗ dễ hỏng, 🔁 chỗ có phản hồi. Chốt **một nguồn sự thật** cho dữ liệu đang sửa; nơi khác chỉ đọc hoặc làm dự phòng.

## Bước 3. Spec: cái gì và vì sao, trước khi nói làm thế nào

Việc lớn hoặc mơ hồ thì để Claude **hỏi ngược chủ kênh**, từng câu một, về kỹ thuật, trường hợp biên, đánh đổi; không hỏi điều hiển nhiên. Spec gồm 5 mục trong `plan.md`: **Vấn đề · Ràng buộc · Tiêu chí thành công (đo được, bằng dữ liệu thật) · Tình huống lỗi · Ngoài phạm vi.**

## Bước 4. Plan

Chia phase nhỏ. Mỗi phase: tệp sẽ sửa, các bước, cách kiểm, rủi ro, cách lùi lại. Nêu rõ **điểm có thể hỏng** (rút từ câu 3 ở bước 1). Ưu tiên vá đúng gốc, không che triệu chứng. Không có AK kit thì tự viết `plan.md` theo khung này.

## Bước 5. DỪNG, chờ chủ kênh duyệt

Trình bằng tiếng dễ hiểu: mô hình, spec, plan, các câu hỏi còn mở. **Chưa duyệt thì không làm.**

## Bước 6. Làm, kèm vòng phản hồi

- Ngữ cảnh sạch, bám spec. Prompt giao việc (kể cả cho CLI bên thứ ba) luôn có ba thứ: **dữ liệu đầu vào thật** (log hoặc lỗi thật), **điều kiện dừng** («chạy test đến khi xanh»), **cấm đi tắt** («xử lý tận gốc, không bỏ qua test, không nuốt lỗi»).
- Việc phải xảy ra MỌI lúc thì biến thành hook hoặc test tự động, không dặn bằng lời (agent sẽ quên).
- Sửa cùng một lỗi quá 2 lần vẫn sai thì dừng, quay về điểm trước (`/rewind`), viết lại prompt tốt hơn.

## Bước 7. Phép thử xoá và phản biện

- Hỏi: «xoá phần vừa làm thì hỏng gì, liệt kê tệp:dòng». Mình phải đoán trước được câu trả lời.
- Bắt giải thích đã cân nhắc phương án nào khác, và nếu làm khác thì hỏng gì.
- Người viết không tự chấm bài: giao một sub-agent **ngữ cảnh mới** review so với spec, chỉ báo lỗ hổng, không báo sở thích phong cách.
- Đo lại theo tiêu chí thành công bằng dữ liệu thật. Test xanh chưa phải là xong.

## Bước 8. Ghi trí nhớ gọn

Quyết định kiến trúc mà agent không tự đoán được thì ghi ngắn vào `CLAUDE.md` hoặc ghi chú dự án. Dòng nào xoá đi mà vẫn làm đúng thì xoá.

## Áp dụng cho dự án của bạn

Khi khảo sát bước 1, ghi riêng những nơi trong dự án hay trùng «sự thật» (ví dụ tệp `ho-so-kenh/ho-so.md` so với những gì lỡ ghi cứng trong kịch bản hoặc skill). Đổi nhà cung cấp giọng, ảnh, nhạc, hay công cụ dựng là loại việc nên đi đủ 8 bước, vì giá và đầu ra của dịch vụ ngoài thay đổi mà không báo trước.
