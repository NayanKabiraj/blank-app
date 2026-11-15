"""Step 3: one WAV per sentence and per scene with Kokoro (ONNX build), timings measured, never guessed.
Usage: python make_audio.py <lang> <kokoro.onnx> <voices.bin>"""
import json, sys, subprocess
from pathlib import Path
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

lang, model, voices = sys.argv[1:4]
here = Path(__file__).parent
script = json.loads((here / "script.json").read_text(encoding="utf-8"))
v = script["voices"][lang]
k = Kokoro(model, voices)
out = here / "audio" / lang; out.mkdir(parents=True, exist_ok=True)
SR, GAP, LEAD, TAIL = 24000, 0.28, 0.25, 0.4   # pause between sentences; breathing room per scene
timing, t0, full = [], 0.0, []
for n, sc in enumerate(script["scenes"], 1):
    parts, cues, t = [np.zeros(int(SR * LEAD), np.float32)], [], LEAD
    for s in sc[lang]:
        a, sr = k.create(s, voice=v["voice"], speed=v["speed"], lang=v["lang"])
        assert sr == SR
        a = np.trim_zeros(a.astype(np.float32))
        cues.append({"text": s, "start": round(t, 3), "end": round(t + len(a) / SR, 3)})
        parts += [a, np.zeros(int(SR * GAP), np.float32)]
        t += len(a) / SR + GAP
    parts[-1] = np.zeros(int(SR * TAIL), np.float32)
    wav = np.concatenate(parts)
    sf.write(out / f"scene-{n:02d}.wav", wav, SR)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", str(out / f"scene-{n:02d}.wav")]))
    timing.append({"id": sc["id"], "start": round(t0, 3), "duration": round(dur, 3), "cues": cues})
    t0 += dur; full.append(wav)
sf.write(out / "voiceover.wav", np.concatenate(full), SR)
(out / "timing.json").write_text(json.dumps({"total": round(t0, 3), "scenes": timing}, ensure_ascii=False, indent=1), encoding="utf-8")
print(lang, "total", round(t0, 2), [round(s["duration"], 1) for s in timing])
