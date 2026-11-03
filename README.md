# Kit làm phim tài liệu lịch sử với Claude Code

Bộ quy trình để bạn dựng phim tài liệu cho YouTube từ A đến Z, do Claude Code làm cùng bạn: chọn ngách, chọn đề tài, nghiên cứu, viết kịch bản, đọc giọng, dựng, kiểm chất lượng, đăng, cắt Shorts. Bạn không cần biết lập trình.

## Cách dùng: lấy kit về, rồi mở Claude Code TRONG thư mục kit

Làm theo thứ tự này (xong ba việc ở mục bên dưới trước):

1. Lấy kit về và lập repo riêng cho kênh của bạn: mục «Lập repo kênh riêng» ở cuối tệp này (chép khối lệnh PowerShell, chạy một lần).
2. Nếu đang có cửa sổ Claude Code mở ở thư mục khác, thoát nó (gõ `/exit`).
3. Trong PowerShell, `cd GohaKit` rồi gõ `claude` (lần đầu Claude hỏi có tin cậy thư mục này không: chọn tin cậy).
4. Gõ một chữ: `bắt đầu`.

Vì sao phải mở Claude trong thư mục kit: Claude Code chỉ nạp luật an toàn khoá (`.claude/settings.json`) và các skill của kit (`.claude/skills/`) từ thư mục nó được mở. Mở ở chỗ khác thì Claude không thấy skill `goha-khoi-dong`, không có luật chặn đọc `.env`, và sẽ dừng lại bảo bạn mở lại cho đúng.

Từ đó Claude tự kiểm máy, báo thiếu gì và lệnh cài, rồi dẫn bạn đi từng bước. Chỗ nào cần quyết định hoặc tốn tiền, Claude dừng và hỏi bạn.

## Ba việc bạn tự làm bằng tay trước

Claude chưa chạy được khi thiếu ba thứ này, nên bạn cài trước.

### 1. Cài Claude Code

1. Mở trang cài đặt Claude Code của Anthropic (tìm «Claude Code install»), chọn hướng dẫn cho Windows.
2. Làm theo trang đó. Xong, mở cửa sổ dòng lệnh mới (PowerShell hoặc Windows Terminal) và gõ `claude --version`. Thấy số phiên bản là được.
3. Gõ `claude` lần đầu và đăng nhập tài khoản Claude của bạn khi được hỏi.

<!-- ảnh: trang cài đặt Claude Code và kết quả claude --version -->

### 2. Cài Git và GitHub CLI

1. Mở PowerShell (nhấn phím Windows, gõ PowerShell, Enter).
2. Chép dòng sau, dán vào, nhấn Enter:

   ```text
   winget install Git.Git GitHub.cli
   ```

3. Nếu hỏi đồng ý điều khoản, gõ `Y` rồi Enter. Chờ tới khi xong.
4. Đóng PowerShell, mở cửa sổ mới, kiểm tra: gõ `git --version` rồi `gh --version`. Cả hai ra số phiên bản là đạt.

<!-- ảnh: PowerShell chạy winget install Git.Git GitHub.cli -->

### 3. Đăng nhập GitHub bằng tài khoản đã được mời vào team

Kit là kho riêng tư của một tổ chức (GitHub Organization) và bạn chỉ có quyền ĐỌC (Read): bạn lấy kit về được nhưng không đẩy (push) gì lên đó. Chủ kit đã mời tài khoản GitHub của bạn; bạn cần nhận lời mời trước (email từ GitHub, bấm «Accept invitation»).

1. Trong PowerShell gõ `gh auth login`.
2. Chọn lần lượt: `GitHub.com` → `HTTPS` → `Yes` (xác thực Git) → `Login with a web browser`.
3. Màn hình hiện mã gồm 8 ký tự. Nhấn Enter, trình duyệt mở ra; dán mã vào, đăng nhập bằng đúng tài khoản đã được mời, bấm cho phép.
4. Kiểm tra: gõ `gh auth status`, phải thấy «Logged in to github.com».

<!-- ảnh: các bước gh auth login và trang nhập mã -->

Nếu sau này Claude báo không clone được repo, thường là do đăng nhập nhầm tài khoản chưa được mời. Gõ `gh auth logout`, rồi đăng nhập lại.

## Đường đi tổng quát

```text
Làm một lần:   K1 kiểm máy, cài đặt  →  K2 chọn ngách, top 20 kênh mẫu, hồ sơ kênh
Mỗi tập phim:  P0 chọn đề tài → P1 nghiên cứu → P2 kịch bản → P3 phân cảnh → P4 giọng
               → P5 dựng → P6 kiểm chất lượng → P7 bộ đăng → P8 Shorts
```

