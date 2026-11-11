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

### Context continued: one portfolio, four agents (2026-11-09)

`interactive/context_portfolio/index.html` now follows the portability point
before returning to context-window space. Its eight presenter-controlled beats:

1. Open the literal folder containing ten `.md` files.
2. Open `identity.md` and show its ordinary text.
3. Shrink the monitor into the center of a four-quadrant room view.
4. Send copies of the first five files to all four rooms.
5. Complete the same ten-topic portfolio in each separate conversation.
6. Zoom continuously into the original classroom with its loaded stacks.
7. Move closer to those existing stacks, without reloading or replaying drops.
8. Pull back to see the space the portfolio occupies.

The four rooms are classroom, corporate office, retro spaceship, and wellness
studio. Each has the same approved human character, paired with its own agent.
Three gaze cels adjust his eye line to each new agent's height; the classroom
retains his original downward gaze. The monitor uses a transparent cutout and
fits inside the central gutter without covering the room corners.
The source folder remains visible during delivery. Each cube travels continuously
from the monitor to a visible crest above its room's ceiling, then drops onto its
stack. The same cube geometry renders across quadrant boundaries, with matched
position and velocity at the start of the fall. Deliveries are staggered by 0.28
seconds between rooms, then land with the approved squash, rebound, and dust. Two five-box towers
form in each room. These represent copies of files, not shared live conversation
state. Boxes remain small; camera movement makes their labels readable.

The three new room/agent plates were made with the built-in image-generation
tool using Sarah-approved concept sheets. Assets, reference sheets, and the
exact production prompts are in `assets/context_portfolio/`. The same human
is composited from Pair B cels and a matching generated gaze sheet (with its
prompt saved alongside it). The original classroom and close-up
remain native scene compositions. Every hold retains subtle sketch-line boil;
completed actions stay still. No connected accounts or real personal data are used.

Click, Right Arrow, or Space advances when holding; Left goes back, R replays,
H hides controls, and F enters fullscreen. There is no automatic beat advance.
The silent 1080p30 export is `out/context_portfolio.mp4` (79 seconds, 18 manual beats).
The original context-nugget walkthrough remains unchanged.

The appended maintenance example starts with the user introducing The Industrial
Nugget Factory and its team: Jack Sparrow (Account Manager), Ted Lasso (Solutions
Engineer), and David Beckham (Customer Success Manager). Five individually held
Markdown edits update identity, current projects, goals and priorities, team and
relationships, and role and responsibilities. A pencil writes the revised text;
the existing classroom boxes gain green revision seals. The camera shows five
files saved to the computer before the other agents explicitly load revisions.
Each incoming revision meets its existing box; neither the stacks nor the number
of boxes grows. Saving a portfolio file alone is not shown as automatically
refreshing a running conversation. All names and account data are fictional.

Use `?start=updates` to hold at the classroom immediately before the new section.
The first update beat still waits for a click. `source/context_portfolio/update-storyboard.jpg`
contains the visual checkpoints.

Rebuild the current version with:

```bash
../.venv/bin/python render_context_portability.py
../.venv/bin/python render_context_portfolio_update.py
```

`--prepare-only` produces stills and each renderer's storyboard. The update
renderer reuses the first eight existing clips; rerun only it to revise this
section. Running portability alone produces the eight-beat opening sequence.
The older `render_context_portfolio.py` supplies shared monitor, cube, and impact
code; running it directly rebuilds the earlier classroom-only study. The new
player uses `shared-beat-*.mp4` and `shared-hold-*.mp4` so old clips remain available.

### Context continued: one very long conversation

`interactive/context_monothread/index.html` combines the 18 portfolio beats with
seven new beats. Use `?start=monothread` to hold immediately before the new section;
the first action still requires a presenter click. The earlier portfolio preview
and its 79-second export remain available independently.

