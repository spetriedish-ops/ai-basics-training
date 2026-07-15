# Codex build spec — staged (click-paced) animations for the AI Basics presentation

**Author:** Sarah Petrie
**For:** Codex (GPT-5.6 Sol), working in the `ai-basics-training` repo on Sarah's personal machine
**Repo path of interest:** `animations/pencil-codex/`
**Date:** 2026-07-15

---

## Orientation — where things live in the repo (read first, don't hunt)

- **Reference pattern to copy (the proven staged/click-paced renderer):**
  `animations/pencil-codex/render_harness_mind_map.py` — see its
  `build_stage_maps()`, `render_interactive_clips()`, `write_interactive_player()`.
- **Shared scene renderer + scene configs (`SCENES`, `PieceSpec`, `focus_order`):**
  `animations/pencil-codex/render_sketch_set.py` — Frontier Labs and MCP/CLI/API
  scenes are already defined here with grouped pieces.
- **Source sketches (photographed drawings):** `animations/pencil-codex/../assets/sketches/`
  (e.g. `02-frontier-labs-landscape-v2.jpeg`, `03-mcp-cli-api-tools-v2.jpeg`,
  `04-harness-mind-map-v2.jpeg`). The new brain-in-harness sketch (Task C) will
  be added here by Sarah.
- **Continuous outputs:** `animations/pencil-codex/out/<scene>.{mp4,gif}`
- **Interactive staged output (the target structure to reproduce):**
  `animations/pencil-codex/interactive/<scene>/` → `index.html` + `manifest.json`
  + `stages/NN-*.mp4` (harness_mind_map is the existing working example).
- **Pipeline overview + render commands:** `animations/pencil-codex/README.md`
- **Verify scripts:** `animations/pencil-codex/verify.py`, `verify_sketch_set.py`

## 0. How to read this spec (please read before touching code)

This is deliberately over-specified. It contains the *reasoning* behind every
decision, not just the instructions — because the whole point of these
animations is pedagogical, and if you only follow the literal asks without the
intent, you'll optimize the wrong thing. Where I say "the goal is X," treat X as
the real acceptance criterion; the specific technical instruction is just my
current best idea for achieving X. If you find a cleaner way to hit the goal,
take it, but **state what you changed and why** in your summary.

**Three explicit anti-patterns I want you to avoid (I've been burned by these):**

1. **Don't over-rotate on any single emphasized word.** This doc repeats
   "persist / don't fade" and "build on click" a lot because they're the core
   asks — but that does NOT mean bolt on extra animation flourish, add new
   visual effects, or re-typeset anything. The asks are *behavioral* (when does
   content appear, when does it stop), not *stylistic*. Keep the existing pencil
   / boiling-graphite art exactly as it is.
2. **Don't invent new content or re-letter Sarah's handwriting.** Every word on
   screen comes from Sarah's photographed sketches. You are changing *pacing and
   reveal grouping*, not content. If a stage boundary seems to need a label that
   doesn't exist in the source photo, stop and flag it — do not synthesize
   lettering or swap in a font.
3. **Don't "improve" the framing or reorder concepts on your own.** The concept
   order is intentional and was worked out separately. Your job is the two
   staged re-renders + one new animation described below, nothing adjacent.

**When in doubt, produce the smaller change and leave a note, rather than the
larger change silently.**

---

## 1. Context: what this is all for

This is a live "AI Basics" training for a team of enterprise Solutions
Engineers (non-developers, mixed AI literacy). The core framing of the whole
session is: **"What are you actually interacting with?"** — teaching people that
the different AI experiences they've used (embedded chat, ChatGPT, a CLI, an
IDE, Slack bots) are the *same kind of reasoning model* wrapped in different
**harnesses**, and that the harness is what determines what the AI can actually
do. The single most important concept in the whole session is the
**anatomy of an agent / harness mind map.**

### CRITICAL — the delivery format has changed (read this)

**We have pivoted AWAY from embedding these animations in Google Slides. The
HTML click-through artifact IS the presentation now.** There is no slide deck in
the live delivery. The presenter runs the HTML player full-screen, screen-shares
it, and clicks through it while narrating. Design everything for that reality.

Two hard consequences of this pivot, both non-negotiable:

