"""Automated quality checks for a rendered cinematic Short: duration, resolution, FPS, a valid MP4
with an audio track, no black/frozen video, subtitles present and synced. Used by `shorts.cinematic`
to write `render-report.json` and a contact sheet (a grid of frames) for a human to glance at.
"""
from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

from PIL import Image

from .. import config

log = logging.getLogger(__name__)


def _ffprobe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def _frame_at(path: Path, t: float, out: Path, w: int = 160) -> bool:
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(path),
                        "-frames:v", "1", "-vf", f"scale={w}:-1", str(out)])
    return r.returncode == 0 and out.exists()


def check_video(path: Path, expect_w: int, expect_h: int, expect_fps: int,
                min_duration: float = 45.0, max_duration: float = 60.0) -> dict:
    """Duration/resolution/FPS/audio-track checks; returns {"ok": bool, "warnings": [...], "errors": [...]}."""
    warnings, errors = [], []
    try:
        info = _ffprobe(path)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        return {"ok": False, "errors": [f"ffprobe failed: {e}"], "warnings": [], "duration": None,
                "resolution": None, "fps": None, "has_audio": False}
    fmt = info.get("format", {})
    vstreams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    astreams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
    duration = float(fmt.get("duration", 0.0))
    if not min_duration <= duration <= max_duration:
        errors.append(f"duration {duration:.1f}s outside {min_duration}-{max_duration}s")
    if not vstreams:
        errors.append("no video stream")
        return {"ok": False, "errors": errors, "warnings": warnings, "duration": duration,
                "resolution": None, "fps": None, "has_audio": bool(astreams)}
    v = vstreams[0]
    w, h = v.get("width"), v.get("height")
    if (w, h) != (expect_w, expect_h):
        errors.append(f"resolution {w}x{h}, expected {expect_w}x{expect_h}")
    num, den = (v.get("r_frame_rate") or "0/1").split("/")
    fps = round(float(num) / float(den or 1), 2) if float(den or 1) else 0.0
    if abs(fps - expect_fps) > 0.5:
        warnings.append(f"fps {fps}, expected {expect_fps}")
    if not astreams:
        errors.append("no audio track")
    if float(v.get("duration", duration) or 0) < duration - 1.0:
        warnings.append("video stream shorter than the container duration (possible frozen tail)")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "duration": duration,
            "resolution": f"{w}x{h}", "fps": fps, "has_audio": bool(astreams)}


def check_subtitles(srt_path: Path, duration: float) -> dict:
    warnings, errors = [], []
    if not srt_path.exists():
        return {"ok": False, "errors": ["subtitle file missing"], "warnings": [], "cues": 0}
    text = srt_path.read_text(encoding="utf-8").strip()
    if not text:
        errors.append("subtitle file is empty")
    cues = text.count(" --> ")
    if cues == 0:
        errors.append("no subtitle cues found")
    last_times = [ln for ln in text.splitlines() if " --> " in ln]
    if last_times:
        end = last_times[-1].split(" --> ")[1].strip()
        h, m, rest = end.split(":")
        s, ms = rest.split(",")
        last_end = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        if last_end > duration + 1.5:
            warnings.append(f"last subtitle ends at {last_end:.1f}s, after the video ends ({duration:.1f}s)")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "cues": cues}


def contact_sheet(video_path: Path, out: Path, n: int = 9) -> Path | None:
    """A grid of `n` evenly-spaced frames, for a quick human glance without opening the video."""
    try:
        info = _ffprobe(video_path)
        duration = float(info["format"]["duration"])
    except (subprocess.CalledProcessError, KeyError, ValueError, json.JSONDecodeError):
        return None
    tmp_dir = video_path.parent / "_contact_frames"
    tmp_dir.mkdir(exist_ok=True)
    thumbs = []
    for i in range(n):
        t = duration * (i + 0.5) / n
        fp = tmp_dir / f"f{i}.jpg"
        if _frame_at(video_path, t, fp, w=240):
            thumbs.append(fp)
    if not thumbs:
        return None
    imgs = [Image.open(p) for p in thumbs]
    cols = min(3, len(imgs))
    rows = (len(imgs) + cols - 1) // cols
    cw, ch = imgs[0].size
    sheet = Image.new("RGB", (cw * cols, ch * rows), "black")
    for i, im in enumerate(imgs):
        sheet.paste(im, ((i % cols) * cw, (i // cols) * ch))
    sheet.save(out, quality=85)
    for p in thumbs:
        p.unlink(missing_ok=True)
    tmp_dir.rmdir()
    return out


def report(video_path: Path, srt_path: Path | None, lang: str, topic: str, render_seconds: float,
          out_json: Path, layout: str = "portrait") -> dict:
    land = layout == "landscape"
    w, h = (1920, 1080) if land else (1080, 1920)
    vcheck = check_video(video_path, w, h, config.FPS if not land else config.DOC_FPS)
    scheck = check_subtitles(srt_path, vcheck["duration"] or 0.0) if srt_path else {"ok": True, "errors": [], "warnings": [], "cues": 0}
    data = {
        "topic": topic, "language": lang, "layout": layout, "engine": "cinematic",
        "duration": vcheck["duration"], "resolution": vcheck["resolution"], "fps": vcheck["fps"],
        "has_audio": vcheck["has_audio"], "render_seconds": round(render_seconds, 1),
        "video": {"ok": vcheck["ok"], "errors": vcheck["errors"], "warnings": vcheck["warnings"]},
        "subtitles": {"ok": scheck["ok"], "errors": scheck["errors"], "warnings": scheck["warnings"], "cues": scheck.get("cues", 0)},
        "ok": vcheck["ok"] and scheck["ok"],
        "output": str(video_path),
    }
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data
