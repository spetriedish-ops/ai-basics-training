# AI Basics bonus — The Mall Behind the Mall

## Creative direction

This nugget pivots from the notebook-pencil world into a spooky 1985 mall
animation. Following Sarah's feedback, use the recognizable Stranger Things
title vocabulary: crimson outlined serif letters, deep shadows, eerie neon,
industrial tunnels, and the sense of an ordinary storefront concealing a
much larger system.

The opening is deliberately an ordinary, unbranded daylight mall. Establish
the storefronts and reveal the back corridors before introducing the show
reference. A presenter click then dims the lights and brings in Starcourt's
names, red title, and spooky palette. Do not show that branding during either
of the neutral opening holds.

The teaching priority is invisibility to the end user. Computer control uses
the public storefronts, where we can watch a cursor navigate. MCP, CLI, and
direct API requests begin and remain entirely backstage. Their paths must
never cross the public concourse or enter through a storefront. A viewer-only
cutaway exposes the hidden routes; the public interface remains still.

The animation should be an original homage rather than a shot recreation.
Use fictional storefronts, original characters, and no Stranger Things
character likenesses. The narration can name Starcourt. The images borrow the
period vocabulary: cream tile, angular skylights, brass rails, tropical
planters, saturated pink/cyan/orange neon, geometric signs, fluorescent back
hallways, steel service doors, pipes, rolling inventory cages, and chunky
access badges.

### Visual grammar

- **Public UI:** shadowed storefront glass, neon signage and reflections,
  geometric skylights, tropical planters, and visible cursor interactions.
- **Service/API layer:** cold blue-gray concrete, fluorescent tubes, red lamps,
  pipes, loading carts, and locked doors. Show this only as a labeled cutaway.
- **Agent:** a small teal mall courier in an oversized 1980s windbreaker. Teal
  remains the familiar AI cue from the earlier animation set.
- **User authority:** a laminated access badge. The badge always names its
  permitted action; a key never implies unlimited access.
- **Request:** a small order slip with a verb and object, such as
  `GET ISSUE TEAM-24` or `CREATE ISSUE IN PROJECT A`.
- **Response:** a matching labeled parcel or receipt. Errors return as visible
  stamped slips; nothing silently succeeds.
- **MCP:** a large illuminated mall directory/menu containing named tools and
  short descriptions.
- **CLI:** a service-desk terminal that accepts a typed command and prints a
  response.
- **Direct API:** the courier presents a precise request and scoped badge at a
  particular locked service door.
- **Guardrails:** security checkpoints, velvet ropes, badge readers, and audit
  cameras. Labels carry meaning; color only reinforces it.

The public mall has gentle neon bloom. The back corridor should feel cooler
and more ominous, with restrained dust and creeping cable silhouettes. Keep
the spooky atmosphere readable and playful. An over-engineered basement
control room can supply the script's Starcourt wink after the teaching point.

## Research anchors

The production used Gwinnett Place Mall near Duluth, Georgia, which opened in
the early 1980s. Its existing two-story food-court atrium, angular architecture,
and vaulted geometric ceiling made it a strong period location. The crew
reconstructed storefronts, signs, displays, kiosks, and a theater facade; many
stores were dressed deeply enough to be camera-ready. The set's neon was
custom-built and the mall itself supplied much of the colored light.

The season's service hallway, loading dock, hidden elevator, tunnel, and base
are story geography. For this nugget, the real retail/service relationship is
the teaching model; the fantastical underground scale is a visual joke, not a
claim about how a mall or an API works.

Reference reading:

- Los Angeles Times interview with production designer Chris Trujillo:
  https://www.latimes.com/entertainment/tv/la-et-st-stranger-things-3-starcourt-mall-how-they-made-it-20190711-story.html
- Australian Cinematographer interview with Lachlan Milne, pages 29–30:
  https://cinematographer.org.au/wp-content/uploads/2021/09/Issue_83_webres.pdf
- Official Netflix behind-the-scenes episode on Starcourt:
  https://www.youtube.com/watch?v=48mFNGf5gdE
- Netflix Season 3 recap for the fictional loading-elevator route:
  https://www.netflix.com/tudum/articles/stranger-things-season-3-recap

## Animation sequence

These are presenter-paced clips, not one continuous five-minute film. Each
clip should end on a living hold: neon hum, escalator motion, fluorescent
flicker, or a gently moving cart. Existing Toolbox and MCP/CLI/API animations
can be used as quick callbacks before this new world opens.

### Clip 1 — Welcome to the mall · 12–15 seconds

**Narration:** recap of Nuggets 6 and 7; this nugget teaches the mental model.

The teal courier exits the old pencil world through a sketched doorway. The
paper peels away like a construction tarp to reveal a saturated 1985 mall
atrium. A neon title switches on: `THE MALL BEHIND THE MALL`. A directory
shows five fictional stores: ISSUES, PROJECTS, DOCS, PEOPLE, and CALENDAR.

