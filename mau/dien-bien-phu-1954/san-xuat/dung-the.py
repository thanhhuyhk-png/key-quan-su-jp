"""Lô L1: dựng 64 thẻ chữ, số của tập 1 (khối template/cards) theo phan-canh.json.

Mỗi thẻ: cấu hình SHOT ở THE bên dưới; thời lượng = đúng số khung của cảnh (24 fps); mốc "@N" / "@N:k" = lúc đọc
chữ k của câu N (mốc thật từ moc-cau.json), đổi sang giây tính từ đầu cảnh; ghi nguồn = cột ghi_nguon của cảnh.
Ra trang template/cards/dbp1-<mã>.html và video <output>/261101-dien-bien-phu-1954/hinh/the/<mã>.mp4.

python -I -X utf8 dung-the.py [--stills] [--render] [MÃ ...]
"""
import json, re, subprocess, sys
from pathlib import Path

GOC = Path(__file__).resolve().parent
TPL = GOC.parents[2] / "template"
sys.path.insert(0, str(GOC))
from demo import cat_demo, nhom_cua  # noqa: E402
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
DUNG_TRANG = ["node", str(REPO_GOC / "tools/kit/dung-trang.mjs")]  # dựng trang HTML thành mp4/mov/ảnh
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")
RA = OUT / "261101-dien-bien-phu-1954/hinh/the"
FPS = 24
PC = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))
MOC = json.loads((GOC / "moc-cau.json").read_text(encoding="utf-8"))
CANH = {c["id"]: c for c in PC["canh"]}
DO, KEM = "#c93b2b", "#efe6d2"
THE_SANG = ("so-lieu", "lich", "dong-thoi-gian", "hai-cot")

