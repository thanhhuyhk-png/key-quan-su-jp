# Hướng dẫn đầy đủ cho hội viên

Đọc `README.md` trước (cài Claude Code, Git, đăng nhập GitHub, lập repo kênh riêng, mở Claude Code trong thư mục kit). Phải mở Claude TRONG thư mục kit thì luật an toàn khoá và các skill của kit mới có hiệu lực. Tài liệu này giải thích phần còn lại: yêu cầu máy, tài khoản cần chuẩn bị, cách điền khoá, quy trình một tập phim và cách xử lý sự cố.

## 1. Yêu cầu máy

Hệ điều hành: chỉ Windows 10 hoặc 11. Claude kiểm hộ bạn ở bước K1 (`python -X utf8 tools/kiem-may/kiem-may.py`), in bảng «có / thiếu / lệnh cài». Bảng dưới là để bạn biết trước.

| Thành phần | Yêu cầu | Lệnh cài (PowerShell) |
|---|---|---|
| Python | 3.10 trở lên (khuyên 3.12) | `winget install Python.Python.3.12` |
| Thư viện Python | cài từ `requirements.txt` | `python -m pip install -r requirements.txt` |
| Node.js | 22 trở lên (bắt buộc cho bản đồ 3D, thẻ chữ, bìa) | `winget install OpenJS.NodeJS.LTS` |
| ffmpeg | bản đầy đủ có ffprobe | `winget install Gyan.FFmpeg` |
| Chrome hoặc Edge | để chụp ảnh tự động; Edge có sẵn trong Windows | — |
| Ổ đĩa | trống ít nhất 60 GB cho mỗi tập đang dựng | — |
| RAM | 16 GB trở lên là thoải mái; 8 GB vẫn chạy ở chế độ nhẹ | — |

Sau khi cài xong, đóng và mở lại cửa sổ dòng lệnh để máy nhận lệnh mới.

Hai ứng dụng đã được tặng cho hội viên, cài theo bộ cài chủ kit gửi:
- **Goha AVS**: trộn tiếng, hậu kỳ, xem lại bản dựng. Bắt buộc ở mức chạy Đầy đủ; tuỳ chọn ở mức Tiết kiệm và Miễn phí, nơi kit trộn bằng `kit.py tron` và `kit.py master` (chuỗi ffmpeg, hậu kỳ kém tinh hơn một chút). Bảng kiểm máy của K1 có thể vẫn ghi «thiếu» khi chưa cài; ở hai mức sau thì bỏ qua được.
- **Goha Flow**: sinh hình minh hoạ cho kênh NGÁCH KHÁC. Kênh sử Việt không dùng (cấm ảnh AI).

Thư mục media nặng (hình, âm, bản dựng) không nằm trong repo. Bạn khai chỗ để nó ở `cau-hinh.toml` (xem mục 4), nên chọn ổ còn nhiều chỗ trống.

## 2. Ba mức chạy và chi phí

K1 hỏi bạn chọn một mức và ghi tạm ở cuối `kiem-may.md`; khi K2 làm xong, mức nằm trong mục 1 của `ho-so-kenh/ho-so.md` và từ đó chỉ sửa ở hồ sơ (nơi duy nhất các skill đọc). Có thể đổi sau.

| Mức | Dành cho | Dùng gì |
|---|---|---|
| Đầy đủ | Muốn chất lượng như kênh mẫu | ElevenLabs (giọng, chép lời, tiếng động), Goha AVS, tuỳ chọn Deepgram, vidIQ, Suno |
| Tiết kiệm | Có Claude, ít ngân sách dịch vụ | Giọng rẻ hơn (VieNeu), nhạc và tiếng động miễn phí có phép kiếm tiền, STT bằng Deepgram hoặc tiết kiệm lượt gọi |
| Miễn phí | Chỉ có Claude Code | Phần mềm miễn phí: giọng chạy trên máy, Whisper chạy trên máy, nhạc thư viện miễn phí, top 20 bằng yt-dlp (không cần khoá nào) |

