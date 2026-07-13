# Pencil boil — Claude's bake-off entry

The agentic-loop sketch (assets/sketches/01), animated in the boiling-lines
style. Every mark on screen is Sarah's pencil line — no image generation,
no redrawing. One script goes from the committed photo to the finished
files.

## Approach

`make_agentic_loop.py` does the whole pipeline:

1. **Upright + flatten** — rotate the photo, then divide by a heavy
   Gaussian blur of itself to cancel shadows and glare (pencil survives,
   lighting doesn't).
2. **Ink extraction** — a threshold curve turns the flattened image into
   an ink-alpha map: her lines, with pencil texture, composited as ink
   (#33323E) on paper (#FAF7EF).
3. **Slice** — each diagram element (title, 5 nodes, 4 arrows, 3 example
   fragments) is a rectangle in the CONFIG dict, cut from the alpha map.
4. **Build-out** — elements fade/rise in teaching order; then a teal
   pulse travels the loop twice (node by node); then the worked example
   writes in below; hold; fade to blank paper for a clean loop.
5. **Boil** — three deterministic two-scale sinusoid displacement fields
   (same math as `src/style.py`'s `_wobble`), one per seed, held 5 frames
   each at 30fps ≈ 6 Hz. Applied to the whole frame with bilinear
   sampling. Low amplitude — lively, never strobing.
6. **Encode** — raw frames piped straight to ffmpeg (H.264 MP4), then a
   960px 15fps palette-optimized GIF.

## Re-render

```bash
cd animations && source .venv/bin/activate   # needs numpy, Pillow, ffmpeg
python3 pencil-claude/make_agentic_loop.py            # 1080p MP4 + GIF (~3 min)
python3 pencil-claude/make_agentic_loop.py --draft    # 640px check (~30 s)
python3 pencil-claude/make_agentic_loop.py --stills   # 4 key-frame PNGs (~10 s)
```

## Revision turnaround

Everything tunable is in the CONFIG block at the top of the script:
element boxes (preview-pixel coordinates on the 906×1208 grid), appear
times, boil amplitude, ink contrast, pulse schedule. A timing or crop
change is one edit + one run — about 3 minutes to a new 1080p file, 30
seconds to a draft check.

## Outputs

- `out/agentic_loop.mp4` — 1920×1080, 30fps, ~18.4s, clean loop
- `out/agentic_loop.gif` — 960px wiki embed

## Judgment calls (per the handoff doc's "write it down" rule)

- The crossed-out smudge left of Sarah's title is cropped out; everything
  else is untouched linework.
- The teal pulse (#2EA79A, "the AI" color from STYLE.md) is the one
  added element — it ties the pencil piece to the Jobsite family and
  makes the loop visibly RUN, which a static build-out can't. Meaning is
  carried by motion and sequence, never by color alone.
- No captions added: the sketch already says everything it needs to.
