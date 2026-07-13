"""
Scene 6 — The Toolbox: the MCP analogy.

From Sarah's sketch (assets/sketches/03): an agent using an MCP is like
opening a box of tools with no training beyond an instruction card. The
more tools in the box, the more you can do — and the more likely you grab
the wrong one. And a full toolbox is heavy: the cards cost tokens, used
or not. Distinct job from Truck v2: that scene teaches WEIGHT; this one
teaches SELECTION and ends on the fix — curate the box.

Beats:
  1. one MCP box arrives — a whole toolbox from one connection
  2. it pops open: four tools, four instruction cards into the bed
  3. capability demo: the right tool handles a job, easy
  4. GAG escalation: two more boxes ("surely one more box"), meter red
  5. a simple job — and a tool from the WRONG box grabs it
  6. the fix: unbolt the extra boxes, right tool, done
  7. exit

Render draft:  SCRIBBLE_SEED=1 manim -ql src/scenes/toolbox.py Toolbox
Render final:  ./scripts/boil.sh toolbox Toolbox
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from jobsite import (  # noqa: E402
    CaptionManager, GROUND_Y, build_job_card, build_meter, build_stage,
    build_truck, roll, scribble_cargo,
)
from style import (  # noqa: E402
    ALERT, AI_TEAL, AI_TEAL_DARK, CARGO_AMBER, CARGO_CORAL, CARGO_LILAC,
    CARGO_SAGE, INK, INK_SOFT, PAPER_SCRIBBLE, STROKE_W, crayonify,
    hand_label, puff, rrect,
)


def build_toolbox(label: str, fill: str, seed: int) -> dict:
    """A tool chest: body, hinged lid, scrawled service name."""
    body = rrect(1.5, 0.55, fill, radius=0.10)
    body.move_to([0, -0.14, 0])
    lid = rrect(1.5, 0.26, fill, radius=0.10)
    lid.move_to([0, 0.27, 0])
    clasp = Dot([0, 0.02, 0], radius=0.05, color=INK)
    tag = hand_label(label, size=24, scrawl=True)
    tag.scale_to_fit_width(min(tag.width, 1.2))
    tag.move_to([0, -0.14, 0])
    g = crayonify(VGroup(body, lid, clasp), seed=seed)
    return {"box": VGroup(g, tag), "lid": g}


def build_tool(kind: str, seed: int) -> VGroup:
    """Chunky tool silhouettes, all teal (abilities are the agent's)."""
    if kind == "wrench":
        shaft = rrect(0.14, 0.62, AI_TEAL, radius=0.06)
        head = Circle(radius=0.17, fill_color=AI_TEAL, fill_opacity=1,
                      stroke_color=INK, stroke_width=4).move_to([0, 0.38, 0])
        notch = Circle(radius=0.08, fill_color=PAPER_SCRIBBLE, fill_opacity=1,
                       stroke_width=0).move_to([0, 0.44, 0])
        g = VGroup(shaft, head, notch)
    elif kind == "hammer":
        shaft = rrect(0.13, 0.60, CARGO_AMBER, radius=0.06)
        head = rrect(0.46, 0.20, AI_TEAL, radius=0.07).move_to([0, 0.36, 0])
        g = VGroup(shaft, head)
    elif kind == "mallet":
        shaft = rrect(0.15, 0.70, CARGO_AMBER, radius=0.06)
        head = rrect(0.55, 0.30, AI_TEAL_DARK, radius=0.10
                     ).move_to([0, 0.44, 0])
        g = VGroup(shaft, head)
    elif kind == "screwdriver":
        shaft = rrect(0.09, 0.42, INK_SOFT, radius=0.04
                      ).move_to([0, -0.12, 0])
        handle = rrect(0.18, 0.34, AI_TEAL, radius=0.07
                       ).move_to([0, 0.24, 0])
        g = VGroup(shaft, handle)
    else:  # pen (comment)
        body = rrect(0.14, 0.52, AI_TEAL, radius=0.06)
        tip = Polygon([-0.07, -0.26, 0], [0.07, -0.26, 0], [0, -0.42, 0],
                      fill_color=INK, fill_opacity=1, stroke_color=INK,
                      stroke_width=3)
        g = VGroup(body, tip)
    return crayonify(g, seed=seed)


class Toolbox(Scene):
    def construct(self):
        self.camera.background_color = PAPER_SCRIBBLE
        stage = build_stage("THE MCP TOOLBOX", "one connection, many tools")
        self.add(stage)
        cap = CaptionManager(self)
        self.wait(0.4)

        # ------------------------------------------- beat 1: arrival -----
        parts = build_truck()
        truck = parts["truck"]
        truck.shift(LEFT * 11)
        self.add(truck)
        roll(self, parts, RIGHT * 11, 1.6,
             rate_func=rate_functions.ease_out_sine)

        md = build_meter()
        meter, bar = md["meter"], md["fill"]
        self.play(FadeIn(meter, shift=DOWN * 0.2), run_time=0.4)
        cap.set("one connection brings a whole toolbox")

        def tick(w, color=None):
            a = bar.animate.stretch_to_fit_width(w, about_edge=LEFT)
            return a.set_fill(color) if color else a

        tb1 = build_toolbox("TICKETS", CARGO_LILAC, seed=50)
        box1 = tb1["box"]
        box1.move_to([-1.55, 0.09, 0]).shift(UP * 5.0)
        self.add(box1)
        d1 = puff([-1.55, -0.25, 0])
        self.play(box1.animate.shift(DOWN * 5.0), run_time=0.6,
                  rate_func=rate_functions.ease_in_quad)
        self.play(FadeIn(d1), run_time=0.2)
        self.play(FadeOut(d1), run_time=0.25)
        truck.add(box1)
        self.wait(0.3)

        # ----------------------------- beat 2: pop open, cards billed ----
        cap.set("every tool ships an instruction card")
        kinds = ["wrench", "hammer", "screwdriver", "pen"]
        names = ["SEARCH", "CREATE", "UPDATE", "COMMENT"]
        fan_x = [-4.05, -2.75, -1.45, -0.15]
        tools, tool_tags = [], []
        for kind, name, fx, s in zip(kinds, names, fan_x, range(60, 64)):
            t = build_tool(kind, seed=s)
            t.move_to([-1.55, 0.25, 0]).scale(0.3)
            tools.append(t)
            tag = hand_label(name, size=20, scrawl=True, color=INK_SOFT)
            tag.move_to([fx, 0.85, 0])
            tool_tags.append(tag)
        for t, tag, fx in zip(tools, tool_tags, fan_x):
            self.add(t)
            self.play(t.animate.scale(1 / 0.3).move_to([fx, 1.55, 0]),
                      FadeIn(tag), run_time=0.28,
                      rate_func=rate_functions.ease_out_back)

        cards = []
        card_slots = [[-2.10, -1.19, 0], [-1.20, -1.19, 0],
                      [-0.30, -1.19, 0], [0.60, -1.19, 0]]
        widths = [0.55, 0.95, 1.35, 1.75]
        for name, slot, w, s in zip(names, card_slots, widths,
                                    range(70, 74)):
            c = scribble_cargo(name, CARGO_LILAC, seed=s, w=0.85, h=0.48)
            c.set_z_index(2)
            c.move_to([slot[0], 3.6, 0])
            self.add(c)
            cards.append(c)
            self.play(c.animate.move_to(slot), tick(w),
                      run_time=0.3, rate_func=rate_functions.ease_out_quad)
        cap.set("the cards ride along, used or not")
        self.play(VGroup(truck, *cards).animate.shift(DOWN * 0.06),
                  run_time=0.3)
        self.wait(0.5)

        # ------------------------------- beat 3: the right tool, easy ----
        job1 = build_job_card("FIND TICKET 42", seed=80, w=2.5, h=0.75)
        job1.move_to([-4.6, 2.55, 0]).shift(UP * 3)
        self.play(job1.animate.shift(DOWN * 3), run_time=0.5,
                  rate_func=rate_functions.ease_out_sine)
        cap.set("more tools, more you can do")
        wrench = tools[0]
        self.play(wrench.animate.move_to([-4.85, 1.55, 0]).rotate(-25 * DEGREES),
                  run_time=0.45)
        spark = crayonify(Star(n=4, outer_radius=0.22, inner_radius=0.08,
                               fill_color=CARGO_AMBER, fill_opacity=1,
                               stroke_width=0), seed=81)
        spark.move_to([-3.9, 2.35, 0])
        done1 = hand_label("found!", size=26, scrawl=True,
                           color=AI_TEAL_DARK)
        done1.next_to(job1, RIGHT, buff=0.2)
        self.play(FadeIn(spark, scale=0.4), FadeIn(done1), run_time=0.35)
        self.play(FadeOut(spark, scale=1.5),
                  wrench.animate.move_to([fan_x[0], 1.55, 0]
                                         ).rotate(25 * DEGREES),
                  run_time=0.45)
        self.wait(0.5)
        self.play(FadeOut(job1), FadeOut(done1), run_time=0.35)

        # --------------------------- beat 4: GAG — surely one more box ---
        cap.set("surely one more box")
        tb2 = build_toolbox("CALENDAR", CARGO_AMBER, seed=51)
        box2 = tb2["box"]
        box2.move_to([0.15, 0.09, 0]).shift(UP * 4.6)
        self.add(box2)
        extra2 = []
        for name, slot, s in zip(["MEET", "INVITE", "REMIND"],
                                 [[-2.10, -0.60, 0], [-1.20, -0.60, 0],
                                  [-0.30, -0.60, 0]], range(74, 77)):
            c = scribble_cargo(name, CARGO_AMBER, seed=s, w=0.85, h=0.48)
            c.set_z_index(2)
            c.move_to([slot[0], 3.6, 0])
            extra2.append((c, slot))
        self.play(box2.animate.shift(DOWN * 4.6),
                  VGroup(truck, *cards).animate.shift(DOWN * 0.05),
                  run_time=0.5, rate_func=rate_functions.ease_in_quad)
        truck.add(box2)
        for c, slot in extra2:
            self.add(c)
            self.play(c.animate.move_to(slot), tick(2.0),
                      run_time=0.22, rate_func=rate_functions.ease_out_quad)

        tb3 = build_toolbox("WIKI", CARGO_SAGE, seed=52)
        box3 = tb3["box"]
        box3.move_to([-1.55, 0.85, 0]).shift(UP * 4.4)  # stacks on box 1
        self.add(box3)
        extra3 = []
        for name, slot, s in zip(["PAGE", "EDIT", "LINK"],
                                 [[0.60, -0.60, 0], [-2.10, -0.02, 0],
                                  [-1.20, -0.02, 0]], range(77, 80)):
            c = scribble_cargo(name, CARGO_SAGE, seed=s, w=0.85, h=0.48)
            c.set_z_index(2)
            c.move_to([slot[0], 3.6, 0])
            extra3.append((c, slot))
        all_cards = VGroup(*cards, *[c for c, _ in extra2])
        self.play(box3.animate.shift(DOWN * 4.4),
                  VGroup(truck, all_cards).animate.shift(DOWN * 0.05),
                  run_time=0.5, rate_func=rate_functions.ease_in_quad)
        truck.add(box3)
        for c, slot in extra3:
            self.add(c)
            self.play(c.animate.move_to(slot),
                      tick(2.34, ALERT),
                      run_time=0.22, rate_func=rate_functions.ease_out_quad)
        self.wait(0.5)

        # ------------------------------ beat 5: the wrong tool grabs -----
        job2 = build_job_card("COMMENT ON 42", seed=82, w=2.5, h=0.75)
        job2.move_to([-4.6, 2.55, 0]).shift(UP * 3)
        self.play(job2.animate.shift(DOWN * 3), run_time=0.5,
                  rate_func=rate_functions.ease_out_sine)
        cap.set("so many tools it grabs the wrong one", color=ALERT)

        # tools twitch, unsure...
        self.play(*[t.animate.shift(UP * 0.12) for t in tools],
                  run_time=0.18)
        self.play(*[t.animate.shift(DOWN * 0.12) for t in tools],
                  run_time=0.18)
        # ...and the CALENDAR mallet lunges for a commenting job
        mallet = build_tool("mallet", seed=64)
        mallet.move_to([0.15, 0.35, 0]).scale(0.3)
        self.add(mallet)
        self.play(mallet.animate.scale(1 / 0.3).move_to([-4.0, 1.7, 0]
                                                        ).rotate(35 * DEGREES),
                  run_time=0.5, rate_func=rate_functions.ease_out_back)
        bonk = puff([-4.35, 2.15, 0], n=4, spread=0.4)
        qmark = hand_label("?", size=80, color=ALERT)
        qmark.move_to([2.05, 0.9, 0])
        self.play(mallet.animate.shift(UP * 0.35 + LEFT * 0.3),
                  FadeIn(bonk), FadeIn(qmark, scale=0.4),
                  job2.animate.rotate(-6 * DEGREES).shift(DOWN * 0.1),
                  run_time=0.3)
        self.play(FadeOut(bonk), run_time=0.3)
        self.wait(0.8)

        # ------------------------------------ beat 6: curate the box -----
        cap.set("curate the toolbox for the job")
        gone_cards = VGroup(*[c for c, _ in extra2], *[c for c, _ in extra3])
        truck.remove(box2, box3)
        d2 = puff([2.6, GROUND_Y + 0.3, 0], n=3, spread=0.4)
        self.play(
            FadeOut(qmark),
            mallet.animate.shift(RIGHT * 4.5 + DOWN * 3.5).rotate(50 * DEGREES),
            box2.animate.shift(RIGHT * 3.2 + DOWN * 2.6).rotate(18 * DEGREES),
            box3.animate.shift(RIGHT * 4.0 + DOWN * 3.4).rotate(-14 * DEGREES),
            FadeOut(gone_cards, shift=RIGHT * 1.5 + DOWN * 0.5),
            tick(1.75, AI_TEAL),
            run_time=0.7, rate_func=rate_functions.ease_in_quad,
        )
        self.play(FadeIn(d2), FadeOut(VGroup(mallet, box2, box3)),
                  VGroup(truck, *cards).animate.shift(UP * 0.10),
                  run_time=0.4)
        self.play(FadeOut(d2), run_time=0.25)

        pen = tools[3]
        self.play(pen.animate.move_to([-4.5, 1.6, 0]).rotate(-30 * DEGREES),
                  run_time=0.45)
        check = hand_label("done!", size=26, scrawl=True, color=AI_TEAL_DARK)
        check.next_to(job2, RIGHT, buff=0.2)
        self.play(job2.animate.rotate(6 * DEGREES).shift(UP * 0.1),
                  FadeIn(check, scale=0.6), run_time=0.4)
        self.wait(0.9)

        # ------------------------------------------------ beat 7: exit ---
        self.play(FadeOut(job2), FadeOut(check),
                  *[FadeOut(t) for t in tools],
                  *[FadeOut(t) for t in tool_tags],
                  *[FadeOut(c) for c in cards],
                  run_time=0.5)
        truck.remove(box1)
        roll(self, parts, RIGHT * 11, 1.7,
             rate_func=rate_functions.ease_in_sine,
             extra_mobs=[box1],
             extra_anims=[FadeOut(cap.current), FadeOut(meter)])
        self.wait(0.5)
