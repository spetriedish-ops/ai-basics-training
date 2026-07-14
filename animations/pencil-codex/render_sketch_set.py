#!/usr/bin/env python3
"""Render sketches 02–05 in the established pencil-on-notebook style.

Every visible handwritten mark is extracted from Sarah's photographed pages.
The renderer only corrects the page, lifts graphite onto transparency,
recomposes semantic regions for a 16:9 slide, reveals those original pixels in
writing order, and applies the same restrained paper/line boil as sketch 01.
"""

from __future__ import annotations

import argparse
import math
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy.ndimage import gaussian_filter

import render_agentic_loop as established
import personality_motifs as personality


HERE = Path(__file__).resolve().parent
SKETCH_DIR = HERE.parent / "assets" / "sketches"
SOURCE_DIR = HERE / "source"
OUT_DIR = HERE / "out"

WIDTH, HEIGHT = 1920, 1080
FPS = 30
PAPER = established.PAPER
INK = established.INK
AI_TEAL = established.AI_TEAL
ACCENT_WASH = established.ACCENT_WASH
RECTIFIED_PAGE_SIZE = (2400, 3200)


@dataclass(frozen=True)
class PieceSpec:
    name: str
    crop: tuple[int, int, int, int]
    center: tuple[int, int]
    max_size: tuple[int, int]
    start: float
    reveal_duration: float = 0.90
    order: str = "rows"
    group: str = ""
    boil_amplitude: float = 0.40


@dataclass(frozen=True)
class SceneSpec:
    key: str
    source: str
    page_quad: tuple[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]]
    duration: float
    pieces: tuple[PieceSpec, ...]
    focus_order: tuple[str, ...]
    focus_start: float
    focus_step: float


@dataclass
class PreparedPiece:
    spec: PieceSpec
    variants: tuple[Image.Image, Image.Image, Image.Image]
    reveal_order: np.ndarray
    position: tuple[int, int]
    size: tuple[int, int]


