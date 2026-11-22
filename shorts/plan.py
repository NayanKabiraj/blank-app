"""The daily video plan: niche, topic and the English + Hindi scripts.

Claude (running as a scheduled task) writes a JSON file matching this schema and passes it
to the GitHub Actions workflow, which only renders and uploads.

    python -m shorts.plan schema            # print the JSON schema
    python -m shorts.plan validate p.json   # validate a plan (exit 1 if invalid)
    python -m shorts.plan doc-schema        # the schema of a documentary plan
    python -m shorts.plan validate-doc d.json   # validate a documentary plan
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

# Icons the explainer can draw for title/keyword scenes (shorts/explainer/scene.js)
PROPS = ["star", "bulb", "coin", "planet", "globe", "phone", "bank", "rocket", "brain", "chip",
         "heart", "clock", "gear", "atom", "book", "magnet", "cloud"]


KINDS = ["title", "keyword", "stat", "steps", "flow", "build", "cycle", "race", "compare", "bars",
         "chat", "quiz", "myth"]
CONVO_KINDS = ("chat", "quiz", "myth")


class Graphic(BaseModel):
    """What the explainer animation (shorts/explainer/scene.js) draws for a scene. Text is in
    the video's language; keep it short, it is shown big on a phone screen."""
    kind: Literal["title", "keyword", "stat", "steps", "flow", "build", "cycle", "race", "compare", "bars",
                  "chat", "quiz", "myth"] = Field(
        description="title: a big headline with an icon. keyword: a key term with an icon and a one-line "
        "explanation. stat: one big number counting up, with a label. steps: 2-4 stages, one lit at a time. "
        "flow: 2-4 stages in a chain with dots flowing along the connectors (something moves from A to B). "
        "build: 2-4 layers stacking up one at a time. cycle: 3-4 states around a loop with a token "
        "travelling round. race: exactly 2 lanes with 2 values = relative speeds; dots stream along each "
        "lane and an arrival counter shows the difference. compare: two discs sized by their values. "
        "bars: 2-4 horizontal bars growing to their values. Conversation scenes: chat: a text-message "
        "exchange, 2-4 bubbles, the first is the viewer asking, the next is the answer, and so on. "
        "quiz: the headline is a question put to the viewer, 2-4 answer options, a short countdown, then "
        "the right one (`answer`, 0-based) lights up. myth: items = [the common myth, the truth]; the myth "
        "is struck out and the truth stamps in.")
    headline: str = Field(description="Main text: the headline, the number with its unit "
                          "(e.g. '71 km/s', '1966'), the key term, or for quiz the question. Max 28 characters "
                          "(quiz: max 48).")
    caption: str = Field(default="", description="Optional smaller line under the headline, max 40 characters.")
    items: List[str] = Field(default_factory=list, description="Short labels in order (max 18 characters "
                             "each; chat bubbles and myth/quiz options may use up to 36).")
    values: List[float] = Field(default_factory=list, description="race: 2 speeds. compare: 2 sizes. "
                                "bars: one number per item.")
    answer: Optional[int] = Field(default=None, description="quiz only: 0-based index of the correct option.")
    prop: Optional[str] = Field(default=None, description="title/keyword scenes: an icon. One of: " + ", ".join(PROPS))


class Scene(BaseModel):
    text: str = Field(description="Narration for this scene, 1-2 short spoken sentences. Talk TO the viewer: "
                      "questions, 'you', short replies, as if in a conversation.")
    keyword: Optional[str] = Field(default=None, description="Optional: the stressed word or short "
                                   "phrase in `text` (copied exactly). The scene's main motion lands "
                                   "on it and the caption highlights it. One per scene.")
    graphic: Optional[Graphic] = Field(default=None, description="The animation for this scene.")


