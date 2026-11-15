"""Explainer animation, generated entirely by code.

Dark navy, flat step-by-step diagrams, one guiding "spark" carried from scene to scene, word-by-word
headlines, chat bubbles, quizzes and rounded caption pills (shorts/explainer/scene.js), rendered frame
by frame in headless Chromium by shorts/explainer/render.cjs and encoded with FFmpeg. Each scene's
`graphic` in the plan says what to draw; voice, music and sound effects are added by compose.py.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path

from . import config
from .plan import LangScript

log = logging.getLogger(__name__)
DIR = Path(__file__).resolve().parent / "explainer"


def keyword_time(keyword, text: str, start: float, end: float):
    """When the keyword is spoken, estimated inside the scene's own audio span.

    Each scene is synthesized separately, so the span is one or two short sentences and
    a position-by-characters estimate is usually within a couple of frames of the real word
    (the method from the kazi skill would use forced alignment; Piper gives no word times).
    """
    if not keyword:
        return None
    pos = text.lower().find(keyword.lower())
    if pos < 0:
        return None
    return start + (end - start) * (pos / max(1, len(text)))


def caption_chunks(timeline, keywords, words_per_chunk: int = 3) -> list[dict]:
    """The spoken text cut into short caption chunks with their timing (same rule as the ASS captions),
    with the scene keyword's words flagged so the renderer can colour them."""
    out = []
    for k, (start, end, text) in enumerate(timeline):
        kw = set((keywords[k] or "").lower().split()) if keywords and k < len(keywords) else set()
        words = text.split()
        chunks = [words[i:i + words_per_chunk] for i in range(0, len(words), words_per_chunk)]
        weights = [max(1, len(" ".join(c))) for c in chunks]
        t, span = start, end - start
        for c, w in zip(chunks, weights):
            d = span * w / sum(weights)
            out.append({"start": round(t, 3), "end": round(t + d, 3),
                        "words": [{"t": x, "kw": x.strip(".,!?;:\"'()।").lower() in kw} for x in c]})
            t += d
    return out


def render(script: LangScript, lang: str, niche: str, timeline, total: float, work: Path) -> Path:
    """Render work/video.mp4 (picture only) and keep work/timeline.json (the timeline, for sound cues)."""
    segments = []
    for i, (start, end, text) in enumerate(timeline):
        seg_end = timeline[i + 1][0] if i + 1 < len(timeline) else total
        g = script.scenes[i].graphic
        graphic = g.model_dump() if g else {"kind": "keyword", "headline": " ".join(text.split()[:3])}
        seg = {"start": 0.0 if i == 0 else start, "end": seg_end, "graphic": graphic}
        hit = keyword_time(script.scenes[i].keyword, text, start, end)
        if hit is not None:
            seg["hit"] = hit
        segments.append(seg)
    cfg = {"niche": niche, "lang": lang, "total": total, "fps": config.FPS, "segments": segments,
           "workers": int(os.getenv("RENDER_WORKERS", "3")),
           "captions": caption_chunks(timeline, [sc.keyword for sc in script.scenes])}
    cfg_path = work / "timeline.json"
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    out = work / "video.mp4"
    log.info("Rendering the explainer (%d scenes, %.1fs)", len(segments), total)
    subprocess.run(["node", str(DIR / "render.cjs"), str(cfg_path), str(out)], check=True)
    return out
