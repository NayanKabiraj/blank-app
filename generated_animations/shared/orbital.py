"""Orbital / tide visuals for authored shots: a top-down Earth with an ocean that bulges toward the Moon, rotating
continents and a beach marker, the Moon, the Sun, a live tide graph and a rising-water harbour. All are drawn on the
scene clock and keep a constant number of parts (see timed.py), so they can run for minutes."""
from __future__ import annotations

import math

import numpy as np
from manim import (Circle, Dot, Ellipse, Line, Polygon, Rectangle, RoundedRectangle, VGroup, VMobject, always_redraw)

OCEAN, LAND, ATMO = "#1F6FB5", "#3FA066", "#7FD6FF"
_BLOBS = [(0.4, 0.45, 0.30, 0.2), (2.0, 0.5, 0.32, 0.22), (3.4, 0.35, 0.26, 0.18), (4.6, 0.55, 0.3, 0.2), (5.6, 0.3, 0.22, 0.16)]


def _a(m, alpha):
    """Apply a visibility factor to every part of a freshly built group."""
    if alpha is not None:
        k = alpha()
        for s in m.get_family():
            if isinstance(s, VMobject):
                s.set_fill(opacity=s.get_fill_opacity() * k, family=False)
                s.set_stroke(opacity=s.get_stroke_opacity() * k, family=False)
    return m


def ocean_earth(C, R, *, bulge=lambda: 0.0, amp=lambda: 0.35, offset=lambda: 0.0, rot=lambda: 0.0, marker=None,
                core=lambda: (0.0, 0.0), alpha=None, labels=None):
    """Top-down Earth: an ocean ellipse stretched toward `bulge()` (radians) by `amp()` (and optionally shifted
    toward it by `offset()` x R), a land core that turns by `rot()`, and an optional beach marker at core angle `marker`."""
    def build():
        Cc = np.asarray(C() if callable(C) else C, float)
        th, am, off = bulge(), amp(), offset()
        d = np.array([math.cos(th), math.sin(th), 0.0])
        ocean = Ellipse(width=2 * R * (1 + am), height=2 * R * (1 - 0.35 * am), stroke_color=ATMO, stroke_width=4,
                        fill_color=OCEAN, fill_opacity=0.92).rotate(th).move_to(Cc + d * off * R)
        cs = np.array(list(core()) + [0.0])
        c0 = Cc + cs
        body = Circle(radius=R * 0.8, stroke_color="#0B2A4A", stroke_width=2, fill_color="#14507E", fill_opacity=1).move_to(c0)
        g = VGroup(ocean, body)
        r0 = rot()
        for a, rr, w, h in _BLOBS:
            ang = a + r0
            pos = c0 + R * 0.52 * rr * 1.6 * np.array([math.cos(ang), math.sin(ang), 0.0])
            g.add(Ellipse(width=R * w * 1.3, height=R * h * 1.3, stroke_width=0, fill_color=LAND, fill_opacity=0.95).rotate(ang + math.pi / 2).move_to(pos))
        mk = marker if marker is not None else 0.0
        mpos = c0 + R * 0.8 * np.array([math.cos(r0 + mk), math.sin(r0 + mk), 0.0])
        on = 1.0 if marker is not None else 0.0
        g.add(Dot(mpos, radius=R * 0.1, color="#FF4D6D", fill_opacity=on), Dot(mpos, radius=R * 0.2, color="#FF4D6D", fill_opacity=0.3 * on))
        return _a(g, alpha)
    m = always_redraw(build)
    m._dynamic = True
    return m


def moon(center, r: float = 0.4) -> VGroup:
    c = np.asarray(center, float)
    g = VGroup(Circle(radius=r, stroke_color="#E6E6E6", stroke_width=3, fill_color="#C9CCD3", fill_opacity=1).move_to(c))
    for dx, dy, k in ((-0.3, 0.25, 0.2), (0.25, -0.2, 0.26), (0.1, 0.4, 0.14)):
        g.add(Circle(radius=r * k, stroke_width=0, fill_color="#9EA3AE", fill_opacity=1).move_to(c + r * np.array([dx, dy, 0.0])))
    return g


def sun(center, r: float = 0.9) -> VGroup:
    c = np.asarray(center, float)
    g = VGroup(*[Circle(radius=r * (1.0 + 0.35 * k), stroke_width=0, fill_color="#FFB703", fill_opacity=0.12).move_to(c) for k in (3, 2, 1)])
    g.add(Circle(radius=r, stroke_color="#FFE08A", stroke_width=3, fill_color="#FFC93C", fill_opacity=1).move_to(c))
    return g


def curve(origin, w: float, h: float, fn, u_now, color="#2EC5FF", width=7, n=160, alpha=None, dashed=False):
    """A graph line y=fn(u), u in 0..1, drawn up to u_now() (a constant-size polyline)."""
    o = np.asarray(origin, float)

    def build():
        un = max(0.001, min(1.0, u_now()))
        pts = []
        for i in range(n):
            u = min(un, i / (n - 1))
            pts.append(o + np.array([w * u, h * fn(u), 0.0]))
        m = VMobject(stroke_color=color, stroke_width=width, fill_opacity=0)
        m.set_points_as_corners(pts)
        if dashed:
            m.set_stroke(opacity=0.55)
        return _a(VGroup(m, Dot(pts[-1], radius=0.13, color=color)), alpha)
    g = always_redraw(build)
    g._dynamic = True
    return g


def axes(origin, w: float, h: float, color="#4A5A80") -> VGroup:
    o = np.asarray(origin, float)
    return VGroup(Line(o + np.array([0, -h, 0]), o + np.array([0, h, 0]), color=color, stroke_width=3),
                  Line(o + np.array([0, 0, 0]), o + np.array([w, 0, 0]), color=color, stroke_width=3))


def boat(center, s: float = 1.0) -> VGroup:
    c = np.asarray(center, float)
    hull = Polygon(c + s * np.array([-0.7, 0.1, 0]), c + s * np.array([0.7, 0.1, 0]), c + s * np.array([0.45, -0.25, 0]), c + s * np.array([-0.45, -0.25, 0]),
                   stroke_width=0, fill_color="#C0392B", fill_opacity=1)
    mast = Line(c + s * np.array([0, 0.1, 0]), c + s * np.array([0, 0.95, 0]), color="#F5F7FA", stroke_width=4)
    sail = Polygon(c + s * np.array([0.05, 0.9, 0]), c + s * np.array([0.05, 0.2, 0]), c + s * np.array([0.6, 0.2, 0]), stroke_width=0,
                   fill_color="#F5F7FA", fill_opacity=1)
    return VGroup(hull, mast, sail)


def building(base_left, floors: int = 5, fh: float = 0.5, w: float = 1.4) -> VGroup:
    b = np.asarray(list(base_left) + [0.0] * (3 - len(base_left)), float)
    g = VGroup()
    for k in range(floors):
        g.add(Rectangle(width=w, height=fh, stroke_color="#0B1020", stroke_width=2, fill_color="#5B6B96", fill_opacity=1).move_to(b + np.array([w / 2, fh / 2 + k * fh, 0.0])))
        for dx in (-0.35, 0.0, 0.35):
            g.add(Rectangle(width=0.22, height=0.22, stroke_width=0, fill_color="#FFE08A", fill_opacity=0.9).move_to(b + np.array([w / 2 + dx, fh / 2 + k * fh, 0.0])))
    return g