class LangScript(BaseModel):
    title: str = Field(description="Catchy YouTube title, max 80 characters, no hashtags.")
    description: str = Field(description="2-3 sentence YouTube description plus 3-5 hashtags.")
    tags: List[str] = Field(description="8-12 search tags.")
    hook_text: str = Field(description="On-screen hook shown in the first 3 seconds, max 6 words.")
    thumbnail_text: str = Field(default="", description="Thumbnail headline, 1-4 big words that show the consequence "
                                "(not a copy of the title). Empty = the hook text is used.")
    next_video: str = Field(default="", description="The next video's title or question: the close hands the viewer on, and the "
                            "description gets an 'Up next' line.")
    pinned_comment: str = Field(default="", description="One viewer decision tied to the central dilemma, to pin as the first "
                                "comment (saved in the *_youtube.txt file).")
    scenes: List[Scene] = Field(description="6-9 scenes; first is the hook, last is a call to follow.")
    animation_pack: str = Field(default="", description="id of the animation pack Claude wrote for this video: the folder "
                                "generated_animations/scenes/<id>/ with shots.json + one Python module per shot (scene-specific "
                                "motion animation). Required: the generic graphic kinds are only a fallback.")


class Plan(BaseModel):
    niche: str
    topic: str
    research_summary: str = Field(description="Why this niche/topic today, with the key facts used.")
    mood: Literal["calm", "upbeat", "dramatic", "inspiring", "mysterious"]
    cluster: str = Field(default="", description="The content cluster this video belongs to (e.g. 'The Moon'); 5-10 videos grow from one.")
    follow_ups: List[str] = Field(default_factory=list, description="Three follow-up video ideas that continue the cluster.")
    gate_score: int = Field(default=0, description="The /100 quality-gate score from the video-strategy skill (85+ strong, 75-84 improve, below 75 rework).")
    english: LangScript
    hindi: Optional[LangScript] = None   # English-only by default (config.LANGS); required when Hindi is produced


def _scene_problems(sc: "Scene", where: str) -> list[str]:
    """Checks on one scene's graphic and keyword (shared by Shorts and documentaries)."""
    problems = []
    g = sc.graphic
    if g is None:
        return [f"{where}: no graphic (a keyword card will be used)"]
    n, label = len(g.items), g.kind
    if len(g.headline) > (48 if g.kind == "quiz" else 28):
        problems.append(f"{where}: graphic headline too long ({len(g.headline)} characters)")
    if g.kind in ("steps", "flow", "build", "bars") and not 2 <= n <= 4:
        problems.append(f"{where}: {label} needs 2-4 items")
    elif g.kind in ("compare", "myth") and n != 2:
        problems.append(f"{where}: {label} needs exactly 2 items")
    elif g.kind == "cycle" and not 3 <= n <= 4:
        problems.append(f"{where}: cycle needs 3-4 items")
    elif g.kind == "chat" and not 2 <= n <= 4:
        problems.append(f"{where}: chat needs 2-4 bubbles")
    elif g.kind == "quiz" and (not 2 <= n <= 4 or g.answer is None or not 0 <= g.answer < n):
        problems.append(f"{where}: quiz needs 2-4 options and `answer` = the 0-based index of the right one")
    elif g.kind == "race" and (n != 2 or len(g.values) != 2 or min(g.values or [0]) <= 0):
        problems.append(f"{where}: race needs exactly 2 items and 2 positive values")
    elif g.kind == "bars" and (len(g.values) != n or min(g.values or [0]) <= 0):
        problems.append(f"{where}: bars needs one positive value per item")
    if g.prop and g.prop not in PROPS:
        problems.append(f"{where}: unknown prop {g.prop!r} (choose from {', '.join(PROPS)})")
    if sc.keyword and sc.keyword.lower() not in sc.text.lower():
        problems.append(f"{where}: keyword {sc.keyword!r} does not appear in the narration")
    return problems


def _present(plan):
    """[(label, script)] for the languages this plan has (Hindi is optional)."""
    return [(l, x) for l, x in (("english", plan.english), ("hindi", plan.hindi)) if x is not None]


