# Run of show — AI Basics, July 16 2026

For paths, controls, approved visual decisions, and all interactive pencil
sequences, see [`CLAUDE-HANDOFF.md`](CLAUDE-HANDOFF.md).

Sarah's flow (updated 2026-07-14). Sarah kicks the session off with the
Garage, Marta covers the history of AI, then Sarah takes over for
everything agentic. The harness mind map is the SPINE of the middle:
Sarah walks its spokes in the player's stage order, detouring to other
imagery and returning. Session is fully remote (attendees on their own
screens).

## Session kickoff — Sarah

- 🎬 **The Garage** (`deliverables/00-garage-session-kickoff.mp4`, plays straight through) opens the whole
  session — the history arc in Jobsite form; the NEXT YEAR'S TRUCK gag
  plants the model-release-hullabaloo line Sarah pays off in beat 1.

## Marta — history of AI

Basic AI → autocomplete → agentic systems.

## Sarah

| # | Beat | Visuals | Status |
|---|------|---------|--------|
| 1 | LLM = the brain; needs a harness to interact; what an LLM is; pre-training → post-training lifecycle; "models" + release hullabaloo | ✏️ `pencil-codex/interactive/brain_in_harness/index.html` (Brain → Harness), then 🎬 Engine Factory `deliverables/01-engine-factory.mp4` | 🧪 brain player built; ready for Sarah review / ✅ |
| 2 | How the model works: prediction, tokens, hallucination | 🎬 The Paver `deliverables/02-paver.mp4` | ✅ |
| 3 | The agentic loop | ✏️ `pencil-codex/out/agentic_loop.mp4` | ✅ approved |
| 4 | Frontier labs: companies vs models vs harnesses; API wrap-up; multimodal vs multi-model | ✏️ `pencil-codex/interactive/frontier_labs/index.html` (Labs → Models → Harnesses + API) | 🧪 staged player built; ready for Sarah review |
| 5 | Harness mind map — staged walk begins | ✏️ `pencil-codex/interactive/harness_mind_map/index.html` | ✅ approved |
| 6 | Tools spoke (player stage 5) → detour off the map | 🎬 The Toolbox `deliverables/06-toolbox.mp4`, then ✏️ `pencil-codex/interactive/mcp_cli_api/index.html` (MCP → CLI → API) | 🧪 staged player built; ready for Sarah review |
| 7 | Context spoke (player stage 6) | 🎬 The Truck v2 `deliverables/08-context-truck.mp4` (+ optional simulator demo) | ✅ |
| 8 | Return to map → skills spoke (page closes on "if this is a harness, what is an agent?") | ✏️ Harness stages 07–08 | ✅ approved |
| 9 | Assembly payoff: the whole walk clicks together; ends on van tease | 🎬 Pop the Hood `deliverables/09-pop-the-hood.mp4` | ✅ |
| 10 | What is an Agent: definition, ambiguity beat, general vs specialized | ✏️ `pencil-codex/out/what_is_an_agent.mp4` | ✅ approved |
| 11 | Multi-agent orchestration finale | 🎬 The Fleet `deliverables/11-fleet.mp4` + ✏️ `pencil-codex/out/multi_agent_orchestration.mp4` | ✅ approved |

## Open items

1. ~~Pre/post-training lifecycle~~ — resolved: The Engine Factory
   (`engine_factory.py`) covers it in beat 1.
2. ~~Mind-map animation build order~~ — resolved: the player's eight-stage
   sequence is authoritative (tools before context, per Sarah); beats 6–7
   above follow it.
3. ~~Garage placement~~ — resolved: Sarah opens the session with it.
4. Van tease → Fleet gap is now one page; talk track holds it easily.
5. Kahoot breaks: natural slots after beat 4 and at close.
6. Automated player/codec/persistence checks pass. **Full-screen test on the
   presentation machine** — Sarah owns.
7. ~~Projector legibility check~~ — waived: session is fully remote.

## Jobsite interactive players — SHELVED for the session (2026-07-15)

Sarah's call on session day: the Jobsite scenes present as CONTINUOUS
videos (`deliverables/` masters, above) — the click-paced players showed
frame-jumping on the presentation machine across two player architectures
and were shelved rather than debugged on session day. The players and
`scripts/stage_split.py` remain in `interactive/` for post-session
forensics; do not wire them into a live session without a click-through
on the actual presentation machine.
