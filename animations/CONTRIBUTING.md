# Contributing — working agreement for this repo

Audience: future Claude sessions (especially Claude Code), and any human
collaborator. This is the operational handoff; the creative brief lives in
the root `README.md`, the visual language in `animations/STYLE.md`.

## The loop

Every change to an animation follows the same cycle:

1. **Draft** — render one seed at low quality while iterating:
   `SCRIBBLE_SEED=1 manim -ql --media_dir /tmp/draft src/scenes/<stem>.py <Class>`
2. **Verify** — run the pixel checks BEFORE declaring anything done:
   `python3 scripts/verify.py <path-to-mp4>`
   This is mandatory, not optional. This repo once shipped a colorless,
   label-less render because review relied on eyeballing frames. The checks
   assert that expected fill colors and label ink actually exist per story
   beat. If you change a scene's palette or timing, update the beat spec at
   the top of `scripts/verify.py` in the same commit.
3. **Final** — full boil pipeline (3 seed renders + frame interleave):
   `./scripts/boil.sh <stem> <Class>`
   If running under an execution time limit, render the three seeds as
   separate commands, then run `scripts/interleave.py` on its own.
4. **Verify the final** too. Then commit source + `renders/final/` outputs
   together, with a message that says what changed and why.

Commit straight to `main` (team of two: Sarah + Claude). One logical change
per commit. Rendered finals are committed by convention so slide-ready
assets always travel with their source.

## Engine constraints (learned the hard way)

- `_wobble` uses a **position-based** noise field. Never switch to per-point
  or index-based noise: manim shapes chain bezier curves through duplicated
  anchor points, and moving those duplicates apart shatters the path —
  strokes still draw, but fills silently vanish.
- Keep `amp × k` (amplitude × highest spatial frequency) under ~0.9 or the
  field can fold paths into self-intersection and punch holes in fills.
- **Never wobble text.** `crayonify()` exempts `Text` mobjects; keep it that
  way. The handwriting fonts carry the hand-drawn feel; glyph paths are
  thinner than the wobble amplitude and turn to mush.
- Boil = 3 seeds, 5 frames per seed at 30 fps (≈6 Hz). If it reads too busy
  in a room, raise hold to 8 (≈4 Hz) in `scripts/interleave.py --hold`.
- Scenes must loop cleanly: open on the empty stage, end on the empty stage.
- Determinism: all randomness must derive from `SCRIBBLE_SEED` + a per-shape
  seed, or the three boil passes won't line up frame-for-frame.

## Content guardrails (from the brief — non-negotiable)

- Audience is mixed-technical; tone is warm, casual, "safe to not know."
- Captions ≤ 8 words, legible from the back of a room.
- The "it's not X, it's Y" construction is banned in all on-screen text.
- Accuracy beats cuteness. In P0 specifically: the bed must visibly empty at
  session end, and a new session must visibly start empty.
- Color never carries meaning alone; labels do. "The AI" is always teal.
- No borrowed IP: the scribble style is generic kid-crayon, not any show's
  specific characters or designs.

## Environment notes

- macOS setup: `brew install ffmpeg pkg-config pango`, then
  `pip install -r requirements.txt` in a venv. (The
  `--break-system-packages` flag some docs mention is Linux-only.)
- Fonts are bundled in `assets/fonts/` (OFL) and registered by
  `src/style.py` at import — no system font installs needed.
- `renders/boil_s*/` and `renders/boil_frames/` are scratch and gitignored;
  only `renders/final/` is committed.
- Expect scribble GIFs to be heavy (boiling defeats GIF compression). Ship
  the MP4 to slides; the `_small.gif` variant is for wiki embeds.

## Queue

The set is planned end-to-end in `STORYBOARDS.md` (five scenes, one world,
escalation-gag humor style). Production waits on Sarah's redline of that
doc. Recommended production order: Truck v2 → Pop the Hood → Paver →
Fleet → Garage. Storyboard first, get a nod in chat or a review comment,
then produce.