def _animation_problems(plan) -> list[str]:
    """Every video's picture is authored animation code (generated_animations packs), not template cards."""
    from . import config
    out = []
    if config.ENGINE != "generated":
        return out
    for lang, s in _present(plan):
        pack = (s.animation_pack or "").strip()
        if not pack:
            out.append(f"{lang}: animation_pack is empty - write the scene-specific animation (generated_animations/scenes/<id>/) for this video")
            continue
        try:
            from generated_animations import packs
            have = packs.covered(pack)
        except Exception as exc:  # noqa: BLE001
            out.append(f"{lang}: animation pack {pack!r} cannot be read ({exc})")
            continue
        missing = [i + 1 for i in range(len(s.scenes)) if i not in have]
        if not have:
            out.append(f"{lang}: animation pack {pack!r} has no shots.json / shots")
        elif missing:
            out.append(f"{lang}: scenes {missing} have no authored animation in pack {pack!r}")
    return out


def _strategy_problems(plan) -> list[str]:
    """The standing strategy (skills/video-strategy): researched packaging, a quality gate, a cluster and a next video."""
    out = _animation_problems(plan)
    rs = plan.research_summary.lower()
    for marker, label in (("title", "the title options and why this one"), ("thumbnail", "the thumbnail concepts and the chosen one"),
                          ("hook", "the opening hook options")):
        if marker not in rs:
            out.append(f"research_summary should also record {label} (see the video-strategy skill)")
    if not plan.gate_score:
        out.append("gate_score is missing: score the concept /100 with the quality gate (85+ proceed, 75-84 improve, below 75 rework)")
    elif plan.gate_score < 75:
        out.append(f"gate_score {plan.gate_score} is below 75: rework the weakest components before rendering")
    if not plan.cluster:
        out.append("cluster is missing: name the content cluster this video belongs to")
    if len(plan.follow_ups) < 3:
        out.append("follow_ups: list three follow-up video ideas that continue the cluster")
    for lang, s in _present(plan):
        if not s.next_video.strip():
            out.append(f"{lang}: next_video is missing (the close hands the viewer to the next video)")
        if "?" not in s.pinned_comment:
            out.append(f"{lang}: pinned_comment should be one viewer decision tied to the central dilemma, as a question")
    return out


def _thumb_problems(lang: str, s) -> list[str]:
    t = (getattr(s, "thumbnail_text", "") or "").strip()
    out = []
    if t and (len(t.split()) > 8 or len(t) > 46):
        out.append(f"{lang}: thumbnail_text {t!r} is too long, write one short sentence (at most 8 words, 46 characters)")
    if t and t.lower().strip("?!. ") == s.title.lower().strip("?!. "):
        out.append(f"{lang}: thumbnail_text repeats the title; the thumbnail should show the consequence, the title the premise")
    return out


def validate(plan: Plan) -> list[str]:
    """Extra checks beyond the schema. Returns a list of problems."""
    problems = _strategy_problems(plan)
    for lang, s, (lo, hi) in [(l, x, {"english": (100, 142), "hindi": (85, 125)}[l]) for l, x in _present(plan)]:
        words = sum(len(sc.text.split()) for sc in s.scenes)
        if not lo <= words <= hi:
            problems.append(f"{lang}: {words} narration words, expected {lo}-{hi} for 40-59s (the closing like/share/subscribe line is added automatically; do not write it)")
        if not 5 <= len(s.scenes) <= 10:
            problems.append(f"{lang}: {len(s.scenes)} scenes, expected 6-9")
        if len(s.title) > 90:
            problems.append(f"{lang}: title longer than 90 characters")
        problems += _thumb_problems(lang, s)
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
            problems += _scene_problems(sc, f"{lang} scene {i}")
        # conversational feel: the narrator keeps asking and answering, and ends by asking the viewer
        qs = [i for i, sc in enumerate(s.scenes, 1) if "?" in sc.text]
        if len(qs) < 3:
            problems.append(f"{lang}: only {len(qs)} scenes ask a question, make it a conversation (3 or more)")
        if not any(i <= 2 for i in qs):
            problems.append(f"{lang}: no question in the first two scenes (open the conversation early)")
        if s.scenes and "?" not in s.scenes[-1].text:
            problems.append(f"{lang}: the last scene should ask the viewer a question to answer in the comments")
        if not any(sc.graphic and sc.graphic.kind in CONVO_KINDS for sc in s.scenes):
            problems.append(f"{lang}: use at least one chat, quiz or myth scene")
        kinds = [sc.graphic.kind for sc in s.scenes if sc.graphic]
        if len(set(kinds)) < 4:
            problems.append(f"{lang}: only {len(set(kinds))} different graphic kinds, vary the scenes (4 or more)")
    if "candidate" not in plan.research_summary.lower():
        problems.append("research_summary should start with 'Candidates:' (top 3 with scores) and say why the winner won")
    from .niches import NAMES
    if plan.niche not in NAMES:
        problems.append(f"niche {plan.niche!r} is not one of the channel's niches: {', '.join(NAMES)}")
    if plan.hindi is not None and not any("\u0900" <= ch <= "\u097f" for sc in plan.hindi.scenes for ch in sc.text):
        problems.append("hindi: narration is not in Devanagari script")
    return problems


