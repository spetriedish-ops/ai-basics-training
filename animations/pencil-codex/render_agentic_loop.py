#!/usr/bin/env python3
"""Render Sarah's photographed agentic-loop sketch as a slide-ready animation.

The source handwriting and shapes are extracted directly from the committed
photograph. This script corrects the page perspective and lighting, isolates
the pencil strokes, recomposes the original pieces for 16:9, reveals those
pixels in a fast hand-writing order, and adds a shared three-state boil to the
ink and crinkled notebook paper. It does not trace or regenerate the drawing.
"""

from __future__ import annotations

import argparse
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy.ndimage import gaussian_filter, map_coordinates

import personality_motifs as personality


HERE = Path(__file__).resolve().parent
SOURCE_PHOTO = HERE.parent / "assets" / "sketches" / "01-llm-harness-agentic-loop.jpeg"
SOURCE_DIR = HERE / "source"
OUT_DIR = HERE / "out"

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION = 23.5
FRAME_COUNT = round(FPS * DURATION)

PAPER = (250, 247, 239)
INK = (51, 50, 62)
AI_TEAL = (46, 167, 154)
ACCENT_WASH = (211, 237, 231)

# Page corners in the EXIF-corrected 3024x4032 photograph.  The transform
# removes the slight trapezoid caused by shooting the page at an angle.
PAGE_QUAD = (
    (185, 245),    # top left
    (170, 3748),   # bottom left
    (2855, 3815),  # bottom right
    (2850, 245),   # top right
)
PAGE_SIZE = (2400, 3200)


@dataclass(frozen=True)
class PieceSpec:
    name: str
    crop: tuple[int, int, int, int]
    center: tuple[int, int]
    max_size: tuple[int, int]
    start: float
    reveal_duration: float = 0.80


# Crops are measured on the rectified PAGE_SIZE image.  They intentionally
# include Sarah's original outlines and lettering as a single inseparable
# piece.  Spacing changes happen only when these pieces are composed.
PIECES = (
    PieceSpec("title", (800, 1945, 1465, 2080), (960, 112), (760, 150), 0.30, 0.78),
    PieceSpec("receive", (480, 2125, 950, 2245), (390, 350), (470, 190), 1.05, 0.78),
    PieceSpec("arrow_receive_reason", (945, 2140, 1110, 2215), (661, 346), (150, 95), 1.78, 0.40),
    PieceSpec("reason", (1090, 2085, 1490, 2285), (900, 338), (400, 220), 2.10, 0.82),
    PieceSpec("arrow_reason_tools", (1480, 2165, 1655, 2360), (1117, 448), (180, 165), 2.88, 0.42),
    PieceSpec("tools", (1450, 2325, 1950, 2600), (1380, 520), (490, 245), 3.22, 0.86),
    PieceSpec("arrow_tools_observe", (1480, 2595, 1680, 2725), (1275, 660), (180, 118), 4.03, 0.42),
    PieceSpec("observe", (1040, 2535, 1465, 2805), (1040, 770), (410, 235), 4.38, 0.84),
    PieceSpec("arrow_observe_repeat", (815, 2640, 1045, 2725), (752, 772), (215, 118), 5.17, 0.40),
    PieceSpec("repeat", (280, 2530, 840, 2790), (430, 760), (530, 270), 5.50, 0.88),
)

@dataclass
class PreparedPiece:
    spec: PieceSpec
    variants: tuple[Image.Image, Image.Image, Image.Image]
    reveal_order: np.ndarray
    position: tuple[int, int]
    size: tuple[int, int]


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    if edge0 == edge1:
        return float(x >= edge1)
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)


def rectify_photo() -> Image.Image:
    photo = ImageOps.exif_transpose(Image.open(SOURCE_PHOTO)).convert("RGB")
    return photo.transform(
        PAGE_SIZE,
        Image.Transform.QUAD,
        data=tuple(value for point in PAGE_QUAD for value in point),
        resample=Image.Resampling.BICUBIC,
    )


