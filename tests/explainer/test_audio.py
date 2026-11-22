import math
import struct
import sys
import wave
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from explainer.audio_engine import audio_validator


def _write_tone_wav(path: Path, seconds: float = 1.5, sr: int = 22050) -> None:
    n = int(seconds * sr)
    frames = b"".join(struct.pack("<h", int(3000 * math.sin(2 * math.pi * 440 * i / sr))) for i in range(n))
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(frames)


def test_validate_audio_passes_a_real_wav(tmp_path):
    wav = tmp_path / "tone.wav"
    _write_tone_wav(wav)
    assert audio_validator.validate_audio(wav, expected_min_seconds=1.0) == []


def test_validate_audio_flags_missing_file(tmp_path):
    problems = audio_validator.validate_audio(tmp_path / "nope.wav")
    assert problems and "does not exist" in problems[0]


def test_validate_audio_flags_too_short(tmp_path):
    wav = tmp_path / "short.wav"
    _write_tone_wav(wav, seconds=0.2)
    problems = audio_validator.validate_audio(wav, expected_min_seconds=5.0)
    assert any("expected at least" in p for p in problems)
