# Writing the animation for a video (strict: Claude drives the animation, not only the story)

Every video plan names an `animation_pack` (same id in `english` and `hindi`). The pack is the folder
`generated_animations/scenes/<pack>/`:

```
shots.json            {"topic": "...", "shots": [{"module": "scene_001", "scenes": [0, 1]}, ...]}   # scene = index into plan scenes
scene_001.py ...      one module per shot, each with  def animate(ctx):
```

A shot covers one or more consecutive narration scenes and draws THE TOPIC'S OWN animation for them: an orbit, a signal
travelling, water rising, a graph being drawn as the Earth turns - never generic cards. Design the visual for what the
sentence says, then make it move. The renderer adds captions (per sentence) and the presenter; the shot code adds the
picture and may direct the presenter (look, point, gesture, expression).

## The shot API (`ctx`)
- `ctx.stage` -> `(centre, width, height)` of the free screen area (vertical Short or landscape documentary; position relative to it).
- `ctx.lang` ("en" / "hi"): every label comes from a `T = {"en": {...}, "hi": {...}}` dict; use `ctx.text(s, size, color, width)`.
- time: `ctx.t_of(i)` = start of narration scene i of the shot (seconds from shot start); `ctx.tt(i, k)` = start of sentence k of scene i;
  `ctx.config["subs"][i]` has text/start/end; `ctx.elapsed()`, `ctx.until(t)`, `ctx.play(...)`, `ctx.timeline.t` (global clock).
- `timed.show(ctx, mobject, t_in, t_out=None, pop=0.1, z=3)` adds an object that fades/pops in at `t_in` and out at `t_out`; `timed.level(ctx, t0, dur)` is a 0-1 progress;
  `timed.window(ctx, t_in, t_out)` is an alpha() for dynamic objects.
- dynamic objects: `always_redraw(...)` builders whose number of parts never changes (set `m._dynamic = True`), driven by `ctx.timeline.t`. Never create or delete
  parts while a play runs (Manim caches the moving list per play); animate opacity/position/angle instead.
- library: `shared/diagrams.py` (earth, satellite, phone, ...), `shared/orbital.py` (ocean Earth, Moon, Sun, live graph, boat, building), `shared/particles.py`
  (pulse rings, signal packets, sparkles), `shared/icons.py`, `shared/lighting.py`, `avatar/` gestures + expressions. Add new reusable pieces to `shared/`.

## Workflow (Mode A, per video)
1. Write the plan, then the pack. Every plan scene index must be covered by a shot (the validator checks `animation_pack`).
2. `python -m generated_animations scan <pack>` (safety scan: allow-listed imports, no shell/network/file/secret access).
3. Render a low-res preview and LOOK at the frames (contact sheet): `SHORTS_FAKE_TTS=1 GA_PIXEL_SCALE=0.4` with `shorts.compose.build(...)`;
   fix overlaps, clipping, dead moments (a held picture longer than ~4 s needs motion), unreadable text; re-render.
4. Interactive sessions put a pack into the repository through a branch and pull request. Scheduled daily runs commit their new pack folder (only that folder) straight to
   `main` before dispatching the workflow (CLAUDE.md rule 7, owner-authorised). Scenes without a shot fall back to generic cards, which is a fallback only, not acceptable for production.
