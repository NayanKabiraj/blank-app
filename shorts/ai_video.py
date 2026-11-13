"""AI-generated video clips for selected scenes, using free models.

Pipeline for one clip (each step falls back to the next):
  1. A still image from Pollinations (`gen.pollinations.ai`, model tongyi-mai/z-image-turbo,
     which is not paid-only). It needs a key from a free account: set POLLINATIONS_KEY.
  2. "wan": animate that image with Wan 2.2 image-to-video on a free Hugging Face ZeroGPU
     Space (HF_TOKEN gives your free account's daily GPU quota).
  3. "ltx": text-to-video with LTX-Video on a free Hugging Face ZeroGPU Space.
  4. "pollinations": Pollinations video models. These are paid (Pollen credits), so
     this provider is off unless you list it in AI_VIDEO_PROVIDERS and set POLLINATIONS_KEY.
  5. "image": a slow cinematic zoom over the still image (always works if step 1 did).

Nothing here is required: if every step fails, the scene keeps its motion graphic.
"""
from __future__ import annotations

import logging
import os
import random
import shutil
import subprocess
import urllib.parse
from pathlib import Path

import requests

from . import config

log = logging.getLogger(__name__)

POLLINATIONS = "https://gen.pollinations.ai"
IMAGE_MODEL = os.getenv("AI_IMAGE_MODEL", "tongyi-mai/z-image-turbo")
WAN_SPACE = os.getenv("AI_WAN_SPACE", "zerogpu-aoti/wan2-2-fp8da-aoti-faster")
LTX_SPACE = os.getenv("AI_LTX_SPACE", "Lightricks/ltx-video-distilled")
POLLINATIONS_VIDEO_MODEL = os.getenv("AI_POLLINATIONS_VIDEO_MODEL", "alibaba/wan-2.2-fast")
PROVIDERS = [p.strip() for p in os.getenv("AI_VIDEO_PROVIDERS", "wan,ltx,image").split(",") if p.strip()]
MAX_CLIPS = int(os.getenv("AI_VIDEO_MAX_CLIPS", "2"))
HF_TIMEOUT = float(os.getenv("AI_HF_TIMEOUT", "300"))
# Positive prompts must not contain negations ("no text"): video models often draw what
# they read. Everything to avoid goes in NEGATIVE instead.
STYLE = "photorealistic, cinematic, highly detailed, natural lighting, vertical 9:16 composition"
NEGATIVE = ("text, letters, words, numbers, subtitles, captions, watermark, logo, user interface, "
            "HUD, screen, display, dashboard, people, faces, hands, blurry, distorted, low quality, "
            "deformed, jittery, inconsistent motion")

CREDITS = {
    "wan": "Wan 2.2 (Alibaba, Apache-2.0) image-to-video via a Hugging Face ZeroGPU Space",
    "ltx": "LTX-Video (Lightricks) via a Hugging Face ZeroGPU Space",
    "pollinations": "Pollinations.ai video",
    "image": "AI image (Z-Image via Pollinations.ai)",
}

_cache: dict[str, tuple[Path, str]] = {}   # prompt -> (clip, provider); Hindi reuses English clips
_hf_exhausted = False                      # stop calling HF Spaces after a quota error


def enabled() -> bool:
    return os.getenv("AI_VIDEO", "on").lower() not in ("0", "off", "false", "no")


def _pollinations_headers() -> dict:
    key = os.getenv("POLLINATIONS_KEY", "")
    return {"Authorization": f"Bearer {key}"} if key else {}


def _image(prompt: str, out: Path) -> Path | None:
    if not os.getenv("POLLINATIONS_KEY"):
        return None  # Pollinations images need a (free) key; without one, LTX text-to-video is used
    url = (f"{POLLINATIONS}/image/{urllib.parse.quote(prompt + ', ' + STYLE)}?"
           + urllib.parse.urlencode({"model": IMAGE_MODEL, "width": 576, "height": 1024,
                                     "seed": random.randint(1, 2**31 - 1)}))
    for attempt in range(2):
        try:
            r = requests.get(url, headers=_pollinations_headers(), timeout=180)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("image/"):
                out.write_bytes(r.content)
                return out
            log.warning("Pollinations image HTTP %s: %s", r.status_code, r.text[:200])
        except requests.RequestException as e:
            log.warning("Pollinations image failed: %s", e)
    return None


