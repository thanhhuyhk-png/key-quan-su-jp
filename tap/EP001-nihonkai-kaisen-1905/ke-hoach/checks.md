# Checks EP001 日本海海戦 T字戦法の地図分析

## P1

| Mã sổ | Nội dung | Nguồn 1 | Nguồn 2 | Kết quả |
|---|---|---|---|---|
| A1 | 東郷平八郎 大将 + 連合艦隊司令長官 | JA Wiki (line 673) | EN Wiki (line 286) | ĐẠT |
| A2 | ロジェストヴェンスキー 中将 | JA Wiki (line 745) | EN Wiki | ĐẠT |
| A3 | JP fleet 15 knots | JA Wiki (line 447) | EN Wiki (line 912) | ĐẠT |
| A4 | RU fleet 11 knots | JA Wiki (line 447) | EN Wiki | ĐẠT |
| A5 | 4 battleships: 三笠敷島富士朝日, 16 × 12-inch guns | EN Wiki (line 418/419) | JA Wiki | ĐẠT |
| B1 | T-crossing 8,200m (14:07) → 5,800m (14:19) | EN Wiki (line 928-929) | JA Wiki (line 447) | ĐẠT |
| B2 | 1905年5月27-28日 対馬海峡 | EN Wiki (line 285) | JA Wiki | ĐẠT |
| B3 | Oslyabya 15:10 | EN Wiki (line 939) | JA Wiki (line 460) | ĐẠT (JA: 15:07 or 15:10) |
| B4 | Suvorov 19:20 | EN Wiki (line 952) | JA Wiki (line 482) | ĐẠT |
| B5 | Borodino 18:50 | EN Wiki (line 461) | — | MỘT NGUỒN |
| C1 | Nga tử trận 4,830 | JA Wiki (line 511) | EN Wiki (line 865) | ĐẠT (khớp hoàn toàn) |
| C2 | Nga tù binh 6,000+ | JA Wiki 6,106; EN 5,907 | | LỆCH → dùng "6千名以上" |
| C3 | Nhật tử trận 117, bị thương 583 | JA Wiki (line 511) | EN Wiki (line 879) | ĐẠT |
| C4 | Nhật mất 3 tàu ngư lôi | JA Wiki (line 511) | EN Wiki (line 879) | ĐẠT |
| C5 | Nga 21 chìm, 6 bắt | JA Wiki (line 511) | EN Wiki (line 287) | ĐẠT |
| C6 | Rozhestvensky thoát lúc 17:30 | EN Wiki (line 945) | JA Wiki (line 482) | ĐẠT |

**kiem-so.py:** 0 lỗi (15 ĐẠT, 1 MỘT NGUỒN)

## P2

**Cổng 1 — Chính sách:** 0 CHẶN, 0 CẢNH BÁO (kich-ban-v1.md + loi-doc-v1.txt)

**Cổng 2 — Ký tự loi-doc-v1.txt:**
- 7,432 ký tự (không tính newline/space)
- @ 300 chars/min (硝煙 pace): **24.8 phút** ✓ tiệm cận 25 phút
- @ 330 chars/min (sổ tay min): 22.5 phút — cần thêm 818 chars sau P4 khi đo tốc độ thật
- **Ghi chú:** tốc độ giọng thật chưa đo (P4 chưa làm). Nếu ElevenLabs đọc nhanh hơn 硝煙 (330+ chars/min), cần thêm ~800-1,500 ký tự ở v2.

**Cổng 3 — Chống trùng:**
- GỘP: 0.00% (0/602 cụm 6 tiếng); 0 câu ≥10 tiếng trùng
- So với: 3 video đối thủ Tsushima + 15 video Shu
- **ĐẠT** (ngưỡng ≤1%)

**Mã sổ đã dùng trong v1:** A1 A2 A3 A4 A5 B1 B2 B3 B4 B5 C1 C2 C3 C4 C5 C6
(B5 MỘT NGUỒN — đã ghi trong kịch bản)

**Điểm còn mở:**
- Tốc độ giọng thật cần đo ở P4 → có thể cần v2 thêm ~800 ký tự
- Câu hỏi trung tâm xuất hiện ở ~3% thời lượng (câu "では、この圧倒的な勝利は…") ✓ (target ≤5%)


## P2 v2 (2026-11-11) — sau phản biện Gemini

**Phản biện ngoài (Gemini):** chấm v1 9.5/10 (Hook 9.5, Research 10, Structure 9.0, Depth 9.5). Phê bình: khô khan, thiếu hook cảm xúc.

