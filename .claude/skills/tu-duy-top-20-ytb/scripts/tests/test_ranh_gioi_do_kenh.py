"""Test biên của do_kenh.py: cửa sổ thiếu tổng video, kênh lai Shorts khi xếp hạng, meta của thu_video, cờ ghi đè,
độ nhạy với cách tính có ít kênh, trung vị bằng 0, trạng thái kiểm số theo từ nguyên vẹn."""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import do_kenh as dk  # noqa: E402

AS_OF = date(2026, 10, 22)
GOC = Path(dk.__file__)


def mk_ds(n, bat_dau_truoc, buoc=3, goc=1000, short=False, tien_to="L"):
    return [dk.Video(id=f"{tien_to}{i}", title="t", published=AS_OF - timedelta(days=bat_dau_truoc - i * buoc),
                     views=goc + i * 10, likes=10, comments=1, duration_s=30 if short else 1200,
                     is_short_flag=short) for i in range(n)]


# ---------- cửa sổ mà thiếu tổng video ----------

def test_cua_so_thieu_tong_video_khong_tinh_sub_moi_video_va_bao_co():
    trong = mk_ds(100, 400)
    xa = [dk.Video(id=f"O{i}", title="t", published=AS_OF - timedelta(days=900 + i), views=5000, likes=5,
                   comments=1, duration_s=1200, is_short_flag=False) for i in range(10)]
    cs = AS_OF - timedelta(days=400)
    m = dk.chi_so_kenh(trong + xa, 50_000, AS_OF, cua_so_tu=cs)
    assert m["sub_moi_video"] is None
    assert "THIEU_TONG_VIDEO_CHO_CUA_SO" in m["co"]
    m2 = dk.chi_so_kenh(trong + xa, 50_000, AS_OF, tong_video=300, cua_so_tu=cs)
    assert m2["sub_moi_video"] == pytest.approx(50_000 / 300)
    assert "THIEU_TONG_VIDEO_CHO_CUA_SO" not in m2["co"]
    m3 = dk.chi_so_kenh(trong, 50_000, AS_OF)                       # không có cửa sổ: như cũ
    assert m3["sub_moi_video"] == pytest.approx(500)


def _meta(tmp_path, **them):
    d = {"kenh": "UCx", "tong_flat": 300, "ngay_video_dau": (AS_OF - timedelta(days=1500)).isoformat(),
         "cua_so_tu": (AS_OF - timedelta(days=400)).isoformat(), "so_hoi_vien": 4}
    d.update(them)
    p = tmp_path / "UCx.meta.json"
    p.write_text(json.dumps(d), encoding="utf-8")
    return p


def _tsv(tmp_path):
    p = tmp_path / "UCx.tsv"
    dong = ["id\tngay_dang\tthoi_luong_s\tview\tlike\tbinh_luan\tis_short\ttieu_de"]
    for v in mk_ds(100, 400):
        dong.append(f"{v.id}\t{v.published.isoformat()}\t1200\t{v.views}\t10\t1\t0\tt")
    p.write_text("\n".join(dong) + "\n", encoding="utf-8")
    return p


def _chay_kenh(tmp_path, *them):
    out = tmp_path / "k.json"
    dk.main(["kenh", str(_tsv(tmp_path)), "--subs", "50000", "--as-of", AS_OF.isoformat(), "--json", str(out), *them])
    return json.loads(out.read_text(encoding="utf-8"))["chi_so"]


def test_kenh_meta_dien_tong_video_ngay_dau_hoi_vien_va_cua_so(tmp_path):
    ci = _chay_kenh(tmp_path, "--meta", str(_meta(tmp_path)))
    assert ci["n_video"] == 300 and ci["sub_moi_video"] == pytest.approx(50_000 / 300)
    assert ci["tuoi_tu_video_dau"] == 1500 and ci["so_hoi_vien"] == 4 and "HOI_VIEN" in ci["co"]
    assert ci["cua_so_tu"] == (AS_OF - timedelta(days=400)).isoformat()
    assert "THIEU_TONG_VIDEO_CHO_CUA_SO" not in ci["co"]


