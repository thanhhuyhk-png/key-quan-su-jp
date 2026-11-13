# -*- coding: utf-8 -*-
"""
dung-3d.py — EP002: dựng cảnh bản đồ bằng ban-do-3d/ban-do-3d.html (three.js + tàu Meshy) qua dung-trang.mjs.

  python -I -X utf8 dung-3d.py --map          # in bảng cảnh → cú máy / biến thể / cửa sổ k
  python -I -X utf8 dung-3d.py --stills S004 …
  python -I -X utf8 dung-3d.py --render S004 …  /  --render-het
dung-p5.py gọi render_ban_do(c, out) cho cảnh kiểu ban-do.
Mỗi cảnh = một lát [k0,k1] của một cú máy, tốc độ tự nhiên (8 s cú máy), góc máy đổi theo biến thể.
"""
import json, re, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
REPO = next(p for p in GOC.parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO / "tools"))
from cau_hinh import duong  # noqa: E402

OUT = duong("output") / "261113-kokai-kaisen-1904"
B3 = GOC / "ban-do-3d"
FPS = 24
DT = ["node", str(REPO / "tools/kit/dung-trang.mjs")]
DUR_CU = 8.0

# loại bản đồ → cú máy (EP002 黄海海戦): mỗi loại một cú máy; ryojun sau 1100 s đổi sang ryojun12 (12月)
XOAY = {"koukai": ["koukai"], "ryojun": ["ryojun"], "kosen1": ["kosen1"], "tsuigeki": ["tsuigeki"], "kosen2": ["kosen2"],
        "senkai": ["senkai"], "sanran": ["sanran"], "churitsu": ["churitsu"], "ulsan": ["ulsan"]}


def lap_bang(PC):
    """gán (cú máy, biến thể, cửa sổ k) cho từng cảnh ban-do. Cảnh cùng cú máy đi tuần tự theo thời gian phim:
    cửa sổ bắt đầu tăng dần từ 0 tới 1−w (w = dài cảnh / 8 s, tốc độ tự nhiên) nên đồng hồ và hạm đội tiến theo mạch kể."""
    ds = [c for c in PC if c["kieu"] == "ban-do"]
    def shot_cua(c):
        ten = c["ten"].split("+")[0]
        if ten == "ryojun" and c["t0"] > 1100:
            return "ryojun12"
        return XOAY.get(ten, ["koukai"])[0]
    dem = {}
    for c in ds:
        dem[shot_cua(c)] = dem.get(shot_cua(c), 0) + 1
    chi, bang = {}, {}
    for c in ds:
        shot = shot_cua(c)
        i = chi.get(shot, 0)
        chi[shot] = i + 1
        n = round(c["t1"] * FPS) - round(c["t0"] * FPS)
        d = n / FPS
        w = min(1.0, d / DUR_CU)
        k0 = (i / max(1, dem[shot] - 1)) * (1 - w) if dem[shot] > 1 else 0.0
        bang[c["id"]] = {"shot": shot, "var": i % 4, "k0": round(k0, 3), "k1": round(k0 + w, 3), "scene": d, "n": n}
    return bang


def trang(cid, sh):
    p = B3 / f"_c_{cid}.html"
    s = (B3 / "ban-do-3d.html").read_text(encoding="utf-8")
    s = s.replace("window.SHOT=window.SHOT||{shot:'koukai',duration:8};",
                  "window.SHOT=" + json.dumps({"shot": sh["shot"], "duration": DUR_CU, "var": sh["var"], "k0": sh["k0"], "k1": sh["k1"], "scene": sh["scene"]}) + ";", 1)
    p.write_text(s, encoding="utf-8")
    return p


TAM_IDS = {"S027", "S044", "S124", "S196", "S262", "S270"}  # nối liền bằng tấm tư liệu (thu-tam-tu-lieu.py, user duyệt 13/11)


def render_ban_do(c, out, bang=None, stills=None):
    if bang is None:
        PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))["canh"]
        bang = lap_bang(PC)
    if c["id"] in TAM_IDS and not stills:
        import importlib.util
        sp = importlib.util.spec_from_file_location("thu_tam", GOC / "thu-tam-tu-lieu.py")
        tt = importlib.util.module_from_spec(sp); sp.loader.exec_module(tt)
        return tt.chay(c["id"], bang, out=out)
    sh = bang[c["id"]]
    p = trang(c["id"], sh)
    try:
        if stills:
            a = [f"0.2,{sh['scene'] * 0.5:.2f},{sh['scene'] - 0.05:.2f}", "--out-dir", str(stills)]
            r = subprocess.run(DT + [str(p), "--stills"] + a, capture_output=True, text=True, encoding="utf-8")
        else:
            r = subprocess.run(DT + [str(p), "--out", str(out), "--fps", str(FPS), "--force"], capture_output=True, text=True, encoding="utf-8")
        if r.returncode:
            raise RuntimeError(r.stderr[-700:])
    finally:
        p.unlink(missing_ok=True)
    return sh["n"]


def main():
    a = sys.argv[1:]
    PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))["canh"]
    bang = lap_bang(PC)
    ids = [x for x in a if re.fullmatch(r"S\d{3}", x)]
    bd = [c for c in PC if c["kieu"] == "ban-do"]
    chon = bd if "--render-het" in a else [c for c in bd if c["id"] in ids]
    if "--map" in a:
        for c in bd:
            b = bang[c["id"]]
            print(c["id"], c["ten"], round(b["scene"], 1), b["shot"], "var", b["var"], b["k0"], b["k1"])
        return
    if "--stills" in a:
        d = OUT / "hinh" / "bd3d-scenes"
        for c in chon:
            dd = d / c["id"]; dd.mkdir(parents=True, exist_ok=True)
            render_ban_do(c, None, bang, dd)
            print("stills", c["id"], bang[c["id"]]["shot"])
        return
    for c in chon:
        out = OUT / "hinh" / "p5" / f"{c['id']}.mp4"
        try:
            n = render_ban_do(c, out, bang)
            print(f"  {c['id']} {bang[c['id']]['shot']:<20} {n} khung", flush=True)
        except Exception as e:
            print("LỖI", c["id"], e, flush=True)


if __name__ == "__main__":
    main()
