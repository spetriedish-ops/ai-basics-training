"""
Preamble clips P01-P11 — visuals under Sarah's recorded narration.

Treatment approved 2026-07-15 (see PREAMBLE section in RUN-OF-SHOW.md).
Design rules for this set:
  * NO titles/captions — the voiceover carries the words. Drawn text
    appears only where the text IS the content (ledger cards, seat card,
    series title).
  * No vendor names in pixels; the narration names names.
  * Every clip ends on a ~3 s static hold (boil-alive) so the editor can
    stretch it against the narration.
  * Sincere register: the labor-economics beats (P06, P08) get no gags.

Draft one:   SCRIBBLE_SEED=1 manim -ql src/scenes/preamble.py Preamble01
Boil batch:  see scripts/preamble_batch.sh
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from jobsite import (  # noqa: E402
    GROUND_Y, build_crane, build_job_card, build_package, build_truck,
    build_van, roll, roll_van, scribble_cargo,
)
from style import (  # noqa: E402
    ALERT, AI_TEAL, AI_TEAL_DARK, CARGO_AMBER, CARGO_CORAL, CARGO_LILAC,
    CARGO_SAGE, INK, INK_SOFT, PAPER_SCRIBBLE, STROKE_W, crayonify,
    hand_label, puff, rrect,
)

# Global tempo (Sarah, 2026-08-10: everything moved too fast and clips
# ran short for the talk track). Movements play 1.5x slower, pauses sit
# 1.7x longer, and the final hold lands around 7 s after pacing.
PACE_PLAY = 1.5
PACE_WAIT = 1.7
HOLD = 4.0   # final boil-alive hold on every clip (~6.8 s after pacing)


class PacedScene(Scene):
    """Scene with the preamble's global tempo applied uniformly.

    run_time uses a None sentinel: Scene.wait() internally calls
    self.play(Wait(...)) with NO run_time kwarg, and a plain default
    here would clobber every wait down to the default length.
    """

    def play(self, *args, run_time=None, **kwargs):
        if run_time is not None:
            kwargs["run_time"] = run_time * PACE_PLAY
        super().play(*args, **kwargs)

    def wait(self, duration=1.0, **kwargs):
        super().wait(duration * PACE_WAIT, **kwargs)


def stage_min(scene):
    """Ground + sun only — no title; narration owns the words."""
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
               stroke_color=INK, stroke_width=4), rays,
    ), seed=98).move_to([-6.2, 3.15, 0])
    scene.add(ground, sun)
    return ground, sun


def stickfig(seed=200, scale=1.0, arm_up=False):
    """A pencil person: the audience's stand-in. Kept neutral and warm."""
    head = Circle(radius=0.22, fill_color=PAPER_SCRIBBLE, fill_opacity=1,
                  stroke_color=INK, stroke_width=4).move_to([0, 1.15, 0])
    body = Line([0, 0.93, 0], [0, 0.25, 0], stroke_color=INK, stroke_width=4)
    legs = VGroup(Line([0, 0.25, 0], [-0.22, -0.35, 0], stroke_color=INK,
                       stroke_width=4),
                  Line([0, 0.25, 0], [0.22, -0.35, 0], stroke_color=INK,
                       stroke_width=4))
    if arm_up:
        arms = VGroup(Line([0, 0.78, 0], [-0.3, 0.55, 0], stroke_color=INK,
                           stroke_width=4),
                      Line([0, 0.78, 0], [0.38, 1.05, 0], stroke_color=INK,
                           stroke_width=4))
    else:
        arms = VGroup(Line([0, 0.78, 0], [-0.3, 0.5, 0], stroke_color=INK,
                           stroke_width=4),
                      Line([0, 0.78, 0], [0.3, 0.5, 0], stroke_color=INK,
                           stroke_width=4))
    g = crayonify(VGroup(head, body, arms, legs), amp=0.02, seed=seed)
    g.scale(scale, about_point=[0, -0.35, 0])
    g.shift(UP * (GROUND_Y + 0.35))
    return g


def parcel(color, seed, w=0.7):
    box = rrect(w, w * 0.72, color, radius=0.08)
    tie = Line([0, -w * 0.36, 0], [0, w * 0.36, 0], stroke_color=INK,
               stroke_width=3)
    return crayonify(VGroup(box, tie), seed=seed)


def white_card(text, seed, w=1.9, h=0.55, color=INK):
    c = rrect(w, h, "#FFFFFF", radius=0.10, stroke_w=4)
    t = hand_label(text, size=26, scrawl=True, color=color)
    t.scale_to_fit_width(min(t.width, w * 0.85))
    t.move_to([0, 0, 0])
    return crayonify(VGroup(c), seed=seed).add(t)


