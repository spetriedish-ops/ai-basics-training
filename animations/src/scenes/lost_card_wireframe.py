"""
WIREFRAME (still, not production) — the lost-card multi-agent flow.

Sarah's capstone use case: reporting a lost credit card. One conversation
on the left of the curtain; a system of agents and deterministic services
behind it. Color code: TEAL = agents (judgment), GREY = services (rails),
WHITE = surface. Guardrails are the canopy over everything.

Render:  SCRIBBLE_SEED=1 manim -qh -s src/scenes/lost_card_wireframe.py LostCardWireframe
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from style import (  # noqa: E402
    ALERT, AI_TEAL, AI_TEAL_DARK, CARGO_AMBER, CARGO_SAGE, INK, INK_SOFT,
    PAPER_SCRIBBLE, STROKE_W, crayonify, hand_label, rrect,
)

SERVICE_FILL = "#E7E2D6"   # deterministic services: warm grey, "rails"


def box(w, h, fill, title, sub=None, seed=0, title_size=26, sub_size=20,
        sub_color=INK_SOFT):
    g = crayonify(rrect(w, h, fill, radius=0.14, stroke_w=4), seed=seed)
    t = hand_label(title, size=title_size, scrawl=True)
    t.scale_to_fit_width(min(t.width, w * 0.9))
    parts = [g, t]
    if sub:
        s = hand_label(sub, size=sub_size, color=sub_color)
        s.scale_to_fit_width(min(s.width, w * 0.92))
        t.move_to([0, 0.16, 0])
        s.move_to([0, -0.22, 0])
        parts.append(s)
    else:
        t.move_to([0, 0, 0])
    return VGroup(*parts)


def bubble(text, fill, w, seed, size=22):
    b = crayonify(rrect(w, 0.55, fill, radius=0.20, stroke_w=3.5), seed=seed)
    t = hand_label(text, size=size, scrawl=True)
    t.scale_to_fit_width(min(t.width, w * 0.9))
    t.move_to([0, 0, 0])
    return VGroup(b, t)


def arrow(p, q, seed, color=INK):
    a = Arrow(np.array(p), np.array(q), buff=0.08, stroke_width=4,
              max_tip_length_to_length_ratio=0.12, color=color)
    return crayonify(a, amp=0.02, seed=seed)


def step_dot(n, at):
    c = Circle(radius=0.16, fill_color="#FFFFFF", fill_opacity=1,
               stroke_color=INK, stroke_width=3).move_to(at)
    t = hand_label(str(n), size=22).move_to(at)
    return VGroup(c, t)


class LostCardWireframe(Scene):
    def construct(self):
        self.camera.background_color = PAPER_SCRIBBLE

        title = hand_label("THE LOST CARD", size=48).to_edge(UP, buff=0.25)
        subtitle = hand_label("one conversation, a whole system",
                              size=28, color=INK_SOFT)
        subtitle.next_to(title, DOWN, buff=0.06)
        self.add(title, subtitle)

        # ------------------------------------------------- the curtain ---
        curtain = DashedLine([-2.95, 2.45, 0], [-2.95, -3.15, 0],
                             dash_length=0.18).set_stroke(INK_SOFT, 3)
        you_see = hand_label("what you see", size=24, color=INK_SOFT)
        you_see.move_to([-5.1, 2.55, 0])
        behind = hand_label("what's behind it", size=24, color=INK_SOFT)
        behind.move_to([-0.6, 2.55, 0])
        self.add(curtain, you_see, behind)

        # ------------------------------------------------ customer side --
        panel = crayonify(rrect(3.4, 2.5, "#FFFFFF", radius=0.18,
                                stroke_w=4), seed=10)
        panel.move_to([-5.15, 0.45, 0])
        b1 = bubble("I LOST MY CARD!", CARGO_SAGE, 2.6, seed=11)
        b1.move_to([-5.35, 1.05, 0])
        b2 = bubble("frozen. new card tuesday.", "#FFFFFF", 2.9, seed=12)
        b2.move_to([-4.95, 0.30, 0])
        b3 = bubble("3 charges flagged for review", "#FFFFFF", 2.9, seed=13)
        b3.move_to([-4.95, -0.42, 0])
        surface = hand_label("THE SURFACE", size=24, scrawl=True)
        surface.move_to([-5.15, -1.15, 0])
        self.add(panel, b1, b2, b3, surface)

        # -------------------------------------------- guardrails canopy --
        canopy = box(9.4, 0.62, "#FFFFFF",
                     "GUARDRAILS  -  policy check on every message",
                     seed=20, title_size=24)
        canopy[0][0].set_stroke(AI_TEAL_DARK)  # outline only accent
        canopy.move_to([2.15, 1.95, 0])
        self.add(canopy)

        # ------------------------------------------------- the agents ----
        concierge = box(2.7, 1.2, AI_TEAL, "CONCIERGE AGENT",
                        "owns the conversation", seed=21,
                        sub_color=PAPER_SCRIBBLE)
        concierge.move_to([-0.75, 0.45, 0])

        fraud = box(2.8, 1.2, AI_TEAL, "FRAUD AGENT",
                    "standing specialist", seed=22,
                    sub_color=PAPER_SCRIBBLE)
        fraud.move_to([4.85, 0.45, 0])
        badge = bubble("ALWAYS ON DUTY", CARGO_AMBER, 1.9, seed=23, size=18)
        badge.scale(0.85).move_to([5.55, 1.18, 0]).rotate(-4 * DEGREES)

        self.add(concierge, fraud, badge)

        # ------------------------------------------------ the services ---
        auth = box(2.7, 1.05, SERVICE_FILL, "AUTH SERVICE",
                   "rails - no judgment", seed=24)
        auth.move_to([-0.75, -1.85, 0])
        card = box(2.5, 1.05, SERVICE_FILL, "CARD SERVICE",
                   "freeze - replace", seed=25)
        card.move_to([1.85, -1.85, 0])
        ship = box(2.6, 1.05, SERVICE_FILL, "ADDRESS + SHIPPING",
                   "exactly right, every time", seed=26)
        ship.move_to([5.05, -1.85, 0])
        self.add(auth, card, ship)

        # -------------------------------------------------- the arrows ---
        self.add(arrow([-3.65, 1.05, 0], [-2.15, 0.75, 0], seed=30))
        self.add(step_dot(1, [-2.95, 1.15, 0]))

        self.add(arrow([-1.15, -0.15, 0], [-1.15, -1.28, 0], seed=31))
        self.add(arrow([-0.35, -1.28, 0], [-0.35, -0.15, 0], seed=32))
        slip = hand_label('"verified" only', size=19, color=INK_SOFT)
        slip.move_to([0.42, -1.02, 0])
        self.add(slip, step_dot(2, [-1.5, -0.75, 0]))

        self.add(arrow([0.6, 0.15, 0], [1.45, -1.28, 0], seed=33))
        self.add(step_dot(3, [1.35, -0.5, 0]))

        self.add(arrow([3.2, -1.85, 0], [3.7, -1.85, 0], seed=34))
        self.add(step_dot(4, [3.45, -1.45, 0]))

        self.add(arrow([3.4, 0.45, 0], [0.65, 0.45, 0], seed=35,
                       color=ALERT))
        flags = hand_label("3 charges look wrong", size=19, color=ALERT)
        flags.move_to([2.05, 0.75, 0])
        self.add(flags, step_dot(5, [2.05, 0.18, 0]))

        self.add(arrow([-2.15, 0.15, 0], [-3.55, -0.2, 0], seed=36))
        self.add(step_dot(6, [-2.95, -0.25, 0]))

        # --------------------------------------------------- the rule ----
        rule = hand_label(
            "exactly right every time = service   -   takes judgment = agent",
            size=27)
        rule.move_to([0, -3.55, 0])
        self.add(rule)
