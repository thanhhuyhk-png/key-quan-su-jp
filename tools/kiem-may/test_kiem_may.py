"""Test kiem-may.py: giả lập lệnh ngoài, RAM, ổ đĩa, cổng; dùng tệp khoá và cau-hinh.toml giả trong thư mục tạm."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

_TEP = Path(__file__).with_name("kiem-may.py")
_spec = importlib.util.spec_from_file_location("kiem_may", _TEP)
km = importlib.util.module_from_spec(_spec)
sys.modules["kiem_may"] = km
_spec.loader.exec_module(km)

BI_MAT = "sk-THU-NGHIEM-bi-mat-9f8e7d6c5b4a"
TEP_KHOA = "." + "env"

LENH_DU = {
    "node": (0, "v24.22.1"),
    "ffmpeg": (0, "ffmpeg version 7.1-full_build-www.gyan.dev Copyright (c) 2000-2024"),
    "ffprobe": (0, "ffprobe version 7.1-full_build-www.gyan.dev Copyright"),
    "git": (0, "git version 2.47.0.windows.1"),
    "gh --version": (0, "gh version 2.60.1 (2024-10-01)"),
    "gh auth": (0, "Logged in to github.com"),
    "claude": (0, "2.1.5 (Claude Code)"),
}


def gia_chay(bang):
    def chay(lenh, timeout=15):
        chuoi = " ".join(lenh)
        for dau, ra in bang.items():
            if chuoi.startswith(dau):
                return ra
        return None
    return chay


@pytest.fixture
def may(tmp_path, monkeypatch):
    """Máy đủ mọi thứ; mỗi test bỏ bớt thứ cần thử."""
    repo = tmp_path / "repo"
    (repo / "tools").mkdir(parents=True)
    (repo / ".claude" / "skills").mkdir(parents=True)
    avs = tmp_path / "avs"
    avs.mkdir()
    chrome = tmp_path / "chrome.exe"
    chrome.write_text("x")
    (tmp_path / "out").mkdir()
    (repo / "cau-hinh.toml").write_text(
        f'[duong_dan]\noutput = "{(tmp_path / "out").as_posix()}"\nchrome = "{chrome.as_posix()}"\n'
        f'goha_avs = "{avs.as_posix()}"\n', encoding="utf-8")
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("DEEPGRAM_API_KEY", raising=False)
    monkeypatch.setattr(km, "chay", gia_chay(dict(LENH_DU)))
    monkeypatch.setattr(km, "tim_module", lambda ten: "1.0")
    monkeypatch.setattr(km, "ram_gb", lambda: 32.0)
    monkeypatch.setattr(km, "dung_luong_trong_gb", lambda p: 500.0)
    monkeypatch.setattr(km, "cong_mo", lambda host, cong: False)
    monkeypatch.setattr(km, "ung_vien_trinh_duyet", lambda: [])
    return repo


def dat_chay(monkeypatch, **sua):
    bang = dict(LENH_DU)
    for k, v in sua.items():
        k = k.replace("__", " ")
        if v is None:
            bang.pop(k, None)
        else:
            bang[k] = v
    monkeypatch.setattr(km, "chay", gia_chay(bang))


def hang(kq, dau):
    return next(m for m in kq.muc if m.ten.startswith(dau))


def viet_khoa(repo, **khoa):
    (repo / TEP_KHOA).write_text("".join(f"{k}={v}\n" for k, v in khoa.items()), encoding="utf-8")


def test_may_du_tat_ca_dat_toi_thieu(may):
    viet_khoa(may, ELEVENLABS_API_KEY=BI_MAT)
    kq = km.kiem(may)
    assert kq.thieu_bat_buoc == []
    assert kq.dat_toi_thieu
    assert kq.muc_chay == "Đầy đủ"


def test_thieu_node_goi_y_winget(may, monkeypatch):
    dat_chay(monkeypatch, node=None)
    kq = km.kiem(may)
    m = hang(kq, "Node")
    assert not m.co and "winget install OpenJS.NodeJS.LTS" in m.lenh_cai
    assert not kq.dat_toi_thieu


def test_node_cu_hon_22_coi_la_thieu(may, monkeypatch):
    dat_chay(monkeypatch, node=(0, "v20.11.0"))
    m = hang(km.kiem(may), "Node")
    assert not m.co and "20.11.0" in m.phien_ban


def test_thieu_ffprobe_rieng_voi_ffmpeg(may, monkeypatch):
    dat_chay(monkeypatch, ffprobe=None)
    kq = km.kiem(may)
    assert hang(kq, "ffmpeg").co
    assert not hang(kq, "ffprobe").co
    assert "winget install Gyan.FFmpeg" in hang(kq, "ffprobe").lenh_cai


def test_gh_chua_dang_nhap(may, monkeypatch):
    dat_chay(monkeypatch, gh__auth=(1, "You are not logged into any GitHub hosts"))
    m = hang(km.kiem(may), "GitHub CLI")
    assert not m.co and "gh auth login" in m.lenh_cai


def test_thieu_git_va_claude(may, monkeypatch):
    dat_chay(monkeypatch, git=None, claude=None)
    kq = km.kiem(may)
    assert not hang(kq, "Git").co and "Git.Git" in hang(kq, "Git").lenh_cai
    assert not hang(kq, "Claude Code").co


def test_thu_vien_thieu_goi_y_pip(may, monkeypatch):
    monkeypatch.setattr(km, "tim_module", lambda ten: None if ten == "cv2" else "1.0")
    kq = km.kiem(may)
    m = hang(kq, "Thư viện cv2")
    assert not m.co and "pip install -r requirements.txt" in m.lenh_cai
    assert hang(kq, "Thư viện numpy").co
    assert "cv2" in " ".join(kq.thieu_bat_buoc)


def test_du_9_thu_vien_theo_requirements_gom_fonttools(may):
    ten = [m.ten for m in km.kiem(may).muc if m.ten.startswith("Thư viện")]
    assert len(ten) == 9 and "Thư viện fontTools" in ten


def test_thieu_fonttools_la_thieu_bat_buoc(may, monkeypatch):
    monkeypatch.setattr(km, "tim_module", lambda ten: None if ten == "fontTools" else "1.0")
    kq = km.kiem(may)
    m = hang(kq, "Thư viện fontTools")
    assert not m.co and m.bat_buoc and "pip install -r requirements.txt" in m.lenh_cai
    assert not kq.dat_toi_thieu


def test_o_trong_duoi_60gb(may, monkeypatch):
    monkeypatch.setattr(km, "dung_luong_trong_gb", lambda p: 59.0)
    m = hang(km.kiem(may), "Ổ trống")
    assert not m.co and "59" in m.phien_ban
    monkeypatch.setattr(km, "dung_luong_trong_gb", lambda p: 60.0)
    assert hang(km.kiem(may), "Ổ trống").co


def test_o_trong_do_o_chua_output_khong_ton_tai_thi_di_len_cha(tmp_path):
    sau = tmp_path / "a" / "b" / "c"
    assert km.thu_muc_do_duoc(sau) == tmp_path


def test_ram_ba_muc(may, monkeypatch):
    monkeypatch.setattr(km, "ram_gb", lambda: 16.0)
    m = hang(km.kiem(may), "RAM")
    assert m.co and "tốt" in m.ghi_chu
    monkeypatch.setattr(km, "ram_gb", lambda: 8.0)
    m = hang(km.kiem(may), "RAM")
    assert m.co and "chế độ nhẹ" in m.ghi_chu
    monkeypatch.setattr(km, "ram_gb", lambda: 4.0)
    assert not hang(km.kiem(may), "RAM").co


def test_goha_avs_chua_cau_hinh(may):
    (may / "cau-hinh.toml").unlink()
    m = hang(km.kiem(may), "Goha AVS")
    assert not m.co and "cau-hinh.toml" in m.ghi_chu


def test_goha_avs_duong_dan_khong_ton_tai(may):
    (may / "cau-hinh.toml").write_text('[duong_dan]\ngoha_avs = "Z:/khong/co"\n', encoding="utf-8")
    assert not hang(km.kiem(may), "Goha AVS").co


def test_goha_avs_dang_chay_khi_cong_8787_tra_loi(may, monkeypatch):
    goi = []
    monkeypatch.setattr(km, "cong_mo", lambda host, cong: goi.append(cong) or True)
    m = hang(km.kiem(may), "Goha AVS")
    assert m.co and "đang chạy" in m.phien_ban and goi == [8787]


def test_thieu_avs_o_muc_day_du_la_bat_buoc(may):
    viet_khoa(may, ELEVENLABS_API_KEY=BI_MAT)
    (may / "cau-hinh.toml").unlink()
    kq = km.kiem(may)
    assert hang(kq, "Goha AVS").bat_buoc and "Goha AVS" in kq.thieu_bat_buoc
    assert km.main(["--repo", str(may)]) == 1


def test_thieu_avs_o_muc_khac_la_tuy_chon_khong_lam_thoat_1(may, tmp_path, capsys):
    (may / "cau-hinh.toml").write_text(
        f'[duong_dan]\nchrome = "{(tmp_path / "chrome.exe").as_posix()}"\n', encoding="utf-8")
    for khoa in ({}, {"DEEPGRAM_API_KEY": BI_MAT}):
        viet_khoa(may, **khoa)
        kq = km.kiem(may)
        m = hang(kq, "Goha AVS")
        assert not m.co and not m.bat_buoc and "Goha AVS" not in kq.thieu_bat_buoc
        assert "kit.py tron" in m.ghi_chu and "master" in m.ghi_chu
        assert kq.dat_toi_thieu and kq.muc_chay is not None
        assert km.main(["--repo", str(may)]) == 0
        out = capsys.readouterr().out
        assert "Goha AVS (tuỳ chọn)" in out and "kit.py tron" in out


def test_goha_avs_co_nhung_chua_chay(may):
    m = hang(km.kiem(may), "Goha AVS")
    assert m.co and "chưa chạy" in m.phien_ban


def test_trinh_duyet_theo_khoa_chrome(may):
    assert hang(km.kiem(may), "Chrome").co


def test_trinh_duyet_in_duong_dan_tim_duoc(may, tmp_path):
    m = hang(km.kiem(may), "Chrome")
    assert m.phien_ban == (tmp_path / "chrome.exe").as_posix()
    assert "chrome" in km.bang_md(km.kiem(may))


def test_trinh_duyet_mac_dinh_khi_khoa_sai(may, monkeypatch, tmp_path):
    (may / "cau-hinh.toml").write_text('[duong_dan]\nchrome = "Z:/khong/co.exe"\n', encoding="utf-8")
    edge = tmp_path / "msedge.exe"
    edge.write_text("x")
    monkeypatch.setattr(km, "ung_vien_trinh_duyet", lambda: [edge])
    m = hang(km.kiem(may), "Chrome")
    assert m.co and "msedge" in m.phien_ban


def test_khong_co_trinh_duyet(may):
    (may / "cau-hinh.toml").write_text('[duong_dan]\nchrome = "Z:/khong/co.exe"\n', encoding="utf-8")
    m = hang(km.kiem(may), "Chrome")
    assert not m.co and "winget install Google.Chrome" in m.lenh_cai


def test_khoa_chi_bao_co_khong_va_khong_lo_gia_tri(may, capsys):
    viet_khoa(may, ELEVENLABS_API_KEY=BI_MAT, DEEPGRAM_API_KEY="")
    kq = km.kiem(may)
    assert hang(kq, "Khoá ELEVENLABS_API_KEY").co
    assert not hang(kq, "Khoá DEEPGRAM_API_KEY").co
    ra = km.bang_md(kq) + km.ra_json(kq) + repr(kq)
    assert BI_MAT not in ra
    tep = may / "kiem-may.md"
    assert km.main(["--repo", str(may), "--ra", str(tep), "--json"]) in (0, 1)
    assert BI_MAT not in tep.read_text(encoding="utf-8") + capsys.readouterr().out


def test_khoa_tu_bien_moi_truong(may, monkeypatch):
    monkeypatch.setenv("DEEPGRAM_API_KEY", BI_MAT)
    kq = km.kiem(may)
    assert hang(kq, "Khoá DEEPGRAM_API_KEY").co


def test_doc_khoa_co_bo_qua_chu_thich_ngoac_va_export(tmp_path):
    tep = tmp_path / TEP_KHOA
    tep.write_text('# ghi chú\nELEVENLABS_API_KEY="abc"\nexport DEEPGRAM_API_KEY=\nKHAC=1\n', encoding="utf-8-sig")
    assert km.doc_khoa_co(tep, {}) == {"ELEVENLABS_API_KEY"}


def test_chon_muc_theo_khoa(may):
    assert km.kiem(may).muc_chay == "Miễn phí"
    viet_khoa(may, DEEPGRAM_API_KEY=BI_MAT)
    assert km.kiem(may).muc_chay == "Tiết kiệm"
    viet_khoa(may, ELEVENLABS_API_KEY=BI_MAT)
    assert km.kiem(may).muc_chay == "Đầy đủ"


def test_ram_thap_van_day_du_nhung_ghi_chu_che_do_nhe(may, monkeypatch):
    viet_khoa(may, ELEVENLABS_API_KEY=BI_MAT)
    monkeypatch.setattr(km, "ram_gb", lambda: 8.0)
    kq = km.kiem(may)
    assert kq.muc_chay == "Đầy đủ" and "chế độ nhẹ" in kq.ly_do_muc


def test_thieu_bat_buoc_thi_chua_chon_muc(may, monkeypatch):
    viet_khoa(may, ELEVENLABS_API_KEY=BI_MAT)
    dat_chay(monkeypatch, node=None)
    kq = km.kiem(may)
    assert kq.muc_chay is None and "chưa đủ" in kq.ly_do_muc.lower()


def test_phat_hien_lenh_reelcrew_con_sot(may):
    sk = may / ".claude" / "skills" / "x"
    sk.mkdir()
    (sk / "SKILL.md").write_text("Chạy:\n  reelcrew deliver video.mp4 --lufs -14\n", encoding="utf-8")
    (may / "tools" / "a.py").write_text('subprocess.run(["reelcrew", "check", "v.mp4"])\n', encoding="utf-8")
    kq = km.kiem(may)
    m = hang(kq, "Kit không gọi reelcrew")
    assert not m.co and not m.bat_buoc
    assert any("SKILL.md:2" in d for d in kq.reelcrew)
    assert any("a.py:1" in d for d in kq.reelcrew)
    # lỗi của kit chỉ cảnh báo, không chặn hội viên cài máy
    assert kq.dat_toi_thieu and "Kit không gọi reelcrew" not in kq.thieu_bat_buoc
    assert kq.muc_chay is not None
    assert any("reelcrew" in c and "báo chủ kit" in c for c in kq.canh_bao)
    md = km.bao_cao_md(kq)
    assert "SKILL.md:2" in md and "a.py:1" in md
    assert km.main(["--repo", str(may)]) == 0


def test_reelcrew_nhac_ten_hoac_duong_dan_khong_phai_lenh(may):
    sk = may / ".claude" / "skills" / "x"
    sk.mkdir()
    (sk / "SKILL.md").write_text(
        "Máy hội viên không có ReelCrew.\nMedia ở <output>/x và <output>\n"
        "Thư mục reelcrew-cu không dùng nữa.\n", encoding="utf-8")
    assert hang(km.kiem(may), "Kit không gọi reelcrew").co


def test_quet_reelcrew_bo_qua_chinh_tools_kiem_may_va_node_modules(may):
    (may / "tools" / "kiem-may").mkdir()
    (may / "tools" / "kiem-may" / "t.py").write_text("reelcrew deliver x\n", encoding="utf-8")
    (may / "tools" / "node_modules").mkdir()
    (may / "tools" / "node_modules" / "m.js").write_text("reelcrew deliver x\n", encoding="utf-8")
    assert km.quet_reelcrew(may) == []


def test_main_ra_tep_md_va_ma_thoat(may, tmp_path, capsys):
    viet_khoa(may, ELEVENLABS_API_KEY=BI_MAT)
    tep = tmp_path / "kiem-may.md"
    ma = km.main(["--repo", str(may), "--ra", str(tep)])
    assert ma == 0
    chu = tep.read_bytes().decode("utf-8")
    assert "| Thành phần | Có/thiếu | Phiên bản | Lệnh cài |" in chu
    assert "Đầy đủ" in chu
    assert "\r" not in chu
    assert "Đầy đủ" in capsys.readouterr().out


def test_main_thieu_thi_ma_thoat_1(may, monkeypatch):
    dat_chay(monkeypatch, ffmpeg=None)
    assert km.main(["--repo", str(may)]) == 1


def test_main_json_hop_le(may, capsys):
    viet_khoa(may, ELEVENLABS_API_KEY=BI_MAT)
    assert km.main(["--repo", str(may), "--json"]) == 0
    d = json.loads(capsys.readouterr().out)
    assert d["muc_chay"] == "Đầy đủ" and d["dat_toi_thieu"] is True
    assert any(m["ten"].startswith("Node") for m in d["muc"])


def test_chay_tra_none_khi_thieu_lenh(monkeypatch):
    monkeypatch.setattr(km.shutil, "which", lambda ten: None)
    assert km.chay(["khong-co-lenh", "-v"]) is None


def test_chay_goi_subprocess_bang_danh_sach_co_timeout(monkeypatch):
    thay = {}

    def gia(lenh, **kw):
        thay.update(lenh=lenh, kw=kw)
        return subprocess.CompletedProcess(lenh, 0, stdout="v24.1.0\n", stderr="")

    monkeypatch.setattr(km.shutil, "which", lambda ten: "C:/x/node.exe")
    monkeypatch.setattr(km.subprocess, "run", gia)
    assert km.chay(["node", "-v"]) == (0, "v24.1.0")
    assert thay["lenh"] == ["C:/x/node.exe", "-v"]
    assert thay["kw"].get("shell", False) is False and thay["kw"]["timeout"] > 0


def test_chay_het_gio_tra_none(monkeypatch):
    def gia(lenh, **kw):
        raise subprocess.TimeoutExpired(lenh, 1)

    monkeypatch.setattr(km.shutil, "which", lambda ten: "x")
    monkeypatch.setattr(km.subprocess, "run", gia)
    assert km.chay(["node", "-v"]) is None


def test_tep_khoa_ma_hoa_la_khong_lam_sap(tmp_path):
    tep = tmp_path / TEP_KHOA
    tep.write_bytes("ELEVENLABS_API_KEY=abc\n".encode("utf-16"))
    canh_bao = []
    assert km.doc_khoa_co(tep, {"DEEPGRAM_API_KEY": "x"}, canh_bao) == {"DEEPGRAM_API_KEY"}
    assert any("không đọc được" in c and TEP_KHOA in c for c in canh_bao)
    assert "abc" not in "".join(canh_bao)


def test_kiem_voi_tep_khoa_hong_van_chay(may):
    (may / TEP_KHOA).write_bytes(b"\xff\xfe\x00\x01 ELEVENLABS_API_KEY=" + BI_MAT.encode() )
    kq = km.kiem(may)
    assert not hang(kq, "Khoá ELEVENLABS_API_KEY").co
    assert any("không đọc được" in c for c in kq.canh_bao)
    assert BI_MAT not in km.bao_cao_md(kq) + km.ra_json(kq)


def test_ra_tao_thu_muc_cha(may, tmp_path):
    tep = tmp_path / "moi" / "con" / "kiem-may.md"
    assert km.main(["--repo", str(may), "--ra", str(tep)]) in (0, 1)
    assert tep.exists()


def test_quet_reelcrew_lien_ket_hong_khong_sap(may, monkeypatch):
    goc = may / ".claude" / "skills"
    goc.mkdir(parents=True, exist_ok=True)
    that = km.os.walk

    def walk_gia(duong, *a, **kw):
        for dg, d, t in that(duong, *a, **kw):
            yield dg, d, list(t) + (["ma-hong.py"] if Path(dg) == goc else [])

    monkeypatch.setattr(km.os, "walk", walk_gia)
    assert km.quet_reelcrew(may) == []
