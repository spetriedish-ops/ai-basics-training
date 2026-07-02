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


# ===================================================================
# Scribble mode — "kid's drawing brought to life"
# Hand-wobbled lines + crayon fill that colors outside the lines.
# Set SCRIBBLE_SEED env var and render multiple passes, then
# interleave frames (scripts/boil.sh) to get the "boiling" effect
# of a drawing being redrawn every few frames.
# ===================================================================
import os

import numpy as np

SCRIBBLE_SEED = int(os.environ.get("SCRIBBLE_SEED", "1"))

PAPER_SCRIBBLE = "#FAF7EF"   # plain white-ish drawing paper
FONT_HAND = "Patrick Hand"   # captions/titles — legible handwriting
FONT_SCRAWL = "Gochi Hand"   # block labels — extra kid-scrawl


def hand_label(text: str, size: float = 34, color: str = INK,
               scrawl: bool = False) -> Text:
    return Text(text, font=FONT_SCRAWL if scrawl else FONT_HAND,
                font_size=size, color=color)


def _wobble(vm: VMobject, amp: float, rng, skip_ids=frozenset()) -> VMobject:
    """Displace points with a smooth POSITION-BASED noise field.

    Manim shapes chain bezier curves that share duplicated anchor points;
    index-based noise moves the duplicates apart, shattering the path into
    open slivers whose fill is invisible. A spatial field guarantees points
    at the same location move identically, so paths stay welded and fills
    stay solid. Two scales: a low-frequency sway + high-frequency jitter.
    """
    waves = []
    for k_lo, k_hi in ((2.5, 5.0), (14.0, 22.0)):
        k = rng.uniform(k_lo, k_hi)
        ang = rng.uniform(0, 2 * np.pi)
        kx, ky = k * np.cos(ang), k * np.sin(ang)
        waves.append((kx, ky, rng.uniform(0, 2 * np.pi),
                      rng.uniform(0, 2 * np.pi),
                      0.65 if k < 10 else 0.35))

    def field(pts):
        out = np.zeros_like(pts)
        for kx, ky, p1, p2, wgt in waves:
            phase = kx * pts[:, 0] + ky * pts[:, 1]
            out[:, 0] += wgt * np.sin(phase + p1)
            out[:, 1] += wgt * np.sin(phase + p2)
        return amp * out

    for sm in vm.family_members_with_points():
        if len(sm.points) == 0 or id(sm) in skip_ids:
            continue
        try:
            arc = sm.get_arc_length()
            sm.insert_n_curves(max(2, int(arc / 0.22)))
        except Exception:
            pass
        sm.points = sm.points + field(sm.points)
    return vm


def crayonify(vm: VMobject, amp: float = 0.028, seed: int = 0,
              fill_slop: float = 1.4) -> VGroup:
    """
    Turn a clean vector shape into a crayon drawing:
      - fill layer: wobblier, slightly translucent (colors outside the lines)
      - outline layer: wobbled ink line with slightly uneven width
    Text submobjects pass through UNTOUCHED — wobbling glyph paths destroys
    letterforms (they are thinner than the wobble amplitude); the handwriting
    fonts already carry the scrawl. Deterministic per (SCRIBBLE_SEED, seed)
    so multi-pass boiling lines up.
    """
    rng = np.random.default_rng(SCRIBBLE_SEED * 7919 + seed)

    text_family = set()
    for m in vm.get_family():
        if isinstance(m, Text):
            text_family.update(id(g) for g in m.get_family())

    fill = vm.copy()
    fill.text_ids = _text_ids(fill)
    for sm in fill.family_members_with_points():
        if id(sm) in fill.text_ids:
            continue
        sm.set_stroke(width=0)
        if sm.get_fill_opacity() > 0:
            sm.set_fill(opacity=min(0.85, float(sm.get_fill_opacity())))

    outline = vm.copy()
    outline.text_ids = _text_ids(outline)
    for sm in outline.family_members_with_points():
        if id(sm) in outline.text_ids:
            sm.set_fill(opacity=0.0)  # text lives on the fill layer only
            sm.set_stroke(width=0)
            continue
        sm.set_fill(opacity=0.0)
        w = sm.get_stroke_width()
        if w:  # zero-stroke shapes (meter fill, dust) stay outline-free
            sm.set_stroke(width=max(3.5, w * rng.uniform(0.8, 1.15)))

    _wobble(fill, amp * fill_slop, rng, skip_ids=fill.text_ids)
    _wobble(outline, amp, rng, skip_ids=outline.text_ids)
    return VGroup(fill, outline)


def _text_ids(vm: VMobject) -> set:
    """ids of every submobject belonging to a Text mobject in the family."""
    ids = set()
    for m in vm.get_family():
        if isinstance(m, Text):
            ids.update(id(g) for g in m.get_family())
    return ids
