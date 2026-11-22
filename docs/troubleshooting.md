# Troubleshooting

## `pip install manim` fails: `RequiredDependencyException: pangocairo >= 1.30.0 is required`

Missing system packages. `sudo apt-get install libcairo2-dev libpango1.0-dev pkg-config
python3-dev` first (see `docs/installation.md`), then retry.

## `pip install manim` fails building `srt`: `AttributeError: install_layout`

This is Debian's patched `distutils` conflicting with `srt`'s old-style `setup.py` - happens on
**system** Python 3.13 on this repo's own dev container. Confirmed fix: install into a
virtualenv instead (`python3 -m venv .venv-explainer && source .venv-explainer/bin/activate`),
where the Debian patch doesn't apply. Do not try to patch `srt` or downgrade setuptools on
system Python; the venv is the actual fix.

## Hindi text renders as empty boxes ("tofu")

No Devanagari font is installed/found. Install `fonts-noto-extra` (Debian/Ubuntu) or your
distro's Noto Sans Devanagari package, then re-run the one-line check in
`docs/installation.md`'s "Hindi font rendering" section before trusting any Hindi render. Pango
(which Manim's `Text` uses) does correct glyph shaping once the font exists - this was tested
and confirmed, not assumed - so a tofu box means the font truly isn't present, not a code bug.

## `ffmpeg: Error opening input file picture_*.mp4`

Manim writes its output nested under `<work>/media/videos/<resolution>/picture_*.mp4`, not
directly in `<work>/`. `ffmpeg_renderer.burn_subtitles()`/`mux_final()` already resolve the
actual path returned by `scene.renderer.file_writer.movie_file_path` rather than guessing a
flat filename - if you see this error from custom code calling Manim directly, use that
attribute rather than assuming the output sits next to your working directory.

## Subtitles filter errors on an absolute path containing specific characters

FFmpeg's `subtitles=` filter parses colons in its argument as option separators. This repo's
`burn_subtitles()` works around it by passing the `.ass` path relative to FFmpeg's `cwd`
(`work`), never an absolute path, specifically to avoid this. If you call the `subtitles` filter
directly elsewhere, do the same.

## A render looks right but total duration doesn't match the storyboard exactly

**Known limitation** (see the implementation report): the current renderer's per-scene "hold"
time (`diagram_builder.reveal_time()`) accounts for element-reveal animations, but camera moves
and the between-scene transition itself (`camera_controller`/`transition_engine`) take real
wall-clock time on top of a scene's nominal `start`/`end` window. A storyboard scheduled for
exactly 50s can render a few seconds longer. This does not break anything - `quality_engine`
checks against a window (`duration_seconds ± 10` in the CLI/workflow), not an exact number -
but if you need frame-exact timing, reduce transition/camera animation `run_time`s in
`camera_controller.py`/`transition_engine.py` or build the per-scene "hold" calculation to
subtract those durations too.

## GitHub Actions: render step times out

`render-explainer.yml`'s job timeout is 90 minutes. A `high`-quality multi-scene Manim render
across two languages and two formats can be slow on a GitHub-hosted runner (no GPU). Use
`quality: draft` for CI smoke tests, and consider `parallel_jobs` in `production.yaml` only once
you've measured one real render's wall-clock time at your chosen quality - this hasn't been
benchmarked at `high` quality yet (see the implementation report's "known limitations").

## GitHub Actions: out of memory / killed

Not yet encountered in testing at `draft`/`medium` quality on a short (6-scene, ~50s) video, but
Manim's SVG/Cairo rendering is memory-hungry per frame at high resolution. If this happens,
lower `quality` first; GitHub-hosted runners are not a substitute for a self-hosted renderer if
daily volume grows toward the spec's full 5-topics/day scale (see `docs/configuration.md`).
