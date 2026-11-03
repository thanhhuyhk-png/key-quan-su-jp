---
name: tu-duy-top-20-ytb
description: "Tư duy Top 20 YouTube: chọn đúng 20 kênh hình mẫu và 1 Model Link để bám sát bằng số liệu đo chuẩn hoá, phản biện từng chi tiết, xuất Google Sheet nhiều tab (TOP 20, TOP 20 kèm video top, báo cáo thăng hạng 30 ngày, khảo sát kênh, kho video vượt trội, đối chứng, nhân bản đề tài, theo dõi định kỳ). DÙNG NGAY khi user nói: top 20, tư duy top 20, tìm kênh mẫu/hình mẫu/model link, nghiên cứu đối thủ YouTube/TikTok/Facebook, học trọn kênh, chọn ngách, kênh nào đang lên, video vượt trội/outlier, bảng theo dõi kênh, báo cáo thăng hạng, phân tích kênh trước khi mở kênh mới — kể cả khi user không nhắc tên skill. Không dùng cho viết kịch bản hay dựng video."
---

# Tư duy Top 20 YouTube

**Lựa chọn hơn nỗ lực.** Chọn sai kênh mẫu thì cả quy trình làm đúng vẫn mất tiền và thời gian. Một con số sai đơn vị, một bảng chấm bằng cảm tính, một nhóm tuổi bị trộn đã từng làm hỏng kết luận thật (`references/bay-so-lieu.md`). Skill này tồn tại để không lặp lại các lỗi đó.

Nguồn phương pháp: tổng hợp và thử nghiệm trên kênh mẫu (nhiều vòng chạy thật, nhiều vòng phản biện độc lập). Mọi công thức nằm trong mã và trong `references/`, không cần tài liệu ngoài.

## Ba luật thép
1. **Số trước, cảm sau.** Xếp hạng chỉ bằng chỉ số đo được, có cả **đà hiện tại** (tăng 30 ngày, đà trung vị) chứ không chỉ số tích luỹ. Điểm chấm tay chỉ để lọc. Mỗi con số có nguồn, ngày đo, cỡ mẫu n.
2. **Mỗi kết luận một nhãn**: [ĐO], [SUY LUẬN], [CHƯA CÓ] (ghi cách lấp), [CHÍNH THỨC]. Kết luận về khán giả chỉ là kết luận về **mẫu bình luận**; kết luận từ đối chứng chỉ là **giả thuyết**.
3. **Không chốt khi chưa phản biện.** Trước khi đưa TOP 20 và Model Link cho người dùng, chạy pha 7, gồm câu bắt buộc: «Kênh nào ít video mà sub nhiều, video dài, view tốt? Nó có ở hạng 1 không? Nếu không thì vì sao (bằng số)?»

## Nguồn dữ liệu theo mức chạy
- **Nhánh miễn phí (mặc định), không cần khoá API nào:** `yt-dlp` cho danh sách video, view, like, bình luận, ảnh bìa, heatmap và cả số sub (trường `channel_follower_count`; lệnh ở `references/nguon-du-lieu.md` mục «Lấy số sub bằng yt-dlp»). Tổng video và ngày video đầu đã nằm sẵn trong `<khoá>.meta.json` do `thu_video.py` ghi. Ngày lập kênh (tuỳ chọn) đọc ở tab Giới thiệu của kênh. Nhánh này không đọc `.env`.
- **Tuỳ chọn trả phí:** vidIQ (điểm từ khoá, tăng sub 30 ngày có sẵn, video vượt trội theo ngách). Có thì nhanh hơn, không có vẫn đủ làm hết quy trình. Chỗ nào skill nhắc vidIQ đều có nhánh miễn phí tương đương ở `references/nguon-du-lieu.md`.
- **Nơi lưu dữ liệu thô:** thư mục khoá `nghien_cuu` trong `cau-hinh.toml` (không nằm trong repo). Lấy đường dẫn: `python -c "import sys; sys.path.insert(0,'tools'); from cau_hinh import duong; print(duong('nghien_cuu'))"` chạy ở gốc repo. Mỗi lần chạy đặt một thư mục con theo ngách và ngày, rồi truyền làm `--out-dir`.

## Quy trình 9 pha (0–8); chưa qua cổng thì không sang pha sau
**Thứ tự chạy:** 0 → 1 → 2 → lọc sơ bộ (5.1: hướng, nguồn lực, ràng buộc) → 3 đo (mọi kênh Giữ) → 4 gắn tuổi → 5.2–5.5 xếp trên tập Giữ, TOP, kho video → 6 → 7 → 8. Pha 3 không có cổng riêng (cổng dữ liệu nằm ở pha 2, cổng chọn ở pha 5).

