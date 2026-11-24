"""Upload to YouTube with the official Data API v3 (OAuth refresh token stored as a secret)."""
from __future__ import annotations

import logging
import time
from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from . import config, ytauth

log = logging.getLogger(__name__)
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def can_upload(lang: str) -> bool:
    """The Google client is configured. A missing/expired token is not a reason to skip: upload() then asks for authorization."""
    return bool(config.YT_CLIENT_ID and config.YT_CLIENT_SECRET)


def _retry(fn, tries: int = 4):
    """Rate limits, 5xx and network errors: back off and retry. Every other error (auth, quota, scope...) is raised at once."""
    for i in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            if ytauth.classify(e) not in ("rate", "retry") or i == tries - 1:
                raise
            log.warning("YouTube said %s (%s); retrying in %d s", ytauth.classify(e), str(e)[:80], 2 ** (i + 1))
            time.sleep(2 ** (i + 1))


def _clean_tags(tags: list[str]) -> list[str]:
    out, total = [], 0
    for t in tags:
        t = t.replace("<", "").replace(">", "").replace("#", "").strip()
        if t and total + len(t) + 3 < 480:
            out.append(t)
            total += len(t) + 3
    return out


def set_thumbnail(yt, video_id: str, thumbnail: Path) -> bool:
    """Upload a custom thumbnail (JPEG/PNG under 2 MB; the channel must be verified). Never raises: a missing thumbnail
    must not lose or re-queue a video that is already on YouTube."""
    try:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumbnail), mimetype="image/jpeg")).execute()
        log.info("Thumbnail set for %s", video_id)
        return True
    except Exception as e:  # noqa: BLE001
        log.warning("Thumbnail upload failed for %s: %s", video_id, str(e)[:200])
        return False


def upload(video: Path, script, lang: str, short: bool = True, description: str | None = None,
           privacy: str | None = None, thumbnail: Path | None = None, synthetic: bool | None = None) -> str:
    """Upload a Short (default) or a long-form video. `description` overrides the script's (chapters added)."""
    creds = _retry(lambda: ytauth.credentials(lang, SCOPES))     # silent refresh; AuthRequired on invalid_grant
    yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
    title = script.title.replace("<", "").replace(">", "").strip()
    description = (description or script.description).replace("<", "").replace(">", "")
    if short:
        title = (title[:90] + " #Shorts") if len(title) <= 90 else title[:100]
        if "#shorts" not in description.lower():
            description += "\n\n#Shorts"
    else:
        title = title[:100]
    body = {
        "snippet": {
            "title": title,
            "description": description[:4900],
            "tags": _clean_tags(script.tags + (["shorts"] if short else [])),
            "categoryId": config.YT_CATEGORY_ID,
            "defaultLanguage": lang,
            "defaultAudioLanguage": lang,
        },
        "status": {
            "privacyStatus": privacy or config.YT_PRIVACY,
            "selfDeclaredMadeForKids": False,
            # YouTube's synthetic-media label: the repository default (see config.py), unless this upload
            # overrides it (e.g. shorts/stockreel used an AI-generated image, which gets flagged regardless)
            "containsSyntheticMedia": config.YT_AI_DISCLOSURE if synthetic is None else synthetic,
        },
    }
    media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=-1, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    response = None
    while response is None:
        status, response = _retry(req.next_chunk)
        if status:
            log.info("Upload %d%%", int(status.progress() * 100))
    vid = response["id"]
    if thumbnail and Path(thumbnail).exists():
        set_thumbnail(yt, vid, Path(thumbnail))
    log.info("Uploaded %s: https://youtube.com/%s%s", lang, "shorts/" if short else "watch?v=", vid)
    return vid