Giá các dịch vụ thay đổi theo thời gian, nên kit KHÔNG ghi giá cứng. Khi cần, Claude tra trang giá chính thức lúc chạy, ghi kèm ngày tra, và báo bạn trong chat TRƯỚC khi gọi bất kỳ bước tốn tiền nào (đọc giọng, chép lời, tiếng động, sinh hình). Bạn đồng ý mới chạy. Mức Tiết kiệm và Miễn phí đánh đổi chất lượng: giọng kém tự nhiên hơn, chép lời chậm hơn, hậu kỳ kém tinh hơn; Claude nói rõ đánh đổi ở bước K1.

## 3. Chuẩn bị tài khoản

Chỉ cần các tài khoản hợp với mức bạn chọn. Mỗi hội viên dùng khoá RIÊNG của mình và tự trả phí cho dịch vụ của mình.

**ElevenLabs** (cần cho mức Đầy đủ; elevenlabs.io)
- Dùng cho: đọc giọng (Text to Speech), chép lời kiểm tra (Speech to Text, Scribe), tiếng động (Sound Effects).
- Gói: cần gói trả phí có truy cập API và đủ dung lượng cho phim 12 đến 20 phút (vài chục nghìn ký tự mỗi tập). Gói thấp nhất có thể không đủ model giọng mới nhất hay không đủ ký tự; xem trang giá hiện hành, hoặc hỏi Claude kiểm hộ.
- Lấy khoá: đăng nhập → Developers → API Keys → Create API Key. Ở phần quyền, bật ba quyền Text to Speech, Speech to Text, Sound Effects (hoặc để quyền đầy đủ). Chép khoá ngay vì chỉ hiện một lần.

**Deepgram** (tuỳ chọn; console.deepgram.com)
- Dùng cho: chép lời lần hai để soi chéo với Scribe, giúp bắt lỗi đọc sai. Tài khoản mới thường được tặng tín dụng dùng thử.
- Lấy khoá: đăng ký → API Keys → Create a New API Key.

**YouTube (không cần khoá):** top 20 miễn phí lấy toàn bộ số liệu bằng `yt-dlp`, kể cả số sub, nên bạn KHÔNG cần tạo khoá YouTube Data API và `khoa-api.mau` không có dòng nào cho nó.

**vidIQ** (tuỳ chọn; vidiq.com)
- Dùng cho: điểm từ khoá, tìm video vượt trội, số liệu kênh nhanh hơn. Có thể làm top 20 không cần nó.

**Tài khoản YouTube/Google** của kênh bạn, để đăng ở bước P7. Claude không đăng hộ; bạn chép gói đăng dán vào YouTube Studio.

## 4. Điền khoá và cấu hình

### Khoá API: bạn tự làm, KHÔNG gửi khoá cho Claude

1. Trong thư mục kit, chép tệp `khoa-api.mau` thành một tệp tên `.env` (cùng thư mục, có dấu chấm đầu). Cách dễ: trong PowerShell, ở thư mục kit gõ `Copy-Item khoa-api.mau .env`.
2. Mở `.env` bằng Notepad. Dán khoá sau dấu `=` trên dòng tương ứng, không có dấu cách quanh `=`, không ngoặc kép:

   ```text
   ELEVENLABS_API_KEY=dán-khoá-của-bạn-ở-đây
   DEEPGRAM_API_KEY=
   ```

3. Lưu tệp. Dòng nào bạn không dùng thì để trống.
4. Không gửi khoá vào khung chat với Claude, không chụp màn hình có khoá, không commit. `.gitignore` đã chặn `.env`, và `.claude/settings.json` đã cấm Claude mở `.env`. Claude chỉ kiểm khoá «có hay không» qua `kiem-may.py`, không bao giờ in giá trị.
5. Nếu lỡ lộ khoá: vào trang của dịch vụ, thu hồi (Revoke) khoá cũ rồi tạo khoá mới.

### `cau-hinh.toml`: đường dẫn trên máy bạn