### Pha 0 — Khung câu hỏi
Ghi rõ: khán giả mục tiêu (tuổi chính, phụ), định dạng làm được (hình, giọng, độ dài), nguồn lực (người, tiền, số video mỗi tuần) **kèm tiêu chí cụ thể để gắn nhãn «cùng nguồn lực»**, ràng buộc (đề tài cấm, nền tảng), thị trường (kênh nước ngoài để riêng). Ràng buộc áp lên **nội dung của mình**; với kênh mẫu chỉ loại khi **lõi** kênh vi phạm (`references/phan-bien.md` câu 12). Đọc `ho-so-kenh/ho-so.md` và `ho-so-kenh/luat-noi-dung.md` nếu đã có để lấy sẵn các mục này.
**Cổng:** thiếu mục nào thì hỏi người dùng.

### Pha 1 — Khảo sát rộng (~100 kênh)
Tìm theo 3 hướng: ngách chính, ngách lân cận cùng khán giả, ngách khác đề tài nhưng cùng cách kể. Công cụ: tìm bằng cụm tiêu đề của video thắng (`ytsearch`, `references/nguon-du-lieu.md` mục «Khám phá kênh bằng ytsearch»), vidIQ nếu có. Gắn mỗi kênh các nhóm **chồng lấp**: **mới < 12 tháng** (script tính từ ngày video đầu), **ổn định ≥ 2 năm**, **cùng nguồn lực** ([SUY LUẬN], theo tiêu chí pha 0; `references/tieu-chi-va-cong-thuc.md` mục 8).
**Cổng:** ≥ 60 kênh thật (mục tiêu 100) trong khảo sát (không phải TOP), mỗi nhóm ≥ 5; nhóm «mới» không trống.

### Pha 2 — Thu và làm sạch số liệu (cổng dữ liệu)
- Danh sách video: `python scripts/thu_video.py <kênh>… --out-dir <thư mục nghien_cuu/...>` (tuần tự, không cookie, có file PID, nghỉ giữa yêu cầu, khoảng 3 giây mỗi video; lỗi yt-dlp là lỗi, mã thoát khác 0; **lấy ≥ 100 video dài mới nhất** để hệ số có hàng xóm). **Tổng video và ngày video đầu lấy từ trang kênh, API hoặc meta**, không suy từ danh sách đã lấy.
- Số sub của kênh (cho `--subs`): lấy bằng `yt-dlp` theo `references/nguon-du-lieu.md` mục «Lấy số sub bằng yt-dlp», ghi vào bảng kênh.
- Đo: `python scripts/do_kenh.py kenh <ds.tsv> --subs N --meta <khoá>.meta.json [--tong-video T] [--ngay-video-dau D] [--cua-so-tu <ngày>] [--so-hoi-vien H] [--ty-trong-view-short 0..1] [--sub-30-ngay-truoc S] [--ngay-lap L] --json <kenh.json>`.
- Đọc dòng «Đọc n dòng; bỏ …» và cột **Cờ**; xử lý theo `references/bay-so-lieu.md` trước khi xếp hạng.
**Cổng:** 0 cờ NGHI_LOI_DON_VI hoặc DANH_SACH_CO_THE_BI_CAT chưa xử lý; kiểm tay ≥ 3 số ngẫu nhiên với một nguồn độc lập (trang video gốc, hoặc `yt-dlp --skip-download --print "%(view_count)s" <link video>`, hoặc vidIQ), lệch ≤ 3 %.

### Pha 3 — Đo
Chỉ số theo `references/tieu-chi-va-cong-thuc.md`: trung vị 20 video dài đủ tuổi (đây là lọc tuổi tối thiểu, **chưa phải chuẩn hoá tuổi**), trung vị ÷ sub, đà trung vị, % tăng sub 30 ngày (trần 100 % khi kênh < 90 ngày; bỏ khi nền < 5.000 sub, có chủ ý), sub mỗi video, sub mỗi ngày (từ video đầu và từ ngày lập), tỉ trọng view Shorts, hệ số vượt trội từng video (chỉ trong cửa sổ). Cờ TAI_SINH (ngày lập cách video đầu > 12 tháng), HOI_VIEN.

### Pha 4 — Gắn khán giả
Định dạng hình–giọng là giả thuyết tuổi ban đầu (bảng ở `references/do-tuoi-khan-gia.md`). Đo bằng bình luận tự khai và tín hiệu, ghi mức tin. Đo tuổi tốn công: với giới hạn thời gian hoặc credit, chỉ đo ứng viên Model Link và top 5, kênh còn lại ghi «chưa đo».
**Cổng mềm:** chỉ loại kênh vì tuổi khi bằng chứng mức **Vừa trở lên** cho thấy lệch khán giả mục tiêu; mức Thấp hoặc Chưa xác định thì giữ, ghi «cần kiểm», không rút luật chung từ kênh khác tuổi.

