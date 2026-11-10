# Sổ tay văn phong: 戦陣再審

Nguồn: phụ đề 15 video (戦いのヒストリア×6, 硝煙の記憶×5, 日本史再審×4). Ngày: 2026-11-10.

Ghi chú kỹ thuật: phụ đề 戦い/硝煙 dạng rolling (2 dòng cuộn), đã dedup trước khi đếm. Phụ đề 日本史再審 dạng NHK-style (câu ngắn rõ ràng, từng dòng là một ý). Số tốc độ bên dưới là sau dedup.

---

## 1. Tốc độ giọng (ký tự Nhật/phút, sau dedup rolling subtitle)

| Video ID | Kênh | Phút | Ký tự (dedup) | Tốc độ |
|---|---|---|---|---|
| EpuFNr2q5gc | 戦いのヒストリア | 48,4 | 20.471 | 423 |
| hySCDeAwmZ0 | 戦いのヒストリア | 34,3 | 15.380 | 448 |
| cslyx4HoV4w | 戦いのヒストリア | 32,2 | 14.295 | 444 |
| W4VHbYTWYNg | 硝煙の記憶 | 26,6 | 7.791 | 293 |
| UzhvzcpHeOI | 硝煙の記憶 | 45,2 | 13.641 | 301 |

**Trung bình 5 video mục tiêu: 382 ký tự/phút**

Mục tiêu kịch bản 戦陣再審:
- 25 phút = khoảng **9.550 ký tự**
- 30 phút = khoảng **11.460 ký tự**

Trung bình toàn 15 video: 361 ký tự/phút.

Theo kênh:
- 戦いのヒストリア (n=6): **418** ký tự/phút — nhanh, kể chuyện liên tục
- 硝煙の記憶 (n=4): **340** ký tự/phút — chậm hơn, có khoảng lặng và nhạc
- 日本史再審 (n=5): **311** ký tự/phút — NHK-pace, câu ngắn, dừng có chủ ý

戦陣再審 dùng ElevenLabs (tự nhiên) → tham chiếu tốc độ **330–380 ký tự/phút** (giữa 硝煙 và 戦い). Không ép nhanh theo 戦いのヒストリア vì họ dùng ゆっくり tổng hợp.

---

## 2. Khuôn mở 90 giây (đo 15/15 video)

**Hook trong 10 giây đầu:** 0/15 video có câu hỏi dạng ？ trong 10 giây đầu.
Tất cả đều dùng bối cảnh/cảnh mở — KHÔNG mở bằng câu hỏi ngay.

**Câu hỏi trung tâm (なぜ/どうして/のか) xuất hiện lần đầu:**
- Trung bình: **88 giây** (1 phút 28 giây)
- Nhanh nhất: 16 giây (cslyx4HoV4w — 戦い)
- Chậm nhất: 264 giây (2MX3iF94SwE — 硝煙, video đặc biệt về chiến tranh đang diễn ra)
- Không tính 2 video ngoại lệ: trung bình **~60 giây**

**Cơ chế mở phổ biến nhất (n=15):**

| Cơ chế | Số video | Mô tả ngắn |
|---|---|---|
| (a) Ngày cụ thể + cảnh người thật | 6 | Mốc ngày → ai đó làm gì → tình huống bí ẩn |
| (a) Công thức "ときは〜年" | 4 | 戦い đặc trưng: mở như kể truyện |
| Khác (chiến tranh đang diễn ra, v.v.) | 2 | Mở bằng ngữ cảnh thời sự |
| Cảnh khí quyển (gió, tuyết, biển) | 1 | 硝煙 đặc trưng |
| (c) Lật kỳ vọng (実は) | 1 | |
| (a) Chỉ có ngày, không có người | 1 | |

**Cơ chế mở thắng (日本史再審 — view và nhận xét cao nhất nhóm):**
Khuôn: `[Ngày phương Tây + năm hiệu Nhật]。[Địa điểm cụ thể]。[Một người làm một việc nhỏ]。[Chi tiết vật lý kỳ lạ làm bật câu hỏi]。`

Ví dụ khuôn (không phải câu chép): `1905年、明治38年5月27日` → địa điểm → nhân vật → hành động cụ thể → 5–6 giây sau: câu hỏi.

