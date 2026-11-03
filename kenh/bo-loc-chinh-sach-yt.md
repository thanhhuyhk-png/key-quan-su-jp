# Bộ lọc chính sách YouTube cho chữ của kênh

Tên kênh, ngách, ngôn ngữ: đọc `ho-so-kenh/ho-so.md`. Tệp này dùng chung cho mọi kênh làm từ kit; luật riêng của ngách nằm ở `ho-so-kenh/luat-noi-dung.md`.

Mục đích: mọi chữ người xem thấy hoặc nghe (kịch bản, lời đọc, tiêu đề, chữ trên ảnh bìa, chữ trên hình, mô tả, thẻ, bình luận ghim) **không bị tắt hoặc hạn chế quảng cáo, không bị gỡ, không mất quyền kiếm tiền cả kênh**.
Nghiên cứu ngày 01/11/2026 từ trang chính thức của YouTube (nguồn ở cuối). Rà lại mỗi 3 tháng hoặc khi YouTube cập nhật nhật ký thay đổi.

## Điều cần biết trước
- **YouTube không công bố danh sách từ cấm nào.** YouTube xét theo **nhóm nội dung**, **ngữ cảnh** (giáo dục, tài liệu là ngữ cảnh tốt) và **vị trí** (tiêu đề và ảnh bìa bị xét nặng hơn lời đọc). Danh sách từ ở `tools/loc-chinh-sach/tu-cam.tsv` do chủ kit suy ra từ chính sách YouTube và từ bình luận người xem của một kênh mẫu. Đó là lưới an toàn, không phải luật của YouTube.
- Ba mức: **xanh** (quảng cáo đầy đủ) · **vàng** (hạn chế quảng cáo) · **đỏ** (không quảng cáo). Nếu phần lớn video của kênh không phù hợp, YouTube có thể **tắt quảng cáo cả kênh**.
- Kênh tài liệu lịch sử, chiến tranh nằm ở vùng xanh **nếu** có ngữ cảnh giáo dục và **không có hình hoặc lời tả thương tích**.

## A. Chính sách áp vào kênh lịch sử, quân sự

