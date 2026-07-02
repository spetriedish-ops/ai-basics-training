"""
Style test — scribble/crayon redesign ("kid's drawing brought to life").

Short clip: truck rolls in, one block drops. Render 3 passes with different
SCRIBBLE_SEED values and interleave frames (scripts/boil.sh) so the lines
"boil" like a drawing being redrawn every few frames.

  SCRIBBLE_SEED=1 manim -ql src/scenes/style_test_scribble.py StyleTestScribble
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from style import (  # noqa: E402
    AI_TEAL, AI_TEAL_DARK, CARGO_AMBER, INK, INK_SOFT, PAPER_SCRIBBLE,
    STROKE_W, cargo_block, crayonify, hand_label, make_roller, puff,
    rrect, wheel,
)

GROUND_Y = -2.55


class StyleTestScribble(Scene):
    def construct(self):
        self.camera.background_color = PAPER_SCRIBBLE

        ground = crayonify(
            Line([-8, GROUND_Y, 0], [8, GROUND_Y, 0],
                 stroke_color=INK, stroke_width=STROKE_W),
            amp=0.045, seed=99,
        )

        title = hand_label("THE CONTEXT WINDOW", size=52).to_edge(UP, buff=0.3)
        subtitle = hand_label("the agent's working memory", size=30,
                              color=INK_SOFT)
        subtitle.next_to(title, DOWN, buff=0.08)

        self.add(ground, title, subtitle)

        # ------------------------------------------------------ truck ----
        chassis = crayonify(rrect(4.6, 0.32, INK, radius=0.10), seed=1)
        chassis.move_to([0.0, -1.95, 0])

        cab_base = rrect(1.35, 1.45, AI_TEAL, radius=0.18)
        cab = crayonify(cab_base, seed=2).move_to([2.05, -1.10, 0])
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

        # ------------------------------------------------ animation ----
        truck.shift(LEFT * 11)
        self.add(truck)
        for w in wheels:
            w.add_updater(make_roller(0.40))
        self.play(truck.animate.shift(RIGHT * 11),
                  run_time=1.7, rate_func=rate_functions.ease_out_sine)
        for w in wheels:
            w.clear_updaters()

        caption = hand_label("everything you load takes tokens", size=36)
        caption.move_to([0, GROUND_Y - 0.75, 0])
        self.play(FadeIn(caption, shift=UP * 0.15), run_time=0.4)

        block_base = cargo_block("INSTRUCTIONS", CARGO_AMBER)
        block_base[1].become(
            hand_label("INSTRUCTIONS", size=26, scrawl=True)
            .scale_to_fit_width(block_base[0].width * 0.82)
            .move_to(block_base[0].get_center())
        )
        block = crayonify(block_base, seed=20).set_z_index(2)
        block.move_to([-1.55, 3.6, 0])
        self.add(block)
        self.play(block.animate.move_to([-1.55, -1.19, 0]),
                  run_time=0.9, rate_func=rate_functions.ease_out_bounce)

        dust = puff([-1.0, -1.5, 0])
        self.play(FadeIn(dust), run_time=0.2)
        self.play(FadeOut(dust), run_time=0.3)
        self.wait(1.4)
