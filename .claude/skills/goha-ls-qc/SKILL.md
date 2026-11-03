---
name: goha-ls-qc
description: P6 QC và xuất của quy trình sản xuất phim tài liệu lịch sử, quân sự (kit Goha Lịch Sử) — hai cổng trước khi user xem: (A) QC nội dung trước khi đọc giọng, render (cổng máy quet, sổ cách nói, sổ số liệu, chống trùng; reviewer Opus ngữ cảnh mới soát câu sửa và câu bên cạnh; xưng hô đúng thời điểm; chữ trên hình khớp lời và sổ) và (B) QC kỹ thuật file cuối (STT ElevenLabs bản trộn ≥ 97 % soi chéo Deepgram, soi khung mọi cảnh bản đồ Hoàng Sa, Trường Sa, Biển Đông, kit.py kiem tra về mã cảnh, độ to −14 LUFS và đỉnh thật ≤ −1 dBTP đo ebur128 trên file cuối, soi dấu kênh Full HD); rồi DỪNG cho user xem. Dùng ngay khi user nói "P6", "QC", "kiểm bản cuối", "xuất file", "deliver", "soát nội dung trước khi render", hoặc khi tập đã có bản ghép đủ hình từ P5 hay vừa sửa lời — kể cả khi không nhắc tên skill. Không dùng để dựng (goha-ls-dung) hay làm postpack (goha-ls-dang).
---

# P6 QC, xuất (Goha Lịch Sử)

Đường dẫn dạng `<output>`, `<nghien_cuu>`, `<vst_python>`, `<chep_loi>` là khoá trong `cau-hinh.toml` ở gốc repo (mẫu: `cau-hinh.mau.toml`; script đọc bằng `tools/cau_hinh.py`). Đường dẫn khác tính từ gốc repo.

Danh tính kênh, ngưỡng độ to và luật riêng của ngách đọc từ `ho-so-kenh/ho-so.md`, `ho-so-kenh/luat-noi-dung.md`. Ví dụ mang nhãn «tập mẫu EP001» (Điện Biên Phủ 1954) chỉ để minh hoạ.

