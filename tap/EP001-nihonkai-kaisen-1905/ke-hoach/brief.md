# Brief tập: 東郷艦隊はなぜバルチック艦隊を全滅できたのか｜T字戦法の地図分析【日本海海戦】

## Đề tài
- **Đề tài:** 日本海海戦 (Trận hải chiến Tsushima)
- **Năm, địa điểm:** 1905年5月27–28日、対馬海峡（日本海）
- **Ngôn ngữ, thị trường:** Tiếng Nhật, thị trường Nhật
- **Góc kể (khác biệt so với video cùng đề tài):** Phân tích chiến thuật thuần túy bằng bản đồ — tại sao T字戦法 lại quyết định được trận đấu: tốc độ hạm đội, cự ly hải pháo, góc ngắm, số lượng đạn pháo. Góc này chưa kênh nào làm kỹ; các kênh khác (硝煙の記憶, 日本史再審) đều làm góc "9 giờ trước" và cảm xúc, không phân tích cơ học chiến thuật.
- **Cấu trúc kể:** S2 — Bàn cờ hai kế hoạch (kế hoạch của Togo vs Rozhestvensky, chỗ va nhau, bên nào tính sai)
- **Câu hỏi trung tâm của tập:** 東郷平八郎がバルチック艦隊を全滅させたのは「幸運」か「必然」か？T字戦法が成立した物理的条件を地図で検証する。
- **Độ dài mục tiêu:** 25–30 phút

## Vì sao chọn
| Cột | Điểm 0–5 | Bằng chứng |
|---|---|---|
| Nhu cầu | 5 | 硝煙の記憶 273k view; 日本史再審 242k view (Shinano-Maru episode) cho cùng trận |
| Cạnh tranh | 3 | Góc "9h trước" và cảm xúc đã có; góc bản đồ chiến thuật thuần túy chưa ai làm kỹ |
| Tư liệu sẵn có | 5 | JACAR phong phú (hải quân đế quốc), NARA (Russian records), ảnh hải chiến PD |
| Rủi ro chính sách | 5 | 0 CHẶN 0 CẢNH BÁO (kiểm 2026-11-10) |

Video mẫu trong sheet top 20:
- 硝煙の記憶「日本海海戦 最初の一発の9時間前、すでに勝負はついていた」273,236 view (10 ngày)
- 日本史再審「タタタタ 日本海海戦は砲火の9時間前に始まっていた」242,777 view (15 ngày)

## Kiểm trùng
- Lệnh: `python -I -X utf8 tools/lichsu/kiem-de-tai.py "日本海海戦" --goc "T字戦法はなぜ決定的だったか — 東郷艦隊の艦速・射程・砲角を地図で再現する戦術分析" --ngon-ngu ja --so-chung E:/Goha-JP/so-chung.tsv`
- Kết quả: **ĐẠT** (sổ cấm: 16 dòng đã so; sổ chung: 2 dòng đã so) — ngày kiểm: 2026-11-10
- Đã đăng ký vào sổ chung: **chưa** (người dùng tự điền qua Form ở HUONG-DAN.md mục 6)

## Giao cho P1
- **Dữ kiện cần tra trước:**
  - Tốc độ hạm đội Nhật vs Nga tại thời điểm khai hỏa (hải lý/giờ)
  - Khoảng cách giao chiến khi T字戦法 bắt đầu (mét/yards)
  - Số lượng đạn 12 inch bắn ra của từng bên
  - Thời gian tiêu diệt từng chiến hạm chủ lực Nga
  - Quân hàm chính xác: 東郷平八郎 (連合艦隊司令長官 大将), ロジェストヴェンスキー (中将)
  - Tổng thương vong Nga vs Nhật (tàu chìm, tù binh, tử trận)

- **Nguồn chính thống đã biết:**
  - JACAR (国立公文書館アジア歴史資料センター) — 海軍省公文備考, Ref. C09050476900
  - 明治38年 海戦史 (Hải quân đế quốc, lưu trữ công cộng)
  - Novikov-Priboy "Tsushima" (phía Nga, dịch tiếng Nhật có)
  - 海軍大学校「海戦要務令」1905

- **Tư liệu hình đã biết:**
  - Hạng A (PD): ảnh JACAR — 戦艦三笠、信濃丸、東郷司令長官 (Shimbun Tsushima photos 1905)
  - Hạng A: US Naval Institute collection (1905 naval charts)
  - Hạng B: NHK documentary stills (3–5 giây, tắt tiếng)

- **Bản đồ, đồ hoạ code cần dựng:**
  - Bản đồ hải trình từ Madeira → Tsushima (toàn hành trình Rozhestvensky)
  - Bản đồ T字戦法: vị trí tàu, góc xoay, vùng bắn của từng pháo tháp
  - Animation hạm đội tiếp cận và xoay đầu (key moment)
  - Infographic: so sánh vận tốc, trọng lượng đạn, số pháo 12 inch hai bên

- **Điểm nhạy cảm riêng của đề tài** (đối chiếu `ho-so-kenh/luat-noi-dung.md`):
  - Thương vong Nga (~5,000 tử trận, 6,000 tù binh): nêu số liệu trung tính có nguồn, không tả ghê rợn
  - Rozhestvensky bị bắt tù binh: ghi chú Nhật Bản đối xử nhân đạo (theo Công ước Geneva), tránh bị hiểu là miệt thị
  - Không có vấn đề Nam Kinh / 慰安婦 / Kamikaze ở đề tài này

- **Việc không làm:**
  - Không làm lại góc "9 giờ trước" hay "Shinano-Maru phát hiện hạm đội" (đã có trên các kênh mẫu)
  - Không dùng ảnh AI của đô đốc Togo
  - Không nhắc đến chiến sự đang diễn ra
