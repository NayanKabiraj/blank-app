---
name: explainer-diagram
description: Plan, preview and extend the one and only look of the daily YouTube Shorts, the explainer. Dark navy, flat step-by-step diagrams (chains with flowing dots, races, stacks, loops, discs, bars), conversation scenes (chat bubbles, quiz, myth vs fact), one guiding spark carried between scenes, word-by-word headlines and rounded caption pills with the keyword lit, all drawn in code (shorts/explainer/scene.js). Use when writing a day's plan (graphic kind, items, values, answer and prop per scene), previewing or debugging the render, or adding scene kinds, icons or layouts.
---

# explainer: the channel's only look (drawn by code)

Flat, dark and explanatory, like the studio's "Why is the sky blue?" Shorts: nothing on screen is
decoration, every shape shows a step of the mechanism or a beat of the conversation. There is no
presenter and no photo. Older looks (cartoon 2D/3D, stickman, Manim motion graphics, stock footage)
were removed on purpose; do not bring them back.

- `shorts/explainer/scene.js`: a canvas scene, a pure function of time `t`. Poppins (Latin and
  Devanagari, SIL OFL) is bundled in `shorts/explainer/fonts/`, so the render needs no network.
- `shorts/explainer/scene.html`: the page and the word-by-word headline layer (HTML, so Devanagari
  is shaped correctly).
- `shorts/explainer/render.cjs` (Node + Playwright, headless Chromium, JPEG frames into FFmpeg);
  `shorts/animate.py` builds its config (scenes, keyword timing, caption chunks).
- Voice (Piper), music (synthesized) and the pop/bell sound effects are added by `shorts/compose.py`.
  `SFX=off` mutes the effects. Only the hook line is burned in by FFmpeg; all other captions are drawn
  by the scene as cream rounded pills with the scene's `keyword` lit in the accent colour.

## The look

- Background `#0b1524`, text `#f5f1e6`, secondary orange `#ff8a3c`, spark `#fff6d8`. The **accent colour
  follows the niche** (pink for Human Body, violet for Space, green for Money and India, mint for Nature,
  amber for History and Brain, blue otherwise). Orange is the contrast or the answer.
- **The guiding spark** (a glowing orb with turning rays) is carried from scene to scene: it glides to a
  new anchor each time and pulses on the keyword beat. It is the channel's recurring character.
- A faint backdrop motif changes every scene (nothing, dot grid, rings, diagonal lines).
- A short accent bar, then the headline rises word by word, then the diagram.
- The main beat of every scene lands about 3 frames before its `keyword`. Pop-ins use the measured
  overshoot table (up to +28 %), numbers stamp in.

## Writing a plan: pick the kind that acts out the line

| kind | what is drawn | needs |
|---|---|---|
| `title` | the `prop` icon pops in with burst lines. Hook and close | `headline`, `prop` |
| `keyword` | the `prop` icon in a turning dashed ring | `headline`, `caption`, `prop` |
| `stat` | the number counts up and stamps in (years do not count), ten dots fill. `caption` becomes the headline | `headline` = number + unit |
| `steps` | numbered discs down the screen, the active one lights in turn | 2-4 `items` |
| `flow` | the same chain, each node appears when named, dots flow along the connectors | 2-4 `items` |
| `build` | layers drop in and stack, the newest is lit | 2-4 `items` |
| `cycle` | states around a loop, a token travelling round | 3-4 `items` |
| `race` | two lanes, dots stream, counters show who arrived | 2 `items`, 2 positive `values` |
| `compare` | two discs whose **area follows `values`**, joined by an arc | 2 `items`, optional `values` |
| `bars` | horizontal bars grow to their values and count up | 2-4 `items`, same number of positive `values` |
| `chat` | a text-message exchange. Odd bubbles are the viewer (cream, left), even ones the answer (accent, right), typing dots before each reply | 2-4 `items` (up to 36 characters each) |
| `quiz` | the `headline` is the question, options A-D pop in, a countdown ring runs, then the right one lights green (on the `keyword` beat if it is late enough) | 2-4 `items`, `answer` = 0-based index |
| `myth` | the myth card is struck through, then the truth card stamps in | `items` = [myth, truth] |

- Headline at most 28 characters (quiz: 48; it wraps to two lines), caption at most 40, items at most 18
  (chat, myth and quiz options up to 36).
- `prop` icons: `star, bulb, coin, planet, globe, phone, bank, rocket, brain, chip, heart, clock, gear,
  atom, book, magnet, cloud`. Pick one that stands for the idea, different from the previous scene's.
- Use at least 4 different kinds per video and at least one of `chat`, `quiz`, `myth` (the validator checks).
- Prefer the diagram kinds for the mechanism: they show the process happening. Use `race`, `bars` or
  `compare` with real numbers for a countable difference, and `stat` for the single most striking number.
- Scripts are a **conversation**: see "Make it a conversation" in the `animated-explainer-method` skill.

## Landscape (documentaries)

The same scene renders 1920x1080 for the documentaries (`layout: landscape` in the config): the headline sits in
the left column (left-aligned, up to three lines), the spark top left, the diagram area is moved into the right-hand
panel, and the caption pill runs along the bottom. Every kind works unchanged. `shorts/documentary.py` and
`CLAUDE_DOCUMENTARY_TASK.md` cover the long-form pipeline (chapters, 5-15 minutes, 24 fps).

## Previewing

```bash
SHORTS_FAKE_TTS=1 python -m shorts.main --plan-file plan.json --langs en --dry-run --out /tmp/p
git checkout -- videos/ data/          # the dry run still saves a copy under videos/
ffmpeg -ss 12 -i /tmp/p/*_en.mp4 -frames:v 1 frame.png
```
(`SHORTS_FAKE_TTS=1` makes placeholder tones when the Piper voices cannot be downloaded.)

## Extending

- **New scene kind:** add a `draw...` function and a branch in `updateSegment`, register it in
  `DIAGRAM_OK` and `ANCHOR` (the spark's position), add it to `Graphic.kind`, `KINDS` and its check in
  `shorts/plan.py`, add its sound cue in `shorts/sfx.py` (`cues_from_timeline`), and document it here and in
  `shorts/CLAUDE_DAILY_TASK.md`.
- **New icon:** add a function to `PROPS` in `scene.js` and its name to `PROPS` in `plan.py`.
- **New niche accent:** add a pattern to `NICHE_ACCENT` in `scene.js`.
- Keep everything a function of `t`: no `Math.random()`, `Date` or CSS animation (frames are rendered in parallel).
