# Channel learnings (read at the start of every run; newest evidence first)

How this file works: the daily task runs `python -m shorts.channel_trends summary` and `python -m shorts.channel_trends trending`, reads this file, applies the rules below
and writes `Learning applied:` (which rule, what was changed) in `research_summary`. After the channel check, add or revise ONE dated line under "Evidence" if the new data
says something new (never invent numbers; small samples are labelled as such). Rules move from "Test" to "Rule" only after two or more videos agree.

## Evidence (24 Nov 2026, YouTube Analytics, last 28 days; samples are small - hints, not proof)
- Channel: 11,285 views, 47 subscribers, 144 videos. Only **+2 subscribers** from ~1,840 views.
- **Shorts carry the channel**: 1,789 views, **40 % average viewed**. **Long-form: 50 views, 11 % average viewed** (a 6 min documentary held 7 %).
- Viewers of the better Shorts leave after **~22 s** (average view duration 16-29 s) of a ~50-55 s video: the payoff and the subscribe cue come after most viewers are gone.
- Best reach: everyday-curiosity about the viewer's own body or phone ("Face unlock kaise kaam karta hai" 143 views, "Why Does Déjà Vu Feel So Real?" 100) and a timely hook (Leonid meteor shower 121 views, 56 %).
- Best retention: Space & Universe (84 % over 7 videos), Earth & Nature (57 %), Engineering Marvels (56 %, but ~1 view each). Brain & Psychology has the highest reach (39 views/video) but only 30 % retention.
- Weak: Hindi Shorts held ~31 %; "Why Does a Crowd Start Clapping in Rhythm" 30 %; "supermoon looks huge? (it isn't)" 13 views / 24 % - a myth-bust without a personal hook.
- YouTube's own signals (vendor blogs, unverified thresholds): Shorts are shown to a small test audience and widened by viewed-vs-swiped-away and watch percentage; since Oct 2026 original content is favoured over re-uploads. Fresh trending data: `youtube_trending.json` (fetched daily by channel-trends.yml).

## Rules (apply to every Short and documentary)
1. **Shorter Shorts: 38-45 seconds (100-112 words).** The payoff (the surprising answer) must land by second ~22; everything after it is a bonus. End with a loop: the last line leads back to the first.
2. **Hook = the viewer's own life in the first 2 seconds** ("Your phone knows your face in the dark. How?"). Concrete object, one question, no preamble. Prefer topics about the viewer's body, phone, home, city or sleep.
3. **Timely beats evergreen when it is free**: check what is happening this week (sky events, launches, news) in the research step; a timely Short can ride the 24-72 h attention.
4. **Documentaries are the weak format right now (11 % viewed).** Only build one when a Short on the same topic already got traction (>= 100 views or >= 50 % viewed), keep it <= 4 min, make every chapter pay off a question, and cut the plan to what the Short did not cover. Never more than one a week until a documentary beats 25 % viewed.
5. **Subscribe where viewers still are**: a one-line "Follow for part 2 of this" inside the first 20 s of a Short (series promise) and a pinned comment; the generic outro stays but is not relied on.
6. **Niche mix**: lead with Space & Universe and Earth & Nature (best retention) using Brain/Psychology-style personal hooks (best reach); treat Engineering Marvels and India Explained as tests, one per week.
7. **Every Short gets a one-line retention check after upload**: after 48 h compare average viewed % with the 40 % channel average; note the result under "Evidence".

## Tests running (move to Rules after 2 agreeing videos)
- Short length 38-45 s vs the old 55 s: compare average viewed % and view duration.
- Series promise in the first 20 s: compare subscribers per 1,000 views (today ~1).
- Topic from YouTube's trending/most-popular Education and Science charts (see `youtube_trending.json`) adapted to a personal hook.
