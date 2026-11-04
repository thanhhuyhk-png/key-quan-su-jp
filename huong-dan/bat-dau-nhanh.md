# Bắt đầu nhanh: từ máy trống tới tập phim đầu tiên

Bản tóm tắt thao tác (từ buổi hướng dẫn hội viên 04/11/2026). Chi tiết đầy đủ: `README.md` (cài đặt) và `HUONG-DAN.md` (quy trình, chi phí, sự cố). Mọi lệnh dưới đây gõ trong **PowerShell** trên Windows 10/11, trừ chỗ ghi «gõ trong Claude Code».

---

## Trước khi bắt đầu

1. Mở email từ GitHub mời vào **goha-members**, bấm **Join goha-members**. Chưa có tài khoản GitHub thì tạo bằng **đúng email đã mua hàng**. Không thấy email thì xem Thư rác hoặc tab Quảng cáo của Gmail.
2. Cài sẵn **Claude Code** (tìm «Claude Code install», chọn Windows) và đăng nhập tài khoản Claude.
3. Ổ đĩa còn trống ít nhất 60 GB.

---

## Phần 1. Tạo thư mục trên máy và đưa kit về

### Bước 1.1: Cài Git và GitHub CLI (một lần)

Mở PowerShell (phím Windows → gõ PowerShell → Enter), dán:

```powershell
winget install Git.Git GitHub.cli
```

Hỏi điều khoản thì gõ `Y`. Xong thì **đóng PowerShell, mở cửa sổ mới**, kiểm tra:

```powershell
git --version
gh --version
```

Hai dòng đều ra số phiên bản là đạt.

### Bước 1.2: Khai tên cho Git (một lần; README chưa có bước này, thiếu thì commit báo lỗi)

```powershell
git config --global user.name "Tên của bạn"
git config --global user.email "<email GitHub của bạn>"
```

### Bước 1.3: Đăng nhập GitHub bằng đúng tài khoản đã nhận lời mời

```powershell
gh auth login
```

Chọn lần lượt: `GitHub.com` → `HTTPS` → `Yes` (xác thực Git bằng tài khoản GitHub) → `Login with a web browser`. Màn hình hiện mã 8 ký tự: nhấn Enter, trình duyệt mở, dán mã, bấm cho phép. Kiểm tra:

```powershell
gh auth status
```

Phải thấy «Logged in to github.com account <tên của bạn>».

### Bước 1.4: Tạo thư mục làm việc

Lệnh dưới tạo thư mục `Goha` trong thư mục người dùng của bạn (`$HOME`). Kit nhẹ nên để đâu cũng được; media nặng đi vào thư mục `output` khai riêng ở K1. Muốn đặt ở ổ khác thì thay `$HOME` bằng ổ đó, ví dụ ổ D.

```powershell
mkdir $HOME\Goha
cd $HOME\Goha
```

### Bước 1.5: Lấy kit về và lập repo kênh RIÊNG của bạn

Repo kit chỉ cho **đọc**. Công việc của bạn (hồ sơ kênh, các tập) nằm trong repo riêng, private, trên tài khoản GitHub của bạn. Dán cả khối (đổi `ten-kenh-cua-ban` thành tên không dấu, ví dụ `su-viet-ke-chuyen`):

```powershell
gh repo clone https://github.com/goha-members/goha-lich-su-kit GohaKit
cd GohaKit
git remote rename origin kit
gh repo create ten-kenh-cua-ban --private --source=. --remote=origin --push
```

Kiểm tra:

```powershell
git remote -v
```

Phải thấy hai remote: **kit** (trỏ `goha-members/goha-lich-su-kit`, chỉ để lấy bản mới) và **origin** (trỏ repo riêng của bạn). Thư mục kit trên máy: `$HOME\Goha\GohaKit`.

> Lỗi «Repository not found» khi clone: chưa bấm Join lời mời, hoặc đăng nhập nhầm tài khoản. Gõ `gh auth logout`, rồi làm lại bước 1.3.

---

## Phần 2. Mở Claude Code đúng chỗ, đồng bộ GitHub để commit và push

### Bước 2.1: Luôn mở Claude Code TRONG thư mục kit