**Hold:** wide atrium with shoppers, escalators, and the courier at the map.

### Clip 2 — Storefront and back room · 20–24 seconds

**Narration:** public concourse and storefronts are the user interface; storage
rooms and kitchens stay out of sight.

Begin with a shopper entering the bright ISSUES storefront. A clerk performs a
curated interaction at the counter. The camera rises into a clean architectural
cutaway: glass storefront and merchandise in front, shelves and boxes in the
stockroom, then the service corridor behind it. Other stores join the cutaway,
all opening onto the same hidden corridor.

**Teaching labels:** `USER INTERFACE`, `BACK ROOM`, `SERVICE CORRIDOR`.

**Gag:** a mountain of boxes passes behind the wall while the shopper calmly
receives one tiny, perfectly wrapped parcel.

### Clip 3 — Every back door is an endpoint · 18–22 seconds

**Narration:** locked back doors are API endpoints; the right key may allow a
read or write.

Track down the corridor past labeled doors:

- `GET / ISSUE`
- `CREATE / ISSUE`
- `SEARCH / DOCS`
- `READ / PROJECT`

The courier tries the wrong badge at `CREATE / ISSUE`; the reader returns
`DENIED — READ ONLY`. The correct scoped badge opens only the intended hatch.
The courier passes in `GET ISSUE TEAM-24`; a labeled issue parcel returns.

**Accuracy note:** use a badge with named permissions rather than a skeleton
key. The door checks the request and the caller's authority every time.

### Clip 4 — Storefront route versus API route · 22–26 seconds

**Narration:** computer use approaches through storefronts with the signed-in
user's access; an API call makes a more specific request.

Split screen, then merge into one mall cutaway:

- On the public side, the courier enters the main doors, checks the directory,
  rides an escalator, finds ISSUES, opens the signed-in user's view, searches,
  selects a project, opens a form, and clicks Create.
- In the service corridor, a second courier walks directly to
  `CREATE / ISSUE`, presents `CREATE ISSUE IN PROJECT A` plus a badge labeled
  `PROJECT A · CREATE`, and receives either the created record or a clear error.

Above both routes, an audit ticker records each action. The API side has fewer,
more explicit steps. The storefront side retains broader navigational freedom.

**Caption:** `Same service. Different interaction surface.`

### Clip 5 — The MCP menu · 22–25 seconds

**Narration:** MCP provides a menu of tools and descriptions; a huge menu costs
context and can lead to a wrong choice.

The MCP directory lights up with a useful handful of tool cards. The courier
chooses `GET ISSUE` and reaches the right door. Then the directory mechanically
unfolds—one panel, four panels, sixteen panels—until hundreds of nearly similar
entries fill the backstage corridor. Description cards spill from the directory into the
courier's backpack, whose `CONTEXT` meter rises. The courier selects
`GET ISSUE COMMENTS` when it needed `GET ISSUE`, receives the wrong parcel,
returns it, and pays two more token-shaped arcade coins to try again.

**Recovery beat:** collapse the directory back to a curated set. The correct
choice becomes easy again.

### Clip 6 — The CLI service terminal · 18–22 seconds

**Narration:** the agent can type a command and read the result; it may use less
context, but can choose a wrong command or misread output.

At an employee service desk, the courier types a concise command into a green
phosphor terminal. A pneumatic tube carries the request toward the same locked
door from Clip 3. A receipt prints with the issue result.

For the failure beat, one character is mistyped. The tube diverts to the wrong
door and an error receipt unspools across the floor. A second result arrives as
a dense wall of text; the courier follows the wrong line with a ruler before
correcting itself.

**Caption:** `Lighter directions. More interpretation.`

### Clip 7 — Same destination, different route · 20–24 seconds

**Narration:** direct API, MCP, and CLI often converge; one route may call the
API behind the scenes.

Use an overhead mall map. Three routes animate toward the same service door:

1. `DIRECT REQUEST` enters at the badge reader.
2. `MCP TOOL` begins at the directory and travels through a tool chute.
3. `CLI COMMAND` begins at the terminal and travels through a pneumatic tube.

All three become the same small request slip before reaching the door. The
door performs the same permission check and returns the same issue parcel.

**Caption:** `Same destination. Different way of getting there.`

This is the core mental-model tableau and should be reusable as a still.

### Clip 8 — MCP and CLI can overlap · 18–22 seconds

**Narration:** Rovo MCP and Teamwork Graph CLI are not an either-or choice;
some capabilities overlap and an agent may use either or both.

Two entrances feed a shared concourse behind the mall: MCP DIRECTORY and CLI
TERMINAL. Their route maps overlap at several capability doors. The courier
uses MCP for one request and CLI for the next. Matching capability cards light
up behind both access points to show the overlap. Both routes finish at the
same service desk. Do not imply MCP necessarily invokes the CLI executable;
overlapping capabilities do not establish that implementation relationship.

