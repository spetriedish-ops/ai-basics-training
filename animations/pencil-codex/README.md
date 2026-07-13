# Pencil Codex — agentic loop

This animation brings Sarah's photographed agentic-loop drawing to life while
keeping her handwriting, wording, node outlines, and original arrows intact.
The output is silent, presenter-paced, and designed to read on a 16:9 slide.

## Approach

`render_agentic_loop.py` performs the full pipeline from the committed JPEG:

1. applies EXIF rotation and a measured perspective correction;
2. divides away glare and broad shadows, then isolates the real graphite as a
   transparent ink layer;
3. extracts the original title, five labeled nodes, and four arrows;
4. recomposes those pieces at larger scale with more deliberate spacing;
5. adds three deterministic, sub-pixel redraw states held for five frames each
   (about 6 Hz at 30 fps);
6. adds one teal return arrow and a motion-plus-outline highlight so the loop
   visibly runs without relying on color alone;
7. fades back to the same empty paper used at the opening for a clean loop.

No generated or replacement artwork is used. The return arrow is the only new
drawn line; it clarifies where “REPEAT UNTIL TASK IS DONE” returns to the
reasoning step. The worked example remains on the source page rather than in
this animation so the five primary beats can stay large enough for a room.

The generated audit assets in `source/` show the cleanup and every extraction
region. They make it easy to confirm that the final lettering came from the
photograph rather than a font or redraw.

## Fresh-checkout setup and render

From `animations/pencil-codex/` on macOS:

```bash
brew install ffmpeg
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./render.sh
.venv/bin/python verify.py
```

The renderer also reuses the parent project environment when
`animations/.venv/` already exists. Override it explicitly with
`PYTHON=/path/to/python ./render.sh`.

Outputs:

- `out/agentic_loop.mp4` — 1920x1080, 30 fps, H.264, silent, 23.5 seconds
- `out/agentic_loop.gif` — 800x450, 12 fps, looping, optimized for wiki use

## Revision ergonomics

All crop boxes, layout positions, teaching-beat times, colors, and motion
settings are near the top of `render_agentic_loop.py`. A spacing, timing, or
contrast request normally takes 2–5 minutes to edit and a few seconds to
render on the machine used for the initial delivery. Replacing handwritten
wording takes about 5–10 minutes because the new linework must first be added
to the source photo or supplied as another photographed handwritten label.

Run `./render.sh` after any revision. It regenerates the audit images, MP4, and
GIF deterministically; then run `verify.py` before committing the result.
