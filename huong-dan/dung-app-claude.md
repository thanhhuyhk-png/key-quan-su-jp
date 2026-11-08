# Lấy kit Goha Lịch Sử về máy và làm việc bằng app Claude

Không cần mở cửa sổ lệnh (Terminal, PowerShell). Bạn chỉ bấm nút và dán chữ vào app Claude; phần kỹ thuật Claude làm hộ.

## Chọn cách lấy kit

| Cách | Hợp với ai | Cần Git, GitHub CLI | Cất công việc | Lấy bản kit mới |
|---|---|---|---|---|
| **1. Tải ZIP** (đơn giản nhất) | Người mới, muốn bắt đầu ngay | Không | Tự chép thư mục sang ổ khác hoặc Google Drive | Tải ZIP mới, nhờ Claude chép phần của bạn sang |
| 2. Nhờ app Claude lấy bằng Git | Muốn cất công việc lên GitHub, cập nhật một câu lệnh | Claude cài hộ | Repo riêng tư trên GitHub của bạn | `cập nhật kit về bản mới` |
| 3. Tự gõ lệnh PowerShell | Người quen cửa sổ lệnh | Tự cài | Như cách 2 | Như cách 2 |

Không chắc thì chọn **Cách 1**. Sau này muốn cất lên GitHub, nhờ Claude chuyển sang Cách 2 mà không mất việc đã làm (mục 1.4 bên dưới).

## Cần có trước (mọi cách)

- Máy Windows 10/11, ổ đĩa còn trống ít nhất 60 GB cho thư mục làm phim.
- **App Claude** bản máy tính, đã đăng nhập tài khoản Claude có dùng được Claude Code.
- Tài khoản **GitHub** đã bấm **Join** trong email mời vào tổ chức `goha-members` (không thấy email thì xem Thư rác, hoặc đăng nhập github.com rồi bấm hình cái chuông ở góc trên).
- **Goha AVS** (bộ cài hội viên) nếu chọn mức chạy Đầy đủ; mức Tiết kiệm và Miễn phí không bắt buộc.

## Cách 1. Tải ZIP rồi làm với app Claude (đơn giản nhất)

### 1.1 Tải và giải nén

1. Mở trình duyệt, vào **github.com/goha-members/goha-lich-su-kit**. Đăng nhập đúng tài khoản GitHub đã Join (trang báo 404 là chưa Join hoặc đăng nhập nhầm tài khoản).
2. Bấm nút xanh **Code**, chọn **Download ZIP**. Máy tải về tệp `goha-lich-su-kit-main.zip`.
3. Tạo thư mục `D:\Goha` (chuột phải → **Mới** → **Thư mục**). Chép tệp ZIP vào đó.
4. Chuột phải tệp ZIP → **Extract All…** (Giải nén tất cả) → **Extract**.
5. Mở vào trong thư mục vừa giải nén cho tới khi thấy tệp `CLAUDE.md`, `README.md` và thư mục `.claude`. Thường phải vào hai lớp: `goha-lich-su-kit-main\goha-lich-su-kit-main`. **Thư mục chứa `CLAUDE.md` chính là thư mục kit.**
6. Nên đổi tên thư mục kit cho gọn, ví dụ `D:\Goha\GohaKit`, rồi xoá tệp ZIP và lớp thư mục thừa bên ngoài.

### 1.2 Mở app Claude đúng trong thư mục kit

1. Mở app Claude, chuyển sang thẻ **Code** (nằm cạnh Chat và Cowork).
2. Bấm **+ New** ở thanh bên (hoặc Ctrl+N) để tạo phiên mới.
3. Ở hàng nút ngay dưới ô chat: ô môi trường chọn **Local** (chạy trên máy bạn), rồi bấm **nút hình thư mục** và chọn thư mục kit (thư mục có `CLAUDE.md`). Phải chọn thư mục **trước** khi gửi tin đầu tiên. App hỏi có tin cậy thư mục này không thì chọn tin cậy.

Vì sao phải đúng thư mục: Claude chỉ thấy các skill của kit và luật giữ an toàn khoá API khi được mở đúng thư mục này. Chọn nhầm thư mục ngoài, Claude sẽ dừng lại và nhắc bạn mở lại. Từ nay, lần nào làm kênh cũng mở thư mục này.

Rồi làm tiếp phần **«Sau khi có kit: gõ bắt đầu»** bên dưới.

### 1.3 Cất công việc và lấy bản kit mới (bản ZIP)

