"""Hindi-specific script writing: the shared writer with lang='hi' pinned, plus a Devanagari
sanity check (the spec's own warning in section 6: "never assume Hindi text will render
correctly without testing it" - this is the cheapest part of that, a script-level check; real
glyph-rendering is checked later by subtitle_engine/subtitle_validator.py and quality_engine).
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from . import script_generator as _g

DEVANAGARI = range(0x0900, 0x0980)


def is_devanagari(text: str) -> bool:
    return any(ord(ch) in DEVANAGARI for ch in text)


def write(topic_id: str, topic: str, lines: List[_g.ScriptLine], root: Path = _g.ROOT) -> Path:
    bad = [l.scene_id for l in lines if not is_devanagari(l.narration)]
    if bad:
        raise ValueError(f"Hindi script scenes with no Devanagari text: {', '.join(bad)}")
    return _g.write_script(topic_id, topic, "hi", lines, root)
