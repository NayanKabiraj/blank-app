"""Mode B pipeline: approved modules -> narration -> render -> mix -> final mp4 (no Claude session needed)."""
from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path

from .authoring import safety
from .registry import animation_registry as reg

ROOT = Path(__file__).resolve().parent.parent
LEAD, TAIL = 0.45, 0.5


def _ceil_frames(seconds: float, fps: int) -> float:
    return math.ceil(seconds * fps) / fps


def plan_durations(cfg: dict, narration_secs: list[float], fps: int) -> list[float]:
    out = []
    for s, n in zip(cfg["scenes"], narration_secs):
        out.append(_ceil_frames(max(s.get("min_seconds", 4.0), n + s.get("pad_before", LEAD) + s.get("pad_after", TAIL) + 0.5), fps))
    return out


def render_topic(topic_id: str, out_dir: Path, *, preview: bool = False, voice: str = "auto",
                 require_approved: bool = True, narrate: bool = True) -> dict:
    from . import audio
    cfg = reg.load_config(topic_id)
    problems = safety.scan_dir(reg.topic_dir(topic_id))
    if problems:
        raise SystemExit("safety scan failed:\n  " + "\n  ".join(problems))
    if require_approved:
        ok, why = reg.check_approved(topic_id)
        if not ok:
            raise SystemExit(why)
    out_dir = Path(out_dir).resolve()
    work = out_dir / "work"
    work.mkdir(parents=True, exist_ok=True)
    fps = 12 if preview else cfg.get("fps", 24)
    w, h = (360, 640) if preview else tuple(cfg.get("resolution", [720, 1280]))

    # 1. narration per scene (existing TTS, offline fallback is recorded as provenance)
    wavs, secs, providers = [], [], set()
    for i, s in enumerate(cfg["scenes"]):
        wav, prov = audio.synthesize_line(s["narration"], work / f"line_{i + 1:02d}.wav", cfg.get("language", "en"), voice)
        wavs.append(wav); secs.append(audio.wav_seconds(wav)); providers.add(prov)
    durations = plan_durations(cfg, secs, 24)
    starts, t = [], 0.0
    for d, s in zip(durations, cfg["scenes"]):
        starts.append(t + s.get("pad_before", LEAD)); t += d
    total = t
    voice_wav = audio.place_track(wavs, starts, total, work / "narration.wav")
    narration = audio.Narration(voice_wav, fps=24)

    # 2. render the Claude-authored scene code with Manim
    import manim
    from manim import config as mc
    from .renderer import GeneratedScene
    mc.pixel_width, mc.pixel_height, mc.frame_rate = w, h, fps
    mc.frame_height, mc.frame_width = 16.0, 9.0
    mc.media_dir = str(work / "media")
    mc.output_file = "picture"
    mc.disable_caching = True
    mc.verbosity = "WARNING"
    mc.progress_bar = "none"
    mc.write_to_movie = True
    modules = reg.scene_modules(topic_id)
    scene_cfgs = [{**c, "narration_seconds": n} for c, n in zip(cfg["scenes"], secs)]
    scene = GeneratedScene(modules, durations, scene_cfgs, narration=narration)
    scene.render()
    picture = Path(scene.renderer.file_writer.movie_file_path)
    shutil.copy(picture, out_dir / ("preview_silent.mp4" if preview else "picture.mp4"))

    info = {"topic_id": topic_id, "title": cfg["title"], "resolution": [w, h], "fps": fps, "scenes": scene.reports,
            "durations": durations, "total_seconds": total, "narration_provider": sorted(providers)}
    if preview:
        info["picture"] = str(out_dir / "preview_silent.mp4")
    elif narrate:
        final = out_dir / f"{topic_id}.mp4"
        info["music"] = audio.mix_final(out_dir / "picture.mp4", voice_wav, cfg.get("mood", "inspiring"), total, final, work)
        info["final"] = str(final)
    (out_dir / "render_report.json").write_text(json.dumps(info, indent=2))
    return info