| Nhóm | Xanh (được) | Vàng hoặc đỏ (tránh) |
|---|---|---|
| **Bạo lực, chiến tranh** | Chiến tranh kể có tính giáo dục, không ghê rợn. Thi thể trong sự kiện lịch sử ở video giáo dục **nếu đã che hoặc làm mờ hẳn** | Vàng: thi thể có thương tích rõ (kể cả trong phim tài liệu); phim chiến trường thô không có ngữ cảnh; **tả chi tiết thảm kịch bằng lời**. Đỏ: hình hoặc lời kể ghê rợn về bắn giết, nổ, hành quyết, ném bom; mọi cảnh chiến tranh có thương tích, cái chết, đau đớn ghê rợn; cổ vũ, ca ngợi bạo lực |
| **Ngữ cảnh tài liệu** | Ngữ cảnh phải nằm **ngay trong hình hoặc lời** của video; riêng đề tài chiến tranh thì tiêu đề, mô tả cũng tính | Chỉ ghi ngữ cảnh ở tiêu đề hoặc mô tả mà hình thì sốc. Tiêu đề kiểu "cảnh báo: nhiều máu" là yếu tố bất lợi |
| **Thù hằn** | Nhắc dân tộc, quốc gia không xúc phạm; tài liệu về phân biệt đối xử; hình ảnh thù hằn làm trọng tâm trong video giáo dục | Vàng: từ miệt thị không che trong phim tài liệu. Đỏ: hạ thấp một nhóm người, từ miệt thị ngoài ngữ cảnh giáo dục, cổ vũ bạo lực, **phủ nhận thảm kịch** |
| **Tổ chức cực đoan** (Quốc xã, Khmer Đỏ, IS…) | Kể có ngữ cảnh tài liệu ngay trong video | "Không phải giấy phép để ca ngợi". Cấm đăng lại nguyên bản phim tuyên truyền, cấm phô biểu tượng để tôn vinh |
| **Chửi tục** | Từ nhẹ, hoặc đã che | Chửi tục vừa trong tiêu đề, ảnh bìa thì vàng; chửi tục mạnh trong tiêu đề, ảnh bìa thì đỏ; dùng dày đặc trong video cũng bị hạn chế. (Từ 07/2025 chửi tục ở 7 giây đầu không còn bị phạt, nhưng kit không dùng) |
| **Gây sốc** | Nội dung gây sốc vừa phải mà đã che, hoặc có ngữ cảnh giáo dục | Đỏ: mục đích là gây sốc, ít hoặc không có ngữ cảnh |
| **Vũ khí** | Kể lịch sử, cấu tạo, tháo lắp để giải thích | Đỏ: hướng dẫn chế tạo, độ chế vũ khí; chỉ chỗ mua bán |
| **Hành vi nguy hiểm** | Giáo dục, bác bỏ tin sai | Đỏ: hướng dẫn chế bom, chất nổ |
| **Vấn đề gây tranh cãi** (xâm hại tình dục, tự sát…) | Nhắc thoáng qua, không mô tả | Vàng: làm trọng tâm dù là tài liệu, ảnh bìa có hình ảnh mạnh. Đỏ: mô tả chi tiết |
| **Tình dục** | Không | Đỏ: mọi nội dung tình dục, kể cả trong ảnh bìa |
| **Sự kiện nhạy cảm** | Bàn về mất mát, thảm kịch một cách không khai thác | Đỏ: **dùng từ khoá của sự kiện để kéo view**. Ukraine: nội dung "khai thác, xem nhẹ hoặc dung túng" cuộc chiến bị tắt kiếm tiền |
| **Nội dung không chân thực** (đổi tên từ 15/07/2025) | Cùng khung mở, kết nhưng phần lớn nội dung khác nhau; mỗi tập một câu chuyện, trọng tâm riêng | Trình chiếu ảnh hoặc chữ chạy mà ít lời kể, ít giá trị giáo dục; "nội dung AI làm từ khuôn mẫu chung chung"; cảm giác sản xuất hàng loạt. Hậu quả: **mất quyền kiếm tiền cả kênh** |
| **Nội dung dùng lại** | Có lời bình, phân tích, dựng lại đủ để người xem thấy khác hẳn bản gốc | Tải về rồi đăng gần như nguyên vẹn; ghép đoạn phim mà ít lời kể; chỉ đọc lại tài liệu của người khác. Có xin phép vẫn bị tính |
| **Khai báo AI** | Không bắt buộc khai: dùng AI viết, sửa kịch bản, tiêu đề, ảnh bìa; chỉnh màu; phụ đề; nhân bản giọng của chính mình | **Bắt buộc khai** ("AI use" trong YouTube Studio): làm người thật như đã nói hoặc làm điều họ không làm; cảnh thật giả lập trông như thật. Khai báo **không** làm giảm quảng cáo |
| **Nhân vật AI** | Người dẫn kể ngôi thứ ba | Giọng tổng hợp **tự nhận là chuyên gia người thật** |

## B. Luật riêng của kit (chồng thêm lên chính sách YouTube)
Luật cứng ở `CLAUDE.md` của kit và luật riêng ngách ở `ho-so-kenh/luat-noi-dung.md` vẫn đứng trên hết. Luật cứng gồm: sử chính thống; cấm AI với lãnh tụ; bản đồ có Hoàng Sa, Trường Sa, "Biển Đông"; không cờ chính quyền Sài Gòn; không thù hằn; không nêu Trung Quốc trừ khi người dùng yêu cầu (cổ trung đại dùng tên triều đại). Ngoài ra:
1. **Tiêu đề và ảnh bìa không có chữ máu me hoặc "không che".** Nói kết quả quân sự và nghịch lý, không nói vết thương.
2. **Lời đọc kể con số thương vong có nguồn, không tả thương tích.** Một câu nêu sự việc là đủ.
3. **Hình:** thi thể phải che hoặc làm mờ hẳn, hoặc không dùng; không cận cảnh vết thương; 7 giây đầu và ảnh bìa không có cảnh ghê.
4. **Phim tư liệu thô dài quá 10 giây phải có lời kể, bản đồ hoặc chữ đè lên.** (Đây là luật của kit, YouTube không nêu con số; tư liệu hạng B vẫn theo `CLAUDE.md` là 3–5 giây.) Mỗi tập phải có câu hỏi trung tâm, nhân vật, chương riêng, để không thành "nội dung khuôn mẫu".
5. **Biểu tượng Quốc xã, cực đoan** chỉ xuất hiện trong phim tư liệu có lời kể đi kèm. Không đặt làm trọng tâm ảnh bìa, không làm logo, không phóng to.
6. **Chiến sự đang diễn ra** (Ukraine, Gaza…) không làm đề tài.
7. **Lời trích của người thật.** Lãnh tụ Việt Nam: chỉ hiện nguyên văn bằng chữ kèm nguồn, tuyệt đối không giả giọng, không đọc lại bằng giọng tổng hợp. Người khác (sĩ quan nước ngoài, chiến sĩ, nhân chứng, nhà thơ…): được dựng lại bằng giọng người dẫn hoặc giọng tổng hợp khi ghi rõ «mô phỏng lại» trên hình và ghi "trích" cùng nguồn; không nhái giọng thật của người đó; khi đăng, khai «nội dung tổng hợp» (AI use) trong YouTube Studio nếu giọng hay hình trông như thật.

