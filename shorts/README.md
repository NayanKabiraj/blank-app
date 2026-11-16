# YouTube Shorts and documentaries (English + Hindi)

Two products come out of this repo, in the same explainer look, with the same voice and music:

- **Daily Shorts** (45-55 seconds, vertical): one in English and one in Hindi, every day.
- **Documentaries** (5-15 minutes, landscape 1920x1080): one in English and one in Hindi, with chapters,
  started by their own Claude task through the same workflow with `format: documentary` (see
  [`CLAUDE_DOCUMENTARY_TASK.md`](CLAUDE_DOCUMENTARY_TASK.md)). Chapter markers are added to the YouTube
  description automatically. Because the files are large they are kept as workflow artifacts (14 days)
  and uploaded to YouTube, not committed to the repo, unless you tick `keep_in_repo`.

The work is split into two parts:

- **Claude, as a scheduled task (every day at 08:23 IST),** does the thinking. The channel
  is an **explainer channel**: every Short answers one "how does X work?" or "why does X
  happen?" question. Claude hunts for the question with the best chance of going viral:
  it collects 10+ candidate questions across all of the 12 niches in
  [`niches.py`](niches.py) (this week's trends in India and worldwide, everyday mysteries,
  and what over-performs), scores each for curiosity gap, universality, timeliness,
  search demand, surprise, visual potential, shareability and safety, and picks the
  winner. The topic decides the niche, and a variety guard stops the same niche
  appearing twice in a row. It then researches how it works and writes an English and a
  Hindi script built for retention: a hook that starts on the surprising fact, a promise,
  a mechanism told in beats with a re-hook every 8-10 seconds, one striking number, an
  analogy, a payoff that reuses the hook's words and a looping close. The script is a **conversation**: it asks
  the viewer questions, answers them in a chat-bubble scene, challenges them with a quiz or a myth, and ends by
  asking a question for the comments. The plan's
  `research_summary` records the scored candidates. Claude then starts the GitHub workflow with the plan. Its instructions are in
  [`CLAUDE_DAILY_TASK.md`](CLAUDE_DAILY_TASK.md). To change the niches, edit `NICHES` in
  `niches.py`. To check which niche is next, run `python -m shorts.niches next`.
- **GitHub Actions** (`.github/workflows/daily-shorts.yml`) only produces the videos and
  publishes them:

1. **Checks the plan.** It validates the JSON plan it receives (`python -m shorts.plan validate`).
2. **Uses two scripts.** One in English and one in Hindi (Devanagari), each 6–9 scenes long
   and sized for 45–55 seconds of speech.
