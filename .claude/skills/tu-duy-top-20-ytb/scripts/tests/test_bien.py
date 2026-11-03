"""Test trường hợp biên theo phản biện (phản biện độc lập) 22/10/2026."""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import openpyxl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import do_kenh as dk  # noqa: E402
import heatmap as hm  # noqa: E402
import xuat_sheet as xs  # noqa: E402

AS_OF = date(2026, 10, 22)


def mk(n_days_ago, views, dur=1200, vid=None, short=None, likes=None):
    return dk.Video(id=vid or f"v{n_days_ago}_{views}", title="t", published=AS_OF - timedelta(days=n_days_ago),
                    views=views, likes=likes if likes is not None else max(1, views // 100), comments=1,
                    duration_s=dur, is_short_flag=short)


# ---------- đọc số / ngày / file ----------

@pytest.mark.parametrize("vao,ra", [("nan", None), ("n/a", None), ("-5", None), ("ẩn", None), ("1 triệu", 1_000_000),
                                    ("0.123", 0), ("12.345", 12345), ("1,234.5K", None), ("2 tỷ", 2_000_000_000),
                                    ("38K", 38_000), ("38.000", 38_000)])
def test_so_bien(vao, ra):
    assert dk.so(vao) == ra


def test_thoi_luong_dang_gio_phut():
    assert dk.thoi_luong("20:58") == 1258
    assert dk.thoi_luong("1:02:03") == 3723
    assert dk.thoi_luong("PT20M58S") == 1258


def test_doc_ngay_kieu_viet_va_iso_ngan():
    assert dk.doc_ngay("22/10/2026").date() == date(2026, 10, 22)
    assert dk.doc_ngay("2026-9-3").date() == date(2026, 9, 3)
    assert dk.doc_ngay("rác") is None


def test_doc_video_file_rong_trung_id_thieu_view(tmp_path):
    p = tmp_path / "rong.tsv"
    p.write_text("", encoding="utf-8")
    assert dk.doc_video(p) == []
    p2 = tmp_path / "ds.tsv"
    p2.write_text("id\tngay_dang\tview\tthoi_luong_s\n"
                  "a\t2026-09-01\t100\t1200\n"
                  "a\t2026-09-01\t150\t1200\n"
                  "b\t2026-09-02\t\t1200\n"
                  "c\t22/09/2026\t1.234\t20:00\n", encoding="utf-8")
    tk = {}
    vids = dk.doc_video(p2, tk)
    assert sorted(v.id for v in vids) == ["a", "c"]
    assert next(v for v in vids if v.id == "a").views == 150
    assert tk["bo_trung_id"] == 1 and tk["bo_thieu_view_ngay"] == 1
    assert next(v for v in vids if v.id == "c").duration_s == 1200


# ---------- Shorts ----------

def test_co_is_short_false_thang_thoi_luong_ngan():
    v = mk(40, 1000, dur=150, short=False)
    assert v.is_short is False
    assert mk(40, 1000, dur=150).is_short is True


def test_kenh_lai_shorts_khong_dung_chi_so_theo_sub():
    vids = [mk(40 + i, 1000) for i in range(12)] + [mk(40 + i, 50_000, dur=40, vid=f"s{i}") for i in range(5)]
    m = dk.chi_so_kenh(vids, subs=100_000, as_of=AS_OF)
    assert "SUB_LAN_SHORTS" in m["co"]
    assert m["sub_moi_video"] is None and m["sub_moi_video_tho"] is not None


# ---------- chỉ số kênh ----------

def test_trung_vi_can_it_nhat_5_video_va_co_mau_nho():
    m = dk.chi_so_kenh([mk(40 + i, 1000) for i in range(3)], subs=1000, as_of=AS_OF)
    assert m["trung_vi_20_dai"] is None and "KHONG_DU_VIDEO_DAI_DU_30_NGAY" in m["co"]
    m2 = dk.chi_so_kenh([mk(40 + i, 1000) for i in range(6)], subs=1000, as_of=AS_OF)
    assert m2["trung_vi_20_dai"] == 1000 and "MAU_TRUNG_VI_NHO" in m2["co"]


def test_sub_bang_0_khong_thanh_none():
    m = dk.chi_so_kenh([mk(40 + i, 1000) for i in range(12)], subs=0, as_of=AS_OF)
    assert m["sub_moi_video"] == 0


def test_danh_sach_bi_cat_va_tong_video_that():
    vids = [mk(31 + i, 1000) for i in range(50)]
    m = dk.chi_so_kenh(vids, subs=600_000, as_of=AS_OF)
    assert "DANH_SACH_CO_THE_BI_CAT" in m["co"]
    m2 = dk.chi_so_kenh(vids, subs=600_000, as_of=AS_OF, tong_video=600, ngay_video_dau=AS_OF - timedelta(days=1800))
    assert m2["sub_moi_video"] == 1000
    assert m2["tuoi_tu_video_dau"] == 1800
    assert "DANH_SACH_THIEU_VIDEO" in m2["co"]


def test_da_trung_vi_va_tang_30_ngay():
    vids = [mk(31 + i, 2000 if i < 10 else 1000) for i in range(20)]
    m = dk.chi_so_kenh(vids, subs=10_000, as_of=AS_OF, sub_30_ngay_truoc=8_000)
    assert m["da_trung_vi"] == pytest.approx(2.0)
    assert m["tang_sub_30"] == 2000 and m["pct_tang_sub_30"] == pytest.approx(0.25)


def test_ngay_tuong_lai_bi_loai_va_co():
    m = dk.chi_so_kenh([mk(40 + i, 1000) for i in range(6)] + [mk(-3, 5)], subs=10, as_of=AS_OF)
    assert "NGAY_TUONG_LAI" in m["co"] and m["n_trong_danh_sach"] == 6


# ---------- hệ số ----------

def test_he_so_sau_can_du_5_va_video_non_la_chua_chin():
    vids = [mk(200 - i, 1000) for i in range(15)] + [mk(100, 9000, vid="x")] + [mk(90, 1000, vid="y")]
    r = {h["id"]: h for h in dk.he_so_vuot_troi(vids, AS_OF)}
    assert r["x"]["he_so"] == pytest.approx(9.0) and r["x"]["he_so_sau"] is None and r["x"]["n_sau"] == 1
    vids2 = [mk(200 - i, 1000) for i in range(15)] + [mk(10, 9000, vid="non")]
    r2 = {h["id"]: h for h in dk.he_so_vuot_troi(vids2, AS_OF)}
    assert r2["non"]["muc"] == "chua_chin" and r2["non"]["tuoi_ngay"] == 10


# ---------- xếp hạng ----------

def test_kenh_thieu_chi_so_khong_bi_xep_cuoi_ma_khong_xep():
    kenh = {
        "moi": dk.chi_so_kenh([mk(5 + i, 50_000) for i in range(12)], subs=30_000, as_of=AS_OF),
        "a": dk.chi_so_kenh([mk(40 + i, 3000) for i in range(30)], subs=5000, as_of=AS_OF),
        "b": dk.chi_so_kenh([mk(40 + i, 2000) for i in range(30)], subs=4000, as_of=AS_OF),
    }
    bang = {b["kenh"]: b for b in dk.xep_hang(kenh)}
    assert bang["moi"]["diem"] is None and bang["moi"]["hang"] is None
    assert "KHONG_DU_CHI_SO" in bang["moi"]["co"]
    assert bang["a"]["hang"] == 1


def test_kenh_tre_ha_nguong_tuoi_video():
    vids = [mk(15 + 2 * i, 40_000) for i in range(12)]   # kênh 37 ngày tuổi, video 15–37 ngày
    m = dk.chi_so_kenh(vids, subs=30_000, as_of=AS_OF)
    assert m["nguong_tuoi_video"] == 14 and m["trung_vi_20_dai"] == 40_000
    assert "TRUNG_VI_DUNG_VIDEO_TU_14_NGAY" in m["co"]


def test_dong_diem_dong_hang_va_khong_ngay_lap_thi_none():
    m = dk.chi_so_kenh([mk(40 + i, 1000) for i in range(25)], subs=1000, as_of=AS_OF)
    bang = dk.xep_hang({"x": dict(m), "y": dict(m), "z": dk.chi_so_kenh([mk(40 + i, 10) for i in range(25)],
                                                                      subs=10, as_of=AS_OF)})
    h = {b["kenh"]: b for b in bang}
    assert h["x"]["hang"] == h["y"]["hang"] == 1
    assert h["z"]["hang"] == 3
    assert h["x"]["hang_theo_ngay_lap"] is None


def test_xep_hang_rong():
    assert dk.xep_hang({}) == []


# ---------- heatmap ----------

def _hm(vals, dur=1000.0):
    step = dur / len(vals)
    return {"id": "v", "duration": dur,
            "heatmap": [{"start_time": i * step, "end_time": (i + 1) * step, "value": v} for i, v in enumerate(vals)]}


def test_heatmap_khong_lay_suon_doc_lam_dinh_thu_hai():
    vals = [0.1] * 100
    for i, v in enumerate([1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7]):
        vals[50 + i] = v
    vals[80] = 0.5
    kq = hm.phan_tich(_hm(vals), so_dinh=2)
    assert [d["phan_tram"] for d in kq["dinh"]] == [50.5, 80.5]


def test_heatmap_bien():
    assert hm.phan_tich(_hm([0.3] * 100))["dinh"] == []          # phẳng
    assert hm.phan_tich(_hm([0.1, 0.9, 0.1]), so_dinh=0)["dinh"] == []
    assert hm.phan_tich(_hm([0.1, 0.9, 0.1], dur=0))["co_du_lieu"] is False


def test_heatmap_doc_bom(tmp_path):
    p = tmp_path / "v.info.json"
    p.write_text(json.dumps({"id": "a", "duration": 10, "heatmap": []}), encoding="utf-8-sig")
    assert hm.doc(p)["id"] == "a"


# ---------- xuất sheet ----------

def _hs(**them):
    kenh = [{"id": f"k{i}", "ten": f"Kênh {i}", "link": f"https://www.youtube.com/@k{i}", "subs": 1000 * (30 - i),
             "diem": 100 - i, "giu_loai": "giữ", "nguon_so": "test"} for i in range(1, 25)]
    hs = {"du_an": "T", "ngay_do": "2026-10-22", "kenh": kenh, "video": [], "model_link": {"kenh": "k1"}}
    hs.update(them)
    return hs


def _xuat(tmp_path, hs, bom=False):
    p = tmp_path / "hs.json"
    p.write_text(json.dumps(hs, ensure_ascii=False), encoding="utf-8-sig" if bom else "utf-8")
    out = tmp_path / "con" / "chau" / "t.xlsx"
    _, kiem = xs.xuat(p, out)
    return openpyxl.load_workbook(out), kiem


def test_chong_cong_thuc_bom_hang_null_co_list(tmp_path):
    hs = _hs()
    hs["kenh"][0]["ten"] = '=HYPERLINK("http://x","y")'
    hs["kenh"][0]["hang"] = None
    hs["kenh"][0]["co"] = ["A", "B"]
    wb, _ = _xuat(tmp_path, hs, bom=True)
    ws = wb[xs.TEN_TAB[1]]
    hdr = [c.value for c in ws[xs.DONG_TIEU_DE]]
    o = ws.cell(xs.DONG_TIEU_DE + 1, hdr.index("Tên kênh") + 1)
    assert o.data_type == "s" and o.value.startswith("=HYPERLINK")
    assert ws.cell(xs.DONG_TIEU_DE + 1, 1).value == 1
    assert ws.cell(xs.DONG_TIEU_DE + 1, hdr.index("Cờ dữ liệu") + 1).value == "A, B"


def test_lan_do_dau_khong_gan_vao_top_moi(tmp_path):
    wb, _ = _xuat(tmp_path, _hs())
    ws = wb[xs.TEN_TAB[3]]
    hdr = [c.value for c in ws[xs.DONG_TIEU_DE]]
    st = {r[hdr.index("Trạng thái TOP 20")] for r in ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1, values_only=True)}
    assert "Vào TOP mới" not in st and "Chưa có mốc trước" in st


