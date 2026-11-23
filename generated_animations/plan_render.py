"""Render a daily video plan (a Short's LangScript or a documentary's DocScript) with the generated_animations
engine. Same signatures and outputs as shorts.compose.build / build_documentary, so thumbnails, uploads, chapters and
history are untouched. Narration is shorts.tts (English: edge Andrew, Hindi: Piper pratham, no other voice), music and
sound effects are the repo's own mixer."""
from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

from . import packs
from .layout import LANDSCAPE, VERTICAL

log = logging.getLogger("generated_animations")
LEAD = 0.3


def _scene_dicts(scenes):
    return [s.model_dump() if hasattr(s, "model_dump") else dict(s) for s in scenes]


def boundaries(timeline, total: float):
    """Scene window edges: a scene starts a little before its narration; the last one runs to the end."""
    edges = [0.0]
    for start, _e, _t in timeline[1:]:
        edges.append(max(edges[-1] + 0.5, start - LEAD))
    edges.append(total)
    return edges


def render_picture(scenes, timeline, total: float, lang: str, work: Path, voice_wav: Path, landscape: bool,
                   pack: str = "") -> Path:
    from manim import config as mc

    from . import audio
    from .plan_scene import PlanScene
    from shorts import animate

    layout = LANDSCAPE if landscape else VERTICAL
    plan_scenes = _scene_dicts(scenes)
    narration = audio.Narration(voice_wav, fps=24)
    import os
    k = float(os.getenv("GA_PIXEL_SCALE", "1"))   # < 1 for quick previews while developing
    mc.pixel_width, mc.pixel_height = int(layout.pixels[0] * k) // 2 * 2, int(layout.pixels[1] * k) // 2 * 2
    mc.frame_rate = 24
    mc.frame_width, mc.frame_height = layout.frame_w, layout.frame_h
    mc.media_dir = str(work / "media")
    mc.output_file = "picture"
    mc.disable_caching = True
    mc.verbosity = "WARNING"
    mc.progress_bar = "none"
    mc.write_to_movie = True
    shots = packs.load(pack) if pack else []
    if not shots:
        log.warning("no animation pack for this video: falling back to the generic graphic kinds")
    scene = PlanScene(plan_scenes, boundaries(timeline, total), timeline, layout, lang, narration=narration, shots=shots, look=packs.look(pack) if pack else "classic")
    scene.render()
    out = work / "video.mp4"
    shutil.copy(scene.renderer.file_writer.movie_file_path, out)
    # sound-effect cues (pops and bells) come from the same timeline the old renderer wrote
    segs = []
    for i, (start, end, text) in enumerate(timeline):
        g = plan_scenes[i].get("graphic") or {"kind": "keyword", "headline": ""}
        seg = {"start": 0.0 if i == 0 else start, "end": timeline[i + 1][0] if i + 1 < len(timeline) else total, "graphic": g}
        hit = animate.keyword_time(plan_scenes[i].get("keyword"), text, start, end)
        if hit is not None:
            seg["hit"] = hit
        segs.append(seg)
    (work / "timeline.json").write_text(json.dumps({"segments": segs, "total": total}, ensure_ascii=False), encoding="utf-8")
    return out


def build(script, lang: str, mood: str, work: Path, niche: str = "") -> Path:
    """A Short: vertical, 40-59 s."""
    from shorts import compose, config, outro
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    script = outro.with_outro(script, lang)
    voice, timeline, voice_end = compose._voice_track(script.scenes, lang, work, window=(config.MIN_DURATION, config.MAX_DURATION))
    total = min(config.MAX_DURATION, max(config.MIN_DURATION, voice_end + config.TAIL))
    render_picture(script.scenes, timeline, total, lang, work, voice, landscape=False, pack=getattr(script, "animation_pack", ""))
    out = work / f"short_{lang}.mp4"
    compose._mix(work, voice, total, mood, out)
    return out


def build_documentary(script, lang: str, mood: str, work: Path, niche: str = "") -> tuple[Path, list[tuple[str, float]]]:
    """A documentary: landscape, natural length. Returns (video, [(chapter title, start second)])."""
    from shorts import compose, outro
    work = work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    script = outro.with_outro(script, lang)
    scenes = script.scenes
    starts, n = {}, 0
    for ch in script.chapters:
        starts[n] = ch.title
        n += len(ch.scenes)
    voice, timeline, voice_end = compose._voice_track(scenes, lang, work, chapter_starts=frozenset(starts), style="documentary")
    total = voice_end + 3.0
    render_picture(scenes, timeline, total, lang, work, voice, landscape=True, pack=getattr(script, "animation_pack", ""))
    out = work / f"documentary_{lang}.mp4"
    compose._mix(work, voice, total, mood, out, lufs=-16, music_volume=0.22)
    return out, [(title, 0.0 if i == 0 else timeline[i][0]) for i, title in sorted(starts.items())]
