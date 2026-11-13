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
from typing import List, Literal

from pydantic import BaseModel, Field, ValidationError


class Scene(BaseModel):
    text: str = Field(description="Narration for this scene, 1-2 short spoken sentences.")
    visual_query: str = Field(
        description="2-4 ENGLISH keywords describing concrete, filmable stock footage for "
        "this scene (e.g. 'city traffic night', 'hands counting money')."
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
