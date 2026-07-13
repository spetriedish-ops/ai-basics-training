#!/usr/bin/env python3
"""
Pencil-boil bake-off — Claude's entry.

Builds the agentic-loop animation from Sarah's pencil sketch
(../assets/sketches/01-llm-harness-agentic-loop.jpeg), entirely from
this one script: rotate -> lighting-flatten -> ink extraction -> slice
elements by coordinate boxes -> staged build-out -> highlight laps ->
"boiling lines" displacement (3 seeds, held 5 frames = ~6 Hz) ->
ffmpeg encode. No image generation anywhere: every mark on screen is
Sarah's pencil line, cleaned and moved.

Usage (from animations/, venv active):
  python3 pencil-claude/make_agentic_loop.py            # 1080p MP4 + GIF
  python3 pencil-claude/make_agentic_loop.py --draft    # 640px quick pass
  python3 pencil-claude/make_agentic_loop.py --stills   # 4 preview PNGs

Revision knobs all live in CONFIG below (element boxes, timings, boil
amplitude, ink contrast). A caption/timing change is one edit + one run
(~2 min at 1080p).
"""

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "assets" / "sketches" / "01-llm-harness-agentic-loop.jpeg"
OUT = HERE / "out"

# ---------------------------------------------------------------- config --
PAPER = np.array([250, 247, 239], dtype=np.float32)   # #FAF7EF
INK = np.array([51, 50, 62], dtype=np.float32)        # #33323E
TEAL = np.array([46, 167, 154], dtype=np.float32)     # #2EA79A — the AI

FPS = 30
HOLD = 5          # frames per boil seed (5 @ 30fps ~ 6 Hz)
BOIL_AMP = 2.6    # px at 1080p — lively, never strobing
INK_T0, INK_T1, INK_GAMMA = 0.05, 0.32, 0.85  # ink extraction curve

# The sketch photo, rotated upright, addressed in 906x1208 "preview" px
# (the grid I picked coordinates on). CROP is the diagram region.
PREVIEW_W = 906
CROP = (55, 700, 845, 1105)   # x0, y0, x1, y1

# name: (box in preview px, appear time s). Order = z-order.
ELEMENTS = {
    "title":    ((323, 712, 560, 768), 0.4),  # x0 excludes a crossed-out smudge
    "receive":  ((208, 768, 368, 818), 1.4),
    "arrow1":   ((366, 776, 424, 812), 2.1),
    "reason":   ((418, 760, 548, 834), 2.5),
    "arrow2":   ((544, 796, 618, 860), 3.3),
    "use":      ((528, 842, 704, 918), 3.7),
    "arrow3":   ((536, 898, 622, 972), 4.5),
    "observe":  ((392, 912, 548, 992), 4.9),
    "arrow4":   ((322, 926, 404, 962), 5.7),
    "repeat":   ((142, 896, 334, 984), 6.1),
    "ex_line1": ((58, 992, 736, 1038), 11.2),
    "ex_decide": ((688, 1022, 838, 1068), 12.4),
    "ex_line2": ((328, 1038, 704, 1098), 13.2),
}
FADE_IN = 0.45    # per-element fade/rise
RISE_PX = 14

# highlight laps around the loop (teal pulse), after the build-out
NODE_ORDER = ["receive", "reason", "use", "observe", "repeat"]
LAPS = 2
LAP_STEP = 0.38   # s per node
LAPS_START = 7.2
PULSE_W = 0.55    # s width of one pulse

T_HOLD_END = 16.8   # full diagram holds until here
T_END = 18.4        # fade to empty paper -> clean loop


# ----------------------------------------------------------------- build --
def extract_ink():
    """Upright, lighting-flattened ink alpha for the crop region (float 0-1)."""
    img = Image.open(SRC).transpose(Image.Transpose.ROTATE_270).convert("L")
    s = img.width / PREVIEW_W
    box = tuple(int(round(v * s)) for v in CROP)
    crop = img.crop(box)
    bg = crop.filter(ImageFilter.GaussianBlur(int(40 * s)))
    v = np.asarray(crop).astype(np.float32)
    b = np.maximum(np.asarray(bg).astype(np.float32), 1.0)
    norm = v / b                                # 1.0 = paper, <1 = ink
    a = np.clip((1.0 - norm - INK_T0) / (INK_T1 - INK_T0), 0.0, 1.0)
    return a ** INK_GAMMA, s, box


def layout(width):
    """Output geometry: scale crop to fit width x (9/16 width) canvas."""
    W = width
    H = int(W * 9 / 16)
    cw = (CROP[2] - CROP[0])
    ch = (CROP[3] - CROP[1])
    scale = min((W * 0.92) / cw, (H * 0.92) / ch)   # margins
    ox = (W - cw * scale) / 2
    oy = (H - ch * scale) / 2
    return W, H, scale, ox, oy


def slice_elements(alpha, src_scale, W, H, out_scale, ox, oy):
    """Per element: (alpha array at output res, (x, y) paste offset)."""
    els = {}
    for name, (box, t0) in ELEMENTS.items():
        x0, y0, x1, y1 = box
        fx0 = int(round((x0 - CROP[0]) * src_scale))
        fy0 = int(round((y0 - CROP[1]) * src_scale))
        fx1 = int(round((x1 - CROP[0]) * src_scale))
        fy1 = int(round((y1 - CROP[1]) * src_scale))
        sub = alpha[fy0:fy1, fx0:fx1]
        ow = max(1, int(round(sub.shape[1] / src_scale * out_scale * src_scale / 1)))
        # output size straight from preview box * out_scale_preview
        ow = max(1, int(round((x1 - x0) * src_scale * out_scale)))
        oh = max(1, int(round((y1 - y0) * src_scale * out_scale)))
        a = np.asarray(Image.fromarray((sub * 255).astype(np.uint8)
                                       ).resize((ow, oh), Image.LANCZOS)
                       ).astype(np.float32) / 255.0
        px = int(round((x0 - CROP[0]) * src_scale * out_scale + ox))
        py = int(round((y0 - CROP[1]) * src_scale * out_scale + oy))
        els[name] = {"a": a, "pos": (px, py), "t0": t0}
    return els


