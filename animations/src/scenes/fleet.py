"""
Scene 5 — The Fleet: subagents & orchestration.

Storyboard: animations/STORYBOARDS.md (Scene 5):
  * the chief truck faces a job too big alone (BUILD THE SHED)
  * ONE van first: dispatched, works at its own corner with its OWN bed
    and OWN fuel meter, returns with ONE wrapped package (only the result)
  * scale up: three specialists in parallel, the shed assembles
  * GAG: over-delegation — vans everywhere, two collide, one dispatches
    its own van, package avalanche buries the chief
  * recovery: three vans, staggered, smooth; golden-hour wide.

Render draft:  SCRIBBLE_SEED=1 manim -ql src/scenes/fleet.py Fleet
Render final:  ./scripts/boil.sh fleet Fleet
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from jobsite import (  # noqa: E402
    CaptionManager, GROUND_Y, build_job_card, build_meter, build_package,
    build_stage, build_truck, build_van, roll, roll_van,
)
from style import (  # noqa: E402
    ALERT, CARGO_AMBER, CARGO_CORAL, CARGO_SAGE, INK, INK_SOFT,
    PAPER_SCRIBBLE, STROKE_W, crayonify, hand_label, make_roller, puff,
    rrect,
)


def radio_waves(at, seed: int = 90) -> VGroup:
    return crayonify(VGroup(
        Arc(radius=0.22, start_angle=-0.5, angle=1.0, stroke_color=INK_SOFT,
            stroke_width=3).move_to(at),
        Arc(radius=0.38, start_angle=-0.5, angle=1.0, stroke_color=INK_SOFT,
            stroke_width=3).move_to(at + RIGHT * 0.18),
    ), seed=seed)


def drive(scene, van_parts_list, anims, rt, rate_func=None):
    """Play `anims` with every listed van's wheels rolling."""
    for vp in van_parts_list:
        for w in vp["wheels"]:
            w.add_updater(make_roller(w.width / 2))
    kw = {"run_time": rt}
    if rate_func is not None:
        kw["rate_func"] = rate_func
    scene.play(*anims, **kw)
    for vp in van_parts_list:
        for w in vp["wheels"]:
            w.clear_updaters()


