# -*- coding: utf-8 -*-
"""sfx-kho.py — EP002: tạo 8 tiếng động riêng (kho EP001 22 tiếng dùng lại)  (ElevenLabs SFX qua ai33, kit.py tieng-ai33). Mỗi tiếng dùng lại nhiều lần.
  python -I -X utf8 sfx-kho.py            # tạo mọi tiếng chưa có (tốn credit, 60/giây)
"""
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO / "tools"))
from cau_hinh import duong  # noqa: E402

D = duong("output") / "261113-kokai-kaisen-1904" / "sfx"
D.mkdir(parents=True, exist_ok=True)

# tên: (mô tả tiếng Anh, giây)
KHO = {
    "dong-ho-tick": ("deliberate slow mechanical clock ticking, close, dry, cinematic tension, steady rhythm", 4),
    "dong-ho-chuong": ("single deep clock chime strike, resonant brass bell, long decay, dry", 2),
    "phao-xa": ("very distant heavy naval gun firing across open sea, faint boom with long echo, far away", 3),
    "tau-quay-gap": ("large steel warship turning hard through water, rushing water along the hull, metal groan, rudder strain", 4),
    "den-pha-dem": ("naval searchlight carbon arc electric buzz with a mechanical shutter clack, night, close", 3),
    "ngu-loi-phong": ("torpedo launch splash then underwater whining propeller fading away", 3),
    "hoang-hon-bien": ("calm evening sea ambience with gentle waves and distant seagulls, sunset, no music", 6),
    "phao-cong-thanh": ("heavy siege howitzer firing with a long shell whistle passing overhead and a distant impact boom", 3),
}


def tao(ten):
    mo, g = KHO[ten]
    out = D / f"{ten}.mp3"
    if out.exists():
        return ten, "đã có"
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", str(REPO / "tools/kit/kit.py"), "tieng-ai33",
                        "--text", mo, "--giay", str(g), "--out", str(out), "--yes"], capture_output=True, text=True, encoding="utf-8")
    return ten, ("OK" if r.returncode == 0 else "LỖI " + (r.stderr or r.stdout)[-300:])


if __name__ == "__main__":
    tong = sum(g for _, g in KHO.values()) * 60
    print(f"{len(KHO)} tiếng, ~{tong} credit", flush=True)
    with ThreadPoolExecutor(4) as ex:
        for ten, kq in ex.map(tao, KHO):
            print(ten, kq, flush=True)