# ---------------------------------------------------------------- P01 ----
class Preamble01(PacedScene):
    """The algorithm era: the van learns what you pick.

    Labeled per Sarah's note: the audience's first look at the world, so
    the boxes say what they are (your usage data) and the van says what
    it is (the algorithm).
    """

    def construct(self):
        stage_min(self)
        vp = build_van(seed=70)
        van = vp["van"]
        tag = hand_label("THE ALGORITHM", size=22, scrawl=True)
        tag.scale_to_fit_width(1.38)
        tag.move_to([-0.25, GROUND_Y + 0.95, 0])   # on the van body
        van.add(tag)
        van.shift(RIGHT * 3.2)
        self.add(van)

        picks = [scribble_cargo("WATCHED", CARGO_AMBER, seed=20,
                                w=1.05, h=0.68),
                 scribble_cargo("CLICKED", CARGO_CORAL, seed=21,
                                w=1.05, h=0.68),
                 scribble_cargo("BOUGHT", CARGO_LILAC, seed=22,
                                w=1.05, h=0.68)]
        for i, p in enumerate(picks):
            p.move_to([-4.9 + i * 1.5, GROUND_Y + 0.36, 0])
            self.play(FadeIn(p, shift=UP * 0.25), run_time=0.4)
            self.wait(0.15)
        # the van looks: dotted sightline sweeps the row
        sight = DashedLine([3.6, GROUND_Y + 1.15, 0],
                           [-4.4, GROUND_Y + 0.55, 0],
                           dash_length=0.14).set_stroke(INK_SOFT, 3)
        self.play(Create(sight), run_time=0.6)
        self.play(FadeOut(sight), run_time=0.3)
        # it leaves... and returns already loaded with your next pick
        roll_van(self, vp, RIGHT * 5.5, 0.9,
                 rate_func=rate_functions.ease_in_sine)
        nxt = scribble_cargo("NEXT", CARGO_SAGE, seed=23, w=0.9, h=0.6)
        nxt.move_to([3.0, GROUND_Y + 1.75, 0]).shift(RIGHT * 5.5)
        self.add(nxt)
        for w in vp["wheels"]:
            w.add_updater(__import__("style").make_roller(w.width / 2))
        self.play(van.animate.shift(LEFT * 5.5), nxt.animate.shift(LEFT * 5.5),
                  run_time=1.1, rate_func=rate_functions.ease_out_sine)
        for w in vp["wheels"]:
            w.clear_updaters()
        spark = crayonify(Star(n=4, outer_radius=0.2, inner_radius=0.08,
                               fill_color=CARGO_AMBER, fill_opacity=1,
                               stroke_width=0), seed=40)
        spark.move_to([3.7, GROUND_Y + 2.1, 0])
        self.play(FadeIn(spark, scale=0.4), run_time=0.3)
        self.play(FadeOut(spark, scale=1.5), run_time=0.35)
        self.wait(HOLD)


# ---------------------------------------------------------------- P02 ----
class Preamble02(PacedScene):
    """Fraud detection: normal transactions load into the bed; the
    abnormal one gets refused at the tailgate. (Sarah's note: cards are
    cargo, labeled — the deck's own grammar, no floating abstractions.)
    """

    def construct(self):
        stage_min(self)
        parts = build_truck(seed=0)
        truck = parts["truck"]
        truck.shift(LEFT * 3.6)
        self.add(truck)

        slots = [[-5.55, -1.19, 0], [-4.45, -1.19, 0],
                 [-5.55, -0.50, 0], [-4.45, -0.50, 0]]
        for i, slot in enumerate(slots):
            c = scribble_cargo("NORMAL", CARGO_SAGE, seed=60 + i,
                               w=1.05, h=0.60).set_z_index(2)
            c.move_to([7.8, GROUND_Y + 0.9, 0])
            self.add(c)
            self.play(c.animate.move_to([slot[0], 0.9, 0]),
                      run_time=0.55, rate_func=rate_functions.ease_in_out_sine)
            self.play(c.animate.move_to(slot),
                      run_time=0.35, rate_func=rate_functions.ease_out_bounce)
        # the odd one out: refused at the tailgate
        bad_box = crayonify(rrect(1.35, 0.62, "#FFFFFF", radius=0.10,
                                  stroke=ALERT, stroke_w=5), seed=64)
        bad_lbl = hand_label("ABNORMAL", size=24, scrawl=True, color=ALERT)
        bad_lbl.scale_to_fit_width(1.1)
        bad = VGroup(bad_box, bad_lbl)
        bad_lbl.move_to([0, 0, 0])
        bad.move_to([7.8, GROUND_Y + 0.9, 0])
        self.add(bad)
        self.play(bad.animate.move_to([-4.9, 0.9, 0]),
                  run_time=0.55, rate_func=rate_functions.ease_in_out_sine)
        bang = hand_label("!", size=64, color=ALERT)
        bang.move_to([-4.9, 1.9, 0])
        self.play(FadeIn(bang, scale=0.5), run_time=0.3)
        for dx in (0.06, -0.06, 0.06, -0.06):
            self.play(bad.animate.shift(RIGHT * dx), run_time=0.08)
        # bounced off the tailgate: lands clear of the truck, flagged
        self.play(bad.animate.move_to([0.75, GROUND_Y + 0.33, 0]
                                      ).rotate(-10 * DEGREES),
                  bang.animate.move_to([0.75, GROUND_Y + 1.2, 0]),
                  run_time=0.7, rate_func=rate_functions.ease_out_quad)
        self.wait(HOLD)