def isolate_pencil(page: Image.Image) -> tuple[Image.Image, Image.Image]:
    """Return a cleaned page preview and a transparent pencil-ink layer."""
    gray = np.asarray(page.convert("L"), dtype=np.float32)

    # Divide away broad shadows and glare while retaining local pencil texture.
    illumination = gaussian_filter(gray, sigma=46.0)
    normalized = np.clip(gray / np.maximum(illumination, 1.0) * 242.0, 0.0, 255.0)

    # A soft alpha ramp keeps graphite edges and pressure variation intact.
    darkness = np.clip((238.0 - normalized) / 78.0, 0.0, 1.0)
    alpha = np.power(darkness, 0.82)
    alpha[alpha < 0.055] = 0.0
    alpha = gaussian_filter(alpha, sigma=0.32)

    rgba = np.zeros((*alpha.shape, 4), dtype=np.uint8)
    rgba[..., :3] = INK
    rgba[..., 3] = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)
    ink = Image.fromarray(rgba, "RGBA")

    paper = Image.new("RGB", PAGE_SIZE, PAPER)
    paper.paste(ink, mask=ink.getchannel("A"))
    return paper, ink


def trim_transparent(image: Image.Image, padding: int = 10) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.point(lambda value: 255 if value >= 32 else 0).getbbox()
    if not bbox:
        raise ValueError("crop contains no pencil strokes")
    left = max(0, bbox[0] - padding)
    top = max(0, bbox[1] - padding)
    right = min(image.width, bbox[2] + padding)
    bottom = min(image.height, bbox[3] + padding)
    return image.crop((left, top, right, bottom))


def fit_piece(image: Image.Image, max_size: tuple[int, int]) -> Image.Image:
    scale = min(max_size[0] / image.width, max_size[1] / image.height)
    size = (max(1, round(image.width * scale)), max(1, round(image.height * scale)))
    return image.resize(size, Image.Resampling.LANCZOS)


def clean_piece_edges(name: str, image: Image.Image) -> Image.Image:
    """Mask neighboring connector fragments captured by rectangular crops."""
    alpha = np.asarray(image.getchannel("A"), dtype=np.uint8).copy()
    height, width = alpha.shape

    if name == "arrow_reason_tools":
        # The crop also catches a short section of the tools oval below the
        # arrowhead; the complete oval lives in the tools piece.
        alpha[round(height * 0.82) :, :] = 0
    elif name == "tools":
        # Remove the beginning of the outgoing connector below the oval.
        alpha[round(height * 0.82) :, :] = 0
    elif name == "observe":
        # Remove the outgoing connector stub at the far left of the oval.
        alpha[:, : round(width * 0.035)] = 0
    elif name == "repeat":
        # Remove a duplicate incoming arrowhead caught at the far-right edge.
        alpha[:, round(width * 0.975) :] = 0

    cleaned = image.copy()
    cleaned.putalpha(Image.fromarray(alpha, "L"))
    return cleaned


def warp_alpha(alpha: np.ndarray, seed: int, amplitude: float = 0.52) -> np.ndarray:
    """Create a sub-pixel redraw variation without changing the linework."""
    rng = np.random.default_rng(seed)
    h, w = alpha.shape
    raw_x = rng.normal(size=(h, w)).astype(np.float32)
    raw_y = rng.normal(size=(h, w)).astype(np.float32)
    dx = gaussian_filter(raw_x, sigma=15.0)
    dy = gaussian_filter(raw_y, sigma=15.0)
    dx /= max(float(np.std(dx)), 1e-6)
    dy /= max(float(np.std(dy)), 1e-6)
    dx *= amplitude
    dy *= amplitude
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    warped = map_coordinates(alpha, (yy + dy, xx + dx), order=1, mode="nearest")
    return np.clip(warped, 0.0, 255.0)


def boil_variants(
    image: Image.Image,
    seed: int,
    amplitude: float = 0.52,
) -> tuple[Image.Image, Image.Image, Image.Image]:
    base = np.asarray(image.getchannel("A"), dtype=np.float32)
    variants: list[Image.Image] = []
    for index in range(3):
        alpha = warp_alpha(base, seed * 101 + index * 17, amplitude=amplitude)
        # Tiny pressure changes read as graphite being redrawn, without flicker.
        alpha = np.clip(alpha * (0.98 + index * 0.018), 0.0, 255.0).astype(np.uint8)
        rgba = np.zeros((*alpha.shape, 4), dtype=np.uint8)
        rgba[..., :3] = INK
        rgba[..., 3] = alpha
        variants.append(Image.fromarray(rgba, "RGBA"))
    return tuple(variants)  # type: ignore[return-value]