def test_kenh_tham_so_dong_lenh_uu_tien_hon_meta(tmp_path):
    ci = _chay_kenh(tmp_path, "--meta", str(_meta(tmp_path)), "--tong-video", "200", "--so-hoi-vien", "0",
                    "--ngay-video-dau", (AS_OF - timedelta(days=1000)).isoformat())
    assert ci["n_video"] == 200 and ci["tuoi_tu_video_dau"] == 1000 and "HOI_VIEN" not in ci["co"]


def test_kenh_meta_loi_thi_tu_choi(tmp_path):
    with pytest.raises(SystemExit) as e:
        _chay_kenh(tmp_path, "--meta", str(_meta(tmp_path, loi="thiếu 30/140 video")))
    assert "thiếu 30/140" in str(e.value)


def test_bang_xep_hang_doc_cot_meta(tmp_path):
    _tsv(tmp_path)
    meta = _meta(tmp_path)
    b = tmp_path / "bang.tsv"
    b.write_text(f"kenh\tfile\tsubs\tmeta\nUCx\tUCx.tsv\t50000\t{meta.name}\n", encoding="utf-8")
    out = tmp_path / "xh.json"
    dk.main(["xep-hang", str(b), "--as-of", AS_OF.isoformat(), "--json", str(out)])
    ci = json.loads(out.read_text(encoding="utf-8"))["chi_so"]["UCx"]
    assert ci["n_video"] == 300 and ci["so_hoi_vien"] == 4


def test_tai_sinh_khong_tinh_khi_ngay_video_dau_suy_tu_danh_sach_bi_cat():
    vs = mk_ds(100, 300)
    cs = AS_OF - timedelta(days=300)
    m = dk.chi_so_kenh(vs, 80_000, AS_OF, ngay_lap=date(2019, 3, 1), cua_so_tu=cs)
    assert "TAI_SINH" not in m["co"]
    m2 = dk.chi_so_kenh(vs, 80_000, AS_OF, ngay_lap=date(2019, 3, 1), cua_so_tu=cs, ngay_video_dau=AS_OF - timedelta(days=300))
    assert "TAI_SINH" in m2["co"]
    m3 = dk.chi_so_kenh(vs, 80_000, AS_OF, ngay_lap=date(2019, 3, 1), tong_video=400)     # danh sách thiếu, không rõ ngày đầu
    assert "TAI_SINH" not in m3["co"]
    m4 = dk.chi_so_kenh(mk_ds(40, 120), 80_000, AS_OF, ngay_lap=date(2019, 3, 1))           # danh sách coi là đủ
    assert "DANH_SACH_CO_THE_BI_CAT" not in m4["co"]
    assert "TAI_SINH" in m4["co"]


# ---------- kênh lai Shorts khi xếp hạng ----------

def _bon_kenh(ty_short_b=0.5):
    kenh = {}
    for ten in "ABCD":
        v = mk_ds(30, 200, goc=1000 + (ord(ten) - 65) * 500)
        ty = ty_short_b if ten == "B" else None
        if ty:
            v += mk_ds(30, 200, goc=50_000, short=True, tien_to="S")
        kenh[ten] = dk.chi_so_kenh(v, 20_000 + ord(ten), AS_OF, ngay_lap=AS_OF - timedelta(days=300),
                                   sub_30_ngay_truoc=10_000)
    return kenh


def test_kenh_lai_shorts_bo_ca_pct_tang_sub_nen_khong_du_chi_so():
    kenh = _bon_kenh()
    b = kenh["B"]
    assert "SUB_LAN_SHORTS" in b["co"]
    assert b["pct_tang_sub_30"] is None and b["pct_tang_sub_30_tho"] is not None
    assert b["tang_sub_30"] is None and b["tang_sub_30_tho"] is not None
    hang = {r["kenh"]: r for r in dk.xep_hang(kenh)}
    assert hang["B"]["hang"] is None and hang["B"]["n_tieu_chi"] < 3 and "KHONG_DU_CHI_SO" in hang["B"]["co"]
    assert all(hang[k]["hang"] is not None for k in "ACD")


