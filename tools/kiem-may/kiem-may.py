#!/usr/bin/env python3
"""Kiểm máy cho bước K1: máy này đã đủ phần mềm để chạy kit chưa, thiếu gì thì cài bằng lệnh nào.

Chỉ dùng thư viện chuẩn Python (chạy được ngay khi máy vừa có Python >= 3.10).

    python -X utf8 tools/kiem-may/kiem-may.py [--ra kiem-may.md] [--json]

Kiểm: Python, 9 thư viện (gồm fontTools) trong requirements.txt, Node >= 22 (dung-trang.mjs cần WebSocket toàn cục),
ffmpeg, ffprobe, Chrome/Edge, git, gh (đã đăng nhập), claude, ổ trống >= 60 GB ở ổ chứa khoá `output`,
RAM, Goha AVS (khoá `goha_avs` trỏ tới thư mục có thật; cổng 8787 trả lời thì ghi «đang chạy»; chỉ bắt buộc khi
gợi ý mức Đầy đủ, ở mức khác là tuỳ chọn, thay bằng `kit.py tron`, `master`), đường dẫn Chrome/Edge tìm được,
khoá API ELEVENLABS_API_KEY, DEEPGRAM_API_KEY (CHỈ báo có/thiếu; đọc tệp khoá ở gốc repo hoặc biến môi
trường; không bao giờ in hay ghi giá trị), và quét .claude/skills + tools tìm lệnh CLI `reelcrew` còn sót.

Mã thoát: 0 khi mọi thứ bắt buộc đủ; 1 khi thiếu ít nhất một thứ bắt buộc. Thứ tuỳ chọn (khoá API) không ảnh
hưởng mã thoát; RAM dưới 8 GB thì tính là thiếu bắt buộc. Lệnh reelcrew còn sót là lỗi của kit, không phải của máy:
chỉ CẢNH BÁO (liệt kê tệp:dòng, dặn báo chủ kit), không làm mã thoát 1, không chặn chọn mức chạy.

Gợi ý mức chạy (chỉ là điểm xuất phát, người dùng quyết):
  - Chưa đủ thứ bắt buộc  -> chưa chọn mức; cài xong chạy lại.
  - Có ELEVENLABS_API_KEY -> Đầy đủ (RAM dưới 16 GB thì kèm lưu ý bật chế độ nhẹ).
  - Không có ElevenLabs, có DEEPGRAM_API_KEY -> Tiết kiệm.
  - Không có khoá nào     -> Miễn phí.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Mapping

TEP_KHOA = "." + "env"
CONG_AVS = 8787
O_TRONG_TOI_THIEU_GB = 60.0
RAM_TOT_GB, RAM_TOI_THIEU_GB = 16.0, 8.0
NODE_TOI_THIEU = 22
PY_TOI_THIEU = (3, 10)
KHOA_API = ("ELEVENLABS_API_KEY", "DEEPGRAM_API_KEY")
# (tên module import, tên gói pip) theo requirements.txt
THU_VIEN = (("numpy", "numpy"), ("PIL", "pillow"), ("cv2", "opencv-python"), ("soundfile", "soundfile"),
            ("pytest", "pytest"), ("openpyxl", "openpyxl"), ("yt_dlp", "yt-dlp"), ("requests", "requests"),
            ("fontTools", "fonttools"))
CAI_PIP = "python -m pip install -r requirements.txt"
KHONG_QUET = {"__pycache__", "node_modules", ".git", ".venv", "kiem-may"}
DUOI_QUET = {".md", ".py", ".mjs", ".js", ".json", ".toml", ".sh", ".ps1", ".bat", ".cmd", ".txt", ".tsv"}
LENH_REELCREW = re.compile(r"""(?<![\w/\\.-])reelcrew(?:\.exe)?\s+[a-z][\w-]*|["']reelcrew(?:\.exe)?["']""")


@dataclass
class Muc:
    ten: str
    co: bool
    phien_ban: str = ""
    lenh_cai: str = ""
    ghi_chu: str = ""
    bat_buoc: bool = True


@dataclass
class KetQua:
    muc: list[Muc] = field(default_factory=list)
    reelcrew: list[str] = field(default_factory=list)
    canh_bao: list[str] = field(default_factory=list)
    muc_chay: str | None = None
    ly_do_muc: str = ""

    @property
    def thieu_bat_buoc(self) -> list[str]:
        return [m.ten for m in self.muc if m.bat_buoc and not m.co]

    @property
    def dat_toi_thieu(self) -> bool:
        return not self.thieu_bat_buoc


# ---- lớp tiếp xúc máy (tách ra để test giả lập) ----

def chay(lenh: list[str], timeout: int = 15) -> tuple[int, str] | None:
    """Chạy lệnh ngoài bằng danh sách đối số, không qua shell, có timeout. Không có lệnh hay quá giờ thì trả None."""
    day_du = shutil.which(lenh[0])
    if not day_du:
        return None
    try:
        r = subprocess.run([day_du, *lenh[1:]], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, shell=False)
    except (subprocess.TimeoutExpired, OSError):
        return None
    return r.returncode, (r.stdout or r.stderr or "").strip()


def tim_module(ten: str) -> str | None:
    """Phiên bản module nếu import được (chỉ tra, không nạp); không có thì None."""
    import importlib.metadata
    import importlib.util
    try:
        if importlib.util.find_spec(ten) is None:
            return None
    except (ImportError, ValueError):
        return None
    goi = {"PIL": "pillow", "cv2": "opencv-python", "yt_dlp": "yt-dlp", "fontTools": "fonttools"}.get(ten, ten)
    try:
        return importlib.metadata.version(goi)
    except importlib.metadata.PackageNotFoundError:
        return "có"


def ram_gb() -> float:
    if sys.platform == "win32":
        import ctypes

        class _Bo(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        bo = _Bo()
        bo.dwLength = ctypes.sizeof(_Bo)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(bo))
        return bo.ullTotalPhys / 1024 ** 3
    return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024 ** 3


def dung_luong_trong_gb(duong: Path) -> float:
    return shutil.disk_usage(duong).free / 1024 ** 3


def cong_mo(host: str, cong: int) -> bool:
    try:
        with socket.create_connection((host, cong), timeout=1):
            return True
    except OSError:
        return False


def ung_vien_trinh_duyet() -> list[Path]:
    goc = [os.environ.get(k) for k in ("ProgramFiles", "ProgramFiles(x86)", "LocalAppData")]
    ra = []
    for g in filter(None, goc):
        ra.append(Path(g) / "Google/Chrome/Application/chrome.exe")
    for g in filter(None, goc[:2]):
        ra.append(Path(g) / "Microsoft/Edge/Application/msedge.exe")
    return ra


# ---- đọc cấu hình và khoá ----

def doc_cau_hinh(repo: Path, canh_bao: list[str]) -> dict[str, str]:
    """Khoá trong [duong_dan] của cau-hinh.toml (chưa có tệp thì rỗng: K1 chạy trước khi tạo tệp)."""
    tep = repo / "cau-hinh.toml"
    if not tep.exists():
        return {}
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    try:
        from cau_hinh import doc_toml
        return doc_toml(tep.read_text(encoding="utf-8-sig")).get("duong_dan", {})
    except (ValueError, ImportError) as e:
        canh_bao.append(f"cau-hinh.toml không đọc được: {e}")
        return {}


def doc_khoa_co(tep: Path, moi_truong: Mapping[str, str], canh_bao: list[str] | None = None) -> set[str]:
    """Tên các khoá API có giá trị (biến môi trường hoặc tệp khoá). Chỉ trả TÊN, không bao giờ trả giá trị.

    Tệp khoá không đọc được (sai mã hoá, bị khoá) thì coi như không có tệp và thêm cảnh báo, không in nội dung."""
    co = {k for k in KHOA_API if moi_truong.get(k, "").strip()}
    if tep.exists():
        try:
            dong_khoa = tep.read_text(encoding="utf-8-sig").splitlines()
        except (OSError, UnicodeDecodeError):
            if canh_bao is not None:
                canh_bao.append(f"Tệp khoá {tep.name} không đọc được (cần UTF-8); bỏ qua tệp, chỉ dùng biến môi trường.")
            return co
        for dong in dong_khoa:
            dong = dong.strip()
            if not dong or dong.startswith("#") or "=" not in dong:
                continue
            ten, gia_tri = dong.split("=", 1)
            ten = ten.strip().removeprefix("export ").strip()
            if ten in KHOA_API and gia_tri.strip().strip("\"'").strip():
                co.add(ten)
    return co


def thu_muc_do_duoc(duong: Path) -> Path:
    """Thư mục tồn tại gần nhất (chính nó hoặc cha) để đo ổ đĩa."""
    p = duong
    while not p.exists() and p != p.parent:
        p = p.parent
    return p


# ---- từng nhóm kiểm ----

def _so(chu: str) -> tuple[int, ...]:
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", chu)
    return tuple(int(x) for x in m.groups() if x) if m else ()


def _dong_dau(chu: str) -> str:
    return chu.strip().splitlines()[0] if chu.strip() else ""


def kiem_lenh(ten: str, lenh: list[str], cai: str, **kw) -> Muc:
    r = chay(lenh)
    if not r or r[0] != 0:
        return Muc(ten, False, "", cai, **kw)
    v = _so(r[1])
    return Muc(ten, True, ".".join(map(str, v)) if v else _dong_dau(r[1]), "", **kw)


def kiem_python() -> Muc:
    v = sys.version_info
    ban = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) >= PY_TOI_THIEU:
        return Muc("Python 3.10 trở lên", True, ban)
    return Muc("Python 3.10 trở lên", False, ban, "winget install Python.Python.3.12")


