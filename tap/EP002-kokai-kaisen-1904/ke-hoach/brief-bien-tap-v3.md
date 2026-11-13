# Brief biên tập v3 · EP002 黄海海戦 1904 (2026-11-13)

Bạn là người biên tập. Từ `kich-ban-v2.md` và `loi-doc-v2.txt` (thư mục `tap/EP002-kokai-kaisen-1904/ke-hoach/`) viết ra `kich-ban-v3.md` và `loi-doc-v3.txt`. Lời tiếng Nhật; báo cáo tiếng Việt. Được đọc: tệp này, hai tệp v2, `so-so-lieu.csv`, `brief-viet-p2.md`. Không đọc tệp khác, không tra web, không thêm dữ kiện ngoài sổ.

**Cách làm bắt buộc:** viết một script Python (đặt ở `E:/Goha-JP/output/261113-kokai-kaisen-1904/sua-v3.py`) chứa từng cặp thay thế cho CẢ HAI tệp (kịch bản: câu có mã sổ; lời đọc: cùng câu viết số bằng chữ Hán), mỗi cặp `assert t.count(cu)==1` trước khi thay, để hai tệp không lệch nhau. Đoạn lớn thì thay nguyên khối. Chạy script, rồi sửa tiêu đề mốc thời gian các phần trong kịch bản theo độ dài mới.

Số dòng dưới đây là dòng trong `kich-ban-v2.md`. Danh sách đã được Claude chính lọc từ hai người phản biện vòng 2; mục nào không có thì giữ nguyên.

## Hook
E1. Thay 開幕 (dòng 16–25) bằng:
```
戦艦の数は、ロシア6隻、日本4隻。 [A7a]
この日、沈んだ戦艦は、1隻もありません。 [C7]
それでも、旅順艦隊は、目的地のウラジオストクへ、たどり着けませんでした。 [A2][B7]
そして、この日を境に、大規模な出撃ができなくなります。 [C7b]
戦艦の数で上回り、1隻も沈まなかった艦隊が、なぜ、逃げ切れなかったのか。 [A7a][C7]
勝敗を分けたのは、東郷大将の戦術か、それとも、一発の砲弾か。
1904年、明治37年8月10日、黄海海戦。 [A1]
この日の日没は、午後8時ごろ。暗くなれば、追う側は、相手を見失いやすくなります。 [B8a][C7]
一発の砲弾で、旅順艦隊の隊形が崩れたのは、午後6時40分ごろ。日没まで、あと1時間20分ほどでした。 [B6a][B6b][B8a]
この動画では、その一日を、朝から日没まで、時計と地図でたどります。
```
Thẻ chữ hook: 「戦艦 ロシア6 対 日本4」「戦艦の沈没 0」. Dòng `Hình:` của hook: bỏ `Maps-of-the-Russo-Japanese-War_084…Carte-de-l-Extreme-Orient` (bản đồ Viễn Đông có thể chứa vùng Biển Đông không đúng luật), thay bằng コード地図 黄海.

## Dữ kiện (CHẶN)
E2. Dòng 242: xoá cả câu 「昼は、15キロ近く。夕方は、6から7キロ。距離は、半分以下に縮まりました。」. Dòng 241 giữ.
E3. Dòng 207: 「画面の隊列図で、最後尾の艦が、少しずつ、離れていきます。 [B4]」 → xoá. Dòng 208 giữ (ý chung, không mã sổ).
E4. Dòng 145: 「日没まで、あと7時間半ほどです。」 → 「日没まで、まだ7時間以上あります。」 [B2][B8a].
E5. Dòng 394: 「旅順艦隊の一日は、逃げ切りの一日であり、同時に、逃げ切れなかった一日でもありました。」 → 「旅順艦隊の一日は、逃げ切りまで、あと1時間あまりに迫りながら、届かなかった一日でした。」 [B6a][B8a].

## Dữ kiện (NÊN SỬA)
E6. Dòng 198: 「午後1時すぎから、午後5時半すぎまで、およそ4時間半。追跡が続きます。」 → 「昼の砲撃のあと、午後5時半すぎまで、数時間にわたって、追跡が続きます。」 [B2b][B5].
E7. Dòng 215–216 thay bằng: 「ただし、追う側には、ためらう理由があったとされます。追撃は続けながらも、戦艦を危険にさらす接近は避けた、という見方です。」 [A9].
E8. Dòng 325: → 「午後8時ごろ、日は沈みました。そのとき、旅順艦隊は、すでに一つの艦隊ではなくなっていました。」 [B7][B8a].
E9. Dòng 97: 「戦艦と防護巡洋艦を合わせて、10隻です。」 → 「主力は、この戦艦6隻と防護巡洋艦4隻です。ほかに、駆逐艦も加わっていました。」 [A5a][A5b] (không nói số khu trục).
E10. Dòng 116–117: xoá 「画面の表を、読み上げます。」 và phần đọc bảng; giữ một câu: 「戦艦は、日本4隻、ロシア6隻。日本は、駆逐艦18隻、水雷艇およそ30隻をそろえていました。」 [A7a][A6c].
E11. Dòng 20 cũ đã thay ở E1. Ở mọi chỗ khác có 「数で上回る艦隊」 (ví dụ quanh dòng 192) → 「戦艦の数で上回る艦隊」.
E12. Dòng 328: 「沈没艦が出ないまま」 → 「戦艦の沈没がないまま」.
E13. Dòng 50 (hoặc nơi có 「陸からも、海からも、狭められていました」): bỏ 「海からも、」 → 「港の中は、陸からの砲撃で、狭められていました。」.
E14. Dòng 406: bỏ chữ 「だけ」.
E15. Dòng 319: → 「結果として、艦隊としての、ウラジオストクへの針路は、この日、閉じました。」.
E16. Dòng 167: bỏ 「もう一度、」.
E17. Dòng 344: thêm 「大きな艦では、」 ở đầu câu.
E18. Dòng 21 cũ đã thay ở E1; mọi chỗ khác 「見失います」 tuyệt đối → 「見失いやすくなります」 (trừ câu C7 「薄暮に至り、旅順艦隊を見失いました」 giữ nguyên).

