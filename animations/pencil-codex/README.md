# Pencil Codex — animated sketch set

These animations bring Sarah's photographed drawings and brain reference to life while
keeping her handwriting, wording, shapes, and original arrows intact. The
outputs are silent, presenter-paced, and designed to read in a full-screen
16:9 HTML player. They play on softly crumpled ruled notebook paper that boils
with the drawing.

## Approach

`render_agentic_loop.py` handles sketch 01. `render_brain_in_harness.py`
combines Sarah's giant-headed figure with a graphite redraw of her supplied
brain reference. `render_sketch_set.py` is the
shared, scene-configured renderer for sketches 02–05, delegating the staged
Harness page to `render_harness_mind_map.py`. The motion-rich sixth sketch is
handled by `render_multi_agent_orchestration.py`.
`render_rovo_architecture.py` handles the Rovo architecture flows and Agentic
Spectrum while keeping each complete photographed composition and its original
connectors intact.
Together they:

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
9. holds the complete drawing with the paper and graphite still boiling until
   the presenter advances.

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

Brain in Harness, Frontier Labs, MCP/CLI/API, the Harness page, and both Rovo
architecture diagrams have presenter-controlled players under
`interactive/<scene>/index.html`. Serve the `pencil-codex`
directory over localhost, open the desired page, and use click, Space, or Right
Arrow to draw the next teaching stage. Left Arrow moves back, `H` hides the
small presenter overlay, and `R` restarts. Each completed stage holds
indefinitely with the paper and pencil boil still moving. Each stage has a
dedicated half-second native hold clip under `holds/`; this prevents a
background/throttled browser tab from replaying the drawing reveal.

The renderer also reuses the parent project environment when
`animations/.venv/` already exists. Override it explicitly with
`PYTHON=/path/to/python ./render.sh`.

Outputs:

- `out/agentic_loop.mp4` — 1920x1080, 30 fps, H.264, silent, 23.5 seconds
- `out/agentic_loop.gif` — 800x450, 12 fps, looping, optimized for wiki use
- `out/brain_in_harness.{mp4,gif}` — brain → embodied harness take-home master
- `interactive/brain_in_harness/` — click-gated Brain → Harness player
- `out/frontier_labs.{mp4,gif}` — sketch 02 vendor landscape
- `interactive/frontier_labs/` — click-paced Labs → Models → Harnesses/API player
- `out/mcp_cli_api.{mp4,gif}` — visual MCP, CLI, and API tools comparison
- `interactive/mcp_cli_api/` — click-paced MCP → CLI → API player
- `out/harness_mind_map.{mp4,gif}` — updated sketch 04 mind map
- `interactive/harness_mind_map/` — click-paced Harness player and eight stage clips
- `out/what_is_an_agent.{mp4,gif}` — sketch 05 definition and examples
- `out/multi_agent_orchestration.{mp4,gif}` — sketch 06 delegation, synthesis, and cleanup story
- `out/rovo_cli_flow.{mp4,gif}` — User → RovoCLI → Nemo runtime → gateway → models
- `interactive/rovo_cli_flow/` — four-stage click-paced Rovo CLI architecture player
- `out/rovo_chat_agents_flow.{mp4,gif}` — two-lane Rovo Chat and Agents architecture
- `interactive/rovo_chat_agents_flow/` — five-stage click-paced Rovo Chat/Agents player
- `out/agentic_spectrum.{mp4,gif}` — single-pass least-to-most-agentic spectrum

## Revision ergonomics

### Full context-nugget click-through (2026-10-12)

Open `interactive/context_nugget/index.html` for the complete 27-beat rehearsal.
All rendered clips, artwork, and fonts are committed. Playback does not require
Blender, image generation, or the rendering environment.

