

**Animation pack (strict, every video, scheduled runs included).** After the plan is written, write the video's animation: read `generated_animations/AUTHORING.md` and
an existing pack (`generated_animations/scenes/gps_short/`, `tides_doc/`) as a model, create `generated_animations/scenes/<pack>/` (`shots.json` + `scene_NNN.py` shots with
scene-specific motion animation for what each sentence says, English and Hindi labels; use a new unique `<pack>` id such as `<topic-slug>-<date>`), set `animation_pack` in both
`english` and `hindi`, run `python -m generated_animations scan <pack>`, render a low-res preview (`SHORTS_FAKE_TTS=1 GA_PIXEL_SCALE=0.4`, see AUTHORING.md) and inspect the frames,
fix defects. Then commit ONLY that new folder to `main` with the GitHub tool (`push_files`) before starting the workflow (owner-authorised exception to "scheduled tasks commit
nothing"). `python -m shorts.plan validate` / `validate-doc` fails the plan until every scene is covered by a shot. No scene may be a static card: the picture must be dynamic with a lot of motion.
