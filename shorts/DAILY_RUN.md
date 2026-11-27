# Daily run guide (token-lean; the scheduled task points here)

Goal of everything: subscribers and watch time toward monetization, safely (CLAUDE.md rules 17-19, `strategy/monetization.md`). Details live in the files named below: open one only when you need it, by line range (`sed -n`), never whole.

## 0. One command first
`python3 -m shorts.runbrief` prints the whole morning brief: today's plan, auth banner (show it if present, rule 14), queue, the generated `Channel check:` line, scoreboard, milestones, trending, SEO data age, recent topics, the researched
queue and the learnings rules. Do not run the individual channel/progress/niches commands again, and do not read learnings/monetization/growth files in full (the brief carries what you need).

## 1. Topics: follow what the views say (no waiting period)
The brief's **RECOMMENDED SLOTS TODAY** (from `shorts.patterns`: families tech / space+nature / mind+body / story, ranked by views per day, shrunk by sample size, plus ONE explore slot for the least-sampled family) decide the families of today's three topics. Override one only with a stated
reason in `Growth:` (a timely hook, a series follow-up). **Part 2 candidates** (>= 2x the channel median) get a follow-up topic from their saved follow_ups before anything else. Respect the guards: the day's videos differ in structure and angle (anti-template); no health/medical advice (Mind & Body topics explain mechanisms only); no story/horror Shorts (niche dropped 26 Nov 2026). Documentary days (Sunday, plus Wednesday from 9 Dec): 2 Short topics + one 6-8 min search-led long-form on a winning Short topic (chapters, each paying off a question), each EN+HI; target 6 Short uploads a day otherwise (3 x EN+HI; 10 only if learnings.md says so). Prefer a **researched queue entry** of the chosen family (read its dossier, re-verify only `recheck` items); the timely slot is fresh research. Also read the
language, length and title-shape lines: write the hook and title in the shapes that score, and keep Hindi/English parity (both languages are always produced).

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

## Story craft (26 Nov 2026)

Before writing narration read `strategy/story-craft.md` (hook killers, BUT/THEREFORE beats, open loops, specificity, banned AI tells). After writing a plan run `python3 -m shorts.storycheck plan.json` (advisory) and fix what it flags.

## Prepared topic for 27 Nov 2026 (owner request, 26 Nov)
Slot 1 (space+nature) is READY: plan `strategy/prepared/2026-11-27-silent-space.json` ("Why Is There No Sound in Space?", validated, claims verified, EN+HI) and the committed pack
`generated_animations/scenes/silent_space_vox/` (2D cartoon astronaut from `shared/cartoon.py` in the vox look, previews inspected in EN and HI). Do not rewrite it: re-check the Gap with
`seo-research.yml` (title phrase 'why is there no sound in space'), update `Channel check:` with the morning numbers, then dispatch it with `daily-batch.yml` first, and research slots 2 and 3 as usual. The
`cartoon.astro/ear/eye_icon` helpers are available to every new pack (2D cartoon character look, same render time as other vox packs).

## Myth Busters and full-screen art (26 Nov 2026)
The patterns brief now lists a `myth` family (niche "Myth Busters", examples in `shorts/niches.py`); with no data yet it is the explore slot, so one of the three Shorts each day is a myth buster: hook = the belief
stated as a fact ("You only use 10% of your brain."), turn in scene 3 ("That's false."), the real mechanism in the middle, the reframe at the end. Two sources per claim, status VERIFIED, never health/finance/legal advice.
New packs paint the whole screen: `"stage": "full"` in `shots.json` and `b.backdrop(top, bottom)` per beat (see `silent_space_vox`); art zone is local y -4.8..+4.8, x +-4.4 around `b.C`; keep key art above the caption pill.

Direct pushes to main are allowed by `.claude/settings.json` (owner request, 27 Nov 2026); scheduled runs still commit only new pack folders (rule 7).

## Videosly horror Short (27 Nov 2026, rule 22)
Do this FIRST in every daily run (it needs 25-45 minutes to generate and render, so it overlaps with the batch): follow `shorts/VIDEOSLY_HORROR_TASK.md` - a topic-only prompt to Videosly with skill horror-story, then title/description/tags by Claude and `videosly_post_video`.
It is on top of the day's Shorts (Videosly posts to the channel through its own connection, not our YouTube quota; 2 YouTube posts a day max). Report it in the final summary.
