# Kit làm phim tài liệu lịch sử bằng Claude Code

Đây là bộ quy trình để một người làm YouTube tự dựng phim tài liệu (kể chuyện bằng bản đồ, số liệu, tư liệu thật, đồ hoạ code). Repo này KHÔNG phải một kênh cụ thể. Danh tính kênh của bạn nằm ở `ho-so-kenh/`. Hướng dẫn cho người dùng: `README.md`, `HUONG-DAN.md`.

## Bộ định tuyến: mỗi lần mở repo, kiểm rồi chọn bước

0. **Kiểm nơi mở Claude trước.** Claude Code chỉ nạp `.claude/settings.json` (chặn đọc `.env`) và `.claude/skills/` của thư mục nó được mở lúc khởi động. Nếu danh sách skill của phiên không có `goha-khoi-dong`, hoặc thư mục làm việc hiện tại không có cả `CLAUDE.md` lẫn `.claude/settings.json` ở gốc, thì DỪNG: không chạy bước nào, không đọc `.env`, không đoán. Bảo người dùng: «Thoát Claude (gõ `/exit`), mở PowerShell, `cd` vào thư mục kit, gõ `claude`, rồi gõ: bắt đầu». Chỉ khi cả hai có mới đi tiếp.
1. Trong `kiem-may.md` ở gốc repo chưa có dòng `K1: xong` → chạy skill `goha-khoi-dong` (K1: kiểm máy, cài đặt, chọn mức chạy). Chỉ có `cau-hinh.toml` thì chưa đủ: tệp đó được tạo giữa chừng K1.
2. K1 đã xong, `ho-so-kenh/ho-so.md` chưa có hoặc chưa có dòng `Trạng thái: đã duyệt` → chạy `tu-duy-top-20-ytb` rồi `goha-ho-so-kenh` (K2: chọn ngách, top 20 kênh mẫu, hồ sơ kênh). Chỉ có thư mục `ho-so-kenh/` thì chưa đủ.
3. Cả hai xong → hỏi người dùng một câu: «Làm tập mới (P0) hay làm tiếp tập dở?». Tập dở: đọc `tap/<EPxxx-slug>/ke-hoach/progress.md` của từng tập, báo tập nào đang ở phase nào.

Quy trình mỗi tập, mỗi bước một skill; chỉ qua bước sau khi người dùng duyệt cổng DỪNG của bước trước:
P0 `goha-ls-chon-de-tai` → P1 `goha-ls-nghien-cuu` → P2 `goha-ls-kich-ban` → P3 `goha-ls-phan-canh` → P4 `goha-ls-giong` → P5 `goha-ls-dung` → P6 `goha-ls-qc` → P7 `goha-ls-dang` → P8 `goha-ls-shorts`.
Dùng chung: `video-harness` (kiểm soát chất lượng khi dựng), `tu-duy-he-thong` (trước việc lớn), `dieu-phoi-cli`, `delegate-cli-agents`. Skill nào không có trong danh sách skill của phiên thì đừng bịa; dùng công cụ gốc của Claude Code và nói rõ với người dùng.

## Danh tính kênh

Tên kênh, ngách, ngôn ngữ, khán giả, giọng đọc, màu, font, logo, mức chạy: đọc `ho-so-kenh/ho-so.md` (trước khi K2 xong, mức chạy nằm ở dòng cuối `kiem-may.md`). Luật nhạy cảm riêng của ngách: `ho-so-kenh/luat-noi-dung.md`. Không tự suy ra danh tính từ tập mẫu `mau/` hay từ tên thư mục. Thiếu thông tin thì hỏi người dùng hoặc quay lại K2, đừng đoán.

## Luật cứng nội dung sử Việt (chủ kit chốt, không tự nới)

