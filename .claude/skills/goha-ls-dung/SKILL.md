---
name: goha-ls-dung
description: P5 Dựng của quy trình sản xuất phim tài liệu lịch sử, quân sự (kit Goha Lịch Sử) — dựng hình và âm cả tập từ phan-canh.json đã đo trên giọng thật, theo lô có máy dựng riêng: thẻ chữ số (template/cards), ảnh tư liệu Ken Burns và phim tư liệu hạng B, bản đồ map3d/vnmap (Hoàng Sa, Trường Sa), cảnh 3D trên sân khấu kho bản mẫu (cảnh mẫu + biến thể máy), lớp chữ trong suốt (thẻ tên, ghi nguồn), ghép đúng tổng khung, trộn nhạc và tiếng động (kit.py tron, master −14 LUFS). Dùng ngay khi user nói "P5", "dựng tập", "render cảnh", "ghép hình", "trộn âm", "bản nháp có tiếng", hoặc khi tập đã có moc-cau.json và phan-canh.json ĐẠT mà chưa có video — kể cả khi không nhắc tên skill. Không dùng để phân cảnh (goha-ls-phan-canh) hay kiểm xuất (goha-ls-qc).
---

# P5 Dựng (Goha Lịch Sử)

Đường dẫn dạng `<output>`, `<nghien_cuu>`, `<vst_python>`, `<chep_loi>` là khoá trong `cau-hinh.toml` ở gốc repo (mẫu: `cau-hinh.mau.toml`; script đọc bằng `tools/cau_hinh.py`). Đường dẫn khác tính từ gốc repo.

Danh tính kênh (logo, màu, font, mức chạy) đọc từ `ho-so-kenh/ho-so.md`. Ví dụ mang nhãn «tập mẫu EP001» (Điện Biên Phủ 1954) chỉ để minh hoạ số đo.

