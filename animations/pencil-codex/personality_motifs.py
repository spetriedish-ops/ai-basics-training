#!/usr/bin/env python3
"""Small hand-drawn character beats shared by the pencil animations.

The photographed lettering remains the primary artwork. These overlays are
deliberately compact, wordless, and temporary: they act like marginal doodles
that clarify a teaching beat, then get out of the way.
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw


INK = (51, 50, 62)
TEAL = (46, 167, 154)
ORANGE = (232, 102, 48)
YELLOW = (249, 191, 63)
PAPER = (250, 247, 239)


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def smooth(value: float) -> float:
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def window(time_s: float, start: float, end: float, fade: float = 0.16) -> float:
    """Opacity for a short beat with a soft entrance and exit."""
    if time_s < start or time_s > end:
        return 0.0
    return min(smooth((time_s - start) / fade), smooth((end - time_s) / fade))


def _jitter(variant: int, amount: float = 1.0) -> tuple[float, float]:
    return ((-0.85, 0.15, 0.75)[variant % 3] * amount,
            (0.45, -0.65, 0.20)[variant % 3] * amount)


def rough_line(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    variant: int,
    fill: tuple[int, int, int, int],
    width: int = 3,
) -> None:
    dx, dy = _jitter(variant)
    draw.line([(x + dx, y + dy) for x, y in points], fill=fill, width=width, joint="curve")


def stick_figure(
    layer: Image.Image,
    feet: tuple[float, float],
    scale: float,
    variant: int,
    opacity: float,
    pose: str = "stand",
    phase: float = 0.0,
    direction: int = 1,
) -> None:
    """Draw a friendly, boiling-pencil figure using the sketch's visual grammar."""
    if opacity <= 0.0:
        return
    draw = ImageDraw.Draw(layer, "RGBA")
    color = INK + (round(235 * opacity),)
    accent = TEAL + (round(160 * opacity),)
    x, y = feet
    sway = math.sin(phase) * 1.7 * scale
    bob = abs(math.sin(phase)) * 2.5 * scale if pose == "run" else 0.0
    x += sway
    y -= bob
    head_r = 11.5 * scale
    head = (x, y - 67 * scale)
    neck = (x, y - 53 * scale)
    hip = (x, y - 25 * scale)
    shoulder = (x, y - 47 * scale)
    width = max(2, round(3.0 * scale))
    dx, dy = _jitter(variant, 0.75)
    draw.ellipse(
        (head[0] - head_r + dx, head[1] - head_r + dy,
         head[0] + head_r + dx, head[1] + head_r + dy),
        outline=color,
        width=width,
    )
    rough_line(draw, [neck, shoulder, hip], variant, color, width)

    if pose == "catch":
        arms = [((shoulder[0], shoulder[1]), (x - 18 * scale, y - 64 * scale)),
                ((shoulder[0], shoulder[1]), (x + 19 * scale, y - 68 * scale))]
    elif pose == "think":
        arms = [((shoulder[0], shoulder[1]), (x - 17 * scale, y - 35 * scale)),
                ((shoulder[0], shoulder[1]), (x + 13 * scale, y - 59 * scale),
                 (x + 8 * scale, y - 67 * scale))]
    elif pose in ("carry", "inspect"):
        target_y = y - (39 if pose == "carry" else 31) * scale
        arms = [((shoulder[0], shoulder[1]), (x + direction * 19 * scale, target_y)),
                ((shoulder[0], shoulder[1]), (x + direction * 24 * scale, target_y + 6 * scale))]
    elif pose == "present":
        arms = [((shoulder[0], shoulder[1]), (x - direction * 14 * scale, y - 35 * scale)),
                ((shoulder[0], shoulder[1]), (x + direction * 27 * scale, y - 58 * scale))]
    elif pose == "juggle":
        arms = [((shoulder[0], shoulder[1]), (x - 23 * scale, y - 56 * scale)),
                ((shoulder[0], shoulder[1]), (x + 23 * scale, y - 56 * scale))]
    else:
        swing = math.sin(phase) * 17 * scale if pose == "run" else 0.0
        arms = [((shoulder[0], shoulder[1]), (x - 17 * scale, y - 36 * scale + swing)),
                ((shoulder[0], shoulder[1]), (x + 17 * scale, y - 36 * scale - swing))]
    for arm in arms:
        rough_line(draw, list(arm), variant, color, width)

    if pose == "run":
        kick = math.sin(phase) * 20 * scale
        legs = [((hip[0], hip[1]), (x - 10 * scale, y - 10 * scale), (x - 17 * scale - kick, y)),
                ((hip[0], hip[1]), (x + 9 * scale, y - 10 * scale), (x + 16 * scale + kick, y))]
    else:
        legs = [((hip[0], hip[1]), (x - 9 * scale, y)),
                ((hip[0], hip[1]), (x + 10 * scale, y))]
    for leg in legs:
        rough_line(draw, list(leg), variant, color, width)

    # The two dots and tiny smile are what give Sarah's original figures their charm.
    eye_y = head[1] - 2 * scale + dy
    for eye_x in (head[0] - 4 * scale, head[0] + 4 * scale):
        draw.ellipse((eye_x - 1.2 * scale + dx, eye_y - 1.2 * scale,
                      eye_x + 1.2 * scale + dx, eye_y + 1.2 * scale), fill=color)
    rough_line(draw, [(head[0] - 4 * scale, head[1] + 4 * scale),
                      (head[0], head[1] + 7 * scale),
                      (head[0] + 5 * scale, head[1] + 3.5 * scale)], variant, accent, max(1, width - 1))


