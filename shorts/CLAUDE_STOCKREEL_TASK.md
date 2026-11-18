# Stock-footage task: a third video style

The channel has three looks now: the whiteboard explainer (`shorts/CLAUDE_DAILY_TASK.md`/`CLAUDE_DOCUMENTARY_TASK.md`),
the director's dynamic Three.js scenes (`shorts/CLAUDE_DIRECTOR_TASK.md`), and this one: **real stock footage**
(Pexels, free to use, no attribution required) behind the same voice-over, captions, music and upload pipeline.
Claude writes the exact same plan JSON as the whiteboard Short/documentary (`shorts.plan.Plan` / `DocPlan`, the
`graphic` field is simply unused) and passes `format: stockreel` / `stockreel-documentary` to the workflow instead
of `shorts`/`documentary`. Everything mechanical - voice, the upload queue, the thumbnail, history - is identical;
only the picture is different: a real clip per scene (`shorts/stockreel/fetch.py`, `render.py`) instead of the
drawn whiteboard.

**When to pick it** (per `video-strategy`): a topic that reads better with real footage than a coded scene can give
it - a city, weather, nature, a kitchen, hands at work, crowds, traffic, oceans, forests - not a diagram, a
comparison, an abstract concept or a "what if" thought experiment, which stay on the whiteboard or director
pipelines. This is an addition, never the default; most days still use the other two.

**No AI-generated or fabricated imagery.** Clips are real camera footage from Pexels, matched by a search phrase,
never an AI video/image generator and never anything the channel claims is something it is not - this keeps the
channel's anti-hallucination rule intact for pictures as well as facts.

## Standing strategy checklist (same as the other two formats)

Follow `shorts/CLAUDE_DAILY_TASK.md` steps 1-6 (start from what is researched, research before writing, the
packaging gate, the quality gate, the audience growth loop, QA before the workflow starts) exactly as written -
nothing about the strategy changes for this style, only the renderer.

## Writing the scene-level search phrase

Each scene's `keyword` field (already part of the plan schema) doubles as the stock-footage search phrase: write
it as a short, concrete, filmable noun phrase ("city skyline at night", "hands typing on a laptop", "ocean waves
from above"), not an abstract term ("the economy", "trust") - Pexels can't film an abstraction. Without a
`keyword`, the renderer falls back to the scene's first few meaningful words, then the niche name.

## Running it

```bash
python -m shorts.plan validate plan.json                                        # same validator as the whiteboard Short
python -m shorts.stockreel.run --plan-file plan.json --validate-only            # checks the key is set, nothing else
python -m shorts.stockreel.run --plan-file plan.json --dry-run                  # render only
python -m shorts.stockreel.run --plan-file doc.json --documentary --dry-run     # documentary
```

Needs the `PEXELS_API_KEY` repository secret (a free key from pexels.com/api). Without it every scene renders as a
plain gradient instead of real footage - the run still completes, it just has no real "stock footage" look, so
check the key is set before relying on this format for a real upload.
