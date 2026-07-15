# Run of show — AI Basics, July 15 2026

For paths, controls, approved visual decisions, and all interactive pencil
sequences, see [`CLAUDE-HANDOFF.md`](CLAUDE-HANDOFF.md).

Sarah's flow (updated 2026-07-14). Sarah kicks the session off with the
Garage, Marta covers the history of AI, then Sarah takes over for
everything agentic. The harness mind map is the SPINE of the middle:
Sarah walks its spokes in the player's stage order, detouring to other
imagery and returning. Session is fully remote (attendees on their own
screens).

## Session kickoff — Sarah

- 🎬 **The Garage** (`interactive/garage/index.html`, 5 click-paced stages;
  archival `renders/final/garage.mp4`) opens the whole
  session — the history arc in Jobsite form; the NEXT YEAR'S TRUCK gag
  plants the model-release-hullabaloo line Sarah pays off in beat 1.

## Marta — history of AI

Basic AI → autocomplete → agentic systems.

## Sarah

| # | Beat | Visuals | Status |
|---|------|---------|--------|
| 1 | LLM = the brain; needs a harness to interact; what an LLM is; pre-training → post-training lifecycle; "models" + release hullabaloo | ✏️ sketch 01a (brain) + 🎬 Engine Factory `interactive/engine_factory/` (5 stages) | Static sketch / ✅ |
| 2 | How the model works: prediction, tokens, hallucination | 🎬 The Paver `interactive/paver/` (7 stages) | ✅ |
| 3 | The agentic loop | ✏️ `pencil-codex/out/agentic_loop.mp4` | ✅ approved |
| 4 | Frontier labs: companies vs models vs harnesses; API wrap-up; multimodal vs multi-model | ✏️ `pencil-codex/interactive/frontier_labs/index.html` (Labs → Models → Harnesses + API) | 🧪 staged player built; ready for Sarah review |
| 5 | Harness mind map — staged walk begins | ✏️ `pencil-codex/interactive/harness_mind_map/index.html` | ✅ approved |
| 6 | Tools spoke (player stage 5) → detour off the map | 🎬 The Toolbox `interactive/toolbox/` (6 stages), then ✏️ `pencil-codex/interactive/mcp_cli_api/index.html` (MCP → CLI → API) | 🧪 staged player built; ready for Sarah review |
| 7 | Context spoke (player stage 6) | 🎬 The Truck v2 `interactive/context_window/` (8 stages; + optional simulator demo) | ✅ |
| 8 | Return to map → skills spoke (page closes on "if this is a harness, what is an agent?") | ✏️ Harness stages 07–08 | ✅ approved |
| 9 | Assembly payoff: the whole walk clicks together; ends on van tease | 🎬 Pop the Hood `interactive/agent_anatomy/` (8 stages) | ✅ |
| 10 | What is an Agent: definition, ambiguity beat, general vs specialized | ✏️ `pencil-codex/out/what_is_an_agent.mp4` | ✅ approved |
| 11 | Multi-agent orchestration finale | 🎬 The Fleet `interactive/fleet/` (8 stages) + ✏️ `pencil-codex/out/multi_agent_orchestration.mp4` | ✅ approved |

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

## Jobsite interactive players (2026-07-15)

All seven vector scenes are click-paced players now, mirroring the pencil
player contract (same controls, same hold-with-boil behavior). Stage cuts
fall at caption beats; the old roll-off-to-empty endings are cut, so every
scene holds on its complete final tableau. Regenerate with
`scripts/stage_split.py`; cut times derive from `scripts/beat_times.py`.
Hardening: if autoplay is blocked, the first click plays the current stage
instead of skipping it.