def boil_fields(W, H, amp):
    """3 deterministic two-scale displacement fields (dx, dy)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    fields = []
    for seed in (1, 2, 3):
        rng = np.random.default_rng(7919 * seed)
        dx = np.zeros((H, W), np.float32)
        dy = np.zeros((H, W), np.float32)
        for k_lo, k_hi, wgt in ((2.5, 5.0, 0.65), (9.0, 15.0, 0.35)):
            k = rng.uniform(k_lo, k_hi)
            ang = rng.uniform(0, 2 * np.pi)
            kx, ky = k * np.cos(ang) / 150.0, k * np.sin(ang) / 150.0
            p1, p2 = rng.uniform(0, 2 * np.pi, 2)
            dx += wgt * np.sin(kx * xx + ky * yy + p1)
            dy += wgt * np.sin(kx * xx + ky * yy + p2)
        sc = amp * (W / 1920.0)
        fields.append((dx * sc, dy * sc))
    return fields


def warp(frame, field, xx, yy, W, H):
    """Bilinear whole-frame displacement — the boiling line."""
    dx, dy = field
    mx = np.clip(xx + dx, 0, W - 1.001)
    my = np.clip(yy + dy, 0, H - 1.001)
    x0 = mx.astype(np.int32); y0 = my.astype(np.int32)
    fx = (mx - x0)[..., None]; fy = (my - y0)[..., None]
    c00 = frame[y0, x0]; c01 = frame[y0, x0 + 1]
    c10 = frame[y0 + 1, x0]; c11 = frame[y0 + 1, x0 + 1]
    top = c00 * (1 - fx) + c01 * fx
    bot = c10 * (1 - fx) + c11 * fx
    return top * (1 - fy) + bot * fy


def ease_out(u):
    return 1 - (1 - u) ** 3


def pulse_level(name, t):
    """0..1 teal-highlight level for a node during the laps."""
    if name not in NODE_ORDER:
        return 0.0
    idx = NODE_ORDER.index(name)
    lvl = 0.0
    for lap in range(LAPS):
        c = LAPS_START + (lap * len(NODE_ORDER) + idx) * LAP_STEP
        u = (t - c) / PULSE_W
        if 0.0 <= u <= 1.0:
            lvl = max(lvl, float(np.sin(np.pi * u)))
    return lvl


def compose(t, els, W, H):
    frame = np.ones((H, W, 3), np.float32) * PAPER
    g = 1.0
    if t > T_HOLD_END:
        g = max(0.0, 1.0 - (t - T_HOLD_END) / (T_END - T_HOLD_END - 0.25))
    for name, el in els.items():
        k = np.clip((t - el["t0"]) / FADE_IN, 0.0, 1.0)
        if k <= 0 or g <= 0:
            continue
        k = ease_out(k)
        a = el["a"] * (k * g)
        px, py = el["pos"]
        py = py + int(round((1 - k) * RISE_PX))
        h, w = a.shape
        if py + h > H or px + w > W or px < 0 or py < 0:
            h = min(h, H - py); w = min(w, W - px)
            a = a[:h, :w]
        color = INK + (TEAL - INK) * pulse_level(name, t)
        region = frame[py:py + h, px:px + w]
        frame[py:py + h, px:px + w] = region * (1 - a[..., None]) \
            + color * a[..., None]
    return frame


# ------------------------------------------------------------------ main --
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", action="store_true", help="640px quick pass")
    ap.add_argument("--stills", action="store_true", help="4 preview PNGs")
    args = ap.parse_args()

    width = 640 if args.draft else 1920
    OUT.mkdir(exist_ok=True)

    alpha, src_scale, _ = extract_ink()
    W, H, out_scale, ox, oy = layout(width)
    # H must be even for yuv420p
    H -= H % 2
    els = slice_elements(alpha, src_scale, W, H,
                         out_scale / src_scale, ox, oy)
    fields = boil_fields(W, H, BOIL_AMP)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

    if args.stills:
        for t in (2.7, 6.6, 8.6, 14.0):
            f = compose(t, els, W, H)
            f = warp(f, fields[0], xx, yy, W, H)
            Image.fromarray(f.astype(np.uint8)).save(
                OUT / f"still_{t}.png")
        print("stills written to", OUT)
        return

    n_frames = int(T_END * FPS)
    suffix = "_draft" if args.draft else ""
    mp4 = OUT / f"agentic_loop{suffix}.mp4"
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo",
         "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(mp4)],
        stdin=subprocess.PIPE)
    for i in range(n_frames):
        t = i / FPS
        f = compose(t, els, W, H)
        f = warp(f, fields[(i // HOLD) % 3], xx, yy, W, H)
        enc.stdin.write(f.astype(np.uint8).tobytes())
        if i % 60 == 0:
            print(f"  frame {i}/{n_frames}", file=sys.stderr)
    enc.stdin.close()
    enc.wait()
    if not args.draft:
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(mp4),
             "-vf", ("fps=15,scale=960:-1:flags=lanczos,split[a][b];"
                     "[a]palettegen=max_colors=96[p];"
                     "[b][p]paletteuse=dither=bayer:bayer_scale=4"),
             "-loop", "0", str(OUT / "agentic_loop.gif")],
            check=True)
    print("done:", mp4)


if __name__ == "__main__":
    main()
