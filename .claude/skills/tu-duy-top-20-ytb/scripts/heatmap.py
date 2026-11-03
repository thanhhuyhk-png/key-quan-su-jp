"""Đọc đường "Được phát lại nhiều nhất" (Most replayed) của YouTube từ JSON yt-dlp.

Lấy dữ liệu (chạy TUẦN TỰ, không song song kẻo YouTube chặn IP; không dùng cookie trình duyệt):
  yt-dlp --skip-download --write-info-json -o "%(id)s" <link>
Dùng:
  python heatmap.py <id.info.json> [<id2.info.json> ...] [--so-dinh 3] [--bo-dau 3] [--cach 5] [--out heatmap.md]

Giới hạn: YouTube chỉ trả heatmap khi video đủ lượt xem lại; giá trị là TƯƠNG ĐỐI (đỉnh = 1),
không phải tỉ lệ giữ chân thật. Nó cho biết đoạn nào được tua lại xem nhiều, không cho biết % người còn ở lại.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DO_PHANG = 0.05   # đỉnh − đáy < 0,05 thì coi như đường phẳng, không báo đỉnh


def doc(path: Path) -> dict:
    d = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    return {"id": d.get("id"), "title": d.get("title", ""), "duration": d.get("duration"),
            "heatmap": d.get("heatmap") or []}


def _moc(giay: float) -> str:
    g = int(round(giay))
    return f"{g // 3600}:{g % 3600 // 60:02d}:{g % 60:02d}" if g >= 3600 else f"{g // 60:02d}:{g % 60:02d}"


def phan_tich(info: dict, so_dinh: int = 3, bo_dau_phan_tram: float = 3.0, cach_phan_tram: float = 5.0) -> dict:
    """Đỉnh = cực đại cục bộ (≥ hai bên), xếp theo giá trị, cách nhau ≥ cach_phan_tram % thời lượng,
    bỏ bo_dau_phan_tram % đầu (người mới vào luôn cao). Mốc đỉnh = trung điểm khoảng."""
    kq = {"id": info.get("id"), "title": info.get("title", ""), "co_du_lieu": False, "dinh": [],
          "nua_sau_chia_nua_dau": None, "ghi_chu": ""}
    hm = [h for h in (info.get("heatmap") or [])
          if isinstance(h, dict) and isinstance(h.get("value"), (int, float))
          and h.get("start_time") is not None and h.get("end_time") is not None]
    if not hm:
        kq["ghi_chu"] = "YouTube không trả heatmap (video chưa đủ lượt xem lại hoặc bị chặn); không suy đoán."
        return kq
    dur = info.get("duration") or hm[-1]["end_time"]
    if not dur or dur <= 0:
        kq["ghi_chu"] = "Thiếu thời lượng video; không tính được %."
        return kq
    kq["co_du_lieu"] = True
    vals = [h["value"] for h in hm]
    if max(vals) - min(vals) < DO_PHANG:
        kq["ghi_chu"] = "Đường gần như phẳng; không có đỉnh rõ."
    elif so_dinh > 0:
        diem = []
        for i, h in enumerate(hm):
            trai = vals[i - 1] if i > 0 else -1
            phai = vals[i + 1] if i + 1 < len(vals) else -1
            giua = (h["start_time"] + h["end_time"]) / 2
            if h["value"] >= trai and h["value"] >= phai and 100 * giua / dur >= bo_dau_phan_tram:
                diem.append((giua, h["value"]))
        diem.sort(key=lambda d: d[1], reverse=True)
        chon: list[tuple] = []
        for g, v in diem:
            if len(chon) >= so_dinh:
                break
            if all(abs(g - c[0]) * 100 / dur >= cach_phan_tram for c in chon):
                chon.append((g, v))
        kq["dinh"] = [{"phan_tram": 100 * g / dur, "giay": g, "moc": _moc(g), "gia_tri": v} for g, v in chon]
    giua_video = dur / 2
    dau = [h["value"] for h in hm if (h["start_time"] + h["end_time"]) / 2 < giua_video]
    sau = [h["value"] for h in hm if (h["start_time"] + h["end_time"]) / 2 >= giua_video]
    if dau and sau and sum(dau):
        kq["nua_sau_chia_nua_dau"] = round((sum(sau) / len(sau)) / (sum(dau) / len(dau)), 2)
    return kq


def _o(x) -> str:
    return "–" if x is None else str(x).replace("|", "\\|").replace("\n", " ")


def main(argv=None) -> int:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--so-dinh", type=int, default=3)
    ap.add_argument("--bo-dau", type=float, default=3.0, help="bỏ %% đầu video (người mới vào luôn cao)")
    ap.add_argument("--cach", type=float, default=5.0, help="khoảng cách tối thiểu giữa hai đỉnh, %% thời lượng")
    ap.add_argument("--out")
    ns = ap.parse_args(argv)
    dong = ["| video | có dữ liệu | đỉnh (mốc · % thời lượng · giá trị) | nửa sau / nửa đầu | ghi chú |",
            "|---|---|---|---|---|"]
    for f in ns.files:
        try:
            kq = phan_tich(doc(Path(f)), ns.so_dinh, ns.bo_dau, ns.cach)
        except (OSError, ValueError, KeyError, TypeError) as e:
            dong.append(f"| {_o(Path(f).name)} | lỗi đọc | – | – | {_o(e)} |")
            continue
        d = "; ".join(f"{x['moc']} · {x['phan_tram']:.0f} % · {x['gia_tri']:.2f}" for x in kq["dinh"]) or "–"
        dong.append(f"| {_o(kq['id'])} {_o((kq.get('title') or '')[:40])} | {'có' if kq['co_du_lieu'] else 'không'} "
                    f"| {d} | {_o(kq['nua_sau_chia_nua_dau'])} | {_o(kq['ghi_chu'])} |")
    out = "\n".join(dong) + "\n"
    if ns.out:
        Path(ns.out).parent.mkdir(parents=True, exist_ok=True)
        Path(ns.out).write_text(out, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
