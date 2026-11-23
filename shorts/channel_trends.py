"""The channel check that comes BEFORE research each day: how are the videos doing, and what should change?

    python -m shorts.channel_trends fetch      # YouTube Data + Analytics API -> data/channel_trends.json (run daily by channel-trends.yml)
    python -m shorts.channel_trends summary    # prints the digest the daily task reads (per niche, Shorts vs long-form, top/bottom videos)

It needs the YouTube sign-in to include the read-only scopes (python -m shorts.ytauth url asks for them) and the YouTube Analytics API
enabled in the Google Cloud project. If either is missing, `fetch` writes {"available": false, "reason": ...}; nothing is invented, and the
daily task records "Channel check: NOT AVAILABLE: <reason>" instead. Signals from a few videos are hints, not proof: the digest says so.
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path

from . import config

log = logging.getLogger("shorts.trends")
FILE = config.DATA_DIR / "channel_trends.json"


def _service(name: str, version: str):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    creds = Credentials(None, refresh_token=config.YT_REFRESH_TOKENS["en"], token_uri="https://oauth2.googleapis.com/token",
                        client_id=config.YT_CLIENT_ID, client_secret=config.YT_CLIENT_SECRET)   # no scopes: use what the token was granted
    return build(name, version, credentials=creds, cache_discovery=False)


def fetch(days: int = 28, max_videos: int = 50) -> dict:
    out = {"available": False, "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "days": days}
    if not (config.YT_CLIENT_ID and config.YT_CLIENT_SECRET and config.YT_REFRESH_TOKENS["en"]):
        out["reason"] = "no YouTube credentials in this environment"
        return out
    try:
        yt = _service("youtube", "v3")
        uploads = yt.channels().list(part="contentDetails,statistics", mine=True).execute()["items"][0]
        out["channel"] = {k: int(v) for k, v in uploads.get("statistics", {}).items() if str(v).isdigit()}
        pl = uploads["contentDetails"]["relatedPlaylists"]["uploads"]
        ids = [i["contentDetails"]["videoId"] for i in yt.playlistItems().list(part="contentDetails", playlistId=pl, maxResults=max_videos).execute().get("items", [])]
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
            "signals": signals, "analytics_note": data.get("analytics_reason")}


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
        return 0
    data = json.loads(FILE.read_text(encoding="utf-8")) if FILE.exists() else {"available": False, "reason": "data/channel_trends.json does not exist yet (channel-trends.yml has not run)"}
    print(json.dumps(digest(data, _load(config.HISTORY_FILE), _load(config.DATA_DIR / "documentary_history.json")), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
