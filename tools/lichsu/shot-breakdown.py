"""Cắt cảnh một video và xuất tư liệu để bóc tách từng shot.

Dùng: python shot-breakdown.py <video.mp4> <thư mục ra> [--vtt phụ-đề.vtt] [--thr 30] [--step 2] [--rows-per-sheet 10]

Ra:
  shots.csv          mốc mỗi shot, độ dài, độ chuyển động, độ sáng, độ bão hoà, lời đọc trùng shot
  frames/NNNN_KK.jpg  khung của từng shot, mỗi 2 giây một khung (640x360)
  sheets/sheet_NNN.jpg    tờ liên khung: mỗi shot một khối 4 cột, mỗi ô ghi mốc giờ
  summary.json       số shot, độ dài shot trung vị, số cắt mỗi phút
"""
import argparse, csv, json, os, re, subprocess, statistics
import numpy as np
import cv2

W, H = 160, 90


def read_small_frames(path, w=W, h=H):
    """Giải mã tuần tự toàn bộ khung ở cỡ w x h qua ffmpeg (tránh seek chậm của cv2)."""
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "stream=avg_frame_rate", "-of", "csv=p=0", path], capture_output=True, text=True)
    num, den = probe.stdout.strip().split("/")
    fps = float(num) / float(den)
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = w * h * 3
    while True:
        buf = proc.stdout.read(size)
        if len(buf) < size:
            break
        yield fps, np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    proc.wait()


def detect(path, thr, min_len, gthr):
    """Cắt cứng: chênh lệch HSV hai khung liền nhau > thr (giống ContentDetector).
    Chuyển mềm (hoà hình, bay máy qua cảnh khác): chênh lệch giữa khung i và khung i-1 giây (ảnh đã làm mờ)
    > gthr và là cực đại trong cửa sổ ±1 giây; mốc cắt đặt giữa đoạn chuyển."""
    diffs, wdiffs, motion, bright, sat = [], [], [], [], []
    prev, hist = None, []
    fps = 30.0
    for fps, f in read_small_frames(path):
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.int16)
        blur = cv2.GaussianBlur(f, (9, 9), 0).astype(np.int16)
        bright.append(float(hsv[..., 2].mean()))
        sat.append(float(hsv[..., 1].mean()))
        if prev is None:
            diffs.append(0.0); motion.append(0.0)
        else:
            d = np.abs(hsv - prev)
            diffs.append(float(d.mean(axis=(0, 1)).mean()))
            motion.append(float(d[..., 2].mean()))
        w = int(round(fps))
        hist.append(blur)
        if len(hist) > w + 1:
            hist.pop(0)
        wdiffs.append(float(np.abs(blur - hist[0]).mean()) if len(hist) > w else 0.0)
        prev = hsv
    n = len(diffs)
    w = int(round(fps))
    min_frames = int(min_len * fps)
    kinds = {0: "dau"}
    for i in range(1, n):
        if diffs[i] > thr:
            kinds[i] = "cat"
    for i in range(w, n):
        lo, hi = max(0, i - w), min(n, i + w + 1)
        if wdiffs[i] > gthr and wdiffs[i] == max(wdiffs[lo:hi]):
            mid = i - w // 2
            if not any(abs(mid - c) < w for c in kinds):
                kinds[mid] = "mem"
    cuts = []
    for c in sorted(kinds):
        if not cuts or c - cuts[-1] >= min_frames:
            cuts.append(c)
    cuts.append(n)
    shots = []
    for k in range(len(cuts) - 1):
        a, b = cuts[k], cuts[k + 1]
        inner = motion[a + 1:b] or [0.0]
        shots.append(dict(idx=k + 1, f0=a, f1=b - 1, start=round(a / fps, 2), end=round(b / fps, 2),
                          dur=round((b - a) / fps, 2), vao=kinds.get(a, "cat"), motion=round(statistics.mean(inner), 2),
                          bright=round(statistics.mean(bright[a:b]), 1), sat=round(statistics.mean(sat[a:b]), 1)))
    return fps, n, shots


def parse_vtt(path):
    """Phụ đề tự động YouTube: lấy cue (bắt đầu, kết thúc, chữ), bỏ trùng lặp dạng cuộn."""
    def t(s):
        h, m, rest = s.split(":")
        return int(h) * 3600 + int(m) * 60 + float(rest)
    cues, seen = [], set()
    txt = open(path, encoding="utf-8").read()
    for block in txt.split("\n\n"):
        m = re.search(r"(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)", block)
        if not m:
            continue
        lines = [re.sub(r"<[^>]+>", "", l).strip() for l in block.split("\n")[1:]]
        for line in lines:
            if line and "-->" not in line and line not in seen:
                seen.add(line)
                cues.append((t(m.group(1)), t(m.group(2)), line))
    return cues


