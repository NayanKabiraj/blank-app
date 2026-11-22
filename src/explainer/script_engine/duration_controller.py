"""Keeps a script inside its target spoken duration (45-60s per spec section 8) and maps the
spec's six-beat timing table onto estimated seconds, the same way shorts/plan.py's word-count
windows keep the existing pipeline's Shorts in range - same idea, standalone implementation
since this is a separate engine.
"""
from __future__ import annotations

from typing import NamedTuple

# words/sec measured the same way shorts/plan.py documents its own figures (comment there:
# "Piper pace measured on the same paragraph"); kept as a separate constant here since this
# engine does not assume Piper specifically.
WORDS_PER_SEC = {"en": 2.7, "hi": 2.3}

BEATS = [
    ("hook", 0, 4),
    ("intro", 4, 12),
    ("concept", 12, 30),
    ("example", 30, 45),
    ("why_it_matters", 45, 55),
    ("ending", 55, 60),
]


class DurationCheck(NamedTuple):
    estimated_seconds: float
    target_min: float
    target_max: float
    ok: bool
    message: str


def estimate_seconds(word_count: int, lang: str) -> float:
    return word_count / WORDS_PER_SEC[lang]


def check_duration(word_count: int, lang: str, target_min: float = 45, target_max: float = 60) -> DurationCheck:
    secs = estimate_seconds(word_count, lang)
    if secs < target_min:
        return DurationCheck(secs, target_min, target_max, False, f"{secs:.1f}s estimated, below the {target_min}s floor - add detail")
    if secs > target_max:
        return DurationCheck(secs, target_min, target_max, False, f"{secs:.1f}s estimated, above the {target_max}s ceiling - trim")
    return DurationCheck(secs, target_min, target_max, True, f"{secs:.1f}s estimated, within {target_min}-{target_max}s")


def beat_for_second(t: float) -> str:
    for name, start, end in BEATS:
        if start <= t < end:
            return name
    return BEATS[-1][0]
