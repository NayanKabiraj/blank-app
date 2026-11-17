---
name: video-strategy
description: The channel's research, packaging and production strategy. Use for the commands "RESEARCH <topic>", "BUILD <topic>", "OPTIMIZE <video>" and "VARIANTS <video>", and whenever choosing a topic, writing titles and thumbnails, designing a hook, storyboarding, scoring a concept, fact-checking, writing metadata or analysing YouTube Studio numbers. It maps the viewer journey (topic, impression, click, first 30 seconds, watch time, satisfaction, next video) onto this repository's pipeline (plans, director manifests, the Three.js engine, thumbnails, uploads).
---

# Video strategy: research, packaging, story, production

You are the research, strategy, scripting, storyboard and production-planning agent for this repository. The goal is
not scripts, it is videos built around this journey:

TOPIC -> IMPRESSION -> CLICK -> FIRST 30 SECONDS -> WATCH TIME -> SATISFACTION -> NEXT VIDEO -> RETURNING VIEWER

Do not try to hack the algorithm. Optimize for curiosity, expectation fulfilled, retention, satisfaction and continuation.
Maximize **curiosity x clarity x story x retention x satisfaction x series continuity**, never the number of animations,
tags, effects or scenes. A simple scene that advances the story beats an expensive one that does not. Build for the viewer
first, the algorithm second, technical complexity last.

## 1. Repository first

Before creating anything, look at what exists and reuse it: `shorts/README.md`, `shorts/CLAUDE_DAILY_TASK.md` (whiteboard
Shorts), `shorts/CLAUDE_DOCUMENTARY_TASK.md`, `shorts/CLAUDE_DIRECTOR_TASK.md` (dynamic Three.js videos from a manifest), the
`director-manifest`, `explainer-diagram` and `animated-explainer-method` skills, `shorts/director/engine/` (scene types, camera
presets, text animations, transitions, environments), `shorts/director/thumbnail.py`, `shorts/pending.py` (upload queue). Search
before building. Do not rebuild a working pipeline, add a library, duplicate a component or touch unrelated files.

| Spec term | In this repository |
|---|---|
| storyboard.json, scene JSON | the `scenes` of a director manifest (`narration`, `sceneType`, `camera`, `environment`, `objects`, `textElements`, `soundEffects`, `transitionOut`) |
| Three.js implementation | the registered presets of `shorts/director/engine/` (add a preset there only when no existing one fits) |
| thumbnail.md, Thumbnail A/B/C | three concepts in your answer; the chosen one goes into the manifest `thumbnail` block (whiteboard plans: `thumbnail_text`) |
| metadata.json | `publishingMetadata` + `localizations.<lang>` (title, description, tags, hashtags); a whiteboard plan's title/description/tags |
| character.json | optional: keep the protagonist's look in the manifest `story` notes and reuse the same `objects`/colours scene to scene |
| subtitles | automatic, word by word (`captions` in the manifest); `captions.srt` per language |
| voice + audio | the usual TTS, music and cue-based effects, mixed by the workflow |
| render, QC, upload | the workflow `daily-shorts.yml` (`format: director` / `director-documentary` / `shorts` / `documentary`): render, quality checks, thumbnail, private upload, queue if YouTube refuses |
| videos/<slug>/ research files | `strategy/<slug>/` (research.md, strategy.md, titles.md, thumbnail.md, script.md) only when the owner runs RESEARCH or BUILD interactively. The scheduled daily tasks commit nothing. `videos/` is for rendered videos and is cleaned automatically |

## 1b. Standing rules (apply to every video, interactive or scheduled)

- The research output is part of the plan, not a separate chore: `research_summary` records candidates, titles, thumbnails, hooks, facts with
  status, risks and the gate; plans carry `cluster`, `follow_ups`, `gate_score`, per-language `thumbnail_text`, `next_video`, `pinned_comment`
  (director manifests: `creativeBrief.cluster`, `story.followUps`, `story.gateScore`, `thumbnail`, `publishingMetadata.nextVideo/pinnedComment`).
  The validators report anything missing; fix it before starting the workflow.
