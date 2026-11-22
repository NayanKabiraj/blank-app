"""Command-line entry point.

    python -m explainer.cli validate-manifest content/manifests/<id>.json
    python -m explainer.cli render --topic-id <id> --lang en --format vertical [--style cinematic]
    python -m explainer.cli demo                      # renders the bundled sample topic, no network

Run with the repo root on PYTHONPATH and `src` added (see docs/installation.md), or via
`python -m src.explainer.cli` from the repo root.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _cmd_validate_manifest(args) -> int:
    from .schemas.production_manifest import load_manifest
    from .research_engine.source_validator import validate_research
    from .research_engine.fact_checker import check_summary

    manifest = load_manifest(Path(args.manifest))
    problems = validate_research(manifest.research) + check_summary(manifest.research.summary)
    for lang in manifest.production.languages:
        sb_path = manifest.storyboard_path(lang, ROOT)
        if not sb_path.exists():
            problems.append(f"storyboard missing for {lang}: {sb_path}")
    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {manifest.topic_id} | {manifest.topic}")
    return 0


def _cmd_render(args) -> int:
    from .schemas.production_manifest import load_manifest
    from .video_engine import video_composer
    from .quality_engine import production_report
    from .subtitle_engine.subtitle_generator import cues_for_storyboard
    from .storyboard_engine.storyboard_generator import load_storyboard
    from .video_engine.ffmpeg_renderer import RESOLUTIONS, QUALITY_FPS
    from .config.settings import load_config

    manifest_path = args.manifest or (ROOT / "content" / "manifests" / f"{args.topic_id}.json")
    manifest = load_manifest(Path(manifest_path))
    cfg = load_config()

    t0 = time.time()
    result = video_composer.compose(manifest, args.lang, args.format, root=ROOT,
                                    quality=args.quality or cfg.render.quality)
    elapsed = time.time() - t0

    storyboard = load_storyboard(manifest.topic_id, args.lang, ROOT)
    cues = cues_for_storyboard(storyboard.scenes)
    width, height = RESOLUTIONS[args.format]
    fps = QUALITY_FPS.get(args.quality or cfg.render.quality, 24)
    report = production_report.build_report(
        topic_id=manifest.topic_id, lang=args.lang, fmt=args.format,
        video_path=result.video_path, srt_path=result.srt_path, storyboard=storyboard, cues=cues,
        expect_width=width, expect_height=height, expect_fps=fps,
        min_duration=manifest.production.duration_seconds - 10,
        max_duration=manifest.production.duration_seconds + 10,
        render_seconds=elapsed)
    report_path = production_report.write_report(report, manifest.topic_id, args.lang, args.format, ROOT)

    print(f"Rendered: {result.video_path}")
    print(f"Report:   {report_path} (ok={report['ok']})")
    if not report["ok"]:
        print("Problems:", report["video"]["errors"] + report["black_frame_warnings"] +
              report["subtitle_problems"] + report["storyboard_timing_problems"])
    return 0 if report["ok"] else 1


def _cmd_demo(args) -> int:
    """Renders the bundled sample topic (content/manifests/sample_topic_001.json) end to end,
    English, vertical, cinematic style - no network, no paid service (spec section 22's demo
    requirement). Set SHORTS_FAKE_TTS=1 first for a narration-free offline smoke test."""
    args.topic_id = "sample_topic_001"
    args.manifest = ROOT / "content" / "manifests" / "sample_topic_001.json"
    args.lang = "en"
    args.format = "vertical"
    args.quality = "draft"
    return _cmd_render(args)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="explainer")
    sub = ap.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate-manifest")
    p_val.add_argument("manifest")
    p_val.set_defaults(func=_cmd_validate_manifest)

    p_render = sub.add_parser("render")
    p_render.add_argument("--topic-id")
    p_render.add_argument("--manifest")
    p_render.add_argument("--lang", choices=["en", "hi"], required=True)
    p_render.add_argument("--format", choices=["vertical", "landscape"], required=True)
    p_render.add_argument("--quality", choices=["draft", "medium", "high"])
    p_render.set_defaults(func=_cmd_render)

    p_demo = sub.add_parser("demo")
    p_demo.set_defaults(func=_cmd_demo)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
