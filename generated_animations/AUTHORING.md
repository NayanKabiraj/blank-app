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

## The intro scene (every video)
Plan scene 2 (index 1) is the intro: right after the hook the narrator says what the video covers and what the viewer will get
("In this video you'll see ..."). Give it its own shot: a visual roadmap - the 2-3 promised things appear as icons/mini-diagrams in step with each
mention (`ctx.tt(1, k)`), the presenter points at each in turn, then the picture hands over to the first real scene.

## The presenter
Pip is the owner's own 3D-style cartoon picture (bearded, glasses, hoodie) (`avatar/assets/pip_base.png`), animated by `avatar/face.py` + `controller.py`: lip-sync, blinks, sway, and leaning/tilting toward
whatever he looks at or points at. He is a bust (no arms), so `point_at`, `wave`, `present` and `shrug` act as body language (lean, sway, tilt, lift); direct attention with
`ctx.avatar.look_at(...)` and put the thing being pointed at in the picture itself (an arrow or a highlight). `avatar/assets/pip_speaking.gif` (transparent) shows the speaking animation.

## The vox look (default for every new pack since 23 Nov 2026)
Packs draw in the paper cut-out explainer style: `shots.json` has `"look": "vox"` (the plan validator requires it; `VIDEO_LOOK=classic` brings the dark space theme back). The renderer then
uses a warm paper background, cream caption pills with ink text and the presenter as a white-bordered sticker. Shots draw with `generated_animations/shared/vox.py`:
`vox.torn_card(w, h, seed, rot)` (torn paper card: put drawings on top), `vox.cutout(group)` (white border + shadow for any drawing, e.g. little people or buildings), `vox.marker(ctx, text_mob, t_in, dur)`
(yellow highlighter swipe behind a key word), `vox.tape(ctx, "LABEL", center, color)` (tape label / stamp), `vox.doodle_arrow(start, end, color)`, and the palette (`INK` for text, `YEL`, `BLUE`, `RED`, `GREEN`, `ORANGE`, `PINK`).
Rules of the look: text is `vox.INK` (dark) in BIG bold capitals for headlines and short labels; one marker swipe per key word; 3-6 torn cards or cut-outs per shot, slightly rotated (-4..+4 degrees);
colour fills with an ink outline (stroke_color=INK, stroke_width 3-6); things still move a lot (bars growing, fluids filling, hands turning, people popping in, arrows drawing), because rule 10 still applies.
Model pack: `scenes/time_flies_vox/` (a vertical Short). Keep everything inside the stage; the sticker presenter sits bottom-left.

### Newspaper clippings (vox look): when to use them
`vox.newspaper(ctx, masthead, headline, date, w, h, seed, rot)` builds a newspaper front-page clipping (newsprint card, serif masthead, rules, date line, big headline, hatched photo box, text columns) and
`vox.arrive(ctx, clipping, t_in, t_out, side="right")` slaps it into frame (slides in with a little spin and overshoot, and slides out at `t_out`). Position the clipping where it should end up first.
Decide per scene (do not use it everywhere; at most 1-3 times per Short, 2-6 per documentary, only where it helps the story):
- **Use it** when the sentence is about a **dated or historical event** ("in 1960 ...", "in 2005 a survey ..."), a **named incident or disaster**, an **announcement, discovery, record, law or study** being reported, a **first/last** of something,
  or anything that reads like a news item. Put the year or date in the date line and a headline that says the same thing as the narration.
- **Do not use it** for explanations of how something works, definitions, steps, comparisons, jokes, or anything without a real date or event.
- **Facts rule:** a clipping is a claim on screen. The headline and date must be supported by the research (Claims table); never invent a quote, an outlet or a statistic. Use a generic masthead (for example "The Curious Loop Times") instead of a real newspaper's name.
- **Timing:** arrive on the sentence that names the event, hold about 2 seconds, then let it leave before the next visual starts. Model: `scenes/time_flies_vox/scene_003.py` (the 2005 survey).

## Hindi (vox look in both languages)
A Hindi video uses the SAME vox look and normally the same pack as the English one (`hindi.animation_pack` = the pack id; the plan validator requires the vox look for each language and, for Hindi, that the pack
chooses its text by language). Write every on-screen string with `vox.L(ctx, "JUST GUESSING?", "सिर्फ़ अंदाज़ा?")` or a `T = {"en": {...}, "hi": {...}}` dict read as `T[ctx.lang]`; `ctx.text`, `vox.tape` and `vox.newspaper`
switch to the Devanagari font (Noto Sans Devanagari) for `hi`. Sentence indices (`ctx.tt`) stay the same because the Hindi plan has the same scenes; keep text short (Hindi runs ~20 % wider: widths in `ctx.text(..., width)` scale it down).


## Pack kit and preview (25 Nov 2026)
New packs start with `from generated_animations.shared.packkit import *` (Beat helpers, figure/phone/plane/recorder/flame/sea/sub, vox, level/show/window; do not copy `_kit.py` any more). Preview with
`python3 -m generated_animations.authoring.preview <plan.json> --lang en|hi [--doc]` and open the printed contact sheet once. See `shorts/DAILY_RUN.md` section 4.

## Vox style v2 (26 Nov 2026)

Measured easings, durations, borders, palette and pacing rules for the paper cut-out look: `generated_animations/VOX_STYLE_V2.md` and `shared/vox_style.py` (example pack `vox2_demo`). Use `vs.enter` for entrances, `vs.rim` for the yellow offset echo, one slow push-in per shot, one accent colour. Paid AI-video skills are NOT used (rule 10).

## Full-screen art (26 Nov 2026)
`shots.json` `"stage": "full"` + `b.backdrop(top, bottom, seed=n)` per beat (instead of `b.card`): a full-bleed gradient with stars behind everything, caption pill and presenter on top, and a taller art zone
(`b.C` = (0, 2.65), x +-4.4, local y -4.8..+4.8; keep key art above the caption). Example pack: `silent_space_vox`. Text on a dark backdrop is white; the cartoon character is `shared/cartoon.py`.