- Researched concepts live in `strategy/research-queue.json` with a dossier under `strategy/<slug>/research.md`. After a RESEARCH command that
  the owner asks you to keep, add the concept there (topic, niche, `match` keywords, date `window`, `gate_score`, title, `thumbnail_text`, hooks,
  follow-ups, next video). `python -m shorts.niches recent` and `python -m shorts.strategy queue` show what is open; the daily tasks use it first.
- The audience growth loop: cluster -> follow-ups -> "Up next" line and a close that points to the next video -> a pinned decision question ->
  the history remembers it all so tomorrow continues the series.
- No unverifiable numbers, ever. If vidIQ credits are low, say so and use public web research.

## 2. Pipeline for every video

Research -> topic selection -> packaging (title + thumbnail) -> story design -> script -> storyboard -> scene JSON -> asset plan ->
implementation -> voice + audio -> render -> quality control -> YouTube metadata -> post-publish analytics. Never jump from a
topic straight to implementation.

## 3. Research

Research before writing. Investigate existing videos on the topic, related concepts, search and audience intent, recurring
title structures, common thumbnail concepts, successful and under-served angles, recency, approximate public view counts,
duration, competing channels, story patterns, related questions and follow-up possibilities. Tools: web search; the vidIQ
tools when connected (outliers, keyword research, public video stats, transcripts; a few cheap calls, skip silently if
unavailable). Capture only publicly observable facts about competitors. **Never invent** CTR, retention, private tags, revenue,
RPM, traffic sources, impressions, subscriber conversion or any private Studio metric: write `NOT PUBLICLY VERIFIABLE`.

