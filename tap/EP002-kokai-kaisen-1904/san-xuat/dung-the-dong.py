# -*- coding: utf-8 -*-
"""
dung-the-dong.py — dựng thẻ số liệu ĐỘNG (EP002: 44 thẻ) (the-dong/the-dong.js, GSAP) qua dung-trang.mjs.

  python -I -X utf8 dung-the-dong.py --stills S001 S010 …   # ảnh soi: 0,4 s / giữa / cuối
  python -I -X utf8 dung-the-dong.py --render S001 S010 …   # mp4 đúng số khung → hinh/p5/<mã>.mp4 (không phủ nhãn)
  python -I -X utf8 dung-the-dong.py --render-het           # mọi cảnh the:* của phan-canh.json
dung-p5.py gọi hàm render_the(c, out) của tệp này cho các cảnh kiểu `the`.
"""
import json, re, subprocess, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
REPO = next(p for p in GOC.parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO / "tools"))
from cau_hinh import duong  # noqa: E402

OUT = duong("output") / "261113-kokai-kaisen-1904"
TD = GOC / "the-dong"
FPS = 24
DT = ["node", str(REPO / "tools/kit/dung-trang.mjs")]
W = "Wikipedia"


KICK = "黄海海戦 · 1904年8月10日"


def gio(g, tu, nhan, kicker=KICK):
    return {"kieu": "dong-ho", "gio": g, "tu": tu, "nhan_gio": nhan, "kicker": kicker}


def mg(d1, d2="", kicker=KICK):
    return {"kieu": "moc-gio", "kicker": kicker, "dong1": d1, "dong2": d2}


def dem(kicker, *rows):
    return {"kieu": "dem-so", "kicker": kicker, "rows": list(rows)}


def hang(truoc, value, don_vi, mau):
    return {"truoc": truoc, "value": value, "don_vi": don_vi, "mau": mau}


# Quy ước màu: đỏ = 連合艦隊, xám lạnh = 旅順艦隊, kem = trung lập. Số liệu chỉ từ so-so-lieu.csv (mã trong phan-canh.md).
CARDS = {
    "kazu": {"kieu": "thanh-so-sanh", "kicker": "戦艦の数", "a": {"nhan": "露", "so": 6, "mau": "nga", "don_vi": "隻"}, "b": {"nhan": "日", "so": 4, "mau": "nhat", "don_vi": "隻"}, "ket": "数ではロシアが上"},
    "chin0": dem("1904年8月10日", hang("戦艦の沈没", 0, "隻", "kem")),
    "hizuke": mg("1904年8月10日", "黄海 · 日露戦争"),
    "nichibotsu": gio("20:00", "19:30", "日没（午後8時ごろ）"),
    "nokori": dem("日没まで", hang("あと", 1, "時間", "kem"), hang("", 20, "分ほど", "kem")),
    "soucho": mg("1904年8月10日", "早朝"),
    "daikozan": mg("8月7日〜", "大孤山から港内を砲撃"),
    "makarov": mg("4月 マカロフ司令長官 戦死", "戦艦ペトロパヴロフスク 触雷"),
    "meirei": mg("極東総督アレクセーエフ", "ウラジオストクへ回航を命令"),
    "tsar": mg("皇帝ニコライ2世", "これを支持"),
    "nigekiri": mg("逃げ切り ＝", "日没の時点で 隊形と針路を保つこと"),
    "nichibotsu2": gio("20:00", "19:30", "日没（午後8時ごろ）"),
    "jikoku7": mg("七つの時刻", "早朝 / 正午すぎ / 13時すぎ / 17時半すぎ / 18時40分ごろ / 20時ごろ / 夜"),
    "rokoku": dem("旅順艦隊", hang("戦艦", 6, "隻", "nga"), hang("防護巡洋艦", 4, "隻", "nga")),
    "dai1": dem("連合艦隊 第1戦隊", hang("戦艦", 4, "隻", "nhat"), hang("装甲巡洋艦", 2, "隻", "nhat")),
    "dai3": mg("第3戦隊", "出羽重遠中将"),
    "hikaku": {"kieu": "thanh-so-sanh", "kicker": "戦艦の数", "a": {"nhan": "露", "so": 6, "mau": "nga", "don_vi": "隻"}, "b": {"nhan": "日", "so": 4, "mau": "nhat", "don_vi": "隻"}, "ket": "戦艦の数ではロシアが上"},
    "suirai": dem("連合艦隊", hang("駆逐艦", 18, "隻", "nhat"), hang("水雷艇", 30, "隻ほど", "nhat")),
    "shogo": gio("12:00", "11:30", "正午すぎ · 日没まで 7時間以上"),
    "t13": gio("13:00", "12:30", "午後1時すぎ · 砲撃開始"),
    "kyori15": dem("砲撃開始の距離（海外資料）", hang("距離", 15, "キロ近く", "kem")),
    "t13b": gio("13:00", "12:30", "午後1時すぎ · 日没まであと7時間ほど"),
    "kazu2": {"kieu": "thanh-so-sanh", "kicker": "戦艦の数", "a": {"nhan": "露", "so": 6, "mau": "nga", "don_vi": "隻"}, "b": {"nhan": "日", "so": 4, "mau": "nhat", "don_vi": "隻"}, "ket": "なぜ、逃げ切れなかったのか"},
    "sokudo": dem("速力（海外資料）", hang("連合艦隊 約", 15, "ノット", "nhat"), hang("旅順艦隊", 13, "〜14ノット", "nga")),
    "t1730": gio("17:30", "17:00", "午後5時半すぎ · 砲撃再開"),
    "osoi": mg("艦隊は", "一番遅い艦に合わせる"),
    "kyoso": mg("追いつくのが先か", "日が沈むのが先か"),
    "t1730b": gio("17:30", "17:00", "午後5時半すぎ · 日没まであと2時間半ほど"),
    "kyori67": dem("砲撃再開の距離（海外資料）", hang("距離", 6, "〜7キロ", "kem")),
    "hidan": dem("旗艦「三笠」", hang("被弾", 20, "発あまり", "nhat")),
    "t1840": gio("18:40", "18:10", "午後6時40分ごろ · 日没まであと1時間20分ほど"),
    "nidome": mg("司令長官の戦死は この年2度目", "4月 マカロフ / 8月 ヴィトゲフト"),
    "renzoku": mg("17時半すぎ 砲戦再開", "18時40分ごろ 命中"),
    "t1840c": gio("18:40", "18:10", "午後6時40分ごろ"),
    "ukhtom": mg("次席指揮官 ウフトムスキー少将", "戦艦ペレスヴェート座乗"),
    "t20": gio("20:00", "19:30", "午後8時ごろ · 日没"),
    "nido": dem("この日", hang("砲撃戦", 2, "度", "kem"), hang("戦艦の沈没", 0, "隻", "kem")),
    "yoru": mg("七つ目の時刻", "夜"),
    "kikan": dem("旅順へ帰還", hang("戦艦", 5, "隻", "nga"), hang("防護巡洋艦パルラーダ", 1, "隻", "nga")),
    "nenpyo": mg("8月10日 / 8月14日 / 8月20日"),
    "t125": mg("12月5日"),
    "nihonkai": mg("→ 日本海海戦", "（翌年）"),
    "matome": mg("逃げ切りまで", "あと1時間あまり"),
    "comment": mg("隊形を保てていたら？", "コメントで教えてください"),
}


