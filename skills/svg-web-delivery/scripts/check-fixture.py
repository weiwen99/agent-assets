#!/usr/bin/env python3
"""Structural regression for this skill's fixture, not an SVG sanitizer/browser test."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

SVG = "{http://www.w3.org/2000/svg}"
INKSCAPE = "{http://www.inkscape.org/namespaces/inkscape}"
FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def check(svg: str, html: str) -> list[str]:
    errors: list[str] = []
    if "<!DOCTYPE" in svg or "<!ENTITY" in svg:
        return ["fixture must not declare entities or a doctype"]
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as error:
        return [f"invalid XML: {error}"]
    nodes = list(root.iter())
    by_id = {e.get("id"): e for e in nodes if e.get("id")}

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(root.tag == SVG + "svg" and root.get("viewBox") == "0 0 640 360", "fixture canvas changed")
    require(len(by_id) == sum(e.get("id") is not None for e in nodes), "duplicate IDs")
    allowed = {"svg", "title", "desc", "style", "defs", "marker", "path", "linearGradient", "stop", "mask", "rect", "circle", "g", "text"}
    for element in nodes:
        require(element.tag.startswith(SVG) and element.tag[len(SVG):] in allowed, "unexpected fixture element")
        for name, value in element.attrib.items():
            require(not name.lower().startswith("on"), "event handler in fixture")
            if name.endswith("href"):
                require(value.startswith("#") and value[1:] in by_id, "non-internal or missing href")
            for target in re.findall(r"url\(([^)]+)\)", value):
                require(target.startswith("#") and target[1:] in by_id, "non-internal or missing url")
    style = "\n".join(e.text or "" for e in nodes if e.tag == SVG + "style")
    require("@import" not in style and "url(" not in style, "external CSS dependency")
    require("@media (prefers-color-scheme: dark)" in style, "missing dark palette")
    require(style.find("@media print") > style.find("@media (prefers-color-scheme: dark)"), "print must override dark")
    require("color-scheme: light dark" in style and "color-scheme: light;" in style, "missing standalone/print scheme")
    require(".arrow-fill { fill: var(--accent); }" in style, "marker has no theme role")
    require(".wash { fill: var(--surface); fill-opacity: var(--wash-alpha); }" in style, "wash has no theme role")
    for layer in ["Canvas", "Panels", "Connectors", "Nodes", "Labels"]:
        require(any(e.get(INKSCAPE + "label") == layer for e in nodes), f"missing editable layer {layer}")
    canvas = by_id.get("canvas")
    require(canvas is not None and len(canvas) == 0, "page rectangle must not be painted")
    mask = by_id.get("knockouts")
    require(mask is not None and mask.get("mask-type") == "luminance" and mask.get("maskUnits") == "userSpaceOnUse", "missing explicit luminance mask")
    early = by_id.get("early-paint")
    require(early is not None and early.get("mask") == "url(#knockouts)", "earlier drawing is not masked")
    label = by_id.get("later-label")
    require(label is not None and label.tag == SVG + "text" and label.text == "label", "later live text missing")
    require(early is not None and label is not None and label not in early.iter() and nodes.index(label) > nodes.index(early), "label must survive outside earlier mask")
    point = by_id.get("open-point")
    require(point is not None and point.get("r") == "9" and point.get("class") == "guide", "hollow point changed")
    require(all(name in by_id for name in ["label-hole", "point-hole", "fade-strip", "arrow"]), "missing regression object")
    expected = {
        "label-hole": {"x": "268", "y": "166", "width": "104", "height": "48"},
        "later-label": {"x": "320", "y": "198"},
        "point-hole": {"cx": "492", "cy": "252", "r": "9"},
        "open-point": {"cx": "492", "cy": "252", "r": "9"},
    }
    for name, attributes in expected.items():
        element = by_id.get(name)
        require(element is not None and all(element.get(k) == v for k, v in attributes.items()), f"knockout geometry drift: {name}")
    for theme in ["auto", "light", "dark"]:
        require(f'data-theme="{theme}"' in html, f"host case {theme} missing")
    require(html.count('src="theme-aware.svg"') == 3, "host must embed the same SVG three times")
    require("color-scheme: light dark" in html and "color-scheme: dark" in html, "host schemes missing")
    require(html.find("@media print") > html.find('.case[data-theme="dark"] img'), "host print override missing or misplaced")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="also check deliberate broken fixtures")
    args = parser.parse_args()
    svg = (FIXTURES / "theme-aware.svg").read_text(encoding="utf-8")
    html = (FIXTURES / "index.html").read_text(encoding="utf-8")
    errors = check(svg, html)
    for error in errors:
        print("FAIL", error)
    if errors:
        return 1
    if args.self_test:
        broken = [
            svg.replace('mask-type="luminance"', 'mask-type="alpha"'),
            svg.replace('id="later-label"', 'id="lost-label"'),
            svg.replace('.arrow-fill { fill: var(--accent); }', '.arrow-fill { fill: black; }'),
            svg.replace('<g id="early-paint" mask="url(#knockouts)">', '<g id="early-paint">'),
            svg.replace('id="point-hole" cx="492"', 'id="point-hole" cx="400"'),
        ]
        if any(not check(value, html) for value in broken):
            print("FAIL a broken fixture passed")
            return 1
        print(f"PASS {len(broken)} negative structural checks")
    print("PASS fixture structure; browser rendering, contrast and print remain separate checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
