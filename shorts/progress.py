"""Milestones and the weekly progress report (owner instruction, 24 Nov 2026; goal: strategy/monetization.md).

    python -m shorts.progress report        # snapshot the channel, update milestones, write reports/progress-<date>.md (+ reports/latest.md)
    python -m shorts.progress milestones    # print the milestone status from the latest data without writing anything

Data: data/channel_trends.json (YouTube Data + Analytics APIs, refreshed by channel-trends.yml / weekly-report.yml), data/history.json,
data/documentary_history.json, data/youtube_trending.json. State: data/progress_history.json (one snapshot per report + the date each milestone was first reached).
Nothing is invented: a metric the APIs did not return is shown as n/a and its milestone stays open.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

from . import channel_trends as ct
from . import config

ROOT = Path(__file__).resolve().parents[1]
MILESTONES = ROOT / "strategy" / "milestones.json"
HISTORY = config.DATA_DIR / "progress_history.json"
REPORTS = ROOT / "reports"


def _load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return default


def upload_stats(history: list, doc_history: list, today: dt.date) -> dict:
    """Uploads per day from our own history (a video id = uploaded) -> last-7-day counts by language/format and the current daily streak."""
    days: dict[str, dict] = {}
    seen: set[str] = set()                                   # a re-run of the same day repeats the same video id: count each video once
    for kind, rows in (("short", history), ("documentary", doc_history)):
        for e in rows:
            for lang, v in (e.get("videos") or {}).items() if kind == "short" else [("en", (e.get("videos") or {}).get("en") or {})]:
                if (v or {}).get("video_id") and v["video_id"] not in seen:
                    seen.add(v["video_id"])
                    d = days.setdefault(e["date"], {"short": 0, "documentary": 0, "en": 0, "hi": 0})
                    d[kind] += 1
                    d[lang if lang in ("en", "hi") else "en"] += 1
    week = [(today - dt.timedelta(days=i)).isoformat() for i in range(7)]
    tot = {k: sum(days.get(d, {}).get(k, 0) for d in week) for k in ("short", "documentary", "en", "hi")}
    streak = 0
    d = today
    if today.isoformat() not in days:                 # today's run may not have happened yet
        d = today - dt.timedelta(days=1)
    while d.isoformat() in days:
        streak += 1
        d -= dt.timedelta(days=1)
    return {"week": tot, "week_total": tot["short"] + tot["documentary"], "streak": streak}


def snapshot(data: dict, history: list, doc_history: list, today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    mon = ct.monetization(data) if data.get("available") else {}
    analytics = data.get("analytics", [])
    shorts = next((r for r in data.get("split", []) if r.get("creatorContentType") == "shorts"), {})
    tot = data.get("totals_365d") or {}
    s90 = data.get("shorts_90d") or {}
    up = upload_stats(history, doc_history, today)
    snap = {"date": today.isoformat(), "available": bool(data.get("available")),
            "subscribers": (data.get("channel") or {}).get("subscriberCount"),
            "total_views": (data.get("channel") or {}).get("viewCount"),
            "videos": (data.get("channel") or {}).get("videoCount"),
            "watch_hours_28d": mon.get("watch_hours_last_28d"),
            "watch_hours_365d": round(float(tot["minutes"]) / 60, 1) if tot.get("minutes") is not None else None,   # long-form only: the qualifying hours
            "shorts_watch_hours_365d": round(float(tot["shorts_minutes"]) / 60, 1) if tot.get("shorts_minutes") is not None else None,
            "shorts_views_28d": int(shorts.get("views", 0)) if shorts else None,
            "shorts_views_90d": int(s90["views"]) if s90.get("views") is not None else None,
            "shorts_avg_view_pct": shorts.get("averageViewPercentage"),
            "best_video_views": max([int(r.get("views") or 0) for r in analytics], default=None),
            "subs_per_1000_views": mon.get("subscribers_per_1000_views"),
            "uploads_7d": up["week_total"], "uploads_7d_detail": up["week"], "upload_streak_days": up["streak"]}
    return snap


def evaluate(snap: dict, ladders: list, reached: dict) -> list[dict]:
    """For each ladder: current value, milestones reached (with the first-seen date) and the next one with progress. Updates `reached` in place."""
    out = []
    for lad in ladders:
        val = snap.get(lad["key"])
        done, nxt = [], None
        for step in lad["steps"]:
            key = f"{lad['key']}>={step}"
            if val is not None and val >= step:
                reached.setdefault(key, snap["date"])
                done.append({"step": step, "date": reached[key], "mark": lad.get("marks", {}).get(str(step), "")})
            elif nxt is None:
                nxt = {"step": step, "mark": lad.get("marks", {}).get(str(step), "")}
        if nxt and val is not None:
            prev = done[-1]["step"] if done else 0
            nxt["progress"] = round(100 * (val - prev) / (nxt["step"] - prev), 1) if nxt["step"] > prev else 0.0
        out.append({"key": lad["key"], "label": lad["label"], "value": val, "reached": done, "next": nxt})
    return out


def _fmt(v, suffix=""):
    if v is None:
        return "n/a"
    return (f"{v:,.1f}".rstrip("0").rstrip(".") if isinstance(v, float) else f"{v:,}") + suffix


def _delta(cur, prev):
    if cur is None or prev is None:
        return ""
    d = cur - prev
    return f" ({'+' if d >= 0 else ''}{_fmt(round(d, 1) if isinstance(d, float) else d)} vs last report)"


def _bar(pct: float, width: int = 20) -> str:
    n = max(0, min(width, int(round(width * pct / 100))))
    return "█" * n + "░" * (width - n)


def render(snap: dict, prev: dict | None, status: list[dict], dig: dict, trend: dict, week_note: str = "") -> str:
    p = prev or {}
    L = [f"# Weekly progress report - {snap['date']}", "",
         "Goal: grow subscribers and watch time toward YouTube monetization, safely (`strategy/monetization.md`).", ""]
    if not snap["available"]:
        L += ["**Channel data NOT AVAILABLE this week** (" + str(dig.get("reason", "the YouTube APIs returned nothing")) + "). Milestones stay open; nothing is estimated.", ""]
    L += ["## Scoreboard", "", "| Metric | Now | Change |", "|---|---|---|"]
    for label, key in (("Subscribers", "subscribers"), ("Total views", "total_views"), ("Watch hours (Shorts + long-form), last 28 days", "watch_hours_28d"),
                       ("Qualifying watch hours (LONG-FORM only), last 365 days", "watch_hours_365d"), ("Shorts watch hours, last 365 days (do not count)", "shorts_watch_hours_365d"), ("Shorts views, last 28 days", "shorts_views_28d"),
                       ("Shorts views, last 90 days", "shorts_views_90d"), ("Shorts average viewed %", "shorts_avg_view_pct"),
                       ("Subscribers per 1,000 views", "subs_per_1000_views"), ("Most-viewed video, 28 days", "best_video_views"),
                       ("Uploads in the last 7 days", "uploads_7d"), ("Upload streak (days)", "upload_streak_days")):
        L.append(f"| {label} | {_fmt(snap.get(key))} | {_delta(snap.get(key), p.get(key)).strip(' ()') or '-'} |")
    d7 = snap.get("uploads_7d_detail", {})
    L += ["", f"Uploads this week: {d7.get('short', 0)} Shorts + {d7.get('documentary', 0)} documentaries; {d7.get('en', 0)} English, {d7.get('hi', 0)} Hindi (target 6 a day = 42 a week).", "",
          "## Milestones", ""]
    for m in status:
        if m["reached"]:
            last = m["reached"][-1]
            L.append(f"- **{m['label']}**: {_fmt(m['value'])} - reached {_fmt(last['step'])} on {last['date']}" + (f" ({last['mark']})" if last["mark"] else ""))
        else:
            L.append(f"- **{m['label']}**: {_fmt(m['value'])} - no milestone reached yet")
        if m["next"]:
            n = m["next"]
            L.append(f"  - next: {_fmt(n['step'])}" + (f" ({n['mark']})" if n["mark"] else "") + (f"  `{_bar(n['progress'])}` {n['progress']} %" if "progress" in n else ""))
    new = [f"{m['label']} {_fmt(r['step'])}" for m in status for r in m["reached"] if r["date"] == snap["date"]]
    L += ["", "**Reached this week:** " + (", ".join(new) if new else "nothing new."), ""]
    if dig.get("available"):
        L += ["## What worked and what did not (28 days)", ""]
        if dig.get("split"):
            L.append("- Shorts vs long-form: " + "; ".join(f"{r['creatorContentType']} {r['views']} views, {r['averageViewPercentage']} % viewed" for r in dig["split"]))
        for n, v in sorted((dig.get("niches") or {}).items(), key=lambda kv: -kv[1]["views_per_video"])[:6]:
            L.append(f"- {n}: {v['videos']} videos, {v['views_per_video']} views/video, viewed {_fmt(v['avg_view_pct'], ' %')}")
        L += [f"- Top: {t['title'][:60]} ({t['views']} views, {_fmt(t['avg_view_pct'], ' %')})" for t in dig.get("top", [])]
        L += [f"- Bottom: {t['title'][:60]} ({t['views']} views)" for t in dig.get("bottom", [])]
        L += [f"- Signal: {s}" for s in dig.get("signals", [])]
        L.append("")
    if trend.get("available"):
        L += ["## What YouTube is pushing", "", f"- Most-popular Science & Tech charts: {int(trend['share_under_60s'] * 100)} % under 60 s, median {trend['median_title_chars']}-character titles; recurring words: {', '.join(trend['recurring_words'][:8])}.", ""]
    L += ["## Next week", ""] + [f"- {x}" for x in next_week(snap, status)] + [""]
    if week_note:
        L += [week_note, ""]
    L += ["_Generated by `python -m shorts.progress report`; thresholds are checked against YouTube Help (see monetization.md), analytics numbers come from the YouTube APIs and are never estimated._"]
    return "\n".join(L) + "\n"


def next_week(snap: dict, status: list[dict]) -> list[str]:
    """Rule-based focus for next week (honest, from the numbers; the Sunday run adds judgment in learnings.md)."""
    out = []
    spk = snap.get("subs_per_1000_views")
    if spk is not None and spk < 2:
        out.append(f"Conversion is the bottleneck ({_fmt(spk)} subscribers per 1,000 views, target 2): put the series promise in the first 20 s of every Short and answer `next_video` in the pinned comment before adding more videos.")
    pct = snap.get("shorts_avg_view_pct")
    if pct is not None and pct < 50:
        out.append(f"Shorts are viewed {_fmt(pct)} % on average (target 50): shorten to 38-45 s and move the payoff before second 22.")
    if snap.get("uploads_7d", 0) < 30:
        out.append(f"Only {snap.get('uploads_7d', 0)} uploads this week (target 42): check the queue, the YouTube quota and any authorization banner before changing the plan.")
    nxt = [m for m in status if m["key"] == "subscribers" and m["next"]]
    if nxt:
        out.append(f"Next subscriber milestone: {_fmt(nxt[0]['next']['step'])} ({_fmt(nxt[0]['next']['step'] - (snap.get('subscribers') or 0))} to go).")
    return out or ["Keep the plan; review the numbers above."]


def run_report(today: dt.date | None = None, write: bool = True) -> str:
    today = today or dt.date.today()
    data = _load(ct.FILE, {"available": False, "reason": "data/channel_trends.json does not exist yet"})
    hist, doc = _load(config.HISTORY_FILE, []), _load(config.DATA_DIR / "documentary_history.json", [])
    state = _load(HISTORY, {"snapshots": [], "reached": {}})
    snap = snapshot(data, hist, doc, today)
    prev = state["snapshots"][-1] if state["snapshots"] else None
    ladders = _load(MILESTONES, {"ladders": []})["ladders"]
    status = evaluate(snap, ladders, state["reached"])
    dig = ct.digest(data, hist, doc)
    trend = ct.trending_digest(_load(ct.TRENDING_FILE, {}))
    text = render(snap, prev, status, dig, trend)
    if write:
        state["snapshots"] = [s for s in state["snapshots"] if s["date"] != snap["date"]] + [snap]
        config.DATA_DIR.mkdir(exist_ok=True)
        HISTORY.write_text(json.dumps(state, indent=1) + "\n", encoding="utf-8")
        REPORTS.mkdir(exist_ok=True)
        (REPORTS / f"progress-{snap['date']}.md").write_text(text, encoding="utf-8")
        (REPORTS / "latest.md").write_text(text, encoding="utf-8")
    return text


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd in ("report", "milestones"):
        print(run_report(write=(cmd == "report")))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
