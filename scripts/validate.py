#!/usr/bin/env python3
"""Validate every skills/<name>/SKILL.md in this repository."""

from __future__ import annotations

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


def main() -> int:
    if not SKILLS.is_dir():
        print("FAIL skills/ directory is missing")
        return 1

    errors: list[str] = []
    dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if not dirs:
        errors.append("skills/ has no skill directory")

    for skill_dir in dirs:
        name = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{name}: missing SKILL.md")
            continue

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
            for pattern, label in FORBIDDEN:
                match = pattern.search(content)
                if match:
                    relative = path.relative_to(ROOT)
                    errors.append(f"{relative}: {label} ({match.group(0)})")

    for error in errors:
        print(f"FAIL {error}")
    print(f"{len(dirs)} skills checked, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
