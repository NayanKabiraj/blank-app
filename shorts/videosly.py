"""Videosly horror Shorts (owner decision, 27 Nov 2026): one horror Short a day made by Videosly from a TOPIC ONLY.

Claude picks a new topic and sends it to Videosly as a plain `prompt` with the `horror-story` skill; Videosly writes the story, draws the pictures and records the
voice. Claude never sends a script or composition. When the video is rendered, Claude writes the title, description and tags (from the story Videosly wrote,
read back with videosly_open_video) and posts it to the channel with videosly_post_video. The procedure is `shorts/VIDEOSLY_HORROR_TASK.md`; this module only builds
and checks the data. Videosly is an MCP connector, so it is called by Claude, not by a workflow.

    python3 -m shorts.videosly request "a night-shift guard and a lift that stops on the wrong floor"   # the exact videosly_generate_video arguments
    python3 -m shorts.videosly check-meta meta.json       # title / description / tags / duration checks
    python3 -m shorts.videosly post-args meta.json VIDEO_ID CHANNEL_ID   # the exact videosly_post_video arguments
    python3 -m shorts.videosly record entry.json          # append to data/videosly/history.json
    python3 -m shorts.videosly recent                     # recent topics (never repeat)
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys

from . import config

SKILL = "horror-story"
DURATION = "medium"                 # Videosly's 60 s length; the finished video is accepted from 45 to 65 s
ASPECT = "9:16"
PRIVACY = os.getenv("VIDEOSLY_PRIVACY", "private").strip().lower()   # rule 6: private unless the owner changes it (public | unlisted | private)
HISTORY = config.DATA_DIR / "videosly" / "history.json"
MIN_SECONDS, MAX_SECONDS = 45.0, 65.0
BANNED_IN_TOPIC = re.compile(r"\b(blood|bloody|gore|gory|murder|kill(ed|er|ing)?|corpse|dead bod(y|ies)|suicide|rape|abuse|torture|mutilat\w*|massacre|school shooting|serial killer)\b", re.I)
REAL_WORLD = re.compile(r"\b(Instagram|TikTok|YouTube|Facebook|WhatsApp|Google|Amazon|Apple|Netflix|Disney|McDonald)\b|\b(President|Prime Minister)\b", re.I)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def history() -> list[dict]:
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []


def recent_topics(n: int = 20) -> list[str]:
    return [h.get("topic", "") for h in history()[-n:]]


def topic_problems(topic: str, past: list[str] | None = None) -> list[str]:
    p = []
    t = (topic or "").strip()
    if not 20 <= len(t) <= 220:
        p.append("topic must be one line of 20-220 characters: a person, an ordinary place and the one thing that is wrong")
    if "\n" in t:
        p.append("topic must be a single line (the story is written by Videosly, not by us)")
    if BANNED_IN_TOPIC.search(t):
        p.append("topic mentions gore or violence: bloodless suspense only, no harm to anyone (YouTube advertiser-friendly rules)")
    if REAL_WORLD.search(t):
        p.append("topic names a real brand, platform or office: invent the place, nothing real")
    if re.search(r"\b(child|children|kid|kids|baby|toddler)\b", t, re.I):
        p.append("no child in the topic (the skill allows no child in danger; keep adults)")
    for old in (past if past is not None else recent_topics(60)):
        a, b = set(_norm(t).split()), set(_norm(old).split())
        if a and b and len(a & b) / len(a | b) > 0.6:
            p.append(f"too close to an earlier topic: {old!r}")
            break
    return p


def request(topic: str, day: dt.date | None = None) -> dict:
    """The arguments for videosly_generate_video: a PROMPT and the skill, nothing else (no script, no composition, no title)."""
    day = day or dt.date.today()
    args = {"prompt": f"A horror story. {topic.strip().rstrip('.')}.", "skill": SKILL, "duration": DURATION, "aspectRatio": ASPECT,
            "idempotencyKey": f"horror-{day.isoformat()}-{hashlib.sha1(_norm(topic).encode()).hexdigest()[:8]}"}
    assert not {"script", "composition", "content", "title"} & set(args)
    return args


def meta_problems(meta: dict) -> list[str]:
    p = []
    title, desc, tags = meta.get("title", ""), meta.get("description", ""), meta.get("tags", [])
    if not 8 <= len(title) <= 65:
        p.append(f"title must be 8-65 characters (got {len(title)})")
    if "fiction" not in (title + " " + desc).lower():
        p.append("label it fiction in the title or the description ('A fictional story')")
    if not 5 <= len(tags) <= 8:
        p.append(f"5-8 tags (got {len(tags)})")
    if len(desc) < 80:
        p.append("description too short (80+ characters: first line makes sense alone, 2-3 hashtags, says it is a fictional AI-made story)")
    if not 2 <= len(re.findall(r"#\w+", desc)) <= 3:
        p.append("2-3 hashtags in the description")
    if "#Shorts" not in desc:
        p.append("add #Shorts to the description")
    if re.search(r"https?://", desc):
        p.append("no links in the description")
    sec = meta.get("duration_seconds")
    if sec is not None and not MIN_SECONDS <= float(sec) <= MAX_SECONDS:
        p.append(f"video is {float(sec):.1f} s: a Short must be {MIN_SECONDS:.0f}-{MAX_SECONDS:.0f} s (target 50-60)")
    return p


def post_args(meta: dict, video_id: str, channel_id: str) -> dict:
    """The arguments for videosly_post_video. aiGenerated stays true (YouTube's altered or synthetic content label)."""
    return {"videoId": video_id, "channelId": channel_id, "title": meta["title"], "description": meta["description"], "content": meta["description"],
            "tags": list(meta["tags"]), "privacy": PRIVACY, "aiGenerated": True}


def record(entry: dict) -> None:
    h = history()
    h.append({"date": entry.get("date") or dt.date.today().isoformat(), **{k: v for k, v in entry.items() if k != "date"}})
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    HISTORY.write_text(json.dumps(h, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def brief_line() -> str:
    rec = recent_topics(6)
    return ("VIDEOSLY HORROR (1 video a day, owner decision 27 Nov 2026): follow shorts/VIDEOSLY_HORROR_TASK.md - send ONLY a topic as a prompt with skill horror-story; Videosly writes and makes the video; "
            "you write the title, description and tags and post it (privacy " + PRIVACY + "). Recent horror topics: " + (" | ".join(t[:60] for t in rec) if rec else "none yet"))


def _cli(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 0
    cmd = argv[0]
    if cmd == "request" and len(argv) > 1:
        topic = " ".join(argv[1:])
        probs = topic_problems(topic)
        if probs:
            print("TOPIC PROBLEMS:\n  " + "\n  ".join(probs))
            return 1
        print(json.dumps(request(topic), ensure_ascii=False, indent=1))
    elif cmd == "check-meta" and len(argv) > 1:
        probs = meta_problems(json.load(open(argv[1], encoding="utf-8")))
        print("\n".join(probs) if probs else "meta OK")
        return 1 if probs else 0
    elif cmd == "post-args" and len(argv) > 3:
        print(json.dumps(post_args(json.load(open(argv[1], encoding="utf-8")), argv[2], argv[3]), ensure_ascii=False, indent=1))
    elif cmd == "record" and len(argv) > 1:
        record(json.load(open(argv[1], encoding="utf-8")))
        print("recorded")
    elif cmd == "recent":
        print("\n".join(recent_topics(20)) or "none yet")
    else:
        print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli(sys.argv[1:]))
