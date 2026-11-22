# Architecture: the sketch/cinematic explainer engine

`src/explainer/` is a second, independent video-production engine living alongside the
existing `shorts/` whiteboard/cinematic/stockreel/director pipeline. It does not replace,
modify or depend on `shorts/` for rendering - the only place it reuses `shorts/` code is
`audio_engine/tts_engine.py`, which wraps `shorts/tts.py` (Piper/Parler) rather than
reimplementing narration from scratch (see "What's reused" below).

## Pipeline

```
Research (interactive)  →  Script (EN + HI)  →  Storyboard (EN + HI)  →  Manifest
        ↓                                                                    ↓
content/research/*.json   content/scripts/<id>/*.md   content/storyboards/<id>/*.json
                                                                              ↓
                                                            video_engine.compose()
                                                                              ↓
                              Manim render (picture) → TTS narration → subtitles
                                        → burn subtitles → mux audio → quality_engine
                                                                              ↓
                                          generated/videos/<id>/<lang>_<format>.mp4
                                          generated/reports/<id>_<lang>_<format>.json
```

## Why research is interactive, not automated

GitHub Actions has no LLM or search credentials configured for this engine (and the spec it
implements says not to assume otherwise). Every video in the existing `shorts/` pipeline is
already researched this way - a Claude session does real web search, writes the result as a
plan/manifest, and a workflow only renders it. `src/explainer/research_engine/` keeps that
same division: `topic_discovery.py` and `source_validator.py`/`fact_checker.py` are
bookkeeping and validation, not a research API client. `web_research.py`'s
`ManualResearchProvider` is where an interactive session's findings get shaped into the
schema; a future automated provider could implement the same `ResearchProvider` protocol
without anything downstream changing.

## One continuous Manim render, not clip-and-concatenate

`shorts/cinematic_engine` (the existing pipeline's own cinematic renderer) encodes each scene
as a separate clip and stitches them with FFmpeg's `xfade`. This engine does it differently:
one Manim `Scene` subclass (`animation_engine/sketch_renderer.py:SketchRenderScene`) loops over
every storyboard scene inside a single `construct()`, so camera moves, element reveals and
transitions all happen on Manim's own timeline in one pass. No external concatenation step,
and no risk of audio/video drift between clips.

## Why three "renderer" files share one implementation

The spec's file tree lists `whiteboard_renderer.py`, `colourful_renderer.py` and
`cinematic_renderer.py` as separate files. They exist as separate files (so grep/imports match
the spec and future contributors can find "the whiteboard one"), but each is one line:
`sketch_renderer.style_scene_class("whiteboard")` etc. The actual drawing/camera/transition
logic lives once, in `sketch_renderer.py` + `diagram_builder.py` + `camera_controller.py` +
`transition_engine.py` - a style is just a `Palette` (background, ink, accent colours, paper
texture on/off). Adding a fourth style later means adding one `Palette` entry and one
one-line file, not a fourth animation implementation.

## Layout adapts to aspect ratio, not crop-after-the-fact

`diagram_builder._positions_for()` reads Manim's live `config.frame_width`/`frame_height`
(set by `video_engine/ffmpeg_renderer.py` before the scene is constructed) and places elements
as *fractions* of the actual frame, not fixed coordinate offsets. The same storyboard therefore
lays out correctly for both vertical (9:16, narrow) and landscape (16:9, wide) without cropping
the vertical version's edges off or leaving the landscape version crowded in the middle.

## What's reused from the existing repo

| Need | Reused from `shorts/` | Why |
|---|---|---|
| Narration (TTS) | `shorts/tts.py` via `audio_engine/tts_engine.py` | Piper + Indic Parler-TTS already proven in production, EN+HI, cached, no hardcoded paid provider |

Everything else - schemas, storyboard planning, the animation engine, subtitles, video
composition, quality checks, CLI, workflows - is new, standalone code under `src/explainer/`,
per the owner's explicit decision to build the full parallel system rather than extend
`shorts/cinematic_engine` directly (see the implementation report for that discussion).

## Module map

See the repository tree for the full list; each package's own module docstrings explain its
role (`research_engine/`, `script_engine/`, `storyboard_engine/`, `animation_engine/`,
`audio_engine/`, `subtitle_engine/`, `video_engine/`, `quality_engine/`, `schemas/`, `config/`).
