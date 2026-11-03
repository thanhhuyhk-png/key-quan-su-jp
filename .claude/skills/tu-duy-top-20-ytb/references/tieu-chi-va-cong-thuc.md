# Tiêu chí và công thức (chính xác, máy tính được)

`scripts/do_kenh.py` cài đúng các công thức dưới đây (hằng số ở đầu file, phiên bản `PHIEN_BAN`); sửa ở đây thì sửa cả script và test.

## 1. Chỉ số một kênh
| Chỉ số | Công thức | Ngưỡng / đọc thế nào |
|---|---|---|
| Video dài / Short | Cờ `is_short` (từ URL `/shorts/` hoặc tab Shorts) là chuẩn; không có cờ thì ước 0 < thời lượng ≤ 180 giây và gắn cờ SHORT_UOC_THEO_THOI_LUONG | Kênh > 50 % Short: NHIEU_SHORT |
| Trung vị 20 video dài | Trung vị view của 20 video dài gần nhất **đã đủ 30 ngày tuổi** (kênh < 90 ngày: đủ 14 ngày); cần ≥ 5 video, < 10 thì cờ MAU_TRUNG_VI_NHO | Mức «bình thường» của kênh. Đây là **lọc tuổi tối thiểu**, không phải chuẩn hoá tuổi: video 31 ngày và 300 ngày vẫn khác thời gian tích luỹ |
| Trung vị ÷ sub | Trung vị ÷ sub | < 5 % kênh yếu đi · 10–30 % bình thường · > 50 % được đề xuất cho cả người chưa đăng ký |
| Đà trung vị | Trung vị 10 video dài đủ tuổi gần nhất ÷ trung vị 10 video trước đó (cần ≥ 15 video) | > 1 đang lên · < 1 đang xuống |
| % tăng sub 30 ngày | (sub nay − sub 30 ngày trước) ÷ sub 30 ngày trước. **Khi xếp hạng:** kênh < 90 ngày tuổi (từ video đầu) bị chặn trần 100 % (cờ PCT_TANG_BI_CHAN_100); sub 30 ngày trước < 5.000 thì không dùng (cờ DA_SUB_NEN_NHO; **có chủ ý**: kênh nền nhỏ mất tiêu chí đà này, còn ≥ 3 tiêu chí khác thì vẫn xếp được). Kênh SUB_LAN_SHORTS bỏ luôn chỉ số này (và `tang_sub_30`). Bản thô giữ ở `pct_tang_sub_30_tho` | Mốc tham khảo: ≥ 10.000 sub mỗi tháng tốt, 8.000 tạm, 5.000 thấp (chưa kiểm chứng, đổi theo ngách) |
| Video > 2× trung vị | Đếm trong 20 video trên (và tỉ lệ /n) | **Chỉ để đọc**, không cộng điểm: nhiều video đột biến không có nghĩa là cách làm lặp lại được |
| Phân tán | View cao nhất ÷ trung vị | > 20: phụ thuộc vài video đột biến |
| Sub mỗi video | Sub ÷ **tổng video của kênh** (từ trang kênh) | Hiệu suất mỗi video |
| Sub mỗi ngày, view mỗi ngày | Sub (tổng view) ÷ số ngày từ **ngày video đầu thật** (và từ ngày lập) | Tốc độ từ đầu |
| Tỉ trọng view Shorts | `--ty-trong-view-short` (nguồn ngoài, ví dụ vidIQ, 30 ngày) nếu có, không thì View Shorts ÷ tổng view trong danh sách đã lấy (ước từ mẫu, sai khi mẫu Shorts không đủ) | ≥ 20 %: cờ SUB_LAN_SHORTS, 4 chỉ số dựa trên sub (sub/video, trung vị ÷ sub, sub/ngày hai cách) bị bỏ khỏi xếp hạng (giữ bản thô `*_tho`); kênh lai có thể còn < 3 tiêu chí và thành «Không đủ chỉ số». `xep-hang --ghi-de` ép cờ bằng tay kèm lý do |
| Tỉ lệ like trung vị | Trung vị like ÷ view | Like < 1 % kèm bình luận chung chung: nghi mua view |

