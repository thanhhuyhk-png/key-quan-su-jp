---
name: goha-ls-phan-canh
description: P3 Phân cảnh của quy trình sản xuất phim tài liệu lịch sử, quân sự (kit Goha Lịch Sử) — chia lời đọc đã chốt thành cảnh neo vào câu/chữ, gán cho mỗi cảnh một nguồn hình (ảnh tư liệu, phim tư liệu hạng B, cảnh 3D của bản mẫu hoặc mới, bản đồ map3d/vnmap, thẻ chữ số), chữ trên hình có nguồn, âm; rồi chạy máy kiểm luật cứng (nguồn mọi cảnh, trần 5 s hạng B và A?, lãnh tụ, Hoàng Sa Trường Sa, cỡ góc không lặp, mật độ, đặc tả) và sinh danh sách tài sản cần dựng. Dùng ngay khi user nói "P3", "phân cảnh", "storyboard tập", "gán tư liệu", "danh sách tài sản cần dựng", hoặc khi tập đã có `loi-doc-v*.txt` chốt mà chưa có `san-xuat/phan-canh.md` — kể cả khi không nhắc tên skill. Không dùng để viết lời (goha-ls-kich-ban) hay dựng hình (goha-ls-dung).
---

# P3 Phân cảnh (Goha Lịch Sử)

Danh tính kênh, giọng, độ dài tập, mức chạy đọc từ `ho-so-kenh/ho-so.md`; luật nhạy cảm riêng của ngách từ `ho-so-kenh/luat-noi-dung.md`. Ví dụ mang nhãn «tập mẫu EP001» (Điện Biên Phủ 1954) chỉ để minh hoạ số đo.

Đầu ra trong `tap/<slug>/san-xuat/`: `phan-canh.md` (bảng = nguồn sự thật), `anh.tsv` (ảnh: hạng, ghi nguồn), `kiem-phan-canh.py` (máy kiểm), và do máy sinh: `phan-canh.json` (cho P5), `tai-san-can-dung.md`, mục Tóm tắt. Không tốn tiền. Mẫu đã chạy: tập mẫu EP001 (`mau/` hoặc `tap/EP001-dien-bien-phu-1954/san-xuat/`, 248 cảnh, 01/11/2026, 15 phút làm bảng + 10 phút máy kiểm).

Đọc trước: `CLAUDE.md` (luật cứng), `template/chuan-dao-dien.md`, `template/README.md` (tham số các khối), kịch bản chốt (dòng `Hình:`, `Chữ trên hình:` của từng khối là ý đồ của biên kịch), `ke-hoach/so-tai-san.md`, phân cảnh của tập mẫu (nếu kit có `mau/`): cảnh 3D đã dựng, tái dùng bằng `3d:<mã>`.

## Vì sao làm theo neo chứ không theo khung
Chuẩn đạo diễn: mốc chữ trước, hình sau. Ở P3 chưa có giọng, nên mỗi cảnh neo vào **câu `N`**, **chữ `N:k`** (k đếm từ 0) hoặc **tên khoảng lặng**; giây chỉ là ước tính theo tốc độ giọng đã đo ở P2 (tập mẫu EP001: 242 tiếng/phút). Sau P4, ghi `moc-cau.json` (mốc chữ thật từ STT) rồi chạy lại máy kiểm: mọi trần thời lượng được đo lại, không phải viết lại bảng.

## Các bước
1. Ghi giờ bắt đầu vào `ke-hoach/progress.md`.
2. Đánh số câu: `python -I -c` in `số câu · số tiếng · giây ước · 6 chữ đầu` của `loi-doc`. Dòng trống trong lời là khoảng lặng P1, P2…
3. Lập `anh.tsv` từ sổ tài sản (CSV nhóm C và bản mẫu): chỉ ảnh định dùng, cột `hang` (A, A?, B), `ghi_nguon` ngắn đúng chữ sẽ in góc phải dưới. Ảnh lãnh tụ chỉ đưa bản đã thấy gốc (A), chỉ cắt khung vuông vắn rồi đóng khung trang trọng; không tách nền, không sửa mặt, không chế ảnh.
4. Viết bảng: mỗi cảnh một dòng `| # | Neo | Nguồn hình | Cỡ / góc | Hình | Chữ trên hình | Âm |`. Cảnh thường bằng một câu; câu dài (> 5 s) hoặc câu có hai ý thì tách bằng `N:k`. Thêm **khoảng lặng có tên** khi cần tiếng lớn hoặc ảnh không lời (tập mẫu EP001: `A1` 2,5 s cho nổ bộc phá, `GN` 3 s cho Giơ-ne-vơ, `KT` 6 s cho thẻ câu hỏi cuối); khi đặt giọng ở P4 tách tại ranh câu đó. Câu có lời người khác dựng lại bằng giọng (sĩ quan nước ngoài, chiến sĩ, nhân chứng, nhà thơ…) phải có cảnh ghi chữ trên hình «mô phỏng lại». Máy kiểm chưa có luật này: soát tay từng câu trích trước bước 5.
5. **Chép máy kiểm của tập mẫu trước lần chạy đầu của tập:** `kiem-phan-canh.py` không có sẵn trong tập mới. Chép nó từ `san-xuat/` của tập mẫu nằm ở `mau/dien-bien-phu-1954/` (ở repo của chủ kit là `tap/EP001-dien-bien-phu-1954/`) sang `tap/<EPxxx-slug>/san-xuat/`, mở đầu tệp và sửa bảng dữ liệu theo tập mới (đường dẫn, mã cảnh, hạng ảnh), không sửa logic trừ khi có lý do. Rồi `python -I kiem-phan-canh.py` → sửa đến ĐẠT. Sửa trong bảng, không sửa JSON.
6. Thử đột biến (cài lỗi vào bản sao rồi `--md <bản sao>`; chế độ này không ghi đè đầu ra): tập mẫu EP001 bắt 6/6 (lãnh tụ 3D, vnmap thiếu Hoàng Sa, ảnh cấm, Karmen > 5 s, số không nguồn, lời lãnh tụ trùng lời đọc).
7. Ghi `checks.md` mục P3, giờ xong, commit `feat: phan canh ...`.

