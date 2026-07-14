# Storyboards — the Jobsite set

Status: **produced** (2026-07-03) — the original five scenes built from
this doc at Sarah's "build it all in its current state" go-ahead,
pixel-verified, and committed to `renders/final/`. Scene 6 (The Toolbox)
added 2026-07-13 at Sarah's direct request, produced same-day. Redlines
now apply to the rendered set; deviations taken during production are
listed at the bottom. Locked decisions this doc builds on:

- **World: the Jobsite.** One world, five zoom levels. Chosen over kitchen /
  brick-studio / music alternatives: physics teaches the limits (weight, sag,
  spill, fuel), the agent is a machine (no anthropomorphism, no character
  animation), and every concept on the agenda has a slot.
- **Humor: feral escalation.** Each scene may carry ONE escalation gag — a beat
  that goes exactly one step too far. Gags mock failure modes, never the
  audience, never the tech's usefulness. No running gags, no meta-humor: a gag
  that flops flops once, in one scene.
- **Honesty beats stay sincere.** Metaphor-limit corrections (bed empties,
  attachments come off, only the result returns) are straight beats with
  straight captions. Comedy and guardrails don't share a beat.
- Chatbot-vs-agent gets no standalone scene — the Garage's forklift beat
  carries that ah-ha.

## The world legend (recurring vocabulary)

| Image | Meaning |
|---|---|
| engine | the model (a prediction engine) |
| the paver | how the model works inside (companion scene) |
| truck | the agent |
| bed | context window |
| fuel gauge | tokens (in AND out) |
| bolt-on attachments | tools |
| manual cards riding in the bed | tool definitions (cost even when unused) |
| glovebox blueprints, pulled on match | skills |
| look → pick → work → check | the agent loop |
| the site: pump, dispatch radio, gates + foreman | the harness (and permissions) |
| vans with their own beds, returning one package | subagents |
| the fleet + crew chief | orchestration |

Caption rules: ≤ 8 words, lowercase, no "it's not X, it's Y" variants.
Every scene opens and closes on an empty stage (clean loop).

---

## Scene 1 — The Garage (types of AI & model progression) · ~35s

| # | Action | Caption |
|---|--------|---------|
| 1 | Garage backdrop. A forklift runs a painted floor line, flawless. | rules: perfect on the line |
| 2 | A pallet sits two feet off the line. Forklift stops dead. Alert "!". | step off the line? it stops |
| 3 | A route van drives its learned route smoothly — then repeats it exactly through a traffic cone. One beat only. | learned one route. just that route |
| 4 | A teal engine lowers on a chain into an open chassis. | then: an engine for anything |
| 5 | Generation montage: same silhouette, bed grows, fuel-per-haul shrinks. | each generation hauls more per gallon |
| 6 | **GAG** — one poster past today: half-scribbled concept truck bristling with speculative nonsense (drawn sketchy/dashed), labeled NEXT YEAR'S TRUCK (PROBABLY). | *(label carries the joke)* |
| 7 | Today's truck rolls out. Forklift still working its line in the background — the old machines didn't leave. | meet today's truck |

Honesty flags: beat 3 stays short (no ML taxonomy lesson); beat 7 keeps the
forklift visible so "newer" never reads as "replaced everything."

## Scene 2 — The Paver (the model, tokens, hallucination) · ~40s

| # | Action | Caption |
|---|--------|---------|
| 1 | A teal paving machine at the end of a half-laid brick road. | the model predicts the next piece |
| 2 | A signpost word gets chopped into brick-sized chunks that feed the hopper. | words get chopped into tokens |
| 3 | Paver glances back along laid bricks (dotted sightline), lays the next. ×3, rhythmic. | each brick: whatever fits so far |
| 4 | Fuel gauge returns: ticks for bricks read AND bricks laid. | tokens in and tokens out both cost |
| 5 | A clear turnoff marker. The paver paves confidently straight past it — smooth, beautiful, into an empty field. | confident. smooth. wrong. |
| 6 | **GAG** — unbothered, it paves a proud little cul-de-sac around itself and plants a DONE flag. | *(none — let it breathe)* |
| 7 | Hold, then straight beat: | it predicts — it never checks the map |
| 8 | Zoom out: older bricks fade behind it; it only sees the recent stretch. Sets up the truck. | it only sees the recent road |

