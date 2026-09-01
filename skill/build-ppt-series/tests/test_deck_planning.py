from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from detect_structural_reuse import compare
from sync_deck_spec import plan_issues, sync


COMPLETE_PLAN = """# Deck Plan

## Context

- deck_id: deck-02
- title: Independent deck
- audience: Engineers
- presentation_context: Design review
- source_scope: chapter-02.md

## Planning Basis

- estimated_page_range: 20-26
- selected_page_count: 23
- page_count_reason: Source complexity requires three explanatory sections.
- previous_deck_page_count_used: false

## Page Plan

| Page | Title | Purpose | Key content |
|---:|---|---|---|
| 1 | Opening | Orient | Current chapter question |
"""


class DeckPlanningTests(unittest.TestCase):
    def write_plan(self, path: Path, rows: list[tuple[str, str]]) -> None:
        table = "\n".join(
            f"| {index} | Slide {index} | {purpose} | Content {index} | medium | {layout} |"
            for index, (purpose, layout) in enumerate(rows, start=1)
        )
        path.write_text(
            "# Deck Plan\n\n"
            "| Page | Title | Purpose | Key content | Density | Layout family |\n"
            "|---:|---|---|---|---|---|\n"
            f"{table}\n",
            encoding="utf-8",
        )

    def test_plan_rejects_previous_deck_page_count(self) -> None:
        invalid = COMPLETE_PLAN.replace(
            "previous_deck_page_count_used: false",
            "previous_deck_page_count_used: true",
        )
        self.assertIn(
            "previous_deck_page_count_used must be false",
            plan_issues(invalid),
        )

    def test_snapshot_references_but_does_not_embed_deck_plan(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ppt-series-plan-test-") as temp:
            root = Path(temp)
            series = root / "series"
            deck = root / "decks" / "deck-02"
            analysis = deck / "analysis"
            series.mkdir(parents=True)
            analysis.mkdir(parents=True)
            (series / "spec_lock.md").write_text(
                "---\nversion: 3\n---\n# Series Lock\n- accent: blue\n",
                encoding="utf-8",
            )
            (analysis / "deck_plan.md").write_text(COMPLETE_PLAN, encoding="utf-8")
            (analysis / "deck_overrides.md").write_text(
                "# Deck Overrides\n- approval_mode: guided\n",
                encoding="utf-8",
            )

            target = sync(root, "deck-02")
            snapshot = target.read_text(encoding="utf-8")

            self.assertIn("schema: ppt-series-design-snapshot.v3", snapshot)
            self.assertIn('deck_plan: "analysis/deck_plan.md"', snapshot)
            self.assertIn("# Series Lock", snapshot)
            self.assertNotIn("Current chapter question", snapshot)
            self.assertNotIn("selected_page_count: 23", snapshot)

    def test_same_page_count_and_sequence_is_suspected_copy(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ppt-series-reuse-test-") as temp:
            root = Path(temp)
            previous = root / "previous.md"
            current = root / "current.md"
            rows = [("orient", "cover"), ("explain", "concept"), ("apply", "case")]
            self.write_plan(previous, rows)
            self.write_plan(current, rows)

            report = compare(previous, current)

            self.assertEqual(report["status"], "suspected_template_copy")
            self.assertFalse(report["ok"])

    def test_same_page_count_is_allowed_when_structure_differs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ppt-series-reuse-test-") as temp:
            root = Path(temp)
            previous = root / "previous.md"
            current = root / "current.md"
            self.write_plan(
                previous,
                [("orient", "cover"), ("explain", "concept"), ("apply", "case")],
            )
            self.write_plan(
                current,
                [("question", "evidence"), ("compare", "comparison"), ("decide", "summary")],
            )

            report = compare(previous, current)

            self.assertEqual(report["status"], "distinct_structure")
            self.assertTrue(report["ok"])

    def test_suspected_copy_can_only_pass_with_recorded_justification(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ppt-series-reuse-test-") as temp:
            root = Path(temp)
            previous = root / "previous.md"
            current = root / "current.md"
            rows = [("orient", "cover"), ("explain", "concept"), ("apply", "case")]
            self.write_plan(previous, rows)
            self.write_plan(current, rows)

            report = compare(
                previous,
                current,
                justification="The regulated agenda requires the same three functions.",
            )

            self.assertTrue(report["approved_exception"])
            self.assertTrue(report["ok"])


if __name__ == "__main__":
    unittest.main()
