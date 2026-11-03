"""Cắt Shorts từ bản v4 đã duyệt: hình và bản master giữ nguyên, chỉ cắt tại khoảng lặng giữa câu.

Mỗi Shorts là danh sách các đoạn khối phụ đề (số khối trong Final/EP001-dien-bien-phu-1954.vi.srt).
- Hình: cắt thẳng từ v4, đặt vào khuôn template/shorts-doc.html (dọc 1080×1920 hoặc vuông 1080×1080).
- Tiếng: cắt bản master v4; mỗi đoạn kéo dài thêm NOI giây vào khoảng lặng rồi crossfade với đoạn sau,
  nên tổng độ dài và khớp hình tiếng không đổi. Cuối cùng chuẩn về −14 LUFS, chặn đỉnh.
- Phụ đề cháy chữ lấy nguyên câu từ .vi.srt; câu có số đọc bằng chữ thì ghi tay bản chữ số ở CHU_SO
  (đối chiếu sổ số liệu), không chuyển tự động.
- Thẻ kết KET giây: giữ khung ở giữa câu cuối (khung cuối đoạn có thể đã chuyển cảnh tối), tối đi, chữ «xem trọn phim».

Chạy: python -I -X utf8 tap/EP001-dien-bien-phu-1954/san-xuat/shorts.py S1 [--kieu doc|vuong|ca-hai]
Ra:   <output>/261103-dbp-shorts/<S>-<kiểu>.mp4
"""
import sys
import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlencode
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

GOC = Path(__file__).resolve().parent
REPO = GOC.parents[2]
FINAL = REPO / "tap/EP001-dien-bien-phu-1954/Final"
V4 = FINAL / "EP001-dien-bien-phu-1954.mp4"
SRT = FINAL / "EP001-dien-bien-phu-1954.vi.srt"
MASTER = OUT / "261102-dbp-v3/am/mix-v4-master.wav"
GIONG = MASTER.with_name("mix-v4-stem-giong.wav")
RA = OUT / "261103-dbp-shorts"
CHROME = str(duong("chrome"))
FPS, NOI, KET, LUFS = 24, 0.2, 1.8, -14.0

SHORTS = {
    "S1": dict(h1="KÉO PHÁO VÀO", h2="SAO LẠI KÉO RA?",
               doan=[[129], [104], [110, 111], [118, 119], [122, 124], [126, 128], [130, 131], [133, 134], [146]]),
    "S2": dict(h1="LỜI HỨA 3 PHÁT", h2="GIỮ ĐƯỢC KHÔNG?",
               doan=[[12, 15], [147, 149], [152, 154], [161, 167]]),
    "S3": dict(h1="THẢ XUỐNG 195 TẤN", h2="VỀ TAY BAO NHIÊU?",
               doan=[[1, 5], [197, 200], [223, 224]]),
    "S4": dict(h1="PHÁO TRÔI XUỐNG DỐC", h2="AI ĐÃ CHẶN LẠI?",
               doan=[[104], [135, 139]]),
    "S5": dict(h1="MỘT CHIẾC XE ĐẠP", h2="CHỞ ĐƯỢC BAO NHIÊU?",
               doan=[[251, 259]]),
}
# Câu có số đọc bằng chữ: bản chữ số cho phụ đề, chép tay từ lời đọc v4 (giữ nguyên chữ, chỉ đổi cách viết số).
CHU_SO = {
    104: "Mỗi khẩu pháo nặng 2,4 tấn cần 80 đến 100 người kéo.",
    111: "Gần 10 đêm như thế.",
    118: "Đến ngày 25/1, phần lớn số pháo ấy đã vào trận địa, chờ giờ bắn.",
    122: "Ngày 26/1,",
    129: "Ngay đêm 26/1, những khẩu pháo vừa kéo vào nhận lệnh kéo ra.",
    1: "Ngày 9/4/1954,",
    2: "máy bay Pháp thả xuống lòng chảo Điện Biên Phủ 195 tấn hàng tiếp tế.",
    3: "Phía Pháp thu về được 6 tấn.",
    4: "6 tấn.",
    13: "hứa không để khẩu pháo nào của đối phương bắn quá 3 phát mà không bị tiêu diệt,",
    135: "Ngày 1/2, ở Dốc Chuối, đường hẹp,",
    137: "Khẩu pháo cao xạ nặng hơn 2 tấn trôi xuống dốc.",
    147: "Câu trả lời đến vào chiều 13/3.",
    148: "17 giờ 05 phút chiều 13/3,",
    163: "Theo TTXVN, quanh đồi Him Lam, Pi-rốt cho bắn khoảng 6.000 viên đại bác.",
    165: "Lời hứa 3 phát không giữ được.",
    197: "Tập đoàn cứ điểm cần bổ sung khoảng 200 tấn đạn dược mỗi ngày.",
    198: "Nhưng theo TTXVN, cao nhất phía Pháp chỉ thu được khoảng 100 tấn.",
    224: "khoảng 1/3 số dù rơi vào trận địa ta.",
    252: "Lúc đầu, mỗi xe thồ chỉ chở được 80 đến 100 kg.",
    253: "Rồi dân công buộc thêm một đoạn tre dài chừng 1 mét vào ghi-đông để lái,",
    255: "Sau cải tiến, mỗi xe chở được 200 đến 300 kg.",
    256: "Chiếc xe của ông Ma Văn Thắng, dân công Phú Thọ, có chuyến chở hơn 3 tạ hàng.",
    257: "Cả chiến dịch có hơn 260.000 dân công hỏa tuyến,",
    258: "gần 21.000 xe đạp thồ, hơn 23.000 tấn gạo.",
}
KIEU = {  # cỡ khung, y của khung phim, y phụ đề, lề phải phụ đề, cỡ chữ
    "doc": dict(w=1080, h=1920, y=592, sub_y=1236, sub_r=120, co=56),
    "vuong": dict(w=1080, h=1080, y=236, sub_y=856, sub_r=60, co=44),
}