**Lọc phản biện theo bằng chứng:**
| Đề xuất | Quyết định | Lý do |
|---|---|---|
| Lai tạo hook 信濃丸 9 giờ + tia lửa điện | BÁC | Vi phạm chống trùng — đúng góc 硝煙+日本史再審, brief P0 cấm |
| Thêm 伊集院信管/下瀬3000度 | BÁC | Không có sổ số liệu (chi tiết video đối thủ) |
| Tả máu/nướng chín lính Nga | BÁC | Vi phạm bộ lọc chính sách mục 4 |
| Foreshadowing 4 knot ở hook | NHẬN | Có sổ A3/A4 |
| Nhân cách hóa 三笠 | NHẬN | Có sổ A1 |
| Mạnh vế lời nguyền chiến thắng | NHẬN | Có sổ D9 (làm mềm, không nêu 大和/武蔵) |

**Mini-P1 bổ sung sổ:** thêm 9 dòng D1-D9 (các dữ kiện v1 thêm để đủ số chữ). kiem-so.py: 0 lỗi (23 ĐẠT 2 nguồn, 2 MỘT NGUỒN: B5, D9).

**3 cổng v2:**
- Chính sách: 0 CHẶN 0 CẢNH BÁO
- Ký tự: 7,812 → 26.0 phút @ 300 chars/min ✓
- Chống trùng: 0.00% (0/633); 0 câu ≥10 tiếng — ĐẠT

**Mã sổ v2:** A1-A5, B1-B5, C1-C6, D1-D9 (25 dòng)


## P2 v3 (2026-11-11) — Học DNA hook Model Link

**Yêu cầu user:** học DNA hook Model Link, KHÔNG chép. Rút 5 gen DNA từ 4 hook (Gemini mổ 203高地, マレー, WW2, Tsushima 9h).

**Phát hiện:** hook v2 mở bằng 信濃丸 sương mù = trùng ảnh mở 硝煙+日本史再審.

**V3 áp DNA, nghịch lý RIÊNG:**
- Gen 1+2: mở bằng nghịch lý 4 knot → 21 tàu chìm (~8s)
- Nghịch lý số pháo 20>16 mà Nga thua (A5/C4/C5) — chưa đối thủ dùng
- 信濃丸 → Chương 3 (dòng thời gian), hết trùng ảnh mở
- Câu hỏi trung tâm ~48s@300 (~43s@335 thực tế)

**3 cổng v3:** 0 CHẶN; 7,663 ký tự ~25.5 phút; chống trùng 0.00% (0/630), 0 câu ≥10 tiếng.

**Mã sổ v3:** giữ nguyên A1-A5, B1-B5, C1-C6, D1-D9 (không thêm dữ kiện mới; chỉ tái cấu trúc hook)


## P3 Phân cảnh (2026-11-11)

**Máy kiểm thích ứng cho kênh Nhật** (sửa từ máy kiểm tập mẫu): tách câu theo KÝ TỰ (tiếng Nhật không dấu cách), tốc độ 300 ký tự/phút; nguồn chính thống Nhật (JACAR, 国立国会図書館, NARA, Wikipedia); loại hình anh/the/ban-do/can-tim; bỏ luật riêng VN (vnmap Hoàng Sa, Karmen, pháo 105, 3D sân khấu VN); giữ guard luật cứng bản đồ VN (chặn nếu lỡ nhắc Việt Nam/Biển Đông) + chặn tả máu + bắt số kanji không nguồn.

**Kết quả:**
- 310 cảnh, 1,533 s (25:33), 12.1 cảnh/phút (trong 10–20)
- Mở đầu trailer cinema: 20.3 cảnh/phút (cắt nhanh, 2 cảnh/câu, theo yêu cầu user)
- Theo kiểu: the 157, ban-do 128, anh 25
- Tư liệu thật 25 cảnh; hạng A?/B dài nhất 3.4 s (trần 5 s ✓)
- Mọi chương ≥ 9 cảnh/phút, ≥ 1 đặc tả ✓

**Đột biến: 5/5 bắt** (ảnh ngoài tsv, bản đồ VN, số không nguồn, mã bản đồ sai, tả máu). Vá thêm: regex bắt số kanji (十五/二十) ngoài số Ả Rập.

**Tài sản cần dựng (P5):** 10 ảnh PD/CC (三笠, 東郷, スヴォーロフ, オスリャービャ, ボロジノ, ロジェストヴェンスキー, 信濃丸, バルチック艦隊, 記念艦三笠); 6 bản đồ hải chiến vẽ code (koukai hành trình, tsushima eo biển, tjifa T字, yoru đêm, tsuigeki truy kích, sekai thế giới); thẻ số liệu infographic.

**Điểm refine ở P5:** 157 cảnh "the:gaiyo" là thẻ mặc định (gán theo từ khoá) — P5 nâng thành infographic/bản đồ cụ thể cho kênh 地図と論理. Ảnh A? (信濃丸, バルチック艦隊) cần xác minh nguồn gốc PD trước khi dùng.
