---
name: goha-ho-so-kenh
description: K2 dựng hồ sơ kênh riêng cho người dùng sau khi chọn ngách — tạo `ho-so-kenh/ho-so.md` (tên kênh, ngách, ngôn ngữ, khán giả, độ dài tập, giọng, bảng màu, font, logo, Model Link, link sheet top 20, mức chạy), `ho-so-kenh/luat-noi-dung.md` (luật nhạy cảm riêng của ngách, tự nghiên cứu), `kenh/cach-noi-da-chot.tsv` trống, `kenh/` năm tệp khung kênh, lịch nội dung, bìa, mô tả, SEO tạo từ khuôn, và bộ thương hiệu sinh bằng code; ép giọng và màu khác kênh mẫu. Ba cổng DỪNG: duyệt ngách, duyệt Model Link, duyệt thương hiệu (kèm nghe thử giọng, báo chi phí trước). Dùng ngay khi người dùng nói "K2", "hồ sơ kênh", "chọn ngách xong", "tạo thương hiệu", "đặt giọng kênh", "làm logo kênh", hoặc khi chưa có dòng «Trạng thái: đã duyệt» trong `ho-so-kenh/ho-so.md` mà đã có kết quả top 20 — kể cả khi không nhắc tên skill. Không dùng để chọn ngách và đo top 20 (tu-duy-top-20-ytb) hay chọn đề tài từng tập (goha-ls-chon-de-tai).
---

# K2 Hồ sơ kênh

Mọi skill khác của kit đọc danh tính kênh từ `ho-so-kenh/ho-so.md`. Hồ sơ sai thì mọi tập sau sai theo, nên dựng kỹ một lần ở đây. Đường dẫn dạng `<output>`, `<chrome>` là khoá trong `cau-hinh.toml` ở gốc repo; đường dẫn khác tính từ gốc repo.

**Nguyên tắc: chép quy trình, không chép danh tính.** Kênh mẫu của chủ kit (Goha Studio) chỉ để so khác biệt. Hồ sơ của bạn phải có giọng, bảng màu, tên, logo, khung hình khác kênh mẫu, vì nhiều kênh cùng giọng, cùng khung dễ bị YouTube xếp vào nội dung dùng lại và mất kiếm tiền cả kênh. Hồ sơ cũ của kênh mẫu (nếu có trong máy) không phải đầu vào, không đọc để bắt chước.

## Đầu vào
Ngách đề xuất · Model Link (kênh mẫu để bám) · link Google Sheet top 20 đã duyệt từ skill `tu-duy-top-20-ytb` · mức chạy (Đầy đủ, Tiết kiệm, Miễn phí) ở dòng «Mức chạy» của `kiem-may.md` do K1 ghi (bước 6 của K1). Mức chạy chỉ ghi một nơi: sau K2 là mục 1 của `ho-so-kenh/ho-so.md`; K2 chép từ `kiem-may.md` sang đó. Thiếu cái nào thì quay về bước tương ứng, không đoán.

