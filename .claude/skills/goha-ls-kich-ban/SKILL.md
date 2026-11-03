---
name: goha-ls-kich-ban
description: P2 Kịch bản của quy trình sản xuất phim tài liệu lịch sử, quân sự (kit Goha Lịch Sử) — giao sub-agent Sonnet viết lời từ kịch bản khung và sổ số liệu, chạy cổng bộ lọc chính sách YouTube và cổng chống trùng đối thủ, Agy phản biện trong thư mục cách ly, Claude rà sổ và sửa, rồi DỪNG chờ user duyệt. Dùng ngay khi user nói "P2", "viết kịch bản", "viết lời đọc", "chống trùng", "so trùng đối thủ", "phản biện kịch bản", hoặc khi tập đã có `so-so-lieu.csv` từ P1 mà chưa có `kich-ban-v*.md` — kể cả khi user không nhắc tên skill. Không dùng để tra nguồn (goha-ls-nghien-cuu) hay làm giọng (goha-ls-giong).
---

# P2 Kịch bản (Goha Lịch Sử)

Đường dẫn dạng `<output>`, `<nghien_cuu>`, `<vst_python>`, `<chep_loi>` là khoá trong `cau-hinh.toml` ở gốc repo (mẫu: `cau-hinh.mau.toml`; script đọc bằng `tools/cau_hinh.py`). Đường dẫn khác tính từ gốc repo.

Danh tính kênh (tên, ngôn ngữ, khán giả, độ dài tập, giọng, Model Link) lấy từ `ho-so-kenh/ho-so.md`; luật nhạy cảm riêng của ngách từ `ho-so-kenh/luat-noi-dung.md`. Ví dụ mang nhãn «tập mẫu EP001» (Điện Biên Phủ 1954) chỉ để minh hoạ số đo, không phải luật.

Đầu ra: `tap/<slug>/ke-hoach/kich-ban-vN.md` (lời có mã sổ sau mỗi câu dữ kiện, dòng `Hình:`, `Chữ trên hình:`) và `loi-doc-vN.txt` (lời thuần, số viết bằng chữ, mỗi câu một dòng, số tiếng = độ dài tập trong `ho-so.md` × tốc độ giọng bên dưới; tập mẫu EP001: **3.400–3.700 tiếng** cho phim 15–16 phút). Kết thúc bằng **DỪNG, user duyệt**; không làm giọng (bước tốn tiền) trước khi user gật.

**Tốc độ giọng thật:** đo trên giọng của kênh (`ho-so.md` mục Giọng), không đoán. Ví dụ tập mẫu EP001: giọng ElevenLabs `eleven_v4` thẻ `[fast-paced]` đọc **242 tiếng/phút**; lần đầu viết theo 170 tiếng/phút (tốc độ của một giọng chậm hơn) được 2.582 tiếng tưởng 16 phút, thực ra 11 phút. Giọng khác (VieNeu, Kokoro, giọng tiếng Anh) thì đọc một đoạn mẫu 1 phút để lấy tốc độ rồi mới đặt số tiếng.

**Luật của kit (áp cho mọi kênh dùng kit):** bước 1 là **Shu**: viết theo `kenh/hoc-shu/so-tay-van-phong.md` do chính kênh rút ra từ video triệu view của các kênh top 20 và Model Link của mình: khuôn mở 90 s, giữa phim, kết, văn phong. Kit không kèm kho Shu của kênh khác. Tệp này KHÔNG do K2 tạo; nó là sản phẩm của bước «Chưa có sổ tay văn phong thì chạy Shu trước» ngay dưới, chạy một lần cho cả kênh ở tập đầu. Phản biện thật kỹ (hai người phản biện độc lập, vai biên tập viên khó tính, ít nhất hai vòng), hook phải hấp dẫn (chấm điểm), chất lượng ngang phim đài.

Vì sao nhiều lớp kiểm: kênh có thể mất kiếm tiền cả kênh nếu bị coi là "nội dung dùng lại" hoặc "không chân thực", và mất uy tín nếu sai một con số. Người viết giỏi văn nhưng hay chép câu trích báo vào lời, hay thêm chi tiết không có trong sổ; người phản biện bắt được lỗi sử nhưng cũng báo nhầm. Mỗi lớp bắt một loại lỗi khác nhau.

Đọc trước: `CLAUDE.md` (luật cứng), `ho-so-kenh/ho-so.md`, `ho-so-kenh/luat-noi-dung.md`, `kenh/lich-noi-dung.md` (khung giữ chân, cấu trúc S1–S5 của tập; do K2 tạo từ khuôn, thiếu thì quay lại `goha-ho-so-kenh` bước 10), `kenh/bo-loc-chinh-sach-yt.md` mục C, `tap/<slug>/ke-hoach/kich-ban-khung.md`, `so-so-lieu.csv`, `checks.md` phần P1.