1. **The presenter must never have to talk faster (or slower) to match an
   animation.** Pacing is presenter-controlled, not time-controlled. Every place
   a concept builds, it must build **on the presenter's click** and then WAIT.
   An animation that auto-advances through its own content on a timer is a
   failure, even if it looks nice — because it forces the presenter to race it.
   This is exactly why Tasks A and B must become click-gated stages rather than
   continuous timed builds. Staged builds are REQUIRED, not a nice-to-have.

2. **Nothing may fade out. This is a real, currently-broken behavior — fix it at
   the source render, not with a player workaround.** In the current animations,
   after a scene finishes drawing it **fades back to empty notebook paper**
   (the repo README literally describes this as step 9: "fades back to empty
   notebook paper for a clean loop"). That fade is the bug. During a live
   click-through, Sarah watched every scene draw itself and then dissolve while
   she was still talking about it. The final built-up state must **persist
   indefinitely** — held on screen, paper + pencil boil still alive, until the
   presenter advances. Do NOT rely on a downstream HTML player freezing a frame
   to hide the fade (that just freezes a half-faded frame). **Remove/disable the
   fade-to-empty at the end of each render so the final frame is the complete
   drawing, and have each stage hold on that complete frame.**

The presenter flips through animations, talking over each one. That
is why pacing control and persistence matter so much: **if a visual builds
faster than the presenter is talking, or fades away while she's still talking
about it, the teaching breaks.**

The animations are Sarah's hand-drawn pencil sketches, brought to life as
"boiling graphite" on notebook paper (the drawing looks continuously
re-drawn). This art style is loved and must be preserved exactly.

---

## 2. The proven reference pattern (start here)

**`animations/pencil-codex/render_harness_mind_map.py` already does exactly the
behavior we want, for one scene.** It renders the Harness mind map as
presenter-controlled **stages**: each stage draws one more part of the diagram,
then **holds indefinitely** (paper + pencil still boiling) until the presenter
clicks/Space/→ for the next stage. Left arrow goes back. `H` hides the overlay,
`R` restarts.

Key functions in that file, which are the template to generalize:

- `build_stage_maps(size)` — assigns pieces of the drawing to numbered stages
  using `add_part(stage_masks, stage_orders, occupied, STAGE_INDEX, mask, order,
  (phase_start, phase_end))`. Each `add_part` call adds one visual element
  (a box, a connector line, a block of text) to a given stage.
- `render_interactive_clips(...)` — renders one short mp4 per stage, where each
  clip draws that stage's new content and then holds on the final frame.
- `write_interactive_player(clips)` — writes `interactive/harness_mind_map/index.html`
  (the click-paced player) + a `manifest.json`. The player logic already handles
  "play this stage, freeze on last frame, wait for input, allow back/forward."

The output structure that works and that we want to mirror:

```
pencil-codex/interactive/harness_mind_map/
  index.html          # click-paced player
  manifest.json       # {stages:[...], controls:[...]}
  stages/
    01-harness.mp4
    02-model.mp4
    ...
    08-what-is-an-agent.mp4
```

**Your task is to produce the same kind of `interactive/<scene>/` output for two
more scenes (Frontier Labs and MCP/CLI/API), plus build one brand-new animation
(brain-in-harness). Details below.**

---

## 3. The scene config you'll build on

`animations/pencil-codex/render_sketch_set.py` defines `SCENES` with a
`SceneSpec` per scene. Each `SceneSpec` has a list of `PieceSpec`s, and each
`PieceSpec`'s last fields already tag it with a **group** and there's a
`focus_order` tuple naming the groups in teaching order. This is the raw
material for stage boundaries — the grouping already exists; you're turning
each group into a presenter-gated stage.

- `frontier_labs`: `focus_order=("labs", "models", "harnesses", "api")`
  Pieces are already tagged into those groups.
- `mcp_cli_api`: `focus_order=("mcp", "cli", "api")`
  Pieces tagged `mcp` / `cli` / `api`.

These `focus_order` groups are *exactly* the stage boundaries Sarah wants (see
§4 and §5). That is not a coincidence — build the stages off these groups.

---

## 4. TASK A — Frontier Labs: stage it into 3 presenter-gated builds

### The goal (why)
This visual teaches the vocabulary hierarchy: **Companies (Frontier / Tier-1 /
Tier-2-3 labs) → the Models they produce → the Harnesses those models run in
(including API access and open-source models).** Sarah narrates each level and
wants the diagram to **wait** at each level so she can talk before the next
level appears. Right now it's one continuous MP4 that builds straight through
and then fades — which means it races ahead of her narration and then disappears
while she's still talking. Both are fatal for teaching.

### Sarah's own words (verbatim from her review Loom — treat as source of truth)
> "The change I want to make on this animation is I'd like for it to build on
> clicks. So at the top it builds out as Frontier Labs, and then Tier 1 Labs,
> and Tier 2, 3 Labs. I'd like for it to stop after that, and let me talk, and
> then when I click, then it builds out the next tier, which is Models, and the
> names of the models. And then it should pause again, and not build out the
> harnesses until I click. And when you build out the harnesses, you can build
> out everything underneath too, including API and the asterisk that indicates
> open source models. And once again, we need this image, when it's done being
> built out, to persist instead of fading."

### Concrete asks
1. Produce `interactive/frontier_labs/` with the same structure as the harness
   player (`index.html`, `manifest.json`, `stages/*.mp4`), using the proven
   pattern from `render_harness_mind_map.py`.
2. **Stages (3), based on the existing `focus_order` groups:**
   - **Stage 1 — Labs:** the "Frontier Labs" heading + Tier-1 labs + Tier-2/3
     labs. (Groups: `labs`.) Then hold.
   - **Stage 2 — Models:** the model tier and the model names. (Group: `models`.)
     Then hold.
   - **Stage 3 — Harnesses:** the harness tier AND everything under it,
     including the **API** row and the **asterisk/open-weight note** that marks
     open-source models. (Groups: `harnesses` + `api` + the
     `open_weight_note` piece.) Then hold **indefinitely** — no fade.
3. **Persistence:** every stage holds its final frame indefinitely with the
   paper/pencil boil still going, exactly like the harness player. The final
   stage especially must never fade to blank.
4. Keep a continuous master MP4 (`out/frontier_labs.mp4`) for archival, BUT it
   too must end on the persistent complete drawing (no fade-to-empty). The fade
   is being removed everywhere — see §1. The interactive staged version is the
   one used in the live presentation.

### Watch-outs
- The asterisk/open-weight note is easy to drop because it's a small marginal
  piece — make sure it arrives with Stage 3, not silently omitted.
- Don't split "labs" into two stages (Tier-1 vs Tier-2/3) — Sarah wants all
  labs in Stage 1 together. Three stages total, not four+.

---

## 5. TASK B — MCP / CLI / API: stage it into 3 presenter-gated builds + it becomes a "cutaway"

### The goal (why)
This is a **deep-dive that Sarah cuts to from the middle of the harness mind
map** (right after the "Tools" stage of the harness). It compares three ways an
AI reaches external systems: **MCP, CLI, API.** She narrates each one fully
before the next appears. Same problem as Frontier Labs today: continuous build
+ fade.

### Sarah's own words (verbatim)
> "I want it to render on click, so I want MCP to render — the whole MCP section
> — and then nothing else, I don't want the CLI section to render until I click,
> and then when I'm done with the CLI section, then I want the API section to
> render when I click. And then after those are all done, I would like to make
> sure that the image doesn't fade."

### Concrete asks
1. Produce `interactive/mcp_cli_api/` with the same structure/pattern.
2. **Stages (3), based on `focus_order=("mcp","cli","api")`:**
   - **Stage 1 — MCP:** the MCP heading + MCP official + MCP unofficial pieces
     (all `mcp`-group pieces). Hold.
   - **Stage 2 — CLI:** CLI heading + CLI agent + CLI terminal (all `cli`
     group). Hold.
   - **Stage 3 — API:** API heading + API rack (all `api` group). Hold
     indefinitely, no fade.
3. Keep a continuous `out/mcp_cli_api.mp4` for archival, but it too must end on
   the persistent complete drawing (no fade). The interactive staged version is
   what's used live.

### Watch-out
- "the whole MCP section" = both the official and unofficial MCP pieces together
  in Stage 1. Don't split MCP across stages.

---

## 6. TASK C — NEW animation: "LLM = brain in a harness" (brain → harnessed body)

### The goal (why this needs to exist)
This is the **missing on-ramp to the entire harness thesis**, and it must play
**before** the Engine Factory animation. Right now the presentation jumps into
model lifecycle (Engine Factory) without first establishing the single most
important mental model: *the LLM by itself is just a brain — it can reason, but
it can't do anything or even be interacted with until it's put in a harness.*
The harness is what gives it senses and hands. Everything else in the session
(interaction layer, tools, guardrails, context) is "what the harness adds."

### Sarah's own words (verbatim)
> "I describe the LLM as the brain... it doesn't actually work like a brain, but
> it is similar insofar as by itself it's just where the reasoning happens — it
> can think, but it can't do anything else, and you can't even really interact
> with it without there being an interaction layer. So an LLM needs a harness to
> be interacted with. I need a new visual... where the LLM is the brain, and
> then I need to visualize the brain being harnessed, so I'll probably draw a
> body around the brain, and draw arms and legs... because that represents the
> LLM/model being in a harness, and therefore being able to interact and perform
> actions. When I come up with that sketch, I will give it to Codex, Codex will
> build the animated version of it, I'll bring that back into Rovo CLI, and it
> needs to be added before the Engine Factory cartoon."

### Important dependency / sequencing
- **Sarah will provide a NEW hand-drawn sketch** for this (brain, then a body/
  arms/legs drawn around it = the harness). **Do not fabricate the drawing.**
  The animation must be built from her photographed sketch in the same
  boiling-graphite pipeline as the others (EXIF-rotate, perspective-correct,
  isolate graphite, per-pixel writing order, boil, hold — same as
  `render_sketch_set.py` does for the other sketches).
- If the sketch is not yet in the repo when you pick this up, **stop on Task C
  and do Tasks A and B first**, and leave a clear note that Task C is blocked on
  the incoming sketch file. Do not build a placeholder brain from scratch.

### Concrete asks (once the sketch exists)
1. Add it to the pipeline like the other sketches (a new `SceneSpec` in
   `render_sketch_set.py`, source photo in `assets/sketches/`).
2. Suggested 2-stage build (confirm with the sketch when it arrives):
   - **Stage 1 — the brain alone** (reasoning happens here, but it's inert).
     Hold.
   - **Stage 2 — the harness drawn around it** (body/arms/legs/senses) so it can
     now interact + act. Hold indefinitely.
   A staged version fits the teaching beat ("here's the brain… now here's what
   the harness adds"), and matches the click-paced pattern of everything else.
3. Output both a continuous `out/brain_in_harness.mp4` (take-home) and an
   `interactive/brain_in_harness/` staged player.

### Watch-out
- The teaching nuance Sarah is careful about: **it's a brain-like analogy, not a
  literal claim that an LLM is a brain.** Keep any added marginal doodles
  wordless and restrained (same rule as the other scenes) — do NOT add text that
  asserts "the LLM is a brain." The analogy lives in Sarah's narration, not in
  new lettering.

---

## 7. Global acceptance criteria (all tasks)

- [ ] Existing pencil/boiling-graphite art style preserved exactly; no new
      effects, no re-lettering, no font substitutions.
- [ ] Each new interactive scene mirrors the harness player's UX: click / Space
      / → advances; ← goes back; `H` hides overlay; `R` restarts; every completed
      stage **holds indefinitely** with paper + pencil boil still moving; nothing
      fades to blank.
- [ ] Stage boundaries match §4/§5/§6 exactly (Frontier: labs → models →
      harnesses+API+open-weight; MCP/CLI/API: mcp → cli → api; brain: brain →
      harnessed).
- [ ] **The fade-to-empty at the end of EVERY scene is removed at the render
      level** — not just the three tasks here, but all existing scenes too
      (agentic loop, what-is-an-agent, multi-agent orchestration, etc. all
      currently fade and must instead hold their complete final drawing). This
      is the delivery format now; there is no Google Slides fallback.
- [ ] Continuous master MP4s may be kept for archival, but they too must end on
      the persistent complete drawing; the interactive staged versions are what
      run in the live presentation.
- [ ] `verify.py` / `verify_sketch_set.py` pass (or, if they need updating for
      the new scenes, update them and say what you changed).
- [ ] Output structure matches the harness pattern:
      `interactive/<scene>/index.html` + `manifest.json` + `stages/NN-*.mp4`.

## 8. What to hand back
A short summary (NOT a wall of text) listing:
1. What you built + the exact output paths.
2. Any deviations from this spec and the reason for each.
3. Anything you flagged/skipped (esp. Task C if the brain sketch wasn't present).
4. How to preview each (which dir to serve, which URL).

Keep new code consistent with the existing renderers' conventions (crop boxes,
timing, and motion settings live near the top of the renderer files, per the
repo README).
