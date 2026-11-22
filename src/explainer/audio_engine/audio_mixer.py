"""Mixes narration for every scene into one continuous track, with per-scene start times that
match the storyboard (so the renderer and the narration agree on timing) - the audio twin of
how storyboard scenes already carry their own start/end. Background music/SFX mixing reuses
shorts/music.py + shorts/sfx.py via the same cwd-relative FFmpeg pattern shorts/compose.py
already uses, rather than re-implementing loudness-normalised mixing from scratch.
"""
from __future__ import annotations

import subprocess
import wave
from pathlib import Path
from typing import List

from ..schemas.storyboard_schema import Scene
from .tts_engine import TTSProvider


def _run(cmd: list, cwd: Path | None = None) -> None:
    subprocess.run([str(c) for c in cmd], check=True, cwd=cwd)


def synthesize_narration(scenes: List[Scene], lang: str, work: Path, provider: TTSProvider) -> Path:
    """One WAV per scene, concatenated back-to-back at the scene's own start time (silence-padded
    to fill any gap), matching the storyboard's timeline exactly."""
    work.mkdir(parents=True, exist_ok=True)
    clip_paths = []
    for scene in scenes:
        clip = work / f"{scene.scene_id}_{lang}.wav"
        provider.synthesize(scene.narration, clip, lang)
        clip_paths.append((scene, clip))

    with wave.open(str(clip_paths[0][1]), "rb") as w:
        params = w.getparams()
    sr, width, nch = params.framerate, params.sampwidth, params.nchannels
    silence = lambda sec: b"\x00" * max(0, int(sr * sec)) * width * nch   # noqa: E731

    out = work / f"narration_{lang}.wav"
    t = 0.0
    with wave.open(str(out), "wb") as wo:
        wo.setparams(params)
        for scene, clip in clip_paths:
            if scene.start > t:
                wo.writeframes(silence(scene.start - t))
                t = scene.start
            with wave.open(str(clip), "rb") as wi:
                wo.writeframes(wi.readframes(wi.getnframes()))
                clip_duration = wi.getnframes() / sr
            t = scene.start + clip_duration
    return out


def mix_with_video(work: Path, video_in: Path, narration: Path, out: Path, *, lufs: int = -14) -> None:
    """Mux narration onto the rendered (silent) video, loudness-normalised the same way
    shorts/compose.py does its final mix."""
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video_in), "-i", str(narration),
          "-filter_complex", f"[1:a]loudnorm=I={lufs}:TP=-1.5:LRA=11[a]",
          "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
          "-shortest", str(out)], cwd=work)
