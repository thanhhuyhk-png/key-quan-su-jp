---
name: goha-ls-giong
description: P4 Giọng của quy trình sản xuất phim tài liệu lịch sử, quân sự (kit Goha Lịch Sử) — đọc lời đã chốt bằng giọng kênh (theo `ho-so-kenh/ho-so.md`: ElevenLabs, hoặc VieNeu / Kokoro ở mức Tiết kiệm, Miễn phí) theo lượt ≤ 5.000 ký tự cắt ở ranh chương, cân độ to, cắt câu theo mốc chữ TTS, nối kèm khoảng lặng có tên của phân cảnh, kiểm STT ElevenLabs, soi chéo chỗ nghi bằng Deepgram, đọc lại câu sai (kèm câu trước và sau), ghi moc-cau.json để đo lại phân cảnh. Bước trả phí: báo chi phí trong chat. Dùng ngay khi user nói "P4", "làm giọng", "lồng tiếng tập", "đọc lời", "ElevenLabs", hoặc khi tập đã có `san-xuat/phan-canh.md` ĐẠT mà chưa có đường giọng — kể cả khi không nhắc tên skill. Không dùng để viết lời (goha-ls-kich-ban) hay trộn nhạc (goha-ls-dung).
---

# P4 Giọng (Goha Lịch Sử)

Đường dẫn dạng `<output>`, `<nghien_cuu>`, `<vst_python>`, `<chep_loi>` là khoá trong `cau-hinh.toml` ở gốc repo (mẫu: `cau-hinh.mau.toml`; script đọc bằng `tools/cau_hinh.py`). Đường dẫn khác tính từ gốc repo.

Giọng của kênh nằm ở `ho-so-kenh/ho-so.md` mục Giọng: nhà cung cấp, `voice_id`, model, thẻ đầu bài, quy tắc sửa câu. Đọc đúng các giá trị đó, không đoán và không tự đổi giọng giữa chừng một tập. Dưới đây `<voice_id>`, `<model>`, `<thẻ>` là các giá trị ấy. Ví dụ tập mẫu EP001 (kênh chủ, ElevenLabs `eleven_v4`, thẻ `[fast-paced]`): model này bỏ qua `speed`, nên **không** tăng tốc bằng xử lý sau. Đầu ra: `<output>/<ngày>-<tập>\giong\giong-v1.wav` (48 kHz, −18 LUFS) và `tap/<slug>/san-xuat/moc-cau.json` (mốc từng chữ, khoảng lặng). Mẫu đã chạy: tập mẫu EP001, 01/11/2026, 13 phút, 15:18.

**Bước trả phí:** trước khi gọi, báo trong chat số ký tự TTS (≈ credit) và số phút STT, rồi chờ người dùng đồng ý. Mức Miễn phí không có bước trả phí.

**Luật cứng về giọng (CLAUDE.md, user chốt 03/11/2026):** cấm mọi AI với lãnh tụ Việt Nam (không giả giọng, không đọc lại lời họ; lời họ chỉ hiện chữ trên hình, giọng dẫn dừng lại khoảng lặng). Giọng dựng lại lời trích của người khác (sĩ quan nước ngoài, chiến sĩ, nhân chứng, nhà thơ…) được làm, nhưng cảnh đó phải ghi «mô phỏng lại» trên hình (kiểm ở P3, P6) và không nhái giọng thật của người có thật.

**Nhánh thay thế giọng (mức Tiết kiệm / Miễn phí):**
- Tiếng Việt, không có ElevenLabs: VieNeu V4 (tính token) hoặc V3 chạy máy (miễn phí). Giọng kém tự nhiên hơn, nên **đo đuôi câu** trước khi cắt: `python -I -X utf8 tools/vieneu-ab/tail.py <wav…>` (đuôi < 25 ms nghi bị cắt cụt), so các biến thể bằng `tools/vieneu-ab/ab.py`. Lượt đọc, cắt câu, `moc-cau.json` giữ nguyên cách làm; mốc chữ lấy bằng STT ở bước 5 nếu máy đọc không trả mốc.
- Tiếng Anh, không có ElevenLabs: Kokoro chạy máy (ít cảm xúc hơn); cùng quy trình đo tốc độ ở P2.
- Giọng thay phải qua cùng cổng STT ≥ 97 % ở bước 5.