def grab_all(path, wanted):
    """Lượt giải mã thứ hai ở 640x360, giữ đúng các khung cần lấy: {số khung: [đường dẫn ra]}."""
    got = {}
    for i, (_, img) in enumerate(read_small_frames(path, 640, 360)):
        if i in wanted:
            img = img.copy()
            for out in wanted[i]:
                cv2.imwrite(out, img, [cv2.IMWRITE_JPEG_QUALITY, 85])
            got[i] = img
    return got


def fmt(sec):
    return f"{int(sec // 60):02d}:{sec % 60:05.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--vtt"); ap.add_argument("--thr", type=float, default=30.0)
    ap.add_argument("--min-len", type=float, default=0.35)
    ap.add_argument("--gthr", type=float, default=22.0)
    ap.add_argument("--step", type=float, default=2.0)
    ap.add_argument("--rows-per-sheet", type=int, default=10)
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, "frames"), exist_ok=True)
    os.makedirs(os.path.join(a.out, "sheets"), exist_ok=True)

    fps, nframes, shots = detect(a.video, a.thr, a.min_len, a.gthr)
    cues = parse_vtt(a.vtt) if a.vtt and os.path.exists(a.vtt) else []
    for s in shots:
        s["loi"] = " ".join(c[2] for c in cues if c[0] < s["end"] and c[1] > s["start"] and c[0] >= s["start"] - 1.5)

    # Chuyển cảnh mềm (bay bản đồ, hoà hình) không tạo cú cắt, nên mỗi shot lấy thêm một khung mỗi `step` giây.
    wanted, picks = {}, {}
    step = int(a.step * fps)
    for s in shots:
        pad = min(int(0.2 * fps), max(0, (s["f1"] - s["f0"]) // 4))
        fs = list(range(s["f0"] + pad, s["f1"] - pad, step)) + [s["f1"] - pad]
        if len(fs) > 1 and fs[-1] - fs[-2] < step // 3:
            fs.pop(-2)
        picks[s["idx"]] = fs
        for k, f in enumerate(fs):
            wanted.setdefault(f, []).append(os.path.join(a.out, "frames", f"{s['idx']:04d}_{k:02d}.jpg"))
    got = grab_all(a.video, wanted)
    blank = np.zeros((360, 640, 3), np.uint8)
    tw, th, cols = 360, 203, 4

    def shot_block(s):
        tiles = []
        for f in picks[s["idx"]]:
            t = cv2.resize(got.get(f, blank), (tw, th))
            cv2.putText(t, fmt(f / fps), (6, th - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
            tiles.append(t)
        while len(tiles) % cols:
            tiles.append(np.full((th, tw, 3), 20, np.uint8))
        grid = np.vstack([np.hstack(tiles[r:r + cols]) for r in range(0, len(tiles), cols)])
        label = np.full((30, grid.shape[1], 3), 20, np.uint8)
        cv2.putText(label, f"SHOT {s['idx']}  {fmt(s['start'])}-{fmt(s['end'])}  {s['vao']}  dur {s['dur']}s  motion {s['motion']}",
                    (8, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        return np.vstack([label, grid])

    sheet, rows_used, n = [], 0, 0
    for s in shots:
        block = shot_block(s)
        r = (block.shape[0] - 30) // th
        if sheet and rows_used + r > a.rows_per_sheet:
            n += 1
            cv2.imwrite(os.path.join(a.out, "sheets", f"sheet_{n:03d}.jpg"), np.vstack(sheet), [cv2.IMWRITE_JPEG_QUALITY, 80])
            sheet, rows_used = [], 0
        sheet.append(block); rows_used += r
    if sheet:
        n += 1
        cv2.imwrite(os.path.join(a.out, "sheets", f"sheet_{n:03d}.jpg"), np.vstack(sheet), [cv2.IMWRITE_JPEG_QUALITY, 80])

    with open(os.path.join(a.out, "shots.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["idx", "start", "end", "dur", "vao", "motion", "bright", "sat", "loi"])
        w.writeheader()
        for s in shots:
            w.writerow({k: s[k] for k in w.fieldnames})

    durs = [s["dur"] for s in shots]
    total = nframes / fps
    per_min = [0] * (int(total // 60) + 1)
    for s in shots[1:]:
        per_min[int(s["start"] // 60)] += 1
    summary = dict(video=os.path.basename(a.video), fps=round(fps, 3), duration=round(total, 1), shots=len(shots),
                   median_shot=statistics.median(durs), soft_transitions=sum(s["vao"] == "mem" for s in shots), mean_shot=round(statistics.mean(durs), 2),
                   pct_shot_under_2s=round(100 * sum(d < 2 for d in durs) / len(durs), 1),
                   pct_shot_over_6s=round(100 * sum(d > 6 for d in durs) / len(durs), 1),
                   cuts_per_minute=per_min, threshold=a.thr, has_subs=bool(cues))
    json.dump(summary, open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "cuts_per_minute"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
