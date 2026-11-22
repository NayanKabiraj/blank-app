"""Pluggable narration. Rather than reimplementing TTS (the spec's own section 19 rule:
preserve and reuse existing integrations), this adapts the repo's own shorts/tts.py - Piper by
default, Indic Parler-TTS when configured - which already does exactly what this spec asks for:
EN+HI, configurable voice, no hardcoded paid provider, SHORTS_FAKE_TTS=1 for a no-network demo
mode. A caller never talks to Piper/Parler directly; it calls `synthesize()` here, which is the
one place that could later be repointed at a different provider.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Protocol

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class TTSProvider(Protocol):
    def synthesize(self, text: str, out_wav: Path, lang: str, length_scale: float = 1.0) -> float:
        """Writes `out_wav`, returns its duration in seconds."""
        ...


class ShortsPiperProvider:
    """Wraps shorts.tts.synthesize - the repo's existing Piper/Parler pipeline."""

    name = "piper"

    def synthesize(self, text: str, out_wav: Path, lang: str, length_scale: float = 1.0) -> float:
        from shorts import tts as shorts_tts   # imported lazily: only needed if this provider runs
        style = "shorts"
        return shorts_tts.synthesize(text, out_wav, lang, length_scale, style)


PROVIDERS: dict[str, TTSProvider] = {"piper": ShortsPiperProvider()}


def get_provider(name: str = "piper") -> TTSProvider:
    if name not in PROVIDERS:
        raise ValueError(f"unknown TTS provider {name!r}; available: {', '.join(PROVIDERS)}")
    return PROVIDERS[name]