## 2. Hệ số vượt trội một video
- **Hệ số** = view ÷ trung vị view của **15 video dài đăng ngay trước** (sắp theo giờ đăng nếu có, không thì theo ngày; cùng ngày không có giờ thì cờ `cung_ngay`). < 5 video trước thì không tính.
- **Hệ số sau** = trung vị **đúng 5** video dài đăng ngay sau ÷ cùng trung vị trước; thiếu 5 thì không tính. ≥ 1,5: kênh đã tìm ra cách làm mới; ≈ 1: video là trường hợp riêng.
- **Mức** (một bảng duy nhất, `MUC_HE_SO`): < 2 bình thường · 2 đến dưới 3 hơi cao · 3 đến dưới 5 đáng ghi · 5 đến dưới 10 mạnh · ≥ 10 kiểm kỹ · video < 30 ngày tuổi: **chưa chín** (view chưa đủ thời gian).
- **Cửa sổ liên tục:** `--cua-so-tu <ngày>` chỉ tính hệ số cho video đăng từ ngày đó và chỉ cho chúng làm hàng xóm của nhau; video cũ hơn (ví dụ video top lẻ) có hệ số None, `ly_do_khong_tinh` = `ngoai_cua_so`. Hệ số None còn có lý do `it_hon_5_video_truoc`. Cần ≥ 20 video dài trong cửa sổ để có hệ số cho phần lớn video: lấy **≥ 100 video dài mới nhất**.
- Kho vượt trội = hệ số ≥ 3. Tô xanh trong sheet chỉ khi hệ số ≥ 5 **và** «kiểm tra số thật» = đạt.
- **Kiểm tra số thật** (trước khi tin một video vượt trội): like ≥ 0,5 % view, like không vượt view, bình luận có nội dung thật (không toàn câu chung chung), video đủ 30 ngày tuổi. Đạt đủ và người đã đọc bình luận mới ghi `dat`.

## 3. Điểm hiệu suất và hạng
- **Lọc trước, xếp sau:** chỉ xếp trên tập kênh «Giữ»; phân vị tính trên tập có cả kênh bị loại sẽ méo.
- Phân vị kiểu **trung bình hạng** (mid-rank) 0–100: (số kênh thấp hơn + ½ số kênh bằng) ÷ số kênh có giá trị.
- Điểm = trung bình phân vị của các tiêu chí **có giá trị**; cần ≥ 3 tiêu chí, không thì «Không đủ chỉ số» (không xếp, không chấm 0).
- Ba bộ tiêu chí để thấy độ nhạy:
  - **Tích luỹ:** sub mỗi video, trung vị 20 video dài, trung vị ÷ sub, sub mỗi ngày.
  - **Đà:** % tăng sub 30 ngày, đà trung vị, sub mỗi ngày.
  - **Tổng** (dùng làm hạng chính): hợp của hai bộ trên.
- Hạng kiểu cạnh tranh trên điểm làm tròn 1 chữ số (1, 2, 2, 4). Báo **khoảng hạng** (thấp nhất đến cao nhất qua 3 bộ) và hạng theo ngày lập (khi ≥ 80 % kênh có ngày lập).
- Kênh «ít video mà sub nhiều» = sub mỗi video ở phân vị ≥ 75 và số video ≤ trung vị của bảng.
- **Độ nhạy** (`xep-hang --do-nhay`): chạy 6 cách (tổng, tích luỹ, đà, tổng bỏ % tăng sub 30 ngày, tổng chỉ kênh ≥ 90 ngày tuổi, chỉ trung vị tuyệt đối gồm trung vị + đà trung vị + trung vị ÷ sub) và in «hạng 1 ở n/6 cách» cho từng kênh. Mỗi cách in `n_xep` (số kênh xếp được); cách xếp được < 3 kênh không hợp lệ, không tính vào «hạng 1 ở n/m» (m = số cách hợp lệ). Kênh hạng 1 ở ≥ 5/6 số cách hợp lệ là vững; chênh điểm lớn ở cách chính chưa đủ.
- Không cộng điểm chấm tay. Đổi bộ tiêu chí hoặc trọng số thì ghi lý do, đổi `PHIEN_BAN`, và báo kết quả cả cách cũ.

