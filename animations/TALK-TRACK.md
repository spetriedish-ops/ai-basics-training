# AI Basics — talk track (beat-level speaker notes)

Working draft for Sarah's edit pass, 2026-07-14. Format: per beat — the
mental model to lead with, speaker notes, **verbatim lines** worth saying
as written, the visual cue, and a timing target. Not a teleprompter;
improvise between the bolded lines. Timing assumes ~40 min for Sarah's
portion inside a 50-min remote session.

Voice rules applied throughout (VOICE.md): declarative openings,
mental-model-first, precise adjectives, explicit "so what," functional
labels, no negation-flip constructions.

---

## Kickoff — Sarah · 🎬 00-garage · 2 min

Lead: the mental model for the whole hour is a jobsite, and the industry
history is a garage.

- Welcome; name the culture up front: **"Everything today is foundations.
  It is safe to not know any of this yet — that is exactly why we built
  the session."**
- Play the Garage over the intro. Narrate lightly: rules-following
  forklift, the van that learned one route, then an engine that can
  drive anywhere.
- Land the gag: **"And there's next year's truck — probably. By the end
  of today you'll be able to read that announcement yourself."**
- Hand off to Marta for how we actually got here.

## Marta — history of AI · ~8 min

Her content. Cue to retake: her arc ends at "agentic systems," which is
where the truck rolled out of the garage.

## Beat 1 — the model, the harness, the lifecycle · ✏️ 01b brain sketch + 🎬 01-engine-factory · 5 min

Lead with the lens: a model alone can do nothing for you; everything you
have ever used is a model wearing a harness.

- Brain sketch: **"A model on its own is a brilliant brain in a jar. It
  can think; it has no ears to hear you and no mouth to answer. The
  harness is the software built around it so you can interact with it —
  and so it can do things."**
- What an LLM is: trained on language; it reasons and generates. Keep it
  to two sentences — the Paver does the mechanics next.
- Play the Engine Factory. Narrate the lifecycle: **"Pre-training builds
  the engine from mountains of material — once, at the factory.
  Post-training is the dyno: tuning it to be helpful and safe. Release
  day is the hullabaloo you keep reading about — a new engine, nothing
  more."**
- The inference beat (odometer on screen): **"After the factory closes,
  the engine still runs — every chat message, every step an agent takes.
  That count is inference. Training happens once; inference happens every
  time, and it's the meter your bill runs on."**
- So-what for the room: when a customer asks why AI costs scale with
  usage, inference is the answer — the engine fires per request.

## Beat 2 — how the engine works · 🎬 02-paver · 3 min

Lead: the model is a prediction engine, and that one fact explains both
its power and its failures.

- Play the Paver. **"It lays the road it drives on, one brick at a time,
  choosing each brick by the road already behind it. Words in, words
  out — the bricks are tokens, and tokens in and tokens out both cost."**
- Hallucination, honestly: **"Sometimes it paves straight past the
  turnoff — confident, smooth, wrong. It predicts; it never checks the
  map. That's why it can be fluently wrong, and why your judgment stays
  in the loop."**

## Beat 3 — the agentic loop · ✏️ 03-agentic-loop · 3 min

Lead: everything an agent does is one loop, repeated.

- Play the pencil loop. Walk it as it draws: receive input → reason →
  use tools / take an action → observe the result → repeat until done.
- **"Hold onto this shape. Every agent you meet today — and every one a
  vendor shows you next quarter — is this loop wearing different
  clothes."**
- Worked example is on the page (search → inspect → decide what's
  missing → search again → answer). Let it play; no extra words needed.

## Beat 4 — frontier labs, models, harnesses, APIs · ✏️ 04-frontier-labs · 4 min

Lead: the industry chart everyone struggles to read becomes simple with
yesterday's vocabulary — companies build engines, engines ship in
vehicles.

- Walk the rows: labs → their models → their harnesses. **"The company
  is the factory. The model is the engine. The harness is the vehicle it
  ships in. Most confusion you hear in customer meetings is someone
  mixing those three rows."**
- The API row: **"The API is the fourth row — buying engine access
  directly and building your own vehicle around it."**
- Foundation models: **"A foundation model is an engine built to be
  built on. Few factories, many badges — Cursor's Composer is a Kimi
  engine, re-tuned in Cursor's shop, shipped under Cursor's name. Open
  weights are the factories that publish their blueprints."** (Asterisks
  on the page: Gemma, Llama.)
- Wrap the page: **"Multimodal is one engine with many senses — text,
  images, audio. Multi-model is many engines in one product. They sound
  the same in a meeting and they are different architecture decisions."**
- Kahoot slot here if using the mid-session break.

## Beats 5–8 — the harness, walked spoke by spoke · ✏️ harness player (stages) · 10 min

Lead: this map is the whole middle of the session; everything so far
plugs into it. Use the interactive player; each stage holds while you
talk.

- **Stage 1–2 (Harness, Model):** re-anchor. The engine slots into the
  center. Model examples on the page tie back to the landscape.
