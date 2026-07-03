"""
Shared Jobsite parts — every scene in the set imports from here.

The world legend lives in STORYBOARDS.md; the visual rules in STYLE.md.
Builders return crayonified groups (or dicts of named parts) positioned at
their canonical spots; scenes shift whole groups to place them. Every
builder takes a seed so multi-pass boiling stays deterministic — keep seeds
unique within a scene.

z-index convention (so cargo rides *inside* the bed):
  0 rear props (crane mast) · 1 bed back panel · 2 cargo/manuals ·
  3 bed front panel · 4 foreground sparkle/dust
"""

import numpy as np

from manim import *
from style import (
    ALERT, AI_TEAL, AI_TEAL_DARK, CARGO_AMBER, CARGO_CORAL, CARGO_LILAC,
    CARGO_SAGE, INK, INK_SOFT, PAPER_SCRIBBLE, STROKE_W, cargo_block,
    crayonify, hand_label, make_roller, puff, rrect, wheel,
)

GROUND_Y = -2.55
CAPTION_Y = GROUND_Y - 0.75


def scribble_cargo(text: str, fill: str, seed: int,
                   w: float = 1.30, h: float = 0.72) -> VGroup:
    """Cargo block with a kid-scrawl label, crayonified."""
    base = cargo_block(text, fill, w=w, h=h)
    tag = hand_label(text, size=26, scrawl=True)
    tag.scale_to_fit_width(min(base[0].width * 0.82, tag.width))
    tag.move_to(base[0].get_center())
    base[1].become(tag)
    return crayonify(base, seed=seed)


def build_stage(title_text: str, subtitle_text: str,
                seed: int = 98) -> VGroup:
    """Ground line + doodled sun + title/subtitle. Add once, keep all scene."""
    ground = crayonify(
        Line([-8, GROUND_Y, 0], [8, GROUND_Y, 0],
             stroke_color=INK, stroke_width=STROKE_W),
        amp=0.045, seed=seed + 1,
    )
    rays = VGroup(*[
        Line(RIGHT * 0.44, RIGHT * 0.68, stroke_color=INK, stroke_width=4
             ).rotate(a * DEGREES, about_point=ORIGIN)
        for a in range(0, 360, 45)
    ])
    sun = crayonify(VGroup(
        Circle(radius=0.32, fill_color=CARGO_AMBER, fill_opacity=1,
               stroke_color=INK, stroke_width=4),
        rays,
    ), seed=seed).move_to([-6.2, 3.15, 0])
    title = hand_label(title_text, size=52).to_edge(UP, buff=0.3)
    subtitle = hand_label(subtitle_text, size=30, color=INK_SOFT)
    subtitle.next_to(title, DOWN, buff=0.08)
    return VGroup(ground, sun, title, subtitle)


class CaptionManager:
    """Swap the single caption line under the ground with a soft fade."""

    def __init__(self, scene: Scene, y: float = CAPTION_Y):
        self.scene = scene
        self.y = y
        self.current = hand_label("", size=36)

    def set(self, text: str, color: str = INK, run_time: float = 0.45):
        new = hand_label(text, size=36, color=color).move_to([0, self.y, 0])
        anims = [FadeIn(new, shift=UP * 0.15)]
        if self.current.family_members_with_points():
            anims.append(FadeOut(self.current))
        self.scene.play(*anims, run_time=run_time)
        self.current = new
        return new

    def clear(self, run_time: float = 0.3):
        if self.current.family_members_with_points():
            self.scene.play(FadeOut(self.current), run_time=run_time)
            self.current = hand_label("", size=36)