## Chưa có sổ tay văn phong thì chạy Shu trước
Điều kiện chạy: chưa có `kenh/hoc-shu/so-tay-van-phong.md`. Làm một lần cho cả kênh, mất khoảng vài giờ chủ yếu là tải phụ đề; báo người dùng trước khi bắt đầu.
1. **Chọn mẫu:** ghi vào `kenh/hoc-shu/ds-video.tsv` (cột `id`, `kenh`, `tieu_de`, `view`, `nhom`) khoảng 10 video hàng đầu của Model Link và 30–50 video có hệ số vượt trội cao của các kênh top 20 khác, lấy từ tab «5. Kho video vượt trội» và «12. Video top 20 %» của sheet top 20.
2. **Tải phụ đề** (miễn phí, tuần tự, không cookie), từng video: `yt-dlp --ignore-config --skip-download --write-subs --write-auto-subs --sub-langs "<mã ngôn ngữ ngách>.*" --convert-subs srt --sleep-requests 1 -o "<nghien_cuu>/<ngách>-<ngày>/phu-de/%(id)s.%(ext)s" <link video>`; nghỉ 3 giây giữa các video. Video không có phụ đề thì bỏ qua; chỉ khi thiếu quá nửa mẫu mới chép lời bằng `kit.py chep-loi` (bước trả phí, báo chi phí trước; mức Miễn phí dùng `--adapter whisper`).
3. **Đo bằng sub-agent Sonnet** (chỉ đọc phụ đề, KHÔNG viết lời): mỗi video đo giây xuất hiện câu hỏi trung tâm, cách mở 90 giây, tần suất câu hỏi tu từ, lời trích, câu «Nhưng», độ dài câu trung vị, cách kết, ghi thêm cột vào `ds-video.tsv`; rồi tổng hợp thành `kenh/hoc-shu/so-tay-van-phong.md` theo khuôn `.claude/skills/goha-ho-so-kenh/references/khuon-kenh/so-tay-van-phong.md`, mỗi con số kèm n/N.
4. **Claude kiểm:** đọc lại phụ đề của 3 video ngẫu nhiên và đối chiếu 3 con số của sổ tay; sai thì sửa. Trình người dùng tóm tắt sổ tay trong báo cáo P2 (không thêm cổng DỪNG).
5. Phụ đề thô ở `<nghien_cuu>`, không commit; dùng chúng làm kho so trùng ở bước 3 của P2 (`trung-lap.py`). Shu chép cách viết, không chép câu.

## Các bước
Ghi giờ vào `progress.md` (giờ máy thật).

1. **Chốt cấu trúc trước khi giao.** Soát kịch bản khung có tự mâu thuẫn không (ví dụ tập mẫu EP001: lời hứa "hai của Pháp, một của ta" trái với tên chương; đã sửa thành "một của Pháp, hai của ta"). Lấy danh sách góc đối thủ đã dùng từ tiêu đề video cùng đề tài (bảng video vượt trội trong sheet top 20 của kênh), chỉ đưa **tên góc** cho người viết, không đưa câu chữ.
2. **Viết brief** `ke-hoach/brief-viet-p2.md` theo `references/brief-nguoi-viet.md`, chép khối luật mục C nguyên văn, rồi máy xác nhận: `python -I -c` so khối trong brief với khối trong `bo-loc-chinh-sach-yt.md` (phải `True`). Giao sub-agent **Sonnet**, prompt = toàn văn brief. Mất khoảng 8 phút. *Không có sub-agent* (Miễn phí): chính Claude viết theo brief, rồi phản biện bằng sub-agent Opus ngữ cảnh mới như bước 6.
3. **Tự chạy ba cổng máy**, không tin báo cáo của người viết:
   - `python -I tools/loc-chinh-sach/quet.py <kich-ban> <loi-doc>` → 0 CHẶN.
   - Đếm tiếng `loi-doc` → trong khoảng độ dài tập × tốc độ giọng đã đo (tập mẫu EP001: 3.400–3.700).
   - `python -I tools/loc-chinh-sach/trung-lap.py <loi-doc> "<kho phụ đề đối thủ cùng đề tài>" "<kho phụ đề kênh Model Link, trong <nghien_cuu>>" <lời đọc các tập đã làm của kênh> <lời đọc tập mẫu trong mau/>` → ≤ 1 % và 0 câu ≥ 10 tiếng.