```powershell
cd $HOME\Goha\GohaKit
claude
```

Lần đầu Claude hỏi có tin cậy thư mục không: chọn tin cậy. Rồi gõ trong Claude Code:

```text
bắt đầu
```

Vì sao: Claude chỉ nạp các skill của kit và luật chặn đọc khoá API từ thư mục nó được mở. Mở chỗ khác thì Claude sẽ bảo bạn thoát (`/exit`) và mở lại cho đúng.

### Bước 2.2: Commit và push công việc của bạn

Bạn không cần nhớ lệnh Git. Sau mỗi bước duyệt xong, gõ trong Claude Code:

```text
commit và push lên repo riêng của tôi
```

Claude sẽ `git add`, `git commit` kèm lời mô tả, rồi `git push` lên **origin**. Muốn tự làm thì trong PowerShell ở thư mục kit:

```powershell
git add -A
git commit -m "P0: chon de tai EP001"
git push origin main
```

Ba điều cần nhớ:
- **Không bao giờ push lên `kit`** (bạn không có quyền, Git sẽ từ chối).
- `.env` (khoá API) và `cau-hinh.toml` không bao giờ lên Git: kit đã chặn sẵn.
- Video và media nặng nằm ở thư mục `output` (khai trong `cau-hinh.toml`), không nằm trong repo.

### Bước 2.3: Lấy bản kit mới khi chủ kit phát hành

Gõ trong Claude Code: `cập nhật kit về bản mới`, hoặc trong PowerShell:

```powershell
git pull kit main
```

Đừng sửa tệp thuộc kit (`tools/`, `.claude/skills/`…), nếu không `git pull` sẽ xung đột. Báo xung đột thì dừng lại, hỏi Claude hoặc nhóm Zalo, đừng tự xoá.

---

## Phần 3. Các phase và skill chạy như thế nào

### Bức tranh chung

```text
Làm một lần:   K1 kiểm máy, cài đặt  →  K2 chọn ngách, top 20 kênh mẫu, hồ sơ kênh
Mỗi tập phim:  P0 chọn đề tài → P1 nghiên cứu → P2 kịch bản → P3 phân cảnh → P4 giọng
               → P5 dựng → P6 kiểm chất lượng → P7 bộ đăng → P8 Shorts
```

- Mỗi bước có **một skill** (một bộ hướng dẫn Claude tự nạp). Bạn **không phải gọi tên skill**: gõ `bắt đầu`, Claude tự xem bạn đang ở đâu và chạy đúng skill.
- Mỗi bước kết thúc bằng **cổng DỪNG**: Claude trình kết quả, bạn xem, gõ **«duyệt»** thì mới sang bước sau. Chưa ưng thì nói sửa gì.
- **Bước tốn tiền** (đọc giọng, chép lời, tiếng động): Claude báo trước gọi gì, ước tính bao nhiêu, chờ bạn gõ «đồng ý».
- **Làm tiếp tập dở:** trạng thái mỗi tập ghi ở `tap/<EPxxx-slug>/ke-hoach/progress.md`. Mở lại Claude, gõ `bắt đầu`, Claude hỏi làm tập mới hay làm tiếp tập nào.

### Bảng skill theo bước

