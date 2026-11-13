"""The daily video plan: niche, topic and the English + Hindi scripts.

Claude (running as a scheduled task) writes a JSON file matching this schema and passes it
to the GitHub Actions workflow, which only renders and uploads.

    python -m shorts.plan schema            # print the JSON schema
    python -m shorts.plan validate p.json   # validate a plan (exit 1 if invalid)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, ValidationError


class Graphic(BaseModel):
    """What the motion-graphics renderer (shorts/motion.py) draws for a scene. Text is in
    the video's language; keep it short, it is shown big on a phone screen."""
    kind: Literal["title", "stat", "keyword", "steps", "compare"] = Field(
        description="title: a big headline. stat: one big number with a label. keyword: a "
        "key term with a one-line explanation. steps: 2-4 stages of a process. compare: two "
        "things side by side, optionally with values drawn as bars.")
    headline: str = Field(description="Main text: the headline, the number with its unit "
                          "(e.g. '71 km/s', '1966'), or the key term. Max 24 characters.")
    caption: str = Field(default="", description="Optional smaller line under the headline, max 40 characters.")
    items: List[str] = Field(default_factory=list, description="steps: 2-4 short labels in order. "
                             "compare: exactly 2 labels. Max 18 characters each.")
    values: List[float] = Field(default_factory=list, description="compare only: 2 numbers "
                                "for the bar lengths (optional).")


class Scene(BaseModel):
    text: str = Field(description="Narration for this scene, 1-2 short spoken sentences.")
    graphic: Optional[Graphic] = Field(default=None, description="Motion graphic for this scene.")
    visual_query: str = Field(
        description="2-3 ENGLISH keywords for filmable stock footage of scenery, nature, "
        "objects or space (e.g. 'meteor timelapse', 'ocean waves'); never people or news."
    )


class LangScript(BaseModel):
    title: str = Field(description="Catchy YouTube title, max 80 characters, no hashtags.")
    description: str = Field(description="2-3 sentence YouTube description plus 3-5 hashtags.")
    tags: List[str] = Field(description="8-12 search tags.")
    hook_text: str = Field(description="On-screen hook shown in the first 3 seconds, max 6 words.")
    scenes: List[Scene] = Field(description="6-9 scenes; first is the hook, last is a call to follow.")


class Plan(BaseModel):
    niche: str
    topic: str
    research_summary: str = Field(description="Why this niche/topic today, with the key facts used.")
    mood: Literal["calm", "upbeat", "dramatic", "inspiring", "mysterious"]
    english: LangScript
    hindi: LangScript


def validate(plan: Plan) -> list[str]:
    """Extra checks beyond the schema. Returns a list of problems."""
    problems = []
    for lang, s, (lo, hi) in (("english", plan.english, (100, 160)), ("hindi", plan.hindi, (85, 145))):
        words = sum(len(sc.text.split()) for sc in s.scenes)
        if not lo <= words <= hi:
            problems.append(f"{lang}: {words} narration words, expected {lo}-{hi} for 40-59s")
        if not 5 <= len(s.scenes) <= 10:
            problems.append(f"{lang}: {len(s.scenes)} scenes, expected 6-9")
        if len(s.title) > 90:
            problems.append(f"{lang}: title longer than 90 characters")
        for i, sc in enumerate(s.scenes, 1):
            g = sc.graphic
            if g is None:
                problems.append(f"{lang} scene {i}: no graphic (a keyword card will be used)")
            elif len(g.headline) > 28:
                problems.append(f"{lang} scene {i}: graphic headline longer than 28 characters")
            elif g.kind == "steps" and not 2 <= len(g.items) <= 4:
                problems.append(f"{lang} scene {i}: steps needs 2-4 items")
            elif g.kind == "compare" and len(g.items) != 2:
                problems.append(f"{lang} scene {i}: compare needs exactly 2 items")
    if not any("\u0900" <= ch <= "\u097f" for sc in plan.hindi.scenes for ch in sc.text):
        problems.append("hindi: narration is not in Devanagari script")
    return problems


def _cli() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "schema":
        print(json.dumps(Plan.model_json_schema(), ensure_ascii=False, indent=2))
        return 0
    if len(sys.argv) == 3 and sys.argv[1] == "validate":
        try:
            plan = Plan.model_validate_json(Path(sys.argv[2]).read_text(encoding="utf-8"))
        except ValidationError as e:
            print(e)
            return 1
        problems = validate(plan)
        print("\n".join(problems) if problems else f"OK: {plan.niche} | {plan.topic}")
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(_cli())