def _video_path(result) -> Path | None:
    """gradio_client returns a path, a dict with 'video', or a tuple whose first item is either."""
    if isinstance(result, (list, tuple)):
        result = result[0] if result else None
    if isinstance(result, dict):
        result = result.get("video") or result.get("path")
        if isinstance(result, dict):
            result = result.get("path")
    return Path(result) if result else None


def _hf(space: str, api_name: str, **kwargs) -> Path | None:
    global _hf_exhausted
    if _hf_exhausted:
        return None
    from gradio_client import Client
    try:
        client = Client(space, token=os.getenv("HF_TOKEN") or None, verbose=False)
        return _video_path(client.submit(api_name=api_name, **kwargs).result(timeout=HF_TIMEOUT))
    except Exception as e:  # noqa: BLE001
        msg = str(e)
        log.warning("%s failed: %s", space, msg[:300])
        if "quota" in msg.lower() or "exceeded" in msg.lower():
            _hf_exhausted = True
            log.warning("Hugging Face GPU quota used up; no more Space calls this run")
        return None


def _wan(prompt: str, image: Path, seconds: float) -> Path | None:
    from gradio_client import handle_file
    return _hf(WAN_SPACE, "/generate_video", input_image=handle_file(str(image)),
               prompt=f"{prompt}, smooth cinematic camera motion",
               negative_prompt=NEGATIVE, steps=6,
               duration_seconds=max(2.0, min(5.0, seconds)), randomize_seed=True)


def _ltx(prompt: str, seconds: float) -> Path | None:
    return _hf(LTX_SPACE, "/text_to_video", prompt=f"{prompt}, {STYLE}", negative_prompt=NEGATIVE,
               height_ui=1024, width_ui=576, mode="text-to-video",
               duration_ui=max(2.0, min(5.0, seconds)), randomize_seed=True)


def _pollinations_video(prompt: str, out: Path) -> Path | None:
    if not os.getenv("POLLINATIONS_KEY"):
        return None
    url = (f"{POLLINATIONS}/video/{urllib.parse.quote(prompt + ', ' + STYLE)}?"
           + urllib.parse.urlencode({"model": POLLINATIONS_VIDEO_MODEL, "duration": 5, "aspectRatio": "9:16"}))
    try:
        r = requests.get(url, headers=_pollinations_headers(), timeout=600)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("video/"):
            out.write_bytes(r.content)
            return out
        log.warning("Pollinations video HTTP %s: %s", r.status_code, r.text[:200])
    except requests.RequestException as e:
        log.warning("Pollinations video failed: %s", e)
    return None


def _ken_burns(image: Path, out: Path, seconds: float) -> Path:
    frames = max(1, int(seconds * config.FPS))
    vf = (f"scale=2160:-2,zoompan=z='min(1.0+0.0009*on,1.25)':x='iw/2-(iw/zoom/2)':"
          f"y='ih/2-(ih/zoom/2)':d={frames}:s={config.WIDTH}x{config.HEIGHT}:fps={config.FPS},"
          "format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(image), "-vf", vf,
                    "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", str(out)],
                   check=True)
    return out


def _valid(path: Path | None) -> bool:
    if not path or not path.exists() or path.stat().st_size < 10_000:
        return False
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width", "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() != ""


def make_clip(prompt: str, work: Path, idx: int, seconds: float) -> tuple[Path, str] | None:
    """Generate one clip for a scene. Returns (clip path, provider) or None."""
    if prompt in _cache and _cache[prompt][0].exists():
        return _cache[prompt]
    work.mkdir(parents=True, exist_ok=True)
    image = _image(prompt, work / f"ai_{idx}.jpg")
    for provider in PROVIDERS:
        clip = None
        if provider == "wan" and image:
            clip = _wan(prompt, image, seconds)
        elif provider == "ltx":
            clip = _ltx(prompt, seconds)
        elif provider == "pollinations":
            clip = _pollinations_video(prompt, work / f"ai_{idx}_pv.mp4")
        elif provider == "image" and image:
            clip = _ken_burns(image, work / f"ai_{idx}_kb.mp4", seconds)
        if _valid(clip):
            final = work / f"ai_{idx}_{provider}.mp4"
            if clip != final:
                shutil.copyfile(clip, final)
            log.info("AI clip for scene %d from %s", idx + 1, provider)
            _cache[prompt] = (final, provider)
            return _cache[prompt]
    log.info("No AI clip for scene %d; keeping the motion graphic", idx + 1)
    return None
