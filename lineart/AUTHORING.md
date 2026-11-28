# Line-art stories: authoring guide

Library: JDhruv14/line-art-animation (MIT, `LICENSE-line-art-animation`), copied into `lineart/lib/` (ink drawing, gait, motion, day/night palette). Skill with the full rules: `.claude/skills/line-art-animation/` (read `SKILL.md` and `references/style.md`, `motion.md`, `scenes.md`, `verify.md` before writing a new scene). What suits the format and why: `strategy/research/lineart-format.md`.

## One story = one plan + one scene
- Plan: the usual `Plan` JSON (see `strategy/prepared/2026-11-29-ash-lane-lineart.json`): niche `Line-art Stories`, english + hindi blocks, 7-10 scenes of 1-2 short sentences (60-110 English words in total; the closing line is added automatically), `animation_pack` = the scene id in BOTH blocks. Write the story with `.claude/skills/dopamine-storyteller` (hook, loop, reversal, payoff; record `Hooks:` and `Loops:` in `research_summary`). Invented stories are labelled "story"/"fiction"; no gore, no real people or brands.
- Scene: `lineart/scenes/<id>/index.html` + `story.ts`. START by copying `scenes/ash_lane/` and rewrite it: new place, character, props and action. Never reuse a finished story's scene with new words (YouTube's inauthentic-content rule; rule 10 says Claude authors the animation of every video).
- Timing: the scene reads `?cues=` (start second of each narration scene, plus the closing line), `?durs=` and `?total=` from the URL, so the picture follows the voice. Drive every event off `C[i]` / `D[i]`, never fixed seconds. The scene must run to `total` (the closing line plays over the last frame).
- 9:16 card, viewBox 300 x 533 in `ash_lane`; capture page flag `?capture` makes the card fill the screen; `?debug` makes time steppable.

## Checks before committing (Claude does these, nothing is "done" untested)
```bash
cd lineart && npm ci && npx tsc -p tsconfig.json --noEmit           # types
python3 -m shorts.lineart.run --plan-file plan.json --langs en,hi --validate-only
# look at the frames: run the dev server (npx vite --port 5199) and step it
node scripts/preview.mjs <scene_id> 7 14 22 30        # writes /tmp/lineart_preview/*.png at those seconds (cues default to the scene's own)
```
Inspect frames at the key beats (arrival, the action, the payoff, the end) for overlaps, clipping and dead moments in EN and HI timing; then commit ONLY the new `lineart/scenes/<id>/` folder (rule 7) and dispatch `daily-batch.yml` with `format` = `lineart`, `plans_json` = `[plan]`, `langs` = `en,hi`.

## Render path (workflow `daily-shorts.yml`, format `lineart`)
`python -m shorts.lineart.run` -> narration (edge-tts Andrew EN, Piper Hindi, strict) -> cues -> vite + headless Chromium capture at 1080x1920, 30 fps (about 7 minutes per language) -> ffmpeg -> burned captions -> ducked music -> thumbnail from the payoff frame -> upload queue (private) -> history (`engine: lineart`).

## Style rules that matter (from the skill)
One thin pen; limbs are two open strokes; feet planted (move by exactly gait speed x scale); clothes drawn around the skeleton; ink is `currentColor`, paper is `.pp`; interactions are the world reacting; the page behind the card never changes. Keep key action above the caption pill (bottom ~18 %).
