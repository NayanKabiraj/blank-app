# Stock-footage task: a third video style

The channel has three looks now: the whiteboard explainer (`shorts/CLAUDE_DAILY_TASK.md`/`CLAUDE_DOCUMENTARY_TASK.md`),
the director's dynamic Three.js scenes (`shorts/CLAUDE_DIRECTOR_TASK.md`), and this one: **real stock footage**
(Wikimedia Commons, public domain/CC0 only, no API key, no signup - the same source already used for thumbnails,
animated with a slow Ken Burns pan/zoom) behind the same voice-over, captions, music and upload pipeline.
Claude writes the exact same plan JSON as the whiteboard Short/documentary (`shorts.plan.Plan` / `DocPlan`, the
`graphic` field is simply unused) and passes `format: stockreel` / `stockreel-documentary` to the workflow instead
of `shorts`/`documentary`. Everything mechanical - voice, the upload queue, the thumbnail, history - is identical;
only the picture is different: a real clip per scene (`shorts/stockreel/fetch.py`, `render.py`) instead of the
drawn whiteboard.

**When to pick it** (per `video-strategy`): a topic that reads better with real footage than a coded scene can give
it - a city, weather, nature, a kitchen, hands at work, crowds, traffic, oceans, forests - not a diagram, a
comparison, an abstract concept or a "what if" thought experiment, which stay on the whiteboard or director
pipelines. This is an addition, never the default; most days still use the other two.

**The picture source, in order** (`shorts/stockreel/fetch.py` -> `aiframes.py`): an AI-generated image if a source is
configured - the local diffusion model first (only with the repo variable `IMAGEENGINE=local` - a small model run
on the runner's own CPU), then Pollinations, then Hugging Face's free Inference API - else a real Wikimedia
Commons public-domain/CC0 photo, else a plain gradient. None of this needs a key to run at all: with nothing
configured it is exactly the free, no-signup Wikimedia path.
**Any video that used even one AI-generated image is uploaded with YouTube's "altered or synthetic content" label
set automatically** (regardless of the channel-wide `YT_AI_DISCLOSURE` setting) - this is handled in code
(`shorts.stockreel.build`/`run` thread a `used_ai` flag through to `pending.publish`/`upload.upload`), not something
to remember per video. Never claim or imply an AI-generated image is real footage in a title, description or
narration - the anti-hallucination rule covers pictures exactly like it covers facts.

## Standing strategy checklist (same as the other two formats)

Follow `shorts/CLAUDE_DAILY_TASK.md` steps 1-6 (start from what is researched, research before writing, the
packaging gate, the quality gate, the audience growth loop, QA before the workflow starts) exactly as written -
nothing about the strategy changes for this style, only the renderer.

## Writing the scene-level search phrase

Each scene's `keyword` field (already part of the plan schema) doubles as the stock-footage search phrase: write
it as a short, concrete, photographable noun phrase ("city skyline at night", "hands typing on a laptop", "ocean
waves from above"), not an abstract term ("the economy", "trust") - there's no photo of an abstraction. Without a
`keyword`, the renderer falls back to the scene's first few meaningful words, then the niche name. Commons' free
public-domain/CC0 inventory is smaller than a commercial stock library, so a specific or recent subject may find
nothing; that scene then gets a plain gradient instead (never a broken render) - prefer generic, commonly
photographed phrases over narrow or brand-specific ones.

## Running it

```bash
python -m shorts.plan validate plan.json                                        # same validator as the whiteboard Short
python -m shorts.stockreel.run --plan-file plan.json --validate-only            # checks the key is set, nothing else
python -m shorts.stockreel.run --plan-file plan.json --dry-run                  # render only
python -m shorts.stockreel.run --plan-file doc.json --documentary --dry-run     # documentary
```

No secret or signup is required for the base path (Wikimedia + gradient). Optional, to prefer an AI-generated
image per scene over a real photo: the repository variable `IMAGEENGINE` (named without an underscore - this
repo's variable names can't take one) set to `local` installs and runs a small model (`stabilityai/sd-turbo`)
on the CPU runner itself - no key needed, but slow, so it is opt-in and tried *first* whenever it's set,
for both a still image and an animated (crossfaded) clip; `POLLINATIONS_API_KEY` and/or `HF_TOKEN` (the same
free Hugging Face token already used for Indic Parler-TTS) as repository secrets are the fallback, tried in
that order, whether or not the local model is on. A scene whose search/generation finds nothing at any
configured source renders as a plain gradient instead - the run still completes, it just has no real "stock
footage" look for that scene.