## Các bước
1. **Đối chiếu số còn treo trước khi đọc** (sửa lời sau khi có giọng rất tốn): dòng sổ chỉ một nguồn thì tìm nguồn thứ hai (WebSearch, WebFetch trích nguyên văn), ghi vào `ghi_chu_chenh_lech`, chạy `tools/lichsu/kiem-so.py`.
2. **Chia lượt ≤ 5.000 ký tự ở ranh chương** (trần một lần gọi ElevenLabs; `kit.py giong` báo lỗi khi vượt). Mỗi lượt: `<thẻ> ` + các câu nối bằng dòng trống. Ghi `phan.json` (`phan, tu, den`).
3. Gọi lần lượt (không song song, tránh giới hạn tốc độ):
   `python -I -X utf8 tools/kit/kit.py giong --text-file phan-<x>.txt --model <model> --voice <voice_id> --lang <ngôn ngữ trong ho-so.md> --out phan-<x>.wav --json > phan-<x>.json` (trả về mốc từng chữ; khoảng 40–60 s mỗi lượt 2.500–4.600 ký tự; khoá `ELEVENLABS_API_KEY` trong `.env` ở gốc repo).
4. **Chép script của tập mẫu trước lần chạy đầu của tập:** `dung-duong-giong.py` (và `kiem-phan-canh.py` nếu P3 chưa chép) không có sẵn trong tập mới. Chép từ `san-xuat/` của tập mẫu nằm ở `mau/dien-bien-phu-1954/` (ở repo của chủ kit là `tap/EP001-dien-bien-phu-1954/`) sang `tap/<EPxxx-slug>/san-xuat/`, mở đầu tệp và sửa bảng dữ liệu theo tập mới (tên tập, thư mục giọng, bảng khoảng lặng, đường dẫn trong `<output>`), không sửa logic trừ khi có lý do. Rồi `python -I tap/<slug>/san-xuat/dung-duong-giong.py <thư mục giọng>`: cân −18 LUFS từng lượt, cắt câu (`tools/eleven-speed/cat-cau.py`, gọi với `-I -X utf8`), kiểm chữ TTS khớp từng chữ lời, nối, chèn khoảng lặng có tên (bảng trong `phan-canh.md`), thay câu đọc lại trong `sua/`, ghi `moc-cau.json`.
5. **STT ElevenLabs** (mức Tiết kiệm: Deepgram, đổi `--adapter deepgram`; mức Miễn phí: `--adapter whisper` (faster-whisper chạy máy, không cần khoá; model `medium` đo 03/11: 27 s cho 23 s âm trên CPU, 96,8 % trên đoạn thử, nghe nhầm cả chữ thường nên chỗ lệch phải nghe tai)): `python -I -X utf8 tools/kit/kit.py chep-loi giong-v1.mp3 --adapter elevenlabs --lang vi --out-dir stt`, rồi `python -I -X utf8 tools/kit/kit.py so-loi --text loi-chuan.txt --words stt/giong-v1.words.json --lang vi --min 0.97`. Đạt khi ≥ 97 %. (Không có cờ tên riêng: API không nhận danh sách từ, nên tên Pháp lệch cách viết thì phân loại ở bước 6.)
6. **Phân loại chỗ lệch:** cách viết (mùng/mồng, tên Pháp viết kiểu Pháp, "c" cho "xê", "im lặng" ở khoảng lặng) bỏ qua. Chỗ đổi nghĩa thì cắt đoạn 5–8 s, cho Deepgram nova-2 nghe (`python -I -X utf8 tools/kit/kit.py chep-loi <wav> --adapter deepgram --lang vi --out-dir stt-dg`, khoá `DEEPGRAM_API_KEY`). **Hai máy cùng nghe sai thì đọc lại**; chỉ một máy sai, có cách giải thích bằng giọng Bắc (gi/d/r, vần -inh) hoặc đoạn cắt hụt mép → đạt.
7. **Đọc lại câu n:** `sua/sua-<n>.txt` = `<thẻ>` + câu n−1, n, n+1; gọi như bước 3, Deepgram nghe lại; còn nghi thì STT ElevenLabs đoạn đó. Chạy lại bước 4 (tự lấy câu giữa).
8. Đo: `ebur128` toàn bài, độ to từng câu (lệch chuẩn ≤ 1 dB; câu thay trong ±1 dB so với bên cạnh).
9. `python -I tap/<slug>/san-xuat/kiem-phan-canh.py` trên mốc thật: trần 5 s cho hạng B, A? hay vượt nhẹ → tách cảnh (`N:k`) hoặc lùi điểm vào.
10. Ghi `progress.md`, `checks.md` (kèm chi phí), commit (không đưa âm thanh lên Git).

