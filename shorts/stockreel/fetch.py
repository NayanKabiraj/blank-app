"""Stock video clips from Pexels (https://www.pexels.com/api/): free, no attribution required, real camera
footage only (never an AI-generated clip, keeping the channel's no-fabricated-imagery rule). Needs `PEXELS_API_KEY`
(a free key from pexels.com/api); without it, or offline, every call here returns None and the caller falls back
to a plain colour clip (see `placeholder_clip`), so a missing key never breaks a render.

    python -m shorts.stockreel.fetch "city skyline at night" --orientation portrait --out clip.mp4
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

log = logging.getLogger(__name__)
API = "https://api.pexels.com/videos/search"
UA = "faceless-explainers-stockreel/1.0"


def api_key() -> str:
    return os.environ.get("PEXELS_API_KEY", "")


def search(query: str, orientation: str = "portrait", per_page: int = 6) -> list[dict]:
    """Up to `per_page` Pexels video results for `query` (orientation: portrait/landscape/square). Empty list on
    any failure (no key, offline, rate limit, no match) - never raises."""
    key = api_key()
    if not key:
        return []
    import urllib.parse
    url = API + "?" + urllib.parse.urlencode({"query": query, "orientation": orientation, "per_page": per_page, "size": "medium"})
    try:
        req = urllib.request.Request(url, headers={"Authorization": key, "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read())
        return data.get("videos", [])
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
        log.warning("Pexels search failed for %r: %s", query, e)
        return []


def _best_file(video: dict, orientation: str) -> dict | None:
    """The smallest file at least 720px on its short side, in the right shape - small enough to download quickly,
    large enough to upscale cleanly to 1080x1920 or 1920x1080."""
    want_portrait = orientation == "portrait"
    files = [f for f in video.get("video_files", []) if f.get("width") and f.get("height")
             and (f["height"] > f["width"]) == want_portrait and min(f["width"], f["height"]) >= 540]
    if not files:
        files = [f for f in video.get("video_files", []) if f.get("width") and f.get("height")]
    return min(files, key=lambda f: f["width"] * f["height"]) if files else None


def download_clip(query: str, out: Path, orientation: str = "portrait", min_duration: float = 2.0, seed: int = 0) -> Path | None:
    """The best-matching Pexels clip for `query`, downloaded to `out`. None if nothing usable was found (caller
    falls back to `placeholder_clip`). `seed` picks among the top results so repeated scenes in one topic do not
    all grab the first hit."""
    hits = [v for v in search(query, orientation) if v.get("duration", 0) >= min_duration] or search(query, orientation)
    if not hits:
        return None
    video = hits[seed % len(hits)]
    f = _best_file(video, orientation)
    if not f:
        return None
    try:
        urllib.request.urlretrieve(f["link"], out)  # noqa: S310 - a Pexels CDN URL from their own API response
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        log.warning("Pexels download failed for %r: %s", query, e)
        return None
    if not out.exists() or out.stat().st_size < 20_000:
        return None
    log.info("Stock clip for %r: Pexels video %s by %s (free to use, no attribution required)",
             query, video.get("id"), (video.get("user") or {}).get("name", "?"))
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--orientation", default="portrait", choices=["portrait", "landscape", "square"])
    ap.add_argument("--out", default="clip.mp4")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    p = download_clip(a.query, Path(a.out), a.orientation)
    if not p:
        log.error("No clip found for %r (check PEXELS_API_KEY)", a.query)
        return 1
    print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
