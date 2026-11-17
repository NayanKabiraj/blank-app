# Documentary task: instructions for the Claude task that writes a long-form video

The channel makes two kinds of video: the daily **Shorts** (`CLAUDE_DAILY_TASK.md`) and
**documentaries** of **5 to 15 minutes**, in **English and Hindi**, in the same explainer look
(a whiteboard drawn in marker, the smiling sun, chat bubbles, quizzes) but landscape, 1920x1080.
A documentary answers one big question properly instead of a quick "why": it has chapters, a
story and a real payoff. Claude researches and writes the plan; the GitHub workflow
`daily-shorts.yml` (with `format: documentary`) renders it with the same Piper voice and synthesized music, and uploads it
(if the YouTube secrets exist) with automatic chapter markers.

It runs every day right after the daily Shorts task, in the same Claude session: start the Shorts workflow first, then do this task and start the documentary workflow (it has its own concurrency group, so it renders in parallel with the Shorts on a separate runner).

## Standing strategy (applies to every video, from now on)

Every video is built around one journey: topic -> impression -> click -> first 30 seconds -> watch time -> satisfaction -> next video ->
returning viewer. The full rules are in the `video-strategy` skill (`.claude/skills/video-strategy/SKILL.md`); this is the checklist for
the task. Do not try to hack the algorithm: maximize curiosity x clarity x story x retention x satisfaction x series continuity.

1. **Start from what is already researched.** `python -m shorts.niches recent` also prints `researched_queue` (concepts researched and
   scored in `strategy/research-queue.json`, whose date window is open and which are not made yet) and `open_follow_ups` (ideas earlier
   videos promised). A researched concept of the right kind (Short or documentary) wins unless another candidate beats its gate score by 4 or
   more points; a follow-up continues a cluster and gets a tie-break bonus. Read the concept's `dossier` first and re-verify its facts.
2. **Research before writing, and record it** in `research_summary` (the validator checks the markers): `Candidates:` (top three with
   scores), `Titles:` (at least ten, scored /50 for curiosity, clarity, emotional pull, thumbnail synergy, originality; the chosen one and
   two backups), `Thumbnails:` (three materially different concepts: different subject, event or emotion, not recolours; the chosen one),
   `Hooks:` (five openers, the chosen one), the facts with their sources and status (VERIFIED / PARTIALLY VERIFIED / FICTIONAL
   ASSUMPTION / UNVERIFIED), the risks, and the quality gate. Separate FACT, OBSERVATION, INFERENCE and RECOMMENDATION. Never invent
   metrics, views, CTR, retention, sources or numbers; if vidIQ credits are low or a tool is unavailable, say the competitor data is
   NOT PUBLICLY VERIFIABLE and continue with web research.
3. **Packaging gate.** The title explains the premise, the thumbnail shows the consequence (`thumbnail_text`, 1-4 big words, never a copy of
   the title). The first line proves the premise within 10 seconds; the first 30 seconds escalate. Every 20-40 seconds there is a reason to keep
   watching. Every narration sentence says what the viewer sees.
4. **Quality gate (`gate_score`, /100):** topic, curiosity, title, thumbnail, opening, story, visual potential, emotional engagement,
   retention design, series potential, /10 each. 85-100 proceed; 75-84 improve the weakest parts first, then proceed; below 75 do not render
   this concept, rework it or take the next candidate.
5. **Audience growth loop (series and returning viewers).** Name the `cluster` (a 5-10 video series the idea belongs to) and write three
   `follow_ups`. The close hands the viewer on: current question -> bigger question -> the next video, saved as `next_video` for each language
   (the description gets an "Up next:" line automatically). Write one `pinned_comment` per language: a single viewer decision tied to the
   central dilemma, as a question (saved in the `*_youtube.txt` file to pin). The history stores the cluster, follow-ups and next video, so the next
   day's task can continue the series.
6. **QA before the workflow starts** (the checklist in the skill: promise clear, hook immediate, no repeated scene, narration matches the picture,
   no unsupported claim, safe areas, an ending that leads to another video) and run the validator. The workflow only renders and uploads.

## Steps

**Strategy:** follow the `video-strategy` skill too (research evidence, title and thumbnail, retention, pre-render QA). Write
`thumbnail_text` for English and Hindi (1-4 big words, at most 24 characters, showing the consequence rather than repeating the title);
the workflow draws a 1280x720 thumbnail from it and uploads it with the video.

1. **Check the history.** In `NayanKabiraj/blank-app` on `main`, read `data/documentary_history.json`
   (it may not exist yet), `data/history.json` and `python -m shorts.niches recent`. Never repeat a
   topic. If `NICHE_HINT.txt` exists, it overrides the choices below.
