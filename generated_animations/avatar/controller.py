"""The presenter "Pip": a hand-drawn teacher - swept-back grey hair, glasses, a big smile, an orange vest over a white
rolled-sleeve shirt, light trousers and shoes. Full body, ink outlines and a little pencil hatching.

State (all ValueTrackers, so ordinary Manim animations drive them):
  pos x/y/scale ........ where Pip stands: (x, y) is the point between his feet (movement.py)
  expr[...] ............ face (expressions.py)
  pose_* weights ....... arm gestures (gestures.py); the resting pose is "explaining": a pencil pointer in one hand, a finger in the other
  gaze target .......... Pip's eyes + head follow a world-space point or moving mobject
Automatic behaviours: idle breathing/sway, eye blinks, and lip-sync from the narration's loudness envelope.
"""
from __future__ import annotations

import math

import numpy as np
from manim import Arc, Circle, Ellipse, Line, Polygon, Rectangle, ValueTracker, VGroup

from .expressions import EXPRESSIONS

INK = "#2B2B2B"
SKIN, HAIR, HAIR_D = "#F2C6A0", "#A9ABB0", "#5D6068"
VEST, VEST_D, SHIRT, TROUSERS, SHOE, PENCIL = "#F2A03D", "#C87818", "#F7F7F5", "#E9E9E6", "#8A8F98", "#E8903A"

HEIGHT = 4.35          # local units from the soles to the top of the hair
S_R, S_L = np.array([0.62, 2.78, 0.0]), np.array([-0.62, 2.78, 0.0])    # shoulders (viewer's right / left)
UPPER, FORE = 0.82, 0.78
REST_R = (0.35, 0.95)                        # pencil arm: out and up, like a teacher explaining
REST_L = (-math.pi / 2 - 0.65, 0.2)         # other forearm across the body, finger pointing


def _lerp(a: float, b: float, w: float) -> float:
    return a + (b - a) * w


def _limb(p0, p1, width: float, fill: str, cap: bool = True) -> VGroup:
    """A drawn limb: a dark outline stroke under a fill stroke."""
    return VGroup(Line(p0, p1, color=INK, stroke_width=width + 7), Line(p0, p1, color=fill, stroke_width=width))


