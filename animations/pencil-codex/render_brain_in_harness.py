#!/usr/bin/env python3
"""Render the two-stage "LLM brain in a harness" pencil animation.

Sarah's comically large-headed stick figure is lifted from her photographed
drawing. The brain is redrawn from the supplied reference as graphite linework
so it belongs to the same notebook-paper world as the other pencil artifacts.
The interactive player is intentionally click-gated: stage one draws and holds
the brain; stage two draws the face and body around it only after advancement.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

import render_agentic_loop as established
import render_sketch_set as shared


HERE = Path(__file__).resolve().parent
SKETCH_DIR = HERE.parent / "assets" / "sketches"
PERSON_SOURCE = SKETCH_DIR / "06-brain-in-harness-person.jpeg"
BRAIN_REFERENCE = SKETCH_DIR / "06-brain-reference.jpg"
SOURCE_DIR = HERE / "source" / "brain_in_harness"
OUT_DIR = HERE / "out"
INTERACTIVE_DIR = HERE / "interactive" / "brain_in_harness"
STAGE_DIR = INTERACTIVE_DIR / "stages"
HOLD_DIR = INTERACTIVE_DIR / "holds"

WIDTH, HEIGHT = shared.WIDTH, shared.HEIGHT
FPS = shared.FPS
DURATION = 12.0
PAGE_SIZE = (1800, 2400)
PAGE_QUAD = ((20, 25), (15, 3790), (2835, 3800), (2830, 20))


@dataclass
class PreparedLayer:
    variants: tuple[Image.Image, Image.Image, Image.Image]
    reveal_order: np.ndarray
    position: tuple[int, int]
    size: tuple[int, int]


def cubic(
    p0: tuple[float, float],
    p1: tuple[float, float],
    p2: tuple[float, float],
    p3: tuple[float, float],
    steps: int = 28,
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for t in np.linspace(0.0, 1.0, steps):
        point = (
            (1 - t) ** 3 * np.asarray(p0)
            + 3 * (1 - t) ** 2 * t * np.asarray(p1)
            + 3 * (1 - t) * t**2 * np.asarray(p2)
            + t**3 * np.asarray(p3)
        )
        points.append((float(point[0]), float(point[1])))
    return points


def draw_graphite_path(
    layer: Image.Image,
    points: list[tuple[float, float]],
    width: int = 9,
    alpha: int = 226,
) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    draw.line(points, fill=shared.INK + (alpha,), width=width, joint="curve")
    # A lighter offset pass gives the clean reference icon a pencil-pressure
    # texture before the normal boil warp is applied.
    draw.line(
        [(x + 1.2, y - 0.7) for x, y in points],
        fill=shared.INK + (62,),
        width=max(2, width // 3),
        joint="curve",
    )


def make_brain_asset() -> Image.Image:
    """Redraw the supplied brain reference as loose graphite linework."""
    image = Image.new("RGBA", (590, 405), (0, 0, 0, 0))

    outline_segments = (
        ((115, 230), (66, 218), (72, 167), (111, 162)),
        ((111, 162), (72, 125), (111, 78), (160, 96)),
        ((160, 96), (166, 51), (227, 43), (250, 78)),
        ((250, 78), (276, 34), (340, 37), (355, 83)),
        ((355, 83), (397, 48), (458, 66), (451, 111)),
        ((451, 111), (499, 99), (531, 136), (512, 170)),
        ((512, 170), (560, 184), (554, 235), (515, 242)),
        ((515, 242), (518, 294), (463, 312), (431, 285)),
        ((431, 285), (416, 327), (350, 333), (325, 294)),
        ((325, 294), (293, 332), (228, 325), (216, 286)),
        ((216, 286), (184, 316), (129, 294), (137, 258)),
        ((137, 258), (102, 274), (76, 247), (115, 230)),
    )
    outline: list[tuple[float, float]] = []
    for index, segment in enumerate(outline_segments):
        points = cubic(*segment)
        outline.extend(points if index == 0 else points[1:])
    draw_graphite_path(image, outline, width=6)

    folds = (
        ((113, 165), (145, 151), (144, 116), (183, 120)),
        ((183, 120), (203, 89), (246, 98), (248, 126)),
        ((248, 126), (282, 140), (301, 102), (334, 112)),
        ((334, 112), (369, 88), (407, 106), (415, 135)),
        ((148, 222), (170, 184), (217, 191), (225, 220)),
        ((225, 220), (252, 189), (296, 194), (303, 226)),
        ((303, 226), (335, 196), (378, 199), (389, 229)),
        ((389, 229), (414, 251), (448, 244), (466, 222)),
        ((220, 286), (233, 251), (266, 244), (293, 259)),
        ((325, 293), (343, 258), (383, 253), (408, 278)),
    )
    for segment in folds:
        draw_graphite_path(image, cubic(*segment), width=5, alpha=214)
    return shared.trim_transparent(image, padding=14)


def rectify_person_photo() -> Image.Image:
    photo = ImageOps.exif_transpose(Image.open(PERSON_SOURCE)).convert("RGB")
    return photo.transform(
        PAGE_SIZE,
        Image.Transform.QUAD,
        data=tuple(value for point in PAGE_QUAD for value in point),
        resample=Image.Resampling.BICUBIC,
    )


def strengthen_graphite(image: Image.Image, factor: float = 1.75) -> Image.Image:
    alpha = np.asarray(image.getchannel("A"), dtype=np.float32)
    # Sarah's light pencil lines are strong local features, while the phone
    # photo's page grain lives almost entirely in the low-alpha tail.
    alpha[alpha < 50.0] = 0.0
    strengthened = np.clip(alpha * factor, 0.0, 255.0).astype(np.uint8)
    result = image.copy()
    result.putalpha(Image.fromarray(strengthened, "L"))
    return result


def prepare_layer(
    image: Image.Image,
    center: tuple[int, int],
    max_size: tuple[int, int],
    order: str,
    seed: int,
    amplitude: float = 0.42,
) -> PreparedLayer:
    fitted = shared.fit_piece(shared.trim_transparent(image), max_size)
    position = (
        round(center[0] - fitted.width / 2),
        round(center[1] - fitted.height / 2),
    )
    return PreparedLayer(
        variants=established.boil_variants(fitted, seed=seed, amplitude=amplitude),
        reveal_order=shared.make_reveal_order(order, fitted),
        position=position,
        size=fitted.size,
    )


def prepare_layers() -> tuple[
    PreparedLayer,
    PreparedLayer,
    PreparedLayer,
    tuple[Image.Image, Image.Image, Image.Image],
    Image.Image,
]:
    page = rectify_person_photo()
    clean, ink = established.isolate_pencil(page)
    ink = strengthen_graphite(ink)

    # The large head and the body are independent layers so the head/face can
    # draw around the already-visible brain before the limbs appear.
    # Stop the head crop at the jawline. The original portrait's neck belongs
    # only to the body layer; including it twice creates a line through the
    # face once the two pieces are recomposed for landscape.
    head_source = ink.crop((390, 90, 1410, 930))
    # Begin the body at the same jawline boundary. Starting a little higher
    # reintroduced a sliver of the lower face beside the neck after scaling.
    body_source = ink.crop((430, 930, 1420, 2380))

    brain = prepare_layer(
        make_brain_asset(), center=(975, 270), max_size=(380, 220), order="rows", seed=607
    )
    head = prepare_layer(
        head_source, center=(960, 365), max_size=(680, 575), order="outline", seed=619
    )
    body = prepare_layer(
        body_source, center=(960, 850), max_size=(500, 440), order="down", seed=631
    )
    return brain, head, body, established.make_notebook_backgrounds(), clean


def add_brain_focus(canvas: Image.Image, brain: PreparedLayer, variant: int, opacity: float) -> None:
    if opacity <= 0.0:
        return
    pad_x, pad_y = 32, 24
    layer = Image.new(
        "RGBA", (brain.size[0] + pad_x * 2, brain.size[1] + pad_y * 2), (0, 0, 0, 0)
    )
    draw = ImageDraw.Draw(layer, "RGBA")
    wobble = (-2, 0, 2)[variant]
    draw.ellipse(
        (7 + wobble, 7, layer.width - 7 + wobble, layer.height - 7),
        fill=shared.ACCENT_WASH + (round(62 * opacity),),
        outline=shared.AI_TEAL + (round(92 * opacity),),
        width=3,
    )
    canvas.alpha_composite(
        layer,
        (brain.position[0] - pad_x, brain.position[1] - pad_y),
    )


def composite_layer(
    canvas: Image.Image,
    layer: PreparedLayer,
    variant: int,
    progress: float,
) -> None:
    if progress <= 0.0:
        return
    asset = shared.revealed_asset(
        layer.variants[variant], layer.reveal_order, min(progress, 1.0), 1.0
    )
    canvas.alpha_composite(asset, layer.position)


def compose(
    frame_index: int,
    brain: PreparedLayer,
    head: PreparedLayer,
    body: PreparedLayer,
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    brain_progress: float,
    head_progress: float,
    body_progress: float,
) -> Image.Image:
    variant = (frame_index // 5) % 3
    canvas = backgrounds[variant].copy()
    focus = math.sin(math.pi * min(max(brain_progress, 0.0), 1.0))
    if head_progress <= 0.0:
        add_brain_focus(canvas, brain, variant, 0.25 + 0.35 * focus)
    composite_layer(canvas, brain, variant, brain_progress)
    composite_layer(canvas, head, variant, head_progress)
    composite_layer(canvas, body, variant, body_progress)
    return canvas.convert("RGB")


def render_continuous(
    brain: PreparedLayer,
    head: PreparedLayer,
    body: PreparedLayer,
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
) -> Path:
    output = OUT_DIR / "brain_in_harness.mp4"
    frames = round(DURATION * FPS)

    def frame_builder(index: int) -> Image.Image:
        time_s = index / FPS
        brain_progress = (time_s - 0.25) / 1.65
        head_progress = (time_s - 3.10) / 1.70
        body_progress = (time_s - 4.35) / 2.25
        return compose(
            index,
            brain,
            head,
            body,
            backgrounds,
            brain_progress,
            head_progress,
            body_progress,
        )

    shared.encode_frames(output, frames, frame_builder)
    return output


def render_interactive(
    brain: PreparedLayer,
    head: PreparedLayer,
    body: PreparedLayer,
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
) -> list[Path]:
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    HOLD_DIR.mkdir(parents=True, exist_ok=True)
    labels = ("The brain", "The harness")
    durations = ((1.75, 0.70), (3.35, 0.70))
    outputs: list[Path] = []

    for stage_index, (label, (draw_duration, hold_duration)) in enumerate(
        zip(labels, durations, strict=True)
    ):
        frames = round((draw_duration + hold_duration) * FPS)
        output = STAGE_DIR / f"{stage_index + 1:02d}-{shared.file_slug(label)}.mp4"

        def frame_builder(index: int, current: int = stage_index) -> Image.Image:
            local = index / FPS
            if current == 0:
                brain_progress = local / 1.65
                head_progress = 0.0
                body_progress = 0.0
            else:
                brain_progress = 1.0
                head_progress = local / 1.60
                body_progress = (local - 1.05) / 2.15
            return compose(
                index,
                brain,
                head,
                body,
                backgrounds,
                brain_progress,
                head_progress,
                body_progress,
            )

        print(f"brain_in_harness: rendering stage {stage_index + 1}/2 ({label})", flush=True)
        shared.encode_frames(output, frames, frame_builder)
        hold_frames = max(2, round(0.52 * FPS))
        hold_start = max(0, frames - hold_frames)
        shared.encode_frames(
            HOLD_DIR / output.name,
            hold_frames,
            lambda hold_index: frame_builder(hold_start + hold_index),
        )
        outputs.append(output)
    return outputs


def write_player(clips: list[Path]) -> None:
    key = "brain_in_harness"
    shared.INTERACTIVE_SCENES[key] = shared.InteractiveSceneSpec(
        labels=("The brain", "The harness"),
        groups=((), ()),
        personality_ranges=((0.0, 0.0), (0.0, 0.0)),
    )
    scene = shared.SceneSpec(
        key=key,
        source="06-brain-in-harness-person.jpeg",
        page_quad=((0, 0), (0, 0), (0, 0), (0, 0)),
        duration=DURATION,
        pieces=(),
        focus_order=(),
        focus_start=0.0,
        focus_step=0.0,
    )
    shared.write_interactive_player(scene, clips)


def make_debug_assets(
    brain: PreparedLayer,
    head: PreparedLayer,
    body: PreparedLayer,
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    clean: Image.Image,
) -> None:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    clean.save(SOURCE_DIR / "cleaned_person_page.png", optimize=True)
    Image.open(BRAIN_REFERENCE).convert("RGB").save(
        SOURCE_DIR / "brain_reference.jpg", quality=92
    )
    compose(55, brain, head, body, backgrounds, 1.0, 0.0, 0.0).save(
        SOURCE_DIR / "stage_01_brain.jpg", quality=94
    )
    compose(155, brain, head, body, backgrounds, 1.0, 1.0, 1.0).save(
        SOURCE_DIR / "stage_02_harness.jpg", quality=94
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-gif", action="store_true")
    parser.add_argument("--skip-interactive", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    brain, head, body, backgrounds, clean = prepare_layers()
    make_debug_assets(brain, head, body, backgrounds, clean)
    if args.prepare_only:
        print(f"wrote brain-in-harness source audits to {SOURCE_DIR}")
        return

    mp4 = render_continuous(brain, head, body, backgrounds)
    established.probe(mp4)
    if not args.skip_gif:
        gif = OUT_DIR / "brain_in_harness.gif"
        shared.render_gif(mp4, gif)
        established.probe(gif)

    if not args.skip_interactive:
        clips = render_interactive(brain, head, body, backgrounds)
        write_player(clips)
        for clip in clips:
            established.probe(clip)


if __name__ == "__main__":
    main()