def build_truck(seed: int = 0) -> dict:
    """The agent. Canonical spot: chassis centered at x=0 on the ground.

    Returns named parts; 'truck' is the full group. Scenes animate the
    'bed' subgroup for the dump beat.
    """
    chassis = crayonify(rrect(4.6, 0.32, INK, radius=0.10), seed=seed + 1)
    chassis.move_to([0.0, -1.95, 0])

    cab = crayonify(rrect(1.35, 1.45, AI_TEAL, radius=0.18), seed=seed + 2)
    cab.move_to([2.05, -1.10, 0])
    window = crayonify(rrect(0.72, 0.52, PAPER_SCRIBBLE, radius=0.10,
                             stroke_w=4), seed=seed + 3)
    window.move_to(cab.get_center() + UP * 0.28 + RIGHT * 0.02)
    eye = Dot(window.get_center() + RIGHT * 0.14, radius=0.06, color=INK)

    bed_back = crayonify(rrect(3.55, 1.45, AI_TEAL_DARK, radius=0.10),
                         seed=seed + 4).move_to([-0.85, -1.05, 0])
    bed_back.set_z_index(1)
    bed_front = crayonify(rrect(3.55, 0.85, AI_TEAL, radius=0.10),
                          seed=seed + 5).move_to([-0.85, -1.35, 0])
    bed_front.set_z_index(3)

    wheels = VGroup(*[
        crayonify(wheel(), seed=seed + 10 + i, amp=0.022).move_to(p)
        for i, p in enumerate([[-2.10, GROUND_Y + 0.40, 0],
                               [-0.55, GROUND_Y + 0.40, 0],
                               [1.95, GROUND_Y + 0.40, 0]])
    ])

    truck = VGroup(chassis, bed_back, bed_front, cab, window, eye, wheels)
    return {"truck": truck, "chassis": chassis, "cab": cab, "window": window,
            "eye": eye, "bed_back": bed_back, "bed_front": bed_front,
            "wheels": wheels}


def roll(scene: Scene, truck_parts: dict, shift, run_time: float,
         rate_func=None, extra_anims=(), extra_mobs=()):
    """Drive the truck (wheels spinning) by `shift`. extra_mobs move along."""
    wheels = truck_parts["wheels"]
    for w in wheels:
        w.add_updater(make_roller(0.40))
    anims = [truck_parts["truck"].animate.shift(shift)]
    anims += [m.animate.shift(shift) for m in extra_mobs]
    anims += list(extra_anims)
    kw = {"run_time": run_time}
    if rate_func is not None:
        kw["rate_func"] = rate_func
    scene.play(*anims, **kw)
    for w in wheels:
        w.clear_updaters()


# ------------------------------------------------------- attachments ----
# Canonical positions match build_truck's canonical spot; bolt them on,
# then truck_parts["truck"].add(attachment) so they travel together.

def build_crane(seed: int = 50) -> VGroup:
    """Knuckle-boom crane on the bed rear: chunky mast, stubby boom, hook.

    Mast base sits at (-2.45, -0.475); joint at (-2.45, 0.85);
    boom tip at (-3.42, 1.93); hook dangles to (-3.42, 0.93).
    """
    mast = rrect(0.44, 1.35, AI_TEAL_DARK, radius=0.10)
    mast.move_to([-2.45, 0.20, 0])
    joint = Circle(radius=0.19, fill_color=AI_TEAL_DARK, fill_opacity=1,
                   stroke_color=INK, stroke_width=4)
    joint.move_to([-2.45, 0.85, 0])
    boom = rrect(1.45, 0.30, AI_TEAL, radius=0.10)
    boom.rotate(48 * DEGREES)
    boom.move_to([-2.45 - 0.725 * np.cos(48 * DEGREES),
                  0.85 + 0.725 * np.sin(48 * DEGREES), 0])
    tip = [-2.45 - 1.45 * np.cos(48 * DEGREES),
           0.85 + 1.45 * np.sin(48 * DEGREES), 0]
    cable = Line(tip, [tip[0], tip[1] - 0.85, 0],
                 stroke_color=INK, stroke_width=4)
    hook = Arc(radius=0.16, start_angle=0.15 * PI, angle=1.35 * PI,
               stroke_color=INK, stroke_width=STROKE_W)
    hook.move_to([tip[0], tip[1] - 1.0, 0])
    g = crayonify(VGroup(mast, boom, joint, cable, hook), seed=seed)
    g.set_z_index(0)
    return g


