---
name: goha-ls-nghien-cuu
description: P1 Nghiên cứu của quy trình sản xuất phim tài liệu lịch sử, quân sự (kit Goha Lịch Sử) — lập sổ số liệu có câu trích nguyên văn đã máy đối chiếu, sổ tài sản hình có hạng bản quyền, và kho phụ đề đối thủ cho cổng chống trùng. Dùng ngay khi bắt đầu một tập mới trong `tap/<slug>/`, khi user nói "P1", "nghiên cứu tập", "lập sổ số liệu", "tra nguồn", "mở rộng sổ", "tìm tư liệu hình", "sổ tài sản", hoặc khi kịch bản khung có dòng [SỔ] chưa có nguồn — kể cả khi user không nhắc tên skill. Không dùng để viết kịch bản (đó là goha-ls-kich-ban).
---

# P1 Nghiên cứu (Goha Lịch Sử)

Đường dẫn dạng `<output>`, `<nghien_cuu>`, `<vst_python>`, `<chep_loi>` là khoá trong `cau-hinh.toml` ở gốc repo (mẫu: `cau-hinh.mau.toml`; script đọc bằng `tools/cau_hinh.py`). Đường dẫn khác tính từ gốc repo.

Danh tính kênh (tên, ngách, ngôn ngữ, Model Link, mức chạy) đọc từ `ho-so-kenh/ho-so.md`; luật nhạy cảm riêng của ngách đọc từ `ho-so-kenh/luat-noi-dung.md`. Ví dụ mang nhãn «tập mẫu EP001» (Điện Biên Phủ 1954) chỉ để minh hoạ số đo, không phải luật.

Đầu ra của P1 là ba thứ mà P2 (viết kịch bản) đứng lên trên đó:
1. `tap/<slug>/ke-hoach/so-so-lieu.csv`: mỗi con số, ngày, tên trong lời đọc có một dòng, kèm câu trích **nguyên văn đã máy đối chiếu** với trang nguồn, và hai cột `muc_dung`, `cach_noi` do Claude chốt.
2. `tap/<slug>/ke-hoach/so-tai-san.md`: tư liệu hình theo chương, hạng A/A?/B/C, cái gì thay bằng đồ họa code.
3. Kho phụ đề đối thủ cùng đề tài (ngoài repo) để P2 chạy cổng chống trùng.

Vì sao làm kỹ: luật cứng của dự án bắt mọi số có nguồn chính thống (với ngách ngoài sử Việt: nguồn chính thống của nước, thời kỳ đó, theo `luat-noi-dung.md`); sai một số là mất uy tín kênh lịch sử. Sub-agent tra web hay chép "gần đúng" câu trích, nên câu trích phải được máy so với chữ thô của chính URL đó, không tin lời báo cáo.

Đọc trước: `CLAUDE.md` của repo (luật cứng), `ho-so-kenh/ho-so.md`, `ho-so-kenh/luat-noi-dung.md`, `tap/<slug>/ke-hoach/brief.md` hoặc `kich-ban-khung.md` (các dòng [SỔ], mục "Nguồn chính thống cần tra"), `kenh/lich-noi-dung.md` nếu có.

## Công cụ (đã có trong repo, đừng viết lại)
| Lệnh | Việc |
|---|---|
| `python -I tools/lichsu/lay-trang.py <url> <thư mục>` | Tải trang, lưu chữ hiển thị thành `.txt`, dòng đầu `URL: …`. Giữ cookie (qdnd.vn cần). Lỗi chứng chỉ SSL thì báo lỗi: **tìm nguồn khác**, không bỏ kiểm chứng chỉ (hệ thống chặn, và đúng là nên chặn). |
| `python -I tools/lichsu/kiem-so.py <sổ.csv> <thư mục chữ thô> [--chi-loi]` | Đối chiếu từng câu trích với chữ thô đúng URL. ĐẠT / MỘT NGUỒN (cảnh báo) / LỖI. Mã thoát 1 khi có lỗi. Câu trích nối mảnh bằng `[...]` hoặc `…`. |
| `python -I tools/loc-chinh-sach/trung-lap.py <lời.txt> <kho phụ đề>…` | Cổng chống trùng (dùng ở P2; P1 chỉ chuẩn bị kho). |

