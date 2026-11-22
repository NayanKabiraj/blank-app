"""Cinematic entry point: the SAME plan schema as the whiteboard pipeline (`shorts.plan.Plan` - every
`graphic` is used, picked by `kind` exactly as the whiteboard explainer picks it), rendered as a premium
motion-graphics Short (deep navy/black, glow, particles, a slow camera drift, FFmpeg crossfades) instead
of a marker-drawn whiteboard. Reuses the existing voice (`shorts.tts`), music/sfx mixing (`shorts.compose`)
and subtitle chunking (`shorts.director.build`) - only the picture is new.

    python -m shorts.cinematic --plan-file plan.json --langs en,hi --out output_cinematic

This renderer never uploads or publishes: it only writes the rendered MP4s, SRT subtitles, thumbnails,
a render-report.json (quality checks) and a contact sheet into `--out`, plus a copy under `videos/<date>/`
so the video is kept regardless of what happens next. Publishing stays a separate, explicit step
(`shorts.pending` / `shorts.upload`), run by hand or by the `upload` workflow format.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import shutil
import sys
import time
from pathlib import Path

from . import compose, config, outro
from .cinematic_engine import quality as cquality
from .cinematic_engine import renderer as crenderer
from .cinematic_engine import effects, typography
from .director import build as dbuild
from .plan import Plan, validate

log = logging.getLogger("shorts.cinematic")


def _burn_captions(video_in: Path, srt_path: Path, out: Path, work: Path, lang: str) -> bool:
    """Best-effort: burn readable mobile captions via FFmpeg's `subtitles` filter (libass + fontconfig).
    Returns False (leaving `video_in` as the final picture) if the system has no matching font."""
    import subprocess
    font_name = "Noto Sans Devanagari" if lang == "hi" else "Noto Sans"
    style = (f"FontName={font_name},Fontsize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00120906,"
            f"BorderStyle=1,Outline=2.4,Shadow=0,Bold=1,Alignment=2,MarginV=190")
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", video_in.name,
             "-vf", f"subtitles={Path(srt_path).name}:force_style='{style}'",
             "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", str(out)],
            cwd=work, check=True)
        return True
    except Exception as e:  # noqa: BLE001 - captions are a nice-to-have, never fail the render for them
        log.warning("Could not burn captions (%s); keeping uncaptioned picture, .srt is still written", e)
        return False


def _thumbnail(script, accent: str, lang: str, out_jpg: Path) -> Path:
    """A simple on-brand thumbnail: the engine's own gradient + glow + the plan's thumbnail_text."""
    from PIL import Image
    w, h = 1080, 1920
    text = script.thumbnail_text or script.hook_text
    canvas = effects.gradient_background(w, h, vignette=0.7).convert("RGBA")
    draw_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    import PIL.ImageDraw as ImageDraw
    draw = ImageDraw.Draw(draw_layer, "RGBA")
    f, lines = typography.fit_size(draw, text, lang, int(w * 0.84), int(h * 0.36), 140, min_size=56)
    line_h = (f.getbbox("Ag")[3] - f.getbbox("Ag")[1]) * 1.2
    y = h * 0.62 - line_h * len(lines) / 2
    for ln in lines:
        tw = draw.textlength(ln, font=f)
        draw.text((w / 2 - tw / 2, y), ln, font=f, fill=(255, 255, 255, 255))
        y += line_h
    canvas.alpha_composite(effects.glow(draw_layer, radius=10, boost=1.15))
    canvas.convert("RGB").save(out_jpg, quality=92)
    return out_jpg


def run(plan: Plan, langs: list[str], out: Path) -> dict:
    today = dt.date.today().isoformat()
    scripts = {"en": plan.english, "hi": plan.hindi}
    results, failures = {}, []
    for lang in langs:
        t0 = time.time()
        try:
            script = outro.with_outro(scripts[lang], lang)
            work = (out / f"work_{lang}").resolve()
            work.mkdir(parents=True, exist_ok=True)
            voice, timeline, voice_end = compose._voice_track(
                script.scenes, lang, work, window=(config.MIN_DURATION, config.MAX_DURATION))
            total = min(config.MAX_DURATION, max(config.MIN_DURATION, voice_end + config.TAIL))
            crenderer.render(script, lang, plan.niche, timeline, total, work)   # writes work/video.mp4

            m = {"captions": {"maximumWordsPerCaption": 6}, "scenes": [
                {"narration": {"text": sc.text, "startSeconds": s, "endSeconds": e}}
                for sc, (s, e, _t) in zip(script.scenes, timeline)
            ]}
            chunks = dbuild.caption_chunks(m, lang)
            srt_path = work / "captions.srt"
            dbuild.srt(chunks, srt_path)
            captioned = work / "video_captioned.mp4"
            if _burn_captions(work / "video.mp4", srt_path, captioned, work, lang):
                shutil.move(captioned, work / "video.mp4")

            final = out / f"{today}_{lang}.mp4"
            compose._mix(work, voice, total, plan.mood, Path(final.name))
            shutil.move(work / final.name, final)

            thumb = out / f"{today}_{lang}.jpg"
            _thumbnail(script, effects.accent_for(0), lang, thumb)
            final_srt = out / f"{today}_{lang}.srt"
            shutil.copy2(srt_path, final_srt)

            report = cquality.report(final, final_srt, lang, plan.topic, time.time() - t0,
                                     out / f"{today}_{lang}_render-report.json")
            sheet = cquality.contact_sheet(final, out / f"{today}_{lang}_contact-sheet.jpg")

            # Same flat videos/<date>/<lang>.mp4 layout the other renderers use (not a cinematic/ subfolder):
            # `shorts.upload_saved --date` and `shorts.pending` look for the video there, so whichever format
            # actually renders a given day's Short, a separate, explicit "upload" workflow run can publish it.
            day = config.VIDEOS_DIR / today
            day.mkdir(parents=True, exist_ok=True)
            shutil.copy2(final, day / f"{lang}.mp4")
            shutil.copy2(final_srt, day / f"{lang}.srt")
            shutil.copy2(thumb, day / f"{lang}_thumbnail.jpg")
            youtube_txt = (f"TITLE:\n{script.title} #Shorts\n\nDESCRIPTION:\n{script.description}\n\n"
                          f"TAGS:\n{', '.join(script.tags)}\n\nPINNED COMMENT:\n{script.pinned_comment}\n")
            (out / f"{today}_{lang}_youtube.txt").write_text(youtube_txt, encoding="utf-8")
            (day / f"{lang}_youtube.txt").write_text(youtube_txt, encoding="utf-8")

            results[lang] = {"file": final.name, "engine": "cinematic", "saved_to": f"videos/{today}/{lang}.mp4",
                             "report": report, "contact_sheet": str(sheet) if sheet else None}
            if not report["ok"]:
                log.warning("%s: quality checks failed: %s", lang, report["video"]["errors"] + report["subtitles"]["errors"])
        except Exception:  # noqa: BLE001 - keep going so the other language can still render
            log.exception("Failed to produce the %s cinematic Short", lang)
            failures.append(lang)

    if results:
        config.DATA_DIR.mkdir(exist_ok=True)
        hist = json.loads(config.HISTORY_FILE.read_text()) if config.HISTORY_FILE.exists() else []
        hist.append({"date": today, "niche": plan.niche, "topic": plan.topic, "mood": plan.mood, "cluster": plan.cluster,
                     "follow_ups": plan.follow_ups, "next_video": plan.english.next_video, "gate_score": plan.gate_score,
                     "engine": "cinematic", "videos": results})
        config.HISTORY_FILE.write_text(json.dumps(hist[-365:], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # same place shorts.upload_saved/-shorts.pending read titles/descriptions/tags from for a later publish
        plans_dir = config.DATA_DIR / "plans"
        plans_dir.mkdir(exist_ok=True)
        (plans_dir / f"{today}.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    return {"results": results, "failures": failures}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-file", required=True, help="the plan JSON written by the daily Claude task")
    ap.add_argument("--langs", default="en,hi", help="comma-separated: en,hi")
    ap.add_argument("--out", default="output_cinematic", help="output directory")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    plan = Plan.model_validate_json(Path(args.plan_file).read_text(encoding="utf-8"))
    for problem in validate(plan):
        log.warning("Plan check: %s", problem)
    (out / "plan.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    langs = [l.strip() for l in args.langs.split(",") if l.strip()]
    outcome = run(plan, langs, out)
    log.info("Done: %s", json.dumps({l: {"file": r["file"], "ok": r["report"]["ok"]} for l, r in outcome["results"].items()}, ensure_ascii=False))
    return 1 if outcome["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
