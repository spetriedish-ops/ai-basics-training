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

# the frontier player is the newest pattern: dedicated native hold clips
# (holds/NN.mp4, loop=true) instead of JS tail-seeking — immune to
# throttled-tab replay glitches
PLAYER_TEMPLATE_PATH = (HERE / "pencil-codex" / "interactive" /
                        "frontier_labs" / "index.html")


def slug(label):
    keep = "".join(c if c.isalnum() or c == " " else "" for c in label.lower())
    return "-".join(keep.split())[:40]


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
    template = PLAYER_TEMPLATE_PATH.read_text()
    for stem, (title, stages) in SCENES.items():
        src = FINAL / f"{stem}.mp4"
        scene_dir = OUT / stem
        stages_dir = scene_dir / "stages"
        holds_dir = scene_dir / "holds"
        stages_dir.mkdir(parents=True, exist_ok=True)
        holds_dir.mkdir(parents=True, exist_ok=True)
        manifest = {"stages": [], "controls":
                    ["click", "Space", "ArrowRight", "ArrowLeft",
                     "H (hide HUD)", "R (restart)"],
                    "source": f"renders/final/{stem}.mp4"}
        prev = 0.0
        for i, (label, end) in enumerate(stages, 1):
            name = f"{i:02d}-{slug(label)}.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-ss", str(prev),
                 "-to", str(end), "-i", str(src),
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                 str(stages_dir / name)], check=True)
            # native hold loop: the stage's final boil cycle as its own clip
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-ss", str(end - HOLD),
                 "-to", str(end), "-i", str(src),
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                 str(holds_dir / name)], check=True)
            manifest["stages"].append({"label": label,
                                       "src": f"stages/{name}",
                                       "hold": f"holds/{name}"})
            prev = end
        (scene_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2))

        import re
        html = template
        html = re.sub(r"<title>.*?</title>",
                      f"<title>{title} — presenter player</title>", html)
        html = re.sub(r'aria-label="Advance [^"]*"',
                      f'aria-label="Advance {title} animation"', html)
        html = re.sub(r"const stages = \[.*?\];",
                      "const stages = " + json.dumps(manifest["stages"]) + ";",
                      html, count=1, flags=re.S)
        # hardening: if autoplay was blocked, the first click PLAYS the
        # current stage instead of skipping past it
        old_adv = "function advance() { if (index < stages.length - 1)"
        assert old_adv in html, "player template changed; update the patch"
        html = html.replace(
            old_adv,
            "function advance() {\n"
            "      if (video.paused && video.currentTime < 0.05) {"
            " video.play().catch(() => {}); return; }\n"
            "      if (index < stages.length - 1)")
        (scene_dir / "index.html").write_text(html)
        print(f"{stem}: {len(stages)} stages -> {scene_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheets", action="store_true")
    a = ap.parse_args()
    sheets() if a.sheets else split()
