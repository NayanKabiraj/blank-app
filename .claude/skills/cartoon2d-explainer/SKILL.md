---
name: cartoon2d-explainer
description: Plan, preview and extend the cartoon2d style, the default look of the daily YouTube Shorts. It's a traditional 2D-animation explainer drawn entirely in code (shorts/cartoon2d/scene.js), with an original presenter character in full colour with warm brown outlines and cel shading, a painted background chosen by niche, and the subject shown in a round "thought bubble" inset. Use when writing a day's plan (graphic kind, prop and the presenter's pose per scene), previewing or debugging the render, or adding poses, props, backgrounds or layouts.
---

# cartoon2d: traditional-animation explainer (drawn by code)

The look follows a classic explainer-animation reference the channel owner chose: friendly
full-colour characters, ink outlines, flat shading, softly painted settings, and round inset
"bubbles" that show what the narrator is talking about. Everything is original and drawn by
code. There's no AI image or video generation, and no copied characters.

- `shorts/cartoon2d/scene.js`: the canvas scene.
  - **Presenter:** one recurring character (curly dark hair, blue shirt, brown trousers). The
    body is a rig (two-part arms and legs, torso, head) with 8 poses that blend smoothly,
    plus breathing, blinking, eyebrows, a big nose and expressions. **The mouth flaps while
    the narration plays.** The look is fixed in the `SKIN`, `HAIR`, `SHIRT`… constants, so
    the channel has one recognisable host.
  - **Backgrounds:** painted once per video by niche (`BACKDROP` map). There are five:
    `room` (study with a window and bookshelf: tech, AI, science, body, psychology), `town`
    (money, how it's made, engineering), `nature`, `space` and `classical` (history, with
    temple columns). Far layers are softened by shrinking and re-enlarging them (canvas blur
    filters are far too slow in software rendering), and clouds drift outdoors.
  - **Thought bubble:** the scene's `prop` pops into a round inset with a soft gradient and
    trailing dots from the presenter's head.
- `shorts/cartoon2d/scene.html`: the text layer: parchment cards with brown borders, niche
  pill and progress bar. Text is HTML so Devanagari is shaped correctly.
- Rendering reuses `shorts/cartoon3d/render.cjs`, and `shorts/cartoon.py` points it at this
  folder. It takes about 2 minutes per 30 s of video with 3 workers on 4 cores.
- Other styles are still available through the `visual_style` workflow input or the
  `VISUAL_STYLE` variable: `stickman`, `cartoon3d`, `motion` and `footage`.

## Writing a plan for this style

| kind | what is drawn | the presenter |
|---|---|---|
| `title` | the `prop` in a big bubble with burst lines (default `star`) | first scene: shocked, then points. Last scene: waves, then cheers. Otherwise points |
| `keyword` | the `prop` in a thought bubble linked to the head by dots (default `bulb`) | thinks (with a "?"), then points |
| `stat` | a stack of gold coins that grows while the number counts up, then sparkle lines | stands, then is shocked |
| `steps` | 2–4 round floor tiles; the active one turns the accent colour | hops from tile to tile as each step lights up in the card |
| `compare` | two classical columns that rise like bars (heights from `values`, equal if omitted) | points, then shrugs |

- `prop`: `star, bulb, coin, planet, globe, phone, bank, rocket, brain, chip, heart, clock,
  gear, atom, book, magnet, cloud`. Pick one that stands for the line, and don't use the
  same one in two scenes in a row.
- `pose` (optional): `stand, point, wave, cheer, shrug, think, shock, walk`. Use it to act out
  the line, for example `shock` on the reveal, `shrug` on "nobody knows", `cheer` on the payoff.
- Text limits: `headline` ≤ 24 characters, `caption` ≤ 40, items ≤ 18. The steps card is the
  tallest, so keep its headline short.
- `ai_prompt` is ignored in this style.
- Validate with `python -m shorts.plan validate plan.json`.

## Previewing

```bash
python - <<'EOF'
import json; p = json.load(open("shorts/sample_plan.json")); segs, t = [], 0
for sc in p["english"]["scenes"]: segs.append({"start": t, "end": t + 3.2, "graphic": sc["graphic"]}); t += 3.2
json.dump({"niche": p["niche"], "lang": "en", "total": t, "fps": 30, "segments": segs, "workers": 3,
           "root": "shorts/cartoon2d"}, open("/tmp/c2.json", "w"))   # add "backdrop": "town" to force one
EOF
(cd shorts/cartoon3d && npm ci && node render.cjs /tmp/c2.json /tmp/c2.mp4)
ffmpeg -ss 5 -i /tmp/c2.mp4 -frames:v 1 frame.png
```
For the full pipeline (voice, captions, music):
`python -m shorts.main --plan-file <plan> --langs en --dry-run --out /tmp/p`. Add
`SHORTS_FAKE_TTS=1` if the Piper voices can't be downloaded; the voice is then a
placeholder tone. Afterwards, restore `videos/` with `git checkout -- videos/`.

## Extending

- **Pose:** add to `POSES` in `scene.js` (radians: 0 = straight down, positive = screen
  right; `aL`/`aR`/`lL`/`lR` = `[upper, lower]`, plus `lean`, `tilt`, `face`) and to `POSES`
  in `shorts/plan.py`. Keep the stickman `POSES` list the same, since plans share the names.
- **Expression:** `face` values are handled in the face block of `drawPerson` (eyes, brows,
  mouth).
- **Prop:** add to `PROPS` (draw within ±100 px using `pen/circle/ellipse/rect/arcPts` and
  pass `p` through for the draw-on), and to `PROPS` in `plan.py`.
- **Background:** add a branch to `paintBackground` and map niche names to it in `BACKDROP`.
  Keep the floor line near y 1150 and the stage clear between the card (from 350 px, or
  470 px in the first scene so the hook text stays clear) and the caption band (about
  1290–1400 px). Characters stand at y 1255.
- Keep every frame a pure function of `t`. Don't use `ctx.filter` per frame (it's slow in
  software rendering): paint expensive things once in `setup`.
