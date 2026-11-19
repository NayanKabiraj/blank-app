"""Reusable cinematic visual atmosphere: gradient backgrounds, a glow/bloom helper, a particle field and a
subtle parallax/camera drift - the pieces every scene in `graphics.py` is built on top of, so the identity
(deep navy/black, electric blue/cyan, purple/gold accents) stays consistent without each scene re-inventing it.
Built on Pillow + NumPy only (no GPU, no extra heavy dependencies), and written so a background/particle field
is computed ONCE per scene and reused across its frames - the per-frame cost is just compositing, which is
what keeps a 1080x1920x30fps render affordable on a GitHub-hosted CPU runner.
"""
from __future__ import annotations

import colorsys
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Brand palette (hex). "accent" is picked per-scene from here unless the plan's scene.graphic.prop implies one.
PALETTE = {
    "navy": "#060912",
    "black": "#010103",
    "blue": "#2EC5FF",
    "cyan": "#5BFBEA",
    "purple": "#9B6BFF",
    "gold": "#F4C95D",
    "white": "#F5F7FA",
}
ACCENTS = [PALETTE["blue"], PALETTE["cyan"], PALETTE["purple"], PALETTE["gold"]]


def _hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def accent_for(seed: int) -> str:
    return ACCENTS[seed % len(ACCENTS)]


def gradient_background(w: int, h: int, top: str = PALETTE["navy"], bottom: str = PALETTE["black"],
                          vignette: float = 0.55) -> Image.Image:
    """A smooth vertical gradient plus a soft radial vignette - the base every scene composites onto."""
    t, b = np.array(_hex_rgb(top), dtype=np.float32), np.array(_hex_rgb(bottom), dtype=np.float32)
    ramp = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    rows = (t[None, :] * (1 - ramp) + b[None, :] * ramp)
    arr = np.repeat(rows[:, None, :], w, axis=1)
    if vignette:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        cy, cx = h / 2, w / 2
        d = np.sqrt(((xx - cx) / (w / 2)) ** 2 + ((yy - cy) / (h / 2)) ** 2)
        shade = np.clip(1 - vignette * np.clip(d - 0.35, 0, None), 0, 1)[:, :, None]
        arr *= shade
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def glow(img: Image.Image, radius: int = 24, boost: float = 1.0) -> Image.Image:
    """A soft bloom: blur a copy and add it back, brighter - how every glowing line/node gets its halo."""
    base = img.convert("RGBA")
    blurred = base.filter(ImageFilter.GaussianBlur(radius))
    if boost != 1.0:
        arr = np.asarray(blurred, dtype=np.float32)
        arr[..., :3] = np.clip(arr[..., :3] * boost, 0, 255)
        blurred = Image.fromarray(arr.astype(np.uint8), "RGBA")
    return Image.alpha_composite(blurred, base)


class ParticleField:
    """A fixed set of soft drifting dots (depth cue, never the focal point). Positions are generated once
    (seeded, so every scene's field looks intentional rather than random-each-frame) and advanced with cheap
    vectorized NumPy per frame; only the compositing touches Pillow."""

    def __init__(self, w: int, h: int, count: int = 46, seed: int = 0, color: str = PALETTE["cyan"]):
        rng = np.random.default_rng(seed)
        self.w, self.h = w, h
        self.x = rng.uniform(0, w, count).astype(np.float32)
        self.y = rng.uniform(0, h, count).astype(np.float32)
        self.r = rng.uniform(1.2, 3.6, count).astype(np.float32)
        self.speed = rng.uniform(6, 22, count).astype(np.float32)   # px/sec, drifting upward
        self.phase = rng.uniform(0, 2 * math.pi, count).astype(np.float32)
        self.alpha = rng.uniform(0.25, 0.75, count).astype(np.float32)
        self.color = _hex_rgb(color)

    def frame(self, t: float, opacity: float = 1.0) -> Image.Image:
        layer = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        y = (self.y - self.speed * t) % self.h
        x = self.x + np.sin(self.phase + t * 0.6) * 10
        for xi, yi, ri, ai in zip(x, y, self.r, self.alpha):
            a = int(255 * ai * opacity)
            if a <= 0:
                continue
            draw.ellipse([xi - ri, yi - ri, xi + ri, yi + ri], fill=(*self.color, a))
        return layer


def camera_drift(t: float, duration: float, w: int, h: int, zoom_from: float = 1.0, zoom_to: float = 1.06,
                  pan_px: float = 18.0) -> tuple[float, float, float]:
    """A slow, barely-there zoom + pan (the "camera-like movement" the spec asks for) - returns
    (scale, dx, dy) for `apply_camera` below. Never jarring: a documentary pan, not a zoom-burst."""
    p = min(1.0, max(0.0, t / max(0.01, duration)))
    ease = p * p * (3 - 2 * p)  # smoothstep
    scale = zoom_from + (zoom_to - zoom_from) * ease
    dx = math.sin(ease * math.pi) * pan_px
    dy = -ease * pan_px * 0.5
    return scale, dx, dy


def apply_camera(img: Image.Image, scale: float, dx: float, dy: float) -> Image.Image:
    w, h = img.size
    if scale != 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    bw, bh = img.size
    x0 = max(0, min(bw - w, int((bw - w) / 2 + dx)))
    y0 = max(0, min(bh - h, int((bh - h) / 2 + dy)))
    return img.crop((x0, y0, x0 + w, y0 + h))


def ease_out_cubic(p: float) -> float:
    p = min(1.0, max(0.0, p))
    return 1 - (1 - p) ** 3


def ease_in_out(p: float) -> float:
    p = min(1.0, max(0.0, p))
    return p * p * (3 - 2 * p)
