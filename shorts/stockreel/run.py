"""Stock-footage entry point: the SAME plan schema as the whiteboard pipeline (`shorts.plan.Plan`/`DocPlan` -
`graphic` on each scene is simply ignored) rendered with real Pexels footage instead of the drawn whiteboard,
with the same upload queue, thumbnail-with-headline and history as the other two styles.

    python -m shorts.stockreel.run --plan-file plan.json                       # Short: render + upload
    python -m shorts.stockreel.run --plan-file doc.json --documentary          # documentary
    python -m shorts.stockreel.run --plan-file plan.json --dry-run             # render only

Uses Wikimedia Commons (public domain/CC0 photos, no API key, no signup) animated with a slow Ken Burns pan/zoom;
a scene whose search finds nothing renders as a soft gradient placeholder instead, so a miss degrades the look
rather than failing the run.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import shutil
import sys
from pathlib import Path

from .. import config, pending, strategy, upload
from ..plan import DocPlan, Plan, doc_seconds, validate, validate_doc
from . import build, thumbnail as thumbs

log = logging.getLogger("shorts.stockreel")


def _stamp(sec: float) -> str:
    sec = int(sec)
    return f"{sec // 60}:{sec % 60:02d}" if sec < 3600 else f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def run_short(plan: Plan, langs: list[str], out: Path, dry_run: bool) -> dict:
    scripts = {"en": plan.english, "hi": plan.hindi}
    today = dt.date.today().isoformat()
    results, failures = {}, []
    if not dry_run and upload.can_upload("en"):
        log.info("Queue: %s", pending.flush(langs))
    for lang in langs:
        try:
            script = scripts[lang]
            video, used_ai = build.build_short(script, lang, plan.mood, out / f"work_{lang}", plan.niche)
            final = out / f"{today}_{lang}.mp4"
            shutil.move(video, final)
            thumb = thumbs.for_script(script, plan.niche, lang, out / f"{today}_{lang}.jpg", short=True)
            desc = strategy.up_next(script.description, script.next_video, lang)
            (out / f"{today}_{lang}_youtube.txt").write_text(
                f"TITLE:\n{script.title} #Shorts\n\nDESCRIPTION:\n{desc}\n\nTAGS:\n{', '.join(script.tags)}\n\nPINNED COMMENT:\n{script.pinned_comment}\n", encoding="utf-8")
            entry = {"file": final.name, "engine": "stockreel", "synthetic": used_ai}
            day = config.VIDEOS_DIR / today
            day.mkdir(parents=True, exist_ok=True)
            shutil.copy2(final, day / f"{lang}.mp4")
            shutil.copy2(out / f"{today}_{lang}_youtube.txt", day / f"{lang}_youtube.txt")
            if thumb and Path(thumb).exists():
                shutil.copy2(thumb, day / f"{lang}_thumbnail.jpg")
            entry["saved_to"] = f"videos/{today}/{lang}.mp4"
            if dry_run:
                log.info("Dry run: not uploading %s", final)
            else:
                entry.update(pending.publish(final, script, lang, description=desc, topic=plan.topic, thumbnail=thumb, synthetic=used_ai))
            results[lang] = entry
        except Exception:  # noqa: BLE001 - keep going so the other language can still be made
            log.exception("Failed to produce the %s stock-footage Short", lang)
            failures.append(lang)
    if not dry_run and results:
        config.DATA_DIR.mkdir(exist_ok=True)
        hist = json.loads(config.HISTORY_FILE.read_text()) if config.HISTORY_FILE.exists() else []
        hist.append({"date": today, "niche": plan.niche, "topic": plan.topic, "mood": plan.mood, "cluster": plan.cluster,
                     "follow_ups": plan.follow_ups, "next_video": plan.english.next_video, "gate_score": plan.gate_score,
                     "engine": "stockreel", "videos": results})
        plans_dir = config.DATA_DIR / "plans"
        plans_dir.mkdir(exist_ok=True)
        (plans_dir / f"{today}.json").write_text(plan.model_dump_json(indent=2), encoding="utf-8")
        config.HISTORY_FILE.write_text(json.dumps(hist[-365:], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"results": results, "failures": failures}


def run_documentary(plan: DocPlan, langs: list[str], out: Path, dry_run: bool, keep_in_repo: bool) -> dict:
    scripts = {"en": plan.english, "hi": plan.hindi}
    today = dt.date.today().isoformat()
    if not dry_run and upload.can_upload("en"):
        log.info("Queue: %s", pending.flush(langs))
    results, failures = {}, []
    for lang in langs:
        try:
            script = scripts[lang]
            log.info("Stock-footage documentary %s: about %.1f minutes planned", lang, doc_seconds(script, lang) / 60)
            video, chapters, used_ai = build.build_documentary(script, lang, plan.mood, out / f"work_{lang}", plan.niche)
            lines = "\n".join(f"{_stamp(s)} {t}" for t, s in chapters)
            desc = f"{strategy.up_next(script.description, script.next_video, lang)}\n\nChapters:\n{lines}\n"
            thumb = thumbs.for_script(script, plan.niche, lang, out / f"{today}_documentary_{lang}.jpg", short=False)
            final = out / f"{today}_documentary_{lang}.mp4"
            shutil.move(video, final)
            (out / f"{today}_documentary_{lang}_youtube.txt").write_text(
                f"TITLE:\n{script.title}\n\nDESCRIPTION:\n{desc}\nTAGS:\n{', '.join(script.tags)}\n\nPINNED COMMENT:\n{script.pinned_comment}\n", encoding="utf-8")
            entry = {"file": final.name, "engine": "stockreel", "synthetic": used_ai, "chapters": [{"title": t, "start": round(s, 1)} for t, s in chapters]}
            if keep_in_repo:
                day = config.VIDEOS_DIR / today
                day.mkdir(parents=True, exist_ok=True)
                shutil.copy2(final, day / f"documentary_{lang}.mp4")
                shutil.copy2(out / f"{today}_documentary_{lang}_youtube.txt", day / f"documentary_{lang}_youtube.txt")
                entry["saved_to"] = f"videos/{today}/documentary_{lang}.mp4"
            if dry_run:
                log.info("Dry run: not uploading %s", final)
            else:
                entry.update(pending.publish(final, script, lang, short=False, description=desc, topic=plan.topic, thumbnail=thumb, synthetic=used_ai))
            results[lang] = entry
        except Exception:  # noqa: BLE001 - keep going so the other language can still be made
            log.exception("Failed to produce the %s stock-footage documentary", lang)
            failures.append(lang)
    if not dry_run and results:
        hist_file = config.DATA_DIR / "documentary_history.json"
        hist = json.loads(hist_file.read_text()) if hist_file.exists() else []
        hist.append({"date": today, "niche": plan.niche, "topic": plan.topic, "cluster": plan.cluster, "follow_ups": plan.follow_ups,
                     "next_video": plan.english.next_video, "gate_score": plan.gate_score, "engine": "stockreel", "videos": results})
        hist_file.write_text(json.dumps(hist[-200:], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"results": results, "failures": failures}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-file", required=True)
    ap.add_argument("--langs", default="en,hi")
    ap.add_argument("--documentary", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="render but do not upload")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--keep-in-repo", action="store_true", help="documentaries: also copy the video into videos/<date>/")
    ap.add_argument("--out", default="output_stockreel")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    langs = [x.strip() for x in args.langs.split(",") if x.strip()]
    raw = Path(args.plan_file).read_text(encoding="utf-8")

    if args.documentary:
        plan = DocPlan.model_validate_json(raw)
        problems = validate_doc(plan)
    else:
        plan = Plan.model_validate_json(raw)
        problems = validate(plan)
    for p in problems:
        log.warning("Plan check: %s", p)
    if args.validate_only:
        log.info("Plan OK: %s | %d problem(s)", plan.topic, len(problems))
        return 0

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "plan.json").write_text(raw, encoding="utf-8")
    r = run_documentary(plan, langs, out, args.dry_run, args.keep_in_repo) if args.documentary else run_short(plan, langs, out, args.dry_run)
    (out / "result.json").write_text(json.dumps(r["results"], ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("Done: %s", json.dumps(r["results"], ensure_ascii=False))
    return 1 if r["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
