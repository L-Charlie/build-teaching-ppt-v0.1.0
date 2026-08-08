#!/usr/bin/env python3
"""Validate selected visual assets, provenance, generation records, and placeholders."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROUTES = {"user", "source", "external", "screenshot", "native", "generated", "none"}
STATUSES = {"planned", "candidate-selected", "complete", "placeholder", "skipped"}


def load_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def resolve(base: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value).expanduser()
    return path if path.is_absolute() else (base / path).resolve()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(plan_path: Path, exceptions_path: Path | None, require_final: bool) -> dict[str, object]:
    plan = load_object(plan_path)
    errors: list[str] = []
    warnings: list[str] = []
    base = plan_path.parent
    if plan.get("schema") != "ppt-series-visual-plan.v1":
        errors.append("plan schema must be ppt-series-visual-plan.v1")
    tasks = plan.get("tasks")
    if not isinstance(tasks, list):
        errors.append("tasks must be an array")
        tasks = []

    exception_items: dict[str, dict[str, object]] = {}
    if exceptions_path and exceptions_path.is_file():
        exceptions = load_object(exceptions_path)
        if exceptions.get("schema") != "ppt-series-visual-exceptions.v1":
            errors.append("exceptions schema must be ppt-series-visual-exceptions.v1")
        raw_items = exceptions.get("items")
        if not isinstance(raw_items, list):
            errors.append("exceptions items must be an array")
        else:
            for item in raw_items:
                if isinstance(item, dict) and isinstance(item.get("asset_id"), str):
                    exception_items[str(item["asset_id"])] = item

    placeholders: list[str] = []
    task_reports: list[dict[str, object]] = []
    seen: set[str] = set()
    for index, raw in enumerate(tasks, start=1):
        task_errors: list[str] = []
        if not isinstance(raw, dict):
            errors.append(f"task[{index}] must be an object")
            continue
        asset_id = raw.get("asset_id")
        if not isinstance(asset_id, str) or not asset_id.strip():
            asset_id = f"task[{index}]"
            task_errors.append("asset_id is required")
        elif asset_id in seen:
            task_errors.append("duplicate asset_id")
        else:
            seen.add(asset_id)
        route = raw.get("route")
        status = raw.get("status", "planned")
        if route not in ROUTES:
            task_errors.append(f"invalid route: {route}")
        if status not in STATUSES:
            task_errors.append(f"invalid status: {status}")

        if status == "complete" and route == "native":
            slide_objects = raw.get("slide_objects")
            if not isinstance(slide_objects, list) or not slide_objects:
                task_errors.append("complete native visual requires slide_objects")
            elif not all(isinstance(item, str) and item.strip() for item in slide_objects):
                task_errors.append("native slide_objects must contain non-empty object names")

        if status == "complete" and route not in {"none", "native"}:
            asset = resolve(base, raw.get("selected_asset"))
            if asset is None:
                task_errors.append("complete task requires selected_asset")
            elif not asset.is_file():
                task_errors.append(f"selected asset not found: {asset}")
            else:
                declared_hash = raw.get("sha256")
                if declared_hash and declared_hash != sha256(asset):
                    task_errors.append("selected asset sha256 does not match")

            provenance = raw.get("provenance")
            if not isinstance(provenance, dict):
                task_errors.append("complete visual requires provenance object")
                provenance = {}
            if route == "external":
                if not provenance.get("source_url"):
                    task_errors.append("external asset requires provenance.source_url")
                if not provenance.get("rights"):
                    task_errors.append("external asset requires provenance.rights")
            if route in {"user", "source", "screenshot"} and not provenance.get("source"):
                task_errors.append(f"{route} asset requires provenance.source")
            if route == "generated":
                if raw.get("risk") == "high":
                    if raw.get("high_risk_schematic_approved") is not True:
                        task_errors.append("high-risk generated asset lacks schematic approval")
                    if raw.get("visible_disclosure") is not True:
                        task_errors.append("high-risk generated asset lacks visible disclosure")
                record = resolve(base, raw.get("generation_record"))
                if record is None:
                    task_errors.append("generated asset requires generation_record")
                elif not record.is_file():
                    task_errors.append(f"generation record not found: {record}")
                else:
                    try:
                        record_data = load_object(record)
                        if record_data.get("asset_id") != asset_id:
                            task_errors.append("generation record asset_id does not match")
                        attempts = record_data.get("attempts")
                        if not isinstance(attempts, list) or not 1 <= len(attempts) <= 2:
                            task_errors.append("generation record must contain one or two attempts")
                        if not record_data.get("prompt") and not record_data.get("prompt_path"):
                            task_errors.append("generation record requires prompt or prompt_path")
                    except (OSError, ValueError, json.JSONDecodeError) as exc:
                        task_errors.append(f"invalid generation record: {exc}")
            if raw.get("reused_from") and not raw.get("reuse_reason"):
                task_errors.append("reused asset requires reuse_reason")

        if status == "placeholder":
            placeholders.append(str(asset_id))
            exception = exception_items.get(str(asset_id))
            if exception is None:
                task_errors.append("placeholder requires a matching visual exception")
            else:
                for field in ("slide", "brief", "prompt", "negative_constraints", "attempts", "failures"):
                    if field not in exception or exception[field] in (None, "", []):
                        task_errors.append(f"visual exception missing {field}")

        errors.extend(f"{asset_id}: {message}" for message in task_errors)
        task_reports.append({"asset_id": asset_id, "status": status, "errors": task_errors})

    final_state = "draft/review" if placeholders else "eligible-for-final"
    if placeholders:
        warnings.append("Unresolved illustration placeholders: " + ", ".join(placeholders))
        if require_final:
            errors.append("--require-final failed because placeholders remain")
    return {
        "schema": "ppt-series-visual-asset-report.v1",
        "plan": str(plan_path),
        "ok": not errors,
        "delivery_state": final_state,
        "task_count": len(tasks),
        "placeholders": placeholders,
        "errors": errors,
        "warnings": warnings,
        "tasks": task_reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--exceptions", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--require-final", action="store_true")
    args = parser.parse_args()
    try:
        plan = args.plan.expanduser().resolve()
        exceptions = args.exceptions.expanduser().resolve() if args.exceptions else None
        report = validate(plan, exceptions, args.require_final)
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
