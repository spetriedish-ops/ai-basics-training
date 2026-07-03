"""
Scene 4 — Pop the Hood: anatomy of an agent (the flagship).

Storyboard: animations/STORYBOARDS.md (Scene 4). The truck assembles part
by part, each labeled as it clicks in:
  engine = the model (tiny paver cameo in a callout bubble)
  bed = context window · attachments = tools · glovebox blueprints = skills
  the loop (LOOK - PICK - WORK - CHECK, two laps, the check catches a
  crooked crate) · the harness = the site (pump, dispatch radio, gate with
  a foreman sign-off — the polite-bounce gag) · subagent van tease.

Render draft:  SCRIBBLE_SEED=1 manim -ql src/scenes/agent_anatomy.py AgentAnatomy
Render final:  ./scripts/boil.sh agent_anatomy AgentAnatomy
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from jobsite import (  # noqa: E402
    CaptionManager, GROUND_Y, build_crane, build_job_card, build_lights,
    build_stage, build_truck, build_van, roll, roll_van, scribble_cargo,
)
from style import (  # noqa: E402
    ALERT, AI_TEAL, AI_TEAL_DARK, CARGO_AMBER, CARGO_CORAL, CARGO_LILAC,
    CARGO_SAGE, INK, INK_SOFT, PAPER_SCRIBBLE, STROKE_W, crayonify,
    hand_label, make_roller, puff, rrect,
)


def tag(text: str, at, target, seed: int) -> VGroup:
    """A hand-scrawled label with a connector line to its part."""
    t = hand_label(text, size=28, scrawl=True).move_to(at)
    line = crayonify(Line(t.get_center() + DOWN * 0.28, target,
                          stroke_color=INK_SOFT, stroke_width=3),
                     amp=0.02, seed=seed)
    return VGroup(t, line)


def mini_paver(center) -> VGroup:
    """Tiny paver cameo (the callback to Scene 2)."""
    cx, cy = center[0], center[1]
    body = rrect(0.78, 0.42, AI_TEAL, radius=0.10).move_to([cx + 0.05, cy, 0])
    funnel = rrect(0.30, 0.22, AI_TEAL_DARK, radius=0.06
                   ).move_to([cx + 0.05, cy + 0.30, 0])
    roller = Circle(radius=0.15, fill_color=INK_SOFT, fill_opacity=1,
                    stroke_color=INK, stroke_width=3
                    ).move_to([cx + 0.42, cy - 0.24, 0])
    bricks = VGroup(*[
        Square(0.16, fill_color=c, fill_opacity=1, stroke_color=INK,
               stroke_width=2).move_to([cx - 0.42 - 0.20 * i, cy - 0.25, 0])
        for i, c in enumerate([CARGO_AMBER, CARGO_CORAL, CARGO_LILAC])
    ])
    return VGroup(bricks, body, funnel, roller)


class AgentAnatomy(Scene):
    def construct(self):
        self.camera.background_color = PAPER_SCRIBBLE
        stage = build_stage("ANATOMY OF AN AGENT", "the parts that make it work")
        self.add(stage)
        cap = CaptionManager(self)
        self.wait(0.4)

        # ------------------------------------- beat 1: chassis rolls in --
        parts = build_truck()
        chassis, wheels = parts["chassis"], parts["wheels"]
        rolling = VGroup(chassis, wheels)
        rolling.shift(LEFT * 11)
        self.add(rolling)
        for w in wheels:
            w.add_updater(make_roller(0.40))
        self.play(rolling.animate.shift(RIGHT * 11), run_time=1.6,
                  rate_func=rate_functions.ease_out_sine)
        for w in wheels:
            w.clear_updaters()
        cap.set("meet the agent, part by part")

        # --------------------------------------- beat 2: engine + cab ----
        cab_grp = VGroup(parts["cab"], parts["window"], parts["eye"])
        cab_grp.shift(UP * 6.2)  # fully above frame — nothing parks in shot
        self.add(cab_grp)
        d1 = puff([2.05, -1.9, 0])
        self.play(cab_grp.animate.shift(DOWN * 6.2), run_time=0.6,
                  rate_func=rate_functions.ease_out_bounce)
        self.play(FadeIn(d1), run_time=0.2)
        self.play(FadeOut(d1), run_time=0.25)

        bubble = crayonify(Circle(radius=0.95, fill_color="#FFFFFF",
                                  fill_opacity=1, stroke_color=INK,
                                  stroke_width=4), seed=60)
        bubble.move_to([4.6, 1.75, 0])
        cameo = crayonify(mini_paver([4.6, 1.75, 0]), seed=61)
        bub_line = crayonify(Line([3.9, 1.1, 0], [2.5, -0.30, 0],
                                  stroke_color=INK_SOFT, stroke_width=3),
                             amp=0.02, seed=62)
        model_tag = hand_label("THE MODEL", size=28, scrawl=True)
        model_tag.move_to([4.6, 0.45, 0])
        cap.set("the model: the prediction engine inside")
        self.play(FadeIn(bubble, scale=0.6), FadeIn(cameo, scale=0.6),
                  Create(bub_line), FadeIn(model_tag), run_time=0.7)
        self.wait(1.0)

        # --------------------------------------------- beat 3: the bed ---
        bed_grp = VGroup(parts["bed_back"], parts["bed_front"])
        bed_grp.shift(UP * 6.2)
        d2 = puff([-0.85, -1.9, 0])
        cap.set("the context window: its working memory")
        self.add(bed_grp)
        self.play(bed_grp.animate.shift(DOWN * 6.2), run_time=0.6,
                  rate_func=rate_functions.ease_out_bounce)
        self.play(FadeIn(d2), run_time=0.2)
        self.play(FadeOut(d2), run_time=0.25)
        bed_tag = tag("CONTEXT WINDOW", [-4.5, 0.55, 0], [-2.75, -0.55, 0],
                      seed=63)
        self.play(FadeIn(bed_tag), run_time=0.5)
        self.wait(0.8)

        # ----------------------------------------------- beat 4: tools ---
        crane = build_crane(seed=50)
        lights = build_lights(seed=52)
        VGroup(crane, lights).shift(UP * 5.2)
        self.add(crane, lights)
        cap.set("tools: what it can do")
        self.play(crane.animate.shift(DOWN * 5.2),
                  lights.animate.shift(DOWN * 5.2),
                  run_time=0.65, rate_func=rate_functions.ease_in_quad)
        tools_tag = tag("TOOLS", [-4.6, 2.75, 0], [-3.1, 1.75, 0], seed=64)
        self.play(FadeIn(tools_tag), run_time=0.5)
        self.wait(0.8)

        # ---------------------------------------------- beat 5: skills ---
        glovebox = crayonify(rrect(0.55, 0.38, AI_TEAL_DARK, radius=0.08,
                                   stroke_w=4), seed=65)
        glovebox.move_to([2.42, -1.62, 0])
        self.play(FadeIn(glovebox), run_time=0.3)

        job = build_job_card("POUR A DRIVEWAY", seed=66, w=2.6, h=0.8)
        job.move_to([8.6, 3.15, 0])
        self.add(job)
        self.play(job.animate.move_to([4.75, 3.15, 0]), run_time=0.6,
                  rate_func=rate_functions.ease_out_sine)

        blueprint = scribble_cargo("HOW-TO", CARGO_LILAC, seed=67,
                                   w=1.05, h=0.55).set_z_index(2)
        blueprint.move_to([2.42, -1.62, 0]).scale(0.35)
        cap.set("skills: how to do jobs well")
        self.play(blueprint.animate.scale(1 / 0.35).move_to([2.42, -0.35, 0]),
                  run_time=0.5, rate_func=rate_functions.ease_out_back)
        self.play(blueprint.animate.move_to([-0.35, -0.50, 0]),
                  run_time=0.6, rate_func=rate_functions.ease_in_out_sine)
        skills_tag = tag("SKILLS", [4.5, -0.65, 0], [2.65, -1.5, 0], seed=68)
        self.play(FadeIn(skills_tag), run_time=0.5)
        self.wait(0.9)

        # --------------------------------------- beats 6-7: the loop -----
        self.play(FadeOut(bubble), FadeOut(cameo), FadeOut(bub_line),
                  FadeOut(model_tag), FadeOut(bed_tag), FadeOut(tools_tag),
                  FadeOut(skills_tag), FadeOut(glovebox), run_time=0.5)

        lc = np.array([4.75, 1.35, 0])  # right side: clear of crane + title
        ring = crayonify(Circle(radius=0.88, stroke_color=INK, stroke_width=4),
                         seed=69).move_to(lc)
        steps = VGroup(
            hand_label("LOOK", size=24, scrawl=True).move_to(lc + UP * 1.18),
            hand_label("PICK", size=24, scrawl=True).move_to(lc + RIGHT * 1.42),
            hand_label("WORK", size=24, scrawl=True).move_to(lc + DOWN * 1.18),
            hand_label("CHECK", size=24, scrawl=True).move_to(lc + LEFT * 1.48),
        )
        marker = Dot(lc + UP * 0.88, radius=0.11, color=AI_TEAL)
        cap.set("look, pick a tool, work, check")
        self.play(FadeIn(ring), FadeIn(steps), FadeIn(marker), run_time=0.6)

        def quarter(k, rt=0.55, **extra):
            arc = Arc(radius=0.88, start_angle=PI / 2 - k * PI / 2,
                      angle=-PI / 2, arc_center=lc)
            anims = [MoveAlongPath(marker, arc)]
            anims += extra.get("with_anims", [])
            self.play(*anims, run_time=rt)

        crate = scribble_cargo("MIX", CARGO_AMBER, seed=70, w=0.95, h=0.60)
        crate.set_z_index(2)
        crate.move_to([-4.6, GROUND_Y + 0.32, 0])  # left, clear of the ring

        # lap 1 — the check catches a crooked crate
        quarter(0, with_anims=[Indicate(steps[0], color=AI_TEAL)])
        quarter(1, with_anims=[Indicate(steps[1], color=AI_TEAL)])
        self.add(crate)
        quarter(2, rt=0.8, with_anims=[
            crate.animate.move_to([0.45, -0.38, 0]).rotate(16 * DEGREES)])
        bang = hand_label("!", size=54, color=ALERT).move_to([0.85, 0.45, 0])
        quarter(3, with_anims=[FadeIn(bang, scale=0.5),
                               Indicate(steps[3], color=ALERT)])
        # lap 2 — go again, fix it, done
        cap.set("and go again until it's done")
        quarter(0, rt=0.4)
        quarter(1, rt=0.4)
        quarter(2, rt=0.7, with_anims=[
            crate.animate.rotate(-16 * DEGREES).shift(DOWN * 0.07),
            FadeOut(bang)])
        check = hand_label("done!", size=34, color=AI_TEAL_DARK)
        check.next_to(job, LEFT, buff=0.25)
        quarter(3, with_anims=[FadeIn(check, scale=0.6)])
        self.wait(0.8)

        # --------------------------------------------- beat 8: harness ---
        self.play(FadeOut(ring), FadeOut(steps), FadeOut(marker),
                  FadeOut(check), FadeOut(job), run_time=0.5)

        pump = crayonify(VGroup(
            rrect(0.75, 1.15, CARGO_AMBER, radius=0.12
                  ).move_to([-6.35, GROUND_Y + 0.58, 0]),
            rrect(0.42, 0.28, PAPER_SCRIBBLE, radius=0.06, stroke_w=3
                  ).move_to([-6.35, GROUND_Y + 0.85, 0]),
            ArcBetweenPoints([-5.98, GROUND_Y + 0.75, 0],
                             [-5.55, GROUND_Y + 0.25, 0], angle=-1.2,
                             stroke_color=INK, stroke_width=4),
        ), seed=71)
        radio = crayonify(VGroup(
            Line([-5.05, GROUND_Y, 0], [-5.05, 0.45, 0], stroke_color=INK,
                 stroke_width=STROKE_W),
            Polygon([-5.05, 0.45, 0], [-4.55, 0.80, 0], [-4.55, 0.28, 0],
                    fill_color=INK_SOFT, fill_opacity=1, stroke_color=INK,
                    stroke_width=4),
            Arc(radius=0.28, start_angle=-0.6, angle=1.2,
                stroke_color=INK_SOFT, stroke_width=3
                ).move_to([-4.15, 0.62, 0]),
            Arc(radius=0.45, start_angle=-0.6, angle=1.2,
                stroke_color=INK_SOFT, stroke_width=3
                ).move_to([-3.90, 0.70, 0]),
        ), seed=72)
        rail_y = GROUND_Y + 0.85
        fence = crayonify(VGroup(
            *[rrect(0.16, 1.15, "#D8CBB2", radius=0.05, stroke_w=4
                    ).move_to([x, GROUND_Y + 0.58, 0])
              for x in (6.15, 6.75)],
            Line([5.95, rail_y, 0], [7.2, rail_y, 0], stroke_color=INK,
                 stroke_width=4),
        ), seed=73)
        gate = crayonify(VGroup(
            rrect(0.16, 1.15, "#D8CBB2", radius=0.05, stroke_w=4
                  ).move_to([5.75, GROUND_Y + 0.58, 0]),
            Line([5.05, rail_y - 0.28, 0], [5.72, rail_y - 0.02, 0],
                 stroke_color=INK, stroke_width=STROKE_W),
        ), seed=74)

        cap.set("the harness: the site around it")
        self.play(FadeIn(pump, shift=UP * 0.2), FadeIn(radio, shift=UP * 0.2),
                  FadeIn(fence, shift=UP * 0.2), FadeIn(gate, shift=UP * 0.2),
                  run_time=0.7)
        self.wait(0.9)

        # ------------------------------------------ beat 9: gate gag -----
        truck = parts["truck"]
        truck.add(crane, lights)
        aboard = VGroup(blueprint, crate)
        cap.set("gates and sign-offs keep it safe")
        roll(self, parts, RIGHT * 2.1, 1.0,
             rate_func=rate_functions.ease_in_out_sine,
             extra_mobs=[aboard])
        # the polite bounce
        self.play(VGroup(truck, aboard).animate.shift(RIGHT * 0.22),
                  gate.animate.rotate(6 * DEGREES,
                                      about_point=[5.75, GROUND_Y, 0]),
                  run_time=0.18)
        self.play(VGroup(truck, aboard).animate.shift(LEFT * 0.30),
                  gate.animate.rotate(-6 * DEGREES,
                                      about_point=[5.75, GROUND_Y, 0]),
                  run_time=0.25)
        stamp = crayonify(VGroup(
            rrect(1.9, 0.7, "#FFFFFF", radius=0.10, stroke=AI_TEAL_DARK),
        ), seed=75).rotate(-8 * DEGREES).move_to([5.5, 1.1, 0])
        stamp_txt = hand_label("APPROVED", size=30, scrawl=True,
                               color=AI_TEAL_DARK)
        stamp_txt.rotate(-8 * DEGREES).move_to([5.5, 1.1, 0])
        self.play(FadeIn(VGroup(stamp, stamp_txt), scale=1.6), run_time=0.35)
        d3 = puff([5.6, GROUND_Y + 0.3, 0])
        self.play(gate.animate.rotate(-75 * DEGREES,
                                      about_point=[5.75, GROUND_Y, 0]),
                  FadeIn(d3), run_time=0.5)
        self.play(FadeOut(d3), run_time=0.25)
        self.wait(0.6)

        # ------------------------------------------ beat 10: van tease ---
        vp = build_van(seed=76, scale=0.85)
        van = vp["van"]
        van.shift(LEFT * 11 + RIGHT * 3.2)  # park left of the truck
        self.add(van)
        roll_van(self, vp, RIGHT * 4.6, 1.1,
                 rate_func=rate_functions.ease_out_sine)
        cap.set("and sometimes... it calls for backup")
        self.wait(1.0)

        # ----------------------------------------------- beat 11: exit ---
        exit_anims = [FadeOut(m) for m in (pump, radio, stamp, stamp_txt)]
        roll(self, parts, RIGHT * 9, 1.6,
             rate_func=rate_functions.ease_in_sine,
             extra_mobs=[aboard, van],
             extra_anims=exit_anims + [FadeOut(cap.current)])
        self.play(FadeOut(fence), FadeOut(gate), run_time=0.4)
        self.wait(0.5)