def test_ghi_de_sub_lan_shorts_cung_bo_pct_tang_sub():
    kenh = _bon_kenh(ty_short_b=None)
    assert dk.xep_hang(kenh)[0]["hang"] is not None
    dk.ap_dung_ghi_de(kenh["D"], "SUB_LAN_SHORTS", "vidIQ 22 %")
    hang = {r["kenh"]: r for r in dk.xep_hang(kenh)}
    assert hang["D"]["hang"] is None and "KHONG_DU_CHI_SO" in hang["D"]["co"]
    dn = dk.do_nhay(kenh)
    assert "D" not in dn["hang_1_o"]


def test_bo_chi_so_sub_giu_ban_tho_goc_khi_da_bi_chan_tran():
    vids = [dk.Video(id=f"y{i}", title="t", published=AS_OF - timedelta(days=58 - 4 * i), views=5000, likes=5,
                     comments=1, duration_s=1200, is_short_flag=False) for i in range(15)]
    m = dk.chi_so_kenh(vids, 40_000, AS_OF, sub_30_ngay_truoc=13_202)
    goc = m["pct_tang_sub_30_tho"]
    assert goc > 2 and m["pct_tang_sub_30"] == 1.0
    dk.ap_dung_ghi_de(m, "SUB_LAN_SHORTS", "x")
    assert m["pct_tang_sub_30"] is None and m["pct_tang_sub_30_tho"] == pytest.approx(goc)   # không bị đè bằng 1.0


# ---------- cờ ghi đè hợp lệ ----------

def test_ghi_de_chi_nhan_co_hop_le():
    for xau in ("k:SUB_LAN_SHORT:typo", "k:CO_LA"):
        with pytest.raises(ValueError, match="cờ"):
            dk.phan_tich_ghi_de([xau])
    assert dk.phan_tich_ghi_de(["k:HOI_VIEN:x"]) == [("k", "HOI_VIEN", "x")]
    assert dk.phan_tich_ghi_de(["k:khong_du_chi_so"]) == [("k", "KHONG_DU_CHI_SO", "")]


def test_moi_co_script_gan_deu_nam_trong_danh_sach_hop_le():
    nguon = GOC.read_text(encoding="utf-8")
    cac_co = set(re.findall(r'co\.append\("([A-Z0-9_]+)"\)', nguon))
    assert "SUB_LAN_SHORTS" in cac_co and len(cac_co) > 15
    assert cac_co <= set(dk.CO_HOP_LE), cac_co - set(dk.CO_HOP_LE)


