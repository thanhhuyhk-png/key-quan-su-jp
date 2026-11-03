# Bẫy số liệu và sai sót đã gặp (đọc trước pha 2)

Mỗi dòng là một lỗi **đã xảy ra thật** khi nghiên cứu kênh mẫu, kèm hậu quả, dấu hiệu và cách bắt. Gặp lỗi mới thì thêm một dòng: ngày, bằng chứng, cách bắt.

## A. Lấy số
| # | Bẫy | Hậu quả đã thấy | Cách bắt / sửa |
|---|---|---|---|
| A1 | `yt-dlp --flat-playlist` chạy với giao diện tiếng Việt đọc «809 N» (N là nghìn) thành 809 | View và sub sai 1.000 lần: kênh 38.000 sub hiện thành 38 | Dấu hiệu: like lớn hơn view, kênh ≥ 10.000 sub mà mọi video < 1.000 view. `do_kenh.py` gắn cờ NGHI_LOI_DON_VI. Lấy số từ metadata đầy đủ từng video hoặc API, đặt ngôn ngữ tiếng Anh, kiểm tay 3 số với trang gốc |
| A2 | Chạy nhiều yt-dlp song song | YouTube chặn IP máy (lỗi 429) cả buổi | Chạy tuần tự, có nghỉ giữa lệnh, **không** dùng cookie hay profile trình duyệt |
| A3 | Nhiều tiến trình cùng gọi một dịch vụ trả credit | Lỗi kết nối, hao credit, hai nơi cùng báo «đã dùng» trên một tài khoản nên đếm chồng | Một tiến trình giữ quyền gọi; xem số dư trước và sau mỗi lô; đặt trần credit trong brief |
| A4 | API hoặc công cụ chỉ trả một phần danh sách video | Lấy được 94–98 video mỗi kênh, tưởng là toàn bộ | Ghi n lấy được so với tổng trên trang kênh; trung vị chỉ tính trên phần có |
| A5 | Sub-agent báo «đã lấy» nhưng không ghi được file | Mất dữ liệu, phải thu lại | Kiểm file tồn tại ngay sau mỗi lần lấy; ghi đường dẫn thật vào báo cáo |
| A6 | Không xem được ảnh bìa (trình duyệt bị chặn domain ảnh) | Kết luận về ảnh bìa bị bỏ trống mà không ai nói | Tải ảnh bằng `yt-dlp --write-thumbnail` rồi mở xem; không được thì ghi [CHƯA CÓ], không đoán |
| A7 | `--flat-playlist` bỏ qua sắp xếp theo view, làm tròn view, dịch tiêu đề khi `lang=en` | Không lấy trực tiếp được «video nhiều view nhất»; view 200000 thay vì 200.583; tiêu đề tiếng Anh thay nguyên văn | Flat chỉ để lấy id và chọn top 10 theo view; số và tiêu đề lấy bằng metadata đầy đủ (`scripts/thu_video.py`) |
| A8 | Video hội viên (members-only) nằm trong danh sách flat nhưng không đọc được | Nếu video cũ nhất là hội viên thì ngày video đầu bị lệch | `thu_video.py` đếm `so_hoi_vien`, lấy ngày nhỏ nhất của video cũ nhất đọc được; `do_kenh.py --so-hoi-vien` gắn cờ HOI_VIEN; ghi chú khi dùng sub/ngày |
| A9 | Chạy nền hai lệnh thu dữ liệu | Hai yt-dlp song song (rủi ro 429), log trống nên khó thấy | File PID trong thư mục đầu ra, từ chối chạy khi PID còn sống; xem tiến trình bằng `Get-CimInstance Win32_Process` |

