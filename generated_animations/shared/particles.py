"""Particle / signal effects, driven by the scene timeline so they keep moving whatever else is playing."""
from __future__ import annotations

import numpy as np
from manim import Circle, Dot, Line, VGroup, always_redraw


def pulse_rings(source, timeline, color: str, n: int = 3, period: float = 1.6, max_radius: float = 1.6,
                width: float = 3.0):
    """Expanding, fading rings emitted from `source` (point-function or mobject)."""
    def make():
        centre = source() if callable(source) else source.get_center()
        g = VGroup()
        for i in range(n):
            f = ((timeline.t / period) + i / n) % 1.0
            g.add(Circle(radius=0.05 + max_radius * f, color=color, stroke_width=width * (1 - f) + 0.3,
                         stroke_opacity=(1 - f) ** 1.5).move_to(centre))
        return g
    m = always_redraw(make)
    m._dynamic = True
    return m


def signal_packets(start_fn, end_fn, timeline, color: str, n: int = 4, period: float = 1.4, size: float = 0.07):
    """Dots travelling from start to end along a straight signal path (loops forever)."""
    def make():
        a, b = np.asarray(start_fn(), float), np.asarray(end_fn(), float)
        g = VGroup()
        for i in range(n):
            f = ((timeline.t / period) + i / n) % 1.0
            g.add(Dot(a + (b - a) * f, radius=size, color=color, fill_opacity=min(1, 3 * f, 3 * (1 - f) + 0.2)))
        return g
    m = always_redraw(make)
    m._dynamic = True
    return m


def signal_path(start_fn, end_fn, color: str, width: float = 2.0, opacity: float = 0.5):
    m = always_redraw(lambda: Line(start_fn(), end_fn(), color=color, stroke_width=width, stroke_opacity=opacity))
    m._dynamic = True
    return m


class Sparkle(VGroup):
    """A burst of dots that fly outward and fade - call `.restart()` then add to the scene."""

    def __init__(self, center, timeline, color: str = "#FFD166", n: int = 18, speed: float = 1.8,
                 life: float = 0.9, seed: int = 3):
        super().__init__()
        rng = np.random.default_rng(seed)
        self.center = np.asarray(center, float)
        self.timeline, self.life, self.speed = timeline, life, speed
        self.angles = rng.uniform(0, 2 * np.pi, n)
        self.speeds = rng.uniform(0.5, 1.0, n) * speed
        self.t0 = -1e9          # hidden until restart() is called
        self.dots = [Dot(center, radius=0.05, color=color) for _ in range(n)]
        self.add(*self.dots)
        self.add_updater(lambda m: m._tick())

    def restart(self):
        self.t0 = self.timeline.t

    def _tick(self):
        age = self.timeline.t - self.t0
        f = min(1.0, max(0.0, age / self.life))
        for d, a, s in zip(self.dots, self.angles, self.speeds):
            d.move_to(self.center + np.array([np.cos(a), np.sin(a), 0]) * s * f)
            d.set_opacity(1 - f)
