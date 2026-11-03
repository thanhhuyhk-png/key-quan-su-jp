# Phụ đề dịch

Chỉ làm khi `ho-so-kenh/ho-so.md` khai ngôn ngữ phụ (tập mẫu có Anh, Pháp vì khán giả xin để chia sẻ cho người thân nước ngoài). Không khai thì bỏ bước này.

## Đầu vào
`Final/EPxxx-<slug>.vi.srt` (sinh từ lời chuẩn đã chốt và mốc câu của P4/P5; tập mẫu: `san-xuat/phu-de.py`). Số khối và mốc thời gian là bất biến.

## Bảng thuật ngữ trước khi dịch
Lập `ke-hoach/thuat-ngu-dich.md`: tên người (kèm chức vụ khi ấy), đơn vị, địa danh, cứ điểm, thuật ngữ quân sự, quy tắc số và ngày. Mọi bản dịch bám bảng này; chưa có bảng thì dịch sẽ lệch tên giữa các khối.

## Dịch (sub-agent Sonnet, mỗi ngôn ngữ một agent)
Brief gồm: đường dẫn `.vi.srt`, bảng thuật ngữ, kịch bản có mã sổ (chỉ để hiểu nghĩa), tệp được ghi (`.<mã ngôn ngữ>.srt` và `dich-<mã>-ghi-chu.md` ghi câu khó), cùng khối luật mục C.
Quy cách:
- UTF-8, xuống dòng như tệp gốc, số khối liên tục, mốc chép nguyên từng ký tự.
- Mỗi khối ≤ 2 dòng, mỗi dòng ≤ khoảng 42 ký tự; tốc độ đọc ≤ khoảng 20 ký tự/giây. Quá dài thì rút ý phụ, giữ ý chính và mọi con số.
- Câu trải qua nhiều khối thì dịch cho từng khối đọc trôi, khớp lời đang đọc.
- Số viết bằng chữ số; ngày giờ theo chuẩn ngôn ngữ đích. Lời trích giữ ngoặc kép và ghi người nói; lời lãnh tụ dịch sát nghĩa, trang trọng.
- Hệ từ của kênh giữ nguyên nghĩa («kháng chiến chống Mỹ, cứu nước» không dịch thành «Vietnam War»; xem `kenh/khung-kenh.md`).

## Soát (agent khác, ngữ cảnh mới)
Đối chiếu từng bản dịch với bản Việt: số khối, mốc, mọi con số, tên riêng theo bảng, hệ từ, xưng hô (nhân vật phía ta giữ chức vụ). Chỉ nhận lỗi có bằng chứng. Sau đó chạy `quet.py` lên `.srt` (câu trong 30 s đầu xét gắt). Cập nhật cả tiêu đề và mô tả dịch nếu kênh dùng.

## Tải lên
Mỗi `.srt` tải ở mục Phụ đề của Studio theo đúng ngôn ngữ; ghi tên tệp vào khối «Cài đặt khi tải lên» của postpack.
