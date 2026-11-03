"""Test thu_video.py: chọn id, đếm video hội viên, ngày video đầu, cửa sổ, file PID, không cookie. Không gọi mạng."""
import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import thu_video as tv  # noqa: E402

GOC = datetime(2026, 10, 22, 12, tzinfo=timezone.utc)


def ts(ngay_truoc):
    return int((GOC - timedelta(days=ngay_truoc)).timestamp())


# ---------- phân tích đầu ra yt-dlp ----------

def test_phan_tich_flat_doc_id_thoi_luong_view_va_bo_dong_hong():
    out = "a1\t1200\t200000\nb2\tNA\tNA\nrac\n\nc3\t45\t12\n"
    ds = tv.phan_tich_flat(out)
    assert [d["id"] for d in ds] == ["a1", "b2", "c3"]
    assert ds[0]["views"] == 200000 and ds[1]["views"] == 0 and ds[2]["duration"] == 45


def test_phan_tich_dump_json_tung_dong_va_ngay_utc():
    dong = json.dumps({"id": "a1", "timestamp": ts(5), "duration": 900, "view_count": 10, "like_count": None,
                       "comment_count": 3, "title": "Có\ttab và\nxuống dòng", "channel_id": "UCx"})
    ds = tv.phan_tich_dump(dong + "\nkhông phải json\n")
    assert len(ds) == 1
    d = ds[0]
    assert d["ngay_dang"].startswith("2026-10-17") and d["like"] == "" and d["binh_luan"] == "3"
    assert "\t" not in d["tieu_de"] and "\n" not in d["tieu_de"]


MEMBERS = "ERROR: [youtube] {}: Join this channel to get access to members-only content like this video, and other exclusive perks."


def test_dem_loi_tach_hoi_vien_khoi_loi_khac():
    err = "\n".join([MEMBERS.format("m1"), MEMBERS.format("m2"),
                     "ERROR: [youtube] z9: Video unavailable", "WARNING: gì đó"])
    kq = tv.dem_loi(err)
    assert kq["hoi_vien_ids"] == ["m1", "m2"] and kq["so_hoi_vien"] == 2
    assert kq["loi_khac"] == 1


# ---------- chọn id ----------

def test_chon_id_theo_cua_so_top_view_cu_nhat_va_mau_short():
    dai = [{"id": f"L{i}", "views": 100 + (5000 if i in (110, 7) else 0) + i} for i in range(130)]   # mới → cũ
    short = [{"id": f"S{i}", "views": 10 + i} for i in range(40)]
    c = tv.chon_id(dai, short, so_dai=100, top_view=10, so_cu=8, so_short_moi=15)
    assert c["cua_so"] == [f"L{i}" for i in range(100)]
    assert "L110" in c["pho_bien"] and len(c["pho_bien"]) == 10 and "L7" in c["pho_bien"]
    assert c["cu_dai"] == [f"L{i}" for i in range(122, 130)]
    assert c["short_moi"] == [f"S{i}" for i in range(15)] and c["short_cu"] == [f"S{i}" for i in range(32, 40)]
    assert len(c["tat_ca"]) == len(set(c["tat_ca"]))
    assert {"L110", "L129", "S39"} <= set(c["tat_ca"])


def test_chon_id_danh_sach_ngan_khong_trung():
    dai = [{"id": f"L{i}", "views": i} for i in range(5)]
    c = tv.chon_id(dai, [], so_dai=100, top_view=10, so_cu=8, so_short_moi=15)
    assert sorted(c["tat_ca"]) == [f"L{i}" for i in range(5)]


# ---------- ngày video đầu ----------

def test_ngay_nho_nhat_chi_tinh_video_doc_duoc():
    rows = [{"id": "a", "ngay_dang": "2026-09-04T01:00:00"}, {"id": "b", "ngay_dang": "2026-08-01T00:00:00"},
            {"id": "c", "ngay_dang": ""}]
    assert tv.ngay_nho_nhat(rows, ["a", "b", "c", "khong-co"]) == "2026-08-01"
    assert tv.ngay_nho_nhat(rows, ["c"]) is None


# ---------- chạy một kênh với yt-dlp giả ----------

class GiaYtdlp:
    """Giả lập yt-dlp: danh sách dài 120 video mới → cũ, 20 video cũ nhất là hội viên; 30 Shorts."""

    def __init__(self, hoi_vien_cuoi=0, n_dai=120):
        self.n_dai, self.goi = n_dai, []
        self.hoi_vien = {f"L{i}" for i in range(n_dai - hoi_vien_cuoi, n_dai)}
        self.ngay = {f"L{i}": 3 * i + 1 for i in range(n_dai)}
        self.ngay.update({f"S{i}": 2 * i + 1 for i in range(30)})

    def __call__(self, args):
        self.goi.append(list(args))
        dong_lenh = " ".join(args)
        if "--flat-playlist" in args:
            if dong_lenh.endswith("/videos"):
                return "\n".join(f"L{i}\t1200\t{1000 + i}" for i in range(self.n_dai)) + "\n", "", 0
            return "\n".join(f"S{i}\t30\t{50 + i}" for i in range(30)) + "\n", "", 0
        lst = Path(args[args.index("-a") + 1]).read_text(encoding="utf-8").split()
        ids = [u.split("v=")[1] for u in lst]
        out, err = [], []
        for i in ids:
            if i in self.hoi_vien:
                err.append(MEMBERS.format(i))
                continue
            out.append(json.dumps({"id": i, "timestamp": ts(self.ngay[i]), "duration": 30 if i[0] == "S" else 1200,
                                   "view_count": 1000, "like_count": 10, "comment_count": 1,
                                   "title": f"Tiêu đề {i}", "channel_id": "UCtest"}))
        return "\n".join(out) + "\n", "\n".join(err), 1 if err else 0