**Caption:** `One, the other, or both.`

The Venn-like overlap must be explicit; avoid drawing MCP and CLI as mutually
exclusive stacks.

### Clip 9 — Agency and guardrails · 24–28 seconds

**Narration:** predictable API call versus autonomous agent judgment; trust and
risk determine how much freedom an enterprise grants.

The first courier rides a fixed delivery belt from one request slot to one
door and back. A sign reads `ONE APPROVED ACTION`. This behaves like an
automation.

The second courier receives a goal card: `PREPARE THE PROJECT UPDATE`. It sees
several possible doors and plans a route. Security gates define the approved
zone; some doors are open, some require human approval, and some remain closed.
Audit cameras record its path. The courier completes the goal inside the
boundary and places a neat bundle on the counter.

Then briefly show the unsafe counterfactual: all gates lift at once and the
courier's route map explodes into hundreds of branches. Freeze before it takes
an action; a guard lowers the boundaries back into place.

**Caption:** `More judgment requires more trust.`

### Clip 10 — Context handoff · 10–12 seconds

**Narration:** next nugget digs into context.

Return to the MCP directory. Tool-description cards, the user's goal, recent
receipts, and route notes fill the courier's backpack. The `CONTEXT` meter
approaches full. The courier looks at the audience, then at a nearby luggage
scale labeled `NEXT: CONTEXT`.

**Hold:** backpack on the scale, with the mall continuing to glow behind it.

## Reuse map

- Open with 2–3 seconds from the existing Toolbox and MCP/CLI/API pieces as
  callbacks, then let the pencil artwork peel into the mall world.
- Reuse the computer-control cursor motion concept inside Clip 4, translated
  into the mall's storefront journey.
- Reuse the established teal agent cue, context meter, and labeled-card
  convention. Redraw them in the new cel/VHS treatment.
- Clip 7's overhead route map can recur during Clips 8 and 9.
- The API service door from Clip 3 should remain spatially identical in every
  later clip. This makes the convergence claim visually trustworthy.

## Production approach

Build the mall as reusable layered vector assets rather than a single painted
background: atrium, storefront row, stockrooms, service corridor, endpoint
doors, MCP directory, CLI terminal, security gates, and overhead map. Camera
moves and lighting changes can then create variety without redrawing the mall.

The recommended first proof is Clip 7. It tests the new style, the mall cutaway,
all three interaction routes, permission checks, and the central teaching
point in one 20-second sequence. If the style lands, Clips 2–9 can reuse most
of its geometry.

## Revised first sequence — 2026-10-01

Clip 7's first cut is available at `starcourt/interactive/index.html`, with a
silent 1080p master at `starcourt/out/mall_routes.mp4` and a standalone final
tableau at `starcourt/out/mall_routes_still.png`. Its six presenter beats cover
visible computer control, a hidden-corridor reveal, MCP, CLI, direct API, and
a return to the public view. The revised cut runs 46 seconds.

The mall, cursor, backstage agent, service door, paths, and reveal are editable in
`starcourt/render_mall_routes.py`. The other proposed clips remain storyboard
concepts pending feedback on this visual treatment. The bright first cut's
source and still are preserved in `starcourt/source/v1/`. Its frontend-crossing
routes are superseded by the revised topology.

## Presenter collection built — 2026-10-01

The same player now opens with a 19-second, three-beat mall introduction:
daylight public view, daylight corridor cutaway, and a separately cued spooky
transformation. It holds indefinitely before the reference until advanced.

The 34-second MCP directory film shows a useful menu unfolding into more
tool descriptions, those descriptions filling the context backpack, a wrong
comments-tool choice, and a retry that retrieves the issue details. Symbolic
arcade coins accompany menu reading and recovery; context does not reset.

The 35-second CLI film types an illustrative command, sends a request down a
hidden pipe, and prints the returned data. It demonstrates confusing checklist
completion with issue status, then a separate command typo that never reaches
the service. The final beat corrects the command and receives the issue.

The player now contains eight scenes with per-beat holds and matching
downloads. A 13-second secret-elevator interlude starts in an ordinary service
hallway, descends to B27, and reveals an original underground-lab gag.

Clip 8 is a 26-second MCP/CLI capability map. The interfaces enter on separate
lanes, retain exclusive actions, and meet only at the shared READ ISSUE and
SEARCH DOCS doors. This keeps overlap distinct from an implementation claim.

Clip 9 runs 31 seconds. It contrasts one fixed request with an agentic goal,
then shows several approved choices, persistent audit cameras, a denied
out-of-bounds door, a brief explosion of unsafe routes, and restored gates.

Clip 10 runs 15 seconds. The task, tool descriptions, recent results, and route
notes fill the courier's context backpack before it lands on a scale labeled
`NEXT: CONTEXT`.

Sarah chose to skip the standalone scoped-credentials/endpoint clip for this
recording set. The existing route-comparison scene still shows an access check
before the hidden service door opens.
