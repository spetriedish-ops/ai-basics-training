#!/usr/bin/env python3
"""
Split the Jobsite scenes' final renders into click-paced stage clips and
emit an interactive/<scene>/ player for each, matching the pencil-codex
player contract (index.html + manifest.json + stages/NN-*.mp4; click/
Space/-> advance, <- back, H hides HUD, R restarts; each stage holds by
looping its final 0.52 s boil cycle).

Cut times were derived from scripts/beat_times.py dry-run timelines,
scaled by (final duration / code duration), and verified frame-by-frame
via the --sheets contact sheets. The scenes' exit beats (truck rolls
off to an empty stage — the old slide-loop convention) are deliberately
cut: the last stage holds on the complete tableau.

Usage (from animations/):
  python3 scripts/stage_split.py --sheets   # contact sheets to /tmp for review
  python3 scripts/stage_split.py            # split + write players
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
FINAL = HERE / "renders" / "final"
OUT = HERE / "interactive"
HOLD = 0.52   # one 3-seed boil cycle + margin, matches the codex player

# scene -> (title, [(label, end_time_in_final_seconds), ...])
SCENES = {
    "garage": ("The Garage", [
        ("Rules: perfect on the line", 5.84),
        ("One learned route", 8.60),
        ("An engine for anything", 14.27),
        ("Each generation hauls more", 20.59),
        ("Meet today's truck", 22.50),
    ]),
    "paver": ("The Paver", [
        ("The prediction engine", 3.05),
        ("Words become tokens", 6.18),
        ("One brick at a time", 11.38),
        ("Tokens in, tokens out", 15.80),
        ("Confident. Smooth. Wrong.", 22.75),
        ("It never checks the map", 24.62),
        ("Only the recent road", 27.20),
    ]),
    "context_window": ("The Truck — context window", [
        ("Everything you load takes tokens", 6.12),
        ("Tools bolt on abilities", 10.51),
        ("Every tool adds weight", 13.63),
        ("Surely one more", 16.56),
        ("Too many to choose", 18.69),
        ("Overfill and things fall out", 21.66),
        ("The dump: session over", 25.50),
        ("Every new session starts empty", 27.30),
    ]),
    "toolbox": ("The Toolbox — MCP", [
        ("One connection, a whole toolbox", 4.16),
        ("Every tool ships a card", 8.76),
        ("More tools, more you can do", 11.35),
        ("Surely one more box", 15.19),
        ("The wrong tool grabs", 17.95),
        ("Curate the toolbox", 21.70),
    ]),
    "agent_anatomy": ("Pop the Hood — anatomy", [
        ("Meet the agent", 3.42),
        ("The model inside", 5.59),
        ("The context window", 8.42),
        ("Tools", 11.76),
        ("Skills", 14.55),
        ("The loop, twice around", 21.90),
        ("The harness: the site", 29.44),
        ("Backup arrives", 30.70),
    ]),
    "fleet": ("The Fleet — orchestration", [
        ("Some jobs are too big alone", 3.56),
        ("A subagent goes out", 6.59),
        ("Its own bed, its own fuel", 8.95),
        ("Only the result comes back", 12.33),
        ("One coordinator, many specialists", 16.87),
        ("Coordination is also a job", 21.61),
        ("Three vans, on a schedule", 24.28),
        ("The whole site", 26.60),
    ]),
    "engine_factory": ("The Engine Factory — model lifecycle", [
        ("Pre-training", 4.16),
        ("Post-training", 7.40),
        ("Release day", 10.44),
        ("To work; the factory closes", 15.36),
        ("Inference: every time it runs", 22.00),
    ]),
}

# Self-contained player: each stage is ONE file that plays once and ends
# frozen on its tableau (the boiling hold is baked into the file's tail).
# No src swaps mid-flight, no native loops of tiny files — both stuttered
# on the presentation machine.
PLAYER = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>__TITLE__ — presenter player</title>
  <style>
    :root { color-scheme: light; }
    * { box-sizing: border-box; }
    html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #111; }
    body { display: grid; place-items: center; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }
    .stage { position: relative; width: min(100vw, calc(100vh * 16 / 9)); aspect-ratio: 16 / 9; background: #faf7ef; cursor: pointer; }
    video { display: block; width: 100%; height: 100%; object-fit: contain; }
    .hud { position: absolute; right: 1.15rem; bottom: 1rem; display: grid; gap: .35rem; justify-items: end; color: #34323e; text-shadow: 0 1px rgba(250,247,239,.9); transition: opacity .18s; pointer-events: none; }
    .hud.hidden { opacity: 0; }
    .count { padding: .34rem .55rem; border: 1px solid rgba(52,50,62,.28); border-radius: 999px; background: rgba(250,247,239,.76); font-size: clamp(.66rem, 1.05vw, .94rem); }
    .hint { font-size: clamp(.58rem, .88vw, .80rem); opacity: .72; }
    .stage:focus-visible { outline: 4px solid #2ea79a; outline-offset: -4px; }
  </style>
</head>
<body>
  <main class="stage" tabindex="0" role="button" aria-label="Advance __TITLE__ animation">
    <video muted playsinline preload="auto"></video>
    <div class="hud">
      <div class="count" aria-live="polite"></div>
      <div class="hint">click / space / → next · ← back · H hide</div>
    </div>
  </main>
  <script>
    const stages = __STAGES__;
    const shell = document.querySelector('.stage');
    const video = document.querySelector('video');
    const hud = document.querySelector('.hud');
    const count = document.querySelector('.count');
    let index = 0;

    function label() {
      count.textContent = `${index + 1} / ${stages.length} · ${stages[index].label}`;
    }

    function loadStage(next, playFromStart = true) {
      index = Math.max(0, Math.min(stages.length - 1, next));
      label();
      video.src = stages[index].src;
      video.load();
      video.addEventListener('loadedmetadata', () => {
        if (playFromStart) { video.play().catch(() => {}); }
        else { video.currentTime = Math.max(0, video.duration - 0.05); }
      }, { once: true });
    }

    function advance() {
      // autoplay was blocked on a fresh stage: first click plays it
      if (video.paused && !video.ended && video.currentTime < 0.1) {
        video.play().catch(() => {});
        return;
      }
      if (index < stages.length - 1) loadStage(index + 1);
    }

    function back() { if (index > 0) loadStage(index - 1, false); }

    shell.addEventListener('click', advance);
    window.addEventListener('keydown', (event) => {
      if (event.key === ' ' || event.key === 'ArrowRight' || event.key === 'Enter') { event.preventDefault(); advance(); }
      if (event.key === 'ArrowLeft') { event.preventDefault(); back(); }
      if (event.key.toLowerCase() === 'h') hud.classList.toggle('hidden');
      if (event.key.toLowerCase() === 'r') loadStage(0);
    });
    loadStage(0);
    shell.focus();
  </script>
</body>
</html>
"""


