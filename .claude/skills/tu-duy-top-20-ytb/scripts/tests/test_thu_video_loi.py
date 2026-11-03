"""Test thu_video.py khi yt-dlp lỗi: 429, rỗng, từng phần, quá thời gian, thiếu yt-dlp; mã thoát; file PID chặt hơn."""
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
E429 = "ERROR: [youtube:tab] HTTP Error 429: Too Many Requests"
MEMBERS = "ERROR: [youtube] {}: Join this channel to get access to members-only content like this video."


def ts(n):
    return int((GOC - timedelta(days=n)).timestamp())


class Gia:
    """yt-dlp giả: n_dai video dài (L0 mới nhất), n_short Shorts; có thể làm hỏng từng phần."""

    def __init__(self, n_dai=40, n_short=5, flat_dai=None, flat_short=None, dump=None):
        self.n_dai, self.n_short, self.goi = n_dai, n_short, []
        self.flat_dai, self.flat_short, self.dump = flat_dai, flat_short, dump

    def __call__(self, args):
        self.goi.append(list(args))
        if "--flat-playlist" in args:
            if args[-1].endswith("/videos"):
                if self.flat_dai:
                    return self.flat_dai
                return "\n".join(f"L{i}\t900\t{1000 + i}" for i in range(self.n_dai)) + "\n", "", 0
            if self.flat_short:
                return self.flat_short
            return "\n".join(f"S{i}\t30\t{50 + i}" for i in range(self.n_short)) + ("\n" if self.n_short else ""), "", 0
        ids = [u.split("v=")[1] for u in Path(args[args.index("-a") + 1]).read_text(encoding="utf-8").split()]
        if self.dump:
            return self.dump(ids)
        out = [json.dumps({"id": i, "timestamp": ts(3 * int(i[1:]) + 1), "duration": 900, "view_count": 10,
                           "like_count": 1, "comment_count": 0, "title": i, "channel_id": "UCz"}) for i in ids]
        return "\n".join(out) + "\n", "", 0


def chay(kenh, tmp_path, gia, **kw):
    return tv.thu_kenh(kenh, tmp_path, chay=gia, nghi=0, ngu=lambda s: None, log=lambda s: None, **kw)


def khong_file(tmp_path, khoa):
    return not (tmp_path / f"{khoa}.tsv").exists() and not (tmp_path / f"{khoa}.meta.json").exists()


# ---------- lỗi cứng: không ghi file ----------

def test_429_o_tab_videos_la_loi_khong_ghi_file_va_lan_sau_thu_lai(tmp_path):
    gia = Gia(flat_dai=("", E429, 1))
    with pytest.raises(tv.LoiThu, match="429"):
        chay("UCx", tmp_path, gia)
    assert khong_file(tmp_path, "UCx")
    gia2 = Gia(flat_dai=("", E429, 1))
    with pytest.raises(tv.LoiThu):
        chay("UCx", tmp_path, gia2)
    assert gia2.goi                                  # không dùng cache của lần hỏng


def test_tab_videos_rong_ma_ma_thoat_0_va_khong_shorts_la_loi(tmp_path):
    with pytest.raises(tv.LoiThu, match="không có video"):
        chay("UCx", tmp_path, Gia(n_dai=0, n_short=0))
    assert khong_file(tmp_path, "UCx")


def test_videos_ok_nhung_shorts_loi_429_la_loi(tmp_path):
    with pytest.raises(tv.LoiThu, match="shorts"):
        chay("UCy", tmp_path, Gia(flat_short=("", E429, 1)))
    assert khong_file(tmp_path, "UCy")


def test_kenh_khong_co_tab_shorts_van_binh_thuong(tmp_path):
    gia = Gia(flat_short=("", "ERROR: [youtube:tab] The channel does not have a shorts tab", 1))
    m = chay("UCy", tmp_path, gia)
    assert m["n_short_flat"] == 0 and m["so_dong"] > 0 and "loi" not in m


