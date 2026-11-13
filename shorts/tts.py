"""Text-to-speech with Piper (open source, runs on CPU, has English + Hindi voices)."""
from __future__ import annotations

import logging
import math
import os
import struct
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


def synthesize(text: str, out_wav: Path, lang: str, length_scale: float = 1.0) -> float:
    """Render `text` to a mono WAV and return its duration in seconds."""
    if os.getenv("SHORTS_FAKE_TTS"):  # offline testing only: placeholder tone
        return _fake(text, out_wav, length_scale)
    from piper import SynthesisConfig

    voice = _load(config.VOICES[lang])
    with wave.open(str(out_wav), "wb") as wf:
        voice.synthesize_wav(text, wf, syn_config=SynthesisConfig(length_scale=length_scale))
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
