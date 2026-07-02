# Visual language — "The Jobsite"

One recurring cartoon world so the set feels like a family. Read this before
adding a scene; all constants live in `src/style.py`.

## The world

A friendly jobsite. Work gets done here: things get loaded, hauled, built,
delivered. It maps naturally onto agents (goal → work → result) and it's warm
and physical for a mixed-literacy audience.

## The cast

- **The agent is always TEAL** (`#2EA79A`). In P0 it's the dump truck; in later
  scenes teal marks whatever plays the AI (the robot arm, the crew chief, the
  brain in the anatomy diagram). One glance = "that part is the AI."
- **Context/data/inputs are CARGO** — warm labeled blocks (amber, coral, lilac,
  sage). Color is variety only; the label carries the meaning (accessibility:
  never meaning-by-color-alone).
- **Trouble is ALERT orange-red** (`#E4572E`), used sparingly.

## The look

- Soft warm paper background (`#FDF6EC`), chunky ink outlines (`#33323E`),
  rounded corners everywhere. No gradients, no 3D.
- Labels: **Baloo 2** (bundled). Title top center, one short caption at the
  bottom per beat. Captions ≤ 8 words, ≥ 28 pt equivalent — legible from the
  back of a room.
- Motion: bouncy ease-outs for arrivals (`ease_out_bounce`), gentle sine for
  travel. Dust puffs mark impacts. Nothing strobing or high-flicker.

## Voice rules for on-screen text

- Casual, direct, lowercase captions; UPPERCASE only for titles and block labels.
- Empowerment framing ("you're early").
- **Banned:** the "it's not X, it's Y" construction and all its variants.
  State the point directly.

## Pedagogy guardrails baked into P0

- The bed **visibly empties at session end** and the next session starts empty —
  context is working memory, never permanent memory.
- Token meter fills as cargo loads — tokens are the fuel bill, tied to load size.
- Overflow shows both failure modes: things fall out AND the truck gets sluggish.
