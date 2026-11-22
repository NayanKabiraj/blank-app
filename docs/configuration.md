# Configuring daily production

Everything about daily volume, languages, formats and style lives in
`src/explainer/config/production.yaml` - no source code change needed to adjust it.

```yaml
production:
  topics_per_day: 1        # owner's decision (22 Nov 2026): keep current cadence, not the
                            # spec's 5/day, until quota/cost is checked at this volume first
  duration_min: 45
  duration_max: 60
  languages: [en, hi]
  formats: [vertical]      # add "landscape" once it's been validated for this engine
  visual_style: cinematic  # whiteboard | colourful | cinematic
  render:
    enabled: true
    parallel_jobs: 1
    quality: medium         # draft (fast manim -ql-style preview) | medium | high
  publishing:
    enabled: false          # never auto-publish; see docs/production-guide.md
    approval_required: true
```

`topics_per_day x len(languages) x len(formats)` is how many render jobs one day's batch is.
At today's settings that's `1 x 2 x 1 = 2` jobs/day. The full spec's 5-topic/day, 2-language,
2-format scale would be `5 x 2 x 2 = 20` jobs/day - a real jump in both GitHub Actions minutes
and YouTube's daily upload quota (this repo's own `shorts/` pipeline has already hit that quota
with just 4 Shorts in one day). Raise `topics_per_day`/`formats` only after checking both at
the smaller volume first.

Read it in code:

```python
from explainer.config.settings import load_config
cfg = load_config()
print(cfg.jobs_per_day)
```

## Per-render overrides

`python -m explainer.cli render` takes `--quality` to override `render.quality` for one run
without editing the file (handy for a fast draft preview: `--quality draft`).

## Publishing stays separate and off

`production.yaml`'s `publishing.enabled` and a manifest's own `publishing.enabled` are both
`false` by default and are never flipped by anything in this engine. Rendering a video writes
an MP4 to `generated/videos/` and nothing else - no upload, no YouTube API call, no Metricool
call. See `docs/production-guide.md` for how a finished video actually gets published (a
separate, explicit, human-authorized step).
