"""Test them_tab.py: thêm tab «1b. Kênh mới nổi» (tuỳ chọn) và «12. Video top 20 %» vào sheet của xuat_sheet.py."""
import json
import subprocess
import sys
from pathlib import Path

import openpyxl

SCRIPT = Path(__file__).resolve().parent.parent / "them_tab.py"
COT_VIDEO = "id\tngay_dang\tthoi_luong_s\tview\tlike\tbinh_luan\tis_short\ttieu_de\n"
COT_MOI_NOI = ("ten\ttuoi_ngay\tvideo_dai\tshort\tdai_du_7_ngay\ttrung_vi_dai_7ngay\tview_cao_nhat\tsub\t"
               "sub_moi_ngay\tvideo_dai_moi_tuan\tghi_chu\n")


def chuan_bi(tmp: Path) -> tuple[Path, Path, Path]:
    xlsx = tmp / "top20.xlsx"
    wb = openpyxl.Workbook()
    wb.active.title = "0. Tổng quan & Model Link"
    wb.create_sheet("1. TOP 20")
    wb.save(xlsx)
    dinh_tinh = tmp / "dinh-tinh.json"
    dinh_tinh.write_text(json.dumps({
        "UCmau": {"ten": "Kênh A", "link": "https://youtube.com/@a", "giu_loai": "Giữ"},
        "UCloai": {"ten": "Kênh B", "link": "https://youtube.com/@b", "giu_loai": "Loại"},
    }, ensure_ascii=False), encoding="utf-8")
    video = tmp / "thu-video"
    video.mkdir()
    dong = "".join(f"v{i}\t2026-10-0{i % 9 + 1}\t600\t{i * 100}\t\t\t0\tVideo {i}\n" for i in range(1, 11))
    (video / "UCmau.tsv").write_text(COT_VIDEO + dong + "s1\t2026-10-01\t30\t99999\t\t\t1\tShort\n", encoding="utf-8")
    (video / "UCloai.tsv").write_text(COT_VIDEO + dong, encoding="utf-8")
    return xlsx, dinh_tinh, video


def chay(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), *args], capture_output=True, text=True,
                          encoding="utf-8")


def test_tab_12_lay_20_phan_tram_video_dai_bo_kenh_loai_va_short(tmp_path):
    xlsx, dinh_tinh, video = chuan_bi(tmp_path)
    r = chay(str(xlsx), "--dinh-tinh", str(dinh_tinh), "--video-dir", str(video), "--model", "UCmau")
    assert r.returncode == 0, r.stderr
    ws = openpyxl.load_workbook(xlsx)["12. Video top 20 %"]
    hang = [[c.value for c in row] for row in ws.iter_rows(min_row=3)]
    assert hang[0][0] == "★ Kênh A — 3/10 video dài"  # tối thiểu 3 video, Short không tính
    assert [h[6] for h in hang[1:]] == [1000, 900, 800]
    assert not any("Kênh B" in str(h[0]) for h in hang)
    assert "1b. Kênh mới nổi (làm theo)" not in openpyxl.load_workbook(xlsx).sheetnames
    assert "bỏ qua tab 1b" in r.stdout


def test_tab_1b_khi_co_bang_moi_noi_va_danh_dau_model_link(tmp_path):
    xlsx, dinh_tinh, video = chuan_bi(tmp_path)
    moi_noi = tmp_path / "moi-noi.tsv"
    moi_noi.write_text(COT_MOI_NOI + "Kênh A\t120\t15\t3\t12\t5400\t90000\t2000\t16.7\t1.5\t\n", encoding="utf-8")
    r = chay(str(xlsx), "--dinh-tinh", str(dinh_tinh), "--video-dir", str(video), "--model", "UCmau",
             "--moi-noi", str(moi_noi), "--ngay-do", "01/12/2026")
    assert r.returncode == 0, r.stderr
    wb = openpyxl.load_workbook(xlsx)
    assert wb.sheetnames.index("1b. Kênh mới nổi (làm theo)") == 2
    ws = wb["1b. Kênh mới nổi (làm theo)"]
    assert "01/12/2026" in ws["A2"].value
    assert [c.value for c in ws[4]][:5] == [1, "★ MODEL LINK", "Kênh A", "https://youtube.com/@a", 120]


def test_chay_lai_thay_tab_cu_khong_nhan_doi(tmp_path):
    xlsx, dinh_tinh, video = chuan_bi(tmp_path)
    for _ in range(2):
        assert chay(str(xlsx), "--dinh-tinh", str(dinh_tinh), "--video-dir", str(video), "--model", "UCmau").returncode == 0
    assert openpyxl.load_workbook(xlsx).sheetnames.count("12. Video top 20 %") == 1


def test_thieu_tep_dau_vao_bao_loi_ro(tmp_path):
    xlsx, _, video = chuan_bi(tmp_path)
    r = chay(str(xlsx), "--dinh-tinh", str(tmp_path / "khong-co.json"), "--video-dir", str(video), "--model", "UCmau")
    assert r.returncode != 0
    assert "khong-co.json" in r.stderr


