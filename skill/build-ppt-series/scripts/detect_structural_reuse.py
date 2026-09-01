#!/usr/bin/env python3
"""Detect suspicious page-for-page reuse between two deck plans."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def parse_plan(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        headers = [normalize(cell).replace(" ", "_") for cell in line.strip().strip("|").split("|")]
        if "page" not in headers or "purpose" not in headers or "layout_family" not in headers:
            continue
        rows: list[dict[str, str]] = []
        for row_line in lines[index + 2 :]:
            if not row_line.lstrip().startswith("|"):
                break
            cells = [cell.strip() for cell in row_line.strip().strip("|").split("|")]
            if len(cells) != len(headers) or not re.fullmatch(r"\d+", cells[headers.index("page")]):
                continue
            rows.append(dict(zip(headers, cells)))
        if rows:
            return rows
    raise ValueError(f"No populated Page Plan table with Purpose and Layout family: {path}")


def position_similarity(previous: list[dict[str, str]], current: list[dict[str, str]], field: str) -> float:
    if not previous or len(previous) != len(current):
        return 0.0
    matches = sum(
        normalize(left.get(field, "")) == normalize(right.get(field, ""))
        and bool(normalize(left.get(field, "")))
        for left, right in zip(previous, current)
    )
    return matches / len(current)


def compare(
    previous_plan: Path,
    current_plan: Path,
    threshold: float = 0.70,
    justification: str | None = None,
) -> dict[str, object]:
    previous = parse_plan(previous_plan)
    current = parse_plan(current_plan)
    same_page_count = len(previous) == len(current)
    purpose_similarity = position_similarity(previous, current, "purpose")
    layout_similarity = position_similarity(previous, current, "layout_family")
    suspected = (
        same_page_count
        and purpose_similarity >= threshold
        and layout_similarity >= threshold
    )
    approved_exception = suspected and bool(justification and justification.strip())
    return {
        "schema": "ppt-series-structural-reuse-report.v1",
        "previous_plan": str(previous_plan),
        "current_plan": str(current_plan),
        "previous_page_count": len(previous),
        "current_page_count": len(current),
        "same_page_count": same_page_count,
        "purpose_position_similarity": round(purpose_similarity, 4),
        "layout_position_similarity": round(layout_similarity, 4),
        "threshold": threshold,
        "status": "suspected_template_copy" if suspected else "distinct_structure",
        "approved_exception": approved_exception,
        "justification": justification.strip() if justification else None,
        "ok": not suspected or approved_exception,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("previous_plan", type=Path)
    parser.add_argument("current_plan", type=Path)
    parser.add_argument("--threshold", type=float, default=0.70)
    parser.add_argument("--justification")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if not 0 <= args.threshold <= 1:
        print("Error: --threshold must be between 0 and 1", file=sys.stderr)
        return 2
    try:
        report = compare(
            args.previous_plan.resolve(),
            args.current_plan.resolve(),
            args.threshold,
            args.justification,
        )
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if report["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
