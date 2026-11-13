"""3D cartoon explainer visuals, generated entirely by code.

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

from . import config
from .plan import LangScript

log = logging.getLogger(__name__)
DIR = Path(__file__).resolve().parent / "cartoon3d"


def render(script: LangScript, lang: str, niche: str, timeline, total: float, work: Path) -> Path:
    segments = []
    for i, (start, _end, _text) in enumerate(timeline):
        seg_start = 0.0 if i == 0 else start
        seg_end = timeline[i + 1][0] if i + 1 < len(timeline) else total
        g = script.scenes[i].graphic
        graphic = g.model_dump() if g else {"kind": "keyword", "headline": " ".join(_text.split()[:3])}
        segments.append({"start": seg_start, "end": seg_end, "graphic": graphic})
    cfg = {"niche": niche, "lang": lang, "total": total, "fps": config.FPS, "segments": segments,
           "workers": int(os.getenv("CARTOON_WORKERS", "3")),
           "glScale": float(os.getenv("CARTOON_GL_SCALE", "0.67"))}
    cfg_path = work / "cartoon.json"
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    out = work / "video.mp4"
    log.info("Rendering 3D cartoon track (%d scenes, %.1fs)", len(segments), total)
    subprocess.run(["node", str(DIR / "render.cjs"), str(cfg_path), str(out)], check=True)
    return out
