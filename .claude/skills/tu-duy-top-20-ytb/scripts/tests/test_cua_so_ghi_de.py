"""Test cửa sổ video, tỉ trọng Shorts từ nguồn ngoài, ghi đè có lý do, độ nhạy xếp hạng, cờ mới."""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import do_kenh as dk  # noqa: E402

AS_OF = date(2026, 10, 22)


def mk(n_days_ago, views, dur=1200, vid=None, short=None, likes=None):
    return dk.Video(id=vid or f"v{n_days_ago}_{views}", title="t", published=AS_OF - timedelta(days=n_days_ago),
                    views=views, likes=likes if likes is not None else max(1, views // 100), comments=1,
                    duration_s=dur, is_short_flag=short)


# ---------- cửa sổ ----------

def _kenh_co_video_xa():
    trong = [mk(100 - i, 1000, vid=f"t{i}") for i in range(20)]            # 100..81 ngày trước
    xa = [mk(300 - i, 100_000, vid=f"x{i}") for i in range(5)]             # nổi tiếng nhưng ngoài cửa sổ
    return trong, xa, AS_OF - timedelta(days=110)


def test_he_so_ngoai_cua_so_la_none_co_ly_do_va_khong_lam_hang_xom():
    trong, xa, cs = _kenh_co_video_xa()
    hs = {h["id"]: h for h in dk.he_so_vuot_troi(trong + xa, AS_OF, cua_so_tu=cs)}
    assert hs["x0"]["he_so"] is None and hs["x0"]["ly_do_khong_tinh"] == "ngoai_cua_so"
    assert hs["t0"]["n_truoc"] == 0 and hs["t0"]["he_so"] is None      # không mượn 5 video xa làm hàng xóm
    assert hs["t5"]["n_truoc"] == 5 and hs["t5"]["he_so"] == pytest.approx(1.0)
    assert hs["t5"]["ly_do_khong_tinh"] is None
    assert hs["t1"]["ly_do_khong_tinh"] == "it_hon_5_video_truoc"


def test_khong_co_cua_so_thi_video_xa_van_lam_hang_xom_nhu_cu():
    trong, xa, _ = _kenh_co_video_xa()
    hs = {h["id"]: h for h in dk.he_so_vuot_troi(trong + xa, AS_OF)}
    assert hs["t0"]["n_truoc"] == 5 and hs["t0"]["he_so"] == pytest.approx(0.01)


def test_cua_so_khong_bat_danh_sach_thieu_video_va_chi_do_trong_cua_so():
    trong, xa, cs = _kenh_co_video_xa()
    m = dk.chi_so_kenh(trong + xa, subs=50_000, as_of=AS_OF, tong_video=900, cua_so_tu=cs,
                       ngay_video_dau=AS_OF - timedelta(days=1500))
    assert "DANH_SACH_THIEU_VIDEO" not in m["co"] and "DANH_SACH_CO_THE_BI_CAT" not in m["co"]
    assert m["trung_vi_20_dai"] == 1000                      # video xa không lọt vào trung vị
    assert m["n_ngoai_cua_so"] == 5 and m["cua_so_tu"] == cs.isoformat()
    assert m["n_trong_danh_sach"] == 20
    assert m["tuoi_tu_video_dau"] == 1500
    m2 = dk.chi_so_kenh(trong + xa, subs=50_000, as_of=AS_OF, tong_video=900,
                        ngay_video_dau=AS_OF - timedelta(days=1500))
    assert "DANH_SACH_THIEU_VIDEO" in m2["co"]               # không có cửa sổ thì vẫn báo như cũ


def test_cua_so_ngay_video_dau_mac_dinh_lay_tu_toan_danh_sach():
    trong, xa, cs = _kenh_co_video_xa()
    m = dk.chi_so_kenh(trong + xa, subs=1000, as_of=AS_OF, cua_so_tu=cs)
    assert m["tuoi_tu_video_dau"] == 300


# ---------- tỉ trọng Shorts từ nguồn ngoài ----------

def _kenh_lai(short_views):
    return [mk(40 + i, 10_000) for i in range(30)] + [mk(40 + i, short_views, dur=40, vid=f"s{i}") for i in range(3)]


def test_ty_trong_short_ngoai_uu_tien_hon_mau_khi_mau_noi_thap():
    vids = _kenh_lai(100)     # mẫu Shorts chỉ ~0,1 % view
    m = dk.chi_so_kenh(vids, subs=100_000, as_of=AS_OF, ty_trong_view_short=0.22)
    assert "SUB_LAN_SHORTS" in m["co"]
    assert m["ty_trong_view_short"] == pytest.approx(0.22) and m["ty_trong_view_short_nguon"] == "ngoai"
    assert m["ty_trong_view_short_mau"] < 0.01
    assert m["sub_moi_video"] is None and m["sub_moi_video_tho"] is not None


def test_ty_trong_short_ngoai_thap_go_bo_ket_luan_sai_cua_mau():
    vids = _kenh_lai(300_000)     # mẫu nói ~75 % nhưng nguồn ngoài (vidIQ 30 ngày) nói 1 %
    m = dk.chi_so_kenh(vids, subs=100_000, as_of=AS_OF, ty_trong_view_short=0.01)
    assert "SUB_LAN_SHORTS" not in m["co"]
    assert m["sub_moi_video"] is not None and m["ty_trong_view_short_nguon"] == "ngoai"
    m2 = dk.chi_so_kenh(vids, subs=100_000, as_of=AS_OF)
    assert "SUB_LAN_SHORTS" in m2["co"] and m2["ty_trong_view_short_nguon"] == "mau"


@pytest.mark.parametrize("gia_tri", ["22", "-0.1", "1.5", "abc"])
def test_tham_so_ty_trong_short_phai_trong_0_1(gia_tri, tmp_path, capsys):
    p = tmp_path / "ds.tsv"
    p.write_text("id\tngay_dang\tview\n" + "".join(f"a{i}\t2026-0{(i % 8) + 1}-01\t100\n" for i in range(8)), encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        dk.main(["kenh", str(p), "--subs", "1000", "--ty-trong-view-short", gia_tri])
    assert e.value.code == 2


# ---------- cờ mới ----------

def test_co_tai_sinh_khi_ngay_lap_cach_video_dau_hon_12_thang():
    vids = [mk(40 + i, 1000) for i in range(12)]
    dau = AS_OF - timedelta(days=51)
    m = dk.chi_so_kenh(vids, subs=100, as_of=AS_OF, ngay_lap=dau - timedelta(days=366), ngay_video_dau=dau)
    assert "TAI_SINH" in m["co"]
    m2 = dk.chi_so_kenh(vids, subs=100, as_of=AS_OF, ngay_lap=dau - timedelta(days=365), ngay_video_dau=dau)
    assert "TAI_SINH" not in m2["co"]
    m3 = dk.chi_so_kenh(vids, subs=100, as_of=AS_OF)
    assert "TAI_SINH" not in m3["co"]


def test_co_hoi_vien_va_dem():
    vids = [mk(40 + i, 1000) for i in range(12)]
    m = dk.chi_so_kenh(vids, subs=100, as_of=AS_OF, so_hoi_vien=19)
    assert "HOI_VIEN" in m["co"] and m["so_hoi_vien"] == 19
    assert "HOI_VIEN" not in dk.chi_so_kenh(vids, subs=100, as_of=AS_OF)["co"]


# ---------- trần và sàn cho đà ----------

def test_tran_100_phan_tram_cho_kenh_duoi_90_ngay_giu_ban_tho():
    vids = [mk(2 + 4 * i, 50_000) for i in range(15)]     # video đầu cách 58 ngày
    m = dk.chi_so_kenh(vids, subs=40_000, as_of=AS_OF, sub_30_ngay_truoc=13_202)
    assert m["tuoi_tu_video_dau"] == 58
    assert m["pct_tang_sub_30"] == pytest.approx(1.0)
    assert m["pct_tang_sub_30_tho"] == pytest.approx((40_000 - 13_202) / 13_202)
    assert "PCT_TANG_BI_CHAN_100" in m["co"]
    assert m["tang_sub_30"] == 40_000 - 13_202                              # số tuyệt đối không bị chạm


def test_kenh_tu_90_ngay_khong_bi_chan_tran():
    vids = [mk(2 + 10 * i, 50_000) for i in range(15)]    # 142 ngày
    m = dk.chi_so_kenh(vids, subs=40_000, as_of=AS_OF, sub_30_ngay_truoc=13_202)
    assert m["pct_tang_sub_30"] > 1.0 and "PCT_TANG_BI_CHAN_100" not in m["co"]


def test_san_sub_nen_cho_pct_tang_30_ngay():
    vids = [mk(2 + 10 * i, 50_000) for i in range(15)]
    m = dk.chi_so_kenh(vids, subs=6_000, as_of=AS_OF, sub_30_ngay_truoc=3_000)
    assert m["pct_tang_sub_30"] is None and m["pct_tang_sub_30_tho"] == pytest.approx(1.0)
    assert "DA_SUB_NEN_NHO" in m["co"]
    m0 = dk.chi_so_kenh(vids, subs=6_000, as_of=AS_OF, sub_30_ngay_truoc=0)
    assert m0["pct_tang_sub_30"] is None and "DA_SUB_NEN_NHO" in m0["co"]
    m5 = dk.chi_so_kenh(vids, subs=8_000, as_of=AS_OF, sub_30_ngay_truoc=5_000)
    assert m5["pct_tang_sub_30"] == pytest.approx(0.6) and "DA_SUB_NEN_NHO" not in m5["co"]


def test_phien_ban_cong_thuc_da_tang():
    assert dk.PHIEN_BAN == "2026-10-22.3"


# ---------- ghi đè có lý do ----------

def test_phan_tich_ghi_de():
    assert dk.phan_tich_ghi_de(["Kênh A:SUB_LAN_SHORTS:nguồn ngoài 22 % view 30 ngày: Shorts"]) == \
        [("Kênh A", "SUB_LAN_SHORTS", "nguồn ngoài 22 % view 30 ngày: Shorts")]
    assert dk.phan_tich_ghi_de(["k:sub_lan_shorts"]) == [("k", "SUB_LAN_SHORTS", "")]
    for xau in ("khong-co-dau-hai-cham", "k:", ":SUB_LAN_SHORTS", "k:co gach"):
        with pytest.raises(ValueError):
            dk.phan_tich_ghi_de([xau])


def test_ap_dung_ghi_de_sub_lan_shorts_bo_chi_so_theo_sub_va_ghi_ly_do():
    m = dk.chi_so_kenh([mk(40 + i, 1000) for i in range(30)], subs=100_000, as_of=AS_OF)
    assert "SUB_LAN_SHORTS" not in m["co"] and m["sub_moi_video"] is not None
    dk.ap_dung_ghi_de(m, "SUB_LAN_SHORTS", "nguồn ngoài 22 %")
    assert "SUB_LAN_SHORTS" in m["co"] and m["sub_moi_video"] is None and m["sub_moi_video_tho"] is not None
    assert m["ghi_de"] == [{"co": "SUB_LAN_SHORTS", "ly_do": "nguồn ngoài 22 %"}]
    dk.ap_dung_ghi_de(m, "SUB_LAN_SHORTS", "lần hai")      # không nhân đôi cờ, không mất bản thô
    assert m["co"].count("SUB_LAN_SHORTS") == 1 and m["sub_moi_video_tho"] is not None


def _bang(tmp_path, n_kenh=4, them_cot=None):
    dong = ["kenh\tfile\tsubs\tngay_lap\tcua_so_tu\tty_trong_view_short\tso_hoi_vien"]
    for i in range(n_kenh):
        f = tmp_path / f"k{i}.tsv"
        f.write_text("id\tngay_dang\tthoi_luong_s\tview\tlike\ttieu_de\n" + "".join(
            f"k{i}v{j}\t{(AS_OF - timedelta(days=40 + j)).isoformat()}\t1200\t{1000 * (i + 1)}\t10\tt\n" for j in range(30)),
            encoding="utf-8")
        cs = (them_cot or {}).get(i, "")
        dong.append(f"Kênh {i}\tk{i}.tsv\t{10_000 * (i + 1)}\t2024-01-01\t{cs}\t\t")
    b = tmp_path / "bang.tsv"
    b.write_text("\n".join(dong) + "\n", encoding="utf-8")
    return b


def test_xep_hang_cli_ghi_de_ghi_ly_do_vao_json(tmp_path):
    b = _bang(tmp_path)
    out = tmp_path / "xh.json"
    rc = dk.main(["xep-hang", str(b), "--as-of", AS_OF.isoformat(), "--json", str(out),
                  "--ghi-de", "Kênh 3:SUB_LAN_SHORTS:vidIQ báo 22 % view là Shorts"])
    assert rc == 0
    d = json.loads(out.read_text(encoding="utf-8"))
    ci = d["chi_so"]["Kênh 3"]
    assert "SUB_LAN_SHORTS" in ci["co"] and ci["sub_moi_video"] is None
    assert ci["ghi_de"][0]["ly_do"] == "vidIQ báo 22 % view là Shorts"
    row = next(r for r in d["xep_hang"] if r["kenh"] == "Kênh 3")
    assert "SUB_LAN_SHORTS" in row["co"] and row["ghi_de"][0]["co"] == "SUB_LAN_SHORTS"


def test_xep_hang_cli_ghi_de_kenh_la_thi_dung_lai(tmp_path):
    b = _bang(tmp_path)
    with pytest.raises(SystemExit) as e:
        dk.main(["xep-hang", str(b), "--as-of", AS_OF.isoformat(), "--ghi-de", "Không có:SUB_LAN_SHORTS:x"])
    assert e.value.code != 0


def test_xep_hang_cli_doc_cot_cua_so_va_ty_trong_short(tmp_path):
    b = _bang(tmp_path)
    txt = b.read_text(encoding="utf-8").splitlines()
    txt[1] = txt[1].replace("\t\t\t", "\t" + (AS_OF - timedelta(days=60)).isoformat() + "\t0.5\t7", 1)
    b.write_text("\n".join(txt) + "\n", encoding="utf-8")
    out = tmp_path / "xh.json"
    dk.main(["xep-hang", str(b), "--as-of", AS_OF.isoformat(), "--json", str(out)])
    ci = json.loads(out.read_text(encoding="utf-8"))["chi_so"]["Kênh 0"]
    assert ci["cua_so_tu"] == (AS_OF - timedelta(days=60)).isoformat()
    assert "SUB_LAN_SHORTS" in ci["co"] and ci["so_hoi_vien"] == 7 and "HOI_VIEN" in ci["co"]


# ---------- độ nhạy ----------

def _m(**kw):
    m = {"co": [], "n_video": 50, "tuoi_tu_video_dau": 400, "n_dai_dung_tinh": 20, "subs": 1000}
    m.update(kw)
    return m


def _bo_ba_kenh():
    return {
        "A": _m(sub_moi_video=100, trung_vi_20_dai=300, trung_vi_chia_sub=0.5, sub_moi_ngay_video_dau=200,
                pct_tang_sub_30=0.3, da_trung_vi=3.0),
        "Y": _m(tuoi_tu_video_dau=40, sub_moi_video=50, trung_vi_20_dai=200, trung_vi_chia_sub=0.4,
                sub_moi_ngay_video_dau=350, pct_tang_sub_30=1.0, da_trung_vi=2.0),
        "Z": _m(sub_moi_video=10, trung_vi_20_dai=100, trung_vi_chia_sub=0.1, sub_moi_ngay_video_dau=50,
                pct_tang_sub_30=0.1, da_trung_vi=0.9),
        "W": _m(sub_moi_video=9, trung_vi_20_dai=90, trung_vi_chia_sub=0.09, sub_moi_ngay_video_dau=45,
                pct_tang_sub_30=0.09, da_trung_vi=0.8),
        "V": _m(sub_moi_video=8, trung_vi_20_dai=80, trung_vi_chia_sub=0.08, sub_moi_ngay_video_dau=40,
                pct_tang_sub_30=0.08, da_trung_vi=0.7),
    }


def test_do_nhay_dem_hang_1_o_bao_nhieu_cach_va_vung():
    kq = dk.do_nhay(_bo_ba_kenh())
    assert kq["so_cach"] == 6 and kq["so_cach_hop_le"] == 6 and len(kq["bien_the"]) == 6
    ten = [b["ten"] for b in kq["bien_the"]]
    assert any("bỏ % tăng" in t for t in ten) and any("≥ 90 ngày" in t for t in ten) and any("trung vị" in t for t in ten)
    assert kq["hang_1_o"] == {"A": 5, "Y": 1}
    assert kq["hang_1_vung"] == ["A"]
    be90 = next(b for b in kq["bien_the"] if "≥ 90 ngày" in b["ten"])
    assert be90["n_kenh"] == 4 and be90["n_xep"] == 4 and "Y" not in be90["hang_1"]
    da = next(b for b in kq["bien_the"] if b["ten"] == "đà")
    assert da["hang_1"] == ["Y"]


def test_do_nhay_khong_goi_vung_khi_qua_it_cach_hop_le():
    # 3 kênh chỉ có 3 tiêu chí: phần lớn cách tính không xếp đủ kênh, nên hạng 1 ở 2/2 chưa đủ để gọi là vững
    chi_3 = dict(sub_moi_video=None, trung_vi_chia_sub=None, sub_moi_ngay_video_dau=None)
    kenh = {
        "A": _m(trung_vi_20_dai=300, pct_tang_sub_30=0.5, da_trung_vi=1.5, **chi_3),
        "B": _m(trung_vi_20_dai=200, pct_tang_sub_30=0.3, da_trung_vi=1.2, **chi_3),
        "C": _m(trung_vi_20_dai=100, pct_tang_sub_30=0.1, da_trung_vi=0.9, **chi_3),
    }
    kq = dk.do_nhay(kenh)
    assert 0 < kq["so_cach_hop_le"] < dk.SO_CACH_HOP_LE_TOI_THIEU_DE_VUNG
    assert kq["hang_1_o"].get("A") == kq["so_cach_hop_le"]
    assert kq["hang_1_vung"] == []


def test_do_nhay_rong():
    kq = dk.do_nhay({})
    assert kq["hang_1_o"] == {} and kq["hang_1_vung"] == []


def test_xep_hang_cli_do_nhay_in_hang_1_o_n_m_cach(tmp_path, capsys):
    b = _bang(tmp_path)
    out = tmp_path / "xh.json"
    dk.main(["xep-hang", str(b), "--as-of", AS_OF.isoformat(), "--do-nhay", "--json", str(out)])
    o = capsys.readouterr().out
    assert "hạng 1 ở" in o and "cách" in o and "n_xep" in o
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["do_nhay"]["so_cach"] == 6
