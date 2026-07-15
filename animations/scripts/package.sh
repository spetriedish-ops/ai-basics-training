#!/usr/bin/env bash
# Assemble the presentation-ready deliverables folder in run-of-show order.
# Usage (from animations/):  ./scripts/package.sh
# Output: animations/deliverables/  (gitignored — regenerate anywhere)
set -euo pipefail
cd "$(dirname "$0")/.."

OUT="deliverables"
rm -rf "$OUT"
mkdir -p "$OUT/05-harness-stages" "$OUT/extras"

cp renders/final/garage.mp4                       "$OUT/00-garage-session-kickoff.mp4"
cp renders/final/engine_factory.mp4               "$OUT/01-engine-factory.mp4"
cp assets/sketches/01-llm-harness-agentic-loop.jpeg "$OUT/01b-brain-sketch-static.jpeg"
cp renders/final/paver.mp4                        "$OUT/02-paver.mp4"
cp pencil-codex/out/agentic_loop.mp4              "$OUT/03-agentic-loop.mp4"
cp pencil-codex/out/frontier_labs.mp4             "$OUT/04-frontier-labs.mp4"
cp -R pencil-codex/interactive/frontier_labs      "$OUT/04-frontier-labs-player"
cp pencil-codex/out/harness_mind_map.mp4          "$OUT/05-harness-mind-map-full.mp4"
cp pencil-codex/interactive/harness_mind_map/stages/*.mp4 "$OUT/05-harness-stages/"
cp -R pencil-codex/interactive/harness_mind_map   "$OUT/05-harness-player"
cp renders/final/toolbox.mp4                      "$OUT/06-toolbox.mp4"
cp pencil-codex/out/mcp_cli_api.mp4               "$OUT/07-mcp-cli-api.mp4"
cp -R pencil-codex/interactive/mcp_cli_api        "$OUT/07-mcp-cli-api-player"
cp renders/final/context_window.mp4               "$OUT/08-context-truck.mp4"
cp renders/final/agent_anatomy.mp4                "$OUT/09-pop-the-hood.mp4"
cp pencil-codex/out/what_is_an_agent.mp4          "$OUT/10-what-is-an-agent.mp4"
cp renders/final/fleet.mp4                        "$OUT/11-fleet.mp4"
cp pencil-codex/out/multi_agent_orchestration.mp4 "$OUT/12-multi-agent-orchestration.mp4"
cp renders/final/lost_card_wireframe.png          "$OUT/13-lost-card-wireframe.png"
cp renders/final/sdlc_wireframe.png               "$OUT/14-sdlc-wireframe.png"

# wiki-sized GIFs and alternates, kept out of the main sequence
cp renders/final/*_small.gif "$OUT/extras/" 2>/dev/null || true
cp pencil-codex/out/*.gif "$OUT/extras/"
cp pencil-claude/out/agentic_loop.mp4 "$OUT/extras/alt-agentic-loop-claude.mp4"

cat > "$OUT/INDEX.md" <<'EOF'
# AI Basics — deliverables (run-of-show order)

Session: July 15, 2026 · fully remote · all MP4s silent, 1080p30.
Regenerate this folder anytime: `./scripts/package.sh` from animations/.
The HTML players are the primary live artifacts. Serve `deliverables/` over
localhost (for example, `python3 -m http.server`) and open each player's
`index.html`. Continuous MP4s are archival/take-home fallbacks.

| File | Slot | Notes |
|------|------|-------|
| 00-garage-session-kickoff.mp4 | Sarah opens the session | NEXT YEAR'S TRUCK gag plants the hullabaloo line |
| — | Marta: history of AI | no repo asset |
| 01-engine-factory.mp4 + 01b-brain-sketch-static.jpeg | Beat 1: LLM, lifecycle, inference | odometer beat = inference |
| 02-paver.mp4 | Beat 2: prediction engine | |
| 03-agentic-loop.mp4 | Beat 3 | pencil (Codex set) |
| 04-frontier-labs-player/ | Beat 4 | primary; click-paced Labs → Models → Harnesses + API |
| 04-frontier-labs.mp4 | Beat 4 | continuous fallback; complete drawing persists |
| 05-harness-player/ | Beat 5 + 8 | primary eight-stage click-paced player |
| 05-harness-mind-map-full.mp4 / 05-harness-stages/ | Beat 5 + 8 | continuous and per-stage fallbacks |
| 06-toolbox.mp4 → 07-mcp-cli-api-player/ | Beat 6: tools spoke detour | primary MCP → CLI → API player; tools BEFORE context |
| 07-mcp-cli-api.mp4 | Beat 6 | continuous fallback; complete drawing persists |
| 08-context-truck.mp4 | Beat 7: context spoke | simulator demo optional (animations/simulator.html, serve repo) |
| 09-pop-the-hood.mp4 | Beat 9: assembly payoff | ends on van tease |
| 10-what-is-an-agent.mp4 | Beat 10 | pencil |
| 11-fleet.mp4 → 12-multi-agent-orchestration.mp4 | Beat 11: finale | Fleet = delegation; pencil page closes it |
| 13/14 wireframes (PNG) | optional orchestration slides | lost card = hub, SDLC = relay |
| extras/ | wiki GIFs + alternates | includes Claude's alternate agentic loop |
EOF

echo "Packaged $(ls "$OUT" | wc -l | tr -d ' ') entries into animations/$OUT/"
