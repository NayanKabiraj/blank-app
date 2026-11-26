"""Shared pack kit for vox-look animation packs (vertical Shorts and landscape documentaries): `from generated_animations.shared.packkit import *`.

`Beat(ctx, i, n)` = narration scene i of an n-scene shot (`b.t0` start, `b.t1` end, `b.card/put/text/tape/live/mover` helpers that fade with the beat).
WRAP EACH BEAT IN ITS OWN FUNCTION (`def beat0(b): ...; beat0(B[0])`): closures over a loop/reused variable `b` would all see the last beat.
Drawing helpers: figure(), phone(), plane(), recorder(), flame(), sea(), sub(), ring_pings(); vox.* from shared/vox.py; vox.L(ctx, en, hi) for bilingual text."""
from __future__ import annotations

import math

import numpy as np
from manim import Circle, Ellipse, Line, Polygon, Rectangle, RoundedRectangle, VGroup, always_redraw, interpolate_color

from generated_animations.shared import vox
from generated_animations.shared.vox import BLUE, CREAM, GREEN, INK, ORANGE, PINK, RED, YEL
from generated_animations.timed import level, show, window

__all__ = ["v", "ease", "Beat", "plane", "recorder", "flame", "sea", "sub", "ring_pings", "figure", "phone", "np", "math", "vox", "level", "show", "window",
           "BLUE", "CREAM", "GREEN", "INK", "ORANGE", "PINK", "RED", "YEL", "Circle", "Ellipse", "Line", "Polygon", "Rectangle", "RoundedRectangle", "VGroup", "always_redraw"]


def v(x, y):
    return np.array([float(x), float(y), 0.0])


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


class Beat:
    """One narration scene inside a shot: its start/end times and short helpers that fade things out when the beat ends."""

    def __init__(self, ctx, i, n):
        self.ctx, self.i = ctx, i
        self.C, self.W, self.H = ctx.stage
        self.t0 = ctx.t_of(i)
        self.t1 = ctx.t_of(i + 1) - 0.25 if i + 1 < n else None

    def at(self, k=0):
        return self.ctx.tt(self.i, k)

    def card(self, w=None, h=None, seed=1, rot=0.0, dx=0.0, dy=0.0, t=None):
        w, h = w or self.W - 0.3, h or self.H - 0.3
        return show(self.ctx, vox.torn_card(w, h, seed=seed, rot=rot).move_to(self.C + v(dx, dy)), self.t0 + 0.05 if t is None else t, t_out=self.t1, pop=0.12, z=2)

    def backdrop(self, top="#0E1A3A", bottom="#3B2A66", stars=True, seed=1, strips=16):
        """FULL-SCREEN art (shots.json {"stage": "full"}): a full-bleed gradient behind everything (caption and presenter sit on top) plus twinkling stars. Use INSTEAD of card()."""
        from manim import ManimColor
        g = VGroup()
        h = 16.6 / strips
        for k in range(strips):
            g.add(Rectangle(width=9.4, height=h + 0.03, stroke_width=0, fill_color=interpolate_color(ManimColor(top), ManimColor(bottom), k / (strips - 1)), fill_opacity=1).move_to(v(0, 8.3 - h * (k + 0.5))))
        show(self.ctx, g, self.t0 + 0.02, t_out=self.t1, pop=0, z=1)
        if stars:
            rng = np.random.default_rng(seed)
            pts = [(rng.uniform(-4.4, 4.4), rng.uniform(-7.5, 7.5), rng.uniform(0, 6.28), rng.uniform(0.03, 0.07)) for _ in range(34)]

            def mk(a):
                tm = self.ctx.elapsed()
                return VGroup(*[Circle(radius=r * (0.7 + 0.5 * math.sin(tm * 2 + ph)), stroke_width=0, fill_color="#FFFFFF", fill_opacity=a * 0.85).move_to(v(x, y)) for x, y, ph, r in pts])
            self.live(mk, self.t0 + 0.05, z=2)
        return g

    def put(self, mob, t=None, z=5, pop=0.1, dur=0.28):
        return show(self.ctx, mob, self.t0 + 0.3 if t is None else t, dur=dur, t_out=self.t1, pop=pop, z=z)

    def text(self, s, size, pos, col=INK, width=4.0, t=None, z=6, weight="BOLD"):
        return self.put(self.ctx.text(s, size, col, width, weight).move_to(self.C + pos), t, z)

    def tape(self, s, pos, col=BLUE, w=3.6, size=28, rot=-2.0, t=None):
        return self.put(vox.tape(self.ctx, s, self.C + pos, col, w, size, rot), t, z=8, pop=0.25)

    def mover(self, mob, pos_fn, t_in=None, z=6):
        """A mobject that follows pos_fn() (a point) and fades in/out with this beat."""
        show(self.ctx, mob, self.t0 + 0.2 if t_in is None else t_in, dur=0.3, t_out=self.t1, pop=0, z=z)
        mob.add_updater(lambda m: m.shift(pos_fn() - m.get_center()))
        return mob

    def live(self, make, t_in=None, z=5):
        """An always_redraw mobject whose alpha follows this beat."""
        m = always_redraw(lambda: make(window(self.ctx, self.t0 + 0.1 if t_in is None else t_in, self.t1)()))
        m._dynamic = True
        self.ctx.add(m, z=z)
        return m

    def lv(self, t, dur=1.0):
        return ease(level(self.ctx, t, dur))


