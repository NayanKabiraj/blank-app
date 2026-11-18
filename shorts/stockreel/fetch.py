"""Stock photos from Wikimedia Commons (the same source and licence filter `shorts/director/stock.py` already
uses for thumbnails: Public domain / CC0 only, so no attribution is legally required, no API key, no signup).
A still photo becomes moving footage with a slow Ken Burns pan/zoom (`ken_burns_clip`) - real photography, never
an AI-generated image, and nothing to sign up for. A scene whose search finds nothing gets a plain gradient
instead (`placeholder_clip`), so a render never breaks for want of a match.

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


def download_photo(query: str, out_dir: Path, name: str = "stock") -> dict | None:
    """An image for `query`: an AI-generated picture if a source is configured (`aiframes.generate_image` -
    Pollinations/Hugging Face/a local model, tried in that order), else the best Wikimedia Commons
    public-domain/CC0 photo. None on any failure (offline, no match, nothing configured) - the caller falls
    back to `placeholder_clip`."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    got = aiframes.generate_image(query, out_dir / f"{name}.jpg", 1024, 1024)
    return got or stock.fetch_broad(query, out_dir, name)


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
    """A `duration`-second clip at w x h for `query`: a Ken-Burns-animated Commons photo, or a gradient
    placeholder when nothing was found. Returns (clip path, credit dict or None)."""
    with_photo = out.with_suffix(".photo.jpg")
    got = download_photo(query, out.parent, out.stem + "_photo")
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
