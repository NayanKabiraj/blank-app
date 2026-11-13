---
name: cartoon-explainer
description: Plan, preview and extend the 3D cartoon explainer style of the daily YouTube Shorts (three.js toon scene rendered by code in shorts/cartoon3d/). Use when writing a day's plan (choosing each scene's graphic kind and 3D prop), when previewing or debugging the cartoon render, or when adding new props, scene layouts or mascot moves.
---

# 3D cartoon explainer videos (rendered by code)

The default visual style (`VISUAL_STYLE=cartoon3d`) draws every Short as a 3D cartoon,
entirely in code. There's no stock footage and no AI video in this style:

- `shorts/cartoon3d/scene.js`: three.js scene with toon shading and black outlines. It has a
  pastel sky, a round stage, drifting clouds, a coral **mascot** (bobs, blinks, waves, hops),
  **procedural props**, and per-scene layouts. Every frame is a pure function of time `t`.
- `shorts/cartoon3d/scene.html`: the HTML text layer (cartoon cards, niche pill, progress
  bar). Text is HTML, not 3D, so Devanagari is shaped correctly.
- `shorts/cartoon3d/render.cjs`: serves the folder locally, drives the scene frame by frame
  in headless Chromium (software WebGL, no GPU), with 3 browsers in parallel, and pipes JPEGs
  into FFmpeg. About 5 minutes per 50-second Short on a 4-core GitHub runner.
- `shorts/cartoon.py`: builds the scene timeline from the narration and calls the renderer.
  Voice, music, captions and upload are unchanged (`compose.py`).
- three.js r170 is vendored in `shorts/cartoon3d/vendor/` (MIT). Playwright comes from
  `shorts/cartoon3d/package.json`.

## Writing a plan for this style

Each scene's `graphic` decides the layout. Text goes in the video's language:

| kind | 3D stage | card |
|---|---|---|
| `title` | the `prop`, spinning and bobbing (default `star`) | big headline + caption |
| `keyword` | the `prop` on a pedestal with an orbit ring (default `bulb`) | key term in accent colour + caption |
| `stat` | a stack of gold coins that grows as the number counts up | big number (years don't count up) + unit + caption |
| `steps` | 2–4 pads; the mascot hops onto each pad as its step lights up | headline + step list, active step highlighted |
| `compare` | two pillars rising, with heights from `values` (equal if omitted) | headline + two coloured labels |

`prop` (title, keyword and stat scenes) is one of: `star, bulb, coin, planet, globe, phone,
bank, rocket, brain, chip, heart, clock, gear, atom, book, magnet, cloud`. Pick the one
that best stands for the scene's idea: `bank` for banks or money, `chip` for computers or AI,
`brain` for psychology, `planet` or `rocket` for space, `clock` for time, `heart` for the
body, `atom` for physics or chemistry, `gear` for machines, `globe` for the internet or Earth,
`book` for history or ideas. Don't use the same prop in two scenes in a row.

Rules of thumb:
- `headline` ≤ 24 characters, `caption` ≤ 40, step and compare items ≤ 18. Cards wrap,
  but shorter reads better on a phone.
- Use `steps` for the mechanism and `stat` for the one verified number. Use `compare` only
  when the two sides are clear opposites or before/after.
- `ai_prompt` is ignored in this style. You can still fill it in, because the `motion` and
  `footage` styles use it.
- Validate with `python -m shorts.plan validate plan.json`. It flags unknown props.

## Previewing a render locally

```bash
cd shorts/cartoon3d && npm ci && npx playwright install chromium   # once
cd ../.. && SHORTS_FAKE_TTS=1 VISUAL_STYLE=cartoon3d python -m shorts.main \
  --plan-file shorts/sample_plan.json --langs en --dry-run --out /tmp/preview
```
`SHORTS_FAKE_TTS=1` replaces the voice with a tone, so you can check the visuals without
downloading Piper voices. Pull frames with
`ffmpeg -ss 5 -i /tmp/preview/*_en.mp4 -frames:v 1 frame.png` and look at them. A dry run
also writes `videos/<date>/`, so restore those files afterwards (`git checkout -- videos/`).

## Extending the style

- **New prop:** add a builder to `PROPS` in `scene.js`. Build it from three.js primitives
  with `mesh(geometry, colour)`, about 2 units tall and centred on the origin. Add the same
  name to `PROPS` in `shorts/plan.py`.
- **New layout (kind):** add a branch in `buildSegment` (3D objects plus card DOM) and in
  `updateSegment` (animation driven by `t`). Add the kind to `Graphic.kind` in `plan.py`,
  and document it in this table and in `shorts/CLAUDE_DAILY_TASK.md`.
- Keep everything a function of `t`: no `Math.random()`, `Date` or CSS animations. The
  render is split across parallel browsers and must be identical in each.
- Keep the layout clear of the caption band (about 1290–1400 px from the top) and the
  hook text (about 260 px). The stage sits between the card and the captions. Check that
  the left and right edges aren't cropped (visible half-width at the stage is about 2 units).
- Performance: `CARTOON_GL_SCALE` (default 0.67) is the 3D layer's internal resolution,
  and `CARTOON_WORKERS` (default 3) is the number of parallel browsers. Shadows and outlines
  cost the most.
