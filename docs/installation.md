# Installing the explainer engine

## Important: use a virtualenv, not system Python

On this repository's own dev container (Debian/Ubuntu, Python 3.13 system install), `pip
install manim` on system Python **fails** building its `srt` dependency, because `srt`'s
old-style `setup.py` hits an `AttributeError: install_layout` against Debian's patched
`distutils`. This is a `srt`/Debian-Python interaction bug, not a Manim problem - it does not
happen inside a clean virtualenv. **Always install into a venv.**

```bash
python3 -m venv .venv-explainer
source .venv-explainer/bin/activate
```

## System packages (apt, Debian/Ubuntu)

```bash
sudo apt-get update
sudo apt-get install -y \
  ffmpeg libcairo2-dev libpango1.0-dev pkg-config python3-dev \
  fonts-noto-core fonts-noto-extra
```

- `libcairo2-dev` + `libpango1.0-dev` + `pkg-config` + `python3-dev`: required to build Manim's
  Cairo/Pango text-rendering dependency. Confirmed: Manim fails to even install without these.
- `fonts-noto-core` / `fonts-noto-extra`: gives Manim's Pango-based text rendering both Latin
  and **Devanagari** glyphs (see "Hindi font rendering" below). On non-Debian distros, the
  package may just be `fonts-noto`.
- On Fedora/RHEL: `cairo-devel pango-devel pkgconf-pkg-config python3-devel`.
- On macOS (Homebrew): `brew install ffmpeg cairo pango pkg-config`.

## Python packages

```bash
pip install -r src/explainer/requirements.txt
pip install -r shorts/requirements.txt   # only needed for the TTS adapter (audio_engine/tts_engine.py)
```

Confirmed working in this environment: Python 3.13 (venv), `manim==0.22.1`.

## Hindi font rendering - verified, not assumed

Per this engine's own rule (never assume Hindi renders correctly without testing it), this was
actually tested: `manim.Text("चंद्रमा दूर जा रहा है", font="Noto Sans Devanagari")` renders with
correct conjuncts and matras via Pango, confirmed by extracting a frame and inspecting it. If
your system has no Devanagari font installed, Hindi text will render as empty boxes ("tofu") -
install `fonts-noto-extra` (or your distro's Devanagari font package) and re-test with the same
one-line check before trusting a Hindi render.

## Running

```bash
export PYTHONPATH=src
python -m explainer.cli validate-manifest content/manifests/sample_topic_001.json
SHORTS_FAKE_TTS=1 python -m explainer.cli demo        # no network, no paid service
python -m explainer.cli render --topic-id sample_topic_001 --lang en --format vertical
pytest tests/explainer/ -q                             # most tests need no Manim install at all
```

`SHORTS_FAKE_TTS=1` makes `shorts/tts.py` (the narration backend) generate placeholder tones
instead of calling Piper/Parler - useful for an offline smoke test of the rest of the pipeline.
Omit it for real narration (Piper downloads its voice model on first use, Parler needs `HF_TOKEN`).