## Luật máy kiểm (đổi theo tập ở đầu file: `LOI`, `CHUONG`, `CAM`, `SAN_KHAU`)
- Neo tăng dần, phủ đủ mọi câu; mỗi khoảng lặng có cảnh riêng.
- Nguồn hình thuộc `anh, karmen, 3d, 3d-moi, map3d, vnmap, the, can-tim`; `can-tim` phải ghi phương án thay ("chưa có … thì …").
- Ảnh cấm (`CAM`): ảnh C, ảnh màu nghi tô màu, ảnh lãnh tụ A?, ảnh logo đè giữa. Ảnh phải có trong `anh.tsv`.
- Chữ có số phải có "Nguồn:" thuộc danh sách chính thống (Báo Nhân Dân, Báo QĐND, TTXVN, Báo Chính phủ, Tư liệu văn kiện Đảng, VTV, Báo Văn hóa). Nhãn năm của ảnh và tiêu đề phim được miễn.
- Hạng B và A? ≤ 5 s mỗi cảnh.
- Lãnh tụ: lời nhắc Hồ Chí Minh, Võ Nguyên Giáp, "Đại tướng" thì cảnh không 3D; ảnh lãnh tụ ghi `lanhTu`; lời lãnh tụ chỉ ở thẻ trong khoảng lặng.
- Bản đồ (áp cho **mọi** bản đồ có Việt Nam, kể cả kênh ngách khác): `vnmap` phải ghi "Hoàng Sa" (khung rộng, có Trường Sa, ghi «Biển Đông», không đường lưỡi bò) hoặc "không chạm biển" (khung Tây Bắc, dừng ≤ 105,5° Đông); hình nhắc Hà Nội, đồng bằng, biển, vịnh mà không phải vnmap thì trượt. Không cờ chính quyền Sài Gòn.
- Không 3D lá cờ; không 3D pháo 105 của ta cho loạt mở màn 13/3 (riêng tập mẫu EP001, đổi `CAM`/`SAN_KHAU` theo tập).
- Hai cảnh liền nhau không cùng cỡ và góc khi một bên là cảnh quay (3D, phim, ảnh). Thẻ, bản đồ liền nhau được phép.
- Mỗi chương ≥ 9 cảnh/phút và ≥ 1 cận đặc tả; cả tập 10–20 cảnh/phút.

## Bài học tập mẫu EP001
- Mật độ thật ra 16,4 cảnh/phút (plan ghi 10–12): Mở và Ch4 hành động 17–18, Kết 14,5. Giữ vì chuẩn đạo diễn cho đoạn hành động 25–35 cú cắt/phút; plan ghi số tối thiểu.
- Ô trống trong bảng markdown: tách cột bằng `[1:-1].split("|")`, không tách theo `" | "`.
- Tên khoảng lặng có thể là chữ + số (`A1`): regex `[A-Z][A-Z0-9]`.
- Tư liệu thật chỉ khoảng 41/248 cảnh (139 s) vì ảnh A? và phim B bị trần 5 s và ít ảnh có giấy phép; phần còn lại là 3D, bản đồ, thẻ. Muốn hình "như QPVN" thì P5 phải nâng chất 3D và bản đồ, không thêm tư liệu chưa rõ quyền.
- Không có ảnh dùng được cho nhân vật nào đó (ví dụ Na-va, Pi-rốt): thẻ tên trên nền 3D hoặc bản đồ, ghi "(không có ảnh)".
- Tách ảnh và thẻ: thẻ không đè lên ảnh lãnh tụ (đặt nền riêng cạnh ảnh); ảnh thường được thẻ góc dưới.

## Nhánh thay thế (mức Tiết kiệm / Miễn phí, máy yếu)
- Không có kho 3D hay máy chạy được cảnh 3D nặng (`ho-so.md` ghi chế độ nhẹ): gán nhiều thẻ chữ, bản đồ, tư liệu hơn; bỏ `3d`, `3d-moi` khỏi nguồn hình; mật độ vẫn giữ 10–20 cảnh/phút và vẫn phải qua máy kiểm.
- Phân cảnh không tốn tiền, không cần dịch vụ nào; mức chạy chỉ đổi khi tới P4, P5.
