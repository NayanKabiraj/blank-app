"""Copyright-free stock photos for thumbnails: Wikimedia Commons files that are public domain or CC0 (NASA images are the common case).

    fetch("full moon", dir)  ->  {"path": Path, "credit": "...", "source": "https://commons.wikimedia.org/wiki/File:..."} or None

Only files whose license is Public domain / CC0 / PD-USGov are accepted, so no attribution is legally required; the credit is still
written next to the image and into the video's history. Needs internet (GitHub Actions has it); returns None offline.
"""
from __future__ import annotations

import json
import logging
import re
import urllib.parse
import urllib.request
from pathlib import Path

log = logging.getLogger(__name__)
API = "https://commons.wikimedia.org/w/api.php"
UA = "faceless-explainers-thumbnail/1.0 (public-domain image lookup)"
FREE = re.compile(r"public domain|\bpd\b|pd-|cc0|cc-0|no known copyright", re.I)
NONFREE = re.compile(r"cc[- ]by|share ?alike|fair use|non-?free|gpl", re.I)


def _get(url: str, timeout: int = 25) -> bytes:
    import time
    import urllib.error
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 2:
                raise
            wait = int(e.headers.get("Retry-After", 20)) if e.headers else 20
            log.warning("Wikimedia rate limit (429), waiting %ss (attempt %d/3)", wait, attempt + 1)
            time.sleep(min(wait, 45))
    raise RuntimeError("unreachable")


# curated public-domain NASA files for the common subjects (checked in CI logs): title -> (focus x, focus y, zoom) for the round crop
CURATED = {"moon": ("File:Full moon partially obscured by atmosphere.jpg", (0.51, 0.54, 2.5)),
           "sun": ("File:The Sun by the Atmospheric Imaging Assembly of NASA's Solar Dynamics Observatory - 20100819.jpg", (0.5, 0.5, 2.2))}


def search(query: str, limit: int = 12, title: str | None = None) -> list[dict]:
    q = {"action": "query", "format": "json", "generator": "search", "gsrsearch": f'intitle:"{query}" filetype:bitmap', "gsrnamespace": 6, "gsrlimit": limit,
         "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 2000}
    if title:
        q = {"action": "query", "format": "json", "titles": title, "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 2000}
    data = json.loads(_get(API + "?" + urllib.parse.urlencode(q)))
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata") or {}
        lic = (meta.get("LicenseShortName") or {}).get("value", "") + " " + (meta.get("UsageTerms") or {}).get("value", "")
        if not FREE.search(lic) or NONFREE.search(lic):
            continue
        if ii.get("mime") not in ("image/jpeg", "image/png") or min(ii.get("width", 0), ii.get("height", 0)) < 700:
            continue
        artist = re.sub(r"<[^>]+>", "", (meta.get("Artist") or {}).get("value", "")).strip()
        bad = bool(re.search(r"atmosphere|horizon|rise|set\b|silhouette|tree|building|city|diagram|map|logo|icon|crater|surface|mountain|rover|landing|tower|eclipse|shuttle|launch|pad\b|rocket|apollo|station|aircraft|plane|bird|people|man\b|woman|flag|painting|drawing", p["title"], re.I))
        out.append({"bad": bad, "url": ii.get("thumburl") or ii["url"], "title": p["title"], "license": lic.strip(),
                    "credit": f"{artist or 'Unknown'} / Wikimedia Commons ({lic.strip()})", "source": ii.get("descriptionurl", "")})
    return sorted(out, key=lambda h: (h["bad"], not re.search(re.escape(query.split()[0]), h["title"], re.I), len(h["title"])))      # keep the search order, but plain subject photos before scenery


def fetch(query: str, out_dir: Path, name: str = "stock", subject: str | None = None) -> dict | None:
    """Download the best public-domain match for `query`. None on any failure (offline, no match): the caller falls back."""
    out_dir = Path(out_dir)
    try:
        focus = (0.5, 0.5, 1.0)
        hits = []
        if subject in CURATED:     # a known good photo first, the search is the fallback
            hits = search(query, title=CURATED[subject][0]); focus = CURATED[subject][1] if hits else focus
        hits = hits or search(query) or search(query.split()[0])    # no title match: the plain keyword
        log.info("Stock candidates for %r: %s", query, [h["title"] for h in hits[:5]])
        for hit in hits:
            ext = ".png" if hit["url"].lower().endswith(".png") else ".jpg"
            path = out_dir / f"{name}{ext}"
            out_dir.mkdir(parents=True, exist_ok=True)
            path.write_bytes(_get(hit["url"], 40))
            if path.stat().st_size < 20_000:
                continue
            (out_dir / f"{name}.credit.txt").write_text(f"{hit['credit']}\n{hit['source']}\n", encoding="utf-8")
            log.info("Stock image for %r: %s (%s)", query, hit["title"], hit["license"])
            return {"path": path, "credit": hit["credit"], "source": hit["source"], "focus": focus}
    except Exception as e:     # noqa: BLE001 - network, JSON, anything: thumbnails must never fail because of a photo
        log.warning("Stock image lookup failed for %r: %s", query, e)
    return None