class Avatar(VGroup):
    def __init__(self, rig, timeline, mouth_level=None, position=(-2.6, -7.85), scale: float = 0.92, seed: int = 11):
        super().__init__()
        self.rig, self.timeline = rig, timeline
        self.mouth_level = mouth_level or (lambda t: 0.0)
        self.x, self.y, self.s = ValueTracker(position[0]), ValueTracker(position[1]), ValueTracker(scale)
        self.expr = {k: ValueTracker(v) for k, v in EXPRESSIONS["neutral"].items()}
        self.pose = {k: ValueTracker(0.0) for k in ("point", "wave", "present", "shrug")}
        self.look_fn = None          # callable -> world point, or None (look at the viewer)
        self.point_fn = None
        self.facing = ValueTracker(0.0)   # head turn toward the stage (-1..1)
        rng = np.random.default_rng(seed)
        self._blinks = np.cumsum(rng.uniform(2.2, 4.2, 40))
        self._mouth = 0.0
        self.add_updater(lambda m: m._refresh())
        self._refresh()

    # -- helpers ---------------------------------------------------------------------------
    def _world(self, canon_pt):
        k = self.rig.frame.width / self.rig.base_w
        return np.asarray(canon_pt, float) * k + self.rig.frame.get_center()

    def _to_canon(self, world_pt):
        k = self.rig.frame.width / self.rig.base_w
        return (np.asarray(world_pt, float) - self.rig.frame.get_center()) / k

    def look_at(self, target):
        """Look at a mobject, a callable returning a world point, or a world point. None = look at the viewer."""
        if target is None:
            self.look_fn = None
        elif callable(target):
            self.look_fn = target
        elif hasattr(target, "get_center"):
            self.look_fn = target.get_center
        else:
            self.look_fn = lambda p=np.asarray(target, float): p
        return self

    def set_point_target(self, target):
        if callable(target):
            self.point_fn = target
        elif hasattr(target, "get_center"):
            self.point_fn = target.get_center
        else:
            self.point_fn = lambda p=np.asarray(target, float): p
        return self

    def _blink(self, t: float) -> float:
        for b in self._blinks:
            if 0 <= t - b < 0.16:
                return math.sin((t - b) / 0.16 * math.pi)
        return 0.0

    # -- geometry --------------------------------------------------------------------------
    def _arm(self, shoulder, a1, a2, finger: float, pencil: float):
        """Sleeve (rolled), forearm, hand, an optional pointing finger and an optional pencil pointer. Constant part count."""
        d1 = np.array([math.cos(a1), math.sin(a1), 0.0])
        d2 = np.array([math.cos(a2), math.sin(a2), 0.0])
        elbow = shoulder + UPPER * d1
        wrist = elbow + FORE * d2
        cuff = elbow + FORE * 0.34 * d2
        hand = wrist + 0.1 * d2
        tip_f = hand + (0.12 + 0.3 * finger) * d2
        pen0 = hand - 0.12 * d2
        pen1 = hand + (0.25 + 0.75 * pencil) * d2
        g = VGroup(
            _limb(shoulder, elbow, 24, SHIRT),
            _limb(elbow, cuff, 22, SHIRT),                       # rolled sleeve
            _limb(cuff, wrist, 17, SKIN),                        # forearm
            Line(pen0, pen1, color=INK, stroke_width=11, stroke_opacity=1.0 if pencil > 0 else 0.0),
            Line(pen0, pen1, color=PENCIL, stroke_width=6, stroke_opacity=1.0 if pencil > 0 else 0.0),
            Circle(radius=0.13, stroke_color=INK, stroke_width=3.5, fill_color=SKIN, fill_opacity=1).move_to(hand),
            Line(hand, tip_f, color=INK, stroke_width=9, stroke_opacity=1.0 if finger > 0 else 0.0),
            Line(hand, tip_f, color=SKIN, stroke_width=5, stroke_opacity=1.0 if finger > 0 else 0.0),
        )
        return g

    def _build(self):
        t = self.timeline.t
        e = {k: v.get_value() for k, v in self.expr.items()}
        w = {k: v.get_value() for k, v in self.pose.items()}

        # gaze + head turn toward the target
        gx = gy = 0.0
        if self.look_fn is not None:
            head_world = self._world((self.x.get_value(), self.y.get_value() + 3.55 * self.s.get_value(), 0))
            d = np.asarray(self.look_fn(), float) - head_world
            n = max(1e-6, np.linalg.norm(d[:2]))
            gx, gy = d[0] / n, d[1] / n
        turn = float(np.clip(gx, -1, 1)) * self.facing.get_value()
        sway = math.sin(t * 1.3) * 0.025
        breathe = 0.008 * math.sin(t * 2.1)
        bob = 0.02 * math.sin(t * 2.1)

        # lip sync (smoothed so the mouth does not flutter)
        target_open = min(1.0, self.mouth_level(t) * 1.2)
        self._mouth += (target_open - self._mouth) * 0.55
        mouth_open = max(self._mouth, e["mouth_o"])

        hip_sway = 0.03 * math.sin(t * 0.9)

        # ---- legs, shoes, trousers
        legs = VGroup()
        for sx in (-1, 1):
            hip = np.array([sx * 0.22 + hip_sway, 1.85, 0.0])
            ankle = np.array([sx * 0.27 + hip_sway * 0.4, 0.22, 0.0])
            legs.add(_limb(hip, ankle, 25, TROUSERS))
            legs.add(Ellipse(width=0.62, height=0.22, stroke_color=INK, stroke_width=3.5, fill_color=SHOE, fill_opacity=1).move_to((sx * 0.3 + sx * 0.06 + hip_sway * 0.4, 0.12, 0)))
        crotch = Polygon((-0.46 + hip_sway, 1.85, 0), (0.46 + hip_sway, 1.85, 0), (0.0 + hip_sway, 1.42, 0), stroke_width=0, fill_color=TROUSERS, fill_opacity=1)

        # ---- torso: white shirt under an orange vest with a V neck, pencil hatching on the vest
        top, hem = 2.84 + breathe, 1.72
        shirt = Polygon((-0.64, top, 0), (0.64, top, 0), (0.52, hem, 0), (-0.52, hem, 0), stroke_color=INK, stroke_width=3.5, fill_color=SHIRT, fill_opacity=1)
        vest_l = Polygon((-0.64, top, 0), (-0.13, top, 0), (0.0, 2.25, 0), (-0.03, hem - 0.05, 0), (-0.52, hem, 0), stroke_color=INK, stroke_width=3.5, fill_color=VEST, fill_opacity=1)
        vest_r = Polygon((0.64, top, 0), (0.13, top, 0), (0.0, 2.25, 0), (0.03, hem - 0.05, 0), (0.52, hem, 0), stroke_color=INK, stroke_width=3.5, fill_color=VEST, fill_opacity=1)
        hatch = VGroup(*[Line((sx * (0.55 - 0.1 * k) + sx * 0.02, 2.65 - 0.2 * k, 0), (sx * (0.4 - 0.1 * k), 2.45 - 0.2 * k, 0), color=VEST_D, stroke_width=3)
                         for sx in (-1, 1) for k in range(4)])
        collar = VGroup(Polygon((-0.13, top, 0), (-0.02, top + 0.02, 0), (-0.08, 2.5, 0), stroke_color=INK, stroke_width=2.5, fill_color=SHIRT, fill_opacity=1),
                        Polygon((0.13, top, 0), (0.02, top + 0.02, 0), (0.08, 2.5, 0), stroke_color=INK, stroke_width=2.5, fill_color=SHIRT, fill_opacity=1))
        neck = Line((0, 2.9, 0), (0, 3.12, 0), color=INK, stroke_width=33)
        neck2 = Line((0, 2.9, 0), (0, 3.12, 0), color=SKIN, stroke_width=26)

        # ---- arms (pose blending from the resting "explaining" pose)
        def blend(rest, pt, wave, pres, shr):
            a1, a2 = rest
            for wt, tgt in ((w["point"], pt), (w["wave"], wave), (w["present"], pres), (w["shrug"], shr)):
                a1 = _lerp(a1, tgt[0], wt)
                a2 = _lerp(a2, tgt[1], wt)
            return a1, a2
        point_ang = 0.6
        if self.point_fn is not None:
            sh_world = self._world((self.x.get_value() + S_R[0] * self.s.get_value(), self.y.get_value() + S_R[1] * self.s.get_value(), 0))
            d = np.asarray(self.point_fn(), float) - sh_world
            point_ang = math.atan2(d[1], d[0])
        rest_sway = 0.04 * math.sin(t * 1.7)
        r1, r2 = blend((REST_R[0] + rest_sway, REST_R[1] - rest_sway), (point_ang, point_ang), (1.15, 1.6 + 0.55 * math.sin(t * 11)), (0.05, 0.7), (-0.2, 0.95))
        l1, l2 = blend((REST_L[0] - rest_sway * 0.5, REST_L[1]), REST_L, REST_L, (math.pi - 0.3, math.pi - 0.65), (math.pi + 0.2, math.pi - 0.95))
        arm_r = self._arm(S_R, r1, r2, w["point"], 1.0 - 0.7 * w["wave"])
        arm_l = self._arm(S_L, l1, l2, 1.0 - 0.6 * (w["present"] + w["shrug"]), 0.0)

        # ---- head
        hc = np.array([0.0 + turn * 0.08, 3.62 + bob, 0.0])
        face = Ellipse(width=0.82, height=1.02, stroke_color=INK, stroke_width=3.5, fill_color=SKIN, fill_opacity=1).move_to(hc)
        ears = VGroup(*[Circle(radius=0.09, stroke_color=INK, stroke_width=3, fill_color=SKIN, fill_opacity=1).move_to(hc + np.array([sx * 0.41, -0.02, 0])) for sx in (-1, 1)])
        # swept-back grey hair: an outer cap, an inner hairline, and pencil strokes
        outer = [hc + np.array([0.47 * math.cos(a), 0.58 * math.sin(a) + 0.08, 0.0]) for a in np.linspace(math.radians(8), math.radians(172), 14)]
        inner = [hc + np.array([0.4 * math.cos(a), 0.3 * math.sin(a) + 0.28 + 0.05 * math.cos(3 * a), 0.0]) for a in np.linspace(math.radians(172), math.radians(8), 12)]
        hair = Polygon(*outer, *inner, stroke_color=INK, stroke_width=3, fill_color=HAIR, fill_opacity=1)
        strokes = VGroup(*[Line(hc + np.array([-0.3 + 0.13 * k, 0.5 - 0.03 * k, 0]), hc + np.array([-0.18 + 0.14 * k, 0.65, 0]), color=HAIR_D, stroke_width=3) for k in range(5)])
        tufts = VGroup(*[Line(hc + np.array([sx * 0.45, 0.15, 0]), hc + np.array([sx * 0.4, -0.05, 0]), color=HAIR_D, stroke_width=6) for sx in (-1, 1)])
        # glasses with eyes inside
        eye_y = hc[1] + 0.08
        eye_open = max(0.0, e["eye_open"] * (1 - 0.95 * self._blink(t)))
        glasses, eyes, brows = VGroup(), VGroup(), VGroup()
        for sx in (-1, 1):
            ex = hc[0] + sx * 0.2 + turn * 0.06
            white = Ellipse(width=0.25, height=0.25 * min(1.3, max(0.05, eye_open)), stroke_width=0, fill_color="#FFFFFF", fill_opacity=1 if eye_open > 0.12 else 0).move_to((ex, eye_y, 0))
            pupil = Circle(radius=0.055, stroke_width=0, fill_color=INK, fill_opacity=1 if eye_open > 0.12 else 0).move_to((ex + gx * 0.045 + turn * 0.03, eye_y + gy * 0.04, 0))
            lid = Line((ex - 0.12, eye_y, 0), (ex + 0.12, eye_y, 0), color=INK, stroke_width=4, stroke_opacity=0 if eye_open > 0.12 else 1)
            eyes.add(white, pupil, lid)
            glasses.add(Circle(radius=0.17, stroke_color=INK, stroke_width=5, fill_opacity=0).move_to((ex, eye_y, 0)))
            by = eye_y + 0.27 + 0.1 * e["brow_raise"]
            tilt = 0.12 * e["brow_tilt"]
            brows.add(Line((ex + sx * 0.14, by - tilt * 0.5, 0), (ex - sx * 0.14, by + tilt * 0.5, 0), color=HAIR_D, stroke_width=6))
        glasses.add(Line((hc[0] - 0.03 + turn * 0.06, eye_y, 0), (hc[0] + 0.03 + turn * 0.06, eye_y, 0), color=INK, stroke_width=4))
        for sx in (-1, 1):
            glasses.add(Line((hc[0] + sx * 0.37 + turn * 0.06, eye_y, 0), (hc[0] + sx * 0.42, eye_y - 0.02, 0), color=INK, stroke_width=3))
        nose = Arc(radius=0.1, start_angle=math.pi * 1.1, angle=math.pi * 0.75, stroke_color=INK, stroke_width=3).move_to((hc[0] + 0.02 + turn * 0.08, hc[1] - 0.16, 0))
        # mouth: a big smile; opens (with teeth) when he talks
        mx, my = hc[0] + turn * 0.1, hc[1] - 0.3
        smile = e["smile"] * 1.1
        ang = max(0.06, 1.0 * abs(smile))
        arc = Arc(radius=0.3, start_angle=(-math.pi / 2 - ang / 2) if smile >= 0 else (math.pi / 2 - ang / 2), angle=ang, stroke_width=5, color=INK).move_to((mx, my + (0.04 if smile >= 0 else -0.04), 0))
        arc.set_stroke(opacity=1 if mouth_open < 0.08 else 0)
        mouth = Ellipse(width=0.3 + 0.12 * smile, height=0.05 + 0.2 * mouth_open, stroke_color=INK, stroke_width=3, fill_color="#7A2630", fill_opacity=1 if mouth_open >= 0.08 else 0).move_to((mx, my - 0.02, 0))
        mouth.set_stroke(opacity=1 if mouth_open >= 0.08 else 0)
        teeth = Rectangle(width=0.24 + 0.06 * smile, height=0.07, stroke_width=0, fill_color="#FFFFFF", fill_opacity=1 if mouth_open >= 0.18 else 0).move_to((mx, my + 0.03 + 0.1 * mouth_open, 0))
        cheeks = VGroup(*[Circle(radius=0.07, stroke_width=0, fill_color="#F08A8A", fill_opacity=0.2 + 0.12 * smile).move_to((hc[0] + sx * 0.27 + turn * 0.08, hc[1] - 0.2, 0)) for sx in (-1, 1)])
        head = VGroup(ears, face, hair, strokes, tufts, cheeks, glasses, eyes, brows, nose, arc, mouth, teeth)
        head.rotate(sway + turn * 0.1, about_point=np.array([0.0, 3.0, 0.0]))

        full = VGroup(legs, crotch, shirt, vest_l, vest_r, hatch, collar, neck, neck2, arm_l, head, arm_r)
        full.scale(self.s.get_value(), about_point=np.zeros(3))
        full.shift((self.x.get_value(), self.y.get_value(), 0))
        return self.rig.hud_transform(full)

    def _refresh(self):
        # in place: Manim caches the moving-mobject list at the start of each play, so children must keep identity
        self.become(self._build())