# ---------------------------------------------------------------- P03 ----
class Preamble03(PacedScene):
    """Decades: the road was being laid the whole time.

    Mile markers carry the receipts (researched 2026-07-15): spell check
    reached home computers in 1980; fraud detection and spam filtering
    went mainstream in the 90s; shopping recommendations arrived in the
    late 90s and ruled the 2000s; Siri shipped 2011; generative AI 2020s.
    """

    DECADES = [
        ("1980s", "SPELL CHECK"),
        ("1990s", "FRAUD ALERTS"),
        ("2000s", "SHOPPING RECS"),
        ("2010s", "VOICE ASSISTANTS"),
        ("2020s", "GENERATIVE AI"),
    ]

    def construct(self):
        stage_min(self)
        BRICK_Y = GROUND_Y + 0.16
        colors = [CARGO_AMBER, CARGO_CORAL, CARGO_LILAC, CARGO_SAGE]
        road = VGroup(*[
            crayonify(rrect(0.62, 0.30, colors[i % 4], radius=0.06,
                            stroke_w=4), seed=i
                      ).move_to([-8 + i * 0.66, BRICK_Y, 0])
            for i in range(70)
        ])
        markers = VGroup()
        for k, ((decade, example), mx) in enumerate(
                zip(self.DECADES, [0.0, 7.5, 15.0, 22.5, 30.0])):
            panel = rrect(2.5, 1.05, "#FFFFFF", radius=0.10, stroke_w=4)
            panel.move_to([mx, GROUND_Y + 2.0, 0])
            pole = Line([mx, GROUND_Y + 0.3, 0], [mx, GROUND_Y + 1.47, 0],
                        stroke_color=INK, stroke_width=4)
            sign = crayonify(VGroup(pole, panel), seed=30 + k)
            yr = hand_label(decade, size=30)
            yr.move_to([mx, GROUND_Y + 2.22, 0])
            ex = hand_label(example, size=22, scrawl=True, color=INK_SOFT)
            ex.scale_to_fit_width(min(ex.width, 2.2))
            ex.move_to([mx, GROUND_Y + 1.78, 0])
            markers.add(VGroup(sign, yr, ex))
        world = VGroup(road, markers)
        self.add(world)
        # open centered on the 1980s, then hop sign to sign with a
        # reading pause at each (Sarah: the drive-by was too fast)
        self.wait(1.0)
        for _ in range(4):
            self.play(world.animate.shift(LEFT * 7.5), run_time=1.0,
                      rate_func=rate_functions.ease_in_out_sine)
            self.wait(0.9)
        self.wait(HOLD)