K1 tạo giúp từ `cau-hinh.mau.toml` và hỏi bạn các đường dẫn. Bạn cũng có thể tự chép tệp mẫu thành `cau-hinh.toml` rồi sửa. Viết đường dẫn Windows bằng dấu gạch xuôi, ví dụ `"E:/Phim/output"`. Các khoá chính:
- `output`: nơi để media nặng của từng tập (cần ≥ 60 GB trống).
- `chrome`: đường dẫn `chrome.exe` hoặc `msedge.exe`, để chụp ảnh tự động.
- `goha_avs`: thư mục cài Goha AVS.
- `nghien_cuu`: nơi lưu dữ liệu nghiên cứu (phụ đề, số liệu kênh mẫu), đặt ngoài repo.
- Các khoá tuỳ chọn (`vst_python`, `vst3`, `teardown`, `chep_loi`): để trống nếu không dùng.

`cau-hinh.toml` cũng không lên Git. Thiếu khoá bắt buộc thì kit dừng và nói rõ phải sửa gì.

## 5. Quy trình một tập phim, P0 đến P8

Hai bước làm một lần: **K1** (kiểm máy, cài, chọn mức) và **K2** (chọn ngách, top 20 kênh mẫu, hồ sơ kênh, thương hiệu). Sau đó mỗi tập đi qua 9 phase. Mỗi phase có một skill và một cổng DỪNG: Claude làm xong phần của mình, trình bạn xem, bạn nói «duyệt» mới sang bước kế.

| Phase | Việc | Bạn duyệt gì |
|---|---|---|
| P0 chọn đề tài | Chọn từ kho video vượt trội của top 20; kiểm đề tài không trùng tập mẫu, không trùng hội viên khác | Đề tài và góc kể |
| P1 nghiên cứu | Lập sổ số liệu có nguồn, sổ tài sản hình có hạng bản quyền | Sổ đủ dòng, nguồn đáng tin |
| P2 kịch bản | Nhiều phương án hook chấm điểm, viết, phản biện kép, qua máy quét chính sách và sổ cách nói | Kịch bản |
| P3 phân cảnh | Chia cảnh, chọn hình cho từng câu, ảnh tĩnh duyệt trước | Storyboard ảnh tĩnh |
| P4 giọng | Đọc giọng cả bài rồi cắt câu, đo mốc | Chi phí giọng trước khi đọc; nghe thử |
| P5 dựng | Dựng hình và âm cả tập, trộn nhạc và tiếng động | 3 phút đầu |
| P6 QC, xuất | Đo −14 LUFS, đỉnh ≤ −1 dBTP; STT ≥ 97 %; soi khung mọi cảnh bản đồ | Xem cả phim |
| P7 bộ đăng | Tiêu đề, mô tả, thẻ, 3 thumbnail A/B/C, phụ đề dịch, bình luận ghim | Gói đăng |
| P8 Shorts | Cắt 3 đến 5 Shorts dọc, chữ và bìa; sau 7 ngày ghi bản thắng | Shorts mẫu đầu tiên |

Thuật ngữ gặp trong các bước:

| Từ | Nghĩa |
|---|---|
| Chủ kit | Người làm ra và phát hành kit này (người bạn liên hệ khi cần hỗ trợ). |
| Model Link | Kênh số 1 trong top 20 mà kênh bạn bám sát về cách làm; Claude đề xuất, bạn duyệt ở K2. |
| Top 20 | 20 kênh hình mẫu đo bằng số liệu (sheet nhiều tab), nguồn để chọn đề tài và học cách kể. |
| Shu | Bước học khuôn viết từ phụ đề các video thành công của top 20 và Model Link, ra sổ tay văn phong của kênh bạn (`kenh/hoc-shu/`). Học cách viết, không chép câu. Claude chạy ở P2 nếu chưa có sổ tay. |
| Hạng A / B / C | Hạng bản quyền tư liệu hình: A phạm vi công cộng dùng thoải mái; B còn bản quyền, chỉ trích 3 đến 5 giây, tắt tiếng gốc, ghi nguồn; C tránh dùng. |
| Agy, Codex, Grok | Các công cụ AI bên ngoài (Gemini, GPT, Grok) dùng làm người phản biện thứ hai. Không có thì dùng sub-agent Opus của Claude ngữ cảnh mới. |
| Sub-agent | Một Claude phụ chạy ngầm làm việc riêng (viết, phản biện, thu dữ liệu) rồi báo lại Claude chính. |
| Tập mẫu | Tập phim hoàn chỉnh trong `mau/dien-bien-phu-1954/` để học cách làm; cấm đăng lại. |

