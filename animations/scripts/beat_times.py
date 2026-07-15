#!/usr/bin/env python3
"""
Dry-run a scene's construct() to extract its beat timeline.

Patches Scene.play/wait to a pure clock (no rendering), logs every
CaptionManager.set with its cumulative code-time, and prints the total.
Cut points for the interactive stage split are chosen from this log,
then scaled by (final mp4 duration / total code time) to correct the
per-play frame-rounding drift.

Usage: python3 scripts/beat_times.py <stem> <SceneClass>
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "scenes"))

from manim import Scene  # noqa: E402
import jobsite  # noqa: E402

CLOCK = {"t": 0.0}


def fake_play(self, *anims, run_time=1.0, **kw):
    CLOCK["t"] += float(run_time)


def fake_wait(self, duration=1.0, **kw):
    CLOCK["t"] += float(duration)


def fake_noop(self, *a, **kw):
    pass


real_cap_set = jobsite.CaptionManager.set


def logged_cap_set(self, text, color=None, run_time=0.45):
    print(f"{CLOCK['t']:7.2f}  CAPTION  {text}")
    CLOCK["t"] += run_time
    new = jobsite.hand_label(text, size=36)
    self.current = new
    return new


def main():
    stem, cls_name = sys.argv[1], sys.argv[2]
    mod = __import__(stem)
    cls = getattr(mod, cls_name)

    Scene.play = fake_play
    Scene.wait = fake_wait
    Scene.add = fake_noop
    Scene.remove = fake_noop
    jobsite.CaptionManager.set = logged_cap_set
    jobsite.CaptionManager.clear = lambda self, run_time=0.3: fake_wait(
        None, run_time)

    scene = cls.__new__(cls)          # skip renderer-heavy __init__

    class _Cam:                        # the only attribute construct touches
        background_color = None
    cls.camera = _Cam()               # shadow the Scene.camera property

    scene.construct()
    print(f"{CLOCK['t']:7.2f}  TOTAL")


if __name__ == "__main__":
    main()
