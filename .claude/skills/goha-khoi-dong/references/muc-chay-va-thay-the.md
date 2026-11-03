# Mức chạy và phương án thay thế

Đọc khi chạy bước 6, 7 của K1.

## Ba mức chạy

| Mức | Dành cho | Chi phí tháng (ước) |
|---|---|---|
| Đầy đủ | Muốn chất lượng cao nhất của quy trình | Gói ElevenLabs Creator trở lên, Claude Max, tuỳ chọn Suno, vidIQ |
| Tiết kiệm | Có Claude, ít ngân sách dịch vụ | VieNeu hoặc ElevenLabs gói thấp, nhạc miễn phí |
| Miễn phí | Chỉ có Claude Code | Mọi thứ còn lại là phần mềm miễn phí |

Mức giá cụ thể tra lúc chạy, ghi kèm ngày tra; không ghi cứng vào kit.

Quy tắc gợi ý của `kiem-may.py` (chỉ là điểm xuất phát): thiếu thứ bắt buộc thì chưa chọn mức; có khoá ElevenLabs thì Đầy đủ; không có ElevenLabs nhưng có Deepgram thì Tiết kiệm; không khoá nào thì Miễn phí. RAM dưới 16 GB thì thêm lưu ý bật chế độ nhẹ. Người dùng được chọn mức khác với gợi ý, ví dụ có khoá vẫn chọn Tiết kiệm để giảm chi.

## Phương án thay thế khi thiếu

| Thiếu | Thay bằng | Đánh đổi |
|---|---|---|
| Hình minh hoạ (ngách ngoài sử Việt) | Goha Flow (hội viên có sẵn), chỉ cho hình không có người thật | Luật kênh sử Việt vẫn cấm ảnh AI |
| ElevenLabs giọng tiếng Việt | VieNeu V4 (tính token, rẻ), hoặc VieNeu V3 chạy trên máy (miễn phí) | Giọng kém tự nhiên hơn; phải đo đuôi câu bằng `tools/vieneu-ab`. Cách cài và gọi: `goha-ho-so-kenh/references/giong.md` mục «Giọng thay thế» (chưa thử đầu cuối trên kit) |
| ElevenLabs giọng tiếng Anh | Kokoro chạy trên máy (mã nguồn mở) | Ít cảm xúc hơn. Cách cài và gọi: cùng mục trên |
| ElevenLabs tiếng động (SFX) | YouTube Audio Library, Pixabay, Freesound CC0 | Ghi nguồn vào `kit/ASSETS.tsv` |
| Suno (nhạc) | YouTube Audio Library, Pixabay Music (cho phép kiếm tiền) | Ít bài hợp cao trào hơn |
| Chép lời ElevenLabs, Deepgram | `kit.py chep-loi --adapter whisper` (cài `python -m pip install faster-whisper`, lần đầu tự tải model) | Chậm trên CPU; nghe nhầm nhiều hơn, chỗ lệch phải nghe tai |
| VST FabFilter, Valhalla | Chuỗi ffmpeg (equalizer, acompressor, alimiter, aecho), hoặc plugin miễn phí TDR Nova, Valhalla Supermassive, LoudMax | Hậu kỳ kém tinh hơn một chút |
| vidIQ | Chỉ yt-dlp (kể cả số sub, `tu-duy-top-20-ytb/references/nguon-du-lieu.md`); không cần khoá API | Không có điểm từ khoá; dễ bị YouTube chặn nếu gọi dồn |
| Agy, Codex, Grok | Sub-agent Opus của Claude, ngữ cảnh mới, làm người phản biện | Cùng hãng nên ít góc nhìn khác hơn |
| AK kit | Công cụ gốc của Claude Code | Mất vài lệnh tiện |
| teardown kit | Bỏ cảnh cắt dọc cơ cấu | Mất một loại cảnh |
| Máy yếu (RAM 8 GB) | Chế độ nhẹ: 720p, ít cảnh 3D, tăng tư liệu và thẻ chữ | Hình kém hoành tráng |

Trộn âm, hậu kỳ, xem lại dùng **Goha AVS** (bắt buộc ở mức Đầy đủ; mức khác có thể thay bằng `kit.py tron`, `kit.py master`); gọi giọng, chép lời, đo độ to dùng `tools/kit/` (ffmpeg cho ebur128 và freezedetect). Không có đường nào đi qua CLI `reelcrew`.

## Ghi vào hồ sơ

Mức đã chốt (dòng «Mức chạy») và danh sách «thiếu gì, thay bằng gì» ghi trong `kiem-may.md` ở K1; K2 chép sang `ho-so-kenh/ho-so.md` (mục «Mức chạy» và «Công cụ thay thế đang dùng»). Các skill P1 đến P8 đọc hồ sơ này để chọn nhánh: có khoá thì đi nhánh Đầy đủ, không có thì đi nhánh thay thế đã ghi.