# ---------------------------------------------------------------- P04 ----
class Preamble04(PacedScene):
    """The factory runs hot; crates are stamped at the gate."""

    def construct(self):
        stage_min(self)
        fac = crayonify(VGroup(
            rrect(3.4, 2.6, "#E7E2D6", radius=0.12).move_to(
                [-4.6, GROUND_Y + 1.3, 0]),
            rrect(1.0, 1.3, INK_SOFT, radius=0.08).move_to(
                [-3.6, GROUND_Y + 2.9, 0]),
        ), seed=50)
        gate_x = 3.4
        gate = crayonify(VGroup(
            rrect(0.18, 1.6, "#D8CBB2", radius=0.05, stroke_w=4
                  ).move_to([gate_x, GROUND_Y + 0.8, 0]),
            rrect(0.18, 1.6, "#D8CBB2", radius=0.05, stroke_w=4
                  ).move_to([gate_x + 1.7, GROUND_Y + 0.8, 0]),
            rrect(2.3, 0.3, CARGO_AMBER, radius=0.08, stroke_w=4
                  ).move_to([gate_x + 0.85, GROUND_Y + 1.75, 0]),
        ), seed=51)
        self.add(fac, gate)

        def engine_crate(seed):
            eng = VGroup(
                rrect(1.0, 0.75, AI_TEAL_DARK, radius=0.10),
                *[Circle(radius=0.09, fill_color=AI_TEAL, fill_opacity=1,
                         stroke_color=INK, stroke_width=3
                         ).move_to([x, 0.22, 0]) for x in (-0.28, 0.0, 0.28)])
            return crayonify(eng, seed=seed)

        for i in range(3):
            e = engine_crate(60 + i)
            e.move_to([-4.4, GROUND_Y + 0.55, 0])
            self.play(FadeIn(e, shift=RIGHT * 0.3), run_time=0.3)
            self.play(e.animate.move_to([gate_x - 1.3, GROUND_Y + 0.55, 0]),
                      run_time=0.7, rate_func=rate_functions.ease_in_out_sine)
            # the stamp STICKS to the crate and rides out with it
            stamp = white_card("OK TO SHIP", seed=70 + i, w=1.35, h=0.45,
                               color=AI_TEAL_DARK)
            stamp.rotate(-7 * DEGREES).move_to([gate_x - 1.3,
                                                GROUND_Y + 1.25, 0])
            self.play(FadeIn(stamp, scale=1.5), run_time=0.35)
            gp = puff([gate_x + 0.85, GROUND_Y + 0.3, 0])
            dx = 4.6 if i < 2 else 3.3   # the last crate parks in frame
            self.play(e.animate.shift(RIGHT * dx),
                      stamp.animate.shift(RIGHT * dx),
                      FadeIn(gp), run_time=0.55,
                      rate_func=rate_functions.ease_in_sine)
            self.play(FadeOut(gp), run_time=0.2)
            if i < 2:
                self.remove(e, stamp)
        self.wait(HOLD)


# ---------------------------------------------------------------- P05 ----
class Preamble05(PacedScene):
    """The poster stops being a joke: the dashes fill in."""

    def construct(self):
        stage_min(self)
        frame = crayonify(rrect(5.4, 4.0, "#FFFFFF", radius=0.15, stroke_w=5),
                          seed=91).move_to([0, 0.6, 0])
        txt = hand_label("NEXT YEAR'S TRUCK (PROBABLY)", size=30,
                         scrawl=True, color=INK_SOFT)
        txt.move_to([0, 2.05, 0])
        self.add(frame, txt)

        def concept_truck(fill_op, amp, seed, stroke_op=1.0):
            g = VGroup(
                rrect(2.6, 0.85, AI_TEAL, radius=0.12).move_to([-0.4, 0.35, 0]),
                rrect(0.95, 0.95, AI_TEAL, radius=0.12).move_to([1.45, 0.4, 0]),
                Circle(radius=0.3, fill_color=INK, fill_opacity=fill_op,
                       stroke_color=INK, stroke_width=4
                       ).move_to([-1.2, -0.25, 0]),
                Circle(radius=0.3, fill_color=INK, fill_opacity=fill_op,
                       stroke_color=INK, stroke_width=4
                       ).move_to([0.85, -0.25, 0]),
                Polygon([-0.9, 0.8, 0], [-0.45, 0.8, 0], [-0.68, 1.75, 0],
                        fill_color=CARGO_CORAL, fill_opacity=fill_op,
                        stroke_color=INK, stroke_width=4),
                Polygon([0.4, 0.75, 0], [1.5, 1.4, 0], [0.55, 1.05, 0],
                        fill_color=CARGO_LILAC, fill_opacity=fill_op,
                        stroke_color=INK, stroke_width=4),
            )
            g.set_fill(opacity=fill_op)
            out = crayonify(g, amp=amp, seed=seed)
            out.set_stroke(opacity=stroke_op)
            return out.move_to([0, 0.25, 0])

        sketchy = concept_truck(0.30, 0.06, 89, stroke_op=0.65)
        solid = concept_truck(1.0, 0.028, 90)
        self.play(Create(sketchy), run_time=1.2)
        self.wait(0.8)
        new_txt = hand_label("NEXT YEAR'S TRUCK", size=30, scrawl=True)
        new_txt.move_to([0, 2.05, 0])
        self.play(FadeTransform(sketchy, solid),
                  FadeOut(txt), FadeIn(new_txt), run_time=1.4)
        self.wait(HOLD)


