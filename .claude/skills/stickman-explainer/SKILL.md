---
name: stickman-explainer
description: Plan, preview and extend the 2D stickman explainer style (VISUAL_STYLE=stickman; the default is now cartoon2d). A hand-drawn stick figure on white paper is drawn entirely in code (shorts/stickman/scene.js) and rendered frame by frame. Use when writing a day's plan (graphic kind, prop and the figure's pose per scene), previewing or debugging the stickman render, or adding poses, faces, doodle props or layouts.
---

# 2D stickman explainer videos (drawn by code)

`VISUAL_STYLE=stickman` (an alternative; the default is the `cartoon2d` style) draws every Short as a hand-drawn explainer, with no
stock footage, AI video or image generator:

- `shorts/stickman/scene.js`: a 2D canvas with off-white paper and black marker strokes that
  **boil** (redraw with a fresh wobble 8 times a second, like hand animation) and **draw on**
  stroke by stroke. It has one **stick figure** with a rig (head, torso, two-part arms and
  legs), 8 poses blended smoothly, blinking, and faces (smile, grin, flat, hmm, shock).
  There are **doodle props** with the same names as the 3D ones, and one accent colour per
  niche. Every frame is a pure function of time `t`.
- `shorts/stickman/scene.html`: the HTML text layer: niche pill, headline with a
  highlighter swipe, caption, step list, compare labels and progress bar. Text is HTML so
  Devanagari is shaped correctly.
- Rendering reuses `shorts/cartoon3d/render.cjs` (headless Chromium → JPEG frames →
  FFmpeg, 3 browsers in parallel). `shorts/cartoon.py` points it at `shorts/stickman/`.
  It takes about 3 minutes per 55-second Short on 4 cores, which is faster than the 3D style.
- Voice, music, captions and upload are unchanged (`compose.py`). Choose this style with the
  workflow input `visual_style: stickman` or the repo variable `VISUAL_STYLE`.

## Writing a plan for this style

| kind | what is drawn | the figure |
|---|---|---|
| `title` | the `prop` doodle draws on, bobs, with burst lines (default `star`) | first scene: shock, then points. Last scene: waves, then cheers. Otherwise points |
| `keyword` | the `prop` doodle, then an accent circle scribbled around it (default `bulb`) | thinks (with a "?"), then points |
| `stat` | a stack of coins that grows while the number counts up, then sparkle lines | stands, then is shocked |
| `steps` | 2–4 numbered pads with arrows; the active pad fills with the accent colour | hops from pad to pad as each step lights up in the list |
| `compare` | two hatched bars that grow (heights from `values`, equal if omitted) | points, then shrugs |

- `prop` (title/keyword/stat): `star, bulb, coin, planet, globe, phone, bank, rocket, brain,
  chip, heart, clock, gear, atom, book, magnet, cloud`. Pick one that stands for the line,
  and don't use the same one in two scenes in a row.
- `pose` (optional, any kind): `stand, point, wave, cheer, shrug, think, shock, walk`.
  It overrides the default acting for that scene. Use it to land a joke: `shrug` on
  "nobody knows why", `shock` on the big reveal, `cheer` on a win, `think` on a question.
- Text limits as usual: `headline` ≤ 24 characters, `caption` ≤ 40, items ≤ 18.
- The figure walks between its spots when the scene changes, so consecutive kinds with
  different layouts feel connected. Plan a mix of kinds.
- `ai_prompt` is ignored in this style.
- Validate with `python -m shorts.plan validate plan.json`. It flags unknown props and poses.

## Previewing

Render just the video track (no voice), which is fastest:
```bash
python - <<'EOF'
import json; p = json.load(open("shorts/sample_plan.json")); segs, t = [], 0
for sc in p["english"]["scenes"]: segs.append({"start": t, "end": t + 3.2, "graphic": sc["graphic"]}); t += 3.2
json.dump({"niche": p["niche"], "lang": "en", "total": t, "fps": 30, "segments": segs, "workers": 3,
           "root": "shorts/stickman"}, open("/tmp/sm.json", "w"))
EOF
(cd shorts/cartoon3d && npm ci && node render.cjs /tmp/sm.json /tmp/sm.mp4)
ffmpeg -ss 5 -i /tmp/sm.mp4 -frames:v 1 frame.png
```
For the full pipeline with captions and music:
`SHORTS_FAKE_TTS=1 python -m shorts.main --plan-file <plan> --langs en --dry-run --out /tmp/p`,
then restore `videos/` with `git checkout -- videos/`.

## Extending the style

- **New pose:** add an entry to `POSES` in `scene.js` (absolute angles in radians: 0 = straight
  down, positive = towards screen right; `aL`/`aR` arms and `lL`/`lR` legs as
  `[upper, lower]`; plus `lean`, `tilt` and `face`), and the same name to `POSES` in
  `shorts/plan.py`.
- **New face:** add a branch in the face section of `drawFigure`.
- **New doodle prop:** add a function to `PROPS` in `scene.js` that draws within about ±100 px
  using `pen`, `circle`, `ellipse`, `rect` and `arcPts`, and passes `p` through for the draw-on.
  Add the name to `PROPS` in `plan.py` too. The 3D style needs a matching prop, or it falls
  back to its default.
- **New layout:** add a branch in `buildSegment` (HTML card and data) and in `updateSegment`
  (drawing), then add the kind to `Graphic.kind` in `plan.py` and to this table.
- Rules: no `Math.random()`, `Date` or CSS animation (use `rnd()` and `T`). Keep drawings
  between the card (from 350 px, or 470 px in the first scene so the hook text stays clear)
  and the caption band (about 1290–1400 px). The ground line is at 1255 px.
