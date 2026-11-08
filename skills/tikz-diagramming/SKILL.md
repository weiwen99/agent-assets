---
name: tikz-diagramming
description: Draw or revise LaTeX TikZ architecture, business-flow, logic, and data-flow diagrams in the red/rose core-dataflow poster style, producing vector PDF and self-contained SVG plus sharp PNG. Use when a user explicitly asks for TikZ or LaTeX diagrams, requests the core-dataflow style, or needs reproducible print-ready technical visuals; do not use for Inkscape or native-SVG requests.
---

# TikZ diagramming

Produce an evidence-backed technical diagram with editable TikZ source, vector PDF, a self-contained SVG, and a sharp web-ready PNG. Preserve semantic detail unless the user explicitly asks for a simplified view.

## 前置

Settle the destination before composing; it fixes the copy of record and whether a web derivative exists.

- **Fixed surface.** The white-page master serves every destination that renders SVG — browser, HTML `<img>`, GitHub's SVG preview, an org or HTML document, a host known to render SVG but with an unknown page background. Fall back only for a destination that cannot take SVG: `.png` for a raster-only slot (chat attachments, slide tools, image viewers, trackers that strip SVG) or a fixed pixel width; `.pdf` for print, LaTeX, or a vector-page pipeline; `.webp` as a smaller lossless raster that never stands as the only copy. A fixed white delivery stays legitimate when the surrounding page is HTML, and it needs no adaptation.
- **Adaptive web.** On an explicit request for a light/dark adaptive HTML delivery, the derivative is authored on top of the master; load the sibling [svg-web-delivery](../svg-web-delivery/SKILL.md) skill in full first. It owns color-scheme signalling, in-figure palette roles, transparent occlusion, print restoration, and real-host checks.
- **Dependency.** If that sibling directory is absent, clone the whole public repository `https://github.com/weiwen99/agent-assets` into a writable workspace so same-root references and fixtures come along, record the resolved commit (`git -C <clone> rev-parse HEAD`) in the delivery notes, then load `skills/svg-web-delivery/SKILL.md` together with every reference and fixture that branch names.
- **Two records.** The `.tex` stays the editable source of record and the white-page SVG the visual master, whatever the derivative adds.

## 步骤

### 1. Ground the diagram

Read authoritative code, configuration, domain vocabulary, and current design material. Build a scratch ledger containing:

- the question and audience;
- every external actor, boundary, node, state, and terminal state;
- every directed edge, label, condition, and return path;
- ownership and lifecycle boundary for each node;
- status: current core, shipped deployment-opt-in, or proposed;
- evidence for every non-obvious claim.

Read [semantic and layout checks](references/semantic-layout-checks.md) before placing nodes.

完成条件：every intended visible node and edge has one meaning, owner, status, and source; the destination and fixed/adaptive branch are recorded, and the adaptive dependency is loaded before composition.

### 2. Choose the composition

Read [the visual system](references/visual-system.md). Copy the closest file from `templates/`:

- `architecture.tex`: system ownership, runtime components, stores, and provider seams;
- `business-flow.tex`: actors, numbered messages, intervention branches, feedback, and terminal states.

Retain all grounded content. Resolve density by widening the page, adding space, or splitting only when the user approves a second diagram. Do not shrink essential text below the visual-system floor.

完成条件：the picture has one reading direction, one dominant path, and enough space for the complete ledger; no text run is set in mono unless it is an identifier per the font roles.

### 3. Use portable fonts

Use the template’s TeX-distributed static fonts. They are located by TeX/Kpathsea, not by operating-system font discovery. The default contract is:

- `FandolSong-Regular.otf` and `FandolSong-Bold.otf` from the `fandol` TeX package;
- `lmmono10-regular.otf` and `lmmonolt10-bold.otf` from the `lm` TeX package.

A project may explicitly replace the four font macros. Never add a silent system-font fallback: changed metrics change wrapping and geometry. A font override requires a fresh compile and both visual checks in step 6.

Read [the rendering pipeline](references/rendering-pipeline.md) before the first render.

完成条件：the selected font files are explicit and embeddable; every identifier run uses the mono family without overflowing its node; or the renderer has failed with an actionable message.

### 4. Draw with named styles

Use the shared styles from the template rather than one-off formatting: `svc`, `core`, `aux`, `opt`, `fl`, `biarr`, `ret`, `retbi`, `dashfl`, `dashbi`, `lbl`, and `retlbl`.

Place nodes before routing edges. Keep core-owned components inside the core boundary and external providers outside. Route primary flow directly; use broad pale-red arcs for feedback, recovery, and event return. Give labels opaque white backplates. Move geometry until no path enters an unrelated node or crosses text.