Chữ thô lưu ngoài repo: `<output>/<yymmdd>-<slug>/nguon-tho/<nhóm>/`. Test công cụ: `python -m pytest tools/lichsu tools/loc-chinh-sach -q -p no:cacheprovider`.

## Các bước
Ghi giờ bắt đầu, kết thúc vào `tap/<slug>/ke-hoach/progress.md` (giờ máy thật, `date`).

1. **Liệt kê dữ kiện cần tra** từ mọi [SỔ] của kịch bản khung, cộng luận điểm trung tâm (vd "niềm tin của bên kia") vì luận điểm cũng phải có nguồn. Nếu tập có sổ cũ (bản mẫu, tập trước cùng chiến dịch), chạy `lay-trang` cho mọi URL cũ rồi `kiem-so` trước: dòng cũ đạt thì giữ, dòng lỗi thì giao tra lại.
2. **Chia nhóm và giao sub-agent Sonnet chạy song song**, mỗi nhóm một file CSV riêng (`ke-hoach/nhap/so-nhom-<x>.csv`) và một thư mục chữ thô riêng. Chia theo phe hoặc theo chương, 7–9 dữ kiện mỗi nhóm. Một agent nữa lo tư liệu hình. Mẫu giao việc: `references/brief-tra-cuu.md`. Mỗi agent mất 8–12 phút.
3. **Tự chạy lại `kiem-so.py`** cho từng file nhóm khi agent báo xong. Không nhận "0 lỗi" từ báo cáo.
4. **Chốt `muc_dung` và `cach_noi` cho từng dòng** (quy tắc ở dưới), gộp thành `so-so-lieu.csv` bằng một script gộp đặt ngoài repo (dict mã dòng → quyết định; dòng chưa chốt thì script báo lỗi). Cột: 10 cột chuẩn + `muc_dung`, `cach_noi`. Mã dòng: `M` cho sổ cũ, chữ nhóm cho dòng mới.
5. **Kiểm toàn sổ**: `kiem-so.py` trên thư mục `nguon-tho/` gốc (quét mọi nhóm) phải 0 lỗi. Lập bảng phủ [SỔ] → mã dòng trong `ke-hoach/checks.md`; phải phủ 100 %.
6. **Sổ tài sản**: gộp sổ ảnh cũ và kết quả agent hình thành `so-tai-san.md` theo chương (tư liệu thật | đồ họa code), mục "Không dùng hoặc khoá", mục "Rủi ro treo". Kho 3D và bản đồ có sẵn: `template/kho-quan-su/NGUON.tsv`, `template/map3d`, `template/vnmap`, `template/cards`.
7. **Kho phụ đề đối thủ** (cho P2): lọc video cùng đề tài trong bảng video vượt trội của sheet top 20 của kênh (K2), cộng `yt-dlp --flat-playlist "ytsearch12:<đề tài>"`; tải phụ đề **tuần tự**, chạy nền, đặt `--sub-langs` theo ngôn ngữ trong `ho-so.md` (ví dụ tiếng Việt `"vi,vi-orig,vi-VN"`):
   `yt-dlp --skip-download --write-subs --write-auto-subs --sub-langs "<ngôn ngữ>" --sub-format vtt --sleep-subtitles 3 -o "sub/%(channel)s__%(id)s.%(ext)s" <url>`, nghỉ 4 s giữa video. Lưu `<nghien_cuu>/doi-thu-<đề tài>/`. Bản `vi` và `vi-orig` thường giống hệt: xoá bản trùng bằng `cmp`. Người viết P2 không được thấy kho này.

**Nhánh thay thế (mức Tiết kiệm / Miễn phí):** không có sub-agent tra web song song thì tự tra từng nhóm theo đúng thứ tự trên, vẫn bắt buộc `lay-trang.py` rồi `kiem-so.py`; nguồn chỉ là chữ thô đã tải, không tin trí nhớ. Video đối thủ không có phụ đề thì phiên âm bằng `tools/kit/kit.py chep-loi <video> --adapter whisper` (chạy máy, không cần khoá, chậm trên CPU) hoặc `tools/kit/kit.py chep-loi` nếu có khoá Deepgram, ElevenLabs.

