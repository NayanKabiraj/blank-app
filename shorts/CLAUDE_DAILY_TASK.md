# Daily Shorts task: instructions for the scheduled Claude task

Each morning a scheduled Claude task does the **research and script writing**, then
starts the GitHub Actions workflow `daily-shorts.yml`, which only **renders and uploads**.
To change how Claude picks topics or writes scripts, edit this file.

## Steps

1. **Read the channel's memory.** In `NayanKabiraj/blank-app` on branch `main`, read
   `data/history.json`, which lists past videos. If `NICHE_HINT.txt` exists at the repo
   root, read it too: it holds the owner's niche preferences.
2. **Research today's niche.** Use web search to see what is trending today in India and
   worldwide (Google Trends, news, YouTube Shorts trends) and pick **one niche and one
   specific topic**:
   - It should make people curious enough to watch a 40–60 second Short to the end.
   - Avoid breaking tragedies, politics, elections, medical or financial advice, and real
     private individuals.
   - It must be easy to show with generic stock footage (no celebrities or brands needed).
   - It must work in both English and Hindi.
   - Don't repeat a topic from `history.json`, and rotate the niche from day to day
     (science, space, history, psychology, tech, nature, money habits, geography,
     inventions, human body, animals, productivity, and so on).
   - Collect 4–6 accurate, surprising facts and check each one against a reliable source.
3. **Write the plan** as JSON following `shorts/sample_plan.json` exactly (the full schema
   is in `shorts/plan.py`):
   - `niche`, `topic`, `research_summary` (why this topic today, the facts and their sources),
     and `mood`, which must be one of `calm`, `upbeat`, `dramatic`, `inspiring`, `mysterious`.
   - `english` and `hindi`, each with `title` (80 characters max, no hashtags),
     `description` (2–3 sentences plus 3–5 hashtags), `tags` (8–12), `hook_text`
     (6 words max) and `scenes` (6–9 of them, each with `text`, `graphic` and `visual_query`).
   - Length: the English narration is 120–140 words in total and the Hindi narration is
     105–125 words, which gives 45–55 seconds of speech.
   - Scene 1 is a hook that grabs attention in under 3 seconds. Then tell the facts as a
     short story, one idea per scene. The last scene asks viewers to follow for a new fact
     every day.
   - Use short, natural spoken sentences. Write numbers and years as words, for example
     "nineteen sixty-nine". No emojis, and no hashtags in the narration.
   - Write the Hindi in natural everyday spoken Hindi in **Devanagari** script, adapting
     the English rather than translating it word for word. Put the Hindi title and
     description in Hindi.
   - `graphic` is what the motion-graphics renderer draws for the scene, written in the
     **video's language** (Hindi graphics in Devanagari). Pick the `kind` that fits the line:
     - `title`: a big headline (use it for the hook and the closing line).
     - `stat`: one striking number with its unit in `headline` (`"71 km/s"`, `"1966"`,
       `"243 दिन"`). The number counts up on screen, so only use numbers you verified.
     - `keyword`: a key term in `headline` with a one-line explanation in `caption`.
     - `steps`: a process, with a short `headline` and 2–4 `items` in order.
     - `compare`: two things, with exactly 2 `items` and optionally 2 `values` drawn as bars.
     Keep `headline` ≤ 24 characters, `caption` ≤ 40 and each item ≤ 18. Vary the kinds
     across scenes, and use at least one `stat` when the topic has a good number.
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
6. **Report back** in 3–4 lines: the niche, the topic, both titles, and whether the
   workflow started. Don't commit or push anything. The workflow records history on its own.
