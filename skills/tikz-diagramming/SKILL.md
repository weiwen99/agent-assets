---
name: tikz-diagramming
description: Draw or revise LaTeX TikZ architecture, business-flow, logic, and data-flow diagrams in the red/rose core-dataflow poster style, producing vector PDF and sharp PNG. Use when a user explicitly asks for TikZ or LaTeX diagrams, requests the core-dataflow style, or needs reproducible print-ready technical visuals; do not use for Inkscape or native-SVG requests.
---

# TikZ diagramming

Produce an evidence-backed technical diagram with editable TikZ source, vector PDF, and a sharp web-ready PNG. Preserve semantic detail unless the user explicitly asks for a simplified view.

## Process

### 1. Ground the diagram

Read authoritative code, configuration, domain vocabulary, and current design material. Build a scratch ledger containing:

- the question and audience;
- every external actor, boundary, node, state, and terminal state;
- every directed edge, label, condition, and return path;
- ownership and lifecycle boundary for each node;
- status: current core, shipped deployment-opt-in, or proposed;
- evidence for every non-obvious claim.

Read [semantic and layout checks](references/semantic-layout-checks.md) before placing nodes.

**Done when:** every intended visible node and edge has one meaning, owner, status, and source.

### 2. Choose the composition

Read [the visual system](references/visual-system.md). Copy the closest file from `templates/`:

- `architecture.tex`: system ownership, runtime components, stores, and provider seams;
- `business-flow.tex`: actors, numbered messages, intervention branches, feedback, and terminal states.

Retain all grounded content. Resolve density by widening the page, adding space, or splitting only when the user approves a second diagram. Do not shrink essential text below the visual-system floor.

**Done when:** the picture has one reading direction, one dominant path, and enough space for the complete ledger.

### 3. Use portable fonts

Use the template’s TeX-distributed static fonts. They are located by TeX/Kpathsea, not by operating-system font discovery. The default contract is:

- `FandolSong-Regular.otf` and `FandolSong-Bold.otf` from the `fandol` TeX package;
- `lmmono10-regular.otf` from the `lm` TeX package.

A project may explicitly replace the three font macros. Never add a silent system-font fallback: changed metrics change wrapping and geometry. A font override requires a fresh compile and both visual checks in step 6.

Read [the rendering pipeline](references/rendering-pipeline.md) before the first render.

**Done when:** the selected font files are explicit and embeddable, or the renderer has failed with an actionable missing-package message.

### 4. Draw with named styles

Use the shared styles from the template rather than one-off formatting: `svc`, `core`, `aux`, `opt`, `fl`, `biarr`, `ret`, `retbi`, `dashfl`, `dashbi`, `lbl`, and `retlbl`.

Place nodes before routing edges. Keep core-owned components inside the core boundary and external providers outside. Route primary flow directly; use broad pale-red arcs for feedback, recovery, and event return. Give labels opaque white backplates. Move geometry until no path enters an unrelated node or crosses text.

**Done when:** every ledger item is represented and each line style has one declared meaning.

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

The renderer rejects unacknowledged input, missing tools/fonts, process timeouts, TeX errors, overfull boxes, missing glyph warnings, multi-page PDFs, malformed output, wrong PNG width/color type, and a non-white page corner. It keeps `.tex`, `.pdf`, and `.png`; intermediates stay in a temporary directory.

**Done when:** the renderer exits zero, reports exactly one page, and validates an RGB PNG.

### 6. Inspect both delivery scales

Inspect the actual artifacts, not just source:

1. **Native pixels:** zoom the PNG to 100%; letter edges, thin strokes, curves, dashes, and arrowheads must be crisp, with no enlarged-raster halo.
2. **Fit-to-window:** open the delivered PNG in a real browser around 1568×1161. Every node title, node detail, CJK edge label, numbered step, and terminal state must be identifiable without zoom.

Then compare the final visible node/edge inventory with the grounded ledger. Fix clipping, ownership errors, status mismatches, ambiguous endpoints, semantic shortcuts, and typography below the floor. Re-render after every font or geometry change.

**Done when:** native raster and browser-fit checks pass, and every ledger item remains present.

### 7. Deliver and clean

Deliver `.tex`, `.pdf`, and `.png` under a collision-free stem. Keep prior diagram variants unless replacement was explicitly requested. Remove `.aux`, `.log`, `.xdv`, temporary SVG, screenshots, and trial renders.