def build_plow(seed: int = 51) -> VGroup:
    """Angled plow blade mounted ahead of the cab (truck faces right)."""
    blade = Polygon([3.05, GROUND_Y + 0.05, 0],
                    [3.55, GROUND_Y + 0.05, 0],
                    [3.35, GROUND_Y + 1.05, 0],
                    [2.95, GROUND_Y + 0.95, 0],
                    fill_color=AI_TEAL, fill_opacity=1,
                    stroke_color=INK, stroke_width=STROKE_W)
    arm = rrect(0.55, 0.14, AI_TEAL_DARK, radius=0.05)
    arm.move_to([2.85, -1.95, 0])
    return crayonify(VGroup(arm, blade), seed=seed)


def build_lights(seed: int = 52) -> VGroup:
    """Floodlight bar on the cab roof."""
    cab_center = np.array([2.05, -1.10, 0])
    bar = rrect(0.95, 0.16, AI_TEAL_DARK, radius=0.06)
    bar.move_to(cab_center + UP * 0.85)
    lamps = VGroup(*[
        Circle(radius=0.11, fill_color=CARGO_AMBER, fill_opacity=1,
               stroke_color=INK, stroke_width=4
               ).move_to(cab_center + UP * 1.02 + RIGHT * dx)
        for dx in (-0.25, 0.25)
    ])
    return crayonify(VGroup(bar, lamps), seed=seed)


def build_pizza_oven(seed: int = 53) -> VGroup:
    """Gag prop: wood-fired pizza oven, obviously wrong on a work truck."""
    base = rrect(0.85, 0.42, CARGO_CORAL, radius=0.08)
    base.move_to([0.55, 0.80, 0])
    dome = Arc(radius=0.42, start_angle=0, angle=PI,
               fill_color=CARGO_CORAL, fill_opacity=1,
               stroke_color=INK, stroke_width=STROKE_W)
    dome.move_to([0.55, 1.18, 0])
    mouth = Arc(radius=0.18, start_angle=0, angle=PI, fill_color=INK,
                fill_opacity=1, stroke_width=0).move_to([0.55, 1.10, 0])
    return crayonify(VGroup(base, dome, mouth), seed=seed)


def build_disco_ball(at, seed: int = 54) -> VGroup:
    """Gag prop: disco ball on a little rod, hung wherever `at` says."""
    rod = Line(at, [at[0], at[1] - 0.28, 0], stroke_color=INK, stroke_width=4)
    ball = Circle(radius=0.26, fill_color=INK_SOFT, fill_opacity=1,
                  stroke_color=INK, stroke_width=4)
    ball.move_to([at[0], at[1] - 0.54, 0])
    lat = VGroup(*[
        Line([at[0] - 0.26 + d, at[1] - 0.74, 0],
             [at[0] - 0.26 + d, at[1] - 0.34, 0],
             stroke_color=INK, stroke_width=2)
        for d in (0.13, 0.26, 0.39)
    ])
    lon = Line([at[0] - 0.26, at[1] - 0.54, 0], [at[0] + 0.26, at[1] - 0.54, 0],
               stroke_color=INK, stroke_width=2)
    return crayonify(VGroup(rod, ball, lat, lon), seed=seed)


# ------------------------------------------------------------- meter ----

def build_meter(seed: int = 30, corner=UR) -> dict:
    """The token/fuel meter. Animate d['fill'] width; bg is 2.4 wide."""
    panel = crayonify(rrect(3.0, 1.05, "#FFFFFF", radius=0.16, stroke_w=4),
                      seed=seed)
    panel.to_corner(corner, buff=0.35).shift(DOWN * 1.1)
    tag = hand_label("TOKENS = fuel = $", size=26)
    tag.move_to(panel.get_center() + UP * 0.24)
    bar_bg = crayonify(rrect(2.4, 0.26, PAPER_SCRIBBLE, radius=0.10,
                             stroke_w=3), seed=seed + 1)
    bar_bg.move_to(panel.get_center() + DOWN * 0.22)
    bar_fill = crayonify(rrect(2.20, 0.18, AI_TEAL, radius=0.06, stroke_w=0),
                         seed=seed + 2)
    bar_fill.move_to(bar_bg.get_center())
    bar_fill.stretch_to_fit_width(0.02, about_edge=LEFT)
    bar_fill.align_to(bar_bg, LEFT).shift(RIGHT * 0.06)
    return {"meter": VGroup(panel, tag, bar_bg, bar_fill),
            "panel": panel, "fill": bar_fill, "bg": bar_bg}


