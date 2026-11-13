# -*- coding: utf-8 -*-
"""Thử đột biến cho kiem-nhip-hinh.py: một phân cảnh mẫu ĐẠT, mỗi đột biến phải làm đúng một luật bật CHẶN.
  python -I -X utf8 rieng/tools/test-kiem-nhip-hinh.py
"""
import copy, importlib.util, sys, tomllib
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
sp = importlib.util.spec_from_file_location("knh", GOC / "kiem-nhip-hinh.py"); K = importlib.util.module_from_spec(sp); sp.loader.exec_module(K)
N = tomllib.loads((GOC / "nguong-nhip-hinh.toml").read_text(encoding="utf-8"))
CH = [("A", 1, 50), ("B", 51, 100)]
CO = ["toan", "trung", "can", "dac-ta"]


def mau():
    """200 s, 4 s/cảnh (15/phút): lặp [anh, ban-do, clip, the, anh]; mọi tài sản khác nhau."""
    ds, t, i = [], 0.0, 0
    vong = ["anh", "ban-do", "clip", "the", "anh"]
    while t < 200 - 1e-6:
        k = vong[i % 5]
        ten = {"anh": f"A{i}", "clip": f"V{i}", "the": f"T{i}", "ban-do": f"M{i % 30}"}[k]
        ds.append({"id": f"S{i + 1:03d}", "kieu": k, "ten": ten, "co": "ban-do" if k == "ban-do" else CO[i % 4],
                   "goc": ["cao", "thap", "ngang", "chech"][i % 4], "t0": t, "t1": t + 4, "dai": 4, "cau": [1 + int(t / 2)]})
        t += 4; i += 1
    return ds


def chay(ds):
    return K.kiem(ds, CH, N, ds[-1]["t1"])[0]


def doi(ds, i, **kw):
    ds = copy.deepcopy(ds); ds[i].update(kw); return ds


goc = mau()
ca = []
ca.append(("gốc phải ĐẠT", goc, None))
# clip dùng 3 lần (cách xa nhau không đủ): dùng V2 ở S008, S013
d = doi(doi(goc, 7, ten="V2"), 12, ten="V2"); ca.append(("clip 3 lần", d, "[dùng lại] clip V2 dùng 3"))
d = doi(goc, 7, ten="V2"); ca.append(("clip cách < 180 s", d, "[dùng lại] clip V2: S003 → S008"))
d = doi(goc, 5, ten="A0"); ca.append(("ảnh cách < 60 s", d, "[dùng lại] ảnh A0: S001 → S006"))
d = doi(doi(doi(goc, 25, ten="A0"), 40, ten="A0"), 45, ten="A0"); ca.append(("ảnh 4 lần", d, "[dùng lại] ảnh A0 dùng 4"))
d = doi(goc, 8, ten="T3"); ca.append(("thẻ 2 lần", d, "[dùng lại] thẻ T3 dùng 2"))
d = copy.deepcopy(goc)
for j in (1, 6, 11, 16):
    d[j].update(ten="MX", goc="cao")
ca.append(("cặp 3D 4 lần", d, "[3D] cặp [MX + cao] dùng 4"))
d = copy.deepcopy(goc)
for j, g in zip((1, 6, 11, 16), ("cao", "thap", "ngang", "chech")):
    d[j].update(ten="MY", goc=g)
ca.append(("bản đồ 4 cảnh/chương", d, "bản đồ MY có 4 cảnh (tối đa 3)"))
d = copy.deepcopy(goc)
for j in (20, 24, 25, 29):
    d[j].update(kieu="ban-do", ten=f"MZ{j}", co="ban-do")
ca.append(("khoảng > 15 s không hình thật", d, "[dòng chảy] "))
d = copy.deepcopy(goc)
for j, c in enumerate(d):
    if c["kieu"] == "ban-do":
        c.update(ten="MW", goc=["cao", "thap", "ngang", "chech", "phang", "tren-xuong"][j % 6])
ca.append(("quá ít bối cảnh 3D", d, "[3D] chỉ có 1 bản đồ"))
d = doi(goc, 5, co="toan"); d = doi(d, 4, co="toan"); ca.append(("hai cảnh thật liền nhau cùng cỡ", d, "cùng cỡ «toan»"))
d = copy.deepcopy(goc)
for c in d:
    if c["kieu"] == "anh" and int(c["id"][1:]) % 3:
        c.update(kieu="the", ten="T" + c["id"])
ca.append(("tỉ lệ hình thật thấp", d, "[dòng chảy] tỉ lệ hình thật"))
d = copy.deepcopy(goc)
for c in d:
    if c["kieu"] == "clip":
        c["ten"] = "V-chung"
    elif c["kieu"] == "anh":
        c["ten"] = f"A-chung{int(c['id'][1:]) % 9}"
ca.append(("kho ít tài sản", [dict(c) for c in d], "[kho]"))
d = copy.deepcopy(goc)
for c in d:
    c.update(t0=c["t0"] * 1.5, t1=c["t1"] * 1.5, dai=6)
ca.append(("nhịp < 12 cảnh/phút", d, "[nhịp]"))

hong = 0
for ten, ds, mong in ca:
    ch = chay(ds)
    if mong is None:
        ok = not ch
    else:
        ok = any(mong in x for x in ch)
    print(("ĐẠT " if ok else "HỎNG"), ten, "" if ok else f"→ {ch[:4]}")
    hong += not ok
print(f"{len(ca) - hong}/{len(ca)}")
sys.exit(1 if hong else 0)
