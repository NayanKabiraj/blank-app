# Channel learnings (read at the start of every run; newest evidence first)

How this file works: the daily task runs `python -m shorts.channel_trends summary` and `python -m shorts.channel_trends trending`, reads this file, applies the rules below
and writes `Learning applied:` (which rule, what was changed) in `research_summary`. After the channel check, add or revise ONE dated line under "Evidence" if the new data
says something new (never invent numbers; small samples are labelled as such). Rules move from "Test" to "Rule" only after two or more videos agree.

## Evidence (24 Nov 2026, YouTube Analytics, last 28 days; samples are small - hints, not proof)
- Channel: 11,285 views, 47 subscribers, 144 videos. Only **+2 subscribers** from ~1,840 views.
- **Shorts carry the channel**: 1,789 views, **40 % average viewed**. **Long-form: 50 views, 11 % average viewed** (a 6 min documentary held 7 %).
- Viewers of the better Shorts leave after **~22 s** (average view duration 16-29 s) of a ~50-55 s video: the payoff and the subscribe cue come after most viewers are gone.
- **Correction after the full upload list (24 Nov, 147 videos):** the three most-viewed videos of the last 28 days are older horror/mystery story Shorts from 7-9 Nov ("Haunted Hotel Reception" 505 views, "The Mirror's Deadly Secret" 394, a Hindi haveli story 79), before the explainer pivot. Story-format Shorts out-reached every explainer so far, at 31-35 % viewed (65 % for the Hindi one). This is a different format, not a niche rule - the owner decides whether to bring story Shorts back.
- Best explainer reach: everyday-curiosity about the viewer's own body or phone ("Face unlock kaise kaam karta hai" 143 views, "Why Does Déjà Vu Feel So Real?" 100) and a timely hook (Leonid meteor shower 121 views, 56 %).
- Best retention: Space & Universe (84 % over 7 videos), Earth & Nature (57 %), Engineering Marvels (56 %, but ~1 view each). Brain & Psychology has the highest reach (39 views/video) but only 30 % retention.
- Weak: Hindi Shorts held ~31 %; "Why Does a Crowd Start Clapping in Rhythm" 30 %; "supermoon looks huge? (it isn't)" 13 views / 24 % - a myth-bust without a personal hook.
- YouTube's own signals (vendor blogs, unverified thresholds): Shorts are shown to a small test audience and widened by viewed-vs-swiped-away and watch percentage; since Oct 2026 original content is favoured over re-uploads. Fresh trending data: `youtube_trending.json` (fetched daily by channel-trends.yml).

## What YouTube itself is pushing (youtube_trending.json, 24 Nov; Science & Technology most-popular charts US/IN/GB; the Education chart does not exist in these regions - 404)
- Almost everything on the chart is a **Short of 12-35 s** (median 30 s); 76 % are under 60 s. Titles ~50 characters, half contain a number, 16 % a question; many carry #shorts.
- Winning shapes: "How This Device Copies Keys In Seconds" (15.6 M views), "How much does it cost to charge a phone to 100%?" (5.5 M), "What To Do If Someone Drops Your Phone In WATER?!" (2.2 M), "Why Apple needed Face ID!" (4.3 M), "How Old Antennas Worked? (3D)" (2.6 M), "How to Speed up Your Laptop" (2.8 M): **a phone/gadget the viewer owns + a practical or surprising "how/why/what if"**. The rest of the chart is product-launch and gadget showcase Shorts (not our format).
- Our own "Face unlock kaise kaam karta hai" (143 views, best explainer) is the same pattern. The channel's How Tech Works niche has only 1 video: it is under-tested, not weak.

## Hindi vs English (24 Nov; Shorts since 11 Nov, 30-65 s, non-story; Hindi = Devanagari or romanised-Hindi title)
- English n=19: median 6 views, mean 23, median viewed 56 %. Hindi n=11: median 6 views, mean 43 (one video, "Face unlock kaise kaam karta hai", 143), median viewed 42 %. Hindi long-form: median 4 views, 7 % viewed.
- Reading: **no proven winner**. Reach is equal at the median; Hindi retention is lower, English retention higher. Both are hit-driven (one video carries the mean). Story Shorts: mean 143 views (two videos: 505 and 394), median 10.

