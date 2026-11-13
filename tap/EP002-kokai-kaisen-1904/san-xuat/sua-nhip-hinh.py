# -*- coding: utf-8 -*-
"""
sua-nhip-hinh.py — EP002, 13/11/2026: sửa «phần dễ» theo rieng/tools/kiem-nhip-hinh.py trên phan-canh.md (user duyệt).
Chỉ đổi cột nguồn / cỡ-góc / mô tả hình / chữ của từng cảnh; mốc thời gian giữ nguyên nên giọng không lệch.
  - 13 lần dùng clip vượt trần (3 lần hoặc cách < 180 s) → ảnh tư liệu chưa dùng/ít dùng hoặc clip mới dùng 1 lần, chọn theo câu đọc
  - 2 khoảng > 15 s không có hình thật → S225 (レトヴィザン突進), S302 (距離が縮まる) đổi sang ảnh tư liệu
  - 2 cặp hình thật liền nhau cùng cỡ → S079, S094 đổi ảnh khác cỡ
Chạy: python -I -X utf8 sua-nhip-hinh.py  rồi  python -I -X utf8 kiem-phan-canh.py  (ghi lại phan-canh.json)
"""
import csv, re, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GOC = Path(__file__).resolve().parent
MD = GOC / "phan-canh.md"
ANH = {r["tep"]: r for r in csv.DictReader(open(GOC / "anh.tsv", encoding="utf-8"), delimiter="\t")}
CLIP = {r["ma"]: r for r in csv.DictReader(open(GOC / "clip.tsv", encoding="utf-8"), delimiter="\t")}
NHAN_AI = 'Nhãn "イラスト" (chữ nhỏ góc dưới trái)'

# mã cảnh → (nguồn mới, cỡ/góc mới, lý do theo câu đọc)
SUA = {
    "S079": ("anh:MIK3", "can/ngang", "一方、連合艦隊です → 三笠 (Brassey) thay ảnh tàu Nga; khác cỡ với S080"),
    "S094": ("anh:BASE1", "can/thap", "戦艦の数 → 根拠地の軍艦, tiền cảnh pháo chính; khác cỡ với S095"),
    "S128": ("anh:YOSH", "toan/ngang", "V09 lần 3 → ảnh biển trong 写真帖"),
    "S130": ("anh:NISN", "trung/chech", "後ろについた側 → 日進 (cuối hàng 第1戦隊); V21 lần 3"),
    "S132": ("anh:ASK2", "trung/ngang", "最初の勝負は旅順艦隊 → tàu Nga アスコルド; V08 lần 3"),
    "S137": ("anh:STEAM", "toan/ngang", "差を決めるのは速さ → 主力艦隊 敵に向かう(煙); V05 cách < 180 s"),
    "S145": ("anh:RSA", "trung/chech", "十三〜十四ノット, ポルタヴァ → ảnh tàu Nga ở 旅順; V03 cách < 180 s"),
    "S148": ("anh:FUJ", "trung/ngang", "追う時間 → 戦艦「富士」; V19 lần 3"),
    "S166": ("clip:V32", "toan-xa/thap", "時間は味方 → tàu đơn độc chiều tà (V32 lần 2); V25 cách < 180 s"),
    "S168": ("anh:SRCH", "toan-xa/ngang", "夜になれば見失う → 探照灯 夜間 (ảnh thật; clip V20 là cảnh tàu cháy, sai nghĩa); V14 lần 3"),
    "S180": ("anh:NORD", "can/ngang", "はるかに近い距離 → pháo thủ ノルデンフェルト; V10 cách < 180 s"),
    "S208": ("anh:SCH", "toan/tren-xuong", "隊形を壊しました → 戦闘経過図 (Nga 1907); V26 cách < 180 s"),
    "S225": ("anh:RETR", "trung/chech", "レトヴィザンが突進 → ảnh レトヴィザン; lấp khoảng 16,5 s không hình thật"),
    "S253": ("clip:V27", "toan/thap", "逃げ切りの時計が止まる → hàng thiết giáp chạy ra xa (V27 lần 2); V34 cách < 180 s"),
    "S297": ("anh:GHILL", "toan-xa/cao", "なぜ逃げ切れなかったのか → 旅順港 nhìn từ 黄金山; V24 lần 3"),
    "S300": ("anh:SUNS", "dac-ta/ngang", "届かなかった一日 → 根拠地の夕景; V16 cách < 180 s"),
    "S302": ("anh:MIKT", "can/thap", "距離が縮まりました → 三笠 12インチ砲塔; lấp khoảng 17,9 s không hình thật"),
}


def main():
    s = MD.read_text(encoding="utf-8")
    dem = 0
    for cid, (nguon, cogoc, _) in SUA.items():
        m = re.search(rf"^\| {cid} \|([^\n]*)$", s, re.M)
        if not m:
            sys.exit(f"không thấy dòng {cid}")
        cot = [x.strip() for x in m.group(0).strip().strip("|").split("|")]
        kieu, ten = nguon.split(":")
        if kieu == "anh":
            hinh = ("Cận đặc tả: " if cogoc.startswith("dac-ta") else "") + "Ảnh tư liệu: " + ANH[ten]["mo_ta"]
            chu = "—"
        else:
            hinh = "Clip AI: " + CLIP[ten]["mo_ta"]
            chu = NHAN_AI
        moi = [cot[0], cot[1], nguon, cogoc, hinh, chu, cot[6]]
        s = s.replace(m.group(0), "| " + " | ".join(moi) + " |", 1)
        dem += 1
    MD.write_text(s, encoding="utf-8", newline="\n")
    print(f"sửa {dem} dòng trong {MD.name}")


if __name__ == "__main__":
    main()