Mẫu đã chạy: tập mẫu EP001 (v1 01/11, v3, v4 02/11/2026). File cuối dựng ở `<output>/<ngày>-<tập>\final\`; user duyệt xong thì **chuyển** (không chép, tiết kiệm ổ) video về `tap/<slug>/Final/` cùng phụ đề, `do-cuoi`, `check` (video không lên Git). Kết thúc bằng **DỪNG, user xem bản cuối**.

Vì sao hai cổng: chủ đề lịch sử dân tộc thì một sai về xưng hô, số liệu là khán giả bắt ngay và lan trong bình luận (yêu cầu của chủ kit: "không được có 1 tý sai phạm"). Lỗi nội dung phải chặn **trước** khi đọc giọng và render, vì sửa sau tốn tiền giọng và hàng giờ dựng lại. Lỗi kỹ thuật thì chỉ thấy trên file cuối.

## A. QC nội dung (trước khi đọc giọng, trước mỗi lần render lại)
1. **Cổng máy, tự chạy, không tin báo cáo người viết** (mọi cổng 0 lỗi mới đi tiếp):
   - `python -I tools/loc-chinh-sach/quet.py <kịch bản> <lời đọc>` → 0 CHẶN.
   - `python -I -X utf8 tools/lichsu/kiem-da-chot.py <lời đọc> <kịch bản> <phan-canh.md> <dung-the.py>` → 0 chỗ phạm (sổ `kenh/cach-noi-da-chot.tsv`).
   - `python -I -X utf8 tools/lichsu/kiem-so.py <so-so-lieu.csv> <nguon-tho>` → 0 dòng lỗi (câu trích khớp trang gốc). Dòng mới phải tải trang bằng `tools/lichsu/lay-trang.py` trước.
   - `trung-lap.py` (bộ so ở `goha-ls-kich-ban`) → ≤ 1 %, 0 câu ≥ 10 tiếng.
2. **Xưng hô đúng thời điểm sự kiện** (user chốt 02/11/2026; luật sử Việt, ngách khác theo `luat-noi-dung.md`): nhân vật phía ta có quân hàm hoặc chức vụ **lúc đó**; quân hàm về sau (vd Đại tá, Thượng tướng khi kể hồi ký) phải kèm «khi ấy/lúc đó ông là <chức vụ>». QĐNDVN phong quân hàm lần đầu năm 1958 (Nghị định 306-TTg), nên năm 1945–1957 phía ta chỉ có chức vụ. Không có nguồn chức vụ thì dùng đúng chữ nguồn gọi (vd «chiến sĩ»), không đoán. Phía đối phương không được trang trọng hơn phía ta. Thêm luật máy cho nhân vật mới vào sổ cách nói `kenh/cach-noi-da-chot.tsv` (mẫu `quan-ham-thoi-diem-giong`).
3. **Dữ kiện còn treo phải tra nguồn trước khi viết**: giao sub-agent tra nguồn chính thống (QĐND, Nhân Dân, TTXVN, Chính phủ, VTV, bảo tàng; không nhận Wikipedia), chép nguyên văn; Claude **tự mở lại** ít nhất các trang quyết định danh hiệu, quân hàm, con số rồi mới ghi sổ. Nguồn mâu thuẫn (vd ngày phong hàm) thì lời không nêu chi tiết đó.
4. **Bình luận khán giả** (chủ đề nhạy cảm): đọc 100 % bình luận các video cùng đề tài (cả phần đuôi bình luận dài), đối chiếu mọi chi tiết khán giả hay sửa với sổ; ghi kết quả vào `checks.md` của tập (không lưu bình luận người khác vào repo).
5. **Reviewer Opus ngữ cảnh mới** soát riêng phần sửa: mỗi câu sửa **cùng câu trước và câu sau** (tập mẫu EP001 v4: sửa câu 156 «rơi vào trận địa ta» làm câu 158 không đổi «thả dù ra ngoài trận địa» thành nghe ngược), chữ trên hình đã sửa, kịch bản khớp lời, json phân cảnh đã sinh lại. Chỉ nhận PHẢI SỬA có bằng chứng; NÊN SỬA về nghĩa, xưng hô thì làm luôn.
6. **Lãnh tụ và giọng dựng lại** (luật cứng, user chốt 03/11/2026): lời lãnh tụ không có trong giọng; ảnh lãnh tụ chỉ ảnh thật cắt khung vuông vắn đóng khung, không tách nền, không sửa mặt; mọi cảnh có giọng dựng lại lời người khác (sĩ quan nước ngoài, chiến sĩ, nhân chứng, nhà thơ…) có chữ «mô phỏng lại» trên hình.
7. **Chữ trên hình**: mọi thẻ có số ghi «Nguồn:» đúng báo có dữ kiện; chữ «trên/hơn/khoảng» đúng `cach_noi` của sổ; danh hiệu (Anh hùng) có dòng sổ; thẻ tên đồng bộ với lời.

## B. QC kỹ thuật file cuối
1. **STT trên bản trộn** (bước trả phí, báo trong chat): `ffmpeg -i <master.wav> -ac 1 -b:a 128k x.mp3`, `python -I -X utf8 tools/kit/kit.py chep-loi x.mp3 --adapter elevenlabs --lang <ngôn ngữ phim> --out-dir stt`, `python -I -X utf8 tools/kit/kit.py so-loi --text <lời chuẩn> --words stt/x.words.json --lang <ngôn ngữ phim> --min 0.97` (chạy được ngay sau khi trộn âm, không cần chờ hình). *Nhánh thay thế:* không có ElevenLabs thì `--adapter deepgram`; không có cả hai thì `kit.py chep-loi x.mp3 --adapter whisper` (faster-whisper chạy máy, không cần khoá; chậm trên CPU với phim dài) rồi `so-loi`; Whisper `medium` nghe nhầm cả chữ thường (96,8 % trên đoạn thử 03/11), nên mọi chỗ lệch phải nghe tai. Soi chéo bằng máy thứ hai chỉ làm được khi có hai máy; chỉ có Whisper thì nghe tai các chỗ lệch. Bỏ qua: cách viết (tên Pháp kiểu Latin, mồng/mùng, «xê» → «c»), nhãn tiếng nền, thanh điệu đã chấp nhận. Chỗ STT trả cụm lạ («nhạc nền», «đọc lại») thay chữ: cắt đoạn ≥ 12 s **từ đầu câu** (mốc ở `moc-cau.json` + intro) cho Deepgram (`chep-loi --adapter deepgram`); hai máy cùng nghe sai thì sửa.
2. **Soi tờ** (luật bản đồ áp cho mọi phim có bản đồ Việt Nam; `soi-qc.py` chép từ `san-xuat/` của tập mẫu nằm ở `mau/dien-bien-phu-1954/` (ở repo của chủ kit là `tap/EP001-dien-bien-phu-1954/`) sang `tap/<EPxxx-slug>/san-xuat/` và sửa bảng dữ liệu đầu tệp theo tập mới nếu P5 chưa chép): `python -I -X utf8 tap/<slug>/san-xuat/soi-qc.py <final.mp4> --ten vN --check <kết quả kit.py kiem>` → `soi-ban-do-vN.jpg` (mọi vnmap × 3 khung: Hoàng Sa, Trường Sa cùng màu Việt Nam có nhãn, «Biển Đông», không lưỡi bò, Tây Bắc không chạm biển), `to-khung-64-vN.jpg`, `check-vN.md` (cảnh báo tra về mã cảnh, ghi «ranh với» khi mốc sát cuối cảnh).
3. **Âm cuối**: không dùng loudnorm một lượt hay bộ `aac` mặc định (từng đẩy đỉnh +1,7 … +2,6 dBTP). Master tăng mức cố định: `python -I -X utf8 tools/kit/kit.py master --am <mix.wav> --ra <master.wav> --lufs -14 --tp -3` (máy có VST trả phí thì `hau-ky-am.py`, Pro-L 2 trần −3,5 dBTP; mức Tiết kiệm, Miễn phí dùng chuỗi ffmpeg ở `goha-ls-dung`); ghép bằng `python -I -X utf8 tools/kit/kit.py ghep --hinh <hình.mp4> --am <master.wav> --ra <final.mp4>` (`aac_mf` 256k, tự đo lại) hoặc `ghep-hinh.py --am <master> --ra <final>`.
3a. **Cân bằng nhạc, lời** (trước khi cho user xem): `python -I -X utf8 tools/lichsu/do-am.py <thư mục âm> --ten <tập> --chuong tap/<slug>/san-xuat/phan-canh.json --do-thi am-vN.png > do-am-vN.txt` đo trên stem giọng, nhạc, tiếng động của bản trộn cuối (`<tập>-stem-*.wav`, hoặc `<tập>-tach-*.wav` tách Demucs). Mã thoát 1 (có CHẶN) thì sửa trộn rồi đo lại, chưa cho user xem. Mã 2 là sai đầu vào: sửa lệnh, không sửa trộn. Mã 3 là chỉ có bản trộn, không đo được: lấy stem. CẢNH BÁO ghi vào `checks.md` kèm lý do. Đoạn cao trào cố ý thì khai `--loai-tru <giây-giây>` và ghi lý do. Chỉ số, ngưỡng và cách dùng ở đầu script.
4. **Đo trên file cuối**: `ffmpeg -i final.mp4 -af ebur128=peak=true -f null -` → I −14 ± 0,5 LUFS, đỉnh ≤ −1 dBTP; lưu `do-cuoi-vN.txt`.
5. **`python -I -X utf8 tools/kit/kit.py kiem final.mp4 --lufs -14 --size 1920x1080 --fps 24 > check-vN.txt`**: cảnh báo trùng bản đã duyệt và cố ý (khung đầu thẻ nền tối, thẻ/ảnh/sa bàn đứng yên) thì chấp nhận; khung chớp ở đầu cảnh 3D là lỗi (ghep-hinh tự thay, xem `goha-ls-dung`).
6. **Dấu kênh**: `ghep-hinh.py --soi-dau <thư mục>` xuất khung Full HD mỗi lần đổi góc; soát không đè thẻ tên, nhãn ngày, tiêu đề thẻ, ghi nguồn, không chạm ảnh lãnh tụ; đưa đường dẫn cho user mở cỡ thật.
7. Ghi `checks.md` mục vN (kết quả, chi phí), `progress.md`, commit (tách nhóm: nội dung, code, trang dựng sinh lại); báo user đường dẫn file và những điểm cần mắt người. **DỪNG.**

## Bài học (tập mẫu EP001)
- Tiếng động trong lời ≤ −30 dB, máy chữ ≤ 2 s: ở −20 dB STT tụt 98,1 % → 95,8 %.
- Deepgram viết số kiểu khác («một trăm ba mươi ba», «h30», «2.412»): là cách viết, không phải lỗi đọc.
- STT bản trộn chỉ khác lời ở thanh điệu (chèn/chen) thì đo các lớp tại chữ đó trước khi kết luận lấp lời.
- Bộ `aac` của ffmpeg vọt đỉnh +2…+5 dB ở cú nổ: dùng `aac_mf` 256k, đo ebur128 trên file mp4, không trên WAV.
- (v4) Tờ soi ghi đè tên bản trước: luôn dùng hậu tố `--ten vN`.
- (v4) Câu đọc lại sau khi đã dựng: đệm bội số khung (`goha-ls-giong`) giữ cảnh phía sau nguyên khung; vẫn có vài cảnh ±1 khung do mốc làm tròn mili giây → so `phan-canh.json` cũ và mới để lấy danh sách dựng lại.

## Nhánh thay thế khi thiếu công cụ
- Không có sub-agent Opus ngữ cảnh mới riêng thì mở một lượt đọc mới (cùng brief, chỉ đưa các câu sửa kèm câu trước, sau); không đọc lại bằng chính ngữ cảnh đã viết.
- Không có Agy, Codex: dùng sub-agent Opus cho cả phản biện nội dung (bước A.5); ghi vào `checks.md` là phản biện cùng hãng.