## 4. Điểm cơ hội đề tài
6 mục, mỗi mục 1–5 (số nguyên), tổng /30: Nhu cầu · Bằng chứng nhiều kênh · Khoảng trống · Hợp khán giả mục tiêu · Chi phí làm được · Rủi ro thấp. > 22 thử ngay · 16–22 theo dõi · < 16 bỏ. Thiếu mục hoặc ngoài 1–5 thì không kết luận. Sáu mục này do kênh đặt ra để chấm đều tay, có thể điều chỉnh theo ngách nhưng phải ghi lý do.

## 5. Kiểm chứng nhiều kênh
Đề tài hoặc kiểu video đáng tin khi: ≥ 3 kênh có video cùng đề tài hệ số > 3, có cả kênh nhỏ và lớn, nhiều góc vẫn thắng, bình luận cùng nhu cầu, vẫn nhận view 2 tuần gần đây. Chỉ một kênh thắng thì hỏi kênh đó có lợi thế riêng không.

## 6. Bình luận
Đếm: yêu cầu đề tài, yêu cầu phần tiếp, bổ sung hoặc sửa, chia sẻ trải nghiệm, phàn nàn (độ dài, giọng, sai thông tin), tự nói tuổi hoặc nghề, nhóm cảm xúc (khóc, xúc động, sợ, cười, nhận ra mình). Yêu cầu ≥ 10 lần hoặc ở ≥ 3 kênh thì đưa vào kế hoạch.

## 7. Lịch sử phiên bản công thức (`PHIEN_BAN`)
- `2026-10-22.3`: % tăng sub 30 ngày bị chặn trần 100 % khi kênh < 90 ngày tuổi và bỏ khi nền < 5.000 sub (cũng bỏ ở kênh lai Shorts); `--cua-so-tu` (thiếu tổng video thì bỏ sub mỗi video, cờ THIEU_TONG_VIDEO_CHO_CUA_SO); `--meta` (hệ số và trung vị chỉ trong cửa sổ, không báo thiếu video); `--ty-trong-view-short` và `--ghi-de`; `--do-nhay`; cờ TAI_SINH, HOI_VIEN, DA_SUB_NEN_NHO, PCT_TANG_BI_CHAN_100. Hạng cũ không so được với hạng mới ở kênh có `pct_tang_sub_30` bị chặn hoặc bỏ.
- `2026-10-22.2`: bản phản biện (khoảng hạng 3 bộ, hạng theo ngày lập, cờ cổng dữ liệu).
Đổi công thức thì thêm dòng ở đây, đổi `PHIEN_BAN`, báo kết quả cả hai cách (mục 3).

## 8. Nhóm kênh và cờ tuổi
- Ba nhóm **chồng lấp**, một kênh có thể thuộc nhiều nhóm; trong hồ sơ `nhom` là danh sách mã (`moi`, `on_dinh`, `cung_nguon_luc`; chuỗi cũ vẫn nhận).
- **Mới** = tuổi từ **ngày video đầu** < 365 ngày (script tính, ghi đè nhãn tay). **Ổn định** = từ video đầu ≥ 730 ngày (gắn tay hoặc từ ngày video đầu).
- **Cùng nguồn lực** = nhãn người gắn, [SUY LUẬN], không đo được: chỉ gắn khi kênh thoả đủ tiêu chí do pha 0 ghi cụ thể (ví dụ: không lộ mặt hoặc 2D, ≤ 2 video dài mỗi tuần, không hãng hay đài, không diễn viên) và ghi tiêu chí vào cột Chú ý. Cổng «mỗi nhóm ≥ 5» tính trên **60 kênh khảo sát** (không phải TOP); nhóm này không được tự đạt bằng cách gắn rộng.
- **TAI_SINH** = ngày lập cách ngày video đầu > 12 tháng (cần `--ngay-lap`; chỉ tính khi ngày video đầu truyền tay hoặc lấy từ meta, hoặc danh sách coi là đủ, không tính trên danh sách bị cắt): sub có thể là lịch sử của kênh cũ. Kênh TAI_SINH ở nhóm «mới» bị cảnh báo ở tab Chú ý và **không tính là kênh mới** cho luật «TOP phải có kênh mới».
