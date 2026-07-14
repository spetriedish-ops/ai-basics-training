"""
Scene 7 — The Engine Factory: the life cycle of a model.

For run-of-show beat 1 (the LLM/brain section): pre-training builds the
engine from mountains of material, post-training tunes it on the dyno,
release day brings the hullabaloo, and then it goes to work.

Honesty guardrail: the raw material feeds the ASSEMBLY MACHINE, never
the engine itself — the finished engine visibly does not contain the
blocks. Teaching "the model stores its training data" would undo the
Paver's whole lesson.

Render draft:  SCRIBBLE_SEED=1 manim -ql src/scenes/engine_factory.py EngineFactory
Render final:  ./scripts/boil.sh engine_factory EngineFactory
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from jobsite import (  # noqa: E402
    CaptionManager, GROUND_Y, build_stage, build_truck, roll,
)
from style import (  # noqa: E402
    ALERT, AI_TEAL, AI_TEAL_DARK, CARGO_AMBER, CARGO_CORAL, CARGO_LILAC,
    CARGO_SAGE, INK, INK_SOFT, PAPER_SCRIBBLE, STROKE_W, crayonify,
    hand_label, puff, rrect,
)

MAT_COLORS = [CARGO_AMBER, CARGO_CORAL, CARGO_LILAC, CARGO_SAGE]


def build_engine(pistons=CARGO_AMBER, seed=93) -> VGroup:
    """Same silhouette as the Garage's engine; piston color = tune state."""
    return crayonify(VGroup(
        rrect(1.0, 0.75, AI_TEAL_DARK, radius=0.10),
        *[Circle(radius=0.09, fill_color=pistons, fill_opacity=1,
                 stroke_color=INK, stroke_width=3
                 ).move_to([x, 0.22, 0]) for x in (-0.28, 0.0, 0.28)],
    ), seed=seed)