def slug(label):
    keep = "".join(c if c.isalnum() or c == " " else "" for c in label.lower())
    return "-".join(keep.split())[:40]


FPS = 30
SEED_CYCLE = 15          # 3 boil seeds x 5 frames
HOLD_FRAMES = SEED_CYCLE + 1
TAIL_REPS = 15           # boil cycles baked onto each stage (~8.5 s)


def gray_frames(path):
    """Whole video, 240x135 grayscale, as an (n, h, w) uint8 array."""
    import numpy as np
    p = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path),
         "-vf", "scale=240:135,format=gray", "-f", "rawvideo", "-"],
        capture_output=True, check=True)
    n = len(p.stdout) // (240 * 135)
    return np.frombuffer(p.stdout[:n * 240 * 135], "uint8"
                         ).reshape(n, 135, 240).astype("int16")


def loop_scores(f):
    """score[i] = motion across the would-be hold window starting at i.

    Compares frames one full boil-seed cycle apart, so pure boil scores
    ~0.1-0.9 and any real animation scores >2. A hold window is the
    HOLD_FRAMES frames from i; it loops seamlessly iff static.
    """
    import numpy as np
    d = np.abs(f[SEED_CYCLE:] - f[:-SEED_CYCLE]).mean(axis=(1, 2))
    n = len(d)
    return np.array([max(d[i], d[min(i + 1, n - 1)]) for i in range(n)])


def place_cuts(scores, semantic_ends, duration):
    """Snap each semantic cut to the nearest static boil window.

    Prefers the latest static window at or before the semantic cut
    (teaching content complete, tableau at rest); if the beat is still
    moving there, walks forward toward the next cut. Returns
    (end_frames, mode) per stage; mode 'freeze' marks no-window-found.
    """
    placed = []
    prev = 0
    n = len(scores)
    for k, end_s in enumerate(semantic_ends):
        c = min(int(end_s * FPS), n - 1)
        hi = (min(int(semantic_ends[k + 1] * FPS), n) - 4
              if k + 1 < len(semantic_ends)
              else min(int(duration * FPS) - 2, n))
        lo = prev + 8
        pick, mode = None, "static"
        for thr in (0.9, 1.8):
            back = [i for i in range(lo, min(c, hi) - HOLD_FRAMES + 1)
                    if scores[i] < thr]
            if back:
                pick = back[-1]
                break
            fwd = [i for i in range(min(c, hi) - HOLD_FRAMES + 1,
                                    hi - HOLD_FRAMES + 1)
                   if i >= lo and scores[i] < thr]
            if fwd:
                pick = fwd[0]
                break
        if pick is None:                    # fully animated beat tail
            pick, mode = min(c, hi) - HOLD_FRAMES, "freeze"
        placed.append((pick + HOLD_FRAMES, mode))
        prev = pick + HOLD_FRAMES
    return placed


