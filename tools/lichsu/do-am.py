"""Máy đo lớp âm của bản trộn (lời, nhạc, tiếng động) và kết luận ĐẠT / CẢNH BÁO / CHẶN.

Dùng (python -I -X utf8 tools/lichsu/do-am.py ...):
  do-am.py <thư mục> [--ten EP001]          tự tìm <ten>-stem-{giong,nhac,tieng}.wav (đầu ra hau-ky-am.py)
                                            hoặc <ten>-tach-{...}.wav (Demucs); master: <ten>-master.wav
  do-am.py --giong g.wav --nhac n.wav [--tieng t.wav] [--master m.wav]
  --mau "{ten}-{k}.wav"                     mẫu tên riêng khi thư mục dùng tên khác
  --chuong 0,117,245 | phan-canh.json       mốc đầu mỗi chương (giây, theo trục âm thanh), hoặc phan-canh.json
                                            (lấy các cảnh nguồn «the:chuong/N»); không có thì chia đều mỗi --do-dai-chuong giây
  --lui 6.875                               giây intro cộng vào mốc của phan-canh.json (mặc định: thời lượng âm − "het")
  --loai-tru 600-650,900-930                đoạn cao trào cố ý, không tính vào lời − nhạc và nhạc ở khe
  --json ra.json  --do-thi ra.png           ghi số đo và chuỗi theo giây; vẽ lớp âm (cần matplotlib)
  --tat-db 30                               nhạc «tắt hẳn» khi thấp hơn mức lời nói bấy nhiêu dB
  --do-dai-chuong 180                       độ dài mỗi chương khi chia đều (mốc giả định: chỉ CẢNH BÁO, không CHẶN)

Mã thoát: 0 không có CHẶN · 1 có CHẶN · 2 sai đầu vào (sửa lệnh, không sửa trộn) · 3 thiếu stem nên không kết luận được
(chỉ có bản trộn).

Mọi mức đo theo giây (RMS cửa sổ 1 s, dBFS). Ngưỡng «có lời», «nhạc tắt» tính tương đối theo mức giọng đang nói,
nên đo đúng cả trên stem chưa master (chưa tăng tới −14 LUFS). Âm được hạ về 11025 Hz trước khi đo, nên RMS không tính
dải trên khoảng 5,5 kHz (đủ cho số tương đối giữa các lớp; không so thẳng với ebur128). Định nghĩa và lý do ngưỡng: NGUONG ở dưới và
plans/reports/p4-261103-2113-may-do-am.md.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 11025
DAT, CANH_BAO, CHAN, KHONG_DO = "ĐẠT", "CẢNH BÁO", "CHẶN", "KHÔNG ĐO ĐƯỢC"
THU_TU = {DAT: 0, KHONG_DO: 1, CANH_BAO: 1, CHAN: 2}

# Ngưỡng, căn cứ số đo cùng một máy đo trên CLD ĐBP / B-52 (mẫu user ưng), Demo EP001 (đã duyệt), EP001 bản dài (user chê nhạc to).
NGUONG = {
    "loi_nhac_dB": (15.0, 12.0),          # trung vị lời − nhạc khi có lời: ĐẠT ≥ 15, CHẶN < 12 (EP001 9; Demo 16,2; CLD 19)
    "loi_nhac_p10_dB": (10.0, None),      # 10 % giây tệ nhất: chỉ cảnh báo (Demo đã duyệt có 1,7 do cao trào cố ý)
    "nhac_khe_dB": (6.0, 2.0),            # nhạc ở khe giữa lời − nhạc lúc có lời: ĐẠT ≥ 6, CHẶN < 2 (EP001 −0,1; CLD 4,4; Demo 11,6)
    "nhac_chay_pct": (98.0, None),        # % giây nhạc còn chạy: chỉ cảnh báo (CLD 97 vẫn được ưng)
    "nghi_xa_nhat_s": (90.0, 180.0),      # đoạn nhạc căng liền dài nhất: ĐẠT ≤ 90 s (luật «không căng liền quá 60–90 s»), CHẶN > 180 s
    "tieng_so_loi_dB": (-30.0, None),     # tiếng động − lời: chỉ cảnh báo
    "nhan_moi_phut": (0.5, 8.0),          # cú nhấn mạnh/phút: ngoài [0,5; 8] là cảnh báo (CLD 1,0; Demo 6,6; EP001 12,4)
    "lra": (2.5, 6.0),                    # LRA (LU): ngoài [2,5; 6] là cảnh báo, không chặn
}
TAT_DB = 30.0       # nhạc «tắt hẳn» khi thấp hơn mức giọng đang nói ≥ 30 dB (tương đương −45 dB của đo cũ)
TAT_TOI_THIEU = 3   # giây
KHE_TOI_THIEU = 2   # giây không lời mới là «khe»
KHE_TOI_DA_THIEU = 10  # dưới số giây khe này thì không đủ mẫu để kết luận
DAY_TUONG_DOI = 10.0   # «lắng» = thấp hơn trung vị 60 s quanh nó ≥ 10 dB, kéo ≥ 2 s
CANG_DB = 15.0      # nhạc «căng» khi cao hơn mức lời nói − 15 dB (nhạc thấp hơn lời ≥ 15 dB là nền, không cần lắng)
LECH_TOI_DA = 2     # giây lệch tối đa giữa stem giọng và nhạc
HO_CANG = 2         # giây: chỗ nhạc tụt dưới ngưỡng «căng» ngắn hơn mức này không ngắt chuỗi căng
NHAN_DB = 7.0       # cú nhấn mạnh: tiếng động cao hơn mức lời − 7 dB (tương đương −22 dB của đo cũ)


def loi(thong_bao: str) -> None:
    """Sai đầu vào: in lý do ra stderr, thoát mã 2 (khác mã 1 của CHẶN)."""
    print(thong_bao, file=sys.stderr)
    raise SystemExit(2)


def chay_ffmpeg(args: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["ffmpeg", "-v", "error", "-nostats", *args], capture_output=True, check=False)
    except FileNotFoundError:
        loi("không thấy ffmpeg trong PATH")


def doc_wav(tep: Path, sr: int = SR) -> np.ndarray:
    p = chay_ffmpeg(["-i", str(tep), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"])
    if p.returncode != 0 or not p.stdout:
        loi(f"ffmpeg không đọc được {tep}: {p.stderr.decode('utf-8', 'replace')[:200]}")
    return np.frombuffer(p.stdout, dtype=np.float32)


def rms_db(a: np.ndarray, sr: int = SR, cua_so: float = 1.0) -> np.ndarray:
    k = max(1, int(sr * cua_so))
    n = len(a) // k
    return 20 * np.log10(np.sqrt((a[:n * k].astype(np.float64).reshape(n, k) ** 2).mean(1)) + 1e-9)


def doan(mask: np.ndarray, toi_thieu: int) -> list[tuple[int, int]]:
    """Các đoạn True liền nhau dài ≥ toi_thieu: [(bắt đầu, độ dài)]."""
    out, cur, bd = [], 0, 0
    for i, b in enumerate(list(mask) + [False]):
        if b:
            if cur == 0:
                bd = i
            cur += 1
        else:
            if cur >= toi_thieu:
                out.append((bd, cur))
            cur = 0
    return out


def lap_ho(mask: np.ndarray, toi_da: int) -> np.ndarray:
    """Lấp các chỗ hở False ngắn ≤ toi_da giây nằm giữa hai đoạn True (độ trễ: nhạc dao động quanh ngưỡng không ngắt chuỗi)."""
    out = mask.copy()
    for b, c in doan(~mask, 1):
        if c <= toi_da and b > 0 and b + c < len(mask):
            out[b:b + c] = True
    return out


def lra_tu(tep_vao: list[Path]) -> dict:
    """I, LRA, đỉnh thật bằng ebur128. Nhiều tệp thì cộng thẳng (amix không chuẩn hoá): LRA không đổi theo gain chung."""
    if len(tep_vao) == 1:
        loc = ["-i", str(tep_vao[0]), "-af", "ebur128=peak=true"]
    else:
        loc = [x for t in tep_vao for x in ("-i", str(t))] + [
            "-filter_complex", f"amix=inputs={len(tep_vao)}:normalize=0:duration=longest,ebur128=peak=true"]
    try:
        p = subprocess.run(["ffmpeg", "-nostats", *loc, "-f", "null", "-"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return {"loi": "không thấy ffmpeg trong PATH"}
    if p.returncode != 0:
        dong = [x for x in p.stderr.splitlines() if x.strip()]
        return {"loi": f"ffmpeg báo lỗi: {dong[-1][:160] if dong else p.returncode}"}
    đuôi = p.stderr[p.stderr.rfind("Summary:"):]
    kq = {}
    for khoa, mau in (("I_LUFS", r"I:\s*(-?[\d.]+) LUFS"), ("LRA_LU", r"LRA:\s*(-?[\d.]+) LU"),
                      ("dinh_that_dBTP", r"Peak:\s*(-?[\d.]+) dBFS")):
        m = re.search(mau, đuôi)
        if m:
            kq[khoa] = float(m.group(1))
    if "LRA_LU" not in kq:
        kq["loi"] = "ffmpeg không in số LRA"
    return kq


def cu_nhan(s50: np.ndarray, nguong: float, gian_cach: float = 0.5, tran: float = 3.0, nhay: float = 10.0) -> list[float]:
    """Mốc (giây) các cú nhấn mạnh: tiếng động vượt `nguong` dB và vọt lên ≥ `nhay` dB so với 0,5 s trước đó (loại nền ồn
    liên tục), tính một lần cho tới khi hạ dưới nguong − tran; hai cú cách nhau ≥ gian_cach giây."""
    out, trong, cuoi = [], False, -1e9
    for i, x in enumerate(s50):
        t = i * 0.05
        if not trong and x > nguong and t - cuoi >= gian_cach and x - s50[max(0, i - 10):i + 1].min() >= nhay:
            out.append(round(t, 2))
            cuoi, trong = t, True
        elif trong and x < nguong - tran:
            trong = False
    return out


def chia_chuong(n: int, moc: list[float] | None, do_dai: float) -> tuple[list[float], bool]:
    """Mốc đầu các chương (giây), và cờ «mốc thật». Không có mốc thì chia đều theo `do_dai`."""
    if moc:
        ms = sorted({0.0, *[float(x) for x in moc if 0 <= x < n]})
        return ms, True
    k = max(1, int(round(n / do_dai)))
    return [i * n / k for i in range(k)], False


def phan_loai(gia_tri, dat, chan, thap_tot=False) -> str:
    """Kết luận 1 chỉ số một chiều. thap_tot: số nhỏ là tốt (ĐẠT khi ≤ dat, CHẶN khi > chan)."""
    if gia_tri is None:
        return KHONG_DO
    if thap_tot:
        if gia_tri <= dat:
            return DAT
        return CHAN if chan is not None and gia_tri > chan else CANH_BAO
    if gia_tri >= dat:
        return DAT
    return CHAN if chan is not None and gia_tri < chan else CANH_BAO


def phan_tich(v: np.ndarray, m: np.ndarray, s: np.ndarray | None, s50: np.ndarray | None = None, *,
              lra: dict | None = None, chuong: list[float] | None = None, do_dai_chuong: float = 180.0,
              loai_tru: list[tuple[float, float]] | None = None, tat_db: float = TAT_DB) -> dict:
    """v, m, s: mức dB theo giây của giọng, nhạc, tiếng động (s có thể None). Trả {"chi_so": [...], "ket_luan", ...}."""
    n = min(len(v), len(m))
    if abs(len(v) - len(m)) > LECH_TOI_DA:
        raise ValueError(f"stem giọng ({len(v)} s) và nhạc ({len(m)} s) lệch nhau quá {LECH_TOI_DA} s: không cùng một bản trộn?")
    if n < 20:
        raise ValueError("âm quá ngắn (dưới 20 giây) để đo")
    v, m = v[:n], m[:n]
    if s is not None:  # tiếng động ngắn hơn thì phần thiếu coi là lặng, không cắt cả phim
        s = np.concatenate([s, np.full(max(0, n - len(s)), -120.0)])[:n]
    if s50 is not None:
        s50 = np.concatenate([s50, np.full(max(0, n * 20 - len(s50)), -120.0)])[:n * 20]
    cong = np.maximum(np.percentile(v, 90) - 20, -60)
    co_loi = v > cong
    if co_loi.sum() < 10:
        raise ValueError("stem giọng gần như không có lời (dưới 10 giây vượt ngưỡng)")
    ref = float(np.median(v[co_loi]))
    dung = np.ones(n, bool)
    for a, b in loai_tru or []:
        dung[int(a):int(np.ceil(b))] = False
    loi_dung = co_loi & dung
    if loi_dung.sum() < 10:
        raise ValueError("--loai-tru phủ gần hết các giây có lời (còn dưới 10 giây): bớt đoạn loại trừ")
    goc_loi = int(np.argmax(co_loi))
    cuoi_loi = n - 1 - int(np.argmax(co_loi[::-1]))

    ds: list[dict] = []

    def them(ten, gia_tri, kl, chu_thich="", don_vi=""):
        ds.append(dict(ten=ten, gia_tri=gia_tri, don_vi=don_vi, ket_luan=kl, chu_thich=chu_thich))

    # 1. lời − nhạc khi có lời
    d = (v - m)[loi_dung]
    ln, ln10 = float(np.median(d)), float(np.percentile(d, 10))
    ng = NGUONG["loi_nhac_dB"]
    them("Lời cao hơn nhạc (trung vị, khi có lời)", round(ln, 1), phan_loai(ln, *ng), f"đích ≥ {ng[0]:g}, chặn < {ng[1]:g}", "dB")
    ng = NGUONG["loi_nhac_p10_dB"]
    them("Lời cao hơn nhạc, 10 % giây tệ nhất", round(ln10, 1), phan_loai(ln10, *ng), f"đích ≥ {ng[0]:g} (chỉ cảnh báo)", "dB")

    # 2. nhạc ở khe giữa lời so với lúc có lời
    khe = np.zeros(n, bool)
    for b, c in doan(~co_loi, KHE_TOI_THIEU):
        if b > goc_loi and b + c <= cuoi_loi:
            khe[b:b + c] = True
    khe &= dung
    ng = NGUONG["nhac_khe_dB"]
    if khe.sum() >= KHE_TOI_DA_THIEU:
        dk = float(np.median(m[khe]) - np.median(m[loi_dung]))
        them("Nhạc ở khe giữa lời so với lúc có lời", round(dk, 1), phan_loai(dk, *ng),
             f"{int(khe.sum())} s khe; đích ≥ +{ng[0]:g}, chặn < +{ng[1]:g}", "dB")
    else:
        them("Nhạc ở khe giữa lời so với lúc có lời", None, CANH_BAO,
             f"chỉ {int(khe.sum())} s khe không lời (cần ≥ {KHE_TOI_DA_THIEU}): chưa có chỗ nào cho nhạc dâng")

    # 3. tỉ lệ thời gian nhạc còn chạy
    nguong_tat = ref - tat_db
    chay = float((m > nguong_tat).mean() * 100)
    ng = NGUONG["nhac_chay_pct"]
    them("Thời gian nhạc còn chạy (trên mức tắt)", round(chay, 1), phan_loai(chay, ng[0], ng[1], thap_tot=True),
         f"mức tắt = lời nói − {tat_db:g} dB = {nguong_tat:.0f} dBFS; chỉ cảnh báo khi > {ng[0]:g}", "%")

    # 4. nhạc tắt hẳn ≥ 3 s, theo chương (bỏ đoạn tắt trong hook trước lời và ở đuôi sau lời cuối)
    tat = doan(m < nguong_tat, TAT_TOI_THIEU)
    hook = [(b, c) for b, c in tat if b + c <= goc_loi]
    duoi = [(b, c) for b, c in tat if b > cuoi_loi]
    tat_the = [(b, c) for b, c in tat if (b, c) not in hook and (b, c) not in duoi]

    def con_tieng(b, c):
        return s is not None and float(np.median(s[b:b + c])) > ref + NGUONG["tieng_so_loi_dB"][0]

    moc_chuong, thuc = chia_chuong(n, chuong, do_dai_chuong)
    ranh = moc_chuong + [float(n)]
    thieu, chi_tiet = [], []
    for i in range(len(moc_chuong)):
        a, b = ranh[i], ranh[i + 1]
        trong = [x for x in tat_the if a <= x[0] < b]
        chi_tiet.append(dict(chuong=i, bd=round(a, 1), kt=round(b, 1), so_lan=len(trong),
                             lan=[dict(bd=x[0], dai=x[1], con_tieng=con_tieng(*x)) for x in trong]))
        if not trong or all(con_tieng(*x) for x in trong):
            thieu.append(i)
    kl = DAT if not thieu else (CHAN if thuc else CANH_BAO)
    mo_ta = f"{len(tat_the)} lần tắt ≥ {TAT_TOI_THIEU} s ngoài hook và đuôi ({len(hook)} lần trong hook, {len(duoi)} lần sau lời cuối); {len(moc_chuong)} chương" \
            + ("" if thuc else " (chia đều, mốc giả định)")
    if thieu:
        mo_ta += "; chương thiếu: " + ", ".join(f"{i + 1}@{int(ranh[i]) // 60}:{int(ranh[i]) % 60:02d}" for i in thieu)
        if any(chi_tiet[i]["so_lan"] for i in thieu):
            mo_ta += " (có chương nhạc tắt nhưng tiếng động còn chạy, không tính là nghỉ)"
    them("Chương có nhạc tắt hẳn ≥ 3 s", len(moc_chuong) - len(thieu), kl, mo_ta + f"; đích {len(moc_chuong)}/{len(moc_chuong)}",
         f"/{len(moc_chuong)}")

    # 5. đoạn dài nhất không có chỗ nhạc lắng
    med60 = np.array([np.median(m[max(0, i - 30):i + 30]) for i in range(n)])
    lang = np.zeros(n, bool)
    for b, c in doan(m < med60 - DAY_TUONG_DOI, 2) + doan(m < nguong_tat, 2):
        lang[b:b + c] = True
    cang = lap_ho(m > ref - CANG_DB, HO_CANG)
    chuoi = doan(cang & ~lang, 1)
    xa = max((c for _, c in chuoi), default=0)
    ng = NGUONG["nghi_xa_nhat_s"]
    them("Đoạn nhạc căng liền dài nhất", xa, phan_loai(xa, ng[0], ng[1], thap_tot=True),
         f"căng = nhạc cao hơn lời − {CANG_DB:g} dB, hết căng khi lắng ≥ 10 dB hoặc tắt; {int(lang.sum())} s lắng trong {len(doan(lang, 1))} chỗ; đích ≤ {ng[0]:g}, chặn > {ng[1]:g}", "s")

    # 6. tiếng động
    nhan = []
    if s is not None:
        ts = float(np.median(s)) - ref
        ng = NGUONG["tieng_so_loi_dB"]
        them("Tiếng động (trung vị) so với lời", round(ts, 1), phan_loai(ts, ng[0], ng[1], thap_tot=True),
             f"đích ≤ {ng[0]:g} (chỉ cảnh báo)", "dB")
        if s50 is not None:
            nhan = cu_nhan(s50, ref - NHAN_DB)
            pm = len(nhan) / (n / 60)
            lo, hi = NGUONG["nhan_moi_phut"]
            them("Cú nhấn mạnh", round(pm, 1), DAT if lo <= pm <= hi else CANH_BAO,
                 f"{len(nhan)} cú; ĐẠT trong [{lo:g}; {hi:g}]: dưới là phim phẳng, trên là dồn dập", "/phút")
    else:
        them("Tiếng động (trung vị) so với lời", None, KHONG_DO, "không có stem tiếng động")

    # 7. LRA
    if lra and "LRA_LU" in lra:
        lo, hi = NGUONG["lra"]
        x = lra["LRA_LU"]
        them("LRA", x, DAT if lo <= x <= hi else CANH_BAO, f"ĐẠT trong [{lo:g}; {hi:g}] (không phải chỉ số quyết định)", "LU")
    else:
        them("LRA", None, KHONG_DO, "không đo được ebur128" + (f": {lra['loi']}" if lra and lra.get("loi") else ""))

    tong = max((THU_TU[c["ket_luan"]] for c in ds), default=0)
    ket_luan = {0: DAT, 1: CANH_BAO, 2: CHAN}[tong]
    return dict(chi_so=ds, ket_luan=ket_luan, thoi_luong_s=n, giay_co_loi_pct=round(float(co_loi.mean() * 100)),
                muc_loi_noi_dB=round(ref, 1), nguong_co_loi_dB=round(float(cong), 1), nguong_tat_dB=round(nguong_tat, 1),
                chuong=chi_tiet, chuong_la_moc_that=thuc, tat_trong_hook=[list(map(int, x)) for x in hook], tat_o_duoi=[list(map(int, x)) for x in duoi],
                lang=[list(map(int, x)) for x in doan(lang, 1)],
                loai_tru=[list(x) for x in (loai_tru or [])], cu_nhan=nhan)


def in_bang(kq: dict, ten: str) -> None:
    print(f"== Đo lớp âm: {ten} ({kq['thoi_luong_s'] // 60}:{kq['thoi_luong_s'] % 60:02d}; "
          f"{kq['giay_co_loi_pct']} % giây có lời; lời nói ở {kq['muc_loi_noi_dB']} dBFS)")
    rong = max(len(c["ten"]) for c in kq["chi_so"])
    for c in kq["chi_so"]:
        gt = "  -  " if c["gia_tri"] is None else f"{c['gia_tri']:g}"
        print(f"{c['ket_luan']:<14} {c['ten']:<{rong}}  {gt}{c['don_vi'] if c['gia_tri'] is not None else ''}   {c['chu_thich']}")
    if kq["loai_tru"]:
        print("(đã loại trừ đoạn cao trào cố ý: " + ", ".join(f"{a:g}-{b:g} s" for a, b in kq["loai_tru"]) + ")")
    print(f"== KẾT LUẬN: {kq['ket_luan']}")


def tim_tep(thu_muc: Path, ten: str | None, mau: str | None) -> tuple[dict, str]:
    """Tìm giong/nhac/tieng/master trong thư mục. Trả (tệp, tên)."""
    if mau:
        mau_ds = [mau]
    else:
        mau_ds = ["{ten}-stem-{k}.wav", "{ten}-tach-{k}.wav"]
    ten_ds = [ten] if ten else sorted({re.sub(r"-(stem|tach)-(giong|nhac|tieng)\.wav$", "", f.name)
                                       for f in thu_muc.glob("*.wav") if re.search(r"-(stem|tach)-giong\.wav$", f.name)})
    if mau and not ten:
        loi("--mau cần --ten")
    if len(ten_ds) != 1:
        loi("không xác định được tập: " + (", ".join(ten_ds) if ten_ds else "không thấy stem giọng") + " (dùng --ten)")
    ten = ten_ds[0]
    kq = {}
    for k in ("giong", "nhac", "tieng"):
        for md in mau_ds:
            f = thu_muc / md.format(ten=ten, k=k)
            if f.exists():
                kq[k] = f
                break
    f = thu_muc / f"{ten}-master.wav"
    if f.exists():
        kq["master"] = f
    return kq, ten


def doc_moc_chuong(chuoi: str | None, lui: float | None, thoi_luong: float) -> list[float] | None:
    if not chuoi:
        return None
    p = Path(chuoi)
    if p.suffix.lower() == ".json" and p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        if lui is None:
            het = d.get("het")
            if het and 0 <= thoi_luong - het < 30:
                lui = thoi_luong - het
                print(f"(lùi mốc phan-canh.json {lui:.3f} s = thời lượng âm − het)")
            else:
                lui = 0.0
                print("(cảnh báo: phan-canh.json không có «het» khớp thời lượng âm, không suy ra được lùi intro, dùng 0: "
                      "mốc chương có thể lệch; đặt --lui nếu có intro)", file=sys.stderr)
        moc = [c["t0"] + lui for c in d["canh"] if str(c.get("nguon", "")).startswith("the:chuong/")]
        if not moc:
            loi(f"{p} không có cảnh nguồn «the:chuong/N»")
        return moc
    try:
        return [float(x) for x in chuoi.split(",") if x.strip()]
    except ValueError:
        loi("--chuong: danh sách giây cách nhau dấu phẩy, hoặc đường dẫn phan-canh.json có thật")


def doc_loai_tru(chuoi: str | None) -> list[tuple[float, float]]:
    out = []
    for p in (chuoi or "").split(","):
        if p.strip():
            m = re.fullmatch(r"\s*([\d.]+)\s*-\s*([\d.]+)\s*", p)
            if not m or float(m.group(1)) >= float(m.group(2)):
                loi(f"--loai-tru sai ở «{p}»: dạng 600-650")
            out.append((float(m.group(1)), float(m.group(2))))
    return out


def ve_do_thi(kq: dict, v, m, s, ra: Path) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("(bỏ qua --do-thi: máy chưa có matplotlib)", file=sys.stderr)
        return
    W = 5
    fig, ax = plt.subplots(2, 1, figsize=(16, 7), sharex=True)
    for ten, a, mau in (("lời", v, "#1f77b4"), ("nhạc", m, "#d62728"), ("tiếng động", s, "#7f7f7f")):
        if a is None:
            continue
        x = [np.median(a[i:i + W]) for i in range(0, len(a) - W + 1, W)]
        ax[0].plot(np.arange(len(x)) * W / 60, x, color=mau, label=ten, lw=1.3)
    ax[0].axhline(kq["nguong_tat_dB"], color="#d62728", ls=":", lw=1, label="mức nhạc tắt")
    for b, c in kq["lang"]:
        ax[0].axvspan(b / 60, (b + c) / 60, color="#2ca02c", alpha=0.18)
    for ch in kq["chuong"]:
        ax[0].axvline(ch["bd"] / 60, color="k", lw=0.6, alpha=0.5)
    ax[0].set_ylabel("dBFS (RMS)")
    ax[0].legend(loc="lower right", fontsize=8)
    ax[0].set_title(f"Lớp âm theo thời gian (xanh lá = nhạc lắng/tắt, vạch đen = đầu chương) · kết luận {kq['ket_luan']}")
    g = [np.median((v - m)[i:i + 30][v[i:i + 30] > kq["nguong_co_loi_dB"]])
         if (v[i:i + 30] > kq["nguong_co_loi_dB"]).sum() > 5 else np.nan for i in range(0, len(v) - 29, 30)]
    ax[1].plot((np.arange(len(g)) * 30 + 15) / 60, g, color="#9467bd", lw=1.5)
    ax[1].axhline(NGUONG["loi_nhac_dB"][0], color="g", ls="--", lw=1, label="đích")
    ax[1].axhline(NGUONG["loi_nhac_dB"][1], color="r", ls="--", lw=1, label="chặn")
    ax[1].set_ylabel("lời − nhạc (dB, mỗi 30 s)")
    ax[1].set_xlabel("phút")
    ax[1].legend(fontsize=8)
    for a in ax:
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ra, dpi=80)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Đo lớp âm giọng, nhạc, tiếng động; ĐẠT/CẢNH BÁO/CHẶN.")
    ap.add_argument("thu_muc", nargs="?")
    ap.add_argument("--ten")
    ap.add_argument("--mau")
    ap.add_argument("--giong")
    ap.add_argument("--nhac")
    ap.add_argument("--tieng")
    ap.add_argument("--master")
    ap.add_argument("--chuong")
    ap.add_argument("--lui", type=float)
    ap.add_argument("--do-dai-chuong", type=float, default=180.0)
    ap.add_argument("--loai-tru")
    ap.add_argument("--tat-db", type=float, default=TAT_DB)
    ap.add_argument("--json")
    ap.add_argument("--do-thi")
    a = ap.parse_args(argv)

    tep, ten = {}, "âm"
    if a.thu_muc:
        thu = Path(a.thu_muc)
        if not thu.is_dir():
            print(f"không có thư mục {thu}", file=sys.stderr)
            return 2
        tep, ten = tim_tep(thu, a.ten, a.mau)
    for k in ("giong", "nhac", "tieng", "master"):
        if getattr(a, k):
            tep[k] = Path(getattr(a, k))
    for k, f in tep.items():
        if not Path(f).exists():
            print(f"không có tệp {k}: {f}", file=sys.stderr)
            return 2
    if not tep:
        ap.print_usage(sys.stderr)
        return 2

    if a.do_dai_chuong <= 0:
        loi("--do-dai-chuong phải lớn hơn 0")
    if "giong" not in tep or "nhac" not in tep:
        lra = lra_tu([tep["master"]]) if "master" in tep else None
        print(f"== Đo lớp âm: {ten}\nthiếu stem {'giọng' if 'giong' not in tep else 'nhạc'}: chỉ có bản trộn thì không tách được "
              "lời − nhạc, nhạc tắt, nhạc ở khe.")
        if lra and "LRA_LU" in lra:
            print(f"{'':<14} LRA {lra['LRA_LU']:g} LU, I {lra.get('I_LUFS', float('nan')):g} LUFS (chỉ đo được hai số này)")
        print(f"== KẾT LUẬN: {KHONG_DO}. Cần stem giọng, nhạc, tiếng động (hau-ky-am.py ghi <ten>-stem-*.wav; "
              "hoặc tách Demucs từ bản trộn, kém chắc hơn).")
        return 3

    v, m = rms_db(doc_wav(Path(tep["giong"]))), rms_db(doc_wav(Path(tep["nhac"])))
    s = s50 = None
    if "tieng" in tep:
        s_raw = doc_wav(Path(tep["tieng"]))
        s, s50 = rms_db(s_raw), rms_db(s_raw, cua_so=0.05)
        del s_raw
    n = min(len(v), len(m))
    if "master" in tep:
        lra = lra_tu([tep["master"]])
    elif "tieng" in tep:
        lra = lra_tu([tep["giong"], tep["nhac"], tep["tieng"]])
        print("(không có master: LRA đo trên tổng ba stem)")
    else:
        lra = None
    if lra and lra.get("loi"):
        print(f"(cảnh báo: không đo được LRA: {lra['loi']})", file=sys.stderr)
    try:
        kq = phan_tich(v, m, s, s50, lra=lra, chuong=doc_moc_chuong(a.chuong, a.lui, n),
                       do_dai_chuong=a.do_dai_chuong, loai_tru=doc_loai_tru(a.loai_tru), tat_db=a.tat_db)
    except ValueError as e:
        print(f"không đo được: {e}", file=sys.stderr)
        return 2
    in_bang(kq, ten)
    if a.json:
        n = kq["thoi_luong_s"]
        Path(a.json).write_text(json.dumps(dict(ten=ten, **kq, lra=lra, giong=v[:n].round(1).tolist(), nhac=m[:n].round(1).tolist(),
                                                tieng=np.concatenate([s, np.full(max(0, n - len(s)), -120.0)])[:n].round(1).tolist() if s is not None else None),
                                           ensure_ascii=False), encoding="utf-8", newline="")
    if a.do_thi:
        n = kq["thoi_luong_s"]
        ve_do_thi(kq, v[:n], m[:n], np.concatenate([s, np.full(max(0, n - len(s)), -120.0)])[:n] if s is not None else None,
                  Path(a.do_thi))
    return 1 if kq["ket_luan"] == CHAN else 0


if __name__ == "__main__":
    sys.exit(main())
