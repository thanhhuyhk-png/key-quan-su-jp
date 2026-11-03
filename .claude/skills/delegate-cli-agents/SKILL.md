---
name: delegate-cli-agents
description: "Giao một phase kế hoạch cho Grok CLI hoặc Codex CLI chạy nền (song song với Claude): chia việc theo tệp, cô lập worktree, viết prompt handoff chuẩn, giám sát chống treo, tự kiểm bằng mutation. Dùng khi cần tăng tốc bằng nhiều agent. Kích hoạt khi nói 'giao Grok/Codex', 'chạy song song', 'delegate', 'tăng tiến độ bằng agent phụ'."
argument-hint: "<đường-dẫn-phase> [--agent grok|codex] [--worktree]"
license: MIT
---

# Delegate CLI agents (Grok / Codex): chạy song song, tự kiểm

Giấy phép: MIT theo khai báo gốc; nguồn gốc chưa xác định (chủ kit không còn nhớ tác giả). Giữ nguyên dòng `license` ở đầu tệp khi chia sẻ lại.

Playbook để Claude (điều phối) giao một **phase đã lập kế hoạch** cho agent CLI bên thứ ba (`grok`, `codex`) chạy nền, rồi **tự giám sát và nghiệm thu**. Đúc kết từ một dự án dựng video trên Windows.

> Nguyên tắc gốc: agent CLI làm việc, **Claude vẫn chịu trách nhiệm**: đọc diff, chạy test và mutation, quyết định gộp. KHÔNG tin báo cáo của agent; tự kiểm bằng chứng.

Luật an toàn khi giao ra ngoài (không gửi khoá, dữ liệu khách, ảnh hay giọng người thật; thư mục rỗng hoặc worktree; sandbox) nằm ở `huong-dan/dieu-phoi/cli-ben-thu-ba.md`. Đọc trước khi giao.

## 1. Khi nào dùng, khi nào KHÔNG

- **Dùng** khi có từ 2 mảng việc **tách sạch theo tệp** (ví dụ giao diện ∥ máy chủ), mỗi mảng là một phase plan rõ.
- **KHÔNG song song** khi các phase **giẫm chung tệp** (tệp API chung, bảng chuỗi song ngữ, cấu hình chung) hoặc có phụ thuộc thứ tự: chạy đồng thời sẽ hỏng tệp hoặc xung đột khi gộp. Làm tuần tự, hoặc tách worktree rồi gộp.
- Mặc định giao **đúng MỘT phase mỗi lượt** cho mỗi agent (agent chạy không giao diện không có đường chờ duyệt giữa chừng).

## 2. Chia việc: kiểm giao lộ tệp TRƯỚC

Liệt kê tệp mỗi phase sẽ tạo hoặc sửa. Hai phase giao nhau ở bất kỳ tệp nào thì **không** cho chạy cùng một cây làm việc.

## 3. Cô lập bằng git worktree (khi cần)

Nếu agent sửa tệp mà agent kia có thể ĐỌC lúc chạy, cho nó worktree riêng:

```bash
git worktree add -b <nhánh> "<thư-mục-worktree>" HEAD
```

Thư mục phụ thuộc bị gitignore (ví dụ `node_modules`) không có trong worktree: tạo liên kết thư mục (junction trên Windows, qua tệp `.bat` vì Git Bash hay nuốt cờ `/J`) từ cây chính, hoặc cài lại trong worktree. Chép các tệp plan mới (chưa commit ở cây chính) vào worktree để agent đọc được.

## 4. Dặn agent làm việc có kỷ luật

Ghi trong prompt: đọc kế hoạch từ tệp phase; định vị code bằng tìm kiếm có mục tiêu thay vì đọc mò cả tệp; làm theo từng lát nhỏ; chạy test sau mỗi lát; tự review trước khi báo xong; với bug thì chứng minh nguyên nhân gốc trước khi vá.

Câu mẫu: *«Định vị bằng tìm kiếm, bám tệp phase, chạy test sau mỗi lát, tự soát lại diff trước khi báo xong. KHÔNG bịa; chỗ chưa chắc thì đọc tệp:dòng.»*

**Không có AK kit:** các bước trên dùng công cụ gốc (Grep, Glob, đọc tệp, lệnh test của dự án); AK kit chỉ là đường tắt, không bắt buộc. Xem `huong-dan/dieu-phoi/khong-co-ak-kit.md`.

## 5. Prompt handoff: cấu trúc chuẩn

Ghi thành tệp (ví dụ `plans/<plan>/prompt-giao-<agent>-<phase>.md`; tệp dài thì để CLI đọc tệp, đừng dán vào dòng lệnh). Các mục theo thứ tự:

