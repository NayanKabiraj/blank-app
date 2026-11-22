"""Reusable diagram pieces: a rotating Earth, satellites, a phone, timer rings. Scene modules compose these."""
from __future__ import annotations

import math

import numpy as np
from manim import (Arc, Circle, Ellipse, Line, Rectangle, RoundedRectangle, VGroup, always_redraw)

OCEAN, LAND, ATMO, GOLD = "#1F6FB5", "#4CAF6A", "#7FD6FF", "#F4C95D"
# (longitude deg, latitude deg, width, height) rough continent blobs - stylised, not a map
_LAND = [(-100, 45, .9, .6), (-60, -15, .5, .9), (10, 5, .55, 1.1), (20, 50, .7, .4), (80, 45, 1.1, .55),
         (105, 15, .5, .5), (135, -25, .55, .4), (-150, 60, .4, .3), (60, 20, .5, .5)]


def earth(center, radius: float, timeline, spin: float = 0.35, grow=None) -> VGroup:
    """Stylised spinning Earth: ocean disc, drifting continents, atmosphere rim, limb shading."""
    c = np.asarray(center, float)
    R0 = radius

    def build():
        radius = R0 * (grow.get_value() if grow is not None else 1.0)
        g = VGroup(Circle(radius=radius * 1.08, stroke_width=0, fill_color=ATMO, fill_opacity=0.18).move_to(c),
                   Circle(radius=radius, stroke_color=ATMO, stroke_width=3, fill_color=OCEAN, fill_opacity=1).move_to(c))
        rot = timeline.t * spin
        for lon, lat, w, h in _LAND:
            la, lo = math.radians(lat), math.radians(lon) + rot
            vis = math.cos(la) * math.cos(lo)
            x, y = radius * math.cos(la) * math.sin(lo), radius * math.sin(la)
            # always add (fixed child count); hidden ones are fully transparent
            g.add(Ellipse(width=max(0.08, w * radius * 0.6 * max(vis, 0.0)), height=h * radius * 0.5, stroke_width=0,
                          fill_color=LAND, fill_opacity=0.0 if vis <= 0.05 else min(1.0, vis * 2)).move_to(c + (x, y, 0)))
        g.add(Circle(radius=radius, stroke_width=0, fill_color="#000000", fill_opacity=0.0).move_to(c))
        g.add(Arc(radius=radius * 0.97, start_angle=-0.9, angle=1.8, stroke_width=10, stroke_color="#02122A",
                  stroke_opacity=0.25).move_to(c + (radius * 0.2, -radius * 0.05, 0)))
        return g
    m = always_redraw(build)
    m._dynamic = True
    return m


def satellite(center, size: float = 0.22, color: str = GOLD) -> VGroup:
    body = Rectangle(width=size * 0.9, height=size * 0.9, stroke_width=0, fill_color="#DADDE5", fill_opacity=1)
    panels = VGroup(*[Rectangle(width=size * 1.5, height=size * 0.65, stroke_color="#0B3B7A", stroke_width=1.5,
                                fill_color="#2B6FD1", fill_opacity=1).next_to(body, d, buff=size * 0.08)
                      for d in (np.array([-1, 0, 0]), np.array([1, 0, 0]))])
    dot = Circle(radius=size * 0.1, stroke_width=0, fill_color=color, fill_opacity=1).move_to(body)
    return VGroup(panels, body, dot).move_to(center)


def phone(center, scale: float = 1.0, screen_color: str = "#0E2A4D") -> VGroup:
    body = RoundedRectangle(corner_radius=0.22, width=1.3, height=2.5, stroke_color="#E6EAF2", stroke_width=4,
                            fill_color="#0B1020", fill_opacity=1)
    screen = RoundedRectangle(corner_radius=0.12, width=1.12, height=2.2, stroke_width=0, fill_color=screen_color,
                              fill_opacity=1).move_to(body).shift((0, -0.02, 0))
    notch = RoundedRectangle(corner_radius=0.05, width=0.3, height=0.08, stroke_width=0, fill_color="#0B1020",
                             fill_opacity=1).move_to(body.get_top() + (0, -0.12, 0))
    return VGroup(body, screen, notch).scale(scale).move_to(center)


def location_dot(center, color: str = "#FF4D6D", r: float = 0.14) -> VGroup:
    return VGroup(Circle(radius=r * 1.9, stroke_width=0, fill_color=color, fill_opacity=0.25),
                  Circle(radius=r, stroke_color="#FFFFFF", stroke_width=3, fill_color=color, fill_opacity=1)).move_to(center)


def timer_ring(center, fraction: float, color: str, radius: float = 0.3) -> VGroup:
    """A stopwatch-style ring filled `fraction` of the way round."""
    base = Circle(radius=radius, stroke_color="#FFFFFF", stroke_width=3, stroke_opacity=0.35)
    fill = Arc(radius=radius, start_angle=math.pi / 2, angle=-2 * math.pi * fraction, stroke_color=color, stroke_width=6)
    tick = Line((0, radius, 0), (0, radius + 0.1, 0), color="#FFFFFF", stroke_width=3)
    return VGroup(base, fill, tick).move_to(center)