NT1 = "Một: ta không đưa được pháo lớn tới."
NT2 = "Hai: ta không nuôi nổi một lực lượng lớn đánh lâu ở xa hậu phương."
THE = {
    "MO03": dict(type="so-lieu", tag="9/4/1954", kicker="CẦU HÀNG KHÔNG", title="HÀNG TIẾP TẾ THẢ XUỐNG LÒNG CHẢO",
                 items=[dict(value=195, from_=0.3, dur=1.4, unit="TẤN", label="máy bay Pháp thả xuống ngày 9/4/1954")]),
    "MO05": dict(type="hook", y=520, lines=[dict(text="6 TẤN", at=0.05, size=280, shake=12, flash=0.3),
                                         dict(text="PHÍA PHÁP THU VỀ ĐƯỢC · 9/4/1954", at=0.45, size=46, color=DO, spacing=8)]),
    "MO10": dict(type="may-chu", kicker="TRƯỚC TRẬN ĐÁNH", title="BỘ CHỈ HUY PHÁP TIN HAI ĐIỀU",
                 blocks=[dict(text=NT1, size=56, y=420, start=0.2, deadline="@T3-0.25", cps=[14, 26]),
                         dict(text=NT2, size=56, y=560, maxW=1560, start="@9", deadline=-0.15, cps=[14, 32])]),
    "MO14": dict(type="may-chu", kicker="LỜI HỨA · THEO TTXVN", title="TRUNG TÁ PI-RỐT",
                 blocks=[dict(text="Không để khẩu pháo nào của đối phương bắn quá 3 phát mà không bị tiêu diệt.", size=60, y=470, maxW=1560,
                              start=0.1, deadline="@T4-0.6", cps=[16, 30], highlight="3 phát")]),
    "MO18": dict(type="may-chu", kicker="CÂU HỎI CỦA TẬP PHIM", title="ĐIỆN BIÊN PHỦ",
                 blocks=[dict(text="Vì sao Bộ chỉ huy Pháp chọn Điện Biên Phủ,", size=58, y=460, maxW=1640, start=0.15, deadline="@15:7", cps=[14, 30]),
                         dict(text="rồi thua ở chính nơi đó?", size=58, y=560, start="@15:8", deadline="@T5-1.6", cps=[12, 24], highlight="thua ở chính nơi đó?")],
                 cite="56 ngày đêm · 13/3 – 7/5/1954", citeGap=0.4),
    "MO20": dict(type="hai-cot", cols=[dict(title="PHÍA PHÁP TIN / GHI", sub="CUỐN SỔ THỨ NHẤT", from_=0.2),
                                       dict(title="QUÂN VÀ DÂN TA LÀM", sub="CUỐN SỔ THỨ HAI", from_=0.6, mau="ta")]),
    "MO22": dict(type="may-chu", kicker="LÝ DO CHỌN VÀ HAI NIỀM TIN", title="QUAY LẠI CHỐNG CHÍNH NGƯỜI ĐẶT RA",
                 blocks=[dict(text="Đường trời: tiếp tế bằng máy bay.", size=52, y=400, start=0.1, deadline=1.7, cps=[16, 30], highlight="Đường trời:"),
                         dict(text="Một: ta không đưa được pháo lớn tới.", size=52, y=500, gap=0.15, deadline=3.3, cps=[16, 30], highlight="Một:"),
                         dict(text="Hai: ta không nuôi nổi một lực lượng lớn đánh lâu.", size=52, y=600, maxW=1600, gap=0.15, deadline="@T7-0.4", cps=[16, 30], highlight="Hai:")]),
    "MO26": dict(type="hai-cot", cols=[dict(title="PHÍA PHÁP TIN / GHI", sub="CUỐN SỔ THỨ NHẤT", from_=0.0, lines=[
                     dict(text="Đường trời, cầu hàng không", at=0.4), dict(text="Hai niềm tin", at=0.7), dict(text="Lời hứa ba phát", at=1.0)]),
                 dict(title="QUÂN VÀ DÂN TA LÀM", sub="CUỐN SỔ THỨ HAI", from_=0.0, mau="ta", lines=[
                     dict(text="Kéo pháo qua núi", at="@22:14"), dict(text="Đánh chắc, tiến chắc", at="@22:17"), dict(text="Hào, cao xạ, dân công", at="@22:20")])]),
    "MO30": dict(type="hook", y=500, lines=[dict(text="ĐIỆN BIÊN PHỦ", at=0.4, size=170, shake=6, flash=0.25, spacing=10),
                                         dict(text="1954", at=1.1, size=90, color=DO, shake=0, flash=0, spacing=24)], fadeOut=0.5, toi=0.72),
    "C1-01": dict(type="chuong", number=1, title="LÒNG CHẢO", hit=0.1),
    "C1-03": dict(type="may-chu", source="Nguồn: Báo Nhân Dân", kicker="HỒ SƠ · 1953", title="KẾ HOẠCH NA-VA",
                  blocks=[dict(text="Điện Biên Phủ", size=100, y=500, start=0.2, deadline=1.3, cps=[10, 20], strike=True),
                          dict(text="lúc đầu nằm ngoài kế hoạch", size=46, y=620, color=DO, gap=0.5, deadline="@T9-0.4", cps=[12, 26])]),
    "C1-04": dict(type="lich", tag="1953", kicker="KẾ HOẠCH NA-VA", title="HỘI ĐỒNG QUỐC PHÒNG PHÁP", month=7, year=1953, day=24, circleAt=0.9,
                  note="24/7/1953", noteSub="kế hoạch được thông qua"),
    "C1-05": dict(type="dong-thoi-gian", tag="1953 – 1955", kicker="KẾ HOẠCH NA-VA", title="KHOẢNG 18 THÁNG",
                  axis=dict(frm=[1, 7, 1953], to=[31, 1, 1955], ticks=[dict(d=[24, 7, 1953], label="7/1953"), dict(d=[1, 1, 1954], label="1954"), dict(d=[1, 1, 1955], label="1955")]),
                  lanes=[dict(name="DỰ TÍNH", start=[24, 7, 1953], end=[24, 1, 1955], open=True, dates="khoảng 18 tháng", note="“kết thúc chiến tranh trong danh dự”", activeFrom=0.5, grow=1.8)]),
    "C1-11": dict(type="dong-thoi-gian", tag="20/11/1953", kicker="HÀNH QUÂN CÁT-TO (HẢI LY)", title="6 TIỂU ĐOÀN DÙ",
                  axis=dict(frm=[19, 11, 1953], to=[26, 11, 1953], ticks=[dict(d=[20, 11, 1953], label="20/11"), dict(d=[22, 11, 1953], label="22/11"), dict(d=[24, 11, 1953], label="24/11")]),
                  lanes=[dict(name="NGÀY ĐẦU", start=[20, 11, 1953], end=[21, 11, 1953], dates="20/11", note="3 tiểu đoàn dù", activeFrom=0.3, grow=0.6),
                         dict(name="TIẾP THEO", start=[21, 11, 1953], end=[23, 11, 1953], open=True, dates="những ngày kế tiếp", note="3 tiểu đoàn dù", activeFrom="@33:7", grow=1.0)]),
    "C1-16": dict(type="may-chu", kicker="THEO BÁO NHÂN DÂN", title="TƯỚNG CÔ-NHI GỌI ĐIỆN BIÊN PHỦ LÀ",
                  blocks=[dict(text="“nhọt hút độc”", size=110, y=560, start="@38:13", cps=[10, 16], highlight=True)],
                  cite="— tướng Cô-nhi · theo Báo Nhân Dân", citeGap=0.8),
    "C1-18": dict(type="lich", tag="1953", kicker="BỘ CHỈ HUY PHÁP", title="NA-VA RA CHỈ THỊ", month=12, year=1953, day=3, circleAt=0.7,
                  note="3/12/1953", noteSub="chấp nhận giao chiến ở Điện Biên Phủ"),
    "C1-23": dict(type="may-chu", kicker="LỜI KỂ · ĐẠI ĐOÀN 304", title="ÔNG TRẦN QUỐC HANH",
                  blocks=[dict(text="“Ở Phú Thọ hơn tháng trời trong rừng nứa, bộ đội không được tiếp xúc với dân, không được tập luyện vì sợ lộ.”",
                               size=54, y=380, maxW=1600, start=0.3, deadline="@V2-0.4", cps=[12, 34], highlight="vì sợ lộ.”")],
                  cite="— cán sự chính trị Tiểu đoàn 418, Đại đoàn 304 · theo Báo QĐND", citeGap=0.3),
    "C2-01": dict(type="chuong", number=2, title="CON NHÍM", hit=0.1),
    "C2-07": dict(type="so-lieu", tag="13/3/1954", kicker="TẬP ĐOÀN CỨ ĐIỂM", title="QUÂN PHÁP LÚC MỞ MÀN",
                  items=[dict(value=11800, from_=0.3, dur=1.4, prefix="KHOẢNG", unit="QUÂN", label="trong lòng chảo Điện Biên Phủ")]),
    "C2-09": dict(type="so-lieu", tag="1954", kicker="TẬP ĐOÀN CỨ ĐIỂM", title="HỎA LỰC PHÍA PHÁP",
                  items=[dict(value=24, from_=0.2, dur=0.8, unit="PHÁO 105 MM"), dict(value=4, from_=0.6, dur=0.6, unit="PHÁO 155 MM"),
                         dict(value=10, from_=1.0, dur=0.7, unit="XE TĂNG")]),
    "C2-11": dict(type="may-chu", kicker="TRUNG TÁ PI-RỐT TIN", title="CHỈ HUY PHÁO BINH TẬP ĐOÀN CỨ ĐIỂM",
                  blocks=[dict(text="Ta chỉ đưa được pháo nhỏ và súng cối vào chiến trường.", size=62, y=470, maxW=1600, start=0.2,
                               deadline="@V6-0.4", cps=[12, 26], highlight="pháo nhỏ và súng cối")],
                  cite="— theo TTXVN", citeGap=0.3),
    "C2-20": dict(type="hai-cot", cols=[dict(title="24/12/1953", sub="NA-VA NÓI VỚI BINH LÍNH", from_=0.1, lines=[
                      dict(text="Trận đánh chỉ có thể diễn biến thuận lợi cho phía Pháp.", at="@67:21", size=44)])]),
    "C2-21": dict(type="hai-cot", cols=[dict(title="24/12/1953", sub="NA-VA NÓI VỚI BINH LÍNH", from_=-1, lines=[
                      dict(text="Trận đánh chỉ có thể diễn biến thuận lợi cho phía Pháp.", at=-1, size=44)]),
                  dict(title="1/1/1954", sub="THƯ RIÊNG", from_="@68:4", mau="ta", lines=[dict(text="về khả năng thành công…", at="@68:20", size=44, font="serif")])]),
    "C2-22": dict(type="van-kien", kicker="NA-VA · THƯ RIÊNG 1/1/1954", title="VỀ KHẢ NĂNG THÀNH CÔNG", y=460,
                  blocks=[dict(text="“Trước đây hai tuần, tôi đánh giá khả năng đó là 100% (…)”", font="serif", size=70, from_="@69:6", perWord=0.18,
                               marks=[dict(phrase="100% (…)”", type="highlight", at="@69:20", dur=0.5)])],
                  cite="— theo Báo Nhân Dân (trích tài liệu Pháp)", citeAt=1.0),
    "C2-23": dict(type="van-kien", kicker="NA-VA · THƯ RIÊNG 1/1/1954", title="VỀ KHẢ NĂNG THÀNH CÔNG", y=460,
                  blocks=[dict(text="“Trước đây hai tuần, tôi đánh giá khả năng đó là 100% (…)”", font="serif", size=70, from_=-2, perWord=0, dimAt="@70:10",
                               marks=[dict(phrase="100% (…)”", type="strike", at="@70:12", dur=0.5)]),
                          dict(text="không dám khẳng định như thế nữa", size=46, from_="@70:13", perWord=0.06, color=DO)],
                  cite="— theo Báo Nhân Dân (trích tài liệu Pháp)", citeAt=-1),
    "C2-24": dict(type="hai-cot", source="Nguồn: Báo Nhân Dân", cols=[dict(title="24/12/1953", sub="NÓI VỚI BINH LÍNH", from_=-1, dimAt="@72", lines=[dict(text="chỉ có thể thuận lợi", at=-1, size=44)]),
                                        dict(title="1/1/1954", sub="THƯ RIÊNG", from_=-1, mau="ta", lines=[dict(text="không dám khẳng định nữa", at=-1, size=44, font="serif")])]),
    "C3-01": dict(type="chuong", number=3, title="ĐỔI CÁCH ĐÁNH", hit=0.1),
    "C3-05": dict(type="so-lieu", tag="1/1954", kicker="LỜI KỂ ÔNG PHẠM ĐỨC CƯ", title="KÉO MỘT KHẨU PHÁO",
                  items=[dict(value=2.4, dec=1, from_=0.2, dur=0.9, unit="TẤN", label="mỗi khẩu pháo"),
                         dict(value=100, prefix="80 –", from_="@80:5", dur=1.0, unit="NGƯỜI KÉO", label="mỗi khẩu")]),
    "C3-14": dict(type="so-lieu", tag="1954", kicker="PHÁO BINH CỦA TA", title="HƠN 200 KHẨU PHÁO VÀ CỐI",
                  items=[dict(value=200, prefix="HƠN", from_=0.2, dur=1.0, unit="KHẨU", label="pháo và cối các loại", size=130),
                         dict(value=24, from_="@89:4", dur=0.6, unit="LỰU PHÁO", label="105 mm", size=130),
                         dict(value=16, from_="@89:9", dur=0.6, unit="CỐI", label="120 mm", size=130),
                         dict(value=24, from_="@89:14", dur=0.6, unit="CAO XẠ", label="37 mm", size=130)]),
    "C3-18": dict(type="hook", source="Nguồn: Báo Nhân Dân", y=520, lines=[dict(text="25/1/1954", at=0.05, size=120, shake=0, flash=0, spacing=6),
                                          dict(text="GIỜ BẮN ẤY KHÔNG ĐẾN", at=0.5, size=64, color=DO, shake=8, flash=0.15, spacing=8)]),
    "C3-20": dict(type="van-kien", kicker="LỜI DẶN", title="CHỦ TỊCH HỒ CHÍ MINH GIAO NHIỆM VỤ CHO ĐẠI TƯỚNG VÕ NGUYÊN GIÁP", blocks=[]),
    "C3-21": dict(type="van-kien", kicker="LỜI DẶN", title="CHỦ TỊCH HỒ CHÍ MINH GIAO NHIỆM VỤ CHO ĐẠI TƯỚNG VÕ NGUYÊN GIÁP", y=430,
                  blocks=[dict(text="“Trận này rất quan trọng, phải đánh cho thắng. Chắc thắng mới đánh, không chắc thắng, không đánh”",
                               font="serif", size=60, from_=0.15, perWord=0.11, maxW=1620)],
                  cite="— lời Chủ tịch Hồ Chí Minh · theo Báo Nhân Dân", citeAt=2.0),
    "C3-22": dict(type="van-kien", kicker="26/1/1954 · ĐẠI TƯỚNG VÕ NGUYÊN GIÁP, ĐẢNG ỦY VÀ BỘ CHỈ HUY CHIẾN DỊCH", title="PHƯƠNG CHÂM TÁC CHIẾN", y=470,
                  blocks=[dict(text="Đánh nhanh, thắng nhanh", size=96, from_=0.3, perWord=0.1, marks=[dict(phrase="Đánh nhanh, thắng nhanh", type="strike", at="@95:3", dur=0.5)]),
                          dict(text="Đánh chắc, tiến chắc", size=96, from_="@95:5", perWord=0.12, color=DO)]),
    "C3-27": dict(type="may-chu", kicker="LỆNH KÉO PHÁO RA · ĐÊM 26/1/1954", title="ÔNG NGUYỄN QUANG THUẬN NHỚ LẠI",
                  blocks=[dict(text="“như sét đánh ngang tai”", size=96, y=520, start="@101:15", deadline="@W7-0.4", cps=[8, 18], highlight="ngang tai”")],
                  cite="— Đại đội 815 · theo Báo QĐND", citeGap=0.3),
    "C3-33": dict(type="lich", tag="1954", kicker="KÉO PHÁO RA", title="XONG VIỆC KÉO PHÁO RA", month=2, year=1954, day=5, circleAt=0.8,
                  note="5/2/1954", noteSub="mồng 3 Tết Giáp Ngọ"),
    "C3-38": dict(type="hook", y=540, lines=[dict(text="Quyết định ấy đúng hay sai?", at=0.1, size=96, shake=0, flash=0, weight=600, spacing=1)]),
    "C4-01": dict(type="chuong", number=4, title="PHÁO NỔ, HÀO SIẾT", kicker="13/3/1954 · 17 GIỜ 5 PHÚT", hit=0.1),
    "C4-04": dict(type="hook", y=520, lines=[dict(text="3 PHÁT", at=0.05, size=280, shake=16, flash=0.3)]),
    "C4-14": dict(type="may-chu", kicker="TRƯỚC TRẬN · THEO BÁO QĐND", title="TRUNG TÁ PI-RỐT",
                  blocks=[dict(text="“Tôi có thừa số pháo cần thiết.”", size=90, y=520, start="@125:14", deadline="@X3-0.5", cps=[8, 18], highlight="thừa số pháo")],
                  cite="— theo Báo QĐND", citeGap=0.3),
    "C4-17": dict(type="hook", y=500, lines=[dict(text="3 PHÁT", at=0.0, size=280, shake=0, flash=0),
                                          dict(text="KHÔNG GIỮ ĐƯỢC", at="@128:4", size=72, color=DO, shake=18, flash=0.5, spacing=10)]),
    "C4-19": dict(type="van-kien", kicker="BỘ CHỈ HUY PHÁP TIN", title="NIỀM TIN THỨ NHẤT", y=470,
                  blocks=[dict(text="Ta không đưa được pháo lớn tới.", size=72, from_=0.0, perWord=0.03, marks=[dict(phrase="Ta không đưa được pháo lớn tới.", type="strike", at=0.4)]),
                          dict(text="SAI", size=150, from_=0.8, perWord=0, color=DO)]),
    "C4-23": dict(type="so-lieu", tag="SAU 13/3/1954", kicker="TẬP ĐOÀN CỨ ĐIỂM", title="QUÂN ĐỘI VIỄN CHINH PHÁP TĂNG VIỆN",
                  items=[dict(value=4000, prefix="KHOẢNG", from_=0.3, dur=1.0, unit="QUÂN", label="tăng viện sau 13/3/1954"),
                         dict(value=16200, from_=1.4, dur=1.0, unit="QUÂN", label="lúc đông nhất")]),
    "C4-28": dict(type="dong-thoi-gian", tag="13/3 – 7/5/1954", kicker="CHIẾN DỊCH ĐIỆN BIÊN PHỦ", title="BA ĐỢT TIẾN CÔNG",
                  axis=dict(frm=[10, 3, 1954], to=[10, 5, 1954], ticks=[dict(d=[13, 3, 1954], label="13/3"), dict(d=[30, 3, 1954], label="30/3"), dict(d=[1, 5, 1954], label="1/5"), dict(d=[7, 5, 1954], label="7/5")]),
                  lanes=[dict(name="ĐỢT 1", start=[13, 3, 1954], end=[17, 3, 1954], dates="13–17/3", activeFrom=0.2, activeTo=0.9),
                         dict(name="ĐỢT 2", start=[30, 3, 1954], end=[30, 4, 1954], dates="30/3 – cuối tháng 4", note="điểm cao phía Đông · vây lấn · khống chế sân bay", activeFrom=0.9, activeTo=99, grow=1.4),
                         dict(name="ĐỢT 3", start=[1, 5, 1954], end=[7, 5, 1954], dates="1–7/5", activeFrom=99)]),
    "C5-01": dict(type="chuong", number=5, title="LẤY ĐI BẦU TRỜI", hit=0.1),
    "C5-03": dict(type="hook", y=520, lines=[dict(text="6 TẤN", at=0.0, size=280, shake=10, flash=0.25),
                                          dict(text="TRONG 195 TẤN THẢ XUỐNG · 9/4/1954", at=0.3, size=46, color=DO, spacing=8)]),
    "C5-04": dict(type="so-lieu", tag="4/1954", kicker="TẬP ĐOÀN CỨ ĐIỂM", title="ĐẠN DƯỢC MỖI NGÀY",
                  items=[dict(value=200, prefix="CẦN KHOẢNG", from_=0.2, dur=1.0, unit="TẤN", label="đạn dược phải bổ sung mỗi ngày"),
                         dict(value=100, prefix="CAO NHẤT KHOẢNG", from_="@155:4", dur=1.0, unit="TẤN", label="phía Pháp thu được")]),
    "C5-08": dict(type="may-chu", kicker="LỜI KỂ · TRUNG ĐOÀN CAO XẠ 367", title="ÔNG TRẦN XUÂN KÌNH",
                  blocks=[dict(text="“giữ yên bầu trời”", size=110, y=520, start="@157:31", deadline="@Y2-0.4", cps=[8, 16], highlight="bầu trời”")],
                  cite="— theo Báo Nhân Dân", citeGap=0.3),
    "C5-15": dict(type="hook", y=470, lines=[dict(text="Làm sao đào sâu vào chân một cứ điểm", at=0.1, size=80, shake=0, flash=0, weight=600, spacing=1),
                                          dict(text="mà đối phương không hay biết?", at="@163:8", size=80, shake=0, flash=0, weight=600, spacing=1)]),
    "C5-17": dict(type="may-chu", kicker="ĐỒI A1 · ĐẠI TÁ NGUYỄN BỘI GIONG", title="BA ĐIỀU PHẢI GIẢI QUYẾT",
                  blocks=[dict(text="1. Không để đối phương phát hiện.", size=56, y=400, start=0.1, deadline="@166", cps=[14, 34]),
                          dict(text="2. Đổ đất không lộ cửa hầm, giữ đúng hướng.", size=56, y=500, start="@166", deadline="@167", cps=[14, 34]),
                          dict(text="3. Người đào không bị ngạt.", size=56, y=600, start="@167", deadline="@Y4-0.4", cps=[12, 30], highlight=True)],
                  cite="— theo Báo QĐND", citeGap=0.3),
    "C5-22": dict(type="dong-thoi-gian", tag="13/3 – 7/5/1954", kicker="CHIẾN DỊCH ĐIỆN BIÊN PHỦ", title="BA ĐỢT TIẾN CÔNG",
                  axis=dict(frm=[10, 3, 1954], to=[10, 5, 1954], ticks=[dict(d=[13, 3, 1954], label="13/3"), dict(d=[30, 3, 1954], label="30/3"), dict(d=[1, 5, 1954], label="1/5"), dict(d=[7, 5, 1954], label="7/5")]),
                  lanes=[dict(name="ĐỢT 1", start=[13, 3, 1954], end=[17, 3, 1954], dates="13–17/3", activeFrom=0.1, activeTo=0.3, grow=0.2),
                         dict(name="ĐỢT 2", start=[30, 3, 1954], end=[30, 4, 1954], dates="30/3 – cuối tháng 4", activeFrom=0.2, activeTo=0.6, grow=0.3),
                         dict(name="ĐỢT 3", start=[1, 5, 1954], end=[7, 5, 1954], dates="1–7/5", note="đánh nốt các điểm cao phía Đông", activeFrom=0.6, activeTo=99, grow=0.8)]),
    "C5-26": dict(type="lich", tag="1954", kicker="ĐỒI A1", title="ĐIỂM HỎA KHỐI BỘC PHÁ", month=5, year=1954, day=6, circleAt=0.6,
                  note="20 giờ 30 phút", noteSub="gần 1 tấn bộc phá"),
    "C5-36": dict(type="van-kien", kicker="BỘ CHỈ HUY PHÁP TIN", title="CÒN LẠI NIỀM TIN THỨ HAI", y=430,
                  blocks=[dict(text=NT1 + "  SAI", size=54, from_=0.0, perWord=0, dimAt=0.3, marks=[dict(phrase=NT1, type="strike", at=0.0, dur=0.01)]),
                          dict(text=NT2 + "  ?", size=54, from_=0.3, perWord=0.05, maxW=1550, marks=[dict(phrase="Hai:", type="highlight", at="@184:4")])]),
    "C6-01": dict(type="chuong", number=6, title="HAI LOẠI CON SỐ", hit=0.1),
    "C6-03": dict(type="hai-cot", cols=[dict(title="CON SỐ CỦA TRẬN ĐÁNH", sub="LOẠI THỨ NHẤT", from_=0.1)]),
    "C6-06": dict(type="hai-cot", source="Nguồn: Báo Chính phủ", cols=[dict(title="CON SỐ CỦA TRẬN ĐÁNH", sub="LOẠI THỨ NHẤT", from_=-1, dimAt=0.3, lines=[
                      dict(text="16.200 quân địch bị tiêu diệt và bắt sống", at=-1), dict(text="62 máy bay bị bắn rơi, phá hủy", at=-1)]),
                  dict(title="CON SỐ CỦA SỨC NGƯỜI", sub="LOẠI THỨ HAI", from_=0.2, mau="ta")]),
    "C6-09": dict(type="so-lieu", tag="1954", kicker="QUÂN ĐỘI NHÂN DÂN VIỆT NAM", title="5 ĐẠI ĐOÀN",
                  items=[dict(value=40000, prefix="KHOẢNG", from_=0.2, dur=1.2, unit="QUÂN CHỦ LỰC", label="khoảng 55.000 kể cả tuyến hai")]),
    "C6-14": dict(type="so-lieu", tag="1954", kicker="XE ĐẠP THỒ", title="MỖI XE CHỞ ĐƯỢC",
                  items=[dict(value=100, prefix="80 –", from_=0.0, dur=0.3, unit="KG", label="lúc đầu"),
                         dict(value=300, prefix="200 –", from_=0.4, dur=1.0, unit="KG", label="sau cải tiến (tay ngai)")]),
    "C6-18": dict(type="hai-cot", cols=[dict(title="CON SỐ CỦA TRẬN ĐÁNH", sub="LOẠI THỨ NHẤT", from_=-1, dimAt=-1, lines=[
                      dict(text="16.200 quân địch bị tiêu diệt và bắt sống", at=-1), dict(text="62 máy bay bị bắn rơi, phá hủy", at=-1)]),
                  dict(title="CON SỐ CỦA SỨC NGƯỜI", sub="LOẠI THỨ HAI", from_=-1, mau="ta", lines=[
                      dict(text="hơn 260.000 dân công hỏa tuyến", at=0.1), dict(text="gần 21.000 xe đạp thồ", at=0.5), dict(text="hơn 23.000 tấn gạo", at=0.9)])]),
    "C6-21": dict(type="van-kien", kicker="BỘ CHỈ HUY PHÁP TIN", title="HAI NIỀM TIN SỤP ĐỔ", y=430,
                  blocks=[dict(text=NT1, size=54, from_=0.0, perWord=0.02, marks=[dict(phrase=NT1, type="strike", at=0.3)]),
                          dict(text=NT2, size=54, from_=0.2, perWord=0.02, maxW=1550, marks=[dict(phrase=NT2, type="strike", at="@205:10", dur=0.8)]),
                          dict(text="SAI", size=130, from_="@205:12", perWord=0, color=DO)]),
    "KT-08": dict(type="lich", tag="1954", kicker="THƯ KHEN", title="CỦA CHỦ TỊCH HỒ CHÍ MINH", month=5, year=1954, day=8, circleAt=0.7,
                  note="8/5/1954", noteSub="bộ đội, dân công, thanh niên xung phong, đồng bào Tây Bắc"),
    "KT-10": dict(type="van-kien", kicker="THƯ KHEN · 8/5/1954", title="CỦA CHỦ TỊCH HỒ CHÍ MINH", y=420,
                  blocks=[dict(text="“Thắng lợi tuy lớn nhưng mới là bắt đầu. Chúng ta không nên vì thắng mà kiêu, không nên chủ quan khinh địch.”",
                               font="serif", size=62, maxW=1560, from_=0.15, perWord=0.1,
                               marks=[dict(phrase="mới là bắt đầu.", type="highlight", at=2.6, dur=0.6)])],
                  cite="— thư ngày 8/5/1954 của Chủ tịch Hồ Chí Minh · theo Báo QĐND", citeAt=2.2),
    "KT-17": dict(type="hook", y=520, lines=[dict(text="3 PHÁT", at=0.0, size=280, shake=0, flash=0, to="@216:13")]),
    "KT-23": dict(type="so-lieu", tag="BÁO CÁO 8/2026", kicker="ĐIỆN BIÊN PHỦ HÔM NAY", title="NGHĨA TRANG LIỆT SĨ QUỐC GIA A1",
                  items=[dict(value=645, from_=0.2, dur=1.0, unit="MỘ", label="tổng số"), dict(value=10, from_="@222:12", dur=0.6, unit="MỘ", label="có đủ thông tin"),
                         dict(value=39, from_="@222:20", dur=0.6, unit="MỘ", label="có một phần thông tin")]),
    "KT-25": dict(type="hook", y=480, lines=[dict(text="Theo bạn, quyết định nào trong ba quyết định ấy", at=0.3, size=70, shake=0, flash=0, weight=600, spacing=1),
                                          dict(text="là quan trọng nhất?", at=0.6, size=70, shake=0, flash=0, weight=600, spacing=1)], fadeOut=1.0),
    "KT-22": dict(type="hook", source="Nguồn: Báo Văn hóa, TTXVN · báo cáo 8/2026", y=440, glows=[], lines=[dict(text="NGHĨA TRANG LIỆT SĨ QUỐC GIA A1", at=0.2, size=64, shake=0, flash=0, spacing=6, color="#d6c9a3"),
                                                dict(text="645 ngôi mộ", at=0.9, y=640, size=110, shake=0, flash=0, weight=600, spacing=2)]),
    "KT-24": dict(type="hook", source="Nguồn: Báo Văn hóa, TTXVN · báo cáo 8/2026", y=500, lines=[dict(text="596", at=0.1, size=220, shake=0, flash=0, spacing=4),
                                          dict(text="ngôi mộ chưa có thông tin", at=0.7, size=56, shake=0, flash=0, weight=500, spacing=2, color="#d6c9a3")]),
}