def kiem_node() -> Muc:
    ten, cai = "Node.js 22 trở lên", "winget install OpenJS.NodeJS.LTS"
    r = chay(["node", "-v"])
    if not r or r[0] != 0:
        return Muc(ten, False, "", cai)
    v = _so(r[1])
    ban = ".".join(map(str, v))
    return Muc(ten, bool(v) and v[0] >= NODE_TOI_THIEU, ban, "" if v and v[0] >= NODE_TOI_THIEU else cai)


def kiem_gh() -> Muc:
    ten = "GitHub CLI (gh)"
    r = chay(["gh", "--version"])
    if not r or r[0] != 0:
        return Muc(ten, False, "", "winget install GitHub.cli")
    ban = ".".join(map(str, _so(r[1])))
    a = chay(["gh", "auth", "status"])
    if a and a[0] == 0:
        return Muc(ten, True, ban, ghi_chu="đã đăng nhập")
    return Muc(ten, False, ban, "gh auth login", "đã cài nhưng chưa đăng nhập")


def kiem_trinh_duyet(cfg: dict[str, str]) -> Muc:
    ten, cai = "Chrome hoặc Edge", "winget install Google.Chrome"
    ung = ([Path(cfg["chrome"])] if cfg.get("chrome") else []) + ung_vien_trinh_duyet()
    for p in ung:
        if p.exists():
            return Muc(ten, True, p.as_posix())
    return Muc(ten, False, "", cai)