# --------------------------------------------------------------- van ----

def build_van(seed: int = 70, scale: float = 1.0) -> dict:
    """A subagent van: half-size teal box van, 2 wheels, canonical x=0."""
    body = crayonify(rrect(1.55, 0.95, AI_TEAL, radius=0.14), seed=seed + 1)
    body.move_to([-0.25, GROUND_Y + 0.95, 0])
    cab = crayonify(rrect(0.62, 0.75, AI_TEAL_DARK, radius=0.12),
                    seed=seed + 2)
    cab.move_to([0.85, GROUND_Y + 0.85, 0])
    window = crayonify(rrect(0.34, 0.28, PAPER_SCRIBBLE, radius=0.07,
                             stroke_w=3), seed=seed + 3)
    window.move_to(cab.get_center() + UP * 0.14 + RIGHT * 0.03)
    eye = Dot(window.get_center() + RIGHT * 0.07, radius=0.045, color=INK)
    wheels = VGroup(*[
        crayonify(wheel(0.26), seed=seed + 5 + i, amp=0.018).move_to(p)
        for i, p in enumerate([[-0.60, GROUND_Y + 0.26, 0],
                               [0.75, GROUND_Y + 0.26, 0]])
    ])
    van = VGroup(body, cab, window, eye, wheels)
    if scale != 1.0:
        van.scale(scale, about_point=[0, GROUND_Y, 0])
    return {"van": van, "body": body, "wheels": wheels}


def roll_van(scene: Scene, van_parts: dict, shift, run_time: float,
             rate_func=None, extra_anims=()):
    wheels = van_parts["wheels"]
    r = wheels[0].width / 2
    for w in wheels:
        w.add_updater(make_roller(r))
    anims = [van_parts["van"].animate.shift(shift)] + list(extra_anims)
    kw = {"run_time": run_time}
    if rate_func is not None:
        kw["rate_func"] = rate_func
    scene.play(*anims, **kw)
    for w in wheels:
        w.clear_updaters()


def build_package(seed: int = 80, w: float = 0.85) -> VGroup:
    """One wrapped result package — ribbon cross + bow."""
    h = w * 0.75
    box = rrect(w, h, CARGO_AMBER, radius=0.08)
    ribbon_v = Line([0, -h / 2, 0], [0, h / 2, 0],
                    stroke_color=ALERT, stroke_width=5)
    ribbon_h = Line([-w / 2, 0, 0], [w / 2, 0, 0],
                    stroke_color=ALERT, stroke_width=5)
    bow = VGroup(
        Arc(radius=0.11, start_angle=0.2, angle=2.2, stroke_color=ALERT,
            stroke_width=4).move_to([-0.10, h / 2 + 0.08, 0]),
        Arc(radius=0.11, start_angle=PI - 0.2, angle=-2.2, stroke_color=ALERT,
            stroke_width=4).move_to([0.10, h / 2 + 0.08, 0]),
    )
    return crayonify(VGroup(box, ribbon_v, ribbon_h, bow), seed=seed)


def build_job_card(text: str, seed: int = 85, w: float = 2.5,
                   h: float = 1.1) -> VGroup:
    """A dispatch job card: white panel, scrawled ask."""
    panel = rrect(w, h, "#FFFFFF", radius=0.12, stroke_w=4)
    tag = hand_label(text, size=30, scrawl=True)
    tag.scale_to_fit_width(min(tag.width, w * 0.85))
    tag.move_to(panel.get_center())
    return crayonify(VGroup(panel, tag), seed=seed)