4. **Đọc từng cụm trùng** máy in ra và phân loại:
   - Chữ chính thống (câu trích có ngoặc trong nguồn, chức danh, tên văn kiện, khẩu hiệu, người nhận văn kiện) → thêm vào `tools/loc-chinh-sach/cum-chinh-thong.txt` kèm dòng ghi ngày, tập.
   - Cách viết (cụm sáo, câu chép gần nguyên văn câu trích của báo) → **viết lại**, không nới cổng.
   - Sau khi sửa, chạy lại với danh sách cụm cũ (`--cum-chinh-thong <bản cũ>`) để chứng minh phần viết lại tự qua cổng; ghi cả hai số vào `checks.md`.
5. **Claude rà sổ** từng câu có mã: đúng `gia_tri`/`cach_noi`; không chi tiết ngoài sổ; không mâu thuẫn giữa các câu; trục thời gian không đảo. Soi chữ thô (`<output>/<tập>/nguon-tho/`) khi một câu trích có người nói chưa rõ.
6. **Agy phản biện** (nạp skill `dieu-phoi-cli` trước; *không có Agy/Codex* thì giao sub-agent Opus ngữ cảnh mới, cùng brief, thư mục cách ly riêng; cùng hãng nên chạy thêm vòng hai để bù góc nhìn): tạo thư mục rỗng mới `<output>/<yymmdd>-<slug>/phan-bien-p2/`, chép vào đó **chỉ** kịch bản, sổ, brief (`references/brief-agy.md` + khối luật C); chạy
   `agy -p "$(cat brief-agy.md)" --model gemini-4-argon-high --sandbox --print-timeout 900s > agy-phan-bien.txt` (chạy nền, khoảng 5 phút). Không dùng `--dangerously-skip-permissions`.
7. **Lọc phản biện bằng bằng chứng**: nhận lỗi có dẫn chứng sổ hoặc nguồn; bác bỏ lỗi mà số đo hoặc sổ chứng minh sai (ví dụ tập mẫu EP001: Agy đếm tiếng trên kịch bản ghi số bằng chữ số nên báo "hụt nửa thời lượng" — sai). Ghi cả phần nhận và phần bác kèm lý do vào `checks.md`. Lưu bản phản biện vào `ke-hoach/agy-phan-bien-vN.md`.
8. **Sửa bằng script có assert** (`<output>/<tập>/sua-vN.py`): mỗi cặp (kịch bản cũ → mới, lời đọc cũ → mới) phải khớp đúng một lần, để hai file không lệch nhau. Đoạn cần xếp lại thì thay nguyên khối.
9. **Kiểm cuối** trên bản trình duyệt: ba cổng máy; mọi mã sổ tồn tại và không phải KHÔNG DÙNG; lời lãnh tụ không có trong `loi-doc`; không chữ cấm của tập (vd số đã loại ở P1); đo vị trí phần trăm của câu hỏi trung tâm (≤ 45 s), lời hứa, từng chương, cao trào (55–70 %) trên `loi-doc`, ghi mốc thật vào tiêu đề các phần.
10. **Ghi `checks.md` mục P2**, giờ vào `progress.md`, rồi **DỪNG**: báo user bản trình duyệt, kết quả cổng, những gì đã đổi so với khung, câu hỏi còn mở.

## Luật nội dung hay vấp
- Lãnh tụ Việt Nam (Chủ tịch Hồ Chí Minh, Đại tướng Võ Nguyên Giáp…): cấm mọi AI (giả giọng, đọc lại, ảnh/video AI, sửa ảnh). Lời họ chỉ hiện `[CHỮ TRÊN HÌNH: "…" · nguồn]`; lời đọc dẫn vào rồi để khoảng lặng ~4 s (dòng trống trong `loi-doc`). Ảnh lãnh tụ chỉ ảnh thật, cắt khung vuông vắn rồi đóng khung trang trọng; không tách nền, không sửa mặt, không chế ảnh (user chốt 03/11/2026).
- Lời người khác (sĩ quan Pháp, Mỹ, chiến sĩ, nhân chứng, nhà thơ…): giọng dựng lại được, nhưng phải ghi rõ trên hình «mô phỏng lại», không nhái giọng thật; nói rõ ai nói và nguồn (user chốt 03/11/2026). Đánh dấu ngay dòng `Chữ trên hình:` tương ứng trong kịch bản để P3, P5 không sót.
- Hy sinh: một hai câu nêu việc làm, không tả thương tích.
- Số liệu lệch nguồn → nói theo `cach_noi`; người viết hay lấy chi tiết từ cột trích hoặc ghi chú thay vì `gia_tri`, cần soát.
- Đặt tên phe rõ ràng ở câu then chốt, không gộp cả dân tộc (ví dụ tập mẫu EP001: "quân viễn chinh", "Bộ chỉ huy Pháp", "thực dân Pháp"; không cần thay mọi chữ "Pháp"). Luật phân biệt này theo `luat-noi-dung.md` của ngách.
- Bản đồ trong kịch bản, mô tả hình: mọi bản đồ có Việt Nam (kể cả kênh ngách khác) phải có Hoàng Sa, Trường Sa, ghi «Biển Đông», không đường lưỡi bò, không cờ chính quyền Sài Gòn.
- Năm đọc bằng chữ rất dài (tiếng Việt: "một nghìn chín trăm năm mươi tư" = 7 tiếng): ở phần mở chỉ đọc năm một lần để kịp mốc 45 giây.

