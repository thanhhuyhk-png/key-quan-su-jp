# -*- coding: utf-8 -*-
"""
so-loi-ja.py — So lời chuẩn với bản chép lời (STT) cho TIẾNG NHẬT.
Bản riêng thay cho `kit.py so-loi` (kit tách từ theo dấu cách nên hỏng với tiếng Nhật).

Cách làm: chuẩn hoá cả hai bên (NFKC, bỏ dấu câu và khoảng trắng, katakana → hiragana,
số kanji → số Ả Rập, ヶ→か) rồi so từng ký tự bằng difflib. In tỉ lệ khớp tổng,
tỉ lệ theo từng khối 600 ký tự và các chỗ lệch để người nghe soát.

Dùng:
  python -I -X utf8 rieng/tools/so-loi-ja.py <loi-chuan.txt> <stt.txt> [--min 0.97] [--chi-tiet 40]
Mã thoát 1 nếu tỉ lệ < --min.
Lưu ý: STT hay nghe nhầm đồng âm hiếm (長征→調整). Chỗ lệch tập trung ở tên riêng, thuật ngữ
nghĩa là chưa chắc giọng sai: nghe lại đúng chỗ đó.
"""
import argparse, re, sys, unicodedata
from difflib import SequenceMatcher

KANJI_DIGIT = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
               "六": 6, "七": 7, "八": 8, "九": 9}
KANJI_UNIT = {"十": 10, "百": 100, "千": 1000}
BIG = {"万": 10000}
RUN = re.compile(r"[〇零一二三四五六七八九十百千万]+")


def kanji_to_int(s):
    # Kiểu "positional" (二〇〇五) hoặc kiểu đơn vị (二十一, 千九百五).
    if all(c in KANJI_DIGIT for c in s) and len(s) > 1:
        return int("".join(str(KANJI_DIGIT[c]) for c in s))
    total = 0; section = 0; num = None
    for c in s:
        if c in KANJI_DIGIT:
            num = KANJI_DIGIT[c]
        elif c in KANJI_UNIT:
            section += (1 if num is None else num) * KANJI_UNIT[c]; num = None
        elif c in BIG:
            section += (num or 0); total += (section or 1) * BIG[c]; section = 0; num = None
    return total + section + (num or 0)


def chuan_hoa(t):
    t = unicodedata.normalize("NFKC", t).casefold()   # T字 = t字 (STT hay viết thường)
    t = RUN.sub(lambda m: str(kanji_to_int(m.group())), t)
    out = []
    for ch in t:
        o = ord(ch)
        if 0x30A1 <= o <= 0x30F6:      # katakana -> hiragana
            ch = chr(o - 0x60)
        cat = unicodedata.category(ch)
        if cat[0] in "PZSC" or ch.isspace():
            continue
        out.append({"ゖ": "か", "ゕ": "か"}.get(ch, ch))   # ヶ, ヵ -> か
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("loi"); ap.add_argument("stt")
    ap.add_argument("--min", type=float, default=0.97)
    ap.add_argument("--chi-tiet", type=int, default=40, help="số chỗ lệch tối đa in ra")
    a = ap.parse_args()
    L = chuan_hoa(open(a.loi, encoding="utf-8").read())
    S = chuan_hoa(open(a.stt, encoding="utf-8").read())
    sm = SequenceMatcher(None, L, S, autojunk=False)
    r = sm.ratio()
    print(f"Ký tự lời chuẩn: {len(L)} · STT: {len(S)} · khớp tổng: {r:.3f}")
    # theo khối 600 ký tự của lời chuẩn
    khop = [0] * (len(L) // 600 + 1); tong = [0] * len(khop)
    for i in range(len(L)):
        tong[i // 600] += 1
    for blk in sm.get_matching_blocks():
        for i in range(blk.a, blk.a + blk.size):
            khop[i // 600] += 1
    print("Khối 600 ký tự (khớp %): " + " ".join(f"{100*k//max(t,1)}" for k, t in zip(khop, tong)))
    print("Chỗ lệch (lời chuẩn → STT), 4 ký tự ngữ cảnh:")
    n = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        n += 1
        if n <= a.chi_tiet:
            print(f"  [{i1}] …{L[max(0,i1-4):i1]}【{L[i1:i2]}】{L[i2:i2+4]}…  →  【{S[j1:j2]}】")
    print(f"Tổng {n} chỗ lệch.")
    ok = r >= a.min
    print(("ĐẠT" if ok else f"CHƯA ĐẠT (< {a.min})") + f" — ngưỡng {a.min}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
