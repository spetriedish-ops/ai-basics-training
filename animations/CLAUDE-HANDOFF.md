# Handoff to Claude Code — finished pencil animations

**From:** Sarah + Codex
**To:** Claude Code
**Date:** 2026-07-15
**Purpose:** Assemble the full presentation run of show using the finished,
Sarah-approved pencil animation set.

## Read this first

`CODEX-HANDOFF.md` is the historical brief that started the pencil-animation
bake-off. It is useful background, but its scope and status table are stale.
This document describes the finished work. `RUN-OF-SHOW.md` now contains the
current visual mapping.

The completed personality pass is merged into `main`. Commit `a038091` is the
preserved fallback: it contains the approved pencil set immediately before the
later personality and timing pass.

## Primary live-delivery artifacts

The delivery format has changed: the full-screen HTML click-through is the
presentation, not a Google Slides deck. Use these presenter players for the
three teaching visuals that need narration-controlled pacing:

| Presentation concept | Presenter player | Stages |
|---|---|---:|
| Frontier labs, models, harnesses, APIs | `pencil-codex/interactive/frontier_labs/index.html` | 3 |
| Harness mind map | `pencil-codex/interactive/harness_mind_map/index.html` | 8 |
| MCP vs CLI vs API | `pencil-codex/interactive/mcp_cli_api/index.html` | 3 |

Serve `pencil-codex/` over localhost and open the relevant `index.html`.
Controls are consistent across all three players:

- click, Space, Enter, or Right Arrow: draw the next stage;
- Left Arrow: return to the previous completed stage;
- `H`: hide/show the presenter HUD;
- `R`: restart at stage one.

Each completed stage waits indefinitely while the paper and pencil retain
their subtle boil. Frontier stages are Labs → Models → Harnesses + API; the
last stage includes the open-weight note. MCP stages are MCP → CLI → API; the
entire official/unofficial MCP section appears together in stage one.

## Jobsite scene players (added 2026-07-15)

The seven vector Jobsite scenes follow the same presenter-player contract
(identical controls and hold behavior; one extra hardening: if autoplay is
blocked, the first click plays the current stage instead of advancing).
Serve `animations/` over localhost:

| Presentation concept | Presenter player | Stages |
|---|---|---:|
| The Garage (session kickoff) | `interactive/garage/index.html` | 5 |
| Engine Factory (model lifecycle + inference) | `interactive/engine_factory/index.html` | 5 |
| The Paver (prediction engine) | `interactive/paver/index.html` | 7 |
| The Truck (context window) | `interactive/context_window/index.html` | 8 |
| The Toolbox (MCP) | `interactive/toolbox/index.html` | 6 |
| Pop the Hood (anatomy) | `interactive/agent_anatomy/index.html` | 8 |
| The Fleet (orchestration) | `interactive/fleet/index.html` | 8 |

Stage clips are cut from the verified boiled finals at caption beats
(`scripts/stage_split.py`, timelines from `scripts/beat_times.py`); each
stage holds by looping its last 0.52 s boil cycle. The scenes' old
roll-off-to-empty endings are deliberately cut — every player ends holding
the complete tableau. The `renders/final/*.mp4` masters are unchanged
(archival; they still include the exit beats).

## Continuous take-home masters

The silent H.264, 1920x1080, 30 fps MP4s remain useful as archival/take-home
versions. All now end on the complete drawing and keep boiling; none fades back
to empty notebook paper. The GIFs are smaller wiki previews.

| Presentation concept | Slide master | Duration |
|---|---|---:|
| Agentic loop | `pencil-codex/out/agentic_loop.mp4` | 23.5 s |
| Frontier labs, models, harnesses, APIs | `pencil-codex/out/frontier_labs.mp4` | 22.5 s |
| Harness mind map, automatically paced | `pencil-codex/out/harness_mind_map.mp4` | 24.8 s |
| MCP vs CLI vs API | `pencil-codex/out/mcp_cli_api.mp4` | 24.0 s |
| What is an agent? | `pencil-codex/out/what_is_an_agent.mp4` | 21.5 s |
| Multi-agent orchestration | `pencil-codex/out/multi_agent_orchestration.mp4` | 23.0 s |

