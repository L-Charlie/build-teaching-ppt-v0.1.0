#!/usr/bin/env python3
"""Create or extend a recoverable PPT-series project."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ASSET_DIR = SKILL_DIR / "assets"
SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


def write_once(path: Path, content: str) -> None:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def copy_once(source: Path, target: Path) -> None:
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def write_json_template(source: Path, target: Path, deck_id: str) -> None:
    if target.exists():
        return
    data = json.loads(source.read_text(encoding="utf-8"))
    data["deck_id"] = deck_id
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def create_deck(root: Path, deck_id: str, deck_title: str, profile: str) -> Path:
    if not SAFE_ID.fullmatch(deck_id):
        raise ValueError("deck_id must use lowercase letters, digits, and hyphens")
    deck = root / "decks" / deck_id
    for name in ("sources", "images", "analysis", "svg_output", "notes", "exports", "backup"):
        (deck / name).mkdir(parents=True, exist_ok=True)
    for name in ("candidates", "sourced", "generated"):
        (deck / "images" / name).mkdir(parents=True, exist_ok=True)
    (deck / "analysis" / "image_briefs").mkdir(parents=True, exist_ok=True)
    plan = deck / "analysis" / "deck_plan.md"
    if not plan.exists():
        text = (ASSET_DIR / "deck_plan_template.md").read_text(encoding="utf-8")
        text = text.replace("- deck_id:", f"- deck_id: {deck_id}", 1)
        text = text.replace("- title:", f"- title: {deck_title}", 1)
        text = text.replace("- profile: general", f"- profile: {profile}", 1)
        plan.write_text(text, encoding="utf-8")
    copy_once(ASSET_DIR / "deck_overrides_template.md", deck / "analysis" / "deck_overrides.md")
    write_json_template(
        ASSET_DIR / "visual_asset_plan_template.json",
        deck / "analysis" / "visual_asset_plan.json",
        deck_id,
    )
    write_json_template(
        ASSET_DIR / "visual_exceptions_template.json",
        deck / "analysis" / "visual_exceptions.json",
        deck_id,
    )
    copy_once(
        ASSET_DIR / "image_brief_template.json",
        deck / "analysis" / "image_briefs" / "_template.json",
    )
    manifest = deck / "analysis" / "deck.json"
    if not manifest.exists():
        manifest.write_text(
            json.dumps(
                {
                    "schema": "ppt-deck.v2",
                    "deck_id": deck_id,
                    "title": deck_title,
                    "profile": profile,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "status": "initialized",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return deck


def initialize(
    root: Path,
    series_name: str,
    deck_id: str | None,
    deck_title: str | None,
    profile: str,
) -> Path | None:
    root.mkdir(parents=True, exist_ok=True)
    series = root / "series"
    for name in ("template", "shared-assets", "history"):
        (series / name).mkdir(parents=True, exist_ok=True)
    for name in ("illustration-style", "reusable-assets"):
        (series / "shared-assets" / name).mkdir(parents=True, exist_ok=True)
    (root / "decks").mkdir(exist_ok=True)
    manifest = series / "series.json"
    if not manifest.exists():
        manifest.write_text(
            json.dumps(
                {
                    "schema": "ppt-series.v2",
                    "name": series_name,
                    "profile": profile,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "active_lock_version": 1,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    lock = series / "spec_lock.md"
    if not lock.exists():
        lock_text = (ASSET_DIR / "spec_lock_template.md").read_text(encoding="utf-8")
        lock_text = lock_text.replace("profile: general", f"profile: {profile}", 1)
        lock.write_text(lock_text, encoding="utf-8")
    if deck_id:
        return create_deck(root, deck_id, deck_title or deck_id, profile)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("series_root", type=Path)
    parser.add_argument("--series-name", required=True)
    parser.add_argument(
        "--profile",
        choices=("general", "teaching", "technical", "business"),
        default="general",
    )
    parser.add_argument("--deck-id")
    parser.add_argument("--deck-title")
    parser.add_argument("--template", type=Path, help="Reference PPTX to retain and audit")
    parser.add_argument(
        "--replace-lock",
        action="store_true",
        help="Archive and replace an existing series lock with a new template-derived draft",
    )
    args = parser.parse_args()
    root = args.series_root.expanduser().resolve()
    try:
        lock_existed = (root / "series" / "spec_lock.md").exists()
        deck = initialize(root, args.series_name, args.deck_id, args.deck_title, args.profile)
        print(f"series_root: {root}")
        if deck:
            print(f"deck_root: {deck}")
        if args.template:
            from audit_template import run

            outputs = run(
                args.template.expanduser().resolve(),
                root,
                replace_lock=args.replace_lock or not lock_existed,
            )
            for name, path in outputs.items():
                print(f"{name}: {path}")
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
