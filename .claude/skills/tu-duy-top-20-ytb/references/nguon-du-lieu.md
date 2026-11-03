# Nguồn dữ liệu, chi phí, chỗ lưu

Hai nhánh, chọn theo mức chạy ghi trong `ho-so-kenh/ho-so.md` (chưa có hồ sơ vì đang ở K2 thì đọc dòng «Mức chạy» trong `kiem-may.md` do K1 ghi):
- **Miễn phí (đủ để làm hết quy trình, KHÔNG cần khoá API):** chỉ `yt-dlp`, kể cả số sub (mục «Lấy số sub bằng yt-dlp» dưới). Không có biến `YOUTUBE_API_KEY` trong kit và không script nào đọc nó; đừng bảo người dùng tạo khoá YouTube.
- **Tuỳ chọn trả phí:** vidIQ. Nhanh hơn ở mục tăng sub 30 ngày, từ khoá, video vượt trội; không bắt buộc.

## Chọn công cụ
| Cần | Nhánh miễn phí | Nhánh vidIQ (tuỳ chọn) | Lưu ý |
|---|---|---|---|
| Danh sách video, view, like, bình luận, thời lượng, ngày | `scripts/thu_video.py` (yt-dlp: flat chỉ lấy id, rồi metadata đầy đủ từng video) | `vidiq_channel_videos` | Tuần tự, nghỉ giữa lệnh, không cookie, `lang=en`; xem mục «Thu video» |
| Cờ Short | id từ tab `/shorts` của kênh, hoặc URL dạng `/shorts/` | — | Ghi cột `is_short`; không có thì script ước theo thời lượng và gắn cờ |
| Sub, tổng video, ngày lập kênh | Sub: `yt-dlp` trường `channel_follower_count` (mục «Lấy số sub bằng yt-dlp»); tổng video và ngày video đầu: `<khoá>.meta.json` của `thu_video.py`; ngày lập: tab Giới thiệu của kênh (tuỳ chọn) | `vidiq_channel_stats` | Sub của YouTube công bố bị làm tròn 3 chữ số có nghĩa. Truyền `--tong-video`, `--ngay-video-dau` cho `do_kenh.py` (bẫy A4); `--meta` làm sẵn việc này |
| Sub 30 ngày trước (cho % tăng) | Lần đo trước của chính bạn ở tab 9; lần đầu thì để trống, không ước | `vidiq_channel_performance_trends` | Bẫy D6 |
| Tỉ trọng view Shorts của kênh (cho `--ty-trong-view-short`) | Cần cho kênh lai: tính từ view Shorts ÷ tổng view trong 30 ngày đã lấy bằng `thu_video.py` (lấy đủ Shorts 30 ngày, không chỉ 15 video) | `shortViewCount30d` ÷ tổng view 30 ngày | Mẫu Shorts không đủ thì sai (bẫy B14) |
| **Kiểm tay ≥ 3 số với nguồn độc lập** (pha 2) | Mở trang video, hoặc `yt-dlp --ignore-config --skip-download --print "%(view_count)s" <link video>` | `vidiq_get_videos_by_ids` | Đạt khi lệch ≤ 3 %. Chọn 3–4 video ở các kênh khác nhau, gồm ít nhất một kênh nhiều video |
| Khám phá kênh | `yt-dlp ytsearch` (mục dưới) | `vidiq_similar_channels`, `vidiq_outliers`, `vidiq_youtube_search` | |
| Video vượt trội theo ngách | Tự tính hệ số bằng `do_kenh.py` | `vidiq_outliers` | Kiểm số thật (`tieu-chi-va-cong-thuc.md` mục 2) |
| Đường «được phát lại nhiều nhất» | `yt-dlp --skip-download --write-info-json` → trường `heatmap` (100 khoảng) → `scripts/heatmap.py` | — | Chỉ có khi video đủ lượt xem lại; giá trị tương đối |
| Ảnh bìa | `yt-dlp --skip-download --write-thumbnail` | — | Phải mở ảnh xem (bẫy A6) |
| Chép lời video không có phụ đề | Công cụ gỡ băng của kit (STT trong `tools/kit`), hoặc Whisper chạy trên máy khi không có khoá STT | — | Whisper trên CPU chậm (cỡ 13 phút mỗi video) |
| Lượng tìm kiếm | Gợi ý tìm kiếm của YouTube (tự gõ, ghi lại), cả tiếng Việt và tiếng Anh | `vidiq_keyword_research` | Từ khoá Việt bằng 0 không có nghĩa là không có cầu (bẫy B9) |
| Tuổi khán giả kênh mình | YouTube Analytics (Studio) | — | Sau 2–3 video |
| Tuổi khán giả kênh khác | `yt-dlp --write-comments` rồi `do-tuoi-khan-gia.md` | `vidiq_video_comments` (≈ 15 credit mỗi kênh) | Xem «Phạm vi đo tuổi» dưới |

