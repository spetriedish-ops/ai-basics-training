"""
Scene 3 — The Truck v2: the context window, tools, and tool overload.

Storyboard: animations/STORYBOARDS.md (Scene 3). Evolves P0 v1:
  * info cargo loads (INSTRUCTIONS / DOCS / CHAT) — beds are finite
  * tools bolt on as ATTACHMENTS and each drops a MANUAL card in the bed
    (tool definitions cost tokens even when unused)
  * escalation gag: pizza oven, disco ball, a second crane for the crane
  * the job arrives and the truck can't choose — tool overload
  * overflow, then the dump: bed empties AND attachments come off
    (context is working memory; nothing persists across sessions)

Render draft:  SCRIBBLE_SEED=1 manim -ql src/scenes/context_window.py ContextWindow
Render final:  ./scripts/boil.sh context_window ContextWindow
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from jobsite import (  # noqa: E402
    CaptionManager, GROUND_Y, build_crane, build_disco_ball, build_lights,
    build_meter, build_pizza_oven, build_plow, build_stage, build_truck,
    roll, scribble_cargo,
)
from style import (  # noqa: E402
    ALERT, AI_TEAL, CARGO_AMBER, CARGO_CORAL, CARGO_LILAC, CARGO_SAGE, INK,
    PAPER_SCRIBBLE, STROKE_W, crayonify, hand_label, puff,
)


class ContextWindow(Scene):
    def construct(self):
        self.camera.background_color = PAPER_SCRIBBLE
        stage = build_stage("THE CONTEXT WINDOW", "the agent's working memory")
        self.add(stage)
        cap = CaptionManager(self)
        self.wait(0.4)

        # ---------------------------------------------- beat 1: enter ----
        parts = build_truck()
        truck = parts["truck"]
        truck.shift(LEFT * 11)
        self.add(truck)
        roll(self, parts, RIGHT * 11, 1.8,
             rate_func=rate_functions.ease_out_sine)

        md = build_meter()
        meter, bar = md["meter"], md["fill"]
        self.play(FadeIn(meter, shift=DOWN * 0.2), run_time=0.5)
        cap.set("everything you load takes tokens")

        def tick(width, color=None):
            a = bar.animate.stretch_to_fit_width(width, about_edge=LEFT)
            return a.set_fill(color) if color else a

        # ----------------------------------------------- beat 2: load ----
        cargo = [
            ("INSTRUCTIONS", CARGO_AMBER, [-1.90, -1.19, 0], 20),
            ("DOCS",         CARGO_LILAC, [-0.50, -1.19, 0], 21),
            ("CHAT",         CARGO_SAGE,  [0.35, -0.44, 0], 22),
        ]
        blocks = {}
        for (name, color, pos, seed), fw in zip(cargo, [0.35, 0.70, 1.05]):
            b = scribble_cargo(name, color, seed=seed).set_z_index(2)
            b.move_to([pos[0], 3.6, 0])
            self.add(b)
            blocks[name] = b
            self.play(b.animate.move_to(pos), tick(fw),
                      run_time=0.8, rate_func=rate_functions.ease_out_bounce)
            self.wait(0.08)
        self.wait(0.4)

        # ------------------------------------- beat 3: crane bolts on ----
        cap.set("tools bolt on new abilities")

        crane = build_crane(seed=50)
        crane.shift(UP * 5.2)
        self.add(crane)
        dust = puff([-2.45, -0.35, 0])
        self.play(crane.animate.shift(DOWN * 5.2),
                  run_time=0.7, rate_func=rate_functions.ease_in_quad)
        self.play(FadeIn(dust), run_time=0.2)
        self.play(FadeOut(dust), run_time=0.25)
        truck.add(crane)

        crane_manual = scribble_cargo("CRANE", CARGO_CORAL, seed=25,
                                      w=1.00, h=0.55).set_z_index(2)
        crane_manual.move_to([-1.90, 3.6, 0])
        self.add(crane_manual)
        self.play(crane_manual.animate.move_to([-1.90, -0.50, 0]),
                  tick(1.30),
                  run_time=0.7, rate_func=rate_functions.ease_out_bounce)

        # demo: the crane hoists a crate the truck couldn't touch before
        crate = scribble_cargo("BEAM", CARGO_AMBER, seed=26, w=1.05, h=0.60)
        crate.set_z_index(2)
        crate.move_to([-4.6, GROUND_Y + 0.32, 0])
        self.play(FadeIn(crate, shift=UP * 0.2), run_time=0.35)
        self.play(crate.animate.move_to([-3.9, 1.0, 0]).rotate(6 * DEGREES),
                  run_time=0.6, rate_func=rate_functions.ease_in_out_sine)
        self.play(crate.animate.move_to([-0.50, -0.50, 0]).rotate(-6 * DEGREES),
                  tick(1.55),
                  run_time=0.7, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.4)

        # --------------------------------- beat 4: plow + floodlights ----
        cap.set("every tool adds weight, even unused")

        plow = build_plow(seed=51)
        plow.shift(UP * 5.2)
        self.add(plow)
        plow_manual = scribble_cargo("PLOW", CARGO_LILAC, seed=27,
                                     w=1.00, h=0.55).set_z_index(2)
        plow_manual.move_to([0.35, 3.6, 0])
        self.play(plow.animate.shift(DOWN * 5.2),
                  run_time=0.55, rate_func=rate_functions.ease_in_quad)
        truck.add(plow)
        self.add(plow_manual)
        self.play(plow_manual.animate.move_to([0.35, 0.28, 0]),
                  tick(1.75),
                  VGroup(truck, *blocks.values(), crane_manual, crate
                         ).animate.shift(DOWN * 0.05),
                  run_time=0.6, rate_func=rate_functions.ease_out_bounce)
        plow_manual.shift(DOWN * 0.05)

        lights = build_lights(seed=52)
        lights.shift(UP * 5.2)
        self.add(lights)
        lights_manual = scribble_cargo("LIGHTS", CARGO_SAGE, seed=28,
                                       w=1.00, h=0.55).set_z_index(2)
        lights_manual.move_to([-0.80, 3.6, 0])
        self.play(lights.animate.shift(DOWN * 5.25),
                  run_time=0.55, rate_func=rate_functions.ease_in_quad)
        truck.add(lights)
        self.add(lights_manual)
        in_bed = VGroup(*blocks.values(), crane_manual, crate, plow_manual)
        self.play(lights_manual.animate.move_to([-0.80, 0.23, 0]),
                  tick(1.95),
                  VGroup(truck, in_bed).animate.shift(DOWN * 0.05),
                  run_time=0.6, rate_func=rate_functions.ease_out_bounce)
        lights_manual.shift(DOWN * 0.05)
        in_bed.add(lights_manual)
        self.wait(0.35)

        # ------------------------------------ beat 5: GAG escalation -----
        cap.set("surely one more")

        oven = build_pizza_oven(seed=53)
        oven.shift(UP * 4.2)
        self.add(oven)
        self.play(oven.animate.shift(DOWN * 4.24),
                  VGroup(truck, in_bed).animate.shift(DOWN * 0.04),
                  run_time=0.5, rate_func=rate_functions.ease_in_quad)
        truck.add(oven)

        # disco ball hangs off the crane boom
        ball = build_disco_ball([-2.74, 1.17, 0], seed=54)
        self.play(FadeIn(ball, shift=DOWN * 0.4),
                  VGroup(truck, in_bed).animate.shift(DOWN * 0.04),
                  run_time=0.5)
        ball.shift(DOWN * 0.04)
        truck.add(ball)

        # the punchline: a second, smaller crane for the first crane,
        # perched on the big crane's boom
        mini = build_crane(seed=55)
        mini.scale(0.45, about_point=[-2.45, -0.475, 0])
        mini.shift(np.array([-3.08, 1.51, 0]) - np.array([-2.45, -0.475, 0]))
        self.play(FadeIn(mini, shift=DOWN * 0.6),
                  VGroup(truck, in_bed).animate.shift(DOWN * 0.05),
                  tick(2.34, ALERT),
                  run_time=0.55)
        mini.shift(DOWN * 0.05)
        truck.add(mini)
        self.wait(0.5)

        # -------------------------------- beat 6: it can't choose --------
        job = scribble_cargo("LIFT ME", CARGO_AMBER, seed=29, w=1.30, h=0.85)
        job.move_to([5.35, GROUND_Y + 0.45, 0])
        ring = crayonify(Arc(radius=0.17, start_angle=0, angle=PI,
                             stroke_color=INK, stroke_width=STROKE_W),
                         seed=56)
        ring.move_to([5.35, GROUND_Y + 0.98, 0])
        self.play(FadeIn(job, shift=UP * 0.2), FadeIn(ring, shift=UP * 0.2),
                  run_time=0.4)
        cap.set("so many tools it can't choose", color=ALERT)

        qmark = hand_label("?", size=84, color=ALERT)
        qmark.move_to([2.05, 0.85, 0])
        self.play(FadeIn(qmark, scale=0.4), run_time=0.3)
        shaky = VGroup(truck, in_bed)
        for dx in (0.05, -0.05, 0.05, -0.05):
            self.play(shaky.animate.shift(RIGHT * dx), run_time=0.09)
        self.wait(0.7)
        self.play(FadeOut(qmark), run_time=0.3)

        # ----------------------------------------- beat 7: overflow ------
        cap.set("overfill the bed and things fall out", color=ALERT)

        big = scribble_cargo("MORE DOCS", CARGO_LILAC, seed=24,
                             w=1.75, h=0.80).set_z_index(2)
        big.move_to([-1.45, 3.6, 0])
        self.add(big)
        chat = blocks["CHAT"]
        in_bed.remove(chat)
        dust2 = puff([1.3, -0.6, 0])
        self.play(big.animate.move_to([-1.45, 0.85, 0]),
                  tick(2.42),
                  run_time=0.75, rate_func=rate_functions.ease_out_bounce)
        in_bed.add(big)
        self.play(
            VGroup(truck, in_bed).animate.shift(DOWN * 0.06),
            chat.animate.move_to([4.0, GROUND_Y + 0.38, 0]
                                 ).rotate(-24 * DEGREES),
            run_time=0.65, rate_func=rate_functions.ease_out_quad,
        )
        self.play(FadeIn(dust2), run_time=0.2)
        self.play(FadeOut(dust2), run_time=0.3)
        self.wait(0.6)

        # --------------------------------------------- beat 8: dump ------
        cap.set("session over — everything comes off")

        bed = VGroup(parts["bed_back"], parts["bed_front"], in_bed)
        pivot = [parts["bed_back"].get_left()[0],
                 parts["chassis"].get_top()[1], 0]
        # crane (plus its passengers) rides the bed rear, tips out with it
        truck.remove(crane, mini, ball)
        self.play(Rotate(VGroup(bed, crane, mini, ball), angle=28 * DEGREES,
                         about_point=pivot),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_sine)

        falling = VGroup(in_bed, crane, mini, ball)
        gp = puff([-4.0, GROUND_Y + 0.25, 0], n=4, spread=0.5)
        self.play(
            falling.animate.shift(LEFT * 2.6 + DOWN * 2.1).rotate(18 * DEGREES),
            FadeOut(chat, shift=DOWN * 0.3),
            FadeOut(job, shift=DOWN * 0.2), FadeOut(ring, shift=DOWN * 0.2),
            run_time=0.8, rate_func=rate_functions.ease_in_quad,
        )
        # the rest of the attachments unbolt and drop
        truck.remove(plow, lights, oven)
        gp2 = puff([2.9, GROUND_Y + 0.2, 0], n=3, spread=0.4)
        self.play(
            FadeIn(gp), FadeOut(falling),
            plow.animate.shift(DOWN * 0.9).rotate(14 * DEGREES),
            lights.animate.shift(RIGHT * 1.1 + DOWN * 2.6).rotate(-20 * DEGREES),
            oven.animate.shift(LEFT * 0.4 + DOWN * 3.2).rotate(10 * DEGREES),
            run_time=0.55, rate_func=rate_functions.ease_in_quad,
        )
        self.play(
            FadeIn(gp2),
            FadeOut(VGroup(plow, lights, oven)),
            Rotate(VGroup(parts["bed_back"], parts["bed_front"]),
                   angle=-28 * DEGREES, about_point=pivot),
            run_time=0.5,
        )
        self.play(
            FadeOut(gp), FadeOut(gp2),
            truck.animate.shift(UP * 0.24),
            bar.animate.stretch_to_fit_width(0.02, about_edge=LEFT
                                             ).set_fill(AI_TEAL),
            run_time=0.7,
        )

        # -------------------------------------------- beat 9: fresh ------
        cap.set("every new session starts empty")
        spark = crayonify(VGroup(
            Star(n=4, outer_radius=0.18, inner_radius=0.07,
                 fill_color=CARGO_AMBER, fill_opacity=1, stroke_width=0
                 ).move_to([-1.4, -0.55, 0]),
            Star(n=4, outer_radius=0.12, inner_radius=0.05,
                 fill_color=CARGO_AMBER, fill_opacity=1, stroke_width=0
                 ).move_to([-0.3, -0.75, 0]),
        ), seed=40).set_z_index(4)
        self.play(FadeIn(spark, scale=0.3), run_time=0.4)
        self.play(FadeOut(spark, scale=1.6), run_time=0.4)
        self.wait(0.7)

        # --------------------------------------------- beat 10: exit -----
        roll(self, parts, RIGHT * 11, 1.7,
             rate_func=rate_functions.ease_in_sine,
             extra_anims=[FadeOut(cap.current), FadeOut(meter)])
        self.wait(0.5)
