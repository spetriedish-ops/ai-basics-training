#!/usr/bin/env python3
"""Animate Sarah's multi-agent orchestration sketch.

The renderer lifts the original graphite from the photographed portrait page,
recomposes its three teaching beats for a 16:9 slide, and adds two restrained
motion treatments: the original sub-agent figures walk away from the main
agent, and a warm hand-drawn fire flickers inside the incinerator.
"""

from __future__ import annotations

import argparse
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

import render_agentic_loop as established
import render_sketch_set as shared


HERE = Path(__file__).resolve().parent
SKETCH = HERE.parent / "assets" / "sketches" / "06-multi-agent-orchestration.jpeg"
SOURCE_DIR = HERE / "source" / "multi_agent_orchestration"
OUT_DIR = HERE / "out"

WIDTH, HEIGHT = shared.WIDTH, shared.HEIGHT
FPS = shared.FPS
DURATION = 23.0
PAGE_SIZE = (2400, 3200)
PAGE_QUAD = ((145, 90), (100, 3735), (2800, 3735), (2790, 70))


@dataclass(frozen=True)
class PieceSpec:
    name: str
    crop: tuple[int, int, int, int]
    center: tuple[int, int]
    max_size: tuple[int, int]
    start: float
    reveal_duration: float
    order: str = "rows"
    boil_amplitude: float = 0.30
    clear_boxes: tuple[tuple[int, int, int, int], ...] = ()


@dataclass(frozen=True)
class WalkerSpec:
    name: str
    crop: tuple[int, int, int, int]
    start_center: tuple[int, int]
    end_center: tuple[int, int]
    max_size: tuple[int, int]
    reveal_start: float
    move_start: float
    move_duration: float
    phase: float
    clear_boxes: tuple[tuple[int, int, int, int], ...] = ()


@dataclass
class PreparedAsset:
    variants: tuple[Image.Image, Image.Image, Image.Image]
    reveal_order: np.ndarray
    position: tuple[int, int]
    size: tuple[int, int]


STATIC_SPECS = (
    PieceSpec("title", (1440, 55, 2240, 390), (960, 76), (720, 128), 0.28, 0.95, "left", 0.24),
    PieceSpec("subagents_heading", (490, 555, 1260, 700), (430, 170), (520, 86), 1.30, 0.70, "left", 0.25),
    PieceSpec("delegator_agent", (215, 825, 445, 1350), (235, 370), (160, 226), 2.00, 0.85, "down", 0.30),
    PieceSpec("delegator_bubble", (425, 700, 855, 1070), (365, 280), (305, 168), 2.55, 0.95, "rows", 0.28),
    PieceSpec("speed_lines", (500, 1165, 690, 1385), (580, 414), (140, 118), 3.65, 0.55, "left", 0.24),
    PieceSpec("fresh_workers", (1250, 710, 2160, 1050), (1460, 328), (720, 215), 2.90, 1.30, "rows", 0.27),
    PieceSpec("returns", (245, 1580, 1225, 2220), (540, 655), (870, 315), 7.35, 2.20, "rows", 0.30),
    PieceSpec("orchestrator_text", (1425, 1660, 2240, 2200), (1470, 620), (690, 250), 9.85, 1.65, "rows", 0.27),
    PieceSpec("finished_product", (0, 2390, 515, 3180), (270, 910), (360, 320), 12.10, 1.30, "rows", 0.31),
    PieceSpec(
        "incinerator",
        (1115, 2310, 1905, 2995),
        (1535, 920),
        (515, 330),
        13.20,
        1.55,
        "rows",
        0.30,
        ((1115, 2645, 1195, 3130),),
    ),
)


WALKER_SPECS = (
    WalkerSpec("depart_1", (705, 1145, 825, 1410), (650, 405), (850, 405), (84, 178), 3.95, 4.65, 2.05, 0.00),
    WalkerSpec("depart_2", (865, 1120, 1000, 1410), (760, 405), (1000, 405), (88, 180), 4.08, 4.78, 2.20, 1.35),
    WalkerSpec("depart_3", (1010, 1145, 1150, 1440), (870, 418), (1145, 418), (88, 180), 4.20, 4.92, 2.35, 2.65),
    WalkerSpec("discard_1", (730, 2735, 845, 3110), (620, 930), (1110, 930), (82, 190), 14.55, 15.20, 3.05, 0.25),
    WalkerSpec("discard_2", (875, 2680, 1025, 3100), (750, 923), (1215, 923), (86, 194), 14.70, 15.35, 3.15, 1.60),
    # Stop just before the incinerator's left wall so that stationary graphite
    # does not travel with the nearest figure.
    WalkerSpec(
        "discard_3",
        (1025, 2660, 1140, 3085),
        (880, 918),
        (1320, 918),
        (88, 196),
        14.85,
        15.50,
        3.25,
        2.90,
        ((1110, 2660, 1140, 2765),),
    ),
)


