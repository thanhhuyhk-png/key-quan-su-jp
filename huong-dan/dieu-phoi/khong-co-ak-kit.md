# Khi không có AK kit

Một số skill và tài liệu trong kit nhắc các lệnh dạng `ak:*` (của AK kit). AK kit là tuỳ chọn. Không có nó, mọi việc vẫn làm được bằng công cụ gốc của Claude Code, chỉ mất vài lệnh tiện.

| Chỗ ghi | Làm thay bằng |
|---|---|
| `ak:scout` (định vị tệp) | Công cụ Glob và Grep, hoặc sub-agent `Explore` của Claude Code |
| `ak:plan` (lập kế hoạch) | Tự viết `plans/<ngày>-<slug>/plan.md`: mục tiêu, ràng buộc, tiêu chí nghiệm thu, các bước, rủi ro. Có thể dùng chế độ plan của Claude Code |
| `ak:cook` (làm theo plan) | Làm lần lượt từng bước của plan, chạy kiểm sau mỗi bước |
| `ak:debug`, `ak:fix` | Tìm nguyên nhân gốc có bằng chứng (log, kết quả chạy) trước khi sửa; sửa xong chạy lại đúng lệnh đã lỗi |
| `ak:test` | Chạy lệnh kiểm của dự án (ghi ở Hồ sơ dự án trong `CLAUDE.md`) |
| `ak:code-review` | Giao một sub-agent ngữ cảnh mới, chỉ đọc, review so với tiêu chí; hoặc lệnh `/review` |
| `ak:handoff` | Tự viết `plans/handoffs/<ngày>-<slug>.md` theo mục 5 của `luat-van-hanh.md` |
| `ak:brainstorm` | Cho Claude hỏi ngược chủ kênh từng câu một về ràng buộc và trường hợp biên, rồi tóm lại bằng 5 mục: vấn đề, ràng buộc, tiêu chí thành công, tình huống lỗi, ngoài phạm vi |
| `ak:worktree` | `git worktree add` và `git worktree remove` |
| `ak:git` | Lệnh `git` thường, commit kiểu `<loại>: <mô tả>` |
| `ak:diagram` | Viết sơ đồ bằng khối mã mermaid trong tệp Markdown |
| `ak run`, `ak:handoff --dispatch` | Tự chạy CLI bên thứ ba theo `cli-ben-thu-ba.md`, hoặc để Claude tự làm |

## Agent cố vấn «kongming»

Chỗ nào nhắc agent `kongming` (cố vấn model mạnh nhất): spawn một sub-agent chỉ cố vấn bằng **model mạnh nhất bạn có**, ngữ cảnh mới, chỉ đọc. Đưa cho nó: nhiệm vụ, bằng chứng đã thu, các cách đã thử, câu hỏi cụ thể. Nó chỉ trả lời khuyên; người gọi vẫn là người làm và chịu trách nhiệm. Trần số lượt xem `luat-van-hanh.md` mục 2. Nếu chỉ có Opus thì dùng sub-agent Opus.

## Skill kèm theo

Các skill trong kit (`dieu-phoi-cli`, `delegate-cli-agents`, `video-harness`, `tu-duy-he-thong`) có thêm một đoạn «Không có AK kit» ở chỗ cần. Skill vẫn chạy đủ khi chỉ có Claude Code.
