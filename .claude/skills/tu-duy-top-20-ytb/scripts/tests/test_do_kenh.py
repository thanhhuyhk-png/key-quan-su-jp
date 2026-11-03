"""Test cho do_kenh.py: chỉ số kênh theo chuẩn Top 20 + hiệu suất chuẩn hoá."""
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import do_kenh as dk  # noqa: E402

AS_OF = date(2026, 10, 22)


def mk(n_days_ago, views, likes=None, comments=10, dur=1200, vid=None):
    d = AS_OF - timedelta(days=n_days_ago)
    return dk.Video(
        id=vid or f"v{n_days_ago}",
        title="t",
        published=d,
        views=views,
        likes=likes if likes is not None else max(1, views // 100),
        comments=comments,
        duration_s=dur,
    )


# ---------- đọc file ----------

def test_doc_tsv_bang_ten_cot_tieng_viet(tmp_path):
    p = tmp_path / "ds.tsv"
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["id", "ngay_dang", "thoi_luong_s", "view", "like", "binh_luan", "tieu_de"])
        w.writerow(["a1", "2026-09-13", "1258", "809756", "6176", "324", "Video mẫu"])
    vids = dk.doc_video(p)
    assert len(vids) == 1
    v = vids[0]
    assert v.views == 809756 and v.likes == 6176 and v.duration_s == 1258
    assert v.published == date(2026, 9, 13)


def test_doc_csv_ten_cot_tieng_anh(tmp_path):
    p = tmp_path / "ds.csv"
    p.write_text("video_id,published,duration,views,likes,comments,title\n"
                 "b1,2026-10-01,45,12000,300,5,short\n", encoding="utf-8")
    v = dk.doc_video(p)[0]
    assert v.id == "b1" and v.views == 12000 and v.is_short


def test_doc_so_co_dau_cham_phay_va_chu_N():
    assert dk.so("1.234.567") == 1234567
    assert dk.so("809 N") == 809000
    assert dk.so("1,2 Tr") == 1200000
    assert dk.so("") is None
    assert dk.so("1258.0") == 1258
    assert dk.so("1,234,567") == 1234567
    assert dk.so("3.4K") == 3400


# ---------- trung vị video dài đủ tuổi ----------

def test_trung_vi_bo_short_va_video_duoi_30_ngay():
    vids = [mk(40 + i, 1000 * (i + 1)) for i in range(5)]  # 1000..5000, đủ tuổi
    vids += [mk(5, 999_999)]                                # quá non, bỏ
    vids += [mk(60, 888_888, dur=40)]                       # Short, bỏ
    m = dk.chi_so_kenh(vids, subs=10_000, as_of=AS_OF)
    assert m["trung_vi_20_dai"] == 3000
    assert m["n_dai_dung_tinh"] == 5
    assert m["n_short"] == 1


def test_chi_lay_20_video_dai_gan_nhat():
    vids = [mk(31 + i, 100 if i < 20 else 1_000_000) for i in range(30)]
    m = dk.chi_so_kenh(vids, subs=1000, as_of=AS_OF)
    assert m["trung_vi_20_dai"] == 100


def test_trung_vi_chia_sub_va_lap_lai_va_phan_tan():
    vids = [mk(31 + i, v) for i, v in enumerate([100] * 15 + [300] * 4 + [5000])]
    m = dk.chi_so_kenh(vids, subs=1000, as_of=AS_OF)
    assert m["trung_vi_20_dai"] == 100
    assert m["trung_vi_chia_sub"] == pytest.approx(0.10)
    assert m["so_video_tren_2x"] == 5
    assert m["phan_tan"] == pytest.approx(50.0)
    assert "PHAN_TAN_CAO" in m["co"]


# ---------- hệ số vượt trội ----------

def test_he_so_vuot_troi_dung_15_video_truoc():
    # 16 video cũ hơn, cách nhau 1 ngày; video mới nhất là video cần đo
    vids = [mk(100 - i, 1000) for i in range(16)]
    vids.append(mk(60, 12_000, vid="hit"))
    vids += [mk(50 - i, 3000) for i in range(5)]  # 5 video sau
    hs = {r["id"]: r for r in dk.he_so_vuot_troi(vids)}
    assert hs["hit"]["he_so"] == pytest.approx(12.0)
    assert hs["hit"]["n_truoc"] == 15
    assert hs["hit"]["he_so_sau"] == pytest.approx(3.0)
    assert hs["hit"]["muc"] == "can_kiem_ky"  # > 10


