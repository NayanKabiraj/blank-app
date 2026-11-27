"""Helpers for this pack (kept inside the pack folder: scheduled runs may commit only new pack folders)."""
from __future__ import annotations

import numpy as np
from manim import Arc, Circle, Line, RoundedRectangle, VGroup, Rectangle

INK = "#221E1C"


def _p(x, y):
    return np.array([float(x), float(y), 0.0])


def satellite(c, s: float = 1.0, a: float = 1.0) -> VGroup:
    """A cartoon satellite: body, two solar panels with grid lines, a gold dish. Constant part count."""
    from manim import Rectangle
    g = VGroup()
    for sx in (-1, 1):
        g.add(Rectangle(width=1.25, height=0.5, stroke_color=INK, stroke_width=4, fill_color="#3A66C4", fill_opacity=1).move_to(_p(sx * 1.05, 0)))
        g.add(Line(_p(sx * 1.05, -0.25), _p(sx * 1.05, 0.25), color="#9DB7F0", stroke_width=3), Line(_p(sx * 0.75, -0.25), _p(sx * 0.75, 0.25), color="#9DB7F0", stroke_width=3), Line(_p(sx * 1.35, -0.25), _p(sx * 1.35, 0.25), color="#9DB7F0", stroke_width=3))
    g.add(RoundedRectangle(corner_radius=0.12, width=0.8, height=0.6, stroke_color=INK, stroke_width=4, fill_color="#D9DDE6", fill_opacity=1).move_to(_p(0, 0)))
    g.add(Circle(radius=0.17, stroke_color=INK, stroke_width=3, fill_color="#F2C14E", fill_opacity=1).move_to(_p(0, -0.42)))
    g.scale(s).move_to(np.asarray(c, float))
    g.set_opacity(a) if a < 0.999 else None
    return g