def paper_plane(layer: Image.Image, center: tuple[float, float], scale: float,
                variant: int, opacity: float) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    color = TEAL + (round(220 * opacity),)
    points = [(x - 18 * scale, y - 6 * scale), (x + 20 * scale, y),
              (x - 14 * scale, y + 10 * scale), (x - 6 * scale, y + 1 * scale)]
    rough_line(draw, points + [points[0]], variant, color, max(2, round(3 * scale)))
    rough_line(draw, [(x - 6 * scale, y + scale), (x + 20 * scale, y)], variant, color, max(1, round(2 * scale)))


def scribble(layer: Image.Image, center: tuple[float, float], scale: float,
             variant: int, opacity: float) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    points = []
    for index in range(22):
        angle = index * 1.72
        radius = (5 + index * 0.72) * scale
        points.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius * 0.58))
    rough_line(draw, points, variant, ORANGE + (round(205 * opacity),), max(2, round(3 * scale)))


def toolbox(layer: Image.Image, center: tuple[float, float], scale: float,
            variant: int, opacity: float, huge: bool = False) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    w = (62 if huge else 44) * scale
    h = (35 if huge else 27) * scale
    color = INK + (round(225 * opacity),)
    fill = ORANGE + (round(112 * opacity),)
    dx, dy = _jitter(variant)
    draw.rounded_rectangle((x - w / 2 + dx, y - h / 2 + dy, x + w / 2 + dx, y + h / 2 + dy),
                           radius=max(2, round(4 * scale)), fill=fill, outline=color,
                           width=max(2, round(3 * scale)))
    draw.arc((x - 15 * scale, y - h / 2 - 13 * scale,
              x + 15 * scale, y - h / 2 + 7 * scale), 180, 360,
             fill=color, width=max(2, round(3 * scale)))
    rough_line(draw, [(x - w / 2, y), (x + w / 2, y)], variant, color, max(1, round(2 * scale)))


def magnifier(layer: Image.Image, center: tuple[float, float], scale: float,
              variant: int, opacity: float) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    color = TEAL + (round(225 * opacity),)
    r = 13 * scale
    dx, dy = _jitter(variant)
    draw.ellipse((x - r + dx, y - r + dy, x + r + dx, y + r + dy),
                 outline=color, width=max(2, round(3 * scale)))
    rough_line(draw, [(x + r * 0.72, y + r * 0.72),
                      (x + r * 1.75, y + r * 1.8)], variant, color, max(2, round(3 * scale)))


