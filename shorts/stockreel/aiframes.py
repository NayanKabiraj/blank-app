"""Optional AI-generated images for a scene, tried in order before the free, no-key Wikimedia photo
(`fetch.download_photo`) and the gradient placeholder:

    1. Pollinations (`POLLINATIONS_API_KEY` secret: https://enter.pollinations.ai) - gen.pollinations.ai/image/...
    2. Hugging Face Inference (`HF_TOKEN` secret - the same one already used for Indic Parler-TTS, if set)
    3. A small diffusion model run locally in the job (`IMAGE_ENGINE=local`; needs torch+diffusers installed,
       see daily-shorts.yml - heavy and slow on a CPU runner, so it is opt-in, never on by default)

Each step is independent and never raises: a missing key, a network error, a model that refuses to load, all
just mean "try the next source". `generate_image` returns None when every configured source failed (or none is
configured), and the caller (`fetch.clip_for`) falls back to the real Wikimedia photo.

Every image is a *picture of the prompt*, drawn by a model, not a photograph of a real event: label it as what
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


def huggingface_image(prompt: str, w: int, h: int, model: str = "black-forest-labs/FLUX.1-schnell") -> bytes | None:
    token = os.environ.get("HF_TOKEN", "")
    if not token:
        return None
    url = f"https://router.huggingface.co/hf-inference/models/{model}"
    payload = json.dumps({"inputs": prompt, "parameters": {"width": w, "height": h}}).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=payload, headers={
            "Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=90) as r:
            body = r.read()
        if r.headers.get("Content-Type", "").startswith("application/json"):
            # the model is still loading: HF returns JSON with an "estimated_time", not an image, yet
            log.warning("Hugging Face image not ready for %r: %s", prompt, body[:200])
            return None
        return body
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        log.warning("Hugging Face image failed for %r: %s", prompt, e)
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


def generate_image(prompt: str, out: Path, w: int, h: int) -> dict | None:
    """Try every configured AI source in order; the first one that returns image bytes wins. None if none are
    configured/available, so the caller falls back to a real Wikimedia photo."""
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