# ---------------------------------------------------------------- P06 ----
class Preamble06(PacedScene):
    """Recommending a movie vs reaching for your job card. No gags."""

    def construct(self):
        stage_min(self)
        fig = stickfig(seed=200, arm_up=True)
        fig.shift(LEFT * 1.2)
        vp = build_van(seed=70)
        van = vp["van"]
        van.shift(RIGHT * 2.6)
        self.add(fig, van)
        # a topical recommendation, per Sarah — the fake sequel energy
        gift = scribble_cargo("SPACE TRUCKS 4", CARGO_SAGE, seed=24,
                              w=1.7, h=0.72)
        gift.move_to([1.6, GROUND_Y + 1.5, 0])
        self.play(FadeIn(gift, scale=0.6), run_time=0.4)
        self.play(gift.animate.move_to([-0.55, GROUND_Y + 1.35, 0]),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.8)
        self.play(FadeOut(gift), FadeOut(van), run_time=0.5)

        # the job board: both reach for the same card
        rail = crayonify(Line([-2.4, 1.7, 0], [4.6, 1.7, 0],
                              stroke_color=INK, stroke_width=STROKE_W),
                         seed=52)
        cards = VGroup()
        for i, x in enumerate([-1.4, 0.4, 2.2, 4.0]):
            hook = Line([x, 1.7, 0], [x, 1.35, 0], stroke_color=INK,
                        stroke_width=3)
            if i == 1:
                # the contested one says what it is
                jc = build_job_card("YOUR JOB", seed=80 + i, w=1.5, h=0.9)
                jc.move_to([x, 0.85, 0])
                cards.add(VGroup(crayonify(hook, amp=0.02, seed=95 + i), jc))
                continue
            jc = build_job_card("", seed=80 + i, w=1.5, h=0.9)
            jc.move_to([x, 0.85, 0])
            squig = crayonify(VGroup(
                Line([x - 0.5, 1.0, 0], [x + 0.5, 1.0, 0],
                     stroke_color=INK_SOFT, stroke_width=3),
                Line([x - 0.5, 0.72, 0], [x + 0.15, 0.72, 0],
                     stroke_color=INK_SOFT, stroke_width=3)),
                amp=0.02, seed=90 + i)
            cards.add(VGroup(crayonify(hook, amp=0.02, seed=95 + i), jc, squig))
        self.play(FadeIn(rail), FadeIn(cards, shift=DOWN * 0.2), run_time=0.7)

        parts = build_truck(seed=0)
        truck = parts["truck"]
        truck.shift(RIGHT * 11 + RIGHT * 0.0)
        truck.scale(0.85, about_point=[0, GROUND_Y, 0])
        self.add(truck)
        roll(self, parts, LEFT * 6.0, 1.4,
             rate_func=rate_functions.ease_out_sine)
        crane = build_crane(seed=50)
        crane.scale(0.85, about_point=[0, GROUND_Y, 0])
        crane.shift(RIGHT * 3.3)   # hook lands over the YOUR JOB card
        self.play(FadeIn(crane), run_time=0.4)
        # both reach toward the SAME card, freeze there
        fig.set_z_index(5)   # never lost behind the truck
        self.play(fig.animate.shift(RIGHT * 1.6),
                  run_time=0.9, rate_func=rate_functions.ease_in_out_sine)
        self.wait(HOLD)


# ------------------------------------------------------- P07a/b/c ----
# The upside, click-paced (Sarah 2026-08-10): three sub-clips the
# presenter advances through. a) the labeled tedium drives away;
# b) the family gardens instead; c) the breakthrough symbols arrive.
# P07c opens on P07b's exact final tableau (same builders, same seeds)
# so the click-through is seamless.

