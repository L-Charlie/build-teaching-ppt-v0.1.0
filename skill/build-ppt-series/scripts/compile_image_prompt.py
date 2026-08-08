#!/usr/bin/env python3
"""Compile a provider-neutral image prompt from a structured JSON brief."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_brief(path: Path) -> dict[str, object]:
    brief = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(brief, dict):
        raise ValueError("Image brief must be a JSON object")
    if brief.get("schema") != "ppt-series-image-brief.v1":
        raise ValueError("schema must be ppt-series-image-brief.v1")
    for field in ("asset_id", "purpose", "subject"):
        if not isinstance(brief.get(field), str) or not str(brief[field]).strip():
            raise ValueError(f"{field} is required")
    if brief.get("risk") not in {"low", "medium", "high"}:
        raise ValueError("risk must be low, medium, or high")
    for field in ("style", "composition"):
        if not isinstance(brief.get(field), dict):
            raise ValueError(f"{field} must be an object")
    return brief


def text_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def compile_prompt(brief: dict[str, object]) -> str:
    style = brief["style"]
    composition = brief["composition"]
    assert isinstance(style, dict) and isinstance(composition, dict)
    must_show = text_list(brief.get("must_show"))
    palette = text_list(style.get("palette"))
    continuity = text_list(style.get("continuity_ids"))
    factual_basis = text_list(brief.get("factual_basis"))
    avoid = text_list(brief.get("must_avoid"))
    fixed_avoid = [
        "text, labels, captions, arrows, logos, signatures, or watermarks inside the image",
        "unsupported factual details or misleading evidence-like treatment",
    ]
    avoid = list(dict.fromkeys(avoid + fixed_avoid))

    lines = [
        f"Create one presentation illustration for asset {brief['asset_id']}.",
        f"Communication purpose: {brief['purpose']}.",
        f"Subject: {brief['subject']}.",
    ]
    if must_show:
        lines.append("Must visibly show: " + "; ".join(must_show) + ".")
    lines.extend(
        [
            f"Base visual style: {style.get('base_style', 'follow the approved series style')}.",
            f"Scene profile: {style.get('scene_profile', 'conceptual')}.",
        ]
    )
    if palette:
        lines.append("Palette guidance: " + ", ".join(palette) + ".")
    if continuity:
        lines.append("Maintain continuity for IDs: " + ", ".join(continuity) + ".")
    lines.extend(
        [
            f"Aspect ratio: {composition.get('aspect_ratio', 'match the slide frame')}.",
            f"Placement context: {composition.get('placement', 'main visual area')}.",
            f"Subject position: {composition.get('subject_position', 'center')}.",
            f"Reserved whitespace: {composition.get('reserved_whitespace', 'none')}.",
            f"Background: {composition.get('background', 'simple and coherent')}.",
        ]
    )
    if factual_basis:
        lines.append("Only use these source-grounded facts: " + "; ".join(factual_basis) + ".")
    lines.append("Avoid: " + "; ".join(avoid) + ".")
    lines.append(
        "Leave all educational or explanatory text to editable PowerPoint elements. "
        "Return a clean bitmap composition that fits the stated frame."
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("brief", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        brief = load_brief(args.brief.expanduser().resolve())
        prompt = compile_prompt(brief)
        if args.output:
            target = args.output.expanduser().resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(prompt, encoding="utf-8")
        print(prompt, end="")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
