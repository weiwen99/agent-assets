#!/usr/bin/env python3
"""Structural checks for the argument-review wiring. Standard library only.

Covers the mode pointers, reachability of the shared method file, the
zero-hanzi guard in `de-ai-flavor`'s measurement script, and the frozen
fixtures' structure and hashes. Nothing here judges a fixture case: semantics
are graded by running a model on `inputs.json` and comparing with
`expected.json`, which this file deliberately does not do.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SKILLS = REPO / "skills"
DE_AI = SKILLS / "de-ai-flavor"
DESIGN = SKILLS / "design-scope-discipline"
REF = DE_AI / "references" / "argument-review.md"
FIXTURES = DE_AI / "fixtures" / "argument-review"

# Recorded in fixtures/argument-review/README.md under 冻结记录. A mismatch means
# an input or expectation moved; re-record the hash and rerun all 14 cases.
# v2: sources gained the premises the four keep cases previously assumed
# (ar-01/06/10/12); dispositions and the 6/2/6 split are unchanged.
# v3: ar-04's must_keep dropped the unsourced deployment decision, and ar-13
# gained a synthetic user_question scoping the round to this week's same-floor
# retest; dispositions and the 6/2/6 split are unchanged.
FROZEN = {
    "inputs.json": "40ae8a950ca8b07c5a824adde574dcdd3205b43926592da2908a2a92dd4d6161",
    "expected.json": "fbe1419273e250757267b8f0c84a262eef885629b78224b1150f3c09fae9ddce",
}

METHOD_HEADING = "## The five questions"
PYTHON_FENCE = re.compile(r"```python\n(.*?)```", re.S)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measurement_script() -> str:
    match = PYTHON_FENCE.search(read(DE_AI / "SKILL.md"))
    assert match is not None, "SKILL.md has no ```python measurement script"
    return match.group(1)


class ModePointersTest(unittest.TestCase):
    def test_reference_file_exists_and_carries_the_method(self) -> None:
        self.assertTrue(REF.is_file(), REF)
        body = read(REF)
        self.assertGreater(len(body), 1000)
        self.assertIn(METHOD_HEADING, body)

    def test_skill_md_links_the_reference(self) -> None:
        body = read(DE_AI / "SKILL.md")
        target = "references/argument-review.md"
        self.assertIn(f"]({target})", body)
        self.assertTrue((DE_AI / target).is_file())

    def test_skill_md_declares_both_modes(self) -> None:
        body = read(DE_AI / "SKILL.md")
        self.assertIn("Rewrite mode", body)
        self.assertIn("Review mode", body)
        self.assertIn("not applicable", body)

    def test_method_has_one_home(self) -> None:
        self.assertIn(METHOD_HEADING, read(REF))
        for skill in (DE_AI / "SKILL.md", DESIGN / "SKILL.md"):
            with self.subTest(skill=skill.parent.name):
                self.assertNotIn(METHOD_HEADING, read(skill))

    def test_design_scope_discipline_points_at_the_review_mode(self) -> None:
        body = read(DESIGN / "SKILL.md")
        link = "../de-ai-flavor/SKILL.md"
        self.assertIn(f"]({link})", body)
        self.assertTrue((DESIGN / link).is_file())
        item = next(line for line in body.splitlines() if link in line)
        self.assertIn("论证审读", item)
        self.assertIn("纯代码", item)
        self.assertIn("README", item)
        self.assertIn("references/argument-review.md", item)


class ZeroHanziScriptTest(unittest.TestCase):
    def run_script(self, text: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "measure.py"
            script.write_text(measurement_script(), encoding="utf-8")
            target = Path(tmp) / "doc.md"
            target.write_text(text, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(script), str(target)],
                capture_output=True,
                text=True,
                check=False,
            )

    def test_zero_hanzi_does_not_divide_by_zero(self) -> None:
        result = self.run_script(
            "## Heading\n\nPlain English prose with **bold** and an — aside.\n\n"
            "| k | v |\n|---|---|\n| a | 1 |\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("零汉字", result.stdout)
        self.assertIn("语言口径", result.stdout)
        self.assertNotIn("/千字", result.stdout)

    def test_hanzi_document_still_reports_density(self) -> None:
        result = self.run_script(
            "## 标题\n\n这是中文正文，包含**加粗**和——破折号。\n\n"
            "| 列 | 值 |\n|---|---|\n| 名称 | 数值 |\n"
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("/千字", result.stdout)
        self.assertNotIn("零汉字", result.stdout)


class FixturesTest(unittest.TestCase):
    def load(self) -> tuple[dict, dict]:
        return (
            json.loads(read(FIXTURES / "inputs.json")),
            json.loads(read(FIXTURES / "expected.json")),
        )

    def test_structure_is_aligned(self) -> None:
        inputs, expected = self.load()
        ids = [case["id"] for case in inputs["cases"]]
        eids = [case["id"] for case in expected["cases"]]
        self.assertEqual(len(ids), 14)
        self.assertEqual(len(set(ids)), 14)
        self.assertEqual(ids, eids)
        for case in inputs["cases"]:
            with self.subTest(case=case["id"]):
                self.assertTrue(case["role"] and case["request"] and case["sources"])
                self.assertTrue(
                    "draft" in case or {"before", "after", "review"} <= set(case)
                )
        counts = {"revise": 0, "reject_review": 0, "keep": 0}
        for case in expected["cases"]:
            with self.subTest(case=case["id"]):
                self.assertIn(case["disposition"], counts)
                counts[case["disposition"]] += 1
                self.assertTrue(case["reason"])
                self.assertIn("must_keep", case)
                self.assertIn("must_remove", case)
        self.assertEqual(counts, {"revise": 6, "reject_review": 2, "keep": 6})

    def test_frozen_hashes_match_reader_record(self) -> None:
        record = read(FIXTURES / "README.md")
        for name, digest in FROZEN.items():
            with self.subTest(fixture=name):
                self.assertEqual(sha256(FIXTURES / name), digest)
                self.assertIn(digest, record)

    def test_fixtures_carry_no_external_links(self) -> None:
        for name in ("inputs.json", "expected.json"):
            with self.subTest(fixture=name):
                body = read(FIXTURES / name)
                self.assertNotIn("http://", body)
                self.assertNotIn("https://", body)


class WiringTest(unittest.TestCase):
    def test_ci_runs_the_structural_check(self) -> None:
        workflow = read(REPO / ".github" / "workflows" / "validate.yml")
        self.assertIn("scripts/test_argument_review.py", workflow)


if __name__ == "__main__":
    unittest.main(verbosity=2)
