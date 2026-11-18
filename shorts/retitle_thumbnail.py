"""Redraw and re-upload the thumbnail of a video that is already on YouTube (e.g. after a thumbnail design change).

    python -m shorts.retitle_thumbnail --video-id WmKvkO7H8gs --headline "Why are there two tides every day?" \
        --lang en --short false --tag SPACE --title "How the Moon Moves the Ocean"

Never touches the video itself, only `thumbnails().set`.
"""
from __future__ import annotations

import argparse
import logging
import tempfile
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from . import config, upload
from .director import manifest as M, thumbnail as T

log = logging.getLogger(__name__)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--video-id", required=True)
    ap.add_argument("--headline", required=True)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--short", default="false")
    ap.add_argument("--tag", default="")
    ap.add_argument("--title", default="")
    ap.add_argument("--stock-query", default="")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    short = a.short.lower() in ("1", "true", "yes")
    head = T.shorten(a.headline)
    spec = {"headline": head, "lang": a.lang, "sceneType": "object-assembly", "environment": "abstract-dark", "objects": None,
            "accentWords": T._accent_words(head, None, a.lang), "palette": M.DEFAULTS["brandSystem"]["defaultPalette"],
            "seed": sum(map(ord, a.title or head)) % 100000, "concept": "", "title": a.title or head,
            "tag": a.tag or T.pick_tag(a.title or head, "Space & Universe", None, a.lang)}
    if a.stock_query:
        spec["stock_query"] = a.stock_query
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "thumbnail.jpg"
        if not T.render(spec, out, "short" if short else "long"):
            log.error("Render failed for %s", a.video_id)
            return 1
        creds = Credentials(None, refresh_token=config.YT_REFRESH_TOKENS[a.lang], token_uri="https://oauth2.googleapis.com/token",
                            client_id=config.YT_CLIENT_ID, client_secret=config.YT_CLIENT_SECRET, scopes=upload.SCOPES)
        creds.refresh(Request())
        yt = build("youtube", "v3", credentials=creds)
        ok = upload.set_thumbnail(yt, a.video_id, out)
        return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
