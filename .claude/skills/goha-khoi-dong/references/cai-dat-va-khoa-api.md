# Cài đặt và khoá API (Windows)

Đọc khi chạy bước 2, 4, 5 của K1. Mọi lệnh chạy trong PowerShell hoặc Git Bash; sau khi cài phải **mở lại cửa sổ lệnh** để PATH mới có hiệu lực.

## Bảng lệnh cài

| Thành phần | Bắt buộc | Lệnh cài | Ghi chú |
|---|---|---|---|
| Claude Code | Có | Theo trang Anthropic | Người dùng tự cài trước K1 |
| Git | Có | `winget install Git.Git` | Tự cài trước K1 |
| GitHub CLI | Có | `winget install GitHub.cli`, rồi `gh auth login` | Đăng nhập bằng tài khoản đã được mời vào team |
| Python 3.10 trở lên | Có | `winget install Python.Python.3.12` | Tích chọn «Add to PATH» nếu bộ cài hỏi |
| Thư viện Python | Có | `python -m pip install -r requirements.txt` | numpy, pillow, opencv-python, soundfile, pytest, openpyxl, yt-dlp, requests, scipy, fonttools |
| Node.js 22 trở lên | Có | `winget install OpenJS.NodeJS.LTS`, rồi `npm install` trong `template/` | Cần Node 22 vì `tools/kit/dung-trang.mjs` dùng WebSocket có sẵn của Node, bản cũ không có |
| ffmpeg và ffprobe | Có | `winget install Gyan.FFmpeg` | Một lệnh cài cả hai |
| Chrome hoặc Edge | Có | Edge có sẵn trong Windows; hoặc `winget install Google.Chrome` | Dùng chụp ảnh headless (thẻ chữ, bìa); đường dẫn ghi ở khoá `chrome` nếu nằm chỗ lạ |
| Ổ trống | Có | Không cài | ≥ 60 GB cho mỗi tập đang dựng, tính ở ổ chứa khoá `output` |
| RAM | Có | Không cài | 16 GB trở lên là tốt; 8 GB chạy được ở chế độ nhẹ (720p, ít cảnh 3D, tăng tư liệu và thẻ chữ); dưới 8 GB không đủ |
| Goha AVS | Bắt buộc ở mức Đầy đủ; tuỳ chọn ở mức khác (thay bằng `kit.py tron`, `kit.py master`) | Bộ cài Goha của hội viên | Điền thư mục cài vào khoá `goha_avs`. Cổng 8787 trả lời nghĩa là app đang chạy; chưa chạy cũng không sao ở K1 |
| Goha Flow | Tuỳ | Bộ cài Goha của hội viên | Chỉ cho hình minh hoạ ngách không phải sử Việt, và chỉ hình không có người thật |
| pedalboard (hậu kỳ) | Tuỳ | `python -m pip install pedalboard` | Chỉ khi dùng chuỗi VST; không có thì dùng chuỗi ffmpeg |

Hỏi người dùng trước khi chạy bất kỳ lệnh nào ở bảng trên (cổng DỪNG của K1).

## Khoá API

Người dùng **tự** làm, Claude không đọc giá trị:

1. Chép `khoa-api.mau` thành tệp tên `.env` ở gốc repo (cùng chỗ với `khoa-api.mau`).
2. Dán khoá sau dấu `=`, không dấu cách, không ngoặc kép. Lưu tệp.
3. Báo Claude «xong». Claude chạy lại `python -X utf8 tools/kiem-may/kiem-may.py` và chỉ đọc dòng «Khoá ... có/thiếu».

`.env` không lên Git, không gửi cho ai. `.claude/settings.json` của kit chặn Claude đọc nó.

| Khoá | Dùng cho | Lấy ở đâu | Bắt buộc |
|---|---|---|---|
| `ELEVENLABS_API_KEY` | Đọc giọng, chép lời Scribe, tiếng động | elevenlabs.io, Developers, API Keys, Create API Key | Không (mức Miễn phí không cần) |
| `DEEPGRAM_API_KEY` | Chép lời soi chéo | console.deepgram.com, API Keys, Create a New API Key | Không; tài khoản mới được tặng tín dụng dùng thử |

**Quyền khoá ElevenLabs** (khi tạo khoá, đặt Restrict Key rồi bật đúng ba quyền, các quyền khác để No access): **Text to Speech**, **Speech to Text**, **Sound Effects**. Thiếu quyền nào thì bước tương ứng báo lỗi 401 hoặc quyền; quay lại sửa quyền của khoá.

Đọc giọng, chép lời, tiếng động đều là bước **trả phí**: quy trình sẽ báo chi phí trong chat trước khi chạy. K1 chỉ kiểm khoá có hay không, không gọi dịch vụ.