**Ví dụ mở THẮNG** (EpuFNr2q5gc — video dài nhất, nhiều view):
Mở bằng "ときは1460年頃" → xây bối cảnh 70 giây → câu hỏi 中央 xuất hiện ở giây 81 (2,8%).

---

## 3. Cấu trúc nội dung (đo 5 video đại diện)

**Câu hỏi trung tâm (なぜ/どうして) ở % thời lượng:**

| Video | % | Ghi chú |
|---|---|---|
| EpuFNr2q5gc (戦い) | 11,9% | Xây bối cảnh dài trước |
| W4VHbYTWYNg (硝煙) | 3,2% | Câu hỏi rất sớm |
| UzhvzcpHeOI (硝煙) | 4,5% | |
| E37r1tHa9IU (日本史) | 4,1% | |
| Wsm0HIP5VNY (日本史) | 18,1% | Video dạng "ai quyết định" — tình huống được xây kỹ |

Trung bình: **8,4%** (không tính outlier 18%: ~5–6%).
Nhận xét: ≤5% là tốt cho 戦陣再審 (câu hỏi trung tâm trong 90 giây đầu).

**Văn phong chủ đạo:**

| Kênh | 文語調 (〜のだ/〜である/〜た) | 丁寧語 (〜ます/〜です) |
|---|---|---|
| 戦いのヒストリア | ~40–50% | ~50–60% |
| 硝煙の記憶 | ~37–41% | ~59–63% |
| 日本史再審 | ~35–36% | ~64–65% |

→ **Tất cả ba kênh dùng 丁寧語 làm chủ đạo** (~60–65%). 文語調 chiếm ~35–40%, dùng để nhấn mạnh và tóm tắt. 戦陣再審 nên theo tỷ lệ này.

**Câu hỏi tu từ (rhetorical questions):**

| Kênh | Câu hỏi/10 phút |
|---|---|
| 戦いのヒストリア (EpuFNr2q5gc) | 8,1 |
| 硝煙の記憶 (W4VHbYTWYNg) | 6,8 |
| 硝煙の記憶 (UzhvzcpHeOI) | 5,3 |
| 日本史再審 (E37r1tHa9IU) | 2,7 |
| 日本史再審 (Wsm0HIP5VNY) | 5,5 |

Trung bình: **5,7 câu hỏi/10 phút**.
戦陣再審 mục tiêu: **4–6 câu hỏi/10 phút** (theo 硝煙 và 日本史, không ép cao như 戦い).

**Độ dài câu trung vị:**
- 硝煙 và 日本史: **27–31 ký tự/câu** (câu ngắn, rõ ràng)
- 戦いのヒストリア: phụ đề rolling không tách câu được chính xác → không dùng số này

Mục tiêu 戦陣再審: câu tường thuật **25–35 ký tự**, câu kết luận/nhấn **10–20 ký tự**.

---

## 4. Từ vựng và cách gọi đã chốt

**Thời gian:**

| Kênh | Cách viết | Ví dụ khuôn |
|---|---|---|
| 戦いのヒストリア | Tây lịch thuần túy | `1945年8月15日` |
| 硝煙の記憶 | Tây lịch chính, hiệu Nhật rất hiếm | `1914年6月28日` |
| 日本史再審 | Tây lịch + hiệu Nhật trong cùng câu mở | `1905年、明治38年5月27日` |

→ 戦陣再審 (kênh quân sự Nhật): **dùng cả hai theo khuôn 日本史再審** khi nhắc sự kiện Nhật Bản và đồng minh (`1905年、明治38年`), chỉ Tây lịch khi nhắc sự kiện nước ngoài.

**Đơn vị hải quân (đo từ 日本史再審 — kênh chính xác nhất về lịch sử Nhật):**
- 連合艦隊: 11 lần — dùng khi nói về hạm đội liên hợp Nhật
- 日本海軍: 8 lần — dùng khi nói tổng thể hải quân
- バルチック艦隊: 13 lần — dùng tên tiêu chuẩn, **không** dùng "ロシア艦隊" thay thế
- ロシア艦隊: 10 lần — dùng khi cần phân biệt rõ hơn, không phải tên chính

