"""Upload to YouTube with the official Data API v3 (OAuth refresh token stored as a secret)."""
from __future__ import annotations

import logging
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from . import config
from .research import LangScript

log = logging.getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def can_upload(lang: str) -> bool:
    return bool(config.YT_CLIENT_ID and config.YT_CLIENT_SECRET and config.YT_REFRESH_TOKENS[lang])


def _clean_tags(tags: list[str]) -> list[str]:
    out, total = [], 0
    for t in tags:
        t = t.replace("<", "").replace(">", "").replace("#", "").strip()
        if t and total + len(t) + 3 < 480:
            out.append(t)
            total += len(t) + 3
    return out


def upload(video: Path, script: LangScript, lang: str) -> str:
    creds = Credentials(
        None,
        refresh_token=config.YT_REFRESH_TOKENS[lang],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config.YT_CLIENT_ID,
        client_secret=config.YT_CLIENT_SECRET,
        scopes=SCOPES,
    )
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    title = script.title.replace("<", "").replace(">", "").strip()
    title = (title[:90] + " #Shorts") if len(title) <= 90 else title[:100]
    description = script.description.replace("<", "").replace(">", "")
    if "#shorts" not in description.lower():
        description += "\n\n#Shorts"
    body = {
        "snippet": {
            "title": title,
            "description": description[:4900],
            "tags": _clean_tags(script.tags + ["shorts"]),
            "categoryId": config.YT_CATEGORY_ID,
            "defaultLanguage": lang,
            "defaultAudioLanguage": lang,
        },
        "status": {
            "privacyStatus": config.YT_PRIVACY,
            "selfDeclaredMadeForKids": False,
            # Narration is AI-generated: disclose it, as YouTube's policy requires for
            # realistic synthetic content.
            "containsSyntheticMedia": True,
        },
    }
    media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=-1, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = req.next_chunk()
        if status:
            log.info("Upload %d%%", int(status.progress() * 100))
    vid = response["id"]
    log.info("Uploaded %s: https://youtube.com/shorts/%s", lang, vid)
    return vid
