# Ánh xạ: yêu cầu thành công cụ kiểm

Công cụ kiểm của kit: `python tools/kit/kit.py kiem <video>` (đo độ to, đỉnh, cỡ hình, fps, khung đen, hình đứng, đoạn lặng) và `ffmpeg`/`ffprobe` cho phần còn lại. Cờ có thể đổi theo phiên bản: khi nghi ngờ chạy lệnh kèm `--help`. Thêm `--json` để lấy số liệu cho reviewer. Mọi lệnh trong bảng dưới chạy cục bộ và **không tốn credit**, trừ khi ghi chú khác.

Nếu bạn dùng công cụ dựng khác, nguyên tắc giữ nguyên: mỗi tiêu chí đo được phải có một phép đo cụ thể (xem cuối tệp).

## Kiểm máy đo được

| Yêu cầu | Kiểm bằng | Ghi chú và giới hạn |
|---|---|---|
| Mở được, codec, độ dài | `ffprobe -v error -show_format -show_streams <video>` | |
| Đúng kích thước và fps | `python tools/kit/kit.py kiem <video> --size 1920x1080 --fps 24` | Đặt theo nền tảng đích (dọc 9:16 là `1080x1920`). |
| Hình không đứng hoặc đen bất thường | `kiem <video> --freeze-min <giây>` | Gộp «đen hoặc đứng». **Báo oan** với ảnh tĩnh, Ken Burns chậm, thẻ tiêu đề: ghi chú đó là cố ý. Khung đứng ngắn hơn ngưỡng thì bị bỏ qua. |
| Âm lượng đạt chuẩn, đỉnh | `kiem <video> --lufs -14` | -14 là mục tiêu mặc định cho video mạng xã hội; đổi theo nền tảng. Có báo đỉnh. Muốn đo đỉnh thật (true peak) thì chạy thêm bộ lọc `ebur128` của ffmpeg trên file cuối. |
| Khoảng lặng bất thường | `kiem <video> --silence-min <giây>` | Khoảng lặng kịch tính cố ý thì ghi chú. |
| Lời đọc khớp kịch bản | `python tools/kit/kit.py chep-loi <video>` rồi `python tools/kit/kit.py so-loi ...` | **Tốn credit** (dịch vụ chép lời). Hỏi trước nếu brief chưa cho phép chi. |
| Vùng an toàn dọc 9:16 | Soi ảnh khung theo vùng an toàn (trên ~150 px, dưới ~480 px, trái ~60 px, phải ~140 px) | Công cụ không tự đo; model làm trên ảnh khung. |
| Số cảnh, nhịp cắt | `ffmpeg -i <video> -vf "select='gt(scene,0.3)',showinfo" -f null -` | Số cắt cứng **không bằng** số cảnh (chuyển cảnh mượt không tính). |
| Ảnh tổng hợp để soi | `ffmpeg -i <video> -vf "fps=1/<giây>,scale=320:-1,tile=6x" -frames:v 1 sheet.png` | Đặt khoảng `<giây>` theo quy tắc lấy mẫu ở qa-qc.md, đừng dùng mặc định cho video dài. |
| Chữ và lời khớp nhau | Chép lời bản trộn, rồi đọc so với chữ trên khung | **Tốn credit**. Chép lời đối chiếu *kịch bản* với *âm thanh*, không so với chữ trên hình. |
| Trang HTML dựng ra video đúng | `node tools/kit/dung-trang.mjs <trang.html> --stills 0.5,1.2 --out-dir <thư-mục>` | Xuất ảnh tĩnh tại mốc giờ để soi trước khi dựng dài. |

## Trước khi tốn tiền (phần QA phòng ngừa)

| Việc | Cách |
|---|---|
| Máy và công cụ sẵn sàng chưa | `python tools/kiem-may/kiem-may.py` |
| Soi một cảnh trước khi dựng dài | `node tools/kit/dung-trang.mjs <trang.html> --stills <mốc giờ> --out-dir <thư-mục>` |
| Kiểm WebGL của máy trước khi dựng cảnh 3D | `node tools/kit/dung-trang.mjs --kiem-webgl` |
| Nghe thử một câu đọc | đọc một câu ngắn bằng `kit.py giong` (tốn credit nếu dùng giọng trả phí) |

## Kiểm bằng đọc ảnh, số liệu và chữ (model làm)

- Phóng to khung có chữ tiếng Việt: dấu, chữ bị cắt, tràn khung.
- So thời lượng thực với brief; đếm cảnh so với kịch bản.
- Đối chiếu transcript với kịch bản và với chữ hiện trên hình.
- Kiểm sổ tài sản và sổ số liệu (xem qa-qc.md).

## Chỉ người mới phán xét được (ghi rõ trong báo cáo)

Tất cả những gì cần **nghe hoặc xem video chạy**: giọng đọc có tự nhiên không, nhạc đè giọng ở đâu và có chịu được không, đồng bộ hình và tiếng (độ trễ), hook mở đầu có giữ chân không, nhịp cảm xúc, hợp phong cách thương hiệu không, có gây hiểu nhầm hay phù hợp văn hoá không. Công cụ ở trên không đo được việc nhạc nhỏ đi theo đoạn giọng hay độ lệch hình–tiếng. Máy chỉ nêu giả thuyết kèm bằng chứng (khung, mốc giờ); người quyết định.

## Khi công cụ khác

Mỗi tiêu chí đo được phải có một phép đo cụ thể (`ffprobe`, các bộ lọc `ffmpeg` như `ebur128`, `blackdetect`, `freezedetect`, `volumedetect`; xuất khung để soi). Chưa có công cụ cho phép đo nào thì ghi vào `checks.md` một dòng `blocker: <phép đo>` và tiếp tục các phần còn làm được; đừng bỏ qua im lặng.
