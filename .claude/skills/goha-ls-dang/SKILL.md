---
name: goha-ls-dang
description: P7 Bộ đăng của quy trình phim tài liệu lịch sử Việt Nam — từ file cuối đã đạt QC (goha-ls-qc) làm ra gói đăng chép dán thẳng vào YouTube Studio trong Final/EPxxx-postpack.md: tiêu đề (câu hỏi hoặc nghịch lý trong 40 ký tự đầu, có trong sổ số liệu, không clickbait), mô tả SEO/AEO (cảnh mở, hỏi đáp nhanh, chương, nguồn ghi đủ), thẻ, hashtag, 3 thumbnail A/B/C cho Test & Compare (chỉ ảnh tư liệu thật, không ảnh AI), phụ đề dịch, bình luận ghim, khai báo nội dung tổng hợp; sub-agent viết chữ phải dán khối luật mục C của bộ lọc, máy quét quet.py 0 CHẶN; rồi DỪNG cho user duyệt. Dùng ngay khi user nói "P7", "bộ đăng", "postpack", "tiêu đề mô tả thẻ", "thumbnail", "ảnh bìa", "đăng tập", "phụ đề tiếng Anh", "bình luận ghim", hoặc khi tập đã qua P6 mà chưa có postpack — kể cả khi không nhắc tên skill. Không dùng để cắt Shorts (goha-ls-shorts) hay QC file (goha-ls-qc).
---

# P7 Bộ đăng

Danh tính kênh (tên kênh, ngách, ngôn ngữ, logo, màu, font, khung tên video) đọc từ `ho-so-kenh/ho-so.md`; luật nhạy cảm riêng ở `ho-so-kenh/luat-noi-dung.md`. Các tệp `kenh/mo-ta-chuan.md`, `kenh/thumbnail-chuan.md`, `kenh/seo-kenh.md`, `kenh/khung-kenh.md`, `kenh/lich-noi-dung.md` do K2 (`goha-ho-so-kenh` bước 10) tạo từ khuôn; thiếu tệp nào thì DỪNG và quay lại K2, đừng tự bịa chuẩn. Đường dẫn dạng `<output>` là khoá trong `cau-hinh.toml`. Ví dụ có nhãn «tập mẫu» là tập 1 Điện Biên Phủ của chủ kênh, chỉ để hình dung, đừng chép nội dung.

**Đầu vào:** file cuối đạt P6 ở `<final>/EPxxx-<slug>/` (khoá `final` trống thì ở `tap/<tập>/Final/`), phụ đề `.vi.srt`, sổ số liệu (`ke-hoach/so-so-lieu.csv`), sổ tài sản (nguồn ảnh, phim), mốc chương lấy từ bản dựng cuối (`san-xuat/moc-cau.json`).
**Đầu ra:** `Final/EPxxx-postpack.md` sạch, chép dùng luôn; `EPxxx-thumbnail-a/b/c.jpg`; `EPxxx-<slug>.<ngôn ngữ>.srt`. Mọi tệp mang tiền tố `EPxxx-`. Video không lên Git.

Vì sao nghiêm: chữ cho người xem quyết định video có biểu tượng quảng cáo xanh hay không, và mô tả sai nguồn là chỗ khán giả sử bắt đầu tiên. Chi tiết từng khuôn ở `references/`.

