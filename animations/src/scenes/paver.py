"""
Scene 2 — The Paver: the model is a prediction engine.

Storyboard: animations/STORYBOARDS.md (Scene 2). A track-laying paver
builds the road it then drives on, one brick at a time, choosing each
brick by looking back at the bricks already laid:
  * tokenization: a word gets chopped into brick-sized pieces
  * tokens in AND out cost (the fuel meter ticks on look-back and on lay)
  * the missed turnoff: confident, smooth, wrong
  * GAG: it paves a proud loop-de-loop and plants a DONE flag
    (side-view translation of the storyboard's cul-de-sac)
  * it only sees the recent road (older bricks fade)

Render draft:  SCRIBBLE_SEED=1 manim -ql src/scenes/paver.py Paver
Render final:  ./scripts/boil.sh paver Paver
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from jobsite import (  # noqa: E402
    CaptionManager, GROUND_Y, build_meter, build_stage,
)
from style import (  # noqa: E402
    ALERT, AI_TEAL, AI_TEAL_DARK, CARGO_AMBER, CARGO_CORAL, CARGO_LILAC,
    CARGO_SAGE, INK, INK_SOFT, PAPER_SCRIBBLE, STROKE_W, crayonify,
    hand_label, make_roller, puff, rrect,
)

BRICK_Y = GROUND_Y + 0.16
BRICK_W = 0.62
STEP = 0.66
BRICK_COLORS = [CARGO_AMBER, CARGO_CORAL, CARGO_LILAC, CARGO_SAGE]


def brick(x: float, seed: int, y: float = BRICK_Y, color=None,
          rot: float = 0.0) -> VGroup:
    c = color or BRICK_COLORS[seed % 4]
    b = crayonify(rrect(BRICK_W, 0.30, c, radius=0.06, stroke_w=4),
                  seed=seed)
    b.rotate(rot).move_to([x, y, 0])
    return b


def build_paver(seed: int = 5) -> dict:
    """The paver at canonical x=0 (body center), facing right."""
    body = crayonify(rrect(1.75, 0.95, AI_TEAL, radius=0.16), seed=seed + 1)
    body.move_to([0, GROUND_Y + 1.02, 0])
    window = crayonify(rrect(0.55, 0.42, PAPER_SCRIBBLE, radius=0.09,
                             stroke_w=4), seed=seed + 2)
    window.move_to([0.45, GROUND_Y + 1.18, 0])
    eye = Dot([0.58, GROUND_Y + 1.18, 0], radius=0.055, color=INK)
    hopper = crayonify(Polygon(
        [-0.85, GROUND_Y + 2.05, 0], [-0.05, GROUND_Y + 2.05, 0],
        [-0.20, GROUND_Y + 1.48, 0], [-0.70, GROUND_Y + 1.48, 0],
        fill_color=AI_TEAL_DARK, fill_opacity=1, stroke_color=INK,
        stroke_width=STROKE_W), seed=seed + 3)
    roller_mount = crayonify(rrect(0.5, 0.16, AI_TEAL_DARK, radius=0.05
                                   ).move_to([0.95, GROUND_Y + 0.62, 0]),
                             seed=seed + 4)
    from style import wheel
    roller = crayonify(wheel(0.40), seed=seed + 5, amp=0.02)
    roller.move_to([1.30, GROUND_Y + 0.40 + 0.30, 0])
    back = crayonify(wheel(0.30), seed=seed + 6, amp=0.02)
    back.move_to([-0.55, GROUND_Y + 0.60, 0])
    paver = VGroup(body, hopper, roller_mount, roller, back, window, eye)
    # the paver rides ON the brick road (bricks are 0.3 tall)
    paver.shift(UP * 0.02)
    return {"paver": paver, "roller": roller, "back": back, "eye": eye,
            "body": body, "hopper": hopper}


class Paver(Scene):
    def construct(self):
        self.camera.background_color = PAPER_SCRIBBLE
        stage = build_stage("THE PREDICTION ENGINE",
                            "how the model actually works")
        self.add(stage)
        cap = CaptionManager(self)
        self.wait(0.4)

        # pre-laid road behind the entry point
        road = VGroup(*[brick(-8.0 + i * STEP, seed=i) for i in range(10)])
        self.add(road)
        laid_x = -8.0 + 9 * STEP  # x of last laid brick (≈ -2.06)

        # ---------------------------------------- beat 1: paver enters ---
        pd = build_paver()
        paver = pd["paver"]
        px = laid_x - 0.55           # body center rides just behind road end
        paver.shift(RIGHT * (px - 0) + LEFT * 9)
        self.add(paver)

        def advance(dx, rt=0.5, extra=()):
            for w in (pd["roller"], pd["back"]):
                w.add_updater(make_roller(w.width / 2))
            self.play(paver.animate.shift(RIGHT * dx), *extra, run_time=rt)
            for w in (pd["roller"], pd["back"]):
                w.clear_updaters()

        advance(9, rt=1.8, extra=())
        cap.set("the model predicts the next piece")
        self.wait(0.5)

        # ---------------------------------------- beat 2: tokenization ---
        cap.set("words get chopped into tokens")
        plank = crayonify(rrect(2.5, 0.75, "#FFFFFF", radius=0.10,
                                stroke_w=4), seed=30)
        plank.move_to([3.6, 2.35, 0])
        word = hand_label("DRIVEWAY", size=36, scrawl=True
                          ).move_to([3.6, 2.35, 0])
        self.play(FadeIn(plank, shift=DOWN * 0.3), FadeIn(word), run_time=0.5)

        chunk1 = crayonify(rrect(1.05, 0.55, CARGO_AMBER, radius=0.08,
                                 stroke_w=4), seed=31)
        t1 = hand_label("DRIVE", size=26, scrawl=True)
        chunk1 = VGroup(chunk1, t1)
        chunk1.move_to([3.15, 2.35, 0])
        t1.move_to([3.15, 2.35, 0])
        chunk2 = crayonify(rrect(0.85, 0.55, CARGO_CORAL, radius=0.08,
                                 stroke_w=4), seed=32)
        t2 = hand_label("WAY", size=26, scrawl=True)
        chunk2 = VGroup(chunk2, t2)
        chunk2.move_to([4.25, 2.35, 0])
        t2.move_to([4.25, 2.35, 0])

        self.play(FadeOut(word), FadeOut(plank),
                  FadeIn(chunk1, scale=0.8), FadeIn(chunk2, scale=0.8),
                  run_time=0.45)
        self.play(chunk1.animate.shift(LEFT * 0.35),
                  chunk2.animate.shift(RIGHT * 0.35), run_time=0.35)
        hop = pd["hopper"].get_center() + UP * 0.45
        self.play(chunk1.animate.scale(0.4).move_to(hop),
                  run_time=0.55, rate_func=rate_functions.ease_in_sine)
        self.remove(chunk1)
        self.play(chunk2.animate.scale(0.4).move_to(hop),
                  run_time=0.5, rate_func=rate_functions.ease_in_sine)
        self.remove(chunk2)
        self.wait(0.3)

        # -------------------------------- beat 3: look back, lay, ×3 -----
        cap.set("each brick: whatever fits so far")

        def lay(seed, color=None, meter_anims=(), look=True):
            nonlocal laid_x
            eye_p = pd["eye"].get_center()
            if look:
                sight = DashedLine(eye_p + LEFT * 0.25 + DOWN * 0.1,
                                   [laid_x - 1.2, BRICK_Y + 0.25, 0],
                                   stroke_color=INK_SOFT, stroke_width=3,
                                   dash_length=0.12)
                self.play(Create(sight), run_time=0.3)
                self.play(FadeOut(sight), run_time=0.2)
            laid_x += STEP
            b = brick(laid_x, seed=seed, color=color)
            b.scale(0.2).move_to(pd["roller"].get_center() + RIGHT * 0.5)
            self.add(b)
            self.play(b.animate.scale(5).move_to([laid_x, BRICK_Y, 0]),
                      *meter_anims, run_time=0.4,
                      rate_func=rate_functions.ease_out_back)
            road.add(b)
            advance(STEP, rt=0.4)

        lay(12, color=CARGO_AMBER)   # DRIVE brick — continuity from hopper
        lay(13, color=CARGO_CORAL)   # WAY brick
        lay(14)
        self.wait(0.3)

        # -------------------------- beat 4: tokens in and out both cost --
        md = build_meter()
        meter, bar = md["meter"], md["fill"]
        self.play(FadeIn(meter, shift=DOWN * 0.2), run_time=0.5)
        cap.set("tokens in and tokens out both cost")

        def tick(w):
            return bar.animate.stretch_to_fit_width(w, about_edge=LEFT)

        # look-back costs (tokens in) ... then the lay costs (tokens out)
        eye_p = pd["eye"].get_center()
        sight = DashedLine(eye_p + LEFT * 0.25 + DOWN * 0.1,
                           [laid_x - 1.4, BRICK_Y + 0.25, 0],
                           stroke_color=INK_SOFT, stroke_width=3,
                           dash_length=0.12)
        self.play(Create(sight), tick(0.7), run_time=0.45)
        self.play(FadeOut(sight), run_time=0.2)
        lay(15, meter_anims=[tick(1.05)], look=False)
        lay(16, meter_anims=[tick(1.40)])
        self.wait(0.4)

        # camera pans right (world slides left) to make room for the gag
        self.play(VGroup(road, paver).animate.shift(LEFT * 1.6),
                  run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
        laid_x -= 1.6

        # ------------------------------- beat 5: the missed turnoff ------
        sign_x = laid_x + 2.25
        # tall enough that the plank clears the paver as it drives past
        sign = crayonify(VGroup(
            Line([sign_x, GROUND_Y, 0], [sign_x, GROUND_Y + 2.0, 0],
                 stroke_color=INK, stroke_width=STROKE_W),
            Polygon([sign_x - 0.72, GROUND_Y + 2.58, 0],
                    [sign_x + 0.30, GROUND_Y + 2.58, 0],
                    [sign_x + 0.62, GROUND_Y + 2.28, 0],
                    [sign_x + 0.30, GROUND_Y + 1.98, 0],
                    [sign_x - 0.72, GROUND_Y + 1.98, 0],
                    fill_color="#FFFFFF", fill_opacity=1,
                    stroke_color=INK, stroke_width=4),
        ), seed=33)
        sign.set_z_index(-1)   # the paver drives in front of it later
        sign_txt = hand_label("TURN HERE", size=22, scrawl=True)
        sign_txt.move_to([sign_x - 0.12, GROUND_Y + 2.28, 0])
        sign_txt.set_z_index(-1)
        route = DashedVMobject(ArcBetweenPoints(
            [sign_x + 0.5, GROUND_Y + 2.28, 0], [sign_x + 2.3, 3.0, 0],
            angle=-0.7), num_dashes=12).set_stroke(INK_SOFT, 3)
        route.set_z_index(-1)
        self.play(FadeIn(sign, shift=UP * 0.2), FadeIn(sign_txt),
                  Create(route), run_time=0.6)
        self.wait(0.3)

        cap.set("confident. smooth. wrong.", color=ALERT)
        lay(17, look=False)
        lay(18, look=False)   # sails straight past the turnoff
        lay(19, look=False)
        self.wait(0.4)

        # --------------------------------- beat 6: GAG — loop-de-loop ----
        loop_c = np.array([laid_x + 1.45, BRICK_Y + 1.18, 0])
        angles = np.linspace(-PI / 2, 3 * PI / 2, 9)[1:]  # skip bottom
        for i, a in enumerate(angles):
            p = loop_c + 1.18 * np.array([np.cos(a), np.sin(a), 0])
            lb = brick(p[0], seed=40 + i, y=p[1], rot=a + PI / 2)
            lb.scale(0.3)
            self.add(lb)
            self.play(lb.animate.scale(1 / 0.3).move_to(p), run_time=0.16,
                      rate_func=rate_functions.ease_out_sine)
            road.add(lb)
        flag = crayonify(VGroup(
            Line(loop_c + UP * 1.35, loop_c + UP * 2.15,
                 stroke_color=INK, stroke_width=4),
            Polygon(loop_c + UP * 2.15, loop_c + UP * 1.80 + RIGHT * 0.85,
                    loop_c + UP * 1.60, fill_color=CARGO_AMBER,
                    fill_opacity=1, stroke_color=INK, stroke_width=4),
        ), seed=49)
        done = hand_label("done!", size=26, scrawl=True, color=AI_TEAL_DARK)
        done.move_to(loop_c + UP * 2.35 + LEFT * 0.75)
        self.play(FadeIn(flag, shift=UP * 0.2), FadeIn(done, scale=0.6),
                  run_time=0.45)
        self.wait(1.0)

        # ------------------------------------- beat 7: the sincere one ---
        cap.set("it predicts — it never checks the map")
        self.wait(1.4)

        # ------------------------------ beat 8: only the recent road -----
        cap.set("it only sees the recent road")
        old = VGroup(*road[:-9])  # everything except the loop + last brick
        self.play(old.animate.set_opacity(0.18), run_time=0.9)
        self.wait(1.2)

        # ------------------------------------------------ beat 9: exit ---
        self.play(FadeOut(VGroup(road, flag, done, sign, sign_txt, route)),
                  FadeOut(meter), FadeOut(cap.current),
                  paver.animate.shift(DOWN * 0.30),  # settle onto the dirt
                  run_time=0.7)
        for w in (pd["roller"], pd["back"]):
            w.add_updater(make_roller(w.width / 2))
        self.play(paver.animate.shift(RIGHT * 10), run_time=1.5,
                  rate_func=rate_functions.ease_in_sine)
        for w in (pd["roller"], pd["back"]):
            w.clear_updaters()
        self.wait(0.5)
