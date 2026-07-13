# Handoff → Codex: "pencil boil" animations for the AI Basics training

**From:** Sarah Petrie (Principal Solutions Engineer, Atlassian)
**To:** Codex (OpenAI agent)
**Date:** 2026-07-13
**Heads up:** This is a bake-off. Another agent (Claude, in this repo) is
attempting the same brief in parallel. Work independently. Do not modify
anything outside your delivery folder (see Working agreement).

---

## 1. Mission

Turn Sarah's hand-drawn pencil sketches into short, **silent, loop-friendly
animated explainers** for a live "AI Basics" training session on
**July 15, 2026** (two days out — bias toward shippable). The animations
play inside presentation slides while Sarah talks over them, and later get
embedded in a wiki page.

The look is **"boiling lines"**: the drawing appears to be continuously
redrawn, lines jittering gently like classic hand-drawn animation. The
existing animation set in this repo uses this style — watch any file in
`animations/renders/final/` for the target vibe (those are vector-built;
yours will be built from the pencil sketches).

## 2. Source material

Photos of the sketches are committed in `animations/assets/sketches/`:

| File | Content | Status |
|---|---|---|
| `01-llm-harness-agentic-loop.jpeg` | LLM "brain" needs a harness + the agentic loop diagram | **PRIMARY assignment** |
| `04-harness-mind-map.jpeg` | Harness mind map (context, tools, guardrails, surfaces) | stretch goal |
| `02-frontier-labs-landscape.jpeg` | Vendor landscape | OUT OF SCOPE (slide, being fact-checked separately) |
| `03-mcp-cli-api-tradeoffs.jpeg` | MCP/CLI/API prose | OUT OF SCOPE (handout, not an animation) |

Photos are unprocessed: perspective skew, glare, shadows. Cleanup
(deskew, contrast, background removal, rotation) is expected and welcome.

## 3. The primary assignment

From sketch 01, animate the **agentic loop** (the flowchart half of the
page): a build-out where nodes appear one at a time in teaching order —

1. RECEIVE INPUT
2. REASON / GENERATE
3. USE TOOLS / TAKE AN ACTION
4. OBSERVE THE RESULT
5. REPEAT UNTIL TASK IS DONE (the cycle arrow, then let the loop visibly
   run a lap or two)

Pace it for a presenter talking over each beat (a beat should survive
being paused on). If it strengthens the piece, a second pass may animate
the worked example written below the diagram (search → inspect results →
decide what is missing → search again → produce final answer).

The "brain + harness" half of the page may be a separate short animation
if you have time; it is not required.

## 4. Hard constraints (fail any of these = fail the brief)

1. **Sarah's linework is the foundation.** The output must read as HER
   drawing brought to life. Cleaning and masking her lines is encouraged;
   replacing them with regenerated/redrawn art (image-gen restyling) is
   out of scope for this assignment.
2. **Silent-first.** No audio. It plays in a room with a live speaker.
3. **Loop-friendly.** Clean loop or graceful hold on the final frame.
4. **Legible from the back of a room.** Pencil is faint; boost contrast.
   Any text you ADD: handwriting-style font, lowercase, ≤ 8 words per
   caption. Bundled OFL fonts live in `animations/assets/fonts/`.
5. **Vendor-neutral.** No product names, logos, or brand references in
   any added element.
6. **Banned construction** in any added text: "it's not X, it's Y" and
   all variants ("not X, but Y" / "less X, more Y"). State points directly.
7. **Pedagogical honesty.** Do not add imagery implying the model has
   ears/eyes/feelings, or that anything persists across sessions.
8. **Reproducible.** Commit the SOURCE of the animation (code, config,
   masks, intermediate assets) alongside outputs. Sarah will request
   revisions; a one-shot video with no regeneration path fails.
9. **Accessibility.** Jitter must be lively, never strobing — hold each
   jitter state ~5 frames at 30fps (≈6 Hz), low amplitude. No
   seizure-risk flicker. Meaning never carried by color alone.

## 5. Deliverables

Into `animations/pencil-codex/` (your folder, on a branch named
`codex/pencil`):

- `out/agentic_loop.mp4` — 1920×1080, 30fps, H.264, ≤ ~25s
- `out/agentic_loop.gif` — ≤ 960px wide looping GIF (wiki embed);
  keep it under ~10 MB if you can
- All source needed to re-render, plus a `README.md` covering: your
  approach and why, exact re-render commands from a fresh checkout, and
  the expected time from "Sarah asks for a caption change" to a new file
- Stretch: same set for the harness mind map — USE THE V2 SKETCH
  (`04-harness-mind-map-v2.jpeg`). Build spokes in Sarah's narration
  order: guardrails → interaction layer → context → tools → skills, and
  end holding on the full map. Bonus if the render pauses cleanly after
  the tools spoke (her talk detours to other imagery there and returns
  for skills).

## 6. How Sarah will judge the bake-off

1. **Fidelity** — is it recognizably her drawing, alive?
2. **Room legibility** — contrast and size from the back row
3. **Boil quality** — lively, not strobing; loop cleanliness
4. **Storytelling** — elements arrive in teaching order, presenter-paced
5. **Revision ergonomics** — turnaround for a small change request
6. **Repo hygiene** — reproduces from a fresh checkout with documented steps

## 7. Background reading (in this repo)

- `animations/README.md` — the project and rendering conventions
- `animations/STORYBOARDS.md` — the five-scene animated set and world
- `animations/CONTRIBUTING.md` — working agreement + content guardrails
- Root `README.md` — the original creative brief; §5 is the voice guide

Questions, judgment calls, and anything ambiguous: make a sensible call,
write it down in your README, and keep moving — the session is on the 15th.
