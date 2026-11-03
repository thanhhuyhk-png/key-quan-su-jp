"""Test biên của gop_ho_so.py và xuat_sheet.py: ghi đè phản ánh vào hồ sơ, bảng định tính không đè số đo, % tăng sub
đã qua trần/sàn, kênh tái sinh không tính là kênh mới."""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import openpyxl
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import do_kenh as dk  # noqa: E402
import gop_ho_so as gop  # noqa: E402
import xuat_sheet as xs  # noqa: E402

AS_OF = date(2026, 10, 22)


# ---------- gop_ho_so ----------

@pytest.fixture
def thu_muc(tmp_path):
    (tmp_path / "video").mkdir()
    (tmp_path / "do-kenh").mkdir()
    for cid in ("UCa", "UCb", "UCc"):
        dong = ["id\tngay_dang\tthoi_luong_s\tview\tlike\tbinh_luan\tis_short\ttieu_de"]
        for j in range(30):
            dong.append(f"{cid}v{j}\t{(AS_OF - timedelta(days=40 + j)).isoformat()}\t1200\t{1000 * (ord(cid[-1]) - 96) + j}\t30\t5\t0\tT{j}")
        (tmp_path / "video" / f"{cid}.tsv").write_text("\n".join(dong) + "\n", encoding="utf-8")
        assert dk.main(["kenh", str(tmp_path / "video" / f"{cid}.tsv"), "--subs", str(20_000 * (ord(cid[-1]) - 96)),
                        "--as-of", AS_OF.isoformat(), "--ngay-lap", "2024-01-01",
                        "--json", str(tmp_path / "do-kenh" / f"{cid}.json")]) == 0
    (tmp_path / "bang.tsv").write_text("kenh\tfile\tsubs\tngay_lap\n" + "".join(
        f"{c}\tvideo/{c}.tsv\t{20_000 * (ord(c[-1]) - 96)}\t2024-01-01\n" for c in ("UCa", "UCb", "UCc")), encoding="utf-8")
    return tmp_path


def _xep_hang(t, *them):
    assert dk.main(["xep-hang", str(t / "bang.tsv"), "--as-of", AS_OF.isoformat(), "--json", str(t / "xh.json"), *them]) == 0


def _dt(t, **kenh_a):
    dt = {"ngay_do": AS_OF.isoformat(), "kenh": {"UCa": {"ten": "A", "giu_loai": "Giữ", **kenh_a},
                                                "UCb": {"ten": "B", "giu_loai": "Giữ"}, "UCc": {"ten": "C", "giu_loai": "Giữ"}}}
    (t / "dt.json").write_text(json.dumps(dt, ensure_ascii=False), encoding="utf-8")
    return gop.doc_dinh_tinh(t / "dt.json")


def test_gop_phan_anh_ghi_de_cua_xep_hang(thu_muc):
    _xep_hang(thu_muc, "--ghi-de", "UCa:SUB_LAN_SHORTS:vidIQ báo 22 % view là Shorts")
    hs, _ = gop.gop(thu_muc / "do-kenh", thu_muc / "video", _dt(thu_muc), xep_hang=thu_muc / "xh.json", as_of=AS_OF)
    a = next(k for k in hs["kenh"] if k["id"] == "UCa")
    assert a["sub_moi_video"] is None and a["sub_moi_video_tho"] is not None
    assert "SUB_LAN_SHORTS" in a["co"] and a["ghi_de"][0]["ly_do"].startswith("vidIQ")
    b = next(k for k in hs["kenh"] if k["id"] == "UCb")
    assert b["sub_moi_video"] is not None
    assert a["diem"] is None                                     # khớp xếp hạng: không đủ chỉ số


def test_gop_khong_ghi_de_khi_khong_co_xep_hang_ghi_de(thu_muc):
    _xep_hang(thu_muc)
    hs, _ = gop.gop(thu_muc / "do-kenh", thu_muc / "video", _dt(thu_muc), xep_hang=thu_muc / "xh.json", as_of=AS_OF)
    assert next(k for k in hs["kenh"] if k["id"] == "UCa")["sub_moi_video"] is not None


def test_bang_dinh_tinh_khong_de_len_so_do_va_canh_bao(thu_muc):
    _xep_hang(thu_muc)
    dt = _dt(thu_muc, subs=1, co="TUY_Y", diem=99, hang=1, trung_vi_20_dai=7, nguon_so="vidIQ 22/10", ngach="kể chuyện")
    hs, canh_bao = gop.gop(thu_muc / "do-kenh", thu_muc / "video", dt, xep_hang=thu_muc / "xh.json", as_of=AS_OF)
    a = next(k for k in hs["kenh"] if k["id"] == "UCa")
    assert a["subs"] == 20_000 and a["co"] != "TUY_Y" and a["diem"] != 99 and a["trung_vi_20_dai"] != 7
    assert a["nguon_so"] == "vidIQ 22/10" and a["ngach"] == "kể chuyện" and a["ten"] == "A"
    txt = "\n".join(canh_bao)
    for khoa in ("subs", "co", "diem", "hang", "trung_vi_20_dai"):
        assert f"'{khoa}'" in txt
    assert "'nguon_so'" not in txt


def test_bang_dinh_tinh_van_cho_kenh_chua_do_nhap_so(tmp_path):
    (tmp_path / "do-kenh").mkdir()
    (tmp_path / "video").mkdir()
    dt = {"kenh": gop._kenh_dinh_tinh({"UCq": {"ten": "Q", "giu_loai": "Loại", "subs": 1234, "diem": 5}})}
    hs, canh_bao = gop.gop(tmp_path / "do-kenh", tmp_path / "video", dt, as_of=AS_OF)
    q = hs["kenh"][0]
    assert q["subs"] == 1234 and q["diem"] == 5 and not any("subs" in c for c in canh_bao)