Quy tắc chung:
- **Chi phí:** trước mỗi bước tốn tiền, Claude nói gọi gì và ước tính bao nhiêu. Chưa nghe «đồng ý» thì không gọi.
- **Làm tiếp tập dở:** trạng thái mỗi tập nằm ở `tap/<EPxxx-slug>/ke-hoach/progress.md`. Mở lại repo, Claude đọc và hỏi bạn làm tiếp phase nào.
- **Chữ cho người xem** (kịch bản, tiêu đề, mô tả) đi qua bộ lọc chính sách YouTube và sổ cách nói `kenh/cach-noi-da-chot.tsv`. Mỗi khi bạn sửa một cách nói, bảo Claude ghi vào sổ để lần sau không tái phạm.
- **Chất lượng "xong" là có số:** `python -I -X utf8 tools/kit/kit.py kiem <video> --lufs -14`, `kit.py chep-loi` rồi `kit.py so-loi --min 0.97`, và soi khung bản đồ. Không có số thì chưa xong.
- **Việc lớn:** Claude lập plan ngắn rồi chờ bạn duyệt. Luật model, sub-agent, CLI ngoài: `huong-dan/dieu-phoi/`.

## 6. Chép quy trình, không chép chủ đề

Kit cho bạn phương pháp, không cho bạn nội dung của kênh mẫu. Nếu nhiều kênh đăng cùng đề tài với cùng giọng và khung hình, YouTube có thể xếp vào «nội dung dùng lại» và kênh của bạn có nguy cơ mất kiếm tiền. Vì vậy có 5 lớp chặn, phần lớn do máy kiểm:

1. **Tập mẫu là sách đọc.** Thư mục `mau/dien-bien-phu-1954/` (tập mẫu) để học cấu trúc; cấm đăng lại. `kit/so-chu-de-cam.tsv` liệt kê đề tài bị chặn, P0 đọc file này.
2. **Sổ đăng ký đề tài chung.** Chủ kit giữ sổ, gồm hai link: **xem sổ** https://docs.google.com/spreadsheets/d/1T-4n3Z19BARWsywfG35p4591v3Tfq7USUHgKslU5fiU/edit?usp=sharing (chỉ xem) và **đăng ký** https://docs.google.com/forms/d/e/1FAIpQLSeO00Ix7ebS5OTSvCLKkKgPs5cpW-oDfl5TTTMPj491ZARjFg/viewform (Google Form). Mỗi dòng ghi thời gian, đề tài, góc kể, ngôn ngữ, hội viên. Ai đăng ký trước được làm; người sau được gợi ý góc khác. Bạn chỉ đăng ký đề tài đã duyệt ở P0, qua Form; không ai sửa được dòng của người khác. Để máy so với sổ, Claude tải bản mới nhất bằng `curl -sSL -o so-chung.tsv "https://docs.google.com/spreadsheets/d/1T-4n3Z19BARWsywfG35p4591v3Tfq7USUHgKslU5fiU/export?format=tsv&gid=1450166982"` (hoặc bạn mở link xem sổ, chọn Tệp → Tải xuống → Giá trị phân tách bằng tab (.tsv)), rồi Claude truyền tệp đó vào `kiem-de-tai.py` qua `--so-chung <tệp>` (máy đọc thẳng các cột của Form, cột «Dấu thời gian» là ngày). Chưa có link hoặc chưa tải được thì P0 vẫn so được với sổ cấm đi kèm kit: máy in «sổ chung: chưa có, 0 dòng đã so» và Claude nói rõ với bạn rằng lần kiểm này chưa đối chiếu sổ chung.
3. **Máy kiểm câu chữ.** `tools/loc-chinh-sach/trung-lap.py` so kịch bản với tập mẫu và kho Shu của riêng bạn; trùng trên 1 % cụm sáu tiếng thì CHẶN.
4. **Nhận diện riêng.** K2 bắt bạn chọn giọng, bảng màu, logo, khung hình khác tập mẫu.
5. **Shu theo kênh mẫu của chính bạn.** Bạn học từ top 20 của ngách bạn chọn, không học lại kho của kênh mẫu.

