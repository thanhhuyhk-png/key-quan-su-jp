# -*- coding: utf-8 -*-
"""
them-clip-moi.py — gắn các clip Flow MỚI của EP002 (V25–V34, đã soát sao) vào bảng phân cảnh rồi báo cảnh nào đổi.
  python -I -X utf8 them-clip-moi.py V25 V26 ...      # chỉ các mã có tệp trong <output>/muse/ và đã soát sao
Sửa lap-phan-canh.py (CLIP, CLIP_MOI, TAGS, POOL), chạy lại lap-phan-canh.py + kiem-phan-canh.py, so với phan-canh.json cũ,
xoá hình/p5/Sxxx.mp4 của cảnh đổi để dung-p5.py dựng lại. In danh sách cảnh đổi.
"""
import json, re, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
REPO = next(p for p in GOC.parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO / "tools"))
from cau_hinh import duong  # noqa: E402

OUT = duong("output") / "261113-kokai-kaisen-1904"
# mã: (mô tả, câu gắn thẻ ý đồ, chương cho bể hình)
MOI = {
    "V25": ("hạm đội hàng một hướng về mặt trời thấp", [158, 163], ["C4", "C6"]),
    "V26": ("hai hàng tàu song song lúc chạng vạng, chớp pháo xa", [169, 171], ["C5"]),
    "V27": ("hàng thiết giáp nhìn từ phía sau, chạy ra xa lúc hoàng hôn", [136, 142], ["C4"]),
    "V28": ("loạt pháo cả mạn tầm xa (thân tàu trơn)", [176, 198], ["C5"]),
    "V29": ("tàu đầu hàng quay gấp trái, tàu sau tách ra (nhìn từ trên)", [192, 199], ["C5"]),
    "V30": ("tàu phóng lôi ban đêm, đèn pha giao nhau", [239, 241], ["C6"]),
    "V31": ("pháo công thành bắn xuống cảng", [275, 277], ["C7"]),
    "V32": ("tàu hơi nước đơn độc trên biển lặng lúc chiều tà", [229, 230], ["C6"]),
    "V33": ("tàu hư hại neo ở cảng trung lập lúc bình minh", [254, 255], ["C7"]),
    "V34": ("hạm đội tản ra nhiều hướng trong khói chiều", [215, 218], ["C6"]),
}


def main():
    ma = [a for a in sys.argv[1:] if a in MOI]
    p = GOC / "lap-phan-canh.py"
    t = p.read_text(encoding="utf-8")
    cu = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))["canh"]
    cu_ky = {c["id"]: (c["nguon"], round(c["t0"], 2), round(c["t1"], 2)) for c in cu}
    for m in ma:
        if not (OUT / "muse" / f"{m}.mp4").exists():
            sys.exit(f"thiếu {OUT / 'muse' / (m + '.mp4')}")
        mo, cau, chs = MOI[m]
        if f'"{m}":' not in t.split("CLIP_DIR =")[0]:
            t = t.replace('    "V24": "hạm đội lúc hoàng hôn",\n}', f'    "V24": "hạm đội lúc hoàng hôn",\n    "{m}": "{mo}",\n}}', 1)
        for ch in chs:
            t = re.sub(r'(    "%s": \[)' % ch, r'\1"%s", ' % m, t, count=1)
        for n in cau:
            if re.search(r"\b%d: \[" % n, t.split("TAGS = {")[1]):
                t = re.sub(r"(\b%d: \[)" % n, r'\1"%s", ' % m, t, count=1)
            else:
                t = t.replace("TAGS = {\n", 'TAGS = {\n    %d: ["%s"],\n' % (n, m), 1)
    # đường dẫn clip mới
    if "CLIP_MOI" not in t:
        t = t.replace('CLIP_DIR = "E:/Goha-JP/output/261111-nihonkai-kaisen-1905/muse"',
                      'CLIP_DIR = "E:/Goha-JP/output/261111-nihonkai-kaisen-1905/muse"\nCLIP_MOI = "E:/Goha-JP/output/261113-kokai-kaisen-1904/muse"  # V25+ làm riêng cho EP002')
        t = t.replace("w.writerow([k, mo, f\"{CLIP_DIR}/{ { 'V08': 'V08b'}.get(k, k) }.mp4\", CLIP_DAI])",
                      "w.writerow([k, mo, (f\"{CLIP_MOI}/{k}.mp4\" if int(k[1:3]) >= 25 else f\"{CLIP_DIR}/{ { 'V08': 'V08b'}.get(k, k) }.mp4\"), CLIP_DAI])")
    p.write_text(t, encoding="utf-8")
    for a in (["lap-phan-canh.py"], ["kiem-phan-canh.py"]):
        r = subprocess.run([sys.executable, "-I", "-X", "utf8", str(GOC / a[0])], capture_output=True, text=True, encoding="utf-8", cwd=GOC)
        print(r.stdout[-700:], r.stderr[-500:])
        if r.returncode:
            sys.exit("lỗi " + a[0])
    mo_ = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))["canh"]
    doi = [c["id"] for c in mo_ if cu_ky.get(c["id"]) != (c["nguon"], round(c["t0"], 2), round(c["t1"], 2))]
    for i in doi:
        (OUT / "hinh" / "p5" / f"{i}.mp4").unlink(missing_ok=True)
    print(f"{len(doi)} cảnh đổi (đã xoá hình cũ để dựng lại): {doi[:40]}")


if __name__ == "__main__":
    main()
