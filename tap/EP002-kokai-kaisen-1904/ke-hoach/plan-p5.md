# Plan P5 Dựng · EP002 黄海海戦 1904 (13/11/2026, CHỜ DUYỆT)

Đầu vào đã duyệt: `san-xuat/phan-canh.md` (315 cảnh, 23:07, mốc thật), `moc-cau.json`, `giong/giong-v2.wav` (−18,0 LUFS), `so-tai-san.md` (66 ảnh + 18 clip AI dùng lại + code). Ra: `E:/Goha-JP/output/261113-kokai-kaisen-1904/` (hinh, am, preview), video cuối sang `E:/Goha-JP/final/EP002-kokai-kaisen-1904/` ở P6.

## Cách làm
- **Chép máy dựng của EP001 JP rồi chỉnh theo EP002, không viết lại** (kit dặn): `dung-p5.py` (ảnh Ken Burns, clip, thẻ, lớp chữ bằng PIL/ffmpeg), `dung-3d.py` + `ban-do-3d/` (three.js + mô hình tàu Meshy có sẵn), `the-dong/` + `dung-the-dong.py` (thẻ số động), `ghep-p5.py` (ghép, kiểm số khung), `am-p5.py` (nhạc theo chương + tiếng động), `intro.py` (trailer), `loc-tu-lieu-cu.py`. Hai tập cùng một bộ máy, chỉ khác bảng dữ liệu.
- Màu và font theo `ho-so.md` mục 4 (nền `#111111`, nhấn `#cc2222`, chữ `#f0e8d8`, NotoSerifJP). Quân Nga xám, quân Nhật đỏ (quy ước thẻ và bản đồ của EP001).
- Không tên kênh, logo, dấu kênh trong video (ghi đè 11/11). Clip AI có nhãn nhỏ «イラスト» góc dưới trái (đã chốt 13/11).
- Mốc chữ, mốc hiện thẻ neo theo `moc-cau.json`. Một cảnh = một tệp đúng số khung 24 fps; kiểm tổng khung.
- **Bản đồ (119 cảnh, 9 loại):** 3D như EP001 (three.js, đất Natural Earth cắt khung 黄海/旅順/山東半島, tàu Meshy, HUD đỏ). Loại `churitsu` (3 cảng trung lập tới サイゴン) vẽ trên bản đồ thế giới có Hoàng Sa, Trường Sa (Việt Nam) và «Biển Đông», không đường lưỡi bò; soi từng khung (luật cứng, EP001 từng sót ở P6).
- Soi sao, cờ, huy hiệu trên MỌI clip AI bằng khung phóng to trước khi dùng (EP001: V07, V08, V13 có sao trắng).
- Ảnh hạng A? (ヴィトゲフト, 東郷 1904, ノヴィーク): đối chiếu bản gốc khi dựng; chưa rõ thì thay bằng thẻ chữ. Bốn ảnh Commons mới chỉ có bản 500 px: tải lại bản gốc khi Wikimedia hết giới hạn.

## Thứ tự (mỗi lô: `--stills` soi → sửa → `--render` → kiểm khung; DỪNG cho bạn xem sau Lô 0)
1. **Trailer 10 s** (tuỳ chọn, xem điểm quyết 3).
2. **Lô 0 · 開幕 (S001–S024, 63 s)**: ảnh, clip, bản đồ, thẻ, lớp chữ, âm nháp. Bạn gật → thành sàn chất lượng cả phim.
3. Lô 1 ảnh và clip (107 ảnh + 45 clip) → Lô 2 bản đồ 3D (119) → Lô 3 thẻ số động (44) → ghép cả phim → âm → master.
4. Cổng cuối: `kit.py kiem --lufs -14`, so lời `so-loi-ja.py` trên bản trộn, soi khung mọi bản đồ, `quet-ja.py` cho chữ trên hình.

## Bước tốn tiền (chờ bạn duyệt con số; số dư ai33, Flow đọc lại trước khi chạy)
| Việc | Đề xuất | Chi phí |
|---|---|---|
| Nhạc Suno qua ai33 (3.600 credit mỗi lần, 2 bản) | Dùng lại 6 bản EP001 cho Mở, 第1–4章, 結; **mua 2 lần mới** cho 第5章 (cao trào) và 第6–7章 (hoàng hôn) để hai tập không trùng nhạc ở chỗ cảm xúc nhất | **7.200** |
| Tiếng động ElevenLabs SFX qua ai33 (60 credit/giây) | Dùng lại kho 22 tiếng EP001; làm thêm khoảng 8 tiếng riêng (pháo tầm xa, nước vỡ khi tàu quay gấp, hiệu lệnh cờ, đèn pha, v.v.), ≈ 35 giây | **≈ 2.100** |
| Clip AI mới qua Flow (Veo 3.1 Lite, 8 s, 10 credit/clip) | 10 clip riêng cho EP002 (hoàng hôn trên biển, đội hình hàng dọc, khu trục ban đêm, đèn pha…), giảm việc dùng lại clip EP001 | **≈ 100** |
| Giọng, STT | đã xong | 0 |
| **Tổng dự kiến** | | **≈ 9.400 credit** (EP001 tốn ≈ 20.000 cho nhạc + SFX) |
Rủi ro quyền thương mại nhạc Suno và SFX qua ai33 vẫn ghi vào sổ nguồn âm (bạn đã chấp nhận).

## Điểm cần bạn quyết
1. Duyệt cách làm (chép máy EP001, màu theo kênh, không dấu kênh, nhãn «イラスト» nhỏ).
2. Chi phí: ≈ 9.400 credit như bảng, hay phương án 0 credit (chỉ dùng lại nhạc, SFX và clip của EP001)?
3. **Trailer 10 s đầu phim:** làm mới cho EP002 (miễn phí, khuôn «trailer cinema cắt nhanh» đã chốt 11/11), hay bỏ vì 開幕 đã cắt nhanh 22,9 cảnh/phút?
