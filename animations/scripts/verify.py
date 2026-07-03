#!/usr/bin/env python3
"""Pixel-level render verification. Run after EVERY render, before commit.

Usage: python3 scripts/verify.py <video.mp4> [--scene context_window]

Asserts that expected fill colors / label ink actually exist at key story
beats. Thresholds are calibrated for 1080p and scale with resolution.
Exit code 0 = pass, 1 = fail.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

PALETTE = {
    "teal": (46, 167, 154), "amber": (255, 201, 77), "coral": (255, 138, 92),
    "lilac": (195, 177, 225), "sage": (168, 213, 162), "alert": (228, 87, 46),
    "ink": (51, 50, 62),
}

# beat time (s) -> {color: min pixels at 1920x1080}
SCENES = {
    # Truck v2 (STORYBOARDS.md scene 3) — thresholds ≈ 40% of measured
    "context_window": {
        5.5: {"teal": 40000, "amber": 1800, "lilac": 4500, "sage": 8000,
              "ink": 30000},                     # info cargo loaded
        10.5: {"teal": 40000, "coral": 2300},    # crane on + CRANE manual
        16.5: {"coral": 6000, "alert": 2300},    # gag pile-on, meter red
        18.5: {"alert": 4500, "amber": 11000},   # can't choose + LIFT ME
        21.5: {"lilac": 16000, "alert": 4500},   # MORE DOCS overflow
        25.0: {"teal": 42000, "ink": 30000},     # dump: bed tipped, truck ok
        28.5: {"teal": 42000},                   # fresh: truck present, bare
    },
    "style_test_scribble": {
        3.5: {"teal": 20000, "amber": 1500, "ink": 20000},
    },
    # The Paver (STORYBOARDS.md scene 2)
    "paver": {
        3.0: {"teal": 10000, "amber": 3500, "lilac": 5500, "ink": 20000},
        13.0: {"teal": 11000, "sage": 6500},   # meter on, road growing
        20.0: {"alert": 1600, "ink": 25000},   # missed turnoff, ALERT caption
        25.0: {"amber": 8500, "coral": 5500,
               "lilac": 10000},                # loop-de-loop + DONE flag
        27.0: {"teal": 11000, "lilac": 6500},  # ghost road, loop still lit
    },
    # Pop the Hood (STORYBOARDS.md scene 4)
    "agent_anatomy": {
        6.0: {"teal": 12000, "ink": 25000, "amber": 1800},  # cab + model bubble
        12.0: {"teal": 45000, "ink": 35000},   # bed + tools assembled, tags
        19.0: {"teal": 40000, "amber": 4500},  # loop running, MIX crate
        24.5: {"teal": 40000, "amber": 9000},  # harness props (pump amber)
        28.0: {"teal": 40000, "ink": 35000},   # gate gag / APPROVED stamp
        31.5: {"teal": 45000},                 # van tease + exit begins
    },
}


def count(im: np.ndarray, rgb, tol=70) -> int:
    return int((np.abs(im - np.array(rgb)).sum(axis=2) < tol).sum())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--scene", default=None,
                    help="beat-spec key; inferred from filename if omitted")
    args = ap.parse_args()

    stem = args.scene or Path(args.video).stem.lower()
    spec = SCENES.get(stem)
    if spec is None:
        sys.exit(f"no beat spec for '{stem}' — add one to scripts/verify.py")

    failures = []
    with tempfile.TemporaryDirectory() as td:
        for t, expect in spec.items():
            frame = Path(td) / f"f{t}.png"
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-ss", str(t),
                 "-i", args.video, "-frames:v", "1", str(frame)],
                check=True)
            im = np.array(Image.open(frame).convert("RGB")).astype(int)
            scale = (im.shape[0] * im.shape[1]) / (1920 * 1080)
            for color, min_px in expect.items():
                need = int(min_px * scale)
                got = count(im, PALETTE[color])
                ok = got >= need
                print(f"[{'PASS' if ok else 'FAIL'}] t={t:>5}s  "
                      f"{color:<6} {got:>7} px (need ≥ {need})")
                if not ok:
                    failures.append((t, color, got, need))

    if failures:
        print(f"\n{len(failures)} check(s) FAILED — do not commit this render.")
        return 1
    print("\nAll checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