# ------------------------------------------------------------------ documentaries (5-15 minutes)
WORDS_PER_SEC = {"en": 2.9, "hi": 2.45}   # Piper pace measured on the same paragraph (en_US-ryan-high, hi_IN-rohan-medium)
SCENE_PAUSE, CHAPTER_PAUSE = 0.4, 1.0


class Chapter(BaseModel):
    title: str = Field(description="Chapter title, max 50 characters. It becomes the chapter marker in the "
                       "YouTube description and should also be the headline of the chapter's first scene.")
    scenes: List[Scene] = Field(description="3-12 scenes. The first one is usually a `title` scene with the "
                                "chapter's name.")


class DocScript(BaseModel):
    title: str = Field(description="YouTube title, max 90 characters, no hashtags.")
    description: str = Field(description="3-5 sentence description plus 3-5 hashtags. Chapter timestamps are "
                             "added automatically.")
    tags: List[str] = Field(description="8-15 search tags.")
    thumbnail_text: str = Field(default="", description="Thumbnail headline, 1-4 big words that show the consequence "
                                "(not a copy of the title). Empty = the first words of the title are used.")
    next_video: str = Field(default="", description="The next video's title or question; the description gets an 'Up next' line.")
    pinned_comment: str = Field(default="", description="One viewer decision tied to the central dilemma, to pin as the first comment.")
    chapters: List[Chapter] = Field(description="3-12 chapters in order; chapter 1 is the cold open.")
    animation_pack: str = Field(default="", description="id of the animation pack Claude wrote for this video "
                                "(generated_animations/scenes/<id>/). Required; the generic graphic kinds are only a fallback.")

    @property
    def scenes(self) -> List[Scene]:
        return [sc for ch in self.chapters for sc in ch.scenes]


class DocPlan(BaseModel):
    niche: str
    topic: str
    research_summary: str = Field(description="Candidates considered, why this documentary, the sources and facts used.")
    mood: Literal["calm", "upbeat", "dramatic", "inspiring", "mysterious"]
    target_minutes: int = Field(description="Intended length: 5 to 15 minutes.")
    cluster: str = Field(default="", description="The content cluster this video belongs to; 5-10 videos grow from one.")
    follow_ups: List[str] = Field(default_factory=list, description="Three follow-up video ideas that continue the cluster.")
    gate_score: int = Field(default=0, description="The /100 quality-gate score from the video-strategy skill (85+ strong, 75-84 improve, below 75 rework).")
    english: DocScript
    hindi: Optional[DocScript] = None


def doc_seconds(s: DocScript, lang: str = "en") -> float:
    """Estimated running time of a documentary script."""
    words = sum(len(sc.text.split()) for sc in s.scenes)
    from .outro import OUTRO_SECONDS
    return words / WORDS_PER_SEC[lang] + SCENE_PAUSE * (len(s.scenes) + 1) + CHAPTER_PAUSE * len(s.chapters) + 3 + OUTRO_SECONDS[lang]