## Các bước
1. **Cổng 1, duyệt ngách.** Tóm 5 dòng: ngách, ngôn ngữ và thị trường, khán giả, độ dài tập đề xuất, vì sao hợp (dẫn số từ sheet). **DỪNG** chờ người dùng gật.
2. **Cổng 2, duyệt Model Link.** Nêu tên kênh, điều học được (cấu trúc, độ dài, nhịp), điều cố ý làm khác. **DỪNG** chờ gật.
3. **Luật nội dung riêng của ngách** → `ho-so-kenh/luat-noi-dung.md`. Tự nghiên cứu: chủ đề nhạy cảm của ngách, cách gọi tên đúng với từng bên, địa danh và bản đồ tranh chấp, nhân vật còn sống hoặc lãnh tụ, chính sách YouTube liên quan. Đọc bình luận các video top của sheet để biết khán giả hay sửa gì. Mẫu và câu hỏi gợi ý: `references/luat-noi-dung.mau.md`. Ngách có Việt Nam thì luật cứng sử Việt trong `CLAUDE.md` của kit vẫn áp cho mọi bản đồ, không chép lại ở đây.
4. **Sổ cách nói**: nếu chưa có thì tạo `kenh/cach-noi-da-chot.tsv` chỉ có dòng tiêu đề (6 cột, phân cách tab): `ma`, `cam`, `dung`, `ly_do`, `nguon`, `pham_vi`. Không tạo thêm dòng nào; dòng được thêm khi người dùng sửa cách nói về sau. Nếu ngách đã có cách gọi bắt buộc từ bước 3 thì ghi ở `luat-noi-dung.md` trước, chỉ đưa vào sổ khi cần máy kiểm.
5. **Bộ lọc chính sách**: dùng chung `kenh/bo-loc-chinh-sach-yt.md` và `tools/loc-chinh-sach/`, không viết bản riêng. Ghi vào hồ sơ đường dẫn hai thứ đó.
6. **Giọng** (chi tiết `references/giong.md`): chọn theo ngôn ngữ ngách và mức chạy, **bắt buộc khác** giọng `3VnrjnYrskPMDsapTr8X` của kênh mẫu. Nghe thử 2–3 giọng; ElevenLabs là bước trả phí, **báo số ký tự và chi phí ước trong chat rồi chờ đồng ý** mới gọi. Ghi `voice_id`, model, thẻ đầu bài, quy tắc sửa câu vào hồ sơ.
7. **Thương hiệu** (chi tiết `references/thuong-hieu.md`): chọn tên kênh, bảng màu, font; sinh logo, ảnh đại diện, banner, dấu kênh bằng máy dựng chung `tools/thuong-hieu/thuong_hieu.py` đọc `kenh/thuong-hieu/thuong-hieu.json` (không chép hay sửa máy dựng của kênh mẫu). Bảng màu **bắt buộc khác** cặp ô-liu `#3a4126` + vàng đồng `#e2b04a`; chạy `scripts/kiem-mau.py` (cách dùng ở tài liệu ấy). Không dùng ảnh AI làm logo.
8. **Cổng 3, duyệt thương hiệu.** Đưa đường dẫn ảnh đại diện (xem ở 98 px và 40 px), banner, logo hai nền, 3 mẫu giọng đã nghe. **DỪNG** chờ gật. Chưa gật thì không ghi hồ sơ thành chính thức.
9. **Ghi `ho-so-kenh/ho-so.md`** theo `references/ho-so.mau.md`, đủ mọi mục, không để dấu `<...>`; chép «Mức chạy» và «Công cụ thay thế đang dùng» từ `kiem-may.md` sang. Ghi tên kênh, mô tả kênh, tagline ra một tệp tạm (mỗi dòng một mục) rồi chạy `python -I tools/loc-chinh-sach/quet.py --tieu-de <tệp tạm>`: 0 CHẶN. Dòng «Trạng thái» ghi tạm «nháp» (đổi ở bước 11).
10. **Tạo năm tệp kênh từ khuôn** (P2, P7, P8 đọc chúng; chưa có thì các skill đó không chạy được). Khuôn trống nằm ở `references/khuon-kenh/`. Chép từng tệp sang `kenh/`, điền bằng dữ liệu đã duyệt ở các cổng và sheet top 20 (mở ảnh bìa, đọc mô tả của video thắng; không chép chữ của kênh nào), thay hết `<...>`:
    - `khung-kenh.md` ← cổng 1 và 2 (ngách, Model Link, hệ từ lấy từ `luat-noi-dung.md`).
    - `lich-noi-dung.md` ← chủ đề kênh, thời lượng, cấu trúc kể S1–S5; bảng tập để trống đến khi P0 chốt tập đầu.
    - `thumbnail-chuan.md` ← mở xem ảnh bìa các video thắng trong sheet, màu và font lấy từ hồ sơ mục 4.
    - `mo-ta-chuan.md` ← đọc 5–10 mô tả của video thắng; nguồn và hashtag theo ngách.
    - `seo-kenh.md` ← từ khoá lấy từ gợi ý tìm kiếm của YouTube và tiêu đề video thắng.
    Sau khi điền, quét từng tệp bằng `python -I tools/loc-chinh-sach/quet.py --tieu-de <tệp>`: 0 CHẶN. **Không tạo `kenh/hoc-shu/so-tay-van-phong.md` ở K2**: sổ tay văn phong là sản phẩm của bước Shu cần tải phụ đề video top, do P2 (`goha-ls-kich-ban`) chạy ở tập đầu; K2 chỉ khẳng định khuôn của nó nằm ở `references/khuon-kenh/so-tay-van-phong.md`.
11. **Đánh dấu xong K2.** Đổi dòng `- Trạng thái:` ngay dưới tiêu đề `ho-so-kenh/ho-so.md` thành `- Trạng thái: đã duyệt (<ngày>)`. Đây là dấu bộ định tuyến của `CLAUDE.md` dùng để biết K2 đã xong (tệp chỉ tồn tại thì chưa đủ). Báo người dùng: hồ sơ xong, bước tiếp là P0 (`goha-ls-chon-de-tai`).
12. **Lưu việc của bạn ở repo riêng.** Hồ sơ kênh và tập phim là của bạn, không phải của kit. Repo kit chỉ đọc nên KHÔNG `git push` vào nó. Lưu bằng `git commit` trong repo riêng của bạn (cách tạo ở `README.md`, mục «Lập repo kênh riêng»); commit `ho-so-kenh/`, `kenh/`, không đưa khoá.

## Kiểm xong
- `ho-so-kenh/ho-so.md` không còn `<...>`, có dòng «Trạng thái: đã duyệt», mọi đường dẫn tệp thương hiệu tồn tại.
- Năm tệp `kenh/khung-kenh.md`, `lich-noi-dung.md`, `thumbnail-chuan.md`, `mo-ta-chuan.md`, `seo-kenh.md` tồn tại và không còn `<...>`.
- `voice_id` khác kênh mẫu; lệnh kiểm màu in "ĐẠT".
- `ho-so-kenh/luat-noi-dung.md` có ít nhất: cách gọi tên các bên, chủ đề nhạy cảm, điều cấm, nguồn đã tra.
- Không có khoá API trong bất kỳ tệp nào; không đọc `.env`.

## Lỗi thường gặp
- Chọn giọng đẹp nhất theo cảm tính rồi trùng giọng kênh mẫu: so `voice_id` bằng chữ, không bằng tai.
- Màu chỉ đổi sắc nhẹ (xanh lá đậm thay ô-liu): vẫn tính là gần, cho chạy lệnh kiểm.
- Bỏ qua luật riêng của ngách vì "đã có luật cứng sử Việt": luật cứng chỉ lo Việt Nam, không lo ngách của bạn.
