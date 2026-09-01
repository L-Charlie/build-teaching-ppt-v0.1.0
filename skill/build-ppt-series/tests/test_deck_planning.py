from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

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


if __name__ == "__main__":
    unittest.main()
