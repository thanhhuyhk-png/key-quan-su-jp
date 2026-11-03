"""Test phần thuần Python của máy dựng thương hiệu: cấu hình, kiểm màu, bố cục, đường dẫn ra."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_TEP = Path(__file__).with_name("thuong_hieu.py")
_spec = importlib.util.spec_from_file_location("thuong_hieu", _TEP)
th = importlib.util.module_from_spec(_spec)
sys.modules["thuong_hieu"] = th
_spec.loader.exec_module(th)

REPO = th.tim_repo()
VI_DU = Path(__file__).with_name("vi-du.json")


def cfg_mau(**sua):
    d = json.loads(VI_DU.read_text(encoding="utf-8"))
    d.update(sua)
    return d


def test_doc_vi_du_day_du():
    c = th.doc_cau_hinh(VI_DU)
    assert c["ten"] == "Sử Thép" and c["viet_tat"] == "ST"
    assert c["bo_cuc"] == ["vach", "tron", "gach"]
    assert c["font"]["tieu_de"] == "Oswald-VF.ttf"


@pytest.mark.parametrize("khoa", ["ten", "mau"])
def test_thieu_khoa_bat_buoc(khoa):
    d = cfg_mau()
    del d[khoa]
    with pytest.raises(th.CauHinhLoi, match=khoa):
        th.kiem_cau_hinh(d)


def test_thieu_mot_vai_mau_va_sai_dang():
    with pytest.raises(th.CauHinhLoi, match="mau.nhan"):
        th.kiem_cau_hinh(cfg_mau(mau={"nen": "#000000", "chu": "#ffffff"}))
    with pytest.raises(th.CauHinhLoi, match="#rrggbb"):
        th.kiem_cau_hinh(cfg_mau(mau={"nen": "xanh", "chu": "#ffffff", "nhan": "#ff0000"}))


def test_bo_cuc_sai_va_handle_sai():
    with pytest.raises(th.CauHinhLoi, match="bố cục"):
        th.kiem_cau_hinh(cfg_mau(bo_cuc=["hinh-la"]))
    with pytest.raises(th.CauHinhLoi, match="1 đến 3"):
        th.kiem_cau_hinh(cfg_mau(bo_cuc=["vach", "tron", "gach", "vach"]))
    with pytest.raises(th.CauHinhLoi, match="@"):
        th.kiem_cau_hinh(cfg_mau(handle="suthep"))


def test_mac_dinh_khi_bo_trong():
    c = th.kiem_cau_hinh({"ten": "Kênh A", "mau": cfg_mau()["mau"]})
    assert c["bo_cuc"] == ["vach"] and c["chu_phu"] == "" and c["font"]["noi_dung"].startswith("BeVietnam")


def test_viet_tat():
    assert th.viet_tat("Sử Thép") == "ST"
    assert th.viet_tat("Đại Việt Sử Ký") == "ĐV"
    assert th.viet_tat("Một") == "M"


def test_tuong_phan():
    assert th.tuong_phan("#000000", "#ffffff") == pytest.approx(21, rel=1e-3)
    c = th.kiem_cau_hinh(cfg_mau(mau={"nen": "#14263a", "chu": "#1a2c40", "nhan": "#e4504a"}))
    assert th.thieu_do_tuong_phan(c)


def test_vi_du_dat_tuong_phan_va_khac_kenh_mau():
    c = th.doc_cau_hinh(VI_DU)
    assert th.thieu_do_tuong_phan(c) == []
    assert th.mau_trung_kenh_mau(c, REPO) == []


def test_bat_mau_trung_kenh_mau():
    c = th.kiem_cau_hinh(cfg_mau(mau={"nen": "#3a4126", "chu": "#ebe4c8", "nhan": "#e2b04a"}))
    trung = th.mau_trung_kenh_mau(c, REPO)
    assert any("mau.nen" in t for t in trung) and any("mau.nhan" in t for t in trung)


def test_ke_hoach_dau_ra(tmp_path):
    kh = th.ke_hoach_dau_ra(tmp_path, "tron")
    assert kh["youtube/anh-dai-dien"] == tmp_path / "tron/youtube/anh-dai-dien-800.png"
    assert kh["youtube/banner"].name == "banner-2560x1440.jpg"
    assert kh["svg/logo-ngang-mot-mau-chu"].parent.name == "svg"
    assert len(kh) == 2 * 4 * 2 + 3 + 3


def test_ban_mau_sang_dung_mau_toi():
    c = th.doc_cau_hinh(VI_DU)
    assert th.mau_ban(c, "sang")["chu"] == c["mau"]["nen"]
    assert th.mau_ban(c, "toi")["chu"] == c["mau"]["chu"]
    assert th.mau_ban(c, "mot-mau-chu")["nhan"] == c["mau"]["chu"]


@pytest.fixture(scope="module")
def fonts():
    c = th.doc_cau_hinh(VI_DU)
    return c, th.nap_font(c, REPO / "template/fonts")


def test_font_co_dau_tieng_viet(fonts):
    _, (tt, _) = fonts
    assert tt.rong("SỬ THÉP", 100) > tt.rong("SU THEP", 100) * 0.9
    assert tt.path("ƯỜẶỮ", 100, 0, 100).startswith("M")


def test_font_thieu_ky_tu_bao_ro(fonts):
    _, (tt, _) = fonts
    with pytest.raises(th.CauHinhLoi, match="không có ký tự"):
        tt.rong("\u4e2d", 100)


def test_font_thieu_tep(tmp_path):
    with pytest.raises(th.CauHinhLoi, match="Không thấy font"):
        th.Font(tmp_path / "khong-co.ttf")


@pytest.mark.parametrize("bc", th.BO_CUC)
def test_banner_trong_vung_an_toan(fonts, bc):
    c, (tt, nd) = fonts
    svg, (rw, rh) = th.hinh_banner(c, tt, nd, bc)
    assert rw <= th.AN_TOAN[0] and rh <= th.AN_TOAN[1]
    assert 'viewBox="0 0 2560 1440"' in svg


def test_banner_ten_rat_dai_van_vua(fonts):
    c, (tt, nd) = fonts
    c = {**c, "ten": "Chiến Dịch Mùa Xuân Lịch Sử Dài Dằng Dặc", "khau_hieu": "x " * 40}
    _, (rw, rh) = th.hinh_banner(c, tt, nd, "vach")
    assert rw <= th.AN_TOAN[0] and rh <= th.AN_TOAN[1]


@pytest.mark.parametrize("bc", th.BO_CUC)
@pytest.mark.parametrize("kieu", ["dung", "ngang"])
def test_logo_svg_hop_le_va_khong_co_the_chu(fonts, bc, kieu):
    c, (tt, nd) = fonts
    svg, w, h = th.logo(c, tt, nd, bc, kieu, "toi")
    assert svg.startswith("<svg") and "<text" not in svg  # chữ đã đổi thành path
    assert w > 0 and h > 0
    if kieu == "dung":
        assert h > w * 0.5


def test_khong_co_dau_vet_kenh_mau(fonts):
    c, (tt, nd) = fonts
    svg = th.logo(c, tt, nd, "vach", "ngang", "toi")[0] + th.hinh_banner(c, tt, nd, "vach")[0]
    for cam in ("go" + "ha", "stu" + "dio", "#e2b04a", "#3a4126"):
        assert cam not in svg.lower()
    ma = _TEP.read_text(encoding="utf-8").lower()
    assert "go" + "ha" not in ma.replace("go" + "ha-ho-so-kenh", "")


def test_main_loi_cau_hinh_ma_thoat_2(tmp_path, capsys):
    tep = tmp_path / "x.json"
    tep.write_text('{"ten": "A"}', encoding="utf-8")
    assert th.main(["--cau-hinh", str(tep), "--ra", str(tmp_path / "ra")]) == 2
    assert "mau" in capsys.readouterr().out


def test_main_mau_trung_dung_truoc_khi_dung(tmp_path, capsys):
    tep = tmp_path / "x.json"
    tep.write_text(json.dumps(cfg_mau(mau={"nen": "#3a4126", "chu": "#ebe4c8", "nhan": "#e2b04a"})), encoding="utf-8")
    assert th.main(["--cau-hinh", str(tep), "--ra", str(tmp_path / "ra"), "--chrome", "khong-co"]) == 3
    assert "DỪNG" in capsys.readouterr().out
    assert not (tmp_path / "ra").exists()


# ---------- đường xuất ảnh với Chrome giả ----------

import subprocess


class ChromeGia:
    """Thay subprocess.run: ghi PNG giả đúng kích thước cửa sổ, ghi lại lệnh gọi."""

    def __init__(self, che_do="ghi"):
        self.che_do = che_do
        self.lenh = []
        self.kwargs = []

    def __call__(self, cmd, **kw):
        from PIL import Image, ImageDraw
        self.lenh.append(list(cmd))
        self.kwargs.append(kw)
        if self.che_do == "het_gio":
            raise subprocess.TimeoutExpired(cmd, kw.get("timeout"))
        if self.che_do == "loi":
            return subprocess.CompletedProcess(cmd, 1, "", "dong 1\ndong 2\nGPU process crashed\n")
        if self.che_do == "khong_ghi":
            return subprocess.CompletedProcess(cmd, 0, "", "")
        ra = next(a for a in cmd if a.startswith("--screenshot=")).split("=", 1)[1]
        w, h = map(int, next(a for a in cmd if a.startswith("--window-size=")).split("=", 1)[1].split(","))
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(im).rectangle([w // 4, h // 4, w * 3 // 4, h * 3 // 4], fill=(200, 80, 60, 255))
        im.save(ra)
        return subprocess.CompletedProcess(cmd, 0, "", "")


@pytest.fixture
def chrome_gia(monkeypatch):
    g = ChromeGia()
    monkeypatch.setattr(th.subprocess, "run", g)
    return g


def test_chrome_chup_dung_ho_so_rieng_timeout_va_don_ho_so(chrome_gia, tmp_path):
    th.chrome_chup("chrome-gia", "<svg/>", 100, 60, tmp_path / "a" / "x.png")
    cmd, kw = chrome_gia.lenh[0], chrome_gia.kwargs[0]
    udd = next(a for a in cmd if a.startswith("--user-data-dir=")).split("=", 1)[1]
    assert "--no-first-run" in cmd
    assert kw["timeout"] and kw["timeout"] <= 120
    assert not Path(udd).exists()
    from PIL import Image
    assert Image.open(tmp_path / "a" / "x.png").size == (100, 60)


def test_chrome_khong_ghi_tep_bao_loi_ro(monkeypatch, tmp_path):
    monkeypatch.setattr(th.subprocess, "run", ChromeGia("khong_ghi"))
    with pytest.raises(th.CauHinhLoi, match="không tạo ra ảnh"):
        th.chrome_chup("chrome-gia", "<svg/>", 100, 60, tmp_path / "x.png")


def test_chrome_het_gio_bao_loi_ro(monkeypatch, tmp_path):
    monkeypatch.setattr(th.subprocess, "run", ChromeGia("het_gio"))
    with pytest.raises(th.CauHinhLoi, match="quá .* giây"):
        th.chrome_chup("chrome-gia", "<svg/>", 100, 60, tmp_path / "x.png")


def test_chrome_loi_kem_duoi_stderr(monkeypatch, tmp_path):
    monkeypatch.setattr(th.subprocess, "run", ChromeGia("loi"))
    with pytest.raises(th.CauHinhLoi, match="GPU process crashed"):
        th.chrome_chup("chrome-gia", "<svg/>", 100, 60, tmp_path / "x.png")


def test_chrome_khong_co_bao_loi_ro(tmp_path):
    with pytest.raises(th.CauHinhLoi, match="chrome-khong-co"):
        th.chrome_chup("chrome-khong-co", "<svg/>", 100, 60, tmp_path / "x.png")


def test_main_chrome_loi_ma_thoat_khac_0_khong_traceback(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(th.subprocess, "run", ChromeGia("loi"))
    ma = th.main(["--cau-hinh", str(VI_DU), "--ra", str(tmp_path / "ra"), "--chrome", "chrome-gia",
                  "--nhan-dien", str(tmp_path / "nd.js")])
    assert ma == 2
    assert "GPU process crashed" in capsys.readouterr().out


def test_dung_mot_huong_ra_du_tep(chrome_gia, fonts, tmp_path):
    c, (tt, nd) = fonts
    kh = th.dung_mot_huong(c, tt, nd, "vach", tmp_path, "chrome-gia")
    assert len(kh) == len(th.ke_hoach_dau_ra(tmp_path, "vach"))
    for khoa, p in kh.items():
        assert p.exists() and p.stat().st_size > 0, khoa
    assert not list(tmp_path.rglob("*.tam.png"))
    from PIL import Image
    assert Image.open(kh["youtube/banner"]).size == th.BANNER


def test_dung_mot_huong_loi_giua_chung_don_tam_png(monkeypatch, fonts, tmp_path):
    c, (tt, nd) = fonts
    goi = {"n": 0}
    that = ChromeGia()

    def hong_o_banner(cmd, **kw):
        if "--window-size=2560,1440" in cmd:
            return subprocess.CompletedProcess(cmd, 1, "", "chết")
        goi["n"] += 1
        return that(cmd, **kw)

    monkeypatch.setattr(th.subprocess, "run", hong_o_banner)
    with pytest.raises(th.CauHinhLoi):
        th.dung_mot_huong(c, tt, nd, "vach", tmp_path, "chrome-gia")
    assert not list(tmp_path.rglob("*.tam.png"))


def test_chay_vi_du_ba_huong_ra_anh_soi(chrome_gia, tmp_path, capsys):
    nd = tmp_path / "kenh" / "nhan-dien-kenh.js"
    ma = th.main(["--cau-hinh", str(VI_DU), "--ra", str(tmp_path), "--chrome", "chrome-gia", "--nhan-dien", str(nd)])
    assert ma == 0, capsys.readouterr().out
    assert (tmp_path / "soi.jpg").stat().st_size > 0
    js = nd.read_text(encoding="utf-8")
    assert js.startswith("// Sinh bởi") and '"logo": "../vach/png/logo-ngang-toi.png"' in js
    assert (tmp_path / "soi-tron.jpg").exists() and (tmp_path / "soi-gach.jpg").exists()
    for bc in ("vach", "tron", "gach"):
        assert (tmp_path / bc / "youtube" / "banner-2560x1440.jpg").exists()


def test_ghep_soi_dung_font_cau_hinh_va_co_du_phong(chrome_gia, fonts, tmp_path):
    c, (tt, nd) = fonts
    kh = th.dung_mot_huong(c, tt, nd, "vach", tmp_path, "chrome-gia")
    th.ghep_soi(c, kh, tmp_path / "khong-co-thu-muc-font", tmp_path / "soi.jpg")
    assert (tmp_path / "soi.jpg").exists()


def test_ten_kenh_nfd_duoc_chuan_hoa_nfc():
    import unicodedata
    d = cfg_mau(ten=unicodedata.normalize("NFD", "Sử Thép"))
    assert th.kiem_cau_hinh(d)["ten"] == unicodedata.normalize("NFC", "Sử Thép")


def test_chrome_that_ra_du_anh(tmp_path):
    """Chạy thật với Chrome của cau-hinh.toml; bỏ qua nếu máy không có."""
    sys.path.insert(0, str(REPO / "tools"))
    try:
        from cau_hinh import duong
        chrome = str(duong("chrome"))
    except (Exception, SystemExit) as e:  # cau_hinh dừng bằng SystemExit khi thiếu cau-hinh.toml
        pytest.skip(f"không có Chrome trong cấu hình: {e}")
    if not Path(chrome).exists():
        pytest.skip("Chrome không tồn tại")
    ma = th.main(["--cau-hinh", str(VI_DU), "--ra", str(tmp_path), "--chrome", chrome,
                  "--nhan-dien", str(tmp_path / "nhan-dien-kenh.js")])
    assert ma == 0
    for bc in ("vach", "tron", "gach"):
        for khoa, p in th.ke_hoach_dau_ra(tmp_path, bc).items():
            assert p.exists() and p.stat().st_size > 0, (bc, khoa)
    assert (tmp_path / "soi.jpg").exists()


# ---------- nhận diện thẻ chữ ----------

def test_mau_the_du_vai_va_dat_tuong_phan():
    c = th.kiem_cau_hinh(json.loads(VI_DU.read_text(encoding="utf-8")))
    m = th.mau_the(c)
    vai_mac_dinh = {"nen", "nenToi", "camo", "kem", "kemPhu", "vang", "do", "doHop", "doChu", "than", "gach", "ve",
                    "nenSau", "khung"}
    assert set(m) == vai_mac_dinh
    assert m["nen"] == c["mau"]["nen"].upper() and m["kem"] == c["mau"]["chu"].upper()
    assert th.tuong_phan(m["kem"], m["doHop"]) >= 4.5
    assert th.tuong_phan(m["doChu"], m["nen"]) >= 4.5
    assert th.tuong_phan(m["than"], m["vang"]) >= 4.5


def test_mau_the_nhan_toi_van_ra_chu_nho_doc_duoc():
    c = {"mau": {"nen": "#101820", "chu": "#F5F5F0", "nhan": "#8A3B2E"}}
    m = th.mau_the(c)
    assert th.tuong_phan(m["doChu"], "#101820") >= 4.5


def test_tron_mau_dau_cuoi():
    assert th.tron_mau("#000000", "#FFFFFF", 0) == "#000000"
    assert th.tron_mau("#000000", "#FFFFFF", 1) == "#FFFFFF"
    assert th.tron_mau("#000000", "#FFFFFF", 0.5) == "#808080"


def test_viet_nhan_dien_kenh_logo_tuong_doi(tmp_path):
    c = th.kiem_cau_hinh(json.loads(VI_DU.read_text(encoding="utf-8")))
    logo = tmp_path / "kenh" / "thuong-hieu" / "ra" / "vach" / "png" / "logo-ngang-toi.png"
    dich = tmp_path / "kenh" / "thuong-hieu" / "nhan-dien-kenh.js"
    th.viet_nhan_dien_kenh(c, logo, dich)
    js = dich.read_text(encoding="utf-8")
    assert '"logo": "ra/vach/png/logo-ngang-toi.png"' in js
    assert json.loads(js.split("export default ", 1)[1].rstrip().rstrip(";"))["mau"]["vang"] == c["mau"]["nhan"].upper()


def test_chrome_chup_duong_dan_tuong_doi_thanh_tuyet_doi(monkeypatch, tmp_path):
    """Chrome ghi --screenshot theo thư mục làm việc của nó: phải truyền đường dẫn tuyệt đối (lệnh K2 dùng --ra tương đối)."""
    gia = ChromeGia()
    monkeypatch.setattr(th.subprocess, "run", gia)
    monkeypatch.chdir(tmp_path)
    th.chrome_chup("chrome-gia", "<svg/>", 100, 60, Path("ra/png/x.png"))
    anh = next(a for a in gia.lenh[0] if a.startswith("--screenshot="))
    assert Path(anh.split("=", 1)[1]).is_absolute()
    assert (tmp_path / "ra/png/x.png").exists()