All corresponding `.gif` files are in `pencil-codex/out/`. All passed the
repository's visual/format checks and are below the 10 MB wiki ceiling.

## Harness presenter sequence

The Harness animation has a second, presenter-controlled delivery mode:

`pencil-codex/interactive/harness_mind_map/index.html`

The Sarah-approved stage order is:

1. Harness
2. Model
3. Interaction / Application Layer
4. Guardrails, including the connected diagonal notes
5. Tools
6. Context
7. Skills, followed by the dotted Context-to-Skills line drawing left to right
8. “If this is a harness, what is an agent?”

The continuous Harness MP4 is an archival fallback. The interactive player is
the authoritative live version.

## Approved creative decisions to preserve

- Sarah's photographed handwriting, wording, arrows, and primary drawings are
  the foundation. Do not replace or re-typeset them.
- The crumpled ruled-notebook background, subtle paper boil, live-writing
  reveals, and restrained teal focus treatment are intentional.
- The recurring little agent is deliberately large enough to read in a room
  and appears early enough for each joke to land. Avoid shortening these beats.
- Agentic Loop: the character catches input, thinks, carries tools, inspects
  the result, and runs the loop. Previously reported broken circle/arrow
  intersections were corrected.
- Frontier Labs: use the cleaner V2 source and its Lab → Model → Harness → API
  package-line gag.
- MCP/CLI/API: the final source is
  `assets/sketches/03-mcp-cli-api-tools-v2.jpeg`. It supersedes the crowded
  prose sketch. MCP is the toolbox; CLI is the terminal producing a Swiss Army
  knife (with a brief wrong-corkscrew gag); API is the standardized port.
- Harness: keep the exact stage order above. The guardrail-note arrow, Tools
  spacing, clean Context/Skills dotted line, and section boundaries were all
  refined after visual review.
- What Is an Agent: the left-column section boundaries were repaired; the
  character assembles the concept and contrasts generalist vs specialist.
- Multi-agent Orchestration: walking subagents and the orange/yellow
  incinerator fire are intentional. The main agent owns the goal and combines
  outputs; subagents are short-lived workers.

Sarah explicitly approved the underlying finished visual set and described it
as ready to wrap. The new Frontier and MCP click-pacing versions preserve that
art and are built and verified, but still await Sarah's live review.
Still owed: the brain-in-harness animation (spec Task C) — blocked on
Sarah's incoming sketch; it slots before the Engine Factory. The older
animation set remains recoverable at `a038091` if a run-of-show edit ever
exposes an unforeseen problem.

## Source and regeneration

The reproducible implementation is in `pencil-codex/`:

- `render_agentic_loop.py` — Agentic Loop
- `render_sketch_set.py` — Frontier Labs, MCP/CLI/API, What Is an Agent
- `render_harness_mind_map.py` — Harness master and interactive stage clips
- `render_multi_agent_orchestration.py` — Multi-agent Orchestration
- `personality_motifs.py` — shared characters, props, and visual gags
- `source/` — cleanup, crop, layout, stage, and personality audit images

From `animations/pencil-codex/`:

```bash
./render.sh
../.venv/bin/python verify.py
../.venv/bin/python verify_sketch_set.py
```

For a single shared-renderer page (this also regenerates its interactive player
when the scene is Frontier or MCP):

```bash
../.venv/bin/python render_sketch_set.py --scene mcp_cli_api
```

See `pencil-codex/README.md` for environment setup and revision details.
When changing timing or visuals, regenerate the corresponding MP4/GIF and
audit images, then rerun both verifiers before committing.

## Run-of-show integration guidance

`RUN-OF-SHOW.md` is the current content spine. Claude has additional
presentation and talk-track context and may adjust ordering, but should
preserve each animation's internal teaching order and the creative decisions
above. The set was designed for Sarah to narrate live; no audio track or
additional explanatory captions are needed.