→ 戦陣再審: dùng **バルチック艦隊** (không viết tắt), **連合艦隊** cho phía Nhật.

**Ngôi kể:**
- あなた: 戦い dùng 3 lần/6 video, 硝煙 1 lần, **日本史再審: 0 lần**
- → 戦陣再審 **không dùng あなた** — kể khách quan, không hỏi thẳng khán giả

**Mở chương / chuyển cảnh:**

| Kênh | Từ dùng nhiều nhất | Ít dùng |
|---|---|---|
| 戦いのヒストリア | さて (40 lần/6 video) | では, ここで |
| 硝煙の記憶 | さて (2), 一方 (11) | では |
| 日本史再審 | では (62 lần/5 video) | さて (0!), ここで (3) |

→ 戦陣再審 theo 日本史再審: **「では、〜」** để chuyển cảnh. Tránh 「さて」(nghe thân mật kiểu ゆっくり/戦い). 「一方、〜」cho câu chuyển mang tính đối lập.

**Kết video:**

| Kênh | Khuôn kết |
|---|---|
| 戦いのヒストリア | Thúc CTA → チャンネル登録 → `ご視聴ありがとうございました` |
| 硝煙の記憶 | Câu wrap-up thơ/cảm xúc → (một số không có CTA) |
| 日本史再審 | Câu kết nội dung → Preview tập sau → チャンネル登録 → `ご視聴、ありがとうございました` |

→ 戦陣再審 theo khuôn **日本史再審**: câu tổng kết ý nghĩa (1–2 câu) → thông báo chủ đề tập sau → `ご視聴、ありがとうございました。`. **Không** kêu gọi "高評価" thẳng như 戦いのヒストリア.

---

## 5. Điều KHÔNG học (khác biệt chủ ý)

| Đặc điểm nguồn | Kênh nguồn | Lý do 戦陣再審 không làm theo |
|---|---|---|
| Giọng ゆっくり tổng hợp (robot) | 戦いのヒストリア | 戦陣再審 dùng ElevenLabs — giọng tự nhiên hơn |
| Mở bằng "ときは〜年" (công thức đọc truyện) | 戦いのヒストリア | Nghe truyện thiếu nhi — không phù hợp tone tài liệu nghiêm |
| Câu hỏi tu từ liên tục, dày (8/10min) | 戦いのヒストリア | 戦陣再審 mục tiêu 4–6/10min, để không nghe quá casual |
| 「さて」làm từ chuyển cảnh chính | 戦いのヒストリア | Thay bằng 「では、」 |
| Kết video bằng "高評価お願い" ngay | 戦いのヒストリア | 戦陣再審 kết bằng nội dung trước, CTA sau |
| Không có preview tập sau | 硝煙の記憶 (một số) | 戦陣再審 luôn có preview → xây chuỗi |
| Chỉ Tây lịch, không có hiệu Nhật | 戦いのヒストリア, 硝煙 (phần lớn) | 戦陣再審 dùng cả hai khi về sự kiện Nhật |

---

## 6. Khuôn tham chiếu nhanh cho viết kịch bản

```
[MỞ — 0–60 giây]
Ngày (Tây + hiệu Nhật). Địa điểm. Một người làm một việc cụ thể.
Chi tiết vật lý kỳ lạ / kết quả bất ngờ.
→ Câu hỏi trung tâm trong vòng 60–90 giây đầu (< 5% thời lượng).

[THÂN]
Chuyển cảnh: 「では、〜」/ 「一方、〜」
Tốc độ: 330–380 ký tự/phút
Câu hỏi tu từ: 4–6/10 phút
Câu kể: 25–35 ký tự | Câu nhấn: 10–20 ký tự
Văn phong: 丁寧語 60–65%, 文語調 35–40%

[KẾT]
Câu tổng kết ý nghĩa (1–2 câu, không phải đơn thuần tóm tắt).
Preview chủ đề tập sau (1 câu).
「チャンネル登録をして、お待ちください。」
「ご視聴、ありがとうございました。」
```

---

*Phân tích bởi Claude Code · Phiên 2026-11-10 · Chỉ đo khuôn, không chép câu chữ nguồn.*
