#!/usr/bin/env python3
"""Validate a deck visual plan before slide layout or image generation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VISUAL_NEEDS = {"required", "helpful", "unnecessary", "prohibited"}
ROUTES = {"user", "source", "external", "screenshot", "native", "generated", "none"}
RISKS = {"low", "medium", "high"}
BACKENDS = {"available", "unavailable", "unknown"}
APPROVAL_MODES = {"guided", "automatic"}


def load_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def resolve_path(base: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value).expanduser()
    return path if path.is_absolute() else (base / path).resolve()


def positive_int(value: object, label: str, errors: list[str]) -> int | None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(f"{label} must be a non-negative integer")
        return None
    return value


def validate(plan_path: Path, backend_override: str | None = None) -> dict[str, object]:
    plan = load_object(plan_path)
    errors: list[str] = []
    warnings: list[str] = []
    base = plan_path.parent

    if plan.get("schema") != "ppt-series-visual-plan.v1":
        errors.append("schema must be ppt-series-visual-plan.v1")
    approval_mode = plan.get("approval_mode", "guided")
    if approval_mode not in APPROVAL_MODES:
        errors.append(f"approval_mode must be one of {sorted(APPROVAL_MODES)}")
    backend = backend_override or str(plan.get("image_backend", "unknown"))
    if backend not in BACKENDS:
        errors.append(f"image_backend must be one of {sorted(BACKENDS)}")

    budgets = plan.get("budgets")
    if not isinstance(budgets, dict):
        errors.append("budgets must be an object")
        budgets = {}
    max_generated = positive_int(budgets.get("max_generated_assets"), "max_generated_assets", errors)
    max_candidates = positive_int(budgets.get("max_candidates_per_task"), "max_candidates_per_task", errors)
    max_attempts = positive_int(
        budgets.get("max_generation_attempts_per_asset"),
        "max_generation_attempts_per_asset",
        errors,
    )
    if max_attempts is not None and not 1 <= max_attempts <= 2:
        errors.append("max_generation_attempts_per_asset must be 1 or 2")
    if max_candidates is not None and max_candidates == 0:
        warnings.append("max_candidates_per_task is 0; external search cannot retain candidates")

    tasks = plan.get("tasks")
    if not isinstance(tasks, list):
        errors.append("tasks must be an array")
        tasks = []
    seen: set[str] = set()
    generated_count = 0
    task_reports: list[dict[str, object]] = []

    for index, raw in enumerate(tasks, start=1):
        label = f"task[{index}]"
        task_errors: list[str] = []
        if not isinstance(raw, dict):
            errors.append(f"{label} must be an object")
            continue
        asset_id = raw.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id.strip():
            task_errors.append("asset_id is required")
            asset_id = label
        elif asset_id in seen:
            task_errors.append(f"duplicate asset_id: {asset_id}")
        else:
            seen.add(asset_id)
        slide = raw.get("slide")
        if not isinstance(slide, int) or isinstance(slide, bool) or slide < 1:
            task_errors.append("slide must be a positive integer")
        need = raw.get("visual_need")
        route = raw.get("route")
        risk = raw.get("risk", "low")
        if need not in VISUAL_NEEDS:
            task_errors.append(f"visual_need must be one of {sorted(VISUAL_NEEDS)}")
        if route not in ROUTES:
            task_errors.append(f"route must be one of {sorted(ROUTES)}")
        if risk not in RISKS:
            task_errors.append(f"risk must be one of {sorted(RISKS)}")
        if need in {"unnecessary", "prohibited"} and route != "none":
            task_errors.append(f"{need} visual_need must use route=none")
        if need == "required" and route == "none":
            task_errors.append("required visual_need cannot use route=none")
        candidates = raw.get("candidates", [])
        if not isinstance(candidates, list):
            task_errors.append("candidates must be an array when provided")
        elif max_candidates is not None and len(candidates) > max_candidates:
            task_errors.append(
                f"candidate count {len(candidates)} exceeds max_candidates_per_task {max_candidates}"
            )
        if route == "user" and raw.get("edit_type") in {"semantic", "generative"}:
            if raw.get("semantic_edit_approved") is not True:
                task_errors.append("semantic/generative edits to a user image require approval")
        if raw.get("reused_from") and not raw.get("reuse_reason"):
            task_errors.append("reused assets require reuse_reason")

        if route == "generated":
            generated_count += 1
            if need not in {"required", "helpful"}:
                task_errors.append("generated route requires required/helpful visual_need")
            brief = resolve_path(base, raw.get("brief"))
            if brief is None:
                task_errors.append("generated route requires brief")
            elif not brief.is_file():
                task_errors.append(f"image brief not found: {brief}")
            else:
                try:
                    brief_data = load_object(brief)
                    if brief_data.get("schema") != "ppt-series-image-brief.v1":
                        task_errors.append("image brief has an invalid schema")
                    if brief_data.get("asset_id") != asset_id:
                        task_errors.append("image brief asset_id does not match task")
                    if brief_data.get("risk") != risk:
                        task_errors.append("image brief risk does not match task")
                    for field in ("purpose", "subject", "style", "composition", "must_avoid"):
                        if not brief_data.get(field):
                            task_errors.append(f"image brief missing {field}")
                    if risk in {"medium", "high"} and not brief_data.get("factual_basis"):
                        task_errors.append(f"{risk}-risk image brief requires factual_basis")
                except (OSError, ValueError, json.JSONDecodeError) as exc:
                    task_errors.append(f"invalid image brief: {exc}")
            if risk == "high":
                if raw.get("high_risk_schematic_approved") is not True:
                    task_errors.append("high-risk generation requires explicit schematic approval")
                if raw.get("visible_disclosure") is not True:
                    task_errors.append("high-risk generation requires visible disclosure")
            if backend != "available":
                task_errors.append(f"generated route requires image_backend=available, got {backend}")

        errors.extend(f"{asset_id}: {message}" for message in task_errors)
        task_reports.append({"asset_id": asset_id, "slide": slide, "errors": task_errors})

    if max_generated is not None and generated_count > max_generated:
        errors.append(
            f"generated task count {generated_count} exceeds max_generated_assets {max_generated}"
        )
    if generated_count == 0:
        warnings.append("No generated tasks are planned; this is valid")
    if generated_count and approval_mode == "guided":
        warnings.append("Use the first actual generated slide as the style checkpoint")

    return {
        "schema": "ppt-series-visual-preflight-report.v1",
        "plan": str(plan_path),
        "ok": not errors,
        "image_backend": backend,
        "approval_mode": approval_mode,
        "task_count": len(tasks),
        "generated_task_count": generated_count,
        "errors": errors,
        "warnings": warnings,
        "tasks": task_reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--image-backend", choices=sorted(BACKENDS))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        plan = args.plan.expanduser().resolve()
        report = validate(plan, args.image_backend)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        target = args.report.expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
