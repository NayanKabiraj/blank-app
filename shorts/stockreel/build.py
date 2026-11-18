"""Render one stock-footage Short or documentary: narration (same TTS pipeline as the other two styles) -> real
stock footage cut to that timing -> ducked music + sfx mix. Mirrors `shorts/compose.py`'s build()/build_documentary()
and reuses its voice and mix steps directly (`compose._voice_track`, `compose._mix`), the same way
`shorts/director/build.py` does - only the picture step (`render.render` here, `animate.render`/the Three.js
engine there) differs between the three styles."""
from __future__ import annotations

from pathlib import Path

from .. import compose, config
from . import render as footage

MOODS = {"calm": "calm", "upbeat": "upbeat", "dramatic": "dramatic", "inspiring": "inspiring", "mysterious": "mysterious"}


def build_short(script, lang: str, mood: str, work: Path, niche: str = "") -> Path:
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    voice, timeline, voice_end = compose._voice_track(script.scenes, lang, work, window=(config.MIN_DURATION, config.MAX_DURATION))
    total = min(config.MAX_DURATION, max(config.MIN_DURATION, voice_end + config.TAIL))
    footage.render(script.scenes, lang, niche, timeline, total, work, layout="portrait")
    out = work / f"stockreel_{lang}.mp4"
    compose._mix(work, voice, total, MOODS.get(mood, "dramatic"), out)
    return out


def build_documentary(script, lang: str, mood: str, work: Path, niche: str = "") -> tuple[Path, list[tuple[str, float]]]:
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    scenes = script.scenes
    starts, n = {}, 0
    for ch in script.chapters:
        starts[n] = ch.title
        n += len(ch.scenes)
    voice, timeline, voice_end = compose._voice_track(scenes, lang, work, chapter_starts=frozenset(starts), style="documentary")
    total = voice_end + 3.0
    footage.render(scenes, lang, niche, timeline, total, work, layout="landscape", fps=config.DOC_FPS)
    out = work / f"stockreel_documentary_{lang}.mp4"
    compose._mix(work, voice, total, MOODS.get(mood, "dramatic"), out, lufs=-16, music_volume=0.22)
    chapters = [(title, 0.0 if i == 0 else timeline[i][0]) for i, title in sorted(starts.items())]
    return out, chapters