class EngineFactory(Scene):
    def construct(self):
        self.camera.background_color = PAPER_SCRIBBLE
        stage = build_stage("THE ENGINE FACTORY", "the life of a model")
        self.add(stage)
        cap = CaptionManager(self)
        self.wait(0.4)

        # ------------------------------------ beat 1: pre-training -------
        # the assembly machine: hopper on legs over a covered works box
        machine = crayonify(VGroup(
            Polygon([-4.4, -0.25, 0], [-3.0, -0.25, 0], [-3.3, -1.05, 0],
                    [-4.1, -1.05, 0], fill_color=INK_SOFT, fill_opacity=1,
                    stroke_color=INK, stroke_width=STROKE_W),
            rrect(1.7, 1.1, AI_TEAL_DARK, radius=0.12
                  ).move_to([-3.7, -1.65, 0]),
            rrect(0.5, 0.5, PAPER_SCRIBBLE, radius=0.08, stroke_w=4
                  ).move_to([-3.7, -1.57, 0]),   # little window
        ), seed=50)
        gear = crayonify(VGroup(
            Circle(radius=0.16, fill_color=CARGO_AMBER, fill_opacity=1,
                   stroke_color=INK, stroke_width=3),
            *[Line(ORIGIN, RIGHT * 0.24, stroke_color=INK, stroke_width=3
                   ).rotate(a * DEGREES, about_point=ORIGIN)
              for a in range(0, 360, 60)],
        ), seed=51).move_to([-3.7, -1.57, 0])
        belt = crayonify(Line([-3.7, -2.30, 0], [3.4, -2.30, 0],
                              stroke_color=INK, stroke_width=STROKE_W),
                         amp=0.03, seed=52)
        rollers = VGroup(*[
            crayonify(Circle(radius=0.13, fill_color=INK_SOFT,
                             fill_opacity=1, stroke_color=INK,
                             stroke_width=3), seed=53 + i
                      ).move_to([x, -2.42, 0])
            for i, x in enumerate((-3.2, -1.7, -0.2, 1.3, 2.8))
        ])

        # the mountain of material — only the front row gets fed in;
        # the rest stays (there is always more material than one engine eats)
        pile = VGroup()
        rng_pts = [(-6.6, 0.20), (-6.2, 0.20), (-5.8, 0.20),
                   (-6.4, 0.62), (-6.0, 0.62), (-6.2, 1.04),
                   (-7.0, 0.20), (-6.8, 0.62), (-6.6, 1.04),
                   (-6.4, 1.46), (-5.4, 0.20), (-5.6, 0.62)]
        for i, (x, y) in enumerate(rng_pts):
            b = crayonify(rrect(0.42, 0.34, MAT_COLORS[i % 4], radius=0.06,
                                stroke_w=3), seed=60 + i)
            b.move_to([x, GROUND_Y + y, 0])
            pile.add(b)

        cap.set("pre-training: built from mountains of material")
        self.play(FadeIn(machine), FadeIn(gear), FadeIn(belt),
                  FadeIn(rollers), FadeIn(pile, shift=UP * 0.2),
                  run_time=0.6)

        # blocks feed the machine's hopper; the machine chews (gear spins)
        for i, b in enumerate(list(pile)[:6]):
            self.play(b.animate.move_to([-3.7, -0.05, 0]).scale(0.5),
                      Rotate(gear, angle=-PI / 2), run_time=0.22,
                      rate_func=rate_functions.ease_in_sine)
            self.remove(b)

        engine = build_engine(pistons=CARGO_AMBER, seed=93)
        engine.move_to([-3.7, -1.70, 0]).set_z_index(-1)
        d1 = puff([-2.6, -2.05, 0])
        self.add(engine)
        self.play(engine.animate.move_to([-0.9, -1.83, 0]),
                  Rotate(gear, angle=-PI), FadeIn(d1),
                  run_time=0.9, rate_func=rate_functions.ease_out_sine)
        self.play(FadeOut(d1), run_time=0.25)
        self.wait(0.3)

        # ------------------------------------ beat 2: post-training ------
        cap.set("post-training: tuned to be helpful and safe")
        gauge = crayonify(VGroup(
            Arc(radius=0.42, start_angle=PI, angle=-PI, stroke_color=INK,
                stroke_width=4).move_to([1.0, -0.40, 0]),
            Line([1.0, -0.60, 0], [1.3, -0.30, 0], stroke_color=ALERT,
                 stroke_width=4),
        ), seed=70)
        wrench = crayonify(VGroup(
            rrect(0.12, 0.5, AI_TEAL, radius=0.05),
            Circle(radius=0.14, fill_color=AI_TEAL, fill_opacity=1,
                   stroke_color=INK, stroke_width=3).move_to([0, 0.30, 0]),
            Circle(radius=0.07, fill_color=PAPER_SCRIBBLE, fill_opacity=1,
                   stroke_width=0).move_to([0, 0.34, 0]),
        ), seed=71)
        wrench.rotate(-40 * DEGREES).move_to([-0.15, -1.15, 0])
        card = crayonify(rrect(1.15, 1.0, "#FFFFFF", radius=0.10,
                               stroke_w=4), seed=72).move_to([-2.3, -0.60, 0])
        card_lines = VGroup(*[
            crayonify(Line([-2.62, -0.33 - i * 0.3, 0],
                           [-2.02, -0.33 - i * 0.3, 0],
                           stroke_color=INK_SOFT, stroke_width=3),
                      amp=0.02, seed=73 + i)
            for i in range(3)
        ])
        self.play(FadeIn(gauge), FadeIn(wrench), FadeIn(card),
                  FadeIn(card_lines), run_time=0.5)

        checks = []
        for i in range(3):
            tick = hand_label("ok", size=20, scrawl=True,
                              color=AI_TEAL_DARK)
            tick.move_to([-1.82, -0.33 - i * 0.3, 0])
            checks.append(tick)
            self.play(
                Rotate(wrench, angle=(0.5 if i % 2 else -0.5)),
                gauge[1].animate.rotate((0.5 if i % 2 else -0.35),
                                        about_point=[1.0, -0.60, 0]),
                FadeIn(tick, scale=0.5),
                run_time=0.4,
            )
        # the tune lands: pistons go teal
        tuned = build_engine(pistons=AI_TEAL, seed=93)
        tuned.move_to(engine.get_center())
        spark0 = crayonify(Star(n=4, outer_radius=0.16, inner_radius=0.06,
                                fill_color=CARGO_AMBER, fill_opacity=1,
                                stroke_width=0), seed=74)
        spark0.move_to(engine.get_center() + UP * 0.75)
        self.play(FadeOut(engine), FadeIn(tuned), FadeIn(spark0, scale=0.4),
                  run_time=0.45)
        self.play(FadeOut(spark0, scale=1.5), run_time=0.3)
        engine = tuned
        self.wait(0.3)

        # ------------------------------------- beat 3: release day -------
        cap.set("release day: a new model, much hullabaloo")
        self.play(FadeOut(gauge), FadeOut(wrench), FadeOut(card),
                  FadeOut(card_lines), *[FadeOut(c) for c in checks],
                  FadeOut(machine), FadeOut(gear), run_time=0.4)

        pedestal = crayonify(rrect(1.7, 0.5, "#FFFFFF", radius=0.08),
                             seed=80).move_to([-0.9, -2.30, 0])
        banner = crayonify(VGroup(
            rrect(2.1, 0.6, CARGO_AMBER, radius=0.10),
        ), seed=81).move_to([-0.9, 1.6, 0])
        banner_txt = hand_label("NEW!", size=30, scrawl=True)
        banner_txt.move_to([-0.9, 1.6, 0])
        self.play(FadeIn(pedestal),
                  engine.animate.move_to([-0.9, -1.67, 0]),
                  FadeIn(banner, shift=DOWN * 0.3), FadeIn(banner_txt),
                  run_time=0.5, rate_func=rate_functions.ease_out_bounce)

        confetti = VGroup(*[
            Square(0.12, fill_color=MAT_COLORS[i % 4], fill_opacity=1,
                   stroke_width=0
                   ).move_to([-2.3 + 0.5 * i, 2.3 + 0.3 * (i % 3), 0]
                             ).rotate(i * 0.6)
            for i in range(7)
        ])
        sparks = VGroup(*[
            crayonify(Star(n=4, outer_radius=r, inner_radius=r * 0.4,
                           fill_color=CARGO_AMBER, fill_opacity=1,
                           stroke_width=0), seed=82 + i).move_to(p)
            for i, (r, p) in enumerate([(0.18, [-2.0, -0.4, 0]),
                                        (0.13, [0.3, -0.1, 0]),
                                        (0.16, [-0.7, 0.3, 0])])
        ])
        self.add(confetti)
        self.play(confetti.animate.shift(DOWN * 4.2).rotate(0.8),
                  FadeIn(sparks, scale=0.4),
                  run_time=0.9, rate_func=rate_functions.ease_in_sine)
        self.play(FadeOut(confetti), FadeOut(sparks, scale=1.4),
                  run_time=0.35)
        self.wait(0.4)

        # -------------------------------------- beat 4: off to work ------
        cap.set("then it goes to work")
        parts = build_truck(seed=0)
        chassis, wheels = parts["chassis"], parts["wheels"]
        rig = VGroup(chassis, wheels)   # open chassis — the engine's seat
        rig.shift(RIGHT * 11)
        self.add(rig)
        from style import make_roller
        for w in wheels:
            w.add_updater(make_roller(0.40))
        # the factory belt clears as the chassis arrives at center stage
        self.play(rig.animate.shift(LEFT * 11),
                  FadeOut(belt), FadeOut(rollers),
                  run_time=1.2, rate_func=rate_functions.ease_out_sine)
        for w in wheels:
            w.clear_updaters()

        d2 = puff([2.05, -1.6, 0])
        self.play(engine.animate.move_to([2.05, -1.35, 0]).scale(0.9),
                  FadeOut(banner), FadeOut(banner_txt), FadeOut(pedestal),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeIn(d2), run_time=0.2)
        self.play(FadeOut(d2), run_time=0.25)
        rig.add(engine)

        leftover = VGroup(*list(pile)[6:])
        for w in wheels:
            w.add_updater(make_roller(0.40))
        self.play(rig.animate.shift(RIGHT * 12),
                  FadeOut(cap.current), FadeOut(leftover),
                  run_time=1.5, rate_func=rate_functions.ease_in_sine)
        for w in wheels:
            w.clear_updaters()
        self.wait(0.5)
