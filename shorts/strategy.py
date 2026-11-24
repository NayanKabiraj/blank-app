"""The standing growth strategy in code: the researched-idea queue, open follow-ups and the "up next" line.

Every video is part of a cluster. The daily task starts from `python -m shorts.niches recent`, which now also lists
- `researched_queue`: concepts someone already researched and scored (strategy/research-queue.json) that are not made yet and whose
  window (a news hook with dates) is still open, and
- `open_follow_ups`: the follow-up ideas earlier videos promised and nobody has made.
Entries have a `status`: "researched" (dossier and facts checked, ready) or "idea" (a scored starting point: do the research gate and
fact-check first). A researched concept that fits today wins ties: it already passed the research gate, and series continuity is what brings viewers back.

    python -m shorts.strategy queue          # print what is open today
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys

from . import config

QUEUE_FILE = config.ROOT / "strategy" / "research-queue.json"


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9ऀ-ॿ ]+", " ", (s or "").lower())


def _covered(keywords: list[str], history: list[dict]) -> bool:
    topics = " ".join(_norm(h.get("topic", "")) for h in history)
    return any(_norm(k).strip() and _norm(k).strip() in topics for k in keywords)


def load_queue() -> list[dict]:
    try:
        return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def researched_queue(history: list[dict], today: dt.date | None = None) -> list[dict]:
    """Researched concepts still worth making today, best first (higher gate score, then the earlier window end)."""
    today = today or dt.date.today()
    out = []
    for q in load_queue():
        win = q.get("window") or {}
        start = dt.date.fromisoformat(win["from"]) if win.get("from") else dt.date.min
        end = dt.date.fromisoformat(win["to"]) if win.get("to") else dt.date.max
        if start <= today <= end and not _covered(q.get("match") or [q.get("topic", "")], history):
            out.append({k: q.get(k) for k in ("kind", "status", "topic", "niche", "cluster", "gate_score", "window", "title", "thumbnail_text",
                                              "hooks", "follow_ups", "next_video", "dossier", "notes")})
    # time-boxed researched concepts first (a news hook expires), then other researched ones, then bare ideas; best score first within each
    def rank(q):
        timed = bool((q.get("window") or {}).get("to"))
        tier = 0 if timed and q.get("status") != "idea" else 1 if q.get("status") != "idea" else 2
        return (tier, (q.get("window") or {}).get("to", "9999"), -(q.get("gate_score") or 0))
    return sorted(out, key=rank)


STOP = {"why", "how", "does", "what", "when", "the", "that", "with", "from", "your", "this", "are", "you", "did", "for", "and", "can", "will"}


def _tokens(text: str) -> set[str]:
    return {w for w in _norm(text).split() if len(w) > 2 and w not in STOP}


def open_follow_ups(history: list[dict], limit: int = 12) -> list[dict]:
    """Follow-up ideas promised by earlier videos that no later video covers (a later topic shares most of the idea's key words)."""
    out, seen = [], set()
    for i in range(len(history) - 1, -1, -1):
        h = history[i]
        later = [_tokens(x.get("topic", "")) for x in history[i + 1:]]
        for f in h.get("follow_ups") or []:
            key = " ".join(sorted(_tokens(f)))
            if not key or key in seen:
                continue
            seen.add(key)
            idea = _tokens(f)
            if not any(len(idea & t) >= max(2, round(len(idea) * 0.6)) for t in later):
                out.append({"idea": f, "from": h.get("topic"), "cluster": h.get("cluster", ""), "date": h.get("date")})
    return out[:limit]


def with_sources(description: str, research_summary: str, n: int = 3) -> str:
    """Appends a 'Sources:' line with up to n links found in the plan's research_summary (viewers and the algorithm both read the description)."""
    urls = []
    for u in re.findall(r"https?://[^\s,;)]+", research_summary or ""):
        u = u.rstrip(".")
        if u not in urls and "wikipedia" not in u:
            urls.append(u)
    if not urls or "sources:" in description.lower():
        return description
    return f"{description.rstrip()}\n\nSources:\n" + "\n".join(urls[:n])


def up_next(description: str, next_video: str, lang: str = "en") -> str:
    """The description with a pointer to the next video (viewers who finish one should be handed the next)."""
    next_video = (next_video or "").strip()
    if not next_video:
        return description
    label = "अगला वीडियो" if lang == "hi" else "Up next"
    return f"{description.rstrip()}\n\n{label}: {next_video}"


def with_subscribe(description: str, lang: str = "en") -> str:
    """A one-tap subscribe link (the ?sub_confirmation=1 link asks the viewer to confirm the subscription): conversion is the channel's bottleneck."""
    from . import config
    url = f"https://www.youtube.com/@{config.CHANNEL_HANDLE}?sub_confirmation=1"
    if url in description:
        return description
    label = "अगला एपिसोड मिस न करें, सब्सक्राइब करें" if lang == "hi" else "Subscribe so you don't miss the next episode"
    return f"{description.rstrip()}\n\n{label}: {url}"


def _cli() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "queue":
        hist = json.loads(config.HISTORY_FILE.read_text()) if config.HISTORY_FILE.exists() else []
        print(json.dumps({"researched_queue": researched_queue(hist), "open_follow_ups": open_follow_ups(hist)}, ensure_ascii=False, indent=2))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(_cli())