The classroom retains its updated portfolio. The user keeps account planning,
CRM tools, email drafts, meetings, QBR slides, forecasting, competitor research,
launch planning, debugging, meal planning, and espresso experiments in the same
conversation. A 20-second VHS montage uses horizontal tracking distortion,
scan lines, a fast tape counter, and a persistent `CHAT 01` indicator. The cubes
include MCP tool definitions, tool calls, results, and conversation topics.
Only this montage is accelerated. Tracking and conversation activity finish
before its native hold loop.

The picture returns to normal for an earlier-pilot-goals question. The agent
walks a continuous serpentine aisle, checks a meal-plan stack and an espresso
stack, then finds the original decision: less manual follow-up and faster
handoffs. Cast and boxes share floor perspective and depth sorting. Stack heights
leave the agent visible while its lower body is naturally occluded. The human
steps aside during accumulation and turns to follow the search. Search movement,
the inspection lens, and speech freeze before each narration hold; sketch lines
retain their native boil.

The search now uses six expression cels for each character. The agent scans with
its eyes, blinks, furrows its brow, strokes its mustache/chin, and raises a finger
at the discovery. Its thinking upper-body cels combine with the approved stepping
legs. The human follows the aisles with changing gaze, puzzled reactions, blinks,
and a relieved smile. Expression changes finish before holds. The transparent
sheets were made with built-in image generation; the exact prompts and approved
source references are saved in `assets/context_monothread/expression-prompts.json`.
Use `--search-only` to rebuild only the three changed search clips and the master.
The espresso inspection is composited at its box's depth, so the foreground
human naturally occludes the magnifying glass and its handle. Its stop sits
left of the human, keeping the box, lens, and agent visible beside him.

Rebuild after the portfolio and update renders:

```bash
../.venv/bin/python render_context_monothread.py
```

`--prepare-only` renders stills, `source/context_monothread/storyboard.jpg`, a
floor-plan audit, and the supported cube layout. The renderer reuses all 18
earlier clips. This renderer produces a silent 1080p30 combined export
(133.5 seconds, 25 manual beats). The compaction renderer below extends that master.
The Mac renderer uses Menlo for the VHS display,
with the bundled hand font as a fallback; playback requires no installed fonts.

### Context continued: cost and compaction

`interactive/context_compaction/index.html` is the newest complete click-through:
29 manual beats, with the money gag inserted after accumulation and before the
retrieval question. Nine winged bills flutter out of the user's hoodie pocket,
followed by one last coin. Use `?start=cost` to begin immediately before that gag,
or `?start=compaction` to begin immediately before the chamber reveal.

After the search, blast shutters reveal a grimy, sketch-style sci-fi trash
compactor. Its contents are represented by 49 separate pieces in two shallow
rows, including abandoned stormtrooper armor. `context_press_mechanics.py`
uses one room projection for the wall faces, cartons, armor, floor, and platen.
The walls first close the air gaps: outer cartons move, touch their neighbors,
and transmit pressure inward. Each carton retains its own face and folds inside
its collision bounds. An irregular fifteen-panel fold mesh gives each face
deep asymmetric creases, pinched edges, folded lips, and distorted label
fragments, with alternating light and shadow across the folds. Dented lids and
side creases carry the crumpling around each carton. Depth stays fixed throughout.

The overhead platen contacts the tallest stacks first; supported columns crush
from the top down. The final cube consists of the same pieces, with their
original textures and armor, and stays crushed when the walls and platen lift.
There is no separate replacement cube or whole-pile scale/fade transition.
The SUMMARY label appears on that compacted block. This is a playful metaphor
for summarization, not lossless data compression. Each action ends in a stable,
subtly jittering hold until the presenter clicks.

`verify_context_press.py` checks every piece against the walls, floor, ceiling,
other pieces, and its supports across 422 squeeze/press states. It also checks
outer-first contact, tallest-first press contact, fixed depths, persistent
identities, and narration hold boundaries. A further 30,135 panel checks verify
that the exaggerated folds remain convex and inside their contact bounds.

The room was created with built-in image generation; its saved artwork and exact
prompt are in `assets/context_compaction/`. Moving walls, cubes, cash, the overhead press, the native sketch armor prop,
and the brace are rendered locally. Rebuild after the mono-thread clips:

