"""Render one stock-footage Short or documentary: narration (same TTS pipeline as the other two styles) -> real
stock footage cut to that timing -> ducked music + sfx mix. Mirrors `shorts/compose.py`'s build()/build_documentary()
and reuses its voice and mix steps directly (`compose._voice_track`, `compose._mix`), the same way
`shorts/director/build.py` does - only the picture step (`render.render` here, `animate.render`/the Three.js
engine there) differs between the three styles."""
from __future__ import annotations

from pathlib import Path

from .. import compose, config, outro
from . import render as footage

MOODS = {"calm": "calm", "upbeat": "upbeat", "dramatic": "dramatic", "inspiring": "inspiring", "mysterious": "mysterious"}


def _with_outro_scene(query_scenes, lang: str):
    """`query_scenes` is the English scene list used for footage search; it needs the outro scene too."""
    if not query_scenes:
        return query_scenes
    scenes = list(query_scenes)
    return scenes if outro.has_outro(type('S', (), {'scenes': scenes}), 'en') else [*scenes, outro.outro_scene('en')]


def build_short(script, lang: str, mood: str, work: Path, niche: str = "", query_scenes=None) -> tuple[Path, bool]:
    """Returns (video path, used_ai_image) - the caller flags the upload as synthetic media when True.
    `query_scenes` (the English scenes, when rendering a non-English language) is used only to build the
    image/video search phrase per scene - see `render.render`'s docstring for why."""
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    script = outro.with_outro(script, lang)
    query_scenes = _with_outro_scene(query_scenes, lang)
    voice, timeline, voice_end = compose._voice_track(script.scenes, lang, work, window=(config.MIN_DURATION, config.MAX_DURATION))
    total = min(config.MAX_DURATION, max(config.MIN_DURATION, voice_end + config.TAIL))
    used_ai = footage.render(script.scenes, lang, niche, timeline, total, work, layout="portrait", query_scenes=query_scenes)
    out = work / f"stockreel_{lang}.mp4"
    compose._mix(work, voice, total, MOODS.get(mood, "dramatic"), out)
    return out, used_ai


def build_documentary(script, lang: str, mood: str, work: Path, niche: str = "", query_scenes=None) -> tuple[Path, list[tuple[str, float]], bool]:
    """Returns (video path, chapters, used_ai_image). `query_scenes` - see `build_short`."""
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    script = outro.with_outro(script, lang)
    query_scenes = _with_outro_scene(query_scenes, lang)
    scenes = script.scenes
    starts, n = {}, 0
    for ch in script.chapters:
        starts[n] = ch.title
        n += len(ch.scenes)
    voice, timeline, voice_end = compose._voice_track(scenes, lang, work, chapter_starts=frozenset(starts), style="documentary")
    total = voice_end + 3.0
    used_ai = footage.render(scenes, lang, niche, timeline, total, work, layout="landscape", fps=config.DOC_FPS, query_scenes=query_scenes)
    out = work / f"stockreel_documentary_{lang}.mp4"
    compose._mix(work, voice, total, MOODS.get(mood, "dramatic"), out, lufs=-16, music_volume=0.22)
    chapters = [(title, 0.0 if i == 0 else timeline[i][0]) for i, title in sorted(starts.items())]
    return out, chapters, used_ai
