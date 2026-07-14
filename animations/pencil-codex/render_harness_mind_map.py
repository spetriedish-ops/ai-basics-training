#!/usr/bin/env python3
"""Render the Harness mind map as presenter-controlled teaching stages.

All visible lettering, boxes, spokes, and dots come from Sarah's photographed
page.  This renderer assigns those original graphite pixels to eight semantic
stages, then produces both a conventional timed animation and a browser player
whose next stage is triggered by a click or key press.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

import render_agentic_loop as established
import render_sketch_set as shared


HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "out"
SOURCE_DIR = HERE / "source" / "harness_mind_map"
INTERACTIVE_DIR = HERE / "interactive" / "harness_mind_map"
STAGE_DIR = INTERACTIVE_DIR / "stages"

WIDTH, HEIGHT = shared.WIDTH, shared.HEIGHT
FPS = shared.FPS
SCENE = shared.SCENES["harness_mind_map"]

# The page is slightly compressed vertically so the complete hand-drawn map,
# its long dotted relationship, and the separate question all fit on 16:9
# paper without cropping.  Every stage uses this one transform, so spokes meet
# the central ellipse exactly as they do in the photograph.
MAP_SIZE = (1490, 1000)
MAP_POSITION = (215, 8)
TOOLS_SHIFT_X = 100
QUESTION_CENTER = (1025, 1028)
QUESTION_MAX_SIZE = (1160, 62)

STAGE_NAMES = (
    "Harness",
    "Model",
    "Interaction / Application Layer",
    "Guardrails",
    "Tools",
    "Context",
    "Skills",
    "What is an agent?",
)

# Timed master: each stage gets a deliberate hold after its writing finishes.
# The longer first hold is the requested full pause after Harness.
TIMED_BEATS = (
    (0.25, 1.00),
    (3.00, 2.10),
    (5.75, 2.00),
    (8.40, 2.60),
    (11.65, 2.25),
    (14.55, 2.35),
    (17.55, 2.75),
    (20.95, 1.45),
)
TIMED_DURATION = 24.80


@dataclass
class StageLayer:
    name: str
    variants: tuple[Image.Image, Image.Image, Image.Image]
    reveal_order: np.ndarray
    position: tuple[int, int]


def blank_mask(size: tuple[int, int]) -> Image.Image:
    return Image.new("L", size, 0)


def rectangle_mask(
    size: tuple[int, int], box: tuple[int, int, int, int], padding: int = 0
) -> Image.Image:
    mask = blank_mask(size)
    ImageDraw.Draw(mask).rectangle(
        (box[0] - padding, box[1] - padding, box[2] + padding, box[3] + padding),
        fill=255,
    )
    return mask


def ellipse_mask(
    size: tuple[int, int], box: tuple[int, int, int, int], padding: int = 0
) -> Image.Image:
    mask = blank_mask(size)
    ImageDraw.Draw(mask).ellipse(
        (box[0] - padding, box[1] - padding, box[2] + padding, box[3] + padding),
        fill=255,
    )
    return mask


def polygon_mask(size: tuple[int, int], points: list[tuple[int, int]]) -> Image.Image:
    mask = blank_mask(size)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    return mask


def line_mask(
    size: tuple[int, int], points: list[tuple[int, int]], width: int = 34
) -> Image.Image:
    mask = blank_mask(size)
    ImageDraw.Draw(mask).line(points, fill=255, width=width, joint="curve")
    return mask


def combine_masks(*masks: Image.Image) -> Image.Image:
    result = np.zeros((masks[0].height, masks[0].width), dtype=np.uint8)
    for mask in masks:
        result = np.maximum(result, np.asarray(mask, dtype=np.uint8))
    return Image.fromarray(result, "L")


def normalized_coordinates(
    size: tuple[int, int], box: tuple[int, int, int, int]
) -> tuple[np.ndarray, np.ndarray]:
    yy, xx = np.mgrid[0 : size[1], 0 : size[0]].astype(np.float32)
    xn = np.clip((xx - box[0]) / max(box[2] - box[0], 1), 0.0, 1.0)
    yn = np.clip((yy - box[1]) / max(box[3] - box[1], 1), 0.0, 1.0)
    return xn, yn


def box_order(
    size: tuple[int, int], box: tuple[int, int, int, int]
) -> np.ndarray:
    """Draw a rectangular outline quickly, then write its label."""
    xn, yn = normalized_coordinates(size, box)
    edge_distance = np.minimum.reduce((xn, 1.0 - xn, yn, 1.0 - yn))
    top = yn <= np.minimum(0.16, edge_distance + 0.16)
    right = (xn >= 0.82) & ~top
    bottom = (yn >= 0.82) & ~top & ~right
    left = ~(top | right | bottom)
    perimeter = np.zeros_like(xn)
    perimeter[top] = 0.23 * xn[top]
    perimeter[right] = 0.23 + 0.20 * yn[right]
    perimeter[bottom] = 0.43 + 0.23 * (1.0 - xn[bottom])
    perimeter[left] = 0.66 + 0.16 * (1.0 - yn[left])
    outline = edge_distance < 0.13
    lettering = 0.38 + 0.56 * xn + 0.04 * yn
    return np.where(outline, 0.02 + 0.40 * perimeter / 0.82, lettering)


def ellipse_order(
    size: tuple[int, int], box: tuple[int, int, int, int]
) -> np.ndarray:
    """Lap the Harness ellipse before writing the word within it."""
    xn, yn = normalized_coordinates(size, box)
    rx = (xn - 0.5) / 0.5
    ry = (yn - 0.5) / 0.5
    radius = np.sqrt(rx * rx + ry * ry)
    theta = np.mod(np.arctan2(ry, rx) + math.pi, 2.0 * math.pi) / (2.0 * math.pi)
    outline = radius > 0.79
    return np.where(outline, 0.02 + 0.38 * theta, 0.42 + 0.54 * xn + 0.03 * yn)


def rows_order(
    size: tuple[int, int], box: tuple[int, int, int, int]
) -> np.ndarray:
    xn, yn = normalized_coordinates(size, box)
    row_phase = np.mod(yn * 12.0, 1.0)
    return np.clip(0.03 + 0.84 * yn + 0.10 * xn + 0.03 * row_phase, 0.0, 1.0)


def left_order(
    size: tuple[int, int], box: tuple[int, int, int, int]
) -> np.ndarray:
    xn, yn = normalized_coordinates(size, box)
    return np.clip(0.03 + 0.92 * xn + 0.03 * yn, 0.0, 1.0)


def line_order(
    size: tuple[int, int], start: tuple[int, int], end: tuple[int, int]
) -> np.ndarray:
    yy, xx = np.mgrid[0 : size[1], 0 : size[0]].astype(np.float32)
    vx = float(end[0] - start[0])
    vy = float(end[1] - start[1])
    denominator = max(vx * vx + vy * vy, 1.0)
    return np.clip(((xx - start[0]) * vx + (yy - start[1]) * vy) / denominator, 0.0, 1.0)


def dotted_order(size: tuple[int, int]) -> np.ndarray:
    """Follow the original dotted arc one graphite dot at a time."""
    controls = np.array(
        [
            (185, 1955),
            (330, 2075),
            (720, 2195),
            (1260, 2255),
            (1760, 2260),
            (1970, 2220),
            (2085, 2105),
            (2130, 1885),
            (2260, 1645),
        ],
        dtype=np.float32,
    )
    samples: list[np.ndarray] = []
    progress: list[float] = []
    segment_lengths = np.sqrt(((controls[1:] - controls[:-1]) ** 2).sum(axis=1))
    cumulative = np.concatenate(([0.0], np.cumsum(segment_lengths)))
    total = max(float(cumulative[-1]), 1.0)
    for index in range(len(controls) - 1):
        for local in np.linspace(0.0, 1.0, 36, endpoint=index == len(controls) - 2):
            samples.append(controls[index] * (1.0 - local) + controls[index + 1] * local)
            progress.append(float((cumulative[index] + local * segment_lengths[index]) / total))

    yy, xx = np.mgrid[0 : size[1], 0 : size[0]].astype(np.float32)
    best_distance = np.full((size[1], size[0]), np.inf, dtype=np.float32)
    best_progress = np.zeros((size[1], size[0]), dtype=np.float32)
    # Process a narrow path window at each sample rather than allocating one
    # enormous height x width x samples distance volume.
    radius = 96
    for point, value in zip(samples, progress):
        cx, cy = int(round(point[0])), int(round(point[1]))
        x0, x1 = max(0, cx - radius), min(size[0], cx + radius + 1)
        y0, y1 = max(0, cy - radius), min(size[1], cy + radius + 1)
        distance = (xx[y0:y1, x0:x1] - point[0]) ** 2 + (yy[y0:y1, x0:x1] - point[1]) ** 2
        update = distance < best_distance[y0:y1, x0:x1]
        best_distance[y0:y1, x0:x1][update] = distance[update]
        best_progress[y0:y1, x0:x1][update] = value
    return best_progress


def add_part(
    stage_masks: list[np.ndarray],
    stage_orders: list[np.ndarray],
    occupied: np.ndarray,
    stage_index: int,
    mask: Image.Image,
    local_order: np.ndarray,
    phase: tuple[float, float],
) -> None:
    region = (np.asarray(mask, dtype=np.uint8) > 0) & ~occupied
    stage_masks[stage_index][region] = 255
    stage_orders[stage_index][region] = phase[0] + (phase[1] - phase[0]) * local_order[region]
    occupied[region] = True


def build_stage_maps(size: tuple[int, int]) -> tuple[list[Image.Image], list[np.ndarray]]:
    """Assign the photographed map to the exact requested teaching order."""
    stage_masks = [np.zeros((size[1], size[0]), dtype=np.uint8) for _ in STAGE_NAMES]
    stage_orders = [np.ones((size[1], size[0]), dtype=np.float32) for _ in STAGE_NAMES]
    occupied = np.zeros((size[1], size[0]), dtype=bool)

    # 1. Harness: ellipse and interior word as one inseparable original unit.
    harness_box = (1045, 915, 1790, 1315)
    harness_mask = np.asarray(ellipse_mask(size, harness_box), dtype=np.uint8).copy()
    # The six spokes touch the ellipse in the source drawing.  Clip only the
    # pixels outside the ring here so the first beat is a clean, closed center
    # node; each spoke owns its pixels from the ring outward in a later beat.
    harness_mask[:946, 1425:1495] = 0          # Guardrails, above
    harness_mask[1020:1135, 1760:] = 0        # Tools, right
    harness_mask[1205:1325, 1745:] = 0        # Skills, lower right
    harness_mask[1275:1360, 1400:1475] = 0    # Interaction, below
    add_part(
        stage_masks,
        stage_orders,
        occupied,
        0,
        Image.fromarray(harness_mask, "L"),
        ellipse_order(size, harness_box),
        (0.02, 0.98),
    )

    # 2. Model box, its spoke, then model examples.
    model_box = (55, 45, 505, 225)
    add_part(stage_masks, stage_orders, occupied, 1, rectangle_mask(size, model_box, 8), box_order(size, model_box), (0.02, 0.31))
    add_part(stage_masks, stage_orders, occupied, 1, line_mask(size, [(500, 235), (1265, 975)], 82), line_order(size, (500, 235), (1265, 975)), (0.31, 0.55))
    model_examples = (45, 210, 620, 570)
    add_part(stage_masks, stage_orders, occupied, 1, rectangle_mask(size, model_examples), rows_order(size, model_examples), (0.55, 0.99))

    # 3. Interaction/application layer, connector, then examples.
    interaction_box = (1060, 1515, 2050, 1815)
    add_part(stage_masks, stage_orders, occupied, 2, rectangle_mask(size, interaction_box, 18), box_order(size, interaction_box), (0.02, 0.34))
    add_part(stage_masks, stage_orders, occupied, 2, line_mask(size, [(1435, 1515), (1435, 1275)], 74), line_order(size, (1435, 1515), (1435, 1275)), (0.34, 0.52))
    interaction_examples = (1050, 1770, 2080, 2080)
    add_part(stage_masks, stage_orders, occupied, 2, rectangle_mask(size, interaction_examples), rows_order(size, interaction_examples), (0.52, 0.99))

    # 4. Guardrails box and spoke, followed by the two diagonal explanations.
    guardrails_box = (1190, 80, 1935, 430)
    add_part(stage_masks, stage_orders, occupied, 3, rectangle_mask(size, guardrails_box, 18), box_order(size, guardrails_box), (0.02, 0.25))
    add_part(stage_masks, stage_orders, occupied, 3, line_mask(size, [(1460, 430), (1460, 945)], 82), line_order(size, (1460, 430), (1460, 945)), (0.25, 0.40))
    first_guardrail_note = combine_masks(
        polygon_mask(
            size,
            [(1500, 500), (2100, 430), (2205, 760), (2130, 800), (2080, 900), (2000, 1000), (1690, 1040)],
        ),
        rectangle_mask(size, (2120, 690, 2210, 770)),
    )
    add_part(stage_masks, stage_orders, occupied, 3, first_guardrail_note, rows_order(size, (1500, 430, 2220, 1040)), (0.40, 0.66))
    guardrail_arrow = line_mask(size, [(2180, 575), (2345, 445)], 92)
    add_part(
        stage_masks,
        stage_orders,
        occupied,
        3,
        guardrail_arrow,
        line_order(size, (2180, 575), (2345, 445)),
        (0.66, 0.75),
    )
    second_guardrail_note = polygon_mask(size, [(2190, 0), (3060, 0), (3060, 565), (2440, 565), (2140, 390)])
    add_part(stage_masks, stage_orders, occupied, 3, second_guardrail_note, rows_order(size, (2140, 0, 3060, 565)), (0.75, 0.99))

    # 5. Tools box, horizontal relationship to Harness, then both text columns.
    tools_box = (2240, 620, 2735, 825)
    add_part(stage_masks, stage_orders, occupied, 4, rectangle_mask(size, tools_box, 18), box_order(size, tools_box), (0.02, 0.24))
    add_part(stage_masks, stage_orders, occupied, 4, line_mask(size, [(2240, 1065), (1760, 1080)], 76), line_order(size, (2240, 1065), (1760, 1080)), (0.24, 0.40))
    # Leave breathing room above and below both handwritten columns. Their
    # visual move to the right happens after the common map transform so the
    # original graphite stays intact rather than being re-typeset.
    tools_text = (2140, 715, 3060, 1530)
    tools_text_mask = np.asarray(rectangle_mask(size, tools_text), dtype=np.uint8).copy()
    # The future Skills spoke crosses the lower-left corner of this generous
    # crop. Keep it out of Tools so it arrives only with the Skills stage.
    future_skills_spoke = np.asarray(
        line_mask(size, [(2280, 1590), (1735, 1245)], 132), dtype=np.uint8
    )
    tools_text_mask[future_skills_spoke > 0] = 0
    add_part(
        stage_masks,
        stage_orders,
        occupied,
        4,
        Image.fromarray(tools_text_mask, "L"),
        rows_order(size, tools_text),
        (0.40, 0.99),
    )

    # 6. Context box, connector, and the complete Context block (including the
    # textual “- Skills” bullet, but not its dotted relationship yet).
    context_box = (0, 680, 675, 930)
    add_part(stage_masks, stage_orders, occupied, 5, rectangle_mask(size, context_box, 18), box_order(size, context_box), (0.02, 0.22))
    add_part(stage_masks, stage_orders, occupied, 5, line_mask(size, [(650, 1160), (1075, 1160)], 76), line_order(size, (650, 1160), (1075, 1160)), (0.22, 0.38))
    context_text = (0, 900, 1080, 1942)
    add_part(stage_masks, stage_orders, occupied, 5, rectangle_mask(size, context_text), rows_order(size, context_text), (0.38, 0.99))

    # 7. Skills box, diagonal spoke, explanation, then the original dotted arc.
    skills_box = (2200, 1535, 2770, 1755)
    add_part(stage_masks, stage_orders, occupied, 6, rectangle_mask(size, skills_box, 18), box_order(size, skills_box), (0.02, 0.20))
    add_part(stage_masks, stage_orders, occupied, 6, line_mask(size, [(2280, 1590), (1735, 1245)], 118), line_order(size, (2280, 1590), (1735, 1245)), (0.20, 0.37))
    skills_text = (2140, 1680, 3060, 2225)
    add_part(stage_masks, stage_orders, occupied, 6, rectangle_mask(size, skills_text), rows_order(size, skills_text), (0.37, 0.70))
    dotted = line_mask(
        size,
        [
            (185, 1955),
            (330, 2075),
            (720, 2195),
            (1260, 2255),
            (1760, 2260),
            (1970, 2220),
            (2085, 2105),
            (2130, 1885),
            (2260, 1645),
        ],
        150,
    )
    dotted_array = np.asarray(dotted, dtype=np.uint8).copy()
    # The widened trace catches every faint graphite dot, but must stop before
    # the separate bottom question begins.
    dotted_array[2300:, :] = 0
    dotted = Image.fromarray(dotted_array, "L")
    add_part(stage_masks, stage_orders, occupied, 6, dotted, dotted_order(size), (0.70, 0.995))

    return [Image.fromarray(mask, "L") for mask in stage_masks], stage_orders


def make_variants_from_coverage(
    full_variants: tuple[Image.Image, Image.Image, Image.Image], coverage: Image.Image
) -> tuple[Image.Image, Image.Image, Image.Image]:
    coverage_array = np.asarray(coverage, dtype=np.float32) / 255.0
    variants: list[Image.Image] = []
    for full in full_variants:
        result = full.copy()
        alpha = np.asarray(full.getchannel("A"), dtype=np.float32)
        result.putalpha(Image.fromarray(np.clip(alpha * coverage_array, 0, 255).astype(np.uint8), "L"))
        variants.append(result)
    return tuple(variants)  # type: ignore[return-value]


def extract_question(rectified_ink: Image.Image) -> Image.Image:
    """Lift the exact bottom question retained by the corrected page bounds."""
    question = rectified_ink.crop((1020, 2280, 2550, 2382))
    return shared.fit_piece(shared.trim_transparent(question, padding=8), QUESTION_MAX_SIZE)


def prepare_tools_layer(
    full_variants: tuple[Image.Image, Image.Image, Image.Image],
    stage_mask: Image.Image,
    stage_order: np.ndarray,
    source_size: tuple[int, int],
) -> StageLayer:
    """Move the Tools cluster right while keeping its Harness spoke anchored.

    The handwritten box and both text columns translate together. The original
    horizontal graphite spoke is stretched from its Harness-side endpoint, so
    it still meets the center ellipse and reaches the relocated cluster.
    """
    source_coverage = np.asarray(stage_mask, dtype=np.uint8)
    connector_source = (
        (source_coverage > 0)
        & (stage_order >= 0.235)
        & (stage_order <= 0.405)
    )
    content_source = (source_coverage > 0) & ~connector_source

    connector_coverage = Image.fromarray(connector_source.astype(np.uint8) * 255, "L").resize(
        MAP_SIZE, Image.Resampling.LANCZOS
    )
    content_coverage = Image.fromarray(content_source.astype(np.uint8) * 255, "L").resize(
        MAP_SIZE, Image.Resampling.LANCZOS
    )
    order_image = Image.fromarray(stage_order.astype(np.float32), "F").resize(
        MAP_SIZE, Image.Resampling.BILINEAR
    )
    order_array = np.asarray(order_image, dtype=np.float32)

    output_size = (MAP_SIZE[0] + TOOLS_SHIFT_X, MAP_SIZE[1])
    output_variants: list[Image.Image] = []
    content_variants = make_variants_from_coverage(full_variants, content_coverage)
    connector_variants = make_variants_from_coverage(full_variants, connector_coverage)

    # Source connector bounds after the common 3200x2400 -> MAP_SIZE fit.
    sx = MAP_SIZE[0] / source_size[0]
    sy = MAP_SIZE[1] / source_size[1]
    connector_box = (
        round(1705 * sx),
        round(1000 * sy),
        round(2295 * sx),
        round(1145 * sy),
    )
    stretched_width = connector_box[2] - connector_box[0] + TOOLS_SHIFT_X

    for content_variant, connector_variant in zip(content_variants, connector_variants):
        result = Image.new("RGBA", output_size, (0, 0, 0, 0))
        result.alpha_composite(content_variant, (TOOLS_SHIFT_X, 0))
        connector_crop = connector_variant.crop(connector_box).resize(
            (stretched_width, connector_box[3] - connector_box[1]),
            Image.Resampling.BICUBIC,
        )
        result.alpha_composite(connector_crop, (connector_box[0], connector_box[1]))
        output_variants.append(result)

    output_order = np.ones((output_size[1], output_size[0]), dtype=np.float32)
    content_alpha = np.asarray(content_coverage, dtype=np.uint8) > 0
    translated_order = output_order[:, TOOLS_SHIFT_X : TOOLS_SHIFT_X + MAP_SIZE[0]]
    translated_order[content_alpha] = order_array[content_alpha]

    connector_order_crop = order_image.crop(connector_box).resize(
        (stretched_width, connector_box[3] - connector_box[1]),
        Image.Resampling.BILINEAR,
    )
    connector_alpha_crop = connector_coverage.crop(connector_box).resize(
        (stretched_width, connector_box[3] - connector_box[1]),
        Image.Resampling.LANCZOS,
    )
    connector_order_array = np.asarray(connector_order_crop, dtype=np.float32)
    connector_alpha = np.asarray(connector_alpha_crop, dtype=np.uint8) > 0
    order_region = output_order[
        connector_box[1] : connector_box[3],
        connector_box[0] : connector_box[0] + stretched_width,
    ]
    order_region[connector_alpha] = connector_order_array[connector_alpha]

    return StageLayer(
        STAGE_NAMES[4],
        tuple(output_variants),  # type: ignore[arg-type]
        output_order,
        MAP_POSITION,
    )


def prepare_layers() -> tuple[list[StageLayer], tuple[Image.Image, Image.Image, Image.Image], Image.Image, Image.Image]:
    page = shared.rectify_photo(SCENE)
    clean, ink = shared.isolate_pencil(page)
    stage_masks, stage_orders = build_stage_maps(page.size)

    fitted_map = ink.resize(MAP_SIZE, Image.Resampling.LANCZOS)
    full_variants = established.boil_variants(fitted_map, seed=404, amplitude=0.30)
    layers: list[StageLayer] = []
    for index in range(7):
        if index == 4:
            layers.append(
                prepare_tools_layer(
                    full_variants,
                    stage_masks[index],
                    stage_orders[index],
                    page.size,
                )
            )
            continue
        coverage = stage_masks[index].resize(MAP_SIZE, Image.Resampling.LANCZOS)
        order_image = Image.fromarray(stage_orders[index].astype(np.float32), "F").resize(
            MAP_SIZE, Image.Resampling.BILINEAR
        )
        layers.append(
            StageLayer(
                STAGE_NAMES[index],
                make_variants_from_coverage(full_variants, coverage),
                np.asarray(order_image, dtype=np.float32),
                MAP_POSITION,
            )
        )

    question = extract_question(ink)
    question_position = (
        round(QUESTION_CENTER[0] - question.width / 2),
        round(QUESTION_CENTER[1] - question.height / 2),
    )
    question_order = shared.make_reveal_order("left", question)
    layers.append(
        StageLayer(
            STAGE_NAMES[7],
            established.boil_variants(question, seed=808, amplitude=0.24),
            question_order,
            question_position,
        )
    )
    return layers, established.make_notebook_backgrounds(), clean, question


def revealed(layer: StageLayer, variant: int, progress: float, opacity: float = 1.0) -> Image.Image:
    return shared.revealed_asset(layer.variants[variant], layer.reveal_order, progress, opacity)


def compose(
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    layers: list[StageLayer],
    frame_index: int,
    progress: list[float],
    opacity: float = 1.0,
) -> Image.Image:
    variant = (frame_index // 5) % 3
    canvas = backgrounds[variant].copy()
    for layer, amount in zip(layers, progress):
        if amount <= 0.0:
            continue
        canvas.alpha_composite(revealed(layer, variant, amount, opacity), layer.position)
    return canvas.convert("RGB")


def make_debug_assets(
    layers: list[StageLayer],
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    clean: Image.Image,
    question: Image.Image,
) -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    clean.save(SOURCE_DIR / "cleaned_page.png", optimize=True)
    question.save(SOURCE_DIR / "question_extraction.png", optimize=True)

    cumulative = backgrounds[1].copy()
    for index, layer in enumerate(layers):
        cumulative.alpha_composite(layer.variants[1], layer.position)
        cumulative.convert("RGB").save(
            SOURCE_DIR / f"stage_{index + 1:02d}_{file_slug(layer.name).replace('-', '_')}.jpg",
            quality=94,
        )
    cumulative.convert("RGB").save(SOURCE_DIR / "layout_preview.png", quality=95)


def encode_frames(output: Path, frames: int, frame_builder) -> None:
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
        for index in range(frames):
            process.stdin.write(np.asarray(frame_builder(index), dtype=np.uint8).tobytes())
            if index % 120 == 0:
                print(f"{output.name}: rendered {index:>3}/{frames} frames", flush=True)
    finally:
        process.stdin.close()
    if process.wait() != 0:
        raise subprocess.CalledProcessError(process.returncode, command)


def render_timed(
    layers: list[StageLayer], backgrounds: tuple[Image.Image, Image.Image, Image.Image]
) -> Path:
    output = OUT_DIR / "harness_mind_map.mp4"
    frames = round(TIMED_DURATION * FPS)

    def frame_builder(index: int) -> Image.Image:
        time_s = index / FPS
        progress = [
            np.clip((time_s - start) / duration, 0.0, 1.0)
            for start, duration in TIMED_BEATS
        ]
        opacity = 1.0 - established.smoothstep(23.15, 24.65, time_s)
        return compose(backgrounds, layers, index, progress, opacity)

    encode_frames(output, frames, frame_builder)
    return output


def interactive_duration(stage_index: int) -> tuple[float, float]:
    draw = (1.20, 1.75, 1.65, 2.05, 1.85, 1.95, 2.25, 1.35)[stage_index]
    return draw, 0.70


def file_slug(label: str) -> str:
    return "-".join(
        part for part in label.lower().replace("/", " ").replace("?", "").split() if part
    )


def render_interactive_clips(
    layers: list[StageLayer], backgrounds: tuple[Image.Image, Image.Image, Image.Image]
) -> list[Path]:
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for stage_index in range(len(layers)):
        draw_duration, hold_duration = interactive_duration(stage_index)
        duration = draw_duration + hold_duration
        frames = round(duration * FPS)
        output = STAGE_DIR / f"{stage_index + 1:02d}-{file_slug(layers[stage_index].name)}.mp4"

        def frame_builder(index: int, current: int = stage_index, draw: float = draw_duration) -> Image.Image:
            progress = [1.0 if item < current else 0.0 for item in range(len(layers))]
            progress[current] = float(np.clip((index / FPS) / draw, 0.0, 1.0))
            return compose(backgrounds, layers, index, progress)

        encode_frames(output, frames, frame_builder)
        outputs.append(output)
    return outputs


def write_interactive_player(clips: list[Path]) -> None:
    INTERACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    manifest = [
        {"label": STAGE_NAMES[index], "src": f"stages/{clip.name}"}
        for index, clip in enumerate(clips)
    ]
    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
  <title>Harness mind map — presenter player</title>
  <style>
    :root {{ color-scheme: light; }}
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; width: 100%; height: 100%; overflow: hidden; background: #111; }}
    body {{ display: grid; place-items: center; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
    .stage {{ position: relative; width: min(100vw, calc(100vh * 16 / 9)); aspect-ratio: 16 / 9; background: #faf7ef; cursor: pointer; }}
    video {{ display: block; width: 100%; height: 100%; object-fit: contain; }}
    .hud {{ position: absolute; right: 1.15rem; bottom: 1rem; display: grid; gap: .35rem; justify-items: end; color: #34323e; text-shadow: 0 1px rgba(250,247,239,.9); transition: opacity .18s; pointer-events: none; }}
    .hud.hidden {{ opacity: 0; }}
    .count {{ padding: .34rem .55rem; border: 1px solid rgba(52,50,62,.28); border-radius: 999px; background: rgba(250,247,239,.76); font-size: clamp(.66rem, 1.05vw, .94rem); }}
    .hint {{ font-size: clamp(.58rem, .88vw, .80rem); opacity: .72; }}
    .stage:focus-visible {{ outline: 4px solid #2ea79a; outline-offset: -4px; }}
  </style>
</head>
<body>
  <main class=\"stage\" tabindex=\"0\" role=\"button\" aria-label=\"Advance Harness mind map animation\">
    <video muted playsinline preload=\"auto\"></video>
    <div class=\"hud\">
      <div class=\"count\" aria-live=\"polite\"></div>
      <div class=\"hint\">click / space / → next · ← back · H hide</div>
    </div>
  </main>
  <script>
    const stages = {json.dumps(manifest)};
    const HOLD_SECONDS = 0.52;
    const shell = document.querySelector('.stage');
    const video = document.querySelector('video');
    const hud = document.querySelector('.hud');
    const count = document.querySelector('.count');
    let index = 0;
    let holding = false;
    let holdTimer = 0;

    function label() {{
      count.textContent = `${{index + 1}} / ${{stages.length}} · ${{stages[index].label}}`;
    }}

    function loadStage(next, playFromStart = true) {{
      index = Math.max(0, Math.min(stages.length - 1, next));
      holding = false;
      window.clearTimeout(holdTimer);
      label();
      video.src = stages[index].src;
      video.load();
      const start = () => {{
        const loopStart = Math.max(0, video.duration - HOLD_SECONDS);
        if (!playFromStart) {{
          holding = true;
          video.currentTime = loopStart;
        }} else {{
          // Background WebViews may throttle interval/timeupdate events enough
          // to skip the hold boundary. This one-shot arms the final loop at
          // the media-clock moment even when those recurring events are sparse.
          holdTimer = window.setTimeout(() => {{
            holding = true;
            if (video.currentTime < loopStart - 0.08) video.currentTime = loopStart;
          }}, Math.max(0, (loopStart - 0.04) * 1000));
        }}
        video.play().catch(() => {{}});
      }};
      video.addEventListener('loadedmetadata', start, {{ once: true }});
    }}

    function advance() {{
      if (index < stages.length - 1) loadStage(index + 1);
    }}

    function back() {{
      if (index > 0) loadStage(index - 1, false);
    }}

    video.addEventListener('timeupdate', () => {{
      if (!video.duration) return;
      const loopStart = Math.max(0, video.duration - HOLD_SECONDS);
      if (!holding && video.currentTime >= loopStart) holding = true;
      if (holding && video.currentTime >= video.duration - 0.08) {{
        video.currentTime = loopStart;
      }}
    }});
    video.addEventListener('ended', () => {{
      holding = true;
      const loopStart = Math.max(0, video.duration - HOLD_SECONDS);
      video.currentTime = loopStart;
      video.play().catch(() => {{}});
    }});
    // WebViews can emit timeupdate too sparsely to catch the last frame before
    // `ended`. A tiny presenter-only poll keeps the hold inside the completed
    // 0.52-second boil segment without replaying the drawing.
    window.setInterval(() => {{
      if (!video.duration) return;
      const loopStart = Math.max(0, video.duration - HOLD_SECONDS);
      if (!holding && video.currentTime >= loopStart) holding = true;
      if (holding && (
        video.currentTime >= video.duration - 0.14 ||
        video.currentTime < loopStart - 0.08
      )) video.currentTime = loopStart;
    }}, 40);
    shell.addEventListener('click', advance);
    window.addEventListener('keydown', (event) => {{
      if (event.key === ' ' || event.key === 'ArrowRight' || event.key === 'Enter') {{ event.preventDefault(); advance(); }}
      if (event.key === 'ArrowLeft') {{ event.preventDefault(); back(); }}
      if (event.key.toLowerCase() === 'h') hud.classList.toggle('hidden');
      if (event.key.toLowerCase() === 'r') loadStage(0);
    }});
    loadStage(0);
    shell.focus();
  </script>
</body>
</html>
"""
    (INTERACTIVE_DIR / "index.html").write_text(html, encoding="utf-8")
    (INTERACTIVE_DIR / "manifest.json").write_text(
        json.dumps({"stages": manifest, "controls": ["click", "Space", "ArrowRight", "ArrowLeft", "H", "R"]}, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-gif", action="store_true")
    parser.add_argument("--skip-interactive", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    layers, backgrounds, clean, question = prepare_layers()
    make_debug_assets(layers, backgrounds, clean, question)
    if args.prepare_only:
        print(f"wrote Harness source audits to {SOURCE_DIR}")
        return

    timed = render_timed(layers, backgrounds)
    established.probe(timed)
    if not args.skip_gif:
        gif = OUT_DIR / "harness_mind_map.gif"
        shared.render_gif(timed, gif)
        established.probe(gif)

    if not args.skip_interactive:
        clips = render_interactive_clips(layers, backgrounds)
        write_interactive_player(clips)
        for clip in clips:
            established.probe(clip)


if __name__ == "__main__":
    main()
