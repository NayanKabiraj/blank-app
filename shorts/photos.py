"""Stock photos per scene for the cartoon2d style (a real photo behind the cartoon presenter).

Sources, in order: Pexels photos when PEXELS_API_KEY is set, then Wikimedia Commons (no key,
freely licensed). Uses the scene's English `visual_query`. Photos are scaled down with FFmpeg and
returned as data URIs for the renderer, with an attribution line for the video description.
Anything whose title suggests people, politics or news is skipped, like the footage search.
"""
from __future__ import annotations

import base64
import logging
import re
import subprocess
import urllib.error
import urllib.parse
from pathlib import Path

from . import config
from .visuals import COMMONS_API, _blocked, _download_raw, _get_json, _relevant, _strip_html

log = logging.getLogger(__name__)
_cache: dict[str, tuple[str, str | None] | None] = {}
PEOPLE = re.compile(r"\b(portrait|selfie|people|person|man|woman|men|women|girl|boy|child|children|"
                    r"kid|face|crowd|family|wedding|actor|actress|singer|player|team)\b", re.I)


def _pexels(query: str) -> list[tuple[str, str]]:
    url = "https://api.pexels.com/v1/search?" + urllib.parse.urlencode(
        {"query": query, "per_page": 8, "orientation": "portrait"})
    data = _get_json(url, {"Authorization": config.PEXELS_API_KEY})
    out = []
    for ph in data.get("photos", []):
        alt = ph.get("alt") or ""
        if PEOPLE.search(alt) or _blocked(alt):
            continue
        out.append((ph["src"].get("large2x") or ph["src"]["large"],
                    f"Photo by {ph.get('photographer', 'unknown')} on Pexels ({ph.get('url', '')})"))
    return out


def _commons(query: str) -> list[tuple[str, str]]:
    params = {
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
        "gsrlimit": 20, "gsrsearch": f"filetype:bitmap {query}",
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 1280,
        "iiextmetadatafilter": "LicenseShortName|Artist",
    }
    pages = _get_json(COMMONS_API + "?" + urllib.parse.urlencode(params)).get("query", {}).get("pages", {})
    out = []
    for p in sorted(pages.values(), key=lambda p: p.get("index", 99)):
        title = p.get("title", "")
        info = (p.get("imageinfo") or [{}])[0]
        if info.get("mime") not in ("image/jpeg", "image/png") or info.get("width", 0) < 900:
            continue
        if _blocked(title) or PEOPLE.search(title) or not _relevant(title, query):
            continue
        meta = info.get("extmetadata", {})
        artist = " ".join((_strip_html(meta.get("Artist", {}).get("value", "")) or "unknown author").split())[:80]
        lic = _strip_html(meta.get("LicenseShortName", {}).get("value", "")) or "see source"
        out.append((info.get("thumburl") or info["url"],
                    f"\"{title.removeprefix('File:')}\" by {artist}, {lic}, via Wikimedia Commons "
                    f"({info.get('descriptionurl', '')})"))
    return out


def _to_data_uri(src: Path, out: Path) -> str | None:
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
                        "-vf", "scale='min(1080,iw)':-2", "-frames:v", "1", "-q:v", "4", str(out)])
    if r.returncode != 0 or not out.exists():
        return None
    return "data:image/jpeg;base64," + base64.b64encode(out.read_bytes()).decode()


def fetch(query: str, work: Path, idx: int) -> tuple[str, str | None] | None:
    """(data URI, credit) for one scene's query, or None."""
    if not query:
        return None
    if query in _cache:
        return _cache[query]
    sources = ([("Pexels", _pexels)] if config.PEXELS_API_KEY else []) + [("Wikimedia Commons", _commons)]
    words = query.split()
    for name, search in sources:
        for q in dict.fromkeys([query, " ".join(words[:2]), " ".join(words[-2:])]):
            try:
                cands = search(q)
            except Exception as e:  # noqa: BLE001
                log.warning("%s photo search failed for %r: %s", name, q, e)
                break
            for url, credit in cands[:2]:
                raw = work / f"photo_{idx}.src"
                try:
                    if not _download_raw(url, raw):
                        continue
                except (urllib.error.URLError, OSError) as e:
                    log.warning("Photo download failed %s: %s", url, e)
                    continue
                uri = _to_data_uri(raw, work / f"photo_{idx}.jpg")
                if uri:
                    log.info("Photo for %r from %s", query, name)
                    _cache[query] = (uri, credit)
                    return _cache[query]
    log.info("No photo found for %r", query)
    _cache[query] = None
    return None
