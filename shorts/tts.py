"""Text-to-speech.

Default: Indic Parler-TTS (expressive, Hindi speaker Rohit and English speaker Thoma; the voice is steered by
a short text description, see STYLES). Fallback: Piper (open source, small, runs on any CPU), used for a whole
run when Parler cannot be loaded. `SHORTS_FAKE_TTS=1` makes placeholder tones for offline testing.
"""
from __future__ import annotations

import hashlib
import logging
import math
import os
import struct
import subprocess
import urllib.request
import wave
from functools import lru_cache
from pathlib import Path

from . import config

log = logging.getLogger(__name__)
HF_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main"


def _voice_files(voice: str) -> tuple[Path, Path]:
    """Download a Piper voice (e.g. 'hi_IN-pratham-medium') once and cache it."""
    locale, name, quality = voice.split("-", 2)
    family = locale.split("_")[0]
    config.VOICES_DIR.mkdir(parents=True, exist_ok=True)
    onnx = config.VOICES_DIR / f"{voice}.onnx"
    cfg = config.VOICES_DIR / f"{voice}.onnx.json"
    for path in (onnx, cfg):
        if not path.exists():
            url = f"{HF_BASE}/{family}/{locale}/{name}/{quality}/{path.name}"
            log.info("Downloading %s", url)
            tmp = path.with_suffix(path.suffix + ".part")
            urllib.request.urlretrieve(url, tmp)
            tmp.rename(path)
    return onnx, cfg


@lru_cache(maxsize=4)
def _load(voice: str):
    from piper import PiperVoice

    onnx, cfg = _voice_files(voice)
    return PiperVoice.load(onnx, config_path=cfg)


QUIET = "Very clear audio, close recording, no background noise."
STYLES = {  # how the narrator sounds; Parler reads these words as a voice direction
    "shorts": "speaks in an expressive, warm, animated storytelling tone with natural pauses and emphasis, at a slightly fast pace.",
    "documentary": "speaks in a warm, engaging documentary narrator tone with natural pauses and gentle emphasis, at a moderate pace.",
}
WORDS_PER_SEC = {"en": 2.6, "hi": 2.3}   # rough speech pace, only used to spot broken generations
_state = {"parler": None}                 # None = untried, True = loaded, False = fell back to Piper
_raw: dict = {}                           # (text, lang, style) -> unscaled Parler wav, so re-fitting costs nothing


def synthesize(text: str, out_wav: Path, lang: str, length_scale: float = 1.0, style: str = "shorts") -> float:
    """Render `text` to a mono WAV and return its duration in seconds. `length_scale` > 1 slows it down."""
    if os.getenv("SHORTS_FAKE_TTS"):  # offline testing only: placeholder tone
        return _fake(text, out_wav, length_scale)
    if config.TTS_ENGINE == "parler" and _state["parler"] is not False:
        try:
            return _parler(text, out_wav, lang, length_scale, style)
        except Exception:  # noqa: BLE001 - the model could not be loaded: keep the whole run on one voice
            if _state["parler"]:
                raise
            log.exception("Parler-TTS is unavailable, falling back to Piper for this run")
            _state["parler"] = False
    return _piper(text, out_wav, lang, length_scale)


def _piper(text: str, out_wav: Path, lang: str, length_scale: float) -> float:
    from piper import SynthesisConfig

    voice = _load(config.VOICES[lang])
    with wave.open(str(out_wav), "wb") as wf:
        voice.synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=length_scale))
    return wav_duration(out_wav)


@lru_cache(maxsize=1)
def _parler_model():
    import torch
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer

    torch.set_num_threads(os.cpu_count() or 4)
    log.info("Loading %s", config.PARLER_MODEL)
    model = ParlerTTSForConditionalGeneration.from_pretrained(config.PARLER_MODEL).eval()
    tok = AutoTokenizer.from_pretrained(config.PARLER_MODEL)
    dtok = AutoTokenizer.from_pretrained(model.config.text_encoder._name_or_path)
    _state["parler"] = True
    return model, tok, dtok


def _parler_raw(text: str, lang: str, style: str, work: Path) -> Path:
    key = (text, lang, style)
    if key in _raw and _raw[key].exists():
        return _raw[key]
    import numpy as np
    import soundfile as sf
    import torch

    model, tok, dtok = _parler_model()
    desc = f"{config.PARLER_SPEAKERS[lang]} {STYLES.get(style, STYLES['shorts'])} {QUIET}"
    d, p = dtok(desc, return_tensors="pt"), tok(text, return_tensors="pt")
    expected = max(1.5, len(text.split()) / WORDS_PER_SEC[lang])
    seed0 = int(hashlib.sha1(text.encode()).hexdigest()[:8], 16)
    best = None
    for attempt in range(3):   # Parler sometimes truncates or rambles: retry with another seed
        torch.manual_seed(seed0 + attempt)
        with torch.inference_mode():
            gen = model.generate(input_ids=d.input_ids, attention_mask=d.attention_mask,
                                 prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask)
        audio = gen.cpu().numpy().squeeze().astype("float32")
        secs = len(audio) / model.config.sampling_rate
        best = audio if best is None or abs(secs - expected) < abs(len(best) / model.config.sampling_rate - expected) else best
        if 0.55 * expected <= secs <= 2.0 * expected:
            break
        log.warning("Parler gave %.1fs for ~%.1fs of text, retrying (%d)", secs, expected, attempt + 1)
    audio = best
    rms = float(np.sqrt(np.mean(audio ** 2))) or 1e-6      # even loudness from scene to scene
    audio = np.clip(audio * (0.085 / rms), -0.98, 0.98)
    raw = work / f"raw_{hashlib.sha1(repr(key).encode()).hexdigest()[:12]}.wav"
    sf.write(raw, audio, model.config.sampling_rate)
    _raw[key] = raw
    return raw


def _parler(text: str, out_wav: Path, lang: str, length_scale: float, style: str) -> float:
    raw = _parler_raw(text, lang, style, out_wav.parent)
    trim = "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse," \
           "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse"
    tempo = f",atempo={1.0 / length_scale:.4f}" if abs(length_scale - 1.0) > 0.01 else ""
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", trim + tempo, "-ac", "1",
                    str(out_wav)], check=True)
    return wav_duration(out_wav)


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as wf:
        return wf.getnframes() / wf.getframerate()


def _fake(text: str, out_wav: Path, length_scale: float) -> float:
    sr, dur = 22050, max(1.0, len(text.split()) * 0.38 * length_scale)
    frames = b"".join(
        struct.pack("<h", int(3000 * math.sin(2 * math.pi * 180 * i / sr) * (0.5 + 0.5 * math.sin(i / 2000))))
        for i in range(int(sr * dur))
    )
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1), wf.setsampwidth(2), wf.setframerate(sr)
        wf.writeframes(frames)
    return dur
