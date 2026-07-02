# Storyboards — the five-scene Jobsite set

Status: **in review** — Sarah redlines this doc (or comments in chat), then scenes
go to production one at a time. Locked decisions this doc builds on:

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

## Parked (not in the five-scene set)

- **MCP vs CLI vs API vs custom tools** (P1 in the original brief) — absent
  from the revised session agenda, so unscheduled here. If it earns a slot
  later it maps cleanly onto the Jobsite: a supplier hands the truck a
  rambling handwritten note (CLI prose output) vs a labeled pallet, shrink-
  wrapped and manifest attached (MCP structured output). Candidate for the
  deep-dive track or a Truck v2 extension.

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
