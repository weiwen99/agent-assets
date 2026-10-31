# Visual system

## Character

A restrained red/rose technical poster: serif text, rounded red boxes, pale rose emphasis, thin directional lines, white label backplates, and generous negative space. Hierarchy comes from fill, border weight, and connector color rather than icons or decoration.

## Palette

```tex
\definecolor{accentcolor}{HTML}{B32F17}
\definecolor{accentlight}{HTML}{D9836F}
\definecolor{ink}{HTML}{1A1A1A}
\definecolor{muted}{HTML}{5A5A5A}
\definecolor{calloutbg}{HTML}{FBF1EE}
\definecolor{loopbg}{HTML}{F7E9E4}
```

- `accentcolor`: core borders, primary arrows, important labels.
- `accentlight`: return/recovery arrows, auxiliary borders, optional edges.
- `ink`: primary text and edge labels.
- `muted`: subtitles and non-critical prose only.
- `calloutbg`: authoritative/core nodes.
- `loopbg`: subsystem or control-loop boundary.

## Portable fonts

```tex
\providecommand{\DiagramCJKRegular}{FandolSong-Regular.otf}
\providecommand{\DiagramCJKBold}{FandolSong-Bold.otf}
\providecommand{\DiagramMonoFont}{lmmono10-regular.otf}

\setCJKmainfont{\DiagramCJKRegular}[BoldFont=\DiagramCJKBold]
\setCJKmonofont{\DiagramCJKRegular}
\setmonofont{\DiagramMonoFont}
```

Map commonly used Unicode arrows to TeX math glyphs instead of assigning U+2190–21FF to the CJK font; Fandol intentionally lacks several arrows:

```tex
\usepackage{amsmath,amssymb}
\usepackage{newunicodechar}
\newunicodechar{←}{\ensuremath{\leftarrow}}
\newunicodechar{↑}{\ensuremath{\uparrow}}
\newunicodechar{→}{\ensuremath{\rightarrow}}
\newunicodechar{↓}{\ensuremath{\downarrow}}
\newunicodechar{↔}{\ensuremath{\leftrightarrow}}
\newunicodechar{⇄}{\ensuremath{\rightleftarrows}}
\newunicodechar{⇒}{\ensuremath{\Rightarrow}}
```

These are TeX package files, not host font-family names. An explicit project override may redefine the three macros before these commands. Do not search for a visually similar operating-system fallback.

## Type floor

Use an 11pt document base for wide diagrams.

```tex
\makeatletter
\renewcommand\footnotesize{\@setfontsize\footnotesize{9pt}{11pt}}
\renewcommand\scriptsize{\@setfontsize\scriptsize{8pt}{9.6pt}}
\makeatother
```

- title: 20pt bold;
- node title: document normal size, bold;
- node detail: at least 9pt;
- lowest annotation: at least 8pt;
- edge labels: `\small\bfseries` with opaque white fill;
- CJK edge labels use `ink` or `accentcolor`, not low-contrast `muted`.

Preserve content by allocating space, not by dropping below these floors.

## Shared TikZ styles

```tex
x=1cm, y=1cm, font=\normalsize, text=ink,
>={Stealth[length=2.8mm]},
svc/.style    ={draw=accentcolor, line width=1.1pt, rounded corners=3pt,
                fill=white, align=center, inner sep=6pt},
core/.style   ={draw=accentcolor, line width=1.3pt, rounded corners=4pt,
                fill=calloutbg, align=center, inner sep=7pt},
aux/.style    ={draw=accentlight, line width=1pt, rounded corners=3pt,
                fill=white, align=center, inner sep=5pt, text=ink},
opt/.style    ={draw=accentlight, line width=1pt, rounded corners=3pt,
                dashed, fill=white, align=center, inner sep=5pt, text=ink},
fl/.style     ={->, draw=accentcolor, line width=1.15pt},
biarr/.style  ={<->, draw=accentcolor, line width=1.15pt},
ret/.style    ={->, draw=accentlight, line width=1.2pt},
retbi/.style  ={<->, draw=accentlight, line width=1.2pt},
dashfl/.style ={->, draw=accentlight, line width=1.05pt, dashed},
dashbi/.style ={<->, draw=accentlight, line width=1.05pt, dashed},
lbl/.style    ={font=\small\bfseries, text=ink, fill=white, inner sep=1.8pt},
retlbl/.style ={font=\small\bfseries, text=accentcolor,
                fill=white, inner sep=1.8pt}
```

## Composition

- Primary flow: short, direct, dark-red arrows.
- Feedback, event return, recovery: broad pale-red curves.
- Current core: solid border.
- Shipped deployment-opt-in node: dashed pale-red border with status text.
- Proposed component: omit from a current-state diagram or place in a separately labeled proposal boundary.
- Core subsystem: `loopbg` fit node on the background layer.
- Labels: white backplate, placed away from arrowheads and node borders.
- No connector may cross node text. Reorder nodes before adding bends.
