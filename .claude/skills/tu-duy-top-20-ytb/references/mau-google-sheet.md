# Mẫu Google Sheet 14 tab và cấu trúc JSON hồ sơ

Bảng mẫu của chủ kit có 14 tab (link: <điền: link Google Sheet top 20 mẫu, chế độ xem>). Hội viên mở link rồi bấm «Tệp → Tạo bản sao» để có bản riêng; nếu chủ kit chưa gửi link thì bỏ qua bảng mẫu, dùng tệp XLSX do `xuat_sheet.py` sinh ra làm bảng của mình; số liệu trong bản mẫu là số đo của ngách mẫu, chỉ để tham khảo cách trình bày. Bảng đi theo cách làm quen thuộc: danh sách kênh với số follow ở hai mốc ngày và tăng trưởng 30 ngày, video triệu view gom theo kênh, bảng khảo sát rộng, tab chú ý quan trọng và tab nhân bản đề tài; skill thêm các cột đo chuẩn hoá, báo cáo thăng hạng và tab Model Link.

## Danh sách tab (đúng tên và thứ tự trong bảng mẫu)
| Tab | Nội dung | Nguồn |
|---|---|---|
| 0. Tổng quan & Model Link | Mục tiêu, ngày đo, số kênh khảo sát / giữ / TOP, Model Link và lý do, cảnh báo mức cao, chú giải màu | `xuat_sheet.py` |
| 1. TOP 20 | 20 kênh hạng cao nhất sau lọc: số follow hai mốc, tăng 30 ngày, chỉ số đo, điểm, hạng, thăng/giáng, cờ, học gì / không học, chú ý, nguồn | `xuat_sheet.py` |
| 1b. Kênh mới nổi (làm theo) | Kênh dưới 400 ngày tuổi (từ video đầu), xếp theo trung vị video dài đủ 7 ngày tuổi; dành cho kênh mới chưa đủ 20 video đủ 30 ngày nên «không đủ chỉ số» ở tab 1 | `them_tab.py` |
| 2. TOP 20 + video top | Mỗi kênh một dòng tiêu đề (★ vàng = Model Link), dưới là video nhiều view nhất: link, tiêu đề, view, view mỗi ngày, hệ số, đề tài, góc, tử huyệt, kiểu mở, ảnh bìa, đỉnh phát lại, yêu cầu bình luận | `xuat_sheet.py` |
| 3. Thăng hạng 30 ngày | Hạng nay so với kỳ trước, sub tăng, % tăng, view 30 ngày, video 30 ngày, Vào TOP mới / Rời TOP. Lần đo đầu: «Chưa có mốc trước», xếp theo % tăng sub; sub mốc trước = 0 hiện «mốc 0», chưa có sub kỳ trước hiện «chưa có mốc». `view_30_ngay` không có nguồn tự động (điền từ API hoặc vidIQ) | `xuat_sheet.py` |
| 4. Khảo sát kênh | Toàn bộ kênh khảo sát, cột Giữ/Loại (danh sách chọn) và lý do; kênh loại tô xám | `xuat_sheet.py` |
| 5. Kho video vượt trội | Mọi video hệ số ≥ 3, xếp theo hệ số | `xuat_sheet.py` |
| 6. Cặp đối chứng | Nhóm video vượt trội so với nhóm video thường cùng kênh, 6 biến, giả thuyết nguyên nhân | `xuat_sheet.py` |
| 7. Nhân bản đề tài | Giữ nhu cầu, đổi nhân vật / bối cảnh / góc / câu hỏi; 3 câu kiểm; 6 điểm cơ hội, tổng /30, kết luận | `xuat_sheet.py` |
| 8. Bám sát Model Link | Thẻ Model Link: chỉ số, vì sao TOP 1, bám gì, không bám gì, theo dõi hằng tuần, khi nào thôi bám | `xuat_sheet.py` |
| 9. Theo dõi định kỳ | Ảnh chụp kỳ này cho mọi kênh Giữ (kể cả kênh chưa xếp) và kênh Theo dõi: id, hạng, điểm, sub, sub/video, trung vị, trung vị ÷ sub, phiên bản công thức; nguồn cho báo cáo thăng hạng kỳ sau | `xuat_sheet.py` |
| 10. Chú ý & phản biện | Cờ dữ liệu, giới hạn, câu hỏi chưa trả lời, kết quả phản biện; mức «cao» tô đỏ | `xuat_sheet.py` |
| 11. Từ điển cột | Ý nghĩa và cách tính từng cột | `xuat_sheet.py` |
| 12. Video top 20 % | Mỗi kênh Giữ hoặc Theo dõi: 20 % video dài nhiều view nhất (tối thiểu 3 video), để thấy «cái gì thắng trong từng kênh» | `them_tab.py` |

