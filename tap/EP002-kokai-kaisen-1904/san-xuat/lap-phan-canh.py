# -*- coding: utf-8 -*-
"""
lap-phan-canh.py — Sinh bảng phân cảnh P3 cho EP002 黄海海戦 1904 (13/11/2026), chép cách làm của EP001 JP.

Chưa có giọng: mốc từng ký tự ƯỚC TÍNH ở 327 ký tự/phút (đo trên giọng thật EP001). Sau P4 ghi `moc-cau.json`
(cùng định dạng EP001: {"cau": [[giây của từng ký tự]...], "lang": {}, "het": ...}) rồi chạy lại script này và máy kiểm.

Cảnh dài ~4,3 s (mở ~2,4 s). Hình chọn theo: (1) thẻ ý đồ của câu (TAGS), (2) bể hình của chương (POOL) xoay vòng,
chịu luật chủ kênh 11/11: ảnh/clip ≤ 3 lần, hai lần cách ≥ 60 s; ≤ 4 cảnh liền không có ảnh/clip; A? ≤ 5 s.
Ghi anh.tsv, clip.tsv, rồi thay khối BANG của phan-canh.md. Sau đó: `python -I -X utf8 kiem-phan-canh.py`.
"""
import csv, json, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
KH = GOC.parent / "ke-hoach"
LOI = KH / "loi-doc-v3.txt"
CAU = [l.strip() for l in LOI.read_text(encoding="utf-8").split("\n") if l.strip()]
N = len(CAU)
GIAY_KT = 60 / 327
if (GOC / "moc-cau.json").exists():
    MOC = json.loads((GOC / "moc-cau.json").read_text(encoding="utf-8"))
else:
    t, cau = 0.0, []
    for c in CAU:
        cau.append([round(t + k * GIAY_KT, 3) for k in range(len(c))])
        t += len(c) * GIAY_KT
    MOC = {"cau": cau, "lang": {}, "het": round(t, 2), "uoc_tinh": True}
CHUONG = [("MO", 1, 12), ("C1", 13, 59), ("C2", 60, 98), ("C3", 99, 130), ("C4", 131, 164),
          ("C5", 165, 213), ("C6", 214, 246), ("C7", 247, 284), ("KT", 285, 303)]