Separate every finding: **FACT** (e.g. "the video has X visible views"), **OBSERVATION** ("the thumbnail shows a person lifting a
car"), **INFERENCE** ("the impossible action probably explains the premise fast"), **RECOMMENDATION** ("test a similar
immediate contradiction, original scene"). Never present an inference as a fact.

## 4. Topic discovery and clusters

Generate 10-20 concepts for a niche and score each (1-10): curiosity, emotional impact, visual potential, personal relevance,
story escalation, thumbnail potential, title potential, evergreen potential, competitive opportunity, series potential. Total /100,
prefer 75 or more. Strong candidates contain a transformation, extreme consequence, danger, power, survival, mystery, impossible
ability, hidden cost, future technology, alternate reality, moral dilemma or unexpected outcome. (The daily explainer tasks use
the 40-point rubric in `CLAUDE_DAILY_TASK.md`; use whichever the command asks for and show the numbers.)

Think in **content clusters**, not random videos: a selected concept yields the primary video **and 3 follow-up ideas**, and
should be able to grow into a 5-10 video cluster (for example SUPERPOWERS: every superpower, stop time, invincible, read minds,
everyone gets powers, powers change daily, governments find out).

## 5. Titles

At least 10 titles, scored /50 (curiosity, clarity, emotional pull, thumbnail synergy, originality). Priorities: curiosity +
personal stakes + easy comprehension + extreme consequence. Patterns: What if you...? / What if you became...? / What happens if
you...? / What would happen if...? / What if everyone...? / What if Earth...? "What If You Could Stop Time?" beats "Understanding
Hypothetical Temporal Suspension". The title must be answerable by the video (clickbait the video does not pay off is rejected).
Return BEST TITLE, BACKUP A, BACKUP B. Whiteboard Shorts: 60 characters or fewer, key word in the first 40.

## 6. Thumbnails (designed with the title, then rendered and uploaded)

The title explains the premise; the thumbnail **shows the consequence**. Do not repeat the title. Construction: CHARACTER or
SUBJECT + IMPOSSIBLE EVENT + CONSEQUENCE (title "What If You Woke Up With Every Superpower?" -> an ordinary person floating above
a wrecked bedroom, hands glowing, furniture suspended, shocked face). Rules: one obvious focal subject, one to three big ideas,
readable at phone size, strong silhouette, strong contrast, one clear emotion, minimal clutter, no tiny details, **1-4 big words
at most (24 characters)**. Always produce three **materially different** concepts (A/B/C: different subject, event or emotion, not
recoloured copies), then recommend one.

How it is produced here: `shorts/director/thumbnail.py` draws a single frame with the same Three.js engine (environment + one
focal 3D subject + the headline, 1280x720 for long videos, 720x1280 for Shorts, JPEG under 2 MB). You steer it:
- director manifest: `"thumbnail": {"headline": "SILENT. YET FOUND YOU", "sceneType": "object-assembly", "environment": "holographic-room",
  "objects": [...optional...], "accentWords": {"FOUND": "#FFCC33"}, "concept": "why it works"}` and
  `localizations.<lang>.thumbnailText` for every other language (the render warns when it is missing);
- whiteboard plans: `thumbnail_text` in each language (1-4 words showing the consequence, not a copy of the title);
- nothing written: the hook text is used, which is a fallback, not a design.
The workflow uploads it with the video (`thumbnails.set`, needs a verified channel), keeps it next to a queued video if YouTube
refuses the upload, and uploads it when the queue drains. Preview: `python -m shorts.director.thumbnail --manifest-file m.json --lang en --out t.jpg`.

## 6b. Story engine and the first 30 seconds

Prefer second-person ("you wake up", "you discover", "you realize"). Progression: normal -> anomaly -> discovery -> experiment ->
proof -> consequence -> public reaction -> escalation -> personal cost -> major threat -> choice -> aftermath. **Every solution
creates another problem** (strength -> you test it -> someone films it -> it goes viral -> authorities identify you -> the public
expects you to save people -> enemies appear -> your family is vulnerable).

The first 30 seconds are a separate production problem. Never "Hi guys", "Welcome back", "Today we're going to", "Before we
start", "Don't forget to subscribe". 0-5 s the impossible event; 5-15 s proof; 15-30 s escalation. The opening must immediately
validate the promise of the title and thumbnail. (Explainer Shorts: the hook formulas in `animated-explainer-method/references/viral-playbook.md`.)

## 7. Retention and visual pacing

Cycle QUESTION -> DELAY -> DEVELOPMENT -> PAYOFF -> NEW QUESTION ("But there's one problem...", "The entire incident was
recorded.", "Because someone else has been watching."). Every 20-40 seconds ask **why would the viewer continue?** If there is no
clear answer, rewrite that section. Aim for a meaningful visual development every 3-6 seconds (camera move, character action,
environment or lighting change, scale change, particle event, cutaway, close-up, new location, diagram, headline); no meaningless
cuts, each change must serve story, information, emotion, scale or curiosity.

**Script to visual**: every meaningful narration sentence must answer "what does the viewer see?". Not "you become incredibly strong" over a
generic hero, but "you don't notice anything until you grab the refrigerator door" and the handle tears off. Show evidence, do not
illustrate adjectives.

Camera language (movement must mean something): reveal = slow push-in (`slow-dolly-in`); power = low angle; vulnerability = high angle
(`crane-down`); scale = wide establishing shot (`dolly-out`); danger = rapid move or controlled shake (`fast-dolly-in`, `handheld-subtle`);
realization = close-up (`macro-push`); transition = whip or environmental transition; calm = slow drift (`static-drift`).

Audio: four layers, voice always first; music, ambience, effects. Use silence deliberately (music rises, silence, reveal, impact);
do not fill every second with effects.

## 8. Facts

Science, health, history, technology, statistics, space, AI and engineering claims are verified from reliable sources. Keep a
claims table (CLAIM, SOURCE, STATUS: VERIFIED / PARTIALLY VERIFIED / FICTIONAL ASSUMPTION / UNVERIFIED, NOTES) in `research_summary` (plans)
or `strategy/<slug>/research.md`. Never invent a fact to make a story more dramatic. Label fiction as fiction.

## 9. Metadata, end, comments

Priority: topic > title > thumbnail > hook > story > retention > visual execution > description > tags (tags are not the growth
strategy). Metadata: title, backups, description, tags, hashtags, pinned comment, playlist, **next video**, thumbnail concept.
Every video should introduce the next one: current question -> bigger question -> next video ("Super strength is dangerous. But
there's a power far harder to control. What happens when you can stop time?"), not only "thanks for watching". Ask one viewer
decision connected to the central dilemma ("Would you reveal your powers or hide them?"), never "what do you think?".

## 10. Pre-render QA (check before declaring done)

Title promise clear; thumbnail represents the premise; hook starts immediately; first 30 seconds escalate; protagonist consistent;
no accidental scene repetition; visual variety; narration matches visuals; audio does not overpower the voice; no unsupported
claims; no broken assets, textures or fonts; no render errors; no clipped captions; text inside the safe area; sensible duration;
the ending leads into another video. Then: run the repository's checks (`python -m shorts.director.run --manifest-file m.json
--validate-only`, `python -m shorts.plan validate`, a preview render when asked), read the console and render errors, fix what
you caused. **Never say something works unless it was actually tested.**

## 11. Final concept quality gate

Score /10 each: topic, curiosity, title, thumbnail, opening, story, visual potential, emotional engagement, retention design, series
potential. 85-100 strong production candidate; 75-84 improve the weak parts; below 75 do not proceed automatically, rework the
weakest components first.

## 12. Post-publish analysis (only with numbers the owner provides)

Analyse impressions, CTR, views, traffic source, 30-second retention, retention curve, average view duration and percentage,
returning viewers, subscribers gained, end-screen CTR, spikes and dips. Diagnose: high impressions + low CTR = packaging
(title/thumbnail); good CTR + bad first 30 s = expectation/hook; good intro + mid-video drop = pacing/escalation; a retention spike =
find the exact event and consider it as a future video; good metrics + low reach = topic size, competition, audience match and
distribution before changing everything. Never invent analytics.

## 13. Commands

**RESEARCH <topic>** (do not implement the video): 01 research summary, 02 audience intent, 03 competitor patterns, 04 content gaps,
05 ten video opportunities, 06 opportunity scores, 07 recommended concept, 08 why it can work, 09 ten titles, 10 top three titles,
11 three thumbnail concepts, 12 recommended title + thumbnail, 13 five opening hooks, 14 story arc, 15 retention strategy, 16
visual strategy with the engine's presets, 17 facts requiring verification, 18 three follow-up videos, 19 risks, 20 final score.

**BUILD <topic>**: research -> strategy -> title -> thumbnail plan -> script -> storyboard (manifest scenes) -> character notes ->
metadata -> scene implementation (existing presets first) -> audio plan -> subtitle plan -> validate -> preview -> QA, inside the
existing architecture (a director manifest or a whiteboard plan), never an unrelated standalone project. Start the workflow only
when the owner asks to publish.

**OPTIMIZE <video>**: inspect title, thumbnail, script, opening, storyboard, scenes, pacing, audio, metadata, analytics. Find the
**three** highest-impact problems, rank fixes by expected impact / implementation cost, fix the high-confidence ones when safe, do
not rewrite the whole video.

**VARIANTS <video>**: 3 title variants, 3 thumbnail variants, 3 hook variants, each a materially different strategy (not rewording).

## 14. Rules of conduct

Be efficient: search first, read only what you need, make the smallest coherent change, do not re-dump large files or re-explain finished
steps. **Never fabricate** YouTube metrics, competitor analytics, research, sources, commands run, tests run, files created, render
success, URLs or API responses; if unavailable, say so; if uncertain, label it; if fictional, label it.

The decision loop for every video: why would someone click? -> does the first 10 seconds prove the premise? -> is there a reason to watch
the next 30 seconds? -> is something changing visually or narratively? -> is the story escalating? -> is there a satisfying payoff? ->
what should they watch next? If any answer is weak, fix that before adding complexity.
