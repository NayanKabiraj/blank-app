"""Runtime objects handed to every scene module: the timeline clock and the SceneContext."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from manim import FadeOut, Mobject

from .shared import typography
from .shared.motion import smooth


def _v(x, y, z=0.0):
    import numpy as _np
    return _np.array([x, y, z], dtype=float)


log = logging.getLogger("generated_animations")

# canonical (HUD) screen layout for a 9 x 16 frame - scene modules position against these
HEADLINE_Y, STAGE_Y, CAPTION_Y = 6.8, 1.9, -2.9


class Timeline:
    """Seconds of video rendered so far = the renderer's own frame clock (frames / fps), so scene timing and
    the narration track cannot drift apart however many short plays a scene makes."""

    def __init__(self, scene=None):
        self.scene = scene
        self._t = 0.0

    @property
    def t(self) -> float:
        return self.scene.renderer.time if self.scene is not None else self._t

    @t.setter
    def t(self, value: float):
        self._t = value

    def __deepcopy__(self, memo):
        return self   # one shared clock; Manim copies mobjects that reference it

    def __copy__(self):
        return self

    def make_clock(self) -> Mobject:
        """A mobject with a time-based (dt) updater. Manim only runs updaters during wait() when at least one
        mobject has one; without it every wait() is rendered as a single frozen frame."""
        clock = Mobject()

        def tick(_m, dt):
            pass
        clock.add_updater(tick)
        return clock


@dataclass
class SceneContext:
    scene: object
    rig: object
    avatar: object
    timeline: Timeline
    duration: float
    index: int
    config: dict
    frame_w: float
    frame_h: float
    start: float = 0.0
    objects: list = field(default_factory=list)
    caption_mob: object = None
    overrun: float = 0.0
    layout: object = None          # shared.layout.Layout when rendering a plan
    lang: str = "en"
    is_last: bool = False

    # time ---------------------------------------------------------------------------------
    def elapsed(self) -> float:
        return self.timeline.t - self.start

    def remaining(self) -> float:
        return self.duration - self.elapsed()

    def hold(self, seconds: float):
        if seconds > 0.02:
            self.scene.wait(seconds)

    def pad(self, reserve: float = 0.0):
        """Wait out the rest of this scene's narration window (minus `reserve` seconds for the outro)."""
        self.hold(self.remaining() - reserve)

    def play(self, *anims, **kw):
        self.scene.play(*anims, **kw)

    # narration-synced beats -----------------------------------------------------------------
    def sentences(self, text=None, t0=None, span=None):
        """[(text, start_in_scene, end_in_scene)] - narration split at sentence ends, timed by character share."""
        import re
        parts = [p for p in re.split(r"(?<=[.!?\u0964])\s+", (text or self.config["narration"]).strip()) if p]
        total = sum(len(p) for p in parts)
        t = t0 if t0 is not None else self.config.get("pad_before", 0.45)
        span = span if span is not None else self.config.get("narration_seconds", self.duration - 1.0)
        out = []
        for p in parts:
            d = span * len(p) / total
            out.append((p, t, t + d))
            t += d
        return out

    def beat(self, i: int, show_caption: bool = True):
        """Wait until sentence i begins in the narration, then show its caption. Returns (text, start, end)."""
        text, start, end = self.sentences()[i]
        self.hold(start - self.elapsed())
        if show_caption:
            self.caption(text)
        return text, start, end

    # shots (an authored animation that spans several narration scenes) ------------------------------
    @property
    def stage(self):
        """(centre, width, height) of the free area of the screen for this layout."""
        import numpy as np
        L = self.layout
        return np.array([L.stage_center[0], L.stage_center[1], 0.0]), L.stage_w, L.stage_h

    def t_of(self, i: int) -> float:
        """Seconds (from the shot's start) at which narration scene i of this shot begins."""
        return self.config["subs"][i]["start"]

    def tt(self, i: int, k: int = 0) -> float:
        """Start time (seconds from the shot's start) of sentence k of narration scene i (clamped to the last sentence)."""
        sub = self.config["subs"][i]
        times = [t for _s, t, _e in self.sentences(sub["text"], sub["start"], sub["end"] - sub["start"])]
        return times[min(k, len(times) - 1)]

    def until(self, t: float):
        """Hold until `t` seconds into the shot."""
        self.hold(t - self.elapsed())

    def text(self, s, size=34, color="#F5F7FA", width=None, weight="BOLD"):
        size = size * (1.3 if self.layout is not None and self.layout.landscape else 1.0)
        return typography.text(str(s), size, color, weight, width or (self.layout.stage_w * 0.9), self.lang)

    # layers -------------------------------------------------------------------------------
    def add(self, *mobs, z: int = 0):
        for m in mobs:
            m.set_z_index(z)
            self.scene.add(m)
            self.objects.append(m)
        return mobs[0] if len(mobs) == 1 else mobs

    def headline(self, text: str, color: str = "#F5F7FA"):
        if self.layout is not None:
            h = typography.headline(text, color, max_width=self.layout.headline_w, lang=self.lang)
            h.move_to((0, self.layout.headline_y, 0))
            self.add(h, z=10)
            return h
        h = typography.headline(text, color)
        h.move_to((0, HEADLINE_Y, 0))
        self.rig.pin(h)
        self.add(h, z=10)
        return h

    def caption(self, text: str, run_time: float = 0.35):
        """Swap the screen caption for `text` (pinned, so camera moves never carry it away)."""
        from manim import FadeIn
        new = typography.caption_pill(text)
        new.move_to((0, CAPTION_Y, 0))
        self.rig.pin(new)
        new.set_z_index(10)
        anims = [FadeIn(new, shift=_v(0, 0.15, 0), run_time=run_time)]
        if self.caption_mob is not None:
            anims.append(FadeOut(self.caption_mob, run_time=run_time))
            old = self.caption_mob
            self.objects = [o for o in self.objects if o is not old]
        self.scene.add(new)
        self.objects.append(new)
        self.caption_mob = new
        self.scene.play(*anims)

    def outro(self, run_time: float = 0.5):
        """Fade this scene's objects out and return the camera home - called by the renderer."""
        objs = [o for o in self.objects]
        anims = [FadeOut(o) for o in objs]
        self.scene.play(*anims, run_time=run_time, rate_func=smooth)
        for o in objs:
            o.clear_updaters()
            self.scene.remove(o)
        self.objects.clear()
        self.caption_mob = None
