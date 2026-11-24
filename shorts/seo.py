"""Free SEO research for the research step (owner request, 24 Nov 2026; goal: strategy/monetization.md). Three tools, no paid API:

    python -m shorts.seo suggest "how does gps work" [--hl en --gl US]      # YouTube autocomplete expansions: what people really type (use --hl hi --gl IN for Hindi)
    python -m shorts.seo outliers "how does gps work" [--n 15]              # yt-dlp metadata of the top search results: views vs channel size, length, title patterns
    python -m shorts.seo summary                                            # print data/seo/latest.json (written by the seo-research.yml workflow)
    python -m shorts.channel_trends summary                                 # includes `search_terms`: the searches that brought viewers to OUR videos (Analytics API)

Caveats: the autocomplete endpoint is undocumented and yt-dlp reads public pages, so both can break or be rate limited; keep volumes low (the workflow
runs a handful of queries), read public metadata only, never download videos. The sandbox cannot reach these hosts: run them through the
`seo-research.yml` workflow, which writes data/seo/latest.json for the daily task to read.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics as st
import sys
import time
from collections import Counter
from pathlib import Path

from . import config

SUGGEST_URL = "https://suggestqueries.google.com/complete/search"
OUT = config.DATA_DIR / "seo" / "latest.json"
STARTERS = ["how", "why", "what", "can", "does", "is"]
LETTERS = list("abcdefghiklmnoprstw")


def expansions(query: str) -> list[str]:
    """The seed itself, with question starters in front, and with letters after it (the usual autocomplete sweep)."""
    q = query.strip()
    return [q] + [f"{s} {q}" for s in STARTERS if not q.lower().startswith(s + " ")] + [f"{q} {c}" for c in LETTERS]


def parse_suggest(payload) -> list[str]:
    """['query', ['s1', 's2', ...]] (the Firefox-style response) -> the suggestions."""
    if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], list):
        return [str(x) for x in payload[1] if isinstance(x, str)]
    return []


def rank(batches: list[list[str]], seed: str, top: int = 40) -> list[dict]:
    """Earlier position in a response = more popular: score = sum of 1/(position+1) over every response; keeps only phrases that contain the seed's words."""
    words = set(re.findall(r"\w+", seed.lower()))
    score: Counter = Counter()
    for b in batches:
        for i, phrase in enumerate(b):
            if words & set(re.findall(r"\w+", phrase.lower())):
                score[phrase.lower().strip()] += 1.0 / (i + 1)
    return [{"phrase": p, "score": round(s, 2)} for p, s in score.most_common(top) if p != seed.lower().strip()]


def suggest(query: str, hl: str = "en", gl: str = "US", pause: float = 0.25) -> list[dict]:
    import requests
    batches = []
    for q in expansions(query):
        try:
            r = requests.get(SUGGEST_URL, params={"client": "firefox", "ds": "yt", "q": q, "hl": hl, "gl": gl}, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            batches.append(parse_suggest(r.json()))
        except Exception:  # noqa: BLE001  (a failed call only thins the list)
            continue
        time.sleep(pause)
    return rank(batches, query)


def outlier_digest(entries: list[dict], today_ord: int | None = None) -> dict:
    """Pure function (tested): from yt-dlp metadata of search results, the videos that beat their channel's size and the patterns of the group."""
    import datetime as dt
    now = dt.date.today() if today_ord is None else dt.date.fromordinal(today_ord)
    rows = []
    for e in entries:
        if not e or not e.get("view_count"):
            continue
        subs = e.get("channel_follower_count") or 0
        try:
            age = max(1, (now - dt.datetime.strptime(e.get("upload_date") or "", "%Y%m%d").date()).days)
        except ValueError:
            age = None
        rows.append({"title": e.get("title", ""), "channel": e.get("channel") or e.get("uploader") or "", "views": int(e["view_count"]), "subs": int(subs),
                     "ratio": round(e["view_count"] / max(subs, 1000), 1), "age_days": age, "seconds": int(e.get("duration") or 0), "tags": (e.get("tags") or [])[:6]})
    if not rows:
        return {"available": False, "reason": "no metadata returned"}
    out = sorted(rows, key=lambda r: -r["ratio"])
    shorts = [r for r in rows if 0 < r["seconds"] <= 60]
    words = Counter(w for r in rows for w in re.findall(r"[a-z']{4,}", r["title"].lower()))
    return {"available": True, "videos": len(rows), "median_seconds": int(st.median(r["seconds"] for r in rows)), "share_shorts": round(len(shorts) / len(rows), 2),
            "share_questions": round(sum("?" in r["title"] for r in rows) / len(rows), 2), "median_title_chars": int(st.median(len(r["title"]) for r in rows)),
            "recurring_words": [w for w, c in words.most_common(10) if c >= 3], "common_tags": [t for t, c in Counter(t.lower() for r in rows for t in r["tags"]).most_common(8) if c >= 2],
            "outliers": [r for r in out if r["ratio"] >= 2][:8], "top_by_views": sorted(rows, key=lambda r: -r["views"])[:5]}


def outliers(query: str, n: int = 15) -> dict:
    from yt_dlp import YoutubeDL
    opts = {"quiet": True, "no_warnings": True, "skip_download": True, "ignoreerrors": True, "socket_timeout": 20, "extractor_args": {"youtube": {"player_client": ["web"]}}}
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(f"ytsearch{n}:{query}", download=False) or {}
    return outlier_digest(info.get("entries") or [])


def run_queries(queries: list[str], hl: str, gl: str, n: int) -> dict:
    res = {"generated": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(timespec="seconds"), "queries": {}}
    for q in queries:
        item = {"suggest": suggest(q, hl, gl)[:30]}
        try:
            item["outliers"] = outliers(q, n)
        except Exception as exc:  # noqa: BLE001
            item["outliers"] = {"available": False, "reason": str(exc)[:160]}
        res["queries"][q] = item
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("suggest", "outliers", "run"):
        p = sub.add_parser(name)
        p.add_argument("query", help="one query (run: several separated by |)")
        p.add_argument("--hl", default="en")
        p.add_argument("--gl", default="US")
        p.add_argument("--n", type=int, default=15)
    sub.add_parser("summary")
    a = ap.parse_args()
    if a.cmd == "summary":
        print(OUT.read_text(encoding="utf-8") if OUT.exists() else "no data/seo/latest.json yet (run the seo-research.yml workflow)")
        return 0
    if a.cmd == "suggest":
        print(json.dumps(suggest(a.query, a.hl, a.gl), ensure_ascii=False, indent=1))
    elif a.cmd == "outliers":
        print(json.dumps(outliers(a.query, a.n), ensure_ascii=False, indent=1))
    else:
        res = run_queries([q.strip() for q in a.query.split("|") if q.strip()][:6], a.hl, a.gl, a.n)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(res, ensure_ascii=False, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