def test_cli_ghi_de_co_la_dung_lai(tmp_path):
    b = tmp_path / "bang.tsv"
    f = tmp_path / "a.tsv"
    f.write_text("id\tngay_dang\tview\n" + "".join(f"a{i}\t2026-0{(i % 8) + 1}-01\t100\n" for i in range(8)), encoding="utf-8")
    b.write_text("kenh\tfile\tsubs\nK\ta.tsv\t100\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        dk.main(["xep-hang", str(b), "--as-of", AS_OF.isoformat(), "--ghi-de", "K:SUB_LAN_SHORT:typo"])
    assert e.value.code not in (0, None)


# ---------- độ nhạy ----------

def _m(**kw):
    m = {"co": [], "n_video": 50, "tuoi_tu_video_dau": 400, "n_dai_dung_tinh": 20, "subs": 1000}
    m.update(kw)
    return m


def _ba_kenh():
    return {
        "A": _m(sub_moi_video=100, trung_vi_20_dai=300, trung_vi_chia_sub=0.5, sub_moi_ngay_video_dau=200,
                pct_tang_sub_30=0.3, da_trung_vi=3.0),
        "Y": _m(tuoi_tu_video_dau=40, sub_moi_video=50, trung_vi_20_dai=200, trung_vi_chia_sub=0.4,
                sub_moi_ngay_video_dau=350, pct_tang_sub_30=1.0, da_trung_vi=2.0),
        "Z": _m(sub_moi_video=10, trung_vi_20_dai=100, trung_vi_chia_sub=0.1, sub_moi_ngay_video_dau=50,
                pct_tang_sub_30=0.1, da_trung_vi=0.9),
    }


def test_do_nhay_cach_co_duoi_3_kenh_xep_khong_tinh_vao_mau_so():
    kq = dk.do_nhay(_ba_kenh())                     # cách "chỉ kênh ≥ 90 ngày" chỉ còn A và Z
    be90 = next(b for b in kq["bien_the"] if "≥ 90 ngày" in b["ten"])
    assert be90["n_xep"] == 2 and be90["hop_le"] is False
    assert kq["so_cach"] == 6 and kq["so_cach_hop_le"] == 5
    assert kq["hang_1_o"] == {"A": 4, "Y": 1}
    assert all("n_xep" in b for b in kq["bien_the"])
    assert kq["hang_1_vung"] == []                  # 4/5 < 5/6
    kq2 = dk.do_nhay({k: v for k, v in _ba_kenh().items() if k != "Y"})       # chỉ còn 2 kênh: không cách nào hợp lệ
    assert kq2["so_cach_hop_le"] == 0 and kq2["hang_1_o"] == {} and kq2["hang_1_vung"] == []


def test_do_nhay_cli_in_n_xep_va_mau_so_hop_le(tmp_path, capsys):
    cac = []
    for i in range(4):
        f = tmp_path / f"k{i}.tsv"
        f.write_text("id\tngay_dang\tthoi_luong_s\tview\tlike\ttieu_de\n" + "".join(
            f"k{i}v{j}\t{(AS_OF - timedelta(days=100 + j)).isoformat()}\t1200\t{1000 * (i + 1)}\t10\tt\n" for j in range(30)),
            encoding="utf-8")
        cac.append(f"Kênh {i}\tk{i}.tsv\t{10_000 * (i + 1)}\t2024-01-01")
    b = tmp_path / "bang.tsv"
    b.write_text("kenh\tfile\tsubs\tngay_lap\n" + "\n".join(cac) + "\n", encoding="utf-8")
    dk.main(["xep-hang", str(b), "--as-of", AS_OF.isoformat(), "--do-nhay"])
    o = capsys.readouterr().out
    assert "n_xep" in o and re.search(r"hạng 1 ở \d+/\d+ cách", o)


# ---------- trung vị bằng 0 ----------

def test_he_so_khi_trung_vi_truoc_bang_0_co_ly_do():
    vs = [dk.Video(id=f"x{i}", title="t", published=AS_OF - timedelta(days=100 - i), views=0, likes=0, comments=0,
                   duration_s=900, is_short_flag=False) for i in range(10)]
    vs.append(dk.Video(id="y", title="t", published=AS_OF - timedelta(days=60), views=500, likes=1, comments=0,
                       duration_s=900, is_short_flag=False))
    r = {h["id"]: h for h in dk.he_so_vuot_troi(vs, AS_OF)}
    assert r["y"]["he_so"] is None and r["y"]["ly_do_khong_tinh"] == "trung_vi_truoc_bang_0"


# ---------- trạng thái kiểm số theo từ nguyên vẹn ----------

@pytest.mark.parametrize("xau,ma", [
    ("nghiên cứu thêm", None), ("nghiệm thu xong", None), ("đạtxx", None), ("datum", None),
    ("loại", "nghi"), ("Loại (reup)", "nghi"), ("nghi ngờ: like thấp", "nghi"), ("nghi", "nghi"),
    ("đạt, đã đọc 20 bình luận", "dat"), ("Đạt (đối chiếu sự kiện)", "dat"), ("sơ bộ: chưa đọc", "so_bo"),
    ("chưa chín (< 30 ngày)", "chua_chin"), ("so_bo", "so_bo"), ("", None)])
def test_trang_thai_kiem_so_khop_tu_nguyen_ven(xau, ma):
    assert dk.trang_thai_kiem_so(xau) == ma
