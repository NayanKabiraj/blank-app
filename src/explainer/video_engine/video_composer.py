"""Ties one (topic, language, format) combination together: load the storyboard, render the
picture, synthesize narration, generate+burn subtitles, mux audio, hand the result to
export_manager. This is what cli.py's `render` command calls once per language x format.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..audio_engine import audio_mixer, tts_engine
from ..schemas.production_manifest import ProductionManifest
from ..storyboard_engine.storyboard_generator import load_storyboard
from ..subtitle_engine import subtitle_formatter, subtitle_generator
from . import export_manager, ffmpeg_renderer

ROOT = Path(__file__).resolve().parents[3]


@dataclass
class ComposeResult:
    video_path: Path
    srt_path: Path
    ass_path: Path
    narration_path: Path


def compose(manifest: ProductionManifest, lang: str, fmt: str, *, root: Path = ROOT,
           quality: str | None = None, tts_provider: str | None = None) -> ComposeResult:
    quality = quality or "medium"
    work = root / "generated" / "scenes" / manifest.topic_id / f"{lang}_{fmt}"
    work.mkdir(parents=True, exist_ok=True)

    storyboard = load_storyboard(manifest.topic_id, lang, root)

    picture = ffmpeg_renderer.render_picture(storyboard, fmt, lang, work, quality=quality)

    provider = tts_engine.get_provider(tts_provider or manifest.audio.provider)
    narration = audio_mixer.synthesize_narration(storyboard.scenes, lang, work / "audio", provider)

    cues = subtitle_generator.cues_for_storyboard(storyboard.scenes)
    width, height = ffmpeg_renderer.RESOLUTIONS[fmt]
    srt_path = subtitle_formatter.write_srt(cues, work / f"{lang}.srt")
    ass_path = subtitle_formatter.write_ass(cues, work / f"{lang}.ass", lang, (width, height))

    captioned = work / "captioned.mp4"
    ffmpeg_renderer.burn_subtitles(picture, ass_path, captioned, work)

    final = export_manager.final_path(manifest.topic_id, lang, fmt, root)
    ffmpeg_renderer.mux_final(captioned, narration, final, work)

    return ComposeResult(video_path=final, srt_path=srt_path, ass_path=ass_path, narration_path=narration)