Dùng vidIQ thì: chỉ một tiến trình gọi tại một thời điểm (bẫy A3), xem `vidiq_balance` trước và sau mỗi lô, đặt trần credit trong brief, không gọi công cụ ghi (đăng, sửa, trả lời).

## Lấy số sub bằng yt-dlp (không cần khoá)
Lệnh sau đọc video mới nhất của kênh và in id kênh, số sub, tên kênh (đã thử chạy thật, không cookie, không khoá):
`yt-dlp --ignore-config --no-warnings --skip-download --playlist-items 1 --print "%(channel_id)s\t%(channel_follower_count)s\t%(channel)s" "https://www.youtube.com/@<handle>/videos"`
- Giá trị cột 2 là số cho `do_kenh.py --subs`. Lấy một lần mỗi kênh, cùng ngày với lần chạy `thu_video.py`, nghỉ 3 giây giữa các kênh.
- Kênh ẩn số sub thì giá trị là `NA`: ghi «chưa có», kênh đó thành «Không đủ chỉ số» (bình thường, không đoán).
- Nhiều kênh: ghi cột `subs` vào `bang-kenh.tsv` (hợp đồng dữ liệu dưới) để `do_kenh.py xep-hang` đọc.
- Sub 30 ngày trước: lần đầu để trống (không ước); lần đo kỳ sau lấy từ tab 9 của lần đo trước.

