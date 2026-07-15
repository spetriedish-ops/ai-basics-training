# Jobsite 3D — the training as a walkable world (experiment)

The whole AI Basics presentation as an interactive 3D jobsite: thirteen
stations along a winding path in run-of-show order. Jobsite scenes stand
as low-poly props in the deck's palette (garage, engine factory, paver
with its brick road, toolbox chests, the loaded truck, the crane truck,
the fleet with its shed); Sarah's pencil pages stand as textured exhibit
boards. Walk it, or teleport station to station.

## Open it (no Blender needed)

```bash
cd animations && python3 -m http.server 4173
# then open http://localhost:4173/jobsite3d/walkthrough/
```

Controls: click to walk (WASD + mouse, Shift to hurry, Esc to release) ·
arrow keys or the buttons to jump stations · station list on the right.

Everything in `walkthrough/` is self-contained: the GLB, a vendored
three.js (0.170.0), GLTFLoader, and PointerLockControls. No CDN calls.

## Rebuild the world (Blender required)

```bash
brew install --cask blender   # once
cd animations
/Applications/Blender.app/Contents/MacOS/Blender --background \
    --python jobsite3d/build_jobsite.py
```

Rebuilds `walkthrough/jobsite.glb` and `preview.png` (~20 s). The whole
world is procedural Python — `build_jobsite.py` has the palette, prop
builders, and the station table at the bottom. Moving a station, adding
a prop, or swapping an exhibit texture is one edit + one rebuild.

Exhibit textures come from `pencil-codex/source/*/cleaned_page.png` —
Codex's cleaned extractions of Sarah's sketches, reused as-is.

## Status: v0 (proof of pipeline)

Verified working: GLB export, texture packing, browser load, station
teleport, signpost text, exhibit boards showing the real sketch pages.

Ideas for v1, in rough value order:

1. **Guided tour mode** — a camera rail that drives the path
   automatically, pausing at each station (presentation replay mode).
2. **Prop fidelity** — the truck/paver/factory are blocky first drafts;
   bevels, better proportions, and cel-shade outlines would bring them
   closer to the deck's look.
3. **Station placards** — the verbatim talk-track key lines on small
   3D cards beside each station.
4. **Embedded animations** — the actual MP4s playing on drive-in-theater
   screens at their stations (three.js VideoTexture).
5. **Publish** — the walkthrough folder is static files; it can ship to
   any static host as a link.