def plane(s=1.0, col=INK):
    body = Ellipse(width=1.5 * s, height=0.34 * s, stroke_width=0, fill_color=CREAM, fill_opacity=1)
    wing = Polygon(v(-0.1 * s, 0.0), v(-0.55 * s, 0.62 * s), v(-0.35 * s, 0.62 * s), v(0.25 * s, 0.05 * s), stroke_width=0, fill_color=BLUE, fill_opacity=1)
    wing2 = Polygon(v(-0.1 * s, 0.0), v(-0.55 * s, -0.62 * s), v(-0.35 * s, -0.62 * s), v(0.25 * s, -0.05 * s), stroke_width=0, fill_color="#3F78C9", fill_opacity=1)
    tail = Polygon(v(-0.65 * s, 0.1 * s), v(-0.85 * s, 0.4 * s), v(-0.7 * s, 0.4 * s), v(-0.45 * s, 0.1 * s), stroke_width=0, fill_color=RED, fill_opacity=1)
    g = VGroup(wing2, body, tail, wing)
    return vox.cutout(g, 6.0)


def recorder(s=1.0, col=ORANGE):
    """The orange recorder: rounded box, two white stripes, a little round beacon on the side."""
    body = RoundedRectangle(corner_radius=0.12 * s, width=1.5 * s, height=0.95 * s, stroke_color=INK, stroke_width=4, fill_color=col, fill_opacity=1)
    st = [Rectangle(width=1.5 * s, height=0.1 * s, stroke_width=0, fill_color="#FFFFFF", fill_opacity=0.9).shift(v(0, 0.2 * s)), Rectangle(width=1.5 * s, height=0.1 * s, stroke_width=0, fill_color="#FFFFFF", fill_opacity=0.9).shift(v(0, -0.2 * s))]
    ulb = Circle(radius=0.17 * s, stroke_color=INK, stroke_width=3, fill_color=YEL, fill_opacity=1).shift(v(0.9 * s, 0.0))
    return vox.cutout(VGroup(body, *st, ulb), 6.0)


def flame(s=1.0, ph=0.0, tm=0.0):
    k = 1.0 + 0.12 * math.sin(tm * 9 + ph)
    a = Polygon(v(-0.3 * s, 0), v(-0.22 * s, 0.5 * s * k), v(-0.05 * s, 0.35 * s), v(0.05 * s, 0.95 * s * k), v(0.2 * s, 0.4 * s), v(0.3 * s, 0.0), stroke_width=0, fill_color=ORANGE, fill_opacity=0.95)
    b = Polygon(v(-0.15 * s, 0), v(-0.08 * s, 0.35 * s * k), v(0.02 * s, 0.6 * s * k), v(0.12 * s, 0.3 * s), v(0.16 * s, 0.0), stroke_width=0, fill_color=YEL, fill_opacity=0.95)
    return VGroup(a, b)