# v2 (02/11/2026, bảng màu quân sự): thẻ tối không đứng trên nền phẳng mà phủ trong suốt lên hình động (làm tối, mờ, đẩy máy chậm).
# Nền: ("demo", mã cảnh 3D Demo, khung lệch) | ("canh", mã cảnh tập 1 đã dựng; chỉ cảnh không có chữ trong hình). Thiếu khung thì giữ khung cuối (dưới lớp mờ khó thấy).
NEN_SAU = {
    "MO05": ("demo", "TN1", 0), "MO10": ("demo", "TN2", 0), "MO14": ("demo", "BD6", 0), "MO18": ("demo", "MM2", 0),
    "MO22": ("demo", "BD8", 0), "MO30": ("demo", "BD9", 0), "C1-01": ("demo", "MM5", 0), "C1-03": ("canh", "C1-02"),
    "C1-16": ("demo", "TN1", 0),
    # cả phim (02/11/2026): mọi thẻ tối trừ lời lãnh tụ (C3-20, C3-21, KT-10) và đoạn tưởng niệm cuối phim (KT-22, KT-24, KT-25)
    "C1-23": ("canh", "C1-21"), "C2-01": ("demo", "TN2", 0), "C2-11": ("canh", "MO12"), "C2-22": ("canh", "C2-10"),
    "C2-23": ("canh", "C2-27"), "C3-01": ("demo", "MM1", 0), "C3-18": ("demo", "MM3", 0), "C3-22": ("canh", "C3-17"),
    "C3-27": ("canh", "C3-28"), "C3-38": ("canh", "C3-37b"), "C4-01": ("demo", "BD6", 0), "C4-04": ("canh", "C4-02"),
    "C4-14": ("canh", "MO13"), "C4-17": ("demo", "BD3", 0), "C4-19": ("canh", "C3-35"), "C5-01": ("demo", "MB1", 0),
    "C5-03": ("canh", "C4-43"), "C5-08": ("canh", "C5-07"), "C5-15": ("demo", "BD9", 0), "C5-17": ("demo", "BD11", 0),
    "C5-36": ("canh", "C1-24"), "C6-01": ("canh", "C6-17"), "C6-21": ("canh", "C6-16"), "KT-17": ("canh", "C3-10"),
}
NGUON_CANH = {"map3d": "ban-do", "vnmap": "ban-do", "3d": "3d", "3d-moi": "3d", "anh": "tu-lieu", "karmen": "tu-lieu"}


