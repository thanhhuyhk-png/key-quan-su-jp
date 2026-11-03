"""Đọc một câu theo nhiều biến thể văn bản (GPU fp32), mỗi biến thể N lần. python -I variants.py <voice> <out_dir> <n>"""
import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")
from vieneu import Vieneu
voice, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
V = {
 "A-cham": "Quân đội viễn chinh Pháp tổ chức bốn mươi chín cứ điểm thành ba phân khu: Bắc, Trung tâm, Nam.",
 "B-ba-cham": "Quân đội viễn chinh Pháp tổ chức bốn mươi chín cứ điểm thành ba phân khu: Bắc, Trung tâm, Nam...",
 "C-noi-cau-sau": "Quân đội viễn chinh Pháp tổ chức bốn mươi chín cứ điểm thành ba phân khu: Bắc, Trung tâm, Nam. Quân đội nhân dân Việt Nam tham chiến với năm đại đoàn chủ lực.",
}
tts = Vieneu(dtype="float32")
for k, t in V.items():
    for i in range(n):
        w = tts.infer(t, voice=voice, show_progress=False)
        tts.save(w, os.path.join(out, f"{k}-{i+1}.wav"))
print("ok")