def sheets():
    from PIL import Image, ImageDraw
    for stem, (title, stages) in SCENES.items():
        tiles = []
        for label, end in stages:
            f = Path(f"/tmp/ss_{stem}_{end}.png")
            subprocess.run(["ffmpeg", "-y", "-v", "error",
                            "-ss", str(max(0, end - 0.06)),
                            "-i", str(FINAL / f"{stem}.mp4"),
                            "-frames:v", "1", "-vf", "scale=480:-1", str(f)],
                           check=True)
            tiles.append((label, end, Image.open(f)))
        w, h = tiles[0][2].size
        cols = min(4, len(tiles))
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w, rows * (h + 22)), (250, 247, 239))
        d = ImageDraw.Draw(sheet)
        for i, (label, end, im) in enumerate(tiles):
            x, y = (i % cols) * w, (i // cols) * (h + 22)
            sheet.paste(im, (x, y + 22))
            d.text((x + 4, y + 4), f"{i+1} @{end}s {label}", fill=(51, 50, 62))
        p = f"/tmp/sheet_{stem}.png"
        sheet.save(p)
        print("sheet:", p)


def split():
    import shutil
    for stem, (title, stages) in SCENES.items():
        src = FINAL / f"{stem}.mp4"
        scene_dir = OUT / stem
        stages_dir = scene_dir / "stages"
        stages_dir.mkdir(parents=True, exist_ok=True)
        shutil.rmtree(scene_dir / "holds", ignore_errors=True)
        manifest = {"stages": [], "controls":
                    ["click", "Space", "ArrowRight", "ArrowLeft",
                     "H (hide HUD)", "R (restart)"],
                    "source": f"renders/final/{stem}.mp4"}
        # snap every cut to a static boil window, then bake the boiling
        # hold INTO the stage file: the static window repeated TAIL_REPS
        # times in one continuous encode. One file per stage, played once,
        # freezing at its end — no src swaps, no native loops, nothing for
        # a browser to stutter on. (Separate looping hold files skipped
        # frames on the presentation machine — twice.)
        import numpy as np  # noqa: F401
        f = gray_frames(src)
        dur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(src)], capture_output=True, text=True,
            check=True).stdout.strip())
        scores = loop_scores(f)
        placed = place_cuts(scores, [e for _, e in stages], dur)
        prev = 0.0
        for i, ((label, _), (end_fr, mode)) in enumerate(
                zip(stages, placed), 1):
            end = end_fr / FPS
            hold_start = (end_fr - HOLD_FRAMES) / FPS
            if mode == "freeze":
                print(f"  NOTE {stem} stage {i}: no static window — "
                      f"tail freezes without boil")
            name = f"{i:02d}-{slug(label)}.mp4"
            fc = (
                f"[0:v]trim=start={prev}:end={end},"
                f"setpts=PTS-STARTPTS[body];"
                f"[0:v]trim=start={hold_start}:end={end},"
                f"setpts=PTS-STARTPTS,loop=loop={TAIL_REPS}:"
                f"size={HOLD_FRAMES}:start=0[tail];"
                f"[body][tail]concat=n=2:v=1[out]"
            )
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-i", str(src),
                 "-filter_complex", fc, "-map", "[out]",
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                 str(stages_dir / name)], check=True)
            manifest["stages"].append({"label": label,
                                       "src": f"stages/{name}"})
            prev = end
        (scene_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2))

        html = (PLAYER
                .replace("__TITLE__", title)
                .replace("__STAGES__", json.dumps(manifest["stages"])))
        (scene_dir / "index.html").write_text(html)
        print(f"{stem}: {len(stages)} stages -> {scene_dir}")


def verify():
    """Every stage file's baked tail must be static boil (no jumping)."""
    import numpy as np
    tail_frames = HOLD_FRAMES * TAIL_REPS
    bad = []
    for mf in sorted(OUT.glob("*/manifest.json")):
        m = json.loads(mf.read_text())
        for st in m["stages"]:
            f = gray_frames(mf.parent / st["src"])
            t = f[-min(tail_frames, len(f) - 1):]
            d = float(np.abs(t[SEED_CYCLE:] - t[:-SEED_CYCLE]).mean())
            ok = d < 1.9
            print(f"[{'PASS' if ok else 'FAIL'}] {mf.parent.name}/"
                  f"{st['src']}  tail motion={d:.2f}")
            if not ok:
                bad.append(st["src"])
    if bad:
        sys.exit(f"{len(bad)} stage tail(s) would jump — do not ship.")
    print("\nAll stage tails hold clean.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheets", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    if a.sheets:
        sheets()
    elif a.verify:
        verify()
    else:
        split()