def test_he_so_khi_it_hon_5_video_truoc_thi_khong_tinh():
    vids = [mk(100 - i, 1000) for i in range(3)] + [mk(50, 9000, vid="x")]
    hs = {r["id"]: r for r in dk.he_so_vuot_troi(vids)}
    assert hs["x"]["he_so"] is None
    assert hs["x"]["n_truoc"] == 3


def test_muc_he_so():
    assert dk.muc_he_so(1.5) == "binh_thuong"
    assert dk.muc_he_so(4) == "dang_ghi"
    assert dk.muc_he_so(2.5) == "hoi_cao"
    assert dk.muc_he_so(5) == "manh"
    assert dk.muc_he_so(10) == "can_kiem_ky"
    assert dk.muc_he_so(7) == "manh"
    assert dk.muc_he_so(11) == "can_kiem_ky"


# ---------- hiệu suất chuẩn hoá ----------

def test_hieu_suat_theo_tuoi_kenh_tinh_tu_video_dau_va_ngay_lap():
    vids = [mk(48 - 2 * i, 200_000) for i in range(22)]  # video đầu cách 48 ngày
    m = dk.chi_so_kenh(vids, subs=38_000, as_of=AS_OF, ngay_lap=AS_OF - timedelta(days=62))
    assert m["tuoi_tu_video_dau"] == 48
    assert m["tuoi_tu_ngay_lap"] == 62
    assert m["sub_moi_video"] == pytest.approx(38_000 / 22)
    assert m["sub_moi_ngay_video_dau"] == pytest.approx(38_000 / 48)
    assert m["sub_moi_ngay_ngay_lap"] == pytest.approx(38_000 / 62)
    assert m["view_moi_ngay_video_dau"] == pytest.approx(22 * 200_000 / 48)


# ---------- cờ bẫy số liệu ----------

def test_co_nghi_loi_don_vi_khi_like_lon_hon_view():
    vids = [mk(40 + i, 809, likes=6176) for i in range(6)]
    m = dk.chi_so_kenh(vids, subs=38, as_of=AS_OF)
    assert "NGHI_LOI_DON_VI" in m["co"]


def test_co_it_video_va_nhieu_short_va_trung_ngay():
    vids = [mk(40, 1000, dur=30, vid=f"s{i}") for i in range(6)]  # 6 Short cùng ngày
    vids += [mk(41, 1000, vid="d1")]
    m = dk.chi_so_kenh(vids, subs=100, as_of=AS_OF)
    assert "IT_VIDEO" in m["co"]
    assert "NHIEU_SHORT" in m["co"]
    assert "NHIEU_VIDEO_CUNG_NGAY" in m["co"]


# ---------- xếp hạng nhiều kênh ----------

def test_xep_hang_kenh_it_video_sub_nhieu_len_dau_va_co_do_nhay():
    kenh = {
        "kenh_moi": dk.chi_so_kenh([mk(48 - 2 * i, 200_000) for i in range(22)], subs=38_000,
                                   as_of=AS_OF, ngay_lap=AS_OF - timedelta(days=62)),
        "kenh_cu": dk.chi_so_kenh([mk(40 + 3 * i, 300_000) for i in range(300)], subs=200_000,
                                  as_of=AS_OF, ngay_lap=AS_OF - timedelta(days=900)),
        "kenh_yeu": dk.chi_so_kenh([mk(40 + i, 5_000) for i in range(80)], subs=20_000,
                                   as_of=AS_OF, ngay_lap=AS_OF - timedelta(days=700)),
    }
    bang = dk.xep_hang(kenh)
    assert bang[0]["kenh"] == "kenh_moi"
    assert bang[-1]["kenh"] == "kenh_yeu"
    r = {b["kenh"]: b for b in bang}
    assert "hang_theo_ngay_lap" in r["kenh_moi"]
    assert r["kenh_moi"]["it_video_sub_nhieu"] is True
    assert r["kenh_cu"]["it_video_sub_nhieu"] is False