## DECISION (24 Nov 2026, owner: "decide the ratio"; updated same day: quota => target 6 a day)
- **CURRENT DAILY TARGET: 6 uploads = 3 Short topics x 2 languages (EN + HI twins).** Why 6, not 10: the YouTube Data API default quota is 10,000 units a day and an upload costs 1,600 (about 6 uploads); the owner asked to target 6 while the quota is the limit. **When the owner confirms a raised quota, change this line to 10 (5 topics x 2) and use the 5-topic list below.** Hindi and English are both enabled in every pipeline (CLAUDE.md rule 11): the Hindi twin costs no extra animation work (one bilingual vox pack via `vox.L`), only render time.
- **The 3 topics (priority order, so a short day still ships the best first)**: 1) everyday-tech/phone/home explainer with a personal hook (the trending pattern), 2) a timely or Space & Universe / Earth & Nature explainer (best retention), 3) **one Horror & Suspense story** (original fiction, bloodless, labelled fiction, ~38-45 s). At 10 a day add: 4) a second explainer from Brain & Psychology / India Explained / the research queue, 5) a wildcard.
- **Documentary: Sunday only, EN + HI = 2 of that day's 6** (Sunday = 2 Short topics x 2 + 1 documentary x 2), and only if a Short on the topic got traction (rule 4), else a third Short topic. Weekly ratio at 6/day: **38 Shorts : 2 documentaries (95 % : 5 %), 50 % English : 50 % Hindi, story Shorts one topic in three**.
- **Review at 14 days** (then every 14 days; move only when evidence agrees): if Hindi median views < 50 % of English -> Hindi only for the best topic of the day; if story Shorts' median beats explainers' -> 2 story topics a day; if a documentary reaches 25 % viewed -> up to 2 a week; if a niche is under the channel median twice -> replace it in slot 2.
- **Quality over quota**: ship fewer rather than rush; never ship a pack that failed frame inspection. Overflow beyond the quota waits in `videos/unpublished/` (flushed 3x a day, oldest first); `quotaExceeded` is never an authorization problem. If it still appears at 6 a day, check Google Cloud -> APIs -> YouTube Data API v3 -> Quotas (not verified from here).

## Rules (apply to every Short and documentary)
1. **Shorter Shorts: 38-45 seconds (100-112 words; the validator floor is 100)** - YouTube's own chart median is 30 s. The payoff (the surprising answer) must land by second ~22; everything after it is a bonus. End with a loop: the last line leads back to the first.
2. **Hook = the viewer's own life in the first 2 seconds** ("Your phone knows your face in the dark. How?"). Concrete object, one question, no preamble. Prefer topics about the viewer's body, phone, home, city or sleep.
3. **Timely beats evergreen when it is free**: check what is happening this week (sky events, launches, news) in the research step; a timely Short can ride the 24-72 h attention.
4. **Documentaries are the weak format right now (11 % viewed).** Only build one when a Short on the same topic already got traction (>= 100 views or >= 50 % viewed), keep it <= 4 min, make every chapter pay off a question, and cut the plan to what the Short did not cover. Never more than one a week until a documentary beats 25 % viewed.
5. **Subscribe where viewers still are**: a one-line "Follow for part 2 of this" inside the first 20 s of a Short (series promise) and a pinned comment; the generic outro stays but is not relied on.
6. **Everyday-tech angle first**: for the next Shorts prefer a phone/gadget/home object the viewer owns with a practical or surprising "how / why / what if" (see the trending list); title <= 55 characters, a number or a concrete object in it.
7. **Niche mix**: lead with Space & Universe and Earth & Nature (best retention) using Brain/Psychology-style personal hooks (best reach); treat Engineering Marvels and India Explained as tests, one per week.
8. **Every Short gets a one-line retention check after upload**: after 48 h compare average viewed % with the 40 % channel average; note the result under "Evidence".

## Tests running (move to Rules after 2 agreeing videos)
- Short length 38-45 s vs the old 55 s: compare average viewed % and view duration.
- Series promise in the first 20 s: compare subscribers per 1,000 views (today ~1).
- Topic from YouTube's trending/most-popular Education and Science charts (see `youtube_trending.json`) adapted to a personal hook.
