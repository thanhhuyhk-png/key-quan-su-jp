"""Lô 3D Demo (v2): cảnh nguồn 'demo:<mã>[>][+khung lệch]' lấy nguyên hình 3D đã render và duyệt của bản Demo, đúng số khung.

Cảnh tập 1 dài hơn đoạn còn lại của nhóm Demo thì giữ khung cuối (cảnh mẫu chọn loại máy tiến chậm, lấy khung cuối tĩnh);
không đổi tốc độ video. In số khung giữ để soi.
Ra <output>/261101-dien-bien-phu-1954/hinh/3d/<mã>.mp4

python -I -X utf8 dung-demo.py [MÃ ...]
"""
import json, subprocess, sys
from pathlib import Path

GOC = Path(__file__).resolve().parent
sys.path.insert(0, str(GOC))
from demo import DEMO_CANH, cat_demo, nhom_cua  # noqa: E402
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

RA = OUT / "261101-dien-bien-phu-1954/hinh/3d"
FPS = 24
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))


def main() -> None:
    chon = [a for a in sys.argv[1:] if not a.startswith("--")]
    canh = [c for c in PC["canh"] if c["kieu"] == "demo" and (not chon or c["id"] in chon)]
    RA.mkdir(parents=True, exist_ok=True)
    for c in canh:
        n = round(c["t1"] * FPS) - round(c["t0"] * FPS)
        ma, _, lech = c["ten"].partition("+")
        noi = ma.endswith(">")  # 'MÃ>': được chạy sang các cảnh 3D liền sau trong nhóm; không có: chỉ trong cảnh đó
        ma, lech = ma.rstrip(">"), int(lech or 0)
        _, a, het = nhom_cua(ma)
        if not noi:
            k0, k1 = DEMO_CANH[ma]["khung"]
            het = a + k1 - k0
        co = min(n, het - a - lech)
        vao, f = cat_demo(ma, lech, co)
        ra = RA / f"{c['id']}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", *vao, "-vf", f"{f},tpad=stop_mode=clone:stop={n - co},format=yuv420p", "-an",
                        "-frames:v", str(n), "-r", str(FPS), "-c:v", "libx264", "-crf", "16", "-preset", "medium", str(ra)], check=True)
        so = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets",
                             "-of", "csv=p=0", str(ra)], capture_output=True, text=True).stdout.strip().rstrip(",")
        print(f"{c['id']}: {so} khung (cần {n}), giữ khung cuối {n - co}{'' if int(so) == n else '  LỆCH'}", flush=True)


if __name__ == "__main__":
    main()