def rectify_photo() -> Image.Image:
    photo = ImageOps.exif_transpose(Image.open(SKETCH)).convert("RGB")
    return photo.transform(
        PAGE_SIZE,
        Image.Transform.QUAD,
        data=tuple(value for point in PAGE_QUAD for value in point),
        resample=Image.Resampling.BICUBIC,
    )


def prepare_asset(
    ink: Image.Image,
    crop: tuple[int, int, int, int],
    max_size: tuple[int, int],
    order: str,
    seed: int,
    amplitude: float,
    clear_boxes: tuple[tuple[int, int, int, int], ...] = (),
) -> tuple[tuple[Image.Image, Image.Image, Image.Image], np.ndarray]:
    source = ink.crop(crop).copy()
    if clear_boxes:
        alpha = source.getchannel("A")
        alpha_draw = ImageDraw.Draw(alpha)
        for box in clear_boxes:
            alpha_draw.rectangle(
                (box[0] - crop[0], box[1] - crop[1], box[2] - crop[0], box[3] - crop[1]),
                fill=0,
            )
        source.putalpha(alpha)
    fitted = shared.fit_piece(shared.trim_transparent(source, padding=8), max_size)
    return (
        established.boil_variants(fitted, seed=seed, amplitude=amplitude),
        shared.make_reveal_order(order, fitted),
    )


def prepare_assets(
    ink: Image.Image,
) -> tuple[dict[str, PreparedAsset], dict[str, PreparedAsset]]:
    pieces: dict[str, PreparedAsset] = {}
    for index, spec in enumerate(STATIC_SPECS):
        variants, order = prepare_asset(
            ink,
            spec.crop,
            spec.max_size,
            spec.order,
            600 + index * 17,
            spec.boil_amplitude,
            spec.clear_boxes,
        )
        size = variants[0].size
        pieces[spec.name] = PreparedAsset(
            variants,
            order,
            (round(spec.center[0] - size[0] / 2), round(spec.center[1] - size[1] / 2)),
            size,
        )

    walkers: dict[str, PreparedAsset] = {}
    for index, spec in enumerate(WALKER_SPECS):
        variants, order = prepare_asset(
            ink,
            spec.crop,
            spec.max_size,
            "down",
            900 + index * 19,
            0.28,
            spec.clear_boxes,
        )
        size = variants[0].size
        walkers[spec.name] = PreparedAsset(variants, order, (0, 0), size)
    return pieces, walkers


def smooth_progress(start: float, duration: float, time_s: float) -> float:
    return established.smoothstep(start, start + duration, time_s)


def panel_highlight(time_s: float, variant: int, opacity: float) -> Image.Image:
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    beats = (
        ((145, 138, 1775, 465), 5.55, 7.10),
        ((145, 500, 1780, 790), 10.65, 12.15),
        ((145, 790, 1790, 1038), 18.35, 20.55),
    )
    for box, start, end in beats:
        if start <= time_s <= end:
            local = (time_s - start) / max(end - start, 0.001)
            strength = math.sin(math.pi * local) * opacity
            draw = ImageDraw.Draw(image, "RGBA")
            jitter = (-2, 1, 2)[variant]
            draw.rounded_rectangle(
                (box[0] + jitter, box[1], box[2] - jitter, box[3]),
                radius=36,
                fill=shared.ACCENT_WASH + (round(42 * strength),),
                outline=shared.AI_TEAL + (round(110 * strength),),
                width=3,
            )
    return image