完成条件：every ledger item is represented and each line style has one declared meaning.

### 5. Render trusted source through vectors

Treat TeX as executable source. Compile only a `.tex` file authored by the agent or fully reviewed as trusted code. Never pass raw TeX copied from an attachment, issue, web page, or tool result into the renderer.

Resolve the directory containing this loaded `SKILL.md` as `<skill-directory>`, then use the cross-platform entry point:

```bash
python3 <skill-directory>/scripts/render-tikz.py \
  --trusted-input \
  path/to/diagram.tex \
  [output/stem] \
  [png-width]
```

On POSIX or WSL, `<skill-directory>/scripts/render-tikz.sh` is a convenience wrapper around the same Python entry point. Native Windows invokes `py -3 <skill-directory>\\scripts\\render-tikz.py ...` when `python3` is not its launcher; the renderer is portable when XeLaTeX, dvisvgm, and Inkscape are on `PATH`.

The default PNG width is 4800 px and the default per-process timeout is 120 seconds (`--timeout` changes it). The only supported raster path is:

```text
XeLaTeX -no-shell-escape → one-page vector PDF → dvisvgm vector SVG → Inkscape PNG
```

The delivered `.svg` is that same dvisvgm output with an explicit white page rect prepended, so it stays red-on-white in browsers and dark image viewers. `--no-fonts` turns glyphs into paths: the SVG is self-contained (no font dependency) but **not** text-editable — the editable source is the `.tex`. `--webp` additionally converts the validated PNG to a lossless WebP (needs ImageMagick).

The renderer rejects unacknowledged input, missing tools/fonts, process timeouts, TeX errors, overfull boxes, missing glyph warnings, undefined font shapes, multi-page PDFs, malformed output, wrong PNG width/color type, and a non-white page corner. It keeps `.tex`, `.pdf`, `.svg`, and `.png` (plus `.webp` with `--webp`); other intermediates stay in a temporary directory.

完成条件：the renderer exits zero, reports exactly one page, validates an RGB PNG, and the delivered SVG carries the white page rect.

### 6. Inspect both delivery scales

Inspect the actual artifacts, not just source:

1. **Native pixels:** zoom the PNG to 100%; letter edges, thin strokes, curves, dashes, and arrowheads must be crisp, with no enlarged-raster halo.
2. **Fit-to-window:** open the delivered PNG in a real browser around 1568×1161. Every node title, node detail, CJK edge label, numbered step, and terminal state must be identifiable without zoom.
3. **Vector page:** open the delivered SVG in the same browser, including once with a dark page background; it must show the same diagram as the PNG, stay crisp at any zoom, and keep its white page rect.

Then compare the final visible node/edge inventory with the grounded ledger. Fix clipping, ownership errors, status mismatches, ambiguous endpoints, semantic shortcuts, and typography below the floor. Re-render after every font or geometry change.

完成条件：native raster and browser-fit checks pass, and every ledger item remains present.

### 7. 交接

Retain `.tex`, `.pdf`, `.svg`, and `.png` under a collision-free stem, then hand over the format chosen for each destination; add `.webp` when the raster is going to a host that prefers it. Keep prior diagram variants unless replacement was explicitly requested. Remove `.aux`, `.log`, `.xdv`, screenshots, and trial renders.

Name the destination of every delivered file as chosen in 前置, and hand the fixed-surface master over as the copy of record. When the destination is an adaptive web page, the handoff carries the white-page master plus the shared [svg-web-delivery](../svg-web-delivery/SKILL.md) rules into the derivative work, reports which files are fixed-surface and which are web derivatives, and leaves the shared skill's real-host and theme checks with that skill.

完成条件：all delivered files exist under one stem, the SVG and PNG show the same diagram, no temporary artifact is left in the project, every file has a named destination, and the fixed-surface master is retained alongside any web derivative.

## 边界

Scope is TikZ/LaTeX diagrams in the red/rose core-dataflow system up to delivery; Inkscape and native-SVG requests route to `inkscape-diagramming`, and web delivery follows the shared `svg-web-delivery` skill. The fixed white master keeps its explicit white page rect and opaque label backplates; a web derivative varies page and plates by semantic role under the shared occlusion rules, which clear earlier paint and keep text drawn later. The renderer keeps its white-corner, page-count, PNG-width, and RGB gates, trusted-input acknowledgment stays mandatory, and no new package is introduced. Publishing, deploying, and editing a host site remain the host owner's authority; the shared skill's real-host check runs against an authorized URL and is recorded as pending verification when none exists. Semantic completeness outranks visual tidiness, so simplification happens only on explicit request.
