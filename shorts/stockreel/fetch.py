"""Turns a scene's search phrase into a clip. `clip_for` is the entry point the renderer calls; it tries, in
order: a real AI-generated video (`aiframes.generate_video`), two AI stills crossfaded into motion
(`crossfade_clip`), one AI or Wikimedia still animated with a Ken Burns pan/zoom (`ken_burns_clip`), and
finally a plain gradient (`placeholder_clip`) so a render never breaks for want of a match. The Wikimedia photo
(`shorts/director/stock.py`, Public domain/CC0 only) is always available with no API key or signup; the AI
steps are optional and only run when a source is configured (see `aiframes.py`).

    python -m shorts.stockreel.fetch "city skyline at night" --orientation portrait --out clip.mp4
"""
from __future__ import annotations

import argparse
import logging
import random
import subprocess
from pathlib import Path

from ..director import stock
from . import aiframes

log = logging.getLogger(__name__)


def ken_burns_clip(photo: Path, out: Path, duration: float, w: int, h: int, seed: int = 0, fps: int = 30) -> Path:
    """Animate a still photo into `duration` seconds of footage: a slow zoom/pan (alternating direction by seed)
    across a photo pre-scaled well above the target size, so the pan never runs out of image."""
    rng = random.Random(seed)
    zoom_in = rng.random() > 0.5
    z0, z1 = (1.0, 1.14) if zoom_in else (1.14, 1.0)
    # oversample so zoompan's internal scaling (it samples the source, not a pre-scaled frame) stays sharp
    big_w, big_h = w * 2, h * 2
    frames = max(2, int(duration * fps))
    dx = rng.uniform(-0.06, 0.06) * big_w
    expr_zoom = f"'{z0}+({z1}-{z0})*on/{frames}'"
    expr_x = f"'iw/2-(iw/zoom/2)+{dx:.1f}*on/{frames}'"
    expr_y = "'ih/2-(ih/zoom/2)'"
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(photo),
        "-vf", f"scale={big_w}:{big_h}:force_original_aspect_ratio=increase,crop={big_w}:{big_h},"
               f"zoompan=z={expr_zoom}:x={expr_x}:y={expr_y}:d={frames}:s={w}x{h}:fps={fps}",
        "-t", f"{duration:.2f}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out),
    ], check=True)
    return out


def _fit_video(raw: Path, out: Path, duration: float, w: int, h: int, fps: int) -> Path:
    """Cover-fit a downloaded video clip to w x h, then trim or loop it to exactly `duration` seconds."""
    vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps={fps}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", str(raw), "-t", f"{duration:.2f}",
                    "-vf", vf, "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)], check=True)
    return out


def crossfade_clip(photo1: Path, photo2: Path, out: Path, duration: float, w: int, h: int, seed: int = 0, fps: int = 30) -> Path:
    """Two AI stills of the same described scene, each gently Ken-Burns'd, crossfaded into one another - a
    cheap, fully local stand-in for real video motion: the picture visibly changes partway through instead of
    just panning across one frame."""
    overlap = min(0.8, duration * 0.3)
    half = duration / 2 + overlap / 2
    with_dir = out.parent
    a = ken_burns_clip(photo1, with_dir / f"{out.stem}_a.mp4", half, w, h, seed, fps)
    b = ken_burns_clip(photo2, with_dir / f"{out.stem}_b.mp4", half, w, h, seed + 1, fps)
    offset = max(0.0, half - overlap)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", a.name, "-i", b.name,
        "-filter_complex", f"[0:v][1:v]xfade=transition=fade:duration={overlap:.2f}:offset={offset:.2f},format=yuv420p",
        "-t", f"{duration:.2f}", "-c:v", "libx264", str(out),
    ], check=True, cwd=with_dir)
    return out


def placeholder_clip(out: Path, duration: float, w: int, h: int, seed: int = 0, fps: int = 30) -> Path:
    """A slow-drifting gradient (never a flat dead frame) for a scene whose stock search found nothing - the
    render must still produce a complete video."""
    rng = random.Random(seed)
    c1 = "0x%02x%02x%02x" % (20 + rng.randrange(40), 20 + rng.randrange(30), 40 + rng.randrange(60))
    c2 = "0x%02x%02x%02x" % (10 + rng.randrange(20), 10 + rng.randrange(20), 20 + rng.randrange(30))
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi",
        "-i", f"gradients=s={w}x{h}:c0={c1}:c1={c2}:duration={duration:.2f}:rate={fps}:speed=0.02",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out),
    ], check=True)
    return out


def clip_for(query: str, out: Path, w: int, h: int, duration: float, seed: int = 0, fps: int = 30) -> tuple[Path, dict | None]:
    """A `duration`-second clip at w x h for `query`, best first:

    1. a real AI-generated video clip (Pollinations, if configured) - actual motion, not a pan/zoom;
    2. two AI stills of the same scene, Ken-Burns'd and crossfaded together (only when an AI source is
       configured - crossfading two different real Wikimedia photos would just be a nonsensical jump cut);
    3. one AI or Wikimedia still, animated with a Ken Burns pan/zoom (the original, always-available path);
    4. a plain gradient placeholder when nothing was found at all.

    Returns (clip path, credit dict or None)."""
    raw = out.with_suffix(".src.mp4")
    vid = aiframes.generate_video(query, raw, w, h, duration)
    if vid:
        try:
            return _fit_video(vid["path"], out, duration, w, h, fps), vid
        except subprocess.SubprocessError as e:
            log.warning("Could not fit the AI video clip for %r, falling back: %s", query, e)
    if aiframes.any_source_configured():
        img1 = aiframes.generate_image(query, out.with_suffix(".a.jpg"), w, h)
        img2 = aiframes.generate_image(query, out.with_suffix(".b.jpg"), w, h)
        if img1 and img2:
            try:
                return crossfade_clip(img1["path"], img2["path"], out, duration, w, h, seed, fps), img1
            except subprocess.SubprocessError as e:
                log.warning("Could not blend the two AI stills for %r, falling back: %s", query, e)
        if img1:
            return ken_burns_clip(img1["path"], out, duration, w, h, seed, fps), img1
    got = stock.fetch_broad(query, out.parent, out.stem + "_photo")
    if not got:
        return placeholder_clip(out, duration, w, h, seed, fps), None
    return ken_burns_clip(got["path"], out, duration, w, h, seed, fps), got


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--orientation", default="portrait", choices=["portrait", "landscape"])
    ap.add_argument("--duration", type=float, default=4.0)
    ap.add_argument("--out", default="clip.mp4")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    w, h = (1080, 1920) if a.orientation == "portrait" else (1920, 1080)
    clip, credit = clip_for(a.query, Path(a.out), w, h, a.duration)
    print(clip, credit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
