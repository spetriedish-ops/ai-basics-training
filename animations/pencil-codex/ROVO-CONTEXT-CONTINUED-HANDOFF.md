# Rovo CLI handoff: Context continued

Sarah approved this nugget on November 11, 2026. The completed animations,
assets, source renderers, presenter cues, and videos are included on branch
`codex/rovo-architecture-animations`.

## Start here

From the repository root, serve the included media:

```bash
python3 -m http.server 8765 --directory animations
```

Open `http://127.0.0.1:8765/pencil-codex/interactive/context_continued/index.html`.
This is the final 43-beat click-through. No rendering, Blender, image generation,
or extra Python packages are needed to play or record it.

- Click, Right Arrow, or Space advances when the animation is holding.
- Left Arrow goes back; R replays; H hides controls; F enters fullscreen.
- Use the jump menu to revisit a beat. Each action finishes before another
  advance is accepted; native looping holds allow unlimited narration time.
- The ending alone is at `interactive/context_ending/index.html`.

## Final editorial choices

The final manifest is `interactive/context_continued/manifest.json`. Use its
ordered `beats`, their `src` action clips, `hold` loops, and presenter `cue`
text as the source of truth. Paths are relative to that manifest's directory.

1. Personal context portfolio: computer folder and Markdown files, four
   agent rooms, classroom close-up, and updates distributed across agents.
2. Mono-thread: VHS conversation buildup, cost, then the agent searching.
3. Compaction: individually crumpling context boxes and the armor Easter egg.
4. Lost detail: the agent inspects the summary in the emptied classroom.
5. Laundry: the approved metaphor, including the heart boxers reaction,
   disposal into the can, and the researcher's return.
6. Getting better: more room, better summaries preserving the approval rule,
   saved memory outside the room returning in a fresh session.
7. Atlassian/Rovo teaser using Sarah's supplied logo images.

Topiary is retained as an alternative, but is not in the final sequence.
The old inbox/stop-phone treatment remains in its standalone source and
preview for history; do not substitute it for laundry. The research anecdote
illustrates a lost constraint and unintended action, not inability to stop.

The full narrative is `source/context_ending/talk-track-updated.txt`.
The approved closing wording is “these capabilities are getting better.”
Avoid describing the problems as solved or promising perfect recall.

## Recording and assembly

All clips are silent, 1920 × 1080, 30 fps. Preserve their action speed and
extend the supplied hold loops to fit narration. Actor positions should stay
fixed during holds; the subtle ink animation is intentional. No extra external
narration captions are needed. Keep speech bubbles and labels already present.

`out/context_continued.mp4` is a 241.5-second continuous preview without
narration-length holds. It is compressed for convenient GitHub delivery.
For editing, use the original individual action clips and hold files in the
manifest. `out/context_ending.mp4` is the 33-second closing sequence.

## Future changes

See `README.md` for renderer commands and scene history. Renderers use the
existing Pillow/NumPy/ffmpeg workflow; prepared media is sufficient for this
handoff. `render_context_ending.py` rebuilds the conclusion and assembles the
full sequence. It intentionally takes the first 33 beats of the earlier loss
manifest, then the six laundry beats, then four ending beats.

Keep the official PNGs in `assets/context_ending/` unchanged. Preserve the
memory archive outside the context room. The previous nugget and historical
preamble handoff documents are separate projects and do not define this
nugget's final order or vendor-logo treatment.
