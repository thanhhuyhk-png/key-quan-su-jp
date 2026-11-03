---
name: goha-ls-shorts
description: P8 Shorts của quy trình phim tài liệu lịch sử Việt Nam — từ file cuối đã đạt QC và các stem giọng, nhạc, tiếng động của tập cắt 3–5 Shorts dọc (đoạn chọn theo khuôn học từ báo cáo Shu Shorts, cắt đúng ranh câu, không đọc giọng mới, không tốn tiền giọng), dựng khung dọc 9:16 (bản đối chứng vuông 1:1), cháy phụ đề, bìa 9:16 chỉ ảnh tư liệu thật, chữ Shorts, SEO gọn cho YouTube Shorts, Facebook Reels, TikTok, đặt tên Final/shorts/EPxxx-Snn-<slug>/, rồi DỪNG cho user duyệt Shorts mẫu đầu tiên; sau 7 ngày ghi bản thắng Test & Compare và số đo vào tập. Dùng ngay khi user nói "P8", "Shorts", "cắt Shorts", "Reels", "TikTok", "video dọc", "bìa 9:16", "đăng Shorts", hoặc khi phim dài đã đạt P6 và đã có bộ đăng (P7) — kể cả khi không nhắc tên skill. Không dùng để dựng phim dài (goha-ls-dung) hay bộ đăng phim dài (goha-ls-dang).
---

# P8 Shorts

Danh tính kênh (tên kênh, màu, logo, nền tảng đăng) đọc từ `ho-so-kenh/ho-so.md`. `<output>` là khoá trong `cau-hinh.toml`. Ví dụ có nhãn «tập mẫu» là tập 1 Điện Biên Phủ của chủ kênh, chỉ để hình dung.

**Đầu vào:** file cuối đạt P6 (`Final/EPxxx-<slug>.mp4`), phụ đề `.vi.srt`, ba stem sau trộn của tập (giọng, nhạc, tiếng động) và bản master ở `<output>`, sổ số liệu, sổ tài sản. **Giữ nguyên các stem** đến khi Shorts xong; đừng dọn trước.
**Đầu ra:** `Final/shorts/EPxxx-Snn-<slug>/` gồm `EPxxx-Snn.mp4` (1080×1920, 24 fps, ≤ 60 s), `EPxxx-Snn-bia.jpg` (9:16), `EPxxx-Snn-seo.md`; cộng `Final/shorts/EPxxx-shorts-cach-dang.md` chung. Video không lên Git.

Vì sao làm riêng một bước: Shorts là cửa kéo người xem về phim dài; làm ẩu thì lệch dữ kiện hoặc lộ phim thô quá 10 s, còn lặp một khuôn quá nhiều thì dính chính sách «nội dung không chân thực». Chi tiết ở `references/`.

## Các bước
1. **Chọn đoạn** (`references/chon-doan-va-khuon-shu.md`): 3–5 Shorts, mỗi cái một câu hỏi hoặc con số lạ ở giây đầu, trả lời được trong chính Shorts, kết trỏ về phim dài. Chọn theo số khối của `.vi.srt`, chỉ cắt tại ranh câu. Căn cứ bình luận khán giả nhắc nhiều (nếu đã có từ P1/P6) và khuôn Shu. Bỏ mọi đoạn có lãnh tụ.
2. **Lập bảng đoạn** `tap/<tập>/ke-hoach/shorts.md`: mã Snn, tên làm việc, khối lời, độ dài ước tính, câu mở, dải chữ trên (hai dòng), cơ sở chọn. Trình user trong cùng cổng ở bước 5 (không dựng khi chưa có bảng).
3. **Dựng Shorts mẫu đầu tiên** (S1) theo `references/dung-shorts.md`: chép `shorts.py`, `ve-bia-shorts.py` của tập mẫu, sửa bảng đoạn và đường dẫn, dựng cả bản dọc 9:16 và vuông 1:1 làm đối chứng. Hình và giọng lấy lại từ bản đã duyệt nên không tốn tiền giọng hay nhạc.
4. **Chữ Shorts** (`references/seo-da-nen-tang.md`): sub-agent Sonnet viết, **dán nguyên khối luật mục C** của `kenh/bo-loc-chinh-sach-yt.md`, người phản biện khác, Claude rà theo sổ. Quét `python -I tools/loc-chinh-sach/quet.py --tieu-de <seo.md>` cộng `--vi-tri metadata` và `python -I -X utf8 tools/lichsu/kiem-da-chot.py <seo.md>`; 0 CHẶN, 0 chỗ phạm mới đi tiếp.
5. **DỪNG, user duyệt Shorts mẫu đầu tiên:** đưa mp4 (cả hai khung), bìa, SEO, bảng đoạn. Chưa duyệt thì không dựng lô.
6. **Dựng S2–Snn** theo khung user chọn; QC từng cái (bước dưới).
7. **QC từng Shorts:** nghe lại mọi chỗ nối; chép lời `python -I -X utf8 tools/kit/kit.py chep-loi` rồi `so-loi --min 0.97` với lời chuẩn; soi khung đầu, giữa, cuối và mọi khung bản đồ (Hoàng Sa, Trường Sa, Biển Đông); `python -I -X utf8 tools/kit/kit.py kiem <mp4> --lufs -14 --size 1080x1920 --fps 24`; đo ebur128 trên file mp4: −14 ± 0,5 LUFS, đỉnh thật ≤ −1 dBTP; dòng nguồn đọc được trên mọi khung.
8. **Đặt tên, ghi `EPxxx-shorts-cach-dang.md`** (thứ tự đăng, nơi gắn liên kết phim dài mỗi nền tảng, nhãn AI), commit, báo user đường dẫn. Thứ tự đăng: mỗi ngày một video, sau khi phim dài đã lên.

## Sau 7 ngày kể từ video đầu đăng
Mở `references/do-sau-7-ngay.md`: lấy số đo từng Shorts và từng khung, ghi **bản thắng** (dọc hay vuông; bìa nào; câu mở nào) cùng số đo vào dòng của tập trong `kenh/lich-noi-dung.md` và `Final/shorts/EPxxx-shorts-cach-dang.md`. Tập sau dùng bản thắng làm mặc định.

## Bài học (tập mẫu)
- Khuôn thắng của một cụm kênh (83 % khung vuông) là thói quen của họ, không phải quy luật: đừng chọn khung chỉ theo mẫu, hãy thử dọc và vuông.
- Cắt giữa câu thì cụt chữ ở chỗ nối; chỉ cắt ranh câu, kéo mỗi đoạn thêm 0,2 s vào khoảng lặng rồi crossfade.
- Bìa dựng từ chính khung của Shorts hoặc phim tư liệu; cảnh đồ hoạ 3D không dùng làm nền bìa, mượn khung phim thật của Shorts khác.
