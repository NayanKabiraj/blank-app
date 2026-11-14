# Daily Shorts task: instructions for the scheduled Claude task

Each morning a scheduled Claude task does the **research and script writing**, then
starts the GitHub Actions workflow `daily-shorts.yml`, which only **renders and uploads**.
To change how Claude picks topics or writes scripts, edit this file.

## Steps

The channel is an **explainer channel**: every Short answers one clear "how does X work?"
or "why does X happen?" question, in simple words, with motion graphics. It sticks to a
fixed set of explainer niches (`shorts/niches.py`) and rotates through them.

1. **Get today's niche.** In `NayanKabiraj/blank-app` on branch `main`, run
   `python -m shorts.niches next` (or read `shorts/niches.py` and `data/history.json`
   yourself). It prints the niche that has gone longest without a video, its angle,
   example topics, and the topics already covered in that niche. Use exactly that niche,
   and copy its `name` into the plan's `niche` field unchanged. If `NICHE_HINT.txt` exists
   at the repo root, it holds the owner's preferences and overrides the rotation.
2. **Pick and research one explainer topic in that niche.**
   - Phrase the topic as a single question a curious 15-year-old would ask ("How does
     UPI move money in two seconds?"). The examples are a starting point, not a list to
     work through in order.
   - Prefer a timely angle: use web search to check what people in India and worldwide are
     searching for or talking about this week, and pick a topic in today's niche that ties
     into it (a launch, a season, an event in the sky, a festival). If nothing fits, choose
     an evergreen question.
   - Don't repeat anything in `already_covered` or `data/history.json`.
   - Avoid breaking tragedies, politics, elections, medical or investment advice, brands
     in a promotional way, and real private individuals.
   - Find out how it actually works: the 3–4 step mechanism, one striking verified number,
     and one everyday analogy that makes it click. Check every fact against a reliable
     source (official sites, encyclopedias, universities, established science outlets).
3. **Write the plan** as JSON following `shorts/sample_plan.json` exactly (the full schema
   is in `shorts/plan.py`). For the script voice (surprising-claim hook, one witty line,
   "then someone checked" twist, physical analogy) and for matching each line to a visual,
   follow the `animated-explainer-method` skill in `.claude/skills/`:
   - `niche` (exactly the name from step 1), `topic` (the question), `research_summary`
     (why this topic today, how it works, the facts and their sources),
     and `mood`, which must be one of `calm`, `upbeat`, `dramatic`, `inspiring`, `mysterious`.
   - `english` and `hindi`, each with `title` (80 characters max, no hashtags),
     `description` (2–3 sentences plus 3–5 hashtags), `tags` (8–12), `hook_text`
     (6 words max) and `scenes` (6–9 of them, each with `text`, `graphic` and `visual_query`).
   - Length: the English narration is 120–140 words in total and the Hindi narration is
     105–125 words, which gives 45–55 seconds of speech.
   - Follow the explainer structure:
     1. **Hook** (scene 1): the question, or a surprising claim that makes viewers want the
        answer, in under 3 seconds. `graphic.kind`: `title`.
     2. **Short answer** (scene 2): the answer in one sentence. Usually a `keyword`.
     3. **How it works** (2–3 scenes): the mechanism step by step, one idea per scene.
        Use a `steps` graphic for the sequence.
     4. **The number** (1 scene): one striking verified number that shows the scale.
        `stat`.
     5. **Make it click** (1 scene): an everyday analogy or a before/after comparison.
        `compare` or `keyword`.
     6. **Close** (last scene): a one-line takeaway, then "Follow to understand one new
        thing every day" (Hindi: "रोज़ एक नई चीज़ समझने के लिए फ़ॉलो करें"). `title`.
   - Explain like a good teacher: plain words, define any technical term the first time
     you use it, and no jargon left unexplained.
   - Use short, natural spoken sentences. Write numbers and years as words, for example
     "nineteen sixty-nine". No emojis, and no hashtags in the narration.
   - Write the Hindi in natural everyday spoken Hindi in **Devanagari** script, adapting
     the English rather than translating it word for word. Put the Hindi title and
     description in Hindi.
   - `graphic` is what the renderer draws for the scene (by default a **3D cartoon** made
     in code: see the `cartoon-explainer` skill in `.claude/skills/`), written in the
     **video's language** (Hindi graphics in Devanagari). Pick the `kind` that fits the line:
     - `title`: a big headline (use it for the hook and the closing line).
     - `stat`: one striking number with its unit in `headline` (`"71 km/s"`, `"1966"`,
       `"243 दिन"`). The number counts up on screen, so only use numbers you verified.
     - `keyword`: a key term in `headline` with a one-line explanation in `caption`.
     - `steps`: a process, with a short `headline` and 2–4 `items` in order.
     - `compare`: two things, with exactly 2 `items` and optionally 2 `values` drawn as bars.
     For `title`, `keyword` and `stat` scenes, also set `prop` to the 3D object that best
     stands for the idea: one of `star, bulb, coin, planet, globe, phone, bank, rocket,
     brain, chip, heart, clock, gear, atom, book, magnet, cloud`. Don't use the same prop in
     two scenes in a row.
     Keep `headline` ≤ 24 characters, `caption` ≤ 40 and each item ≤ 18. Vary the kinds
     across scenes, and use at least one `stat` when the topic has a good number.
   - `ai_prompt` (optional, **at most 2 scenes**; used only when `VISUAL_STYLE` is `motion` or
     `footage`, ignored in the default 3D cartoon style): an English visual description for a free
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
   - `visual_query` is always 2–3 concrete **English** keywords for stock footage. The
     footage comes from Pexels or Wikimedia Commons, so name things that are easy to film:
     scenery, nature, objects, animals, space imagery or time-lapses (for example
     `meteor timelapse`, `milky way timelapse`, `earth from orbit`, `ocean waves`). Never
     ask for people, faces, celebrities, politicians, brands or news events. Use different
     queries for different scenes.
   - Use only facts you verified. Never make up numbers.
4. **Validate the plan.** If the repo is checked out, run
   `pip install -q pydantic && python -m shorts.plan validate plan.json` and fix anything it
   reports. Otherwise check the word counts yourself.
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
7. **Report back** in a few lines: the niche, the question, both titles, which scenes got
   AI clips (from "Visual credits" in `videos/<date>/en_youtube.txt` on `main`), whether
   the run succeeded, and where the videos are: YouTube links if they were uploaded,
   otherwise `videos/<date>/` on `main`. Don't commit or push anything. The workflow
   records history on its own.
