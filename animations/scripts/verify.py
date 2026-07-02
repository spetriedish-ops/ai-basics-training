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
    "context_window": {
        4.5: {"teal": 20000, "amber": 1500, "coral": 1500, "ink": 30000},
        7.0: {"lilac": 5000, "sage": 5000},
        9.0: {"alert": 3000, "lilac": 8000},
        13.8: {"teal": 20000, "ink": 20000},   # dump beat: bed still teal
        16.5: {"teal": 20000},                  # fresh beat: truck present
    },
    "style_test_scribble": {
        3.5: {"teal": 20000, "amber": 1500, "ink": 20000},
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