def doc_srt() -> dict[int, tuple[float, float, str]]:
    def giay(x: str) -> float:
        h, m, s = x.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s.replace(",", "."))
    khoi = {}
    for b in SRT.read_text(encoding="utf-8").strip().split("\n\n"):
        dong = b.splitlines()
        a, c = dong[1].split(" --> ")
        khoi[int(dong[0])] = (giay(a), giay(c), " ".join(dong[2:]))
    return khoi


def khoang_lang(t0: float, t1: float) -> list[tuple[float, float]]:
    """Các khoảng lặng ≥ 0,12 s của stem giọng trong [t0, t1] (cửa sổ 10 ms dưới −45 dBFS)."""
    import numpy as np
    import soundfile as sf
    with sf.SoundFile(str(GIONG)) as f:
        sr = f.samplerate
        f.seek(int(max(0, t0) * sr))
        x = f.read(int((t1 - max(0, t0)) * sr), always_2d=True).mean(axis=1)
    w = sr // 100
    rms = np.sqrt((x[: len(x) // w * w].reshape(-1, w) ** 2).mean(axis=1) + 1e-12)
    lang = 20 * np.log10(rms) < -45
    ra, i = [], 0
    while i < len(lang):
        if lang[i]:
            j = i
            while j < len(lang) and lang[j]:
                j += 1
            if j - i >= 12:
                ra.append((max(0, t0) + i / 100, max(0, t0) + j / 100))
            i = j
        else:
            i += 1
    return ra


def cat_doan(khoi: dict, doan: list[list[int]]) -> list[dict]:
    """Mỗi đoạn [a, b] trong v4, cắt trong khoảng lặng thật của giọng quanh ranh câu.

    a: trước tiếng đầu tiên tối đa 0,35 s. b: sau tiếng cuối 0,06–0,1 s, và b + NOI vẫn còn trong khoảng lặng.
    """
    ra = []
    for d in doan:
        dau, cuoi = d[0], d[-1]
        s0, e1 = khoi[dau][0], khoi[cuoi][1]
        truoc = [q for q in khoang_lang(s0 - 1.2, s0 + 0.4) if q[0] <= s0 + 0.3]
        if not truoc:
            raise SystemExit(f"khối {dau}: không thấy khoảng lặng trước câu")
        l0, l1 = truoc[-1]
        a = max(l0, l1 - 0.35)
        sau = [q for q in khoang_lang(e1 - 0.8, e1 + 1.5) if q[1] - q[0] >= NOI + 0.09 and q[1] >= e1 - 0.3]
        if not sau:
            raise SystemExit(f"khối {cuoi}: không thấy khoảng lặng ≥ {NOI + 0.09:.2f} s sau câu")
        m0, m1 = sau[0]
        b = max(m0 + 0.06, min(m0 + 0.1, m1 - NOI - 0.03))
        ra.append(dict(khoi=list(range(dau, cuoi + 1)), a=round(a, 3), b=round(b, 3), sau=round(m1, 3)))
    return ra


def ve_nen(p: dict, kieu: str, tam: Path) -> None:
    for f in ("Oswald-VF.ttf", "BeVietnamPro-ExtraBold.ttf", "BeVietnamPro-SemiBold.ttf"):
        shutil.copy(REPO / "template/fonts" / f, tam)
    shutil.copy(REPO / "template/shorts-doc.html", tam)
    k = KIEU[kieu]
    for ten, them in (("nen", {}), ("ket", {"ket": "1"})):
        q = {"h1": p["h1"], "h2": p["h2"], **({"kieu": "vuong"} if kieu == "vuong" else {}), **them}
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                        f"--window-size={k['w']},{k['h']}", "--virtual-time-budget=8000", f"--screenshot={tam / (ten + '.png')}",
                        (tam / "shorts-doc.html").as_uri() + "?" + urlencode(q)], check=True, capture_output=True)


def ass(khoi: dict, ds: list[dict], kieu: str) -> str:
    k = KIEU[kieu]

    def tg(t: float) -> str:
        cs = round(t * 100)
        return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"
    dong, t = [], 0.0
    for d in ds:
        for n in d["khoi"]:
            s, e, chu = khoi[n]
            chu = CHU_SO.get(n, chu).replace("\n", " ")
            dong.append(f"Dialogue: 0,{tg(t + max(0, s - d['a']))},{tg(t + min(e, d['b']) - d['a'])},Phu,,0,0,0,,{chu}")
        t += d["b"] - d["a"]
    return "\n".join([
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {k['w']}", f"PlayResY: {k['h']}", "WrapStyle: 0", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Phu,Be Vietnam Pro SemiBold,{k['co']},&H00FFFFFF,&H00FFFFFF,&H00101010,&H00000000,0,0,0,0,100,100,0,0,1,3,0,7,60,{k['sub_r']},{k['sub_y']},1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text", *dong, ""])


def tieng(ds: list[dict], gain_db: float | None) -> list[str]:
    """Lệnh ffmpeg dựng tiếng (đầu vào + filter), dùng chung cho lượt đo và lượt xuất."""
    vao, loc = [], []
    for i, d in enumerate(ds):
        cuoi = i == len(ds) - 1
        dai = d["b"] - d["a"] + (min(KET, d["sau"] - d["b"] - 0.1) if cuoi else NOI)
        vao += ["-ss", f"{d['a']:.3f}", "-t", f"{dai:.3f}", "-i", str(MASTER)]
    nhan = "[0:a]"
    for i in range(1, len(ds)):
        loc.append(f"{nhan}[{i}:a]acrossfade=d={NOI}:c1=qsin:c2=qsin[x{i}]")
        nhan = f"[x{i}]"
    tong = sum(d["b"] - d["a"] for d in ds) + KET
    loc.append(f"{nhan}afade=t=out:st={tong - KET + 0.2:.3f}:d={KET - 0.4:.3f},apad,atrim=0:{tong:.3f}"
               + (f",volume={gain_db:.2f}dB,alimiter=limit=0.75:level=false" if gain_db is not None else "") + "[a]")
    return vao + ["-filter_complex", ";".join(loc), "-map", "[a]"]


def do_lufs(f: Path) -> float:
    o = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1])