## Lặp, câu bù, văn phong
E19. Xoá: dòng 181, 182, 184 (giữ 178–180, 183, 185); dòng 289 (lặp 1時間20分); ở dòng 298 chỉ giữ 「画面の時計は、午後6時40分ごろ。」; dòng 312; dòng 316, 317; dòng 332 (giữ 333); dòng 379; dòng 116 (câu 棒グラフ, nếu còn sau E10).
E20. Dòng 129–133 gộp còn hai câu: 「断定はできません。叩くべきか、守るべきか。二つの要請が、同じ海の上で、せめぎ合っていたとされます。」 [A9]. Dòng 130–131 bỏ.
E21. Đảo dòng 378 lên trước dòng 377. Dòng 380 → 「陸の戦いの結果が、港の中の艦隊に届いたのです。」 [C8].
E22. 「〜のだ。」 → 「〜のです。」 ở dòng 170 và 210. Dòng 283 「戦術はかわされた。しかし、砲弾は、かわされなかった。」 → 「戦術は、かわされました。しかし、砲弾は、かわされませんでした。」.
E23. 結 dòng 401 thay bằng: 「答えは、どちらか一方ではありません。かわされた戦術が追撃に変わり、その追撃が、一発の砲弾を、届く距離まで運びました。」 [B3][B3b][B5][B6a].
E24. Giảm 「画面の〜」 và 「では、」 mở đoạn: mỗi loại giữ tối đa khoảng 10 lần trong lời đọc (hình tự nói, chuyển sang dòng `Hình:`/`Chữ trên hình:` nếu cần).
E25. Đóng 第5章 bằng câu treo: chuyển câu hỏi 「艦列が崩れたあと、旅順艦隊は、どう動いたのでしょうか。」 (dòng 297) về cuối 第5章, thay cho dòng 290; 第6章 mở bằng 「画面の時計は、午後6時40分ごろ。」.
E26. 蔚山沖 (dòng 363–365): thêm một câu nối trước: 「ウラジオストクには、旅順艦隊が合流するはずだった、もう一つの艦隊がいました。」 — KHÔNG thêm: chưa có trong sổ. Thay vào đó dùng: 「では、旅順艦隊が向かうはずだったウラジオストクの艦隊は、どうなったのか。」 [A2].

## Hình
E27. `ndl-yalu-1904-fleet-gun.jpg`: Claude chính đã xem ảnh: thiết giáp hạm thời 1904, cùng người chụp 芦野海軍教授 với ảnh 8/10; GIỮ, chú thích 「黄海海戦 1904年8月10日（写真帖の英題 YALU）」. `ndl-rurik-survivors.jpg`: ghi 「要確認：負傷者が写る場合は使わない」. `ndl-cruiser-full-speed.jpg`: thay bằng コード地図 (bỏ ảnh). `arthur-fleet-wrecks-0105-32.jpg`: chú thích ngày chụp 「1905年1月4日」.

## Độ dài
Sau khi cắt, lời đọc v3 phải 7.700–8.600 ký tự (bỏ khoảng trắng). Nếu hụt, KHÔNG viết câu bù kiểu tóm tắt hay «画面の…»; chỉ thêm câu đọc diễn biến có mã sổ đã có (B3, B5, B6b, B7, C2–C5) hoặc để trống — Claude chính sẽ bù bằng khoảng lặng hình ở P3.

## Tự kiểm
- Script chạy hết, mọi assert qua.
- `python -I -X utf8 rieng/tools/quet-ja.py <kich-ban-v3> <loi-doc-v3>` → 0 CHẶN.
- Đếm ký tự lời đọc v3.
- Bảng E1–E27: ĐÃ LÀM / KHÔNG LÀM (lý do).

Được sửa: chỉ tạo `kich-ban-v3.md`, `loi-doc-v3.txt`, script `sua-v3.py`, báo cáo `plans/reports/bien-tap-v3-261113.md` (≤ 30 dòng). Không sửa tệp khác, không commit, không đọc .env hay tệp có chữ key/secret/token. Kết bằng Status · Summary · Model.