## Thu video: `scripts/thu_video.py`
`python scripts/thu_video.py <kênh>... --out-dir <thư mục> [--ds kenh.txt] [--nghi 3] [--so-dai 100] [--lam-lai]`
- `--out-dir` đặt dưới thư mục khoá `nghien_cuu` của `cau-hinh.toml` (xem SKILL.md mục «Nguồn dữ liệu theo mức chạy»), ví dụ `<nghien_cuu>/<ngách>-<ngày>/thu-video`.
- Mỗi kênh: flat `/videos` và `/shorts` chỉ để lấy **danh sách id** (mới → cũ), rồi đọc metadata đầy đủ của: 100 video dài mới nhất (cửa sổ liên tục), 10 video dài nhiều view nhất, 8 video dài cũ nhất, 15 Shorts mới nhất, 8 Shorts cũ nhất. Ghi `<khoá>.tsv` (đúng hợp đồng dữ liệu dưới) và `<khoá>.meta.json` (`ngay_video_dau`, `cua_so_tu`, `so_hoi_vien`, `n_dai_flat`, `n_short_flat`, `pho_bien`…). Kênh đã có đủ hai file thì bỏ qua (`--lam-lai` để đọc lại).
- Lệnh dùng `--ignore-config` (không để cấu hình yt-dlp có sẵn kéo cookie trình duyệt vào) và không bao giờ dùng cookie.
- **Nối sang `do_kenh.py kenh`**: `--meta <khoá>.meta.json` lấy `tong_flat`, `ngay_video_dau`, `cua_so_tu`, `so_hoi_vien` (tham số truyền tay ưu tiên hơn; bảng `xep-hang` có cột `meta`). Meta ghi `loi` thì `do_kenh.py` từ chối. **Có `--cua-so-tu` mà thiếu tổng video** thì `sub_moi_video` là None và cờ `THIEU_TONG_VIDEO_CHO_CUA_SO` (chia sub cho số video trong cửa sổ sẽ thổi phồng gấp nhiều lần). Có `--cua-so-tu` thì hệ số chỉ tính cho video trong cửa sổ (video top cũ hơn cửa sổ vẫn nằm trong bảng nhưng hệ số là None, lý do `ngoai_cua_so`), và `DANH_SACH_THIEU_VIDEO` không bật vì danh sách bị cắt có chủ ý.
- **Video hội viên** (members-only) có trong danh sách flat nhưng không đọc được: script đếm vào `so_hoi_vien` (cờ `HOI_VIEN`). Ngày video đầu = nhỏ nhất trong các video cũ nhất **đọc được** (thử thêm tối đa 3 lô 8 video cũ kế tiếp nếu cả 8 video cũ nhất là hội viên), nên có thể muộn hơn thực tế: ghi chú khi dùng sub/ngày của kênh đó.
- **Lỗi là lỗi:** mã thoát yt-dlp khác 0 ở tab `/videos`, hoặc `/shorts` (trừ khi kênh không có tab đó), hoặc một lô đọc không ra dòng nào (429, mạng, quá 30 phút) thì kênh đó **không ghi file**, script in `LỖI …` và thoát mã 1 sau khi chạy hết lô; lần sau tự thử lại. Đọc thiếu > 5 % video (không kể hội viên) thì vẫn ghi file nhưng meta có `loi`: lần sau tự làm lại, `do_kenh.py --meta` từ chối. Meta luôn ghi `so_yeu_cau`, `so_thieu`, `thieu_ids`, cờ `DOC_THIEU`.
- **Ước giờ:** lệnh đọc lô có `--sleep-requests 1` (tránh 429); ước thận trọng khoảng 3 giây mỗi video (2.000 video khoảng 1,7 giờ). Không nghỉ giữa yêu cầu thì khoảng 1,2 giây mỗi video nhưng dễ bị 429.

## Ghi chú về `--flat-playlist`
- Không có cách sắp theo view: `--playlist-reverse` và `?sort=p` trên tab kênh bị bỏ qua khi flat. Muốn «5–10 video nhiều view nhất»: liệt kê hết bằng flat, sắp theo view, rồi đọc đúng các video đó bằng metadata đầy đủ (việc `thu_video.py` làm).
- View của flat bị **làm tròn** (3 chữ số có nghĩa) và đọc sai đơn vị với giao diện tiếng Việt (bẫy A1): chỉ dùng để sàng lọc.
- Flat **dịch tiêu đề sang tiếng Anh** khi đặt `lang=en`: tiêu đề lấy từ metadata đầy đủ.

## Chạy nền trên Windows (Git Bash)
- `nohup python scripts/thu_video.py … > thu.log 2>&1 &` trong một lệnh công cụ vẫn sống sau khi lệnh kết thúc. Chạy thêm một lệnh nền thứ hai tạo **hai** tiến trình yt-dlp song song (vi phạm «tuần tự», rủi ro 429) mà log trống nên khó thấy.
- Script giành `thu_video.pid` trong `--out-dir` bằng tạo file nguyên tử và **từ chối chạy** (mã thoát 3) khi PID đó còn sống **và dòng lệnh của nó chứa `thu_video`** (PID bị hệ điều hành tái dùng cho tiến trình khác thì không chặn). Trước khi chạy lại hoặc dừng, xem cả python lẫn yt-dlp: PowerShell `Get-CimInstance Win32_Process -Filter "Name like 'python%' or Name like 'yt-dlp%'" | Select ProcessId,ParentProcessId,CommandLine`. Python bị dừng đột ngột (kể cả `taskkill` không kèm `/T`) để lại **yt-dlp mồ côi** vẫn chạy và vẫn tạo yêu cầu: dừng đúng PID đã xác nhận bằng dòng lệnh, với `/T` để dừng cả tiến trình con. File PID cũ của tiến trình đã chết thì script tự dọn và chạy tiếp; kênh đã đủ file được bỏ qua.
- Không chạy hai `--out-dir` khác nhau cùng lúc trên cùng một máy.

