# Handoff → Rovo CLI: assembling the AI Basics preamble video

**From:** Sarah Petrie (via Claude Code session, 2026-08-10)
**Purpose:** Assemble Sarah's recorded preamble narration with the animated
clips into one video. Everything you need is in this repo; this file is the
assembly manual.

## The clips

Final, verified MP4s (1920×1080, 30 fps, H.264, silent) live in
`animations/deliverables/preamble/`. If that folder is missing (it is
gitignored), regenerate everything with:

```bash
cd animations && source .venv/bin/activate
./scripts/preamble_batch.sh     # boils, verifies, packages all 15 clips
```

Committed masters also exist at `animations/renders/final/preamble*.mp4`
(same content, verification source of truth).

## Assembly rules

1. **Order is the P-number order** (P01 → P11; letter suffixes play in
   sequence: a, then b, then c).
2. **Every clip ends on a ~7 s static hold** with the "boiling lines"
   still alive. To stretch a clip against a longer narration passage,
   loop its final 0.5 s (one full boil cycle — it tiles seamlessly), or
   simply hold the last frame if loop tooling is unavailable.
3. **Trilogies (P07a/b/c, P08a/b/c) are separate files on purpose** —
   each sub-clip advances when its narration line arrives. P07c opens on
   P07b's exact final tableau, and P08b/c each open on the prior clip's
   tableau, so butt-joins are seamless (no crossfades needed — cut
   straight).
4. **No crossfades between clips.** Straight cuts on paper-colored
   frames read as page turns in this style. If a transition feels hard,
   cut during the narration pause, not mid-sentence.
5. The narration audio is the master track: place clips to the script
   alignment below, stretching holds to fit. Never speed up or slow
   down the clips themselves — pacing was tuned deliberately.

## Talk-track alignment

| Clip | Starts at (script cue) | Carries through |
|------|------------------------|-----------------|
| P01-the-algorithm-van | "Think of how long you've had recommendations…" | "…predicting what you will click on, purchase or engage with next." |
| P02-fraud-flag | "Have you ever gotten a message from your credit card company…" | "…don't align with your usual spending trends." |
| P03-decades-road | "Whether we notice it or not, we've been interacting with AI for decades." | End of paragraph. (Five dated signs pace with this line — let it breathe.) |
| P04-factory-export-gate | "So if AI has been around for so long, what has changed now?" | "…without causing this much upheaval." (Gate stamp lands on the export-control mention.) |
| P05-next-years-truck | "The answer is like something out of a science fiction movie…" | "…as well as or better than the average human." (The sketch fills in solid as "how close we are" is spoken.) |
| P06-movie-vs-job | "Let's think about that compared to how we're used to interacting with AI." | "…AI will be able to do some jobs better than humans." (Movie handoff first; the YOUR JOB reach lands on the final sentence.) |
| P07a-tedium-hauled-away | "There are a bunch of reasons why that's awesome…" | "…offloaded to AI." |
| P07b-the-garden | "That theoretically leaves humans with a chance to focus…" | "…spending time with your family." |
| P07c-breakthroughs | "On top of that, the AI-enhanced workforce may be able to accelerate…" | "…clean, sustainable energy or crops. It all sounds pretty great!" |
| P08a-the-worker | "But here's the other side of the same coin." | "…humans are expensive to employ." |
| P08b-the-benefits-stack | "Salaries aside, the entire HR or People ops org…" | "…the best humans still make mistakes." |
| P08c-fuel-lozenge | "So why would a company choose to employ a human…" | "…for a fraction of the headache?" |
| P09-seat-and-vibe-shed | "This is why the economy is freaking out about things like seat-based pricing." | "…everyone hated it to begin with!" (Seat card + ? on the pricing beat; the shed assembles on the vibe-coding passage.) |
| P10-specialist-parade | "The trend has continued, seeping into other types of work." | "…The list goes on." |
| P11-series-title | "In this series, we'll unravel the mystery…" | End. Hold the title card to the fade. |

## Style guardrails (do not violate during assembly)

- No added text overlays, lower-thirds, or logos — the clips are the
  visual language and the narration owns the words.
- No vendor names or product screenshots on screen; the narration names
  names by design and the pixels stay neutral.
- Keep the paper background unletterboxed (deliver 16:9 as-is).
- Music, if any, stays far under the narration and never on P08a-c
  (the labor-economics beats play sincere and quiet by design).

## Regenerating or editing a clip

Each clip is a scene class in `animations/src/scenes/preamble.py`
(Preamble01 … Preamble11, with 07a/b/c and 08a/b/c). Global tempo lives
at the top of that file (PACE_PLAY, PACE_WAIT, HOLD). After ANY edit:
draft-check, then re-boil the single clip:

```bash
for s in 1 2 3; do SCRIBBLE_SEED=$s manim -r 1920,1080 --fps 30 \
  --media_dir renders/boil_s$s src/scenes/preamble.py <ClassName>; done
python3 scripts/interleave.py <stem> <ClassName>
python3 scripts/verify.py renders/final/<stem>.mp4   # must pass
```

Context on the wider project: `CLAUDE-HANDOFF.md` (session assets),
`RUN-OF-SHOW.md` (the live-session sequence), `STORYBOARDS.md` (the
Jobsite world the preamble clips inherit).