def make_reveal_order(name: str, image: Image.Image) -> np.ndarray:
    """Approximate a quick human stroke order for the extracted raster ink.

    The original pixels never move or get retraced. This map only determines
    when each pixel becomes visible: outline first, handwriting by row, and
    arrows in their direction of travel.
    """
    height, width = image.height, image.width
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    xn = xx / max(width - 1, 1)
    yn = yy / max(height - 1, 1)

    if name == "title":
        # Lettering first, then Sarah's long underline from left to right.
        return np.where(yn < 0.63, 0.02 + 0.72 * xn, 0.72 + 0.27 * xn)

    if name == "arrow_receive_reason":
        return 0.04 + 0.92 * xn
    if name == "arrow_reason_tools":
        return 0.04 + 0.46 * xn + 0.47 * yn
    if name == "arrow_tools_observe":
        return 0.04 + 0.66 * yn + 0.27 * (1.0 - xn)
    if name == "arrow_observe_repeat":
        return 0.04 + 0.92 * (1.0 - xn)

    # Node outlines draw in one quick lap. Interior lettering follows in
    # reading order; two-line nodes write their upper row before the lower.
    rx = (xn - 0.5) / 0.50
    ry = (yn - 0.5) / 0.50
    radius = np.sqrt(rx * rx + ry * ry)
    # Keep far-right/left letters out of the outline phase; only the actual
    # outer ring should draw before the words begin.
    outline = radius > 0.88
    theta = np.mod(np.arctan2(ry, rx) + math.pi, 2.0 * math.pi) / (2.0 * math.pi)
    outline_order = 0.02 + 0.32 * theta

    if name == "receive":
        text_order = 0.30 + 0.68 * xn
    else:
        lower_row = (yn >= 0.50).astype(np.float32)
        text_order = 0.30 + 0.33 * lower_row + 0.34 * xn
    return np.where(outline, outline_order, text_order)


def prepare_pieces(ink: Image.Image) -> dict[str, PreparedPiece]:
    pieces: dict[str, PreparedPiece] = {}
    for index, spec in enumerate(PIECES):
        crop = trim_transparent(ink.crop(spec.crop))
        fitted = clean_piece_edges(spec.name, fit_piece(crop, spec.max_size))
        position = (
            round(spec.center[0] - fitted.width / 2),
            round(spec.center[1] - fitted.height / 2),
        )
        pieces[spec.name] = PreparedPiece(
            spec=spec,
            variants=boil_variants(
                fitted,
                seed=index + 11,
                amplitude=0.18 if spec.name == "repeat" else 0.52,
            ),
            reveal_order=make_reveal_order(spec.name, fitted),
            position=position,
            size=fitted.size,
        )
    return pieces