def burst(layer: Image.Image, center: tuple[float, float], scale: float,
          variant: int, opacity: float, color: tuple[int, int, int] = YELLOW) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    for index in range(8):
        angle = math.tau * index / 8
        inner, outer = 17 * scale, 28 * scale
        rough_line(draw, [(x + math.cos(angle) * inner, y + math.sin(angle) * inner),
                          (x + math.cos(angle) * outer, y + math.sin(angle) * outer)],
                   variant, color + (round(205 * opacity),), max(1, round(2.5 * scale)))


def package(layer: Image.Image, center: tuple[float, float], scale: float,
            variant: int, opacity: float, belt: bool = False) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    color = INK + (round(220 * opacity),)
    fill = TEAL + (round(65 * opacity),)
    w, h = 38 * scale, 31 * scale
    dx, dy = _jitter(variant)
    draw.rectangle((x - w / 2 + dx, y - h / 2 + dy, x + w / 2 + dx, y + h / 2 + dy),
                   fill=fill, outline=color, width=max(2, round(2.5 * scale)))
    rough_line(draw, [(x - w / 2, y - h / 2), (x, y - h * 0.08),
                      (x + w / 2, y - h / 2)], variant, color, max(1, round(2 * scale)))
    rough_line(draw, [(x, y - h * 0.08), (x, y + h / 2)], variant, color, max(1, round(2 * scale)))
    if belt:
        rough_line(draw, [(x - w / 2 - 3 * scale, y + 2 * scale),
                          (x + w / 2 + 3 * scale, y + 2 * scale)],
                   variant, ORANGE + (round(230 * opacity),), max(2, round(4 * scale)))


def agentic_loop_overlay(canvas: Image.Image, time_s: float, variant: int, opacity: float) -> None:
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    beats = (
        # The character enters with the first graphite, then performs a quick
        # preview alongside the live writing before the slower teaching lap.
        (0.30, 1.12, "intro"),
        (0.88, 2.25, "receive"),
        (2.02, 3.55, "reason"),
        (3.30, 4.88, "tools"),
        (4.62, 6.18, "observe"),
        (5.92, 7.42, "repeat"),
        (7.22, 9.20, "receive"),
        (8.98, 10.90, "reason"),
        (10.68, 12.60, "tools"),
        (12.38, 14.30, "observe"),
        (14.08, 16.10, "repeat"),
        (15.92, 21.20, "run_home"),
    )
    for start, end, name in beats:
        amount = window(time_s, start, end, 0.22) * opacity
        if amount <= 0.0:
            continue
        local = smooth((time_s - start) / (end - start))
        action = smooth(min(local / 0.56, 1.0))
        if name == "intro":
            stick_figure(layer, (70 + 140 * local, 535), 1.22, variant, amount,
                         "run", time_s * 11.0)
        elif name == "receive":
            stick_figure(layer, (220, 545), 1.28, variant, amount, "catch")
            paper_plane(layer, (82 + 128 * action, 430 - 25 * action), 1.20, variant, amount)
        elif name == "reason":
            stick_figure(layer, (755, 625), 1.25, variant, amount, "think")
            scribble(layer, (815, 470), 1.20, variant, amount)
        elif name == "tools":
            stick_figure(layer, (1640 - 65 * action, 720), 1.22, variant, amount, "carry")
            toolbox(layer, (1700 - 65 * action, 675), 1.28, variant, amount)
        elif name == "observe":
            stick_figure(layer, (1300, 1005), 1.15, variant, amount, "inspect")
            magnifier(layer, (1350, 962), 1.18, variant, amount)
        elif name == "repeat":
            stick_figure(layer, (285 + 135 * action, 975 - 58 * math.sin(math.pi * action)),
                         1.12, variant, amount, "run", time_s * 10.0)
        else:
            # One continuous victory lap along the outside return arrow lets
            # the character remain readable after all five concepts land.
            if local < 0.32:
                part = smooth(local / 0.32)
                x, y = 410 - 250 * part, 955 - 30 * part
            elif local < 0.62:
                part = smooth((local - 0.32) / 0.30)
                x, y = 160 - 65 * part, 925 - 485 * part
            else:
                part = smooth((local - 0.62) / 0.38)
                x, y = 95 + 610 * part, 440 - 190 * part
            stick_figure(layer, (x, y), 1.05, variant, amount, "run", time_s * 11.0)
    canvas.alpha_composite(layer)