Áp cho MỌI bản đồ, thẻ chữ, lời đọc có liên quan Việt Nam, ở mọi ngách và mọi ngôn ngữ, kể cả khi kênh của bạn không phải kênh sử Việt:
- Bám sử chính thống Việt Nam; mọi số liệu, ngày, tên trong lời và chữ trên màn có dòng trong sổ số liệu kèm nguồn chính thống.
- Cấm mọi AI với lãnh tụ Việt Nam: giả giọng, đọc lại, ảnh hoặc video AI, sửa ảnh. Lời của các vị chỉ hiện nguyên văn bằng chữ kèm nguồn.
- Ảnh thật quốc gia được dùng nguyên gốc, ghi nguồn. Ảnh lãnh tụ chỉ cắt khung vuông vắn rồi đóng khung trang trọng; không tách nền, không sửa mặt, không chế ảnh.
- Giọng dựng lại lời trích của người KHÔNG phải lãnh tụ (sĩ quan nước ngoài, chiến sĩ, nhân chứng, nhà thơ…) được làm, nhưng phải ghi rõ trên hình là «mô phỏng lại»; không nhái giọng thật.
- Bản đồ luôn vẽ quần đảo Hoàng Sa, Trường Sa là của Việt Nam và ghi «Biển Đông». Cấm đường lưỡi bò. Không dùng cờ VNCH.
- Hình chỉ từ tư liệu thật và đồ hoạ dựng bằng code; cấm ảnh AI (kênh sử Việt). Tư liệu hạng A: phạm vi công cộng. Hạng B (còn bản quyền): chỉ trích 3 đến 5 giây, tắt tiếng gốc, ghi nguồn. Hạng C: tránh dùng.
- Không thù hằn. Phân biệt chính quyền thực dân hay quân viễn chinh với nhân dân nước họ. Không nêu Trung Quốc trừ khi người dùng yêu cầu.

Kênh NGÁCH KHÁC (không phải sử Việt) dùng Goha Flow (hình minh hoạ) thì: chỉ hình minh hoạ KHÔNG có người thật; ghi chữ «minh hoạ» trên hình; khi đăng khai «nội dung tổng hợp» trong YouTube Studio nếu hình trông như thật. Kênh sử Việt vẫn cấm ảnh AI hoàn toàn.

## Hồ sơ dự án

- **Loại và đầu ra:** video tài liệu lịch sử, quân sự đăng YouTube; Shorts dọc cho YouTube, Facebook Reels, TikTok. Mỗi tập ở `tap/EPxxx-<slug>/`: `ke-hoach/` (brief, kịch bản, sổ số liệu, QC, `progress.md`), `san-xuat/`, `Final/` (video, phụ đề, thumbnail, postpack; Shorts ở `Final/shorts/EPxxx-Snn-<slug>/`). Media nặng nằm ở thư mục `output` khai trong `cau-hinh.toml`, không lên Git.
- **Rủi ro mặc định:** lớn ở nội dung (chủ đề nhạy cảm, đăng công khai, có thể mất kiếm tiền), vừa ở kỹ thuật.
- **Lệnh kiểm "xong":** `python -I -X utf8 tools/kit/kit.py kiem <video> --lufs -14` (−14 ± 0,5 LUFS, đỉnh thật ≤ −1 dBTP); `kit.py chep-loi` rồi `kit.py so-loi --min 0.97` trên bản trộn; soi khung mọi cảnh bản đồ. Kiểm máy: `python -X utf8 tools/kiem-may/kiem-may.py`.
- **Vùng cấm:** không đọc, không sửa, không in, không gửi ra ngoài `.env`, thư mục `cookies/`, mọi tệp có chữ `key`, `secret`, `token` trong tên. Cấm bằng MỌI công cụ, kể cả `cat`, `type`, `Get-Content`, `less`, lệnh `python -c "open('.env')"` hay script tự viết; chỉ `tools/kiem-may/kiem-may.py` và `tools/kit/` được tự nạp khoá, và chúng không in giá trị. `.claude/settings.json` chặn một phần các lệnh đọc (chỉ có hiệu lực khi Claude mở đúng trong thư mục kit, xem bước 0), phần còn lại dựa vào luật này. Không gửi khoá, ảnh hay giọng người thật cho CLI ngoài.
- **Bước tốn tiền:** đọc giọng, chép lời (STT), tiếng động, sinh hình, nhạc, vidIQ. Trước mỗi lần gọi phải nói trong chat: gọi gì, ước tính tốn bao nhiêu, rồi chờ người dùng đồng ý. Giá tra lúc chạy, không đoán.
- **Công cụ riêng:** `python -I -X utf8 tools/kit/kit.py <giong|chep-loi|so-loi|tron|master|ghep|kiem|tieng-dong>`; `node tools/kit/dung-trang.mjs` (cần Node ≥ 22); Goha AVS để trộn và xem lại (bắt buộc ở mức Đầy đủ, mức khác thay bằng `kit.py tron` và `kit.py master`); Goha Flow cho hình minh hoạ ngách khác.

