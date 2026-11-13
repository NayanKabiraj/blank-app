# Daily YouTube Shorts (English + Hindi)

The work is split into two parts:

- **Claude, as a scheduled task (every day at 08:23 IST),** does the thinking. It researches
  what's trending, checks past topics in `data/history.json`, picks today's niche and topic,
  and writes an English and a Hindi script. It then starts the GitHub workflow and passes it
  the plan. Its instructions are in [`CLAUDE_DAILY_TASK.md`](CLAUDE_DAILY_TASK.md): edit
  that file to change how it picks topics or writes scripts.
- **GitHub Actions** (`.github/workflows/daily-shorts.yml`) only produces the videos and
  publishes them:

1. **Checks the plan.** It validates the JSON plan it receives (`python -m shorts.plan validate`).
2. **Uses two scripts.** One in English and one in Hindi (Devanagari), each 6–9 scenes long
   and sized for 45–55 seconds of speech.
3. **Generates the voice-over** with [Piper](https://github.com/OHF-Voice/piper1-gpl), an
   open-source TTS that runs offline on the CPU (`en_US-lessac-medium`, `hi_IN-pratham-medium`).
4. **Creates the background music.** The music is synthesized with numpy for the video's
   mood, so it's original and safe from Content ID. You can also put your own royalty-free
   tracks in `assets/music/` or `assets/music/<mood>/`. The music is ducked under the voice.
5. **Builds the visuals.** It uses real footage for each scene. With a `PEXELS_API_KEY` it
   uses free vertical stock clips from Pexels. Without one it uses freely licensed
   videos from Wikimedia Commons, which need no key, and adds their authors and licenses
   to the video description. An animated gradient is used only when nothing matches.
6. **Edits the video with FFmpeg.** 1080×1920, 30 fps, captions burned in word by word,
   a hook title, loudness normalized to −14 LUFS, and a length kept between 40 and 59 seconds.
7. **Uploads both videos** with the YouTube Data API. They're marked as Shorts, and the AI
   voice is disclosed through `containsSyntheticMedia`.

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
| `PEXELS_API_KEY` | secret | Free key from <https://www.pexels.com/api/> for higher-quality vertical stock footage (without it, Wikimedia Commons is used) |
| `NICHE_HINT.txt` | file at the repo root | Steers Claude's research, e.g. `science, space, history, psychology` |
| `YT_PRIVACY` | variable | `public` (default), `unlisted` or `private` |
| `PIPER_VOICE_EN` / `PIPER_VOICE_HI` | variable | Any voice from <https://huggingface.co/rhasspy/piper-voices>, e.g. `hi_IN-priyamvada-medium` for a female Hindi voice |

## Running it
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
runs as a Claude task on your Claude plan. Pexels and the YouTube API are free.
(`shorts/research.py` is an optional alternative that calls the Claude API from inside the
workflow, but it isn't used by default.)