Honesty flags: beat 7 keeps the lesson on mechanism (predicts, doesn't verify),
so the gag lands on the failure mode, never on "AI is dumb."

## Scene 3 — The Truck v2 (context window & tools) · ~45s · evolves `context_window.py`

| # | Action | Caption |
|---|--------|---------|
| 1 | Truck rolls in; meter fades in. *(existing beat)* | everything you load takes tokens |
| 2 | Info cargo loads: INSTRUCTIONS, DOCS, CHAT. (Generic TOOLS block retired.) | *(carryover)* |
| 3 | Crane bolts on (click, dust puff) + its MANUAL card drops into the bed + meter ticks. Demo: hoists a crate in. | tools bolt on new abilities |
| 4 | Plow + floodlights rapid-fire, each with manual card, truck sagging more each time. | every tool adds weight, even unused |
| 5 | **GAG** — escalation: pizza oven, disco ball, a second smaller crane *for the first crane*. Sagged to the axles, fuel needle bent past the gauge edge. | surely one more |
| 6 | The actual job arrives: one small crate, lift ring. The truck trembles. Nothing deploys. | so many tools it can't choose |
| 7 | Overflow: MORE DOCS lands on the manual pile; CHAT falls out. *(existing beat, caption trimmed to budget)* | overfill the bed and things fall out |
| 8 | Dump — bed empties AND every attachment unbolts and clatters off. Truck returns to stock. Sincere beat, no gag. | session over — everything comes off |
| 9 | Sparkle; fresh truck; roll out. *(existing)* | every new session starts empty |

Honesty flags: beat 8 is the load-bearing correction (context AND tool
definitions reload every session). verify.py beat spec must grow to cover
beats 3–6 (attachment colors, manual-card inks, ALERT at 6).

## Scene 4 — Pop the Hood (anatomy of an agent) · ~60s · the flagship

| # | Action | Caption |
|---|--------|---------|
| 1 | Empty stage; chassis rolls in; parts assemble one by one, labeled. | meet the agent, part by part |
| 2 | Engine lowers in; hood pops open to reveal a tiny paver cameo working inside. | the model: the prediction engine inside |
| 3 | Bed clicks on. | the context window: its working memory |
| 4 | Crane + floodlights bolt on. (Tools BEFORE skills — teaching order.) | tools: what it can do |
| 5 | A job card appears; the glovebox opens and the matching blueprint unrolls — only on match. | skills: how to do jobs well |
| 6 | The loop, drawn as a circular road: LOOK → PICK → WORK → CHECK. Lap 1: the check catches a crooked crate. | look, pick a tool, work, check |
| 7 | Lap 2 fixes it. Job card stamped done. | and go again until it's done |
| 8 | Zoom out: fuel pump, dispatch radio, fences and gates. | the harness: the site around it |
| 9 | **GAG** (light) — truck approaches a keyhole-marked gate, bounces off politely; foreman stamps APPROVED; gate opens; dust puff. | gates and sign-offs keep it safe |
| 10 | A small van pulls up alongside. Hold. Transition bait for Scene 5. | and sometimes… it calls for backup |

Honesty flags: beat 5's on-match unroll is the accuracy point (skills load on
demand; tool manuals ride along always — the bed shows both). Beat 9 makes
permissions physical without mocking them.

## Scene 5 — The Fleet (subagents & orchestration) · ~45s

| # | Action | Caption |
|---|--------|---------|
| 1 | Chief truck faces a BIG job card: BUILD THE SHED. | some jobs are too big alone |
| 2 | Radio squawk; a van is dispatched and drives off-screen. | a subagent goes off to work |
| 3 | Cutaway: the van at its own corner — its OWN little bed, its OWN fuel gauge, loading its own context. | its own bed. its own fuel |
| 4 | Van returns carrying ONE wrapped package → into the chief's bed. Sincere beat. | it brings back only the result |
| 5 | Scale up: three specialists (crane truck, tanker, digger) dispatched in parallel; modules return; the shed assembles. | one coordinator, many specialists |
| 6 | **GAG** — the chief gets cocky: a van for every nail, two vans collide, one van dispatches its *own* van, package avalanche buries the chief to its mirrors. | coordination is also a job |
| 7 | Recover: three vans, staggered, smooth. Shed done. Wide shot: the whole site at golden hour — forklift on its line, paver paving, fleet parked. | now you can read the whole site |
| 8 | Fade to empty stage. | *(none)* |

Honesty flags: one van FIRST (beat 2–4), fleet second — subagents are not
inherently plural/parallel. Beat 4 is the most-misunderstood fact in the set;
it stays gag-free.

---

## Scene 6 — The Toolbox (MCP) · ~25s · added 2026-07-13

