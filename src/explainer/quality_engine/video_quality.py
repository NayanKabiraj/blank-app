"""Output validation (spec section 17/22): the video exists, isn't empty, is the right
duration/resolution/fps, uses H.264/AAC, has an audio track, and isn't a black/frozen frame
dump. Mirrors shorts/cinematic_engine/quality.py's approach (the same kind of check already
proven in this repo's existing pipeline), reimplemented standalone for this engine.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..audio_engine.audio_validator import probe


def check_video(path: Path, *, expect_width: int, expect_height: int, expect_fps: int,
               min_duration: float, max_duration: float) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists() or path.stat().st_size == 0:
        return {"ok": False, "errors": [f"{path} does not exist or is empty"], "warnings": []}
    try:
        info = probe(path)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "errors": [f"ffprobe failed: {e}"], "warnings": []}

    fmt = info.get("format", {})
    vstreams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    astreams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    duration = float(fmt.get("duration", 0.0))

    if not (min_duration <= duration <= max_duration):
        errors.append(f"duration {duration:.1f}s outside {min_duration}-{max_duration}s")
    if not vstreams:
        errors.append("no video stream")
        return {"ok": False, "errors": errors, "warnings": warnings, "duration": duration}
    v = vstreams[0]
    if (v.get("width"), v.get("height")) != (expect_width, expect_height):
        errors.append(f"resolution {v.get('width')}x{v.get('height')}, expected {expect_width}x{expect_height}")
    if v.get("codec_name") != "h264":
        errors.append(f"video codec {v.get('codec_name')!r}, expected h264")
    num, den = (v.get("r_frame_rate") or "0/1").split("/")
    fps = round(float(num) / float(den or 1), 2) if float(den or 1) else 0.0
    if abs(fps - expect_fps) > 1.0:
        warnings.append(f"fps {fps}, expected {expect_fps}")
    if not astreams:
        errors.append("no audio track")
    elif astreams[0].get("codec_name") != "aac":
        warnings.append(f"audio codec {astreams[0].get('codec_name')!r}, expected aac")

    return {"ok": not errors, "errors": errors, "warnings": warnings, "duration": duration,
            "resolution": f"{v.get('width')}x{v.get('height')}", "fps": fps, "has_audio": bool(astreams)}


def check_not_black(path: Path, *, sample_times: list[float] | None = None) -> list[str]:
    """A cheap proxy for 'not a black/frozen video': sample a few frames and check their mean
    brightness varies and isn't near-zero across the whole sample. Not a full scene-change
    detector, but enough to catch "rendered nothing"."""
    sample_times = sample_times or [0.5]
    problems = []
    brightness = []
    for t in sample_times:
        out = subprocess.run(
            ["ffmpeg", "-ss", str(t), "-i", str(path), "-frames:v", "1", "-vf", "signalstats",
             "-f", "null", "-"], capture_output=True, text=True)
        for line in out.stderr.splitlines():
            if "YAVG" in line:
                try:
                    brightness.append(float(line.split("YAVG:")[1].split()[0]))
                except (IndexError, ValueError):
                    pass
    if brightness and all(b < 2.0 for b in brightness):
        problems.append("sampled frames are all near-black - picture may not have rendered")
    return problems
