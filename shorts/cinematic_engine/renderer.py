"""The cinematic picture pipeline: same contract as `shorts.animate.render` and
`shorts.stockreel.render.render` (`render(script, lang, niche, timeline, total, work, layout="portrait",
fps=None) -> Path`, writing `work/video.mp4` + `work/timeline.json`), so `shorts.compose.build`'s pattern
(voice -> picture -> mix) works unchanged for this renderer too.

Per scene: a gradient background with a slow camera drift, a drifting particle field, and the scene's
own `graphics.py` drawer (picked by `Graphic.kind`) - rendered frame by frame with Pillow + NumPy and
piped straight into FFmpeg (no temp frame files), then every scene's clip is stitched with
`transitions.concat_xfade`.
"""
from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

from . import effects, graphics, storyboard, transitions
from .. import config

log = logging.getLogger(__name__)

FADE = 0.45


def _encode_clip(frames_iter, path: Path, w: int, h: int, fps: int) -> None:
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
         "-r", str(fps), "-i", "-", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "medium",
         "-crf", "19", str(path)],
        stdin=subprocess.PIPE,
    )
    try:
        for frame in frames_iter:
            proc.stdin.write(frame)
    finally:
        proc.stdin.close()
        ret = proc.wait()
    if ret != 0:
        raise RuntimeError(f"ffmpeg failed encoding {path} (exit {ret})")


def _render_scene_frames(rs: "storyboard.RenderScene", lang: str, w: int, h: int, fps: int,
                         clip_dur: float, is_last: bool, outro_text: str):
    bg = effects.gradient_background(w, h)
    particles = effects.ParticleField(w, h, count=38, seed=rs.seed, color=rs.accent)
    n_frames = max(1, int(round(clip_dur * fps)))
    for n in range(n_frames):
        t = n / fps
        scale, dx, dy = effects.camera_drift(t, rs.duration, w, h, zoom_to=rs.zoom_to, pan_px=rs.pan_px)
        canvas = effects.apply_camera(bg, scale, dx, dy).convert("RGBA")
        canvas.alpha_composite(particles.frame(t * 0.5, opacity=0.8))
        p = min(1.0, t / max(0.3, rs.duration))
        if rs.graphic is not None:
            graphics.draw_scene(canvas, rs.graphic, lang, p, rs.accent, w, h)
        else:
            graphics.outro(canvas, outro_text, lang, p, w, h)
        if is_last and t > rs.duration:
            tail_p = min(1.0, (t - rs.duration) / max(0.4, clip_dur - rs.duration))
            graphics.outro(canvas, outro_text, lang, tail_p, w, h)
        yield np.asarray(canvas.convert("RGB"), dtype=np.uint8).tobytes()


def render(script, lang: str, niche: str, timeline, total: float, work: Path, layout: str = "portrait",
           fps: int | None = None) -> Path:
    scenes = script.scenes if hasattr(script, "scenes") else script
    land = layout == "landscape"
    w, h = (1920, 1080) if land else (1080, 1920)
    fps = fps or config.FPS
    rscenes = storyboard.build(scenes, timeline, total)
    outro_text = getattr(script, "next_video", "") or getattr(script, "hook_text", "") or ""

    clip_paths, clip_durs = [], []
    for i, rs in enumerate(rscenes):
        is_last = i == len(rscenes) - 1
        clip_dur = rs.duration + (0.0 if is_last else FADE)
        clip_path = work / f"_cine_clip_{i}.mp4"
        frames = _render_scene_frames(rs, lang, w, h, fps, clip_dur, is_last, outro_text)
        _encode_clip(frames, clip_path, w, h, fps)
        clip_paths.append(clip_path)
        clip_durs.append(clip_dur)

    out = work / "video.mp4"
    transitions.concat_xfade(clip_paths, clip_durs, out, fps, w, h, fade=FADE)
    for p in clip_paths:
        p.unlink(missing_ok=True)

    # the same segments/captions shape `shorts.animate.render` writes, so `sfx.build` and the
    # existing quality tooling can read `work/timeline.json` unchanged.
    segments = []
    for i, (start, end, text) in enumerate(timeline):
        seg_end = timeline[i + 1][0] if i + 1 < len(timeline) else total
        g = scenes[i].graphic if i < len(scenes) else None
        seg = {"start": 0.0 if i == 0 else start, "end": seg_end,
               "graphic": g.model_dump() if g else {"kind": "keyword", "headline": " ".join(text.split()[:3])}}
        segments.append(seg)
    cfg = {"niche": niche, "lang": lang, "total": total, "fps": fps, "segments": segments,
           "layout": layout, "width": w, "height": h, "engine": "cinematic"}
    (work / "timeline.json").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    return out