2. **Choose a topic that deserves 5-15 minutes.** It must be big enough to have 4-8 chapters, with a
   mechanism, a surprise, real numbers and a human stake: "How the Indian monsoon works", "What
   actually happens when you press 'Pay' on UPI", "Why the Moon keeps drifting away". Collect 6+
   candidates across niches (this week's news, anniversaries, seasons, everyday mysteries), score
   them like the Shorts (curiosity, universality, timeliness, search demand, surprise, visual,
   shareability, verifiability and safety; max 40) and take the best. Use a *different* topic from today's Short (the
   strongest remaining candidate from the Shorts scoring that is big enough for chapters); a good documentary topic is
   also a good future Short.
   Avoid breaking tragedies, politics, elections, medical or investment advice, promotional brands.
3. **Research it properly** (web search; official sites, universities, encyclopedias, established
   outlets): the mechanism in 4-8 steps, 3+ striking numbers (each from two sources; say which you
   used), one myth people believe, one analogy, one surprise, one "what if it fails" angle. Write
   the audit trail into `research_summary`: start with "Candidates:" (top 3 with scores), why the
   winner won, then the facts and their sources. Mark approximations ("roughly", "about").
4. **Pick the length** (`target_minutes`, **5 to 10**): 5 for a single clean mechanism, 8-10 for a mechanism
   plus history and stakes. Never more than 10 (the Piper voice is fast, but the picture takes about 40 frames per second to
   draw, and a long video is a long upload). Longer is
   not better; never pad. The validator estimates the time from the word count (English 3.3 words and Hindi 2.45
   words per second, plus pauses) and wants it within 20 % of `target_minutes`. Rough budget: 5 min is about
   900 words in English (680 in Hindi), 10 min about 1,900 (1,450).
5. **Write the plan** as JSON that follows `shorts/sample_documentary_plan.json` and the schema
   (`python -m shorts.plan doc-schema`). `niche` (a name from `shorts/niches.py`), `topic`,
   `research_summary`, `mood`, `target_minutes`, and `english` and `hindi`, each with `title`,
   `description`, `tags` and `chapters` (each `title` + `scenes`). Every scene has `text`, `keyword`
   and `graphic`, exactly as in the Shorts (see the `explainer-diagram` skill for every graphic kind).
   - **Structure:** chapter 1 is a cold open (the most surprising thing, plus the question the
     video will answer). Then 3-8 chapters that each answer one sub-question, with a turn at the end
     of each ("But there is a catch."). The last chapter is why it matters, then the close.
   - **Chapters:** 3-12, each 2-12 scenes, the chapter `title` at most 50 characters (it becomes a
     YouTube chapter marker; the first starts at 0:00). The first scene of a chapter is usually a
     `title` scene whose headline is the chapter's name.
   - **Scenes** are 20-40 words (never more than 45), two or three spoken sentences. One idea per scene.
   - **A conversation, not a lecture.** The narrator talks to the viewer: at least one question per
     chapter (and at least four in total), a `chat` scene to play the "ask and answer", at least two
     `chat`, `quiz` or `myth` scenes in total, a guess before the big number, and a final question for
     the comments. Spoken, casual, second person, contractions.
   - **Variety:** at least 6 different graphic kinds. Show the mechanism with `flow`, `steps`, `build`,
     `cycle`; use `stat`, `bars`, `race`, `compare` for numbers; do not leave a long scene on a plain
     icon (a scene over 25 seconds should be a diagram, chat or bars, which keep moving).
   - **Hindi** is written like a native creator talks, in Devanagari, adapted from the English rather
     than translated word by word; its chapters, scenes and graphics match the English in structure.
   - Numbers and years as words in the narration. No emojis. Define every technical term when it first
     appears. Only use facts you verified.
   - `description`: 3-5 sentences plus 3-5 hashtags; the chapter timestamps are added automatically.
6. **Validate:** `python -m shorts.plan validate-doc plan.json` and fix everything it reports.
7. **Start the workflow:** the GitHub tool `actions_run_trigger`, `method: run_workflow`, owner
   `NayanKabiraj`, repo `blank-app`, `workflow_id: daily-shorts.yml`, `ref: main`,
   `inputs: {"format": "documentary", "plan_json": "<the whole plan as one compact JSON string>"}`. Leave out the
   other inputs (add `"dry_run": "true"` only when testing).
8. **Check the render.** A 10-minute documentary takes roughly 15-30 minutes in both languages. Look
   for the newest `daily-shorts.yml` run (`actions_list`, `list_workflow_runs`) and wait for
   `conclusion: success`; if it failed, read the failed job's log (`get_job_logs`) and report the
   error. Don't try to fix code.
9. **Report back** in a few lines: the topic, its score and the runner-up, both titles, the length and
   chapter list, whether the run succeeded, and where the videos are (YouTube links if uploaded,
   otherwise the run's artifacts, `videos-<n>`, kept for 14 days). Don't commit anything.