Mỗi bước dừng lại cho bạn duyệt trước khi sang bước sau. Chi tiết, yêu cầu máy, tài khoản và chi phí: `HUONG-DAN.md`.

## Lập repo kênh riêng

Repo kit chỉ đọc. Hồ sơ kênh (`ho-so-kenh/`), thư mục `kenh/` của bạn và các tập phim (`tap/`) là của bạn nên phải nằm trong repo RIÊNG của bạn (private, tài khoản GitHub của bạn). Cách làm, chọn MỘT:

**Cách A, gõ lệnh (khuyên dùng).** Trong PowerShell, ở thư mục bạn muốn đặt kit:

```text
gh repo clone https://github.com/goha-members/goha-lich-su-kit GohaKit
cd GohaKit
git remote rename origin kit
gh repo create <tên-repo-kênh-của-bạn> --private --source=. --remote=origin --push
```

Sau đó `kit` là remote chỉ để lấy bản mới, `origin` là repo riêng của bạn. Mọi `git commit` và `git push` của bạn đi vào `origin`.

**Cách B, bằng trình duyệt.** Vào trang repo kit, bấm «Use this template» rồi «Create a new repository» (chọn Private, đặt tên). Rồi:

```text
gh repo clone <tài-khoản-của-bạn>/<tên-repo-kênh-của-bạn> GohaKit
cd GohaKit
git remote add kit https://github.com/goha-members/goha-lich-su-kit
```

Cách B chỉ dùng được nếu chủ kit đã đánh dấu repo kit là «template»; nếu không thấy nút «Use this template» thì dùng cách A.

Đừng bao giờ `git push` lên remote `kit`: bạn không có quyền, và việc của bạn không thuộc về kit.

## Cập nhật bản mới

Chủ kit thỉnh thoảng phát hành bản mới (sửa lỗi, thêm skill). Để lấy về, bảo Claude: «cập nhật kit về bản mới», hoặc tự gõ trong thư mục kit:

```text
git pull kit main
```

Nếu bạn tạo repo bằng cách B, lần đầu phải thêm `--allow-unrelated-histories` (`git pull kit main --allow-unrelated-histories`) vì hai repo không chung lịch sử; từ lần sau gõ như trên. Nếu nhánh chính của kit không tên `main`, thay đúng tên (xem trang repo kit).

Khoá API của bạn (`.env`), `cau-hinh.toml`, `ho-so-kenh/`, các tập đã làm và các tệp `kenh/` bạn tự tạo không bị đè, vì chúng không có trong kit. Đừng tự sửa tệp thuộc kit (`tools/`, `.claude/skills/`, `kenh/bo-loc-chinh-sach-yt.md`…): sửa rồi `git pull` sẽ xung đột. Ngoại lệ là `kenh/cach-noi-da-chot.tsv`, nơi bạn thêm dòng khi sửa cách nói; xung đột ở tệp đó thì giữ các dòng của bạn. Nếu `git pull` báo xung đột ở chỗ khác, dừng lại và hỏi Claude hoặc chủ kit, đừng tự xoá.

## Hỗ trợ

Hỏi trong **nhóm Zalo hội viên Goha** (link nhóm nhận khi bạn vào cộng đồng).
Khi báo lỗi, gửi kèm: bước đang làm (K1, P4…), thông báo lỗi nguyên văn, và nội dung `kiem-may.md` nếu có. KHÔNG gửi `.env` hay bất kỳ khoá API nào.

<!--
Chủ kit cần điền trước khi phát hành (hội viên không thấy phần này). Tìm chuỗi «<điền:» trong kit/ để thấy hết các chỗ:
1. Link repo kit (README.md, hai khối lệnh ở mục «Lập repo kênh riêng»), và đánh dấu repo là «template» nếu muốn cách B chạy.
2. Kênh liên lạc hỗ trợ (README.md, mục «Hỗ trợ»).
3. Link sổ đăng ký đề tài chung (HUONG-DAN.md, mục 6, lớp 2) kèm quyền hội viên: comment hoặc điền form, không sửa dòng người khác.
4. Link Google Sheet top 20 mẫu, chế độ xem (kit/skills/tu-duy-top-20-ytb/SKILL.md mục «Bảng 14 tab» và references/mau-google-sheet.md).
5. Tên nhánh chính của repo kit (README.md đang giả định `main`) và quyền Read của team trong Organization.
6. Ảnh minh hoạ các bước cài (các chú thích HTML bắt đầu bằng chữ «ảnh:» trong README.md).
-->
