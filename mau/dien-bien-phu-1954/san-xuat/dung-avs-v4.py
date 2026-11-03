"""Dựng dự án Goha AVS (manifest v2) cho bản v4 đã duyệt, để xem lại, đánh dấu và sửa trong AVS Studio.

Lớp hình: 259 cảnh (intro + 258 cảnh của phan-canh.json), mỗi cảnh cắt từ chính file v4 cuối cùng,
nên hình trong AVS giống hệt bản đã duyệt (có dấu kênh). Mốc khung tính đúng như ghep-hinh.py ghép.
Lớp tiếng: bản master v4 tách từ chính file Final. Stem giọng, nhạc, tiếng động đã xoá khi dọn rác 03/11/2026
(user chốt «chỉ giữ Final»). Video được liên kết cứng (cùng ổ D) vào thư mục dự án, không tốn thêm dung lượng.

Chạy: python -I -X utf8 tap/EP001-dien-bien-phu-1954/san-xuat/dung-avs-v4.py
Mở:   "<goha_avs>\\start-app.bat" "<output>/EP001-avs"
"""
import sys
import json
import os
import shutil
import subprocess
from pathlib import Path
REPO_GOC = next(p for p in Path(__file__).resolve().parents if (p / "cau-hinh.mau.toml").exists())
sys.path.insert(0, str(REPO_GOC / "tools"))
from cau_hinh import duong  # noqa: E402
OUT = duong("output")

GOC = Path(__file__).resolve().parent
REPO = GOC.parents[2]
V4 = REPO / "tap/EP001-dien-bien-phu-1954/Final/EP001-dien-bien-phu-1954.mp4"
DU_AN = OUT / "EP001-avs"
FPS = 24
INTRO_KHUNG = 165  # intro.py


def lien_ket(nguon: Path, ten: str) -> str:
    """Liên kết cứng nguồn vào media/ của dự án (chép nếu không liên kết được); trả đường dẫn tương đối."""
    dich = DU_AN / "media" / ten
    if not dich.exists():
        try:
            os.link(nguon, dich)
        except OSError:
            shutil.copy2(nguon, dich)
    return f"media/{ten}"


def so_khung(p: Path) -> int:
    o = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                        "stream=nb_read_packets", "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return int(o.stdout.strip().rstrip(","))


def main() -> None:
    (DU_AN / "media").mkdir(parents=True, exist_ok=True)
    (DU_AN / "captions").mkdir(exist_ok=True)
    pc = json.loads((GOC / "phan-canh.json").read_text(encoding="utf-8"))
    tong = so_khung(V4)
    src = lien_ket(V4, V4.name)

    canh, t = [("INTRO", INTRO_KHUNG)], INTRO_KHUNG
    for c in pc["canh"]:
        canh.append((c["id"], round(c["t1"] * FPS) - round(c["t0"] * FPS)))
    clips = []
    for id_, n in canh:
        a = sum(x[1] for x in canh[:len(clips)])
        clips.append({"id": id_, "kind": "veo", "src": src, "t0_f": a, "t1_f": a + n, "in_f": a, "out_f": a + n})
    cuoi = clips[-1]["t1_f"]
    if cuoi != tong:
        raise SystemExit(f"LỆCH: phân cảnh {cuoi} khung, file v4 {tong} khung")

    lop = [{"id": "v0", "kind": "video", "name": f"Cảnh v4 ({len(clips)})", "transitions": [], "clips": clips}]
    wav = DU_AN / "media" / "EP001-master.wav"
    if not wav.exists():  # tách tiếng master từ chính file Final, 48 kHz
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(V4), "-vn", "-ac", "2", "-ar", "48000",
                        "-c:a", "pcm_s16le", str(wav)], check=True)
    lop.append({"id": "a_mix", "kind": "audio", "name": "Bản trộn v4 master (−14 LUFS, tách từ Final)",
                "clips": [{"id": "a_mix_0", "kind": "audio", "src": f"media/{wav.name}",
                           "t0_f": 0, "t1_f": tong, "in_f": 0, "out_f": tong, "vol": 1}]})
    # Lớp tách lại bằng Demucs htdemucs từ master (gần đúng; stem gốc đã mất 03/11/2026), để TẮT như dự án cũ
    for id_, ten, f in (("a_vo", "Lời đọc (tách Demucs)", "EP001-tach-giong.wav"),
                        ("a_nhac", "Nhạc nền (tách Demucs)", "EP001-tach-nhac.wav"),
                        ("a_sfx", "Tiếng động (tách Demucs)", "EP001-tach-tieng.wav")):
        if (DU_AN / "media" / f).exists():
            lop.append({"id": id_, "kind": "audio", "name": ten, "muted": True, **({"voice": True} if id_ == "a_vo" else {}),
                        "clips": [{"id": f"{id_}_0", "kind": "audio", "src": f"media/{f}",
                                   "t0_f": 0, "t1_f": tong, "in_f": 0, "out_f": tong, "vol": 1}]})

    # Chữ đã nằm sẵn trong hình: .ass chỉ là bảng kiểu tối thiểu AVS cần, không có dòng nào hiện.
    (DU_AN / "captions/dbp.ass").write_text("\r\n".join([
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "", "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,Be Vietnam Pro,34,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,2,1,2,230,230,86,1",
        "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        "Dialogue: 0,0:00:00.00,0:00:00.01,Default,,0,0,0,,khuon", ""]), encoding="utf-8")
    fonts = DU_AN / "fonts"
    if not fonts.exists():
        shutil.copytree(REPO / "template/fonts", fonts)

    ra = DU_AN / "edit_manifest.v2.json"
    rev = json.loads(ra.read_text(encoding="utf-8"))["rev"] + 1 if ra.exists() else 1
    m = {"schema_version": "2.0.0", "rev": rev, "actor": "agent",
         "meta": {"fps": FPS, "w": 1920, "h": 1080, "duration_f": tong, "ass": "captions/dbp.ass", "fontsdir": "fonts",
                  "ep": "EP001", "markers": []},
         "tracks": lop}
    ra.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    thieu = [c["src"] for tr in lop for c in tr["clips"] if not (DU_AN / c["src"]).exists()]
    if thieu:
        raise SystemExit(f"THIẾU {len(thieu)} file nguồn: {thieu}")
    print(f"ra {ra}: {len(lop)} lớp, {len(clips)} cảnh, {tong} khung ({tong / FPS:.2f} s), rev {rev}")


if __name__ == "__main__":
    main()
