# CLI bên thứ ba: Codex, Grok, Agy

Mặc định Claude tự làm. Các CLI này là tuỳ chọn; không cài thì bỏ qua cả tệp này (xem phần cuối).

## Khi nào đáng dùng

- Việc dài hơn khoảng 20 phút, chạy nền được.
- Lô việc lặp lớn (nhiều test, nhiều tệp mẫu).
- Cần một góc nhìn khác hãng để phản biện.
- Cần năng lực Claude không có (ví dụ ngữ cảnh rất lớn, đa phương thức, tra cứu thời gian thực).

| CLI | Hợp với |
|---|---|
| Codex, bậc sâu | thuật toán khó, bug logic, review chéo |
| Codex, bậc nhanh | lô test, mẫu lặp, đổi định dạng |
| Agy (Gemini) | ngữ cảnh rất lớn, giao diện, đa phương thức, phản biện kịch bản |
| Grok | tra cứu thời gian thực |

Chọn bậc model theo vai như `luat-van-hanh.md` mục 2: đọc và gom thì bậc nhanh, viết thì bậc chuẩn, plan lớn hoặc review cuối thì bậc sâu. Tên bậc đổi theo từng phiên bản CLI; không khớp thì hỏi chủ kênh.

## Cách chạy an toàn

1. **Thư mục rỗng hoặc worktree.** CLI chạy trong một thư mục rỗng chỉ chứa brief, hoặc trong `git worktree` riêng đã loại các vùng cấm. Không chạy trong cây làm việc chính.
2. **Sandbox.** Bật chế độ sandbox của CLI (`--sandbox`). Việc không cần ghi tệp thì dùng sandbox chỉ đọc.
3. **Brief dài ghi vào `brief.md`.** Windows giới hạn độ dài dòng lệnh, nên đừng dán brief dài vào tham số. Ghi `brief.md` trong thư mục làm việc rồi dặn CLI «đọc brief.md và làm theo». Brief theo mẫu ở `giao-viec-sub-agent.md`.
4. **Việc ghi tệp thì cô lập.** Mỗi CLI một worktree; sau khi xong, Claude xem `git diff` rồi mới chép sang cây chính.
5. **Giám sát.** Hỏi trạng thái mỗi vài phút. CLI treo (CPU đứng, đầu ra không đổi) thì dừng đúng tiến trình đó và báo chủ kênh; đừng bỏ đó đến khi có người hỏi.
6. **Claude vẫn chịu trách nhiệm.** Tự chạy test và đọc diff, không tin báo cáo của CLI. Không commit hay đẩy lên remote khi chủ kênh chưa duyệt.

## Không bao giờ gửi ra CLI bên thứ ba

- Khoá API, token, mật khẩu, cookies, nội dung `.env`.
- Dữ liệu khách hàng hay dữ liệu cá nhân.
- Ảnh hoặc giọng người thật.
- Mã độc quyền hoặc bất cứ tệp nằm trong «vùng cấm» của Hồ sơ dự án.

Dự án chưa khai vùng cấm trong `CLAUDE.md` thì hỏi chủ kênh trước khi giao. Việc đụng vùng cấm chỉ do Claude hoặc sub-agent Claude làm.

## Khi không có CLI, hết quota hoặc không giám sát được

Thay bằng **sub-agent Opus, ngữ cảnh mới, chỉ đọc**, đóng vai người phản biện: đưa cho nó bằng chứng và tiêu chí, không đưa lập luận của người làm. Nhược điểm: cùng hãng nên ít góc nhìn khác hơn. Việc chạy dài trên 20 phút thì Claude chia thành các lát ngắn, mỗi lát có điểm kiểm.
