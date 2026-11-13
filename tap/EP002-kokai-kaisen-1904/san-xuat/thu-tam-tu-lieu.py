# -*- coding: utf-8 -*-
"""
thu-tam-tu-lieu.py — BẢN THỬ (13/11/2026): 6 cảnh bản đồ EP002 nối liền với cảnh ảnh kề bên bằng «tấm tư liệu»
(ban-do-3d/tam-tu-lieu.js). Không sửa ban-do-3d.html, không ghi đè hinh/p5/: ra hinh/p5-thu-tam/.

  python -I -X utf8 thu-tam-tu-lieu.py --stills [S027 …]   # ảnh tĩnh để soi
  python -I -X utf8 thu-tam-tu-lieu.py --render [S027 …]   # render cảnh mới
  python -I -X utf8 thu-tam-tu-lieu.py --so-sanh             # ghép cũ | mới cho từng cặp ảnh–bản đồ
"""
import csv, importlib.util, json, shutil, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("d3", GOC / "dung-3d.py"); d3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(d3)
B3, OUT, FPS = d3.B3, d3.OUT, d3.FPS
RA = OUT / "hinh" / "p5-thu-tam"
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))["canh"]
CS = {c["id"]: c for c in PC}
ANH = {r["tep"]: r for r in csv.DictReader(open(GOC / "anh.tsv", encoding="utf-8"), delimiter="\t")}

# cảnh bản đồ → (kiểu, cảnh ảnh kề, điểm neo JS trong phạm vi ban-do-3d.html)
NHAT = "window.__SHIPS.filter(s=>s.mau==='nhat')[{}].g.position.clone().setY(0.02)"
THU = {
    "S027": ("lui", "S026", "E(121.2,38.75,0.03)", {}),        # 旅順口 1904-08-10
    "S044": ("vao", "S045", "E(121.235,38.79,0.03)", {}),      # 虎尾半島前 封鎖船の残骸 (概略)
    "S124": ("lui", "S123", NHAT.format(2), {}),               # 黄海海戦 8/10: giữa hàng 第1戦隊
    "S196": ("lui", "S195", NHAT.format(3), {}),               # 敷島 = tàu thứ 4 của 第1戦隊 (sổ A6a)
    "S262": ("vao", "S263", "E(120.32,36.06,0.1)", {}),        # 青島
    "S270": ("lui", "S269", "E(129.6,35.45,0.1)", {}),         # 蔚山沖 8/14
}


def nguon_ngan(r):
    return "写真: " + r["ghi_nguon"].split(" · ")[0]


def chu_tam(ca):
    import re
    m = re.search(r"[\"“「]([^\"”」]+)[\"”」]", ca.get("chu") or "")
    return m.group(1) if m else ANH[ca["ten"]]["mo_ta"].split("(")[0].split(" 第")[0]


