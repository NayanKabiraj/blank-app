"""Checks on generated subtitle cues (spec section 14): timing is monotonic and non-overlapping,
lines aren't absurdly long (mobile-safe), and Hindi cues actually contain Devanagari glyphs -
the same cheap-but-real check used in script_engine/hindi_generator.py, applied again here
since subtitle text can in principle diverge from the script (it doesn't today, but the check
is free and catches a future regression).
"""
from __future__ import annotations

from typing import List

from .subtitle_generator import SubtitleCue

MAX_CHARS_PER_CUE = 42   # readable in one line at mobile subtitle sizes
DEVANAGARI = range(0x0900, 0x0980)


def validate_cues(cues: List[SubtitleCue], lang: str) -> list[str]:
    problems: list[str] = []
    if not cues:
        return ["no subtitle cues generated"]
    for i, c in enumerate(cues):
        if c.end <= c.start:
            problems.append(f"cue {i}: end ({c.end}) not after start ({c.start})")
        if len(c.text) > MAX_CHARS_PER_CUE:
            problems.append(f"cue {i}: {len(c.text)} characters, over the {MAX_CHARS_PER_CUE}-char mobile-safe limit")
        if lang == "hi" and not any(ord(ch) in DEVANAGARI for ch in c.text):
            problems.append(f"cue {i}: Hindi subtitle has no Devanagari characters: {c.text!r}")
    for a, b in zip(cues, cues[1:]):
        if b.start < a.end - 0.05:
            problems.append(f"cues overlap: one ends {a.end}, next starts {b.start}")
    return problems
