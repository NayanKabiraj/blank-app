"""Daily niche research + bilingual script writing with Claude.

Step 1: Claude researches today's trends on the web (web search tool), seeded with
        free trend signals (Google Trends RSS) and the channel's recent history, and
        picks a niche + topic.
Step 2: Claude turns that research brief into two scene-by-scene Shorts scripts
        (English + Hindi), returned as validated structured output.
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import urllib.request
import xml.etree.ElementTree as ET
from typing import List, Literal

import anthropic
from pydantic import BaseModel, Field

from . import config

log = logging.getLogger(__name__)

FALLBACK_BETA = "server-side-fallback-2026-07-01"


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


def _trend_signals() -> str:
    """Free trend signals that need no API key. Failures are non-fatal."""
    lines = []
    for geo in ("IN", "US"):
        url = f"https://trends.google.com/trending/rss?geo={geo}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 shorts-bot"})
            with urllib.request.urlopen(req, timeout=20) as r:
                root = ET.fromstring(r.read())
            titles = [i.findtext("title") for i in root.iter("item")][:20]
            lines.append(f"Google Trends {geo}: " + "; ".join(t for t in titles if t))
        except Exception as e:  # noqa: BLE001
            log.warning("Trend fetch failed for %s: %s", geo, e)
    return "\n".join(lines) or "(no trend feed available today)"


def _recent_history(n: int = 30) -> str:
    if not config.HISTORY_FILE.exists():
        return "(no videos published yet)"
    hist = json.loads(config.HISTORY_FILE.read_text())[-n:]
    return "\n".join(f"- {h['date']}: [{h['niche']}] {h['topic']}" for h in hist)


def _text_of(msg) -> str:
    return "\n".join(b.text for b in msg.content if b.type == "text").strip()


def _check(msg) -> None:
    if msg.stop_reason == "refusal":
        raise RuntimeError(f"Claude declined the request: {msg.stop_details}")


def research_brief(client: anthropic.Anthropic, today: str) -> str:
    prompt = f"""Today is {today}. You run research for a faceless YouTube Shorts channel that
publishes one English and one Hindi Short every day for an audience mainly in India plus a
global English audience.

Pick TODAY's niche and a single specific video topic. Use web search to check what is
trending right now and what is performing on YouTube Shorts, and to collect 4-6 accurate,
surprising, verifiable facts for the video.

Selection criteria:
- High curiosity / retention potential for a 40-60 second Short.
- Evergreen-safe or timely, but NOT breaking tragedies, politics, elections, medical or
  financial advice, or anything about real private individuals.
- Easy to illustrate with generic stock footage (no specific celebrities or brands needed).
- Works equally well in English and Hindi.
- Do not repeat a topic from the recent history; vary the niche across days
  (e.g. science, space, history, psychology, tech, nature, money habits, geography,
  inventions, human body, animals, productivity).
{f"- Owner preference for niches: {config.NICHE_HINT}" if config.NICHE_HINT else ""}

Free trend signals fetched this morning:
{_trend_signals()}

Recent channel history (avoid repeats):
{_recent_history()}

Finish with a research brief: chosen niche, topic, why it should perform today, the facts
(with source names), and the emotional mood of the video."""
    messages = [{"role": "user", "content": prompt}]
    for _ in range(5):  # handle pause_turn from long server-side tool turns
        msg = client.beta.messages.create(
            model=config.CLAUDE_MODEL,
            max_tokens=16000,
            betas=[FALLBACK_BETA],
            fallbacks="default",
            output_config={"effort": "high"},
            tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 8}],
            messages=messages,
        )
        _check(msg)
        if msg.stop_reason != "pause_turn":
            break
        messages.append({"role": "assistant", "content": msg.content})
    brief = _text_of(msg)
    if not brief:
        raise RuntimeError("Research step returned no text")
    return brief


def write_scripts(client: anthropic.Anthropic, brief: str) -> Plan:
    prompt = f"""Using this research brief, write a faceless YouTube Short in TWO versions.

<brief>
{brief}
</brief>

Rules for both versions:
- Spoken length 45-55 seconds: English 120-140 words total; Hindi 105-125 words total.
- Scene 1 is a hook that creates curiosity in under 3 seconds. Then deliver the facts
  as a mini-story with one idea per scene. The last scene asks viewers to follow for a
  new fact every day.
- Short, punchy, conversational sentences that sound natural when read aloud by TTS.
- Write numbers, years and symbols as words (e.g. "nineteen sixty-nine", "fifty percent")
  so the voice pronounces them correctly. No emojis, no hashtags inside narration.
- Only use facts from the brief; never invent statistics.
- Hindi version: natural everyday spoken Hindi in Devanagari script (Hinglish loanwords
  are fine where common, still written in Devanagari). It is an adaptation, not a literal
  translation. Hindi title/description in Hindi; tags may mix Hindi and English.
- visual_query is always in English, concrete and filmable.
"""
    msg = client.beta.messages.parse(
        model=config.CLAUDE_MODEL,
        max_tokens=16000,
        betas=[FALLBACK_BETA],
        fallbacks="default",
        output_config={"effort": "medium"},
        output_format=Plan,
        messages=[{"role": "user", "content": prompt}],
    )
    _check(msg)
    return msg.parsed_output


def make_plan(niche_override: str = "") -> Plan:
    client = anthropic.Anthropic()
    today = dt.date.today().isoformat()
    if niche_override:
        config.NICHE_HINT = f"Use exactly this niche today: {niche_override}"
    log.info("Researching today's niche with %s ...", config.CLAUDE_MODEL)
    brief = research_brief(client, today)
    log.info("Research brief:\n%s", brief)
    plan = write_scripts(client, brief)
    log.info("Chosen niche: %s | topic: %s | mood: %s", plan.niche, plan.topic, plan.mood)
    return plan
