# Visual language — "The Jobsite"

One recurring cartoon world so the set feels like a family. Read this before
adding a scene; all constants live in `src/style.py`.

## The world

A friendly jobsite. Work gets done here: things get loaded, hauled, built,
delivered. It maps naturally onto agents (goal → work → result) and it's warm
and physical for a mixed-literacy audience.

## The cast

- **The agent is always TEAL** (`#2EA79A`). In P0 it's the dump truck; in later
  scenes teal marks whatever plays the AI (the robot arm, the crew chief, the
  brain in the anatomy diagram). One glance = "that part is the AI."
- **Context/data/inputs are CARGO** — warm labeled blocks (amber, coral, lilac,
  sage). Color is variety only; the label carries the meaning (accessibility:
  never meaning-by-color-alone).
- **Trouble is ALERT orange-red** (`#E4572E`), used sparingly.

## The look — scribble edition ("kid's drawing brought to life")

- Everything is drawn like a child's crayon picture that got up and moved:
  wobbly hand-drawn outlines, translucent fills that color slightly outside
  the lines, a doodled sun in the corner.
- **Boiling lines:** each scene renders 3 times with different `SCRIBBLE_SEED`
  values; `scripts/boil.sh` interleaves the frames (5 frames per seed at
  30 fps ≈ 6 Hz) so the drawing looks continuously redrawn. Low amplitude,
  low frequency — lively, never strobing.
- Paper background (`#FAF7EF`), ink outlines (`#33323E`).
- **Presenter-controlled sketch holds:** keep the gentle line boil alive during
  every completed teaching beat. Supply a dedicated native looping hold clip
  (normally 15 frames: three drawing variants, five frames each, at 30 fps).
  Freeze the action at its completed state; only the sketch jitter continues.
  Hold indefinitely until the presenter explicitly advances. Never replay the
  drawing or the action to make a hold. Static posters are loading fallbacks,
  not the final hold for a sketched scene. Full-clip previews may run through
  beats only when deliberately selected. Plain empty paper needs no line boil.
- Text: **Patrick Hand** for titles/captions (legible handwriting),
  **Gochi Hand** for block labels (extra kid-scrawl). Both bundled, OFL.
  Captions ≤ 8 words, ≥ 28 pt equivalent — legible from the back of a room.
- Motion: bouncy ease-outs for arrivals (`ease_out_bounce`), gentle sine for
  travel. Dust puffs mark impacts.
- The clean flat-vector look (Baloo 2 labels, crisp shapes) lives on in git
  history and in `src/style.py`'s base builders — skip `crayonify()` to get
  it back.

## Context classroom art direction

Sarah's references for new characters and props entering the classroom are
the original *Scooby-Doo, Where Are You!*, *The Jetsons*, and *The Flintstones*.
Use the early Hanna-Barbera cartoon feel: clear, bold silhouettes, expressive
poses, economical linework, simple color fills, and warm painted backgrounds.
The approved empty classroom remains the visual anchor. Design original
characters and props that belong in that setting. Keep the established gentle
sketch-line jitter and presenter-controlled looping holds; these preferences
continue to apply as the classroom fills with context.

For the cast, emphasize goofy caricature and distinctive, imperfect proportions:
contrasting short/broad and tall/gangly silhouettes, eccentric hair, oversized
noses or ears, asymmetrical expressions, and awkwardly appealing robot shapes.
Sarah rejected the first character sheet as too conventionally good-looking
and evenly proportioned. Avoid fashion-model anatomy and polished generic robot
mascots. The comedy should live in each character's silhouette and posture,
while both human and agent remain likable and capable. Character sheet v2 is
an exploration of this correction, not an approved cast selection.

Keep the classic cartoon drawing language, but style the cast's hair and clothes
as exaggerated contemporary Silicon Valley fashion: outsized fleece vests,
hoodies, statement glasses, theatrical haircuts, oversized sneakers, and tech
wearables. Robots can comically echo their humans' styling. Preserve the goofy
body proportions and facial identities under the new outfits. The v3 Silicon
Valley sheet explores this wardrobe direction. Sarah selected **Pair B** from
`pencil-codex/source/context_characters/character-concepts-v4-mustache.png`:
the gangly broccoli-haired human in the beige hoodie and the squat teal robot
with a backwards mustard cap, charcoal vest, and oversized handlebar mustache.
The human walks with a loose, bent-kneed, heel-first Shaggy-like lope; the agent
uses brisk short steps and a barrel-body wobble, keeping its instruction leaflet
close. Preserve this pair's identities in subsequent classroom scenes. The door
may move to the right wall so their entrance reads clearly in profile.

Context occupies solid three-dimensional cubes in the classroom's perspective,
replacing flat Tetris panels. Start at the back-left corner, then spread outward
and stack on supported lower cubes. Reuse the humorous prop illustrations on
cube faces. Size these cubes roughly like basketballs relative to the human.
Early introductions and research should form a modest pile, leaving ample
space; save crowding and stepping aside for later accumulation. Keep speech
bubbles inside the room, but omit narration above and below the room. Preserve
an unobstructed route to the right-wall door.
Keep completed actions still while the established sketch-line boil continues.

For context transport, Sarah currently favors a simple open mine cart inspired
by the original Scooby-Doo reference: dark slate-blue tapered bin, small plain
metal wheels, economical ink outlines, and rails over chunky wooden sleepers.
Use the approved small cubes. Load copies below the rim onto the cart floor,
then stack upwards; near walls occlude the cargo. Avoid arranging flat props
above a vehicle as a decorative pile. Unload upper layers first, keep the model
outside the room, and bring the reply back into the next turn's context.
Use one railway geometry and sleeper spacing across camera views: the wide
view scales the track and cart with the classroom, then continues the same
rails out to the model. The model can briefly squash/stretch, rattle, light up,
and telescope cartoon mechanical parts while processing; finish and recover
before the reply travels back. Presenter holds freeze these actions.

## Voice rules for on-screen text

- Casual, direct, lowercase captions; UPPERCASE only for titles and block labels.
- Empowerment framing ("you're early").
- **Banned:** the "it's not X, it's Y" construction and all its variants.
  State the point directly.

## Pedagogy guardrails baked into P0

- The bed **visibly empties at session end** and the next session starts empty —
  context is working memory, never permanent memory.
- Token meter fills as cargo loads — tokens are the fuel bill, tied to load size.
- Overflow shows both failure modes: things fall out AND the truck gets sluggish.
