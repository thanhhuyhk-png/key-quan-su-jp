# Đo tuổi khán giả của một kênh qua bình luận

Lý do: định dạng hình–giọng gắn chặt với tuổi khán giả, và luật học từ kênh khác tuổi sẽ làm hỏng kênh của mình (bẫy C1–C3). Không xem được YouTube Analytics của kênh khác, nên đo gián tiếp và ghi mức tin.

## Bước
1. **Lấy bình luận** của 3–5 video mỗi kênh (ưu tiên video top cộng một video thường), mỗi video ≥ 100 luồng; bỏ bình luận của chủ kênh; khử trùng lặp. Công cụ: `yt-dlp --write-comments --skip-download` (miễn phí) hoặc vidIQ. Không lưu tên người bình luận vào báo cáo.
2. **Nhãn chắc (tầng 1):** câu tự khai có chủ ngữ ngôi 1: «tôi/mình/em N tuổi», «năm nay 24t», «sinh năm 19xx/20xx», «2k8», «tân sinh viên», «học lớp N», «về hưu», «có cháu nội», hoặc suy từ năm («thi đại học năm 2004»). **Đọc tay từng nhãn**: regex hay bắt nhầm câu nói về người khác (bản đầu từng sai ≥ 10/70).
3. **Nhãn giai đoạn đời (tầng 2):** «chồng tôi», «mẹ chồng tôi», «con tôi học lớp N» (≥ 25 tuổi); «lớp em», «cô giáo em» (< 25). Sai khoảng 20 %.
4. **Tín hiệu yếu** (chỉ để so thứ tự giữa các kênh): tiếng lóng cứng của giới trẻ (vl, vcl, khum, bro, ae, «=)))») → trẻ; xưng «cô chú, quý vị, bác», «Nam mô», chúc sức khoẻ, viết hoa Từng Chữ → lớn tuổi. «ko, đc, k» vô dụng (người lớn cũng viết tắt).
5. **Kiểm định:** trên các bình luận có nhãn, so tín hiệu yếu với nhãn thật. Mẫu thử cho kết quả đúng 71 % (nền 66 %); «lớn tuổi» đúng 89 %, «trẻ» chỉ 60 %. Nghĩa là đủ để nói «kênh này **không có** người trẻ» khi tiếng lóng gần 0 và tín hiệu lớn tuổi cao; **không** đủ để nói «kênh này trẻ».
6. **Kết luận theo kênh, về MẪU BÌNH LUẬN, không phải toàn bộ người xem:** nhóm tuổi chủ đạo trong mẫu kèm mức tin.
   - Cao: ≥ 20 nhãn chắc nhất quán và khớp giả thuyết định dạng.
   - Vừa: 8–19 nhãn, hoặc ≥ 4 nhãn kèm tín hiệu mạnh cùng chiều.
   - Thấp: 1–7 nhãn.
   - Chưa xác định: 0 nhãn.
   Không có tiếng lóng **không** chứng minh không có người trẻ (người trẻ có thể xem im lặng).
7. **Dùng làm cổng thế nào:** chỉ loại kênh khỏi TOP hoặc Model Link vì tuổi khi mức tin từ Vừa trở lên cho thấy lệch khán giả mục tiêu. Mức Thấp hoặc Chưa xác định: giữ, ghi «cần kiểm», đối chiếu thêm định dạng, nhịp dựng, chủ đề, từ vựng kịch bản.

## Giả thuyết ban đầu: định dạng × tuổi (thị trường Việt Nam, đo thử 10/2026, đo lại theo thời điểm)
| Định dạng | Tuổi chủ đạo | Mức tin |
|---|---|---|
| Người que hoặc hoạt hình 2D kể chuyện ngôi «bạn», kinh tế | 16–34 | Vừa |
| Hoạt hình văn học, dân gian | hai đỉnh 13–17 và 35–50, hoặc 18–34 nghiêng trẻ | Thấp–Vừa |
| Hoạt hình, đồ hoạ giải thích đời sống | 18–34 | Thấp–Vừa |
| Shorts khoa học «điều gì xảy ra nếu» | hỗn hợp, nghiêng ≥ 45 | Thấp |
| Phim ngắn AI photoreal về gia đình | 35–60, nữ đã có gia đình | Vừa |
| Phim AI dài huyền sử; điều tra lịch sử; ảnh xưa | 35–60; ảnh xưa ≥ 50 | Vừa |
| Audio dài trên ảnh tĩnh | ≥ 50 | Cao |

Bảng này chỉ là điểm khởi đầu cho giả thuyết; ngách của bạn có thể khác. Sau khi đo, ghi kết quả thật vào hồ sơ kênh.

## Thuộc tính khác gắn với tuổi
Xưng «bạn» hoặc «tôi–anh em» thường là trẻ; «quý cô chú», «Mến chào» thường là ≥ 50. Video 9–25 phút nghiêng trẻ; ≥ 90 phút nghe nền nghiêng ≥ 50. Kết không khuyên răn nghiêng trẻ; kết đạo lý, nhân quả nghiêng ≥ 45. Thumbnail chữ trên nền đen nghiêng ≥ 45 (chưa có CTR để chắc).

## Giới hạn phải ghi trong báo cáo
Nhãn chắc thường < 1 % bình luận; người tự khai khác người im lặng; nhóm 25–34 rất ít tự khai nên vắng thật hay ít khai thì không phân biệt được; bình luận không phải người xem (audio nghe nền ít bình luận). Sau khi kênh của bạn đăng 2–3 video, thay toàn bộ bằng YouTube Analytics (tuổi × thời lượng xem, theo nguồn lưu lượng).
