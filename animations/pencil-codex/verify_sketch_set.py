#!/usr/bin/env python3
"""Verify formats, loop seams, writing reveals, and visual cues for sketches 02–06."""

from __future__ import annotations

import json
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

# writing, written, full, active-highlight sample times
CHECKS = {
    "frontier_labs": (1.55, 3.00, 9.55, 10.70),
    "mcp_cli_api": (0.80, 3.20, 9.35, 10.75),
    "harness_mind_map": (0.60, 1.40, 22.80, 20.00),
    "what_is_an_agent": (0.65, 9.10, 9.65, 10.75),
    "multi_agent_orchestration": (2.20, 6.65, 20.65, 19.35),
}


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


def frame(path: Path, at: float, output: Path) -> np.ndarray:
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-ss", f"{at:.3f}",
            "-i", str(path), "-frames:v", "1", str(output),
        ],
        check=True,
    )
    return np.asarray(Image.open(output).convert("RGB"), dtype=np.int16)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


def verify_scene(stem: str, times: tuple[float, float, float, float]) -> None:
    mp4 = OUT / f"{stem}.mp4"
    gif = OUT / f"{stem}.gif"
    require(mp4.is_file(), f"{stem}: MP4 exists")
    require(gif.is_file(), f"{stem}: GIF exists")

    mp4_info = probe(mp4)
    gif_info = probe(gif)
    video = next(stream for stream in mp4_info["streams"] if stream["codec_type"] == "video")
    gif_video = next(stream for stream in gif_info["streams"] if stream["codec_type"] == "video")
    duration = float(mp4_info["format"]["duration"])

    require(video["codec_name"] == "h264", f"{stem}: MP4 codec is H.264")
    require((video["width"], video["height"]) == (1920, 1080), f"{stem}: MP4 is 1920x1080")
    require(Fraction(video["r_frame_rate"]) == 30, f"{stem}: MP4 is 30 fps")
    require(duration <= 25.0, f"{stem}: duration is no longer than 25 seconds")
    require(not any(s["codec_type"] == "audio" for s in mp4_info["streams"]), f"{stem}: MP4 is silent")
    require(gif_video["codec_name"] == "gif", f"{stem}: wiki output is a GIF")
    require(gif_video["width"] <= 960, f"{stem}: GIF is no wider than 960 px")
    require(gif.stat().st_size < 10_000_000, f"{stem}: GIF is under 10 MB")

    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        opening = frame(mp4, 0.00, temp / "opening.png")
        paper_boil = frame(mp4, 0.17, temp / "boil.png")
        ending = frame(mp4, duration - 0.04, temp / "ending.png")
        writing = frame(mp4, times[0], temp / "writing.png")
        written = frame(mp4, times[1], temp / "written.png")
        full = frame(mp4, times[2], temp / "full.png")
        active = frame(mp4, times[3], temp / "active.png")

        seam_delta = float(np.abs(opening - ending).mean())
        require(seam_delta < 2.6, f"{stem}: opening/ending seam is clean ({seam_delta:.2f})")
        boil_delta = float(np.abs(opening - paper_boil).mean())
        require(0.15 < boil_delta < 2.5, f"{stem}: paper boils without flashing ({boil_delta:.2f})")

        writing_ink = int((writing.mean(axis=2) < 155).sum())
        written_ink = int((written.mean(axis=2) < 155).sum())
        require(written_ink > writing_ink + 450, f"{stem}: live writing adds ink ({writing_ink} → {written_ink})")
        full_ink = int((full.mean(axis=2) < 155).sum())
        require(full_ink > 18_000, f"{stem}: final composition has strong contrast ({full_ink} dark pixels)")

        if stem != "harness_mind_map":
            teal = np.array([46, 167, 154], dtype=np.int16)
            teal_pixels = int((np.abs(active - teal).sum(axis=2) < 125).sum())
            require(teal_pixels > 900, f"{stem}: active teaching cue is visible ({teal_pixels} teal pixels)")

        if stem == "multi_agent_orchestration":
            warm = (
                (active[..., 0] > active[..., 1] + 24)
                & (active[..., 1] > active[..., 2] + 12)
                & (active[..., 0] > 180)
            )
            warm_pixels = int(warm.sum())
            require(warm_pixels > 2_500, f"{stem}: incinerator fire is visibly colored ({warm_pixels} warm pixels)")

            walk_a = frame(mp4, 15.65, temp / "walk_a.png")
            walk_b = frame(mp4, 17.25, temp / "walk_b.png")
            walking_region = np.abs(walk_a[800:1050, 560:1360] - walk_b[800:1050, 560:1360])
            motion_delta = float(walking_region.mean())
            require(motion_delta > 1.0, f"{stem}: sub-agents visibly change position ({motion_delta:.2f} mean delta)")


def verify_harness_player() -> None:
    directory = HERE / "interactive" / "harness_mind_map"
    html = directory / "index.html"
    manifest_path = directory / "manifest.json"
    require(html.is_file(), "Harness player: HTML exists")
    require(manifest_path.is_file(), "Harness player: manifest exists")

    source = html.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    stages = manifest["stages"]
    require(len(stages) == 8, "Harness player: all eight stages are configured")
    require("ArrowRight" in source and "ArrowLeft" in source, "Harness player: keyboard navigation is wired")
    require("shell.addEventListener('click', advance)" in source, "Harness player: click advancement is wired")
    require("HOLD_SECONDS" in source, "Harness player: completed stages keep boiling")

    for index, stage in enumerate(stages, start=1):
        clip = directory / stage["src"]
        require(clip.is_file(), f"Harness player: stage {index} clip exists")
        info = probe(clip)
        video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
        require(video["codec_name"] == "h264", f"Harness player: stage {index} is H.264")
        require((video["width"], video["height"]) == (1920, 1080), f"Harness player: stage {index} is 1920x1080")


def main() -> None:
    for stem, times in CHECKS.items():
        print(f"\n{stem}")
        verify_scene(stem, times)
    print("\nHarness interactive player")
    verify_harness_player()
    print("\nAll sketch-set delivery checks passed.")


if __name__ == "__main__":
    main()
