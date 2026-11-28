"""Line-art story Shorts (owner request, 28 Nov 2026): ink-on-paper SVG animation (library by JDhruv14/line-art-animation, MIT) drawn live by a scene module Claude writes per story
in `lineart/scenes/<id>/`, rendered frame by frame in headless Chromium, with the channel's usual narration, captions, music, closing line, thumbnail, upload queue and history.
Entry point: `python -m shorts.lineart.run --plan-file plan.json` (workflow `daily-shorts.yml`, format `lineart`). Guide: `lineart/AUTHORING.md`."""

import datetime as dt
import json
from pathlib import Path

LINEART_DAYS = (1, 3, 5)           # Tuesday, Thursday, Saturday (owner request, 28 Nov 2026): the line-art story replaces the day's explore slot, so the upload total stays the same
ROOT = Path(__file__).resolve().parents[2]


def prepared(today: dt.date) -> list[str]:
    """Prepared line-art plans (strategy/prepared/*lineart*.json) whose topic has not been published yet."""
    try:
        hist = json.loads((ROOT / "data" / "history.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        hist = []
    done = {h.get("topic") for h in hist}
    out = []
    for f in sorted((ROOT / "strategy" / "prepared").glob("*lineart*.json")):
        try:
            if json.loads(f.read_text(encoding="utf-8")).get("topic") not in done:
                out.append(f.relative_to(ROOT).as_posix())
        except (OSError, ValueError):
            continue
    return out


def brief_line(today: dt.date | None = None) -> str:
    today = today or dt.date.today()
    ready = prepared(today)
    if today.weekday() in LINEART_DAYS:
        return ("LINE-ART STORY TODAY (Tue/Thu/Sat, owner request 28 Nov 2026): the explore slot (slot 3) is a line-art story Short, EN+HI, format `lineart` (dispatch daily-batch.yml with format lineart): "
                + (f"a prepared plan is ready: {ready[0]} (re-check the title, dispatch it as it is). " if ready else "write a NEW invented story (dopamine-storyteller, 60-110 words, one bespoke scene in lineart/scenes/<id>/, commit it first, rule 7). ")
                + "Guide: lineart/AUTHORING.md.")
    return "Line-art story: not today (Tue/Thu/Sat). " + (f"Ready for the next slot: {ready[0]}." if ready else "Write the next story in advance if there is time (lineart/AUTHORING.md).")
