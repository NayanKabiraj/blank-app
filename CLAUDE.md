# Instructions for Claude in this repository

This repository makes faceless YouTube explainers (Shorts and documentaries, English + Hindi): whiteboard template videos
(`shorts/explainer/`), Claude-directed dynamic Three.js videos (`shorts/director/`), and real stock-footage videos
(`shorts/stockreel/`, Wikimedia Commons, public domain/CC0 only, no API key - never an AI-generated clip), rendered and uploaded
(private) by the GitHub Actions workflow `daily-shorts.yml`. Claude researches and writes; the workflow renders.

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

## Quick commands

```bash
python -m shorts.niches recent                       # researched queue, follow-ups, recent topics
python -m shorts.strategy queue                      # what is open today
python -m shorts.plan validate plan.json             # whiteboard Short plan (also checks the strategy fields)
python -m shorts.plan validate-doc plan.json         # documentary plan
python -m shorts.director.run --manifest-file m.json --validate-only
python -m shorts.director.thumbnail --manifest-file m.json --lang en --out t.jpg
```
