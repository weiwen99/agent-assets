---
name: inkscape-diagramming
description: Draw or revise architecture diagrams, business flowcharts, logic diagrams, system maps, and data-flow diagrams in a restrained monochrome Inkscape style, producing editable SVG plus PNG. Use when a user explicitly requests Inkscape or native SVG, asks for the DSP/Adx monochrome reference style, or wants that visual system across projects; do not use when the user explicitly requests TikZ or LaTeX.
---

# Inkscape diagramming

Produce an evidence-backed diagram, not decorated prose. The visual language is monochrome, flat, spacious, and intentionally hand-composed: serif labels, sharp rectangles, light-gray fills, black ink, and direct arrows.

## Process

### 1. Ground the semantic map

Read the authoritative code, configuration, and current design material before drawing. Build a scratch inventory with:

- audience and the single question the diagram answers;
- external actors, system boundaries, nodes, directed edges, and edge labels;
- status of each item: current core, shipped but deployment-opt-in, or proposed;
- the source supporting every non-obvious claim;
- details deliberately omitted to preserve the chosen abstraction level.

For a current-state plate, use solid treatment for active core, dashed treatment for shipped deployment-opt-in elements, and omit proposals. Never infer deployment activation from the existence of code.

**Done when:** every visible node and connection has a defined meaning and status, and adjacent abstraction levels have been removed.

### 2. Select one layout recipe

Read [the visual system](references/visual-system.md), then choose the matching branch in [layout recipes](references/layout-recipes.md):

- architecture: boundaries, components, stores, and provider seams;
- business flow: actors plus numbered messages and return arcs;
- logic/data flow: one dominant direction with explicit decisions or transformations.

Copy the corresponding file in `templates/`; keep its viewBox, CSS tokens, definitions, and layer order. Adapt the canvas only when the content cannot remain legible at the template ratio.

**Done when:** the diagram has one declared viewpoint, one reading direction, and one dominant path.

### 3. Compose before connecting

Place title, boundaries, nodes, and terminal states first. Use a consistent grid and generous gaps. Then route connectors:

1. short local flow: horizontal or vertical line;
2. boundary crossing: orthogonal path with few bends;
3. return, feedback, or recovery: one broad cubic Bézier arc;
4. optional interaction: dashed connector;
5. bidirectional interaction: one line with heads at both ends only when both directions are semantically real.

Keep connectors behind nodes. Put edge labels in the label layer with a white backplate. Move geometry until no connector crosses text, clips an arrowhead, or enters an unrelated node.

**Done when:** the primary path is readable without tracing crossings and every secondary path is visibly subordinate.

### 4. Author an editable SVG

Use live `<text>` and ordinary SVG primitives. Preserve the named Inkscape layers: `Canvas`, `Panels`, `Connectors`, `Nodes`, `Labels`. Give semantic groups stable IDs. Use `<title>` and `<desc>` for accessibility. Keep one shared arrow marker per direction instead of Inkscape-generated duplicates.

Use the explicit white page rectangle. This preserves black ink in browsers and dark image viewers while keeping the output visually identical to the original references on white.

**Done when:** the SVG opens as XML, remains editable in Inkscape, and contains no rasterized text or accidental editor residue.

### 5. Render and inspect the actual image

Render with:

```bash
scripts/render-svg.sh path/to/diagram.svg path/to/diagram.png
```

The default scale is 2×. Inspect the PNG itself on white. Check title and label clipping, text centering, line crossings, arrow direction, boundary membership, dashed-status consistency, whitespace balance, and grayscale-only color usage. Revise the SVG and render again until every check passes.

For semantic verification, compare the final node/edge inventory against the grounded map. A beautiful missing edge is still wrong.

**Done when:** Inkscape exports successfully, visual inspection finds no overlap or clipping, and the final inventory accounts for every intended node and edge.

### 6. Deliver the pair

Deliver both the editable `.svg` and rendered `.png`. State the viewpoint and any important omissions. Keep temporary composites or experimental renders out of the project.
