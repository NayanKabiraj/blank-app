"""Background footage per scene.

Uses free vertical stock video from Pexels when PEXELS_API_KEY is set; otherwise (or if no
match is found) renders an animated gradient background with FFmpeg.
"""
from __future__ import annotations

import json
import logging
import random
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

from . import config

log = logging.getLogger(__name__)

PALETTES = [
    ("0x0f2027", "0x2c5364"), ("0x1d2b64", "0x8e44ad"), ("0x232526", "0x414345"),
    ("0x0b486b", "0xf56217"), ("0x141e30", "0x243b55"), ("0x42275a", "0x734b6d"),
    ("0x134e5e", "0x71b280"), ("0x3a1c71", "0xd76d77"),
]


def _pexels(query: str, used: set[int]) -> str | None:
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
        {"query": query, "orientation": "portrait", "size": "medium", "per_page": 15}
    )
    req = urllib.request.Request(url, headers={"Authorization": config.PEXELS_API_KEY,
                                               "User-Agent": "shorts-bot"})
    with urllib.request.urlopen(req, timeout=30) as r:
        videos = json.load(r).get("videos", [])
    for v in videos:
        if v["id"] in used or v.get("duration", 0) < 3:
            continue
        files = [f for f in v["video_files"]
                 if f.get("height") and f.get("width") and f["height"] > f["width"] and f["height"] >= 1280]
        if not files:
            continue
        best = min(files, key=lambda f: abs(f["height"] - config.HEIGHT))
        used.add(v["id"])
        return best["link"]
    return None


def _gradient(out: Path, duration: float) -> Path:
    c0, c1 = random.choice(PALETTES)
    src = (f"gradients=s={config.WIDTH}x{config.HEIGHT}:c0={c0}:c1={c1}:"
           f"speed=0.015:rate={config.FPS}:duration={duration:.2f}")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", src,
                    "-vf", "noise=alls=6:allf=t", "-c:v", "libx264", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", str(out)], check=True)
    return out


def fetch(query: str, out: Path, duration: float, used: set[int]) -> Path:
    if config.PEXELS_API_KEY:
        for q in (query, " ".join(query.split()[:2]), query.split()[0]):
            try:
                link = _pexels(q, used)
                if link:
                    req = urllib.request.Request(link, headers={"User-Agent": "shorts-bot"})
                    with urllib.request.urlopen(req, timeout=120) as r, open(out, "wb") as f:
                        f.write(r.read())
                    return out
            except Exception as e:  # noqa: BLE001
                log.warning("Pexels lookup failed for %r: %s", q, e)
    log.info("Using generated background for %r", query)
    return _gradient(out, duration)
