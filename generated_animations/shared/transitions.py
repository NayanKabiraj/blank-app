"""Scene transitions. Overlays are pinned to the HUD so they cover the frame whatever the camera is doing."""
from __future__ import annotations

from manim import Circle, FadeIn, FadeOut, Rectangle, Square

from .motion import ease_in_out_cubic


def _cover(ctx, color: str):
    r = Rectangle(width=ctx.frame_w * 1.6 * ctx.rig.frame.width / ctx.rig.base_w,
                  height=ctx.frame_h * 1.6 * ctx.rig.frame.width / ctx.rig.base_w, stroke_width=0,
                  fill_color=color, fill_opacity=1)
    return r.move_to(ctx.rig.frame.get_center())


def fade_through(ctx, color: str = "#060912", run_time: float = 0.5):
    """Fade to a solid colour (the next scene fades in from it)."""
    cover = ctx.rig.pin(_cover(ctx, color).set_opacity(0), canonical=False)
    ctx.scene.add(cover)
    ctx.scene.play(cover.animate.set_opacity(1), run_time=run_time)
    return cover


def fade_from(ctx, cover, run_time: float = 0.5):
    ctx.scene.play(cover.animate.set_opacity(0), run_time=run_time)
    ctx.scene.remove(cover)


def iris_out(ctx, color: str = "#060912", run_time: float = 0.6):
    """Circular iris closing from the edges toward the centre."""
    big = max(ctx.frame_w, ctx.frame_h) * 1.2
    cover = ctx.rig.pin(_cover(ctx, color).set_opacity(0), canonical=False)
    ctx.scene.add(cover)
    ctx.scene.play(cover.animate.set_opacity(1), run_time=run_time, rate_func=ease_in_out_cubic)
    return cover


def slide_wipe(ctx, color: str = "#2EC5FF", run_time: float = 0.5):
    """A colour bar sweeping across the frame left to right."""
    bar = Rectangle(width=ctx.frame_w * 0.35, height=ctx.frame_h * 1.4, stroke_width=0, fill_color=color,
                    fill_opacity=0.9)
    bar.move_to(ctx.rig.frame.get_center() + (-ctx.frame_w * 0.8, 0, 0))
    ctx.scene.add(bar)
    ctx.scene.play(bar.animate.shift((ctx.frame_w * 1.6, 0, 0)), run_time=run_time, rate_func=ease_in_out_cubic)
    ctx.scene.remove(bar)