def shot_cua(c):
    d = dict(CARDS[c["ten"]])
    m = re.search(r"Nguồn: ([^\"·]+)", c["chu"])
    d["nguon"] = (m.group(1).strip() if m else W)
    n = round(c["t1"] * FPS) - round(c["t0"] * FPS)
    d["duration"] = n / FPS
    return d, n


def trang(c, shot):
    p = TD / f"_c_{c['id']}.html"
    p.write_text('<!doctype html><html lang="ja"><head><meta charset="utf-8"><link rel="stylesheet" href="the-dong.css"></head><body><div id="root"></div>'
                 '<script src="gsap.min.js"></script><script>window.SHOT = ' + json.dumps(shot, ensure_ascii=False) + ';</script>'
                 '<script src="the-dong.js"></script></body></html>\n', encoding="utf-8")
    return p


def render_the(c, out):
    shot, n = shot_cua(c)
    p = trang(c, shot)
    r = subprocess.run(DT + [str(p), "--out", str(out), "--fps", str(FPS), "--force"], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise RuntimeError(r.stderr[-700:])
    p.unlink(missing_ok=True)
    return n


def stills(c, d):
    shot, n = shot_cua(c)
    p = trang(c, shot)
    t = shot["duration"]
    r = subprocess.run(DT + [str(p), "--stills", f"0.4,{t * 0.45:.2f},{t - 0.05:.2f}", "--out-dir", str(d)], capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        raise RuntimeError(r.stderr[-700:])
    p.unlink(missing_ok=True)


def main():
    a = sys.argv[1:]
    PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))["canh"]
    the = [c for c in PC if c["kieu"] == "the"]
    ids = [x for x in a if re.fullmatch(r"S\d{3}", x)]
    chon = the if "--render-het" in a else [c for c in the if c["id"] in ids]
    if "--stills" in a:
        d = OUT / "hinh" / "the-dong-stills"
        d.mkdir(parents=True, exist_ok=True)
        for c in chon:
            try:
                dd = d / c["id"]; dd.mkdir(exist_ok=True)
                stills(c, dd)
                print("stills", c["id"], c["ten"])
            except Exception as e:
                print("LỖI", c["id"], e)
        return
    for c in chon:
        out = OUT / "hinh" / "p5" / f"{c['id']}.mp4"
        try:
            n = render_the(c, out)
            print(f"  {c['id']} the:{c['ten']:<8} {n} khung")
        except Exception as e:
            print("LỖI", c["id"], e)


if __name__ == "__main__":
    main()