def validate_doc(plan: DocPlan) -> list[str]:
    problems = _strategy_problems(plan)
    if not 5 <= plan.target_minutes <= 15:
        problems.append(f"target_minutes {plan.target_minutes} is outside 5-15")
    if plan.target_minutes > 10:
        problems.append("target_minutes over 10: keep documentaries to 10 minutes or less (long runs risk the job limit, especially with the slow Parler voice)")
    for lang, s in _present(plan):
        secs = doc_seconds(s, "en" if lang == "english" else "hi")
        if not 270 <= secs <= 930:
            problems.append(f"{lang}: estimated {secs / 60:.1f} min, a documentary runs 5-15 minutes")
        elif abs(secs - plan.target_minutes * 60) > plan.target_minutes * 60 * 0.2:
            problems.append(f"{lang}: estimated {secs / 60:.1f} min but target_minutes is {plan.target_minutes} (stay within 20 %)")
        if not 3 <= len(s.chapters) <= 12:
            problems.append(f"{lang}: {len(s.chapters)} chapters, expected 3-12")
        if len(s.title) > 90:
            problems.append(f"{lang}: title longer than 90 characters")
        problems += _thumb_problems(lang, s)
        for c, ch in enumerate(s.chapters, 1):
            if len(ch.title) > 50:
                problems.append(f"{lang} chapter {c}: title longer than 50 characters")
            if not 2 <= len(ch.scenes) <= 12:
                problems.append(f"{lang} chapter {c}: {len(ch.scenes)} scenes, expected 2-12")
            for i, sc in enumerate(ch.scenes, 1):
                if len(sc.text.split()) > 45:
                    problems.append(f"{lang} chapter {c} scene {i}: {len(sc.text.split())} words, split it (max about 40)")
                problems += _scene_problems(sc, f"{lang} chapter {c} scene {i}")
        scenes = s.scenes
        if scenes and WEAK_OPENER.match(scenes[0].text.strip()):
            problems.append(f"{lang}: the cold open starts with a greeting or filler; start with the story")
        qs = sum(1 for sc in scenes if "?" in sc.text)
        if qs < max(4, len(s.chapters)):
            problems.append(f"{lang}: only {qs} scenes ask a question, a documentary that talks to the viewer needs {max(4, len(s.chapters))}+")
        if scenes and "?" not in scenes[-1].text:
            problems.append(f"{lang}: the last scene should ask the viewer a question for the comments")
        if sum(1 for sc in scenes if sc.graphic and sc.graphic.kind in CONVO_KINDS) < 2:
            problems.append(f"{lang}: use at least two chat, quiz or myth scenes")
        kinds = {sc.graphic.kind for sc in scenes if sc.graphic}
        if len(kinds) < 6:
            problems.append(f"{lang}: only {len(kinds)} different graphic kinds, vary the scenes (6 or more)")
    if "candidate" not in plan.research_summary.lower():
        problems.append("research_summary should list the candidates and say why the winner won")
    from .niches import NAMES
    if plan.niche not in NAMES:
        problems.append(f"niche {plan.niche!r} is not one of the channel's niches: {', '.join(NAMES)}")
    if plan.hindi is not None and not any("\u0900" <= ch <= "\u097f" for sc in plan.hindi.scenes for ch in sc.text):
        problems.append("hindi: narration is not in Devanagari script")
    return problems


def _cli() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "schema":
        print(json.dumps(Plan.model_json_schema(), ensure_ascii=False, indent=2))
        return 0
    if len(sys.argv) >= 2 and sys.argv[1] == "doc-schema":
        print(json.dumps(DocPlan.model_json_schema(), ensure_ascii=False, indent=2))
        return 0
    if len(sys.argv) == 3 and sys.argv[1] == "validate-doc":
        try:
            dplan = DocPlan.model_validate_json(Path(sys.argv[2]).read_text(encoding="utf-8"))
        except ValidationError as e:
            print(e)
            return 1
        problems = validate_doc(dplan)
        print("\n".join(problems) if problems else
              f"OK: {dplan.niche} | {dplan.topic} | ~{doc_seconds(dplan.english, 'en') / 60:.1f} min EN, ~{(doc_seconds(dplan.hindi, 'hi') / 60) if dplan.hindi else 0:.1f} min HI")
        return 1 if problems else 0
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
