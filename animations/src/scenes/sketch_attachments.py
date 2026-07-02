"""
CONCEPT SKETCHES (not for production) — P0 metaphor iteration.

Two still frames pitching the "tools = truck attachments" extension:
  SketchDecked — truck with crane / plow / floodlights bolted on, and each
                 attachment's MANUAL card riding in the bed (the tool
                 definition still occupies context = weight).
  SketchFumble — a job that needs the crane, but with this many attachments
                 the driver grabs the plow. Wrong tool.

Render stills:
  SCRIBBLE_SEED=1 manim -ql -s src/scenes/sketch_attachments.py SketchDecked
  SCRIBBLE_SEED=1 manim -ql -s src/scenes/sketch_attachments.py SketchFumble
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from style import (  # noqa: E402
    ALERT, AI_TEAL, AI_TEAL_DARK, CARGO_AMBER, CARGO_CORAL, CARGO_LILAC,
    CARGO_SAGE, INK, INK_SOFT, PAPER_SCRIBBLE, STROKE_W, cargo_block,
    crayonify, hand_label, puff, rrect, wheel,
)

GROUND_Y = -2.55


def scribble_cargo(text: str, fill: str, seed: int,
                   w: float = 1.30, h: float = 0.72) -> VGroup:
    base = cargo_block(text, fill, w=w, h=h)
    tag = hand_label(text, size=26, scrawl=True)
    tag.scale_to_fit_width(min(base[0].width * 0.82, tag.width))
    tag.move_to(base[0].get_center())
    base[1].become(tag)
    return crayonify(base, seed=seed)


def build_truck() -> dict:
    """Same geometry as context_window.py, returned as named parts."""
    chassis = crayonify(rrect(4.6, 0.32, INK, radius=0.10), seed=1)
    chassis.move_to([0.0, -1.95, 0])

    cab = crayonify(rrect(1.35, 1.45, AI_TEAL, radius=0.18), seed=2)
    cab.move_to([2.05, -1.10, 0])
    window = crayonify(rrect(0.72, 0.52, PAPER_SCRIBBLE, radius=0.10,
                             stroke_w=4), seed=3)
    window.move_to(cab.get_center() + UP * 0.28 + RIGHT * 0.02)
    eye = Dot(window.get_center() + RIGHT * 0.14, radius=0.06, color=INK)

    bed_back = crayonify(rrect(3.55, 1.45, AI_TEAL_DARK, radius=0.10),
                         seed=4).move_to([-0.85, -1.05, 0])
    bed_back.set_z_index(1)
    bed_front = crayonify(rrect(3.55, 0.85, AI_TEAL, radius=0.10),
                          seed=5).move_to([-0.85, -1.35, 0])
    bed_front.set_z_index(3)

    wheels = VGroup(*[
        crayonify(wheel(), seed=10 + i, amp=0.022).move_to(p)
        for i, p in enumerate([[-2.10, GROUND_Y + 0.40, 0],
                               [-0.55, GROUND_Y + 0.40, 0],
                               [1.95, GROUND_Y + 0.40, 0]])
    ])
    truck = VGroup(chassis, bed_back, bed_front, cab, window, eye, wheels)
    return {"truck": truck, "cab": cab, "bed_back": bed_back}


def build_crane(seed: int = 50) -> VGroup:
    """Knuckle-boom crane rising from the bed rear, hook dangling."""
    post = rrect(0.28, 1.05, AI_TEAL_DARK, radius=0.08)
    post.move_to([-2.45, 0.10, 0])          # top of post at y = 0.625
    joint = Circle(radius=0.14, fill_color=AI_TEAL_DARK, fill_opacity=1,
                   stroke_color=INK, stroke_width=4)
    joint.move_to([-2.45, 0.62, 0])
    boom = rrect(1.8, 0.20, AI_TEAL, radius=0.08)
    boom.rotate(35 * DEGREES)
    # boom base sits on the joint; tip lands at (-3.92, 1.65)
    boom.move_to([-2.45 - 0.90 * np.cos(35 * DEGREES),
                  0.62 + 0.90 * np.sin(35 * DEGREES), 0])
    cable = Line([-3.92, 1.60, 0], [-3.92, 0.75, 0],
                 stroke_color=INK, stroke_width=4)
    hook = Arc(radius=0.16, start_angle=0.15 * PI, angle=1.35 * PI,
               stroke_color=INK, stroke_width=STROKE_W)
    hook.move_to([-3.92, 0.58, 0])
    return crayonify(VGroup(post, boom, joint, cable, hook), seed=seed)


def build_plow(seed: int = 51) -> VGroup:
    """Angled plow blade mounted ahead of the cab (truck faces right)."""
    blade = Polygon([3.05, GROUND_Y + 0.05, 0],
                    [3.55, GROUND_Y + 0.05, 0],
                    [3.35, GROUND_Y + 1.05, 0],
                    [2.95, GROUND_Y + 0.95, 0],
                    fill_color=AI_TEAL, fill_opacity=1,
                    stroke_color=INK, stroke_width=STROKE_W)
    arm = rrect(0.55, 0.14, AI_TEAL_DARK, radius=0.05)
    arm.move_to([2.85, -1.75, 0])
    return crayonify(VGroup(arm, blade), seed=seed)


def build_lights(cab_center, seed: int = 52) -> VGroup:
    """Floodlight bar on the cab roof."""
    bar = rrect(0.95, 0.16, AI_TEAL_DARK, radius=0.06)
    bar.move_to(cab_center + UP * 0.85)
    lamps = VGroup(*[
        Circle(radius=0.11, fill_color=CARGO_AMBER, fill_opacity=1,
               stroke_color=INK, stroke_width=4
               ).move_to(cab_center + UP * 1.02 + RIGHT * dx)
        for dx in (-0.25, 0.25)
    ])
    return crayonify(VGroup(bar, lamps), seed=seed)


def stage(scene: Scene, caption_text: str, caption_color=INK):
    scene.camera.background_color = PAPER_SCRIBBLE
    ground = crayonify(
        Line([-8, GROUND_Y, 0], [8, GROUND_Y, 0],
             stroke_color=INK, stroke_width=STROKE_W),
        amp=0.045, seed=99,
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
    ), seed=98).move_to([-6.2, 3.15, 0])
    title = hand_label("THE CONTEXT WINDOW", size=52).to_edge(UP, buff=0.3)
    subtitle = hand_label("the agent's working memory", size=30,
                          color=INK_SOFT)
    subtitle.next_to(title, DOWN, buff=0.08)
    caption = hand_label(caption_text, size=36, color=caption_color)
    caption.move_to([0, GROUND_Y - 0.75, 0])
    scene.add(ground, sun, title, subtitle, caption)


def meter(fill_frac: float, alert: bool = False) -> VGroup:
    panel = crayonify(rrect(3.0, 1.05, "#FFFFFF", radius=0.16, stroke_w=4),
                      seed=30)
    panel.to_corner(UR, buff=0.35).shift(DOWN * 1.1)
    tag = hand_label("TOKENS = fuel = $", size=26)
    tag.move_to(panel.get_center() + UP * 0.24)
    bar_bg = crayonify(rrect(2.4, 0.26, PAPER_SCRIBBLE, radius=0.10,
                             stroke_w=3), seed=31)
    bar_bg.move_to(panel.get_center() + DOWN * 0.22)
    bar_fill = crayonify(rrect(2.20, 0.18, ALERT if alert else AI_TEAL,
                               radius=0.06, stroke_w=0), seed=32)
    bar_fill.move_to(bar_bg.get_center())
    bar_fill.stretch_to_fit_width(2.20 * fill_frac, about_edge=LEFT)
    bar_fill.align_to(bar_bg, LEFT).shift(RIGHT * 0.06)
    return VGroup(panel, tag, bar_bg, bar_fill)


def manual_cards() -> VGroup:
    """The tool definitions riding in the bed: small manual cards."""
    cards = VGroup()
    for i, (name, color, pos, rot) in enumerate([
        ("CRANE",  CARGO_CORAL, [-1.75, -0.55, 0],  4),
        ("PLOW",   CARGO_LILAC, [-0.75, -0.58, 0], -5),
        ("LIGHTS", CARGO_SAGE,  [0.15,  -0.55, 0],  3),
    ]):
        c = scribble_cargo(name, color, seed=60 + i, w=1.00, h=0.55)
        c.rotate(rot * DEGREES).move_to(pos).set_z_index(2)
        cards.add(c)
    return cards


class SketchDecked(Scene):
    """Sketch A — attachments bolted on, manuals in the bed, meter climbing."""

    def construct(self):
        stage(self, "tools bolt on abilities — and weight")
        parts = build_truck()
        truck = parts["truck"]

        instr = scribble_cargo("INSTRUCTIONS", CARGO_AMBER, seed=20)
        instr.move_to([-1.35, -1.19, 0]).set_z_index(2)

        crane = build_crane()
        plow = build_plow()
        lights = build_lights(parts["cab"].get_center())
        cards = manual_cards()

        # everything sags a touch under the new weight
        loaded = VGroup(truck, instr, crane, plow, lights, cards)
        loaded.shift(DOWN * 0.10)

        self.add(truck, instr, crane, plow, lights, cards,
                 meter(0.80))


class SketchFumble(Scene):
    """Sketch B — the job needs the crane; the driver grabs the plow."""

    def construct(self):
        stage(self, "too many tools — easy to grab the wrong one",
              caption_color=ALERT)
        parts = build_truck()
        truck = parts["truck"]

        crane = build_crane()
        plow = build_plow()
        lights = build_lights(parts["cab"].get_center())
        cards = manual_cards()

        # the job: a heavy crate with a lift ring — clearly crane work
        crate = scribble_cargo("HEAVY", CARGO_AMBER, seed=70, w=1.35, h=0.95)
        crate.move_to([5.35, GROUND_Y + 0.50, 0])
        ring = crayonify(Arc(radius=0.18, start_angle=0, angle=PI,
                             stroke_color=INK, stroke_width=STROKE_W),
                         seed=71)
        ring.move_to([5.35, GROUND_Y + 1.08, 0])

        # ...but the plow is deployed, shoving it instead
        shove = VGroup(plow)
        shove.rotate(-8 * DEGREES, about_point=[2.85, GROUND_Y + 0.1, 0])
        dust = puff([4.35, GROUND_Y + 0.25, 0], n=4, spread=0.45)

        confusion = hand_label("?", size=84, color=ALERT)
        confusion.move_to(parts["cab"].get_center() + UP * 1.85)

        self.add(truck, crane, plow, lights, cards, crate, ring, dust,
                 confusion, meter(0.92, alert=True))
