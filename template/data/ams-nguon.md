# Nguồn bản đồ AMS dùng cho map3d nền `ams`

Hai tờ bản đồ địa hình 1:50.000 của Cục Bản đồ Lục quân Hoa Kỳ (US Army Map Service). Tài liệu do chính phủ Hoa Kỳ lập, thuộc phạm vi công cộng (Wikimedia Commons ghi giấy phép `PD-USGov-Military`).

| Tờ | Tệp trong repo | Nguồn gốc | Ghi chú |
|---|---|---|---|
| 5651 IV, Dien Bien Phu, series L7014, 1966 | `ams-5651-4.jpg` | Perry-Castañeda Library Map Collection, Đại học Texas: `https://maps.lib.utexas.edu/maps/topo/vietnam/dien_bien_phu-5651-4.pdf`. Bản sao Wikimedia Commons: `File:Map by the US Army Map Service - Dien Bien Phu - - vietnam - dien bien phu-5651-4.pdf` | ảnh 110 dpi từ trang đầu của PDF |
| 5551 I, Ban Thin Toc, series L7015 (Laos; Vietnam), 1968 | `ams-5551-1.jpg` | Perry-Castañeda Library Map Collection: `https://maps.lib.utexas.edu/maps/topo/laos/ban_thin_toc-laos-vietnam-50k.pdf` (9,5 MB). Bản sao Wikimedia Commons: `File:Map by the US Army Map Service - Ban Thin Toc - - laos - ban thin toc-laos-vietnam-50k.pdf` | tờ kề phía Tây tờ 5651 IV (102°45'-103°00'E). Trang UT chặn máy tải tự động; tải từ Commons |

Tái tạo `ams-5551-1.jpg` từ PDF đã tải (cần PyMuPDF): `python -I -X utf8 tools/nan-ban-do-ams.py --from-pdf-west <thư mục>/ban_thin_toc.pdf`.

Chú thích nguồn trên hình (`CREDIT_MAP3D_AMS` trong `map3d/places.js`) ghi cả hai tờ.

Tờ phía Nam 5651 III (Ban Na Phai) không cần: Hồng Cúm (khoảng 21,335°N) nằm trong tờ 5651 IV (21°15'-21°30'N).
