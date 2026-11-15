"""Voice samples with Indic Parler-TTS (AI4Bharat, Apache 2.0). A standalone script for trying the model
in CI (heavy: torch + a 0.9B model on the CPU). Run in its own virtualenv:

    python shorts/voicelab_parler.py videos/voicelab

Parler-TTS reads a text *description* of the voice ("Divya speaks in a warm, expressive tone ...") next to
the text to speak, so emotion and pace are steered with words.
"""
import subprocess
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "voicelab")
OUT.mkdir(parents=True, exist_ok=True)
torch.set_num_threads(4)
MODEL = "ai4bharat/indic-parler-tts"
HI = "हर जून में पूरा देश आसमान की ओर देखता है। सबको एक ही चीज़ का इंतज़ार है: मॉनसून की पहली बारिश।"
EN = "Every June, a whole country looks up at the sky and holds its breath. Everyone is waiting for one thing: the first rain of the monsoon."
QUIET = "Very clear audio, close recording, no background noise."
STYLES = {
    "expressive": "speaks in an expressive, warm, animated storytelling tone with natural pauses and emphasis, at a moderate pace.",
    "calm": "speaks in a calm, thoughtful documentary narrator tone, slow to moderate pace, with gentle emphasis.",
}
SAMPLES = [(f"parler-hi-{who.lower()}-{style}", HI, f"{who} {desc} {QUIET}")
           for who in ("Divya", "Rohit") for style, desc in STYLES.items()]
SAMPLES += [(f"parler-en-{who.lower()}-{style}", EN, f"{who} {desc} {QUIET}")
            for who in ("Mary", "Thoma") for style, desc in STYLES.items()]

t0 = time.time()
model = ParlerTTSForConditionalGeneration.from_pretrained(MODEL)
tok = AutoTokenizer.from_pretrained(MODEL)
dtok = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)
print(f"model loaded in {time.time() - t0:.0f}s", flush=True)
log = []
for name, text, desc in SAMPLES:
    t1 = time.time()
    d = dtok(desc, return_tensors="pt")
    p = tok(text, return_tensors="pt")
    with torch.no_grad():
        gen = model.generate(input_ids=d.input_ids, attention_mask=d.attention_mask,
                             prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask)
    audio = gen.cpu().numpy().squeeze()
    secs = len(audio) / model.config.sampling_rate
    wav = OUT / f"{name}.wav"
    sf.write(wav, audio, model.config.sampling_rate)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-b:a", "128k", str(OUT / f"{name}.mp3")], check=True)
    wav.unlink()
    line = f"{name}: {secs:.1f}s of audio in {time.time() - t1:.0f}s ({(time.time() - t1) / secs:.1f}x real time)"
    print(line, flush=True)
    log.append(line)
(OUT / "timing.txt").write_text("\n".join(log) + "\n")
