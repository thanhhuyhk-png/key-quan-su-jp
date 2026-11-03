---
name: video-harness
description: Khung điều phối làm video có kiểm soát chất lượng (QA phòng ngừa + QC kiểm thành phẩm), co giãn theo rủi ro. Dùng khi dựng video nhiều bước, tốn credit (giọng, ảnh, nhạc, render dài), có thể đăng công khai hoặc làm cho khách, bằng công cụ dựng của kit, HyperFrames, Remotion, CapCut hay bất kỳ công cụ nào. Bao quanh các skill dựng video, không thay thế chúng. Không dùng cho thao tác lẻ (cắt một clip, đổi định dạng, một lệnh lẻ).
---

# video-harness

Khung này giúp một việc video đi từ ý tưởng đến bản giao mà ít đốt credit vô ích và giảm khả năng giao hàng lỗi (không loại trừ được hoàn toàn). Nó là bộ nguyên tắc có phán đoán, không phải biểu mẫu bắt buộc. Skill dựng video (các skill `goha-ls-*` của kit, v.v.) vẫn lo phần *làm thế nào*; khung này lo *làm có đúng không và có đáng không*.

## 5 nguyên tắc

1. **Mức kiểm soát theo rủi ro, không theo cỡ việc.** Một clip 10 giây đăng cho khách có thể cần nhiều hơn một phim 5 phút để xem nội bộ. Xem [tiers.md](references/tiers.md).
2. **Viết "xong trông thế nào" trước khi làm.** Tiêu chí có trước, sản phẩm có sau. Không có tiêu chí thì mọi thứ đều "pass".
3. **Thử rẻ trước, tốn tiền sau.** Kịch bản, rồi mẫu giọng ngắn, rồi một cảnh, rồi cả video. **Bước trả phí** là mọi bước gọi dịch vụ tính tiền (ElevenLabs, ảnh, nhạc, tiếng động) hoặc render dài. Mặc định hỏi trước mọi bước trả phí. Khi `brief.md` đã ghi mức chi tối đa thì làm trong ngưỡng đó, vượt thì hỏi.
4. **Người làm không tự chấm bài của mình.** Kiểm độc lập bằng ngữ cảnh mới, rồi đến mắt và tai của người. Xem [qa-qc.md](references/qa-qc.md).
5. **Nói thẳng giới hạn.** Model *không xem được video chạy và không nghe được tiếng*. Nó đo được số liệu (âm lượng, kích thước, độ dài), đọc được ảnh khung và transcript, so được chữ với lời. Nhịp, cảm xúc, độ cuốn, giọng đọc có tự nhiên không, hợp thương hiệu không: chỉ người phán xét được. Ghi rõ phần nào chưa được ai xác nhận.

## Bước 0: định mức (30 giây, trong đầu hoặc một dòng trong chat)

Hỏi: *nếu hỏng thì mất gì, và có làm lại rẻ được không?* Chọn **Nhanh**, **Chuẩn** hoặc **Sản xuất** theo [tiers.md](references/tiers.md). Mức là *gói mặc định*, được thêm hoặc bớt từng cổng lẻ (ví dụ "Nhanh + cổng bản quyền", "Chuẩn cho khách nhưng bỏ storyboard"). Ghi một dòng "mức: X vì Y; thêm/bớt: Z". Được đổi mức giữa chừng nếu có dấu hiệu mới, ghi lý do một dòng. Bỏ một bước vì mức đã không yêu cầu nó thì coi như đã nêu lý do.

## Vòng làm (rút gọn hoặc đầy đủ tuỳ mức)

1. **Brief.** Mục tiêu, người xem, nơi đăng và định dạng, tiêu chí "xong", giới hạn chi và thời gian. Thiếu gì ảnh hưởng kết quả thì hỏi **một** câu tập trung. Giữ lại *yêu cầu gốc của người dùng nguyên văn* trong brief, để reviewer đối chiếu được tiêu chí có bị thu hẹp không. Mẫu ở [state-files.md](references/state-files.md). Với việc tốn credit, chạy `python tools/kiem-may/kiem-may.py` trước để chắc máy và khoá sẵn sàng.
2. **Chọn skill dựng.** Dùng skill sản xuất của kit (`goha-ls-*`) hoặc skill dựng bạn đang có để chọn gói. Đừng tự chế lại quy trình mà skill dựng đã có.
3. **Làm theo lát, không làm cả khối.** Mỗi lát (kịch bản, giọng, một cảnh, bản dựng thô) qua QC nhỏ rồi mới ghép tiếp. Lỗi phát hiện sớm rẻ hơn gấp nhiều lần.
4. **QC thành phẩm** theo thang tự động, mắt/tai, độc lập, người ([qa-qc.md](references/qa-qc.md); ánh xạ công cụ ở [video-checks.md](references/video-checks.md)).
5. **Giao** qua cổng duyệt của người ở mọi mức. Với mức Nhanh, người đang xem trực tiếp trong chat chính là cổng. Không tự coi là xong.

## Khi lỗi

- Sửa theo bằng chứng, phạm vi hẹp (chỉ phần lỗi), tối đa **ba lần** cho một lỗi.
- Hết ba lần mà chưa qua: **đổi cách tiếp cận** hoặc hỏi người. Không render lặp lại cùng một thứ.
- Lỗi lặp lại hoặc tốn kém và nguyên nhân không hiển nhiên thì ghi một quy tắc ngắn (kèm lý do) vào `CLAUDE.md` của dự án để phiên sau không lặp. Đừng ghi mọi lỗi vặt: quy tắc phình to cũng là lỗi.

## Không bao giờ

- Đăng, gửi, hoặc chạy bước trả phí vượt mức đã được cho phép mà chưa hỏi.
- Dùng ảnh, nhạc, người thật có bản quyền hoặc quyền hình ảnh chưa rõ mà không báo.
- Báo "pass" cho thứ chưa đo. Thiếu bằng chứng thì ghi `unresolved`, đừng ẩn.
- Bỏ một bước kiểm mà không nêu lý do.

## Nối với phần còn lại của máy bạn

- File trạng thái (brief, checks, progress) nằm trong `plans/<ngày>-<slug>/` của dự án. Mức Nhanh không cần file.
- Chuyển chat giữa chừng: `progress.md` là nguồn sự thật về trạng thái. Có thể viết handoff theo `huong-dan/dieu-phoi/luat-van-hanh.md` mục 5 (hoặc `ak:handoff` nếu có AK kit), nhưng nó chỉ trỏ tới `progress.md`, không thay thế.
- Chọn model cho reviewer có chủ đích theo bậc model ở `huong-dan/dieu-phoi/luat-van-hanh.md`. Quyết định liên quan tiền hoặc đăng công khai giữ ở phiên chính.
- Bí thật hoặc ngã rẽ lớn: hỏi sub-agent cố vấn model mạnh nhất (xem `huong-dan/dieu-phoi/khong-co-ak-kit.md`), không đổi model của phiên.