## Chữ cho người xem (kịch bản, lời đọc, tiêu đề, mô tả, thẻ, chữ trên hình)

- Giao sub-agent viết; một người phản biện khác (sub-agent Opus ngữ cảnh mới, hoặc CLI khác hãng nếu có) rà; Claude chính rà dữ kiện theo sổ số liệu.
- Mọi prompt viết chữ cho người xem phải dán khối luật mục C của `kenh/bo-loc-chinh-sach-yt.md`. Trước khi đọc giọng, chạy `python -I tools/loc-chinh-sach/quet.py <kịch bản>` và với tiêu đề, mô tả, thẻ thêm `--vi-tri metadata`; có lỗi CHẶN thì sửa xong mới đi tiếp.
- Cách nói người dùng đã sửa (xưng hô, từ, câu) ghi ngay vào `kenh/cach-noi-da-chot.tsv`; mọi lời đọc và kịch bản qua `python -I tools/lichsu/kiem-da-chot.py <tệp>` với 0 chỗ phạm.
- Nhân vật phía ta luôn có quân hàm hoặc chức vụ, không gọi trống không. Khi nghi chủ đề nhạy cảm, đọc bình luận người xem trước.
- Kiểm trùng: `tools/lichsu/kiem-de-tai.py` (đề tài), `tools/loc-chinh-sach/trung-lap.py` (câu chữ với tập mẫu và kho Shu của bạn).

## Tập mẫu và chép quy trình, không chép chủ đề

Thư mục `mau/dien-bien-phu-1954/` (tập mẫu; ở repo của chủ kit nó nằm ở `tap/EP001-dien-bien-phu-1954/`, các tài liệu trong kit gọi chung là «tập mẫu») là SÁCH ĐỌC để học cách làm: cấu trúc brief, sổ số liệu, kịch bản, phân cảnh, postpack. CẤM đăng lại, cấm dùng lại câu chữ, đề tài, giọng, khung hình của nó. `kit/so-chu-de-cam.tsv` liệt kê đề tài bị chặn; P0 phải đọc. Chặn trùng bằng 5 lớp ở `HUONG-DAN.md` (mục «Chép quy trình, không chép chủ đề»).

## Model, sub-agent, CLI ngoài

Luật cỡ việc theo rủi ro, bậc model theo vai, mẫu brief giao sub-agent, CLI ngoài (Codex, Grok, Agy), handoff qua nhiều chat: đọc `huong-dan/dieu-phoi/`. Tóm tắt: việc lớn (tiền, đăng công khai, khó đảo ngược) lập plan ngắn rồi DỪNG chờ người dùng duyệt; việc hay đổi ý kiến phải hỏi trước; không nhận một câu «xong» khi chưa chạy lệnh kiểm ở trên.

## Cập nhật kit

Repo kit của chủ kit CHỈ ĐỌC với hội viên (quyền Read): hội viên không `git push` lên đó và Claude không được đề nghị việc đó. Công việc của hội viên (hồ sơ kênh, tập phim) nằm ở repo kênh RIÊNG của họ, tạo từ kit theo `README.md` mục «Lập repo kênh riêng»; commit và push chỉ trong repo riêng đó (remote `origin`). Remote `kit` chỉ để lấy bản mới: `git pull kit main` (cách thêm remote và lần đầu nếu tạo repo từ «Use this template» ở `README.md`). Đừng sửa tệp của kit (`tools/`, `.claude/skills/`, `kenh/bo-loc-chinh-sach-yt.md`…) trừ khi người dùng bảo; nếu `git pull` báo xung đột thì dừng và hỏi người dùng, đừng ghi đè hay xoá.
