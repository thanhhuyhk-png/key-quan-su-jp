"""Test gop_ho_so.py: thư mục do-kenh + TSV video + bảng định tính → JSON hồ sơ đúng cấu trúc của xuat_sheet."""
import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import do_kenh as dk  # noqa: E402
import gop_ho_so as gop  # noqa: E402
import xuat_sheet as xs  # noqa: E402

AS_OF = date(2026, 10, 22)


def ghi_tsv(path, hang):
    """hang: (id, ngay_truoc, view, like, is_short)"""
    dong = ["id\tngay_dang\tthoi_luong_s\tview\tlike\tbinh_luan\tis_short\ttieu_de"]
    for i, n, v, lk, sh in hang:
        dong.append(f"{i}\t{(AS_OF - timedelta(days=n)).isoformat()}\t{40 if sh else 1200}\t{v}\t{lk}\t5\t{int(sh)}\tTiêu đề {i}")
    path.write_text("\n".join(dong) + "\n", encoding="utf-8")


@pytest.fixture
def thu_muc(tmp_path):
    (tmp_path / "video").mkdir()
    (tmp_path / "do-kenh").mkdir()
    ua = [(f"a{i}", 31 + i, 1000, 20, False) for i in range(40)]
    ua[0] = ("new1", 5, 9000, 200, False)           # < 30 ngày tuổi: chưa chín
    ua[10] = ("hit", 41, 20_000, 400, False)        # hệ số cao
    ua[11] = ("lowlike", 42, 5_000, 1, False)       # like < 0,5 %
    ua += [("short1", 7, 50, 1, True)]
    ub = [(f"b{i}", 40 + i, 500, 10, False) for i in range(12)]
    ghi_tsv(tmp_path / "video" / "UCa.tsv", ua)
    ghi_tsv(tmp_path / "video" / "UCb.tsv", ub)
    for cid, subs in (("UCa", 30_000), ("UCb", 8_000)):
        rc = dk.main(["kenh", str(tmp_path / "video" / f"{cid}.tsv"), "--subs", str(subs), "--as-of", AS_OF.isoformat(),
                      "--ngay-lap", "2026-08-01", "--json", str(tmp_path / "do-kenh" / f"{cid}.json")])
        assert rc == 0
    bang = tmp_path / "bang.tsv"
    bang.write_text("kenh\tfile\tsubs\nUCa\tvideo/UCa.tsv\t30000\nUCb\tvideo/UCb.tsv\t8000\n", encoding="utf-8")
    assert dk.main(["xep-hang", str(bang), "--as-of", AS_OF.isoformat(), "--json", str(tmp_path / "xh.json")]) == 0
    dt = {
        "du_an": "Thử", "ngay_do": AS_OF.isoformat(), "ngay_moc_truoc": "2026-09-22",
        "muc_tieu": {"khan_gia": "18–34"}, "model_link": {"kenh": "UCa"},
        "kenh": {
            "UCa": {"ten": "Kênh A", "link": "https://www.youtube.com/@a", "giu_loai": "Giữ", "nhom": ["cung_nguon_luc"],
                    "ngach": "kể chuyện", "nguon_so": "yt-dlp 22/10/2026"},
            "UCb": {"ten": "Kênh B", "giu_loai": "Giữ", "nhom": "on_dinh"},
            "UCc": {"ten": "Kênh C (chỉ định tính)", "giu_loai": "Loại", "ly_do": "reup"},
        },
        "video": {"hit": {"de_tai": "đề tài hit", "kiem_tra_so": "dat"}},
        "chu_y": [{"loai": "gioi_han", "noi_dung": "x", "muc_do": "thấp"}],
    }
    (tmp_path / "dt.json").write_text(json.dumps(dt, ensure_ascii=False), encoding="utf-8")
    return tmp_path


def chay(t, **them):
    return gop.gop(t / "do-kenh", t / "video", gop.doc_dinh_tinh(t / "dt.json"), xep_hang=t / "xh.json", as_of=AS_OF, **them)


def test_gop_kenh_gop_chi_so_xep_hang_va_dinh_tinh(thu_muc):
    hs, canh_bao = chay(thu_muc)
    k = {x["id"]: x for x in hs["kenh"]}
    assert set(k) == {"UCa", "UCb", "UCc"}
    a = k["UCa"]
    assert a["ten"] == "Kênh A" and a["nhom"] == ["cung_nguon_luc"] and a["giu_loai"] == "Giữ"
    assert a["n_video"] == 41 and a["trung_vi_20_dai"] is not None and isinstance(a["co"], str)
    assert a["diem"] is not None and a["hang"] in (1, 2) and a["khoang_hang"]
    assert a["nguon_so"] == "yt-dlp 22/10/2026" and a["phien_ban"] == dk.PHIEN_BAN
    assert k["UCc"]["giu_loai"] == "Loại" and k["UCc"].get("diem") is None
    assert hs["du_an"] == "Thử" and hs["model_link"]["kenh"] == "UCa" and hs["chu_y"][0]["noi_dung"] == "x"
    assert hs["phien_ban_cong_thuc"] == dk.PHIEN_BAN
    assert isinstance(canh_bao, list)