## Quy tắc chốt `muc_dung` / `cach_noi`
- **DÙNG**: hai nguồn khớp. `cach_noi` ghi đúng câu chữ được nói.
- **Nguồn lệch số** → nói dạng tròn hoặc định tính có ở cả hai nguồn ("hàng chục khẩu pháo", "hàng trăm ki-lô-mét", "rạng sáng"), không chọn một số.
- **Số chỉ nằm trong chú thích ảnh**, không có trong văn bản bài → KHÔNG DÙNG số đó (ví dụ tập mẫu EP001: chú thích ảnh ghi 960 kg, văn bản ghi "gần 1.000 kg").
- **Số nước ngoài** → ĐỐI CHIẾU, tối đa một câu, chỉ khi khớp chiều với số chính thống.
- **Nhân vật, sự kiện ngoài khung thời gian của trận** → KHÔNG DÙNG trong phần kể trận (ví dụ tập mẫu EP001: một anh hùng hy sinh trước chiến dịch).
- **Chi tiết nhạy cảm theo bộ lọc chính sách** (tự sát, thương tích, số thương vong từng trận) và theo `ho-so-kenh/luat-noi-dung.md` → KHÔNG DÙNG nếu không cần cho luận điểm.
- **Lời lãnh tụ Việt Nam** → chỉ hiện chữ nguyên văn trên hình kèm nguồn; giọng dẫn AI không đọc nguyên văn (luật cứng cấm AI "đọc lại"). Lời người khác (sĩ quan nước ngoài, chiến sĩ, nhân chứng) giọng dựng lại được, nhưng sẽ phải ghi «mô phỏng lại» trên hình (xem P3, P5).
- **Cách gọi không rõ ai nói** ("con nhím khổng lồ") → dùng được nhưng không gán cho một người cụ thể.
- Quân hàm, chức vụ lệch giữa nguồn → theo số đông cơ quan chính thống, ghi rõ trong `cach_noi`.

## Hạng tư liệu hình
A dùng được, ghi nguồn · A? ảnh lưu trữ nhà nước đăng lại qua báo, chưa thấy bản gốc · B còn bản quyền (kho ảnh/phim lưu trữ thương mại, phim tư liệu của tác giả nước ngoài, Commons do người tải tự gán giấy phép) trích 3–5 s, ghi nguồn · C không dùng (tranh bìa tạp chí, ảnh tô màu chưa xác minh, ảnh có logo đè giữa). Không có ảnh thật dùng được thì thay bằng đồ họa code, đừng hạ chuẩn. Kênh sử Việt: không ảnh do AI tạo hay phục chế bằng AI (luật cứng); ngách khác theo `luat-noi-dung.md`. Ảnh màu thời 1950 phải xác minh không phải tô màu trước khi mở khoá.

## Lỗi đã gặp
| Lỗi | Cách xử lý |
|---|---|
| qdnd.vn trả 302 lặp vô hạn | `lay-trang.py` đã giữ cookie |
| Cổng `.gov.vn` địa phương lỗi chứng chỉ (gặp ở tập mẫu EP001) | Thay bằng QĐND, Nhân Dân, TTXVN |
| dangcongsan.vn từ chối kết nối | Bỏ, dùng nguồn khác |
| Console Windows không in được tiếng Việt | Script tự `sys.stdout.reconfigure(encoding="utf-8")`; `python -I` bỏ qua `PYTHONIOENCODING` |
| Câu trích lệch vì khoảng trắng sát dấu ngoặc, hoặc `[...]` | `kiem-so.py` đã bỏ khoảng trắng và ngoặc trước khi so |
| Hai "nguồn" thực ra cùng một URL | Tính là MỘT NGUỒN; ghi rõ trong ghi chú |

## Mốc đo (tập mẫu EP001, 01/11/2026)
P1 mất 18 phút đồng hồ: 3 sub-agent song song, sổ 71 dòng (68 đủ hai nguồn), 0 lỗi đối chiếu, 26 ảnh mới, 16 phụ đề đối thủ.
