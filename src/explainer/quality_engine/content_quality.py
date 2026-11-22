"""Content-level checks that aren't about the video file itself: subtitle cues are well-formed
and Devanagari-correct (reuses subtitle_engine/subtitle_validator.py directly - no reason to
duplicate that logic), and the storyboard's own internal timing is consistent (already enforced
by the Storyboard schema's model_validator, re-checked here so a quality report can name it
explicitly rather than relying on an exception having been raised earlier).
"""
from __future__ import annotations

from ..schemas.storyboard_schema import Storyboard
from ..subtitle_engine.subtitle_generator import SubtitleCue
from ..subtitle_engine.subtitle_validator import validate_cues


def check_storyboard_timing(storyboard: Storyboard) -> list[str]:
    problems = []
    if storyboard.scenes[0].start > 0.5:
        problems.append(f"first scene starts at {storyboard.scenes[0].start}s, not near 0")
    if abs(storyboard.scenes[-1].end - storyboard.total_duration) > 1.0:
        problems.append("last scene's end does not match total_duration")
    return problems


def check_subtitles(cues: list[SubtitleCue], lang: str) -> list[str]:
    return validate_cues(cues, lang)