## C. Khối luật dán vào mọi prompt viết chữ (kịch bản, tiêu đề, mô tả, chữ trên hình)

Chép nguyên khối dưới đây vào prompt giao cho sub-agent viết và cho người phản biện:

```text
BỘ LỌC CHÍNH SÁCH YOUTUBE: BẮT BUỘC (kênh của bạn, danh tính ở ho-so-kenh/ho-so.md; kênh tài liệu lịch sử, quân sự)
Mục tiêu: video đủ điều kiện quảng cáo đầy đủ (biểu tượng xanh). Vi phạm bất kỳ dòng nào dưới đây thì viết lại.
1. Không chửi tục, kể cả từ nhẹ, kể cả viết tắt hoặc che chữ (đm, vl, "C.H.Ế.T"…).
2. Không từ miệt thị dân tộc, vùng miền, phe phái (khựa, chệt, ba tàu, nhật lùn, mọi rợ, gook, parky, 3 que, bò đỏ, dư luận viên…). Không "thằng/bọn/lũ" đi với tên một dân tộc. Dùng "thực dân Pháp", "quân viễn chinh", "quân xâm lược", không dùng "bọn Tây".
3. Hệ từ: "kháng chiến chống Mỹ, cứu nước"; "chính quyền Sài Gòn", "quân đội Sài Gòn". "Ngụy", "Việt cộng", "VNCH" chỉ được nằm trong câu trích có nguồn. Không viết "Chiến tranh Việt Nam" trong lời, tiêu đề, mô tả (chỉ được trong thẻ). Không nêu "Trung Quốc"; thời cổ trung đại gọi tên triều đại (Nam Hán, Tống, Nguyên Mông, Minh, Thanh).
4. Bạo lực: kể kết quả, con số có nguồn, ý nghĩa quân sự. KHÔNG tả vết thương, máu, xác, cách giết, cảnh hành quyết. Thảm kịch nêu trong 1 câu trung tính có nguồn, không khai thác cảm xúc ghê rợn.
5. Tiêu đề, chữ ảnh bìa, 2 dòng đầu mô tả: cấm các chữ máu me, đẫm máu, chặt đầu, xác chết, thi thể, tàn sát, thảm sát, kinh hoàng, rùng rợn, "không che", "không kiểm duyệt", "uncensored", 18+. Cấm giật tít kiểu "tái mặt", "câm nín", "sốc", "chấn động". Dùng câu hỏi "Vì sao…?", "Toàn cảnh…", nghịch lý, và PHẢI trả lời được trong phim.
6. Không nội dung tình dục; xâm hại tình dục, tự sát chỉ được nhắc một câu, không mô tả.
7. Quốc xã, Khmer Đỏ, IS…: kể trung tính có ngữ cảnh, không khen, không tôn vinh, không trích khẩu hiệu tuyên truyền mà không có lời bình.
8. Vũ khí: được giải thích vai trò, cấu tạo, cách dùng trong trận; cấm hướng dẫn chế tạo, độ chế, chế bom, chất nổ.
9. Không phủ nhận thảm kịch; không đề tài chiến sự đang diễn ra; không dùng từ khoá thời sự để kéo view.
10. Người dẫn kể ngôi thứ ba, không xưng là nhà sử học, chuyên gia; lời trích ghi rõ ai nói, nguồn. Lời của lãnh tụ Việt Nam chỉ hiện bằng chữ nguyên văn kèm nguồn, không đọc thành tiếng. Lời của người khác được dựng lại thì ghi rõ «mô phỏng lại», không nhái giọng thật.
11. Mỗi tập phải có câu hỏi trung tâm, chương và chi tiết riêng; không dùng đoạn văn mẫu lặp giữa các tập (chính sách "nội dung không chân thực").
Cuối bài, tự liệt kê: (a) mọi chỗ có từ thuộc dòng 2–5 và lý do giữ lại (chỉ được giữ khi là câu trích có nguồn); (b) xác nhận tiêu đề, bìa sạch theo dòng 5.
```

