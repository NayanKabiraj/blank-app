# Production flow

```
Research → Fact-check → Script → Storyboard → Assets → Animation → Narration → Subtitles
    → Composition → Quality checks → Artifact
```

## 1. Research (interactive)

A session with real web search researches the topic, the same way every video in `shorts/`
already is. Record findings with `research_engine.topic_discovery.save_research_record()` and
`research_engine.web_research.ManualResearchProvider`, checking `is_duplicate()` first. Every
claim gets a status: `VERIFIED` / `PARTIALLY VERIFIED` / `UNVERIFIED` / `FICTIONAL ASSUMPTION` -
`research_engine.fact_checker.check_summary()` flags a summary that doesn't use any of these.

## 2. Fact-check

`research_engine.source_validator.validate_research()` - malformed/duplicate URLs, a
`verified`/`partially_verified` claim with no sources listed, an `unverified` claim with no
`uncertainties` text saying what's unconfirmed.

## 3. Script (EN + HI)

Write `ScriptLine`s (scene id, start/end, narration, a one-line visual description, sources)
and call `script_engine.english_generator.write()` / `hindi_generator.write()`. The Hindi writer
refuses to save if any line has no Devanagari text. `duration_controller.check_duration()` says
whether the word count lands the script in the configured 45-60s window.

## 4. Storyboard (EN + HI)

Turn each `ScriptLine` into a `PlannedLine` (adds a `template`: hook / explainer_diagram /
comparison / timeline / takeaway, plus an optional `focus_on` for the camera) and call
`storyboard_engine.scene_planner.build_scenes()` then `storyboard_generator.build_storyboard()`
+ `write_storyboard()`. This writes both the JSON the renderer reads and a human-readable `.md`.

## 5. Assets

Illustrations are either a file at `assets/explainer/illustrations/<name>.svg`, or (if that
file doesn't exist yet) a procedural placeholder shape generated on the fly - a storyboard
never fails to render for lack of a drawn asset. Add real illustrations by dropping an SVG at
that path with the matching element `name`; no code change needed for the renderer to pick it up.

## 6. Animation

`video_engine.ffmpeg_renderer.render_picture()` sets Manim's resolution/fps/output path and
renders the chosen style's `SketchRenderScene` subclass - progressive stroke drawing, camera
moves, per-scene transitions, all in one continuous pass (see `docs/architecture.md`).

## 7. Narration

`audio_engine.tts_engine.get_provider("piper")` wraps the existing `shorts/tts.py`.
`audio_engine.audio_mixer.synthesize_narration()` renders one WAV per scene and concatenates
them at each scene's own `start` time, so narration and picture agree on timing without extra
sync logic.

## 8. Subtitles

`subtitle_engine.subtitle_generator.cues_for_storyboard()` chunks each scene's narration into
short cues timed proportionally across the scene; `subtitle_formatter.write_srt()` /
`write_ass()` write both formats. `subtitle_validator.validate_cues()` checks timing, a
mobile-safe character limit, and (for Hindi) that every cue actually contains Devanagari.

## 9. Composition

`video_engine.ffmpeg_renderer.burn_subtitles()` then `mux_final()` - burns the ASS subtitles in,
muxes the narration in with AAC + loudness normalisation, writes the final MP4 via
`video_engine.export_manager.final_path()`.

## 10. Quality checks

`quality_engine.production_report.build_report()` runs `video_quality.check_video()` (duration,
resolution, fps, H.264/AAC, audio track present), `check_not_black()`, and
`content_quality.check_subtitles()`/`check_storyboard_timing()`, and writes
`generated/reports/<topic_id>_<lang>_<format>.json`.

## 11. Artifact

`render-explainer.yml` uploads `generated/videos/<topic_id>/*` and the report as a GitHub
Actions artifact. That is the end of this pipeline's job.

## Publishing is a separate, later, explicit step

Nothing in this pipeline uploads anywhere. `ProductionManifest.publishing` (`enabled`,
`requires_approval`) and `production.yaml`'s own `publishing` block describe intent for a
*future*, separate publishing adapter - today both default to `false`/`true` and nothing reads
them to take an action. If/when a real adapter is added (reusing `shorts/upload.py`'s YouTube
integration, or a new one), it should: require `publishing.enabled: true` AND a human
confirming `requires_approval`, generate title/description/tags/hashtags/a thumbnail brief from
the manifest's own content, and never be invoked automatically from `render-explainer.yml`.