`xuat_sheet.py` chỉ sinh 12 tab (số 0 đến 11). Hai tab «1b» và «12» là tab bổ sung do `scripts/them_tab.py` thêm vào tệp XLSX (cách gọi ở SKILL.md, pha 8 bước 3). Thiếu hai tab này thì phần còn lại vẫn đầy đủ.

## JSON hồ sơ (đầu vào của `xuat_sheet.py`)
```json
{
  "du_an": "Kênh <ngách> — <định dạng>",
  "ngay_do": "2026-10-22",
  "ngay_moc_truoc": "2026-09-22",
  "muc_tieu": {"khan_gia": "18–34 (phụ 35–50)", "dinh_dang": "2D, giọng nam, 9–25 phút",
               "nguon_luc": "1 người + AI, 1 video mỗi tuần", "rang_buoc": ["né chính trị"]},
  "model_link": {"kenh": "<id kênh>", "trang_thai": "đề xuất, chờ duyệt",
                 "ly_do": ["..."], "bam_gi": ["..."], "khong_bam": ["..."],
                 "theo_doi_hang_tuan": ["..."], "dung_bam_khi": ["..."]},
  "kenh": [{
    "id": "UC...", "ten": "...", "link": "https://www.youtube.com/@...", "nen_tang": "YouTube",
    "nhom": ["moi", "cung_nguon_luc"], "ngach": "...", "dinh_dang": "...",
    "tuoi_khan_gia": "16–34", "tuoi_muc_tin": "Vừa",
    "subs": 38000, "subs_30_ngay_truoc": 12000, "view_30_ngay": 3200000, "video_30_ngay": 8,
    "so_video": 22, "so_dai": 22, "so_short": 0, "ngay_video_dau": "2026-09-04", "tuoi_kenh_ngay": 48,
    "trung_vi_20_dai": 193670, "trung_vi_chia_sub": 5.1, "so_video_tren_2x": 2, "phan_tan": 4.2,
    "sub_moi_video": 1727, "sub_moi_ngay": 794, "diem": 92.2,
    "hang": 1, "hang_30_ngay_truoc": 5,
    "giu_loai": "Giữ | Loại | Theo dõi", "ly_do": "...", "co": "IT_VIDEO", "nhan_xet_thang_hang": "...",
    "da_trung_vi": 1.3, "khoang_hang": "1–2", "n_dai_dung_tinh": 20, "phien_ban": "2026-10-22.2",
    "hoc_gi": "...", "khong_hoc_gi": "...", "chu_y": "...", "nguon_so": "API + yt-dlp 22/10/2026"
  }],
  "video": [{
    "kenh": "UC...", "id": "...", "link": "https://youtu.be/...", "tieu_de": "...", "ngay_dang": "2026-09-13",
    "thoi_luong_s": 1258, "views": 809756, "view_moi_ngay": 20763, "trung_vi_15_truoc": 190000,
    "he_so": 4.2, "he_so_sau": 1.1, "muc": "dang_ghi", "la_top_view": true,
    "de_tai": "...", "goc_tiep_can": "...", "tu_huyet": "...", "kieu_mo": "...", "anh_bia": "...",
    "dinh_phat_lai": "12:40 · 61 %", "yeu_cau_binh_luan": "phần 2 (14)", "kiem_tra_so": "so_bo", "ghi_chu": ""
  }],
  "doi_chung": [{"kenh": "UC...", "video_hit": "5 id/tiêu đề", "video_thuong": "5 id/tiêu đề", "khac_chu_de": "...",
                 "khac_tieu_de": "...", "khac_anh_bia": "...", "khac_mo": "...", "khac_goc": "...",
                 "khac_do_dai": "...", "ket_luan": "giả thuyết ..."}],
  "nhan_ban": [{"video_goc": "...", "nhu_cau": "...", "doi_nhan_vat": "...", "doi_boi_canh": "...",
                "goc_nhin": "...", "cau_hoi_trung_tam": "...", "con_nhu_cau": "có", "du_tu_lieu": "có",
                "khac_ro": "có", "diem": {"nhu_cau": 5, "bang_chung": 4, "khoang_trong": 4,
                "hop_khan_gia": 4, "chi_phi": 3, "rui_ro": 4}, "quyet_dinh": "..."}],
  "theo_doi": [{"ngay": "2026-10-22", "kenh": "UC...", "subs": 38000, "view_tong": 4820000,
                "so_video": 22, "trung_vi_20_dai": 193670, "ghi_chu": ""}],
  "chu_y": [{"loai": "co_du_lieu | gioi_han | cau_hoi | phan_bien", "noi_dung": "...",
             "muc_do": "cao | vừa | thấp", "viec_can_lam": "..."}]
}
```
Trạng thái chuẩn của `kiem_tra_so`: `chua_chin` (video < 30 ngày) · `so_bo` (kiểm được like và bình luận bằng số, chưa đọc nội dung bình luận) · `dat` (người đã đọc bình luận và đối chiếu sự kiện, nguồn; **không bao giờ tự động**) · `nghi` (like < 0,5 % view, like > view, hoặc người nghi ngờ; lý do ở `ghi_chu`). Sheet hiển thị nhãn tiếng Việt và tô: `dat` xanh (hệ số ≥ 5), `so_bo` cam nhạt (hệ số ≥ 5), `chua_chin` xám (hệ số ≥ 5), `nghi` đỏ nhạt (mọi hệ số); chuỗi cũ bắt đầu bằng nguyên từ «đạt», «nghi»/«nghi ngờ», «sơ bộ», «chưa chín» vẫn nhận («loại» cũ = nghi); «nghiên cứu…», «đạtxx» không khớp. `nhom` là danh sách mã; chuỗi cũ và nhãn hiển thị vẫn nhận, cờ `moi` được script tính lại từ `ngay_video_dau` (lệch với nhãn tay thì ghi một dòng mức thấp ở tab Chú ý). `ghi_de` (từ `xep-hang --ghi-de`) mỗi mục `{co, ly_do}`.

