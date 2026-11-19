"""Optional AI-generated pictures for a scene, tried in order before the free, no-key Wikimedia photo
and the gradient placeholder - `fetch.clip_for` is what actually calls these, in the
order: AI video, then AI stills blended into motion, then a single AI/Wikimedia still with Ken Burns:

    1. Pollinations video (`POLLINATIONS_API_KEY`) - real AI-generated motion, gen.pollinations.ai/video/...
    2. Pollinations image (same key) - gen.pollinations.ai/image/...
    3. Hugging Face Inference (`HF_TOKEN` secret - the same one already used for Indic Parler-TTS, if set)
    4. A small diffusion model run locally in the job (`IMAGE_ENGINE=local`; needs torch+diffusers installed,
       see daily-shorts.yml - heavy and slow on a CPU runner, so it is opt-in, never on by default)

Each step is independent and never raises: a missing key, a network error, a model that refuses to load, all
just mean "try the next source/step". `generate_image`/`generate_video` return None when every configured
source failed (or none is configured), and the caller falls back the next step down, eventually to the real
Wikimedia photo.

Every picture is a *picture of the prompt*, drawn by a model, not a photograph of a real event: label it as what
it is. The channel's own rule against fabricated imagery (shorts/CLAUDE_STOCKREEL_TASK.md) applies here - this
path exists because the owner asked for it, it is opt-in per source (nothing fires without a key or the local
flag), and it is still never used for a claim that something is real footage of a real thing.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

log = logging.getLogger(__name__)
UA = "faceless-explainers-stockreel/1.0"
_LOCAL_PIPE = None   # the local diffusion pipeline, loaded once and reused across scenes/languages


def _get_bytes(url: str, headers: dict, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={**headers, "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def pollinations_video(prompt: str, w: int, h: int, duration: float) -> bytes | None:
    """A short AI-generated video clip (real motion, not a pan/zoom) from Pollinations - same key as the image
    path. Video generation is slower and the API shape is less settled than the image endpoint, so this is
    tried with a generous timeout and a short poll loop for an async job; any failure (no key, timeout, a
    provider that needs a different flow) just means the caller tries the next, cheaper option."""
    key = os.environ.get("POLLINATIONS_API_KEY", "")
    if not key:
        return None
    dur = max(2, min(10, round(duration)))   # clamp to what the available video models commonly support
    aspect = "9:16" if h > w else "16:9"
    url = "https://gen.pollinations.ai/video/" + urllib.parse.quote(prompt) + "?" + urllib.parse.urlencode(
        {"duration": dur, "aspectRatio": aspect})
    try:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=180) as r:
            content_type, body = r.headers.get("Content-Type", ""), r.read()
        if content_type.startswith("video/"):
            return body
        if not content_type.startswith("application/json"):
            return None
        # an async job was queued instead of a direct video: poll for it to finish, a few times, then give up
        job = json.loads(body)
        job_id = job.get("id") or job.get("job") or job.get("job_id")
        if not job_id:
            log.warning("Pollinations video: unrecognized response for %r: %s", prompt, body[:200])
            return None
        import time
        for _ in range(6):
            time.sleep(10)
            poll = json.loads(_get_bytes(f"https://gen.pollinations.ai/v1/jobs/{job_id}", {"Authorization": f"Bearer {key}"}, 30))
            status = (poll.get("status") or "").lower()
            if status in ("completed", "succeeded", "done"):
                result_url = poll.get("result_url") or poll.get("url") or poll.get("output")
                if not result_url:
                    return None
                return _get_bytes(result_url, {"Authorization": f"Bearer {key}"}, 60)
            if status in ("failed", "error"):
                log.warning("Pollinations video job failed for %r: %s", prompt, poll)
                return None
        log.warning("Pollinations video job for %r did not finish in time", prompt)
        return None
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError, json.JSONDecodeError) as e:
        log.warning("Pollinations video failed for %r: %s", prompt, e)
        return None


def pollinations_image(prompt: str, w: int, h: int) -> bytes | None:
    key = os.environ.get("POLLINATIONS_API_KEY", "")
    if not key:
        return None
    url = "https://gen.pollinations.ai/image/" + urllib.parse.quote(prompt) + "?" + urllib.parse.urlencode(
        {"width": w, "height": h, "nologo": "true"})
    try:
        return _get_bytes(url, {"Authorization": f"Bearer {key}"})
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        log.warning("Pollinations image failed for %r: %s", prompt, e)
        return None


# Which model a provider serves through HF's `hf-inference` route shifts over time (a model can be dropped from
# one provider and only reachable through another); try a short list rather than pin to one that may 404/410.
HF_MODELS = ["black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-xl-base-1.0",
             "stabilityai/stable-diffusion-3-medium-diffusers", "runwayml/stable-diffusion-v1-5"]


def huggingface_image(prompt: str, w: int, h: int, models: list[str] = HF_MODELS) -> bytes | None:
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        return None
    payload = json.dumps({"inputs": prompt, "parameters": {"width": w, "height": h}}).encode("utf-8")
    for model in models:
        url = f"https://router.huggingface.co/hf-inference/models/{model}"
        try:
            req = urllib.request.Request(url, data=payload, headers={
                "Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                body = r.read()
            if r.headers.get("Content-Type", "").startswith("application/json"):
                # the model is still loading: HF returns JSON with an "estimated_time", not an image, yet
                log.warning("Hugging Face image (%s) not ready for %r: %s", model, prompt, body[:200])
                continue
            return body
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            log.warning("Hugging Face image (%s) failed for %r: %s", model, prompt, e)
            continue
    return None


def local_image(prompt: str, w: int, h: int, model: str = "stabilityai/sd-turbo") -> bytes | None:
    """A small single-step diffusion model, loaded once and kept warm for the rest of the run. Requires
    torch+diffusers (installed only when IMAGE_ENGINE=local, see daily-shorts.yml); returns None if they are
    not installed, or on any generation error."""
    global _LOCAL_PIPE
    try:
        if _LOCAL_PIPE is None:
            import torch
            from diffusers import AutoPipelineForText2Image
            log.info("Loading local image model %s (first scene only, this takes a while)...", model)
            _LOCAL_PIPE = AutoPipelineForText2Image.from_pretrained(model, torch_dtype=torch.float32)
            _LOCAL_PIPE.to("cpu")
        # sd-turbo: 1 inference step, no guidance scale - that is what makes it fast enough for a CPU runner
        side = 512   # the model's trained resolution; the caller crops/scales to the real frame afterward
        img = _LOCAL_PIPE(prompt=prompt, num_inference_steps=1, guidance_scale=0.0, width=side, height=side).images[0]
        from io import BytesIO
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:  # noqa: BLE001 - not installed, OOM, a bad prompt: always fall through
        log.warning("Local image generation failed for %r: %s", prompt, e)
        return None


SOURCES = [("pollinations", pollinations_image), ("huggingface", huggingface_image)]
NO_TEXT = "photographic, no text, no words, no letters, no caption, no watermark, no logo"


def any_source_configured() -> bool:
    """True if at least one AI picture source is set up - the caller uses this to decide whether two AI stills
    are worth generating for a motion blend (never worth trying against two real Wikimedia photos: they would
    be two different real things, not two takes of the same scene)."""
    return bool(os.environ.get("POLLINATIONS_API_KEY") or os.environ.get("HF_TOKEN") or os.environ.get("IMAGE_ENGINE") == "local")


def generate_video(prompt: str, out: Path, w: int, h: int, duration: float) -> dict | None:
    """A short AI-generated video clip for `prompt`, if Pollinations is configured. None otherwise (including
    on any failure), so the caller falls back to a still image."""
    data = pollinations_video(f"{prompt}, {NO_TEXT}", w, h, duration)
    if data and len(data) > 20_000:
        out.write_bytes(data)
        log.info("AI video (pollinations) for %r", prompt)
        return {"path": out, "credit": "AI-generated video (pollinations), not real footage", "source": "", "ai": True}
    return None


def generate_image(prompt: str, out: Path, w: int, h: int) -> dict | None:
    """Try every configured AI source in order; the first one that returns image bytes wins. None if none are
    configured/available, so the caller falls back to a real Wikimedia photo."""
    # Diffusion models try to literally render words they are given, which is a problem when the "prompt" is a
    # headline or a caption-shaped phrase (it comes back with garbled text baked into the picture): always ask
    # for a clean photo instead. The caller's own headline/captions are drawn separately, on top.
    prompt = f"{prompt}, {NO_TEXT}"
    for name, fn in SOURCES:
        data = fn(prompt, w, h)
        if data and len(data) > 5_000:
            out.write_bytes(data)
            log.info("AI image (%s) for %r", name, prompt)
            return {"path": out, "credit": f"AI-generated ({name}), not a photograph", "source": "", "ai": True}
    if os.environ.get("IMAGE_ENGINE") == "local":
        data = local_image(prompt, w, h)
        if data and len(data) > 5_000:
            out.write_bytes(data)
            log.info("AI image (local model) for %r", prompt)
            return {"path": out, "credit": "AI-generated (local model), not a photograph", "source": "", "ai": True}
    return None
