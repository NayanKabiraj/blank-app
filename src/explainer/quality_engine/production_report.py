"""Assembles the per-render JSON report (spec section 17: "Generate a production report"):
topic, language, format, every check's result, pass/fail, and where the output files are -
the same shape shorts/cinematic_engine/quality.py's render-report.json already proven useful
for this exact purpose in the existing pipeline.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from . import content_quality, video_quality


def build_report(*, topic_id: str, lang: str, fmt: str, video_path: Path, srt_path: Path,
                 storyboard, cues, expect_width: int, expect_height: int, expect_fps: int,
                 min_duration: float, max_duration: float, render_seconds: float) -> dict:
    video_check = video_quality.check_video(video_path, expect_width=expect_width, expect_height=expect_height,
                                            expect_fps=expect_fps, min_duration=min_duration, max_duration=max_duration)
    black_check = video_quality.check_not_black(video_path, sample_times=[min_duration / 4, min_duration / 2])
    subtitle_problems = content_quality.check_subtitles(cues, lang)
    timing_problems = content_quality.check_storyboard_timing(storyboard)

    ok = video_check["ok"] and not black_check and not subtitle_problems and not timing_problems
    return {
        "topic_id": topic_id, "language": lang, "format": fmt,
        "render_seconds": round(render_seconds, 1),
        "video": video_check,
        "black_frame_warnings": black_check,
        "subtitle_problems": subtitle_problems,
        "storyboard_timing_problems": timing_problems,
        "srt_exists": srt_path.exists(),
        "ok": ok,
        "output": str(video_path),
    }


def write_report(report: dict, topic_id: str, lang: str, fmt: str, root: Path) -> Path:
    out_dir = root / "generated" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{topic_id}_{lang}_{fmt}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
