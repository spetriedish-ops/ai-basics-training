"""
WIREFRAME (still, not production) — the SDLC relay multi-agent system.

Sarah's second capstone example: standing agents at every station of the
SDLC loop, coordinating through the ticket — no shared memory, the
artifact carries the context. Complements the lost-card wireframe: that
one is a HUB (concierge coordinating), this one is a RELAY (work flows
station to station and the loop closes).

Color code matches the set: TEAL = agents (judgment), GREY = services
(rails), WHITE = shared artifacts. Kept vendor-neutral per CONTRIBUTING —
Sarah names the job board out loud.

Render:  SCRIBBLE_SEED=1 manim -qh -s src/scenes/sdlc_wireframe.py SdlcWireframe
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from manim import *  # noqa: E402
from style import (  # noqa: E402
    ALERT, AI_TEAL, AI_TEAL_DARK, CARGO_AMBER, INK, INK_SOFT,
    PAPER_SCRIBBLE, crayonify, hand_label, rrect,
)

SERVICE_FILL = "#E7E2D6"


def box(w, h, fill, title, sub=None, seed=0, title_size=24, sub_size=18,
        sub_color=INK_SOFT):
    g = crayonify(rrect(w, h, fill, radius=0.14, stroke_w=4), seed=seed)
    t = hand_label(title, size=title_size, scrawl=True)
    t.scale_to_fit_width(min(t.width, w * 0.9))
    parts = [g, t]
    if sub:
        s = hand_label(sub, size=sub_size, color=sub_color)
        s.scale_to_fit_width(min(s.width, w * 0.92))
        t.move_to([0, 0.15, 0])
        s.move_to([0, -0.21, 0])
        parts.append(s)
    else:
        t.move_to([0, 0, 0])
    return VGroup(*parts)


def arrow(p, q, seed, color=INK, width=4):
    a = Arrow(np.array(p), np.array(q), buff=0.10, stroke_width=width,
              max_tip_length_to_length_ratio=0.14, color=color)
    return crayonify(a, amp=0.02, seed=seed)


class SdlcWireframe(Scene):
    def construct(self):
        self.camera.background_color = PAPER_SCRIBBLE

        title = hand_label("THE SDLC RELAY", size=48).to_edge(UP, buff=0.25)
        subtitle = hand_label("standing agents, one ticket, a closed loop",
                              size=28, color=INK_SOFT)
        subtitle.next_to(title, DOWN, buff=0.06)
        self.add(title, subtitle)

        # ------------------------------------------- the six stations ----
        pos = {
            "triage":   [0.3, 1.55, 0],
            "coding":   [4.0, 0.55, 0],
            "review":   [4.0, -1.65, 0],
            "qa":       [0.3, -2.6, 0],
            "release":  [-3.4, -1.65, 0],
            "incident": [-3.4, 0.55, 0],
        }
        specs = {
            "triage":   ("TRIAGE AGENT", "dedupe - size - route", 30),
            "coding":   ("CODING AGENT", "writes the change", 31),
            "review":   ("REVIEW AGENT", "can block", 32),
            "qa":       ("QA AGENT", "does the fix fix it?", 33),
            "release":  ("RELEASE AGENT", "ship - watch - roll back", 34),
            "incident": ("INCIDENT AGENT", "watches prod, files tickets", 35),
        }
        boxes = {}
        for k, (t, s, seed) in specs.items():
            b = box(2.7, 1.0, AI_TEAL, t, s, seed=seed,
                    sub_color=PAPER_SCRIBBLE)
            b.move_to(pos[k])
            boxes[k] = b
            self.add(b)

        # nested delegation cameo: the coding agent's disposable helpers
        helpers = crayonify(rrect(1.5, 0.55, PAPER_SCRIBBLE, radius=0.10,
                                  stroke=AI_TEAL_DARK, stroke_w=3), seed=40)
        helpers_t = hand_label("disposable helpers", size=16,
                               color=AI_TEAL_DARK)
        helpers_t.scale_to_fit_width(1.35)
        hp = np.array([6.05, 1.55, 0])
        helpers.move_to(hp)
        helpers_t.move_to(hp)
        hline = DashedLine(pos["coding"] + np.array([0.9, 0.45, 0]),
                           hp + np.array([-0.55, -0.25, 0]),
                           dash_length=0.12).set_stroke(AI_TEAL_DARK, 2.5)
        self.add(hline, helpers, helpers_t)

        # ------------------------------------------- the job board -------
        board = box(3.3, 1.15, "#FFFFFF", "THE JOB BOARD",
                    "every handoff is a status change", seed=41,
                    title_size=26)
        board.move_to([0.3, -0.55, 0])
        self.add(board)

        # ------------------------------------------- the relay arrows ----
        self.add(arrow([1.75, 1.35, 0], [3.05, 0.85, 0], seed=50))
        self.add(arrow([4.0, 0.0, 0], [4.0, -1.1, 0], seed=51))
        self.add(arrow([3.0, -2.0, 0], [1.75, -2.4, 0], seed=52))
        self.add(arrow([-1.15, -2.4, 0], [-2.4, -2.0, 0], seed=53))
        self.add(arrow([-3.4, -1.1, 0], [-3.4, 0.0, 0], seed=54))
        self.add(arrow([-2.35, 0.85, 0], [-1.15, 1.35, 0], seed=55,
                       color=ALERT))
        broke = hand_label("something broke", size=18, color=ALERT)
        broke.move_to([-2.35, 1.45, 0]).rotate(14 * DEGREES)
        self.add(broke)

        # the coding <-> review inner loop
        retry = crayonify(CurvedArrow(
            np.array([3.3, -1.35, 0]), np.array([3.3, 0.15, 0]),
            angle=1.2, stroke_width=3.5, tip_length=0.18
        ).set_color(INK_SOFT), amp=0.02, seed=56)
        retry_t = hand_label("fix & retry", size=17, color=INK_SOFT)
        retry_t.move_to([2.35, -0.6, 0])
        self.add(retry, retry_t)

        # the ticket, mid-hop on triage -> coding
        ticket = box(1.05, 0.5, CARGO_AMBER, "BUG-42", seed=57,
                     title_size=20)
        ticket.move_to([2.6, 1.45, 0]).rotate(-6 * DEGREES)
        self.add(ticket)

        # human gate on qa -> release
        stamp = box(1.5, 0.5, "#FFFFFF", "HUMAN OK", seed=58, title_size=19)
        stamp[0][0].set_stroke(AI_TEAL_DARK)
        stamp.move_to([-1.8, -2.75, 0]).rotate(4 * DEGREES)
        self.add(stamp)

        # ------------------------------------------- the services --------
        vc = box(2.4, 0.75, SERVICE_FILL, "VERSION CONTROL", "rails",
                 seed=59, title_size=19, sub_size=15)
        vc.move_to([-5.75, -2.7, 0])
        ci = box(2.4, 0.75, SERVICE_FILL, "CI + BUILD", "rails",
                 seed=60, title_size=19, sub_size=15)
        ci.move_to([5.7, -2.7, 0])
        self.add(vc, ci)
        self.add(DashedLine([5.0, -2.45, 0], [4.6, -1.95, 0],
                            dash_length=0.12).set_stroke(INK_SOFT, 2.5))
        self.add(DashedLine([-4.85, -2.45, 0], [-4.45, -1.95, 0],
                            dash_length=0.12).set_stroke(INK_SOFT, 2.5))

        # ------------------------------------------------- the rule ------
        rule = hand_label(
            "no shared memory  -  the ticket carries the context",
            size=27)
        rule.move_to([0.3, -3.6, 0])
        self.add(rule)
