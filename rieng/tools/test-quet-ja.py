# -*- coding: utf-8 -*-
"""Thử đột biến cho quet-ja.py: câu xấu phải bị bắt đúng nhóm và mức; câu sạch không được báo.
Chạy: python -I -X utf8 rieng/tools/test-quet-ja.py   (mã thoát 1 nếu có ca sai)"""
import importlib.util
import sys
import tempfile
from pathlib import Path

AQ = Path(__file__).with_name("quet-ja.py")
spec = importlib.util.spec_from_file_location("quet_ja", AQ)
qj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qj)
q = qj.nap_quet()
ds = q.doc_mau(q.DS_MAU) + q.doc_mau(qj.DS_JA)

# (câu, là tiêu đề?, nhóm mong đợi, mức mong đợi); nhóm None = phải sạch
CA = [
    ("この戦いでは敵兵の死体が山のように積み重なり、血の海となった。", False, "bao_luc", "CANH"),
    ("艦内は黒焦げの遺体であふれ、阿鼻叫喚の地獄絵図だった。", False, "bao_luc", "CANH"),
    ("ロシア兵は焼け死に、船は蒸し焼きになった。", False, "bao_luc", "CANH"),
    ("【閲覧注意】日本海海戦の死体が...", True, "bao_luc", "CHAN"),
    ("衝撃の真実！誰も知らない日本海海戦", True, "giat_tit", "CANH"),
    ("ジャップの艦隊が来た。", False, "miet_thi", "CHAN"),
    ("ロスケの艦隊は全滅した。", False, "miet_thi", "CHAN"),
    ("鬼畜米英を討て、という標語があった。", False, "miet_thi", "CANH"),
    ("東郷さんは艦橋に立った。", False, "miet_thi", "CANH"),
    ("南京事件はでっち上げだった。", False, "phu_nhan", "CHAN"),
    ("原爆投下は英断だった。", False, "phu_nhan", "CANH"),
    ("くたばれ、ロシア艦隊め。", False, "tuc_tiu", "CHAN"),
    ("皇軍は玉砕を選んだ。", False, "ton_vinh", "CANH"),
    ("裕仁は何も語らなかった。", False, "nhan_vat", "CANH"),
    ("竹島の領有をめぐって対立した。", False, "ban_do", "CANH"),
    ("これはウクライナ戦争とも重なる。", False, "thoi_su", "CANH"),
    # câu sạch lấy từ phong cách kịch bản thật: không được báo
    ("日本の連合艦隊は、この四ノットの差を武器に、ロシアのバルチック艦隊を壊滅させた。", False, None, None),
    ("ロシア艦隊は二十一隻が沈没。対する日本が失ったのは、水雷艇わずか三隻のみ。", False, None, None),
    ("T字戦法とは、敵艦隊の進路前方に自分の艦列を横向きに配置する戦術だ。", False, None, None),
    ("連合艦隊司令長官 東郷平八郎大将は、三笠の艦橋に立った。", False, None, None),
]

sai = 0
for cau, tieu_de, nhom, muc in CA:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write(cau + "\n")
    ket = q.quet_file(Path(f.name), ds, tieu_de)
    Path(f.name).unlink()
    got = {(m.nhom, m.muc_do) for _, _, m, _ in ket}
    if nhom is None:
        ok = not ket
    else:
        ok = (nhom, muc) in got
    sai += not ok
    print(("ĐẠT " if ok else "SAI  ") + ("[sạch] " if nhom is None else f"[{nhom}/{muc}] ") + cau[:40], "" if ok else f" → thực tế {sorted(got)}")
print(f"\n{len(CA) - sai}/{len(CA)} ca đúng")
sys.exit(1 if sai else 0)
