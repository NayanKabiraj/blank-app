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
3. **Packaging gate.** The title explains the premise, the thumbnail shows the consequence (`thumbnail_text`, one short sentence (up to 8 words), never a copy of
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
`thumbnail_text` for English and Hindi (one short sentence, up to 8 words and 46 characters, showing the consequence rather than repeating the title);
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

**Closing line:** do not write a "thanks for watching / like, share and subscribe" ending - the pipeline appends it to every video automatically (shorts/outro.py).

**Animation pack (strict, every video, scheduled runs included).** After the plan is written, write the video's animation: read `generated_animations/AUTHORING.md` and
an existing pack (`generated_animations/scenes/gps_short/`, `tides_doc/`) as a model, create `generated_animations/scenes/<pack>/` (`shots.json` + `scene_NNN.py` shots with
scene-specific motion animation for what each sentence says, English and Hindi labels; use a new unique `<pack>` id such as `<topic-slug>-<date>`), set `animation_pack` in both
`english` and `hindi`, run `python -m generated_animations scan <pack>`, render a low-res preview (`SHORTS_FAKE_TTS=1 GA_PIXEL_SCALE=0.4`, see AUTHORING.md) and inspect the frames,
fix defects. Then commit ONLY that new folder to `main` with the GitHub tool (`push_files`) before starting the workflow (owner-authorised exception to "scheduled tasks commit
nothing"). `python -m shorts.plan validate` / `validate-doc` fails the plan until every scene is covered by a shot. No scene may be a static card: the picture must be dynamic with a lot of motion.


**English only (owner instruction, 22 Nov 2026):** write only the `english` block (omit `hindi`), and set `animation_pack` in `english`. Do not render or upload Hindi.

**Intro (owner instruction, 22 Nov 2026):** the cold open is scene 1 (the story hook, no greeting). **Scene 2 is the intro**: up to 48 words saying what the documentary covers, the
2-4 questions or chapters the viewer will get answered, and why it matters to them ("In this video you'll find out X, see Y, and learn Z"). The validator rejects a plan without it.
Write an animation shot for it (a roadmap of the chapters appearing as each is named).

**Thumbnail (owner instruction, 22 Nov 2026):** write `thumbnail_question` in the `english` block: 3-8 words, ends with "?" ("Can anything escape a black hole?"). The thumbnail shows it BIG next to the presenter's face.


## Channel check, research template and SEO (owner instruction, 23 Nov 2026) - do these in order

**Step 0, BEFORE choosing a topic: the channel check.** Run `python -m shorts.channel_trends summary` (it reads `data/channel_trends.json`, refreshed daily by `channel-trends.yml` from the
YouTube Data + Analytics APIs) and, if the vidIQ tools are connected, `vidiq_user_channels` (0 credits; spend paid vidIQ calls only when `vidiq_balance` shows at least 10 credits).
Read the digest: Shorts vs documentaries, views and average view percentage per niche, the top and bottom videos, and its `signals`. Then decide and RECORD what you changed:
double down on the niche, cluster or format that is working, change the hook style of videos with a low average view percentage, and avoid the weakest niche unless a candidate clearly beats it.
With fewer than about 8 videos of data the signals are hints, not proof; say so. If the digest says `available: false`, write `Channel check: NOT AVAILABLE: <the reason>` and continue with the normal rubric.
`research_summary` must contain a line starting `Channel check:` (the validator checks it).

**Research template.** `research_summary` also contains `Claims:` (a table: each number or claim, two sources, status VERIFIED / PARTIALLY VERIFIED / FICTIONAL ASSUMPTION / UNVERIFIED; where sources disagree say which
one you used and hedge the narration, e.g. "eleven kilometres" for 10,935 m vs 10,994 m) and `Gap:` (the angle the top three existing videos on this question miss, and how this video covers it). Before dispatching, re-check
every number in the narration against the Claims table.

**SEO rules (checked by the validator where possible).** Title: 65 characters at most, the topic keyword within the first 40 characters, a curiosity gap that the video pays off, never a copy of the thumbnail question.
Tags: 5-8 accurate tags, the exact topic phrase first (YouTube calls tags a minor signal; title, thumbnail and description matter more). Description: the keyword and the promise in the first two lines, then 2-3 hashtags
(the first three show above the title); a `Sources:` line with up to 3 of the plan's research URLs is appended automatically. Sources of these rules: YouTube's own help pages for tags and Test & Compare; the rest
are vendor guides and unverified, so treat numeric claims (CTR benchmarks, retention rates) as hypotheses to test against the channel's own data.


## Vox look (owner instruction, 23 Nov 2026)
New animation packs use the **vox look** (paper cut-out explainer style): `"look": "vox"` in `shots.json`, drawn with `generated_animations/shared/vox.py` as described in the "vox look" section of
`generated_animations/AUTHORING.md` (model pack: `generated_animations/scenes/time_flies_vox/`). The validator rejects a pack without it. The avatar stays, as a sticker. No photos are fetched (drawn paper cut-outs only), so no network
or image licences are involved.

**Newspaper clippings (vox look, owner instruction, 23 Nov 2026):** when a scene reports a dated/historical event, a named incident, an announcement, discovery, record, law or study, show it as a newspaper clipping that flies in
(`vox.newspaper` + `vox.arrive`; rules and timing in AUTHORING.md, "Newspaper clippings: when to use them"). You decide per scene; keep headlines and dates inside the verified Claims.

## Google authorization (phone-first)
After the workflow run, if an upload is queued because of `invalid_grant` ("Google authorization required"), fetch `main` and print `python -m shorts.ytauth banner` in your final message so the owner can tap the link
(then Allow, then "Submit new issue"). Never print tokens. See `docs/oauth-mobile.md`.


## Learnings loop (owner instruction, 24 Nov 2026) - read BEFORE choosing the topic
1. Run `python -m shorts.channel_trends summary` AND `python -m shorts.channel_trends trending` (what YouTube itself pushes in Education / Science & Technology: title shapes, lengths, recurring words, top titles).
2. Read `strategy/learnings.md`. Apply its Rules (38-45 s Shorts = 100-112 words with the payoff by second ~22 and a looping last line; hook about the viewer's own life in the first 2 seconds; timely beats
   evergreen when free; documentaries only after a Short on the topic got traction; series promise inside the first 20 s) and run its Tests.
3. Do a quick trend check with WebSearch for THIS WEEK (sky events, launches, news) and look at the trending digest; adapt a trending topic to a personal hook instead of copying a title.
4. Write `Learning applied:` in `research_summary` (which rule or test, what you changed) and, if the new channel data says something new, add ONE dated evidence line to `strategy/learnings.md` (never invent numbers).
5. Hindi (when `VIDEO_LANGS` includes `hi`): the Hindi video follows the same vox look - the pack writes every on-screen string with `vox.L(ctx, "EN", "हिन्दी")` or `T[ctx.lang]`
   (the validator fails a Hindi pack without it); same shots, same sentence indices.
6. Documentary gate: the learnings file says documentaries are the weak format (11 % viewed). Only produce one when a Short on the same topic got traction, <= 4 min, one a week at most, unless the owner asks otherwise.

## Schedule change (24 Nov 2026)
Documentaries run on **Sunday only**, English + Hindi (2 of that day's 6 uploads), gated by the learnings file (a Short on the topic must already have traction; <= 4 min until a documentary beats 25 % viewed).


## Growth and monetization (owner instruction, 24 Nov 2026) - read `strategy/monetization.md`
The goal of every video is subscribers and watch time toward the Partner Program, without risking it. Write a `Growth:` line in `research_summary`: which lever this video pulls (hook/retention, subscribe trigger such as a series promise in
the first 20 s, series follow-up with `next_video` and the pinned comment, reach) and the policy check (its own angle and structure, not a clone of yesterday's video; nothing off-putting; no health/finance/legal advice). Use the
`monetization` block of the channel check (subscribers to 1,000, watch hours, subscribers per 1,000 views) to decide what to change next.