def ghep_nen(ma, lop, ra, n):
    """Nền động (làm tối, mờ, đẩy máy chậm) + lớp thẻ trong suốt → ra, đúng n khung."""
    loai, *thong = NEN_SAU[ma]
    if loai == "demo":
        vao, f = cat_demo(thong[0], thong[1], min(n, nhom_cua(thong[0])[2] - nhom_cua(thong[0])[1] - thong[1]))
    else:
        c = CANH[thong[0]]
        vao, f = ["-i", str(RA.parent / NGUON_CANH[c["kieu"]] / f"{thong[0]}.mp4")], f"fps={FPS},scale=1920:1080,setsar=1"
    nen = (f"[0:v]{f},tpad=stop_mode=clone:stop={n},trim=end_frame={n},setpts=PTS-STARTPTS,"
           f"eq=saturation=0.6:contrast=1.05,gblur=sigma=4,"
           f"zoompan=z='1+0.05*on/{n}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps={FPS}[b]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *vao, "-i", str(lop), "-filter_complex",
                    f"{nen};[1:v]format=rgba[o];[b][o]overlay=0:0:format=auto,format=yuv420p[v]", "-map", "[v]", "-frames:v", str(n),
                    "-r", str(FPS), "-c:v", "libx264", "-crf", "16", "-preset", "medium", str(ra)], check=True)


