# Daily Shorts task: instructions for the scheduled Claude task

Each morning a scheduled Claude task does the **research and script writing**, then
starts the GitHub Actions workflow `daily-shorts.yml`, which only **renders and uploads**.
To change how Claude picks topics or writes scripts, edit this file.

## Steps

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
     (6 words max) and `scenes` (6–9 of them, each with `text`, `graphic` and `visual_query`).
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
   - `graphic` is what the renderer draws for the scene (by default a **2D cartoon
     explainer** in a traditional-animation look, with a presenter character, a painted
     background and thought-bubble insets, drawn in code: see the `cartoon2d-explainer` skill
     in `.claude/skills/`; `stickman` and `cartoon3d` are alternatives), written in the
     **video's language** (Hindi graphics in Devanagari). Pick the `kind` that fits the line:
     - `title`: a big headline (use it for the hook and the closing line).
     - `stat`: one striking number with its unit in `headline` (`"71 km/s"`, `"1966"`,
       `"243 दिन"`). The number counts up on screen, so only use numbers you verified.
     - `keyword`: a key term in `headline` with a one-line explanation in `caption`.
     - `steps`: a process, with a short `headline` and 2–4 `items` in order.
     - `compare`: two things, with exactly 2 `items` and optionally 2 `values` drawn as bars.
     - Animated diagrams, drawn on a board the presenter points at (prefer these for the
       mechanism, since they *show* the process happening instead of naming it):
       - `flow`: 2–4 `items` in a chain; dots flow along the connectors (A moves to B moves to C).
       - `race`: exactly 2 `items` and 2 positive `values` (relative speeds or rates, from your
         verified numbers); dots race along two lanes and counters show how many arrived.
       - `build`: 2–4 `items` that stack up as layers (how parts combine).
       - `cycle`: 3–4 `items` around a loop with a token travelling round (cycles, feedback).
       See the "Pick a visual grammar" table in the `cartoon2d-explainer` skill. Use at least one
       diagram per video, and animate the verb ("heat flows out" means moving dots).
     For `title`, `keyword` and `stat` scenes, also set `prop` to the doodle (3D object in
     `cartoon3d`) that best
     stands for the idea: one of `star, bulb, coin, planet, globe, phone, bank, rocket,
     brain, chip, heart, clock, gear, atom, book, magnet, cloud`. Don't use the same prop in
     two scenes in a row.
     Optionally set `pose` to direct the presenter's reaction: one of `stand, point, wave,
     cheer, shrug, think, shock, walk` (for example `shock` on the reveal, `shrug` on a
     "nobody knows" line). Left out, it acts according to the scene kind.
     Keep `headline` ≤ 24 characters, `caption` ≤ 40 and each item ≤ 18. Vary the kinds
     across scenes, and use at least one `stat` when the topic has a good number.
   - `ai_prompt` (optional, **at most 2 scenes**; used only when `VISUAL_STYLE` is `motion` or
     `footage`, ignored in the default cartoon2d style and in stickman and cartoon3d): an English visual description for a free
     AI-generated video clip that replaces that scene's graphic. Use it where a real-looking
     shot beats a diagram: usually the hook and the analogy scene, never a `stat` or `steps`
     scene. Describe one concrete, cinematic shot of scenery, objects, nature, machines or
     space ("a glowing comet with a long dust tail crossing a starry sky", "macro shot of
     a smartphone chip with tiny glowing circuits"). Never ask for people, faces, text,
     logos or real brands. Use the **same** `ai_prompt` for the matching English and Hindi
     scene, so the clip is generated once and reused.
     Write it as a plain description of what is in the frame, as if seen from the ground
     or from nearby, in one sentence. Don't write negations like "no text" (the model reads
     them as requests), and never mention screens, dashboards, spacecraft cockpits, signs
     or anything with a display, because the model fills those with made-up text.
   - `visual_query` is always 2–3 concrete **English** keywords. In the default cartoon2d style it
     finds the **stock photo shown behind the presenter** in that scene, so make it match the line
     and give each scene a different one.
   - (Footage styles) `visual_query` is also used for stock footage. The
     footage comes from Pexels or Wikimedia Commons, so name things that are easy to film:
     scenery, nature, objects, animals, space imagery or time-lapses (for example
     `meteor timelapse`, `milky way timelapse`, `earth from orbit`, `ocean waves`). Never
     ask for people, faces, celebrities, politicians, brands or news events. Use different
     queries for different scenes.
   - Use only facts you verified. Never make up numbers.
4. **Validate the plan.** If the repo is checked out, run
   `pip install -q pydantic && python -m shorts.plan validate plan.json` and fix anything it
   reports. It also checks the hook (14 words or fewer, no "Today"/"Did you know"/greeting
   opener), scene length, the `hook_text` length and that `research_summary` lists the candidates. Otherwise check the word counts yourself.
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
   runner-up), both titles, which scenes got
   AI clips (from "Visual credits" in `videos/<date>/en_youtube.txt` on `main`), whether
   the run succeeded, and where the videos are: YouTube links if they were uploaded,
   otherwise `videos/<date>/` on `main`. Don't commit or push anything. The workflow
   records history on its own.