| Bước | Skill | Claude làm gì | Bạn duyệt gì |
|---|---|---|---|
| K1 | `goha-khoi-dong` | Kiểm máy (Python, Node, ffmpeg, Chrome…), in thứ thiếu kèm lệnh cài, tạo `cau-hinh.toml`, cho bạn chọn mức chạy (Đầy đủ / Tiết kiệm / Miễn phí) | Mức chạy |
| K2 | `tu-duy-top-20-ytb` rồi `goha-ho-so-kenh` | Tìm và đo kênh mẫu, chọn TOP 20 và Model Link, rồi dựng hồ sơ kênh, màu, logo, giọng | Ngách, Model Link, thương hiệu |
| P0 | `goha-ls-chon-de-tai` | Chọn 8–12 đề tài từ sheet top 20, chấm điểm, kiểm trùng bằng máy | Đề tài và góc kể |
| P1 | `goha-ls-nghien-cuu` | Sổ số liệu có nguồn, sổ tư liệu hình có hạng bản quyền | Sổ đủ, nguồn tin được |
| P2 | `goha-ls-kich-ban` | Hook chấm điểm, viết, phản biện kép, quét chính sách YouTube | Kịch bản |
| P3 | `goha-ls-phan-canh` | Chia cảnh, chọn hình từng câu, ảnh tĩnh duyệt trước | Storyboard |
| P4 | `goha-ls-giong` | Đọc giọng cả bài rồi cắt câu, đo mốc | Chi phí giọng; nghe thử |
| P5 | `goha-ls-dung` | Dựng hình và âm cả tập | 3 phút đầu |
| P6 | `goha-ls-qc` | Đo âm lượng −14 LUFS, chép lời so ≥ 97 %, soi bản đồ | Xem cả phim |
| P7 | `goha-ls-dang` | Tiêu đề, mô tả, thẻ, 3 thumbnail, phụ đề dịch | Gói đăng |
| P8 | `goha-ls-shorts` | Cắt 3–5 Shorts dọc kèm bìa | Shorts đầu tiên |

Skill dùng chung (Claude tự gọi khi cần): `video-harness` (kiểm soát chất lượng khi dựng), `tu-duy-he-thong` (trước việc lớn).

### Sau P0: đăng ký đề tài để không trùng hội viên khác

Đề tài duyệt xong ở P0 thì **tự gửi Form**: https://docs.google.com/forms/d/e/1FAIpQLSeO00Ix7ebS5OTSvCLKkKgPs5cpW-oDfl5TTTMPj491ZARjFg/viewform

Ghi 4 ô: **Đề tài**, **Góc kể**, **Ngôn ngữ** (mã: `vi`, `en`, `fr`…), **Hội viên** (tên kênh). Ai đăng ký trước được làm. Sổ xem chung (chỉ đọc): https://docs.google.com/spreadsheets/d/1T-4n3Z19BARWsywfG35p4591v3Tfq7USUHgKslU5fiU/edit?usp=sharing. Claude tự tải sổ này mỗi lần kiểm trùng.

Đề tài của tập mẫu (Điện Biên Phủ 1954…) bị máy chặn sẵn: kit cho bạn **cách làm**, không cho bạn **chủ đề**.

---

## Phần 4. Tìm từ khoá chủ đề theo ý muốn và chạy lại Tư duy Top 20

### 4.1. Khi nào chạy lại

- **Lần đầu** (K2): bắt buộc, để có TOP 20 và Model Link của **ngách bạn chọn**.
- **Đổi hoặc mở rộng ngách** (ví dụ từ «chiến tranh Việt Nam» sang «lịch sử cổ trung đại»): chạy lại với từ khoá mới.
- **Đo lại định kỳ 30 ngày**: để có tab «Thăng hạng 30 ngày» thật và cập nhật kho video vượt trội cho P0.

### 4.2. Bảng mẫu để xem trước cách trình bày

https://docs.google.com/spreadsheets/d/1YzYqOGoTml1d3e8SS2LB58vFWI2YSTKJWVifW_BEW9s/edit?usp=sharing

Mở, chọn **Tệp → Tạo bản sao** để có bản riêng. Số liệu trong đó là của ngách mẫu, chỉ để học cách đọc bảng.

### 4.3. Cách tìm từ khoá chủ đề

Không đoán từ khoá: tìm theo **cụm tiêu đề của video đang thắng**. Ba hướng, mỗi hướng 5–7 cụm:

1. **Ngách chính:** tên sự kiện, nhân vật, thời kỳ bạn muốn làm, tiếng Việt và tiếng Anh. Ví dụ «trận Bạch Đằng», «nhà Trần đánh Nguyên Mông», «Vietnam war documentary».
2. **Ngách lân cận, cùng khán giả:** ví dụ «vũ khí quân sự giải thích», «bản đồ chiến dịch».
3. **Khác đề tài, cùng cách kể:** ví dụ «phim tài liệu bản đồ hoạt hình», «history explained map animation».

Thêm đuôi «giải thích», «toàn tập», «documentary», «explained» để ra kênh làm phim dài.

