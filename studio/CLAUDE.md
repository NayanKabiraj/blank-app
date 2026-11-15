# CLAUDE.md — Animated Explainer Video Studio

You are producing animated explainer videos for YouTube in this project.
Follow this file for every video. Everything used must be free and open source.

## 1. Stack (do not substitute paid tools)

| Job | Tool | Licence |
|---|---|---|
| Animation and rendering | HyperFrames (HTML/CSS/GSAP to MP4) | Apache 2.0 |
| Maths, graphs, algorithm scenes | Manim Community (only when a scene needs it) | MIT |
| Voiceover | Kokoro TTS (default), Chatterbox (if cloning the owner's voice) | Apache 2.0 / MIT |
| Captions | Whisper (openai-whisper) | MIT |
| Stitching, audio mix, encoding | FFmpeg | LGPL/GPL |
| Thumbnail | HTML page rendered to PNG, or Inkscape | — |

Never use ElevenLabs, stock-footage APIs, paid fonts, or any service needing an API key.
Fonts: Google Fonts (OFL) only. Icons: Lucide or Tabler (MIT). Music: only files the owner places in `assets/music/`.

## 2. One-time setup

Run these once, and skip any that are already installed:

```bash
node --version            # must be 22+
ffmpeg -version
npx skills add heygen-com/hyperframes
pip install kokoro soundfile openai-whisper
# Kokoro needs espeak-ng: apt install espeak-ng / brew install espeak-ng
# Optional, only for maths-heavy videos:
pip install manim
npx skills add affaan-m/ecc --skill manim-video --agent claude-code
```

The installed HyperFrames skill is the authority on HyperFrames syntax and CLI flags.
If anything here disagrees with the skill or with `npx hyperframes --help`, follow the skill.

## 3. Project layout

```
videos/<slug>/
  brief.md          # topic, audience, promise, length, language
  script.md         # scene-by-scene narration and visual notes
  audio/            # scene-01.wav ... and voiceover.wav
  composition/      # HyperFrames project (created by `npx hyperframes init`)
  captions/         # voiceover.srt
  out/              # final.mp4, short.mp4, thumbnail.png, youtube.md
brand/
  tokens.css        # colours, fonts, spacing, easing — shared by all videos
assets/music/       # owner-supplied tracks
```

## 4. Production pipeline (follow in order)

### Step 1 — Brief
If `brief.md` is missing, ask the owner for: topic, target viewer, the one thing
the viewer should understand by the end, target length, and language. Ask once, then proceed.

### Step 2 — Script (`script.md`)
- Total length: 60–180 seconds unless the brief says otherwise. About 150 words per minute.
- Structure:
  1. **Hook (0–8 s):** a surprising fact, question, or the end result. No greetings, no logo, no "in this video".
  2. **Setup (8–20 s):** why it matters to the viewer.
  3. **3–5 idea scenes:** one idea per scene, each 10–25 s.
  4. **Payoff:** answer the hook's question directly.
  5. **Outro (max 5 s):** one call to action.
- Write for the ear: short sentences, no brackets, spell out numbers and symbols.
- For each scene, write: narration, what is on screen, and what moves.
- Show `script.md` to the owner and wait for approval before generating audio.

### Step 3 — Voiceover (audio comes before animation)
Generate one WAV per scene with Kokoro, then measure each duration with `ffprobe`.

```python
from kokoro import KPipeline
import soundfile as sf, numpy as np
pipe = KPipeline(lang_code="a")   # "a" = American English, "h" = Hindi
chunks = [audio for _, _, audio in pipe(text, voice="af_heart")]
sf.write("audio/scene-01.wav", np.concatenate(chunks), 24000)
```

Scene duration = audio duration + 0.4 s of breathing room. Never guess timings.
Concatenate the scenes into `audio/voiceover.wav` with FFmpeg.

### Step 4 — Animation
- Create the project with `npx hyperframes init`, then work through the `/hyperframes` skill.
- Canvas: 1920×1080, 30 fps. One composition per scene so each can be fixed alone.
- Import `brand/tokens.css`. Never hard-code colours or fonts inside a scene.
- Sync every on-screen change to the word in the narration that it illustrates.
- For a maths or graph scene, render it in Manim to a transparent or matching-background
  clip and place that clip in the HyperFrames timeline.

### Step 5 — Check
Run these and fix every issue before rendering:

```bash
npx hyperframes lint
npx hyperframes inspect      # catches text running off screen
npx hyperframes preview
```

Then extract one frame per scene with FFmpeg and look at each image yourself.
Check for overlapping elements, clipped text, low contrast, and empty frames.

### Step 6 — Render and finish
1. Render the composition to MP4 (see `npx hyperframes render --help`).
2. Captions: `whisper audio/voiceover.wav --model small --output_format srt --output_dir captions`.
   Correct any names or technical terms against `script.md`.
3. If music exists, mix it 18–22 dB below the voice, with a 1 s fade in and out.
4. Normalise loudness to −14 LUFS: `ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 ...`
5. Encode: H.264, yuv420p, CRF 18, AAC 192k, `-movflags +faststart` → `out/final.mp4`.

### Step 7 — YouTube package
Produce all of these in `out/`:
- `short.mp4`: a 1080×1920 version, 30–58 s, built from the hook and the strongest scene,
  re-laid out for vertical (do not just crop), with large burned-in captions.
- `thumbnail.png`: 1280×720, at most 4 words, one focal object, high contrast,
  readable at phone size. Make 2 variants.
- `youtube.md`: 5 title options (under 60 characters, one clear promise each),
  a description whose first 2 lines state the payoff, chapter timestamps taken from the
  real scene start times, and 5–8 relevant tags.

## 5. Visual rules (what makes it look good)

- **One idea per frame.** If a frame needs more than 12 words, split the scene.
- **Type:** two fonts at most. Headlines 96 px or larger, body 48 px or larger. Nothing under 36 px.
- **Colour:** one background, one text colour, one accent, one secondary accent. Contrast 4.5:1 or better.
- **Layout:** 120 px safe margin on all sides. Align to a 12-column grid. Leave empty space.
- **Show, don't list.** Prefer diagrams, counters, charts, and objects transforming over bullet points.
- **Consistency:** the same object keeps the same colour and shape through the whole video.

## 6. Motion rules

- Something changes on screen every 3–5 seconds. No static frame longer than 5 s.
- Elements enter in 0.4–0.7 s with ease-out, and exit faster, in 0.2–0.35 s with ease-in. Never use linear easing for UI motion.
- Stagger groups by 60–100 ms per item. Do not animate everything at once.
- Motion must mean something: draw a line to connect ideas, scale to show emphasis, morph to show change.
- Carry one element across each scene transition instead of hard cuts or stock wipes.
- At most one "big" move (zoom, camera pan, full-screen reveal) per scene.
- Animate only `transform` and `opacity` where possible, so frames render cleanly.

## 7. Hard rules

- Do not render before lint and inspect pass and you have looked at the extracted frames.
- Do not invent facts or statistics. If the script needs a figure, ask the owner or cite the source in `youtube.md`.
- Do not use copyrighted characters, logos, film or TV clips, or commercial music.
- Do not reuse a previous video's script or scene structure. Each video gets a fresh script and its own angle.
- If the video contains realistic synthetic people, voices, or events, note in `youtube.md`
  that the owner must tick YouTube's altered-content disclosure on upload.
- Never upload or publish anything. Hand the files to the owner.

## 8. Definition of done

- [ ] `out/final.mp4` plays start to finish, with audio and visuals in sync
- [ ] Hook lands in the first 8 seconds
- [ ] No static stretch longer than 5 seconds
- [ ] No clipped or overlapping text in any extracted frame
- [ ] Captions match the script
- [ ] `short.mp4`, 2 thumbnails, and `youtube.md` exist
- [ ] Final message to the owner: file locations, total length, and anything they need to review
