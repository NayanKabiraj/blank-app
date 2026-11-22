"""Daily entry point: plan (written by the scheduled Claude task) -> render (EN + HI) -> upload -> log history.

    python -m shorts.main --plan-file plan.json            # render + upload (normal use)
    python -m shorts.main --plan-file plan.json --dry-run  # render only
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
from .plan import Plan, validate

log = logging.getLogger("shorts")


def _store(video: Path, script, lang: str, thumb: Path | None = None) -> str:
    """Keep every video in videos/<date>/ (uploaded or not), together with the title,
    description and tags, so it can be re-used or uploaded by hand."""
    day = config.VIDEOS_DIR / dt.date.today().isoformat()
    day.mkdir(parents=True, exist_ok=True)
    dest = day / f"{lang}.mp4"
    shutil.copy2(video, dest)
    if thumb:
        shutil.copy2(thumb, day / f"{lang}_thumbnail.jpg")
    (day / f"{lang}_youtube.txt").write_text(
        f"TITLE:\n{script.title} #Shorts\n\nDESCRIPTION:\n{strategy.up_next(script.description, script.next_video, lang)}\n\n"
        f"TAGS:\n{', '.join(script.tags)}\n\nPINNED COMMENT:\n{script.pinned_comment}\n", encoding="utf-8")
    log.info("Saved %s", dest)
    return str(dest.relative_to(config.ROOT))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="render videos but do not upload")
    ap.add_argument("--langs", default=config.LANGS, help="comma-separated: en,hi (default: config.LANGS, English only)")
    ap.add_argument("--plan-file", required=True, help="the plan JSON written by the daily Claude task")
    ap.add_argument("--out", default="output", help="output directory")
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

    scripts = {k: v for k, v in {"en": plan.english, "hi": plan.hindi}.items() if v is not None}
    results, failures = {}, []
    if not args.dry_run and upload.can_upload("en"):   # videos waiting from earlier runs go first
        langs0 = [l.strip() for l in args.langs.split(",") if l.strip()]
        log.info("Queue: %s", pending.flush(langs0))
    for lang in [l.strip() for l in args.langs.split(",") if l.strip()]:
        try:
            video = compose.build(scripts[lang], lang, plan.mood, out / f"work_{lang}", plan.niche)
            final = out / f"{dt.date.today().isoformat()}_{lang}.mp4"
            shutil.move(video, final)
            thumb = thumbs.for_script(scripts[lang], plan.niche, lang, out / f"{dt.date.today().isoformat()}_{lang}.jpg", short=True)
            # Always keep a copy first, so the video is saved even if the upload fails
            entry = {"file": final.name, "saved_to": _store(final, scripts[lang], lang, thumb)}
            if args.dry_run:
                log.info("Dry run: not uploading %s", final)
            else:   # uploads, or queues the video in videos/unpublished/ when YouTube refuses (daily limit)
                entry.update(pending.publish(final, scripts[lang], lang, description=strategy.up_next(scripts[lang].description, scripts[lang].next_video, lang),
                                             topic=plan.topic, thumbnail=thumb))
            results[lang] = entry
        except Exception:  # noqa: BLE001 - keep going so one language can still publish
            log.exception("Failed to produce the %s Short", lang)
            failures.append(lang)

    if not args.dry_run and results:
        config.DATA_DIR.mkdir(exist_ok=True)
        hist = json.loads(config.HISTORY_FILE.read_text()) if config.HISTORY_FILE.exists() else []
        hist.append({"date": dt.date.today().isoformat(), "niche": plan.niche,
                     "topic": plan.topic, "mood": plan.mood, "cluster": plan.cluster,
                     "follow_ups": plan.follow_ups, "next_video": plan.english.next_video, "gate_score": plan.gate_score,
                     "thumbnail_text": plan.english.thumbnail_text, "videos": results})
        plans_dir = config.DATA_DIR / "plans"
        plans_dir.mkdir(exist_ok=True)
        (plans_dir / f"{dt.date.today().isoformat()}.json").write_text(
            plan.model_dump_json(indent=2), encoding="utf-8")
        config.HISTORY_FILE.write_text(json.dumps(hist[-365:], ensure_ascii=False, indent=2) + "\n",
                                       encoding="utf-8")
    log.info("Done: %s", json.dumps(results, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