def import_them_tab():
    import importlib.util
    spec = importlib.util.spec_from_file_location("them_tab", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_so_chap_nhan_so_thuc_dau_phay_va_o_trong():
    m = import_them_tab()
    assert m.so("400.0") == 400
    assert m.so("1,234") == 1234
    assert m.so(" 12 ") == 12
    assert m.so("") is None and m.so(None) is None
    assert m.so("abc") is None
    assert m.so("16.7", float) == 16.7


def test_o_so_thuc_trong_tsv_khong_van(tmp_path):
    xlsx, dinh_tinh, video = chuan_bi(tmp_path)
    (video / "UCmau.tsv").write_text(
        COT_VIDEO + "v1\t2026-10-01\t600.0\t1,500\t\t\t0\tVideo 1\nv2\t2026-10-02\t\t\t\t\t0\tVideo 2\n", encoding="utf-8")
    r = chay(str(xlsx), "--dinh-tinh", str(dinh_tinh), "--video-dir", str(video), "--model", "UCmau")
    assert r.returncode == 0, r.stderr
    ws = openpyxl.load_workbook(xlsx)["12. Video top 20 %"]
    hang = [[c.value for c in row] for row in ws.iter_rows(min_row=4)]
    assert hang[0][6] == 1500 and hang[0][5] == 10


def test_tsv_video_thieu_cot_bao_ten_tep_ma_2(tmp_path):
    xlsx, dinh_tinh, video = chuan_bi(tmp_path)
    (video / "UCmau.tsv").write_text("id\tview\nv1\t5\n", encoding="utf-8")
    r = chay(str(xlsx), "--dinh-tinh", str(dinh_tinh), "--video-dir", str(video), "--model", "UCmau")
    assert r.returncode == 2
    assert "UCmau.tsv" in r.stderr and "is_short" in r.stderr and "Traceback" not in r.stderr


def test_bang_moi_noi_thieu_cot_bao_ten_tep_ma_2(tmp_path):
    xlsx, dinh_tinh, video = chuan_bi(tmp_path)
    moi_noi = tmp_path / "moi-noi.tsv"
    moi_noi.write_text("ten\ttuoi_ngay\nKênh A\t120\n", encoding="utf-8")
    r = chay(str(xlsx), "--dinh-tinh", str(dinh_tinh), "--video-dir", str(video), "--model", "UCmau",
             "--moi-noi", str(moi_noi))
    assert r.returncode == 2
    assert "moi-noi.tsv" in r.stderr and "trung_vi_dai_7ngay" in r.stderr and "Traceback" not in r.stderr


def test_loi_dau_vao_khong_dung_vao_sheet_goc(tmp_path):
    xlsx, dinh_tinh, video = chuan_bi(tmp_path)
    (video / "UCmau.tsv").write_text("id\tview\nv1\t5\n", encoding="utf-8")
    truoc = xlsx.read_bytes()
    chay(str(xlsx), "--dinh-tinh", str(dinh_tinh), "--video-dir", str(video), "--model", "UCmau")
    assert xlsx.read_bytes() == truoc
    assert not list(tmp_path.glob("*.part.xlsx"))


def test_ghi_nguyen_tu_khong_de_tep_tam(tmp_path):
    xlsx, dinh_tinh, video = chuan_bi(tmp_path)
    assert chay(str(xlsx), "--dinh-tinh", str(dinh_tinh), "--video-dir", str(video), "--model", "UCmau").returncode == 0
    assert not list(tmp_path.glob("*.part.xlsx"))


def test_o_chu_bat_dau_bang_dau_cong_thuc_ghi_dang_chu(tmp_path):
    xlsx, dinh_tinh, video = chuan_bi(tmp_path)
    dong = "".join(f"v{i}\t2026-10-01\t600\t{100 - i}\t\t\t0\t{t}\n" for i, t in enumerate(["=== TOP ===", "+1 cách", "-x", "@ai"], 1))
    dong += "".join(f"f{i}\t2026-10-01\t600\t{i}\t\t\t0\tBình thường {i}\n" for i in range(12))  # 16 video: lấy 4
    (video / "UCmau.tsv").write_text(COT_VIDEO + dong, encoding="utf-8")
    assert chay(str(xlsx), "--dinh-tinh", str(dinh_tinh), "--video-dir", str(video), "--model", "UCmau").returncode == 0
    ws = openpyxl.load_workbook(xlsx)["12. Video top 20 %"]
    cell = next(c for row in ws.iter_rows() for c in row if c.value == "=== TOP ===")
    assert cell.data_type == "s"
    for t in ("+1 cách", "-x", "@ai"):
        assert next(c for row in ws.iter_rows() for c in row if c.value == t).data_type == "s"


def test_chi_kenh_giu_hoac_theo_doi_vao_tab_12(tmp_path):
    xlsx, dinh_tinh, video = chuan_bi(tmp_path)
    ds = json.loads(dinh_tinh.read_text(encoding="utf-8"))
    ds["UCtheo"] = {"ten": "Kênh C", "giu_loai": "Theo dõi"}
    ds["UCtrong"] = {"ten": "Kênh D", "giu_loai": ""}
    ds["UCla"] = {"ten": "Kênh E", "giu_loai": "Chưa rõ"}
    dinh_tinh.write_text(json.dumps(ds, ensure_ascii=False), encoding="utf-8")
    for cid in ("UCtheo", "UCtrong", "UCla"):
        (video / f"{cid}.tsv").write_bytes((video / "UCmau.tsv").read_bytes())
    assert chay(str(xlsx), "--dinh-tinh", str(dinh_tinh), "--video-dir", str(video), "--model", "UCmau").returncode == 0
    ws = openpyxl.load_workbook(xlsx)["12. Video top 20 %"]
    ten = {str(row[0].value) for row in ws.iter_rows(min_row=3)}
    assert any("Kênh C" in t for t in ten)
    assert not any("Kênh D" in t or "Kênh E" in t or "Kênh B" in t for t in ten)
