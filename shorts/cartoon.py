"""Cartoon explainer visuals, generated entirely by code.

Three styles share this module and the renderer (shorts/cartoon3d/render.cjs):
- "cartoon2d" (default): a traditional-animation look with a full-colour presenter character,
  painted backgrounds chosen by niche and round "thought bubble" insets (shorts/cartoon2d/).
- "stickman": a 2D hand-drawn stick figure explainer on white paper
  (shorts/stickman/scene.js), with marker strokes, poses, faces and doodle props.
- "cartoon3d": the 3D toon scene below.

3D style:

A three.js toon-shaded scene (shorts/cartoon3d/scene.js) with a mascot, procedural props,
step pads, pillars and coin stacks, plus bold cartoon text cards. It is rendered frame by
frame in headless Chromium (software WebGL, no GPU) by shorts/cartoon3d/render.cjs.
Each scene's `graphic` (and optional `prop`) in the plan says what to show. Captions and
audio are added later by compose.py.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
from pathlib import Path

from . import config, photos
from .plan import LangScript

log = logging.getLogger(__name__)
DIR = Path(__file__).resolve().parent / "cartoon3d"
STYLE_DIRS = {"stickman": Path(__file__).resolve().parent / "stickman",
              "cartoon2d": Path(__file__).resolve().parent / "cartoon2d"}


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


def render(script: LangScript, lang: str, niche: str, timeline, total: float, work: Path,
           style: str = "cartoon3d") -> Path:
    segments, credits = [], []
    for i, (start, _end, _text) in enumerate(timeline):  # noqa: B007
        seg_start = 0.0 if i == 0 else start
        seg_end = timeline[i + 1][0] if i + 1 < len(timeline) else total
        g = script.scenes[i].graphic
        graphic = g.model_dump() if g else {"kind": "keyword", "headline": " ".join(_text.split()[:3])}
        seg = {"start": seg_start, "end": seg_end, "graphic": graphic}
        if style == "cartoon2d" and config.STOCK_PHOTOS:
            got = photos.fetch(script.scenes[i].visual_query, work, i)
            if got:
                seg["photo"] = got[0]
                if got[1] and got[1] not in credits:
                    credits.append(got[1])
        hit = keyword_time(script.scenes[i].keyword, _text, start, _end)
        if hit is not None:
            seg["hit"] = hit
        segments.append(seg)
    cfg = {"niche": niche, "lang": lang, "total": total, "fps": config.FPS, "segments": segments,
           "workers": int(os.getenv("CARTOON_WORKERS", "3")),
           "glScale": float(os.getenv("CARTOON_GL_SCALE", "0.67"))}
    if style in STYLE_DIRS:
        cfg["root"] = str(STYLE_DIRS[style])
    cfg_path = work / "cartoon.json"
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    out = work / "video.mp4"
    log.info("Rendering %s track (%d scenes, %.1fs)", style, len(segments), total)
    subprocess.run(["node", str(DIR / "render.cjs"), str(cfg_path), str(out)], check=True)
    # keep the timeline (for sound effect cues) without the large embedded photos
    for sg in cfg["segments"]:
        sg.pop("photo", None)
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    return credits