Mỗi cụm Claude chạy một lệnh tìm 30 kết quả, miễn phí, không cần khoá API:

```text
yt-dlp --ignore-config --no-warnings --encoding utf-8 --flat-playlist --print "%(channel_id)s\t%(channel)s\t%(title)s\t%(view_count)s" "ytsearch30:<cụm tiêu đề>"
```

Kênh xuất hiện ở ≥ 2 cụm, hoặc có ≥ 3 video khớp, được đưa vào danh sách khảo sát (mục tiêu 60–100 kênh), rồi đo bằng số.

### 4.4. Câu lệnh gõ trong Claude Code

Chạy lại cho ngách mới:

```text
chạy lại tư duy top 20 cho ngách "<ngách của bạn>", khán giả <tuổi>, phim dài <số> phút,
từ khoá tìm: "<cụm 1>", "<cụm 2>", "<cụm 3>", "<cụm 4>", "<cụm 5>"
```

Đo lại định kỳ (giữ ngách cũ):

```text
đo lại top 20 kỳ 30 ngày, cập nhật tab thăng hạng và kho video vượt trội
```

Chỉ muốn dò thêm đề tài, chưa chạy cả quy trình:

```text
tìm video vượt trội cho chủ đề "<chủ đề>" trong các kênh top 20 của tôi
```

### 4.5. Claude sẽ làm gì (9 pha, có cổng)

| Pha | Việc | Bạn cần làm |
|---|---|---|
| 0 | Hỏi khung: khán giả, độ dài, nguồn lực, đề tài cấm | Trả lời |
| 1 | Khảo sát rộng ~100 kênh bằng các cụm tìm | Chờ |
| 2 | Thu số liệu từng kênh (≥ 100 video mới nhất mỗi kênh) | Chờ; chạy nền, có thể vài giờ |
| 3–5 | Đo, gắn tuổi khán giả, xếp hạng, chọn TOP 20 và kho video | Xem bảng |
| 6 | Học trọn TOP 1, đề xuất **Model Link** | **Duyệt Model Link** |
| 7 | Phản biện | Xử lý các mục «cao» |
| 8 | Xuất tệp `top20.xlsx` | Tải lên Drive → mở → **Tệp → Lưu dưới dạng Google Trang tính**, gửi link cho Claude ghi vào hồ sơ |

Lưu ý thời gian: thu số liệu khoảng 3 giây mỗi video, nên 60 kênh × 100 video mất vài giờ. Claude chạy nền; bạn để máy chạy và quay lại sau. Dữ liệu thô lưu ở thư mục `nghien_cuu` trong `cau-hinh.toml`, không vào repo.

Xong thì gõ `commit và push` để lưu hồ sơ lên repo riêng.

---

## Hỏi đáp nhanh

| Hỏi | Đáp |
|---|---|
| Clone báo không có quyền | Chưa bấm Join lời mời, hoặc `gh` đăng nhập nhầm tài khoản: `gh auth logout` rồi `gh auth login` |
| Commit báo «Please tell me who you are» | Làm bước 1.2 |
| Push bị từ chối | Bạn đang đẩy lên `kit`; đẩy lên `origin` |
| Claude không thấy skill | Gõ `/exit`, `cd $HOME\Goha\GohaKit`, gõ `claude`, gõ `bắt đầu` |
| Có cần khoá API không | Mức Miễn phí: không. Mức Đầy đủ: ElevenLabs. Khoá dán vào tệp `.env` (chép từ `khoa-api.mau`), không gửi khoá cho Claude hay vào nhóm |
| Mức Miễn phí làm giọng thế nào | Ghi «chưa chọn» ở K2, làm ở P4; đường VieNeu chưa thử đầu cuối, kẹt thì hỏi nhóm Zalo |
| Báo lỗi thế nào | Gửi nhóm Zalo: đang ở bước nào (K1, P4…), lỗi nguyên văn, nội dung `kiem-may.md`. Không gửi `.env` |

Tài liệu đầy đủ trong kit: `README.md` (cài đặt), `HUONG-DAN.md` (quy trình, chi phí, sự cố).
