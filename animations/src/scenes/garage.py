"""
Scene 1 — The Garage: types of AI & model progression.

Storyboard: animations/STORYBOARDS.md (Scene 1):
  * forklift on a painted line — rules: perfect on the line, stops dead
    two feet off it (the chatbot-vs-agent seed)
  * the route van — learned one route, repeats it through a cone
  * an engine for anything lowers into an open chassis
  * generation montage: each generation hauls more per gallon
  * GAG: the half-scribbled NEXT YEAR'S TRUCK (PROBABLY) poster
  * today's truck rolls out — the forklift still working its line

Render draft:  SCRIBBLE_SEED=1 manim -ql src/scenes/garage.py Garage
Render final:  ./scripts/boil.sh garage Garage
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
    hand_label, make_roller, puff, rrect, wheel,
)


def build_forklift(seed: int = 10) -> dict:
    """Small forklift at canonical x=0, facing right, forks forward."""
    body = crayonify(rrect(1.05, 0.75, CARGO_AMBER, radius=0.12),
                     seed=seed + 1)
    body.move_to([-0.15, GROUND_Y + 0.75, 0])
    cage = crayonify(rrect(0.55, 0.55, CARGO_AMBER, radius=0.10, stroke_w=4),
                     seed=seed + 2)
    cage.move_to([-0.30, GROUND_Y + 1.35, 0])
    mast = crayonify(rrect(0.14, 1.15, INK_SOFT, radius=0.04),
                     seed=seed + 3)
    mast.move_to([0.55, GROUND_Y + 0.95, 0])
    fork = crayonify(Line([0.62, GROUND_Y + 0.28, 0],
                          [1.35, GROUND_Y + 0.28, 0],
                          stroke_color=INK, stroke_width=STROKE_W),
                     seed=seed + 4)
    wheels = VGroup(*[
        crayonify(wheel(0.24), seed=seed + 5 + i, amp=0.018).move_to(p)
        for i, p in enumerate([[-0.55, GROUND_Y + 0.24, 0],
                               [0.35, GROUND_Y + 0.24, 0]])
    ])
    lift = VGroup(body, cage, mast, fork, wheels)
    return {"lift": lift, "wheels": wheels, "fork": fork}


def build_route_van(seed: int = 20) -> dict:
    """The classic-ML delivery van: boxy, one route, coral livery."""
    body = crayonify(rrect(1.5, 0.9, CARGO_CORAL, radius=0.14),
                     seed=seed + 1)
    body.move_to([-0.2, GROUND_Y + 0.92, 0])
    cab = crayonify(rrect(0.6, 0.7, CARGO_CORAL, radius=0.12),
                    seed=seed + 2)
    cab.move_to([0.85, GROUND_Y + 0.82, 0])
    window = crayonify(rrect(0.32, 0.26, PAPER_SCRIBBLE, radius=0.06,
                             stroke_w=3), seed=seed + 3)
    window.move_to([0.90, GROUND_Y + 0.95, 0])
    wheels = VGroup(*[
        crayonify(wheel(0.25), seed=seed + 4 + i, amp=0.018).move_to(p)
        for i, p in enumerate([[-0.55, GROUND_Y + 0.25, 0],
                               [0.75, GROUND_Y + 0.25, 0]])
    ])
    van = VGroup(body, cab, window, wheels)
    return {"van": van, "wheels": wheels}


class Garage(Scene):
    def construct(self):
        self.camera.background_color = PAPER_SCRIBBLE
        stage = build_stage("HOW WE GOT HERE", "the garage tour")
        self.add(stage)
        cap = CaptionManager(self)

        # garage backdrop: a big doorway on the left
        garage = crayonify(VGroup(
            rrect(3.1, 3.1, "#E9E2D2", radius=0.15).move_to(
                [-5.4, GROUND_Y + 1.55, 0]),
            rrect(2.3, 2.35, PAPER_SCRIBBLE, radius=0.10, stroke_w=4
                  ).move_to([-5.4, GROUND_Y + 1.18, 0]),
            *[Line([-6.35, GROUND_Y + 2.35 - i * 0.45, 0],
                   [-4.45, GROUND_Y + 2.35 - i * 0.45, 0],
                   stroke_color=INK_SOFT, stroke_width=3)
              for i in range(3)],
        ), seed=97)
        self.add(garage)
        self.wait(0.4)

        # -------------------------- beat 1: forklift on its line ---------
        line = crayonify(Line([-3.6, GROUND_Y + 0.02, 0],
                              [2.6, GROUND_Y + 0.02, 0],
                              stroke_color=CARGO_SAGE, stroke_width=7),
                         amp=0.03, seed=96)
        self.play(Create(line), run_time=0.5)
        fk = build_forklift()
        lift = fk["lift"]
        lift.shift(LEFT * 9)
        self.add(lift)
        cap.set("rules: perfect on the line")
        for w in fk["wheels"]:
            w.add_updater(make_roller(0.24))
        self.play(lift.animate.shift(RIGHT * 7.2), run_time=1.5,
                  rate_func=rate_functions.ease_in_out_sine)
        for w in fk["wheels"]:
            w.clear_updaters()
        self.wait(0.3)

        # ----------------- beat 2: a pallet two feet off the line --------
        pallet = crayonify(VGroup(
            rrect(1.15, 0.14, INK_SOFT, radius=0.03).move_to(
                [0.35, GROUND_Y + 0.82, 0]),           # the shelf
            rrect(0.85, 0.22, "#C8A165", radius=0.04).move_to(
                [0.35, GROUND_Y + 1.0, 0]),
            rrect(0.7, 0.5, CARGO_LILAC, radius=0.07).move_to(
                [0.35, GROUND_Y + 1.36, 0]),
        ), seed=95)
        self.play(FadeIn(pallet, shift=DOWN * 0.3), run_time=0.4)
        cap.set("step off the line? it stops", color=ALERT)
        bang = hand_label("!", size=60, color=ALERT)
        bang.move_to(lift.get_top() + UP * 0.45)
        self.play(FadeIn(bang, scale=0.4), run_time=0.3)
        self.wait(1.0)
        self.play(FadeOut(bang), FadeOut(pallet), FadeOut(line),
                  lift.animate.shift(LEFT * 3.2), run_time=0.6)

        # ------------------------------- beat 3: the route van -----------
        cap.set("learned one route. just that route")
        rv = build_route_van()
        van = rv["van"]
        van.shift(LEFT * 9 + RIGHT * 1.0)
        self.add(van)
        cone = crayonify(Polygon(
            [2.2, GROUND_Y, 0], [2.7, GROUND_Y, 0], [2.45, GROUND_Y + 0.6, 0],
            fill_color=ALERT, fill_opacity=1, stroke_color=INK,
            stroke_width=4), seed=94)
        self.play(FadeIn(cone, shift=UP * 0.2), run_time=0.35)
        for w in rv["wheels"]:
            w.add_updater(make_roller(0.25))
        self.play(van.animate.shift(RIGHT * 9.2), run_time=1.4,
                  rate_func=rate_functions.ease_in_sine)
        for w in rv["wheels"]:
            w.clear_updaters()
        # the cone goes flying — the route never changes
        ding = puff([2.45, GROUND_Y + 0.5, 0], n=4, spread=0.4)
        self.play(cone.animate.shift(RIGHT * 1.3 + UP * 0.9
                                     ).rotate(120 * DEGREES),
                  FadeIn(ding), run_time=0.35)
        self.play(FadeOut(ding), FadeOut(cone, shift=DOWN * 1.2),
                  van.animate.shift(RIGHT * 6.5), run_time=0.7)
        self.remove(van)
        self.wait(0.3)

        # ----------------------- beat 4: an engine for anything ----------
        cap.set("then: an engine for anything")
        parts = build_truck(seed=0)
        truck = parts["truck"]
        bare = VGroup(parts["chassis"], parts["wheels"])
        bare.shift(LEFT * 11)
        self.add(bare)
        for w in parts["wheels"]:
            w.add_updater(make_roller(0.40))
        self.play(bare.animate.shift(RIGHT * 11), run_time=1.4,
                  rate_func=rate_functions.ease_out_sine)
        for w in parts["wheels"]:
            w.clear_updaters()

        engine = crayonify(VGroup(
            rrect(1.0, 0.75, AI_TEAL_DARK, radius=0.10),
            *[Circle(radius=0.09, fill_color=AI_TEAL, fill_opacity=1,
                     stroke_color=INK, stroke_width=3
                     ).move_to([x, 0.22, 0]) for x in (-0.28, 0.0, 0.28)],
        ), seed=93)
        engine.move_to([2.05, 4.6, 0])
        chain = Line([2.05, 6.0, 0], [2.05, 5.0, 0], stroke_color=INK,
                     stroke_width=4)
        self.add(engine, chain)
        d = puff([2.05, -1.6, 0])
        self.play(engine.animate.move_to([2.05, -1.35, 0]),
                  chain.animate.shift(DOWN * 3.4), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeIn(d), FadeOut(chain, shift=UP * 2.5), run_time=0.3)
        self.play(FadeOut(d), run_time=0.25)

        # cab + bed close over it: the truck takes shape
        cab_grp = VGroup(parts["cab"], parts["window"], parts["eye"])
        bed_grp = VGroup(parts["bed_back"], parts["bed_front"])
        VGroup(cab_grp, bed_grp).shift(UP * 6.2)
        self.add(cab_grp, bed_grp)
        self.play(cab_grp.animate.shift(DOWN * 6.2), run_time=0.55,
                  rate_func=rate_functions.ease_out_bounce)
        self.remove(engine)
        self.play(bed_grp.animate.shift(DOWN * 6.2), run_time=0.55,
                  rate_func=rate_functions.ease_out_bounce)
        self.wait(0.4)

        # ------------------- beat 5: each generation hauls more ----------
        cap.set("each generation hauls more per gallon")
        plaques = []
        for i, txt in enumerate(("GEN 1", "GEN 2", "GEN 3")):
            p = hand_label(txt, size=30, scrawl=True, color=INK_SOFT)
            p.move_to([-4.5 + i * 2.0, 1.6, 0])
            plaques.append(p)
        drop = hand_label("fuel / load: down, down, down", size=26,
                          color=INK_SOFT)
        drop.move_to([-0.5, 0.9, 0])
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.2) for p in plaques],
                              lag_ratio=0.35), run_time=1.0)
        self.play(FadeIn(drop), run_time=0.4)
        # the truck visibly perks up a touch with each generation
        for _ in range(2):
            self.play(truck.animate.shift(UP * 0.06), run_time=0.22,
                      rate_func=rate_functions.ease_out_back)
            self.play(truck.animate.shift(DOWN * 0.06), run_time=0.18)
        self.wait(0.5)
        self.play(*[FadeOut(p) for p in plaques], FadeOut(drop),
                  run_time=0.4)

        # --------------- beat 6: GAG — next year's truck (probably) ------
        poster = VGroup(
            rrect(3.4, 2.5, "#FFFFFF", radius=0.12, stroke_w=4),
        )
        poster_frame = crayonify(poster, seed=91).move_to([4.3, 1.55, 0])
        # the concept truck: sketchy, dashed, low-opacity — half-drawn
        concept = VGroup(
            rrect(1.7, 0.55, AI_TEAL, radius=0.10).move_to([4.0, 1.25, 0]),
            rrect(0.6, 0.6, AI_TEAL, radius=0.10).move_to([5.15, 1.30, 0]),
            Circle(radius=0.2, fill_opacity=0, stroke_color=INK,
                   stroke_width=3).move_to([3.45, 0.85, 0]),
            Circle(radius=0.2, fill_opacity=0, stroke_color=INK,
                   stroke_width=3).move_to([4.75, 0.85, 0]),
            # rocket on the bed
            Polygon([3.6, 1.55, 0], [3.9, 1.55, 0], [3.75, 2.25, 0],
                    fill_color=CARGO_CORAL, fill_opacity=1,
                    stroke_color=INK, stroke_width=3),
            # wings
            Polygon([4.5, 1.5, 0], [5.3, 1.95, 0], [4.6, 1.75, 0],
                    fill_color=CARGO_LILAC, fill_opacity=1,
                    stroke_color=INK, stroke_width=3),
            # a third crane, obviously
            Line([4.35, 1.55, 0], [4.05, 2.3, 0], stroke_color=INK,
                 stroke_width=4),
            Line([4.05, 2.3, 0], [3.75, 2.05, 0], stroke_color=INK,
                 stroke_width=4),
        )
        # extra-wobbly crayonify + translucent fills = half-drawn concept art
        concept.set_fill(opacity=0.35)
        concept = crayonify(concept, amp=0.06, seed=89)
        concept.set_stroke(opacity=0.75)
        poster_txt = hand_label("NEXT YEAR'S TRUCK (PROBABLY)", size=24,
                                scrawl=True, color=INK_SOFT)
        poster_txt.move_to([4.3, 2.45, 0])
        self.play(FadeIn(poster_frame, shift=UP * 0.25),
                  FadeIn(poster_txt), run_time=0.5)
        self.play(Create(concept), run_time=1.1)
        self.wait(1.1)

        # ----------------------- beat 7: meet today's truck --------------
        cap.set("meet today's truck")
        # the forklift is still there, still working its line
        line2 = crayonify(Line([-6.3, GROUND_Y + 0.02, 0],
                               [-4.2, GROUND_Y + 0.02, 0],
                               stroke_color=CARGO_SAGE, stroke_width=7),
                          amp=0.03, seed=90)
        self.add(line2)
        lift.move_to([-5.3, lift.get_center()[1], 0])
        for w in fk["wheels"]:
            w.add_updater(make_roller(0.24))
        self.play(lift.animate.shift(RIGHT * 0.9), run_time=0.8,
                  rate_func=rate_functions.there_and_back)
        for w in fk["wheels"]:
            w.clear_updaters()
        self.wait(0.6)

        # -------------------------------------------------- beat 8: exit -
        roll(self, parts, RIGHT * 10, 1.7,
             rate_func=rate_functions.ease_in_sine,
             extra_anims=[FadeOut(cap.current), FadeOut(poster_frame),
                          FadeOut(poster_txt), FadeOut(concept)])
        self.play(FadeOut(lift), FadeOut(line2), FadeOut(garage),
                  run_time=0.5)
        self.wait(0.5)
