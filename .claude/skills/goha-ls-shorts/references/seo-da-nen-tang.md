# Chữ Shorts, SEO gọn đa nền tảng

Mỗi Shorts một tệp `EPxxx-Snn-seo.md`; một tệp chung `EPxxx-shorts-cach-dang.md` ở `Final/shorts/`. Mẫu thật (tập mẫu; ở repo chủ kit nằm ở `tap/EP001-dien-bien-phu-1954/`): `mau/dien-bien-phu-1954/Final/shorts/EP001-S01-keo-phao-vao-ra/EP001-S01-seo.md`.

## Brief cho sub-agent (Sonnet), phản biện bằng agent khác
Nội dung: danh sách Shorts kèm lời nguyên văn và dải chữ trên (xuất từ `.vi.srt` theo khối); phim dài (tiêu đề, độ dài); `ho-so-kenh/ho-so.md`; `kenh/cach-noi-da-chot.tsv`; báo cáo Shu mục «Khuôn rút ra» và «Nên tránh»; **nguyên khối mục C** của `kenh/bo-loc-chinh-sach-yt.md`; luật cứng `CLAUDE.md`. Dữ kiện chỉ lấy từ lời nguyên văn; không thêm số, ngày, tên đơn vị. Tệp duy nhất được ghi: một tệp nháp trong `ke-hoach/`. Không gọi mạng.

Luật ngôn từ đi kèm (chép từ luật cứng): nhân vật phía ta luôn có chức vụ hoặc danh hiệu hợp thời điểm; phía đối phương không trang trọng hơn phía ta, không lời hả hê; không nêu lãnh tụ trong chữ đăng; không «Chiến tranh Việt Nam»; số viết bằng chữ số.

## Mỗi Shorts có
1. **Rà dải chữ trên** (cháy trên hình): mặc định giữ. Đổi khi sai dữ kiện, video không trả lời được câu hỏi, hoặc phạm luật; ghi lý do.
2. **YouTube Shorts**
   - Tiêu đề: 3 phương án chấm 1–10 ở bốn tiêu chí (tò mò, rõ chủ đề, đúng dữ kiện, an toàn chính sách), chọn một. ≤ 60 ký tự, nhắm ~48; câu hỏi hoặc con số trong 40 ký tự đầu; không hashtag trong tiêu đề; viết hoa chữ đầu mỗi từ như phim dài.
   - Mô tả 3–5 dòng: dòng 1 câu móc; 1–2 dòng dữ kiện kèm nguồn đúng như trong lời; một dòng trỏ về phim dài (`Xem trọn phim "<tiêu đề phim dài>" trên kênh <tên kênh>`; liên kết thật gắn bằng «Video liên quan»); dòng cuối 3 hashtag có dấu theo khuôn kênh.
   - Thẻ: 10–15, tổng ≤ 300 ký tự, cách nhau ", ", không ngoặc kép.
3. **TikTok:** chú thích ≤ 150 ký tự cho phần hiện trước «xem thêm» (câu móc + trỏ về phim dài ở YouTube); 4–5 hashtag có dấu, được thêm một hashtag không dấu phổ biến (ghi lý do).
4. **Facebook Reels:** 2–3 câu (câu móc, một dữ kiện có nguồn, trỏ về phim dài); 3 hashtag như YouTube. Liên kết phim dài dán vào bình luận đầu.
5. **Bình luận ghim** dùng chung 3 nền tảng: một dữ kiện hoặc nhận xét ngắn + một câu hỏi mời kể hoặc chọn, bám nội dung video, không chia phe chính trị.

## Cổng máy
```
python -I tools/loc-chinh-sach/quet.py --tieu-de tap/<tập>/Final/shorts/EPxxx-Snn-<slug>/EPxxx-Snn-seo.md
python -I tools/loc-chinh-sach/quet.py --vi-tri metadata <cùng tệp>
python -I -X utf8 tools/lichsu/kiem-da-chot.py <cùng tệp>
```
Cũng quét lời Shorts nếu có câu sửa. 0 CHẶN, 0 chỗ phạm mới trình user.

## Quy tắc chung
- Chữ sạch, chép dùng luôn; không ghi chú nháp trong khung mã.
- Không clickbait; câu hỏi tiêu đề được video trả lời.
- Nội dung tổng hợp: Shorts dùng lại hình và giọng phim dài, nên khai giống phim dài (xem `goha-ls-dang`).