def kiem_o_trong(cfg: dict[str, str], repo: Path) -> Muc:
    goc = Path(cfg["output"]) if cfg.get("output") else repo
    do = thu_muc_do_duoc(goc)
    ghi = "ổ chứa khoá output" if cfg.get("output") else "chưa đặt output, đo ổ chứa repo"
    gb = dung_luong_trong_gb(do)
    dat = gb >= O_TRONG_TOI_THIEU_GB
    return Muc("Ổ trống (mỗi tập đang dựng ≥ 60 GB)", dat, f"{gb:.0f} GB trống", "", ghi)


def kiem_ram() -> Muc:
    gb = ram_gb()
    ban = f"{gb:.0f} GB"
    if gb >= RAM_TOT_GB:
        return Muc("RAM", True, ban, ghi_chu="tốt")
    if gb >= RAM_TOI_THIEU_GB:
        return Muc("RAM", True, ban, ghi_chu="đủ chạy, bật chế độ nhẹ (720p, ít cảnh 3D)")
    return Muc("RAM", False, ban, "", "dưới 8 GB không đủ")


def kiem_avs(cfg: dict[str, str], bat_buoc: bool = True) -> Muc:
    """Goha AVS chỉ bắt buộc ở mức Đầy đủ; mức khác thiếu thì ghi cách thay."""
    m = _kiem_avs(cfg)
    m.bat_buoc = bat_buoc
    if not bat_buoc and not m.co:
        m.ghi_chu = (m.ghi_chu + "; " if m.ghi_chu else "") + "thay bằng `kit.py tron`, `master`"
    return m


