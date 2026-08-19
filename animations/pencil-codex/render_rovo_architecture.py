#!/usr/bin/env python3
"""Render the two Rovo sketches without redrawing or rearranging their ink.

Every visible diagram element comes from Sarah's photographed page: lettering,
containers, connectors, and arrowheads. The renderer only isolates the pencil,
fits the complete composition onto notebook paper, reveals the requested source
regions in stages, and applies the established low-amplitude boil.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import render_agentic_loop as established
import render_sketch_set as shared


HERE = Path(__file__).resolve().parent
SKETCH_DIR = HERE.parent / "assets" / "sketches"
SOURCE_DIR = HERE / "source"
OUT_DIR = HERE / "out"
INTERACTIVE_ROOT = HERE / "interactive"

WIDTH, HEIGHT = shared.WIDTH, shared.HEIGHT
FPS = shared.FPS


@dataclass(frozen=True)
class StageSpec:
    label: str
    delay: float
    duration: float
    regions: tuple[tuple[int, int, int, int], ...]


@dataclass(frozen=True)
class FlowSpec:
    key: str
    source: str
    content_box: tuple[int, int, int, int]
    max_size: tuple[int, int]
    stage_starts: tuple[float, ...]
    duration: float
    stages: tuple[StageSpec, ...]


@dataclass
class PreparedStage:
    spec: StageSpec
    variants: tuple[Image.Image, Image.Image, Image.Image]
    reveal_order: np.ndarray


CLI_FLOW = FlowSpec(
    key="rovo_cli_flow",
    source="07-rovo-cli-flow.png",
    content_box=(160, 25, 4028, 1090),
    max_size=(1880, 900),
    stage_starts=(0.25, 4.00, 7.70, 11.80),
    duration=17.0,
    stages=(
        StageSpec(
            "User + Rovo CLI surface",
            0.00,
            1.75,
            ((160, 300, 1300, 1020),),
        ),
        StageSpec(
            "Local Nemo agent runtime",
            0.00,
            1.65,
            ((1300, 235, 1885, 1100),),
        ),
        StageSpec(
            "AI gateway",
            0.00,
            2.23,
            ((1885, 220, 3080, 1020),),
        ),
        StageSpec(
            "Model choices",
            0.00,
            2.27,
            ((3080, 0, 4028, 1120),),
        ),
    ),
)


CHAT_FLOW = FlowSpec(
    key="rovo_chat_agents_flow",
    source="08-rovo-chat-agents-flow.png",
    content_box=(75, 100, 3990, 1580),
    max_size=(1880, 950),
    stage_starts=(0.25, 4.00, 8.00, 12.20, 16.20),
    duration=22.0,
    stages=(
        StageSpec(
            "Rovo Chat + Rovo Agents",
            0.00,
            1.45,
            ((75, 500, 600, 1025), (75, 1030, 600, 1535)),
        ),
        StageSpec(
            "Chat interfaces + other surfaces",
            0.00,
            1.50,
            ((580, 430, 1320, 1540),),
        ),
        StageSpec(
            "Conversational API + ConvoAI",
            0.00,
            2.36,
            ((1320, 590, 2505, 1410),),
        ),
        StageSpec(
            "Rovo Chat + Rovo Agent harnesses",
            0.00,
            1.86,
            ((2505, 320, 2898, 1520),),
        ),
        StageSpec(
            "AI gateway + models",
            0.00,
            3.20,
            ((2898, 85, 3990, 1610),),
        ),
    ),
)


FLOWS = {flow.key: flow for flow in (CLI_FLOW, CHAT_FLOW)}


def stage_asset(
    ink: Image.Image,
    source_size: tuple[int, int],
    regions: tuple[tuple[int, int, int, int], ...],
    content_box: tuple[int, int, int, int],
    output_size: tuple[int, int],
) -> Image.Image:
    """Copy only requested original pixels; never reconstruct their shapes."""
    mask = Image.new("L", source_size, 0)
    draw = ImageDraw.Draw(mask)
    for region in regions:
        draw.rectangle(region, fill=255)

    asset = ink.copy()
    alpha = np.asarray(asset.getchannel("A"), dtype=np.uint16)
    selected = np.asarray(mask, dtype=np.uint16)
    asset.putalpha(Image.fromarray(((alpha * selected) // 255).astype(np.uint8), "L"))
    return asset.crop(content_box).resize(output_size, Image.Resampling.LANCZOS)


def prepare_flow(flow: FlowSpec) -> tuple[
    tuple[PreparedStage, ...],
    tuple[Image.Image, Image.Image, Image.Image],
    tuple[int, int],
    Image.Image,
]:
    source = Image.open(SKETCH_DIR / flow.source).convert("RGB")
    clean, ink = shared.isolate_pencil(source)

    content_width = flow.content_box[2] - flow.content_box[0]
    content_height = flow.content_box[3] - flow.content_box[1]
    scale = min(flow.max_size[0] / content_width, flow.max_size[1] / content_height)
    output_size = (round(content_width * scale), round(content_height * scale))
    position = (
        round((WIDTH - output_size[0]) / 2),
        round((HEIGHT - output_size[1]) / 2),
    )

    prepared: list[PreparedStage] = []
    for index, spec in enumerate(flow.stages):
        asset = stage_asset(
            ink,
            source.size,
            spec.regions,
            flow.content_box,
            output_size,
        )
        prepared.append(
            PreparedStage(
                spec=spec,
                variants=established.boil_variants(
                    asset,
                    seed=1801 + index * 19,
                    amplitude=0.24,
                ),
                reveal_order=shared.make_reveal_order("left", asset),
            )
        )
    return tuple(prepared), established.make_notebook_backgrounds(), position, clean


def compose(
    prepared: tuple[PreparedStage, ...],
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    position: tuple[int, int],
    frame_index: int,
    stage: int,
    local_time: float,
) -> Image.Image:
    variant = (frame_index // 5) % 3
    canvas = backgrounds[variant].copy()
    for index, item in enumerate(prepared):
        if index < stage:
            progress = 1.0
        elif index > stage:
            continue
        else:
            progress = float(
                np.clip(
                    (local_time - item.spec.delay) / item.spec.duration,
                    0.0,
                    1.0,
                )
            )
        if progress <= 0.0:
            continue
        visible = shared.revealed_asset(
            item.variants[variant],
            item.reveal_order,
            progress,
            1.0,
        )
        canvas.alpha_composite(visible, position)
    return canvas.convert("RGB")


def render_interactive(
    flow: FlowSpec,
    prepared: tuple[PreparedStage, ...],
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    position: tuple[int, int],
) -> list[Path]:
    stage_dir = INTERACTIVE_ROOT / flow.key / "stages"
    hold_dir = INTERACTIVE_ROOT / flow.key / "holds"
    stage_dir.mkdir(parents=True, exist_ok=True)
    hold_dir.mkdir(parents=True, exist_ok=True)
    clips: list[Path] = []
    for stage, item in enumerate(prepared):
        draw_duration = item.spec.delay + item.spec.duration + 0.28
        frames = round((draw_duration + 0.70) * FPS)
        output = stage_dir / f"{stage + 1:02d}-{shared.file_slug(item.spec.label)}.mp4"

        def frame_builder(index: int, current_stage: int = stage) -> Image.Image:
            return compose(
                prepared,
                backgrounds,
                position,
                index,
                current_stage,
                index / FPS,
            )

        print(
            f"{flow.key}: rendering stage {stage + 1}/{len(prepared)} "
            f"({item.spec.label})",
            flush=True,
        )
        shared.encode_frames(output, frames, frame_builder)
        hold_frames = max(2, round(0.52 * FPS))
        hold_start = max(0, frames - hold_frames)
        shared.encode_frames(
            hold_dir / output.name,
            hold_frames,
            lambda hold_index: frame_builder(hold_start + hold_index),
        )
        clips.append(output)
    return clips


def write_player(flow: FlowSpec, clips: list[Path]) -> None:
    labels = tuple(stage.label for stage in flow.stages)
    shared.INTERACTIVE_SCENES[flow.key] = shared.InteractiveSceneSpec(
        labels=labels,
        groups=tuple(() for _ in labels),
        personality_ranges=tuple((0.0, 0.0) for _ in labels),
    )
    scene = shared.SceneSpec(
        key=flow.key,
        source=flow.source,
        page_quad=((0, 0), (0, 0), (0, 0), (0, 0)),
        duration=flow.duration,
        pieces=(),
        focus_order=(),
        focus_start=0.0,
        focus_step=0.0,
    )
    shared.write_interactive_player(scene, clips)


def render_continuous(
    flow: FlowSpec,
    prepared: tuple[PreparedStage, ...],
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    position: tuple[int, int],
) -> Path:
    output = OUT_DIR / f"{flow.key}.mp4"
    frames = round(flow.duration * FPS)

    def frame_builder(index: int) -> Image.Image:
        time_s = index / FPS
        stage = (
            max(i for i, start in enumerate(flow.stage_starts) if time_s >= start)
            if time_s >= flow.stage_starts[0]
            else 0
        )
        local_time = max(0.0, time_s - flow.stage_starts[stage])
        return compose(prepared, backgrounds, position, index, stage, local_time)

    shared.encode_frames(output, frames, frame_builder)
    return output


def make_debug_assets(
    flow: FlowSpec,
    prepared: tuple[PreparedStage, ...],
    backgrounds: tuple[Image.Image, Image.Image, Image.Image],
    position: tuple[int, int],
    clean: Image.Image,
) -> None:
    directory = SOURCE_DIR / flow.key
    directory.mkdir(parents=True, exist_ok=True)
    clean.save(directory / "cleaned_page.png", optimize=True)

    extraction = clean.convert("RGBA")
    draw = ImageDraw.Draw(extraction, "RGBA")
    colors = ((46, 167, 154, 220), (228, 87, 46, 220), (116, 92, 160, 220))
    for stage, spec in enumerate(flow.stages):
        for region in spec.regions:
            draw.rectangle(region, outline=colors[stage % 3], width=5)
    extraction.save(directory / "extraction_map.png", optimize=True)

    for stage, item in enumerate(prepared):
        local_time = item.spec.delay + item.spec.duration + 0.2
        compose(
            prepared,
            backgrounds,
            position,
            50 + stage * 19,
            stage,
            local_time,
        ).save(
            directory
            / f"stage_{stage + 1:02d}_{shared.file_slug(item.spec.label).replace('-', '_')}.jpg",
            quality=94,
        )


def render_flow(flow: FlowSpec, prepare_only: bool, skip_gif: bool) -> None:
    prepared, backgrounds, position, clean = prepare_flow(flow)
    make_debug_assets(flow, prepared, backgrounds, position, clean)
    if prepare_only:
        print(f"wrote {flow.key} source audits to {SOURCE_DIR / flow.key}")
        return

    mp4 = render_continuous(flow, prepared, backgrounds, position)
    established.probe(mp4)
    if not skip_gif:
        gif = OUT_DIR / f"{flow.key}.gif"
        shared.render_gif(mp4, gif)
        established.probe(gif)
    clips = render_interactive(flow, prepared, backgrounds, position)
    write_player(flow, clips)
    for clip in clips:
        established.probe(clip)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", choices=tuple(FLOWS))
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-gif", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected = (FLOWS[args.scene],) if args.scene else tuple(FLOWS.values())
    for flow in selected:
        render_flow(flow, args.prepare_only, args.skip_gif)


if __name__ == "__main__":
    main()