```bash
../.venv/bin/python render_context_compaction.py
```

`--prepare-only` creates the storyboard and review stills without encoding video.
The renderer reuses all 25 prior clips, adds four new clips and their native hold
loops, and writes `out/context_continued.mp4` (156 seconds, silent 1080p30).

### Context continued: missing detail and reported inbox incident

`interactive/context_loss/index.html` is the latest full click-through: 37 manual
beats. Use `?start=loss` to begin before the return to the classroom, or
`?start=inbox` to begin before the separate email example.

The original user and agent return to an otherwise empty classroom with the
same 49 compressed pieces forming the SUMMARY cube. The user asks for the pilot
success measures agreed with Ted—the measures established earlier in the
montage. The agent walks to the cube and unfolds a note containing broad topics,
then explains that the exact measures are missing and asks for a reminder.
The cube is drawn using the same carton surfaces with the classroom projection.

A paper wipe introduces a separate vintage-monitor and phone composition.
A visible approval request remains on the phone while fictional messages move
from an inbox to Trash. Further stop requests appear on the phone, followed by a
local Stop agent action. Some mail stays visible. This is explicitly labeled as
a reported incident, and the interface, dialogue, and local control are stylized.
Source links, claim limits, and suggested narration are in
`source/context_loss/incident-notes.json` and in the player’s source notes.

Build after the compaction clips:

```bash
../.venv/bin/python render_context_loss.py
```

`--prepare-only` writes hold stills and a storyboard. The renderer reuses the
29 previous clips, appends eight new actions and native sketch holds, and writes
`out/context_continued.mp4` (188.5 seconds, silent 1080p30). Every action settles
before its manual hold, including the envelope flights and local stop hand.

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

### Inbox metaphors: topiary and laundry (2026-11-11)

Two alternative silent, 37-second cartoons, each with six presenter-controlled
beats and native half-second line-boil holds:

- `/pencil-codex/interactive/inbox_laundry/index.html`
- `/pencil-codex/interactive/inbox_topiary/index.html`

Click / Space / Right Arrow advances once the current action finishes. Left
Arrow goes back, R replays, H hides controls, and F enters fullscreen. Each
preview links to the other option and its downloadable 1080p MP4. Serve the
`animations/` directory on port 8765. These are standalone alternatives for
review; neither silently replaces the existing full context-continued master.

Both explicitly show an expanding context list, with the original approval
rule retained until compaction. A hand-cranked summarizer produces a shorter
summary; the omitted red approval strip falls beside it and stays visible.
Only then does the agent discard the task inventory. Laundry enters a separate
metal trash can, while the topiary loses individual foliage clumps and its
trunk, leaving a stump with a bow. The fictional researcher returns to the reveal.
This is a metaphor for the reported explanation, not a verified reconstruction.

Renderer: `render_inbox_metaphors.py`. Generated artwork, source concepts and
full built-in-image-generation prompts live in `assets/inbox_metaphors/`;
`animation-prompts.json` covers the cast/clothes and `topiary-v2-prompt.json`
covers the final garden props. Sprites retain alpha; cels, paper, machine,
scissors and individual inventory trajectories are animated separately.
Storyboards and motion contact sheets live in `source/inbox_metaphors/`.
Exports: `out/inbox_laundry.mp4`, `out/inbox_topiary.mp4`.

```bash
# From animations/pencil-codex:
../.venv/bin/python render_inbox_metaphors.py --prepare-only
../.venv/bin/python render_inbox_metaphors.py --kind both
node verify_inbox_metaphors.cjs
```

Validated the manual player flow, loading/replay/error guards, all media paths,
37-second exports, silent 1080p/30 encoding, full master decoding, inventory
preservation and stationary action endpoints across all twelve holds.

