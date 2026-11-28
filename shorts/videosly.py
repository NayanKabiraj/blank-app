"""Videosly Shorts (owner decisions 27-28 Nov 2026): a horror series and a mystery/crime series, one of each a day, made through the Videosly MCP connector.

Since 28 Nov 2026 the connector no longer accepts a topic: Claude WRITES the composition (narration + a caption per picture + title + description) from the Videosly skill
(`horror-story` / `short-mystery`) and the `dopamine-storyteller` skill; Videosly draws the pictures, records the voice and renders. Claude then posts it with
videosly_post_video. The procedure is `shorts/VIDEOSLY_HORROR_TASK.md`; this module builds and checks the data. Videosly is an MCP connector, so Claude calls it, not a workflow.

    python3 -m shorts.videosly series                   # the two series (skill, voice, labels)
    python3 -m shorts.videosly check-comp series comp.json   # validate a composition file {composition,title,description,hashtags}; prints the generate args
    python3 -m shorts.videosly request "a night-shift guard and a lift that stops on the wrong floor"   # (legacy) topic checks
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

SERIES = {
    "horror": {"skill": "horror-story", "voice": os.getenv("VIDEOSLY_HORROR_VOICE", "Mortimer"), "name": "Quiet Dark",
               "label": "A fictional AI-made horror story", "hashtags": "#Shorts #HorrorStory #Fiction", "style": ""},
    "mystery": {"skill": "short-mystery", "voice": os.getenv("VIDEOSLY_MYSTERY_VOICE", ""), "name": "The Fair Clue",
                "label": "A fictional AI-made mystery", "hashtags": "#Shorts #Mystery #Fiction",
                "style": "Warm graphic-novel illustration, clean ink outlines, flat muted colours with golden evening light, quiet suspenseful mood"},
}
SKILL = "horror-story"
DURATION = "medium"                 # Videosly's 60 s length; the finished length is only recorded, never a reason to stop the post (owner decision 27 Nov 2026)
ASPECT = "9:16"
PRIVACY = os.getenv("VIDEOSLY_PRIVACY", "private").strip().lower()   # rule 6: private unless the owner changes it (public | unlisted | private)
HISTORY = config.DATA_DIR / "videosly" / "history.json"
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


BAD_NARRATION = re.compile(r"\b(blood|bloody|gore|gory|corpse|suicide|rape|torture|mutilat\w*|massacre)\b", re.I)


def composition_problems(series: str, args: dict) -> list[str]:
    """Checks a {composition,title,description,hashtags} dict before videosly_generate_video (no gore, no child in danger, fair structure, 9:16 pictures). Length is advisory (about 150-175 words = 60 s)."""
    p = []
    if series not in SERIES:
        return [f"series must be one of {sorted(SERIES)}"]
    c = args.get("composition") or {}
    segs = c.get("segments") or []
    if c.get("language") not in ("en", "hi"):
        p.append("composition.language must be 'en' or 'hi' (horror is made in both; the Hindi one has Devanagari narration, English captions, the same Mortimer voice)")
    if not segs or not segs[0].get("images"):
        p.append("the first segment needs a picture")
    words = sum(len(x.get("narration", "").split()) for x in segs)
    if not 110 <= words <= 190:
        p.append(f"narration is {words} words (advisory: 140-175 words is about 60 s; Shorts max 3 minutes)")
    names = set((c.get("references") or {}))
    for i, sg in enumerate(segs, 1):
        n = sg.get("narration", "")
        if not n or len(n) > 2000:
            p.append(f"segment {i}: narration empty or over 2000 characters")
        if BAD_NARRATION.search(n) or re.search(r"\b(child|children|kid|baby|toddler)\b", n, re.I):
            p.append(f"segment {i}: gore or a child in the narration (not allowed)")
        if re.search(r"https?://|#\w+", n):
            p.append(f"segment {i}: links or hashtags would be read aloud")
        for cap in sg.get("images", []):
            if not 150 <= len(cap) <= 2500:
                p.append(f"segment {i}: a caption must be 150-2500 characters (60-100 words + the place)")
            if "The place:" not in cap:
                p.append(f"segment {i}: end each caption with the same 'The place:' sentence")
            for m in re.findall(r"@([a-z0-9\-]+)", cap):
                if m not in names and not m.startswith("shot"):
                    p.append(f"segment {i}: @{m} is not in references")
    for k in ("title", "description"):
        if not args.get(k):
            p.append(f"{k} is required by videosly_generate_video")
    if len(args.get("title", "")) > 65:
        p.append("title over 65 characters")
    if not 5 <= len(args.get("hashtags", [])) <= 8:
        p.append("5-8 hashtags (no # sign)")
    return p


def generate_args(series: str, args: dict, day: dt.date | None = None) -> dict:
    """The exact videosly_generate_video arguments for a series: composition + skill + title + description + hashtags + 9:16 (+ the series voice and visual style)."""
    day = day or dt.date.today()
    cfg = SERIES[series]
    comp = dict(args["composition"])
    if cfg["style"]:
        comp.setdefault("visualStyle", cfg["style"])
    out = {"composition": comp, "skill": cfg["skill"], "title": args["title"], "description": args["description"], "hashtags": args["hashtags"], "aspectRatio": ASPECT,
           "idempotencyKey": f"{series}-{day.isoformat()}-{hashlib.sha1(_norm(args['title']).encode()).hexdigest()[:8]}"}
    if cfg["voice"]:
        out["voiceId"] = cfg["voice"]
    return out


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
    return ("VIDEOSLY (2 Shorts a day, owner decisions 27-28 Nov 2026): one HORROR ('Quiet Dark', skill horror-story, mysterious voice) and one MYSTERY/CRIME ('The Fair Clue', skill short-mystery); follow shorts/VIDEOSLY_HORROR_TASK.md - "
            "the connector needs a COMPOSITION, so you write the story with .claude/skills/dopamine-storyteller, check it with `python3 -m shorts.videosly check-comp`, generate, then post (privacy " + PRIVACY + "). Recent topics: "
            + (" | ".join(t[:60] for t in rec) if rec else "none yet"))


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
    elif cmd == "series":
        print(json.dumps(SERIES, ensure_ascii=False, indent=1))
    elif cmd == "check-comp" and len(argv) > 2:
        d = json.load(open(argv[2], encoding="utf-8"))
        probs = composition_problems(argv[1], d)
        if probs:
            print("\n".join(probs))
            return 1
        print(json.dumps(generate_args(argv[1], d), ensure_ascii=False))
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
