#!/usr/bin/env python3
"""Check encoded bonus clips, pixel-level story evidence, and stable holds."""
import json
import subprocess
from pathlib import Path
from fractions import Fraction

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
PLAYER = HERE / "interactive" / "computer_control_bonus"


def probe(path):
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))


def frame(path, time):
    pixels = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(time),
        "-i", str(path), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
    return np.frombuffer(pixels, dtype=np.uint8).reshape(1080, 1920, 3).astype(np.int16)


def require(condition, message):
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}", flush=True)


def ink(image):
    return (image.mean(axis=2) < 140).sum()


def geometry(image):
    # Remove sub-pixel graphite jitter when comparing held compositions.
    return np.asarray(Image.fromarray(image.astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(1.5)), dtype=np.int16)


def main():
    for scene, duration in [("computer_control", 25), ("saloon_doors", 31)]:
        path = HERE / "out" / f"{scene}.mp4"
        info = probe(path)
        v = info["streams"][0]
        require(v["codec_name"] == "h264" and (v["width"], v["height"]) == (1920,1080)
                and Fraction(v["r_frame_rate"]) == 30, f"{scene}: H.264, 1080p, 30fps")
        require(len(info["streams"]) == 1 and abs(float(info["format"]["duration"]) - duration) < .04,
                f"{scene}: silent master with correct duration")
        require((HERE / "out" / f"{scene}.gif").stat().st_size < 10_000_000,
                f"{scene}: GIF below 10 MB")
        for i in range(1, 4):
            stage = PLAYER / scene / "stages" / f"{i:02}.mp4"
            hold = PLAYER / scene / "holds" / f"{i:02}.mp4"
            stage_info = probe(stage)
            end = frame(stage, float(stage_info["format"]["duration"]) - .034)
            first, last = frame(hold,0), frame(hold,.4)
            require(float(np.abs(geometry(first)-geometry(end)).mean()) < 3.5,
                    f"{scene} beat {i}: hold preserves the last frame")
            delta = float(np.abs(first-last).mean())
            require(.05 < delta < 4.5, f"{scene} beat {i}: subtle boil without action replay ({delta:.2f})")
    computer = HERE / "out" / "computer_control.mp4"
    before, after = frame(computer, 4.5), frame(computer, 12.5)
    # The empty Done column becomes populated; the In progress card disappears.
    require(ink(after[570:728,1208:1574]) > ink(before[570:728,1208:1574]) + 1800,
            "Desktop: completed ticket visibly occupies Done")
    require(ink(before[570:728,758:1123]) > ink(after[570:728,758:1123]) + 1800,
            "Desktop: ticket leaves In progress")
    saloon = HERE / "out" / "saloon_doors.mp4"
    # Compare the same redraw phase before/after impact to isolate board motion.
    open_frame, boards, final = frame(saloon,10.5), frame(saloon,15.5), frame(saloon,28)
    # Inspect the right end of all three planks, clear of the cowboy's path.
    roi = np.s_[475:820,1480:1630,:]
    require(float(np.abs(open_frame[roi]-boards[roi]).mean()) > 9,
            "Saloon: three boards visibly close the entrance")
    require(float(np.abs(geometry(final)[roi]-geometry(boards)[roi]).mean()) < 3.5,
            "Saloon: boarding stays intact after the failed attempt")
    require(ink(final[480:940,925:1240]) > ink(boards[480:940,925:1240]) + 2000,
            "Saloon: cowboy remains outside after impact")


if __name__ == "__main__":
    main()