def sea(C, w, y0, h, tm, alpha=1.0, col="#3F8FD8"):
    """A band of sea with moving wave crests; y0 is the surface."""
    body = Rectangle(width=w, height=h, stroke_width=0, fill_color=col, fill_opacity=0.9 * alpha).move_to(C + v(0, y0 - h / 2))
    crest = Line(C + v(-w / 2, y0), C + v(w / 2, y0), color="#FFFFFF", stroke_width=0)
    pts = [C + v(-w / 2 + w * k / 30, y0 + 0.09 * math.sin(k * 0.9 + tm * 2.2)) for k in range(31)]
    from manim import VMobject
    wave = VMobject(stroke_color="#FFFFFF", stroke_width=4, stroke_opacity=alpha).set_points_as_corners(pts)
    return VGroup(body, wave)


def sub(s=1.0):
    hull = Ellipse(width=1.3 * s, height=0.55 * s, stroke_color=INK, stroke_width=4, fill_color=YEL, fill_opacity=1)
    tw = Rectangle(width=0.3 * s, height=0.25 * s, stroke_color=INK, stroke_width=3, fill_color=YEL, fill_opacity=1).shift(v(-0.1 * s, 0.38 * s))
    win = Circle(radius=0.1 * s, stroke_color=INK, stroke_width=3, fill_color="#9FD8FF", fill_opacity=1).shift(v(0.25 * s, 0.03 * s))
    return VGroup(tw, hull, win)


def ring_pings(ctx, center, t_in, t_out, period=1.2, rmax=1.6, col=YEL, z=4):
    """Expanding sonar rings from a point (three at a time)."""
    def make():
        a = window(ctx, t_in, t_out)()
        g = VGroup()
        for k in range(3):
            f = ((ctx.elapsed() - t_in) / period + k / 3.0) % 1.0
            g.add(Circle(radius=0.05 + rmax * f, stroke_color=col, stroke_width=5, stroke_opacity=a * (1 - f), fill_opacity=0).move_to(center))
        return g
    m = always_redraw(make)
    m._dynamic = True
    ctx.add(m, z=z)
    return m


def figure(s=1.0, coat=BLUE, head="#F2C9A0"):
    """A paper cut-out person: round head, rounded body in a coloured coat."""
    body = RoundedRectangle(corner_radius=0.25 * s, width=0.8 * s, height=1.1 * s, stroke_color=INK, stroke_width=3, fill_color=coat, fill_opacity=1).shift(v(0, -0.65 * s))
    hd = Circle(radius=0.3 * s, stroke_color=INK, stroke_width=3, fill_color=head, fill_opacity=1).shift(v(0, 0.1 * s))
    return vox.cutout(VGroup(body, hd), 5.0)


def phone(s=1.0, screen=YEL, on=True):
    body = RoundedRectangle(corner_radius=0.18 * s, width=0.9 * s, height=1.7 * s, stroke_color=INK, stroke_width=4, fill_color="#2B2B35", fill_opacity=1)
    scr = RoundedRectangle(corner_radius=0.1 * s, width=0.74 * s, height=1.4 * s, stroke_width=0, fill_color=screen if on else "#15151C", fill_opacity=1).shift(v(0, -0.03 * s))
    return vox.cutout(VGroup(body, scr), 5.0)


def plane(s=1.0, col=INK):
    body = Ellipse(width=1.5 * s, height=0.34 * s, stroke_width=0, fill_color=CREAM, fill_opacity=1)
    wing = Polygon(v(-0.1 * s, 0.0), v(-0.55 * s, 0.62 * s), v(-0.35 * s, 0.62 * s), v(0.25 * s, 0.05 * s), stroke_width=0, fill_color=BLUE, fill_opacity=1)
    wing2 = Polygon(v(-0.1 * s, 0.0), v(-0.55 * s, -0.62 * s), v(-0.35 * s, -0.62 * s), v(0.25 * s, -0.05 * s), stroke_width=0, fill_color="#3F78C9", fill_opacity=1)
    tail = Polygon(v(-0.65 * s, 0.1 * s), v(-0.85 * s, 0.4 * s), v(-0.7 * s, 0.4 * s), v(-0.45 * s, 0.1 * s), stroke_width=0, fill_color=RED, fill_opacity=1)
    g = VGroup(wing2, body, tail, wing)
    return vox.cutout(g, 6.0)


