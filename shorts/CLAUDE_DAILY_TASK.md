# Daily Shorts task: instructions for the scheduled Claude task

Each morning a scheduled Claude task does the **research and script writing**, then
starts the GitHub Actions workflow `daily-shorts.yml`, which only **renders and uploads**.
To change how Claude picks topics or writes scripts, edit this file.

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

**Strategy:** the research, packaging (title + thumbnail), retention and QA rules in the `video-strategy` skill apply to every
video. In this task that means: a title that passes the curiosity test, a **thumbnail** (below), a first line that proves the premise,
a payoff, and a pointer to the next video in the close.

**Thumbnail.** The workflow draws and uploads one per language (`shorts/director/thumbnail.py`). Write `thumbnail_text` for both
`english` and `hindi`: one short sentence (up to 8 words, 46 characters at most) that show the *consequence*, not a copy of the title ("Your body wants
fur", not "Why do we get goosebumps?"). Without it the hook text is used.

The channel is an **explainer channel**: every Short answers one clear "how does X work?"
or "why does X happen?" question, in simple words, with animated explainer graphics. **The
goal of every video is watch-through and shares**: pick the question people are itching to
have answered, then script it so nobody swipes away. Niches (`shorts/niches.py`) are only
labels and a variety guard: **the topic decides the niche, not the other way round.**

1. **See what the channel has done.** In `NayanKabiraj/blank-app` on branch `main`, run
   `python -m shorts.niches recent`. It prints the last videos (niche and topic), how often
   each niche was used lately, the niches that are "cooling down" (used in the last two
   videos), and the list of niches with their angle. Never repeat a topic or a close
   variant. If `NICHE_HINT.txt` exists at the repo root, it holds the owner's preferences
   and overrides everything below.
2. **Choose the topic with the best chance of going viral.**
   - **Collect at least 10 candidate questions across ALL niches**, each phrased as one
     question a curious 15-year-old would ask ("How does UPI move money in two seconds?").
     Sources, in this order:
     1. *This week's talk* (web search; India first, then worldwide): science and tech news,
        launches, sky events, weather and season changes, festivals, exam season, viral
        gadgets or videos. For each, ask "what is the *why/how* behind it that people
        wonder about?". Also search what people type: "why does", "how does", "how do" with
        a trending keyword, and "most searched why questions India".
     2. *Everyday mysteries*: things billions of people see or use daily and almost nobody can
        explain (phone, body, food, money, weather, trains, cricket, chai, the sky).
     3. *Proven performers*: if the vidIQ tools are available, spend at most three cheap calls
        (for example outliers or keyword research for explainer Shorts) to see which
        question types over-perform. If they are missing or credits are low, skip them
        without comment.
   - **Score every candidate 1–5 on each of these, and add them up** (max 40):
     1. *Curiosity gap*: seen by everyone, understood by few. Does the question create an itch?
     2. *Universality*: how many viewers have personally met this?
     3. *Timeliness*: tied to something in the next ~7 days or trending now (5), seasonal (3),
        evergreen (2).
     4. *Search demand*: would people type this exact question?
     5. *Surprise*: a counter-intuitive truth or a striking verified number (below 3: reject).
     6. *Visual*: the mechanism can be shown as moving dots, a race, layers, a loop or steps,
        with a countable number (below 3: reject).
     7. *Shareability*: would someone send it to a friend with "wait, really?".
     8. *Verifiability and safety*: facts you can confirm from reliable sources, and no breaking
        tragedies, politics, elections, medical or investment advice, promotional brands or
        real private individuals (a failure here is an automatic reject).
   - Pick the highest total (tie-break: Surprise, then Timeliness). Its closest niche in
     `shorts/niches.py` becomes the plan's `niche` (copy the `name` unchanged). **Variety
     guard:** if the winner's niche is one of the two cooling-down niches, take the best
     candidate from a different niche instead, unless the winner beats it by 4 points or
     more. If nothing scores well, fall back to `python -m shorts.niches next`.
   - **Title test before you commit:** can you state the video's title as a curiosity question
     in 60 characters or fewer, with the key word in the first 40, and can the video fully pay
     it off? Clickbait that the video does not answer is rejected.
   - **Research it properly.** Find the 3–4 step mechanism, one striking verified number
     (check it against at least two reliable sources and, when they differ, say which you
     used and why), and one everyday analogy that makes it click. Prefer official sites,
     encyclopedias, universities and established science outlets.
   - **Write the audit trail into `research_summary`**: start with "Candidates:" and the top
     three with their scores, then one line on why the winner beat the others (and why now),
     then the mechanism, the facts and their sources.
3. **Write the plan** as JSON following `shorts/sample_plan.json` exactly (the full schema
   is in `shorts/plan.py`). For the script voice (surprising-claim hook, one witty line,
   "then someone checked" twist, physical analogy) and for matching each line to a visual,
   follow the `animated-explainer-method` skill in `.claude/skills/`:
   - `niche` (exactly the name chosen in step 2), `topic` (the question), `research_summary`
     (why this topic today, how it works, the facts and their sources),
     and `mood`, which must be one of `calm`, `upbeat`, `dramatic`, `inspiring`, `mysterious`.
   - `english` and `hindi`, each with `title` (80 characters max, no hashtags),
     `description` (2–3 sentences plus 3–5 hashtags), `tags` (8–12), `hook_text`
     (6 words max) and `scenes` (6–9 of them, each with `text`, an optional `keyword` and a `graphic`).
   - Length: the English narration is 120–140 words in total and the Hindi narration is
     105–125 words, which gives 45–55 seconds of speech.
   - Before writing, state the learning goal in one sentence ("after this the viewer can answer:
     ___"). Every scene proves one claim that serves it; cut anything that doesn't.
   - Pace the narration at about 2–2.4 English words per second (the word limits below already
     fit this). Don't write at the limit: it sounds rushed.
   - **Script for retention.** A Short is won in the first three seconds and lost at every dull
     sentence. Read `.claude/skills/animated-explainer-method/references/viral-playbook.md` for
     hook formulas with examples, then write the scenes as this curve:
     1. **Hook** (scene 1, `title`): at most 14 words, spoken in about 4 seconds. Start with the
        most surprising true thing, never with "Today", "In this video", a greeting, "Did you
        know" or a definition. Use one formula: an impossible-sounding fact, "you already live
        this", a specific number, a contradiction, or a challenge. It must plant a question the
        viewer needs answered.
     2. **Stakes and promise** (scene 2, `keyword`): why this matters to *you*, plus a tease of the
        payoff ("The answer is hiding in every sunbeam."). Do not give the answer away yet.
     3. **How it works** (2–3 scenes: `flow`, `steps`, `build` or `cycle`): one idea per scene.
        Each scene's first sentence must create a reason to hear the second, and each scene
        should end on a mini-cliffhanger or a turn ("But there is a catch.", "Now it gets
        weird."). Re-hook with a new question, number or twist about every 8–10 seconds. Never
        open a scene with a flat connective such as "Next" or "Also".
     4. **The number** (`stat` or `race`): your most striking verified number, placed about
        60–70 % of the way through, ideally as a countable difference.
     5. **Make it click** (`compare` or `keyword`): an everyday analogy or a before/after
        (India-first when natural: chai, auto-rickshaw, cricket, UPI, the metro, the monsoon).
     6. **Payoff** (`keyword`): the answer in 12 words or fewer, reusing the hook's own words so
        the loop closes ("So the sky is blue because...").
     If there is room, add a **boundary** line before the close: where the rule stops working
        ("on a hot day it flips"). It stops viewers over-generalising.
     7. **Close** (last scene, `title`): one punchy takeaway that echoes the hook's wording, so
        the Short loops naturally when it replays, then the follow line: "Follow to understand
        one new thing every day" (Hindi: "रोज़ एक नई चीज़ समझने के लिए फ़ॉलो करें").
   - Engagement rules: sentences of 12 words or fewer with one idea each, a short punch after a
     longer line, second person ("you", "your phone"), concrete nouns, one "wait, what?" moment
     and one "oh, that makes sense" moment, at most one dry joke. Keep to the word limits;
     do not pad.
   - **Make it a conversation, not a lecture.** The narrator talks *to* the viewer and answers back:
     - Scene 1 or 2 asks the viewer something ("Weird, right?", "Ever felt this at a scary scene?").
     - At least 3 scenes contain a question (the validator checks), and the narrator answers each one in the
       next breath ("Why? Because...").
     - One `chat` scene plays the viewer-asks, video-answers exchange as text bubbles (viewer bubble, answer
       bubble, "wait, what?" bubble, answer). Keep bubbles to a few words.
     - One challenge for the viewer: a `quiz` ("Quick quiz: what pulls the hair up?" three options, then the
       reveal) or a `myth` ("Think it keeps you warm? That's the myth.").
     - Ask for a guess before the big number ("Guess how many...") and react after it ("Yes, five million!").
     - The last scene ends with a question the viewer can answer in the comments ("Which one is you? Tell me
       below!"), then the follow line. Hindi: the same, in natural spoken Hindi ("कमेंट में बताइए!").
     Spoken, casual, second person, contractions, short replies ("Right?", "Exactly.", "Nope.").
   - `hook_text` is a teaser, not a summary: 5 words or fewer that make people stay ("It sees you
     in the dark"). The `title` is the curiosity question from your title test, 60 characters or
     fewer if you can (80 is the hard limit). The first line of the `description` states the
     question and teases the answer.
   - Explain like a good teacher: plain words, define any technical term the first time
     you use it, and no jargon left unexplained.
   - Set `keyword` on most scenes: the stressed word or short phrase in that scene's `text`,
     copied exactly (in the Hindi scenes, a Hindi word from the Hindi text). The animation lands
     on it and the caption highlights it. One per scene, never the first word.
   - Use short, natural spoken sentences. Write numbers and years as words, for example
     "nineteen sixty-nine". No emojis, and no hashtags in the narration.
   - Write the Hindi like a native Hindi creator talks, not a translation: its hook may use a
     different formula if that lands harder, and common loan words (फ़ोन, ऐप, ट्रेन) are fine.
     Natural everyday spoken Hindi in **Devanagari** script, adapting
     the English rather than translating it word for word. Put the Hindi title and
     description in Hindi.
   - `graphic` is what the animation draws for the scene. The channel has **one look**: the whiteboard
     explainer (a hand draws marker diagrams in code, a smiling sun is carried from scene to scene, caption
     pills with a yellow highlighter on the keyword; see the `explainer-diagram` skill in `.claude/skills/`). Write graphic text in the
     **video's language** (Hindi graphics in Devanagari). Pick the `kind` that acts out the line:
     - `title`: a big headline with an icon (the hook and the closing line).
     - `keyword`: a key term in `headline`, a one-line explanation in `caption`, an icon.
     - `stat`: one striking number with its unit in `headline` (`"71 km/s"`, `"1966"`, `"243 दिन"`); put
       the label in `caption`. It counts up, so only use numbers you verified.
     - `steps`: a process, 2–4 `items` in order, one lit at a time.
     - `flow`: 2–4 `items` in a chain; dots flow along the connectors (A moves to B moves to C).
     - `build`: 2–4 `items` that stack up as layers (how parts combine).
     - `cycle`: 3–4 `items` around a loop with a token travelling round.
     - `race`: exactly 2 `items` and 2 positive `values` (relative speeds or rates); dots race, counters show who arrived.
     - `compare`: exactly 2 `items`, optional 2 `values`; two discs sized by the values.
     - `bars`: 2–4 `items` and the same number of positive `values`; bars grow and count up (e.g. how much
       more, for several things).
     - `chat`: 2–4 `items` as text bubbles; the 1st, 3rd are the viewer asking, the 2nd, 4th are the answers.
     - `quiz`: `headline` = the question (up to 48 characters), 2–4 `items` = options, `answer` = the
       0-based index of the right option. Put the answer's word as the scene's `keyword` so the reveal lands on it.
     - `myth`: `items` = [the common myth, the truth], `headline` = a few words naming the topic.
     Use at least 4 different kinds per video, at least one diagram of the mechanism (`flow`, `steps`,
     `build` or `cycle`; animate the verb) and at least one of `chat`, `quiz`, `myth`.
     For `title` and `keyword` scenes, also set `prop` to the icon that stands for the idea, one of `star,
     bulb, coin, planet, globe, phone, bank, rocket, brain, chip, heart, clock, gear, atom, book, magnet,
     cloud`. Don't use the same prop in two scenes in a row.
     Keep `headline` ≤ 28 characters (quiz ≤ 48), `caption` ≤ 40, each item ≤ 18 (chat bubbles, myth and quiz options ≤ 36).
   - Use only facts you verified. Never make up numbers.
4. **Validate the plan.** If the repo is checked out, run
   `pip install -q pydantic && python -m shorts.plan validate plan.json` and fix anything it
   reports. It also checks the hook (14 words or fewer, no "Today"/"Did you know"/greeting
   opener), scene length, the `hook_text` length, that `research_summary` lists the candidates, and the
   conversation rules (3+ questions, one early, a question at the end, a chat/quiz/myth scene, 4+ kinds). Otherwise check the word counts yourself.
5. **Start the workflow.** Use the GitHub tool `actions_run_trigger` with
   `method: run_workflow`, owner `NayanKabiraj`, repo `blank-app`,
   `workflow_id: daily-shorts.yml`, `ref: main`, and
   `inputs: {"plan_json": "<the whole plan as one compact JSON string>"}`.
   Leave out the other inputs.
6. **Check the render.** It takes about 8–10 minutes. Then find the newest
   `daily-shorts.yml` run with `actions_list` (`method: list_workflow_runs`,
   `resource_id: daily-shorts.yml`, `perPage: 1`) and check that it finished with
   `conclusion: success`. If it's still running, check again a few minutes later. If it
   failed, read the failed job's log with `get_job_logs` (`run_id`, `failed_only: true`,
   `return_content: true`) and include the error in your report. Don't try to fix code.
7. **Report back** in a few lines: the niche, the question and its total score (and the
   runner-up), both titles, which
   scene kinds were used, whether
   the run succeeded, and where the videos are: YouTube links if they were uploaded,
   otherwise `videos/<date>/` on `main`. Don't commit or push anything. The workflow
   records history on its own.

**Closing line:** do not write a "thanks for watching / like, share and subscribe" ending - the pipeline appends it to every video automatically (shorts/outro.py).

**Animation pack (strict, every video, scheduled runs included).** After the plan is written, write the video's animation: read `generated_animations/AUTHORING.md` and
an existing pack (`generated_animations/scenes/gps_short/`, `tides_doc/`) as a model, create `generated_animations/scenes/<pack>/` (`shots.json` + `scene_NNN.py` shots with
scene-specific motion animation for what each sentence says, English and Hindi labels; use a new unique `<pack>` id such as `<topic-slug>-<date>`), set `animation_pack` in both
`english` and `hindi`, run `python -m generated_animations scan <pack>`, render a low-res preview (`SHORTS_FAKE_TTS=1 GA_PIXEL_SCALE=0.4`, see AUTHORING.md) and inspect the frames,
fix defects. Then commit ONLY that new folder to `main` with the GitHub tool (`push_files`) before starting the workflow (owner-authorised exception to "scheduled tasks commit
nothing"). `python -m shorts.plan validate` / `validate-doc` fails the plan until every scene is covered by a shot. No scene may be a static card: the picture must be dynamic with a lot of motion.


**English only (owner instruction, 22 Nov 2026):** write only the `english` block (omit `hindi`), and set `animation_pack` in `english`. Do not render or upload Hindi.

**Intro (owner instruction, 22 Nov 2026):** scene 1 is the hook (a surprising fact, no greeting). **Scene 2 is the intro**: 18-22 words (about 7 seconds; the promise lands by second 5) that say what the video is about and what the
viewer will get - name the 2-3 things they will see and the question that gets answered ("In this video you'll see X, Y and Z - and why ...") - and give them a reason to stay to the end.
The validator rejects a plan whose scene 2 has no such promise. Count the intro in the word budget; write an animation shot for it (a preview of the 2-3 things, e.g. icons popping in as each is named).

**Thumbnail (owner instruction, 22 Nov 2026):** write `thumbnail_question` in the `english` block: 3-8 words, ends with "?", about the topic ("What if the Moon vanished?"). The thumbnail is built
automatically: that question BIG, the presenter's face with an open-mouth reaction, and a topic picture (`shorts/thumb_avatar.py`). The validator requires it.


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

## Daily production plan (owner instruction, 24 Nov 2026) - 6 uploads a day (10 when the quota is raised)
The current target and the 14-day review rules are in `strategy/learnings.md` ("DECISION"; change the target there when the owner raises the quota). Per day: **3 Short topics x EN+HI = 6 uploads**; on **Sunday** 2 Short
topics x EN+HI + 1 documentary x EN+HI (documentary follows `shorts/CLAUDE_DOCUMENTARY_TASK.md`, only when a Short on its topic got traction, else a third Short topic).
1. Do the channel check, trending digest and learnings (above) ONCE, then pick the topics in this priority order (a short day still ships the best first): (1) everyday-tech / phone / home explainer with a personal
   hook, (2) a timely topic from this week or a Space & Universe / Earth & Nature explainer, (3) ONE **Horror & Suspense** story (niche "Horror & Suspense": an ORIGINAL fictional story, ~38-45 s, hook + twist, bloodless and not
   gory, no real people/places/events/brands as victims; the description says it is fiction ("A fictional story.") and Claims says "FICTIONAL ASSUMPTION - original fiction"; the intro scene may use "Tonight: ..." /
   "In this story ..."). At the 10-a-day target add (4) a second explainer from the research queue and (5) a wildcard. Never repeat a topic; check `python -m shorts.niches recent`.
2. For each topic in order: research (web search for explainers) -> plan JSON with BOTH `english` and `hindi` blocks (same scenes; Hindi narration in Devanagari, Hindi title <= 90 characters, Hindi
   `thumbnail_question`, the same `animation_pack` in both) -> ONE bilingual vox pack (`vox.L(ctx, en, hi)` / `T[ctx.lang]`; check an English AND a Hindi preview frame set for text that is too wide) -> scan -> preview ->
   validate (`python -m shorts.plan validate`) -> commit only the pack folder (rule 7) -> dispatch `daily-shorts.yml` with `plan_json` and `langs` "en,hi".
3. **Dispatch rule**: GitHub keeps only ONE pending run per concurrency group, so never queue more than one: dispatch topic k+1 only when run k is `in_progress` or finished and no other run is queued. Author the next topic
   while the previous one renders.
4. Quality over quota: if time runs short, ship fewer topics rather than rush; never ship a pack that failed frame inspection. Report how many of the day's uploads happened or queued and why any are missing.


## Growth and monetization (owner instruction, 24 Nov 2026) - read `strategy/monetization.md`
The goal of every video is subscribers and watch time toward the Partner Program, without risking it. Write a `Growth:` line in `research_summary`: which lever this video pulls (hook/retention, subscribe trigger such as a series promise in
the first 20 s, series follow-up with `next_video` and the pinned comment, reach) and the policy check (its own angle and structure, not a clone of yesterday's video; nothing off-putting; no health/finance/legal advice). Use the
`monetization` block of the channel check (subscribers to 1,000, watch hours, subscribers per 1,000 views) to decide what to change next.