1. **Bối cảnh** (một đoạn) + trỏ tới tệp phase.
2. **Quyết định đã chốt**: kiến trúc, mặc định; để agent khỏi hỏi lại.
3. **Việc, chia lát mỏng**, đánh số; mỗi lát có điểm **DỪNG chờ duyệt mẫu**.
4. **Bẫy đã biết** (kiểu xuống dòng CRLF, các guard, đường cũ không được phá).
5. **Kiểm bằng mắt** (việc giao diện): cách chụp và đo.
6. **Lệnh kiểm thử**: đủ bộ, kèm yêu cầu **đo nền trước khi sửa** và **mutation thật (bảng đột biến)**.
7. **Ranh giới**: không commit, không đẩy, không đổi nhánh; không thêm thao tác ngoài phase; không đụng phần của agent khác.
8. **Báo cáo** vào `plans/reports/<agent>-<ngày>-<slug>.md`.
9. **Dừng ở đâu**: xong phase thì dừng, không tự đi tiếp.

## 6. Phóng agent (nền)

```bash
# Grok
grok --prompt-file "<prompt.md>" --cwd "<thư-mục-làm-việc>" --always-approve \
     --permission-mode bypassPermissions --output-format plain
#   Cảnh báo: --permission-mode acceptEdits có thể treo vô hạn; dùng bypassPermissions,
#   và CHỈ trong thư mục cô lập (xem cli-ben-thu-ba.md).

# Codex (chọn bậc model tiết kiệm token nếu việc nhẹ)
codex exec --model <tên-model> -C "<thư-mục-làm-việc>" --skip-git-repo-check "$(cat '<prompt.md>')"
```

Chạy nền bằng chế độ chạy nền của Claude Code. Ghi lại: agent, PID, cổng, worktree.

## 7. Giám sát: hỏi định kỳ, chống treo

**Mỗi 3 đến 5 phút** xem một lần. Đừng để chạy rồi bỏ đó tới khi chủ kênh hỏi.

```bash
c1=$(powershell -NoProfile -Command "(Get-Process <tên>).CPU"); sleep 12
c2=$(powershell -NoProfile -Command "(Get-Process <tên>).CPU")
# CPU tăng dưới ~0,5 giây trong 12 giây, đầu ra đứng lâu => nghi TREO
```

Treo thì dừng **đúng PID** (kiểm PID theo cổng, không khớp mờ theo dòng lệnh) và dọn tiến trình con mồ côi: `taskkill //PID <pid> //T //F`. Không đụng tiến trình hay cổng của chủ kênh.

Việc giao diện: chụp ảnh trang bằng trình duyệt không giao diện và XEM ảnh. Phần tử `<video>` thường ra đen khi chụp; đo pixel qua canvas thay vì tin ảnh.

## 8. Nghiệm thu: tự kiểm, KHÔNG tin báo cáo

1. Chạy đủ test và kiểm kiểu của mọi gói bị đụng. So với số đo nền: không đổi hành vi thì kết quả phải bằng nhau, thêm việc thì tăng.
2. **Mutation thật**: đổi một dòng then chốt, test phải ĐỎ đúng chỗ, rồi hoàn nguyên bằng **sửa ngược** (không dùng `git checkout`, vì sẽ xoá cả phần việc chưa commit). Tệp CRLF: dùng `grep` xác nhận mutation đã vào tệp trước khi chạy (regex neo xuống dòng trượt âm thầm).
3. Soi diff: có đúng tệp của phase không, có đè tệp của agent kia không, có làm yếu assertion của test cũ không.
4. Việc giao diện: mở ảnh chụp ra xem, rồi trình chủ kênh duyệt bằng mắt.

## 9. Gộp

KHÔNG commit hay đẩy khi chủ kênh chưa duyệt. Với worktree: đọc `git -C <worktree> diff`, gộp các tệp **rời nhau** sang cây chính sau khi review. Xong thì gỡ worktree và liên kết thư mục, ghi kết quả vào plan.

## Checklist nhanh

- [ ] Tệp hai phase rời nhau (hoặc đã tách worktree)
- [ ] Prompt có: quyết định đã chốt, lát mỏng và điểm dừng, bẫy, lệnh test và mutation, ranh giới, báo cáo, nơi dừng
- [ ] Phóng nền, ghi PID, cổng, worktree
- [ ] Giám sát mỗi 3 đến 5 phút; treo thì dừng đúng PID, dọn tiến trình mồ côi
- [ ] Tự chạy test, kiểm kiểu và ít nhất một mutation thật
- [ ] Kiểm mắt (nếu giao diện), trình chủ kênh duyệt, rồi mới gộp
