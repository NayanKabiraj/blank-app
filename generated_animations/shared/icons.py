"""Small vector icons for the `prop` of title / keyword scenes (all drawn from Manim primitives)."""
from __future__ import annotations

import math

import numpy as np
from manim import (Arc, Circle, Ellipse, Line, Polygon, Rectangle, RoundedRectangle, Square, Star, Text, VGroup)

GOLD, BLUE, RED, GREEN, PINK, WHITE, INKC = "#F4C95D", "#2EC5FF", "#FF4D6D", "#4CD97B", "#FF8FA3", "#F5F7FA", "#0B1020"


def _heart(color=RED) -> VGroup:
    pts = []
    for t in np.linspace(0, 2 * math.pi, 80):
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x / 36, y / 36, 0))
    return VGroup(Polygon(*pts, stroke_color=WHITE, stroke_width=3, fill_color=color, fill_opacity=1))


def _fill(m, color, stroke=WHITE):
    return m.set_fill(color, 1).set_stroke(stroke, 3)


def icon(name: str, size: float = 2.0) -> VGroup:
    """Icon about `size` units across, centred on the origin."""
    g = {
        "star": lambda: VGroup(Star(5, outer_radius=0.5, inner_radius=0.22, stroke_color=WHITE, stroke_width=3,
                                    fill_color=GOLD, fill_opacity=1)),
        "bulb": lambda: VGroup(*[Line(0.42 * np.array([math.cos(a), math.sin(a), 0]) + (0, 0.12, 0),
                                      0.58 * np.array([math.cos(a), math.sin(a), 0]) + (0, 0.12, 0), color=GOLD, stroke_width=4)
                                 for a in np.linspace(0.3, math.pi - 0.3, 5)],
                               _fill(Circle(radius=0.3), GOLD).shift((0, 0.12, 0)),
                               _fill(RoundedRectangle(corner_radius=0.04, width=0.3, height=0.2), "#C9CED8").shift((0, -0.24, 0))),
        "coin": lambda: VGroup(_fill(Circle(radius=0.5), GOLD), Circle(radius=0.38, stroke_color="#C79A1E", stroke_width=3),
                               Text("$", font_size=44, color="#9A6E00", weight="BOLD")),
        "planet": lambda: VGroup(_fill(Circle(radius=0.32), "#B084FF"),
                                 Ellipse(width=1.1, height=0.3, stroke_color=GOLD, stroke_width=5).rotate(0.4)),
        "globe": lambda: VGroup(_fill(Circle(radius=0.5), BLUE), Ellipse(width=0.5, height=1.0, stroke_color=WHITE, stroke_width=2),
                                Line((-0.5, 0, 0), (0.5, 0, 0), color=WHITE, stroke_width=2),
                                _fill(Circle(radius=0.12), GREEN, GREEN).shift((-0.18, 0.18, 0))),
        "phone": lambda: VGroup(_fill(RoundedRectangle(corner_radius=0.1, width=0.55, height=1.0), INKC, WHITE),
                                RoundedRectangle(corner_radius=0.05, width=0.43, height=0.78, stroke_width=0, fill_color=BLUE, fill_opacity=0.8)),
        "bank": lambda: VGroup(Polygon((-0.55, 0.15, 0), (0, 0.55, 0), (0.55, 0.15, 0), fill_color=GOLD, fill_opacity=1, stroke_color=WHITE),
                               *[Rectangle(width=0.1, height=0.55, stroke_width=0, fill_color=WHITE, fill_opacity=1).shift((x, -0.17, 0))
                                 for x in (-0.38, -0.13, 0.13, 0.38)],
                               Rectangle(width=1.2, height=0.1, stroke_width=0, fill_color=GOLD, fill_opacity=1).shift((0, -0.5, 0))),
        "rocket": lambda: VGroup(_fill(Ellipse(width=0.42, height=1.0), WHITE, "#C9CED8"), _fill(Circle(radius=0.1), BLUE).shift((0, 0.15, 0)),
                                 Polygon((-0.2, -0.25, 0), (-0.42, -0.5, 0), (-0.14, -0.4, 0), fill_color=RED, fill_opacity=1, stroke_width=0),
                                 Polygon((0.2, -0.25, 0), (0.42, -0.5, 0), (0.14, -0.4, 0), fill_color=RED, fill_opacity=1, stroke_width=0),
                                 Polygon((-0.1, -0.5, 0), (0, -0.78, 0), (0.1, -0.5, 0), fill_color=GOLD, fill_opacity=1, stroke_width=0)),
        "brain": lambda: VGroup(_fill(Circle(radius=0.3), PINK).shift((-0.2, 0.05, 0)), _fill(Circle(radius=0.3), PINK).shift((0.2, 0.05, 0)),
                                _fill(Circle(radius=0.26), PINK).shift((0, -0.15, 0)),
                                Line((0, 0.35, 0), (0, -0.1, 0), color="#C45A78", stroke_width=3)),
        "chip": lambda: VGroup(*[Line((x, 0.4, 0), (x, 0.58, 0), color=GOLD, stroke_width=4) for x in (-0.25, 0, 0.25)],
                               *[Line((x, -0.4, 0), (x, -0.58, 0), color=GOLD, stroke_width=4) for x in (-0.25, 0, 0.25)],
                               *[Line((0.4, y, 0), (0.58, y, 0), color=GOLD, stroke_width=4) for y in (-0.25, 0, 0.25)],
                               *[Line((-0.4, y, 0), (-0.58, y, 0), color=GOLD, stroke_width=4) for y in (-0.25, 0, 0.25)],
                               _fill(Square(side_length=0.8), "#2B3A67", BLUE), _fill(Square(side_length=0.35), BLUE, BLUE)),
        "heart": _heart,
        "clock": lambda: VGroup(_fill(Circle(radius=0.5), WHITE, BLUE).set_stroke(BLUE, 6), Line((0, 0, 0), (0, 0.3, 0), color=INKC, stroke_width=5),
                                Line((0, 0, 0), (0.22, -0.08, 0), color=RED, stroke_width=4)),
        "gear": lambda: VGroup(_fill(Star(8, outer_radius=0.52, inner_radius=0.4), "#8FA0C8"), _fill(Circle(radius=0.16), INKC, WHITE)),
        "atom": lambda: VGroup(*[Ellipse(width=1.1, height=0.38, stroke_color=BLUE, stroke_width=3).rotate(a) for a in (0, math.pi / 3, 2 * math.pi / 3)],
                               _fill(Circle(radius=0.1), GOLD)),
        "book": lambda: VGroup(_fill(Rectangle(width=0.55, height=0.8), BLUE).shift((-0.28, 0, 0)), _fill(Rectangle(width=0.55, height=0.8), "#1B8FC2").shift((0.28, 0, 0)),
                               *[Line((-0.5 + 0.0, y, 0), (-0.1, y, 0), color=WHITE, stroke_width=2) for y in (0.2, 0.0, -0.2)]),
        "magnet": lambda: VGroup(Arc(radius=0.4, start_angle=0, angle=math.pi, stroke_color=RED, stroke_width=14),
                                 Line((-0.4, 0, 0), (-0.4, -0.4, 0), color=RED, stroke_width=14), Line((0.4, 0, 0), (0.4, -0.4, 0), color=RED, stroke_width=14),
                                 Line((-0.4, -0.3, 0), (-0.4, -0.45, 0), color=WHITE, stroke_width=14), Line((0.4, -0.3, 0), (0.4, -0.45, 0), color=WHITE, stroke_width=14)),
        "cloud": lambda: VGroup(*[_fill(Circle(radius=r), "#E6EEF9", "#E6EEF9").shift((x, y, 0)) for r, x, y in ((0.28, -0.3, -0.05), (0.36, 0, 0.08), (0.28, 0.3, -0.05))],
                                Rectangle(width=0.75, height=0.26, stroke_width=0, fill_color="#E6EEF9", fill_opacity=1).shift((0, -0.15, 0))),
    }.get(name) or (lambda: VGroup(Star(5, outer_radius=0.5, inner_radius=0.22, stroke_color=WHITE, fill_color=GOLD, fill_opacity=1)))
    m = g()
    m.scale_to_fit_height(size) if m.height >= m.width else m.scale_to_fit_width(size)
    return m.move_to((0, 0, 0))