def make_notebook_backgrounds() -> tuple[Image.Image, Image.Image, Image.Image]:
    """Build three softly crumpled ruled-paper states for the 6 Hz boil."""
    rng = np.random.default_rng(20260713)
    yy, xx = np.mgrid[0:HEIGHT, 0:WIDTH].astype(np.float32)

    fine = gaussian_filter(rng.normal(size=(HEIGHT, WIDTH)), sigma=0.72)
    broad = gaussian_filter(rng.normal(size=(HEIGHT, WIDTH)), sigma=68.0)
    fine /= max(float(np.std(fine)), 1e-6)
    broad /= max(float(np.std(broad)), 1e-6)

    crease_specs = []
    for _ in range(13):
        angle = rng.uniform(-1.25, 1.25)
        offset = rng.uniform(-820.0, 820.0)
        width = rng.uniform(3.5, 10.0)
        amplitude = rng.uniform(2.8, 6.0)
        crease_specs.append((angle, offset, width, amplitude))

    backgrounds: list[Image.Image] = []
    for variant, boil_shift in enumerate((-1.15, 0.0, 1.05)):
        creases = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
        centered_x = xx - WIDTH / 2
        centered_y = yy - HEIGHT / 2
        for index, (angle, offset, width, amplitude) in enumerate(crease_specs):
            along = -centered_x * math.sin(angle) + centered_y * math.cos(angle)
            distance = (
                centered_x * math.cos(angle)
                + centered_y * math.sin(angle)
                - offset
                - boil_shift * (0.55 + 0.10 * (index % 3))
                + (2.5 + 0.75 * (index % 4))
                * np.sin(along / (145.0 + 17.0 * (index % 5)) + index * 0.9)
            )
            # Each fold gets a graphite-gray trough and a narrow paper-white
            # ridge, which reads as a real crinkle without harsh flicker.
            creases -= amplitude * np.exp(-((distance + width * 0.42) / width) ** 2)
            creases += amplitude * 0.72 * np.exp(-((distance - width * 0.46) / (width * 0.72)) ** 2)

        vignette = -1.3 * (
            ((xx - WIDTH / 2) / (WIDTH / 2)) ** 2
            + ((yy - HEIGHT / 2) / (HEIGHT / 2)) ** 2
        )
        texture = np.clip(fine * 0.48 + broad * 1.05 + creases + vignette, -9.0, 7.0)
        base = np.empty((HEIGHT, WIDTH, 3), dtype=np.float32)
        base[:] = PAPER
        base += texture[..., None]
        paper = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")

        ruling = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(ruling, "RGBA")
        phase = variant * 0.72
        for y0 in range(72, HEIGHT, 72):
            points = []
            for x in range(-20, WIDTH + 21, 24):
                wobble = 0.90 * math.sin(x / 154.0 + phase + y0 * 0.003)
                wobble += 0.35 * math.sin(x / 43.0 + phase * 0.7)
                points.append((x, y0 + wobble))
            draw.line(points, fill=(117, 177, 193, 92), width=2)

        margin_points = []
        for y in range(-20, HEIGHT + 21, 20):
            x = 148 + 1.0 * math.sin(y / 92.0 + phase)
            margin_points.append((x, y))
        draw.line(margin_points, fill=(213, 113, 111, 105), width=3)
        paper.alpha_composite(ruling)
        backgrounds.append(paper)

    return tuple(backgrounds)  # type: ignore[return-value]


def make_debug_assets(
    clean_page: Image.Image,
    ink: Image.Image,
    pieces: dict[str, PreparedPiece],
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
) -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    clean_page.save(SOURCE_DIR / "cleaned_page.png", optimize=True)

    extraction = clean_page.convert("RGBA")
    draw = ImageDraw.Draw(extraction, "RGBA")
    colors = [(46, 167, 154, 220), (228, 87, 46, 220), (116, 92, 160, 220)]
    for index, spec in enumerate(PIECES):
        draw.rectangle(spec.crop, outline=colors[index % len(colors)], width=5)
    extraction.save(SOURCE_DIR / "extraction_map.png", optimize=True)

    grid = clean_page.convert("RGBA")
    grid_draw = ImageDraw.Draw(grid, "RGBA")
    for x in range(0, PAGE_SIZE[0], 200):
        grid_draw.line((x, 0, x, PAGE_SIZE[1]), fill=(46, 167, 154, 90), width=2)
        grid_draw.text((x + 6, 8), str(x), fill=(31, 122, 113, 230))
    for y in range(0, PAGE_SIZE[1], 200):
        grid_draw.line((0, y, PAGE_SIZE[0], y), fill=(228, 87, 46, 90), width=2)
        grid_draw.text((8, y + 6), str(y), fill=(190, 67, 38, 230))
    grid.save(SOURCE_DIR / "coordinate_grid.png", optimize=True)

    layout = Image.new("RGBA", (WIDTH, HEIGHT), PAPER + (255,))
    for piece in pieces.values():
        layout.alpha_composite(piece.variants[1], piece.position)
    layout.convert("RGB").save(SOURCE_DIR / "layout_preview.png", quality=94)
    backgrounds[1].convert("RGB").save(SOURCE_DIR / "notebook_background_preview.jpg", quality=92)
    for label, seconds in (
        ("intro", 0.72),
        ("receive", 8.10),
        ("reason", 9.92),
        ("tools", 11.76),
        ("observe", 13.56),
        ("repeat", 15.34),
    ):
        render_frame(round(seconds * FPS), backgrounds, pieces).save(
            SOURCE_DIR / f"personality_{label}.jpg", quality=94
        )


