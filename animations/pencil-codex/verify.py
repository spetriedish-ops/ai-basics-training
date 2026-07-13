#!/usr/bin/env python3
"""Verify the format, loop, contrast, and accent cues of the final outputs."""

from __future__ import annotations

import json
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
MP4 = HERE / "out" / "agentic_loop.mp4"
GIF = HERE / "out" / "agentic_loop.gif"


def probe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_streams", "-show_format",
            "-of", "json", str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def frame(path: Path, at: str, output: Path) -> np.ndarray:
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-ss", at, "-i", str(path),
            "-frames:v", "1", str(output),
        ],
        check=True,
    )
    return np.asarray(Image.open(output).convert("RGB"), dtype=np.int16)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


def main() -> None:
    require(MP4.is_file(), "MP4 exists")
    require(GIF.is_file(), "GIF exists")

    mp4 = probe(MP4)
    gif = probe(GIF)
    mp4_video = next(stream for stream in mp4["streams"] if stream["codec_type"] == "video")
    gif_video = next(stream for stream in gif["streams"] if stream["codec_type"] == "video")

    require(mp4_video["codec_name"] == "h264", "MP4 codec is H.264")
    require((mp4_video["width"], mp4_video["height"]) == (1920, 1080), "MP4 is 1920x1080")
    require(Fraction(mp4_video["r_frame_rate"]) == 30, "MP4 is 30 fps")
    require(float(mp4["format"]["duration"]) <= 25.0, "MP4 is no longer than 25 seconds")
    require(not any(stream["codec_type"] == "audio" for stream in mp4["streams"]), "MP4 has no audio")

    require(gif_video["codec_name"] == "gif", "wiki output is a GIF")
    require(gif_video["width"] <= 960, "GIF is no wider than 960 px")
    require(GIF.stat().st_size < 10_000_000, "GIF is under 10 MB")

    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        opening = frame(MP4, "0.00", temp / "opening.png")
        ending = frame(MP4, "23.46", temp / "ending.png")
        full = frame(MP4, "11.10", temp / "full.png")
        active = frame(MP4, "12.55", temp / "active.png")

        seam_delta = float(np.abs(opening - ending).mean())
        require(seam_delta < 2.0, f"opening/ending paper seam is clean (mean delta {seam_delta:.2f})")

        ink_pixels = int((full.mean(axis=2) < 155).sum())
        require(ink_pixels > 28_000, f"assembled loop has strong ink contrast ({ink_pixels} dark pixels)")

        teal = np.array([46, 167, 154], dtype=np.int16)
        teal_pixels = int((np.abs(active - teal).sum(axis=2) < 95).sum())
        require(teal_pixels > 4_000, f"active loop cue is visible ({teal_pixels} teal pixels)")

    print("\nAll delivery checks passed.")


if __name__ == "__main__":
    main()
