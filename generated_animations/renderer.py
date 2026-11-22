"""The one Manim scene that plays a topic's scene modules back to back (camera, HUD, avatar, transitions)."""
from __future__ import annotations

import logging

from manim import MovingCameraScene

from .avatar import Avatar
from .runtime import SceneContext, Timeline
from .shared import lighting
from .shared.camera import CameraRig

log = logging.getLogger("generated_animations")
BG = "#060912"


class GeneratedScene(MovingCameraScene):
    def __init__(self, modules, durations, configs, narration=None, **kwargs):
        self.modules, self.durations, self.configs, self.narration = modules, durations, configs, narration
        self.reports: list[dict] = []
        super().__init__(**kwargs)

    def construct(self):
        from manim import config
        self.camera.background_color = BG
        fw, fh = config.frame_width, config.frame_height
        self.timeline = Timeline(self)
        self.add(self.timeline.make_clock())
        self.rig = CameraRig(self)

        sky = lighting.starfield(fw * 1.15, fh * 1.15)
        sky.set_z_index(-10)
        self.rig.pin(sky)
        vig = lighting.vignette(fw, fh)
        vig.set_z_index(9)
        self.rig.pin(vig)
        self.add(sky, vig)

        level = (lambda t: self.narration.level(t)) if self.narration else None
        self.avatar = Avatar(self.rig, self.timeline, mouth_level=level, position=(-2.6, -7.85), scale=0.92)
        self.avatar.set_z_index(12)
        self.add(self.avatar)

        from manim import Rectangle
        self.cover = Rectangle(width=fw * 1.8, height=fh * 1.8, stroke_width=0, fill_color=BG, fill_opacity=1)
        self.cover.set_opacity(0).set_z_index(8)
        self.rig.pin(self.cover)
        self.add(self.cover)
        self._covered = False

        for i, (mod, dur, cfg) in enumerate(zip(self.modules, self.durations, self.configs)):
            ctx = SceneContext(self, self.rig, self.avatar, self.timeline, dur, i, cfg, fw, fh,
                               start=self.timeline.t)
            if self._covered:
                self.play(self.cover.animate.set_opacity(0), run_time=0.3)
                self._covered = False
            mod.animate(ctx)
            ctx.pad(reserve=0.5)
            over = -ctx.remaining() + 0.5
            if over > 0.05:
                log.warning("scene %s overran by %.2fs", i + 1, over)
            self.reports.append({"scene": i + 1, "planned": dur, "overrun": round(max(0.0, over), 2)})
            self._outro(ctx)

    def _outro(self, ctx):
        """Cover fades in (camera glides home, static items fade) while dynamic objects are hidden under it."""
        from manim import FadeOut
        c, w = self.rig._home
        static = [o for o in ctx.objects if not getattr(o, "_dynamic", False)]
        self.play(self.cover.animate.set_opacity(1), *[FadeOut(o) for o in static],
                  self.rig.frame.animate.set(width=w).move_to(c), run_time=0.5)
        self._covered = True
        for o in list(ctx.objects):
            o.clear_updaters()
            self.remove(o)
        ctx.objects.clear()
        self.avatar.look_at(None)
