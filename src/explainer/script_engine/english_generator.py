"""English-specific script writing: just the shared writer with lang='en' pinned, so callers
don't have to remember the language string and so English-only rules (if any accumulate here
later - e.g. a different idiom check) have a home."""
from __future__ import annotations

from pathlib import Path
from typing import List

from . import script_generator as _g


def write(topic_id: str, topic: str, lines: List[_g.ScriptLine], root: Path = _g.ROOT) -> Path:
    return _g.write_script(topic_id, topic, "en", lines, root)
