"""Check an already-uploaded video's status on YouTube (upload status, privacy, any failure/rejection reason) - useful
when a video shows a blank thumbnail or "No views" right after upload and it's unclear whether it's still
processing or actually failed.

    python -m shorts.check_video VIDEO_ID [VIDEO_ID ...] --lang en
"""
from __future__ import annotations

import argparse
import json
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from . import config, upload

log = logging.getLogger(__name__)


def check(video_ids: list[str], lang: str) -> list[dict]:
    creds = Credentials(None, refresh_token=config.YT_REFRESH_TOKENS[lang], token_uri="https://oauth2.googleapis.com/token",
                        client_id=config.YT_CLIENT_ID, client_secret=config.YT_CLIENT_SECRET, scopes=upload.SCOPES)
    creds.refresh(Request())
    yt = build("youtube", "v3", credentials=creds)
    resp = yt.videos().list(part="status,snippet,contentDetails", id=",".join(video_ids)).execute()
    found = {v["id"]: v for v in resp.get("items", [])}
    out = []
    for vid in video_ids:
        v = found.get(vid)
        if not v:
            out.append({"id": vid, "found": False})
            continue
        st = v.get("status", {})
        out.append({"id": vid, "found": True, "title": v.get("snippet", {}).get("title", ""), "privacyStatus": st.get("privacyStatus"),
                    "uploadStatus": st.get("uploadStatus"), "failureReason": st.get("failureReason"), "rejectionReason": st.get("rejectionReason"),
                    "duration": v.get("contentDetails", {}).get("duration")})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video_ids", nargs="+")
    ap.add_argument("--lang", default="en")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    print(json.dumps(check(a.video_ids, a.lang), ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
