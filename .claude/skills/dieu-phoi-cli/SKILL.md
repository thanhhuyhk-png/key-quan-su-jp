---
name: dieu-phoi-cli
description: Giao việc cho CLI bên thứ ba (Codex, Grok, Agy) và chọn bậc model của chúng. Nạp TRƯỚC khi giao bất kỳ việc nào ra Codex, Grok, Agy, hoặc khi cần quyết định có nên giao ra ngoài hay để Claude tự làm.
---

# Giao việc cho CLI bên thứ ba

Mặc định Claude tự làm. Chỉ giao ra ngoài khi việc dài trên 20 phút, lô việc lặp lớn (nhiều test, nhiều tệp mẫu), cần góc nhìn khác hãng, hoặc cần năng lực Claude không có. Kiểm quota của CLI trước khi giao.

Bản đầy đủ của luật: `huong-dan/dieu-phoi/cli-ben-thu-ba.md` và `huong-dan/dieu-phoi/luat-van-hanh.md`.

## Vai và bậc của từng CLI

| Vai | Codex | Agy | Grok |
|---|---|---|---|
| Đọc, gom, tìm tệp | bậc nhanh, rẻ (mô tả kiểu «fast and affordable») | flash | mặc định |
| Viết code, tài liệu, test | bậc chuẩn (mô tả kiểu «workhorse») | bậc vừa | mặc định |
| Plan lớn, thuật toán khó, review cuối | bậc sâu (mô tả kiểu «frontier»), effort cao | bậc cao | không dùng |

Tên bậc đổi theo phiên bản CLI. Danh sách model của CLI không khớp bảng thì hỏi chủ kênh chọn bậc.

## Chọn CLI

- Codex bậc sâu: thuật toán khó, bug logic, review chéo; cũng là chỗ hỏi tiếp khi Claude đã hỏi cố vấn mà vẫn kẹt.
- Codex bậc nhanh: lô test, mẫu lặp, đổi định dạng.
- Agy: ngữ cảnh rất lớn, giao diện, đa phương thức, phản biện kịch bản hoặc nội dung.
- Grok: tra cứu thời gian thực.

## Ràng buộc

- Việc cần ghi tệp: CLI chạy trong worktree riêng (`git worktree add`), không chạy trong cây chính.
- Không gửi khoá, mật khẩu, cookies, dữ liệu khách, ảnh hoặc giọng người thật, mã độc quyền ra CLI bên thứ ba. CLI chỉ chạy trong thư mục rỗng chứa brief, hoặc trong bản sao/worktree thưa đã loại vùng cấm; bật sandbox (`--sandbox`), chỉ đọc khi không cần ghi. Dự án chưa khai vùng cấm trong `CLAUDE.md` thì hỏi chủ kênh trước. Việc đụng vùng cấm chỉ do Claude hoặc sub-agent Claude làm.
- Brief theo mẫu ở `huong-dan/dieu-phoi/giao-viec-sub-agent.md`. Brief dài thì ghi `brief.md` rồi bảo CLI đọc tệp (dòng lệnh Windows có giới hạn độ dài).
- Thiếu CLI, hết quota, hoặc không giám sát được tiến trình nền: Claude tự làm, hoặc dùng sub-agent Opus ngữ cảnh mới làm người phản biện.

## Không có AK kit

Skill này không phụ thuộc AK kit. Chỗ cần chạy nền, Claude dùng công cụ chạy nền gốc của Claude Code; chỗ cần worktree, dùng `git worktree`. Xem `huong-dan/dieu-phoi/khong-co-ak-kit.md`.

## Cập nhật công cụ

Chỉ khi chủ kênh đồng ý, ở điểm an toàn, không khi đang dở việc. Mỗi CLI (Claude Code, Codex, Agy, Grok) cập nhật bằng trình cập nhật riêng của nó; không chạy cập nhật tự động.
