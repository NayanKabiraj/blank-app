"""Where finished videos land, and the naming convention so EN/HI x vertical/landscape never
collide: generated/videos/<topic_id>/<lang>_<format>.mp4, plus the matching .srt next to it.
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def final_path(topic_id: str, lang: str, fmt: str, root: Path = ROOT) -> Path:
    out_dir = root / "generated" / "videos" / topic_id
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{lang}_{fmt}.mp4"


def copy_subtitle(srt_path: Path, topic_id: str, lang: str, fmt: str, root: Path = ROOT) -> Path:
    out_dir = root / "generated" / "videos" / topic_id
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{lang}_{fmt}.srt"
    shutil.copy2(srt_path, dest)
    return dest
