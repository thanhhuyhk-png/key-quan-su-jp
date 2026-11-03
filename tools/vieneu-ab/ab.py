"""So chất giọng VieNeu v3 Turbo theo thiết bị/độ chính xác: python -I ab.py <text.txt> <voice> <out_dir> <mode...>
mode: gpu-auto | gpu-fp32 | cpu-fp32"""
import sys, os, time, torch
from vieneu import Vieneu
text = open(sys.argv[1], encoding="utf-8").read()
voice, out = sys.argv[2], sys.argv[3]
cfg = {"gpu-auto": dict(), "gpu-fp32": dict(dtype="float32"), "cpu-fp32": dict(device="cpu", backend="onnx", precision="fp32")}
print("bf16_supported", torch.cuda.is_bf16_supported())
for m in sys.argv[4:]:
    tts = Vieneu(**cfg[m])
    eng = tts.engine
    print(m, "backend", tts.backend, "dtype", getattr(eng, "dtype", None), flush=True)
    vs = {vid for _, vid in tts.list_preset_voices()}
    assert voice in vs, voice
    t = time.time()
    wav = tts.infer(text, voice=voice, show_progress=False)
    tts.save(wav, os.path.join(out, f"{m}.wav"))
    print(m, "done %.1fs" % (time.time() - t), flush=True)
    del tts; torch.cuda.empty_cache()
