# Chọn giọng cho kênh

## Quy tắc cứng
1. `voice_id` **khác** `3VnrjnYrskPMDsapTr8X` (giọng kênh mẫu). So bằng chữ trước khi ghi hồ sơ.
2. Không nhân bản giọng của người thật khi chưa có phép của họ bằng văn bản; không dùng giọng nghe như lãnh tụ hay người nổi tiếng.
3. Giọng tổng hợp không được tự nhận là chuyên gia người thật. Người dẫn kể ở ngôi thứ ba.
4. Gọi ElevenLabs là **bước trả phí**: báo số ký tự và chi phí ước trong chat, chờ người dùng đồng ý, mới gọi. Nghe thử mỗi giọng một đoạn 150–300 ký tự (cùng một đoạn lời thật của ngách), tối đa 3 giọng.

## Chọn theo mức chạy và ngôn ngữ
| Mức | Tiếng Việt | Ngôn ngữ khác |
|---|---|---|
| Đầy đủ | ElevenLabs, model `eleven_v4`, `language_code` `vi` | ElevenLabs, chọn giọng có nhãn ngôn ngữ ngách trong thư viện giọng; model hỗ trợ ngôn ngữ đó (tra trang ElevenLabs lúc chọn, ghi ngày tra) |
| Tiết kiệm | VieNeu V4 (tính token) | ElevenLabs gói thấp, hoặc Kokoro chạy trên máy nếu ngôn ngữ có hỗ trợ |
| Miễn phí | VieNeu V3 chạy trên máy | Kokoro chạy trên máy (mã nguồn mở) |

Đánh đổi của bản thay thế: giọng kém tự nhiên hơn, phải kiểm đuôi câu bị cụt hoặc kéo dài, ít điều khiển cảm xúc. Ghi vào mục 6 của hồ sơ.

## Cách nghe thử (ElevenLabs)
Dùng lệnh của kit (khoá `ELEVENLABS_API_KEY` trong `.env` do người dùng tự dán; không đọc giá trị):
`python -I -X utf8 tools/kit/kit.py giong --text-file <đoạn.txt> --voice <voice_id> --model <model> --lang <mã> --out <thu-giong-1.wav>`
Đoạn thử đặt ở thư mục tạm trong `<output>`, không để trong repo. Với VieNeu và Kokoro xem mục «Giọng thay thế» ngay dưới; ghi cách gọi đã dùng vào hồ sơ để P4 dùng lại.

## Giọng thay thế cho mức Tiết kiệm và Miễn phí
Trạng thái: **chưa thử đầu cuối trên kit** (kit chỉ thử đường ElevenLabs). Các lệnh dưới lấy từ mã mẫu có sẵn trong repo hoặc từ tài liệu công khai của từng công cụ; chạy thử một đoạn ngắn trước, nếu lệnh khác thì ghi lệnh thật vào hồ sơ và báo chủ kit.
- **VieNeu V4 (tính token, tiếng Việt):** nếu phiên Claude Code của bạn đã nối dịch vụ VieNeu (kết nối Claude của VieNeu) thì Claude đọc bằng công cụ của kết nối đó: tìm giọng rồi đọc một đoạn nghe thử. Mỗi lần đọc tốn token của tài khoản VieNeu của bạn: báo số ký tự trong chat và chờ đồng ý như bước trả phí. Chưa nối thì hỏi người dùng có muốn nối không, đừng tự cài.
- **VieNeu V3 chạy trên máy (miễn phí, tiếng Việt):** hai cách. (a) Mở ứng dụng VieNeu trên máy, và nếu kết nối VieNeu có sẵn thì Claude đọc qua ứng dụng đó, không tốn token. (b) Gói Python `vieneu`: cài `python -m pip install vieneu` (tên gói theo trang chính thức của VieNeu, kiểm lại nếu pip báo không tìm thấy). Mẫu gọi nằm ở `tools/vieneu-ab/doc-tung-cau.py` (đọc từng câu, tự đọc lại câu bị cụt đuôi): `python -I -X utf8 tools/vieneu-ab/doc-tung-cau.py <lời.txt, mỗi câu một dòng> <mã giọng> <thư mục ra>`. Giọng sẵn có xem bằng `Vieneu().list_preset_voices()`. Chạy CPU chậm; có GPU thì nhanh hơn. Công cụ mẫu `tools/vieneu-ab/ab.py` so chất giọng theo thiết bị.
- **Kokoro (mã nguồn mở, tiếng Anh và vài ngôn ngữ khác, chạy trên máy):** cài `python -m pip install kokoro soundfile` theo tài liệu của Kokoro (lần đầu tự tải model). Kit chưa có lệnh bọc; Claude viết một đoạn Python ngắn gọi `KPipeline` đọc từng câu rồi ghi `.wav`, người dùng nghe thử trước khi dùng. Ghi lệnh đã chạy được vào hồ sơ mục 3.
- Dù dùng công cụ nào, P4 vẫn cần đúng những thứ P4 đọc từ hồ sơ: tên nhà cung cấp, mã giọng, cách đọc (từng câu), và quy tắc kiểm đuôi câu.

## Tiêu chí chọn (người dùng nghe, Claude hỗ trợ đo)
- Hợp khán giả: giới, tuổi, vùng miền (tiếng Việt: giọng Bắc dễ hiểu nhất cho tài liệu).
- Nhịp tự nhiên ở câu dài; không méo ở số, năm, tên riêng (cho đọc thử một câu có 3 số và 1 tên riêng).
- Độ to đo bằng `ebur128` không lệch quá 1 dB giữa các câu.
- Khác kênh mẫu **và** khác các kênh đối thủ cùng ngách nghe được (nghe 2 video top trong sheet), để người xem không nhầm.

## Thẻ đầu bài và sửa câu (nếu chọn model có hỗ trợ)
- Thẻ đầu bài (vd `[fast-paced]`) do model quyết định có tác dụng hay không. Thử trên đoạn nghe thử, không dùng thẻ không có tác dụng.
- Quy tắc sửa một câu: đọc lại ba câu liền (trước, đó, sau) trong một lần gọi rồi cắt lấy câu giữa, để giọng điệu liền mạch.
- Model bỏ qua `speed` thì không tăng tốc bằng xử lý sau (méo cao độ).
