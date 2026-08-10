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
    # Preamble clips P01-P11 (recalibrated for 2026-08-10 pacing)
    "preamble01": {
        7.4: {"teal": 9868, "amber": 5536, "ink": 10847},
        13.4: {"teal": 10131, "amber": 5485, "ink": 10837},
    },
    "preamble02": {
        7.7: {"teal": 31654, "sage": 7518, "ink": 19800},
        13.8: {"teal": 33805, "sage": 7526, "ink": 19876},
    },
    "preamble03": {
        10.2: {"amber": 7168, "lilac": 7061, "ink": 12468},
        19.0: {"lilac": 7304, "sage": 7138, "ink": 11974},
    },
    "preamble04": {
        8.3: {"amber": 5282, "teal": 2692, "ink": 10513},
        15.1: {"amber": 5329, "teal": 2664, "ink": 10651},
    },
    "preamble05": {
        6.0: {"teal": 19335, "lilac": 3132, "ink": 16314},
        10.6: {"teal": 19335, "lilac": 3130, "ink": 16314},
    },
    "preamble06": {
        8.1: {"teal": 32089, "lilac": 3210, "ink": 23127},
        14.6: {"teal": 32174, "lilac": 3124, "ink": 23125},
    },
    "preamble07a": {
        1.0: {"teal": 30000, "ink": 21000},   # labeled tedium aboard
        9.7: {"amber": 1700, "ink": 1400},    # empty stage hold (post-exit)
    },
    "preamble07b": {
        6.7: {"amber": 2270, "lilac": 2148, "ink": 8872},
        11.9: {"amber": 2270, "lilac": 2148, "ink": 8868},
    },
    "preamble07c": {
        5.7: {"lilac": 5202, "amber": 3128, "ink": 10222},
        9.9: {"lilac": 5202, "amber": 3128, "ink": 10222},
    },
    "preamble08": {
        5.6: {"teal": 25549, "lilac": 3249, "ink": 22734},
        9.8: {"teal": 25509, "lilac": 3249, "ink": 22745},
    },
    "preamble09": {
        7.4: {"coral": 5916, "sage": 4356, "ink": 9252},
        13.2: {"coral": 5958, "amber": 4366, "ink": 9606},
    },
    "preamble10": {
        5.4: {"teal": 20806, "amber": 3004, "ink": 13316},
        9.2: {"teal": 20806, "amber": 3004, "ink": 13316},
    },
    "preamble11": {
        4.9: {"teal": 24659, "amber": 15956, "ink": 29210},
        8.2: {"teal": 24659, "amber": 15956, "ink": 29210},
    },
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
    # The Garage (STORYBOARDS.md scene 1)
    "garage": {
        3.0: {"amber": 8500, "ink": 18000},    # forklift on its line
        5.5: {"alert": 1600, "lilac": 5500},   # off-line pallet, it stops
        8.0: {"coral": 10000, "amber": 8500},  # the route van (+ cone)
        14.0: {"teal": 45000, "ink": 35000},   # today's truck assembled
        20.0: {"teal": 45000, "lilac": 9500},  # NEXT YEAR'S TRUCK poster
        23.0: {"teal": 45000, "amber": 8500},  # forklift still on its line
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
    # The Fleet (STORYBOARDS.md scene 5)
    "fleet": {
        4.0: {"teal": 45000, "ink": 30000},    # chief + BUILD THE SHED card
        9.0: {"teal": 55000, "sage": 5000},    # van's own bed/fuel cutaway
        15.0: {"teal": 60000, "amber": 4500},  # one package comes home
        21.0: {"amber": 12000, "coral": 7500,
               "alert": 3500},                 # avalanche gag, ALERT caption
        26.0: {"teal": 60000, "coral": 6000},  # recovery + shed roof
    },
    # The Engine Factory — model lifecycle (STORYBOARDS.md scene 7)
    "engine_factory": {
        2.0: {"teal": 9000, "amber": 3000, "ink": 20000},  # machine + pile
        6.5: {"teal": 12000, "ink": 22000},   # dyno tuning
        10.8: {"amber": 9500},                # release-day hullabaloo
        14.0: {"ink": 22000, "teal": 2500},   # engine seated on chassis
        15.5: {"ink": 20000, "teal": 2000},   # factory CLOSED, truck ready
        21.5: {"ink": 22000, "teal": 2500},   # odometer at 3, meter filled
    },
    # The Toolbox — MCP analogy (STORYBOARDS.md scene 6)
    "toolbox": {
        4.0: {"teal": 45000, "lilac": 11000},   # MCP box mounted
        8.0: {"teal": 45000, "lilac": 12000},   # cards billed into bed
        16.0: {"amber": 12000, "sage": 17000,
               "alert": 2300},                  # box pile-up, meter red
        17.2: {"alert": 2000, "ink": 40000},    # wrong-tool grab
        23.0: {"teal": 45000, "lilac": 11000},  # curated: one box left
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