def what_is_agent_overlay(canvas: Image.Image, time_s: float, variant: int, opacity: float) -> None:
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    intro = window(time_s, 0.24, 9.40, 0.28) * opacity
    if intro > 0.0:
        stick_figure(layer, (1325, 180), 1.30, variant, intro, "present", direction=-1)
        paper_plane(layer, (1375, 105), 0.92, variant, intro)

    assemble = window(time_s, 9.18, 13.02, 0.28) * opacity
    if assemble > 0.0:
        local = smooth(min((time_s - 9.18) / 1.65, 1.0))
        stick_figure(layer, (1005, 650), 1.28, variant, assemble, "stand")
        # Model, harness, and goal arrive as a thought, belt, and target.
        scribble(layer, (915 + 55 * local, 515), 0.72, variant, assemble)
        package(layer, (1115 - 110 * local, 600), 0.82, variant, assemble, belt=True)
        target(layer, (1095 - 50 * local, 510), 0.72, variant, assemble)

    general = window(time_s, 12.80, 16.45, 0.28) * opacity
    if general > 0.0:
        stick_figure(layer, (1010, 850), 1.30, variant, general, "juggle", time_s * 4.0)
        for index, color in enumerate((TEAL, ORANGE, YELLOW)):
            angle = time_s * 2.25 + index * math.tau / 3
            cx = 1010 + math.cos(angle) * 65
            cy = 690 + math.sin(angle) * 24
            burst(layer, (cx, cy), 0.42, variant, general, color)

    specialist = window(time_s, 16.20, 20.25, 0.28) * opacity
    if specialist > 0.0:
        local = smooth(min((time_s - 16.20) / 1.15, 1.0))
        stick_figure(layer, (1010, 970), 1.25, variant, specialist, "present", direction=1)
        target(layer, (1070 + 38 * local, 875), 0.88, variant, specialist)
        rough_line(ImageDraw.Draw(layer, "RGBA"), [(1040, 900), (1078 + 30 * local, 880)],
                   variant, TEAL + (round(190 * specialist),), 3)
    canvas.alpha_composite(layer)


def target(layer: Image.Image, center: tuple[float, float], scale: float,
           variant: int, opacity: float) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    color = ORANGE + (round(220 * opacity),)
    dx, dy = _jitter(variant)
    for radius in (16, 9, 3):
        r = radius * scale
        draw.ellipse((x - r + dx, y - r + dy, x + r + dx, y + r + dy),
                     outline=color, width=max(1, round(2.3 * scale)))
    rough_line(draw, [(x + 12 * scale, y - 12 * scale),
                      (x + 27 * scale, y - 27 * scale)], variant, color, max(1, round(2.3 * scale)))


def mcp_cli_api_overlay(canvas: Image.Image, time_s: float, variant: int, opacity: float) -> None:
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    mcp = window(time_s, 1.85, 8.10, 0.30) * opacity
    if mcp > 0.0:
        local = smooth(min((time_s - 1.85) / 1.25, 1.0))
        stick_figure(layer, (560 - 22 * local, 690), 1.42, variant, mcp, "inspect", direction=-1)
        # The recurring presenter peeks into Sarah's oversized official toolbox.
        burst(layer, (510, 545), 0.52, variant, mcp, YELLOW)
    cli = window(time_s, 9.65, 15.90, 0.30) * opacity
    if cli > 0.0:
        # The photographed character supplies the command; its terminal grows
        # a multi-tool, with the wrong attachment briefly winning the race.
        emerge = smooth((time_s - 9.80) / 1.45)
        wrong = smooth((time_s - 10.55) / 0.55) * (1.0 - smooth((time_s - 11.75) / 0.55))
        right = smooth((time_s - 11.35) / 0.85)
        swiss_army_knife(layer, (970, 690), 1.55, variant, cli * emerge, wrong, right)
        if emerge > 0.74:
            burst(layer, (1055, 575), 0.58, variant, cli, YELLOW)
    api = window(time_s, 15.05, 22.15, 0.30) * opacity
    if api > 0.0:
        local = smooth(min((time_s - 16.00) / 2.70, 1.0))
        # A request travels to one standardized port and returns as a result.
        road(layer, (1330, 790), (1800, 790), variant, api)
        package_x = 1385 + 335 * local
        package(layer, (package_x, 752), 1.22, variant, api, belt=True)
        stick_figure(layer, (1330, 900), 1.62, variant, api,
                     "present" if local > 0.92 else "run", time_s * 6.5)
    canvas.alpha_composite(layer)


