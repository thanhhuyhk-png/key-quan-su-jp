# Phản biện trước khi đưa TOP 20 và Model Link cho người dùng (pha 7)

Ghi kết quả từng câu vào tab «10. Chú ý & phản biện» (loại `phan_bien`, mức cao / vừa / thấp, việc cần làm).

## A. Bỏ sót
1. Kênh nào ít video mà sub nhiều, video dài, view tốt? Nó ở hạng mấy? Nếu không phải hạng 1, vì sao (bằng số)?
2. Nhóm «mới < 12 tháng» có bao nhiêu kênh trong TOP 20? Nếu 0, đã quét đủ chưa (bộ lọc «tháng này» của công cụ tìm kênh, kênh tương tự, và tìm bằng cụm tiêu đề `ytsearch` ở `nguon-du-lieu.md`)?
3. Kênh nào bị loại chỉ vì một điểm chấm tay? Mở lại lý do.
4. Có kênh nào chỉ vào bảng vì một video đột biến (phân tán > 20, 1/20 video > 2×)?

## B. Số liệu
5. Còn cờ NGHI_LOI_DON_VI, IT_VIDEO hoặc NHIEU_VIDEO_CUNG_NGAY nào chưa xử lý?
6. Đã kiểm tay ≥ 3 con số ngẫu nhiên với trang gốc chưa? Lệch bao nhiêu?
7. Hạng theo «tuổi từ video đầu» và «tuổi từ ngày lập» lệch nhau ở kênh nào? Đã ghi chưa?
8. Hai báo cáo con có nói hai số khác nhau cho cùng một thứ không? Chọn nguồn nào, vì sao?
9. Mỗi kết luận có nhãn [ĐO] / [SUY LUẬN] / [CHƯA CÓ] và n chưa?
   - 9a. Xếp hạng có chạy trên **tập Giữ** (không lẫn kênh bị loại) không? Khoảng hạng 3 bộ của TOP 5 có hẹp không (ví dụ «1–2» vững, «1–9» không vững)?
   - 9b. Kênh nào có cờ SUB_LAN_SHORTS, DANH_SACH_CO_THE_BI_CAT, KHONG_DU_CHI_SO? Đã lấy lại tổng video và ngày video đầu thật chưa?
   - 9c. Kênh đứng đầu nhờ số tích luỹ nhưng **đà** (% tăng 30 ngày, đà trung vị) đang xuống không?
   - 9d. `xep-hang --do-nhay`: kênh hạng 1 ở bao nhiêu trong 6 cách tính? Dưới 5/6 số cách hợp lệ (cách xếp được < 3 kênh không tính) thì không chốt một Model Link, trình ≥ 2 ứng viên kèm bảng so. Kênh đứng đầu nhờ % tăng sub 30 ngày của nền nhỏ (cờ DA_SUB_NEN_NHO, PCT_TANG_BI_CHAN_100) có còn hạng 1 khi bỏ chỉ số đó không?
   - 9e. Kênh nào TAI_SINH hoặc HOI_VIEN? Đã ghi chú khi dùng tuổi hoặc sub của kênh đó chưa?

## C. Khán giả và áp dụng
10. Model Link có khớp nhóm tuổi mục tiêu không (mức tin)? Có luật nào mượn từ kênh khác tuổi?
11. Cách làm của Model Link có nằm trong nguồn lực (người, tiền, số video mỗi tuần) không?
12. Model Link có vi phạm ràng buộc đề tài không? Phần nào phải bỏ khi bám? **Quy ước:** ràng buộc «không người thật hay thương hiệu thật» và đề tài cấm áp lên **nội dung của mình**. Với kênh mẫu: chỉ loại khi **lõi** kênh vi phạm đề tài cấm hoặc kênh quay người thật; thương hiệu hay người thật xuất hiện lẻ tẻ thì giữ kênh và ghi vào cột «Không học» (không bám).
13. Kết luận «kênh này thắng vì X» đã qua cặp đối chứng và kiểm mốc đăng chưa?

## D. Chi phí và rủi ro
14. Credit hoặc thời gian đã dùng so với trần? Có lô gọi nào lỗi phải trả lại?
15. Kênh mẫu có rủi ro bản quyền, nội dung lặp, nhãn nội dung AI, hay tài trợ phụ thuộc một nguồn không?

## E. Phản biện độc lập (khi kết quả quyết định tiền của người dùng)
**Do PHIÊN CHÍNH chạy.** Sub-agent làm pha 1–6 **không chạy mục này**: ghi vào tab Chú ý một dòng mức cao loại `phan_bien` «chờ phiên chính chạy mục E» (không ghi «chưa chạy» như thể bị bỏ sót), kèm đường dẫn báo cáo và bảng số.

Gửi báo cáo cùng bảng số (không bí mật, không tên người bình luận) cho một người hoặc công cụ khác trong thư mục nháp riêng, với yêu cầu: chấm 0–10 độ tin của Model Link, nêu 5 lỗ hổng nặng nhất kèm số dòng, kênh có thể bị bỏ sót, phép đo nào cần làm lại. Nếu máy không có CLI ngoài thì dùng một sub-agent ngữ cảnh mới làm người phản biện. Ý nào bác phải ghi lý do có nguồn.