## D. Cách kiểm (máy kiểm trước, người kiểm sau)
1. **Máy quét** sau khi có kịch bản, trước khi làm giọng (bước tốn tiền):
   ```
   python -I tools/loc-chinh-sach/quet.py tap/<slug>/ke-hoach/kich-ban-vN.md
   python -I tools/loc-chinh-sach/quet.py --tieu-de tap/<slug>/Final/<postpack>.md
   ```
   Phụ đề `.srt`: câu bắt đầu trong 30 s đầu tự xét gắt như tiêu đề. Đây là bộ lọc duy nhất của kit: từ điển chính sách YouTube nằm ở nhóm `yt_*` trong `tu-cam.tsv`, không cần chạy bản nào khác; `--vi-tri metadata` dùng được như `--tieu-de`. Máy quét nhận đường dẫn tệp (`-h` hoặc `--help` in cách dùng): muốn quét tên kênh, mô tả kênh, tagline thì ghi chúng ra một tệp tạm rồi quét tệp đó.
   Mã thoát 1 (có lỗi CHẶN) thì sửa xong mới đi tiếp. Mỗi CẢNH BÁO phải có người xem ngữ cảnh: giữ lại thì ghi lý do vào `checks.md` của tập.
2. **Người duyệt** (Claude rà sổ số liệu, người phản biện khác rà chéo) soi thêm những thứ máy không thấy: hình 7 giây đầu, ảnh bìa, thi thể đã che chưa, đoạn tư liệu thô dài, tiêu đề có hứa quá nội dung không.
3. **Lúc tải lên:** trả lời bảng tự đánh giá của YouTube **trung thực**. Khai đúng giúp kênh được tin, khai sai làm hỏng điểm tin cậy. Mục "AI use" chọn "Có" nếu có cảnh giả lập trông như thật.
4. **Sau khi đăng:** nếu video bị vàng thì xem mục nào bị gắn, sửa rồi **gửi yêu cầu người xét lại**. Ghi bài học vào danh sách từ, kèm bằng chứng.

Test của bộ lọc: `python -m pytest tools/loc-chinh-sach -q -p no:cacheprovider`. Thêm hoặc sửa mẫu thì thêm ca test.

## Nguồn (đọc ngày 01/11/2026)
- [Advertiser-friendly content guidelines](https://support.google.com/youtube/answer/6162278)
- [YouTube channel monetization policies: nội dung không chân thực, nội dung dùng lại](https://support.google.com/youtube/answer/1311392)
- [Disclosing altered or synthetic content](https://support.google.com/youtube/answer/14328491)
- [Violent or graphic content policy](https://support.google.com/youtube/answer/2802008)
- [Violent extremist or criminal organizations policy](https://support.google.com/youtube/answer/9229472)
- Thay đổi về chửi tục ở 7 giây đầu, 07/2025: [Engadget](https://www.engadget.com/apps/youtube-will-no-longer-limit-ads-on-videos-that-drop-the-f-bomb-early-124519205.html), [PPC Land](https://ppc.land/youtube-removes-strong-profanity-restrictions-from-first-7-seconds/)
