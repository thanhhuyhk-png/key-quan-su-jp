"""Thêm 2 tab vào sheet do xuat_sheet.py tạo (đủ 14 tab như bảng mẫu):
  «1b. Kênh mới nổi (làm theo)»: kênh dưới 400 ngày tuổi, xếp theo trung vị video dài đủ 7 ngày. Tuỳ chọn: chỉ thêm
      khi có bảng --moi-noi (TSV cột ten, tuoi_ngay, video_dai, short, dai_du_7_ngay, trung_vi_dai_7ngay, view_cao_nhat,
      sub, sub_moi_ngay, video_dai_moi_tuan, ghi_chu). Các kênh này «không đủ chỉ số» ở tab 1 vì chưa có 20 video đủ 30 ngày.
  «12. Video top 20 %»: mỗi kênh Giữ hoặc Theo dõi, 20 % video dài nhiều view nhất (tối thiểu 3 video).

Dùng: python them_tab.py <sheet.xlsx> --dinh-tinh <dinh-tinh.json> --video-dir <thư mục TSV của thu_video.py>
        --model <channel ID Model Link> [--moi-noi <kenh-moi-noi.tsv>] [--ngay-do 01/12/2026]
Chạy lại thì thay tab cũ, không nhân đôi.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Font, PatternFill

TAB_MOI_NOI = "1b. Kênh mới nổi (làm theo)"
TAB_VIDEO_TOP = "12. Video top 20 %"
DAM = Font(bold=True)
VANG = PatternFill("solid", fgColor="FFF2CC")
XANH = PatternFill("solid", fgColor="DDEBF7")


COT_MOI_NOI_BB = ("ten", "tuoi_ngay", "video_dai", "short", "dai_du_7_ngay", "trung_vi_dai_7ngay", "view_cao_nhat",
                  "sub", "sub_moi_ngay", "video_dai_moi_tuan")
COT_VIDEO_BB = ("id", "ngay_dang", "thoi_luong_s", "view", "like", "binh_luan", "is_short", "tieu_de")
DAU_CONG_THUC = ("=", "+", "-", "@")


class LoiDauVao(Exception):
    """Tệp đầu vào thiếu cột hoặc không đọc được: thoát mã 2."""


def doc_tsv(p: Path, cot_bat_buoc: tuple[str, ...] = ()) -> list[dict]:
    try:
        with open(p, encoding="utf-8-sig", newline="") as f:
            doc = csv.DictReader(f, delimiter="\t")
            bang = list(doc)
            thieu = [c for c in cot_bat_buoc if c not in (doc.fieldnames or [])]
    except (OSError, UnicodeDecodeError) as e:
        raise LoiDauVao(f"không đọc được {p}: {e}") from e
    if thieu:
        raise LoiDauVao(f"tệp {p} thiếu cột: {', '.join(thieu)}")
    return bang


def so(x, kieu=int):
    """Ép số mềm: '400.0', '1,234', khoảng trắng đều được; ô trống hoặc không phải số thì None."""
    if x is None:
        return None
    t = str(x).strip().replace(",", "")
    if not t:
        return None
    try:
        return kieu(float(t))
    except ValueError:
        return None


def ghi_chu_la_chu(ws) -> None:
    """Ô chữ bắt đầu bằng = + - @ ghi dạng chữ, không thành công thức."""
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith(DAU_CONG_THUC):
                c.data_type = "s"


def tab_moi_noi(wb: openpyxl.Workbook, bang: list[dict], dinh_tinh: dict, model: str, ngay_do: str) -> None:
    ten_id = {k.get("ten"): cid for cid, k in dinh_tinh.items()}
    ws = wb.create_sheet(TAB_MOI_NOI, 2)
    ws.append(["Kênh mới nổi (dưới 400 ngày từ video đầu): «làm theo kênh nhỏ»; xếp theo trung vị video dài đủ 7 ngày tuổi"])
    ws.append([f"Đo {ngay_do}. Bảng xếp hạng chuẩn cần ≥ 20 video đủ 30 ngày nên các kênh này «không đủ chỉ số» ở tab 1."])
    ws.append(["Thứ tự", "Model Link", "Tên kênh", "Link", "Tuổi kênh (ngày)", "Video dài", "Shorts", "Video dài đủ 7 ngày",
               "Trung vị video dài ≥ 7 ngày", "View cao nhất", "Sub", "Sub/ngày", "Video dài/tuần", "Giữ/Loại", "Học gì",
               "Không học gì", "Chú ý"])
    for c in ws[3]:
        c.font = DAM
    for i, r in enumerate(bang, 1):
        cid = ten_id.get(r["ten"], "")
        k = dinh_tinh.get(cid, {})
        ws.append([i, "★ MODEL LINK" if cid == model else "", r["ten"], k.get("link", ""), so(r["tuoi_ngay"]),
                   so(r["video_dai"]), so(r["short"]), so(r["dai_du_7_ngay"]),
                   so(r["trung_vi_dai_7ngay"]) if r["trung_vi_dai_7ngay"] else "chưa đủ video 7 ngày",
                   so(r["view_cao_nhat"]), so(r["sub"]), so(r["sub_moi_ngay"], float), so(r["video_dai_moi_tuan"], float),
                   k.get("giu_loai", ""), k.get("hoc_gi", ""), k.get("khong_hoc_gi", ""),
                   "; ".join(x for x in (r.get("ghi_chu", ""), k.get("chu_y", "")) if x)])
        if cid == model:
            for c in ws[ws.max_row]:
                c.fill = VANG


def tab_video_top(wb: openpyxl.Workbook, dinh_tinh: dict, video_dir: Path, model: str, ngay_do: str) -> None:
    ws = wb.create_sheet(TAB_VIDEO_TOP)
    ws.append([f"20 % video dài nhiều view nhất của mỗi kênh Giữ hoặc Theo dõi (tối thiểu 3 video); số đo {ngay_do}"])
    ws.append(["Kênh", "Hạng view trong kênh", "Link", "Tiêu đề", "Ngày đăng", "Phút", "View", "Like", "Bình luận"])
    for c in ws[2]:
        c.font = DAM
    for cid, k in dinh_tinh.items():
        tsv = video_dir / f"{cid}.tsv"
        if k.get("giu_loai") not in ("Giữ", "Theo dõi") or not tsv.exists():
            continue
        dai = [r for r in doc_tsv(tsv, COT_VIDEO_BB) if r["is_short"] == "0"]
        if not dai:
            continue
        n = min(len(dai), max(3, math.ceil(len(dai) * 0.2)))
        ws.append([f"{'★ ' if cid == model else ''}{k.get('ten', cid)} — {n}/{len(dai)} video dài"])
        for c in ws[ws.max_row]:
            c.font, c.fill = DAM, XANH
        for i, r in enumerate(sorted(dai, key=lambda r: -(so(r["view"]) or 0))[:n], 1):
            ws.append([k.get("ten", cid), i, f"https://youtu.be/{r['id']}", r["tieu_de"], r["ngay_dang"][:10],
                       round((so(r["thoi_luong_s"]) or 0) / 60), so(r["view"]), so(r["like"]), so(r["binh_luan"])])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sheet", type=Path)
    ap.add_argument("--dinh-tinh", type=Path, required=True, help="dinh-tinh.json (id kênh → ten, link, giu_loai, ...)")
    ap.add_argument("--video-dir", type=Path, required=True, help="thư mục <id kênh>.tsv do thu_video.py ghi")
    ap.add_argument("--model", required=True, help="channel ID của Model Link")
    ap.add_argument("--moi-noi", type=Path, help="bảng kênh mới nổi (TSV); không có thì bỏ qua tab 1b")
    ap.add_argument("--ngay-do", default="(chưa ghi ngày đo)", help="ngày đo ghi lên tab, vd 01/12/2026")
    a = ap.parse_args(argv)
    for p in (a.sheet, a.dinh_tinh, a.video_dir, *([a.moi_noi] if a.moi_noi else [])):
        if not p.exists():
            print(f"Lỗi: không thấy {p}", file=sys.stderr)
            return 2
    try:
        dinh_tinh = json.loads(a.dinh_tinh.read_text(encoding="utf-8"))
        wb = openpyxl.load_workbook(a.sheet)
        for t in (TAB_MOI_NOI, TAB_VIDEO_TOP):
            if t in wb.sheetnames:
                del wb[t]
        if a.moi_noi:
            tab_moi_noi(wb, doc_tsv(a.moi_noi, COT_MOI_NOI_BB), dinh_tinh, a.model, a.ngay_do)
        else:
            print("Không có --moi-noi: bỏ qua tab 1b (Kênh mới nổi).")
        tab_video_top(wb, dinh_tinh, a.video_dir, a.model, a.ngay_do)
    except LoiDauVao as e:
        print(f"Lỗi: {e}", file=sys.stderr)
        return 2
    except (OSError, ValueError) as e:
        print(f"Lỗi: không đọc được đầu vào: {e}", file=sys.stderr)
        return 2
    for t in (TAB_MOI_NOI, TAB_VIDEO_TOP):
        if t in wb.sheetnames:
            ghi_chu_la_chu(wb[t])
    tam = a.sheet.with_name(a.sheet.stem + ".part.xlsx")
    try:
        wb.save(tam)
        os.replace(tam, a.sheet)
    finally:
        tam.unlink(missing_ok=True)
    print(f"{a.sheet}: {len(wb.sheetnames)} tab: {', '.join(wb.sheetnames)}")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
