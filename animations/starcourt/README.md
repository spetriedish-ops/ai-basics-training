# The mall behind the mall — animation collection

The presenter player now contains four independently playable scenes:

| Scene | Duration | Teaching beats |
|---|---:|---|
| Mall opener | 19s | Ordinary mall; hidden corridors; click-cued spooky reveal |
| MCP directory | 34s | Useful tool menu; expanding descriptions/context; wrong tool; retry |
| CLI terminal | 35s | Type command; interpret response; typo; correct and retry |
| Route comparison | 46s | Visible computer control; hidden MCP/CLI/API routes |

## Presenter controls

Open `interactive/index.html`. It starts with an unbranded daylight mall and a
neutral player. Each numbered beat ends in an indefinite native hold. Use
**Next beat**, the right arrow, or a beat button to advance. The first two
opener beats remain in daylight for as long as needed. Click **3. Make it
spooky** when the narration introduces Stranger Things: the lights dim, then
the red outlined title and Starcourt shop names appear. The player changes
color with the film. The reveal is silent; “click” is a presenter action.

Scene tabs select the MCP directory, CLI terminal, or original comparison.
**Play whole scene** is an explicit continuous preview of the selected film,
including its transitions. MP4 and Still download links follow the selection.
R replays the current beat; F enters fullscreen. Left/right also work there.

The three new masters, GIFs, and stills use the names `mall_opener`,
`mcp_directory`, and `cli_terminal` in `out/`. Their chapter and hold clips are
under `interactive/stages/<name>/` and `interactive/holds/<name>/`. Render
checkpoints are in `source/<name>/`.

## New scene source and checks

`render_service_scenes.py` builds the three new clips and writes the collection
player. It reuses the mall architecture and visual helpers from
`render_mall_routes.py`; their default night rendering is preserved.

```bash
animations/.venv/bin/python animations/starcourt/render_service_scenes.py --prepare-only
animations/.venv/bin/python animations/starcourt/render_service_scenes.py
# To regenerate one film, append --scene mall_opener (or mcp_directory / cli_terminal).
animations/.venv/bin/python animations/scripts/verify.py animations/starcourt/out/mall_opener.mp4
animations/.venv/bin/python animations/scripts/verify.py animations/starcourt/out/mcp_directory.mp4
animations/.venv/bin/python animations/scripts/verify.py animations/starcourt/out/cli_terminal.mp4
animations/.venv/bin/python animations/starcourt/verify_service_scenes.py
```

The MCP backpack depicts the agent's context. It fills as descriptions are
loaded and stays full through the retry. Arcade coins symbolize token use;
they are not a measured cost. A comments-tool call can succeed technically
while returning the wrong information for the goal.

The CLI command and response are illustrative, not Teamwork Graph CLI syntax
or a literal Jira response schema. `issue reed TEAM-24` is rejected locally:
no packet travels, no endpoint opens, and no response prints. After correction,
the successful read returns data. The checklist/status beat shows that a
completed checklist need not mean a completed issue. The caption says CLI
*can* be lighter on context, not that every CLI always is.

Checks cover video formats, every chapter-to-hold seam, neutral branding before
the cue, context growth, wrong/correct tool selection, printing after a service
response, and absence of a service call for the invalid command. Browser QA
also exercises manual reveal timing, scene navigation, and looping holds.

## Route comparison

This film combines the storefront contrast with storyboard Clip 7's three
service routes. Starcourt reference research is in
`../NUGGET-08-STARCOURT-STORYBOARD.md`.

The key distinction is visibility: computer control moves a visible cursor
through storefront interactions. MCP, CLI, and direct API requests use only
the hidden service corridor. A continuous wall separates them. The audience
sees the backstage activity through a temporary cutaway; the end-user view
stays still throughout. The wall closes again at the end.

## Review and use

- `out/mall_routes.mp4` — silent 1920×1080, 30 fps, 46-second master.
- `out/mall_routes.gif` — smaller looping preview.
- `out/mall_routes_still.png` — completed comparison tableau.
- `interactive/index.html` — full playback or six independently playable beats
  with native ambient hold clips; left/right selects a beat, R replays, and F
  enters fullscreen. Native video controls support pause and scrubbing.
- `source/storyboard.jpg` — time-stamped visual checkpoints.

Serve `animations/` over localhost and open `/starcourt/interactive/`.

Timing: computer control 0–10s; corridor reveal 10–16s; MCP 16–24s;
CLI 24–32s; API 32–40s; comparison and return to the public view 40–46s.
Each backend route performs one example read of issue TEAM-24 with Project A
read access. The shutter opens only after the access check. A returning packet
travels back along the same hidden route.

## Source and regeneration

`render_mall_routes.py` defines the layered architecture, cursor, agent, routes,
lighting, captions, and timing. Its crimson outlined serif title, shadowed
stores, neon reflections, industrial pipes, and sparse drifting dust move the
look toward Stranger Things. The cutaway below the storefronts is a teaching
diagram, not an assertion about the set's literal floor plan.

Typography uses locally installed Baskerville Bold and Menlo plus the bundled
Fredoka font. System fonts are read at render time and are not redistributed;
the renderer falls back to the bundled font if they are unavailable. No remote
images, footage, or browser recording are needed. `player.html` is the preview
template. `source/v1/` preserves the first proof's source and still for reference.

From the repository root:

```bash
animations/.venv/bin/python animations/starcourt/render_mall_routes.py --prepare-only
animations/.venv/bin/python animations/starcourt/render_mall_routes.py
animations/.venv/bin/python animations/scripts/verify.py animations/starcourt/out/mall_routes.mp4
animations/.venv/bin/python animations/starcourt/verify.py
```

## Teaching boundaries

Invisible means no frontend navigation is required. Backend calls can still
produce results that an app displays and can be recorded in service logs.
The film ends with that distinction: the result can appear; the clicks don't.

The route labels and terminal command are illustrative, not runnable Atlassian
syntax. This example chooses three routes with the same operation and authority;
it does not imply that every MCP tool or CLI command necessarily calls an API,
or that real connectors always expose identical operations, credentials, or
outputs. MCP tools can call a service API, run a computation, or use other
implementations. A permission check precedes each success in this example.

Technical reference: [MCP tools specification](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/server/tools.mdx).

The three labeled stations are distinct agent interfaces located entirely in
the backstage cutaway. They share one endpoint in this example; the matching
returned packets represent the same underlying issue, though response formats
can differ between real interfaces.

Verification checks the encoded 1080p deliverables, six chapter/hold transitions,
door opening after each check, and the revised palette and visible labels.
It also checks backend geometry stays behind the wall, storefront pixels stay
identical throughout backend calls, computer-control pixels visibly change,
and the final wall hides the corridor again.
