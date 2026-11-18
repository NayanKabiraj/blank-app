"""Compose the stock-footage picture: one Pexels clip per scene (trimmed or looped to the scene's real spoken
length), cut together, with burned-in captions (2-6 words at a time, one highlighted) timed to the voice-over.
Reuses the director pipeline's caption chunker (same word-by-word timing math, same `maximumWordsPerCaption`
spec) so captions look and behave the same across all three video styles.
"""
from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path

from ..director import build as dbuild
from . import fetch

log = logging.getLogger(__name__)
STOPWORDS = {"the", "a", "an", "is", "are", "was", "were", "to", "of", "in", "on", "at", "for", "and", "or",
             "but", "so", "you", "your", "it", "this", "that", "right", "now", "what", "if", "do", "does", "can"}
FONT_DIR = Path(__file__).resolve().parents[1] / "explainer" / "fonts"   # Kalam woff2 (Latin + Devanagari), already in the repo


def _run(cmd, cwd=None):
    log.debug("$ %s", " ".join(map(str, cmd)))
    subprocess.run([str(c) for c in cmd], check=True, cwd=cwd)


def scene_query(scene, niche: str, lang: str) -> str:
    """A short, concrete search phrase for the stock library: the scene's keyword if Claude wrote one, else the
    first few meaningful words of the narration, else the niche."""
    if getattr(scene, "keyword", None):
        return scene.keyword
    ws = [w.strip(".,?!।—-’'\"") for w in scene.text.split()]
    picked = [w for w in ws if w.lower() not in STOPWORDS and len(w) > 2][:4]
    return " ".join(picked) or niche or "abstract background"


def _clip_for(query: str, out: Path, w: int, h: int, duration: float, seed: int) -> Path:
    """A clip covering `duration` seconds at w x h: a downloaded Pexels clip (trimmed or looped), or a gradient
    placeholder when nothing was found."""
    orientation = "portrait" if h > w else "landscape"
    raw = out.with_suffix(".src.mp4")
    got = fetch.download_clip(query, raw, orientation, min_duration=min(2.0, duration), seed=seed)
    if not got:
        return fetch.placeholder_clip(out, duration, w, h, seed=seed)
    # cover-fit to w x h, then loop if the clip is shorter than the scene, trim if longer
    vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", raw.name, "-t", f"{duration:.2f}",
          "-vf", vf, "-an", "-r", "30", str(out)], cwd=out.parent)
    return out


def _concat(clips: list[Path], out: Path, work: Path) -> None:
    listfile = work / "clips.txt"
    listfile.write_text("".join(f"file '{c.name}'\n" for c in clips), encoding="utf-8")
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listfile.name,
          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], cwd=work)


def _burn_captions(video_in: Path, srt_path: Path, out: Path, work: Path, land: bool) -> None:
    size = 15 if land else 20
    style = (f"FontName=Kalam,Fontsize={size},PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,"
             f"BorderStyle=1,Outline=3,Shadow=0,Bold=1,Alignment=2,MarginV={60 if land else 170}")
    _run(["ffmpeg", "-y", "-loglevel", "error", "-i", video_in.name,
          "-vf", f"subtitles={srt_path.name}:fontsdir={FONT_DIR}:force_style='{style}'",
          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)], cwd=work)


def render(scenes, lang: str, niche: str, timeline: list[tuple[float, float, str]], total: float, work: Path,
           layout: str = "portrait", fps: int = 30) -> None:
    """Write `work/video.mp4`: stock footage cut to the real scene timing, with burned captions. Same call shape
    as `shorts.animate.render`, so `shorts.compose.build`/`build_documentary` could call either one."""
    w, h = (1080, 1920) if layout == "portrait" else (1920, 1080)
    land = layout != "portrait"
    work.mkdir(parents=True, exist_ok=True)
    clips = []
    prev_end = 0.0
    for i, (sc, (s, e, _text)) in enumerate(zip(scenes, timeline)):
        q = scene_query(sc, niche, lang)
        d = max(0.6, e - prev_end)   # covers this scene's speech AND the silent lead-in/gap before it: no gaps in the picture
        clip = _clip_for(q, work / f"scene_{i}.mp4", w, h, d, seed=hash((q, i)) & 0xFFFF)
        clips.append(clip)
        prev_end = e
    if total > timeline[-1][1]:   # the mix pads with a tail (outro music/breathing room): hold the last frame
        tail = work / "tail.mp4"
        _run(["ffmpeg", "-y", "-loglevel", "error", "-sseof", "-0.1", "-i", clips[-1].name, "-t", f"{total - timeline[-1][1]:.2f}",
              "-vf", "loop=loop=-1:size=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(tail)], cwd=work)
        clips.append(tail)
    joined = work / "joined.mp4"
    _concat(clips, joined, work)
    # captions: build a {"narration": {text,start,end}} manifest shim and reuse the director pipeline's chunker
    m = {"captions": {"maximumWordsPerCaption": 6}, "scenes": [
        {"narration": {"text": sc.text, "startSeconds": s, "endSeconds": e}} for sc, (s, e, _t) in zip(scenes, timeline)
    ]}
    chunks = dbuild.caption_chunks(m, lang)
    srt_path = work / "captions.srt"
    dbuild.srt(chunks, srt_path)
    _burn_captions(joined, srt_path, work / "video.mp4", work, land)