## Các bước
1. **Dọn đầu vào.** Xác nhận P6 đạt (`checks.md` có mục «đạt»). Chạy lại `python -I -X utf8 tools/kit/kit.py kiem <file cuối>` nếu file đổi sau P6. Mốc chương lấy từ bản dựng cuối, mở video nhảy thử từng mốc.
2. **Viết chữ bằng sub-agent Sonnet** (tiêu đề, mô tả, thẻ, chữ bìa, bình luận ghim). Mỗi prompt **dán nguyên khối luật mục C** của `kenh/bo-loc-chinh-sach-yt.md` cộng luật cứng của `CLAUDE.md`, chỉ cho đọc sổ số liệu, kịch bản, sổ cách nói đã chốt; dữ kiện ngoài sổ là cấm. Một sub-agent khác phản biện (Agy nếu có, không thì Opus ngữ cảnh mới). Claude tự rà dữ kiện theo sổ. Khuôn: `references/khuon-postpack.md`.
3. **Tiêu đề:** 2–3 phương án chấm tò mò, rõ chủ đề, đúng dữ kiện, an toàn chính sách; chính + bản thử A/B. Câu hỏi hoặc nghịch lý nằm trọn trong 40 ký tự đầu; mọi chữ đúng nghĩa đen theo sổ; không «sốc», «chấn động», «nhục», «đại bại».
4. **Mô tả, thẻ, hashtag, chương:** theo `kenh/mo-ta-chuan.md` (khuôn 7 khối, nguồn ghi đủ năm thứ, 3 hashtag, 20–25 thẻ ≤ 480 ký tự, cách nhau ", " không ngoặc kép). Thêm khối «Hỏi đáp nhanh» (câu hỏi người ta gõ + đáp 1–2 câu có nguồn) để máy trả lời trích.
5. **Thumbnail A/B/C:** theo `kenh/thumbnail-chuan.md` và `references/thumbnail-ab.md`. Chỉ ảnh tư liệu thật hoặc đồ hoạ code; kênh sử Việt **cấm ảnh AI**, không ảnh lãnh tụ, không máu. Soi cỡ 168×94.
6. **Phụ đề dịch** (khi hồ sơ kênh có ngôn ngữ phụ): `references/phu-de-dich.md`.
7. **Bình luận ghim:** 1 dữ kiện có nguồn + 1 câu hỏi mời người xem chọn hoặc kể, không gây cãi chính trị.
8. **Khai báo nội dung tổng hợp** và cài đặt tải lên: `references/cong-quet-va-khai-bao.md`.
9. **Cổng máy (0 CHẶN mới đi tiếp):**
   - `python -I tools/loc-chinh-sach/quet.py --tieu-de Final/EPxxx-postpack.md`
   - `python -I tools/loc-chinh-sach/quet.py --vi-tri metadata Final/EPxxx-postpack.md` (cùng bộ, tên khác; chạy cả hai cho chắc) và `quet.py` thường trên từng `.srt` (30 s đầu xét gắt)
   - `python -I -X utf8 tools/lichsu/kiem-da-chot.py Final/EPxxx-postpack.md` → 0 chỗ phạm
   - Kiểm tay: mô tả ≤ 4.800 ký tự; mỗi dòng nguồn có dòng trong sổ tài sản; mỗi số có dòng trong sổ số liệu; ≥ 40 % dòng nguồn là nguồn chính thống Việt Nam.
10. **DỪNG, user duyệt bộ đăng.** Đưa đường dẫn postpack, 3 bìa, tiêu đề chính và thử, danh sách CẢNH BÁO còn giữ kèm lý do. Chỉ sau khi duyệt mới ghi `EPxxx-postpack.md` là «đã duyệt ngày …» và commit.

## Sau khi user đăng
- Ghi vào `kenh/lich-noi-dung.md`: ngày đăng, link, mã bìa/tiêu đề đang thử. Test & Compare: sau 7–14 ngày ghi bản thắng và số đo (lượt hiển thị, tỉ lệ nhấp, thời lượng xem) vào cùng chỗ.
- Video bị vàng: xem mục bị gắn, sửa, gửi xét lại, ghi bài học vào `tools/loc-chinh-sach/tu-cam.tsv` kèm bằng chứng.

## Bài học (tập mẫu)
- Tiêu đề cắt quanh ký tự 50–60: đẩy câu hỏi vào 40 ký tự đầu.
- Bìa «chữ gợi tò mò» phải đúng nghĩa đen: «KHÔNG THẤY PHÁO» bị loại vì sổ chỉ ghi «không khống chế được».
- Từ hỏi lệch nghĩa bị loại («SAO PHẢI» gợi ta bị ép; «SAO LẠI» đạt).
- Mốc chương lấy từ kịch bản sẽ lệch bản dựng; luôn lấy từ bản dựng cuối.