def _garden(scene, animate=True):
    """The gardening tableau shared by P07b (animated) and P07c (static)."""
    adult = stickfig(seed=201, arm_up=True)
    adult.shift(LEFT * 2.6)
    kid = stickfig(seed=202, scale=0.58)
    kid.shift(RIGHT * 3.4)
    can = crayonify(VGroup(
        rrect(0.55, 0.4, AI_TEAL_DARK, radius=0.08
              ).move_to([-1.9, GROUND_Y + 1.0, 0]),
        Line([-1.65, GROUND_Y + 1.1, 0], [-1.3, GROUND_Y + 0.9, 0],
             stroke_color=INK, stroke_width=4)), seed=205)
    can.rotate(-18 * DEGREES)
    bed = crayonify(rrect(3.2, 0.35, "#D8CBB2", radius=0.08
                          ).move_to([0.6, GROUND_Y + 0.18, 0]), seed=206)
    petal_colors = [CARGO_CORAL, CARGO_LILAC, CARGO_AMBER]
    flowers = []
    for i, fx in enumerate([-0.4, 0.6, 1.6]):
        stem = Line([fx, GROUND_Y + 0.35, 0], [fx, GROUND_Y + 1.05, 0],
                    stroke_color=CARGO_SAGE, stroke_width=5)
        stem = crayonify(stem, amp=0.02, seed=210 + i)
        petals = crayonify(VGroup(
            *[Circle(radius=0.13, fill_color=petal_colors[i],
                     fill_opacity=1, stroke_color=INK, stroke_width=3
                     ).move_to([fx + 0.16 * np.cos(a), GROUND_Y + 1.15
                                + 0.16 * np.sin(a), 0])
              for a in np.linspace(0, 2 * np.pi, 5, endpoint=False)],
            Circle(radius=0.09, fill_color="#FFFFFF", fill_opacity=1,
                   stroke_color=INK, stroke_width=3
                   ).move_to([fx, GROUND_Y + 1.15, 0])), seed=215 + i)
        flowers.append((stem, petals))
    if animate:
        scene.play(FadeIn(adult, shift=UP * 0.2),
                   FadeIn(kid, shift=UP * 0.2),
                   FadeIn(bed), run_time=0.7)
        scene.play(FadeIn(can, scale=0.7), run_time=0.4)
        drops = crayonify(VGroup(*[
            Line([-0.85 + k * 0.14, GROUND_Y + 0.85, 0],
                 [-0.9 + k * 0.14, GROUND_Y + 0.6, 0],
                 stroke_color=INK_SOFT, stroke_width=3) for k in range(3)
        ]), amp=0.015, seed=220)
        scene.play(FadeIn(drops), run_time=0.35)
        scene.play(FadeOut(drops), run_time=0.35)
        for stem, petals in flowers:
            scene.play(Create(stem), run_time=0.45)
            scene.play(FadeIn(petals, scale=0.3), run_time=0.35)
    else:
        scene.add(adult, kid, bed, can)
        for stem, petals in flowers:
            scene.add(stem, petals)


class Preamble07a(PacedScene):
    """The labeled tedium drives away."""

    def construct(self):
        stage_min(self)
        parts = build_truck(seed=0)
        truck = parts["truck"]
        truck.shift(LEFT * 2.0)
        self.add(truck)
        labels = ["GRUNT WORK", "MENIAL TASKS", "TEDIUM"]
        crates = VGroup(*[
            scribble_cargo(lab, "#D8CBB2", seed=30 + i, w=1.5, h=0.78
                           ).set_z_index(2)
            for i, lab in enumerate(labels)
        ])
        # stacked above the bed rim so every label reads
        crates[0].move_to([-3.6, -0.5, 0])
        crates[1].move_to([-1.95, -0.5, 0])
        crates[2].move_to([-2.8, 0.32, 0])
        self.add(crates)
        self.wait(1.0)
        roll(self, parts, RIGHT * 12.5, 1.8,
             rate_func=rate_functions.ease_in_sine, extra_mobs=[crates])
        self.wait(HOLD)


class Preamble07b(PacedScene):
    """What the people do instead: the garden."""

    def construct(self):
        stage_min(self)
        _garden(self, animate=True)
        self.wait(HOLD)


class Preamble07c(PacedScene):
    """The breakthroughs arrive: medicine, energy, crops (upper right)."""

    def construct(self):
        stage_min(self)
        _garden(self, animate=False)   # P07b's final tableau, held
        pill = crayonify(VGroup(
            rrect(0.55, 1.0, CARGO_LILAC, radius=0.28
                  ).move_to([3.9, 2.55, 0]).rotate(28 * DEGREES),
            Line([3.68, 2.42, 0], [4.15, 2.72, 0], stroke_color=INK,
                 stroke_width=4)), seed=60)
        bolt = crayonify(Polygon(
            [5.15, 3.15, 0], [4.85, 2.35, 0], [5.1, 2.35, 0],
            [4.9, 1.75, 0], [5.4, 2.6, 0], [5.15, 2.6, 0],
            fill_color=CARGO_AMBER, fill_opacity=1, stroke_color=INK,
            stroke_width=4), seed=61)
        wheat = crayonify(VGroup(
            Line([6.3, 1.85, 0], [6.3, 3.05, 0], stroke_color=CARGO_SAGE,
                 stroke_width=5),
            *[Line([6.3, 2.25 + k * 0.25, 0],
                   [6.3 + (0.3 if k % 2 else -0.3), 2.45 + k * 0.25, 0],
                   stroke_color=CARGO_SAGE, stroke_width=4)
              for k in range(3)]), seed=62)
        self.wait(0.5)
        for m in (pill, bolt, wheat):
            self.play(FadeIn(m, scale=0.5), run_time=0.5)
            self.wait(0.3)
        self.wait(HOLD)


# ------------------------------------------------------- P08a/b/c ----
# The ledger, click-paced (Sarah 2026-08-10): a) the worker alone;
# b) the benefit cards pile above them; c) the truck arrives with its
# one-card ledger. Deterministic shared layout = seamless click-through.