def recorder(s=1.0, col=ORANGE):
    """The orange recorder: rounded box, two white stripes, a little round beacon on the side."""
    body = RoundedRectangle(corner_radius=0.12 * s, width=1.5 * s, height=0.95 * s, stroke_color=INK, stroke_width=4, fill_color=col, fill_opacity=1)
    st = [Rectangle(width=1.5 * s, height=0.1 * s, stroke_width=0, fill_color="#FFFFFF", fill_opacity=0.9).shift(v(0, 0.2 * s)), Rectangle(width=1.5 * s, height=0.1 * s, stroke_width=0, fill_color="#FFFFFF", fill_opacity=0.9).shift(v(0, -0.2 * s))]
    ulb = Circle(radius=0.17 * s, stroke_color=INK, stroke_width=3, fill_color=YEL, fill_opacity=1).shift(v(0.9 * s, 0.0))
    return vox.cutout(VGroup(body, *st, ulb), 6.0)


def flame(s=1.0, ph=0.0, tm=0.0):
    k = 1.0 + 0.12 * math.sin(tm * 9 + ph)
    a = Polygon(v(-0.3 * s, 0), v(-0.22 * s, 0.5 * s * k), v(-0.05 * s, 0.35 * s), v(0.05 * s, 0.95 * s * k), v(0.2 * s, 0.4 * s), v(0.3 * s, 0.0), stroke_width=0, fill_color=ORANGE, fill_opacity=0.95)
    b = Polygon(v(-0.15 * s, 0), v(-0.08 * s, 0.35 * s * k), v(0.02 * s, 0.6 * s * k), v(0.12 * s, 0.3 * s), v(0.16 * s, 0.0), stroke_width=0, fill_color=YEL, fill_opacity=0.95)
    return VGroup(a, b)


def sea(C, w, y0, h, tm, alpha=1.0, col="#3F8FD8"):
    """A band of sea with moving wave crests; y0 is the surface."""
    body = Rectangle(width=w, height=h, stroke_width=0, fill_color=col, fill_opacity=0.9 * alpha).move_to(C + v(0, y0 - h / 2))
    crest = Line(C + v(-w / 2, y0), C + v(w / 2, y0), color="#FFFFFF", stroke_width=0)
    pts = [C + v(-w / 2 + w * k / 30, y0 + 0.09 * math.sin(k * 0.9 + tm * 2.2)) for k in range(31)]
    from manim import VMobject
    wave = VMobject(stroke_color="#FFFFFF", stroke_width=4, stroke_opacity=alpha).set_points_as_corners(pts)
    return VGroup(body, wave)


def sub(s=1.0):
    hull = Ellipse(width=1.3 * s, height=0.55 * s, stroke_color=INK, stroke_width=4, fill_color=YEL, fill_opacity=1)
    tw = Rectangle(width=0.3 * s, height=0.25 * s, stroke_color=INK, stroke_width=3, fill_color=YEL, fill_opacity=1).shift(v(-0.1 * s, 0.38 * s))
    win = Circle(radius=0.1 * s, stroke_color=INK, stroke_width=3, fill_color="#9FD8FF", fill_opacity=1).shift(v(0.25 * s, 0.03 * s))
    return VGroup(tw, hull, win)


def ring_pings(ctx, center, t_in, t_out, period=1.2, rmax=1.6, col=YEL, z=4):
    """Expanding sonar rings from a point (three at a time)."""
    def make():
        a = window(ctx, t_in, t_out)()
        g = VGroup()
        for k in range(3):
            f = ((ctx.elapsed() - t_in) / period + k / 3.0) % 1.0
            g.add(Circle(radius=0.05 + rmax * f, stroke_color=col, stroke_width=5, stroke_opacity=a * (1 - f), fill_opacity=0).move_to(center))
        return g
    m = always_redraw(make)
    m._dynamic = True
    ctx.add(m, z=z)
    return m