# ---------------------------------------------------------------- kho ảnh: bí danh → mã trong nhap/tai-san-hinh.csv
ALIAS = {
    "YALU": "NDL-N2-31", "RFS": "NDL-N2-36", "MFS": "NDL-N1-11", "G12": "NDL-N1-12", "G6": "NDL-N1-13",
    "SRCH": "NDL-N1-14", "STEAM": "NDL-N1-15", "OUTA": "NDL-N1-21", "NORD": "NDL-N1-22", "BASE1": "NDL-N1-03",
    "BASE2": "NDL-N1-04", "SUNS": "NDL-N1-05", "BLKD": "NDL-N1-06", "STRM": "NDL-N1-07", "VED": "NDL-N1-08",
    "TORR": "NDL-N1-09", "CLR": "NDL-N1-10", "FUJN": "NDL-N1-24", "ASAN": "NDL-N1-26", "KASN": "NDL-N1-27",
    "YAK": "NDL-N1-28", "IZUN": "NDL-N1-30", "MIKV": "NDL-N2-32", "DSTA": "NDL-N2-33", "DST": "NDL-N2-34",
    "MINE": "NDL-N2-37", "VTB": "NDL-N2-38", "SHG": "NDL-N2-41", "NISN": "NDL-N2-48", "TOK": "NDL-N2-49",
    "SHIN": "NDL-N2-50", "WHAR": "NDL-N2-51", "PALP": "NDL-N2-52", "EBAS": "NDL-N2-53", "RETS": "NDL-N2-54",
    "POLS": "NDL-N2-55", "GIL1": "NDL-N2-56", "GIL2": "NDL-N2-57", "BLK1": "NDL-N2-58", "BLK2": "NDL-N2-59",
    "KAMB": "NDL-N3-66", "ULS": "NDL-N3-67", "ADM1": "NDL-admirals-togo-kataoka-kamimura",
    "ADM2": "NDL-admirals-yamamoto-saito-ito",
    "TSQ1": "COM-tsesarevich-qingdao-1904", "TSQ2": "COM-tsesarevich-qingdao-1904-b",
    "TSQ3": "COM-tsesarevich-qingdao-1904-c", "TSQG": "COM-tsesarevich-qingdao-gun-1904",
    "TSPC": "COM-tsesarevich-postcard-0810", "TST": "COM-tsesarevich-tacoma-times-1904",
    "TSC": "COM-tsesarevich-cassells-1904", "TSL": "COM-tsesarevich-loc-bain", "TSB": "COM-tsesarevich-brassey-1904",
    "RETI": "COM-retvizan-sunk-1905-ijn", "RETD": "COM-retvizan-damage-ijn", "GHILL": "COM-port-arthur-gold-hill-1905",
    "WRK": "COM-arthur-fleet-wrecks-0105-32", "RET5": "COM-arthur-retvizan-0105-28",
    "PR5": "COM-arthur-poltava-retvizan-0105-39", "PAN": "COM-arthur-panorama-0105",
    "RET12": "COM-retvizan-1904-12-arthur", "RETR": "COM-retvizan-1904-03-repair",
    "NH": "COM-nh101324-entrance-arthur-0810", "SHKB": "COM-shikishima-yellow-sea-0810",
    "RECH": "COM-rechitelny-1904-0911", "NOVS": "COM-novik-scuttled-korsakov", "SCH": "COM-schema-boi-zheltoe-more",
    "ASK1": "COM-askold-port-arthur-1904", "ASK2": "COM-askold-newspaper-1904", "ASK3": "COM-askold-generic",
    "NOV1": "COM-novik-port-arthur-1904", "NOV2": "COM-novik-01", "RSA": "COM-russian-ships-port-arthur-album",
    "KASP": "COM-kasai-battle-port-arthur-print", "TORP": "COM-torpedo-attack-arthur-1904",
    "WYL1": "COM-wyllie-second-blocking", "WYL2": "COM-wyllie-lost-prize-arthur", "OUTH": "COM-outer-harbor-arthur-1904",
    "YU16": "COM-yoshimoto-016-0814-ulsan", "YU17": "COM-yoshimoto-017-0814-ulsan", "CDG": "COM-arthur-coast-defense-gun",
    "VIT": "COM-vitgeft-portrait", "TOGOP": "COM-togo-1904-portrait", "HOW": "COM-28cm-howitzer-arthur",
    "MIK1": "EP1-MIK1", "MIK2": "EP1-MIK2", "MIK3": "EP1-MIK3", "MIKT": "EP1-MIKT", "SHK1": "EP1-SHK1",
    "FUJ": "EP1-FUJ", "ASA": "EP1-ASA", "KAS": "EP1-KAS", "NIS": "EP1-NIS", "ASM": "EP1-ASM", "AZM": "EP1-AZM",
    "IZU": "EP1-IZU", "PORT": "EP1-PORT", "YOSH": "EP1-YOSH",
}
# Chú thích bắt buộc (ảnh không phải ngày 10/8 hoặc cần ghi rõ) — in vào cột Chữ trên hình
NHAN = {
    "RETR": "1904年3月 修理中", "RET12": "1904年12月", "WHAR": "1904年末", "SUNS": "当日の写真ではない",
    "TSPC": "絵葉書（撮影日不詳）", "SCH": "ロシア側経過図（ユリウス暦の日付は伏せる）", "HOW": "図版（Collier 1904）",
    "KASP": "錦絵（1904年2月の旅順口海戦）", "TORP": "想像画（1904年3月）", "YALU": "1904年8月10日 黄海海戦（写真帖英題 YALU）",
    "RFS": "1904年8月10日", "MFS": "1904年8月10日", "SHKB": "1904年8月10日 黄海海戦中", "NH": "1904年8月10日 旅順口",
    "WRK": "1905年1月4日", "RET5": "1905年1月4日", "PR5": "1905年1月4日", "PAN": "1905年1月4日", "GHILL": "1905年 降伏後",
    "ULS": "1904年8月14日 蔚山沖", "YU16": "1904年8月14日 蔚山沖", "YU17": "1904年8月14日 蔚山沖",
    "TSQ1": "青島 1904年夏（海戦後）", "TSQ2": "青島（海戦後）", "TSQ3": "青島 1904年夏", "TSQG": "青島（海戦後）",
    "G12": "当日の写真ではない", "G6": "当日の写真ではない", "SRCH": "当日の写真ではない", "TORR": "当日の写真ではない",
    "VIT": "肖像写真", "TOGOP": "肖像写真（1904年頃）", "ADM1": "肖像（日露戦役海軍写真帖）",
}
CAM = {  # không dùng ở EP002 (lý do ghi ở so-tai-san.md / checks.md)
    "EP1-MAPW1": "bản đồ Viễn Đông cổ có thể chứa Biển Đông không đúng luật cứng",
    "EP1-MAPW2": "bản đồ Viễn Đông cổ có thể chứa Biển Đông không đúng luật cứng",
    "NDL-N1-18": "đề gốc «đuổi tàu buôn», không phải trận này (phản biện P2)",
    "NDL-N3-68": "ảnh người sống sót, chưa soi thương tích",
    "NDL-N1-25": "初瀬 chìm tháng 5/1904, không có trong trận",
    "EP1-TOGO": "A? trùng vai với TOGOP",
}

