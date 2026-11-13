# Daily YouTube Shorts (English + Hindi)

A GitHub Actions workflow (`.github/workflows/daily-shorts.yml`) that runs every day at
08:47 IST and:

1. **Researches today's niche.** Claude reads free trend feeds (Google Trends India + US),
   searches the web for what is trending, checks the channel's past topics in
   `data/history.json` so it doesn't repeat itself, and picks a niche, a topic and verified facts.
2. **Writes two scripts.** One in English and one in Hindi (Devanagari), each 6–9 scenes
   long and sized for 45–55 seconds of speech.
3. **Generates the voice-over** with [Piper](https://github.com/OHF-Voice/piper1-gpl), an
   open-source TTS that runs offline on the CPU (`en_US-lessac-medium`, `hi_IN-pratham-medium`).
4. **Creates the background music.** The music is synthesized with numpy for the video's
   mood, so it's original and safe from Content ID. You can also put your own royalty-free
   tracks in `assets/music/` or `assets/music/<mood>/`. The music is ducked under the voice.
5. **Builds the visuals.** It uses free vertical stock clips from Pexels for each scene,
   or animated gradient backgrounds when you don't set a Pexels key.
6. **Edits the video with FFmpeg.** 1080×1920, 30 fps, captions burned in word by word,
   a hook title, loudness normalized to −14 LUFS, and a length kept between 40 and 59 seconds.
7. **Uploads both videos** with the YouTube Data API. They're marked as Shorts, and the AI
   voice is disclosed through `containsSyntheticMedia`.

Each run also saves the MP4s as a workflow artifact for 14 days.

## One-time setup

### 1. Anthropic API key (research + scripts)
Create a key at <https://console.anthropic.com> and add it as the repository secret
`ANTHROPIC_API_KEY`.

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
| `PEXELS_API_KEY` | secret | Free key from <https://www.pexels.com/api/> for real stock footage (recommended) |
| `NICHE_HINT` | variable | Steer research, e.g. `science, space, history, psychology` |
| `YT_PRIVACY` | variable | `public` (default), `unlisted` or `private` |
| `CLAUDE_MODEL` | variable | Defaults to `claude-opus-5-5` |
| `PIPER_VOICE_EN` / `PIPER_VOICE_HI` | variable | Any voice from <https://huggingface.co/rhasspy/piper-voices>, e.g. `hi_IN-priyamvada-medium` for a female Hindi voice |

## Running it
- **Automatic:** daily at 03:17 UTC. To change the time, edit the `cron` line.
- **Manual:** go to Actions → *Daily YouTube Shorts* → *Run workflow*. Tick *dry run* to
  render without uploading, then download the videos from the run's artifacts.
- **Locally:**
  ```bash
  sudo apt install ffmpeg fonts-noto-core
  pip install -r shorts/requirements.txt
  python -m shorts.main --dry-run                                   # needs ANTHROPIC_API_KEY
  python -m shorts.main --plan-file shorts/sample_plan.json --dry-run  # no API key needed
  ```

## Cost
Everything except the research step is free and open source. The daily Claude call (web
research plus two scripts) usually costs a few cents. Pexels and the YouTube API are free.