def test_kiem_tu_dong_bao_thieu_video_top_va_muc_cao_hoa_thuong(tmp_path):
    hs = _hs(chu_y=[{"loai": "gioi_han", "noi_dung": "X", "muc_do": "Cao"}])
    wb, kiem = _xuat(tmp_path, hs)
    assert any("chưa có video top" in k["noi_dung"] for k in kiem)
    ws = wb[xs.TEN_TAB[10]]
    dong = [r for r in ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1) if r[1].value == "X"][0]
    assert dong[0].fill.fgColor.rgb == xs.DO_NHAT


def test_nhan_ban_diem_thuc_va_ngoai_mien(tmp_path):
    hs = _hs(nhan_ban=[{"video_goc": "a", "diem": {"nhu_cau": 4.0, "bang_chung": "4", "khoang_trong": 4,
                                                   "hop_khan_gia": 4, "chi_phi": 4, "rui_ro": 4}},
                       {"video_goc": "b", "diem": {"nhu_cau": 7, "bang_chung": 4, "khoang_trong": 4,
                                                   "hop_khan_gia": 4, "chi_phi": 4, "rui_ro": 4}}])
    wb, _ = _xuat(tmp_path, hs)
    ws = wb[xs.TEN_TAB[7]]
    hdr = [c.value for c in ws[xs.DONG_TIEU_DE]]
    rows = list(ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1, values_only=True))
    assert rows[0][hdr.index("Tổng điểm cơ hội (/30)")] == 24
    assert rows[1][hdr.index("Tổng điểm cơ hội (/30)")] is None


def test_nhan_ten_truong_cua_do_kenh(tmp_path):
    hs = _hs()
    hs["kenh"][0].update({"n_video": 22, "tuoi_tu_video_dau": 48, "sub_moi_ngay_video_dau": 794})
    wb, _ = _xuat(tmp_path, hs)
    ws = wb[xs.TEN_TAB[1]]
    hdr = [c.value for c in ws[xs.DONG_TIEU_DE]]
    r = next(ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1, values_only=True))
    assert r[hdr.index("Số video")] == 22 and r[hdr.index("Sub/ngày")] == 794