Quy ước: script **luôn tính lại hạng** từ `diem` trong các kênh «Giữ» (hạng trong hồ sơ chỉ để đối chiếu). Nhận cả tên trường của `do_kenh.py` (`n_video`, `n_dai`, `n_short`, `tuoi_tu_video_dau`, `sub_moi_ngay_video_dau`, `sub_30_ngay_truoc`): cứ chép nguyên khối `chi_so` của `do_kenh.py --json` vào từng kênh rồi thêm phần định tính. `diem` và `khoang_hang` lấy từ `do_kenh.py xep-hang --json` chạy trên tập Giữ. Số để dạng số, không định dạng sẵn. `trung_vi_chia_sub` là tỉ lệ thập phân (0,3 = 30 %; ví dụ trên 5.1 = 510 %, tức trung vị view gấp 5 lần số sub). `hang_30_ngay_truoc` chỉ lấy từ tab Theo dõi kỳ trước **cùng phiên bản công thức**; lần đo đầu để trống (không ước hạng từ riêng số sub). `subs_30_ngay_truoc` lần đầu có thể ước từ % tăng 30 ngày của nguồn ngoài, ghi «ước» ở cột nguồn.

## Tải lên Google Drive
0. Chạy `xuat_sheet.py ... --nghiem`; xử lý mọi dòng «cao» in ra trước khi tải lên.
1. Tải file XLSX lên Drive bằng tay (Drive → Mới → Tải tệp lên). Mở file, chọn Tệp → «Lưu dưới dạng Google Trang tính» để có Google Sheet thật.
2. Đặt tên «TOP 20 — <dự án> — <ngày>». Kiểm có đủ tab, rồi lấy link. Lần đo sau: tạo bản mới có ngày trong tên (giữ lịch sử), hoặc cập nhật theo yêu cầu người dùng.
3. Muốn chia sẻ cho người khác: chế độ chỉ xem hoặc «tạo bản sao», không công khai khi chưa được yêu cầu.