# Clip AI dùng lại của EP001 (Flow Veo, cảnh chung không định danh). ĐÃ SOÁT SAO (13/11): V07B và V13 có sao trắng trên thân tàu → LOẠI; V08 dùng bản V08b (V08 gốc có sao). mọi cảnh clip ghi nhãn nhỏ «イラスト» (luật kit CLAUDE.md: ghi «minh hoạ» trên hình; chủ kênh 13/11 bỏ chữ «AI生成»)
CLIP = {
    "V01": "hạm đội lúc bình minh (xa, không định danh)", "V02": "hạm đội trong sương", "V03": "biển xa lúc chạng vạng",
    "V05": "bọt sóng dọc mạn tàu chạy nhanh", "V06": "nòng pháo nâng lên",
    "V08": "cột nước đạn rơi quanh tàu", "V09": "hạm đội đổi hướng nhìn từ trên cao", "V10": "khói chiến trận",
    "V14": "đèn pha quét biển đêm", "V16": "quân cảng lúc bình minh",
    "V17": "eo biển buổi sáng", "V18": "nhìn từ cột buồm ra biển", "V19": "mây giông trên biển",
    "V20": "pháo sáng xa trong đêm", "V21": "hai hàng tàu song song", "V24": "hạm đội lúc hoàng hôn",
    "V25": "hạm đội hàng một hướng về mặt trời thấp",
    "V26": "hai hàng tàu song song lúc chạng vạng, chớp pháo xa",
    "V27": "hàng thiết giáp nhìn từ phía sau, chạy ra xa lúc hoàng hôn",
    "V32": "tàu hơi nước đơn độc trên biển lặng lúc chiều tà",
    "V34": "hạm đội tản ra nhiều hướng trong khói chiều",
}
CLIP_DIR = "E:/Goha-JP/output/261111-nihonkai-kaisen-1905/muse"
CLIP_MOI = "E:/Goha-JP/output/261113-kokai-kaisen-1904/muse"  # V25+ làm riêng cho EP002
CLIP_DAI = 7.9

