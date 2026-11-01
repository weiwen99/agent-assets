#!/usr/bin/env python3
"""Tests for scripts/validate.py. Standard library only, no network access.

Every case builds its own temporary skills tree; the repository tree is only
read to prove that the current adapters resolve their shared dependency once
that dependency is present.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import validate  # noqa: E402

REPO_SKILLS = HERE.parent / "skills"
CALLERS = ("tikz-diagramming", "inkscape-diagramming")
SHARED = "svg-web-delivery"


def write_skill(
    root: Path, name: str, body: str = "Body.\n", description: str = "demo skill"
) -> Path:
    skill_dir = root / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\n{body}\n",
        encoding="utf-8",
    )
    return skill_dir


def copy_callers(root: Path) -> None:
    for name in CALLERS:
        shutil.copytree(REPO_SKILLS / name, root / name)


class ValidateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "skills"
        self.root.mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def errors(self) -> list[str]:
        found, _ = validate.validate(self.root)
        return found

    def assert_clean(self) -> None:
        self.assertEqual(self.errors(), [], "expected a clean skills tree")

    def test_current_repo_skills_are_valid_when_shared_skill_is_present(self) -> None:
        shutil.rmtree(self.root)
        shutil.copytree(REPO_SKILLS, self.root)
        self.assertTrue((self.root / SHARED / "SKILL.md").is_file())
        self.assert_clean()

    def test_missing_shared_dependency_fails(self) -> None:
        copy_callers(self.root)
        found = self.errors()
        reported = [e for e in found if SHARED in e and "missing" in e]
        self.assertEqual(len(reported), len(CALLERS), found)

    def test_flattened_copy_with_shared_dependency_passes(self) -> None:
        copy_callers(self.root)
        shutil.copytree(REPO_SKILLS / SHARED, self.root / SHARED)
        self.assert_clean()
        out = StringIO()
        with redirect_stdout(out):
            code = validate.main([str(self.root)])
        self.assertEqual(code, 0, out.getvalue())

    def test_each_caller_needs_only_the_shared_skill(self) -> None:
        for name in CALLERS:
            with self.subTest(caller=name):
                target = self.root / name
                shutil.copytree(REPO_SKILLS / name, target)
                shared = self.root / SHARED
                if not shared.exists():
                    shutil.copytree(REPO_SKILLS / SHARED, shared)
                self.assert_clean()
                shutil.rmtree(target)

    def test_symlink_slots_with_shared_dependency_pass(self) -> None:
        for name in (*CALLERS, SHARED):
            (self.root / name).symlink_to(REPO_SKILLS / name, target_is_directory=True)
        self.assert_clean()
        (self.root / SHARED).unlink()
        self.assertEqual(len([e for e in self.errors() if SHARED in e]), len(CALLERS))

    def test_cli_without_arguments_checks_repo_skills(self) -> None:
        out = StringIO()
        with redirect_stdout(out):
            code = validate.main([])
        self.assertIn("skills checked", out.getvalue())
        self.assertEqual(code, 0, out.getvalue())

    def test_cli_reports_missing_dependency(self) -> None:
        copy_callers(self.root)
        with redirect_stdout(StringIO()):
            self.assertEqual(validate.main([str(self.root)]), 1)

    def test_link_escape_is_rejected(self) -> None:
        (self.root.parent / "outside.md").write_text("outside\n", encoding="utf-8")
        write_skill(
            self.root,
            "demo",
            body="See [up](../../outside.md) and [absolute](/etc/hosts).\n",
        )
        found = self.errors()
        self.assertEqual(len(found), 2, found)
        self.assertTrue(all("escapes the skills root" in e for e in found), found)

    def test_examples_and_external_links_are_ignored(self) -> None:
        body = "\n".join(
            [
                "Real link: [internal](notes.md).",
                "External: [site](https://example.com/x), [mail](mailto:a@example.com).",
                "Anchor only: [top](#section).",
                "",
                "```bash",
                "cat [example](missing-in-fence.md)",
                "```",
                "",
                "~~~markdown",
                "[another](missing-in-tilde.md)",
                "~~~",
                "",
                "Inline `[inline](missing-inline.md)` and `<img>`.",
                "",
                "<!-- [comment](missing-in-comment.md) -->",
                "",
            ]
        )
        skill_dir = write_skill(self.root, "demo", body=body)
        (skill_dir / "notes.md").write_text("# Notes\n", encoding="utf-8")
        self.assert_clean()

    def test_directory_links_are_allowed(self) -> None:
        skill_dir = write_skill(
            self.root,
            "demo",
            body="See [refs](references) and [file](references/note.md).\n",
        )
        (skill_dir / "references").mkdir()
        (skill_dir / "references" / "note.md").write_text("# Note\n", encoding="utf-8")
        self.assert_clean()

    def test_reference_style_links_are_checked(self) -> None:
        write_skill(self.root, "demo", body="See [ref].\n\n[ref]: ../shared/SKILL.md\n")
        found = self.errors()
        self.assertTrue(any("has no target" in e for e in found), found)

    def test_frontmatter_and_privacy_still_checked(self) -> None:
        skill_dir = self.root / "demo"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: other\ndescription:\n---\n\nSee [self](SKILL.md) under /home/example/diagram.tex.\n",
            encoding="utf-8",
        )
        found = self.errors()
        self.assertTrue(any("does not match directory" in e for e in found), found)
        self.assertTrue(any("empty frontmatter description" in e for e in found), found)
        self.assertTrue(any("absolute home path" in e for e in found), found)

    def test_validator_has_no_network_paths(self) -> None:
        source = (HERE / "validate.py").read_text(encoding="utf-8")
        for token in ("urllib.request", "http.client", "socket", "requests", "urlopen"):
            self.assertNotIn(token, source, f"{token} suggests network access")


if __name__ == "__main__":
    unittest.main(verbosity=2)