## Khám phá kênh bằng ytsearch
Khi bảng nhãn ngách của công cụ không phủ hết (lần chạy thử bỏ sót hai kênh nằm trong top 6): tìm bằng **cụm tiêu đề** của video thắng.
- `yt-dlp --ignore-config --no-warnings --encoding utf-8 --flat-playlist --print "%(channel_id)s\t%(channel)s\t%(title)s\t%(view_count)s" "ytsearch30:<cụm tiêu đề>"` (miễn phí, không cookie; 20 truy vấn mất vài phút; nghỉ 3 giây giữa các lệnh).
- Mẫu truy vấn: khuôn tiêu đề của kênh thắng, tên đề tài kèm «giải thích» hoặc «documentary», từ khoá ngách tiếng Việt và tiếng Anh. Mỗi truy vấn tối đa 30 kết quả.
- **Khử trùng theo `channel_id`** (cột 1; không theo tên kênh), giữ số lần xuất hiện và tiêu đề khớp; bỏ kênh đã có trong bảng khảo sát. Kênh xuất hiện ở ≥ 2 truy vấn hoặc ≥ 3 video khớp thì vào danh sách khảo sát, rồi đo như kênh khác (`thu_video.py`).
- Nguồn bổ trợ khi có vidIQ: `similar_channels`, `outliers`, `youtube_search`. Cột «đề xuất» trong trình duyệt ẩn danh và bình luận nhắc kênh chỉ dùng khi **người** làm tay; agent không làm được.

## Phạm vi đo tuổi theo giới hạn
Đo tuổi bằng bình luận tốn công (≈ 15 credit mỗi kênh nếu dùng vidIQ). Với giới hạn thời gian hoặc credit, chỉ đo **ứng viên Model Link và top 5**; các kênh còn lại ghi «chưa đo» (mức Chưa xác định, `do-tuoi-khan-gia.md` bước 7: giữ, ghi «cần kiểm», không loại vì tuổi). Ghi trong báo cáo số kênh chưa đo.

## Chỗ lưu
- Dữ liệu thô (danh sách video, bình luận, phụ đề, ảnh, heatmap, script đo): thư mục khoá `nghien_cuu` trong `cau-hinh.toml`, ngoài repo. Bình luận thô có tên người: chỉ dùng nghiên cứu, không chép vào báo cáo.
- Báo cáo, JSON hồ sơ, XLSX: thư mục `plans/reports` của repo.
- Google Sheet: Drive của người dùng, không chia sẻ công khai khi chưa được yêu cầu.

## Brief cho sub-agent thu dữ liệu
Gồm: danh sách kênh, trường cần lấy, công cụ được dùng (`thu_video.py`, không tự viết script thu), trần credit (nếu có vidIQ), thư mục ghi, cách kiểm file đã ghi, «chạy tuần tự» và nhắc file PID, hợp đồng dữ liệu dưới đây, ước giờ, và yêu cầu báo số dư trước và sau.

## Hợp đồng dữ liệu (đầu vào của `do_kenh.py`)
Mỗi kênh một TSV (UTF-8), dòng đầu là tên cột: `id`, `ngay_dang` (YYYY-MM-DD hoặc ISO có giờ), `thoi_luong_s` (giây hoặc mm:ss), `view`, `like`, `binh_luan`, `is_short` (1/0, để trống nếu không biết), `tieu_de`. Kèm siêu dữ liệu kênh: `subs`, `tong_video`, `ngay_video_dau`, `ngay_lap`, `sub_30_ngay_truoc` (nếu có), `cua_so_tu`, `ty_trong_view_short`, `so_hoi_vien`. Script báo số dòng bị bỏ (thiếu view hoặc ngày, trùng id); số dòng bị bỏ > 5 % thì lấy lại.
`do_kenh.py xep-hang` nhận bảng `bang-kenh.tsv` với các cột `kenh`, `file`, `subs` và các cột siêu dữ liệu trên (tuỳ chọn).