### Pha 5 — Lọc, xếp hạng, chọn TOP 20 và kho video
1. Lọc trước (Giữ / Loại / Theo dõi, lý do có số): hướng nội dung, khán giả (pha 4), nguồn lực, ràng buộc. Kênh loại vẫn ở tab Khảo sát.
2. **Xếp hạng chỉ trên tập Giữ** (phân vị bị méo nếu lẫn kênh bị loại): `python scripts/do_kenh.py xep-hang <bang-giu.tsv> --json <xep-hang.json> --do-nhay [--ghi-de "<kênh>:<CỜ>[:lý do]"]`. Đọc **khoảng hạng** (3 bộ tiêu chí), hạng theo ngày lập, và **«hạng 1 ở n/6 cách tính»**. Kênh «Không đủ chỉ số» không được xếp (thu thêm số). Kênh lai Shorts (SUB_LAN_SHORTS) bị bỏ 4 chỉ số dựa trên sub nên có thể thành «Không đủ chỉ số»: bình thường, không phải lỗi.
3. TOP 20 = 20 kênh hạng cao nhất. Không đủ 20 kênh đáng tin thì để TOP ít hơn, **không độn kênh yếu**.
4. Tách **hình mẫu kênh** khỏi **kho video**: kênh yếu có video hay thì đưa video vào kho, không đưa kênh vào TOP.
5. Mỗi kênh TOP 20: 5–10 video nhiều view nhất, cộng cửa sổ liên tục ≥ 100 video dài mới nhất (hệ số cần ≥ 5 video liền trước, tốt nhất 15). Video hệ số ≥ 3 vào kho vượt trội sau bước «kiểm tra số thật» (`references/tieu-chi-va-cong-thuc.md` mục 2).
**Cổng:** trả lời được câu bắt buộc của luật thép 3; mỗi kênh TOP có ≥ 5 video có link.

### Pha 6 — Học trọn TOP và chọn Model Link
- Học trọn **TOP 1 bắt buộc**, TOP 2–5 nên làm: `references/hoc-tron-kenh.md` (đối chứng **nhóm với nhóm** trên 6 biến kèm mốc đăng, 30–60 giây đầu, cấu trúc theo %, đỉnh phát lại bằng `scripts/heatmap.py`, ảnh bìa phải mở xem, bình luận theo nhóm).
- **Model Link** = kênh số 1 để bám sát: hạng cao **và vững** (top 5 ở cả 3 bộ tiêu chí **và hạng 1 ở ≥ 5/6 cách tính**; không thì trình ≥ 2 ứng viên kèm bảng so) **và** khớp khán giả mục tiêu **và** cách làm nằm trong nguồn lực **và** không vi phạm ràng buộc. Hai kênh chênh < 3 điểm hoặc khoảng hạng chồng nhau thì trình cả hai cho người dùng chọn. Ghi rõ: bám gì, không bám gì, theo dõi gì mỗi tuần, khi nào thôi bám.
**Cổng:** Model Link ở trạng thái «đề xuất» cho đến khi người dùng duyệt.

### Pha 7 — Phản biện
Checklist `references/phan-bien.md`. Mục E (người hoặc CLI phản biện độc lập, thư mục nháp, báo cáo không bí mật) do **phiên chính** chạy; sub-agent ghi «chờ phiên chính chạy mục E», không tự giao CLI ngoài. Không có CLI ngoài thì dùng một sub-agent ngữ cảnh mới. Ý bị bác phải có lý do có nguồn.
**Cổng:** mọi mục «cao» ở tab «Chú ý & phản biện» đã xử lý hoặc được người dùng chấp nhận.

