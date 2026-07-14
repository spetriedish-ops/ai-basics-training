# Handoff to Claude Code — finished pencil animations

**From:** Sarah + Codex
**To:** Claude Code
**Date:** 2026-07-14
**Purpose:** Assemble the full presentation run of show using the finished,
Sarah-approved pencil animation set.

## Read this first

`CODEX-HANDOFF.md` is the historical brief that started the pencil-animation
bake-off. It is useful background, but its scope and status table are stale.
This document describes the finished work. `RUN-OF-SHOW.md` now contains the
current visual mapping.

The completed personality pass was developed on `codex/personality-pass`. If
it has not yet been merged, fetch and switch to that branch before assembling
the deck; confirm the local state with `git status`. Commit `a038091` is the
preserved fallback: it contains the approved pencil set immediately before the
later personality and timing pass.

## Slide-ready deliverables

Use the MP4s for presentation slides. They are silent, H.264, 1920x1080,
30 fps, no longer than 25 seconds, and loop back through empty notebook paper.
The GIFs are smaller wiki previews, not the preferred slide assets.

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

## Harness presenter player

The Harness animation has a second, presenter-controlled delivery mode:

`pencil-codex/interactive/harness_mind_map/index.html`

Serve `pencil-codex/` over localhost and open that page. Controls:

- click, Space, Enter, or Right Arrow: draw the next stage;
- Left Arrow: return to the previous completed stage;
- `H`: hide/show the presenter HUD;
- `R`: restart at Harness.

Each completed stage holds indefinitely while the paper and pencil continue
their gentle boil. The Sarah-approved stage order is:

1. Harness
2. Model
3. Interaction / Application Layer
4. Guardrails, including the connected diagonal notes
5. Tools
6. Context
7. Skills, followed by the dotted Context-to-Skills line drawing left to right
8. “If this is a harness, what is an agent?”

Google Slides cannot directly host this local interactive HTML artifact. For
the deck, choose one of these approaches:

1. Import the 24.8-second master MP4 for automatic playback.
2. Put the eight files in `interactive/harness_mind_map/stages/` on eight
   consecutive slides so slide advancement becomes the presenter click.
3. Keep the browser player open separately and switch to it during the talk.

Option 2 is the closest Google Slides equivalent to the interactive player.

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

Sarah explicitly approved the finished set and described it as ready to wrap.
The older animation set remains recoverable at `a038091` if a run-of-show edit
ever exposes an unforeseen problem.

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

For a single shared-renderer page:

```bash
../.venv/bin/python render_sketch_set.py --scene mcp_cli_api
```

See `pencil-codex/README.md` for environment setup and revision details.
When changing timing or visuals, regenerate the corresponding MP4/GIF and
audit images, then rerun both verifiers before committing.

## Run-of-show integration guidance

`RUN-OF-SHOW.md` is the current content spine. Claude has additional deck and
talk-track context and may adjust slide ordering or playback settings, but
should preserve each animation's internal teaching order and the creative
decisions above. Prefer one animation per slide, autoplay muted, with looping
enabled where the slide software supports it. The full set was designed for
Sarah to narrate live; no audio track or additional explanatory captions are
needed.