From Sarah's pencil sketch (assets/sketches/03). Job: TOOL SELECTION and
curation — deliberately distinct from Truck v2, which teaches weight.
New legend entry: **a tool chest bolted to the truck = an MCP server**
(one connection, many tools at once; matches the simulator's MCP box).

| # | Action | Caption |
|---|--------|---------|
| 1 | Truck rolls in; a chest labeled TICKETS drops onto the bed rim. | one connection brings a whole toolbox |
| 2 | Chest pops open: four tools fan out (SEARCH / CREATE / UPDATE / COMMENT); each drops an instruction card into the bed, meter ticking. Truck sags a touch. | every tool ships an instruction card → the cards ride along, used or not |
| 3 | Job card FIND TICKET 42: the wrench flies over, sparkle, found. | more tools, more you can do |
| 4 | **GAG** — CALENDAR chest, then WIKI chest stack on; six more cards rain in; meter red. | surely one more box |
| 5 | Job card COMMENT ON 42: tools twitch, unsure — the CALENDAR mallet lunges and bonks the card. "?" over the cab. Sincere risk, comic delivery. | so many tools it grabs the wrong one |
| 6 | The fix (sincere): extra chests unbolt and drop away, their cards leave, meter back to teal; the COMMENT pen does the job. done! | curate the toolbox for the job |
| 7 | Exit with the one curated chest aboard. | *(carryover)* |

Honesty flags: the wrong-tool grab is real behavior (selection degrades
with tool count), so beat 5's caption states it straight; the curation
ending gives the practical takeaway rather than ending on failure.

## Scene 7 — The Engine Factory (model lifecycle incl. inference) · ~24s

For run-of-show beat 1: the life of a model, requested by Sarah for the
pre/post-training gap; inference beats added 2026-07-14.

| # | Action | Caption |
|---|--------|---------|
| 1 | An assembly machine chews through a mountain of material blocks; an engine rolls out onto the belt. The leftover pile stays — there is always more material than one engine eats. | pre-training: built from mountains of material |
| 2 | The dyno: gauge sweeps, a wrench makes adjustments, a checklist ticks "ok" three times — and the pistons turn teal. | post-training: tuned to be helpful and safe |
| 3 | Pedestal, NEW! banner, confetti and sparkles. | release day: a new model, much hullabaloo |
| 4 | An open chassis rolls in; the engine seats into it. | then it goes to work |
| 5 | The factory dims behind it; a CLOSED sign swings on. Building is over. | training happens once, back at the factory |
| 6 | The truck cruises through three micro-jobs; each engine rev puffs and ticks TWO counters: the fuel meter and a new INFERENCES odometer (1 → 2 → 3). Then a beat on the engine, unchanged. | inference: every time the engine runs → the road never changes the engine |

Honesty flags: material feeds the MACHINE, never the engine (models
don't store training data); the odometer makes inference COUNTABLE —
the property that separates it from every other concept — and the
same-engine beat pins "no learning during use." No gag; the confetti
carries the wink.

## Parked (not in the set)

- **MCP vs CLI vs API tradeoffs** (P1 in the original brief) — the MCP
  half is now covered by Scene 6; the CLI/API comparison lives in Sarah's
  sketch 03 as a handout/slide. If it later earns an animation: a supplier
  hands the truck a rambling handwritten note (CLI prose output) vs a
  labeled pallet, shrink-wrapped and manifest attached (MCP structured
  output).

## Production notes

- **Recommended production order** (value ÷ risk against the July 10 content
  lock): Truck v2 (closest to done, anchors the attachment parts) → Pop the
  Hood (flagship, reuses everything) → Paver → Fleet → Garage. The Garage
  degrades gracefully to 3 stills on a slide if time runs out.
- **Part reuse:** attachments built once in Truck v2 serve Scenes 1, 4, 5.
  The van = scaled truck with 2 wheels. The paver = new build (hopper + roller
  + laid-brick trail). Garage/backdrop, gates, dispatch board = new flat props.
- Every new scene needs a beat spec in `scripts/verify.py` in the same commit.
- Durations above are talk-track ceilings — each scene must also survive being
  paused on any beat while Sarah talks.
- Concept sketches for the Truck v2 attachment direction live in
  `src/scenes/sketch_attachments.py` (stills, not production code).

## Production deviations (2026-07-03)

- **Scene 2 gag:** the cul-de-sac became a **loop-de-loop** — a circle of
  road reads as nothing in side view; a vertical loop reads instantly and
  is funnier. DONE flag on top kept.
- **Scene 1 montage:** "bed grows per generation" simplified to GEN 1/2/3
  plaques + a perk-up bounce + "fuel / load: down, down, down" — swapping
  bed geometry mid-scene cost more than the beat earned.
- **Scene 4:** the model callout is a bubble with a mini-paver cameo
  pointing at the cab (no literal hood-pop — the cab has no hood seam).
  Runtime came in at ~34s, well under the 60s ceiling.
- **Scene 5 recovery caption** is "three vans, on a schedule" (the doc's
  beat 7 had no caption specified for the recovery moment itself).
- Scene 3's gag order peaks on the crane-for-the-crane (oven → disco ball
  → mini crane), with the disco ball hung from the big crane's boom.