# The measured page quadrilaterals remove the phone-camera perspective before
# any handwriting is extracted. Piece crops are added after the audit-grid pass.
SCENES: dict[str, SceneSpec] = {
    "frontier_labs": SceneSpec(
        key="frontier_labs",
        source="02-frontier-labs-landscape-v2.jpeg",
        page_quad=((95, 135), (55, 3690), (2785, 3700), (2770, 160)),
        duration=22.5,
        pieces=(
            PieceSpec("title", (1040, 15, 1775, 215), (1050, 72), (560, 105), 0.30, 0.72, "left", "title"),
            PieceSpec("labs", (0, 205, 3130, 710), (1050, 225), (1700, 285), 1.05, 1.30, "rows", "labs", 0.28),
            PieceSpec("models_label", (0, 700, 3130, 835), (1050, 392), (1700, 78), 2.45, 0.62, "left", "models", 0.24),
            PieceSpec("models", (0, 825, 3130, 1375), (1050, 545), (1700, 300), 3.15, 1.45, "rows", "models", 0.28),
            PieceSpec("harnesses_label", (0, 1360, 3130, 1500), (1050, 714), (1700, 78), 4.72, 0.62, "left", "harnesses", 0.24),
            PieceSpec("harnesses", (0, 1480, 3130, 2070), (1050, 870), (1700, 285), 5.45, 1.50, "rows", "harnesses", 0.28),
            PieceSpec("api", (1220, 2050, 1640, 2290), (1050, 1015), (300, 80), 7.10, 0.62, "left", "api", 0.24),
            PieceSpec("open_weight_note", (0, 2150, 620, 2400), (390, 1018), (470, 88), 7.82, 0.72, "rows", "api", 0.24),
        ),
        focus_order=("labs", "models", "harnesses", "api"),
        focus_start=7.90,
        focus_step=3.00,
    ),
    "mcp_cli_api": SceneSpec(
        key="mcp_cli_api",
        source="03-mcp-cli-api-tools-v2.jpeg",
        page_quad=((150, 210), (145, 3655), (2770, 3650), (2755, 235)),
        duration=24.0,
        pieces=(
            PieceSpec("tools_title", (1410, 110, 1990, 315), (960, 65), (430, 108), 0.25, 0.78, "left", "title", 0.24),
            PieceSpec("mcp_heading", (300, 435, 900, 600), (360, 190), (430, 112), 1.15, 0.68, "left", "mcp", 0.24),
            PieceSpec("mcp_official", (0, 1050, 1450, 1640), (410, 455), (520, 300), 1.95, 2.10, "rows", "mcp", 0.28),
            PieceSpec("mcp_unofficial", (250, 1750, 1600, 2240), (410, 825), (520, 260), 4.30, 2.05, "rows", "mcp", 0.28),
            PieceSpec("cli_heading", (1270, 420, 1670, 590), (960, 190), (330, 112), 7.05, 0.68, "left", "cli", 0.24),
            PieceSpec("cli_agent", (1270, 625, 2035, 1000), (930, 420), (560, 280), 7.85, 1.55, "rows", "cli", 0.28),
            PieceSpec("cli_terminal", (1815, 980, 2050, 1245), (830, 680), (175, 195), 9.55, 0.90, "outline", "cli", 0.26),
            PieceSpec("api_heading", (2410, 535, 2870, 705), (1590, 190), (350, 112), 14.20, 0.68, "left", "api", 0.24),
            PieceSpec("api_rack", (2380, 835, 3200, 1380), (1590, 515), (590, 390), 15.05, 2.20, "rows", "api", 0.28),
        ),
        focus_order=("mcp", "cli", "api"),
        focus_start=4.00,
        focus_step=6.20,
    ),
    "harness_mind_map": SceneSpec(
        key="harness_mind_map",
        source="04-harness-mind-map-v2.jpeg",
        # Wider cross-page bounds retain both the full Model box and the
        # handwritten question at the physical bottom edge of the sheet.
        page_quad=((40, 140), (0, 3995), (2940, 3995), (3000, 150)),
        duration=22.0,
        pieces=(
            PieceSpec("harness_map", (20, 0, 3180, 2250), (960, 540), (1760, 1050), 0.35, 8.60, "harness_map", "map", 0.30),
        ),
        focus_order=("map",),
        focus_start=10.2,
        focus_step=2.20,
    ),
    "what_is_an_agent": SceneSpec(
        key="what_is_an_agent",
        source="05-what-is-an-agent.jpeg",
        page_quad=((210, 140), (135, 3850), (2885, 3855), (2860, 165)),
        duration=21.5,
        pieces=(
            PieceSpec("title", (990, 0, 2020, 230), (960, 105), (760, 140), 0.30, 0.85, "outline", "definition"),
            PieceSpec("definition", (760, 220, 2570, 465), (960, 245), (1240, 155), 1.22, 1.05, "left", "definition"),
            PieceSpec("general_column", (220, 500, 1820, 1640), (560, 700), (820, 590), 2.40, 3.15, "rows", "general"),
            PieceSpec("specialized_heading", (2020, 500, 3150, 700), (1445, 420), (750, 150), 6.15, 0.90, "left", "specialized"),
            PieceSpec("specialized_examples", (2100, 725, 3200, 2100), (1445, 740), (720, 570), 7.15, 1.75, "rows", "specialized"),
        ),
        focus_order=("definition", "general", "specialized"),
        focus_start=9.20,
        focus_step=3.30,
    ),
}


def rectify_photo(scene: SceneSpec) -> Image.Image:
    photo = ImageOps.exif_transpose(Image.open(SKETCH_DIR / scene.source)).convert("RGB")
    portrait_page = photo.transform(
        RECTIFIED_PAGE_SIZE,
        Image.Transform.QUAD,
        data=tuple(value for point in scene.page_quad for value in point),
        resample=Image.Resampling.BICUBIC,
    )
    # Sketches 02–05 were drawn with the physical paper turned landscape.
    return portrait_page.rotate(90, expand=True, resample=Image.Resampling.BICUBIC)


def isolate_pencil(page: Image.Image) -> tuple[Image.Image, Image.Image]:
    gray = np.asarray(page.convert("L"), dtype=np.float32)
    # Track medium-scale creases as illumination so they divide away; pencil
    # strokes are much narrower and remain in the normalized image.
    illumination = gaussian_filter(gray, sigma=28.0)
    normalized = np.clip(gray / np.maximum(illumination, 1.0) * 242.0, 0.0, 255.0)
    # A local contrast gate separates narrow graphite from folds and phone
    # shadows. Global darkness retains Sarah's pencil-pressure variation;
    # local support suppresses broad bands without turning paper grain to ink.
    global_darkness = np.clip((238.0 - normalized) / 78.0, 0.0, 1.0)
    detail_input = gaussian_filter(normalized, sigma=0.70)
    local_paper = gaussian_filter(detail_input, sigma=10.0)
    local_darkness = np.clip((local_paper - detail_input) / 42.0, 0.0, 1.0)
    support = np.clip((local_darkness - 0.018) / 0.11, 0.0, 1.0)
    darkness = global_darkness * support
    alpha = np.power(darkness, 0.82)
    # These later photos contain stronger fold shadows than sketch 01. A
    # slightly firmer floor removes broad gray bands while retaining graphite.
    alpha[alpha < 0.065] = 0.0
    alpha = gaussian_filter(alpha, sigma=0.32)

    rgba = np.zeros((*alpha.shape, 4), dtype=np.uint8)
    rgba[..., :3] = INK
    rgba[..., 3] = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
    ink = Image.fromarray(rgba, "RGBA")
    clean = Image.new("RGB", page.size, PAPER)
    clean.paste(ink, mask=ink.getchannel("A"))
    return clean, ink


