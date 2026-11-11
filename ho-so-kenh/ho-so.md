# Hồ sơ kênh: 戦陣再審

- Trạng thái: đã duyệt (2026-11-10)

## 1. Kênh
- Tên kênh: `戦陣再審` · handle: `@戦陣再審` (tra 2026-11-10; chưa tồn tại trên YouTube)
- Ngách: Lịch sử quân sự Nhật Bản — phân tích trận đánh thời Meiji, Russo-Japanese War, WWI, WWII qua bản đồ và lý luận chiến thuật
- Ngôn ngữ, thị trường: Tiếng Nhật, thị trường Nhật trong nước
- Khán giả: Nam 30–70 tuổi, quan tâm lịch sử chiến tranh, lịch sử quân sự Nhật
- Độ dài tập: 20–30 phút · nhịp đăng: 2–3 tập mỗi tuần
- Mức chạy: Tiết kiệm (chốt 2026-11-04; lấy từ `kiem-may.md`)
- Công cụ thay thế đang dùng: xem mục 6

## 2. Mẫu để bám
- Model Link (benchmark, chờ 60 ngày): `硝煙の記憶` · `@Những ký ức về thuốc súng` (UCuV7KFF6aSB9JjIbwnYP3Kw)
  - Lý do: format AI voice + bản đồ + chân dung tư liệu, không người thật on-camera; 2k sub nhưng ~300k view/video (trung_vi/sub ≈ 148) — ngách đang được thuật toán ưu đãi mạnh; đúng ngách Russo-Japanese War và WWII
  - Kiểm lại 2027-01-09: nếu đạt ≥10 video đủ 30 ngày tuổi mà trung_vi/sub vẫn cao → chính thức thay thế dự phòng
- Model Link dự phòng active: `戦いのヒストリア` (UCBbD-KHFEOaMVP_Q98rl9eA) — hạng 8, khoảng hạng 2–8, 167k sub, trung vị 142k view; AI voice ゆっくり + battle maps
- Điều học: format một trận/episode cụ thể; tiêu đề trích dẫn kịch tính; AI voice + bản đồ chiến thuật; nhịp 3 video/tuần
- Điều cố ý làm khác: không thumbnail mặt người AI-enhanced; chủ đề thiên Meiji/WWII chứ không rải rác; giọng ElevenLabs/Kokoro tự nhiên hơn ゆっくり
- Không học từ 非株式会社いつかやる: kênh lai có chuỗi bản đồ animation (học được) nhưng cũng có対談/現地/người thật on-camera (không làm được với AI voice+graphics)
- Sheet top 20: https://docs.google.com/spreadsheets/d/1Xn2SGA1XWLpvDNIs4wm6ZKPZL1mx5tVhgICIZz62t58/edit?usp=sharing · ngày đo: 10/11/2026

## 3. Giọng người dẫn
- Nhà cung cấp: ElevenLabs
- `voice_id`: `tu1x0Bmib6kmsrXy16CZ` (khác `3VnrjnYrskPMDsapTr8X` ✓) · tên giọng: (tra trong ElevenLabs dashboard)
- Model: `eleven_v4` · ngôn ngữ (`language_code`): `ja` (đổi từ multilingual_v2 sang v4 ở EP001 P4, 2026-11-11; v4 biểu cảm hơn, hỗ trợ thẻ audio; đọc chậm hơn ~12% so v2)
- Thẻ đầu bài: KHÔNG dùng `[fast-paced]` cho cả tập (phần phân tích cần nhịp tài liệu); nhịp nhanh là ở cắt cảnh (P3)
- Cách đọc: từng đoạn ≤ 500 ký tự; không đọc cả bài một lần (tránh lỗi ngữ điệu giữa đoạn dài)
- Quy tắc sửa một câu: đọc lại câu trước–câu đó–câu sau trong một lần gọi rồi cắt lấy câu giữa
- Ghi chú: cần `ELEVENLABS_API_KEY` trong `.env` (hiện thiếu — dán key vào trước P4). Model `eleven_multilingual_v2` hỗ trợ tiếng Nhật; nếu kit báo lỗi model thì thử `eleven_turbo_v2_5`.
- Chi phí đã báo: chưa nghe thử; người dùng chọn dùng luôn ở P4

## 4. Thương hiệu
- Bảng màu: nền `#111111` · nhấn `#cc2222` · chữ chính `#f0e8d8` · chữ phụ `#9b1c1c` · thẻ cảnh báo `#cc2222`
- Kết quả lệnh kiểm màu khác kênh mẫu: ĐẠT (2026-11-10)
- Font tiêu đề: `NotoSerifJP-Bold.ttf` (OFL, Noto CJK) · font nội dung: `NotoSerifJP-Regular.ttf` (OFL)
- Tagline: 地図と論理で戦史を読み解く
- Tệp (trong `kenh/thuong-hieu/ra/`):
  - Ảnh đại diện: `anh-dai-dien-800.png` (1433×1433 → crop 800×800), `anh-dai-dien-98.png`, `anh-dai-dien-40.png`
  - Banner: `banner.png` (2217×940)
  - Dấu kênh: `dau-kenh-150.png`
  - Nhận diện thẻ chữ: `kenh/thuong-hieu/nhan-dien-kenh.js` (**bắt buộc trước P5**)
- Cấm riêng: không đặt logo trên nền cùng màu đỏ; không ghép logo với biểu tượng quân hiệu hoặc cờ quân đội thật; không dùng 旭日旗 làm biểu tượng kênh

## 5. Luật nội dung
- Luật riêng của ngách: `ho-so-kenh/luat-noi-dung.md`
- Bộ lọc chính sách YouTube: `kenh/bo-loc-chinh-sach-yt.md`, máy quét `tools/loc-chinh-sach/quet.py`
- Tệp kênh dùng cho P2, P7, P8: `kenh/khung-kenh.md`, `kenh/lich-noi-dung.md`, `kenh/thumbnail-chuan.md`, `kenh/mo-ta-chuan.md`, `kenh/seo-kenh.md`; sổ tay văn phong `kenh/hoc-shu/so-tay-van-phong.md` (do bước Shu của P2 tạo tập đầu)
- Sổ cách nói đã chốt: `kenh/cach-noi-da-chot.tsv` (máy kiểm `tools/lichsu/kiem-da-chot.py`)

## 6. Công cụ thay thế đang dùng
- **Giọng:** ElevenLabs `eleven_multilingual_v2`, `ja` — chưa nghe thử; thử ở P4. Cần dán `ELEVENLABS_API_KEY` vào `.env` trước P4.
- **Trộn & master:** `kit.py tron` và `kit.py master` thay Goha AVS (chưa cài Goha AVS).

## 7. Nhật ký thay đổi hồ sơ
- 2026-11-10: tạo hồ sơ; người dùng duyệt ngách (kênh quân sự Nhật Meiji/WWII), Model Link (硝煙の記憶 benchmark + 戦いのヒストリア dự phòng), thương hiệu (tự vẽ logo, đỏ-đen).