Revision `inbox-metaphors-2`: character registration is calculated before any
ink deformation; the agent has no idle deformation or position jitter. The
human keeps subtle local ink movement with a fixed anchor. One continuous,
stationary floor stroke now spans each scene. Speech bubbles use a single
perimeter including their tail. The compactor is composited as a transparent
silhouette, its wheels meet the floor, and its crank retracts after compaction
to clear the laundry throwing pose. Both previews and MP4 exports are rebuilt.

Revision `inbox-metaphors-3`: topiary is the selected treatment. The remaining
apparent white rectangle in the ta-da pose was traced to sprite extraction:
the left glove extends across its nominal atlas cell, so the old crop removed
the fingers. Robot cels now use full connected silhouettes from the original
atlas, recovering the whole hand without replacing the approved artwork.
Topiary shears now have broad isosceles-triangle blades, a heavier outline,
larger handles and a larger hinge. The fixed character extraction also applies
to the retained laundry alternative.

Revision `inbox-metaphors-4` (laundry): returns to the clearer laundry metaphor
with three larger garments instead of twelve patterned items. A plain teal
shirt and slate trousers sit on a simple folding table; white boxers with red
hearts sit in a laundry basket below. The rack is removed. Throws are spaced
apart and slowed. The last garment gets a lift, a 1.45-second disgust reaction,
a cheerful recovery, a casual wrist flick, and a continuous arc into Trash.
The original six beats and 37-second duration are retained; no disposal occurs
before compaction. Stationary character cels remain still. Topiary remains
available as the earlier alternative.

New project assets (built-in image generation):
`assets/inbox_metaphors/laundry-gag-poses-v1.png`,
`assets/inbox_metaphors/laundry-quiet-props-v1.png`.
Full prompts and source paths: `assets/inbox_metaphors/laundry-v4-prompts.json`.
The new robot poses use complete silhouette extraction and fixed feet anchors.
Review stills: `source/inbox_metaphors/laundry-ick-v4.jpg` and
`source/inbox_metaphors/laundry-v4-review.jpg`.

Revision `inbox-metaphors-5` (laundry): garment destinations are centered inside
the trash-can opening, with gentler resting angles. Each throw finishes its
horizontal travel above the opening before descending. Arriving and settled
contents are occluded below the front rim across the complete garment layer,
so sleeves and trouser legs cannot leak past the can's tapered sides. The
heart-boxer reaction, six beats and timing are retained. Landing close-ups:
`source/inbox_metaphors/laundry-trash-fit-v5.jpg`.

Revision `inbox-metaphors-6` (laundry): the agent faces left and looks up toward
the researcher throughout her instructions and exit. At 7.2–7.65 seconds it
makes a brief planted pivot toward the laundry, settling before the next hold
and the context-gathering beat. The opening holds remain stationary.

### Context continued: getting better, then Atlassian and Rovo

For the final recording and assembly handoff, see
[`ROVO-CONTEXT-CONTINUED-HANDOFF.md`](ROVO-CONTEXT-CONTINUED-HANDOFF.md).

`interactive/context_ending/index.html?v=context-ending-1` previews the four
closing beats: a larger classroom, a summary retaining the red approval
instruction, a preference saved outside the room and reloaded in a fresh
session, and the Atlassian/Rovo teaser. Each beat ends in a native ink-loop
hold for manual advance. Actors remain planted during those holds.

`interactive/context_continued/index.html?v=context-ending-1` assembles the
complete 43-beat nugget: portfolio, mono-thread, compaction, lost detail,
the chosen laundry treatment, and this conclusion. Add `&start=ending` to
start immediately before the new ending. This replaces the earlier inbox
treatment with the approved laundry sequence.

The supplied logo PNGs are preserved unchanged in `assets/context_ending/`;
the teaser proportionally displays them on white cards. Review stills and
`talk-track-updated.txt` are in `source/context_ending/`. The closing narration
now says “these capabilities are getting better.” The memory archive remains
outside the active context room; these visuals illustrate improvements, not
guarantees that every instruction survives compaction.

```bash
# From animations/pencil-codex:
../.venv/bin/python render_context_ending.py
```

Exports: `out/context_ending.mp4` and the assembled `out/context_continued.mp4`.