def test_lo_doc_loi_va_khong_ra_dong_nao_la_loi(tmp_path):
    gia = Gia(dump=lambda ids: ("", E429, 1))
    with pytest.raises(tv.LoiThu, match="429"):
        chay("UCx", tmp_path, gia)
    assert khong_file(tmp_path, "UCx")


def test_yt_dlp_khong_ton_tai_va_qua_thoi_gian_la_loi_thu(monkeypatch):
    def thieu(*a, **k):
        raise FileNotFoundError("yt-dlp")

    monkeypatch.setattr(tv.subprocess, "run", thieu)
    with pytest.raises(tv.LoiThu, match="yt-dlp"):
        tv.chay_ytdlp(["yt-dlp", "--version"])

    def lau(*a, **k):
        raise subprocess.TimeoutExpired(a[0], k.get("timeout", 1))

    monkeypatch.setattr(tv.subprocess, "run", lau)
    with pytest.raises(tv.LoiThu, match="quá"):
        tv.chay_ytdlp(["yt-dlp", "x"])


def test_chay_ytdlp_truyen_timeout(monkeypatch):
    thay = {}

    def gia(args, **k):
        thay.update(k)
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(tv.subprocess, "run", gia)
    tv.chay_ytdlp(["yt-dlp", "x"])
    assert thay.get("timeout") and thay["timeout"] > 0


# ---------- đọc thiếu ----------

def test_doc_thieu_it_duoc_ghi_vao_meta_nhung_khong_phai_loi(tmp_path):
    bo = {"L3", "L5"}                               # 2/45 video không đọc được (không phải hội viên)

    def dump(ids):
        out = [json.dumps({"id": i, "timestamp": ts(3 * int(i[1:]) + 1), "duration": 900, "view_count": 10,
                           "like_count": 1, "comment_count": 0, "title": i, "channel_id": "UCz"})
               for i in ids if i not in bo]
        return "\n".join(out) + "\n", "ERROR: [youtube] L3: Video unavailable\nERROR: [youtube] L5: Video unavailable", 1

    m = chay("UCx", tmp_path, Gia(dump=dump))
    assert m["so_thieu"] == 2 and sorted(m["thieu_ids"]) == ["L3", "L5"] and m["loi_khac"] == 2
    assert "loi" not in m and m["so_yeu_cau"] == 45


def test_doc_thieu_nhieu_la_loi_ghi_meta_de_lan_sau_lam_lai(tmp_path):
    def dump(ids):
        out = [json.dumps({"id": i, "timestamp": ts(3 * int(i[1:]) + 1), "duration": 900, "view_count": 10,
                           "like_count": 1, "comment_count": 0, "title": i, "channel_id": "UCz"})
               for k, i in enumerate(ids) if k % 3]
        return "\n".join(out) + "\n", "", 0          # 1/3 video biến mất, yt-dlp vẫn báo thành công

    m = chay("UCx", tmp_path, Gia(dump=dump))
    assert m["loi"] and "thiếu" in m["loi"] and m["so_thieu"] > 5
    gia2 = Gia(dump=dump)
    chay("UCx", tmp_path, gia2)
    assert gia2.goi                                   # meta có loi thì lần sau tự làm lại


def test_hoi_vien_khong_tinh_la_thieu(tmp_path):
    hv = {f"L{i}" for i in range(30, 40)}

    def dump(ids):
        out = [json.dumps({"id": i, "timestamp": ts(3 * int(i[1:]) + 1), "duration": 900, "view_count": 10,
                           "like_count": 1, "comment_count": 0, "title": i, "channel_id": "UCz"})
               for i in ids if i not in hv]
        return "\n".join(out) + "\n", "\n".join(MEMBERS.format(i) for i in ids if i in hv), 1

    m = chay("UCx", tmp_path, Gia(dump=dump))
    assert m["so_hoi_vien"] == 10 and m["so_thieu"] == 0 and "loi" not in m