def _kiem_avs(cfg: dict[str, str]) -> Muc:
    ten = "Goha AVS"
    cai = "Bộ cài Goha AVS của hội viên, rồi điền khoá goha_avs trong cau-hinh.toml"
    duong = cfg.get("goha_avs", "")
    if not duong:
        return Muc(ten, False, "", cai, "chưa có khoá goha_avs (tạo cau-hinh.toml từ cau-hinh.mau.toml)")
    if not Path(duong).exists():
        return Muc(ten, False, "", cai, "đường dẫn goha_avs trong cau-hinh.toml không tồn tại")
    return Muc(ten, True, "đang chạy (cổng 8787)" if cong_mo("127.0.0.1", CONG_AVS) else "chưa chạy (cổng 8787)")


def quet_reelcrew(repo: Path) -> list[str]:
    """Danh sách «tệp:dòng» còn gọi CLI reelcrew trong .claude/skills và tools."""
    ra = []
    for goc in (repo / ".claude" / "skills", repo / "tools"):
        for dg, thu_muc, tep in os.walk(goc):
            thu_muc[:] = [d for d in thu_muc if d not in KHONG_QUET]
            for t in tep:
                p = Path(dg) / t
                try:
                    if p.suffix.lower() not in DUOI_QUET or p.stat().st_size > 2_000_000:
                        continue
                    dong = p.read_text(encoding="utf-8", errors="replace").splitlines()
                except OSError:
                    continue
                ra += [f"{p.relative_to(repo).as_posix()}:{i}" for i, d in enumerate(dong, 1) if LENH_REELCREW.search(d)]
    return ra


def chon_muc(kq: KetQua, khoa_co: set[str], ram: float) -> None:
    if not kq.dat_toi_thieu:
        kq.muc_chay, kq.ly_do_muc = None, "Chưa đủ thứ bắt buộc, cài xong chạy lại rồi mới chọn mức."
        return
    if "ELEVENLABS_API_KEY" in khoa_co:
        kq.muc_chay, kq.ly_do_muc = "Đầy đủ", "Có khoá ElevenLabs (giọng, chép lời, tiếng động)."
    elif "DEEPGRAM_API_KEY" in khoa_co:
        kq.muc_chay, kq.ly_do_muc = "Tiết kiệm", "Không có khoá ElevenLabs nhưng có Deepgram."
    else:
        kq.muc_chay, kq.ly_do_muc = "Miễn phí", "Chưa có khoá API nào; dùng phương án thay thế miễn phí."
    if ram < RAM_TOT_GB:
        kq.ly_do_muc += " RAM dưới 16 GB nên bật chế độ nhẹ."