## Bài học tập mẫu EP001
- Tốc độ thật khớp ước tính 242 tiếng/phút (giọng của tập mẫu; giọng khác tự đo ở P2): lời 3.555 tiếng → 15:18 kèm 25,5 s khoảng lặng.
- 4/223 câu cần đọc lại; ba lỗi là phụ âm đầu hoặc cuối bị nuốt ("chèn", "ngai", "dám"), một lỗi nguyên âm ("chính").
- `-I` bỏ qua biến `PYTHONIOENCODING`: script in tiếng Việt chạy bằng `python -I -X utf8`.
- Khe giữa câu trong một lượt có khi chỉ 0,03 s: cắt câu ở chỗ lặng nhất là đủ, không thêm khoảng nghỉ giả; nghỉ dài chỉ ở khoảng lặng có tên.

## Sổ cách nói đã chốt (chặn tái phạm, 02/11/2026)
- Mỗi lần user sửa một cách nói (xưng hô, từ, câu), ghi ngay một dòng vào `kenh/cach-noi-da-chot.tsv` (mã, regex cấm, cách đúng, lý do, nguồn) trước khi làm tiếp. Không chỉ ghi ở `checks.md` của một tập: tập mẫu EP001 v3 tái phạm «anh hy sinh» vì sửa ở Demo v11 chỉ nằm trong checks Demo.
- Cổng: `python -I tools/lichsu/kiem-da-chot.py <lời đọc> <kịch bản> <phân cảnh>` phải 0 chỗ phạm; `dung-duong-giong.py` tự gọi và dừng nếu phạm.
- Viết lại, rút gọn hay phục hồi một cảnh: lấy lời từ bản đã duyệt gần nhất (Demo, bản user đã nghe), không viết lại từ bản nháp cũ.

## Đọc lại câu sau khi phim đã dựng (tập mẫu EP001 v4, 02/11/2026)
- Ghi số câu vào `sua/dem-khung.json` (script sửa của tập, ví dụ `tao-sua-v4.py <n>…` trong thư mục dựng, tạo `sua-<n>.txt` và cập nhật tệp này): `dung-duong-giong.py` đệm lặng < 1 khung cuối câu để độ dài lệch bản cũ đúng bội số khung 24 fps. Mọi cảnh phía sau chỉ dời nguyên khung; cảnh phải dựng lại chỉ còn cảnh chứa câu sửa, cảnh giữ khoảng thở mới, và vài cảnh lệch ±1 khung do mốc làm tròn mili giây.
- Khoảng thở mới đặt tên bắt đầu bằng T…Z (vd `ZA`): máy kiểm phân cảnh coi là «cảnh trước giữ hình»; tên khác thì bắt phải có cảnh riêng.
- Câu thêm chữ thì dời mọi neo `@n:k`, `n:k` phía sau chữ thêm (grep cả `dung-*.py` và `phan-canh.md`); script sửa phải kiểm hết rồi mới ghi tệp (lỗi giữa chừng từng để lại lời đọc sửa dở).
- Sửa một câu có thể làm câu bên cạnh (không đổi) thành tối nghĩa: 156 «rơi vào trận địa ta» làm 158 «thả dù ra ngoài trận địa» nghe ngược. Cho reviewer ngữ cảnh mới đọc cả câu trước, sau trước khi đọc giọng.
