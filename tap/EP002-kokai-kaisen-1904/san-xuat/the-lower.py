# -*- coding: utf-8 -*-
"""Thẻ lower-third trong suốt (PNG) cho showcase. python the-lower.py <out.png> <kind>"""
import sys
from PIL import Image, ImageDraw, ImageFont
W, H = 1920, 1080
F = "d:/GOHA/GohaKit-JP/template/fonts/NotoSerifJP-Bold.ttf"
KEM, DO, DOC, KEMP = (240, 232, 216), (204, 34, 34), (224, 108, 92), (180, 190, 200)


def fnt(s): return ImageFont.truetype(F, s)


def main():
    out, kind = sys.argv[1], sys.argv[2]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    y0 = 760
    d.rectangle([0, y0, W, y0 + 190], fill=(10, 16, 24, 205))
    d.rectangle([0, y0, W, y0 + 6], fill=DO)
    if kind == "knot":
        d.text((W/2, y0+70), "15ノット  対  11ノット", font=fnt(84), fill=KEM, anchor="mm")
        d.text((W/2, y0+148), "四ノットの速度優位 — T字を可能にした差", font=fnt(38), fill=KEMP, anchor="mm")
    else:
        d.text((W/2, y0+66), "ロシア艦隊 21隻沈没  ⇔  日本 失ったのは水雷艇3隻のみ", font=fnt(56), fill=KEM, anchor="mm")
        d.text((W/2, y0+148), "出典: 海軍軍令部『日本海海戦』", font=fnt(34), fill=KEMP, anchor="mm")
    img.save(out)
    print("ok", out)


main()
