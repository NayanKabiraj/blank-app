# Instructions for Claude in this repository

This repository makes faceless YouTube explainers (Shorts and documentaries, English + Hindi): whiteboard template videos
(`shorts/explainer/`), Claude-directed dynamic Three.js videos (`shorts/director/`), and real stock-footage videos
(`shorts/stockreel/`: a real Wikimedia Commons photo by default, no API key - or, if `POLLINATIONS_API_KEY`/`HF_TOKEN`
is set, an AI-generated image instead, always uploaded with YouTube's synthetic-content label set automatically),
rendered and uploaded (private) by the GitHub Actions workflow `daily-shorts.yml`. Claude researches and writes;
the workflow renders.

## Always

1. **Follow the `video-strategy` skill** (`.claude/skills/video-strategy/SKILL.md`) for every video and every topic decision: the viewer journey
   (topic, impression, click, first 30 seconds, watch time, satisfaction, next video, returning viewer), research before writing, packaging
   (title + thumbnail) before story, retention design, the quality gate, and the audience growth loop (cluster, follow-ups, "Up next", pinned
   question). Commands: `RESEARCH <topic>`, `BUILD <topic>`, `OPTIMIZE <video>`, `VARIANTS <video>`.
2. **Task files**: `shorts/CLAUDE_DAILY_TASK.md` (whiteboard Short), `shorts/CLAUDE_DOCUMENTARY_TASK.md`, `shorts/CLAUDE_DIRECTOR_TASK.md`
   (director manifests), `shorts/CLAUDE_STOCKREEL_TASK.md` (real stock footage, for topics that read better with real footage than a
   coded scene - a third style, never the default). Each starts with the standing strategy checklist.
3. **Start from what is researched**: `python -m shorts.niches recent` shows the researched queue (`strategy/research-queue.json`), open follow-ups
   and recent videos. Never repeat a topic.
4. **Never fabricate** metrics, competitor analytics, sources, commands run, tests run, render success, URLs or API responses. Unavailable data is
   `NOT PUBLICLY VERIFIABLE`; fiction is labelled fiction. Verify facts from reliable sources (status: VERIFIED / PARTIALLY VERIFIED / FICTIONAL
   ASSUMPTION / UNVERIFIED).
5. **Reuse the repository**: search before building; do not rebuild a working pipeline, duplicate a component or touch unrelated files. Never say
   something works unless it was actually tested.
6. **Uploads stay private** unless the owner changes `YT_PRIVACY`. Videos YouTube refuses wait in `videos/unpublished/` and upload first next time.
7. Scheduled tasks commit nothing; interactive work goes on a branch and a pull request.

8. **Every video ends with the closing line** "Thanks for watching the video! Please like, share and subscribe to watch more interesting
   videos like this." (Hindi equivalent in `shorts/outro.py`). It is added automatically to every Short, documentary, stock-footage and
   cinematic video (`shorts.outro.with_outro`) and to every `generated_animations` topic (animated outro scene) - plans must NOT write it
   themselves (the word budget already leaves room). Director-manifest videos are the one style not covered yet.
9. **generated_animations** (`generated_animations/`, README there): per-topic Python scene modules written by Claude, rendered by Mode B
   (`python -m generated_animations render <topic>`, workflow `generated-animations.yml`). Voices (all videos, daily pipeline and generated_animations): English = edge-tts `en-US-AndrewNeural` (falls back to Piper
   if unreachable; `EN_VOICE=piper` forces Piper), Hindi = Piper `hi_IN-pratham-medium`. Code is approved by a human before scheduled use.

## Quick commands

```bash
python -m shorts.niches recent                       # researched queue, follow-ups, recent topics
python -m shorts.strategy queue                      # what is open today
python -m shorts.plan validate plan.json             # whiteboard Short plan (also checks the strategy fields)
python -m shorts.plan validate-doc plan.json         # documentary plan
python -m shorts.director.run --manifest-file m.json --validate-only
python -m shorts.director.thumbnail --manifest-file m.json --lang en --out t.jpg
```
