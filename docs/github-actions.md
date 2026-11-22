# GitHub Actions for the explainer engine

Three workflows, all manually dispatched (`workflow_dispatch`) - none run on a schedule by
default, and none are wired into the existing `daily-shorts.yml` pipeline.

## `daily-research-prep.yml`

Validates that a topic's manifest, research record and storyboards (already committed by an
interactive research session - see `docs/production-guide.md`) are present and internally
consistent, and reports how the requested `topics_per_day` compares to `production.yaml`'s
configured cadence. It does **not** generate topics itself (no LLM/search credentials are
configured for this - see `docs/architecture.md`).

Inputs: `topic_id` (required), `topics_per_day` (informational), `dry_run` (default `true`).

## `render-explainer.yml`

Renders one topic across the languages/formats you ask for, from already-committed content.

Inputs: `topic_id` (required), `langs` (default `en,hi`), `formats` (default `vertical`),
`quality` (`draft`/`medium`/`high`), `dry_run` (validate only, default `false`).

Installs the system packages from `docs/installation.md`, then `src/explainer/requirements.txt`
and `shorts/requirements.txt` (for the TTS adapter only), validates the manifest, renders every
requested `(lang, format)` pair, and uploads `generated/videos/<topic_id>/*` plus the quality
reports as a workflow artifact - it never uploads to YouTube or any other service.

Set the repository variable `EXPLAINER_FAKE_TTS=1` to render with placeholder narration
(`SHORTS_FAKE_TTS=1`) for a fast, networkless CI smoke test instead of real Piper narration.

## `validate-video.yml`

Downloads or reads an already-rendered video and runs `quality_engine`'s checks against it
independently of a render run (useful for re-checking an artifact, or a video produced outside
CI). Writes `generated/reports/<topic_id>_<lang>_<format>_validate.json`.

## Triggering manually

GitHub UI: **Actions → (workflow name) → Run workflow**, fill in the inputs, run.

CLI (`gh`):
```bash
gh workflow run render-explainer.yml -f topic_id=sample_topic_001 -f langs=en -f formats=vertical -f quality=draft
```

## Downloading artifacts

GitHub UI: open the completed run → **Artifacts** section at the bottom → download the zip.
CLI: `gh run download <run-id>`.

## Inspecting a failure

Open the run, expand the failed step - `validate-manifest` failures print every schema/fact-
check problem found; a render failure's FFmpeg/Manim output is in the `render` step's own log.
`docs/troubleshooting.md` covers the specific errors you're most likely to hit.

## Secrets and variables this engine needs

None of its own. `shorts/tts.py` (used for narration) reads the same secrets/variables the
existing pipeline already documents (`HF_TOKEN` for Parler, `PIPER_VOICE_EN`/`PIPER_VOICE_HI`) -
see the existing `daily-shorts.yml` for those. No new secret is introduced by this engine.
