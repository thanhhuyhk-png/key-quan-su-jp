---
name: goha-ls-chon-de-tai
description: P0 Chọn đề tài của quy trình làm phim tài liệu lịch sử, quân sự (kit Goha Lịch Sử) — chọn đề tài cho tập mới từ sheet top 20 của chính kênh người dùng, chấm điểm (nhu cầu, cạnh tranh, tư liệu sẵn có, rủi ro chính sách), kiểm trùng bằng máy với sổ chủ đề cấm của chủ kit và sổ đăng ký đề tài chung, rồi ghi brief tập. Dùng ngay khi người dùng nói "P0", "chọn đề tài", "tập mới", "làm tập gì tiếp", "tập tiếp theo", "kiểm trùng đề tài", "đăng ký đề tài", hoặc khi đã có `ho-so-kenh/` mà chưa có tập nào hay tập trước đã xong — kể cả khi không nhắc tên skill. Không dùng để tra sổ số liệu (goha-ls-nghien-cuu) hay viết kịch bản (goha-ls-kich-ban).
---

# P0 Chọn đề tài

Đường dẫn dạng `<output>` là khoá trong `cau-hinh.toml` ở gốc repo; đường dẫn khác tính từ gốc repo.

Đầu ra: `tap/EPxxx-<slug>/ke-hoach/brief.md` và `progress.md` (mẫu cả hai trong `references/brief.md`), một đề tài đã qua máy kiểm trùng và đã được người dùng duyệt. Kết thúc bằng **DỪNG, người dùng duyệt đề tài**, rồi chuyển P1 `goha-ls-nghien-cuu`.

Vì sao có bước này: nhiều kênh làm cùng một đề tài với cùng giọng, cùng khung hình thì YouTube dễ xếp vào «nội dung dùng lại» và cả kênh có thể mất kiếm tiền. Quy trình được chép, đề tài thì không. Bước này chặn trùng bằng máy chứ không bằng lời dặn.

## Công cụ (đã có trong repo)
| Lệnh | Việc |
|---|---|
| `python -I -X utf8 tools/lichsu/kiem-de-tai.py "<đề tài>" --goc "<góc kể>" --ngon-ngu <vi/en/…> [--so-chung <csv/tsv>]` | So với `kit/so-chu-de-cam.tsv` (đề tài chủ kit đã làm, đã lên lịch) và sổ đăng ký chung. In CHẶN / CẢNH BÁO / ĐẠT kèm dòng khớp. Mã thoát: 0 = ĐẠT hoặc CẢNH BÁO, 1 = CHẶN, 2 = lỗi đầu vào (tệp thiếu, sai mã hoá, sổ thiếu cột `de_tai`; không phải CHẶN). Luôn in số dòng đã so ở mỗi sổ. |
| `python -I tools/loc-chinh-sach/quet.py --tieu-de <tệp>` | Quét tiêu đề dự kiến của đề tài (rủi ro chính sách). |
| `python -I -X utf8 tools/loc-chinh-sach/trung-lap.py <lời.txt> <thư mục hoặc tệp mẫu>` | Dùng ở P2, không dùng ở P0. Nguồn so là tệp hoặc thư mục bất kỳ, nên so được với tập mẫu: `tap/EP001-dien-bien-phu-1954/ke-hoach/` hoặc thư mục `mau/` của kit. Ngưỡng trùng trên 1 % cụm 6 tiếng thì CHẶN. |

## Các bước
1. **Đọc `ho-so-kenh/ho-so.md`**: ngách, ngôn ngữ, khán giả, độ dài tập, link sheet top 20. Thiếu tệp thì dừng, chạy K2 (`goha-ho-so-kenh`) trước. Đọc `ho-so-kenh/luat-noi-dung.md` để biết đề tài nào bị loại từ đầu.
2. **Tập hợp ứng viên** từ sheet top 20 của kênh: tab kho video vượt trội và tab nhân bản đề tài. Lấy 8–12 đề tài; không có sheet thì nói rõ và hỏi người dùng gợi ý, không tự bịa số đo. Bỏ đề tài đã có thư mục trong `tap/`.
3. **Chấm điểm từng ứng viên** (0–5 mỗi cột, ghi bằng chứng ngắn):
   - Nhu cầu: view vượt trội của video cùng đề tài trong sheet.
   - Cạnh tranh: số kênh đã làm kỹ, chất lượng bản hiện có (còn chỗ cho góc mới không).
   - Tư liệu sẵn có: ảnh, phim, văn kiện hạng A/B; có bản đồ, đồ hoạ code thay được không (tra nhanh, chưa làm P1).
   - Rủi ro chính sách: ghi tiêu đề dự kiến ra tệp tạm, chạy `quet.py --tieu-de`; CHẶN thì trừ hết điểm cột này và ghi lý do.
4. **Kiểm trùng** top 3–5 ứng viên bằng `kiem-de-tai.py` (kèm `--goc` và `--ngon-ngu`; nếu người dùng có tệp xuất từ sổ đăng ký chung thì thêm `--so-chung`). Xử lý:
   - **CHẶN**: loại đề tài, hoặc đề xuất góc kể khác (ví dụ đổi cấu trúc kể, nhân vật dẫn, vật chứng) rồi kiểm lại. Không tìm cách lách từ khoá.
   - **CẢNH BÁO**: cùng đề tài khác góc; ghi rõ vào bảng, người dùng quyết.
   - **ĐẠT**: đi tiếp.
5. **Trình bảng** (đề tài, góc kể đề xuất, điểm, kết quả kiểm trùng) và đề xuất 1 lựa chọn kèm lý do. **DỪNG chờ người dùng duyệt.** Không tự chốt thay.
6. **Ghi brief**: số tập kế tiếp là số lớn nhất trong `tap/EP*` cộng 1 (ba chữ số, ví dụ `EP002`); `slug` là tên không dấu nối bằng gạch ngang kèm năm. Tạo `tap/EPxxx-<slug>/ke-hoach/brief.md` theo `references/brief.md`, và cùng lúc tạo `tap/EPxxx-<slug>/ke-hoach/progress.md` theo mẫu ở cuối `references/brief.md` (bảng P0–P8, ngày, cổng đã duyệt). Bộ định tuyến của `CLAUDE.md` đọc đúng tệp này (`tap/<EPxxx-slug>/ke-hoach/progress.md`) để biết tập dở đang ở phase nào, nên thiếu nó thì tập không được nhận ra khi mở lại repo. Ví dụ tên: `EP001-<slug>` cho tập đầu của kênh. Dòng P0 ghi ngày người dùng duyệt đề tài.
7. **Nhắc đăng ký** đề tài (đề tài, góc kể, ngôn ngữ, tên hội viên, ngày) vào sổ đăng ký chung để người sau bị chặn đúng; người dùng tự điền, Claude không ghi hộ vào sổ của người khác.
8. **Chuyển P1** `goha-ls-nghien-cuu` với brief vừa ghi.

## Lưu ý
- Đề tài mới của người dùng nhưng nằm ngoài sheet vẫn phải qua bước 3 và 4.
- Hai tập liền nhau của cùng kênh không nên dùng cùng cấu trúc kể.
- Mọi bản đồ có Việt Nam áp luật cứng trong `CLAUDE.md` của kit, bất kể ngách.
- Không đổi nội dung `kit/so-chu-de-cam.tsv`: đó là sổ của chủ kit. Trong sổ, từ khoá riêng (vd «Him Lam») chặn bất kể năm; từ khoá có dấu `~` đứng trước (vd `~củ chi`) là từ chung, chỉ chặn khi cùng năm.
