"""Cắt dải chữ ghi nguồn ở mép dưới khung hình (độ phân giải gốc) cho từng shot, ghép thành tờ để đọc.

Dùng: python credit-strips.py <video.mp4> <thư mục phân tích có shots.csv> [--band 0.075] [--per-sheet 24]
Ra: <thư mục>/credits/credit_NNN.jpg — mỗi dòng: nhãn SHOT + dải mép dưới của khung giữa shot.
"""
import argparse, csv, os, subprocess
import numpy as np
import cv2


def frame_at(video: str, t: float) -> np.ndarray | None:
    out = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                          "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    if not out:
        return None
    return cv2.imdecode(np.frombuffer(out, np.uint8), cv2.IMREAD_COLOR)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("dir")
    ap.add_argument("--band", type=float, default=0.075)
    ap.add_argument("--per-sheet", type=int, default=24)
    a = ap.parse_args()
    shots = list(csv.DictReader(open(os.path.join(a.dir, "shots.csv"), encoding="utf-8")))
    os.makedirs(os.path.join(a.dir, "credits"), exist_ok=True)
    rows, n = [], 0
    for s in shots:
        img = frame_at(a.video, (float(s["start"]) + float(s["end"])) / 2)
        if img is None:
            continue
        h = img.shape[0]
        band = img[int(h * (1 - a.band)):, :]
        label = np.full((26, band.shape[1], 3), 20, np.uint8)
        cv2.putText(label, f"SHOT {s['idx']}  {s['start']}s", (8, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        rows += [label, band]
        if len(rows) >= 2 * a.per_sheet:
            n += 1
            cv2.imwrite(os.path.join(a.dir, "credits", f"credit_{n:03d}.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 90])
            rows = []
    if rows:
        n += 1
        cv2.imwrite(os.path.join(a.dir, "credits", f"credit_{n:03d}.jpg"), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(f"{n} sheets, {len(shots)} shots")


if __name__ == "__main__":
    main()
