# Handoff → Claude Fable 5: Animated explainers for the "AI Basics" training

**From:** Sarah Petrie (Principal Solutions Engineer, Atlassian)
**To:** Claude Fable 5 (creative/animation partner, running on Sarah's personal machine)
**Date:** 2026-07-02
**Status:** Living brief — version-controlled. Pull the latest before starting a work block.

---

## 0. TL;DR — what I need from you

I'm delivering a live **"AI Basics"** training to my team and I want a set of **fun, cartoon-style
animated visuals** that make abstract AI concepts click. Think short looping animations / GIFs /
short silent video clips that drop into presentation slides and can also be embedded in a wiki.

Two jobs for you:
1. **Design + produce the animations** for the concept list in §4 (metaphor-driven, playful, but
   pedagogically honest — the metaphor must not teach the wrong thing).
2. **Solve for the technology stack** to produce them (see §6). I don't have a pipeline yet —
   recommend one, justify it against my constraints, and give me copy-paste setup steps.

You have creative latitude. Pitch metaphors freely, go deeper or wider than my list where it
helps, and suggest related concepts you think belong. I'd rather react to strong ideas than hand
you a rigid spec.

---

## 1. The session this feeds (context)

- **What:** "AI Basics" — a live, ~45–50 min foundational AI session for my team.
- **When:** July 15, 2026 (content locked ~July 10; I'm drafting the week of July 2).
- **Audience:** Enterprise sales engineers with **mixed AI literacy** — from "never touched it" to
  "already building." Smart, technically confident people, but NOT ML researchers. Explicitly
  **designed for the person who feels behind.**
- **Deliberately vendor-neutral.** This session is pure AI foundations — no company-specific
  products, no branded tools, no vendor framing. (That's a separate later session.) **Keep every
  animation vendor-agnostic** — no logos, no product names, no proprietary anything.
- **The culture we're setting:** "safe to not know." One concept at a time, relatable hooks, build
  from the bottom up. **Engaging over comprehensive** — the goal is to *raise the floor* so people
  can make sense of new AI announcements on their own, not to turn them into data scientists.
- **Format it plugs into:** presentation **slides** + a **Kahoot** quiz (interactive, playful).
  So animations must work **on a slide, playing silently, in a room.**

## 2. Goal / desired outcome

Each animation should give a viewer **one "oh, I get it now" moment** for a concept that's
otherwise abstract or intimidating. Success = a room of mixed-literacy people leaving able to
*explain the concept back in their own words*, using the metaphor as the hook.

The visuals are the "spoonful of sugar" — they lower the intimidation, make it memorable, and give
the group a shared vocabulary. They carry a friendly, human, slightly-playful personality (I have
two young kids, so the dump-truck instinct below is not an accident — cartoonish and warm is on-brand).

## 3. Core assumptions & guardrails (read before designing)

1. **Silent-first.** These play in a live deck with a presenter talking over them. No reliance on
   audio or voiceover. On-screen text/labels are welcome but keep them short and legible from the
   back of a room.
2. **Loop-friendly.** Prefer clips that loop cleanly (GIF or short MP4) so a slide can sit on one
   without an awkward hard stop.
3. **Pedagogically honest > cute.** The metaphor must not create a misconception. If a fun metaphor
   would mislead, adjust it or flag the tradeoff. (Specific example in §4 for the context/token one.)
4. **Vendor-neutral, always.** No brand names, logos, product UIs, or proprietary specifics.
5. **Voice/tone** (so any on-screen text sounds like my program — see §5): casual, direct, precise,
   no hype, no corporate fluff. And a hard stylistic ban: **avoid the "it's not X, it's Y"
   construction** (and variants: "not X, but Y" / "less X, more Y") — it's an overused AI-writing
   tell and my audience pattern-matches it instantly. State the point directly instead.
6. **Consistency.** Establish a small, reusable visual language (a recurring character/world, a
   consistent color for "the AI," etc.) so the set feels like a family, not one-offs. Propose it.
7. **Accessibility.** Readable contrast, no meaning-by-color-alone, motion that isn't seizure-risky.

## 4. The concept shortlist (prioritized) — animate these

Design a metaphor for each. **You may pitch your own metaphors freely** — where I've noted an
existing analogy, feel free to build on it or propose better. The **first one is the
proof-of-concept**: nail the style + stack on it before batching the rest.

**P0 — Proof of concept (do first):**
1. **The context window & tokens.** My instinct: a **dump truck being loaded with "context."** More
   material (instructions, tools, docs, conversation) = the agent can do more — but the truck bed is
   **finite**: overfill it and stuff falls out / it gets sluggish, and hauling more costs more fuel
   ("tokens = cost"). **Critical accuracy note:** the metaphor must make clear the truck bed
   **empties and reloads each session** — context is working memory, NOT permanent memory. Don't
   imply the truck remembers past loads. (This distinction matters a lot to me.)

**P1 — High value:**
2. **MCP vs. CLI vs. API vs. custom tools** (how an agent connects to services). The teaching point:
   a **CLI** makes the agent read unstructured text output (it has to interpret prose, which is
   brittle), while an **MCP server** hands back clean, structured, labeled data (JSON) the agent can
   use reliably — but MCP is a heavier connection and not every service has one. It's a tradeoff of
   **capability vs. cost/complexity vs. reliability of the output**, with security implications.
   (Possible metaphor seed: getting an answer as a rambling handwritten note vs. a pre-filled form —
   but pitch your own.)
3. **Chatbot vs. agent.** The "ah-ha": a **chatbot follows a script and breaks when you step off it**;
   an **agent reasons, uses tools, and adapts** to reach a goal. Show the moment one hits an obstacle
   and stops vs. the other routing around it.
4. **Anatomy of an agent** (the components working together): the **model/brain**, **tools**,
   **skills**, the **agent loop** (think → act → observe → repeat), the **harness** it runs in, and
   **subagents**. I'm building a static diagram; an animation that assembles/labels the parts and
   shows the loop running would be gold. (Teaching order: introduce **tools before skills.**)

**P2 — Valuable, keep light:**
5. **Agent orchestration** — multiple agents coordinating toward a goal (a "manager" agent
   delegating to specialists). Keep it conceptual and short; it gets its own session later.
6. **Why LLMs have limitations** (hallucinations, context overload). Mental model: an LLM is a
   **confident prediction engine**, not a knowledge database or a brain — it predicts the next
   plausible thing, which is why it can be fluently wrong. Pair well with the context-window one.

**Related concepts you're welcome to pitch** (I flagged these as fair game; add if you think they
earn a slot): tokenization (high-level — words/pieces getting chopped up), **inference vs.
training** (using the model vs. building it), and the **generalist-vs-specialist** framing for
choosing tools. I want to keep the live session lean, so treat these as optional/bonus or
deep-dive-track material.

## 5. Voice & tone reference (for any on-screen text)

- Casual, direct, intelligent, useful. No corporate fluff, filler, or performative enthusiasm.
- Precise over dramatic. Trust the visual to carry the weight; don't over-caption.
- Pair a concept with its "so what" when text allows, but brevity wins on a slide.
- **Banned construction:** "it's not X, it's Y" and its variants (see §3.5).
- Empowerment framing: the vibe is "you're early," never "you're behind." Safe to not know.

## 6. Solve for the tech stack (deliverable)

I don't have an animation pipeline. **Recommend one** and justify it against these constraints:

- **Output formats needed:** looping **GIF** and/or short **MP4/WebM**, suitable for (a) embedding
  in presentation slides that play silently, and (b) embedding in a web/wiki page. Transparent
  background a plus where it helps.
- **Runs on a personal machine** (assume macOS; call out anything OS-specific).
- **Reproducible & version-controllable** — I want the *source* of each animation (not just the
  rendered file) in a repo, so we can tweak and re-render. Prefer **code- or config-driven**
  animation (something diffable) over opaque binary project files, unless you make a strong case.
- **Low-friction to iterate** — I'll be requesting revisions; fast re-render matters.
- **Style:** cartoon/playful/warm, cohesive across the set.

Please deliver: (1) a recommended primary stack + one alternative, with the tradeoffs; (2)
copy-paste setup/install steps; (3) a project/repo structure that keeps source + rendered outputs
organized; (4) then produce the **P0 dump-truck animation** as the proof-of-concept and tell me how
to render/preview it. Once I approve style + stack, we batch the rest.

## 7. What you do NOT need / must NOT include

- No company/product names, logos, brand assets, or proprietary UIs (vendor-neutral, always).
- No real customer names, deal data, or confidential internal info — none of that is relevant here,
  and this runs on a personal machine, so keep it clean.
- No audio/voiceover dependency (silent-first).
- Don't try to be comprehensive or teach ML internals — foundations only, one idea per animation.

## 8. How to work with me

- Pitch first when unsure — a quick concept sketch/storyboard beats a finished render I have to redo.
- Flag any place a fun metaphor risks teaching something inaccurate.
- Start with the **P0 dump-truck** proof-of-concept + the stack recommendation. Everything else waits
  on my sign-off of those two.
- This brief is version-controlled; if something here seems stale, say so.