def khung(c):
    return round(c["t0"] * FPS), round(c["t1"] * FPS)


def giai(v, t0):
    """'@N' / '@N:k' → giây kể từ đầu cảnh; đệ quy qua dict, list; khoá from_ → from."""
    m = re.fullmatch(r"@([A-Z][A-Z0-9])([+-][\d.]+)?", v) if isinstance(v, str) else None
    if m and m[1] in MOC["lang"]:  # '@T4-0.5': cuối khoảng lặng T4 (lúc lời nói tiếp) cộng/trừ giây
        return round(MOC["lang"][m[1]][1] + float(m[2] or 0) - t0, 3)
    if isinstance(v, str) and v.startswith("@"):
        n, _, k = v[1:].partition(":")
        return round(MOC["cau"][int(n) - 1][int(k or 0)] - t0, 3)
    if isinstance(v, dict):
        return {("from" if k == "from_" else "frm" if k == "frm" else k): giai(x, t0) for k, x in v.items()}
    if isinstance(v, list):
        return [giai(x, t0) for x in v]
    return v


def cau_hinh(ma):
    c = CANH[ma]
    f0, f1 = khung(c)
    s = giai(THE[ma], f0 / FPS)
    if "axis" in s:
        s["axis"]["from"] = s["axis"].pop("frm")
    s.update(duration=round((f1 - f0) / FPS, 4), seed=sum(map(ord, ma)))
    s.setdefault("source", c["ghi_nguon"])
    # v3 (user chọn 02/11/2026): thẻ sáng trên vải ô-liu quân phục; thẻ tối giữ nền vải sẫm quan-su
    s["mau"] = "xanh-qd" if s["type"] in THE_SANG else "quan-su"
    if ma in NEN_SAU:
        s["nen"] = "trong"
    return s, f1 - f0


