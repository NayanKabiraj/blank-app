"""Background footage per scene. Sources, in order:

1. Pexels (free stock video, best quality) when PEXELS_API_KEY is set.
2. Wikimedia Commons: freely licensed real footage, no API key needed. The clip's
   author and license are returned so they can be credited in the video description.
3. An animated gradient rendered with FFmpeg, only if nothing usable is found.
"""
from __future__ import annotations

import html
import json
import os
import logging
import random
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import config

log = logging.getLogger(__name__)
# Wikimedia asks bots for a descriptive User-Agent with a way to contact the operator:
# set the WIKIMEDIA_CONTACT variable (an email or URL) to include one.
_contact = os.getenv("WIKIMEDIA_CONTACT", "")
UA = "daily-shorts-bot/1.1 (GitHub Actions; python-urllib)" + (f" contact: {_contact}" if _contact else "")
COMMONS_DELAY = 3.0          # seconds between requests to Wikimedia (be polite)
_last_commons = 0.0
_commons_blocked = False     # set after a 429 so we stop asking for the rest of the run
_cache: dict[str, tuple[Path, str | None]] = {}  # query -> footage, reused across languages
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
MAX_BYTES = 150 * 1024 * 1024

PALETTES = [
    ("0x0f2027", "0x2c5364"), ("0x1d2b64", "0x8e44ad"), ("0x232526", "0x414345"),
    ("0x0b486b", "0xf56217"), ("0x141e30", "0x243b55"), ("0x42275a", "0x734b6d"),
    ("0x134e5e", "0x71b280"), ("0x3a1c71", "0xd76d77"),
]


def _get_json(url: str, headers: dict | None = None) -> dict:
    _throttle(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _throttle(url: str) -> None:
    global _last_commons
    if "wikimedia.org" in url:
        wait = COMMONS_DELAY - (time.monotonic() - _last_commons)
        if wait > 0:
            time.sleep(wait)
        _last_commons = time.monotonic()


def _download(url: str, out: Path) -> bool:
    _throttle(url)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r, open(out, "wb") as f:
        size = 0
        while chunk := r.read(1 << 20):
            size += len(chunk)
            if size > MAX_BYTES:
                return False
            f.write(chunk)
    # Make sure FFmpeg can actually decode it
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height", "-of", "csv=p=0", str(out)],
                           capture_output=True, text=True)
    return probe.returncode == 0 and "," in probe.stdout


# ------------------------------------------------------------------ Pexels
def _pexels(query: str, used: set[str]) -> list[tuple[str, str, str | None]]:
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
        {"query": query, "orientation": "portrait", "size": "medium", "per_page": 15})
    videos = _get_json(url, {"Authorization": config.PEXELS_API_KEY}).get("videos", [])
    out = []
    for v in videos:
        key = f"pexels:{v['id']}"
        if key in used or v.get("duration", 0) < 3:
            continue
        files = [f for f in v["video_files"]
                 if f.get("height") and f.get("width") and f["height"] > f["width"] and f["height"] >= 1280]
        if files:
            best = min(files, key=lambda f: abs(f["height"] - config.HEIGHT))
            out.append((key, best["link"], None))  # Pexels license: no attribution required
    return out


# ------------------------------------------------------------------ Wikimedia Commons
def _strip_html(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def _commons(query: str, used: set[str]) -> list[tuple[str, str, str | None]]:
    params = {
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
        "gsrlimit": 20, "gsrsearch": f"filetype:video {query}",
        "prop": "videoinfo", "viprop": "url|size|mime|extmetadata|derivatives",
        "viextmetadatafilter": "LicenseShortName|Artist|Credit",
    }
    pages = _get_json(COMMONS_API + "?" + urllib.parse.urlencode(params)).get("query", {}).get("pages", {})
    ranked = sorted(pages.values(), key=lambda p: p.get("index", 99))
    out = []
    for p in ranked:
        title = p.get("title", "")
        info = (p.get("videoinfo") or [{}])[0]
        key = f"commons:{title}"
        if key in used or not info.get("url"):
            continue
        if info.get("height", 0) < 480 or not 3 <= info.get("duration", 0) <= 1800:
            continue
        # Prefer a transcode around 720-1080p to keep downloads small
        url = info["url"]
        derivs = [d for d in info.get("derivatives", [])
                  if d.get("height") and 480 <= d["height"] <= 1080 and "src" in d]
        if derivs:  # ~720p is plenty after the vertical crop and keeps downloads small
            url = min(derivs, key=lambda d: abs(d["height"] - 720))["src"]
        elif info.get("size", 0) > MAX_BYTES:
            continue
        meta = info.get("extmetadata", {})
        artist = _strip_html(meta.get("Artist", {}).get("value", "")) or "unknown author"
        lic = _strip_html(meta.get("LicenseShortName", {}).get("value", "")) or "see source"
        name = title.removeprefix("File:")
        artist = " ".join(artist.split())[:80]
        credit = f"\"{name}\" by {artist}, {lic}, via Wikimedia Commons ({info.get('descriptionurl', '')})"
        out.append((key, url, credit))
    return out


# ------------------------------------------------------------------ fallback
def _gradient(out: Path, duration: float) -> Path:
    c0, c1 = random.choice(PALETTES)
    src = (f"gradients=s={config.WIDTH}x{config.HEIGHT}:c0={c0}:c1={c1}:"
           f"speed=0.015:rate={config.FPS}:duration={duration:.2f}")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", src,
                    "-vf", "noise=alls=6:allf=t", "-c:v", "libx264", "-preset", "veryfast",
                    "-pix_fmt", "yuv420p", str(out)], check=True)
    return out


def _queries(query: str) -> list[str]:
    words = query.split()
    qs = [query, " ".join(words[:2]), words[-1], words[0]]
    return list(dict.fromkeys(q for q in qs if q))


def fetch(query: str, out: Path, duration: float, used: set[str]) -> tuple[Path, str | None]:
    """Download footage for one scene. Returns (path, attribution or None)."""
    global _commons_blocked
    if query in _cache and _cache[query][0].exists():  # e.g. the Hindi video reusing English footage
        src, credit = _cache[query]
        shutil.copyfile(src, out)
        return out, credit
    sources = []
    if config.PEXELS_API_KEY:
        sources.append(("Pexels", _pexels))
    sources.append(("Wikimedia Commons", _commons))
    for name, search in sources:
        for q in _queries(query)[:3]:
            if name == "Wikimedia Commons" and _commons_blocked:
                break
            try:
                candidates = search(q, used)
            except Exception as e:  # noqa: BLE001
                log.warning("%s search failed for %r: %s", name, q, e)
                break
            for key, url, credit in candidates[:2]:
                try:
                    if _download(url, out):
                        used.add(key)
                        _cache[query] = (out, credit)
                        log.info("Footage for %r from %s (%s)", query, name, key)
                        return out, credit
                except urllib.error.HTTPError as e:
                    log.warning("Download failed (%s) %s", e.code, url)
                    if e.code == 429 and "wikimedia" in url:
                        retry = int(e.headers.get("Retry-After") or 0)
                        if 0 < retry <= 30:
                            time.sleep(retry)
                        else:
                            log.warning("Wikimedia is rate limiting; no more Commons requests this run")
                            _commons_blocked = True
                            break
                except Exception as e:  # noqa: BLE001
                    log.warning("Download failed %s: %s", url, e)
            if _commons_blocked and name == "Wikimedia Commons":
                break
    log.info("No footage found for %r, using generated background", query)
    return _gradient(out, duration), None
