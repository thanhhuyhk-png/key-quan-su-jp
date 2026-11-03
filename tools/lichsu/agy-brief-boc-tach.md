# Việc: bóc tách hình ảnh và nguồn tư liệu của một video tài liệu lịch sử (kênh CLD Media)

Bạn đang ở trong thư mục phân tích của MỘT video. Trong thư mục có:
- `credits/credit_NNN.jpg`: mỗi dòng = nhãn vàng "SHOT n  giây" + dải mép dưới khung hình (độ phân giải gốc).
  Dải này thường có chú thích dạng "<nội dung>, <ngày> · Nguồn: <mã lưu trữ>".
- `sheets/sheet_NNN.jpg`: tờ liên khung. Mỗi khối = một shot, nhãn vàng "SHOT n  bắt đầu-kết thúc  cat|mem  dur  motion".
  Các ô là khung lấy mỗi 2 giây của shot (mốc giờ góc dưới trái ô).
- `shots.csv`: mốc từng shot, `vao` (cat = cắt cứng, mem = chuyển mềm), `motion` (~0 = hình đứng yên), `loi` = lời đọc trùng shot.

Chỉ ghi điều THẤY trong ảnh. Không đọc được thì ghi `?`. Không bịa chữ, không bịa mã nguồn.
Làm lần lượt, ghi file ngay sau mỗi tờ (không giữ hết trong đầu rồi mới ghi).

## Đầu ra 1: `agy-nguon.csv` (từ `credits/`)
Cột: `shot,chu_thich,ma_nguon,kho_nguon`
- `chu_thich`: chép NGUYÊN VĂN cả dòng chú thích (tiếng Việt có dấu). Shot không có chú thích → để trống.
- `ma_nguon`: phần sau "Nguồn:" hoặc "Ảnh:" (vd `NARA WHPO-D0973-08A`).
- `kho_nguon` (chọn một): NARA | Thu-vien-Tong-thong-My | DVIDS | Bo-Quoc-phong-My | TTXVN | Bao-VN | Wikimedia-CC | Ban-do-code | Khac | ?
Dùng dấu ngoặc kép cho ô có dấu phẩy.

## Đầu ra 2: `agy-shots.jsonl` (từ `sheets/`)
Mỗi dòng một CẢNH. Nếu một shot chứa nhiều cảnh nối mềm (bay bản đồ, hoà hình) thì tách cảnh con `"shot":"5.2"`.
```json
{"shot":"5.2","t":"00:52-01:05","loai":"...","chuyen_dong":"...","lop_phu":["..."],"chu_lon":"...","chuc_nang":"...","cach_dung_lai":"..."}
```
- `loai`: ban-do-chinh-tri-phang | ban-do-ve-tinh | ban-do-dia-hinh-3d | ban-do-quan-su-cu (bản đồ giấy AMS) | route-mui-ten | the-motion-giay (lịch, dòng thời gian, số liệu) | phim-tu-lieu | anh-tu-lieu-tinh | chan-dung | tai-lieu-van-ban (báo, điện văn, băng ghi âm) | minh-hoa-AI | the-tieu-de-chuong | credit | khac
- `chuyen_dong`: tinh | zoom-in-cham | zoom-out | pan | bay-ban-do | parallax-2.5D | video-goc | chu-hien-dan | ve-duong | to-vung | khac
- `lop_phu` (nhiều): chu-thich-nguon | logo | nhan-dia-danh | nhan-ngay-thang | mui-ten | vung-to-mau | co | chan-dung-tron | lower-third | song-am (waveform băng ghi âm) | hat-film | vignette | khac
- `chu_lon`: chữ to trên màn (tiêu đề thẻ, số liệu), tối đa 12 từ.
- `chuc_nang`: hook | boi-canh | dien-bien | so-lieu | nhan-vat | trich-dan | chuyen-chuong | ket | credit
- `cach_dung_lai`: một câu (code HTML/SVG/bản đồ, tư liệu thật, hay ảnh AI).

## Đầu ra 3: `agy-tong-hop.md` (tiếng Việt, ≤ 800 từ)
1. Hệ thống hình: bảng màu ước mã hex (bản đồ, thẻ giấy, chữ, điểm nhấn đỏ), kiểu chữ, grade tư liệu, lớp phủ lặp lại.
2. Các khối dựng lặp lại: tên, số lần, độ dài thường gặp, 2–3 số shot ví dụ, chuyển động đặc trưng.
3. Cách mở đầu (60 giây đầu), cách vào chương, cách kết.
4. Tỉ lệ % thời lượng theo `loai`; tỉ lệ % theo `kho_nguon`.

Không đọc hay ghi file ngoài thư mục này. Xong in một dòng: `XONG <số cảnh> <số dòng nguồn>`.