## Gộp hồ sơ bằng `scripts/gop_ho_so.py`
`python scripts/gop_ho_so.py --do-kenh <thư mục do-kenh> --video-dir <thư mục TSV video> --dinh-tinh <dinh-tinh.json|kenh.tsv> --out ho-so-top20.json [--xep-hang xep-hang.json] [--as-of <ngày>]`
- `do-kenh/<id kênh>.json` = `do_kenh.py kenh --json`; `video-dir/<id kênh>.tsv` = `thu_video.py` (cùng id); `xep-hang.json` = `do_kenh.py xep-hang --json` (điểm, hạng, khoảng hạng, ghi đè).
- Bảng định tính (JSON): `du_an`, `ngay_do`, `ngay_moc_truoc`, `muc_tieu`, `model_link`, `doi_chung`, `nhan_ban`, `theo_doi`, `chu_y` (chép nguyên vào hồ sơ), `kenh` = `{<id>: {ten, link, giu_loai, nhom, ngach, dinh_dang, tuoi_khan_gia, tuoi_muc_tin, ly_do, hoc_gi, khong_hoc_gi, chu_y, nguon_so, view_30_ngay, video_30_ngay…}}` (hoặc danh sách có trường `id`), `video` = `{<id video>: {de_tai, goc_tiep_can, tu_huyet, kieu_mo, anh_bia, dinh_phat_lai, yeu_cau_binh_luan, kiem_tra_so, ghi_chu}}` (ghi đè giá trị tự động). Đuôi `.tsv` thì là bảng kênh một dòng một kênh (cột `id`, `ten`, `giu_loai`, `nhom`…).
- Số đo (chỉ số kênh, điểm, hạng, cờ) lấy từ file đo và `--xep-hang`; ghi đè `--ghi-de` được áp lại nên khớp bảng xếp hạng. Bảng định tính **không** ghi đè số đo: trùng khoá thì giữ số đo và cảnh báo (trừ `video_30_ngay`).
- Tab 1 và 3: «% tăng 30 ngày» là `pct_tang_sub_30` đã qua trần 100 % / sàn nền (chữ «bỏ khỏi xếp hạng…» khi bị bỏ); cột «% tăng thô» là bản tính lại để đối chiếu.
- Video vào hồ sơ: 10 video dài nhiều view nhất của mỗi kênh có file đo cộng mọi video hệ số ≥ 3 (`--so-top-view`, `--he-so-toi-thieu`); Shorts không vào. Trường định tính không có nguồn tự động để `[CHƯA CÓ]`. `nguon_so` không tự điền (thiếu thì `xuat_sheet.py` báo). Kênh có đo mà thiếu định tính, hoặc thiếu file video, được báo ở cảnh báo.