3. **Generates the voice-over** with [Indic Parler-TTS](https://huggingface.co/ai4bharat/indic-parler-tts)
   (AI4Bharat, Apache 2.0): an expressive neural voice that is steered by a text description, with the speakers
   **Thoma** (English) and **Rohit** (Hindi), animated for Shorts and measured for documentaries. The model is
   gated on Hugging Face, so it needs the `HF_TOKEN` secret (see below). Without it, or if the model cannot
   load, the whole run falls back to [Piper](https://github.com/OHF-Voice/piper1-gpl), a small offline CPU
   voice (`en_US-ryan-high`, `hi_IN-rohan-medium`).
4. **Creates the background music.** The music is synthesized with numpy for the video's
   mood, so it's original and safe from Content ID. You can also put your own royalty-free
   tracks in `assets/music/` or `assets/music/<mood>/`. The music is ducked under the voice.
5. **Builds the visuals in code.** Every video is a **whiteboard explainer** (`shorts/explainer/`, see the
   `explainer-diagram` skill): a white board where a hand draws the picture in marker while the voice explains it.
   Marker-drawn step-by-step diagrams that show the mechanism (numbered chains with flowing dots, races with arrival
   counters, stacking layers, loops, discs sized by their values, growing bars), **conversation scenes** (text-message
   chat bubbles with typing dots, a quiz with a countdown and a tick on the right answer, a myth struck out and the
   truth stamped in), a smiling sun carried from scene to scene, handwritten headlines, and caption pills with a
   yellow highlighter on the keyword. The accent colour follows the niche. It is rendered frame by frame in headless
   Chromium and encoded with FFmpeg. There is only this one look: the older cartoon, stickman, Manim, stock-footage
   and dark-diagram styles were removed.
6. **Edits the video with FFmpeg.** 1080×1920, 30 fps, captions burned in word by word,
   the hook line (drawn in the scene), loudness normalized to −14 LUFS, and a length kept between 40 and 59 seconds.
7. **Uploads both videos** with the YouTube Data API. They're marked as Shorts (the synthetic-media label is off by
   default, `YT_AI_DISCLOSURE=on` turns it on).

Each run also saves the MP4s as a workflow artifact for 14 days.

## One-time setup

### 1. Merge into `main`
GitHub can only start workflows that are on the default branch, and the scheduled Claude
task starts the workflow on `main`.

### 2. YouTube upload access
1. In <https://console.cloud.google.com>, create a project and enable **YouTube Data API v3**.
2. Set up the **OAuth consent screen** (External), add your Google account as a test user,
   and then **publish the app** ("In production"). Refresh tokens for apps left in
   *Testing* expire after 7 days.
3. Create **Credentials → OAuth client ID → Desktop app** and download the JSON file.
4. On your own computer, run:
   ```bash
   pip install google-auth-oauthlib
   python scripts/get_youtube_token.py client_secret.json
   ```
5. Add these repository secrets with the printed values: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`
   and `YT_REFRESH_TOKEN`.
   - If you want Hindi on a **separate channel**, run step 4 again and choose the Hindi
     channel, then save that token as `YT_REFRESH_TOKEN_HI`.

> **Important:** YouTube locks videos uploaded through an *unverified* API project to
> **private**. To publish publicly, request the free compliance audit:
> <https://support.google.com/youtube/contact/yt_api_form>. Until the audit is approved,
> you can publish the uploaded videos by hand in YouTube Studio.

### 3. Optional
| Name | Type | Purpose |
|---|---|---|
| `NICHE_HINT.txt` | file at the repo root | Overrides the topic and niche choice, e.g. `only How Tech Works and AI Explained this week` |
| `HF_TOKEN` | secret | **Needed for the Parler voices.** On huggingface.co: sign in (free), open <https://huggingface.co/ai4bharat/indic-parler-tts> and accept the terms, then create a *read* token at <https://huggingface.co/settings/tokens> and save it as the `HF_TOKEN` repository secret |
| `TTS_ENGINE` | variable | `parler` (default) or `piper` to force the small fallback voice |
| `PARLER_SPEAKER_EN` / `PARLER_SPEAKER_HI` | variable | Parler speaker names, default `Thoma` and `Rohit` |
| `SFX` | variable | `on` (default): code-synthesized pop and bell effects on the animation cues. `off` to mute them |
| `YT_AI_DISCLOSURE` | variable | `off` (default) or `on`: flag uploads with YouTube's "altered or synthetic content" label |
| `YT_PRIVACY` | variable | `public` (default), `unlisted` or `private` |
| `PIPER_VOICE_EN` / `PIPER_VOICE_HI` | variable | Any voice from <https://huggingface.co/rhasspy/piper-voices>, e.g. `hi_IN-priyamvada-medium` for a female Hindi voice |

## Running it
- **Documentary:** Actions → *Daily YouTube Shorts* → *Run workflow* with `format` = `documentary`. Paste a plan into
  `plan_json` (schema: `python -m shorts.plan doc-schema`) or leave it empty for `shorts/sample_documentary_plan.json`.
  Locally: `python -m shorts.documentary --plan-file shorts/sample_documentary_plan.json --dry-run`.
  Rendering runs at roughly 40 frames per second on a 4-core runner: a 10-minute video takes about
  6 minutes to draw per language, plus the voice and mix.
- **Automatic:** the scheduled Claude task runs daily and starts the workflow. You can
  see, pause or change it under scheduled tasks at claude.ai/code.
- **Manual:** go to Actions → *Daily YouTube Shorts* → *Run workflow*. Paste a plan into
  `plan_json`, or leave it empty to use the sample plan. Tick *dry run* to render without
  uploading, then download the videos from the run's artifacts.
- **Locally:**
  ```bash
  sudo apt install ffmpeg fonts-noto-core
  pip install -r shorts/requirements.txt
  python -m shorts.main --plan-file shorts/sample_plan.json --dry-run
  ```

## Cost
Rendering is free and open source, and runs on free GitHub Actions minutes. The research
runs as a Claude task on your Claude plan. The YouTube API is free.


## Director mode (Claude writes the scenes, the workflow renders them)

Besides the whiteboard template videos there is a second, fully dynamic engine. Claude acts as the **director**: it writes
one JSON manifest (story, narration per scene, scene types, camera moves, environments, objects and their behaviour,
on-screen text animations, sound cues, Hindi localization) and starts the workflow with `format: director` (Short) or
`format: director-documentary`, `manifest_json: <the JSON>`. GitHub Actions then voices the narration (same TTS as before),
rebuilds the timeline around the real speech, renders the scenes with Three.js in headless Chromium
(`shorts/director/engine/`), mixes voice, music and effects, and uploads (private by default).

- Instructions for the director: `shorts/CLAUDE_DIRECTOR_TASK.md` (manifest shape, registered presets, rules).
- Examples: `shorts/director/examples/ai_agents_short.json` (Short, EN + HI), `gps_documentary.json` (documentary, EN + HI).
- Check a manifest: `python -m shorts.director.run --manifest-file m.json --validate-only`; list presets: `python -m shorts.director.run schema`.
- Render locally (slow, software WebGL): `SHORTS_FAKE_TTS=1 python -m shorts.director.run --manifest-file m.json --langs en --dry-run`
  after `cd shorts/director && npm ci`.
- Tuning: `DIRECTOR_SCALE` (3D render scale, default 0.7 Shorts / 0.55 documentaries), `DIRECTOR_MSAA`, `RENDER_WORKERS`,
  `DIRECTOR_PREFLIGHT=off`.