FIG_X = -4.2
LEDGER = ["SALARY", "HEALTHCARE", "401K", "PTO", "MANAGERS"]


def _ledger_fig():
    fig = stickfig(seed=200)
    fig.shift(LEFT * 4.2)
    return fig


def _ledger_cards():
    cards = []
    for i, lab in enumerate(LEDGER):
        c = white_card(lab, seed=30 + i)
        c.move_to([FIG_X, GROUND_Y + 1.9 + i * 0.62, 0])
        cards.append(c)
    return cards


class Preamble08a(PacedScene):
    """The worker, alone. Humans are expensive — meet the human."""

    def construct(self):
        stage_min(self)
        fig = _ledger_fig()
        self.play(FadeIn(fig, shift=UP * 0.2), run_time=0.7)
        self.wait(HOLD)


class Preamble08b(PacedScene):
    """The benefit cards stack up over the worker."""

    def construct(self):
        stage_min(self)
        self.add(_ledger_fig())
        self.wait(0.4)
        for c in _ledger_cards():
            target = c.get_center()
            c.move_to([FIG_X, 3.9, 0])
            self.add(c)
            self.play(c.animate.move_to(target),
                      run_time=0.5, rate_func=rate_functions.ease_out_quad)
            self.wait(0.1)
        self.wait(HOLD)


class Preamble08c(PacedScene):
    """The truck rolls in; its whole ledger is one card: FUEL."""

    def construct(self):
        stage_min(self)
        self.add(_ledger_fig())
        for c in _ledger_cards():
            self.add(c)
        parts = build_truck(seed=0)
        truck = parts["truck"]
        truck.scale(0.8, about_point=[0, GROUND_Y, 0])
        truck.shift(RIGHT * 11)
        self.add(truck)
        roll(self, parts, LEFT * 7.4, 1.5,
             rate_func=rate_functions.ease_out_sine)
        fuel = white_card("FUEL", seed=40, color=AI_TEAL_DARK)
        fuel.move_to([3.0, 3.9, 0])
        self.play(fuel.animate.move_to([3.0, GROUND_Y + 3.0, 0]),
                  run_time=0.6, rate_func=rate_functions.ease_out_quad)
        self.wait(HOLD)


# ---------------------------------------------------------------- P09 ----
class Preamble09(PacedScene):
    """Seat pricing wobbles; then a shed built from a sentence."""

    def construct(self):
        stage_min(self)
        fig = stickfig(seed=200)
        fig.shift(LEFT * 3.0)
        eq = hand_label("=", size=54).move_to([-1.2, GROUND_Y + 1.0, 0])
        seat = white_card("1 SEAT", seed=30, w=1.7, h=0.7)
        seat.move_to([0.6, GROUND_Y + 1.0, 0])
        self.add(fig)
        self.play(FadeIn(eq), FadeIn(seat, shift=LEFT * 0.3), run_time=0.6)
        self.wait(0.6)
        q = hand_label("?", size=110, color=ALERT)
        q.move_to([0.6, GROUND_Y + 2.4, 0])
        self.play(FadeIn(q, scale=0.4), seat.animate.rotate(-9 * DEGREES),
                  run_time=0.5)
        self.wait(0.8)
        self.play(FadeOut(q), FadeOut(seat), FadeOut(eq), run_time=0.5)

        # vibe coding: a request bubble, then the shed assembles under it
        bubble = crayonify(VGroup(
            rrect(2.6, 1.1, "#FFFFFF", radius=0.35, stroke_w=4
                  ).move_to([-1.1, 1.6, 0]),
            Polygon([-2.0, 1.1, 0], [-1.7, 1.15, 0], [-2.3, 0.55, 0],
                    fill_color="#FFFFFF", fill_opacity=1, stroke_color=INK,
                    stroke_width=4),
            Line([-1.9, 1.75, 0], [-0.4, 1.75, 0], stroke_color=INK_SOFT,
                 stroke_width=3),
            Line([-1.9, 1.45, 0], [-0.9, 1.45, 0], stroke_color=INK_SOFT,
                 stroke_width=3)), seed=50)
        self.play(FadeIn(bubble, scale=0.7), run_time=0.5)

        shed_x = 2.6
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
        shed.shift(UP * 5.5)
        self.add(shed)
        self.play(shed.animate.shift(DOWN * 5.5), run_time=0.9,
                  rate_func=rate_functions.ease_out_bounce)
        d = puff([shed_x, GROUND_Y + 0.4, 0], n=4, spread=0.5)
        self.play(FadeIn(d), run_time=0.25)
        self.play(FadeOut(d), run_time=0.3)
        self.wait(HOLD)