def scaled_asset(asset: Image.Image, scale: float, opacity: float) -> Image.Image:
    if abs(scale - 1.0) < 0.001 and opacity >= 0.999:
        return asset
    size = (max(1, round(asset.width * scale)), max(1, round(asset.height * scale)))
    out = asset.resize(size, Image.Resampling.LANCZOS)
    if opacity < 0.999:
        alpha = out.getchannel("A").point(lambda value: round(value * opacity))
        out.putalpha(alpha)
    return out


def active_node(time_s: float) -> tuple[str | None, float]:
    """One deliberately paced lap with enough time to read each character beat."""
    beats = [
        ("receive", 7.25, 9.15),
        ("reason", 8.95, 10.85),
        ("tools", 10.65, 12.55),
        ("observe", 12.35, 14.25),
        ("repeat", 14.05, 16.05),
    ]
    for name, start, end in beats:
        if start <= time_s < end:
            local = (time_s - start) / (end - start)
            return name, math.sin(math.pi * local)
    return None, 0.0


def rough_rounded_highlight(size: tuple[int, int], variant: int) -> Image.Image:
    pad = 18
    w, h = size[0] + 2 * pad, size[1] + 2 * pad
    image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    rng = np.random.default_rng(901 + variant)
    inset = 5 + int(rng.integers(-1, 2))
    draw.rounded_rectangle(
        (inset, inset, w - inset, h - inset),
        radius=max(18, h // 3),
        fill=ACCENT_WASH + (126,),
        outline=AI_TEAL + (190,),
        width=4,
    )
    return image.filter(ImageFilter.GaussianBlur(radius=0.35))


def return_arrow_points() -> list[tuple[float, float]]:
    """Outer cycle arrow from REPEAT back to REASON / GENERATE."""
    segments = (
        (
            np.array([280.0, 650.0]),
            np.array([125.0, 620.0]),
            np.array([80.0, 525.0]),
            np.array([105.0, 430.0]),
        ),
        (
            np.array([105.0, 430.0]),
            np.array([55.0, 275.0]),
            np.array([230.0, 210.0]),
            np.array([700.0, 240.0]),
        ),
    )
    points: list[tuple[float, float]] = []
    for p0, p1, p2, p3 in segments:
        for t in np.linspace(0.0, 1.0, 46):
            point = (
                (1 - t) ** 3 * p0
                + 3 * (1 - t) ** 2 * t * p1
                + 3 * (1 - t) * t**2 * p2
                + t**3 * p3
            )
            points.append((float(point[0]), float(point[1])))
    return points


RETURN_POINTS = return_arrow_points()


def draw_return_arrow(canvas: Image.Image, progress: float, variant: int, opacity: float = 1.0) -> None:
    if progress <= 0.0 or opacity <= 0.0:
        return
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    count = max(2, round(len(RETURN_POINTS) * min(progress, 1.0)))
    pts = RETURN_POINTS[:count]
    rng = np.random.default_rng(441 + variant)
    jittered = [(x + rng.uniform(-1.0, 1.0), y + rng.uniform(-1.0, 1.0)) for x, y in pts]
    color = AI_TEAL + (round(205 * opacity),)
    draw.line(jittered, fill=color, width=5, joint="curve")
    if progress >= 0.98:
        x2, y2 = jittered[-1]
        x1, y1 = jittered[-7]
        angle = math.atan2(y2 - y1, x2 - x1)
        head = []
        for delta in (2.55, -2.55):
            head.append((x2 + 20 * math.cos(angle + delta), y2 + 20 * math.sin(angle + delta)))
        draw.line([head[0], (x2, y2), head[1]], fill=color, width=5, joint="curve")
    canvas.alpha_composite(layer)


def revealed_asset(
    asset: Image.Image,
    reveal_order: np.ndarray,
    progress: float,
    opacity: float,
) -> Image.Image:
    """Expose original graphite pixels behind a narrow moving pencil edge."""
    out = asset.copy()
    base_alpha = np.asarray(asset.getchannel("A"), dtype=np.float32)
    edge = np.clip((progress - reveal_order) * 26.0 + 0.48, 0.0, 1.0)
    alpha = np.clip(base_alpha * edge * opacity, 0.0, 255.0).astype(np.uint8)
    out.putalpha(Image.fromarray(alpha, "L"))
    return out


def composite_piece(
    canvas: Image.Image,
    piece: PreparedPiece,
    time_s: float,
    variant: int,
    highlight_strength: float,
    global_opacity: float,
) -> None:
    progress = max(0.0, min(1.0, (time_s - piece.spec.start) / piece.spec.reveal_duration))
    if progress <= 0.0:
        return
    scale = 1.0 + 0.025 * highlight_strength

    if highlight_strength > 0.01:
        highlight = rough_rounded_highlight(piece.size, variant)
        highlight_alpha = highlight.getchannel("A").point(
            lambda value: round(value * highlight_strength * global_opacity)
        )
        highlight.putalpha(highlight_alpha)
        hx = round(piece.spec.center[0] - highlight.width / 2)
        hy = round(piece.spec.center[1] - highlight.height / 2)
        canvas.alpha_composite(highlight, (hx, hy))

    written = revealed_asset(
        piece.variants[variant], piece.reveal_order, progress, global_opacity
    )
    asset = scaled_asset(written, scale=scale, opacity=1.0)
    x = round(piece.spec.center[0] - asset.width / 2)
    y = round(piece.spec.center[1] - asset.height / 2)
    canvas.alpha_composite(asset, (x, y))


def render_frame(
    frame_index: int,
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    pieces: dict[str, PreparedPiece],
) -> Image.Image:
    time_s = frame_index / FPS
    variant = (frame_index // 5) % 3
    canvas = backgrounds[variant].copy()

    # Fade the assembled drawing back to the same empty-paper opening.
    global_opacity = 1.0 - smoothstep(21.35, 23.25, time_s)
    active, strength = active_node(time_s)

    arrow_progress = smoothstep(0.0, 1.0, (time_s - 6.40) / 0.78)
    draw_return_arrow(canvas, arrow_progress, variant, global_opacity)

    for spec in PIECES:
        piece = pieces[spec.name]
        composite_piece(
            canvas,
            piece,
            time_s,
            variant,
            strength if active == spec.name else 0.0,
            global_opacity,
        )

    personality.agentic_loop_overlay(canvas, time_s, variant, global_opacity)

    return canvas.convert("RGB")


def render_mp4(
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    pieces: dict[str, PreparedPiece],
    output: Path,
) -> None:
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
    try:
        for index in range(FRAME_COUNT):
            frame = render_frame(index, backgrounds, pieces)
            process.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())
            if index % 90 == 0:
                print(f"rendered {index:>3}/{FRAME_COUNT} frames", flush=True)
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise subprocess.CalledProcessError(process.returncode, command)


def render_gif(mp4: Path, output: Path) -> None:
    # 800px/12fps/56 colors keeps the boiling pencil texture below 10 MB while
    # retaining enough resolution for a wiki embed.
    filter_graph = (
        "fps=12,scale=800:-1:flags=lanczos,split[s0][s1];"
        "[s0]palettegen=max_colors=56:stats_mode=diff[p];"
        "[s1][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error", "-i", str(mp4),
            "-vf", filter_graph, "-loop", "0", str(output),
        ],
        check=True,
    )


def probe(output: Path) -> None:
    subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=filename,duration,size",
            "-show_entries", "stream=codec_name,width,height,r_frame_rate",
            "-of", "default=noprint_wrappers=1", str(output),
        ],
        check=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="write cleaned source and extraction/layout previews without rendering video",
    )
    parser.add_argument("--skip-gif", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    page = rectify_photo()
    clean_page, ink = isolate_pencil(page)
    pieces = prepare_pieces(ink)
    backgrounds = make_notebook_backgrounds()
    make_debug_assets(clean_page, ink, pieces, backgrounds)
    if args.prepare_only:
        print(f"wrote source previews to {SOURCE_DIR}")
        return

    mp4 = OUT_DIR / "agentic_loop.mp4"
    gif = OUT_DIR / "agentic_loop.gif"
    render_mp4(backgrounds, pieces, mp4)
    probe(mp4)
    if not args.skip_gif:
        render_gif(mp4, gif)
        probe(gif)


if __name__ == "__main__":
    main()
