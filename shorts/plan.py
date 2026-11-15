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

import re

from pydantic import BaseModel, Field, ValidationError


# Hooks must start on the surprising fact, not with throat-clearing (English and Hindi).
WEAK_OPENER = re.compile(
    r"^(today|in this video|in today|hello|hi\b|hey|welcome|did you know|have you ever|ever wondered|"
    r"आज|नमस्कार|नमस्ते|हेलो|स्वागत|क्या आप जानते|क्या आपने कभी)", re.I)

# Procedural 3D props available in the cartoon style (shorts/cartoon3d/scene.js)
PROPS = ["star", "bulb", "coin", "planet", "globe", "phone", "bank", "rocket", "brain", "chip",
         "heart", "clock", "gear", "atom", "book", "magnet", "cloud"]


# Character poses available in the cartoon2d and stickman styles (shorts/cartoon2d/, shorts/stickman/)
POSES = ["stand", "point", "wave", "cheer", "shrug", "think", "shock", "walk"]


class Graphic(BaseModel):
    """What the motion-graphics renderer (shorts/motion.py) draws for a scene. Text is in
    the video's language; keep it short, it is shown big on a phone screen."""
    kind: Literal["title", "stat", "keyword", "steps", "compare", "flow", "race", "build", "cycle"] = Field(
        description="title: a big headline. stat: one big number with a label. keyword: a "
        "key term with a one-line explanation. steps: 2-4 stages of a process. compare: two "
        "things side by side, optionally with values drawn as bars. Animated diagrams (cartoon2d "
        "style; other styles show them as a keyword card): flow: 2-4 stages in a chain with "
        "particles flowing along the connectors (something moves from A to B). race: exactly 2 "
        "lanes with 2 values = relative speeds; dots stream along each lane and an arrival "
        "counter shows the countable difference. build: 2-4 layers stacking up one at a time "
        "(how parts combine). cycle: 3-4 states around a loop with a token travelling round.")
    headline: str = Field(description="Main text: the headline, the number with its unit "
                          "(e.g. '71 km/s', '1966'), or the key term. Max 24 characters.")
    caption: str = Field(default="", description="Optional smaller line under the headline, max 40 characters.")
    items: List[str] = Field(default_factory=list, description="steps: 2-4 short labels in order. "
                             "compare: exactly 2 labels. Max 18 characters each.")
    values: List[float] = Field(default_factory=list, description="compare only: 2 numbers "
                                "for the bar lengths (optional).")
    prop: Optional[str] = Field(default=None, description="3D cartoon style only: a 3D prop for "
                                "title/keyword/stat scenes. One of: " + ", ".join(PROPS) + ". The 2D styles "
                                "draw the same names as drawings.")
    pose: Optional[str] = Field(default=None, description="cartoon2d and stickman styles, optional: the "
                                "character's reaction for this scene. One of: " + ", ".join(POSES) + ". "
                                "Left empty, the pose is picked from the scene kind.")


class Scene(BaseModel):
    text: str = Field(description="Narration for this scene, 1-2 short spoken sentences.")
    keyword: Optional[str] = Field(default=None, description="Optional: the stressed word or short "
                                   "phrase in `text` (copied exactly). The scene's main motion lands "
                                   "on it and the caption highlights it. One per scene.")
    graphic: Optional[Graphic] = Field(default=None, description="Motion graphic for this scene.")
    ai_prompt: Optional[str] = Field(default=None, description=(
        "Optional, at most 2 scenes per video: an ENGLISH visual description for an "
        "AI-generated clip that replaces this scene's graphic (e.g. 'a glowing comet with a "
        "long dust tail crossing a starry sky'). Scenery, objects, nature or space only: no "
        "people, faces, text, logos or real brands."))
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
        first = s.scenes[0].text if s.scenes else ""
        if len(first.split()) > 18:
            problems.append(f"{lang}: the hook (scene 1) is {len(first.split())} words, aim for 14 or fewer")
        if WEAK_OPENER.match(first.strip()):
            problems.append(f"{lang}: the hook opens with a greeting or filler ({first.strip()[:25]!r}); start with the surprising fact")
        if len(s.hook_text.split()) > 6:
            problems.append(f"{lang}: hook_text has {len(s.hook_text.split())} words, max 6 (5 is better)")
        for i, sc in enumerate(s.scenes, 1):
            if len(sc.text.split()) > 30:
                problems.append(f"{lang} scene {i}: {len(sc.text.split())} words, split it (max about 30)")
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
            elif g.kind in ("flow", "build") and not 2 <= len(g.items) <= 4:
                problems.append(f"{lang} scene {i}: {g.kind} needs 2-4 items")
            elif g.kind == "cycle" and not 3 <= len(g.items) <= 4:
                problems.append(f"{lang} scene {i}: cycle needs 3-4 items")
            elif g.kind == "race" and (len(g.items) != 2 or len(g.values) != 2 or min(g.values or [0]) <= 0):
                problems.append(f"{lang} scene {i}: race needs exactly 2 items and 2 positive values")
            if g is not None and g.prop and g.prop not in PROPS:
                problems.append(f"{lang} scene {i}: unknown prop {g.prop!r} (choose from {', '.join(PROPS)})")
            if sc.keyword and sc.keyword.lower() not in sc.text.lower():
                problems.append(f"{lang} scene {i}: keyword {sc.keyword!r} does not appear in the narration")
            if g is not None and g.pose and g.pose not in POSES:
                problems.append(f"{lang} scene {i}: unknown pose {g.pose!r} (choose from {', '.join(POSES)})")
        n_ai = sum(1 for sc in s.scenes if sc.ai_prompt)
        if n_ai > 2:
            problems.append(f"{lang}: {n_ai} scenes have ai_prompt, at most 2 are used")
    if "candidate" not in plan.research_summary.lower():
        problems.append("research_summary should start with 'Candidates:' (top 3 with scores) and say why the winner won")
    from .niches import NAMES
    if plan.niche not in NAMES:
        problems.append(f"niche {plan.niche!r} is not one of the channel's niches: {', '.join(NAMES)}")
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
