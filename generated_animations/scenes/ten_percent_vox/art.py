"""Helpers for this pack (kept inside the pack folder: scheduled runs may commit only new pack folders)."""
from __future__ import annotations

import numpy as np
from manim import Arc, Circle, Line, RoundedRectangle, VGroup

INK = "#221E1C"


def _p(x, y):
    return np.array([float(x), float(y), 0.0])


BRAIN_POS = [(-0.95, 0.25), (-0.45, 0.72), (0.2, 0.82), (0.85, 0.5), (-0.85, -0.35), (-0.2, -0.45), (0.5, -0.4), (1.0, -0.05)]


def brain(c, s: float = 1.0, lit=None, a: float = 1.0) -> VGroup:
    """A cartoon brain made of 8 lobes; `lit` = a list of 8 colours (None = grey/idle). Constant part count."""
    g = VGroup()
    g.add(RoundedRectangle(corner_radius=0.1, width=0.3, height=0.55, stroke_color=INK, stroke_width=4, fill_color="#E7B9A6", fill_opacity=1).move_to(_p(0.15, -0.95)))
    for i, (x, y) in enumerate(BRAIN_POS):
        col = (lit[i] if lit else None) or "#8E8AA6"
        g.add(Circle(radius=0.5, stroke_color=INK, stroke_width=4, fill_color=col, fill_opacity=1).move_to(_p(x, y)))
    for k in range(3):
        g.add(Arc(radius=0.35, start_angle=0.5 + k, angle=1.6, stroke_color=INK, stroke_width=3, stroke_opacity=0.6).move_to(_p(-0.5 + 0.5 * k, 0.2 - 0.15 * k)))
    g.scale(s).move_to(np.asarray(c, float))
    g.set_opacity(a) if a < 0.999 else None
    return g