class Fleet(Scene):
    def construct(self):
        self.camera.background_color = PAPER_SCRIBBLE
        stage = build_stage("SUBAGENTS & THE FLEET",
                            "many hands, one jobsite")
        self.add(stage)
        cap = CaptionManager(self)
        self.wait(0.4)

        # ------------------------------------ beat 1: the big job --------
        parts = build_truck(seed=0)
        truck = parts["truck"]
        truck.shift(LEFT * 11)
        self.add(truck)
        roll(self, parts, RIGHT * 7.3, 1.6,   # chief parks left of center
             rate_func=rate_functions.ease_out_sine)

        job = build_job_card("BUILD THE SHED", seed=85, w=2.9, h=0.9)
        job.move_to([-3.7, 2.6, 0])
        self.play(FadeIn(job, shift=DOWN * 0.25), run_time=0.5)
        cap.set("some jobs are too big alone")
        self.wait(0.7)

        # ------------------------------- beat 2: dispatch one van --------
        cap.set("a subagent goes off to work")
        waves = radio_waves(np.array([-1.3, -0.35, 0]))
        self.play(FadeIn(waves), run_time=0.3)
        self.play(FadeOut(waves), run_time=0.3)

        vp = build_van(seed=70, scale=0.9)
        van = vp["van"]
        van.shift(LEFT * 1.0)   # pops out from behind the chief
        self.play(FadeIn(van, shift=RIGHT * 0.3), run_time=0.35)
        roll_van(self, vp, RIGHT * 5.2, 1.3,
                 rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.3)

        # ----------------------- beat 3: its own bed, its own fuel -------
        cap.set("its own bed. its own fuel")
        mini_meter = build_meter(seed=95)
        mm = mini_meter["meter"]
        mm.scale(0.62)
        mm.next_to(van, UP, buff=0.55)
        self.play(FadeIn(mm, shift=DOWN * 0.2), run_time=0.4)
        micro = crayonify(rrect(0.55, 0.35, CARGO_SAGE, radius=0.06,
                                stroke_w=3), seed=96)
        micro.move_to(van.get_center() + UP * 2.4)
        self.add(micro)
        self.play(micro.animate.move_to(van.get_center() + UP * 0.25),
                  mini_meter["fill"].animate.stretch_to_fit_width(
                      0.9, about_edge=LEFT),
                  run_time=0.5, rate_func=rate_functions.ease_out_bounce)
        work = puff(van.get_center() + RIGHT * 1.2 + DOWN * 0.4, n=4,
                    spread=0.45)
        self.play(FadeIn(work), run_time=0.3)
        self.play(FadeOut(work), run_time=0.3)
        self.wait(0.4)

        # -------------------- beat 4: back with only the result ----------
        cap.set("it brings back only the result")
        pkg = build_package(seed=80)
        pkg.move_to(van.get_center() + UP * 0.95)
        self.play(FadeIn(pkg, scale=0.5),
                  FadeOut(mm), FadeOut(micro), run_time=0.4)
        drive(self, [vp],
              [van.animate.shift(LEFT * 5.2), pkg.animate.shift(LEFT * 5.2)],
              rt=1.2, rate_func=rate_functions.ease_in_out_sine)
        pkg.set_z_index(2)
        self.play(pkg.animate.move_to([-4.55, -0.55, 0]),
                  run_time=0.5, rate_func=rate_functions.ease_out_bounce)
        self.play(FadeOut(van), run_time=0.3)
        self.wait(0.5)

        # ------------------ beat 5: three specialists in parallel --------
        cap.set("one coordinator, many specialists")
        waves2 = radio_waves(np.array([-1.3, -0.35, 0]), seed=91)
        self.play(FadeIn(waves2), run_time=0.25)
        self.play(FadeOut(waves2), run_time=0.25)

        starts = [-0.6, -0.1, 0.4]
        outs = [2.6, 4.4, 6.2]
        vans = []
        for st, out, s in zip(starts, outs, (100, 110, 120)):
            vpi = build_van(seed=s, scale=0.72)
            vpi["van"].shift(RIGHT * st)
            vans.append((vpi, out))
        self.play(*[FadeIn(vpi["van"], shift=RIGHT * 0.3)
                    for vpi, _ in vans], run_time=0.35)
        drive(self, [vpi for vpi, _ in vans],
              [vpi["van"].animate.shift(RIGHT * (out - st))
               for (vpi, out), st in zip(vans, starts)],
              rt=1.1, rate_func=rate_functions.ease_in_out_sine)
        pf = VGroup(*[puff([out + 0.4, GROUND_Y + 0.5, 0], n=3, spread=0.35)
                      for (_, out) in vans])
        self.play(FadeIn(pf), run_time=0.35)
        self.play(FadeOut(pf), run_time=0.35)

        # the shed assembles as the specialists head home
        shed_x = 4.9
        wall_l = crayonify(rrect(0.22, 1.3, CARGO_AMBER, radius=0.05
                                 ).move_to([shed_x - 0.85, GROUND_Y + 0.65, 0]),
                           seed=130)
        wall_r = crayonify(rrect(0.22, 1.3, CARGO_AMBER, radius=0.05
                                 ).move_to([shed_x + 0.85, GROUND_Y + 0.65, 0]),
                           seed=131)
        roof = crayonify(Polygon(
            [shed_x - 1.15, GROUND_Y + 1.28, 0],
            [shed_x + 1.15, GROUND_Y + 1.28, 0],
            [shed_x, GROUND_Y + 2.15, 0],
            fill_color=CARGO_CORAL, fill_opacity=1, stroke_color=INK,
            stroke_width=STROKE_W), seed=132)
        door = crayonify(rrect(0.55, 0.85, CARGO_SAGE, radius=0.07
                               ).move_to([shed_x, GROUND_Y + 0.43, 0]),
                         seed=133)
        shed = VGroup(wall_l, wall_r, roof, door)
        shed.shift(UP * 5.8)
        self.add(shed)
        drive(self, [vpi for vpi, _ in vans],
              [shed.animate.shift(DOWN * 5.8)] +
              [vpi["van"].animate.shift(LEFT * (out + 10))
               for (vpi, out) in vans],
              rt=0.9, rate_func=rate_functions.ease_out_sine)
        self.wait(0.5)

        # ------------------------- beat 6: GAG — over-delegation ---------
        cap.set("coordination is also a job", color=ALERT)
        gag = []
        gag_starts = [-0.7, -0.2, 0.3, 0.8]
        for i, (st, s) in enumerate(zip(gag_starts, (140, 150, 160, 170))):
            vpi = build_van(seed=s, scale=0.52 if i % 2 else 0.6)
            vpi["van"].shift(RIGHT * st)
            gag.append(vpi)
        self.play(*[FadeIn(vpi["van"], shift=RIGHT * 0.25) for vpi in gag],
                  run_time=0.3)
        drive(self, gag, [
            gag[0]["van"].animate.shift(RIGHT * 2.6),
            gag[1]["van"].animate.shift(RIGHT * 5.7),
            gag[2]["van"].animate.shift(RIGHT * 1.1),
            gag[3]["van"].animate.shift(RIGHT * 1.4),
        ], rt=0.8, rate_func=rate_functions.ease_in_out_sine)
        # two of them meet in the middle
        bonk = puff([1.75, GROUND_Y + 0.6, 0], n=5, spread=0.5)
        self.play(gag[2]["van"].animate.shift(RIGHT * 0.35
                                              ).rotate(6 * DEGREES),
                  gag[3]["van"].animate.shift(LEFT * 0.35
                                              ).rotate(-8 * DEGREES),
                  FadeIn(bonk), run_time=0.3)
        self.play(FadeOut(bonk), run_time=0.25)
        # one van dispatches its OWN tiny van
        baby = build_van(seed=180, scale=0.3)
        baby["van"].move_to(gag[1]["van"].get_center() + DOWN * 0.15)
        self.add(baby["van"])
        self.play(baby["van"].animate.shift(RIGHT * 1.5), run_time=0.5)
        # package avalanche buries the chief
        pkgs = VGroup(*[
            build_package(seed=200 + i, w=0.7 - 0.06 * (i % 3))
            for i in range(7)
        ])
        for i, p in enumerate(pkgs):
            p.move_to([-5.6 + (i % 4) * 0.75, 3.4 + (i // 4) * 0.9, 0])
        self.add(pkgs)
        targets = [[-5.7, -0.5, 0], [-4.9, -0.4, 0], [-4.1, -0.55, 0],
                   [-3.3, -0.45, 0], [-5.3, 0.25, 0], [-4.5, 0.35, 0],
                   [-3.7, 0.28, 0]]
        self.play(*[p.animate.move_to(t) for p, t in zip(pkgs, targets)],
                  run_time=0.7, rate_func=rate_functions.ease_in_quad)
        d = puff([-4.5, GROUND_Y + 0.6, 0], n=5, spread=0.7)
        self.play(FadeIn(d), truck.animate.shift(DOWN * 0.12), run_time=0.3)
        self.play(FadeOut(d), run_time=0.3)
        self.wait(0.8)

        # ----------------------------- beat 7: recovery + golden hour ----
        cap.set("three vans, on a schedule")
        self.play(FadeOut(pkgs, shift=DOWN * 0.4),
                  *[FadeOut(vpi["van"]) for vpi in gag],
                  FadeOut(baby["van"]),
                  truck.animate.shift(UP * 0.12),
                  run_time=0.6)
        # all three exited to x = -10; roll back in, staggered, clear of
        # the shed (left wall at x ≈ 3.8)
        parked = [-0.6, 0.9, 2.4]
        drive(self, [vpi for vpi, _ in vans],
              [vpi["van"].animate.shift(RIGHT * (10 + px))
               for (vpi, _), px in zip(vans, parked)],
              rt=1.2, rate_func=rate_functions.ease_out_sine)
        self.wait(0.4)

        sun = stage[1]
        cap.set("now you can read the whole site")
        self.play(sun.animate.scale(1.35).shift(DOWN * 0.15), run_time=0.8)
        self.wait(1.2)

        # ------------------------------------------------ beat 8: exit ---
        self.play(FadeOut(job), FadeOut(pkg),
                  *[FadeOut(vpi["van"]) for vpi, _ in vans],
                  FadeOut(shed), FadeOut(cap.current), run_time=0.7)
        roll(self, parts, RIGHT * 13, 1.7,
             rate_func=rate_functions.ease_in_sine)
        self.play(sun.animate.scale(1 / 1.35).shift(UP * 0.15), run_time=0.4)
        self.wait(0.5)
