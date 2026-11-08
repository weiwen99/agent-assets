# Rendering pipeline

## Required tools and TeX packages

Commands:

```text
xelatex
kpsewhich
dvisvgm
inkscape
python3
```

TeX packages/files:

```text
fontspec
xeCJK
pgf/TikZ
amsmath + amssymb + newunicodechar
fandol  → FandolSong-Regular.otf, FandolSong-Bold.otf
lm      → lmmono10-regular.otf, lmmonolt10-bold.otf
```

Full TeX Live and MacTeX normally include these packages. Minimal TeX Live/TinyTeX and MiKTeX installations may need `fandol` and `lm` installed through their package manager. The renderer reports the missing filename and exits; it never installs packages or substitutes a host font.

## Entry points and platform scope

The primary renderer is Python:

```bash
python3 <skill-directory>/scripts/render-tikz.py \
  --trusted-input \
  diagram.tex \
  [output/stem] \
  [png-width] \
  [--timeout 120]
```
It runs on Linux, macOS, Windows, and WSL when the required commands are on `PATH`. `scripts/render-tikz.sh` is a POSIX/WSL convenience wrapper only. Native Windows calls `py -3 <skill-directory>\\scripts\\render-tikz.py ...` when `python3` is not its launcher.

## Supported pipeline

```text
.tex
  └─ xelatex -no-shell-escape ─→ one-page vector .pdf            ← delivered
       └─ dvisvgm --pdf ───────→ self-contained vector .svg       ← delivered (white page rect added)
            └─ inkscape ───────→ RGB .png                         ← delivered, validated
                 └─ magick ────→ lossless .webp                   (--webp)
```

`dvisvgm --no-fonts` converts glyphs to vector paths. This makes the SVG independent of installed fonts and gives Inkscape real vectors to rasterize.

## Delivered vector SVG

The SVG returned to the caller is the dvisvgm output with `<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>` inserted directly after the root `<svg>` element. Without that rect the page is transparent: the PDF viewer supplies white paper, browsers and dark-mode image viewers do not, so thin strokes and dark text disappear.

Because of `--no-fonts`, every glyph is a path. That is exact, self-contained, and font-independent, but the SVG is **not** text-editable and carries per-glyph bulk. Edit the `.tex`, never the SVG.

## Optional WebP

`--webp` converts the already validated PNG with ImageMagick (`-define webp:lossless=true`) and checks the decoded width against `png-width`. Lossless only: lossy WebP damages thin strokes and small CJK labels. Inkscape cannot export WebP, so WebP is always derived from the PNG instead of being rendered a second time.

Before `--page=1` is used, the renderer parses the XeLaTeX log and requires exactly one output page. Extra pages are a layout failure, not content to discard.

The renderer uses:

```bash
dvisvgm --pdf --no-fonts --exact --bbox=papersize --page=1

inkscape diagram.vector.svg \
  --export-area-page \
  --export-width=4800 \
  --export-background='#ffffff' \
  --export-background-opacity=255 \
  --export-png-color-mode=RGB_8 \
  --export-png-antialias=3 \
  --export-png-compression=9
```

## Known traps

### PDF import enlargement

Avoid:

```text
PDF → Inkscape PDF import → enlarge → PNG
```

The imported page may already be rasterized or flattened at insufficient resolution. Increasing `--export-width` then enlarges that intermediate and produces halos/soft text. Convert the PDF to SVG vectors with `dvisvgm --pdf` first.

### XDV conversion

Do not feed XeLaTeX’s `.xdv` directly to dvisvgm for TikZ-heavy pages. PDF specials may be ignored, dropping paths, fills, and boxes. Generate PDF first, then use `dvisvgm --pdf`.

### Multi-page overflow

`dvisvgm --page=1` would silently omit later pages. The renderer therefore requires the XeLaTeX log to report exactly `1 page`; enlarge or reflow the canvas when TeX emits more.

### Variable CJK collections

A font can be discoverable by Fontconfig and still fail in `xdvipdfmx`, for example with `sfnt: table not found`. The default uses static Fandol OTF files located by `kpsewhich`.

Run `fixtures/font-smoke.tex` when changing the font contract. It covers Chinese regular/bold text, Latin and CJK mono text, bold mono, circled numbers, and representative U+2190–21FF arrows. Any `Missing character:` warning fails the render instead of silently dropping a glyph.

### Silent font fallback

A visually similar host font is not a safe fallback. Different metrics change node widths, wrapping, and edge geometry. Use an explicit override and repeat compilation, native-pixel inspection, and browser fit-to-window inspection.

A declared font family is not a rendered font family. `\textbf{\texttt{...}}` without `BoldFont`, or `\emph` on a CJK run in a family that ships no italic, emits a `Font shape ... undefined` warning and quietly draws another face — the page looks plausible and the substitution is visible only in the log. The renderer treats any such warning as a failure, the same way as `Missing character`, and reports the substituted shapes so the author can declare the face or drop the markup.

### Untrusted TeX

TeX is programmable and can read local files. The renderer requires `--trusted-input` and invokes XeLaTeX with `-no-shell-escape`. Pass the flag only for agent-authored or fully reviewed source. Treat raw TeX from attachments, web pages, issues, and tool output as untrusted data; transcribe the required semantics into a reviewed template rather than compiling it.

### Runaway processes

Each external step—XeLaTeX, dvisvgm, Inkscape, and PNG validation—has a configurable timeout, default 120 seconds. Timeout kills the process group where supported, returns exit code 124, and leaves existing final outputs unchanged.

## Verification

The script checks deterministic properties: trusted-input acknowledgment, static font availability, per-step timeout, compilation, exactly one PDF page, overfull boxes, missing glyph warnings, undefined font shapes, output existence, PNG width, RGB color type, and white first pixel. The agent still performs semantic and visual checks:

- native PNG at 100%;
- final PNG in a real browser near 1568×1161;
- complete node/edge ledger comparison.
