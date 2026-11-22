"""Easing and motion paths shared by every scene."""
from __future__ import annotations

import math

import numpy as np
from manim.utils.rate_functions import (ease_in_out_cubic, ease_out_back, ease_out_cubic, smooth,
                                        there_and_back)

__all__ = ["ease_in_out_cubic", "ease_out_back", "ease_out_cubic", "smooth", "there_and_back",
           "bezier_point", "orbit_point", "lerp"]


def lerp(a, b, f):
    return a + (b - a) * f


def bezier_point(p0, p1, p2, f: float):
    """Quadratic Bezier point at fraction f (a curved motion path for objects that should arc, not slide)."""
    p0, p1, p2 = (np.asarray(p, dtype=float) for p in (p0, p1, p2))
    return (1 - f) ** 2 * p0 + 2 * (1 - f) * f * p1 + f ** 2 * p2


def orbit_point(center, radius: float, angle: float, tilt: float = 1.0):
    """Point on an (optionally flattened) circular orbit; `tilt` < 1 squashes it into an ellipse."""
    c = np.asarray(center, dtype=float)
    return c + np.array([radius * math.cos(angle), radius * tilt * math.sin(angle), 0.0])