def test_thu_kenh_ghi_tsv_va_meta_voi_hoi_vien_va_cua_so(tmp_path):
    gia = GiaYtdlp(hoi_vien_cuoi=14)
    meta = tv.thu_kenh("UCtest", tmp_path, chay=gia, nghi=0, ngu=lambda s: None)
    rows = list(csv.DictReader((tmp_path / "UCtest.tsv").open(encoding="utf-8"), delimiter="\t"))
    assert rows and set(rows[0]) >= {"id", "ngay_dang", "thoi_luong_s", "view", "like", "binh_luan", "is_short", "tieu_de"}
    assert {r["is_short"] for r in rows if r["id"].startswith("S")} == {"1"}
    assert {r["is_short"] for r in rows if r["id"].startswith("L")} == {"0"}
    assert meta["so_hoi_vien"] == 14 and meta["n_dai_flat"] == 120 and meta["n_short_flat"] == 30
    # video cũ nhất đọc được là L105 (3*105+1 = 316 ngày trước), không phải video hội viên L106…L119
    assert meta["ngay_video_dau"].startswith((GOC - timedelta(days=316)).strftime("%Y-%m-%d"))
    # cửa sổ = ngày của video thứ 100 trong 100 video dài mới nhất: L99, 298 ngày trước
    assert meta["cua_so_tu"] == (GOC - timedelta(days=298)).strftime("%Y-%m-%d")
    assert json.loads((tmp_path / "UCtest.meta.json").read_text(encoding="utf-8"))["so_hoi_vien"] == 14
    assert meta["so_dong"] == len(rows)


def test_thu_kenh_chay_tuan_tu_nghi_giua_lenh_va_khong_cookie(tmp_path):
    gia, nghi = GiaYtdlp(), []
    tv.thu_kenh("UCtest", tmp_path, chay=gia, nghi=2.5, ngu=nghi.append)
    assert len(gia.goi) >= 4                       # flat videos, flat shorts, ít nhất một lô dump
    assert len(nghi) >= len(gia.goi) - 1 and set(nghi) == {2.5}
    for args in gia.goi:
        txt = " ".join(args).lower()
        assert "cookie" not in txt and "--ignore-config" in args and args[0] == "yt-dlp"
        assert "lang=en" in txt


def test_thu_kenh_bo_qua_kenh_da_co_du_file(tmp_path):
    gia = GiaYtdlp()
    tv.thu_kenh("UCtest", tmp_path, chay=gia, nghi=0, ngu=lambda s: None)
    gia2 = GiaYtdlp()
    meta = tv.thu_kenh("UCtest", tmp_path, chay=gia2, nghi=0, ngu=lambda s: None)
    assert gia2.goi == [] and meta["so_dong"] > 0
    tv.thu_kenh("UCtest", tmp_path, chay=gia2, nghi=0, ngu=lambda s: None, lam_lai=True)
    assert gia2.goi


def test_url_kenh():
    assert tv.url_kenh("UCabc_123") == "https://www.youtube.com/channel/UCabc_123"
    assert tv.url_kenh("@ten.kenh") == "https://www.youtube.com/@ten.kenh"
    assert tv.url_kenh("https://www.youtube.com/@x/videos") == "https://www.youtube.com/@x"
    assert tv.khoa_tep("@ten.kenh") == "@ten.kenh" and "/" not in tv.khoa_tep("https://www.youtube.com/@x/videos")


# ---------- PID ----------

def test_pid_tu_choi_khi_tien_trinh_cu_con_song(tmp_path):
    pid = tmp_path / "thu_video.pid"
    pid.write_text(str(os.getpid()), encoding="utf-8")
    with pytest.raises(tv.DangChay) as e:
        with tv.giu_pid(pid, doc_dong_lenh=lambda p: "python thu_video.py UCx --out-dir d"):
            pass
    assert str(os.getpid()) in str(e.value)


def test_pid_cho_chay_khi_tien_trinh_cu_da_chet_va_don_dep(tmp_path):
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    pid = tmp_path / "thu_video.pid"
    pid.write_text(str(p.pid), encoding="utf-8")
    with tv.giu_pid(pid):
        assert pid.read_text(encoding="utf-8").strip() == str(os.getpid())
    assert not pid.exists()


def test_pid_file_rac_khong_chan():
    assert tv.con_song(0) is False and tv.con_song(-5) is False


def test_con_song_nhan_ra_tien_trinh_dang_chay():
    assert tv.con_song(os.getpid()) is True
