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
        duration = float(mp4["format"]["duration"])
        opening = frame(MP4, "0.00", temp / "opening.png")
        paper_boil = frame(MP4, "0.17", temp / "paper_boil.png")
        ending = frame(MP4, f"{duration - 0.04:.2f}", temp / "ending.png")
        writing = frame(MP4, "1.38", temp / "writing.png")
        written = frame(MP4, "1.72", temp / "written.png")
        full = frame(MP4, "7.35", temp / "full.png")
        active = frame(MP4, "8.85", temp / "active.png")

        seam_delta = float(np.abs(opening - ending).mean())
        require(seam_delta < 2.5, f"opening/ending paper seam is clean (mean delta {seam_delta:.2f})")

        boil_delta = float(np.abs(opening - paper_boil).mean())
        require(
            0.15 < boil_delta < 2.5,
            f"paper boil moves without flashing (mean delta {boil_delta:.2f})",
        )

        # Expected colors after the semi-transparent ruling is composited over
        # the warm paper and H.264 encoded.
        rule_blue = np.array([202, 222, 223], dtype=np.int16)
        margin_red = np.array([235, 192, 186], dtype=np.int16)
        blue_pixels = int((np.abs(opening - rule_blue).sum(axis=2) < 34).sum())
        red_pixels = int((np.abs(opening - margin_red).sum(axis=2) < 38).sum())
        require(blue_pixels > 8_000, f"notebook ruling is visible ({blue_pixels} blue pixels)")
        require(red_pixels > 1_000, f"notebook margin is visible ({red_pixels} red pixels)")

        writing_ink = int((writing.mean(axis=2) < 155).sum())
        written_ink = int((written.mean(axis=2) < 155).sum())
        require(
            written_ink > writing_ink + 1_500,
            f"live-writing reveal adds ink over time ({writing_ink} → {written_ink} pixels)",
        )

        ink_pixels = int((full.mean(axis=2) < 155).sum())
        require(ink_pixels > 28_000, f"assembled loop has strong ink contrast ({ink_pixels} dark pixels)")

        teal = np.array([46, 167, 154], dtype=np.int16)
        teal_pixels = int((np.abs(active - teal).sum(axis=2) < 95).sum())
        require(teal_pixels > 4_000, f"active loop cue is visible ({teal_pixels} teal pixels)")

    print("\nAll delivery checks passed.")


if __name__ == "__main__":
    main()
