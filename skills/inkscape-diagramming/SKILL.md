---
name: inkscape-diagramming
description: Draw or revise architecture diagrams, business flowcharts, logic diagrams, system maps, and data-flow diagrams in a restrained monochrome Inkscape style, producing editable SVG plus PNG. Use when a user explicitly requests Inkscape or native SVG, asks for the DSP/Adx monochrome reference style, or wants that visual system across projects; do not use when the user explicitly requests TikZ or LaTeX.
---

# Inkscape diagramming

Produce an evidence-backed diagram, not decorated prose. The visual language is monochrome, flat, spacious, and intentionally hand-composed: serif labels, sharp rectangles, light-gray fills, black ink, and direct arrows.

## 前置

Settle the destination before a layout recipe is chosen; it fixes the copy of record and whether a themed derivative exists.

- **Fixed surface.** The white-page SVG is the master and the editable copy of record: it renders at any zoom in a browser, an HTML `<img>`, GitHub's SVG preview, an org or HTML document, a later Inkscape edit, or a host known to render SVG but with an unknown page background. Use `.png` only for a slot that accepts nothing else (chat attachments, slide tools, image viewers, hosts that strip SVG); the raster always comes from the same SVG at 2×, is never upscaled, and never stands in for an available SVG. A fixed white delivery stays legitimate when the surrounding page is HTML, and it needs no adaptation.
- **Adaptive web.** On an explicit request for a light/dark adaptive HTML delivery, the derivative is authored on top of the master; load the sibling [svg-web-delivery](../svg-web-delivery/SKILL.md) skill in full first. It owns color-scheme signalling, in-figure palette roles, transparent occlusion, print restoration, and real-host checks.
- **Dependency.** If that sibling directory is absent, clone the whole public repository `https://github.com/weiwen99/agent-assets` into a writable workspace so same-root references and fixtures come along, record the resolved commit (`git -C <clone> rev-parse HEAD`) in the delivery notes, then load `skills/svg-web-delivery/SKILL.md` together with every reference and fixture that branch names.
- **Editable form.** The derivative adapts a copy: live `<text>`, the named layers, stable group IDs, and one shared arrow marker per direction survive; marker and light-region fills are recoloured by semantic role, never converted to paths.

## 步骤

### 1. Ground the semantic map

Read the authoritative code, configuration, and current design material before drawing. Build a scratch inventory with:

- audience and the single question the diagram answers;
- external actors, system boundaries, nodes, directed edges, and edge labels;
- status of each item: current core, shipped but deployment-opt-in, or proposed;
- the source supporting every non-obvious claim;
- details deliberately omitted to preserve the chosen abstraction level.

For a current-state plate, use solid treatment for active core, dashed treatment for shipped deployment-opt-in elements, and omit proposals. Never infer deployment activation from the existence of code.

完成条件：every visible node and connection has a defined meaning and status, and adjacent abstraction levels have been removed; the destination and fixed/adaptive branch are recorded, and the adaptive dependency is loaded before composition.

### 2. Select one layout recipe

Read [the visual system](references/visual-system.md), then choose the matching branch in [layout recipes](references/layout-recipes.md):

- architecture: boundaries, components, stores, and provider seams;
- business flow: actors plus numbered messages and return arcs;
- logic/data flow: one dominant direction with explicit decisions or transformations.

Copy the corresponding file in `templates/`; keep its viewBox, CSS tokens, definitions, and layer order. Adapt the canvas only when the content cannot remain legible at the template ratio.

完成条件：the diagram has one declared viewpoint, one reading direction, and one dominant path; prose and quantity numbers stay serif, every identifier run uses the `code` token, and no plate is set entirely in mono.

### 3. Compose before connecting

Place title, boundaries, nodes, and terminal states first. Use a consistent grid and generous gaps. Then route connectors:

1. short local flow: horizontal or vertical line;
2. boundary crossing: orthogonal path with few bends;
3. return, feedback, or recovery: one broad cubic Bézier arc;
4. optional interaction: dashed connector;
5. bidirectional interaction: one line with heads at both ends only when both directions are semantically real.

Keep connectors behind nodes. Put edge labels in the label layer with a white backplate. Move geometry until no connector crosses text, clips an arrowhead, or enters an unrelated node.

完成条件：the primary path is readable without tracing crossings and every secondary path is visibly subordinate.

### 4. Author an editable SVG

Use live `<text>` and ordinary SVG primitives. Preserve the named Inkscape layers: `Canvas`, `Panels`, `Connectors`, `Nodes`, `Labels`. Give semantic groups stable IDs. Use `<title>` and `<desc>` for accessibility. Keep one shared arrow marker per direction instead of Inkscape-generated duplicates.

Use the explicit white page rectangle. This preserves black ink in browsers and dark image viewers while keeping the output visually identical to the original references on white.

完成条件：the SVG opens as XML, remains editable in Inkscape, and contains no rasterized text or accidental editor residue.

### 5. Render and inspect the actual image

Render with:

```bash
scripts/render-svg.sh path/to/diagram.svg path/to/diagram.png
```

The default scale is 2×. Inspect the PNG itself on white. Check title and label clipping, text centering, line crossings, arrow direction, boundary membership, dashed-status consistency, whitespace balance, and grayscale-only color usage. Revise the SVG and render again until every check passes.

For semantic verification, compare the final node/edge inventory against the grounded map. A beautiful missing edge is still wrong.

完成条件：Inkscape exports successfully, visual inspection finds no overlap or clipping, and the final inventory accounts for every intended node and edge.

### 6. Deliver the pair

Keep both the editable `.svg` and rendered `.png` as the delivery set; hand over the selected format for each destination. State the viewpoint and any important omissions. Keep temporary composites or experimental renders out of the project.

完成条件：both files exist under one stem, the SVG still opens as editable XML, and the PNG was rendered from that same SVG.

### 7. 交接

Hand over the pair against the destination chosen in 前置: the `.svg` stays the copy of record and every delivered file gets its destination named, while the editable SVG remains the starting point for any later revision.

When the destination is an adaptive web page, the handoff carries that editable SVG plus the shared [svg-web-delivery](../svg-web-delivery/SKILL.md) rules into the derivative work, reports which files are fixed-surface and which are web derivatives, and leaves the shared skill's real-host and theme checks with that skill.

完成条件：the format handed over is the first one the destination actually renders, the SVG remains the copy of record, every delivered file has a named destination, and an adaptive derivative is handed off with the shared web skill's rules applied.

## 边界

Scope is monochrome Inkscape/native-SVG diagrams up to delivery; TikZ and LaTeX requests route to `tikz-diagramming`, and web delivery follows the shared `svg-web-delivery` skill. The fixed white master keeps its explicit white page rectangle and label backplates; a web derivative varies page and plates by semantic role under the shared occlusion rules, which clear earlier paint and keep text drawn later. `<text>` stays live, the named layers, stable IDs, and shared arrow markers stay intact, and recolouring happens through attributes and CSS custom properties on the same editable drawing; a mask that needs a wrapper group may add one around existing content. `scripts/render-svg.sh`, the 2× default, and the template viewBox and layer order stay as they are, and no new package is introduced. Publishing, deploying, and editing a host site remain the host owner's authority; the shared skill's real-host check runs against an authorized URL and is recorded as pending verification when none exists.