## B. Chuẩn hoá
| # | Bẫy | Hậu quả đã thấy | Cách bắt / sửa |
|---|---|---|---|
| B1 | Xếp hạng bằng số tuyệt đối (tổng sub, tăng 30 ngày tuyệt đối) | Kênh mới 7 tuần, 22 video, ~4,8 triệu view, ~38.000 sub (~1.700 sub mỗi video) bị xếp hạng 5 thay vì hạng 1 | Dùng sub mỗi video, sub mỗi ngày, view mỗi ngày từ video đầu, trung vị mỗi video; tự hỏi câu bắt buộc của luật thép 3 |
| B2 | Cộng điểm chấm tay («hợp hướng», «làm được bằng AI») vào điểm xếp hạng | 13/20 kênh TOP cùng một kiểu vì điểm tay nghiêng về kiểu đó | Điểm tay chỉ để lọc Giữ/Loại, không cộng vào điểm hiệu suất |
| B3 | Tuổi kênh tính từ ngày lập hay từ video đầu | Cùng một kênh ra hạng 1 hoặc hạng 3 tuỳ cách tính | Tính cả hai, báo cả hai hạng (`xep-hang` in sẵn) |
| B4 | View mỗi ngày ưu ái video mới | Video 2 tuần tuổi trông «vượt trội» | So cùng độ tuổi (view sau 7 hoặc 30 ngày); video < 14 ngày đo lại sau 2 tuần |
| B5 | Trộn Shorts với video dài | Trung vị sai, hệ số sai | Tách Shorts (≤ 3 phút) trước khi tính |
| B6 | Kênh tái sinh, đổi đề tài, ngày đăng nhảy | Một kênh có bước nhảy từ 5 lên 105 video trong 1 ngày; tuổi video mơ hồ | Cờ NHIEU_VIDEO_CUNG_NGAY; chỉ tính trên video cùng đề tài mới |
| B7 | Mẫu «video kém» chỉ 1–4 video | Kết luận «hit do premise, không do văn phong» chắc về hướng nhưng yếu về thống kê | Luôn ghi n; n < 5 thì nhãn [SUY LUẬN] |
| B8 | Bỏ qua mốc đăng khi so hit với flop | Kênh mới: video đăng tuần đầu trung vị 119k, sau đó 214–221k; tưởng do nội dung | Thêm biến «tuần thứ mấy của kênh» vào cặp đối chứng; so trong cùng giai đoạn |
| B9 | Từ khoá tiếng Việt bằng 0 rồi kết luận «không có nhu cầu» | Một ngách bị chấm 1/10 trong khi Shorts của nó có 44/44 video ≥ 1 triệu view; người Việt tìm bằng tiếng Anh | Tam giác hoá: lượng tìm (Việt + Anh), view thật, số kênh |
| B10 | Tính phân vị trên cả kênh sẽ bị loại | Thứ hạng trong tập Giữ bị méo | Lọc trước, xếp hạng chỉ trên tập Giữ |
| B11 | Kênh thiếu chỉ số bị chấm 0 | Kênh mới chưa có video đủ 30 ngày rơi xuống đáy | Điểm = trung bình tiêu chí có giá trị; < 3 tiêu chí thì không xếp; kênh < 90 ngày dùng video ≥ 14 ngày |
| B12 | Sub của kênh lai bị Shorts thổi lên | Sub mỗi video, trung vị ÷ sub của kênh nhiều Shorts đẩy kênh lên đầu bảng video dài | Tỉ trọng view Shorts ≥ 20 % → cờ SUB_LAN_SHORTS, bỏ chỉ số dựa trên sub |
| B13 | Chỉ dùng chỉ số tích luỹ | Kênh từng nổi nhưng đang xuống vẫn hạng 1 | Thêm bộ «đà» (% tăng sub 30 ngày, đà trung vị); báo khoảng hạng 3 bộ |
| B14 | Tỉ trọng view Shorts đo từ mẫu Shorts đã lấy | Một kênh: nguồn ngoài báo 22 % view 30 ngày là Shorts (957 Shorts, 39 video dài) nhưng mẫu 15 Shorts đo ra 6 % nên sub không bị bỏ | `--ty-trong-view-short` (nguồn ngoài) ưu tiên hơn mẫu; `xep-hang --ghi-de "<kênh>:SUB_LAN_SHORTS:<lý do>"` |
| B15 | Trộn video nhiều view ngoài cửa sổ vào cùng danh sách rồi tính hệ số | «15 video liền trước» thật ra là những video xa nhau nên hệ số sai mà không có cờ | `--cua-so-tu`: hệ số chỉ cho video trong cửa sổ, ngoài cửa sổ là None kèm lý do |
| B16 | % tăng sub 30 ngày của kênh nền nhỏ hoặc kênh mới | Một kênh hạng 1 nhờ +189 % trên nền ~13.000 sub; luật «chênh < 3 điểm» không bắt được | Trần 100 % cho kênh < 90 ngày, sàn nền 5.000 sub; `xep-hang --do-nhay`; Model Link cần hạng 1 ở ≥ 5/6 cách hoặc trình ≥ 2 ứng viên |
| B17 | Kênh tái sinh (lập nhiều năm trước, video công khai mới chỉ vài tháng) | Bị coi «Mới» mà sub có thể là lịch sử của kênh cũ | Cờ TAI_SINH (ngày lập cách video đầu > 12 tháng); không dùng % tăng sub làm bằng chứng cho kênh này |

