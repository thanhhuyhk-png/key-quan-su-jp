# -*- coding: utf-8 -*-
"""
moc-cau-ja.py — Dựng moc-cau.json (mốc thời gian từng KÝ TỰ của từng câu) cho tiếng Nhật từ bản chép lời STT.
Dùng khi mốc từng chữ của TTS không đáng tin (ElevenLabs eleven_v4 mất mốc ở câu cuối) hoặc sau khi nối giọng.

Cách làm: chuẩn hoá lời và STT như so-loi-ja.py, so từng ký tự bằng difflib, ký tự khớp lấy giờ STT thật,
ký tự lệch (STT nghe nhầm đồng âm) nội suy giữa hai mốc khớp liền kề. Dấu câu nhận giờ ký tự liền sau.

Dùng:
  python -I -X utf8 rieng/tools/moc-cau-ja.py --loi <loi-tts.txt (mỗi dòng một câu)> --words <x.words.json> --out <moc-cau.json> [--het <giây>]
In: số câu, số ký tự, tỉ lệ ký tự khớp giờ thật, và kiểm đơn điệu (mốc không lùi).
"""
import argparse, importlib.util, json, re, sys
from difflib import SequenceMatcher
from pathlib import Path

spec = importlib.util.spec_from_file_location("sl", Path(__file__).with_name("so-loi-ja.py"))
sl = importlib.util.module_from_spec(spec); spec.loader.exec_module(sl)
RUN = sl.RUN


def chuan_hoa_theo_ky_tu(dong):
    """Trả (chuỗi chuẩn hoá, chỉ số ký tự gốc của từng ký tự chuẩn hoá)."""
    s, goc = "", []
    i = 0
    nfkc = dong
    while i < len(nfkc):
        m = RUN.match(nfkc, i)
        if m:
            n = sl.chuan_hoa(m.group())
            s += n; goc += [i] * len(n); i = m.end()
        else:
            n = sl.chuan_hoa(nfkc[i])
            s += n; goc += [i] * len(n); i += 1
    return s, goc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--loi", required=True); ap.add_argument("--words", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--het", type=float)
    a = ap.parse_args()
    dong = [x for x in Path(a.loi).read_text(encoding="utf-8").rstrip("\n").split("\n")]
    env = json.load(open(a.words, encoding="utf-8"))
    ws = [w for w in env["words"] if w.get("text", "").strip()]
    # STT: mỗi từ trải đều giờ lên các ký tự chuẩn hoá của nó
    S, T = "", []
    for w in ws:
        n = sl.chuan_hoa(w["text"])
        if not n:
            continue
        t0, t1 = w["start_ms"] / 1000, w["end_ms"] / 1000
        for k, ch in enumerate(n):
            S += ch; T.append(t0 + (t1 - t0) * k / len(n))
    # lời: ghép các dòng, nhớ (dòng, ký tự gốc)
    L, vt = "", []
    for di, d in enumerate(dong):
        n, goc = chuan_hoa_theo_ky_tu(d)
        L += n; vt += [(di, g) for g in goc]
    sm = SequenceMatcher(None, L, S, autojunk=False)
    tl = [None] * len(L); khop = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                tl[i1 + k] = T[j1 + k]
            khop += i2 - i1
        elif tag == "replace" and j2 > j1:
            for k in range(i2 - i1):
                tl[i1 + k] = T[j1 + min(j2 - j1 - 1, int(k * (j2 - j1) / (i2 - i1)))]
    # nội suy chỗ trống (xoá hoặc không có giờ) giữa hai mốc thật
    prev = None
    i = 0
    while i < len(tl):
        if tl[i] is not None:
            prev = tl[i]; i += 1; continue
        j = i
        while j < len(tl) and tl[j] is None:
            j += 1
        t_a = prev if prev is not None else 0.0
        t_b = tl[j] if j < len(tl) else (T[-1] if T else t_a)
        for k in range(i, j):
            tl[k] = t_a + (t_b - t_a) * (k - i + 1) / (j - i + 1)
        i = j
    # gán về ký tự gốc: ký tự chuẩn hoá đầu tiên của ký tự gốc; dấu câu lấy giờ ký tự gốc liền sau
    cau = []
    for di, d in enumerate(dong):
        gio = [None] * len(d)
        for (dj, g), t in zip(vt, tl):
            if dj == di and gio[g] is None:
                gio[g] = t
        nxt = None
        for k in range(len(d) - 1, -1, -1):
            if gio[k] is None:
                gio[k] = nxt
            else:
                nxt = gio[k]
        cau.append(gio)
    # lấp ô còn None (câu cuối toàn dấu câu) bằng giờ ô trước; ép không lùi
    last = 0.0
    for g in cau:
        for k in range(len(g)):
            if g[k] is None:
                g[k] = last
            if g[k] < last:
                g[k] = last
            g[k] = round(g[k], 3); last = g[k]
    het = a.het or env.get("audio_duration_ms", 0) / 1000
    json.dump({"cau": cau, "het": round(het, 2), "lang": {}}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False)
    so_ky_tu = sum(len(g) for g in cau)
    print(f"{len(cau)} câu, {so_ky_tu} ký tự, khớp giờ thật {khop}/{len(L)} ({100*khop/len(L):.1f} %), het {het:.2f}s")
    xau = [k + 1 for k in range(len(cau) - 1) if cau[k + 1][0] < cau[k][-1]]
    print("Câu có mốc lùi:", xau[:10] if xau else "không")


if __name__ == "__main__":
    main()
