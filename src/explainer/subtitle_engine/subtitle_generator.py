"""Chunks each scene's narration into short, phrase-sized subtitle cues timed proportionally
across the scene's own start/end (same approach proven in shorts/animate.py's caption_chunks:
weight each chunk by its character length so timing tracks natural speech rhythm, not a flat
per-word average).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..schemas.storyboard_schema import Scene

MAX_WORDS_PER_CUE = 5


@dataclass
class SubtitleCue:
    start: float
    end: float
    text: str


def _chunk_words(text: str, max_words: int) -> List[str]:
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]


def cues_for_scene(scene: Scene, max_words: int = MAX_WORDS_PER_CUE) -> List[SubtitleCue]:
    chunks = _chunk_words(scene.subtitle_text, max_words)
    if not chunks:
        return []
    weights = [max(1, len(c)) for c in chunks]
    total_w = sum(weights)
    span = scene.end - scene.start
    cues, t = [], scene.start
    for chunk, w in zip(chunks, weights):
        d = span * w / total_w
        cues.append(SubtitleCue(start=round(t, 3), end=round(t + d, 3), text=chunk))
        t += d
    return cues


def cues_for_storyboard(scenes: List[Scene]) -> List[SubtitleCue]:
    out: List[SubtitleCue] = []
    for scene in scenes:
        out.extend(cues_for_scene(scene))
    return out
