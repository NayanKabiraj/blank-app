"""Lighting: glows, a vignette and a starfield, generated with NumPy (no image assets needed)."""
from __future__ import annotations

import numpy as np
from manim import Circle, ImageMobject, VGroup


def glow(point, color: str, radius: float = 0.6, layers: int = 5, opacity: float = 0.35) -> VGroup:
    """Soft glow built from stacked translucent discs."""
    g = VGroup()
    for i in range(layers):
        f = (i + 1) / layers
        g.add(Circle(radius=radius * (1.8 - f), stroke_width=0, fill_color=color,
                     fill_opacity=opacity * f / layers * 2).move_to(point))
    return g


def _rgba_image(arr: np.ndarray, width: float, height: float) -> ImageMobject:
    img = ImageMobject(arr)
    img.set_resampling_algorithm(2)  # linear
    img.stretch_to_fit_width(width)
    img.stretch_to_fit_height(height)
    return img


def vignette(width: float, height: float, strength: float = 0.55, res: int = 160) -> ImageMobject:
    """Dark edges, transparent centre. Drawn once, pinned to the HUD."""
    ys, xs = np.mgrid[-1:1:complex(res), -1:1:complex(res)]
    d = np.clip(np.sqrt(xs ** 2 + ys ** 2) / 1.35, 0, 1)
    arr = np.zeros((res, res, 4), dtype=np.uint8)
    arr[..., 3] = (255 * strength * d ** 2.4).astype(np.uint8)
    return _rgba_image(arr, width, height)


def starfield(width: float, height: float, n: int = 260, seed: int = 7, res=(540, 960),
              top: tuple = (7, 10, 28), bottom: tuple = (18, 12, 46)) -> ImageMobject:
    """Gradient night sky with scattered stars."""
    rng = np.random.default_rng(seed)
    h, w = res[1], res[0]
    t = np.linspace(0, 1, h)[:, None, None]
    sky = (np.array(top) * (1 - t) + np.array(bottom) * t) * np.ones((h, w, 3))
    for _ in range(n):
        x, y = int(rng.integers(1, w - 1)), int(rng.integers(1, h - 1))
        b = rng.uniform(90, 255)
        sky[y, x] = np.clip(sky[y, x] + b, 0, 255)
        if rng.random() < 0.25:
            sky[y, x - 1:x + 2] = np.clip(sky[y, x - 1:x + 2] + b / 3, 0, 255)
            sky[y - 1:y + 2, x] = np.clip(sky[y - 1:y + 2, x] + b / 3, 0, 255)
    return _rgba_image(np.dstack([sky, np.full((h, w), 255)]).astype(np.uint8), width, height)