### Pha 8 — Xuất Google Sheet và lịch đo lại
1. Gộp: `python scripts/gop_ho_so.py --do-kenh <thư mục> --video-dir <thư mục> --dinh-tinh <bảng định tính> --xep-hang <xep-hang.json> --out ho-so-top20.json` (cấu trúc ở `references/mau-google-sheet.md`). `kiem_tra_so` chuẩn: `chua_chin | so_bo | dat | nghi` (`dat` chỉ khi người đã đọc bình luận).
2. `python scripts/xuat_sheet.py ho-so-top20.json --out top20.xlsx --nghiem` xuất đủ các tab của script (tên ở mục «Bảng 14 tab» dưới); script tự kiểm (thiếu id, thiếu nguồn, cờ lỗi đơn vị trong TOP, Model Link ngoài TOP, kênh mới bị bỏ sót, TAI_SINH ở nhóm mới…) và ghi vào tab «Chú ý & phản biện»; `--nghiem` dừng khi có lỗi mức cao.
3. Thêm 2 tab bổ sung cho đủ 14 tab: `python scripts/them_tab.py top20.xlsx --dinh-tinh <bảng định tính .json> --video-dir <thư mục TSV video> --model <channel ID Model Link> --ngay-do <ngày đo> [--moi-noi <bảng kênh mới nổi .tsv>]`. Không có bảng kênh mới nổi thì tab 1b được bỏ qua (script báo rõ).
4. Tải lên Drive bằng tay là đủ: Drive → Mới → Tải tệp lên, mở file → Tệp → «Lưu dưới dạng Google Trang tính». Kiểm có đủ tab rồi lấy link. Không chia sẻ công khai khi chưa được yêu cầu.
5. **Lần đo đầu** chưa có thăng hay giáng (tab 3 ghi «Chưa có mốc trước», xếp theo % tăng sub). Tab 9 tự lưu ảnh chụp kỳ này cho mọi kênh Giữ và Theo dõi để kỳ sau (30 ngày) tính thăng hạng thật. Kênh rơi khỏi TOP hai kỳ liền thì thay.

## Bảng 14 tab (sheet mẫu của chủ kit: <điền: link Google Sheet top 20 mẫu>; mở chế độ xem rồi «Tạo bản sao». Chưa có link thì dùng XLSX do `xuat_sheet.py` sinh)
Tên thật, đúng thứ tự trong bảng mẫu:
`0. Tổng quan & Model Link` · `1. TOP 20` · `1b. Kênh mới nổi (làm theo)` · `2. TOP 20 + video top` · `3. Thăng hạng 30 ngày` · `4. Khảo sát kênh` · `5. Kho video vượt trội` · `6. Cặp đối chứng` · `7. Nhân bản đề tài` · `8. Bám sát Model Link` · `9. Theo dõi định kỳ` · `10. Chú ý & phản biện` · `11. Từ điển cột` · `12. Video top 20 %`.
`xuat_sheet.py` sinh 12 tab (số 0 đến 11). Hai tab `1b` (kênh dưới 400 ngày tuổi xếp theo trung vị video dài đủ 7 ngày, để «làm theo kênh nhỏ») và `12` (20 % video dài nhiều view nhất của mỗi kênh Giữ hoặc Theo dõi, tối thiểu 3 video) do `scripts/them_tab.py` thêm (pha 8 bước 3); chi tiết ở `references/mau-google-sheet.md`.

## Đầu ra cho K2
Khi người dùng duyệt xong pha 6–7, bàn giao ba thứ cho skill `goha-ho-so-kenh` (bước K2 ghi vào `ho-so-kenh/ho-so.md`):
1. **Ngách đã duyệt**: tên ngách, khán giả mục tiêu và mức tin, định dạng, độ dài tập, ràng buộc nội dung.
2. **Model Link**: kênh, link, ba con số đo (hạng, khoảng hạng, «hạng 1 ở n/6 cách»), bám gì, không bám gì, theo dõi gì mỗi tuần, khi nào thôi bám.
3. **Link Google Sheet** (bản sao của hội viên) và ngày đo.
Không ghi gì vào `ho-so-kenh/` trực tiếp; chuyển qua `goha-ho-so-kenh` để đúng hợp đồng tệp.

## Báo cáo trong chat
Mở bằng kết luận: Model Link đề xuất (kèm 3 con số, khoảng hạng và «hạng 1 ở n/6 cách»), TOP 5, kênh bị chấm sai trước đây (nếu có), link Google Sheet. Rồi cảnh báo mức cao, chi phí đã dùng (credit, phút), câu hỏi cho người dùng. Câu đầy đủ, không viết tắt khó hiểu.

## Tham chiếu
- `references/bay-so-lieu.md` — sai sót đã gặp, dấu hiệu, cách bắt. **Đọc trước pha 2.**
- `references/tieu-chi-va-cong-thuc.md` — công thức, ngưỡng, độ nhạy, lịch sử phiên bản, nhóm kênh.
- `references/do-tuoi-khan-gia.md` — đo tuổi qua bình luận.
- `references/hoc-tron-kenh.md` — học trọn một kênh.
- `references/phan-bien.md` — checklist phản biện.
- `references/nguon-du-lieu.md` — hợp đồng dữ liệu, thu video, ytsearch, chạy nền, chi phí, chỗ lưu.
- `references/mau-google-sheet.md` — các tab, cấu trúc JSON, gộp hồ sơ.
- `scripts/thu_video.py`, `scripts/do_kenh.py`, `scripts/gop_ho_so.py`, `scripts/heatmap.py`, `scripts/xuat_sheet.py` — test: `cd scripts && python -m pytest -q tests` (cần `pip install openpyxl pytest`).
