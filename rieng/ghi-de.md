# Ghi đè của người dùng (kit không ghi vào tệp này)

Không nới được: luật cứng nội dung, luật giữ khoá API, bước tốn tiền phải hỏi trước, quyền tư liệu và chính sách YouTube, các cổng DỪNG chờ duyệt.

## Công cụ riêng
- P4 so lời tiếng Nhật: dùng `rieng/tools/so-loi-ja.py <loi-chuan.txt> <stt.txt> [--min 0.97]` thay `kit.py so-loi` (kit tách từ theo dấu cách nên hỏng với tiếng Nhật). Công cụ so từng ký tự sau chuẩn hoá (katakana→hiragana, số kanji→số Ả Rập). STT hay nghe nhầm đồng âm hiếm nên chỗ lệch ngắn vẫn cần NGHE lại; chỗ lệch dài (≥ 150 ký tự) là câu bị thiếu trong giọng.

## Chuẩn hình (chốt 11/11/2026, theo tập Peleliu)
- Phân cảnh và dựng phải nhiều ảnh/phim tư liệu khác nhau, clip AI có nhãn «AI生成», chuyển cảnh liên tục. Không để chuỗi thẻ/bản đồ liền không hình thật quá 5 cảnh.
- Một ảnh/clip dùng tối đa 3 lần, hai lần cách ≥ 60 s (kể cả nền thẻ).
- Nhạc và SFX AI qua ai33 được chấp nhận; vẫn ghi rủi ro quyền thương mại vào sổ nguồn âm.

## Quyết định của chủ kênh 11/11/2026 (tối)
- Hình cần thiết đều có thể dùng AI (ảnh, clip, nền thẻ). Vẫn giữ: mọi hình AI ghi nhãn «AI生成» và khai «altered or synthetic content» khi đăng; nhân vật có thật định danh (東郷, Rozhestvensky, các đô đốc, sĩ quan có tên) chỉ dùng ảnh tư liệu thật vì luật nội dung và chính sách YouTube không nới được bằng tệp này.
- Không chèn tên kênh, logo, dấu kênh vào video: bỏ bước `dau-kenh` ở P5 (`ghep-hinh.py` không phủ dấu kênh).
- Nhạc và SFX AI qua ai33 được chấp nhận; ghi rủi ro quyền thương mại Suno vào sổ nguồn âm.
- Nguồn chính thống: xem `ho-so-kenh/luat-noi-dung.md` mục 7 (gồm Wikipedia).

## Quét chính sách tiếng Nhật (làm 12/11/2026)
- `quet.py` của kit chỉ có từ điển Việt/Anh, mù tiếng Nhật. Mọi cổng «quét chính sách» cho kênh JP (P2 trước khi đọc giọng, P7 tiêu đề, mô tả, thẻ, chữ bìa) chạy `python -I -X utf8 rieng/tools/quet-ja.py <tệp>` (thêm `--tieu-de` cho tiêu đề, mô tả, thẻ) thay `quet.py`. Bảng từ: `rieng/tools/tu-cam-ja.tsv` (18 mẫu, cùng định dạng kit; sửa thoải mái). Thử đột biến: `python -I -X utf8 rieng/tools/test-quet-ja.py` (20 ca, phải 20/20).

## Máy kiểm nhịp hình (làm 13/11/2026)
- Cuối P3 (trước khi trình duyệt phân cảnh) và trước khi render bản dài P5: chạy `python -I -X utf8 rieng/tools/kiem-nhip-hinh.py tap/<EPxxx-slug>`; trước render bản dài thêm `--hinh <output>/hinh/p5 --sheet <output>/hinh/_nhip-hinh/sheet` (so lặp hình bằng dHash khung giữa, xuất 1 contact sheet mỗi chương để soi bằng mắt). Mã 1 = có lỗi CHẶN: sửa phân cảnh rồi chạy lại, hoặc báo user lỗi nào chấp nhận và vì sao.
- Luật (ngưỡng ở `rieng/tools/nguong-nhip-hinh.toml`): clip ≤ 2 lần, cách ≥ 180 s; ảnh ≤ 3 lần, cách ≥ 60 s; thẻ chữ/đồ thị đúng 1 lần; cặp [bản đồ 3D + góc máy] ≤ 3 lần cả tập, một bản đồ ≤ max(3, 1,5 × số phút của chương) cảnh/chương, ≥ 0,5 bản đồ/bối cảnh 3D khác nhau mỗi phút (nới 13/11 cho tập 20–30 phút); khoảng không có hình thật ≤ 15 s; hình thật 35–60 % số cảnh; hai cảnh hình thật liền nhau khác cỡ; ≥ 3,5 ảnh + clip khác nhau mỗi phút; ≥ 12 cảnh/phút; lặp hình ≤ 30 %. Luật clip siết hơn mục «Chuẩn hình» ở trên (thay dòng «tối đa 3 lần, cách ≥ 60 s» cho clip).
- Nhãn góc (`goc`) của cảnh bản đồ phải là góc máy THẬT lúc dựng: từ EP003 máy dựng bản đồ 3D phải đổi đường máy theo nhãn (trên xuống, chéo, thấp sát biển, ngang theo hàng tàu…), và P3 lên kế hoạch ≥ 0,5 bối cảnh 3D/phút (thêm bối cảnh như máy bám sau hàng tàu, thước khoảng cách, so tốc độ, mặt cắt tàu, tấm tư liệu).
- Áp đầy đủ từ EP003. EP002: đã sửa phần dễ (clip, khoảng hình thật, cùng cỡ); lỗi bản đồ 3D user chọn để nguyên (13/11). Báo cáo ở `tap/EP002-kokai-kaisen-1904/ke-hoach/kiem-nhip-hinh.md`, chỉ sửa khi user chọn.
- Thử đột biến: `python -I -X utf8 rieng/tools/test-kiem-nhip-hinh.py` (14 ca, phải 14/14).