def kiem(repo: Path, moi_truong: Mapping[str, str] | None = None) -> KetQua:
    repo = Path(repo)
    env = os.environ if moi_truong is None else moi_truong
    kq = KetQua()
    cfg = doc_cau_hinh(repo, kq.canh_bao)
    m = kq.muc
    m.append(kiem_python())
    m += [Muc(f"Thư viện {mod}", bool(v := tim_module(mod)), v or "", "" if v else CAI_PIP) for mod, _ in THU_VIEN]
    m.append(kiem_node())
    m.append(kiem_lenh("ffmpeg", ["ffmpeg", "-version"], "winget install Gyan.FFmpeg"))
    m.append(kiem_lenh("ffprobe", ["ffprobe", "-version"], "winget install Gyan.FFmpeg"))
    m.append(kiem_trinh_duyet(cfg))
    m.append(kiem_lenh("Git", ["git", "--version"], "winget install Git.Git"))
    m.append(kiem_gh())
    m.append(kiem_lenh("Claude Code", ["claude", "--version"], "Cài theo trang Anthropic (claude.com/product/claude-code)"))
    m.append(kiem_o_trong(cfg, repo))
    ram = ram_gb()
    m.append(kiem_ram())
    khoa_co = doc_khoa_co(repo / TEP_KHOA, env, kq.canh_bao)
    m.append(kiem_avs(cfg, bat_buoc="ELEVENLABS_API_KEY" in khoa_co))
    for k in KHOA_API:
        m.append(Muc(f"Khoá {k}", k in khoa_co, "", "" if k in khoa_co else
                     f"Tự chép khoa-api.mau thành {TEP_KHOA} và dán khoá", bat_buoc=False))
    kq.reelcrew = quet_reelcrew(repo)
    sach = not kq.reelcrew
    m.append(Muc("Kit không gọi reelcrew", sach, "sạch" if sach else f"{len(kq.reelcrew)} chỗ còn sót",
                 "" if sach else "Lỗi của kit, không chặn cài máy; báo chủ kit", bat_buoc=False))
    if not sach:
        kq.canh_bao.append(f"Kit còn {len(kq.reelcrew)} chỗ gọi lệnh reelcrew (máy hội viên không có); "
                           "đây là lỗi của kit, không chặn bạn cài máy. Hãy báo chủ kit kèm danh sách tệp:dòng ở trên.")
    chon_muc(kq, khoa_co, ram)
    return kq


# ---- xuất ----

def _o(chu: str) -> str:
    return (chu or "—").replace("|", "\\|")


def bang_md(kq: KetQua) -> str:
    dong = ["| Thành phần | Có/thiếu | Phiên bản | Lệnh cài |", "|---|---|---|---|"]
    for x in kq.muc:
        ten = x.ten + ("" if x.bat_buoc else " (tuỳ chọn)")
        ban = x.phien_ban + (f" ({x.ghi_chu})" if x.ghi_chu and x.co else "")
        lenh = x.lenh_cai + (f" ({x.ghi_chu})" if x.ghi_chu and not x.co else "")
        dong.append(f"| {_o(ten)} | {'có' if x.co else 'thiếu'} | {_o(ban)} | {_o(lenh)} |")
    return "\n".join(dong)


def bao_cao_md(kq: KetQua) -> str:
    ra = ["# Kiểm máy", "", bang_md(kq), ""]
    ra.append(f"Mức chạy gợi ý: **{kq.muc_chay or 'chưa chọn'}**. {kq.ly_do_muc}")
    ra.append("")
    if kq.thieu_bat_buoc:
        ra += ["Thiếu bắt buộc: " + ", ".join(kq.thieu_bat_buoc) + ".", ""]
    if kq.reelcrew:
        ra += ["Chỗ còn gọi reelcrew:"] + [f"- {d}" for d in kq.reelcrew] + [""]
    ra += [f"- {c}" for c in kq.canh_bao]
    return "\n".join(ra).rstrip() + "\n"


def ra_json(kq: KetQua) -> str:
    d = {"muc": [asdict(x) for x in kq.muc], "muc_chay": kq.muc_chay, "ly_do_muc": kq.ly_do_muc,
         "thieu_bat_buoc": kq.thieu_bat_buoc, "reelcrew": kq.reelcrew, "canh_bao": kq.canh_bao,
         "dat_toi_thieu": kq.dat_toi_thieu}
    return json.dumps(d, ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    for luong in (sys.stdout, sys.stderr):
        if hasattr(luong, "reconfigure"):
            luong.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kiểm máy cho bước K1 (có/thiếu, lệnh cài, mức chạy).")
    ap.add_argument("--ra", type=Path, help="ghi báo cáo Markdown (vd kiem-may.md)")
    ap.add_argument("--json", action="store_true", help="in JSON thay cho bảng")
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2], help="gốc repo (mặc định: tự tìm)")
    a = ap.parse_args(argv)
    kq = kiem(a.repo)
    if a.ra:
        a.ra.parent.mkdir(parents=True, exist_ok=True)
        with open(a.ra, "w", encoding="utf-8", newline="\n") as f:
            f.write(bao_cao_md(kq))
    print(ra_json(kq) if a.json else bao_cao_md(kq), end="" if not a.json else "\n")
    return 0 if kq.dat_toi_thieu else 1


if __name__ == "__main__":
    sys.exit(main())
