# AI Basics — animated explainers

Cartoon-style looping animations for the "AI Basics" training. Every animation is
**Python source code** (Manim), so the whole set is diffable, version-controlled,
and re-renderable with one command.

## The stack

**Primary: [Manim Community Edition](https://www.manim.community/)** (MIT license)

Why it fits the brief:

- **Code-driven and diffable.** Each animation is a readable Python file. Revisions
  are git diffs, and re-rendering after a tweak is one command.
- **Renders headless.** No GUI needed — which means Claude can write *and render*
  finished GIFs/MP4s directly during a working session, and the identical pipeline
  runs on a Mac. Iterations happen in chat; you only pull and re-render when you
  want to own the output locally.
- **Output formats:** MP4, GIF (`--format=gif`), WebM, and transparent
  MOV/WebM (`-t` flag) for overlaying on slide backgrounds.
- **MIT licensed** — zero commercial licensing questions for work use.
- **Cartoon style is achievable:** rounded shapes, chunky outlines, bounce easing,
  and a bundled playful font (Baloo 2, OFL license, in `assets/fonts/`).

Tradeoffs to know: no real-time scrubbing preview (you render to see — low-quality
renders take seconds, so it's fine in practice), and highly organic "squash and
stretch" character animation takes more code than a dedicated animation tool.

**Alternative: [Motion Canvas](https://motioncanvas.io/)** (MIT license)

TypeScript-based, purpose-built for explainer animations, with a gorgeous
real-time browser preview where you scrub the timeline while editing code.
Better choice if you want to hand-tune timing yourself by feel. Tradeoffs:
export runs through the browser editor (harder to automate in CI or render
headless in a chat session), and GIF output needs an ffmpeg step from the
exported frames. (Remotion is a third option — React-based, excellent headless
CLI — but it requires a paid company license at Atlassian's size, so it's out.)

## Setup (macOS)

```bash
# 1. System dependencies (Homebrew)
brew install ffmpeg pkg-config pango

# 2. Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Sanity check
manim --version
```

## Rendering

```bash
# Fast draft (480p15) — use while iterating
manim -ql --media_dir renders src/scenes/context_window.py ContextWindow

# Final quality (1080p30 MP4)
manim -r 1920,1080 --fps 30 --media_dir renders src/scenes/context_window.py ContextWindow

# Or run the whole final pipeline (MP4 + optimized looping GIF):
./scripts/render.sh context_window ContextWindow

# Scribble style with boiling lines (3 seed renders + frame interleave):
./scripts/boil.sh context_window ContextWindow
```

Finished assets land in `renders/final/`. Manim's intermediate output
(`renders/videos/`, partial movie files) is gitignored; only source and final
assets are committed.

## Repo layout

```
assets/fonts/        Bundled OFL fonts (Baloo 2, Fredoka) — reproducible everywhere
src/style.py         The shared visual language: palette, fonts, reusable parts
src/scenes/          One Python file per animation
scripts/render.sh    One-command final render (MP4 + looping GIF)
renders/final/       Committed, slide-ready outputs
STYLE.md             The visual language spec (read before adding a scene)
```

## Status

| # | Concept | Scene | Status |
|---|---------|-------|--------|
| P0 | Context window & tokens | `context_window.py` | ✅ scribble redesign — awaiting style sign-off |
| P1 | MCP vs CLI vs API vs custom tools | — | waiting on P0 sign-off |
| P1 | Chatbot vs agent | — | waiting on P0 sign-off |
| P1 | Anatomy of an agent | — | waiting on P0 sign-off |
| P2 | Agent orchestration | — | waiting on P0 sign-off |
| P2 | Why LLMs have limitations | — | waiting on P0 sign-off |