def dung(ma: str, kieu: str) -> Path:
    p, khoi = SHORTS[ma], doc_srt()
    ds = cat_doan(khoi, p["doan"])
    k = KIEU[kieu]
    RA.mkdir(parents=True, exist_ok=True)
    ra = RA / f"{ma}-{kieu}.mp4"
    with tempfile.TemporaryDirectory() as tam:
        tam = Path(tam)
        ve_nen(p, kieu, tam)
        (tam / "fonts").mkdir()
        shutil.copy(REPO / "template/fonts/BeVietnamPro-SemiBold.ttf", tam / "fonts")
        (tam / "s.ass").write_text(ass(khoi, ds, kieu), encoding="utf-8")
        # Lượt 1: dựng tiếng chưa chỉnh để đo độ to.
        lenh_a = tieng(ds, None)
        subprocess.run(["ffmpeg", "-v", "error", "-y", *lenh_a, str(tam / "thu.wav")], check=True)
        gain = LUFS - do_lufs(tam / "thu.wav")
        # Lượt 2: hình + tiếng.
        vao, loc = ["-loop", "1", "-framerate", str(FPS), "-i", "nen.png", "-loop", "1", "-framerate", str(FPS), "-i", "ket.png"], []
        for d in ds:
            vao += ["-ss", f"{d['a']:.3f}", "-t", f"{d['b'] - d['a']:.3f}", "-i", str(V4)]
        dau_cau = khoi[ds[-1]["khoi"][-1]][0]  # mốc kết .srt nối liền câu sau nên dùng điểm cắt thật b
        vao += ["-ss", f"{(dau_cau + ds[-1]['b']) / 2:.3f}", "-t", "0.2", "-i", str(V4)]
        n = len(ds)
        for i in range(n):
            loc.append(f"[{i + 2}:v]scale=1080:608,setsar=1,fps={FPS}[v{i}]")
        tong = sum(d["b"] - d["a"] for d in ds)
        loc.append(f"[{n + 2}:v]scale=1080:608,setsar=1,trim=end_frame=1,loop=loop={round(KET * FPS) - 1}:size=1,"
                   f"setpts=N/{FPS}/TB,fps={FPS},eq=brightness=-0.22[vk]")
        loc.append("".join(f"[v{i}]" for i in range(n)) + f"[vk]concat=n={n + 1}:v=1:a=0[vc]")
        loc.append(f"[0:v][vc]overlay=0:{k['y']}:eof_action=pass,subtitles=s.ass:fontsdir=fonts[b]")
        duoi = k["y"] + 608  # chỉ phủ phần chữ dưới khung phim; ô #khung của ket.png là nền đen
        loc.append(f"[1:v]crop=1080:{k['h'] - duoi}:0:{duoi}[kc]")
        loc.append(f"[b][kc]overlay=0:{duoi}:enable='gte(t,{tong:.3f})',format=yuv420p[v]")
        lenh_a = tieng(ds, gain)
        # Đầu vào tiếng đánh số sau các đầu vào hình: đổi nhãn [i:a] cho đúng.
        fa = lenh_a[lenh_a.index("-filter_complex") + 1]
        fa = re.sub(r"\[(\d+):a\]", lambda m: f"[{int(m.group(1)) + n + 3}:a]", fa)
        vao_a = lenh_a[:lenh_a.index("-filter_complex")]
        subprocess.run(["ffmpeg", "-v", "error", "-y", *vao, *vao_a, "-filter_complex", ";".join(loc) + ";" + fa,
                        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-r", str(FPS),
                        "-c:a", "aac_mf", "-b:a", "256k", "-t", f"{tong + KET:.3f}", "-movflags", "+faststart", ra.name],
                       check=True, cwd=tam)
        shutil.move(str(tam / ra.name), ra)
    (RA / f"{ma}-doan.json").write_text(json.dumps(ds, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{ra}: {tong + KET:.2f} s, {n} đoạn, chỉnh tiếng {gain:+.2f} dB")
    return ra


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("ma", choices=sorted(SHORTS))
    ap.add_argument("--kieu", choices=["doc", "vuong", "ca-hai"], default="ca-hai")
    o = ap.parse_args()
    for kieu in (["doc", "vuong"] if o.kieu == "ca-hai" else [o.kieu]):
        dung(o.ma, kieu)


if __name__ == "__main__":
    main()