## 7. Xử lý sự cố thường gặp

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Kit báo thiếu khoá, ví dụ «thiếu ELEVENLABS_API_KEY» | Chưa tạo `.env`, hoặc dòng khoá còn trống, hoặc có dấu cách quanh `=` | Làm lại mục 4; lưu `.env` ở gốc repo; chạy lại `python -X utf8 tools/kiem-may/kiem-may.py` |
| Báo «Node cũ», lỗi cú pháp khi chạy `dung-trang.mjs` | Node dưới 22 | `winget install OpenJS.NodeJS.LTS`, mở lại cửa sổ lệnh, `node -v` phải ≥ 22 |
| «Không tìm thấy Chrome» khi chụp ảnh | `chrome` trong `cau-hinh.toml` sai đường dẫn | Tìm `chrome.exe` hoặc `msedge.exe` trên máy, ghi đường dẫn đúng (dấu gạch xuôi) |
| `python` hoặc `ffmpeg` không nhận ra | Vừa cài, chưa mở lại cửa sổ lệnh; hoặc chưa cài | Đóng mở lại PowerShell; chạy lại lệnh cài ở mục 1 |
| `kit.py kiem` báo LUFS lệch (ngoài −14 ± 0,5) hoặc đỉnh > −1 dBTP | Trộn quá to hoặc quá nhỏ; bước `master` chưa chạy | Chạy `kit.py master` rồi đo lại sau khi xuất file cuối; đừng đo bản nháp |
| STT dưới 97 % | Giọng đọc sai chữ, tên riêng lạ, hoặc số đọc khác chữ viết | Mở bản so lời để xem câu lệch; sửa lời đọc hoặc đọc lại đúng câu đó (kèm câu trước và sau); nếu chỉ một máy STT lệch còn máy kia đúng, hỏi Claude xem có đạt theo luật QC không |
| Giọng đọc cụt đuôi câu hay nghe lạ | Đọc câu rời rạc làm mất ngữ điệu | Đọc lại cả đoạn quanh câu rồi cắt lấy câu giữa |
| `gh auth` hay clone báo không có quyền | Chưa nhận lời mời vào team, hoặc đăng nhập nhầm tài khoản | Nhận lời mời trong email GitHub; `gh auth logout` rồi `gh auth login` lại |
| `git pull kit main` báo xung đột | Bạn đã sửa tệp thuộc kit | Dừng lại, không xoá; hỏi Claude hoặc chủ kit; việc của bạn nên nằm ngoài tệp của kit |
| Claude không nhận ra skill, hoặc bảo «mở lại Claude trong thư mục kit» | Bạn mở Claude ở thư mục khác | Gõ `/exit`, `cd` vào thư mục kit, gõ `claude`, rồi gõ `bắt đầu` |
| `git push` bị từ chối (không có quyền) | Đang đẩy lên remote `kit` (chỉ đọc) | Đẩy lên `origin` (repo riêng của bạn); xem `README.md` mục «Lập repo kênh riêng» |
| Máy chậm, treo khi dựng cảnh 3D | RAM hay GPU yếu | Dùng chế độ nhẹ (720p, ít cảnh 3D, tăng tư liệu và thẻ chữ); báo K1 chọn lại |

Vẫn không xử lý được: xem mục «Hỗ trợ» ở `README.md`. Gửi bước đang làm và thông báo lỗi nguyên văn, không gửi `.env`.
