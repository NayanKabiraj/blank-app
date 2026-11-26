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
2. **Task files**: `shorts/DAILY_RUN.md` (the token-lean daily run guide, start here), `shorts/WEEKLY_RESEARCH.md` (weekly research run), `shorts/CLAUDE_DAILY_TASK.md` (whiteboard Short, detail), `shorts/CLAUDE_DOCUMENTARY_TASK.md`, `shorts/CLAUDE_DIRECTOR_TASK.md`
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
7. Scheduled tasks commit nothing, with ONE exception the owner explicitly authorised (22 Nov 2026): each run commits that day's animation pack (rule 10) - only the new folder
   `generated_animations/scenes/<pack>/`, never edits to existing packs or other code - straight to `main` before dispatching the workflow, because the workflow
   renders from `main`. A second exception (24 Nov 2026): the weekly research run (`shorts/WEEKLY_RESEARCH.md`) may merge ONE pull request that touches only `strategy/research-queue.json` and `strategy/research/`. Interactive work goes on a branch and a pull request.

8. **Every video ends with the closing line** "Thanks for watching the video! Please like, share and subscribe to watch more interesting
   videos like this." (Hindi equivalent in `shorts/outro.py`). It is added automatically to every Short, documentary, stock-footage and
   cinematic video (`shorts.outro.with_outro`) and to every `generated_animations` topic (animated outro scene) - plans must NOT write it
   themselves (the word budget already leaves room). Director-manifest videos are the one style not covered yet.
9. **generated_animations** (`generated_animations/`, README there): per-topic Python scene modules written by Claude, rendered by Mode B
   (`python -m generated_animations render <topic>`, workflow `generated-animations.yml`). Voices (all videos, daily pipeline and generated_animations): English = edge-tts `en-US-AndrewNeural` (falls back to Piper
   if unreachable; `EN_VOICE=piper` forces Piper), Hindi = Piper `hi_IN-pratham-medium`. Code is approved by a human before scheduled use.

10. **STRICT - Claude authors the animation of every video** (`generated_animations/AUTHORING.md`). The picture is not a template: for every Short and
   documentary Claude writes scene-specific motion animation code (orbits, signals travelling, water rising, graphs drawing as things move ...) in
   an animation pack `generated_animations/scenes/<pack>/`, named in `animation_pack` of the plan (each language in the plan). The generic graphic-kind cards
   (`kinds.py`) are only a fallback and the plan validator rejects a plan whose scenes are not all covered by shots. Videos must be dynamic, with a lot of motion.
   Scheduled daily runs follow this rule too: they write the pack, scan it, preview and inspect frames, commit it (rule 7) and only then start the workflow. Voices are strict: English = edge-tts `en-US-AndrewNeural`, Hindi =
   Piper `hi_IN-pratham-medium`; if a voice is unavailable the run fails, no other voice is ever mixed in.

11. **English + Hindi again** (owner instruction, 24 Nov 2026; replaces "English only"): every Short and documentary is produced in both languages (`config.LANGS` / `VIDEO_LANGS`, default `en,hi`; the workflow's `langs` input
   defaults to `en,hi`). Plans carry a `hindi` block (same scenes, Devanagari narration, same `animation_pack`); the pack is bilingual (`vox.L(ctx, en, hi)` / `T[ctx.lang]`) and in the vox look. `VIDEO_LANGS=en` makes a run English only.

12. **Every video starts with a channel check, a research template and SEO rules** (owner instruction, 23 Nov 2026; details in the task files): before choosing a topic run
   `python -m shorts.channel_trends summary` (data from `channel-trends.yml`; "NOT AVAILABLE" until the YouTube sign-in has the read-only scopes) and record `Channel check:` in
   `research_summary`; also `Claims:` and `Gap:`. Scene 1 = hook, scene 2 = intro (Shorts 22 words max), `thumbnail_question` required, title <= 65 characters, 5-8 tags,
   2-3 hashtags, a Sources line is added to the description automatically. The validator checks all of it.

13. **Vox look** (owner instruction, 23 Nov 2026): every new animation pack uses the paper cut-out explainer style (`"look": "vox"` in `shots.json`, helpers in `generated_animations/shared/vox.py`, guide in `AUTHORING.md`);
   the presenter stays as a sticker. The validator requires it; `VIDEO_LOOK=classic` restores the dark theme.

14. **Google/YouTube sign-in is phone-first** (owner instruction, 24 Nov 2026; `docs/oauth-mobile.md`, `shorts/ytauth.py`): when a run reports "Google authorization required" (or `data/oauth_pending.json` on `main`
   has a waiting request), print the output of `python -m shorts.ytauth banner` prominently in the chat (the 🔐 message with the tappable link) - never the token/secret. The owner taps the link, Allow, then
   "Submit new issue"; `oauth-callback.yml` stores the credentials and uploads the queue. Do not ask for terminal commands; quota/scope/rate/5xx errors are NOT authorization problems.

