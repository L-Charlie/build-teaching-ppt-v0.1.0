#!/usr/bin/env python3
"""Select an approved aesthetic reference set after hard exclusions."""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CATALOG = SCRIPT_DIR.parent / "assets" / "aesthetic-references" / "catalog.json"


def load_catalog(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "ppt-series-aesthetic-catalog.v1":
        raise ValueError("Unsupported aesthetic catalog schema")
    if not isinstance(data.get("sets"), list):
        raise ValueError("Catalog sets must be a list")
    return data


def hard_exclusion_reasons(item: dict[str, object], constraints: dict[str, object]) -> list[str]:
    reasons: list[str] = []
    if constraints.get("print_required") and item.get("background") == "dark":
        reasons.append("print_required")
    if constraints.get("images_available") is False and item.get("image_dependency") == "high":
        reasons.append("images_unavailable")
    if constraints.get("formal_regulated") and item.get("formality") == "expressive":
        reasons.append("formal_regulated")
    if constraints.get("high_density") and item.get("density_capacity") != "high":
        reasons.append("insufficient_density_capacity")
    if item.get("id") in set(constraints.get("brand_conflicts", [])):
        reasons.append("brand_conflict")
    return reasons


def select(
    catalog: dict[str, object],
    scene: str,
    constraints: dict[str, object],
    seed: int,
    approval_mode: str,
    require_approved: bool = True,
) -> dict[str, object]:
    candidates = [item for item in catalog["sets"] if item.get("scene") == scene]
    if not candidates:
        raise ValueError(f"Unknown or empty scene: {scene}")
    excluded: list[dict[str, object]] = []
    eligible: list[dict[str, object]] = []
    for item in candidates:
        reasons = hard_exclusion_reasons(item, constraints)
        if require_approved and not item.get("approved"):
            reasons.append("reference_set_not_human_approved")
        if reasons:
            excluded.append({"id": item.get("id"), "reasons": reasons})
        else:
            eligible.append(item)
    if not eligible:
        raise ValueError("No eligible approved aesthetic reference set after hard exclusions")
    selected = random.Random(seed).choice(sorted(eligible, key=lambda item: str(item["id"])))
    return {
        "schema": "ppt-series-aesthetic-selection.v1",
        "scene": scene,
        "seed": seed,
        "approval_mode": approval_mode,
        "requires_confirmation": approval_mode == "guided",
        "selection_method": "hard-exclusions-then-uniform-random",
        "selected": {
            "id": selected["id"],
            "name_zh": selected["name_zh"],
            "intent": selected["intent"],
        },
        "eligible_ids": [item["id"] for item in eligible],
        "excluded": excluded,
    }


def route_or_select(
    catalog: dict[str, object],
    scene: str,
    constraints: dict[str, object],
    seed: int,
    approval_mode: str,
    route_constraints: dict[str, bool],
    require_approved: bool = True,
) -> dict[str, object]:
    precedence = (
        ("existing_lock", "reuse_existing_series_lock"),
        ("has_template", "user_template_controls_design"),
        ("has_brand_guide", "brand_guide_controls_design"),
        ("explicit_style", "explicit_user_style_controls_design"),
    )
    for field, reason in precedence:
        if route_constraints.get(field):
            return {
                "schema": "ppt-series-aesthetic-selection.v1",
                "status": "not_applicable",
                "reason": reason,
                "selected": None,
            }
    report = select(
        catalog,
        scene,
        constraints,
        seed,
        approval_mode,
        require_approved=require_approved,
    )
    report["status"] = "selected"
    return report


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", required=True)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--approval-mode", choices=("guided", "automatic"), default="guided")
    parser.add_argument("--print-required", action="store_true")
    parser.add_argument("--images-unavailable", action="store_true")
    parser.add_argument("--formal-regulated", action="store_true")
    parser.add_argument("--high-density", action="store_true")
    parser.add_argument("--brand-conflict", action="append", default=[])
    parser.add_argument("--has-template", action="store_true")
    parser.add_argument("--has-brand-guide", action="store_true")
    parser.add_argument("--explicit-style", action="store_true")
    parser.add_argument("--existing-lock", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--allow-unapproved",
        action="store_true",
        help="Development only: include reference sets that have not passed human review",
    )
    args = parser.parse_args()
    constraints = {
        "print_required": args.print_required,
        "images_available": not args.images_unavailable,
        "formal_regulated": args.formal_regulated,
        "high_density": args.high_density,
        "brand_conflicts": args.brand_conflict,
    }
    try:
        report = route_or_select(
            load_catalog(args.catalog.resolve()),
            args.scene,
            constraints,
            args.seed,
            args.approval_mode,
            {
                "has_template": args.has_template,
                "has_brand_guide": args.has_brand_guide,
                "explicit_style": args.explicit_style,
                "existing_lock": args.existing_lock,
            },
            require_approved=not args.allow_unapproved,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
