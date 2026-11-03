# Cơ cấu vũ khí cận cảnh (kit teardown)

Cảnh "giải phẫu" một cơ cấu vũ khí: cắt dọc, bộ phận đang làm việc sáng màu nhấn, số đo trên màn đọc từ cùng hàm điều khiển chuyển động. Dùng cho cảnh cận cơ cấu, không thay kho sa bàn `../3d/` (engine three.js r149 riêng).

Dựng bằng kit của skill **teardown** (github.com/elvarofficial/teardown, MIT, xây trên whaleyxbt/claude-motion; bản đã đọc mã ngày 01/11/2026, commit `a91262a`). Kit đặt ngoài repo ở `<teardown>` (đã `npm ci --ignore-scripts`; three 0.186, esbuild, Playwright). Giấy phép: `GIAY-PHEP-TEARDOWN.txt`. Thư mục này không chép mã của kit, chỉ gọi kit qua `teardown-kit/...`.

## Dựng

Chạy trong một thư mục làm việc ngoài repo (đầu ra ở `teardown-out/` của thư mục đó), ví dụ `<output>\<ngày>-<tập>\co-cau\`:

```
node "template/kho-quan-su/co-cau/dung.mjs" khoa-nong-105            # bảng ảnh soát theo timeline.json
node "template/kho-quan-su/co-cau/dung.mjs" khoa-nong-105 --still 9.4
node "template/kho-quan-su/co-cau/dung.mjs" khoa-nong-105 --video    # 1920x1080, 30 fps
```

Trang HTML ở `teardown-out/dist/<tên>.html` mở được offline để xem. Video 17 s xuất mất khoảng 31 s trên RTX 2080 Ti.

## Cấu trúc một cơ cấu

| File | Việc |
|---|---|
| `kin.js` | Số đo (ghi rõ dòng nào có nguồn, dòng nào ước lượng) và `stateAt(t)`: một đầu vào là t, ra mọi tư thế. Không có three.js. |
| `gun.js` | Hình khối dựng bằng code, mặt cắt (`CLIP`), `update(state, t)`. |
| `main.js` | Ánh sáng, góc máy theo t, lớp chữ tiếng Việt, `render(t)` thuần. |
| `style.css` | Chữ Be Vietnam Pro (kit chỉ nhúng font latin, thiếu dấu). |
| `timeline.json` | Các mốc (giây) để chụp bảng soát. |

## Mẫu đã có

- `khoa-nong-105/`: khoá nòng chêm trượt ngang lựu pháo 105 mm M2A1, một vòng mở khoá, nạp đạn, đóng, giật dây cò, giật lùi 1,07 m (quay chậm 4 lần), hất vỏ. **Bản thử**: cỡ nòng, dài nòng, kiểu khoá, kiểu cò, quãng giật lùi, đạn 105 × 372 mm R có nguồn (TM 9-1325; en.wikipedia.org/wiki/M101_howitzer); kích thước vòng khoá, khối chêm, tay quay, đầu đạn là ước lượng. Trước khi lên phim phải đo lại trên hình cắt của TM 9-1325 (archive.org/details/TM9-1325) và cập nhật dòng `khoa-nong-105` trong `NGUON.tsv` của thư mục này (cùng cột với `../NGUON.tsv`; file đó đang đặt chỉ-đọc nên chưa gộp).

## Mẫu prompt (đã chạy được)

> Dựng cảnh cận cơ cấu `<tên vũ khí>` cho tập `<tập>` theo `template/kho-quan-su/co-cau/README.md`, chép cấu trúc từ `khoa-nong-105/`. Trước khi viết hình: tìm số đo công khai và hình cắt tham chiếu, ghi vào `co-cau/NGUON.tsv`; số nào chưa có nguồn thì ghi "ước lượng" trong `kin.js` và không đưa lên chữ. Một đầu vào (t) điều khiển mọi chi tiết; cắt dọc để thấy bộ phận đang làm việc; tối đa 2 dòng chữ mỗi nhịp. Soát bằng `dung.mjs <tên>` (bảng ảnh) tới khi không còn lỗi, rồi xuất `--video`.

## Luật khi dựng

- Luật cứng của repo giữ nguyên: số trên màn phải có dòng trong sổ số liệu; không dựng người, không dựng lãnh tụ; không cờ.
- Bắt đầu từ hình tham chiếu thật, không từ một câu mô tả. Va chạm thì sửa bằng số trong `kin.js`, không giấu bằng góc máy.
- Ít chữ (chuẩn đài): một tiêu đề, một dòng phụ, tối đa hai số đọc. Màu nhấn chỉ cho bộ phận đang làm việc.
- Chuyển động nhanh hơn mắt đọc (giật lùi ~0,1 s) thì quay chậm và ghi "quay chậm" trên màn.