# ---------------------------------------------------------------- P10 ----
class Preamble10(PacedScene):
    """Specialists everywhere: the parade of badged trucks."""

    def construct(self):
        stage_min(self)

        def badged_van(seed, badge_builder, dx):
            vp = build_van(seed=seed, scale=0.9)
            vp["van"].shift(RIGHT * dx + LEFT * 13)
            b = badge_builder()
            b.shift(RIGHT * dx + LEFT * 13)
            vp["van"].add(b)
            return vp

        def briefcase():
            return crayonify(VGroup(
                rrect(0.55, 0.4, CARGO_AMBER, radius=0.06
                      ).move_to([-0.25, GROUND_Y + 0.95, 0]),
                Arc(radius=0.14, start_angle=0, angle=PI, stroke_color=INK,
                    stroke_width=3).move_to([-0.25, GROUND_Y + 1.2, 0])),
                seed=60)

        def wrench():
            return crayonify(VGroup(
                rrect(0.12, 0.5, CARGO_LILAC, radius=0.05
                      ).move_to([-0.25, GROUND_Y + 0.95, 0]),
                Circle(radius=0.14, fill_color=CARGO_LILAC, fill_opacity=1,
                       stroke_color=INK, stroke_width=3
                       ).move_to([-0.25, GROUND_Y + 1.25, 0])), seed=61)

        def headset():
            return crayonify(VGroup(
                Arc(radius=0.22, start_angle=0, angle=PI, stroke_color=INK,
                    stroke_width=4).move_to([-0.25, GROUND_Y + 1.1, 0]),
                Circle(radius=0.08, fill_color=CARGO_CORAL, fill_opacity=1,
                       stroke_color=INK, stroke_width=3
                       ).move_to([-0.47, GROUND_Y + 1.0, 0]),
                Circle(radius=0.08, fill_color=CARGO_CORAL, fill_opacity=1,
                       stroke_color=INK, stroke_width=3
                       ).move_to([-0.03, GROUND_Y + 1.0, 0])), seed=62)

        vans = [badged_van(100, briefcase, 0),
                badged_van(110, wrench, 4.2),
                badged_van(120, headset, 8.4)]
        for vp in vans:
            self.add(vp["van"])
            for w in vp["wheels"]:
                w.add_updater(__import__("style").make_roller(w.width / 2))
        self.play(*[vp["van"].animate.shift(RIGHT * 11.2) for vp in vans],
                  run_time=2.6, rate_func=rate_functions.ease_in_out_sine)
        for vp in vans:
            for w in vp["wheels"]:
                w.clear_updaters()
        self.wait(HOLD)


# ---------------------------------------------------------------- P11 ----
class Preamble11(PacedScene):
    """The series handoff: the whole jobsite, then the title."""

    def construct(self):
        ground, sun = stage_min(self)
        # the world at rest: garage, factory, shed, trucks parked
        garage = crayonify(VGroup(
            rrect(2.6, 2.0, "#E7E2D6", radius=0.12
                  ).move_to([-5.4, GROUND_Y + 1.0, 0]),
            rrect(1.5, 1.3, INK_SOFT, radius=0.08
                  ).move_to([-5.4, GROUND_Y + 0.65, 0])), seed=50)
        shed = crayonify(VGroup(
            rrect(1.7, 1.1, CARGO_AMBER, radius=0.08
                  ).move_to([5.3, GROUND_Y + 0.55, 0]),
            Polygon([4.3, GROUND_Y + 1.12, 0], [6.3, GROUND_Y + 1.12, 0],
                    [5.3, GROUND_Y + 1.85, 0], fill_color=CARGO_CORAL,
                    fill_opacity=1, stroke_color=INK, stroke_width=4)),
            seed=51)
        parts = build_truck(seed=0)
        truck = parts["truck"]
        truck.scale(0.72, about_point=[0, GROUND_Y, 0])
        truck.shift(LEFT * 1.6)
        vp = build_van(seed=70, scale=0.65)
        vp["van"].shift(RIGHT * 2.2)
        self.add(garage, shed, truck, vp["van"])
        self.play(sun.animate.scale(1.4).shift(DOWN * 0.1), run_time=1.0)

        panel = crayonify(rrect(5.6, 1.9, "#FFFFFF", radius=0.18, stroke_w=5),
                          seed=91).move_to([0, 1.9, 0])
        t1 = hand_label("AI BASICS", size=64).move_to([0, 2.2, 0])
        t2 = hand_label("the building blocks", size=30, color=INK_SOFT)
        t2.move_to([0, 1.5, 0])
        self.play(FadeIn(panel, shift=UP * 0.25), FadeIn(t1), FadeIn(t2),
                  run_time=0.9)
        self.wait(HOLD)
