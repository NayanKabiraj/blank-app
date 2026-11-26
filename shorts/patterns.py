"""Follow what works, every day (owner instruction, 26 Nov 2026: "follow the pattern on which Shorts and videos are getting more views and change the strategy accordingly, don't wait for 2 weeks").

    python -m shorts.patterns            # analyse data/channel_trends.json + our history -> data/patterns.json and a short digest (channel-trends.yml runs it daily)
    python -m shorts.patterns --brief    # only the digest the daily run reads (shorts.runbrief prints it)

How it decides (no waiting period, no chasing noise):
* score = views per day since upload (videos at least 2 days old; YouTube's numbers lag about a day), averaged on a log scale so one viral video cannot dominate;
* groups = topic family (tech / space+nature / mind+body / story / india+other), language, cluster (series), length bucket, title shape;
* every group's estimate is shrunk toward the channel average by its sample size (a group with 1-2 videos moves the estimate only a little, a group with 6+ moves it a lot);
* the recommended slots for the day = best family, second family, and ONE explore slot (the least-sampled family) so the channel keeps learning;
* videos with at least twice the channel's median score are Part 2 candidates (their saved follow_ups are listed).
Small samples are labelled; nothing is invented, a missing number is n/a.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import re
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

from . import channel_trends as ct
from . import config

FILE = config.DATA_DIR / "patterns.json"
RETIRED = {"story"}       # owner decision 26 Nov 2026: the horror/story niche was dropped; old story videos are still analysed but never recommended
PRIOR = 2.0            # shrinkage strength: a group needs about 2 videos to count as much as the channel average
FAMILY = {"How Tech Works": "tech", "AI Explained": "tech", "Technology": "tech", "Space & Universe": "space+nature", "Earth & Nature": "space+nature", "Science Explained": "space+nature",
          "Brain & Psychology": "mind+body", "Human Body": "mind+body", "Horror & Suspense": "story", "Myth Busters": "myth"}
ALWAYS = ("myth",)        # owner decision 26 Nov 2026: Myth Busters is a standing family; with no data yet it is the explore slot until it has 3 videos
STORY = re.compile(r"horror|haunted|mystery|suspense|fictional story|hawel|हवेली|हॉरर|सस्पेंस|काल्पनिक", re.I)
DEV = re.compile("[ऀ-ॿ]")


def family(niche: str | None, title: str) -> str:
    if niche in FAMILY:
        return FAMILY[niche]
    if STORY.search(title or ""):
        return "story"
    return "india+other" if niche else "other"


def _lang(meta: dict, title: str) -> str:
    return meta.get("lang") or ("hi" if DEV.search(title or "") else "en")


def _seconds(iso: str) -> int:
    return ct._seconds(iso)


def title_shape(title: str) -> str:
    t = (title or "").lower().strip()
    kind = "question" if "?" in t else "statement"
    first = "what-if" if t.startswith(("what if", "क्या हो")) else "why" if t.startswith(("why", "क्यों")) else "how" if t.startswith(("how", "कैसे")) else "other"
    return f"{kind}/{first}" + ("/number" if re.search(r"\d", t) else "")


def length_bucket(seconds: int) -> str:
    return "long-form" if seconds > 75 else "short <=40s" if seconds <= 40 else "short 41-50s" if seconds <= 50 else "short 51-60s"


def rows(data: dict, history: list, doc_history: list, today: dt.date) -> list[dict]:
    idx = ct._index(history, doc_history)
    an = {r.get("video"): r for r in data.get("analytics", [])}
    out = []
    for v in data.get("videos", []):
        if v.get("privacy") not in (None, "public"):
            continue
        try:
            age = (today - dt.date.fromisoformat(v["published"][:10])).days
        except (KeyError, ValueError):
            continue
        if age < 2 or age > 60:                       # too fresh to judge (analytics lag) or too old to say anything about today's tastes
            continue
        m = idx.get(v["id"], {})
        a = an.get(v["id"], {})
        sec = _seconds(v.get("duration", ""))
        vpd = v["views"] / max(age, 1)
        out.append({"id": v["id"], "title": v["title"], "age": age, "views": v["views"], "vpd": vpd, "score": math.log1p(vpd), "viewed_pct": a.get("averageViewPercentage"), "subs": int(a.get("subscribersGained") or 0),
                    "family": family(m.get("niche"), v["title"]), "niche": m.get("niche"), "cluster": m.get("cluster"), "lang": _lang(m, v["title"]), "kind": m.get("kind") or ("short" if sec <= 75 else "documentary"),
                    "length": length_bucket(sec), "shape": title_shape(v["title"]), "follow_ups": m.get("follow_ups", []), "next_video": m.get("next_video", "")})
    return out


def groups(rs: list[dict], key: str, glob: float) -> list[dict]:
    g = defaultdict(list)
    for r in rs:
        if r.get(key):
            g[r[key]].append(r)
    res = []
    for name, items in g.items():
        n = len(items)
        mean = sum(i["score"] for i in items) / n
        est = (n * mean + PRIOR * glob) / (n + PRIOR)
        pct = [i["viewed_pct"] for i in items if i["viewed_pct"] is not None]
        res.append({"name": name, "n": n, "views_per_day": round(math.expm1(mean), 1), "estimate": round(est, 3), "lift": round(math.exp(est - glob), 2),
                    "viewed_pct": round(sum(pct) / len(pct), 1) if pct else None, "subs": sum(i["subs"] for i in items), "confidence": "low (n<3)" if n < 3 else "ok"})
    return sorted(res, key=lambda r: -r["estimate"])


def analyse(data: dict, history: list, doc_history: list, today: dt.date | None = None) -> dict:
    today = today or dt.date.today()
    if not data.get("available"):
        return {"available": False, "reason": data.get("reason", "no channel data")}
    rs = rows(data, history, doc_history, today)
    if len(rs) < 4:
        return {"available": False, "reason": f"only {len(rs)} videos between 2 and 60 days old: too little to follow a pattern yet"}
    glob = sum(r["score"] for r in rs) / len(rs)
    med_vpd = st.median(r["vpd"] for r in rs)
    fam = groups(rs, "family", glob)
    for name in ALWAYS:
        if name not in {f["name"] for f in fam}:                                         # a standing family with no data yet: shown, and picked as the explore slot (n=0)
            fam.append({"name": name, "n": 0, "views_per_day": None, "estimate": round(glob, 3), "lift": 1.0, "viewed_pct": None, "subs": 0, "confidence": "low (n<3)"})
    ranked = [f for f in fam if f["name"] not in ("other",) and f["name"] not in RETIRED]
    sure = [f for f in ranked if f["n"] >= 3]                                          # a family needs 3+ videos to win a main slot; thinner ones can only get the explore slot
    top = sure[:2] if len(sure) >= 2 else ranked[:2]
    rest = [f for f in ranked if f not in top]
    explore = min(rest, key=lambda f: (f["n"], -f["estimate"])) if rest else None       # the least-sampled of the remaining families keeps the channel learning
    slots = top + ([explore] if explore else [])
    winners = sorted((r for r in rs if r["vpd"] >= 2 * med_vpd and r["views"] >= 30), key=lambda r: -r["vpd"])[:5]
    return {"available": True, "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "videos": len(rs), "channel_median_views_per_day": round(med_vpd, 1),
            "families": fam, "languages": groups(rs, "lang", glob), "clusters": groups(rs, "cluster", glob)[:6], "length": groups(rs, "length", glob), "title_shape": groups(rs, "shape", glob)[:6],
            "recommended_slots": [{"slot": i + 1, "family": f["name"], "why": f"lift {f['lift']}x on {f['n']} videos ({f['confidence']})" + (" - explore slot: least sampled" if explore and f is explore else "")} for i, f in enumerate(slots)],
            "part2_candidates": [{"title": r["title"][:60], "views_per_day": round(r["vpd"], 1), "views": r["views"], "age_days": r["age"], "follow_ups": r["follow_ups"][:3], "next_video": r["next_video"]} for r in winners]}


def digest(p: dict) -> str:
    if not p.get("available"):
        return f"Patterns: n/a ({p.get('reason')})"
    f = p["families"]
    L = [f"Patterns (last 60 d, {p['videos']} videos >= 2 days old; score = views per day, shrunk by sample size; channel median {p['channel_median_views_per_day']}/day):",
         "  families: " + "; ".join(f"{x['name']} {x['lift']}x (n={x['n']}, {x['views_per_day']}/day, viewed {x['viewed_pct']}%)" for x in f),
         "  language: " + "; ".join(f"{x['name']} {x['lift']}x (n={x['n']})" for x in p["languages"]),
         "  length: " + "; ".join(f"{x['name']} {x['lift']}x (n={x['n']})" for x in p["length"]),
         "  title shapes: " + "; ".join(f"{x['name']} {x['lift']}x (n={x['n']})" for x in p["title_shape"][:4]),
         "  RECOMMENDED SLOTS TODAY (change the plan accordingly; override only with a stated reason): " + " | ".join(f"{s['slot']}) {s['family']} - {s['why']}" for s in p["recommended_slots"])]
    if p["part2_candidates"]:
        L.append("  Part 2 candidates (>= 2x the median): " + " | ".join(f"{c['title']} ({c['views_per_day']}/day; follow-ups: {c['follow_ups'][:2]})" for c in p["part2_candidates"]))
    return "\n".join(L)


def main() -> int:
    data = json.loads(ct.FILE.read_text(encoding="utf-8")) if ct.FILE.exists() else {"available": False, "reason": "no data/channel_trends.json"}
    load = lambda path: json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    p = analyse(data, load(config.HISTORY_FILE), load(config.DATA_DIR / "documentary_history.json"))
    if "--brief" not in sys.argv:
        FILE.parent.mkdir(exist_ok=True)
        FILE.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    print(digest(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