# ---------- mã thoát ----------

def test_main_thoat_ma_khac_0_khi_co_kenh_loi(tmp_path, capsys):
    rc = tv.main(["UCz", "--out-dir", str(tmp_path), "--nghi", "0"], chay=Gia(flat_dai=("", E429, 1)))
    assert rc != 0
    o = capsys.readouterr()
    assert "LỖI" in o.out + o.err and "XONG TẤT CẢ" not in o.out


def test_main_mot_kenh_loi_mot_kenh_ok_van_chay_het_va_thoat_khac_0(tmp_path):
    def gia(args):
        if any("UCbad" in a for a in args):
            return "", E429, 1
        return Gia()(args)

    rc = tv.main(["UCbad", "UCgood", "--out-dir", str(tmp_path), "--nghi", "0"], chay=gia)
    assert rc != 0 and (tmp_path / "UCgood.tsv").exists() and not (tmp_path / "UCbad.tsv").exists()


def test_main_ok_thoat_0(tmp_path):
    assert tv.main(["UCgood", "--out-dir", str(tmp_path), "--nghi", "0"], chay=Gia()) == 0


# ---------- nghỉ giữa các yêu cầu ----------

def test_lenh_doc_lo_co_sleep_requests(tmp_path):
    gia = Gia()
    chay("UCx", tmp_path, gia)
    lo = [a for a in gia.goi if "-a" in a]
    assert lo and all("--sleep-requests" in a for a in lo)
    i = lo[0].index("--sleep-requests")
    assert float(lo[0][i + 1]) >= 1


# ---------- file PID ----------

def test_pid_song_nhung_khong_phai_thu_video_thi_cho_chay(tmp_path):
    pid = tmp_path / "thu_video.pid"
    pid.write_text(str(os.getpid()), encoding="utf-8")
    with tv.giu_pid(pid, doc_dong_lenh=lambda p: "notepad.exe"):
        assert pid.read_text(encoding="utf-8").strip() == str(os.getpid())
    assert not pid.exists()


def test_pid_song_va_la_thu_video_thi_tu_choi_va_khong_goi_y_taskkill_mu(tmp_path):
    pid = tmp_path / "thu_video.pid"
    pid.write_text(str(os.getpid()), encoding="utf-8")
    with pytest.raises(tv.DangChay) as e:
        with tv.giu_pid(pid, doc_dong_lenh=lambda p: "python scripts/thu_video.py UCx --out-dir d"):
            pass
    assert "taskkill" not in str(e.value) and "Get-CimInstance" in str(e.value)
    assert pid.read_text(encoding="utf-8").strip() == str(os.getpid())          # không đụng file của tiến trình khác


def test_pid_khong_doc_duoc_dong_lenh_thi_coi_la_dang_chay(tmp_path):
    pid = tmp_path / "thu_video.pid"
    pid.write_text(str(os.getpid()), encoding="utf-8")
    with pytest.raises(tv.DangChay):
        with tv.giu_pid(pid, doc_dong_lenh=lambda p: None):
            pass


def test_pid_ghi_nguyen_tu_khong_de_len_file_vua_tao(tmp_path, monkeypatch):
    pid = tmp_path / "thu_video.pid"
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    pid.write_text(str(p.pid), encoding="utf-8")                                  # PID chết: file cũ bị thay
    real_open = os.open
    cac_co = []

    def mo(path, flags, *a, **k):
        cac_co.append(flags)
        return real_open(path, flags, *a, **k)

    monkeypatch.setattr(tv.os, "open", mo)
    with tv.giu_pid(pid):
        pass
    assert cac_co and all(f & os.O_EXCL for f in cac_co)


def test_dong_lenh_tien_trinh_cua_chinh_minh_doc_duoc():
    d = tv.dong_lenh_tien_trinh(os.getpid())
    assert d is None or "python" in d.lower() or "pytest" in d.lower()
