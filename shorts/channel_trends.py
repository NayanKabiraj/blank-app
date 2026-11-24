"""The channel check that comes BEFORE research each day: how are the videos doing, and what should change?

    python -m shorts.channel_trends fetch      # YouTube Data + Analytics API -> data/channel_trends.json (run daily by channel-trends.yml)
    python -m shorts.channel_trends trending   # what YouTube itself is pushing (most-popular Education / Science charts, data/youtube_trending.json)
    python -m shorts.channel_trends summary    # prints the digest the daily task reads (per niche, Shorts vs long-form, top/bottom videos)

It needs the YouTube sign-in to include the read-only scopes (python -m shorts.ytauth url asks for them) and the YouTube Analytics API
enabled in the Google Cloud project. If either is missing, `fetch` writes {"available": false, "reason": ...}; nothing is invented, and the
daily task records "Channel check: NOT AVAILABLE: <reason>" instead. Signals from a few videos are hints, not proof: the digest says so.
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from . import config

log = logging.getLogger("shorts.trends")
FILE = config.DATA_DIR / "channel_trends.json"


def _service(name: str, version: str):
    from googleapiclient.discovery import build
    from . import ytauth
    creds = ytauth.credentials("en")   # the stored sign-in first, then the secret; no scopes: use what the token was granted
    return build(name, version, credentials=creds, cache_discovery=False)


def fetch(days: int = 28, max_videos: int = 200) -> dict:
    from . import ytauth
    out = {"available": False, "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "days": days}
    if not (config.YT_CLIENT_ID and config.YT_CLIENT_SECRET and ytauth.candidates("en")):
        out["reason"] = "no YouTube credentials in this environment"
        return out
    try:
        yt = _service("youtube", "v3")
        uploads = yt.channels().list(part="contentDetails,statistics", mine=True).execute()["items"][0]
        out["channel"] = {k: int(v) for k, v in uploads.get("statistics", {}).items() if str(v).isdigit()}
        pl = uploads["contentDetails"]["relatedPlaylists"]["uploads"]
        ids, token = [], None
        while len(ids) < max_videos:                       # every upload (50 per page), newest first
            page = yt.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=50, pageToken=token).execute()
            ids += [i["contentDetails"]["videoId"] for i in page.get("items", [])]
            token = page.get("nextPageToken")
            if not token:
                break
        ids = ids[:max_videos]
        vids = []
        for chunk in (ids[i:i + 50] for i in range(0, len(ids), 50)):
            for v in yt.videos().list(part="snippet,statistics,contentDetails,status", id=",".join(chunk)).execute().get("items", []):
                st = v.get("statistics", {})
                vids.append({"id": v["id"], "title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"], "duration": v["contentDetails"]["duration"],
                             "privacy": v.get("status", {}).get("privacyStatus"), "views": int(st.get("viewCount", 0)), "likes": int(st.get("likeCount", 0)), "comments": int(st.get("commentCount", 0))})
        out["videos"] = vids
        out["available"] = True
    except Exception as exc:  # noqa: BLE001
        out["reason"] = f"YouTube Data API: {str(exc)[:200]} (the sign-in needs the youtube.readonly scope: python -m shorts.ytauth url)"
        return out
    try:                                       # Analytics: per-video watch time and average view percentage
        an = _service("youtubeAnalytics", "v2")
        end = dt.date.today()
        start = end - dt.timedelta(days=days)
        rep = an.reports().query(ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(), dimensions="video", sort="-views", maxResults=50,
                                 metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained").execute()
        cols = [c["name"] for c in rep.get("columnHeaders", [])]
        out["analytics"] = [dict(zip(cols, row)) for row in rep.get("rows", [])]
        split = an.reports().query(ids="channel==MINE", startDate=start.isoformat(), endDate=end.isoformat(), dimensions="creatorContentType", metrics="views,estimatedMinutesWatched,averageViewPercentage").execute()
        cols = [c["name"] for c in split.get("columnHeaders", [])]
        out["split"] = [dict(zip(cols, row)) for row in split.get("rows", [])]
    except Exception as exc:  # noqa: BLE001
        out["analytics_reason"] = f"YouTube Analytics API: {str(exc)[:200]} (needs yt-analytics.readonly and the API enabled)"
    return out


def _index(history: list, doc_history: list) -> dict:
    idx = {}
    for kind, rows in (("short", history), ("documentary", doc_history)):
        for e in rows:
            vs = e.get("videos") or {}
            for lang, v in (vs.items() if kind == "short" else [("en", vs.get("en") or {})]):
                vid = (v or {}).get("video_id")
                if vid:
                    idx[vid] = {"niche": e.get("niche"), "topic": e.get("topic"), "cluster": e.get("cluster"), "kind": kind}
    return idx


# YouTube Partner Program thresholds (YouTube Help, checked 24 Nov 2026; third-party reports say they rise on 1 Feb 2027 to 8,000 watch hours or 20 M Shorts views - verify in YouTube Studio -> Earn)
YPP = {"fan_funding_subs": 500, "ads_subs": 1000, "ads_watch_hours_12m": 4000, "ads_shorts_views_90d": 10_000_000}


def monetization(data: dict) -> dict:
    """Progress toward the Partner Program from the 28-day data (pure function, tested). Projections are plain extrapolations, labelled as such."""
    ch = data.get("channel") or {}
    subs = int(ch.get("subscriberCount", 0))
    days = data.get("days") or 28
    minutes = sum(float(r.get("estimatedMinutesWatched") or 0) for r in data.get("analytics", []))
    shorts = next((r for r in data.get("split", []) if r.get("creatorContentType") == "shorts"), {})
    views = sum(int(r.get("views") or 0) for r in data.get("analytics", []))
    hours = round(minutes / 60, 1)
    per_year = hours * 365 / days
    not_public = [v["title"][:40] for v in data.get("videos", []) if v.get("privacy") not in (None, "public")]
    return {"subscribers": subs, "to_500": max(0, YPP["fan_funding_subs"] - subs), "to_1000": max(0, YPP["ads_subs"] - subs),
            "watch_hours_last_%dd" % days: hours, "watch_hours_if_pace_holds_12m": round(per_year), "needed_watch_hours_12m": YPP["ads_watch_hours_12m"],
            "shorts_views_last_%dd" % days: int(shorts.get("views", 0)), "needed_shorts_views_90d": YPP["ads_shorts_views_90d"],
            "subscribers_per_1000_views": round(1000 * float(ch.get("subscribersGained", 0) or sum(int(r.get("subscribersGained") or 0) for r in data.get("analytics", []))) / max(1, views), 2),
            "videos_not_public": len(not_public), "note": "growth lever = subscribers (the slowest requirement); thresholds in channel_trends.YPP, verify in YouTube Studio -> Earn"}


def digest(data: dict, history: list, doc_history: list) -> dict:
    """Per-niche / per-format aggregates joined to our own history, plus plain-language signals. Pure function (tested)."""
    if not data.get("available"):
        return {"available": False, "reason": data.get("reason", "no data")}
    idx = _index(history, doc_history)
    an = {r.get("video"): r for r in data.get("analytics", [])}
    rows = []
    for v in data.get("videos", []):
        meta = idx.get(v["id"], {})
        a = an.get(v["id"], {})
        rows.append({**v, **meta, "avg_view_pct": a.get("averageViewPercentage"), "minutes": a.get("estimatedMinutesWatched"), "subs": a.get("subscribersGained"), "window_views": a.get("views")})
    by_niche = defaultdict(list)
    by_kind = defaultdict(list)
    for r in rows:
        if r.get("niche"):
            by_niche[r["niche"]].append(r)
        if r.get("kind"):
            by_kind[r["kind"]].append(r)

    def agg(rs):
        pct = [r["avg_view_pct"] for r in rs if r.get("avg_view_pct") is not None]
        return {"videos": len(rs), "views_per_video": round(sum(r["views"] for r in rs) / len(rs), 1), "avg_view_pct": round(sum(pct) / len(pct), 1) if pct else None}
    niches = {k: agg(v) for k, v in by_niche.items()}
    kinds = {k: agg(v) for k, v in by_kind.items()}
    ranked = sorted(rows, key=lambda r: r["views"], reverse=True)
    signals = []
    if rows and len(rows) < 8:
        signals.append(f"Only {len(rows)} videos with data: treat everything below as hints, not proof.")
    enough = {k: v for k, v in niches.items() if v["videos"] >= 2}
    if len(enough) >= 2:
        best = max(enough.items(), key=lambda kv: kv[1]["views_per_video"])
        worst = min(enough.items(), key=lambda kv: kv[1]["views_per_video"])
        signals.append(f"Best niche so far: {best[0]} ({best[1]['views_per_video']} views/video); weakest: {worst[0]} ({worst[1]['views_per_video']}).")
    if len(kinds) == 2:
        s, d = kinds.get("short"), kinds.get("documentary")
        if s and d:
            signals.append(f"Shorts average {s['views_per_video']} views, documentaries {d['views_per_video']}: weigh effort against reach, and judge each format separately.")
    low = [r for r in rows if r.get("avg_view_pct") is not None and r["avg_view_pct"] < 40 and r.get("kind") == "short"]
    if low:
        signals.append(f"{len(low)} Shorts have an average view percentage under 40 %: look at their hooks (" + "; ".join(r["title"][:40] for r in low[:3]) + ").")
    return {"available": True, "generated": data.get("generated"), "channel": data.get("channel"), "split": data.get("split"), "niches": niches, "formats": kinds,
            "top": [{"title": r["title"], "views": r["views"], "avg_view_pct": r.get("avg_view_pct"), "niche": r.get("niche")} for r in ranked[:3]],
            "bottom": [{"title": r["title"], "views": r["views"], "avg_view_pct": r.get("avg_view_pct"), "niche": r.get("niche")} for r in ranked[-3:]],
            "monetization": monetization(data), "signals": signals, "analytics_note": data.get("analytics_reason")}


TRENDING_FILE = config.DATA_DIR / "youtube_trending.json"
REGIONS = ("US", "IN", "GB")
CATEGORIES = {"27": "Education", "28": "Science & Technology"}


def _seconds(iso: str) -> int:
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    h, mi, se = (int(x or 0) for x in m.groups()) if m else (0, 0, 0)
    return h * 3600 + mi * 60 + se


def fetch_trending(per_chart: int = 25) -> dict:
    """YouTube's own most-popular charts (Data API, 1 quota unit per call) for Education and Science & Technology in a few regions."""
    out = {"available": False, "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "charts": {}}
    try:
        yt = _service("youtube", "v3")
    except Exception as exc:  # noqa: BLE001
        out["reason"] = str(exc)[:200]
        return out
    for region in REGIONS:
        for cat, name in CATEGORIES.items():
            try:
                items = yt.videos().list(part="snippet,statistics,contentDetails", chart="mostPopular", regionCode=region, videoCategoryId=cat,
                                         maxResults=per_chart).execute().get("items", [])
            except Exception as exc:  # noqa: BLE001  (some region/category charts do not exist)
                out["charts"][f"{region}/{name}"] = {"error": str(exc)[:120]}
                continue
            out["charts"][f"{region}/{name}"] = [{"id": v["id"], "title": v["snippet"]["title"], "channel": v["snippet"]["channelTitle"],
                                                 "views": int(v.get("statistics", {}).get("viewCount", 0)), "seconds": _seconds(v["contentDetails"]["duration"]),
                                                 "published": v["snippet"]["publishedAt"][:10], "tags": v["snippet"].get("tags", [])[:6]} for v in items]
            out["available"] = out["available"] or bool(items)
    return out


def trending_digest(data: dict) -> dict:
    """Patterns in what YouTube itself is pushing (pure function, tested): title shapes, lengths, recurring words, top titles."""
    charts = {k: v for k, v in data.get("charts", {}).items() if isinstance(v, list) and v}
    if not charts:
        return {"available": False, "reason": data.get("reason", "no trending data yet (channel-trends.yml has not fetched it)")}
    rows = [dict(r, chart=k) for k, v in charts.items() for r in v]
    stop = set("the a an of to in and is it how why what this that for on with you your are was be from at as by or not do does".split())
    words = Counter(w for r in rows for w in re.findall(r"[a-z']{3,}", r["title"].lower()) if w not in stop)
    n = len(rows)
    return {"available": True, "generated": data.get("generated"), "videos": n,
            "share_questions": round(sum("?" in r["title"] for r in rows) / n, 2),
            "share_numbers": round(sum(bool(re.search(r"\d", r["title"])) for r in rows) / n, 2),
            "share_under_60s": round(sum(0 < r["seconds"] <= 60 for r in rows) / n, 2),
            "median_title_chars": sorted(len(r["title"]) for r in rows)[n // 2],
            "median_minutes": round(sorted(r["seconds"] for r in rows)[n // 2] / 60, 1),
            "recurring_words": [w for w, c in words.most_common(15) if c >= 3],
            "top": [{"chart": r["chart"], "title": r["title"][:80], "views": r["views"], "minutes": round(r["seconds"] / 60, 1)} for r in sorted(rows, key=lambda r: -r["views"])[:12]]}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "summary"
    if cmd == "fetch":
        data = fetch()
        FILE.parent.mkdir(parents=True, exist_ok=True)
        FILE.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        log.info("channel trends: available=%s %s", data["available"], data.get("reason", ""))
        tr = fetch_trending()
        TRENDING_FILE.write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
        log.info("youtube trending: available=%s %s", tr["available"], tr.get("reason", ""))
        return 0
    if cmd == "trending":
        td = json.loads(TRENDING_FILE.read_text(encoding="utf-8")) if TRENDING_FILE.exists() else {}
        print(json.dumps(trending_digest(td), ensure_ascii=False, indent=2))
        return 0
    data = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {"available": False, "reason": "data/channel_trends.json does not exist yet (channel-trends.yml has not run)"}
    print(json.dumps(digest(data, _load(config.HISTORY_FILE), _load(config.DATA_DIR / "documentary_history.json")), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
