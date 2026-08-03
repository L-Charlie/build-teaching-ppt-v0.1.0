#!/usr/bin/env python3
"""Generate a deck-level spec_lock snapshot from series and deck inputs."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lock_version(text: str) -> str:
    match = re.search(r"(?m)^version:\s*([^\s#]+)", text)
    return match.group(1) if match else "unknown"


def optional_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def optional_hash(path: Path) -> str:
    return file_hash(path) if path.exists() else "missing"


def plan_issues(text: str) -> list[str]:
    issues: list[str] = []
    for field in ("title", "audience", "teaching_context", "source_scope"):
        match = re.search(rf"(?m)^-\s+{field}:\s*(.*)$", text)
        if not match or not match.group(1).strip():
            issues.append(f"missing deck plan field: {field}")
    rows = [
        line
        for line in text.splitlines()
        if re.match(r"^\|\s*\d+\s*\|", line)
    ]
    useful_rows = []
    for row in rows:
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[1] and cells[2] and cells[3]:
            useful_rows.append(row)
    if not useful_rows:
        issues.append("page plan has no populated slide row")
    return issues


def sync(
    series_root: Path,
    deck_id: str,
    force: bool = False,
    allow_incomplete: bool = False,
) -> Path:
    parent = series_root / "series" / "spec_lock.md"
    deck = series_root / "decks" / deck_id
    plan = deck / "analysis" / "deck_plan.md"
    overrides = deck / "analysis" / "deck_overrides.md"
    target = deck / "spec_lock.md"
    if not parent.is_file():
        raise FileNotFoundError(f"Series lock not found: {parent}")
    if not plan.is_file():
        raise FileNotFoundError(f"Deck plan not found: {plan}")
    if not overrides.is_file():
        raise FileNotFoundError(f"Deck overrides not found: {overrides}")
    incomplete = plan_issues(plan.read_text(encoding="utf-8"))
    if incomplete and not allow_incomplete:
        raise ValueError(
            "Deck plan is incomplete: "
            + "; ".join(incomplete)
            + ". Complete the plan or pass --allow-incomplete for a non-production snapshot."
        )
    if target.exists() and not force:
        existing = target.read_text(encoding="utf-8")
        if (
            f'parent_sha256: "{file_hash(parent)}"' in existing
            and f'deck_plan_sha256: "{file_hash(plan)}"' in existing
            and f'deck_overrides_sha256: "{file_hash(overrides)}"' in existing
        ):
            return target
        raise FileExistsError(f"Snapshot inputs changed; rerun with --force: {target}")
    if target.exists():
        backup = deck / "backup"
        backup.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(target, backup / f"spec_lock-{stamp}.md")
    parent_text = parent.read_text(encoding="utf-8")
    snapshot = f"""---
schema: teaching-deck-execution-lock.v1
scope: deck-snapshot
generated_snapshot: true
generated_at: "{datetime.now(timezone.utc).isoformat()}"
deck_id: "{deck_id}"
parent_lock: "../../series/spec_lock.md"
parent_version: "{lock_version(parent_text)}"
parent_sha256: "{file_hash(parent)}"
deck_plan: "analysis/deck_plan.md"
deck_plan_sha256: "{file_hash(plan)}"
deck_overrides: "analysis/deck_overrides.md"
deck_overrides_sha256: "{file_hash(overrides)}"
---

# Deck Execution Lock

Do not edit this generated snapshot. Edit the series lock, deck plan, or deck overrides, then
regenerate it with `sync_deck_spec.py --force`.

## Deck Plan

{optional_text(plan).strip()}

## Deck Overrides

{optional_text(overrides).strip()}

## Inherited Series Lock

{parent_text.strip()}
"""
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(snapshot, encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("series_root", type=Path)
    parser.add_argument("deck_id")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow a non-production snapshot from a plan skeleton",
    )
    args = parser.parse_args()
    try:
        target = sync(
            args.series_root.expanduser().resolve(),
            args.deck_id,
            args.force,
            args.allow_incomplete,
        )
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