15. **Learnings loop** (owner instruction, 24 Nov 2026; `strategy/learnings.md`): before every topic decision read `strategy/learnings.md`, run `python -m shorts.channel_trends summary` and `... trending`, apply the Rules, record
   `Learning applied:` in `research_summary` and keep the file current with dated, honest evidence. Hindi videos (when produced) follow the same vox look: every on-screen string via `vox.L(ctx, en, hi)` / `T[ctx.lang]`.

16. **6 uploads a day (quota), 10 when the quota is raised** (owner instruction, 24 Nov 2026; the current target and review rules are in `strategy/learnings.md` "DECISION", daily steps in
   `shorts/CLAUDE_DAILY_TASK.md` "Daily production plan"): 3 Short topics x EN+HI per day (Sunday: 2 topics + 1 documentary x EN+HI), including one original **Horror & Suspense** story Short (bloodless, no real
   people/places/events, labelled fiction). Quality over quota: ship fewer rather than rush; leave nothing unmerged or unuploaded (the queue is flushed 3x a day).

17. **The goal is growth and monetization** (owner instruction, 24 Nov 2026; `strategy/monetization.md`): everything Claude generates, publishes or changes must serve the goal of subscribers and watch time that qualify the channel
   for the YouTube Partner Program, safely (no template-like mass-produced videos, no off-putting content, no sensitive-topic personas). Every plan's `research_summary` has a `Growth:` line (lever pulled + policy check), the channel
   check includes the `monetization` scoreboard (`python -m shorts.channel_trends summary`) and the computed Partner Program eligibility (fan-funding and ads tier % met, in `python -m shorts.runbrief` and the weekly report; goals in `strategy/monetization.md`), and when a choice trades quantity for quality or policy safety, choose safety.

18. **Milestones and the weekend progress report** (owner instruction, 24 Nov 2026; `strategy/milestones.json`, `shorts/progress.py`, workflow `weekly-report.yml`): the ladders (subscribers, public watch hours, Shorts views, best video, subscribers per
   1,000 views, Shorts viewed %, upload streak) are tracked automatically; every Sunday 21:00 IST the workflow refreshes the numbers, writes `reports/progress-<date>.md` + `reports/latest.md` and opens a GitHub issue with the report (phone
   notification). The Sunday daily run reads `reports/latest.md`, shows its Milestones and Next-week sections in the final message and applies "Next week" to the following week's plan. Never estimate a number the APIs did not return (n/a).

19. **Growth plan** (owner request, 24 Nov 2026; `strategy/growth-plan.md`): the channel will not be monetized by volume alone. Explore across formats until 8 Dec, then at least 60 % of topics come from the top-2 series by views and
   subscribers gained; any Short above 300 views gets a Part 2 within 3 days; every video carries the conversion toolkit (series promise in the first 20 s, series name, pinned comment answering `next_video`, the one-tap subscribe link that the pipeline adds
   to every description); long-form (the only watch time that counts toward the 4,000 hours) is one search-led video a week built on a winning Short topic.

20. **Free SEO research** (owner request, 24 Nov 2026; `shorts/seo.py`, workflow `seo-research.yml`): for every candidate topic dispatch `seo-research.yml` with the topic phrased as people would search it (up to 6 queries separated by `|`; use `hl=hi gl=IN` for the Hindi phrasing), then read
   `data/seo/latest.json` (autocomplete phrases, outlier videos, title/length patterns). Put the best autocomplete phrase in the title and tags, copy what the outliers do in their first seconds, and record the winning phrase in `Gap:`. The channel check also reads `search_terms` (the searches that
   brought viewers to our videos, from the Analytics API). Public metadata only, low volume; the endpoints are unofficial, so a failure means "SEO data NOT AVAILABLE", never an invented number.

21. **Token-lean runs** (owner request, 25 Nov 2026): each daily run is a fresh session (cost = calls x context size). Start with `python3 -m shorts.runbrief`, follow `shorts/DAILY_RUN.md`, write packs on `generated_animations/shared/packkit.py`, preview with `python3 -m generated_animations.authoring.preview`,
   dispatch the day's plans ONCE with `daily-batch.yml`, batch commands and filter outputs. Quality steps (research, claim checks, frame inspection, bespoke animation) never shrink.

## Quick commands

```bash
python -m shorts.niches recent                       # researched queue, follow-ups, recent topics
python -m shorts.strategy queue                      # what is open today
python -m shorts.plan validate plan.json             # whiteboard Short plan (also checks the strategy fields)
python -m shorts.plan validate-doc plan.json         # documentary plan
python -m shorts.director.run --manifest-file m.json --validate-only
python -m shorts.director.thumbnail --manifest-file m.json --lang en --out t.jpg
```