def flame_layer(time_s: float, opacity: float) -> Image.Image:
    """Draw a warm irregular fire behind the original graphite flame lines."""
    scale = 2
    layer = Image.new("RGBA", (WIDTH * scale, HEIGHT * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    phase = time_s * 8.5
    left, right, base = 1370 * scale, 1635 * scale, 1000 * scale
    centers = (1400, 1452, 1506, 1560, 1610)
    for index, center in enumerate(centers):
        sway = math.sin(phase + index * 1.41) * (7 + index % 2 * 3)
        height = 92 + 34 * (0.5 + 0.5 * math.sin(phase * 1.17 + index * 2.03))
        half_width = 34 + (index % 3) * 5
        x = (center + sway) * scale
        tip_y = (1000 - height) * scale
        points = [
            ((center - half_width) * scale, base),
            ((center - half_width * 0.72 + sway * 0.2) * scale, (base / scale - height * 0.43) * scale),
            (x, tip_y),
            ((center + half_width * 0.70 + sway * 0.15) * scale, (base / scale - height * 0.40) * scale),
            ((center + half_width) * scale, base),
        ]
        draw.polygon(points, fill=(235, 91, 42, round(112 * opacity)))

        inner_height = height * 0.62
        inner_width = half_width * 0.52
        inner = [
            ((center - inner_width) * scale, base),
            ((center - inner_width * 0.45 + sway * 0.15) * scale, (base / scale - inner_height * 0.40) * scale),
            ((center + sway * 0.55) * scale, (base / scale - inner_height) * scale),
            ((center + inner_width * 0.48 + sway * 0.12) * scale, (base / scale - inner_height * 0.42) * scale),
            ((center + inner_width) * scale, base),
        ]
        draw.polygon(inner, fill=(255, 194, 63, round(142 * opacity)))

    # Keep all added color inside the open front of the drawn incinerator.
    clip = Image.new("L", layer.size, 0)
    ImageDraw.Draw(clip).rectangle((left, 805 * scale, right, base), fill=255)
    alpha = np.asarray(layer.getchannel("A"), dtype=np.uint8)
    clipped = np.minimum(alpha, np.asarray(clip, dtype=np.uint8))
    layer.putalpha(Image.fromarray(clipped, "L"))
    return layer.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def moving_walker(
    asset: PreparedAsset,
    spec: WalkerSpec,
    variant: int,
    time_s: float,
    opacity: float,
) -> tuple[Image.Image, tuple[int, int]] | None:
    reveal = smooth_progress(spec.reveal_start, 0.62, time_s)
    if reveal <= 0.0:
        return None
    move = smooth_progress(spec.move_start, spec.move_duration, time_s)
    x = spec.start_center[0] + (spec.end_center[0] - spec.start_center[0]) * move
    y = spec.start_center[1] + (spec.end_center[1] - spec.start_center[1]) * move
    walking = 1.0 if spec.move_start <= time_s <= spec.move_start + spec.move_duration else 0.0
    cycle = (time_s - spec.move_start) * math.tau * 2.15 + spec.phase
    y -= abs(math.sin(cycle)) * 5.0 * walking
    angle = math.sin(cycle) * 1.35 * walking
    visible = shared.revealed_asset(asset.variants[variant], asset.reveal_order, reveal, opacity)
    if abs(angle) > 0.05:
        visible = visible.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    position = (round(x - visible.width / 2), round(y - visible.height / 2))
    return visible, position


def compose(
    frame_index: int,
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    pieces: dict[str, PreparedAsset],
    walkers: dict[str, PreparedAsset],
    fade: bool = True,
) -> Image.Image:
    time_s = frame_index / FPS
    variant = (frame_index // 5) % 3
    canvas = backgrounds[variant].copy()
    opacity = (
        1.0 - established.smoothstep(DURATION - 1.65, DURATION - 0.18, time_s)
        if fade
        else 1.0
    )
    canvas.alpha_composite(panel_highlight(time_s, variant, opacity))

    # Draw all static graphite except the incinerator first. Fire is colored
    # behind its original outline and flame strokes in the next pass.
    for spec in STATIC_SPECS:
        if spec.name == "incinerator":
            continue
        progress = smooth_progress(spec.start, spec.reveal_duration, time_s)
        if progress <= 0.0:
            continue
        asset = pieces[spec.name]
        visible = shared.revealed_asset(
            asset.variants[variant], asset.reveal_order, progress, opacity
        )
        canvas.alpha_composite(visible, asset.position)

    fire_progress = smooth_progress(13.85, 0.65, time_s) * opacity
    if fire_progress > 0.0:
        canvas.alpha_composite(flame_layer(time_s, fire_progress))

    incinerator_spec = next(spec for spec in STATIC_SPECS if spec.name == "incinerator")
    incinerator_progress = smooth_progress(
        incinerator_spec.start, incinerator_spec.reveal_duration, time_s
    )
    if incinerator_progress > 0.0:
        # The nearest source figure physically crosses the left wall in the
        # photograph. Its pixels are isolated as a walker above; bridge the
        # small resulting wall gap with the same restrained boiling graphite.
        wall = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        wall_x = 1347 + (-1, 0, 1)[variant]
        ImageDraw.Draw(wall).line(
            (wall_x, 923, wall_x, 1012),
            fill=shared.INK + (round(205 * incinerator_progress * opacity),),
            width=3,
        )
        canvas.alpha_composite(wall)
        asset = pieces["incinerator"]
        visible = shared.revealed_asset(
            asset.variants[variant], asset.reveal_order, incinerator_progress, opacity
        )
        canvas.alpha_composite(visible, asset.position)

    for spec in WALKER_SPECS:
        moving = moving_walker(walkers[spec.name], spec, variant, time_s, opacity)
        if moving is not None:
            visible, position = moving
            canvas.alpha_composite(visible, position)

    return canvas.convert("RGB")


def make_debug_assets(
    clean: Image.Image,
    pieces: dict[str, PreparedAsset],
    walkers: dict[str, PreparedAsset],
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
) -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    clean.save(SOURCE_DIR / "cleaned_page.png", optimize=True)

    extraction = clean.convert("RGBA")
    draw = ImageDraw.Draw(extraction, "RGBA")
    colors = ((46, 167, 154, 220), (228, 87, 46, 220), (116, 92, 160, 220))
    for index, spec in enumerate(STATIC_SPECS):
        draw.rectangle(spec.crop, outline=colors[index % len(colors)], width=5)
        draw.text((spec.crop[0] + 7, spec.crop[1] + 7), spec.name, fill=colors[index % len(colors)])
    for index, spec in enumerate(WALKER_SPECS):
        color = colors[(index + 1) % len(colors)]
        draw.rectangle(spec.crop, outline=color, width=4)
        draw.text((spec.crop[0] + 5, spec.crop[1] + 5), spec.name, fill=color)
    extraction.save(SOURCE_DIR / "extraction_map.png", optimize=True)

    grid = clean.convert("RGBA")
    grid_draw = ImageDraw.Draw(grid, "RGBA")
    for x in range(0, clean.width, 200):
        grid_draw.line((x, 0, x, clean.height), fill=(46, 167, 154, 92), width=2)
        grid_draw.text((x + 6, 8), str(x), fill=(31, 122, 113, 240))
    for y in range(0, clean.height, 200):
        grid_draw.line((0, y, clean.width, y), fill=(228, 87, 46, 92), width=2)
        grid_draw.text((8, y + 6), str(y), fill=(190, 67, 38, 240))
    grid.save(SOURCE_DIR / "coordinate_grid.png", optimize=True)

    for label, seconds in (
        ("departing_mid", 5.55),
        ("delegation", 6.65),
        ("synthesis", 11.80),
        ("discarding_mid", 16.85),
        ("incinerator", 19.35),
    ):
        frame = compose(round(seconds * FPS), backgrounds, pieces, walkers, fade=False)
        frame.save(SOURCE_DIR / f"keyframe_{label}.jpg", quality=95)
    compose(round(20.75 * FPS), backgrounds, pieces, walkers, fade=False).save(
        SOURCE_DIR / "layout_preview.png", quality=95
    )


def render_mp4(
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    pieces: dict[str, PreparedAsset],
    walkers: dict[str, PreparedAsset],
) -> Path:
    output = OUT_DIR / "multi_agent_orchestration.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-",
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    frames = round(DURATION * FPS)
    try:
        for index in range(frames):
            process.stdin.write(
                np.asarray(compose(index, backgrounds, pieces, walkers), dtype=np.uint8).tobytes()
            )
            if index % 120 == 0:
                print(f"multi_agent_orchestration: rendered {index:>3}/{frames} frames", flush=True)
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise subprocess.CalledProcessError(process.returncode, command)
    return output


def render_gif(mp4: Path) -> Path:
    output = OUT_DIR / "multi_agent_orchestration.gif"
    filter_graph = (
        "fps=10,scale=720:-1:flags=lanczos,split[s0][s1];"
        "[s0]palettegen=max_colors=56:stats_mode=diff[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle"
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-vf", filter_graph, "-loop", "0", str(output)],
        check=True,
    )
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-gif", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    page = rectify_photo()
    clean, ink = shared.isolate_pencil(page)
    pieces, walkers = prepare_assets(ink)
    backgrounds = established.make_notebook_backgrounds()
    make_debug_assets(clean, pieces, walkers, backgrounds)
    if args.prepare_only:
        print(f"wrote multi-agent source audits to {SOURCE_DIR}")
        return
    mp4 = render_mp4(backgrounds, pieces, walkers)
    established.probe(mp4)
    if not args.skip_gif:
        gif = render_gif(mp4)
        established.probe(gif)


if __name__ == "__main__":
    main()