def swiss_army_knife(
    layer: Image.Image,
    center: tuple[float, float],
    scale: float,
    variant: int,
    opacity: float,
    wrong_attachment: float,
    right_attachment: float,
) -> None:
    """A playful CLI multi-tool that unfolds in response to a command."""
    if opacity <= 0.0:
        return
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    color = INK + (round(230 * opacity),)
    body = ORANGE + (round(150 * opacity),)
    metal = TEAL + (round(115 * opacity),)
    width = max(2, round(3 * scale))
    dx, dy = _jitter(variant, 0.8)
    w, h = 118 * scale, 42 * scale
    draw.rounded_rectangle(
        (x - w / 2 + dx, y - h / 2 + dy, x + w / 2 + dx, y + h / 2 + dy),
        radius=round(18 * scale), fill=body, outline=color, width=width,
    )
    # A tiny cross makes the silhouette recognizable without relying on color.
    rough_line(draw, [(x - 32 * scale, y - 7 * scale), (x - 32 * scale, y + 7 * scale)],
               variant, color, max(2, round(2 * scale)))
    rough_line(draw, [(x - 39 * scale, y), (x - 25 * scale, y)],
               variant, color, max(2, round(2 * scale)))
    draw.ellipse((x + 40 * scale, y - 5 * scale, x + 50 * scale, y + 5 * scale),
                 outline=color, width=max(1, round(2 * scale)))

    # First, a corkscrew pops out—the not-quite-right command joke.
    wrong = clamp(wrong_attachment)
    if wrong > 0.01:
        points = []
        for index in range(13):
            phase = index / 12
            points.append((
                x - 28 * scale + math.sin(phase * math.pi * 5) * 8 * scale * wrong,
                y - h / 2 - phase * 54 * scale * wrong,
            ))
        rough_line(draw, points, variant, ORANGE + (round(225 * opacity * wrong),), width)

    # Then the useful blade unfolds and holds for the teaching beat.
    right = clamp(right_attachment)
    if right > 0.01:
        pivot = (x + 35 * scale, y - h / 2 + 3 * scale)
        angle = math.radians(-12 - 58 * right)
        length = 88 * scale
        tip = (pivot[0] + math.cos(angle) * length, pivot[1] + math.sin(angle) * length)
        spine = (tip[0] - math.sin(angle) * 17 * scale, tip[1] + math.cos(angle) * 17 * scale)
        root = (pivot[0] - math.sin(angle) * 11 * scale, pivot[1] + math.cos(angle) * 11 * scale)
        draw.polygon([pivot, tip, spine, root], fill=metal, outline=color)
        rough_line(draw, [pivot, tip, spine, root, pivot], variant, color, width)


def wrench(layer: Image.Image, center: tuple[float, float], scale: float,
           variant: int, opacity: float) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    x, y = center
    color = TEAL + (round(225 * opacity),)
    rough_line(draw, [(x - 18 * scale, y + 21 * scale), (x + 15 * scale, y - 15 * scale)],
               variant, color, max(3, round(5 * scale)))
    rough_line(draw, [(x + 9 * scale, y - 18 * scale), (x + 18 * scale, y - 23 * scale),
                      (x + 23 * scale, y - 14 * scale)], variant, color, max(2, round(3 * scale)))
    draw.ellipse((x - 24 * scale, y + 17 * scale, x - 12 * scale, y + 29 * scale),
                 outline=color, width=max(2, round(3 * scale)))


def road(layer: Image.Image, start: tuple[float, float], end: tuple[float, float],
         variant: int, opacity: float) -> None:
    draw = ImageDraw.Draw(layer, "RGBA")
    color = INK + (round(145 * opacity),)
    rough_line(draw, [(start[0], start[1] - 25), (end[0], end[1] - 25)], variant, color, 2)
    rough_line(draw, [(start[0], start[1] + 25), (end[0], end[1] + 25)], variant, color, 2)
    for x in range(round(start[0] + 15), round(end[0]), 42):
        rough_line(draw, [(x, start[1]), (x + 20, start[1])], variant,
                   TEAL + (round(165 * opacity),), 3)


