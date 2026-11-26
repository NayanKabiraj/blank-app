# Vox style v2 (free, code-only rules)

Added 26 Nov 2026 at the owner's request ("get the vox skills and use them"). We did NOT install any paid AI-video skill: `CK42BB/vox-explainer-skill`,
`Alisa0808/vox-director` (both MIT) and `Anil-matcha/vox-ai-motion-graphics-generator` (no licence) generate AI footage through a paid API, which breaks
rule 10 (Claude authors the animation in code) and adds the synthetic-content label and mass-production risk. Only their free STYLE RULES are used here, plus
measured numbers from `ilomon10/vox-style-animation` (docs CC BY 4.0, (c) ilomon10 and contributors; code MIT; "not affiliated with Vox Media").
Numbers live in `generated_animations/shared/vox_style.py`; a worked example is the pack `vox2_demo`.

## Rules to apply in every new pack
1. **Palette**: neutrals 85-95% of the frame, ONE accent colour 2-8% (the highlighter/tape colour). Ink is never black, paper never white.
2. **Cut-outs**: white sticker edge 4-6 px (prints ~5% of their width), soft contact shadow, optional hard yellow offset rim (`vs.rim`). One or two flat geometric accents per frame at most.
3. **Entrances**: `vs.enter` (cubic-bezier .16,1,.3,1): 90% of the travel in the first third; exits `vs.exit_`. No bounce or elastic; the only overshoot is `vs.pop`. Prop entrance 0.58 s, big props 0.83 s, tape unfurl 0.42 s, highlighter 0.5 s.
4. **Camera**: one slow 2D push-in per shot (3-5%, `vs.drift`); never a snap zoom, orbit, shake or morph. Adjacent shots vary the move; the payoff beat is static.
5. **Pacing**: a visual beat ~1 s, a shot 3-6 s (never over ~7 s), two shots per narration idea where it helps (wide with headline, then a detail without text). Beats land 0.2-0.5 s after a narration pause ends.
6. **Hand-made feel**: draw on twos (12 drawings/s), boil jitter ~1 px, the one moving element (smoke, clouds, water) keeps moving.
7. **Typography**: bold condensed sans for titles, small caps for labels, serif for topics; data colours red = bad/on, green = good/off.
8. **Arc**: cold open, turn to context, escalating explanation (50-70% of beats), complication, resolution with a reframe.

## Free public-domain assets
The `ilomon10` catalog (335 entries: NASA, Library of Congress, Wikimedia Commons, Smithsonian, NARA; public domain or CC0; music is CC BY and needs credit)
is a source list, not a dependency. Wikimedia Commons is blocked in this interactive container, so fetch on GitHub runners only (as `shorts/stockreel` does),
accept PD/CC0 only (CC BY needs a Sources line), and commit nothing you have not checked the licence of.
