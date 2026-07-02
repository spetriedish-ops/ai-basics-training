"""
Shared visual language for the AI Basics animation set.

One world, reused everywhere:
  - "The AI" is always TEAL. Anything the AI is or does wears this color.
  - Stuff we GIVE the AI (context, data, inputs) comes as warm CARGO blocks.
  - Chunky ink outlines, rounded corners, soft paper background.
  - All label text: Baloo 2 (bundled in assets/fonts, OFL license).

Every scene imports from here so the set feels like a family.
"""

from pathlib import Path

import manimpango
from manim import *

# ---------------------------------------------------------------- fonts ----
_FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"
for _f in _FONT_DIR.glob("*.ttf"):
    manimpango.register_font(str(_f))

FONT = "Baloo 2"

# -------------------------------------------------------------- palette ----
PAPER = "#FDF6EC"     # background — soft warm paper
INK = "#33323E"       # outlines + text
INK_SOFT = "#8B8A97"  # secondary text, hubs

AI_TEAL = "#2EA79A"       # "the AI" — used for the agent everywhere
AI_TEAL_DARK = "#1F7A71"  # shading / bed panels

CARGO_AMBER = "#FFC94D"   # context blocks come in a warm family;
CARGO_CORAL = "#FF8A5C"   # color is variety only — labels carry meaning
CARGO_LILAC = "#C3B1E1"
CARGO_SAGE = "#A8D5A2"

ALERT = "#E4572E"         # overflow / warning
CLOUD = "#C9C5BD"         # dust puffs

STROKE_W = 5

# -------------------------------------------------------------- helpers ----

def label(text: str, size: float = 30, color: str = INK, bold: bool = True) -> Text:
    return Text(text, font=FONT, font_size=size, color=color,
                weight="BOLD" if bold else "NORMAL")


def rrect(w: float, h: float, fill: str, radius: float = 0.14,
          stroke: str = INK, stroke_w: float = STROKE_W) -> RoundedRectangle:
    return RoundedRectangle(
        corner_radius=radius, width=w, height=h,
        fill_color=fill, fill_opacity=1.0,
        stroke_color=stroke, stroke_width=stroke_w,
    )


def cargo_block(text: str, fill: str, w: float = 1.30, h: float = 0.72) -> VGroup:
    """A labeled block of 'context' that gets loaded into the agent."""
    box = rrect(w, h, fill)
    tag = label(text, size=24)
    tag.scale_to_fit_width(min(tag.width, w * 0.82))
    tag.move_to(box.get_center())
    return VGroup(box, tag)


def wheel(radius: float = 0.40) -> VGroup:
    tire = Circle(radius=radius, fill_color=INK, fill_opacity=1.0,
                  stroke_color=INK, stroke_width=STROKE_W)
    hub = Circle(radius=radius * 0.45, fill_color=INK_SOFT, fill_opacity=1.0,
                 stroke_color=INK, stroke_width=3)
    spoke1 = Line(ORIGIN, RIGHT * radius * 0.42, stroke_color=INK, stroke_width=3)
    spoke2 = Line(ORIGIN, UP * radius * 0.42, stroke_color=INK, stroke_width=3)
    return VGroup(tire, hub, spoke1, spoke2)


def make_roller(radius: float):
    """Updater that spins a wheel to match its horizontal travel."""
    state = {"x": None}

    def roll(m, dt):
        x = m.get_center()[0]
        if state["x"] is not None and dt > 0:
            m.rotate(-(x - state["x"]) / radius)
        state["x"] = x

    return roll


def puff(at, n: int = 3, spread: float = 0.35) -> VGroup:
    """Little dust cloud for impacts."""
    import numpy as np
    rng = np.random.default_rng(7)
    dots = VGroup()
    for i in range(n):
        off = np.array([rng.uniform(-spread, spread),
                        rng.uniform(0.0, spread), 0.0])
        c = Circle(radius=0.10 + 0.05 * i, fill_color=CLOUD, fill_opacity=0.9,
                   stroke_width=0).move_to(at + off)
        dots.add(c)
    return dots
