"""
P0 — The context window & tokens.

Metaphor: a dump truck (the agent) being loaded with cargo blocks (context).
  * More useful cargo -> the agent can do more.
  * The bed is FINITE -> overfill it and things fall out; it gets sluggish.
  * Loading cargo fills the TOKEN meter -> tokens are the fuel bill.
  * KEY ACCURACY BEAT: at end of session the bed EMPTIES COMPLETELY.
    Context is working memory. Every new session starts with an empty bed.

Loops cleanly: opens on an empty stage, ends on an empty stage.

Render:
  manim -qm --format=mp4 src/scenes/context_window.py ContextWindow
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from style import (  # noqa: E402
    ALERT, AI_TEAL, AI_TEAL_DARK, CARGO_AMBER, CARGO_CORAL, CARGO_LILAC,
    CARGO_SAGE, INK, INK_SOFT, PAPER, STROKE_W, cargo_block, label,
    make_roller, puff, rrect, wheel,
)

GROUND_Y = -2.55


class ContextWindow(Scene):
    def construct(self):
        self.camera.background_color = PAPER

        # ------------------------------------------------------ stage ----
        ground = Line([-8, GROUND_Y, 0], [8, GROUND_Y, 0],
                      stroke_color=INK, stroke_width=STROKE_W)

        title = label("THE CONTEXT WINDOW", size=44).to_edge(UP, buff=0.35)
        subtitle = label("the agent's working memory", size=27,
                         color=INK_SOFT, bold=False)
        subtitle.next_to(title, DOWN, buff=0.12)

        caption = label("", size=30)  # swapped per beat
        cap_y = GROUND_Y - 0.75

        self.add(ground, title, subtitle)
        self.wait(0.4)

        # ------------------------------------------------------ truck ----
        chassis = rrect(4.6, 0.32, INK, radius=0.10).move_to([0.0, -1.95, 0])

        cab = rrect(1.35, 1.45, AI_TEAL, radius=0.18).move_to([2.05, -1.10, 0])
        window = rrect(0.72, 0.52, PAPER, radius=0.10, stroke_w=4)
        window.move_to(cab.get_center() + UP * 0.28 + RIGHT * 0.02)
        eye = Dot(window.get_center() + RIGHT * 0.14, radius=0.06, color=INK)

        bed_back = rrect(3.55, 1.45, AI_TEAL_DARK, radius=0.10)
        bed_back.move_to([-0.85, -1.05, 0]).set_z_index(1)
        bed_front = rrect(3.55, 0.85, AI_TEAL, radius=0.10)
        bed_front.move_to([-0.85, -1.35, 0]).set_z_index(3)

        wheels = VGroup(
            wheel().move_to([-2.10, GROUND_Y + 0.40, 0]),
            wheel().move_to([-0.55, GROUND_Y + 0.40, 0]),
            wheel().move_to([1.95, GROUND_Y + 0.40, 0]),
        )

        truck = VGroup(chassis, bed_back, bed_front, cab, window, eye, wheels)

        # ------------------------------------------------- token meter ----
        meter_panel = rrect(3.0, 1.05, "#FFFFFF", radius=0.16, stroke_w=4)
        meter_panel.to_corner(UR, buff=0.35).shift(DOWN * 1.1)
        meter_tag = label("TOKENS  =  fuel  =  $", size=22, color=INK)
        meter_tag.move_to(meter_panel.get_center() + UP * 0.24)
        bar_bg = rrect(2.4, 0.26, PAPER, radius=0.10, stroke_w=3)
        bar_bg.move_to(meter_panel.get_center() + DOWN * 0.22)
        bar_fill = rrect(0.02, 0.18, AI_TEAL, radius=0.06, stroke_w=0)
        bar_fill.align_to(bar_bg, LEFT).shift(RIGHT * 0.05)
        bar_fill.set_y(bar_bg.get_y())
        meter = VGroup(meter_panel, meter_tag, bar_bg, bar_fill)

        # ------------------------------------------------- beat 1: enter --
        truck.shift(LEFT * 11)
        self.add(truck)
        for w in wheels:
            w.add_updater(make_roller(0.40))
        self.play(truck.animate.shift(RIGHT * 11),
                  run_time=1.8, rate_func=rate_functions.ease_out_sine)
        self.play(FadeIn(meter, shift=DOWN * 0.2), run_time=0.5)

        def set_caption(text, color=INK):
            new = label(text, size=30, color=color).move_to([0, cap_y, 0])
            anims = [FadeIn(new, shift=UP * 0.15)]
            if caption.family_members_with_points():
                anims.append(FadeOut(caption))
            self.play(*anims, run_time=0.45)
            return new

        caption = set_caption("everything you load takes tokens")

        # ------------------------------------------------ beat 2: load ----
        cargo = [
            ("INSTRUCTIONS", CARGO_AMBER, [-1.55, -1.19, 0]),
            ("TOOLS",        CARGO_CORAL, [-0.15, -1.19, 0]),
            ("DOCS",         CARGO_LILAC, [-1.55, -0.44, 0]),
            ("CHAT",         CARGO_SAGE,  [-0.15, -0.44, 0]),
        ]
        blocks = {}
        fill_widths = [0.55, 1.10, 1.65, 2.20]
        for (name, color, pos), fw in zip(cargo, fill_widths):
            b = cargo_block(name, color).set_z_index(2)
            b.move_to([pos[0], 3.6, 0])
            self.add(b)
            blocks[name] = b
            self.play(
                b.animate.move_to(pos),
                bar_fill.animate.stretch_to_fit_width(fw, about_edge=LEFT),
                run_time=0.85, rate_func=rate_functions.ease_out_bounce,
            )
            self.wait(0.1)
        self.wait(0.6)

        # -------------------------------------------- beat 3: overflow ----
        caption = set_caption("the bed is finite — overfill and things fall out",
                              color=ALERT)

        big = cargo_block("MORE DOCS", CARGO_LILAC, w=1.75, h=0.80).set_z_index(2)
        big.move_to([-0.85, 3.6, 0])
        self.add(big)

        chat = blocks["CHAT"]
        dust = puff(chat.get_center() + RIGHT * 0.9 + DOWN * 0.4)
        self.play(
            big.animate.move_to([-0.85, 0.32, 0]),
            bar_fill.animate.stretch_to_fit_width(2.30, about_edge=LEFT
                                                  ).set_fill(ALERT),
            run_time=0.8, rate_func=rate_functions.ease_out_bounce,
        )
        # truck sags, CHAT gets knocked out and lands beside the truck
        self.play(
            truck.animate.shift(DOWN * 0.14),
            big.animate.shift(DOWN * 0.14),
            VGroup(*[blocks[k] for k in ("INSTRUCTIONS", "TOOLS", "DOCS")]
                   ).animate.shift(DOWN * 0.14),
            chat.animate.move_to([3.6, GROUND_Y + 0.38, 0]).rotate(-24 * DEGREES),
            run_time=0.7, rate_func=rate_functions.ease_out_quad,
        )
        self.play(FadeIn(dust), run_time=0.25)
        self.play(FadeOut(dust), run_time=0.35)
        self.wait(1.0)

        # ------------------------------------------------ beat 4: dump ----
        caption = set_caption("session over — the bed empties")

        in_bed = VGroup(bed_back, bed_front,
                        blocks["INSTRUCTIONS"], blocks["TOOLS"],
                        blocks["DOCS"], big)
        pivot = [bed_back.get_left()[0], chassis.get_top()[1], 0]

        for w in wheels:
            w.clear_updaters()

        self.play(Rotate(in_bed, angle=28 * DEGREES, about_point=pivot),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_sine)

        falling = VGroup(blocks["INSTRUCTIONS"], blocks["TOOLS"],
                         blocks["DOCS"], big)
        ground_puff = puff([-3.6, GROUND_Y + 0.25, 0], n=4, spread=0.5)
        self.play(
            falling.animate.shift(LEFT * 2.6 + DOWN * 2.2).rotate(20 * DEGREES),
            FadeOut(chat, shift=DOWN * 0.3),
            run_time=0.8, rate_func=rate_functions.ease_in_quad,
        )
        self.play(FadeIn(ground_puff), FadeOut(falling), run_time=0.3)
        self.play(
            FadeOut(ground_puff),
            Rotate(VGroup(bed_back, bed_front),
                   angle=-28 * DEGREES, about_point=pivot),
            truck.animate.shift(UP * 0.14),
            bar_fill.animate.stretch_to_fit_width(0.02, about_edge=LEFT
                                                  ).set_fill(AI_TEAL),
            run_time=0.8,
        )

        # ----------------------------------------------- beat 5: fresh ----
        caption = set_caption("every new session starts empty")
        spark = VGroup(
            Star(n=4, outer_radius=0.16, inner_radius=0.06,
                 fill_color=CARGO_AMBER, fill_opacity=1, stroke_width=0
                 ).move_to([-1.4, -0.55, 0]),
            Star(n=4, outer_radius=0.11, inner_radius=0.045,
                 fill_color=CARGO_AMBER, fill_opacity=1, stroke_width=0
                 ).move_to([-0.3, -0.75, 0]),
        ).set_z_index(4)
        self.play(FadeIn(spark, scale=0.3), run_time=0.4)
        self.play(FadeOut(spark, scale=1.6), run_time=0.4)
        self.wait(0.8)

        # ------------------------------------------------ beat 6: exit ----
        for w in wheels:
            w.add_updater(make_roller(0.40))
        self.play(
            truck.animate.shift(RIGHT * 11),
            FadeOut(caption), FadeOut(meter),
            run_time=1.7, rate_func=rate_functions.ease_in_sine,
        )
        for w in wheels:
            w.clear_updaters()
        self.wait(0.5)  # empty stage = clean loop back to the opening