def main():
    ma_the = [c["id"] for c in PC["canh"] if c["kieu"] in ("the", "can-tim")]  # can-tim: phương án thay bằng thẻ
    thieu = sorted(set(ma_the) - set(THE)) + sorted(set(THE) - set(ma_the))
    if thieu:
        sys.exit(f"THE lệch bảng phân cảnh: {thieu}")
    chon = [a for a in sys.argv[1:] if not a.startswith("--")] or ma_the
    thu = TPL / "cards" / "shots" / "dbp1"
    thu.mkdir(exist_ok=True)
    for ma in chon:
        s, _ = cau_hinh(ma)
        (thu / f"{ma}.js").write_text(f"// Sinh bởi tap/EP001-dien-bien-phu-1954/san-xuat/dung-the.py, đừng sửa tay.\nwindow.SHOT = {json.dumps(s, ensure_ascii=False)};\n", encoding="utf-8")
    subprocess.run([sys.executable, "-I", str(TPL / "tools" / "build_shots.py"), "cards"], check=True, capture_output=True)
    RA.mkdir(parents=True, exist_ok=True)
    for ma in chon:
        s, n = cau_hinh(ma)
        trang = TPL / "cards" / f"dbp1-{ma}.html"
        if "--stills" in sys.argv:
            d = s["duration"]
            subprocess.run([*DUNG_TRANG, str(trang), "--stills", f"{min(1.0, d / 2):.2f},{d * 0.6:.2f},{d - 0.1:.2f}",
                            "--out-dir", str(RA.parent / "story" / "the" / ma)], check=True, capture_output=True)
        if "--render" in sys.argv:
            ra = (RA.parent / "3d" if CANH[ma]["kieu"] == "can-tim" else RA) / f"{ma}.mp4"
            if ma in NEN_SAU:
                lop = RA.parent / "the-lop" / f"{ma}.mov"
                lop.parent.mkdir(exist_ok=True)
                subprocess.run([*DUNG_TRANG, str(trang), "--out", str(lop), "--fps", str(FPS), "--transparent", "--force"],
                               check=True, capture_output=True)
                ghep_nen(ma, lop, ra, n)
            else:
                subprocess.run([*DUNG_TRANG, str(trang), "--out", str(ra), "--fps", str(FPS), "--force"], check=True, capture_output=True)
            so = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries", "stream=nb_read_packets",
                                 "-of", "csv=p=0", str(ra)], capture_output=True, text=True).stdout.strip().rstrip(",")
            print(f"{ma}: {so} khung (cần {n}){'' if int(so) == n else '  LỆCH'}", flush=True)
    print(f"{len(chon)} thẻ xong")


if __name__ == "__main__":
    main()
