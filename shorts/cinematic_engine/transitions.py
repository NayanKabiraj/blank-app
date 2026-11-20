"""Stitches each scene's rendered clip into one picture (`work/video.mp4`) with an FFmpeg `xfade`
crossfade between consecutive scenes - the "professional transitions" the cinematic look needs,
done entirely by FFmpeg so no per-frame Python cost is added for it.
"""
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

log = logging.getLogger(__name__)

# A few different xfade styles so a 6-9 scene Short doesn't crossfade the same way every time.
STYLES = ["fade", "fadeblack", "smoothleft", "smoothright", "circleopen", "diagtl"]


def _run(cmd, cwd=None):
    log.debug("$ %s", " ".join(map(str, cmd)))
    subprocess.run([str(c) for c in cmd], check=True, cwd=cwd)


def concat_xfade(clips: list[Path], durations: list[float], out: Path, fps: int, w: int, h: int,
                 fade: float = 0.45) -> None:
    """Concatenate `clips` (silent, same WxH/fps) into `out`, crossfading by `fade` seconds between
    each pair. Falls back to a hard concat for a single clip."""
    if len(clips) == 1:
        _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(clips[0]), "-c:v", "copy", str(out)])
        return
    fade = min(fade, min(durations) * 0.4)
    inputs = []
    for c in clips:
        inputs += ["-i", str(c)]
    chain, offset, label = [], 0.0, "0:v"
    for i in range(len(clips) - 1):
        offset += durations[i] - fade
        style = STYLES[i % len(STYLES)]
        nxt = f"v{i + 1}"
        chain.append(f"[{label}][{i + 1}:v]xfade=transition={style}:duration={fade:.3f}:offset={offset:.3f}[{nxt}]")
        label = nxt
    filt = ";".join(chain)
    _run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", filt, "-map", f"[{label}]",
          "-r", str(fps), "-s", f"{w}x{h}", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-crf", "20",
          "-preset", "medium", str(out)])