POOL = {
    "MO": ["V09", "SHKB", "V08", "YALU", "V10", "RFS", "V21", "G12", "V05", "NH"],
    "C1": ["NH", "PORT", "OUTH", "RSA", "CDG", "BLK1", "WYL1", "V16", "OUTA", "BLKD", "STRM", "VED", "DSTA", "VTB",
           "KASP", "BLK2", "TORP", "BASE2", "YOSH", "V17", "SHG"],
    "C2": ["TSL", "TSB", "TST", "ASK1", "NOV1", "MIK2", "ASAN", "FUJN", "SHK1", "KASN", "NISN", "YAK", "TOK", "IZUN",
           "ASM", "AZM", "DST", "SHIN", "NORD", "MIK3", "BASE1", "V06", "FUJ", "ASA", "KAS", "NIS", "IZU", "ASK2"],
    "C3": ["STEAM", "MFS", "RFS", "SHKB", "YALU", "CLR", "V05", "V09", "V21", "V08", "G6", "NORD", "V18"],
    "C4": ["V27", "V25", "V05", "V21", "V03", "V19", "STRM", "V18", "V17", "SHK1", "FUJN", "ASAN", "V09", "V01", "STEAM", "MIK3"],
    "C5": ["V26", "G12", "V08", "V10", "MIKT", "G6", "CLR", "V06", "YALU", "SHKB", "V21", "V09", "TSC", "TST"],
    "C6": ["V34", "V32", "V25", "V10", "V03", "V24", "SRCH", "V14", "V20", "TORR", "VTB", "DST", "V19", "SHIN"],
    "C7": ["TSQ1", "TSQ2", "TSQ3", "TSQG", "ASK3", "ULS", "YU16", "YU17", "NOV1", "WHAR", "PALP", "EBAS", "RETS",
           "POLS", "GIL1", "GIL2", "WRK", "RET5", "PR5", "PAN", "GHILL", "RETI", "RETD", "HOW", "RET12", "RECH", "KAMB"],
    "KT": ["V24", "V03", "V16", "V01", "SHKB"],
}
MAPS_CAP = {"MO": ["koukai", "senkai"], "C1": ["ryojun", "koukai"], "C2": ["koukai"], "C3": ["kosen1", "tsuigeki"],
            "C4": ["tsuigeki"], "C5": ["kosen2", "senkai"], "C6": ["sanran", "koukai"], "C7": ["churitsu", "ulsan", "ryojun"],
            "KT": ["koukai"]}
MAP_HINH = {
    "koukai": "Bản đồ 黄海 toàn cảnh: 旅順, 山東半島, hướng ウラジオストク",
    "ryojun": "Bản đồ 旅順口: vòng vây 第三軍, đường pháo từ 大孤山 vào cảng",
    "kosen1": "Bản đồ 13時すぎ: hạm đội Nga lách qua đuôi 第1戦隊, chạy đông nam (xanh=連合艦隊, đỏ=旅順艦隊)",
    "tsuigeki": "Bản đồ truy kích buổi chiều: hai vệt, đồng hồ, dải mặt trời",
    "kosen2": "Bản đồ 17時半すぎ: khoảng cách co lại (6〜7km, tư liệu nước ngoài)",
    "senkai": "Sơ đồ kỳ hạm quay gấp trái, hàng dọc vỡ (không tả cảnh trúng đạn)",
    "sanran": "Bản đồ đội hình tan: các hướng chạy, mũi tên về 旅順",
    "churitsu": "Bản đồ 3 cảng trung lập 青島/上海/サイゴン; có Hoàng Sa, Trường Sa (Việt Nam), Biển Đông; không đường lưỡi bò, không nhãn 南シナ海, không biên giới hiện đại",
    "ulsan": "Bản đồ 蔚山沖 (14/8) và đường ノヴィーク vòng quanh Nhật tới コルサコフ (20/8)",
}

