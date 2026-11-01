#!/usr/bin/env python3
"""Validate a skills tree: frontmatter, privacy, and local Markdown links.

Defaults to this repository's `skills/`. Pass a directory to check another
skills root, e.g. a flattened installation. Never fetches the network: a link
is local only if it resolves inside the given root.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

FORBIDDEN = [
    (re.compile(r"/home/[^/\s]+"), "absolute home path"),
    (re.compile(r"/Users/[^/\s]+"), "absolute macOS home path"),
    (re.compile(r"/nix/store"), "Nix store path"),
    (re.compile(r"chinamobiad"), "internal host"),
    (re.compile(r"code\.weiwen\.org"), "internal host"),
    (re.compile(r"gitea@"), "internal remote"),
]

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)([^`\n]*?)\1")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
INLINE_LINK = re.compile(
    r"!?\[[^\]\n]*\]\(\s*(<[^>\n]*>|[^()\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)"
)
REFERENCE_DEF = re.compile(r"^ {0,3}\[[^\]\n]+\]:\s*(<[^>\n]*>|\S+)", re.M)
SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")


def split_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end < 0:
        return None, text
    fields: dict[str, str] = {}
    key = None
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        match = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if match:
            key = match.group(1)
            fields[key] = match.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fields[key] = f"{fields[key]} {line.strip()}".strip()
    return fields, text[end + len("\n---") :]


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def strip_code(text: str) -> str:
    """Blank out fenced blocks, HTML comments, and inline code.

    Examples inside them are prose about links, not links to resolve.
    """
    kept: list[str] = []
    fence: str | None = None
    for line in text.splitlines(keepends=True):
        opening = FENCE.match(line)
        if fence is None:
            if opening:
                fence = opening.group(1)
                kept.append("\n")
                continue
            kept.append(line)
            continue
        if opening and opening.group(1)[0] == fence[0] and len(opening.group(1)) >= len(fence):
            fence = None
        kept.append("\n")
    masked = "".join(kept)
    masked = HTML_COMMENT.sub("", masked)
    return INLINE_CODE.sub("", masked)


def link_targets(text: str) -> list[str]:
    """Collect Markdown link targets, inline and reference-style."""
    targets = [match.group(1) for match in INLINE_LINK.finditer(text)]
    targets += [match.group(1) for match in REFERENCE_DEF.finditer(text)]
    return targets


def local_path(base: Path, raw: str) -> tuple[Path | None, str]:
    """Resolve one link target. Returns (path, "") for a local link."""
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if not target:
        return None, "empty"
    if SCHEME.match(target) or target.startswith("//"):
        return None, "external"
    target = target.split("#", 1)[0]
    if not target:
        return None, "anchor"
    return Path(os.path.normpath(os.path.join(str(base), target))), ""


def label(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def validate(skills_root: Path) -> tuple[list[str], int]:
    root = Path(os.path.abspath(str(skills_root)))
    if not root.is_dir():
        return [f"{skills_root}: skills root is missing"], 0

    errors: list[str] = []
    dirs = sorted(path for path in root.iterdir() if path.is_dir())
    if not dirs:
        errors.append(f"{skills_root}: has no skill directory")

    for skill_dir in dirs:
        name = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{name}: missing SKILL.md")
        else:
            fields, body = split_frontmatter(skill_md.read_text(encoding="utf-8"))
            if fields is None:
                errors.append(f"{name}: SKILL.md has no frontmatter")
            else:
                declared = unquote(fields.get("name", ""))
                description = unquote(fields.get("description", ""))
                if not declared:
                    errors.append(f"{name}: empty frontmatter name")
                elif declared != name:
                    errors.append(
                        f"{name}: frontmatter name {declared!r} does not match directory"
                    )
                if not description:
                    errors.append(f"{name}: empty frontmatter description")
            if not body.strip():
                errors.append(f"{name}: empty body")

        for path in sorted(skill_dir.rglob("*")):
            if not path.is_file() or path.name == "LICENSE":
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern, problem in FORBIDDEN:
                match = pattern.search(content)
                if match:
                    errors.append(f"{label(path, root)}: {problem} ({match.group(0)})")

        for md in sorted(skill_dir.rglob("*.md")):
            try:
                text = md.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            seen: set[str] = set()
            for raw in link_targets(strip_code(text)):
                if raw in seen:
                    continue
                seen.add(raw)
                target, kind = local_path(md.parent, raw)
                if target is None or kind:
                    continue
                where = label(md, root)
                if not (target == root or root in target.parents):
                    errors.append(
                        f"{where}: link {raw!r} escapes the skills root"
                    )
                elif not target.exists():
                    errors.append(
                        f"{where}: link {raw!r} has no target "
                        f"({label(target, root)} is missing)"
                    )

    return errors, len(dirs)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate skill frontmatter, privacy, and local Markdown links."
    )
    parser.add_argument(
        "skills_root",
        nargs="?",
        help="skills root to check; defaults to this repository's skills/",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)

    errors, checked = validate(Path(args.skills_root) if args.skills_root else SKILLS)
    for error in errors:
        print(f"FAIL {error}")
    print(f"{checked} skills checked, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
