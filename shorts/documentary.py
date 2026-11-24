"""Documentary entry point: a long-form (5-15 minute) landscape video in English and Hindi.

    python -m shorts.documentary --plan-file doc.json            # render + upload (when secrets exist)
    python -m shorts.documentary --plan-file doc.json --dry-run  # render only

The plan is written by the documentary Claude task (shorts/CLAUDE_DOCUMENTARY_TASK.md) and follows
`DocPlan` in shorts/plan.py. The look, voice (Piper), music and sound effects are the same as the Shorts;
the picture is 1920x1080 at 24 fps with the diagram on the right and the headline on the left.
Videos are not committed to the repo (they are large) unless --keep-in-repo is given; they are kept as
workflow artifacts and uploaded to YouTube.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import shutil
import sys
from pathlib import Path

from . import compose, config, pending, upload
from .director import thumbnail as thumbs
from . import strategy
from .plan import DocPlan, doc_seconds, validate_doc

log = logging.getLogger("shorts.documentary")


def _stamp(sec: float) -> str:
    sec = int(sec)
    return f"{sec // 60}:{sec % 60:02d}" if sec < 3600 else f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def chapter_description(base: str, chapters: list[tuple[str, float]]) -> str:
    """The description with YouTube chapter markers (the first must be 0:00, at least 3, 10 s apart)."""
    lines = "\n".join(f"{_stamp(t)} {title}" for title, t in chapters)
    return f"{base}\n\nChapters:\n{lines}\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-file", required=True)
    ap.add_argument("--langs", default=config.LANGS)
    ap.add_argument("--dry-run", action="store_true", help="render but do not upload")
    ap.add_argument("--keep-in-repo", action="store_true", help="copy the videos into videos/<date>/")
    ap.add_argument("--out", default="output_documentary")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    plan = DocPlan.model_validate_json(Path(args.plan_file).read_text(encoding="utf-8"))
    for problem in validate_doc(plan):
        log.warning("Plan check: %s", problem)
    (out / "plan.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")

    scripts = {k: v for k, v in {"en": plan.english, "hi": plan.hindi}.items() if v is not None}
    today = dt.date.today().isoformat()
    if not args.dry_run and upload.can_upload("en"):   # videos waiting from earlier runs go first
        log.info("Queue: %s", pending.flush([x.strip() for x in args.langs.split(",") if x.strip()]))
    results, failures = {}, []
    for lang in [x.strip() for x in args.langs.split(",") if x.strip()]:
        try:
            script = scripts[lang]
            log.info("Documentary %s: about %.1f minutes planned", lang, doc_seconds(script, lang) / 60)
            video, chapters = compose.build_documentary(script, lang, plan.mood, out / f"work_{lang}", plan.niche)
            desc = chapter_description(strategy.with_subscribe(strategy.with_sources(strategy.up_next(script.description, script.next_video, lang), plan.research_summary), lang), chapters)
            thumb = thumbs.for_script(script, plan.niche, lang, out / f"{today}_documentary_{lang}.jpg", short=False)
            final = out / f"{today}_documentary_{lang}.mp4"
            shutil.move(video, final)
            (out / f"{today}_documentary_{lang}_youtube.txt").write_text(
                f"TITLE:\n{script.title}\n\nDESCRIPTION:\n{desc}\nTAGS:\n{', '.join(script.tags)}\n\nPINNED COMMENT:\n{script.pinned_comment}\n", encoding="utf-8")
            entry = {"file": final.name, "chapters": [{"title": t, "start": round(s, 1)} for t, s in chapters]}
            if args.keep_in_repo:
                day = config.VIDEOS_DIR / today
                day.mkdir(parents=True, exist_ok=True)
                shutil.copy2(final, day / f"documentary_{lang}.mp4")
                shutil.copy2(out / f"{today}_documentary_{lang}_youtube.txt", day / f"documentary_{lang}_youtube.txt")
                entry["saved_to"] = f"videos/{today}/documentary_{lang}.mp4"
            if args.dry_run:
                log.info("Dry run: not uploading %s", final)
            else:   # uploads, or queues the video in videos/unpublished/ when YouTube refuses (daily limit)
                entry.update(pending.publish(final, script, lang, short=False, description=desc, topic=plan.topic, thumbnail=thumb))
            results[lang] = entry
        except Exception:  # noqa: BLE001 - keep going so the other language can still be made
            log.exception("Failed to produce the %s documentary", lang)
            failures.append(lang)

    if not args.dry_run and results:
        config.DATA_DIR.mkdir(exist_ok=True)
        hist_file = config.DATA_DIR / "documentary_history.json"
        hist = json.loads(hist_file.read_text()) if hist_file.exists() else []
        hist.append({"date": today, "niche": plan.niche, "topic": plan.topic, "minutes": plan.target_minutes, "cluster": plan.cluster,
                     "follow_ups": plan.follow_ups, "next_video": plan.english.next_video, "gate_score": plan.gate_score,
                     "videos": results})
        hist_file.write_text(json.dumps(hist[-200:], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log.info("Done: %s", json.dumps(results, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