## Hook và phản biện kép (thêm sau tập mẫu EP001)
1. **Hook:** giao người viết 4 phương án phần Mở, mỗi phương án một cơ chế (M1 giấu thông tin, M2 kết quả trước, M3 lật kỳ vọng, M4 khán giả biết trước, M5 áp lực), có đo tiếng và chỉ ra chỗ gặt (mẫu: brief hook của tập mẫu EP001 trong `mau/`, nếu kit có). Hai người phản biện chấm cả phần Mở hiện tại theo 7 tiêu chí /35 (câu hỏi trong 10 s, dẫn vào câu hỏi trung tâm, dựng được, gặt đúng, đúng sổ, giọng QPVN, khác góc đối thủ); dưới 30 thì người phản biện viết lại phần Mở. Ví dụ tập mẫu EP001: mở thắng là **một cảnh có ngày + một con số vật lý gây lệch** (9/4/1954: thả 195 tấn, thu 6 tấn), câu hỏi trung tâm **đúng chữ tiêu đề B**; mở bằng tên nguồn ("Theo TTXVN…") bị chấm thấp.
2. **Phản biện kép mỗi vòng:** Agy (`--sandbox`, thư mục cách ly) + sub-agent Opus ngữ cảnh mới (thư mục cách ly riêng, cùng brief `references/brief-agy.md`). Thiếu Agy thì hai sub-agent Opus độc lập, mỗi vòng một bản. Hai bên bắt lỗi khác nhau (Opus bắt lỗi nhân quả và chữ "Nhưng" đặt sai sau lời lãnh tụ; Agy bắt lỗi trộn nguồn, giật lùi thời gian). Mỗi vòng sửa lại sinh lỗi mới (ví dụ: số sân bay "một" thay "hai"), nên vòng hai là bắt buộc.
3. **Biên tập bằng danh sách quyết định:** Claude lọc phản biện thành danh sách đã chốt có mã sổ (mẫu: danh sách quyết định biên tập của tập mẫu EP001, nếu kit có), giao một người biên tập; tự chạy lại ba cổng.

## Mốc đo (tập mẫu EP001, 01/11/2026)
P2 đến cổng duyệt v3: 23 phút. Sau khi user duyệt, P2b–P2c (hook, học Shu, mở rộng sổ, v4, v5, hai vòng phản biện): khoảng 4 giờ, trong đó tải và phân tích khoảng 190 video mẫu khoảng 2,5 giờ (làm một lần cho cả kênh). Cổng chống trùng: v1 1,73 % và 2 câu (KHÔNG ĐẠT) → v3 0,18 % → v4 0,85 % lần đầu, sửa 7 câu còn 0,36 % → v5 0,65 % (1 câu công thức lãnh đạo, thêm vào cụm chính thống). Bộ so dùng thêm kho phụ đề Shu của kênh (`kenh/hoc-shu/`, người viết đã học khuôn từ đó). Hiệu chỉnh máy so trùng: kênh tự viết 0,45–1,04 %, kênh nghi chép khoảng 9 %, nên ngưỡng 1 % là hợp lý.

## Sổ cách nói đã chốt (chặn tái phạm, 02/11/2026)
- Mỗi lần user sửa một cách nói (xưng hô, từ, câu), ghi ngay một dòng vào `kenh/cach-noi-da-chot.tsv` (mã, regex cấm, cách đúng, lý do, nguồn) trước khi làm tiếp. Không chỉ ghi ở `checks.md` của một tập: tập 1 v3 tái phạm «anh hy sinh» vì sửa ở Demo v11 chỉ nằm trong checks Demo.
- Cổng: `python -I tools/lichsu/kiem-da-chot.py <lời đọc> <kịch bản> <phân cảnh>` phải 0 chỗ phạm; `dung-duong-giong.py` tự gọi và dừng nếu phạm.
- Viết lại, rút gọn hay phục hồi một cảnh: lấy lời từ bản đã duyệt gần nhất (Demo, bản user đã nghe), không viết lại từ bản nháp cũ.