def test_gop_video_top_view_cong_he_so_cao_khong_lay_shorts(thu_muc):
    hs, _ = chay(thu_muc)
    v = [x for x in hs["video"] if x["kenh"] == "UCa"]
    ids = {x["id"] for x in v}
    assert "short1" not in ids
    assert {"hit", "new1", "lowlike"} <= ids
    top = {x["id"] for x in v if x["la_top_view"]}
    assert len(top) == 10 and "hit" in top
    hit = next(x for x in v if x["id"] == "hit")
    assert hit["he_so"] >= 3 and hit["link"] == "https://youtu.be/hit" and hit["de_tai"] == "đề tài hit"
    assert hit["views"] == 20_000 and hit["view_moi_ngay"] == pytest.approx(20_000 / 41, abs=1) and hit["thoi_luong_s"] == 1200
    assert hit["ngay_dang"] == (AS_OF - timedelta(days=41)).isoformat()


def test_kiem_tra_so_trang_thai_chuan(thu_muc):
    hs, _ = chay(thu_muc)
    v = {x["id"]: x for x in hs["video"] if x["kenh"] == "UCa"}
    assert v["hit"]["kiem_tra_so"] == "dat"                      # định tính ghi đè trạng thái tự động
    assert v["new1"]["kiem_tra_so"] == "chua_chin"
    assert v["lowlike"]["kiem_tra_so"] == "nghi" and "0,5" in v["lowlike"]["ghi_chu"]
    assert all(x["kiem_tra_so"] in dk.KIEM_TRA_SO for x in hs["video"])
    sach = next(x for x in v.values() if x["id"].startswith("a") and x["kiem_tra_so"] == "so_bo")
    assert "chưa đọc nội dung bình luận" in sach["ghi_chu"]
    assert not any(x["kiem_tra_so"] == "dat" and x["id"] != "hit" for x in v.values())   # tự động không bao giờ "đạt"


def test_canh_bao_kenh_thieu_dinh_tinh_hoac_video(thu_muc):
    dt = json.loads((thu_muc / "dt.json").read_text(encoding="utf-8"))
    del dt["kenh"]["UCb"]
    (thu_muc / "dt.json").write_text(json.dumps(dt, ensure_ascii=False), encoding="utf-8")
    (thu_muc / "video" / "UCa.tsv").unlink()
    hs, canh_bao = chay(thu_muc)
    txt = "\n".join(canh_bao)
    assert "UCb" in txt and "định tính" in txt
    assert "UCa" in txt and "video" in txt
    assert any(x["id"] == "UCb" for x in hs["kenh"])             # vẫn có mặt, chỉ thiếu phần định tính


def test_dinh_tinh_dang_bang_tsv(tmp_path):
    p = tmp_path / "kenh.tsv"
    p.write_text("id\tten\tgiu_loai\tnhom\tngach\nUCa\tKênh A\tGiữ\tMới < 12 tháng · Cùng nguồn lực\tkể\n", encoding="utf-8")
    dt = gop.doc_dinh_tinh(p)
    assert dt["kenh"]["UCa"]["ten"] == "Kênh A" and dt["kenh"]["UCa"]["nhom"] == ["moi", "cung_nguon_luc"]


def test_dinh_tinh_kenh_dang_danh_sach_va_thieu_id_thi_loi(tmp_path):
    p = tmp_path / "dt.json"
    p.write_text(json.dumps({"kenh": [{"id": "UCa", "ten": "A"}]}), encoding="utf-8")
    assert gop.doc_dinh_tinh(p)["kenh"]["UCa"]["ten"] == "A"
    p.write_text(json.dumps({"kenh": [{"ten": "A"}]}), encoding="utf-8")
    with pytest.raises(ValueError):
        gop.doc_dinh_tinh(p)


def test_cli_ghi_file_va_xuat_sheet_doc_duoc(thu_muc, capsys):
    out = thu_muc / "ho-so.json"
    rc = gop.main(["--do-kenh", str(thu_muc / "do-kenh"), "--video-dir", str(thu_muc / "video"),
                   "--dinh-tinh", str(thu_muc / "dt.json"), "--xep-hang", str(thu_muc / "xh.json"),
                   "--as-of", AS_OF.isoformat(), "--out", str(out)])
    assert rc == 0 and out.exists()
    assert "3 kênh" in capsys.readouterr().out
    xlsx = thu_muc / "t.xlsx"
    _, kiem = xs.xuat(out, xlsx)
    assert xlsx.exists()
    assert not any("thiếu id" in k["noi_dung"] for k in kiem)
