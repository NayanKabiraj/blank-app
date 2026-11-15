---
name: explainer-diagram
description: Plan, preview and extend the explainer diagram style, the default look of the daily YouTube Shorts. Dark navy, flat step-by-step diagrams (numbered chains with flowing dots, races, stacking layers, loops, size-scaled discs), one guiding spark carried between scenes, word-by-word headlines and rounded caption pills with the keyword lit, all drawn in code (shorts/explainer/scene.js). Use when writing a day's plan (graphic kind, items, values and prop per scene), previewing or debugging the render, or adding diagram kinds, icons or layouts.
---

# explainer diagram: the default look (drawn by code)

Flat, dark and explanatory, like the studio's "Why is the sky blue?" Shorts: nothing on screen is
decoration, every shape shows a step of the mechanism. There is no presenter and no photo.

- `shorts/explainer/scene.js`: a canvas scene, a pure function of time `t`. Poppins (Latin and
  Devanagari, SIL OFL) is bundled in `shorts/explainer/fonts/`, so the render needs no network.
- `shorts/explainer/scene.html`: the page and the word-by-word headline layer (HTML, so Devanagari
  is shaped correctly).
- Rendering reuses `shorts/cartoon3d/render.cjs` (headless Chromium, JPEG frames into FFmpeg).
  `shorts/cartoon.py` points it at this folder and passes the caption chunks.
- Voice (Piper), music (synthesized) and the pop/bell sound effects are exactly as for the other
  styles. `SFX=off` mutes the effects. Only the hook line is burned in by FFmpeg; all other captions
  are drawn by the scene as cream rounded pills with the scene's `keyword` in blue.

## The look

- Background `#0b1524`, text `#f5f1e6`, accent blue `#3d9bff`, secondary orange `#ff8a3c`, spark `#fff6d8`.
  Colour always means the same thing: blue is the thing being explained, orange is the contrast or the answer.
- **The guiding spark** (a glowing orb with turning rays) is carried from scene to scene: it glides to a
  new anchor each time (top right for most kinds, above the discs in `compare`, the middle of the loop in
  `cycle`) and pulses on the keyword beat. It is the channel's recurring character.
- A short accent bar, then the headline rises word by word (a new word every 0.08 s), then the diagram.
- The main beat of every scene lands about 3 frames before its `keyword`: the spark pulses and the active
  shape pops. Pop-ins use the measured overshoot table (up to +28 %), numbers stamp in.

## Writing a plan for this style

| kind | what is drawn |
|---|---|
| `title` | the `prop` icon pops in with burst lines (default `star`). Use for the hook and the close |
| `keyword` | the `prop` icon inside a slowly turning dashed ring (default `bulb`). Use for a new term |
| `stat` | the number counts up and stamps in (years do not count), the unit under it, ten dots fill up. `caption` becomes the headline |
| `steps` | 2-4 numbered discs down the screen; all labels visible, the active one lights up in turn |
| `flow` | the same chain, but each node appears when it is named and dots flow along the connectors |
| `race` | exactly 2 labels and 2 positive `values` (relative speeds): dots stream along two lanes and counters show how many arrived |
| `build` | 2-4 layers drop in and stack; the newest is lit |
| `cycle` | 3-4 states around a loop, the spark in the middle, a token travelling round |
| `compare` | exactly 2 labels; two discs whose **area follows `values`** (equal if omitted), joined by an arc |

- Headline at most 24 characters (it wraps to two lines), caption at most 40, items at most 18.
- `prop` icons: `star, bulb, coin, planet, globe, phone, bank, rocket, brain, chip, heart, clock, gear,
  atom, book, magnet, cloud`. Pick one that stands for the idea, different from the previous scene's.
- `pose` and `visual_query` are not used by this style.
- Prefer the diagram kinds for the mechanism: they show the process happening. Use `race` or `compare`
  with real numbers for a countable difference, and `stat` for the single most striking number.

## Previewing

```bash
python - <<'EOF'
import json; from pathlib import Path
from shorts.plan import Plan; from shorts import cartoon
p = Plan(**json.load(open("plan.json"))); sc = p.english
tl, t = [], 0.6
for s in sc.scenes: d = len(s.text.split()) / 2.5; tl.append((t, t + d, s.text)); t += d + 0.35
Path("/tmp/ex").mkdir(exist_ok=True)
cartoon.render(sc, "en", p.niche, tl, t + 0.8, Path("/tmp/ex"), "explainer")   # writes /tmp/ex/video.mp4
EOF
ffmpeg -ss 10 -i /tmp/ex/video.mp4 -frames:v 1 frame.png
```
For the full pipeline: `SHORTS_FAKE_TTS=1 python -m shorts.main --plan-file plan.json --langs en --dry-run --out /tmp/p`
(then `git checkout -- videos/`).

## Extending

- **New diagram kind:** add a `draw...` function and a branch in `updateSegment`, register it in
  `DIAGRAM_OK` and `ANCHOR` (the spark's position), add it to `Graphic.kind` and its check in
  `shorts/plan.py`, and document it here and in `shorts/CLAUDE_DAILY_TASK.md`.
- **New icon:** add a function to `PROPS` (inherited from the cartoon scene) and its name to `PROPS` in `plan.py`.
- Keep everything a function of `t`: no `Math.random()`, `Date` or CSS animation.
