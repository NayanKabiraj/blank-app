"""Invokes Manim to render the picture (spec section 15: vertical 1080x1920 or landscape
1920x1080, 30fps, H.264/AAC MP4), then FFmpeg to burn subtitles and mux narration. Resolution
is set on Manim's global `config` *before* the scene is constructed, since diagram_builder reads
it live to lay elements out correctly for whichever aspect ratio was requested (see its
_positions_for - this is what makes the same storyboard adapt instead of just cropping).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from ..animation_engine.sketch_renderer import style_scene_class
from ..schemas.storyboard_schema import Storyboard

RESOLUTIONS = {"vertical": (1080, 1920), "landscape": (1920, 1080)}
QUALITY_FPS = {"draft": 15, "medium": 24, "high": 30}


def _run(cmd: list, cwd: Path | None = None) -> None:
    subprocess.run([str(c) for c in cmd], check=True, cwd=cwd)


def render_picture(storyboard: Storyboard, fmt: str, lang: str, work: Path, *,
                   quality: str = "medium", fps: int | None = None) -> Path:
    """Renders the silent picture for one (storyboard, format) pair. Manim is imported inside
    this function, not at module load time, so importing video_engine doesn't require Manim to
    already be installed (useful for the schema/script/storyboard unit tests, which don't
    render anything)."""
    from manim import config as manim_config

    width, height = RESOLUTIONS[fmt]
    work.mkdir(parents=True, exist_ok=True)
    manim_config.pixel_width = width
    manim_config.pixel_height = height
    manim_config.frame_rate = fps or QUALITY_FPS.get(quality, 24)
    manim_config.media_dir = str(work / "media")
    manim_config.output_file = f"picture_{lang}_{fmt}"
    manim_config.disable_caching = True

    scene_cls = style_scene_class(storyboard.visual_style)
    scene = scene_cls(storyboard=storyboard, lang=lang)
    scene.render()
    return Path(scene.renderer.file_writer.movie_file_path)


def burn_subtitles(video_in: Path, ass_path: Path, out: Path, work: Path) -> Path:
    """Runs with cwd=work and the subtitle path relative to it, because libass's `subtitles`
    filter parses colons in its argument as option separators - an absolute path is safe on
    this OS today, but a relative name sidesteps the issue entirely. `video_in` itself (e.g.
    Manim's nested media/videos/<res>/picture_*.mp4) is passed as an absolute path since the
    `-i` flag has no such parsing restriction."""
    ass_rel = Path(ass_path).resolve().relative_to(Path(work).resolve())
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(Path(video_in).resolve()),
          "-vf", f"subtitles={ass_rel.as_posix()}",
          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", str(out)],
         cwd=work)
    return out


def mux_final(video_in: Path, audio_in: Path, out: Path, work: Path) -> Path:
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(Path(video_in).resolve()), "-i", str(Path(audio_in).resolve()),
          "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
          "-movflags", "+faststart", "-shortest", str(out)], cwd=work)
    return out