Mẫu đã chạy: tập mẫu EP001, 01/11/2026 (tập mẫu nằm ở `mau/dien-bien-phu-1954/` (ở repo của chủ kit là `tap/EP001-dien-bien-phu-1954/`)). **Máy dựng của từng tập là các script `san-xuat/*.py` của tập mẫu** (`dung-the.py`, `dung-tu-lieu.py`, `dung-ban-do.py`, `dung-3d.py`, `dung-lop-chu.py`, `ghep-hinh.py`, `dung-am.py`, `hau-ky-am.py`, `dung-duong-giong.py`, `kiem-phan-canh.py`…): chúng chứa logic dùng lại lẫn bảng dữ liệu của riêng tập đó. Tập mới KHÔNG có sẵn chúng. Trước khi dựng, chép các script cần dùng sang `tap/<EPxxx-slug>/san-xuat/`, mở đầu từng tệp và sửa bảng dữ liệu (tên tập, đường dẫn `<output>`, bảng cảnh, mốc, thẻ chữ) theo tập mới, không sửa logic trừ khi có lý do; thiếu script nào thì dừng và hỏi chứ đừng viết lại từ đầu. Nơi ra: `<output>/<ngày>-<tập>\hinh\<lô>\<mã>.mp4`, `am\`, `xem-truoc\`. Mọi máy dựng chạy `python -I -X utf8 <file> [--stills] [--render] [MÃ…]`: `--stills` ra ảnh soi ở `hinh\story\<lô>\<mã>\sheet.jpg`, `--render` ra video và in số khung (phải khớp, không có dòng "LỆCH").

## Nguyên tắc
- Một cảnh = một file đúng số khung `round(t1·24) − round(t0·24)`; ghép bằng concat, kiểm tổng khung.
- **Hình sạch, chữ một lớp:** ảnh, phim, 3D render không chữ; thẻ tên, chữ nhấn, nhãn ngày, ghi nguồn ở lớp chữ trong suốt (`dung-lop-chu.py`, khối `template/overlay`), phủ khi ghép. Thẻ và bản đồ tự vẽ ghi nguồn (bản đồ: nguồn nền bản quyền + "Số liệu: …").
- Mốc hiện chữ, mũi tên, đồ họa trong cảnh neo bằng `"@câu:chữ"` (giây thật từ `moc-cau.json`), không gõ giây tay.
- Cảnh dài hơn cảnh mẫu 3D: **co đồng hồ vật lý** (`toc = dài_mẫu / dài_cảnh`), không đổi tốc độ video.

## Các lô và máy dựng
| Lô | Máy | Ghi chú |
|---|---|---|
| L1 thẻ | `dung-the.py` (dict `THE`) | 8 kiểu `cards` + `hai-cot` (hai sổ, hai trang, hai cột số). Câu hỏi, tiêu đề dùng `hook`; niềm tin, ba việc dùng `van-kien` (gạch, tô). Lời lãnh tụ: `van-kien` chữ nguyên văn, trong khoảng lặng |
| L2 tư liệu | `dung-tu-lieu.py` | archival Ken Burns xoay vòng 5 đường máy; ảnh màu hôm nay giữ `goc`, ảnh thời xưa `bw-am`; ảnh lãnh tụ `lanhTu` (chỉ cắt khung vuông vắn rồi đóng khung trang trọng, không tách nền, không sửa mặt, không chế ảnh). Phim tư liệu hạng B: ffmpeg cắt + màu theo tập, tắt tiếng (tập mẫu EP001: phim Karmen, hằng số `KARMEN_CAT/MAU`, màu `film_dbp`) |
| L3 bản đồ | `dung-ban-do.py` (dict `BD`, `VN`) | `base` dùng lại shot a–g (+ `cut`, `route_scale`), `copy`, `pts_tran_dia`; vnmap khung chạm biển dùng zoom ≤ 66 cho thấy Hoàng Sa, Trường Sa, ghi «Biển Đông», không đường lưỡi bò; Tây Bắc zoom ≥ 470 (≤ 105,5° Đông). Luật này áp cho **mọi** bản đồ có Việt Nam, kể cả kênh ngách khác |
| L4+L5 3D | `dung-3d.py` + `trang3d/tap1.js` | mỗi cảnh: cảnh mẫu (bảng nhóm của bản mẫu) + biến thể máy `xoay/keo/cao` quanh điểm nhìn (tia nhìn chạm lưới hiển thị đầu tiên) |
| Lớp chữ | `dung-lop-chu.py` | đọc cột Chữ: cụm "…" → thẻ góc dưới, "Nhãn …" → nhãn ngày, `CHU_NHAN` → chữ nhấn đúng chữ đọc. Cảnh có giọng dựng lại lời người khác (không phải lãnh tụ) phải có nhãn «mô phỏng lại» ở lớp này |
| Ghép | `ghep-hinh.py` | cảnh chưa có → ô giữ chỗ (mã + mô tả) để soi nhịp sớm |
| L6 âm | `dung-am.py` (`--tron`) | nhạc nền theo chương (lặp, duck), hạ 25 % ở lời lãnh tụ, tắt trước tiếng nổ lớn; tiếng động theo từ khoá cột Âm (tiếng lớn chỉ to trong khoảng lặng có tên, trong lời −24 dB); master loudnorm 2 lượt −14 LUFS, TP −1,5 + alimiter |

## Sàn chất lượng: bản đã duyệt (bài học tập mẫu EP001, 02/11/2026)
Chủ kênh chê bản Full v1 kém hơn bản Demo đã duyệt (hook nhạt, tiếng động mờ, không khí thế). Trước khi dựng, đo bản đã duyệt (kênh mới: bản dựng thử đầu tiên mà người dùng đã gật) và lấy làm **sàn**, không làm nhạt để sửa lỗi kỹ thuật:
- **Intro trailer trước lời** (`intro.py`): nổ ngay khung 0, cắt đúng phách nhạc hook, chữ tiêu đề đứng yên, rồi lặng + một tiếng khô, lời vào khi nhạc dâng lại. Mọi mốc phim lùi `INTRO_KHUNG`.
- **Âm ≥ 60 tiếng/phút** (Demo 89): mỗi cú cắt một tiếng theo loại cảnh (ảnh: tiếng chụp; phim, 3D, bản đồ: tiếng vụt), thẻ có tiếng gõ từng chữ, nhãn trên hình gõ phím, lớp nền chiến trường. Tiếng ngắn trong lời −20…−26 dB; tiếng lớn chỉ trong khe lặng đo được (`khe-lang.txt`; khe phải bắt đầu ≤ 1 s sau chữ cuối câu). Không nén cả phim về −30 dB để qua STT (lỗi v1). Tiếng intro cắt sẵn bằng ffmpeg để tắt gọn (cut của mix mờ 0,3 s).
- **Hình**: cảnh 3D yếu (đồng cỏ phẳng, đồi sương lặp) thay bằng phim tư liệu hạng B chưa dùng (≤ 5 s) hoặc nguồn `demo:<mã>[>]` (`dung-demo.py`, nguyên render 3D Demo đã duyệt). Thẻ tối phủ trong suốt lên hình động (`dung-the.py` `NEN_SAU`, chỉ lấy nền không có chữ trong hình).
- **Màu lịch sử, quân sự** (`mau: 'quan-su'` ở `cards.js`, `vnmap.js`): giấy bản đồ tác chiến có đường đồng mức, lưới toạ độ, nếp gấp; mực nâu đen, đỏ son ký hiệu ta, xanh mực ký hiệu địch; Việt Nam màu đất son trên bản đồ tham mưu. Không dùng màu infographic (đỏ tươi trên xanh navy, giấy kraft phẳng).
- Ghi file bằng Python trên Windows: giữ kiểu xuống dòng gốc (`write_bytes`), không thì diff git phình cả file.

## Sóng cảm xúc cả phim (tập mẫu EP001 v2, 02/11/2026)
- Khoảng thở ở mọi bảng chữ: dòng `T*`…`Z*` trong bảng khoảng lặng của `phan-canh.md` (sau câu mà thẻ đang giữ hình, 1–3 s, bội 0,5 s để cảnh sau giữ số khung), rồi `dung-duong-giong.py` nối lại câu đã cắt (không gọi ElevenLabs), `kiem-phan-canh.py`, đo lại khe lặng (`silencedetect=noise=-45dB:d=0.2` trên giọng). Chỉ cảnh giữ khoảng thở đổi số khung: so `phan-canh.json` cũ và mới để biết cảnh cần render lại. Mỗi chương một đáy 3–5 s (`DAY` ở `dung-am.py`). Tư liệu A?/B giữ khoảng thở vẫn chịu trần 5 s (máy kiểm báo).
- Thẻ chữ dài, lời trích nhân chứng → `may-chu`, hạn chót `@<khoảng thở>-0.4`; thẻ có gạch, làm mờ (van-kien có `marks`) giữ nguyên. Mọi thẻ tối đặt lên hình động (`NEN_SAU`), trừ lời lãnh tụ và đoạn tưởng niệm.
- Âm: `python -I -X utf8 tools/kit/kit.py tron <mix.json> --out <wav>` trộn giọng + nhạc (trộn được > 1.000 cue nhưng chậm, ~3 phút mỗi 2 phút phim), tiếng động trộn sẵn một lớp bằng `tron_tieng()` (cùng phép đỉnh tệp → db, cut mờ 0,3 s) rồi cộng vào trước master. Nhạc mỗi chương một bản, `tho_trong()` hạ mỏng ở mỗi khoảng thở.
- Soi lại đoạn phim tư liệu hạng B bằng máy dò cú cắt (`select='gt(scene,0.25)',showinfo`) trước khi dùng: ví dụ tập mẫu EP001: C4-02 cũ (43:05) lộ 2,4 s cảnh người chỉ huy trước cú cắt 2587,4.

## Lỗi gặp ở tập mẫu EP001 và cách sửa
- `template/node_modules` mất sau khi chuyển repo → map3d treo "READY never turned true": `npm install` trong `template/`.
- Đường dẫn ảnh trong shot archival là đường dẫn tương đối từ `template/archival/` tới `<output>` (`dung-tu-lieu.py` tính bằng `os.path.relpath`), nên repo và `<output>` phải cùng ổ đĩa.
- Ghi nguồn thẻ chữ là "Nguồn: …"; "Đồ họa minh họa · Số liệu: …" chỉ cho bản đồ, 3D.
- Lời lãnh tụ dài: size 60, maxW 1620 để không mồ côi chữ.
- vnmap hai nhãn gần nhau (ví dụ tập mẫu EP001: Hà Nội, Điện Biên Phủ ở zoom 60): đẩy nhãn bằng `dx`, `dy`.
- 3D: cảnh mẫu ngắn mà cảnh mới dài → máy đi quá đường, chui vào vách (co đồng hồ). Tia nhìn ngang không chạm đất → điểm nhìn sai, máy lùi ra chân trời (raycast lưới hiển thị, bỏ Sprite: Sprite cần `ray.camera`, nếu không ném lỗi matrixWorld). Cảnh mẫu BD7 (xẻng trong hào) hỏng ở kho hiện tại (trang gốc cũng ra màu nâu) → thay bằng biến thể BD8.
- Kho 3D thiếu món cho một số ý: la bàn, đèn pin trong hầm, điện thoại dã chiến, tay ngai, mưa trong hào, ụ cao xạ 37, pháo phía Pháp. Đã dùng cảnh gần nghĩa; sửa cột Hình của bảng cho đúng cái hiện lên; ghi nợ chất lượng.
- SFX của tập mẫu EP001 nằm phẳng trong kho âm giữ lại dưới `<output>` (không có nhóm con như `kit/ASSETS.tsv` ghi); tiếng và nhạc mới thì ghi nguồn, giấy phép vào `kit/ASSETS.tsv`.

## Hậu kỳ nhà đài, mốc khí thế (tập mẫu EP001 v3, 02/11/2026)
- **Mốc phát động tiến công = khoảng lặng có tên** (`H1`…, 1,5–3,5 s, có cảnh riêng neo vào) chứ không nhét vào khe 0,6 s: lời ngừng, tổ hợp 6–8 lớp (`dung-am.py` `to_hop`: pháo bắn đi → đạn rít → nổ dồn vọng núi → rung trầm → đất rơi; súng máy, hô xung phong xa). Cú nổ lớn nhất phim (A1) phải cao hơn mốc liền kề ≥ 1,5 dB (đo RMS 400 ms). Hình: rung máy tắt dần đúng mốc nổ (`ghep-hinh.py` `RUNG`).
- **Khe giữa dòng** (`n:k` trong bảng khoảng lặng, `dung-duong-giong.py`): kể nhiều câu ngắn trên một dòng lời, mỗi câu một tiếng (dây đứt, bánh nghiến, khựng) mà không đánh số lại câu.
- **Chuỗi VST thật** (mức Đầy đủ; `hau-ky-am.py`, chạy `<vst_python>`): giọng Pro-Q 3 → Pro-DS ≤ 3,5 dB → Pro-C 2, không vang; nhạc khoét 2,5 kHz + duck sidechain −8 dB theo giọng; tiếng chia bus (`kho` giao diện, `ngoai` Valhalla Room 3,2 s, `ham` phòng tối 0,7 s), **đuôi vang duck −9 dB khi có lời** (đuôi 3,2 s từng phủ chữ "chèn"); tổng Pro-C 2 Bus → Pro-L 2.
- **Đỉnh thật sau AAC:** bộ `aac` của ffmpeg vọt đỉnh +2…+5 dB ở cú nổ khởi đầu từ lặng (trần −1,5 ra +0,8; trần −3 ra +1,9). Dùng `aac_mf` 256k và trần Pro-L 2 −3,5 dBTP → file cuối −1,2 dBTP. Cái giá: nhấn còn +8…+10 dB so với lời.
- **Tiếng nhấn tắt gọn trong khe** (`gon()`): đuôi nhấn −4…−8 dB tràn 0,5 s vào câu sau làm STT mất "ba quyết định", "có những" (lỗi có từ v2).
- **Không phủ hạt phim tổng hợp** ở lượt mã hoá cuối: nhiễu ngẫu nhiên làm file 17 phút thành 9,4 GB (71 Mbps) và YouTube nén thành vệt khối.
- **Soi phim tư liệu hạng B phải nhận ra người trong hình**, không chỉ dò cú cắt (ví dụ tập mẫu EP001: 43:48 là tù binh Pháp, 43:49,5 là cờ Pháp trên hầm). Video nhóm 3D Demo có khung đệm đen ở đầu cảnh (BD9: 6 khung) → dùng `demo:<mã>+<lệch>`.
- Deepgram trả rỗng với đoạn cắt ngắn ~4 s; soi chéo bằng đoạn ≥ 12 s có ngữ cảnh.

## Dấu kênh linh hoạt 4 góc (chủ kit duyệt 02/11/2026 15:55)
- `ghep-hinh.py`: dấu kênh (`dau-kenh.png`, logo trong `ho-so.md`, hội viên dùng logo do K2 sinh; tập mẫu EP001: 229×50, kem mờ 58 %) chọn góc từng cảnh bằng quy hoạch động: góc bận (đo cạnh trên 3 khung mỗi cảnh, cộng luật lớp chữ: thẻ tên → dưới trái, nhãn ngày hoặc thẻ chữ → trên trái) phạt nặng, đổi góc phạt, lệch góc của chặng 75 s phạt nhẹ; chỉ đổi ở cú cắt, mờ vào 0,4 s. Góc dưới phải luôn có ghi nguồn nên gần như không dùng.
- Ẩn ở intro, tiêu đề, ảnh và lời lãnh tụ, đoạn tưởng niệm (danh sách `AN_DAU`; tập mẫu EP001: MO30, C1-19, C3-20, C3-21, KT-10, KT-22…KT-25). Ảnh lãnh tụ từng bị dấu chạm mép ảnh: cảnh có ảnh lãnh tụ luôn vào `AN_DAU`.
- Soi trước khi render: `python -I -X utf8 ghep-hinh.py --soi-dau <thư mục>` xuất khung Full HD ở mỗi lần đổi góc (user muốn mở ảnh cỡ thật).
- (v4) Bộ lọc `freezeframes` của ffmpeg cần hai đầu vào (luồng gốc, luồng lấy khung thay): `split=2[a][b];[a][b]freezeframes=...`. Lỗi chỉ lộ khi cảnh 3D có khung hỏng. Đầu cảnh nhấp nháy nhiều khung liền (ví dụ tập mẫu EP001, C1-22: 41, 79, 79, 41, 79, 41…) thì máy dò so hai bên bị lừa: so với mức ổn định (trung vị khung 5–15), thay cả đoạn đầu (`nhap_nhay_dau`).

## Nhánh thay thế (mức Tiết kiệm / Miễn phí, máy yếu)
- **Tiếng động, nhạc:** không có ElevenLabs SFX hoặc Suno thì dùng YouTube Audio Library, Pixabay Music (cho phép kiếm tiền), Freesound CC0; ghi nguồn, giấy phép từng tệp vào `kit/ASSETS.tsv`. Mật độ ≥ 60 tiếng/phút vẫn là sàn: ít tệp thì cắt ngắn, lặp có biến đổi cao độ.
- **Hậu kỳ không có VST FabFilter, Valhalla:** `python -I -X utf8 tools/kit/kit.py master --am <mix.wav> --ra <master.wav> --lufs -14 --tp -3` sau chuỗi ffmpeg (`equalizer` khoét 2,5 kHz cho nhạc, `acompressor`, `aecho` cho vang ngắn, `alimiter`), hoặc plugin miễn phí (TDR Nova, Valhalla Supermassive, LoudMax) qua Goha AVS. Hậu kỳ kém tinh hơn một chút; luật −14 LUFS, đỉnh ≤ −1 dBTP không đổi.
- **Máy yếu (chế độ nhẹ):** 720p khi dựng nháp, ít cảnh 3D, tăng thẻ chữ, bản đồ, tư liệu; render lại Full HD một lần ở cuối. Hình kém hoành tráng nhưng không đổi luật cứng.
