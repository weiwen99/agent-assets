# Visual system

## Character

A monochrome Inkscape engineering plate: formal serif typography, black line work, sharp boxes, restrained gray fills, and large areas of white space. Hierarchy comes from geometry and density, not color or effects.

The source references contained transparent page margins. This system uses an explicit white page so black connectors remain visible in dark-background image viewers.

## Tokens

| Role | Value |
|---|---|
| Page | `#ffffff` |
| Ink and text | `#000000` |
| Business actor fill | `#e7e7e7` |
| Architecture component fill | `#e5e5e5` |
| System boundary fill | `#f3f3f3` |
| Typeface | `Noto Serif CJK SC`, then `Noto Serif`, then `serif` |
| Identifier typeface | `Noto Sans Mono CJK SC` |
| Weight/style | Regular, upright |
| Corners | Square; radius `0` |
| Effects | Flat; no shadow or gradient |

`Noto Serif CJK SC` is explicit because it supports Chinese and is installed in the target environment. Do not request Georgia and silently accept a machine-dependent fallback.

## Standard canvases

| Diagram | SVG viewBox | Default 2× PNG |
|---|---:|---:|
| Architecture | `0 0 1800 1200` | `3600 × 2400` |
| Business flow | `0 0 1920 1080` | `3840 × 2160` |

Use a 60 px outer margin. Place the title at `(60, 72)` in 48 px type. Keep content below y=120.

## Geometry

### Architecture

- Boundary: `#f3f3f3`, 4 px black stroke; label 30–34 px.
- Component: `#e5e5e5`, 3 px black stroke; normal size about 230×76 px; label 22–26 px.
- Compact component: minimum height 62 px; preserve at least 22 px horizontal inset.
- Data store: outline cylinder or a component containing explicit storage roles; use a cylinder when persistence itself matters.
- Connector: 2.5 px black stroke.

### Business flow

- Actor: `#e7e7e7`, 4 px black stroke; normal size about 250×116 px; label 28–34 px.
- Wide actor: increase width for the label; keep actor heights consistent within a lane.
- Connector: 3 px black stroke.
- Message label: 19–21 px, prefixed `1.`, `2.`, or branch forms such as `6A.`.
- Row or lane pitch: roughly 2.2–2.5 actor heights.

### Arrows

Use the shared notched triangular marker from the templates. The arrow tip meets the intended endpoint; stop the path at the node border, not inside the fill. Use heads at both ends only for a genuine request/read-write relationship.

### Optional status

A dashed border or connector means **implemented and shipped, but deployment-opt-in**. Use `10 8` dash spacing. Solid means current core. Proposed elements do not appear on a current-state plate.

## Typography

- Title: 48 px.
- Boundary label: 30–34 px.
- Primary node/actor: 24–32 px.
- Secondary line inside a node: 16–19 px.
- Edge label and annotation: 18–21 px.
- Legend/footnote: 16–18 px.

Center node labels. Keep titles and explanatory notes left-aligned. Prefer two deliberately spaced lines over shrinking important text below 16 px.

### Font roles

Serif carries prose, including numbers that state a quantity (`19 tools`, `37 ADRs`). Mono marks text a reader would copy verbatim or whose spelling is fixed: command signatures and their placeholders, flags, file names, table and field names, literal exit codes.

The templates ship the token for it: `.code { font-family:"Noto Sans Mono CJK SC","Noto Sans Mono",monospace; }`. Put `class="code"` on the label, next to `node-meta` or `edge-label`, or on a `<tspan class="code">` when only one token inside a serif label changes face. Do not write a second font stack.

Keep mono at weight 400. Hierarchy in this system comes from geometry and density, so a bolded token would be the only bold object on the plate. `Noto Sans Mono CJK SC` covers ASCII and Chinese in one family, but CJK glyphs stay full-width, so a mixed identifier is wider than the same number of Latin characters. Turning a label into an identifier therefore changes its advance width: re-center or re-measure it instead of letting the text drift out of its box.

Confirm the face before authoring: `fc-match "Noto Sans Mono CJK SC"` must echo that family. Then confirm the class actually applied by measuring one narrow-letter string (`iiiiiiiiii`) in both faces with `inkscape --query-width` at the same size: Noto Serif gives about 77.8 px against Noto Sans Mono about 111.1 px at 24 px, so a `code` run that is not clearly wider means the class did not apply. A different family from `fc-match`, or two identical widths, blocks the plate — `render-svg.sh` only proves the PNG is non-empty, so these checks are the evidence. Do not use arbitrary identifiers as the probe: mono is often *narrower* than serif for mixed strings, so width direction alone is not a test.

A plate set entirely in mono loses the contrast that marks an identifier.

## Layer order

1. `Canvas`: explicit white page.
2. `Panels`: system boundaries and swimlanes.
3. `Connectors`: every path and arrow.
4. `Nodes`: actors, components, stores, decisions, terminal states.
5. `Labels`: title, node text, edge-label backplates, annotations, legend.

Connectors therefore disappear cleanly behind opaque nodes instead of drawing through them.

## Quality bar

- One obvious reading direction and one dominant path.
- No clipped title, label, border, or arrowhead.
- No connector through text.
- No unexplained line style or shape.
- No decorative icons unless the domain meaning cannot be stated clearly in text.
- No duplicated markers, empty text frames, off-canvas objects, tiny corner ticks, floating arrowheads, or editor artifacts.
- Only grayscale colors; antialiasing is the only permitted non-token shade.
