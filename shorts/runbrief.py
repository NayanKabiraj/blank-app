"""One compact brief for the daily run (replaces reading ~10 files and running ~8 commands; ~900 tokens instead of ~15,000).

    python -m shorts.runbrief            # today's plan, auth/queue status, the generated Channel check line, milestones, trends, SEO age, recent topics, the researched queue, the learnings rules
    python -m shorts.runbrief --check    # only the generated `Channel check:` line for research_summary

Everything is computed from the repository data (nothing is typed by hand, nothing is estimated); a missing source says so.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
from pathlib import Path

from . import channel_trends as ct
from . import config, progress

ROOT = Path(__file__).resolve().parents[1]
IST = dt.timezone(dt.timedelta(hours=5, minutes=30))


def _load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return default


def check_line(data: dict, dig: dict, today: dt.date) -> str:
    """The `Channel check:` line, generated from the channel data (the changes made because of it stay Claude's to write)."""
    if not dig.get("available"):
        return f"Channel check: NOT AVAILABLE: {dig.get('reason', 'no data')}."
    ch, mon = dig.get("channel") or {}, dig.get("monetization") or {}
    split = {r["creatorContentType"]: r for r in dig.get("split") or []}
    sh, lf = split.get("shorts", {}), split.get("videoOnDemand", {})
    top = "; ".join(f"{t['title'][:32]} {t['views']}" for t in dig.get("top", [])[:3])
    return (f"Channel check: {today.isoformat()} (channel_trends, YouTube Analytics 28 d): {ch.get('subscriberCount')} subscribers, Shorts {sh.get('views', 'n/a')} views / {round(sh.get('averageViewPercentage', 0), 1) or 'n/a'} % viewed, "
            f"long-form {lf.get('views', 'n/a')} views / {round(lf.get('averageViewPercentage', 0), 1) or 'n/a'} % viewed, {mon.get('subscribers_per_1000_views', 'n/a')} subscribers per 1,000 views; top: {top}. Changes made because of it: ")


def _rules(learn: Path) -> list[str]:
    if not learn.exists():
        return []
    text = learn.read_text(encoding="utf-8")
    sec = text.split("## Rules", 1)[-1].split("## Tests", 1)[0]
    return [re.sub(r"\*\*|`", "", ln)[:150] for ln in sec.splitlines() if re.match(r"\d+\. ", ln.strip())]


def target(learn: Path) -> str:
    m = re.search(r"CURRENT DAILY TARGET: ([^*.]*(?:\([^)]*\))?)", learn.read_text(encoding="utf-8")) if learn.exists() else None
    return m.group(1).strip() if m else "see strategy/learnings.md DECISION"


def brief(now: dt.datetime | None = None) -> str:
    from . import ytauth
    now = now or dt.datetime.now(IST)
    today = now.date()
    data = _load(ct.FILE, {"available": False})
    hist, doc = _load(config.HISTORY_FILE, []), _load(config.DATA_DIR / "documentary_history.json", [])
    dig = ct.digest(data, hist, doc)
    sunday = today.weekday() == 6
    doc_day = sunday or (today.weekday() == 2 and today >= dt.date(2026, 12, 9))          # long-form test (owner request 26 Nov): Sunday, plus Wednesday from 9 Dec
    L = [f"# Run brief {today.isoformat()} ({today.strftime('%A')} IST)",
         f"Plan today: {'DOCUMENTARY DAY (' + today.strftime('%A') + '): 2 Short topics + 1 search-led long-form of 6-8 min built on a winning Short topic (a Part 2 candidate or a top family topic), each EN+HI' if doc_day else '3 Short topics, each EN+HI'}; target: {target(ROOT / 'strategy' / 'learnings.md')}.",
         "Auth: " + (ytauth.banner() or "OK (no authorization pending)"),
         f"Queue: {len(list((config.VIDEOS_DIR / 'unpublished').glob('*/meta.json'))) if (config.VIDEOS_DIR / 'unpublished').is_dir() else 0} videos waiting in videos/unpublished/.", "",
         check_line(data, dig, today)]
    mon = dig.get("monetization") or {}
    if mon:
        L.append(f"Scoreboard: {mon['subscribers']} subscribers ({mon['to_1000']} to 1,000), watch hours 28 d {mon.get('watch_hours_last_28d')} (long-form only counts), Shorts views 28 d {mon.get('shorts_views_last_28d')}; top subscriber videos: {[t['title'][:30] for t in mon.get('top_subscriber_videos', [])]}.")
    L += ["Signals: " + " | ".join(dig.get("signals", [])[:3]) if dig.get("available") else "Signals: n/a", ""]
    try:
        snap0 = progress.snapshot(data, hist, doc, today)
        el = progress.tier_progress(snap0)
        st = (data.get("channel_status") or {})
        L.append(f"Partner Program eligibility (computed; the slowest requirement decides): fan-funding tier {el['fan']} % , ads tier {el['ads']} % ; subscribers {snap0.get('subscribers')}, long-form hours 365 d {snap0.get('watch_hours_365d')}, Shorts views 90 d {snap0.get('shorts_views_90d')}; "
                 f"isChannelMonetizationEnabled={st.get('isChannelMonetizationEnabled', 'n/a')}. Goal: move the slowest requirement, i.e. subscribers and long-form hours, not Shorts volume.")
    except Exception as exc:  # noqa: BLE001
        L.append(f"Eligibility: n/a ({str(exc)[:60]})")
    try:
        state = _load(progress.HISTORY, {"snapshots": [], "reached": {}})
        snap = progress.snapshot(data, hist, doc, today)
        st = progress.evaluate(snap, _load(progress.MILESTONES, {"ladders": []})["ladders"], dict(state["reached"]))
        L.append("Milestones: " + "; ".join(f"{m['label'][:28]} {progress._fmt(m['value'])}" + (f" -> next {progress._fmt(m['next']['step'])}" if m["next"] else "") for m in st))
    except Exception as exc:  # noqa: BLE001
        L.append(f"Milestones: n/a ({str(exc)[:60]})")
    try:
        from . import patterns
        L += ["", patterns.digest(patterns.analyse(data, hist, doc, today))]
    except Exception as exc:  # noqa: BLE001
        L.append(f"Patterns: n/a ({str(exc)[:60]})")
    tr = ct.trending_digest(_load(ct.TRENDING_FILE, {}))
    L.append("Trending (YouTube Science & Tech charts): " + (f"{int(tr['share_under_60s'] * 100)} % under 60 s, median title {tr['median_title_chars']} chars, words {', '.join(tr['recurring_words'][:6])}" if tr.get("available") else "n/a"))
    seo = ROOT / "data" / "seo" / "latest.json"
    L.append("SEO data: " + (f"data/seo/latest.json from {_load(seo, {}).get('generated', '?')} (queries: {', '.join(_load(seo, {}).get('queries', {}))[:120]})" if seo.exists() else "none yet (dispatch seo-research.yml per candidate topic)"))
    L += ["", "Recent topics (never repeat): " + " | ".join(dict.fromkeys(f"{e['date'][5:]} {e['topic'][:46]}" for e in (hist[-14:] + doc[-4:])))]
    q = [e for e in _load(ROOT / "strategy" / "research-queue.json", []) if e.get("status") in ("researched", "ready")]
    L.append("Researched queue (prefer these; read the dossier, re-verify only items marked recheck): " + (" | ".join(f"{e['topic'][:44]} [{e.get('niche', '')}, {e.get('kind', '')}, gate {e.get('gate_score', '?')}, {e.get('dossier', '')}]" for e in q[:12]) if q else "empty (use fresh research)"))
    rules = _rules(ROOT / "strategy" / "learnings.md")
    L += ["", "Learnings rules: " + " || ".join(rules)] if rules else []
    L += ["", "Topic slots: follow the RECOMMENDED SLOTS above (they come from what is getting views now); override only with a stated reason in `Growth:`; keep the day's videos different in structure and angle. research_summary must contain: Candidates (scored), Titles, Thumbnails, Hooks, 'Claims:', 'Gap:', 'Channel check:' (use the generated line), 'Learning applied:', 'Growth:' (lever + policy check). Scene 1 hook, scene 2 intro (Shorts <= 22 words), thumbnail_question, title <= 65, 5-8 tags, 2-3 hashtags; english + hindi blocks, same scenes, same animation_pack."]
    return "\n".join(L)


def main() -> int:
    if "--check" in sys.argv:
        data = _load(ct.FILE, {"available": False})
        print(check_line(data, ct.digest(data, _load(config.HISTORY_FILE, []), _load(config.DATA_DIR / "documentary_history.json", [])), dt.datetime.now(IST).date()))
        return 0
    print(brief())
    return 0


if __name__ == "__main__":
    sys.exit(main())
