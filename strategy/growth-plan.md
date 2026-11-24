# Growth plan: honest assessment and what we do about it (24 Nov 2026)

## Will the current strategy get the channel monetized? No - not on its own, and not soon
Numbers (YouTube Analytics, 24 Nov): 47 subscribers; **qualifying (long-form) watch time: about 0.4 hours in 28 days**; Shorts 1,789 views in 28 days; about 1.1 subscribers per 1,000 views.
Rules (YouTube Help, via web search 24 Nov): ads tier = 1,000 subscribers AND (4,000 public **long-form** watch hours in 12 months OR 10 M public Shorts views in 90 days); **Shorts-feed watch time does NOT count toward the 4,000 hours**; private/unlisted
videos count for neither. Third-party reports say the bar doubles on 1 Feb 2027 (unverified).

| Path | Needed | Today | Gap |
|---|---|---|---|
| Subscribers | +953 | 47 | at 1.1 per 1,000 views that is ~860,000 views; at 3 per 1,000 ~320,000; at 5 per 1,000 ~190,000 (we get ~1,800 Shorts views a month) |
| Long-form hours | 4,000 | ~0.4 per 28 days | ~48,000 to 80,000 long-form views at 3-5 minutes watched each; we get ~50 a month |
| Shorts views | 10,000,000 in 90 days | ~2,000 | not a realistic route |

Why the current approach stalls: (1) **volume of average videos does not move these numbers** - reach on YouTube is a power law (our 146 videos: a handful of outliers carry the views); (2) the channel spans 12 niches, so
nobody knows what subscribing gets them (conversion ~1 per 1,000); (3) Shorts cannot supply the watch hours and our long-form is the weakest format (11 % viewed); (4) 6 template-looking videos a day invites the "inauthentic / mass-produced" review.
**Honest outlook:** ads monetization within 3 months is very unlikely; with a breakout and a focused series it is a 9-18 month goal, not guaranteed. The plan below maximises the odds of a breakout and of converting it.

## The plan (ranked by expected effect)
1. **Find the winner, then repeat it (explore -> exploit).** Phase 1, now to 8 Dec: 3 topics a day across formats, each tagged (niche/cluster, language, format). Phase 2, from 9 Dec: **at least 60 % of topics come from the top-2 series by views AND subscribers gained**
   (the weekly report lists them). Any Short above 300 views gets a **Part 2 within 3 days**. Evidence so far: Hindi "kaise kaam karta hai" tech explainers (GPS 241, Face unlock 143), the story Shorts (505, 394), Space (84 % viewed), and flute covers on this channel (687 views, 86 % viewed).
2. **One promise per channel (niche down).** Decide at the 8 Dec review which single audience/series the channel is: e.g. "Hindi + English how-it-works for curious Indians (phones, space, everyday science)" or "original suspense stories". A subscriber must be able to say what they get. Until then every video names its series.
3. **Conversion toolkit on every video** (conversion, not reach, is the bottleneck): the series promise inside the first 20 s ("Part 2 tomorrow"), the series name on screen, the pinned comment that answers `next_video`, and a **one-tap subscribe link in every description** (`https://www.youtube.com/@nayankabiraj?sub_confirmation=1`, added automatically now).
   The weekly report lists the top subscriber-gaining videos so we copy what converts.
4. **Long-form is where the 4,000 hours come from.** One long-form a week (Sunday), 6-10 minutes, search-led evergreen "how it works" built on a topic whose Short already won; chapters that each pay off a question; retention above 25 % is the gate before a second a week.
   Shorts feed viewers, long-form builds the hours: end winning Shorts with "the full story is on the channel".
5. **Distribution beyond YouTube** (owner-side, one-time): cross-post the same Shorts to Instagram Reels and Facebook Reels (more exposure, same original video), share winners in relevant WhatsApp/Reddit/Telegram communities, reply to comments in the first hour. I can prepare captions; posting needs the owner's accounts.
6. **Keyword research for long-form**: vidIQ credits renew on 1 Dec (150 credits, 5 per call): spend them weekly on 3-5 searches (India/Hindi "rising" keywords, "questions") to pick the Sunday long-form topic.
7. **Money before ads (owner-side, small)**: affiliate links in descriptions of gadget/phone videos (e.g. Amazon Associates India) once a video has real traffic; not worth the effort below a few thousand views a month.
8. **Safety first**: every video has its own angle, script and hand-built animation; vary structure; nothing off-putting; no health/finance/legal personas. 6 a day is a ceiling, not a target - if quality or variety slips, publish fewer.

## Checkpoints (reviewed in the Sunday report; move only with evidence)
- **8 Dec:** 100 subscribers; one video above 1,000 views; winners identified; niche/series chosen.
- **5 Jan:** 250 subscribers; 20,000 Shorts views in 28 days; two long-form videos above 25 % viewed.
- **1 Feb 2027:** re-assess against YouTube Studio -> Earn (the thresholds may rise); decide whether to aim for the 500-subscriber fan-funding tier first.
If a checkpoint is missed by half, change the strategy (series, format, language), not the volume.

## SEO toolkit (built 24 Nov 2026, free)
`python -m shorts.seo` (workflow `seo-research.yml` -> `data/seo/latest.json`): autocomplete expansions in English and Hindi/Hinglish, yt-dlp metadata of the top results for outlier detection and title/length patterns; the weekly report lists the search terms that brought viewers to our videos (Analytics API). Public metadata, low volume.
