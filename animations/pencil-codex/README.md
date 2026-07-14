# Pencil Codex — animated sketch set

These animations bring Sarah's six photographed drawings to life while
keeping her handwriting, wording, shapes, and original arrows intact. The
outputs are silent, presenter-paced, and designed to read on a 16:9 slide.
They play on softly crumpled ruled notebook paper that boils with the drawing.

## Approach

`render_agentic_loop.py` handles sketch 01. `render_sketch_set.py` is the
shared, scene-configured renderer for sketches 02–05, delegating the staged
Harness page to `render_harness_mind_map.py`. The motion-rich sixth sketch is
handled by `render_multi_agent_orchestration.py`. Together they:

1. applies EXIF rotation and a measured perspective correction;
2. divides away glare and broad shadows, then isolates the real graphite as a
   transparent ink layer;
3. extract original semantic regions directly from each photo;
4. recompose dense pages at larger scale with more deliberate spacing;
5. computes a per-pixel writing order, revealing each original outline,
   handwritten row, and arrow as if an invisible pencil were moving quickly;
6. generates crinkled notebook paper with blue ruling, a red margin, paper
   grain, and three low-amplitude boil states;
7. applies matching deterministic redraw states to the graphite, held for five
   frames each (about 6 Hz at 30 fps);
8. add restrained teal outline-and-wash teaching cues without relying on color
   alone, plus brief wordless character beats from `personality_motifs.py`;
   sketch 01 also adds one teal return arrow to clarify the loop, while sketch
   06 adds a warm flickering fire behind the original graphite flames;
9. fades back to empty notebook paper for a clean loop.

The Frontier Labs scene uses `02-frontier-labs-landscape-v2.jpeg`, Sarah's
cleaner tier/model/harness/API table. The original sketch remains beside it for
history.

No replacement lettering is used. The added figures and props are compact,
wordless marginal doodles in the same boiling graphite language: the loop's
agent catches input, thinks, carries tools, inspects, and runs; the definition
page assembles an agent and contrasts juggling with specialization; the tools
page contrasts an MCP toolbox, a CLI Swiss Army knife, and a standardized API
port; the Frontier page turns Lab -> Model -> Harness -> API into a small
package line; and the Harness finale lets the answer literally hop into the
center circle. These temporary beats never re-typeset or cover Sarah's
intentional wording.

The generated audit assets in `source/` show cleanup, extraction regions,
coordinate grids, final static layouts, and personality checkpoints. They make
it easy to confirm that the lettering came from the photographs rather than a
font or redraw, and to inspect every added gag without scrubbing a video.

## Fresh-checkout setup and render

From `animations/pencil-codex/` on macOS:

```bash
brew install ffmpeg
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./render.sh
.venv/bin/python verify.py
.venv/bin/python verify_sketch_set.py
```

For a faster single-page revision:

```bash
.venv/bin/python render_sketch_set.py --scene harness_mind_map
```

The Harness page also has a presenter-controlled player at
`interactive/harness_mind_map/index.html`. Serve the `pencil-codex` directory
over localhost, open that page, and use click, Space, or Right Arrow to draw
the next teaching stage. Left Arrow moves back, `H` hides the small presenter
overlay, and `R` restarts. Each completed stage holds indefinitely with the
paper and pencil boil still moving.

The renderer also reuses the parent project environment when
`animations/.venv/` already exists. Override it explicitly with
`PYTHON=/path/to/python ./render.sh`.

Outputs:

- `out/agentic_loop.mp4` — 1920x1080, 30 fps, H.264, silent, 23.5 seconds
- `out/agentic_loop.gif` — 800x450, 12 fps, looping, optimized for wiki use
- `out/frontier_labs.{mp4,gif}` — sketch 02 vendor landscape
- `out/mcp_cli_api.{mp4,gif}` — visual MCP, CLI, and API tools comparison
- `out/harness_mind_map.{mp4,gif}` — updated sketch 04 mind map
- `interactive/harness_mind_map/` — click-paced Harness player and eight stage clips
- `out/what_is_an_agent.{mp4,gif}` — sketch 05 definition and examples
- `out/multi_agent_orchestration.{mp4,gif}` — sketch 06 delegation, synthesis, and cleanup story

## Revision ergonomics

All crop boxes, layout positions, teaching-beat times, and motion settings are
near the top of the two renderer files. A spacing, timing, paper, or contrast
request normally takes 2–5 minutes to edit plus render time. A single sketch
can be regenerated independently. Replacing handwritten wording takes about
5–10 minutes because the new linework must first be added to its source photo
or supplied as another photographed label.

Run `./render.sh` after any revision. It regenerates the audit images, MP4, and
GIF deterministically; then run `verify.py` before committing the result.
