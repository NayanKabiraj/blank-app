"""Time-driven visibility: every mobject of a plan scene is created once and then faded/popped by an updater that
reads the scene clock, so no play ever changes an object's structure (Manim caches the moving-mobject list at the
start of each play, which breaks objects that are rebuilt mid-play)."""
from __future__ import annotations

from manim import VMobject


def _clamp(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def show(ctx, m, t_in: float = 0.0, dur: float = 0.28, pop: float = 0.1, z: int = 3, fade_out: bool = True, t_out=None):
    """Add `m` to the scene and fade it in at `t_in` seconds into the scene (and out at the scene's end)."""
    base = [(s, s.get_fill_opacity(), s.get_stroke_opacity()) for s in m.get_family() if isinstance(s, VMobject)]
    centre = m.get_center().copy()
    state = {"k": 1.0}
    if t_out is None:
        t_out = ctx.duration - 0.2 if (fade_out and not ctx.is_last) else None

    def update(_m):
        t = ctx.elapsed()
        a = _clamp((t - t_in) / dur)
        if t_out is not None:
            a *= 1.0 - _clamp((t - t_out) / 0.2)
        for s, fo, so in base:
            s.set_fill(opacity=fo * a, family=False)
            s.set_stroke(opacity=so * a, family=False)
        if pop:
            k = (1 - pop) + pop * _clamp((t - t_in) / dur)
            if abs(k - state["k"]) > 1e-4:
                m.scale(k / state["k"], about_point=centre)
                state["k"] = k
    update(m)
    m.add_updater(update)
    m.set_z_index(z)
    ctx.scene.add(m)
    ctx.objects.append(m)
    return m


def level(ctx, t_start: float, dur: float = 0.3) -> float:
    """0 -> 1 progress of something that starts at t_start (scene seconds)."""
    return _clamp((ctx.elapsed() - t_start) / dur)


def slots(ctx, n: int, lead: float = 0.35, share: float = 0.78) -> list[float]:
    """n reveal times spread across the narration of the scene."""
    pad = ctx.config.get("pad_before", 0.3)
    span = max(0.8, ctx.config.get("narration_seconds", ctx.duration - 1.0) * share)
    return [pad + lead + span * k / max(1, n) for k in range(max(1, n))]


def window(ctx, t_in: float, t_out=None, fade: float = 0.3):
    """alpha() callable (0..1) for dynamic objects: fades in at t_in and out at t_out (scene seconds)."""
    end = t_out if t_out is not None else (ctx.duration - 0.2 if not ctx.is_last else 1e9)

    def alpha():
        t = ctx.elapsed()
        return _clamp((t - t_in) / fade) * (1.0 - _clamp((t - end) / fade))
    return alpha
