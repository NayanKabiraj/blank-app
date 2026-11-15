# Documentary task: instructions for the Claude task that writes a long-form video

The channel makes two kinds of video: the daily **Shorts** (`CLAUDE_DAILY_TASK.md`) and
**documentaries** of **5 to 15 minutes**, in **English and Hindi**, in the same explainer look
(dark navy, flat diagrams, the guiding spark, chat bubbles, quizzes) but landscape, 1920x1080.
A documentary answers one big question properly instead of a quick "why": it has chapters, a
story and a real payoff. Claude researches and writes the plan; the GitHub workflow
`daily-shorts.yml` (with `format: documentary`) renders it with the same Piper voice and synthesized music, and uploads it
(if the YouTube secrets exist) with automatic chapter markers.

Run this task on its own schedule (for example weekly). It does not replace the daily Shorts.

## Steps

1. **Check the history.** In `NayanKabiraj/blank-app` on `main`, read `data/documentary_history.json`
   (it may not exist yet), `data/history.json` and `python -m shorts.niches recent`. Never repeat a
   topic. If `NICHE_HINT.txt` exists, it overrides the choices below.
2. **Choose a topic that deserves 5-15 minutes.** It must be big enough to have 4-8 chapters, with a
   mechanism, a surprise, real numbers and a human stake: "How the Indian monsoon works", "What
   actually happens when you press 'Pay' on UPI", "Why the Moon keeps drifting away". Collect 6+
   candidates across niches (this week's news, anniversaries, seasons, everyday mysteries), score
   them like the Shorts (curiosity, universality, timeliness, search demand, surprise, visual,
   shareability, verifiability and safety; max 40) and take the best. A good documentary topic is also
   a good Shorts topic: you can cut a Short from it later.
   Avoid breaking tragedies, politics, elections, medical or investment advice, promotional brands.
3. **Research it properly** (web search; official sites, universities, encyclopedias, established
   outlets): the mechanism in 4-8 steps, 3+ striking numbers (each from two sources; say which you
   used), one myth people believe, one analogy, one surprise, one "what if it fails" angle. Write
   the audit trail into `research_summary`: start with "Candidates:" (top 3 with scores), why the
   winner won, then the facts and their sources. Mark approximations ("roughly", "about").
4. **Pick the length** (`target_minutes`, 5-15): 5 for a single clean mechanism, 8-10 for a mechanism
   plus history and stakes, 12-15 only when there really are that many strong chapters. Longer is
   not better; never pad. The validator estimates the time from the word count (English 3.1 words and Hindi 2.85
   words per second, plus pauses) and wants it within 20 % of `target_minutes`. Rough budget: 5 min is about
   850 words in English (780 in Hindi), 10 min about 1,800 (1,600), 15 min about 2,700 (2,450).
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