- **Cất công việc:** thỉnh thoảng chép cả thư mục kit sang ổ khác hoặc Google Drive. Thư mục `ho-so-kenh\` là hồ sơ kênh, `tap\` là các tập phim của bạn.
- **Lấy bản kit mới** khi chủ kit báo: tải ZIP mới như 1.1, giải nén ra **thư mục mới** (đừng đè lên thư mục cũ), mở phiên mới ở thư mục mới như 1.2, rồi gõ:

  ```text
  chép phần của tôi từ D:\Goha\GohaKit
  ```

  (thay bằng đường dẫn thư mục cũ của bạn). Claude liệt kê những gì sẽ chép: khoá, cấu hình, hồ sơ kênh, tập phim, phần riêng, cách nói đã chốt; hỏi bạn một lần rồi chép. Thư mục cũ không bị xoá; khi đã ưng bản mới, bạn tự xoá thư mục cũ.

### 1.4 Chuyển từ ZIP sang GitHub (khi muốn)

Gõ trong phiên ở thư mục kit:

```text
nối thư mục kit này với GitHub: tạo repo PRIVATE tên ten-kenh-cua-ban trên tài khoản của tôi để cất công việc
```

Claude cài Git và GitHub CLI nếu thiếu (hỏi bạn trước), nhờ bạn đăng nhập GitHub (như 2.2 bên dưới), rồi nối thư mục với kit gốc mà không đổi tệp nào của bạn. Từ đó dùng được các câu hằng ngày của Cách 2.

## Cách 2. Nhờ app Claude lấy kit bằng Git

### 2.1 Mở Claude Code trong một thư mục trống

Tạo thư mục trống `D:\Goha`, rồi mở phiên như 1.2 nhưng chọn thư mục `D:\Goha`.

### 2.2 Dán lời nhờ Claude lấy kit về

Dán nguyên đoạn dưới vào ô chat, sửa `ten-kenh-cua-ban` thành tên ngắn không dấu (ví dụ `su-viet-minh`), rồi gửi:

```text
Giúp tôi lấy kit Goha Lịch Sử về máy. Làm lần lượt, mỗi bước báo tôi một câu:
1. Kiểm Git và GitHub CLI (gh); thiếu thì cài bằng winget. Git chưa khai tên và email thì hỏi tôi rồi khai.
2. Đăng nhập GitHub bằng gh theo kiểu trình duyệt (gh auth login --web), chạy lệnh ở chế độ nền: đưa tôi mã 8 ký tự và link để tôi tự nhập, chờ tôi báo xong. Đã đăng nhập sẵn thì bỏ qua.
3. Clone repo goha-members/goha-lich-su-kit vào thư mục GohaKit tại đây.
4. Trong GohaKit: đổi tên remote origin thành kit, rồi tạo repo PRIVATE tên ten-kenh-cua-ban trên tài khoản GitHub của tôi làm origin và push lên.
5. Báo tôi đường dẫn đầy đủ của thư mục GohaKit.
```

Trong lúc chạy:

- Claude xin phép chạy lệnh: bấm **Allow** (hoặc **Allow once**). Bấm **Deny** là Claude dừng bước đó. Windows hỏi quyền quản trị khi cài Git hoặc gh: bấm **Yes**.
- Đến bước đăng nhập: Claude đưa một **mã 8 ký tự** (dạng `ABCD-1234`), mã cũng đã được chép sẵn vào bộ nhớ tạm. Mở link Claude đưa
  (github.com/login/device), dán mã (Ctrl+V), bấm **Authorize**, rồi gõ «xong» cho Claude. Làm trong khoảng 15 phút, quá giờ mã hết hạn thì
  nói Claude «làm lại bước 2». Nhớ đăng nhập đúng tài khoản GitHub đã Join.
- Claude báo «Repository not found»: tài khoản chưa Join lời mời, hoặc đăng nhập nhầm tài khoản. Join xong thì nói Claude «làm lại bước 2, 3».

Xong bước này bạn có thư mục `D:\Goha\GohaKit`: bản kit trên máy, nối với repo riêng của bạn để cất công việc.

### 2.3 Mở phiên mới ĐÚNG trong thư mục kit

Đây là bước hay bị sót. Trong thẻ Code bấm **+ New** tạo **phiên mới**, lần này bấm nút thư mục chọn `D:\Goha\GohaKit`
(không phải `D:\Goha`). Rồi làm tiếp phần «Sau khi có kit» bên dưới.

## Cách 3. Tự gõ lệnh PowerShell

Dành cho người quen cửa sổ lệnh: làm theo `README.md` (mục «Lập repo kênh riêng») hoặc `huong-dan/bat-dau-nhanh.md`.

## Sau khi có kit: gõ «bắt đầu»

Trong phiên mở đúng thư mục kit, gõ:

```text
bắt đầu
```

Claude chạy K1: kiểm máy, chỉ cách cài thứ còn thiếu (Python, Node.js, ffmpeg…; hỏi bạn trước khi cài), hỏi chỗ để thư mục làm phim, giúp bạn đặt khoá API và chọn mức chạy (có mức Miễn phí). Sau đó là K2 (chọn ngách, top 20 kênh mẫu, hồ sơ kênh của bạn) rồi tới làm tập đầu từ P0. Cứ làm theo câu Claude hỏi. Claude cài thêm phần mềm thì sau khi cài nhớ **tắt hẳn app Claude** (chuột phải biểu tượng Claude ở khay đồng hồ → **Quit**) **rồi mở lại**.

Đặt khoá API (chỉ cần cho mức Đầy đủ, Tiết kiệm; mức Miễn phí không cần khoá nào):

1. Mở thư mục kit trong File Explorer, chuột phải tệp `khoa-api.mau` → **Mở bằng** → **Notepad**.
2. Dán từng khoá ngay sau dấu `=` của dòng tương ứng, không để dấu cách, không ngoặc kép.
3. Bấm **File → Save As**, ô **Save as type** chọn **All files**, ô tên gõ `.env`, bấm **Save**.
4. Báo Claude «xong». Claude chạy lại kiểm máy và chỉ báo khoá **có** hay **thiếu**.

Không bao giờ dán khoá vào ô chat.

## Câu dùng hằng ngày

| Muốn | Gõ vào Claude |
|---|---|
| Không biết đang ở đâu | `tôi đang ở bước nào, bước tiếp theo là gì?` |
| Cất công việc lên repo riêng (Cách 2, 3; sau mỗi bước duyệt xong) | `commit và push lên repo riêng của tôi` |
| Lấy bản kit mới khi chủ kit báo (Cách 2, 3) | `cập nhật kit về bản mới` |
| Lấy bản kit mới (Cách 1, ZIP) | tải ZIP mới, mở phiên ở thư mục mới, gõ `chép phần của tôi từ <thư mục cũ>` |

## Làm kit theo cách của bạn mà vẫn cập nhật được

Kit chừa sẵn hai chỗ của riêng bạn, bản cập nhật kit không bao giờ đụng tới: thư mục `rieng/` và các skill tên `rieng-…`. Gõ cho Claude, ví dụ:

| Muốn | Gõ vào Claude |
|---|---|
| Đổi cách làm một bước | `làm bản riêng của bước kịch bản: mở đầu bằng một câu hỏi gợi tò mò` |
| Đặt thói quen chung | `ghi vào phần riêng: luôn trả lời ngắn, báo giá trước khi đọc giọng` |
| Tạo kỹ năng mới cho kênh | `tạo skill riêng viết mô tả video theo giọng kênh tôi` |
| Xem mình đã chỉnh những gì | `phần riêng của tôi đang có gì?` |

Claude chép skill của kit thành bản `rieng-…`, sửa bản chép, rồi ghi vào `rieng/ghi-de.md` rằng bước đó dùng bản riêng. Xong thì mở **phiên mới** ở thư mục kit để Claude nạp bản riêng. Phần riêng không nới được luật cứng nội dung sử Việt, luật giữ khoá API, bước tốn tiền phải hỏi, quyền tư liệu và chính sách YouTube.

## Ba điều cần nhớ

1. **Chép quy trình, không chép chủ đề.** Tập mẫu trong `mau/` chỉ để học, cấm đăng lại, cấm dùng lại câu chữ, đề tài, giọng, khung hình. Tên kênh, giọng, nhận diện của bạn phải là của riêng bạn.
2. **Không gửi khoá API cho ai**, kể cả khi hỏi trong nhóm. Kit đã chặn để khoá không lên GitHub.
3. **Muốn kit làm theo cách của bạn thì nhờ Claude làm bản riêng, đừng sửa thẳng tệp của kit** (`tools/`, `.claude/skills/goha-*`, `kenh/bo-loc-chinh-sach-yt.md`…). Sửa thẳng thì lần cập nhật kit sẽ bị vướng.

Kẹt ở đâu: hỏi trong nhóm Zalo hội viên Goha, gửi kèm bạn đang ở bước nào, câu báo lỗi nguyên văn và nội dung tệp `kiem-may.md` trong thư mục kit (không gửi tệp `.env`). Hướng dẫn đầy đủ hơn (cho ai quen dùng cửa sổ lệnh): `huong-dan/bat-dau-nhanh.md` và `HUONG-DAN.md`.
