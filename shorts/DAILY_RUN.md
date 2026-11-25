# Daily run guide (token-lean; the scheduled task points here)

Goal of everything: subscribers and watch time toward monetization, safely (CLAUDE.md rules 17-19, `strategy/monetization.md`). Details live in the files named below: open one only when you need it, by line range (`sed -n`), never whole.

## 0. One command first
`python3 -m shorts.runbrief` prints the whole morning brief: today's plan, auth banner (show it if present, rule 14), queue, the generated `Channel check:` line, scoreboard, milestones, trending, SEO data age, recent topics, the researched
queue and the learnings rules. Do not run the individual channel/progress/niches commands again, and do not read learnings/monetization/growth files in full (the brief carries what you need).

## 1. Topics (priority order; a short day still ships the best first)
(1) everyday-tech / phone / home explainer with a personal hook; (2) a timely topic this week or a Space & Universe / Earth & Nature explainer; (3) ONE original Horror & Suspense story (bloodless, no real people/places/events, labelled
fiction). Sunday: 2 topics + 1 documentary (gate: a Short on the topic got traction). Target 6 a day (3 x EN+HI); 10 only if learnings.md says so. The day's videos differ in structure and angle (anti-template). Prefer a **researched queue entry** (the
brief lists them): read its dossier, re-verify only items marked `recheck`. The timely slot is always fresh research (web search).

## 2. Research (only what the dossier lacks)
Web-search the facts; Claims table (two sources per number, status VERIFIED / PARTIALLY VERIFIED / FICTIONAL ASSUMPTION / UNVERIFIED), Gap line. SEO: dispatch `seo-research.yml` (queries separated by `|`, phrased as a viewer types; a second run `hl=hi gl=IN`), `git pull`,
read `data/seo/latest.json` (best autocomplete phrase -> title + first tag; outliers -> copy hooks and length, not wording).

## 3. Plan JSON (one per topic, english + hindi in the same file)
Fields as `shorts/sample_plan.json`. research_summary has Candidates, Titles, Thumbnails, Hooks, `Claims:`, `Gap:`, `Channel check:` (paste the generated line, then what you changed), `Learning applied:`, `Growth:`. Scene 1 hook, scene 2 intro (Shorts <= 22 words),
thumbnail_question, title <= 65, 5-8 tags, 2-3 hashtags, >= 3 question scenes (one in the first two), >= 4 graphic kinds; Short 100-112 words EN (validator 100-142), Hindi 85-125; Hindi headline <= 28 characters; mood one of calm/upbeat/dramatic/inspiring/mysterious.
`python3 -m shorts.plan validate <file>` must be clean.

## 4. Pack (rule 10, vox look; ONE bilingual pack per topic)
`generated_animations/scenes/<id>/`: `shots.json` {"topic","look":"vox","shots":[{"module","scenes":[..]}]}, `scene_NNN.py` modules, `__init__.py`. Start every scene module with
`from generated_animations.shared.packkit import *` (Beat helpers, figure/phone/plane..., vox, level/show/window). Wrap each beat in its own function (`def beat0(b): ...; beat0(B[0])`), bilingual text via `vox.L(ctx, "EN", "हिन्दी")`, motion tied to `ctx.elapsed()`
(always `b.live`/`b.mover`), fade with the beat, stage inside about +-3.2 x / -2.6..+2.9 y for Shorts. Patterns: `generated_animations/scenes/phone_prox_vox/`, `bh_fall_vox/`, `last_train_vox/`.
Then `python3 -m generated_animations scan <id>`; preview EN **and** HI: `python3 -m generated_animations.authoring.preview <plan.json> --lang en` (and `--lang hi`), open each printed sheet PNG ONCE, fix overlaps/clipping/dead moments, re-render only if you changed something.

## 5. Commit and publish (cheap path)
Commit ONLY the day's new pack folders (one branch + one PR + squash merge, rule 7). Then ONE dispatch: `daily-batch.yml` with `plans_json` = a JSON array of the day's plans (compact) and `langs` "en,hi" (documentary: `format` documentary). It renders and uploads them one after the
other with no polling by you. Wait with ONE Monitor loop on that run, then read the line starting `BATCH_RESULT` in its job log (uploaded URLs or why queued; quotaExceeded is not an authorization problem).

## 6. Token discipline (cost = calls x context size)
Batch independent steps into one Bash call; filter every output (`head`, `jq`, `grep`); poll with Monitor, never repeated checks; one image read per contact sheet; do not re-read files already in context; do not paste large JSON back into the chat.
Quality never drops: research depth, claim checks, frame inspection and bespoke animation are not optional.

## 7. Final summary
Channel check + scoreboard + milestones and what you changed because of them; per topic: niche, score, runner-up, title, pack id, Growth lever, EN/HI uploaded or queued; Sunday: the documentary; how many of the day's uploads happened and why any are missing; any authorization banner.