def trim_transparent(image: Image.Image, padding: int = 9) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.point(lambda value: 255 if value >= 32 else 0).getbbox()
    if not bbox:
        raise ValueError("crop contains no pencil strokes")
    return image.crop(
        (
            max(0, bbox[0] - padding),
            max(0, bbox[1] - padding),
            min(image.width, bbox[2] + padding),
            min(image.height, bbox[3] + padding),
        )
    )


def fit_piece(image: Image.Image, max_size: tuple[int, int]) -> Image.Image:
    scale = min(max_size[0] / image.width, max_size[1] / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    return image.resize(size, Image.Resampling.LANCZOS)


def make_reveal_order(mode: str, image: Image.Image) -> np.ndarray:
    height, width = image.height, image.width
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    xn = xx / max(width - 1, 1)
    yn = yy / max(height - 1, 1)

    if mode == "left":
        return 0.06 + 0.90 * xn + 0.03 * yn
    if mode == "right":
        return 0.06 + 0.90 * (1.0 - xn) + 0.03 * yn
    if mode == "down":
        return 0.06 + 0.90 * yn + 0.03 * xn
    if mode == "up":
        return 0.06 + 0.90 * (1.0 - yn) + 0.03 * xn
    if mode == "radial":
        radius = np.sqrt((xn - 0.5) ** 2 + (yn - 0.5) ** 2)
        return np.clip(0.10 + 1.35 * radius, 0.0, 1.0)
    if mode == "outline":
        edge_distance = np.minimum.reduce((xn, 1.0 - xn, yn, 1.0 - yn))
        outline = edge_distance < 0.12
        outline_order = 0.04 + 0.30 * np.mod(
            np.arctan2(yn - 0.5, xn - 0.5) + math.pi, 2.0 * math.pi
        ) / (2.0 * math.pi)
        text_order = 0.30 + 0.54 * yn + 0.15 * xn
        return np.where(outline, outline_order, text_order)
    if mode == "harness_map":
        # Preserve the exact map as one layer (so spokes never misalign), but
        # reveal its original pixels in Sarah's intended teaching order.
        regions = np.full((height, width), 0.56 + 0.34 * yn + 0.08 * xn, dtype=np.float32)
        center = (xn > 0.33) & (xn < 0.63) & (yn > 0.34) & (yn < 0.66)
        model = (xn < 0.38) & (yn < 0.34)
        context = (xn < 0.39) & (yn >= 0.28)
        guardrails = (xn >= 0.32) & (xn < 0.73) & (yn < 0.45)
        guardrail_note = (xn >= 0.70) & (yn < 0.34)
        tools = (xn >= 0.61) & (yn >= 0.27) & (yn < 0.72)
        interaction = (xn >= 0.28) & (xn < 0.72) & (yn >= 0.62)
        skills = (xn >= 0.64) & (yn >= 0.60)
        regions[center] = 0.02 + 0.11 * xn[center] + 0.05 * yn[center]
        regions[model] = 0.16 + 0.10 * yn[model] + 0.05 * xn[model]
        regions[context] = 0.29 + 0.12 * yn[context] + 0.04 * xn[context]
        regions[guardrails] = 0.43 + 0.10 * yn[guardrails] + 0.04 * xn[guardrails]
        regions[guardrail_note] = 0.54 + 0.08 * yn[guardrail_note] + 0.03 * xn[guardrail_note]
        regions[tools] = 0.64 + 0.09 * yn[tools] + 0.03 * xn[tools]
        regions[interaction] = 0.76 + 0.08 * yn[interaction] + 0.03 * xn[interaction]
        regions[skills] = 0.87 + 0.08 * yn[skills] + 0.03 * xn[skills]
        return np.clip(regions, 0.0, 1.0)

    # Handwritten prose: move down the page while favoring left-to-right
    # movement inside each row. This is intentionally quick, not calligraphic.
    row_phase = np.mod(yn * 12.0, 1.0)
    return np.clip(0.05 + 0.82 * yn + 0.10 * xn + 0.03 * row_phase, 0.0, 1.0)


def prepare_pieces(scene: SceneSpec, ink: Image.Image) -> dict[str, PreparedPiece]:
    pieces: dict[str, PreparedPiece] = {}
    for index, spec in enumerate(scene.pieces):
        fitted = fit_piece(trim_transparent(ink.crop(spec.crop)), spec.max_size)
        position = (
            round(spec.center[0] - fitted.width / 2),
            round(spec.center[1] - fitted.height / 2),
        )
        pieces[spec.name] = PreparedPiece(
            spec=spec,
            variants=established.boil_variants(
                fitted, seed=101 + index * 13, amplitude=spec.boil_amplitude
            ),
            reveal_order=make_reveal_order(spec.order, fitted),
            position=position,
            size=fitted.size,
        )
    return pieces


def make_debug_assets(
    scene: SceneSpec,
    clean: Image.Image,
    pieces: dict[str, PreparedPiece],
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
) -> None:
    directory = SOURCE_DIR / scene.key
    directory.mkdir(parents=True, exist_ok=True)
    clean.save(directory / "cleaned_page.png", optimize=True)

    extraction = clean.convert("RGBA")
    draw = ImageDraw.Draw(extraction, "RGBA")
    colors = [(46, 167, 154, 220), (228, 87, 46, 220), (116, 92, 160, 220)]
    for index, spec in enumerate(scene.pieces):
        draw.rectangle(spec.crop, outline=colors[index % len(colors)], width=5)
        draw.text((spec.crop[0] + 8, spec.crop[1] + 8), spec.name, fill=colors[index % len(colors)])
    extraction.save(directory / "extraction_map.png", optimize=True)

    grid = clean.convert("RGBA")
    grid_draw = ImageDraw.Draw(grid, "RGBA")
    for x in range(0, clean.width, 200):
        grid_draw.line((x, 0, x, clean.height), fill=(46, 167, 154, 92), width=2)
        grid_draw.text((x + 6, 8), str(x), fill=(31, 122, 113, 240))
    for y in range(0, clean.height, 200):
        grid_draw.line((0, y, clean.width, y), fill=(228, 87, 46, 92), width=2)
        grid_draw.text((8, y + 6), str(y), fill=(190, 67, 38, 240))
    grid.save(directory / "coordinate_grid.png", optimize=True)

    layout = backgrounds[1].copy()
    for piece in pieces.values():
        layout.alpha_composite(piece.variants[1], piece.position)
    layout.convert("RGB").save(directory / "layout_preview.png", quality=94)

    personality_times = {
        "frontier_labs": (("intro", 1.00), ("lab", 9.20), ("model", 12.15), ("harness", 15.15), ("api", 18.20)),
        "mcp_cli_api": (("mcp", 5.95), ("cli", 12.35), ("api", 19.20)),
        "what_is_an_agent": (("intro", 1.10), ("definition", 10.80), ("general", 14.10), ("specialist", 17.45)),
    }
    for label, seconds in personality_times.get(scene.key, ()):
        render_frame(scene, round(seconds * FPS), backgrounds, pieces).save(
            directory / f"personality_{label}.jpg", quality=94
        )


def rough_highlight(size: tuple[int, int], variant: int, opacity: float) -> Image.Image:
    pad = 18
    image = Image.new("RGBA", (size[0] + pad * 2, size[1] + pad * 2), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    rng = np.random.default_rng(1701 + variant)
    inset = 5 + int(rng.integers(-1, 2))
    draw.rounded_rectangle(
        (inset, inset, image.width - inset, image.height - inset),
        radius=max(16, min(48, image.height // 5)),
        fill=ACCENT_WASH + (round(110 * opacity),),
        outline=AI_TEAL + (round(185 * opacity),),
        width=4,
    )
    return image.filter(ImageFilter.GaussianBlur(radius=0.35))


def active_group(scene: SceneSpec, time_s: float) -> tuple[str | None, float]:
    for index, group in enumerate(scene.focus_order):
        start = scene.focus_start + index * scene.focus_step
        end = start + scene.focus_step * 0.82
        if start <= time_s < end:
            local = (time_s - start) / (end - start)
            return group, math.sin(math.pi * local)
    return None, 0.0


def revealed_asset(
    asset: Image.Image, reveal_order: np.ndarray, progress: float, opacity: float
) -> Image.Image:
    out = asset.copy()
    base_alpha = np.asarray(asset.getchannel("A"), dtype=np.float32)
    edge = np.clip((progress - reveal_order) * 25.0 + 0.48, 0.0, 1.0)
    alpha = np.clip(base_alpha * edge * opacity, 0.0, 255.0).astype(np.uint8)
    out.putalpha(Image.fromarray(alpha, "L"))
    return out


def render_frame(
    scene: SceneSpec,
    frame_index: int,
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    pieces: dict[str, PreparedPiece],
) -> Image.Image:
    time_s = frame_index / FPS
    variant = (frame_index // 5) % 3
    canvas = backgrounds[variant].copy()
    global_opacity = 1.0 - established.smoothstep(
        scene.duration - 1.85, scene.duration - 0.22, time_s
    )
    active, strength = active_group(scene, time_s)

    for spec in scene.pieces:
        piece = pieces[spec.name]
        progress = max(0.0, min(1.0, (time_s - spec.start) / spec.reveal_duration))
        if progress <= 0.0:
            continue
        if active == spec.group and strength > 0.01:
            highlight = rough_highlight(piece.size, variant, strength * global_opacity)
            canvas.alpha_composite(
                highlight,
                (
                    round(spec.center[0] - highlight.width / 2),
                    round(spec.center[1] - highlight.height / 2),
                ),
            )
        asset = revealed_asset(piece.variants[variant], piece.reveal_order, progress, global_opacity)
        canvas.alpha_composite(asset, piece.position)

    if scene.key == "what_is_an_agent":
        personality.what_is_agent_overlay(canvas, time_s, variant, global_opacity)
    elif scene.key == "mcp_cli_api":
        personality.mcp_cli_api_overlay(canvas, time_s, variant, global_opacity)
    elif scene.key == "frontier_labs":
        personality.frontier_overlay(canvas, time_s, variant, global_opacity)

    return canvas.convert("RGB")


def render_mp4(
    scene: SceneSpec,
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    pieces: dict[str, PreparedPiece],
) -> Path:
    output = OUT_DIR / f"{scene.key}.mp4"
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
    frame_count = round(FPS * scene.duration)
    try:
        for index in range(frame_count):
            process.stdin.write(np.asarray(render_frame(scene, index, backgrounds, pieces), dtype=np.uint8).tobytes())
            if index % 120 == 0:
                print(f"{scene.key}: rendered {index:>3}/{frame_count} frames", flush=True)
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise subprocess.CalledProcessError(process.returncode, command)
    return output


def render_gif(mp4: Path, output: Path) -> None:
    """Create a compact wiki preview; MP4 remains the presentation master."""
    # The dense MCP page has more graphite change per frame and now holds its
    # larger character beats longer. Give that preview a slightly leaner
    # palette/raster so it still honors the wiki's 10 MB upload ceiling.
    compact = output.stem == "mcp_cli_api"
    fps = 9 if compact else 10
    width = 680 if compact else 720
    colors = 40 if compact else 48
    filter_graph = (
        f"fps={fps},scale={width}:-1:flags=lanczos,split[s0][s1];"
        f"[s0]palettegen=max_colors={colors}:stats_mode=diff[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", str(mp4),
            "-vf", filter_graph, "-loop", "0", str(output),
        ],
        check=True,
    )


def render_scene(scene: SceneSpec, prepare_only: bool, skip_gif: bool) -> None:
    if scene.key == "harness_mind_map":
        command = [sys.executable, str(HERE / "render_harness_mind_map.py")]
        if prepare_only:
            command.append("--prepare-only")
        if skip_gif:
            command.append("--skip-gif")
        subprocess.run(command, check=True)
        return

    page = rectify_photo(scene)
    clean, ink = isolate_pencil(page)
    pieces = prepare_pieces(scene, ink)
    backgrounds = established.make_notebook_backgrounds()
    make_debug_assets(scene, clean, pieces, backgrounds)
    if prepare_only:
        print(f"wrote {scene.key} source audits")
        return
    if not pieces:
        raise ValueError(f"{scene.key} has no configured pieces")
    mp4 = render_mp4(scene, backgrounds, pieces)
    established.probe(mp4)
    if not skip_gif:
        gif = OUT_DIR / f"{scene.key}.gif"
        render_gif(mp4, gif)
        established.probe(gif)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", choices=("all", *SCENES), default="all")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-gif", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scenes = SCENES.values() if args.scene == "all" else (SCENES[args.scene],)
    for scene in scenes:
        render_scene(scene, args.prepare_only, args.skip_gif)


if __name__ == "__main__":
    main()
