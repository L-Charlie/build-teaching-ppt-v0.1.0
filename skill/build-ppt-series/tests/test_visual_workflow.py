from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from compile_image_prompt import compile_prompt, load_brief
from validate_visual_assets import validate as validate_assets
from visual_preflight import validate as validate_preflight


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class VisualWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ppt-series-visual-test-")
        self.root = Path(self.temp.name)
        self.analysis = self.root / "analysis"
        self.analysis.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def base_plan(self) -> dict[str, object]:
        return {
            "schema": "ppt-series-visual-plan.v1",
            "deck_id": "deck-01",
            "status": "draft",
            "approval_mode": "guided",
            "image_backend": "unknown",
            "budgets": {
                "max_generated_assets": 2,
                "max_candidates_per_task": 4,
                "max_generation_attempts_per_asset": 2,
            },
            "tasks": [],
        }

    def brief(self, asset_id: str = "VIS-001", risk: str = "low") -> dict[str, object]:
        return {
            "schema": "ppt-series-image-brief.v1",
            "asset_id": asset_id,
            "slide": 2,
            "purpose": "Explain a relationship",
            "subject": "Two components working together",
            "must_show": ["component A", "component B", "clear relationship"],
            "style": {
                "base_style": "clean editorial illustration",
                "scene_profile": "conceptual",
                "palette": ["#176B87", "#F2B134"],
                "continuity_ids": [],
            },
            "composition": {
                "placement": "right",
                "aspect_ratio": "4:3",
                "subject_position": "center",
                "reserved_whitespace": "left 35%",
                "background": "simple",
            },
            "risk": risk,
            "factual_basis": ["approved source fact"] if risk in {"medium", "high"} else [],
            "must_avoid": ["logos", "watermarks"],
            "disclosure": "provenance-only",
        }

    def test_no_generated_tasks_pass_without_backend(self) -> None:
        plan = self.base_plan()
        plan["tasks"] = [
            {
                "asset_id": "VIS-001",
                "slide": 1,
                "visual_need": "unnecessary",
                "route": "none",
                "risk": "low",
            }
        ]
        path = self.analysis / "plan.json"
        write_json(path, plan)
        report = validate_preflight(path, "unavailable")
        self.assertTrue(report["ok"])
        self.assertEqual(report["generated_task_count"], 0)

    def test_generated_task_requires_available_backend(self) -> None:
        write_json(self.analysis / "image_briefs" / "VIS-001.json", self.brief())
        plan = self.base_plan()
        plan["tasks"] = [
            {
                "asset_id": "VIS-001",
                "slide": 2,
                "visual_need": "helpful",
                "route": "generated",
                "risk": "low",
                "brief": "image_briefs/VIS-001.json",
            }
        ]
        path = self.analysis / "plan.json"
        write_json(path, plan)
        self.assertFalse(validate_preflight(path, "unavailable")["ok"])
        self.assertTrue(validate_preflight(path, "available")["ok"])

    def test_high_risk_generation_requires_approval_and_disclosure(self) -> None:
        write_json(self.analysis / "image_briefs" / "VIS-001.json", self.brief(risk="high"))
        plan = self.base_plan()
        plan["tasks"] = [
            {
                "asset_id": "VIS-001",
                "slide": 2,
                "visual_need": "required",
                "route": "generated",
                "risk": "high",
                "brief": "image_briefs/VIS-001.json",
            }
        ]
        path = self.analysis / "plan.json"
        write_json(path, plan)
        self.assertFalse(validate_preflight(path, "available")["ok"])
        plan["tasks"][0]["high_risk_schematic_approved"] = True
        plan["tasks"][0]["visible_disclosure"] = True
        write_json(path, plan)
        self.assertTrue(validate_preflight(path, "available")["ok"])

    def test_candidate_cap_and_user_semantic_edit_are_enforced(self) -> None:
        plan = self.base_plan()
        plan["budgets"]["max_candidates_per_task"] = 1
        plan["tasks"] = [
            {
                "asset_id": "VIS-USER",
                "slide": 3,
                "visual_need": "required",
                "route": "user",
                "risk": "low",
                "edit_type": "semantic",
                "candidates": ["candidate-a", "candidate-b"],
            }
        ]
        path = self.analysis / "plan.json"
        write_json(path, plan)
        report = validate_preflight(path, "unavailable")
        self.assertFalse(report["ok"])
        plan["tasks"][0]["semantic_edit_approved"] = True
        plan["tasks"][0]["candidates"] = ["candidate-a"]
        write_json(path, plan)
        self.assertTrue(validate_preflight(path, "unavailable")["ok"])

    def test_reused_asset_requires_reason(self) -> None:
        plan = self.base_plan()
        plan["tasks"] = [
            {
                "asset_id": "VIS-REUSE",
                "slide": 4,
                "visual_need": "helpful",
                "route": "source",
                "risk": "low",
                "reused_from": "deck-00/VIS-001",
            }
        ]
        path = self.analysis / "plan.json"
        write_json(path, plan)
        self.assertFalse(validate_preflight(path, "unavailable")["ok"])
        plan["tasks"][0]["reuse_reason"] = "recap and subject continuity"
        write_json(path, plan)
        self.assertTrue(validate_preflight(path, "unavailable")["ok"])

    def test_prompt_is_compiled_from_brief(self) -> None:
        path = self.analysis / "brief.json"
        write_json(path, self.brief())
        prompt = compile_prompt(load_brief(path))
        self.assertIn("Aspect ratio: 4:3", prompt)
        self.assertIn("Leave all educational or explanatory text", prompt)
        self.assertIn("logos", prompt)

    def test_placeholder_forces_review_state_with_complete_exception(self) -> None:
        plan = self.base_plan()
        plan["tasks"] = [
            {
                "asset_id": "VIS-009",
                "slide": 9,
                "visual_need": "required",
                "route": "generated",
                "risk": "low",
                "status": "placeholder",
            }
        ]
        plan_path = self.analysis / "plan.json"
        write_json(plan_path, plan)
        exception_path = self.analysis / "exceptions.json"
        write_json(
            exception_path,
            {
                "schema": "ppt-series-visual-exceptions.v1",
                "deck_id": "deck-01",
                "items": [
                    {
                        "asset_id": "VIS-009",
                        "slide": 9,
                        "brief": "image_briefs/VIS-009.json",
                        "prompt": "prompts/VIS-009.txt",
                        "negative_constraints": ["text", "logos"],
                        "attempts": 2,
                        "failures": ["composition mismatch", "backend error"],
                    }
                ],
            },
        )
        report = validate_assets(plan_path, exception_path, require_final=False)
        self.assertTrue(report["ok"])
        self.assertEqual(report["delivery_state"], "draft/review")
        self.assertFalse(validate_assets(plan_path, exception_path, require_final=True)["ok"])

    def test_complete_generated_asset_requires_valid_record_and_hash(self) -> None:
        asset = self.root / "images" / "generated" / "VIS-001.png"
        asset.parent.mkdir(parents=True)
        asset.write_bytes(b"test-image-bytes")
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()
        record = self.analysis / "generation_records" / "VIS-001.json"
        write_json(
            record,
            {
                "asset_id": "VIS-001",
                "backend": "host-imagegen",
                "prompt": "A provider-neutral test prompt",
                "attempts": [{"attempt": 1, "status": "accepted"}],
                "accepted_output": "../../images/generated/VIS-001.png",
            },
        )
        plan = self.base_plan()
        plan["tasks"] = [
            {
                "asset_id": "VIS-001",
                "slide": 2,
                "visual_need": "helpful",
                "route": "generated",
                "risk": "low",
                "status": "complete",
                "selected_asset": "../images/generated/VIS-001.png",
                "sha256": digest,
                "generation_record": "generation_records/VIS-001.json",
                "provenance": {"type": "generated", "backend": "host-imagegen"},
            }
        ]
        plan_path = self.analysis / "plan.json"
        write_json(plan_path, plan)
        report = validate_assets(plan_path, None, require_final=True)
        self.assertTrue(report["ok"], report["errors"])

    def test_complete_native_visual_uses_slide_object_evidence(self) -> None:
        plan = self.base_plan()
        plan["tasks"] = [
            {
                "asset_id": "VIS-NATIVE",
                "slide": 3,
                "visual_need": "required",
                "route": "native",
                "risk": "low",
                "status": "complete",
                "slide_objects": ["stage-1", "stage-2", "stage-connector-1"],
            }
        ]
        plan_path = self.analysis / "plan.json"
        write_json(plan_path, plan)
        self.assertTrue(validate_assets(plan_path, None, require_final=True)["ok"])

        plan["tasks"][0]["slide_objects"] = []
        write_json(plan_path, plan)
        report = validate_assets(plan_path, None, require_final=True)
        self.assertFalse(report["ok"])
        self.assertIn("complete native visual requires slide_objects", report["errors"][0])


if __name__ == "__main__":
    unittest.main()
