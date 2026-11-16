"""Keep the repository small: delete the saved videos of earlier days.

    python -m shorts.cleanup              # keep today and yesterday (KEEP_DAYS=1), delete older videos/<date>/ folders
    python -m shorts.cleanup --keep-days 0   # keep only today's
    python -m shorts.cleanup --dry-run    # only list what would go

Only folders named like a date (videos/2026-11-16/) are touched, so voice samples and anything else under videos/ stay.
The workflow runs this before it commits, so each new run replaces the old files. Titles, descriptions and the topic
history live in data/ and are kept. Old videos remain in git history (a normal delete does not rewrite it).
"""
from __future__ import annotations

import argparse
import datetime as dt
import logging
import os
import re
import shutil
import sys

from . import config

log = logging.getLogger("shorts.cleanup")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def old_folders(today: dt.date, keep_days: int) -> list:
    if not config.VIDEOS_DIR.is_dir():
        return []
    cutoff = today - dt.timedelta(days=keep_days)
    out = []
    for p in sorted(config.VIDEOS_DIR.iterdir()):
        if p.is_dir() and DATE.match(p.name):
            try:
                if dt.date.fromisoformat(p.name) < cutoff:
                    out.append(p)
            except ValueError:
                continue
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-days", type=int, default=int(os.getenv("KEEP_DAYS", "1")),
                    help="keep videos from the last N days besides today (default 1: today and yesterday)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    gone = old_folders(dt.date.today(), args.keep_days)
    for p in gone:
        size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file()) / 1e6
        log.info("%s %s (%.1f MB)", "Would delete" if args.dry_run else "Deleting", p.relative_to(config.ROOT), size)
        if not args.dry_run:
            shutil.rmtree(p)
    if not gone:
        log.info("Nothing older than %d day(s) to delete", args.keep_days)
    return 0


if __name__ == "__main__":
    sys.exit(main())
