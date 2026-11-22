# Daily YouTube Shorts bot

A GitHub Actions workflow that is driven by a daily scheduled Claude task: Claude researches a niche and writes an English and a Hindi script, then GitHub Actions generates the voice-over, music and video with open-source tools. It then publishes both videos as YouTube Shorts (40–60 seconds each).

➡️ **Setup and usage: [shorts/README.md](shorts/README.md)**

(The original Streamlit template is still in `streamlit_app.py`.)

## Explainer engine (`src/explainer/`)

A second, independent video-production engine: research → English/Hindi script → storyboard →
a Manim-rendered sketch/cinematic animation (whiteboard, colourful, or cinematic style) →
narration → subtitles → a quality-checked MP4. It does not modify or depend on the `shorts/`
pipeline above (the only thing it reuses is `shorts/tts.py` for narration).

- **Purpose & features**: `docs/architecture.md`
- **Install** (Python + system packages + the venv you actually need for Manim):
  `docs/installation.md`
- **Run a no-network demo locally**:
  ```bash
  export PYTHONPATH=src
  SHORTS_FAKE_TTS=1 python -m explainer.cli demo
  ```
- **Render a manifest**: `python -m explainer.cli render --topic-id <id> --lang en --format vertical`
- **Run tests**: `pytest tests/explainer/ -q` (most pass with no Manim installed)
- **GitHub Actions**: `docs/github-actions.md` (`render-explainer.yml`, `validate-video.yml`,
  `daily-research-prep.yml` - all manual-dispatch, none wired into the existing `daily-shorts.yml`)
- **Daily volume, languages, formats, style**: `src/explainer/config/production.yaml`, explained
  in `docs/configuration.md`
- **Full production flow**: `docs/production-guide.md`
- **Troubleshooting**: `docs/troubleshooting.md`

Publishing stays disabled by default everywhere in this engine; rendering produces an MP4 in
`generated/videos/`, nothing more.