def frontier_overlay(canvas: Image.Image, time_s: float, variant: int, opacity: float) -> None:
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    intro = window(time_s, 0.26, 8.12, 0.30) * opacity
    if intro > 0.0:
        rough_line(ImageDraw.Draw(layer, "RGBA"), [(520, 1045), (920, 1045)],
                   variant, TEAL + (round(150 * intro),), 4)
        package(layer, (675, 995), 1.34, variant, intro)
        stick_figure(layer, (585, 1045), 1.02, variant, intro, "present")
        burst(layer, (675, 920), 0.58, variant, intro, YELLOW)

    beats = ((7.88, 10.78, False), (10.62, 13.62, False),
             (13.48, 16.50, True), (16.35, 20.75, True))
    for index, (start, end, belt) in enumerate(beats):
        amount = window(time_s, start, end, 0.28) * opacity
        if amount <= 0.0:
            continue
        local = smooth((time_s - start) / (end - start))
        x = 640 + 120 * local
        y = 1000
        # A tiny conveyor in the unused footer turns the taxonomy into a
        # memorable Lab -> Model -> Harness -> API assembly joke.
        rough_line(ImageDraw.Draw(layer, "RGBA"), [(545, 1042), (890, 1042)],
                   variant, TEAL + (round(150 * amount),), 3)
        if index == 0:
            # The lab stamps a fresh box onto the pipeline.
            package(layer, (x, y), 1.34, variant, amount)
            burst(layer, (x, y - 78), 0.70, variant, amount, YELLOW)
            stick_figure(layer, (x - 100, y + 48), 0.98, variant, amount, "present")
        elif index == 1:
            package(layer, (x, y), 1.34, variant, amount)
            scribble(layer, (x, y - 78), 0.72, variant, amount)
            stick_figure(layer, (x - 100, y + 48), 0.98, variant, amount, "think")
        elif index == 2:
            package(layer, (x, y), 1.34, variant, amount, belt=belt)
            stick_figure(layer, (x + 112, y + 48), 0.98, variant, amount, "carry")
        else:
            package(layer, (x + 120 * local, y), 1.34, variant, amount, belt=belt)
            stick_figure(layer, (x - 100 + 62 * local, y + 48), 0.98, variant, amount,
                         "run" if local < 0.96 else "present", time_s * 7.0)
    canvas.alpha_composite(layer)


def harness_overlay(canvas: Image.Image, progress: list[float],
                    variant: int, opacity: float) -> None:
    """Keep a presenter agent onscreen, then hop it into the Harness finale."""
    if not progress or progress[0] <= 0.20:
        return
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    base_amount = smooth((progress[0] - 0.20) / 0.28) * opacity
    final_progress = progress[-1]
    if final_progress <= 0.36:
        current = max(index for index, value in enumerate(progress) if value > 0.001)
        direction = -1 if current in (1, 5) else 1
        pose = "stand" if current in (0, 2) else "present"
        stick_figure(layer, (1040, 990), 1.12, variant, base_amount, pose,
                     progress[current] * math.tau, direction=direction)
        if current > 0 and progress[current] > 0.72:
            burst(layer, (1040 + direction * 66, 900), 0.48, variant,
                  base_amount, TEAL if current % 2 else ORANGE)
        canvas.alpha_composite(layer)
        return

    amount = base_amount
    local = smooth((final_progress - 0.36) / 0.58)
    start = (1020.0, 1010.0)
    end = (1050.0, 560.0)
    x = start[0] + (end[0] - start[0]) * local
    y = start[1] + (end[1] - start[1]) * local - math.sin(math.pi * local) * 95
    stick_figure(layer, (x, y), 1.12, variant, amount, "run", local * math.tau * 2.2)
    if local > 0.90:
        burst(layer, (1050, 490), 0.48, variant, amount, TEAL)
    canvas.alpha_composite(layer)