W = "Wikipedia"
TAGS = {
    1: [("C", "kazu", "戦艦 ロシア6 対 日本4", W), "TSL"], 2: [("C", "chin0", "戦艦の沈没 0", W), "SHKB"],
    3: ["M:koukai", "V02"], 4: ["PAN"], 5: ["V09", "YALU"], 6: ["TOGOP", "G12"],
    7: [("C", "hizuke", "1904年8月10日 黄海", W), "NH"], 8: [("C", "nichibotsu", "日没 午後8時ごろ", W), "V03"],
    9: ["V14"], 10: ["TSPC", "M:senkai"], 11: [("C", "nokori", "日没まで あと1時間20分ほど", W)], 12: ["M:koukai", "RFS"],
    13: [("C", "soucho", "1904年8月10日 早朝", W), "NH"], 16: ["NH", "RSA"], 19: ["M:koukai"], 20: ["OUTH"],
    22: ["M:ryojun"], 23: [("C", "daikozan", "8月7日〜 大孤山から港内砲撃", W), "M:ryojun"], 24: ["RETR"], 25: ["VIT"],
    26: ["CDG"], 28: ["BLKD"], 29: ["M:ryojun"], 31: ["STRM"],
    33: [("C", "makarov", "4月 マカロフ司令長官 戦死（ペトロパヴロフスク 触雷）", W), "MINE"], 34: ["VIT"], 35: ["RSA"],
    37: ["WYL2"], 38: [("C", "meirei", "極東総督アレクセーエフ → ウラジオストクへ回航", W)],
    39: [("C", "tsar", "皇帝ニコライ2世も支持", W)], 40: ["M:koukai"], 42: ["ADM1", "OUTA"], 43: ["MIK1"], 44: ["M:koukai"],
    45: ["BLKD", "DSTA"], 49: [("C", "nigekiri", "逃げ切り＝日没の時点で 隊形と針路を保つこと", W)],
    50: [("C", "nichibotsu2", "日没 午後8時ごろ", W)],
    54: [("C", "jikoku7", "早朝／正午すぎ／13時すぎ／17時半すぎ／18時40分ごろ／20時ごろ／夜", W)], 57: ["V16"], 59: ["MIKV"],
    63: ["TSC", "RETR", "TSB"], 65: ["ASK1", "NOV1"], 66: [("C", "rokoku", "旅順艦隊 戦艦6・防護巡洋艦4", W)], 67: ["RECH"],
    71: ["MIK2", "ASAN", "FUJN", "SHK1"], 72: ["KASN", "NISN"], 73: [("C", "dai1", "第1戦隊 戦艦4＋装甲巡洋艦2", W)],
    74: [("C", "dai3", "第3戦隊 出羽重遠中将", W), "YAK"], 75: ["DST", "SHIN"], 76: ["TORR", "VTB"],
    78: [("C", "hikaku", "戦艦 日本4 対 ロシア6", W)], 81: [("C", "suirai", "駆逐艦18 / 水雷艇およそ30", W)], 82: ["DSTA"],
    83: ["V21"], 85: ["ADM1"], 87: ["M:koukai"], 90: ["TOGOP"], 92: ["V19"], 94: ["MIKV"], 97: ["V18"], 98: ["V17"],
    101: [("C", "shogo", "正午すぎ 日没まで7時間以上", W)], 104: ["STEAM", "M:kosen1"],
    106: [("C", "t13", "午後1時すぎ 砲撃開始", W), "MFS"], 107: ["RFS"],
    108: [("C", "kyori15", "15キロ近く（海外資料）", W)], 109: ["M:kosen1"], 110: ["M:kosen1"], 111: ["SCH"], 112: ["V05"],
    113: ["M:kosen1"], 117: ["SHKB"], 118: ["M:tsuigeki"], 120: ["V09"],
    122: [("C", "t13b", "午後1時すぎ 日没まであと7時間ほど", W)], 125: ["TOGOP"], 127: ["V21"], 129: ["V05"],
    132: [("C", "kazu2", "戦艦 日本4 / ロシア6", W)], 136: ["V27", "M:tsuigeki"],
    137: [("C", "sokudo", "約15ノット 対 13〜14ノット（海外資料）", W)], 139: [("C", "t1730", "午後5時半すぎ 砲撃再開", W)],
    141: ["M:tsuigeki"], 142: ["V27", "M:tsuigeki"], 147: [("C", "osoi", "艦隊は 一番遅い艦に合わせる", W)], 150: ["V03"],
    152: ["MIKV"], 155: ["SUNS"], 158: ["V25", "V24"], 160: ["V14"], 161: [("C", "kyoso", "追いつくのが先か 日が沈むのが先か", W)],
    163: ["V25", "V03"],
    168: [("C", "t1730b", "午後5時半すぎ 日没まであと2時間半ほど", W)], 169: ["V26", "G12"], 171: ["V26", "M:kosen2"],
    172: [("C", "kyori67", "6〜7キロ（海外資料）", W)], 174: ["M:kosen2"], 176: ["MIKT"],
    177: [("C", "hidan", "三笠 被弾 20発あまり", W), "MIK3"], 179: ["CLR"],
    180: [("C", "t1840", "午後6時40分ごろ 日没まであと1時間20分ほど", W)], 184: ["TSC", "M:senkai"], 186: ["VIT"],
    189: [("C", "nidome", "司令長官の戦死 この年2度目（4月 マカロフ / 8月 ヴィトゲフト）", W)], 191: ["M:senkai"],
    192: ["M:senkai", "V09"], 193: ["M:senkai"], 196: ["TSQG"], 198: ["G12"], 199: ["M:senkai"], 200: ["V09"], 201: ["V21"],
    203: ["V05"], 205: ["V10"], 209: [("C", "renzoku", "17時半すぎ 砲戦再開 → 18時40分ごろ 命中", W)], 212: ["MIKT", "TSPC"],
    214: [("C", "t1840c", "午後6時40分ごろ", W)], 215: ["V34", "M:sanran"], 217: ["M:sanran"], 218: ["V34", "M:sanran"],
    222: [("C", "ukhtom", "次席指揮官 ウフトムスキー少将（戦艦ペレスヴェート座乗）", W)], 224: ["M:sanran"], 226: ["M:koukai"],
    229: ["V32", "V24"], 230: ["V32", ("C", "t20", "午後8時ごろ 日没", W)], 232: ["V03"],
    233: [("C", "nido", "砲撃戦 2度 / 戦艦の沈没 0", W)], 239: ["TORR"], 240: ["SRCH"], 241: ["VTB", "V14"],
    242: ["V20"], 244: [("C", "yoru", "七つ目の時刻 夜", W)],
    249: [("C", "kikan", "旅順へ帰還：戦艦5・パルラーダ", W), "PALP"], 250: ["TSL"], 252: ["M:churitsu"],
    254: ["TSQ1", "TSQ2", "M:churitsu"], 255: ["ASK3"], 256: ["M:churitsu"], 257: ["M:churitsu"], 258: ["TSQ3"],
    260: ["M:ulsan"], 262: ["ULS", "YU16"], 263: ["YU17"], 264: ["NOV2", "M:ulsan"], 266: ["NOVS"],
    267: [("C", "nenpyo", "8月10日 / 8月14日 / 8月20日", W)], 269: ["WHAR"], 273: [("C", "t125", "12月5日", W)],
    275: ["HOW", "EBAS"], 277: ["WRK", "POLS", "RETS"], 279: ["PR5", "RET5", "GIL2"], 280: ["PAN", "GHILL"],
    282: [("C", "nihonkai", "→ 日本海海戦（翌年）", W)], 283: ["RETI"],
    285: ["V03"], 287: [("C", "matome", "逃げ切りまで あと1時間あまり", W)], 289: ["M:kosen1"], 290: ["M:kosen2"],
    291: ["M:senkai"], 293: ["TSPC"], 295: [], 296: ["M:sanran"],
    297: [("C", "comment", "隊形を保てていたら？ コメントで", W)], 300: ["V24"], 302: ["V16"],
}

