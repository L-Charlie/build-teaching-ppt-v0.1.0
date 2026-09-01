from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from select_aesthetic_reference import DEFAULT_CATALOG, load_catalog, route_or_select, select


def catalog(approved: bool = True) -> dict[str, object]:
    return {
        "schema": "ppt-series-aesthetic-catalog.v1",
        "sets": [
            {
                "id": "light",
                "scene": "product-technology",
                "name_zh": "明亮",
                "intent": "Light product story",
                "background": "light",
                "image_dependency": "high",
                "formality": "standard",
                "density_capacity": "medium",
                "approved": approved,
            },
            {
                "id": "dark",
                "scene": "product-technology",
                "name_zh": "深色",
                "intent": "Dark system story",
                "background": "dark",
                "image_dependency": "low",
                "formality": "formal",
                "density_capacity": "high",
                "approved": approved,
            },
        ],
    }


class AestheticSelectionTests(unittest.TestCase):
    def constraints(self) -> dict[str, object]:
        return {
            "print_required": False,
            "images_available": True,
            "formal_regulated": False,
            "high_density": False,
            "brand_conflicts": [],
        }

    def test_same_seed_is_reproducible(self) -> None:
        first = select(catalog(), "product-technology", self.constraints(), 42, "automatic")
        second = select(catalog(), "product-technology", self.constraints(), 42, "automatic")
        self.assertEqual(first["selected"], second["selected"])
        self.assertFalse(first["requires_confirmation"])

    def test_bundled_catalog_has_two_unapproved_directions_per_scene(self) -> None:
        sets = load_catalog(DEFAULT_CATALOG)["sets"]
        scenes = {item["scene"] for item in sets}
        self.assertEqual(len(scenes), 7)
        self.assertEqual(len(sets), 14)
        self.assertTrue(all(sum(item["scene"] == scene for item in sets) == 2 for scene in scenes))
        self.assertTrue(all(item["approved"] is False for item in sets))

    def test_hard_exclusion_happens_before_random_selection(self) -> None:
        constraints = self.constraints()
        constraints["print_required"] = True
        report = select(catalog(), "product-technology", constraints, 5, "guided")
        self.assertEqual(report["selected"]["id"], "light")
        self.assertTrue(report["requires_confirmation"])
        self.assertEqual(report["excluded"][0]["reasons"], ["print_required"])

    def test_unapproved_reference_sets_are_rejected_in_production(self) -> None:
        with self.assertRaisesRegex(ValueError, "No eligible approved"):
            select(catalog(approved=False), "product-technology", self.constraints(), 1, "guided")

    def test_existing_lock_skips_random_selection(self) -> None:
        report = route_or_select(
            catalog(),
            "product-technology",
            self.constraints(),
            7,
            "automatic",
            {"existing_lock": True},
        )
        self.assertEqual(report["status"], "not_applicable")
        self.assertEqual(report["reason"], "reuse_existing_series_lock")
        self.assertIsNone(report["selected"])


if __name__ == "__main__":
    unittest.main()