# ---------- xuat_sheet: % tăng sub đã qua trần/sàn ----------

def _hs(kenh_them=()):
    kenh = [{"id": f"k{i}", "ten": f"Kênh {i}", "link": f"https://www.youtube.com/@k{i}", "subs": 1000 * (30 - i),
             "diem": 100 - i, "giu_loai": "Giữ", "nguon_so": "t", "ngay_video_dau": "2024-01-01"} for i in range(1, 6)]
    for k in kenh_them:
        kenh[k["_i"]].update({a: b for a, b in k.items() if a != "_i"})
    return {"du_an": "T", "ngay_do": "2026-10-22", "kenh": kenh, "video": [], "model_link": {"kenh": "k1"}}


def _xuat(tmp_path, hs):
    p = tmp_path / "hs.json"
    p.write_text(json.dumps(hs, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "t.xlsx"
    _, kiem = xs.xuat(p, out)
    return openpyxl.load_workbook(out), kiem


def _dong(ws, ten):
    hdr = [c.value for c in ws[xs.DONG_TIEU_DE]]
    j = hdr.index("Tên kênh")
    for r in ws.iter_rows(min_row=xs.DONG_TIEU_DE + 1):
        if r[j].value == ten:
            return r, hdr
    raise AssertionError(ten)


def test_pct_tang_hien_thi_la_ban_da_chan_tran_va_ban_tho_o_cot_rieng(tmp_path):
    hs = _hs([{"_i": 0, "subs": 40_000, "subs_30_ngay_truoc": 13_202, "pct_tang_sub_30": 1.0},
              {"_i": 1, "subs": 22_000, "subs_30_ngay_truoc": 10_000, "pct_tang_sub_30": 1.2},
              {"_i": 2, "subs": 6_000, "subs_30_ngay_truoc": 3_000, "pct_tang_sub_30": None}])
    wb, _ = _xuat(tmp_path, hs)
    for tab in (xs.TEN_TAB[1], xs.TEN_TAB[3]):
        ws = wb[tab]
        r0, hdr = _dong(ws, "Kênh 1")
        assert r0[hdr.index("% tăng 30 ngày" if tab == xs.TEN_TAB[1] else "% tăng")].value == pytest.approx(1.0)
        assert r0[hdr.index("% tăng thô (chưa chặn trần/sàn)")].value == pytest.approx((40_000 - 13_202) / 13_202)
        r2, _ = _dong(ws, "Kênh 3")
        assert str(r2[hdr.index("% tăng 30 ngày" if tab == xs.TEN_TAB[1] else "% tăng")].value).startswith("bỏ")
        assert r2[hdr.index("% tăng thô (chưa chặn trần/sàn)")].value == pytest.approx(1.0)
    ten = [r[3] for r in wb[xs.TEN_TAB[3]].iter_rows(min_row=xs.DONG_TIEU_DE + 1, values_only=True)]
    assert ten.index("Kênh 2") < ten.index("Kênh 1") < ten.index("Kênh 3")        # xếp theo % đã chặn: 1,2 > 1,0 > bỏ


def test_ho_so_cu_khong_co_pct_tang_sub_30_van_hien_ban_tinh_lai(tmp_path):
    hs = _hs([{"_i": 0, "subs": 3_000, "subs_30_ngay_truoc": 1_000}])
    wb, _ = _xuat(tmp_path, hs)
    r, hdr = _dong(wb[xs.TEN_TAB[1]], "Kênh 1")
    assert r[hdr.index("% tăng 30 ngày")].value == pytest.approx(2.0)


# ---------- xuat_sheet: kênh tái sinh không phải kênh mới ----------

def test_luat_top_phai_co_kenh_moi_khong_tinh_kenh_tai_sinh(tmp_path):
    hs = _hs()
    for k in hs["kenh"]:
        k["ngay_video_dau"] = "2022-01-01"
    hs["kenh"].append({"id": "kr", "ten": "Tái sinh", "giu_loai": "Giữ", "diem": 1, "nguon_so": "t", "subs": 5,
                       "ngay_video_dau": "2026-08-01", "co": ["TAI_SINH"], "nhom": ["moi"]})
    hs["kenh"] += [{"id": f"x{i}", "ten": f"X{i}", "giu_loai": "Giữ", "diem": 50 + i, "nguon_so": "t", "subs": 5,
                    "ngay_video_dau": "2022-01-01"} for i in range(20)]
    _, kiem = _xuat(tmp_path, hs)
    assert not any("được giữ nhưng không vào TOP 20" in k["noi_dung"] for k in kiem)             # kênh mới duy nhất là tái sinh, không đòi hỏi
    hs["kenh"].append({"id": "kn", "ten": "Mới thật", "giu_loai": "Giữ", "diem": 0.5, "nguon_so": "t", "subs": 5,
                       "ngay_video_dau": "2026-08-01", "nhom": ["moi"]})
    _, kiem2 = _xuat(tmp_path, hs)
    assert any("được giữ nhưng không vào TOP 20" in k["noi_dung"] for k in kiem2)


def test_dinh_tinh_hop_le_khong_sinh_canh_bao_thua(thu_muc):
    _xep_hang(thu_muc)
    dt = _dt(thu_muc, nguon_so="vidIQ", ngach="kể", video_30_ngay=9)
    hs, canh_bao = gop.gop(thu_muc / "do-kenh", thu_muc / "video", dt, xep_hang=thu_muc / "xh.json", as_of=AS_OF)
    assert canh_bao == []
    assert next(k for k in hs["kenh"] if k["id"] == "UCa")["video_30_ngay"] == 9
