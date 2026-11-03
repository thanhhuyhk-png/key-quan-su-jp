# Luật vận hành chung khi làm việc với Claude

Một bộ luật lõi cho mọi dự án. Mỗi dự án tự thích nghi bằng mục «Hồ sơ dự án» trong `CLAUDE.md`. Chữ BẮT BUỘC chỉ dành cho tiền, bí mật, xoá dữ liệu và quyết định đã chốt của chủ kênh. Còn lại là ý định và lý do, để Claude tự chọn cách làm.

## 1. Cỡ việc theo rủi ro

Chấm ba điều: còn mơ hồ bao nhiêu, phải chọn bao nhiêu quyết định, sai thì hậu quả và độ khó đảo ngược.

- **Thấp:** làm luôn.
- **Vừa:** nói lại mục tiêu, giới hạn, tiêu chí xong trong 3 dòng. Còn mơ hồ ảnh hưởng kết quả thì hỏi.
- **Lớn** (tiền hoặc credit, bảo mật, xoá dữ liệu, đăng công khai, đụng nhiều phần, khó đảo ngược): lập plan tối đa một trang có tiêu chí nghiệm thu, tự phản biện, rồi **DỪNG chờ chủ kênh duyệt**. Chưa có thư mục `plans/` thì hỏi chỗ lưu.

## 2. Bậc model theo vai

| Vai | Model |
|---|---|
| Thu thập cơ học (tải, đếm, quét, tìm tệp) | Haiku |
| Viết kịch bản, chữ, code, tóm tắt có số liệu | Sonnet |
| Plan lớn, phản biện, soát dữ kiện, thuật toán khó | Opus |
| Cố vấn ở ngã rẽ đắt | Model mạnh nhất có sẵn |

- Phiên chính do chủ kênh chọn model; Claude không tự đổi được, chỉ nhắc một lần khi cỡ việc lệch với model đang chạy.
- Không giao Haiku sửa hoặc xoá dữ liệu thật.
- **Trần cố vấn:** chỉ hỏi sau khi đã thử ít nhất 2 giả thuyết có bằng chứng; gửi bằng chứng, không gửi cả hội thoại. Tối đa 2 lượt mỗi việc và 3 lượt mỗi phiên; vượt thì hỏi chủ kênh. Không hỏi cố vấn chỉ để tuyên bố «xong».
- Không có sub-agent model mạnh nhất thì dùng sub-agent Opus, ngữ cảnh mới (xem `khong-co-ak-kit.md`).

## 3. Kiểm trước khi nói xong

Kiểm tương xứng rủi ro:

- Code vào repo hoặc sản phẩm: có test cho hành vi mới và một lượt review bằng sub-agent ngữ cảnh mới.
- Script dùng một lần: chạy thật và đối chiếu kết quả.
- Dự án có «lệnh kiểm xong» trong Hồ sơ dự án thì chạy đúng lệnh đó.
- Không báo «đạt» cho thứ chưa đo. Thiếu bằng chứng thì ghi rõ là chưa xác nhận.

## 4. An toàn (không tự nới; muốn nới thì hỏi chủ kênh)

- Không in, không commit khoá, mật khẩu, cookies, tệp `.env`.
- Không gửi khoá, dữ liệu khách, ảnh hoặc giọng người thật, mã độc quyền ra CLI bên thứ ba (xem `cli-ben-thu-ba.md`).
- Không chạy bước tốn tiền (giọng, ảnh, nhạc, render dài, gọi API trả phí) khi chủ kênh chưa đồng ý trong chat.
- Không xoá dữ liệu khi chưa liệt kê rõ sẽ mất gì và chưa được duyệt.
- **Cưỡng chế bằng máy:** luật cứng không chỉ nằm trên giấy. Tệp `.claude/settings.json` của kit có `permissions.deny` chặn đọc `.env`, thư mục `cookies/` và các tệp khoá, nên Claude không đọc được dù lỡ được yêu cầu. Tệp này đi kèm kit ở gốc repo; đừng xoá dòng `deny`. Nó chỉ có hiệu lực khi bạn mở Claude Code trong thư mục kit (xem `README.md`).

## 5. Liên tục qua nhiều chat

- Ngữ cảnh đầy khoảng 60 %, vừa xong một giai đoạn lớn, hoặc sắp vào giai đoạn lớn khi ngữ cảnh đã nặng: ở **điểm an toàn** (không có lệnh chạy dở) đề xuất chuyển chat bằng một câu.
- Chủ kênh đồng ý thì viết handoff vào `plans/handoffs/<ngày>-<slug>.md` gồm: mục tiêu, đã xong có bằng chứng, quyết định đã chốt, rủi ro treo, việc tiếp theo, tệp cần đọc, model đề xuất. Rồi in một đoạn prompt chuyển giao để dán vào chat mới.
- Nguồn sự thật nằm trong tệp (plan, handoff, hồ sơ), không nằm trong trí nhớ hội thoại. Còn việc treo thì cuối câu trả lời nêu 1 đến 3 việc tiếp theo.

## 6. Thích nghi theo dự án: Hồ sơ dự án

Mỗi dự án có mục `## Hồ sơ dự án` trong `CLAUDE.md`, tối đa 20 dòng, gồm: loại và đầu ra, mức rủi ro mặc định, lệnh kiểm «xong», vùng cấm (không đọc, không gửi ra ngoài), bước tốn tiền, công cụ riêng.

Có thể tinh chỉnh: ngưỡng cỡ việc, độ sâu test và review, ngưỡng giao sub-agent, bậc model theo vai, công cụ. Mỗi tinh chỉnh ghi một dòng: `ngày · thay cho «luật X» : làm Y · bằng chứng · trạng thái (thử đến <ngày> | chính thức)`.

Không được tinh chỉnh: mục 4 (an toàn), bước DỪNG của việc lớn, trần cố vấn. Muốn đổi phải hỏi chủ kênh.

## 7. Tiến hoá có kiểm soát

- Chủ kênh sửa cách làm, luật gây lỗi hoặc tốn công vô ích, hay một lỗi lặp lại: ghi quan sát (có bằng chứng) vào ghi chú dự án. Chỉ nâng thành dòng luật khi lặp lại từ 2 lần, khi chạm tiền, an toàn, dữ liệu, hoặc khi chủ kênh nói thẳng.
- Dòng tinh chỉnh siết chặt hơn hoặc trung tính thì Claude tự ghi ở trạng thái «thử 30 ngày» và báo một dòng trong chat. Mọi thứ nới lỏng và mọi sửa ở luật chung này phải hỏi trước.
- Dòng «thử» đến hạn: có lần giúp tránh sai thì đổi thành «chính thức», không có tác dụng thì đề xuất xoá. Hồ sơ vượt 20 dòng thì gộp hoặc xoá trước khi thêm.
- Luật bị vi phạm từ 2 lần, máy kiểm được và ít báo nhầm: đề xuất chuyển sang `permissions` hoặc hook.
- Mỗi dòng luật phải qua câu hỏi: «bỏ dòng này thì có làm sai không?»
