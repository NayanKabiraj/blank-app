"""Upload videos that were already rendered and saved under videos/<date>/ (or just check the credentials).

    python -m shorts.upload_saved --date 2026-11-16 --langs en,hi            # upload (privacy from YT_PRIVACY, default private)
    python -m shorts.upload_saved --check                                    # which secrets exist, do the tokens refresh?

Titles, descriptions and tags come from data/plans/<date>.json (the plan the video was made from).
The repository is public, so nothing secret is ever printed: only "set" / "missing" and OK / failed.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from . import config, upload
from .plan import Plan

log = logging.getLogger("shorts.upload_saved")


def check() -> int:
    ok = True
    print(f"YT_CLIENT_ID:     {'set' if config.YT_CLIENT_ID else 'MISSING'}")
    print(f"YT_CLIENT_SECRET: {'set' if config.YT_CLIENT_SECRET else 'MISSING'}")
    print(f"privacy:          {config.YT_PRIVACY}")
    ok &= bool(config.YT_CLIENT_ID and config.YT_CLIENT_SECRET)
    for lang in ("en", "hi"):
        tok = config.YT_REFRESH_TOKENS[lang]
        status = "MISSING"
        if tok and config.YT_CLIENT_ID and config.YT_CLIENT_SECRET:
            try:
                from google.auth.transport.requests import Request
                from google.oauth2.credentials import Credentials
                creds = Credentials(None, refresh_token=tok, token_uri="https://oauth2.googleapis.com/token",
                                    client_id=config.YT_CLIENT_ID, client_secret=config.YT_CLIENT_SECRET,
                                    scopes=upload.SCOPES)
                creds.refresh(Request())
                status = "set, refreshes OK"
            except Exception as e:  # noqa: BLE001
                status = f"set, but refresh FAILED ({type(e).__name__})"
        elif tok:
            status = "set"
        print(f"refresh token {lang}: {status}")
        ok &= status.endswith("OK")
        if lang == "en" and not config.YT_REFRESH_TOKENS["hi"]:
            pass
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default="", help="YYYY-MM-DD of the saved videos")
    ap.add_argument("--langs", default="en,hi")
    ap.add_argument("--check", action="store_true", help="only report which credentials work")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if args.check or not args.date:
        return check()

    raw = (config.DATA_DIR / "plans" / f"{args.date}.json").read_text(encoding="utf-8")
    if '"schemaVersion"' in raw:   # a director manifest: titles, descriptions and tags come from its localizations
        from .director import manifest as dm
        m = dm.complete(json.loads(raw))
        scripts = {lang: dm.script(dm.localize(m, lang)) for lang in ("en", "hi") if lang == "en" or lang in (m.get("localizations") or {})}
    else:
        plan = Plan.model_validate_json(raw)
        scripts = {"en": plan.english, "hi": plan.hindi}
    day = config.VIDEOS_DIR / args.date
    hist_file = config.HISTORY_FILE
    hist = json.loads(hist_file.read_text()) if hist_file.exists() else []
    failures, ids = [], {}
    for lang in [x.strip() for x in args.langs.split(",") if x.strip()]:
        video = day / f"{lang}.mp4"
        if not video.exists():
            log.error("No saved video %s", video)
            failures.append(lang)
        elif not upload.can_upload(lang):
            log.error("YouTube credentials missing for %s", lang)
            failures.append(lang)
        else:
            ids[lang] = upload.upload(video, scripts[lang], lang)
            log.info("Uploaded %s (privacy: %s), video id %s", lang, config.YT_PRIVACY, ids[lang])
    for entry in hist:  # remember the video ids in the history
        if entry.get("date") == args.date:
            for lang, vid in ids.items():
                entry.setdefault("videos", {}).setdefault(lang, {})["video_id"] = vid
    if ids:
        hist_file.write_text(json.dumps(hist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
