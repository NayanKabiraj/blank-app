"""Black-hole visuals for authored shots: a spinning accretion disk with a dark shadow, a gravitationally lensed star
field, and a stretching stick-figure astronaut. All parts have a constant count and are driven by the scene clock."""
from __future__ import annotations

import math

import numpy as np
from manim import Arc, Circle, Dot, Ellipse, Line, VGroup, always_redraw

from .orbital import _a

DISK = ["#FF7B00", "#FF9F1C", "#FFC857"]


def black_hole(C, R: float, timeline, alpha=None, spin: float = 0.9, disk: bool = True):
    C = np.asarray(C, float)

    def build():
        c = np.asarray(C() if callable(C) else C, float)
        g = VGroup(*[Circle(radius=R * (1.9 - 0.25 * k), stroke_width=0, fill_color="#FF9F1C", fill_opacity=0.06 + 0.03 * k).move_to(c) for k in range(3)])
        if disk:
            for k, col in enumerate(DISK):
                g.add(Ellipse(width=R * (4.4 - 0.7 * k), height=R * (0.95 - 0.12 * k), stroke_color=col, stroke_width=5 - k, fill_opacity=0).move_to(c))
            g.add(Arc(radius=R * 1.22, start_angle=0.15, angle=math.pi - 0.3, stroke_color="#FFC857", stroke_width=7, arc_center=c))
            for j in range(6):
                a = spin * timeline.t + j * math.pi / 3
                g.add(Dot(c + np.array([R * 2.0 * math.cos(a), R * 0.42 * math.sin(a), 0.0]), radius=R * 0.07, color="#FFE8A8"))
        g.add(Circle(radius=R, stroke_color="#FFD27F", stroke_width=3, fill_color="#000000", fill_opacity=1).move_to(c))
        return _a(g, alpha)
    m = always_redraw(build)
    m._dynamic = True
    return m


def starfield(C, W: float, H: float, n: int, bh, R: float, warp=lambda: 1.0, seed: int = 4, alpha=None):
    """Stars displaced away from the black hole `bh` (a point or callable) by a lensing-like shift scaled by warp()."""
    C = np.asarray(C, float)
    rng = np.random.default_rng(seed)
    pts = [C + np.array([rng.uniform(-W / 2, W / 2), rng.uniform(-H / 2, H / 2), 0.0]) for _ in range(n)]
    sizes = rng.uniform(0.025, 0.06, n)

    def build():
        b = np.asarray(bh() if callable(bh) else bh, float)
        w = warp()
        g = VGroup()
        for p, s in zip(pts, sizes):
            v = p - b
            d = max(R * 1.05, float(np.linalg.norm(v)))
            shift = 1.0 + w * 1.6 * (R / d) ** 1.4
            q = b + v / max(1e-6, np.linalg.norm(v)) * d * shift if np.linalg.norm(v) > 1e-6 else p
            inside = np.linalg.norm(q - b) < R * 1.02
            g.add(Dot(q, radius=s, color="#F5F7FA", fill_opacity=0.0 if inside else 0.9))
        return _a(g, alpha)
    m = always_redraw(build)
    m._dynamic = True
    return m


def astronaut(pos, scale: float = 1.0, stretch: float = 1.0, angle: float = 0.0, color="#F5F7FA") -> VGroup:
    """Stick-figure astronaut centred at `pos`, head toward +y before rotation by `angle`; `stretch` elongates it along its length
    and thins it sideways (spaghettification)."""
    s = scale
    L = stretch
    T = 1.0 / math.sqrt(max(0.2, stretch))
    pts = lambda x, y: np.array([x * T * s, y * L * s, 0.0])  # noqa: E731
    g = VGroup(Circle(radius=0.17 * s * T, stroke_color=color, stroke_width=4, fill_color="#C9CED8", fill_opacity=1).move_to(pts(0, 0.5)),
               Line(pts(0, 0.3), pts(0, -0.25), color=color, stroke_width=6),
               Line(pts(0, 0.2), pts(-0.3, 0.0), color=color, stroke_width=5), Line(pts(0, 0.2), pts(0.3, 0.0), color=color, stroke_width=5),
               Line(pts(0, -0.25), pts(-0.15, -0.65), color=color, stroke_width=5), Line(pts(0, -0.25), pts(0.15, -0.65), color=color, stroke_width=5))
    g.rotate(angle, about_point=np.zeros(3))
    return g.shift(np.asarray(pos, float))