COGOC = [("trung", "ngang"), ("toan", "chech"), ("can", "thap"), ("toan-xa", "phang"), ("trung", "cao"), ("can", "ngang"),
         ("toan", "thap"), ("trung", "chech")]


def uoc_cau(i):
    t0 = MOC["cau"][i - 1][0]
    t1 = MOC["cau"][i][0] if i < N else MOC["het"]
    return t0, t1


def nap_kho():
    R = {r["ma"]: r for r in csv.DictReader(open(KH / "nhap" / "tai-san-hinh.csv", encoding="utf-8-sig"))}
    A = {}
    for k, ma in ALIAS.items():
        r = R[ma]
        if ma in CAM or r["hang"] == "C":
            sys.exit(f"{k}: {ma} bị cấm/hạng C")
        if not Path(r["tep_cuc_bo"]).exists():
            sys.exit(f"{k}: thiếu tệp {r['tep_cuc_bo']}")
        A[k] = (r["tep_cuc_bo"], r["hang"], r["mo_ta"], r["giay_phep"])
    return A


def main():
    A = nap_kho()
    with open(GOC / "anh.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["tep", "hang", "ghi_nguon", "file", "mo_ta"])
        for k, (p, hang, mo_ta, gp) in A.items():
            nguon = "国立国会図書館デジタルコレクション" if ALIAS[k].startswith("NDL") else "Wikimedia Commons"
            w.writerow([k, hang, f"{nguon} · {mo_ta[:40]}", p.replace("\\", "/"), mo_ta])
    with open(GOC / "clip.tsv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["ma", "mo_ta", "file", "dai"])
        for k, mo in CLIP.items():
            w.writerow([k, mo, (f"{CLIP_MOI}/{k}.mp4" if int(k[1:3]) >= 25 else f"{CLIP_DIR}/{ {'V08': 'V08b'}.get(k, k) }.mp4"), CLIP_DAI])

    cn = {i: ten for ten, a, b in CHUONG for i in range(a, b + 1)}
    bd = [(1, 0, 0.0)]
    for i in range(1, N + 1):
        t0, t1 = uoc_cau(i)
        muc = 2.4 if cn[i] == "MO" else (3.6 if cn[i] == "C5" else 4.3)
        if i > 1:
            if t0 - bd[-1][2] >= muc * 0.68 or cn[i] != cn[bd[-1][0]]:
                bd.append((i, 0, t0))
        L = len(CAU[i - 1])
        tm = MOC["cau"][i - 1]
        cur = bd[-1][2] if bd[-1][0] == i else t0
        while t1 - cur > muc * 1.35:
            cur += muc
            k = next((x for x in range(L) if tm[x] >= cur - 1e-6), None)
            if k is None or k == 0 or (bd[-1][0] == i and k <= bd[-1][1]):
                break
            bd.append((i, k, tm[k]))
            cur = tm[k]
    scenes = []
    for j, (i, k, t0) in enumerate(bd):
        t_next = bd[j + 1][2] if j + 1 < len(bd) else MOC["het"]
        scenes.append(dict(i=i, k=k, t0=t0, t1=t_next, ch=cn[i]))
    for s in scenes:
        s["tags"] = []
        for i in range(1, N + 1):
            ti = MOC["cau"][i - 1][0]
            if s["t0"] - 1e-6 <= ti < s["t1"] - 1e-6 or (i == s["i"] and s["k"] == 0):
                s["tags"] += TAGS.get(i, [])
    scenes[0]["t0"] = 0.0

    dung, ptr, mptr, run, GAP = {}, {c: 0 for c in POOL}, {c: 0 for c in MAPS_CAP}, 0, 68

    def ok_img(key, t0, dur=0.0):
        if key in CLIP and dur > 7.7:
            return False
        if key in A and A[key][1] in ("A?", "B") and dur > 4.8:
            return False
        u = dung.get(key, [])
        return len(u) < 3 and not (u and t0 - u[-1] < GAP)

    def lay_pool(ch, t0, dur=0.0):
        P = POOL[ch]
        for _ in range(len(P)):
            key = P[ptr[ch] % len(P)]
            ptr[ch] += 1
            if ok_img(key, t0, dur):
                return key
        for c2 in POOL:
            for key in POOL[c2]:
                if ok_img(key, t0, dur):
                    return key
        return None

    la_img = lambda p: isinstance(p, str) and not p.startswith("M:")
    for s in scenes:
        t0, dur, tags, pick = s["t0"], s["t1"] - s["t0"], s["tags"], None
        pick = next((tg for tg in tags if isinstance(tg, tuple)), None)
        if pick is None:
            pick = next((tg for tg in tags if la_img(tg) and ok_img(tg, t0, dur)), None)
        if pick is None:
            pick = next((tg for tg in tags if isinstance(tg, str) and tg.startswith("M:")), None)
        if run >= 3 and not la_img(pick):
            cand = lay_pool(s["ch"], t0, dur)
            if cand:
                pick = cand
        if pick is None:
            if run >= 1:
                pick = lay_pool(s["ch"], t0, dur)
            if pick is None:
                m = MAPS_CAP[s["ch"]]
                pick = "M:" + m[mptr[s["ch"]] % len(m)]
                mptr[s["ch"]] += 1
        s["pick"] = pick
        if la_img(pick):
            dung.setdefault(pick, []).append(t0)
            run = 0
        else:
            run += 1

    dong, prev_cg, ch_da_dt, cogoc_i = [], None, set(), 0
    for n_, s in enumerate(scenes, 1):
        p = s["pick"]
        neo = str(s["i"]) if s["k"] == 0 else f"{s['i']}:{s['k']}"
        am = "Nhạc nền; nhấn khi cắt"
        if isinstance(p, tuple):
            _, ten, chu, ng = p
            nguon, co, goc = f"the:{ten}", "the", "phang"
            hinh, chuc = "Thẻ số liệu: " + chu, f"Thẻ: {chu} · Nguồn: {ng}"
        elif p.startswith("M:"):
            mm = p[2:]
            nguon, co, goc = f"ban-do:{mm}", "ban-do", "phang" if mm in ("senkai", "kosen2") else "tren-xuong"
            hinh, chuc = MAP_HINH[mm], "Đồ hoạ code · đồng hồ góc phải"
        elif p in CLIP:
            nguon = f"clip:{p}"
            co, goc = COGOC[cogoc_i % len(COGOC)]
            cogoc_i += 1
            hinh, chuc = f"Clip AI: {CLIP[p]}", 'Nhãn "イラスト" (chữ nhỏ góc dưới trái)'
        else:
            _, hang, mo_ta, _ = A[p]
            nguon = f"anh:{p}"
            co, goc = COGOC[cogoc_i % len(COGOC)]
            cogoc_i += 1
            hinh = f"Ảnh tư liệu: {mo_ta}"
            chuc = f'Chú thích "{NHAN[p]}"' if p in NHAN else "—"
        if s["ch"] not in ch_da_dt and any(x["ch"] == s["ch"] for x in scenes[:n_ - 1]) and nguon.startswith(("anh", "clip")):
            co = "dac-ta"
            ch_da_dt.add(s["ch"])
            hinh = "Cận đặc tả: " + hinh
        if prev_cg == (co, goc) and nguon.startswith(("anh", "clip")):
            co, goc = ("trung", "chech") if (co, goc) != ("trung", "chech") else ("can", "thap")
        prev_cg = (co, goc)
        hinh, chuc = hinh.replace("|", "/"), chuc.replace("|", "/")
        dong.append(f"| S{n_:03d} | {neo} | {nguon} | {co}/{goc} | {hinh} | {chuc} | {am} |")

    md = (GOC / "phan-canh.md").read_text(encoding="utf-8")
    bang = ("<!-- BANG -->\n| # | Neo | Nguồn hình | Cỡ / góc | Hình | Chữ trên hình | Âm |\n|---|---|---|---|---|---|---|\n"
            + "\n".join(dong) + "\n<!-- /BANG -->")
    md = re.sub(r"<!-- BANG -->.*?<!-- /BANG -->", lambda m: bang, md, flags=re.S)
    (GOC / "phan-canh.md").write_text(md, encoding="utf-8", newline="\n")
    dem = {}
    for s in scenes:
        p = s["pick"]
        k = "the" if isinstance(p, tuple) else "ban-do" if p.startswith("M:") else "clip" if p in CLIP else "anh"
        dem[k] = dem.get(k, 0) + 1
    print(len(scenes), "cảnh;", dem, f"{len(scenes) / MOC['het'] * 60:.1f} cảnh/phút", "(ước tính)" if MOC.get("uoc_tinh") else "")


if __name__ == "__main__":
    main()