On another computer, update branch `codex/rovo-architecture-animations`, then
run this from the repository folder:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory animations
```

Open <http://127.0.0.1:8765/pencil-codex/interactive/context_nugget/index.html>.
Keep that terminal open while recording; press H to hide the controls and F
for fullscreen. Stop the server with Ctrl+C when finished.

It follows the pasted narrative: five-branch harness recap → Context reveal →
crumple and toss → four training-factory callbacks → agent chat → room sketch
and watercolor → Pair B entrance → personal context, research prompt, MCP tools,
and retrieved information → UNC narration pause → four mine-cart/model beats →
Dory → gold coins → closing narration holds.

Click the picture, use Next, or press Right Arrow / Space to advance from a
completed hold. Clips never advance themselves. Left Arrow goes back, R replays
the current beat, H hides all controls and cues for recording, and F toggles
fullscreen. The jump menu and expandable run of show support reviewing any
section. Every sketch uses a looping hold with completed action frozen; Dory
keeps her approved gentle hover. Blank paper is held as a still. The player
preserves the outgoing frame during video changes to avoid blank flashes.

The UNC Slack-to-Confluence work request and closing cost/quality paragraphs
reuse existing scene holds, with explicit review notes outside the recording
area. No separate action clips have been made for those passages. The original
pasted draft still contains a context-window-definition placeholder and uses
wheelbarrow/Tetris wording predating the approved mine cart and solid cubes.

`build_context_nugget.py` joins the first five existing map clips, adds four
frozen-action boiling holds for the legacy engine-factory clips, and writes
`manifest.json` plus `sequence.js`. All other media are referenced in their
existing scene directories. `player.js` provides the shared controls.

```bash
../.venv/bin/python build_context_nugget.py
node verify_context_nugget.cjs
```

### Context room study (2026-10-08)

The preceding agent introduction is `interactive/agent_chat/index.html`, rendered
by `render_agent_chat.py`. A chunky cream CRT, keyboard, and corded mouse frame
a provider-neutral chat interface. Three manually advanced beats open the chat,
type and send “Hi! Who are you?”, and introduce the assistant. Its final question,
“What should I call you?”, establishes that it knows its role before it has
learned the user's identity. The ready screen and all three completed beats use
native 15-frame pencil-boil loops. The master is `out/agent_chat.mp4` (18.5 seconds,
silent, 1080p30), with GIF, storyboard, and final still alongside the other studies.
Render using `../.venv/bin/python render_agent_chat.py` from this directory.

`render_context_room.py` builds an empty cartoon classroom as the setting for
the context-window metaphor. Separate pencil strokes construct the room and
its architectural features; textured watercolor washes follow. The camera and
room dimensions stay fixed, leaving open floor space for later context objects.
This first study contains no conversation, characters, or context blocks yet.

`interactive/context_room/index.html` works directly from a local checkout or
the existing local preview server. Click **Draw the room**, then **Paint it in**.
Each beat holds on its completed drawing with a native half-second pencil-boil
loop (three line variants at 6 Hz), until the presenter advances. Right/Left Arrow changes beats,
R replays, H hides the controls for recording, and F enters fullscreen.
**Play full clip** runs the entire 19.5-second animation. The silent 1920×1080,
30 fps master and GIF are `out/context_room.{mp4,gif}`. The final room and
six-frame storyboard live in `source/context_room/`.

```bash
# From animations/pencil-codex:
../.venv/bin/python render_context_room.py --prepare-only
../.venv/bin/python render_context_room.py
```

Opening callbacks for the future context nugget can reuse
`interactive/harness_mind_map/` (including stage 06, Context) and the
pre-training sequence in `../renders/final/engine_factory.mp4`.

The companion paper transition study is
`interactive/paper_transition/index.html`. **Crumple & toss** plays a 4.3-second
transition from the harness map to fresh paper. The next button manually starts
the classroom outlines, holds, then paints the room on the following click.
The initial mind map, pencil room, and painted room all have native looping
sketch holds. **Watch full sequence** deliberately previews the complete flow.
Render with `../.venv/bin/python render_paper_transition.py` after rendering
the room. Rendering requires Blender. `paper_crumple_3d.py` continuously deforms
one dense, smoothly shaded paper surface with the original mind map fixed to
its UV coordinates. Uneven curved folds gather the sheet, free corners extend
beyond the center, and the same object tumbles out of frame. There is no image
swap, crossfade, or opacity animation. This is an art-directed deformation,
not a physically simulated paper collision solver.

`render_paper_transition.py --assemble-only` packages existing full-resolution
frames without repeating the 3D render. Intermediate PNGs are ignored by Git;
the Blender scene and source script are retained. The generated prop under
`assets/paper_transition/` is an earlier visual study and is no longer used
in the animation. Masters are `out/paper_crumple.mp4`
and `out/paper_crumple_to_room.mp4`; review frames are in
`source/paper_transition/`. The full context-nugget walkthrough uses this transition immediately after
the Context branch reveal and before the training recap.

### Pair B walks into the context classroom

`interactive/context_entry/index.html` starts on a native looping empty-room
hold. **Walk in** plays an 8.5-second silent entrance: the side door opens, the
gangly human lopes in, and the mustachioed teal agent follows with shorter,
quicker steps, holding its instruction leaflet. After stopping, the human turns
through four additional drawn poses to look down-right toward the agent, whose
eyes already look up-left. Both plant their feet and remain
in a native sketch-boil hold until the presenter replays or leaves the scene.
The room drawing and paper-transition preview use the same relocated side door.

The approved design is Pair B from `source/context_characters/character-concepts-v4-mustache.png`.
The built-in image-generation tool supplied eight walking cels plus a resting
pose per character. Original transparent sheets, exact prompts, and extracted
RGBA cels are under `assets/context_entry/`. `render_context_entry.py` handles
cel timing, travel, doorway occlusion, settling, and restrained local line boil.
The characters change walking poses without crossfading; the hold never repeats
the walking action. The player shares the existing R / H / F recording shortcuts.

Masters: `out/context_entry.mp4` (1920×1080, 30 fps) and `out/context_entry.gif`.
The final still and storyboard are in `source/context_entry/`.

```bash
../.venv/bin/python render_context_entry.py --prepare-only
../.venv/bin/python render_context_entry.py
```

### Filling the context classroom

`interactive/context_fill/index.html` includes the approved entrance followed
by five manually advanced teaching beats. It can also jump directly to any beat:

1. Personal introductions produce a handshake sales trophy, fleece-vest team
   picture, UNC briefcase covered with follow-up notes, and an oversized-key
   keyboard. These are illustrative facts for the fictional account scenario.
2. The research prompt and Confluence-space link arrive as their own item.
3. Rovo, Gmail, and Calendar MCP tool definitions arrive as three small sets
   of instruction manuals. They precede retrieved data and remain in the room.
4. Pages, email threads, replies, and meeting information arrive as solid cubes
   that spread out from the back-left corner in the classroom's perspective.
5. More cubes join the modest pile and stack on earlier cubes. Each cube is
   roughly basketball-sized beside the human; this early context leaves ample
   room available. The pair stays in place, facing each other.

The original room and character positions stay fixed during this early stage.
Tool definitions, instructions, personal facts, prompt, and results all persist,
even when later cubes hide earlier faces. A clear aisle to the right-wall door
remains open. Tool context varies by harness; cube size is a visual metaphor,
not a measurement of any service's token usage. No real connected
accounts are accessed. Each beat has a native 15-frame sketch-boil hold, with
action frozen until the presenter advances. R replays, H hides the controls
and narration cues, and F enters fullscreen. Full-sequence playback is explicit.

`render_context_fill.py` builds the sequence using `render_context_volume.py`.
The cube projection matches all four floor corners, with shared face vertices,
shaded sides, contact shadows, and depth-sorted overlaps. Upper cubes wait for
their supporting cubes to land. The pair retains its approved face-to-face
poses. Speech bubbles remain inside the room; narration captions above and
below the room are omitted so the animation supports the spoken track.
Eight transparent prop illustrations
were made with built-in image generation; the original sheet, exact prompt, and
individual props are saved in `assets/context_fill/`. Native drawing code adds
the readable labels and three-dimensional cubes. Storyboard, stage stills, and
the cumulative beat inventory are in `source/context_fill/`.

Masters are `out/context_fill.mp4` (39 seconds) and
`out/context_entry_and_fill.mp4` (47.5 seconds including the entrance), both
silent 1920×1080 at 30 fps. `out/context_fill.gif` provides a smaller preview.

```bash
../.venv/bin/python render_context_fill.py --prepare-only
../.venv/bin/python render_context_fill.py
```

### Context transport: mine cart

Sarah is leaning toward the train, with an original Scooby-Doo mine-cart image
as the latest visual reference. `interactive/context_transport/index.html`
now opens on the new dark-blue mine cart. The earlier wheelbarrow and cable
studies remain accessible and are clearly marked as earlier versions; they
still use the older flat context layout.

`render_context_minecart.py` continues from the approved basketball-sized cubes
and stationary, face-to-face characters. Context copies load into the cart's
interior in supported layers. The original generated cart is drawn behind the
cargo, then its near rim and walls are drawn in front, occluding both settled
and descending cubes. Cargo faces share the rim's projection, and the load
unloads top-to-bottom at the model. A supported three-cube response bundle
returns and joins the room; the next load includes that reply and a follow-up
prompt. Originals remain in the classroom throughout. These are illustrative
units, not measurements of token counts or compression.

The four presenter-controlled beats remain: load, travel out, return with a
response, send the next turn. The train master is now 34.5 seconds, including
a 3.5-second processing flourish after the request has fully unloaded. The
computer squashes, stretches, shivers, telescopes side vents and roof feelers,
spins its reel, and lights its display, then recovers before returning the reply.
The railway uses one shared geometry and sleeper cadence through both views;
the wide view scales the cart and entire railway with the classroom. Train
beat boundaries are 8, 14, 24.5, and 34.5 seconds; earlier studies retain theirs. All beats have
native 15-frame sketch-boil holds. Full playback is explicit; R / H / F retain
replay, recording-view, and fullscreen. Dialogue stays inside the room. There
are no narration captions above or below the scene; the wide view retains
only the two location labels, CONTEXT WINDOW and MODEL.

The new transparent prop and exact built-in image-generation prompt are saved
in `assets/context_transport/minecart/`. The user's screenshot is a style/shape
reference, not a background or character asset. The original vehicle studies
and their prompts remain in `assets/context_transport/`. Review frames live
in `source/context_transport/train/`. Outputs are `out/context_train.mp4`
(silent 1920×1080, 30 fps) and `out/context_train.gif`.

```bash
../.venv/bin/python render_context_minecart.py --prepare-only
../.venv/bin/python render_context_minecart.py
```

`render_context_transport.py --kind train` delegates to this new renderer.
Other kinds retain the earlier comparison implementation.

The final train view now has two additional manual beats. Click the scene,
advance, or press C: first Dory swims down from above the frame, then hovers between
the classroom and model with “Hi, I'm Dory. What's your name?” Her two-second
hover loop holds indefinitely. The next click releases six gold coins from
the computer roof while Dory stays in place. Coins can be repeated; Replay
replays the most recent finale action, and Left Arrow returns to the base
final tableau. Neither finale starts automatically after the full preview.
Earlier transport studies do not expose these additions.

`?kind=train&start=final&v=minecart-5` opens directly on the waiting final
view. Dory uses Sarah's supplied image at
`assets/context_transport/dory/supplied.png`, with its original white
background intact. Built-in imagegen background extraction was rejected;
no generated cutout is used. The entrance, hover, and combined coin exports
are `out/context_train_dory.mp4` (4.4s),
`out/context_train_dory-hold.mp4` (2s), and
`out/context_train_dory-coins.mp4` (4s). All are silent 1080p at 30fps.
The player uses their corresponding `train/dory*.mp4` copies.

```bash
../.venv/bin/python render_context_dory.py
# The original standalone coin clip remains available:
../.venv/bin/python render_context_minecart.py --coins-only
```


### Computer-control bonus nugget (2026-10-01)

Two new silent sketch cutaways are ready for visual review:

- `out/computer_control.mp4` (25 seconds): an agent opens a browser, moves an
  onboarding ticket to Done, then visits documents and a calendar in the same
  signed-in session. The illustrated desktop contains fictional work data.
- `out/saloon_doors.mp4` (31 seconds): a tipsy cowboy walks through swinging
  doors, three boards close the entrance, and his next attempt ends in a
  recoil, airborne hat, and seated recovery outside the intact boards.

Both also have GIF previews. `interactive/computer_control_bonus/index.html`
offers full clips and three separate teaching beats per scene. Each beat ends
in a native half-second pencil-boil hold. Right/Left Arrow changes beats,
R replays, and F enters fullscreen; native video controls allow scrubbing.
Serve `animations/` over localhost and open
`/pencil-codex/interactive/computer_control_bonus/index.html`.

The new art uses code-drawn pencil paths, bundled Patrick Hand lettering, and
the existing notebook-paper generator. Existing photographed artwork is
unchanged. Edit timing and paths in `render_computer_control_bonus.py`; the
player template is `computer_control_bonus_player.html`. Review checkpoints
and contact sheets live in `source/computer_control_bonus/`.

```bash
# From animations/pencil-codex:
../.venv/bin/python render_computer_control_bonus.py --prepare-only
../.venv/bin/python render_computer_control_bonus.py
../.venv/bin/python ../scripts/verify.py out/computer_control.mp4
../.venv/bin/python ../scripts/verify.py out/saloon_doors.mp4
../.venv/bin/python verify_computer_control_bonus.py
```

Use `--scene computer_control` or `--scene saloon_doors` for a single scene.

### Existing photographed sketch set

All crop boxes, layout positions, teaching-beat times, and motion settings are
near the top of the two renderer files. A spacing, timing, paper, or contrast
request normally takes 2–5 minutes to edit plus render time. A single sketch
can be regenerated independently. Replacing handwritten wording takes about
5–10 minutes because the new linework must first be added to its source photo
or supplied as another photographed label.

Run `./render.sh` after any revision. It regenerates the audit images, MP4, and
GIF deterministically; then run `verify.py` before committing the result.

## Task C completion (2026-07-15)

The brain-in-harness animation is built from Sarah's supplied brain reference
and giant-headed stick figure. Its presenter player has exactly two gated
stages—Brain, then Harness—and slots before the Engine Factory.
