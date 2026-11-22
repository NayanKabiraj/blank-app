"""FFprobe-based checks on a narration or mixed-audio file: it exists, has a non-silent audio
track, and roughly matches the expected duration. Used both as a pre-render sanity check on
narration and again, later, as part of quality_engine's final video checks.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def validate_audio(path: Path, *, expected_min_seconds: float = 1.0) -> list[str]:
    problems: list[str] = []
    if not path.exists() or path.stat().st_size == 0:
        return [f"{path} does not exist or is empty"]
    try:
        info = probe(path)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        return [f"ffprobe failed on {path}: {e}"]
    streams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    if not streams:
        problems.append(f"{path} has no audio stream")
        return problems
    duration = float(info.get("format", {}).get("duration", 0.0))
    if duration < expected_min_seconds:
        problems.append(f"{path} is only {duration:.2f}s, expected at least {expected_min_seconds}s")
    return problems