def trang(cid, sh):
    mode, ida, neo, them = THU[cid]
    ca = CS[ida]; r = ANH[ca["ten"]]
    tmp = B3 / "_tam"; tmp.mkdir(exist_ok=True)
    anh = tmp / (ca["ten"] + Path(r["file"]).suffix); shutil.copyfile(r["file"], anh)
    s = (B3 / "ban-do-3d.html").read_text(encoding="utf-8")
    s = s.replace("window.SHOT=window.SHOT||{shot:'koukai',duration:8};",
                  "window.SHOT=" + json.dumps({"shot": sh["shot"], "duration": d3.DUR_CU, "var": sh["var"], "k0": sh["k0"], "k1": sh["k1"], "scene": sh["scene"]}) + ";"
                  + "window.TAM=" + json.dumps({"mode": mode, "anh": "_tam/" + anh.name, "chu": chu_tam(ca), "nguon": nguon_ngan(r), **them}, ensure_ascii=False) + ";", 1)
    a = "const g=new THREE.Group();g.add(m);g.visible=false;sc.add(g);return g;}"
    assert a in s; s = s.replace(a, a[:-len("return g;}")] + "(window.__SHIPS=window.__SHIPS||[]).push({g,mau});return g;}", 1)
    b = "const gioE=document.getElementById('gio')"
    assert b in s
    s = s.replace(b, "let TAMO=null;if(window.TAM){TAMO=await (await import('./tam-tu-lieu.js')).lapTam({THREE,sc,cam,W,H,cfg,camf,upd,SD,K0,K1,"
                     f"tam:Object.assign(window.TAM,{{neo:()=>{neo},tranh:[E(113.9,18.6,0.3),E(114.6,7.4,0.3),E(115.5,13.6,0.3)]}})}});camf=TAMO.camf;}}\n" + b, 1)
    c = "window.renderFrame(0);window.READY=true;"
    assert c in s
    s = s.replace(c, "if(TAMO){const rf=window.renderFrame;window.renderFrame=(t)=>{rf(t);el.hud.style.opacity=Math.min(smooth(t/0.6),TAMO.hud());return null;};}\n" + c, 1)
    # nguồn góc phải: thêm nguồn ảnh
    s = s.replace("作図(概略) ・ 地形: Natural Earth", "作図(概略) ・ 地形: Natural Earth ・ " + nguon_ngan(r), 1)
    p = B3 / f"_tam_{cid}.html"; p.write_text(s, encoding="utf-8")
    return p


def chay(cid, bang, stills=None, out=None):
    sh = bang[cid]; p = trang(cid, sh)
    out = Path(out) if out else RA / f"{cid}.mp4"
    try:
        if stills:
            d = sh["scene"]
            a = [",".join(f"{x:.2f}" for x in (0.0, d * 0.18, d * 0.35, d * 0.55, d * 0.8, d - 0.05)), "--out-dir", str(stills)]
            r = subprocess.run(d3.DT + [str(p), "--stills"] + a, capture_output=True, text=True, encoding="utf-8")
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            r = subprocess.run(d3.DT + [str(p), "--out", str(out), "--fps", str(FPS), "--force"], capture_output=True, text=True, encoding="utf-8")
        if r.returncode:
            raise RuntimeError(r.stderr[-900:])
    finally:
        p.unlink(missing_ok=True)
        shutil.rmtree(B3 / "_tam", ignore_errors=True)
    return sh["n"]


def so_sanh():
    """mỗi cặp: [ảnh][bản đồ cũ] rồi [ảnh][bản đồ mới], ghép một tệp để xem liền."""
    P5 = OUT / "hinh" / "p5"; lst = RA / "_so-sanh.txt"; dong = []
    for cid, (mode, ida, _, _t) in THU.items():
        cap = [P5 / f"{ida}.mp4", P5 / f"{cid}.mp4"] if mode == "lui" else [P5 / f"{cid}.mp4", P5 / f"{ida}.mp4"]
        moi = [P5 / f"{ida}.mp4", RA / f"{cid}.mp4"] if mode == "lui" else [RA / f"{cid}.mp4", P5 / f"{ida}.mp4"]
        dong += cap + moi
    lst.write_text("".join(f"file '{x.as_posix()}'\n" for x in dong), encoding="utf-8")
    out = RA / "so-sanh-cu-moi.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(out)], check=True)
    print(out)


def main():
    a = sys.argv[1:]
    ids = [x for x in a if x in THU] or list(THU)
    bang = d3.lap_bang(PC)
    if "--so-sanh" in a:
        return so_sanh()
    for cid in ids:
        try:
            if "--stills" in a:
                d = RA / "stills" / cid; d.mkdir(parents=True, exist_ok=True); chay(cid, bang, d)
            else:
                chay(cid, bang)
            print("OK", cid, THU[cid][0], bang[cid]["shot"], flush=True)
        except Exception as e:
            print("LỖI", cid, e, flush=True)


if __name__ == "__main__":
    main()