## C. Khán giả và diễn giải
| # | Bẫy | Hậu quả đã thấy | Cách bắt / sửa |
|---|---|---|---|
| C1 | Gộp kênh khác nhóm tuổi rồi rút luật chung | Luật văn phong của audio cho người ≥ 50 tuổi bị áp cho kênh 18–34 | Gắn tuổi từng kênh (pha 4); mỗi luật ghi đúng nhóm tuổi |
| C2 | «View lớn = khán giả trẻ» | Một Shorts 1,39 triệu view có 38 % bình luận «cảm ơn», 0 % tiếng lóng → khán giả ≥ 45 | Đo tuổi bằng bình luận, không suy từ view |
| C3 | Tín hiệu tuổi yếu (viết tắt «ko, đc») | Đoán «trẻ» chỉ đúng 60 % | Ưu tiên nhãn tuổi tự khai; tín hiệu yếu chỉ để so thứ tự |
| C4 | Bình luận không phải là khán giả | Chủ kênh trả lời 64 % luồng; có tài khoản gieo bình luận | Bỏ bình luận của chủ kênh; ghi tỉ lệ trả lời trong mẫu |
| C5 | Báo cáo con có hai phiên bản số liệu lệch nhau | Hai bản cùng kênh khác khung số | Một nguồn sự thật; bản cũ đổi tên `*.ban-cu` và không trích |
| C6 | Kết luận «làm khóc» mượn từ kênh khác tuổi | Kênh 16–34 gần như không có bình luận khóc (11/1.365) | Đếm nhóm bình luận cảm xúc theo từng kênh |
| C7 | Ràng buộc đề tài đặt sau khi chấm | Ngách điểm cao nhất có 4/5 kênh tăng nhanh thuộc loại đề tài bị cấm | Lọc ràng buộc ngay từ pha 3, ghi số kênh bị loại vì ràng buộc |

## D. Quy trình
| # | Bẫy | Cách bắt / sửa |
|---|---|---|
| D1 | Chỉ học trọn «TOP 4» theo bảng cũ, bỏ qua kênh hạng 5 có hiệu suất cao nhất | Học trọn theo hạng sau chuẩn hoá; TOP 1 bắt buộc học trọn |
| D2 | Chép cơ chế của kênh nước ngoài mà không hỏi có hợp văn hoá không | Mỗi điều «học» ghi rõ: bằng chứng ở thị trường nào, nhóm tuổi nào |
| D3 | Sub-agent tự đặt mục khi tài liệu gốc thiếu | Ghi rõ «tự đặt», để người dùng xác nhận |
| D4 | Vượt trần credit | Trần trong brief; xem số dư giữa chừng; vượt thì dừng và báo |
| D5 | Tiêu đề hoặc tên kênh bắt đầu bằng «=» thành công thức khi lên Google Sheet | `xuat_sheet.py` ghi mọi ô chữ dạng chuỗi; không dán dữ liệu thô vào Sheet bằng tay |
| D6 | Ước «hạng 30 ngày trước» từ riêng số sub | Không ước; lần đo đầu để trống, lưu ảnh chụp tab 9 để kỳ sau so thật |
| D7 | Đối chứng 1–1 rồi quy kết nhân quả | Nhóm với nhóm, 6 biến, ghi là giả thuyết |