- **Stage 3 (Interaction/application layer):** **"Same agent, different
  surface — chat, CLI, IDE, embedded in the tools you already use. Where
  you meet it changes what it can do for you."**
- **Stage 4 (Guardrails):** **"Guardrails live in three places: the lab
  gates what the model will do, the harness gates what the agent may do,
  and your org gates what it's allowed to touch. When a security buyer
  asks 'how do we stop it doing something it shouldn't' — this is the
  slide in your head."**
- **Stage 5 (Tools) → detour:** play 🎬 06-toolbox, then ✏️ 07-mcp-cli-api.
  **"One MCP connection brings a whole toolbox, and every tool ships an
  instruction card that rides with the agent, used or not. More tools
  mean more ability and more weight — and past a point, worse choices.
  Curate the toolbox for the job."** CLI and API tradeoffs are on the
  pencil page: CLI answers in prose the agent must interpret; the API is
  the standardized port — exactly right, every time, for scripted work.
- **Stage 6 (Context) → detour:** play 🎬 08-context-truck (simulator
  optional). **"The bed is the context window — everything the agent
  knows for this job rides in it, everything in it costs tokens, and the
  bed empties at the end of every session. A brilliant contractor with
  amnesia: superb on the job, blank slate every morning."** Memory =
  notes at the depot, reloaded at a cost. Truncation = oldest cargo
  falls out first.
- **Stage 7 (Skills):** **"A tool is what the agent can do. A skill is
  knowing how to do a job well — the playbook stays in the glovebox
  until the job matches, which is why skills are cheap until used."**
- **Stage 8:** the page asks its own closing question. Read it aloud and
  let it hang: "if this is a harness, what is an agent?"

## Beat 9 — assembly payoff · 🎬 09-pop-the-hood · 2 min

- Minimal narration; the scene re-runs everything just taught in ~30
  seconds. **"Everything you just learned, clicking together."**
- The van pulls up at the end: **"Hold that thought."**

## Beat 10 — what is an agent · ✏️ 10-what-is-an-agent · 4 min

Lead: the definition, then the terminology trap everyone in this room
will hit in the field.

- **"An agent is a model, in a harness, pointed at a goal."**
- The ambiguity, named plainly: **"Codex is a harness and a coding
  agent. Claude Code is a harness and a coding agent. The buyer names
  the bundle by the job; the builder names it by the machine. When a
  customer calls something an agent and a vendor calls it a platform,
  nobody in that meeting is wrong — they're describing different layers
  of the same thing."**
- General-purpose vs specialized, off the page: few famous generalists;
  specialists multiplying by job family. **"A specialized agent is
  usually the same engine in a narrower truck — tools curated, skills
  loaded, guardrails tightened for one job."**
- Takeaway for customer conversations: the fastest way to understand any
  AI product a customer names is to ask which model, which harness,
  what goal.

## Beat 11 — multi-agent orchestration · 🎬 11-fleet + ✏️ 12-orchestration (+ wireframes optional) · 6 min

Lead: two patterns cover everything in this space, and two questions
tell them apart.

- Play the Fleet. Narrate the van: own bed, own fuel, brings back only
  the result. **"Subagents are fresh, short-lived workers with one
  narrow task. The orchestrator owns the goal and synthesizes the
  outputs into the final product."** (Her sketch page plays after — the
  incinerator lands the "disposable" point; let it.)
- The two-question test: **"Who owns the goal, and does anything survive
  the job? One owner and disposable helpers — that's delegation. Standing
  agents with their own roles, coordinating with each other — that's a
  multi-agent system. Vendor decks blur these constantly; you now
  don't have to."**
- Optional depth (wireframes as slides): the lost card — **"You talked
  to one agent; you were served by a system"** — and the SDLC relay —
  **"the agents never share memory; the ticket carries the context, and
  every handoff is a status change."** For this room: the job board is
  the product your customers already run.
- The seam rule, once, slowly: **"If it must be exactly right every
  single time, it's a service. If it takes judgment, it's an agent.
  Everything between two tool calls is inference."**

## Close · 2 min

- Callback to the garage: **"Next year's truck is coming — probably
  several. The difference after today: you'll read the announcement and
  know whether you're looking at a new engine, a bigger bed, a new
  attachment standard, or just a fresh coat of paint."**
- Empowerment close, per the program's framing: **"Nobody in this
  industry is more than a couple of years ahead of you. You're early —
  and now you have the mental model."**
- Final Kahoot / Q&A.

---

### Notes for Sarah's edit pass

- Every bolded line is a candidate for your rewrite — the diff is the
  signal (your preferred calibration method; I'll synthesize patterns
  from whatever you change).
- Nothing here commits you to follow-up sessions or deliverables.
- Beat 5–8 is the compression risk: ten minutes is realistic only if
  stages 1–2 stay under a minute combined. The escape valve is trimming
  the CLI/API sentences in stage 5 — the pencil page carries them.
