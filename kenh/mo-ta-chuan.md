# Chuẩn mô tả, thẻ, hashtag: 戦陣再審

Chữ trong tệp này khi áp cho tập cụ thể phải qua `quet.py --tieu-de` và `kiem-da-chot.py` (0 lỗi) trước khi đăng.

## 1. Khuôn mô tả (tối đa 4.800 ký tự, tiếng Nhật)

| # | Khối | Quy cách |
|---|---|---|
| 1 | Cảnh mở | ≤ 150 ký tự; mở bằng mốc thời gian + địa điểm cụ thể: `「西暦○○年○月、[地名]―」` |
| 2 | Nút thắt | 2–3 đoạn ngắn; kết bằng câu hỏi trùng ý tiêu đề |
| 3 | Tư liệu | 1 đoạn: nêu loại tư liệu dùng (公文書館, NARA...); không nêu nguồn cụ thể ở đây |
| 4 | Mốc chương | `0:00 はじめに` rồi các mốc thực tế từ bản dựng cuối |
| 5 | Xem thêm | Từ tập 2: liên kết tập trước cùng loạt |
| 6 | Nguồn | Mục 2 dưới đây |
| 7 | Hashtag | 3 hashtag, dòng cuối cùng |

## 2. Nguồn và tư liệu
Mỗi dòng: `【出典】機関名 / 資料名 / 年` — ví dụ:
- `【出典】国立公文書館アジア歴史資料センター / 明治37年戦役 陸軍省大日記 / 1904`
- `【出典】US National Archives (NARA) / Record Group 80, Naval Records / 1941`
- `【画像クレジット】Public Domain via JACAR (Ref. CXXXX)`
Ngân sách ký tự: ≤ 500 ký tự cho phần nguồn để cả mô tả ≤ 4.800

## 3. Hashtag (3 cái, dòng cuối)
| Nhóm | Hashtag |
|---|---|
| Ngách chính | `#戦史解説` |
| Chủ đề tập | `#日露戦争` / `#太平洋戦争` / `#日本史` (đổi theo tập) |
| Thương hiệu | `#戦陣再審` |

## 4. Thẻ video (20–25 thẻ, ≤ 480 ký tự)
| Nhóm | Số thẻ | Ví dụ |
|---|---|---|
| Tên sự kiện (nhiều cách gọi) | 4–6 | 日露戦争, 旅順攻囲戦, 203高地, Battle of Port Arthur |
| Địa danh, đơn vị | 4–6 | 旅順, 満州, 第三軍, 連合艦隊 |
| Nhân vật có trong phim | 2–4 | 乃木希典, 東郷平八郎 |
| Tiếng Anh | 3–4 | Japanese military history, Russo-Japanese War, Meiji Japan |
| Chung ngách | 2–3 | 戦史, 日本軍, 歴史解説 |
| Thương hiệu | 1 | 戦陣再審 |

## 5. Mục khi tải lên YouTube Studio
- Danh mục: `Education` (Giáo dục) — đa số kênh mẫu trong sheet dùng
- Ngôn ngữ video: Tiếng Nhật (ja)
- Ngôn ngữ tiêu đề/mô tả: Tiếng Nhật (ja)
- Khai báo AI: Nếu giọng AI hoặc bản đồ animation trông như thật → khai `AI使用コンテンツ` trong YouTube Studio

## 6. Kiểm trước khi đăng
- [ ] Mô tả ≤ 4.800 ký tự; mốc chương từ bản dựng cuối
- [ ] Mỗi dòng nguồn có dòng trong sổ số liệu tập
- [ ] `quet.py --tieu-de` 0 CHẶN
- [ ] `kiem-da-chot.py` 0 chỗ phạm
