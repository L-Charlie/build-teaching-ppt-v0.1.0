#!/usr/bin/env python3
"""Validate ordered slide SVG files before PPTX export."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
XLINK = "http://www.w3.org/1999/xlink"
SEQ_RE = re.compile(r"^[A-Za-z_-]*?(\d+)(?:[_-]|$)")
HEX_RE = re.compile(r"#[0-9A-Fa-f]{6}\b")
RGB_RE = re.compile(r"\brgba?\s*\(", re.IGNORECASE)
URL_RE = re.compile(r"^https?://", re.IGNORECASE)
NUMBER_RE = re.compile(r"^-?\d+(?:\.\d+)?")


def number(value: str | None) -> float | None:
    if value is None:
        return None
    match = NUMBER_RE.match(value.strip())
    return float(match.group()) if match else None


def parse_viewbox(root: ET.Element) -> tuple[float, float, float, float] | None:
    raw = root.get("viewBox")
    if not raw:
        return None
    parts = re.split(r"[\s,]+", raw.strip())
    if len(parts) != 4:
        return None
    try:
        return tuple(float(item) for item in parts)  # type: ignore[return-value]
    except ValueError:
        return None


def extract_lock_colors(path: Path | None) -> set[str]:
    if not path:
        return set()
    return {value.upper() for value in HEX_RE.findall(path.read_text(encoding="utf-8"))}


def element_bounds(element: ET.Element) -> tuple[float, float, float, float] | None:
    tag = element.tag.rsplit("}", 1)[-1]
    if tag in {"rect", "image", "foreignObject"}:
        x = number(element.get("x")) or 0
        y = number(element.get("y")) or 0
        width = number(element.get("width"))
        height = number(element.get("height"))
        if width is not None and height is not None:
            return x, y, x + width, y + height
    if tag == "circle":
        cx = number(element.get("cx"))
        cy = number(element.get("cy"))
        radius = number(element.get("r"))
        if None not in (cx, cy, radius):
            return cx - radius, cy - radius, cx + radius, cy + radius  # type: ignore[operator]
    if tag == "ellipse":
        cx = number(element.get("cx"))
        cy = number(element.get("cy"))
        rx = number(element.get("rx"))
        ry = number(element.get("ry"))
        if None not in (cx, cy, rx, ry):
            return cx - rx, cy - ry, cx + rx, cy + ry  # type: ignore[operator]
    if tag == "line":
        points = [number(element.get(name)) for name in ("x1", "y1", "x2", "y2")]
        if all(value is not None for value in points):
            x1, y1, x2, y2 = points
            return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)  # type: ignore[arg-type]
    return None


def validate_file(path: Path, lock_colors: set[str]) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    facts: dict[str, object] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return {"file": path.name, "errors": [f"read failure: {exc}"], "warnings": [], "facts": {}}
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"file": path.name, "errors": [f"invalid XML: {exc}"], "warnings": [], "facts": {}}
    if root.tag not in {f"{{{SVG_NS}}}svg", "svg"}:
        errors.append("root element is not SVG")
    viewbox = parse_viewbox(root)
    if viewbox is None:
        errors.append("missing or invalid viewBox")
    else:
        facts["viewBox"] = list(viewbox)
    if RGB_RE.search(text):
        warnings.append("uses rgb()/rgba(); prefer explicit hex colors for converter compatibility")
    if "<style" in text:
        warnings.append("contains a style block; inline presentation-critical styles")
    ids: list[str] = []
    used_colors = {value.upper() for value in HEX_RE.findall(text)}
    if lock_colors:
        drift = sorted(used_colors - lock_colors)
        if drift:
            warnings.append(f"colors outside spec_lock: {', '.join(drift[:12])}")
    missing_assets: list[str] = []
    external_assets: list[str] = []
    out_of_bounds: list[str] = []
    if viewbox:
        vx, vy, vw, vh = viewbox
        right, bottom = vx + vw, vy + vh
    else:
        vx = vy = -math.inf
        right = bottom = math.inf
    for element in root.iter():
        if element.get("id"):
            ids.append(element.get("id", ""))
        tag = element.tag.rsplit("}", 1)[-1]
        if tag == "foreignObject":
            errors.append("contains unsupported foreignObject")
        if tag == "image":
            href = element.get("href") or element.get(f"{{{XLINK}}}href") or ""
            if href and not href.startswith("data:"):
                if URL_RE.match(href):
                    external_assets.append(href)
                else:
                    asset = (path.parent / href).resolve()
                    if not asset.is_file():
                        missing_assets.append(href)
        if element.get("transform"):
            continue
        bounds = element_bounds(element)
        if bounds:
            x1, y1, x2, y2 = bounds
            tolerance = 1.0
            if x1 < vx - tolerance or y1 < vy - tolerance or x2 > right + tolerance or y2 > bottom + tolerance:
                out_of_bounds.append(f"{tag}:{element.get('id') or '?'}")
    duplicates = [name for name, count in Counter(ids).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate element ids: {', '.join(duplicates[:12])}")
    if missing_assets:
        errors.append(f"missing local image assets: {', '.join(sorted(set(missing_assets))[:12])}")
    if external_assets:
        warnings.append(f"external image URLs are not portable: {', '.join(sorted(set(external_assets))[:6])}")
    if out_of_bounds:
        warnings.append(f"simple untransformed elements exceed viewBox: {', '.join(out_of_bounds[:12])}")
    facts["colors"] = sorted(used_colors)
    facts["element_count"] = sum(1 for _ in root.iter())
    return {"file": path.name, "errors": errors, "warnings": warnings, "facts": facts}


def validate_directory(directory: Path, lock: Path | None) -> dict[str, object]:
    files = sorted(directory.glob("*.svg"), key=lambda item: item.name)
    errors: list[str] = []
    warnings: list[str] = []
    if not files:
        errors.append("no SVG files found")
    sequences: list[tuple[int, str, int]] = []
    for file in files:
        match = SEQ_RE.match(file.stem)
        if not match:
            errors.append(f"{file.name}: missing numeric sequence prefix")
            continue
        digits = match.group(1)
        sequences.append((int(digits), file.name, len(digits)))
        if len(digits) < 2:
            errors.append(f"{file.name}: sequence prefix must be zero-padded to at least 2 digits")
    numbers = [item[0] for item in sequences]
    if len(numbers) != len(set(numbers)):
        errors.append("duplicate slide sequence numbers")
    if numbers:
        expected = list(range(min(numbers), max(numbers) + 1))
        if sorted(numbers) != expected:
            missing = sorted(set(expected) - set(numbers))
            errors.append(f"non-contiguous slide sequence; missing {missing}")
        numeric_order = [name for _, name, _ in sorted(sequences)]
        lexical_order = [name for _, name, _ in sequences]
        if lexical_order != numeric_order:
            errors.append("lexicographic filename order differs from numeric slide order")
        widths = {width for _, _, width in sequences}
        if len(widths) > 1:
            warnings.append("mixed numeric prefix widths can break lexicographic export order")
    lock_colors = extract_lock_colors(lock)
    results = [validate_file(path, lock_colors) for path in files]
    viewboxes = Counter(tuple(item["facts"].get("viewBox", [])) for item in results if item["facts"].get("viewBox"))
    if len(viewboxes) > 1:
        warnings.append(f"mixed slide viewBox values: {dict(viewboxes)}")
    file_errors = sum(len(item["errors"]) for item in results)
    file_warnings = sum(len(item["warnings"]) for item in results)
    return {
        "schema": "svg-validation.v1",
        "directory": str(directory),
        "slide_count": len(files),
        "passed": not errors and file_errors == 0,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "project_errors": len(errors),
            "project_warnings": len(warnings),
            "file_errors": file_errors,
            "file_warnings": file_warnings,
        },
        "files": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--spec-lock", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    args = parser.parse_args()
    directory = args.directory.expanduser().resolve()
    if not directory.is_dir():
        print(f"Error: directory not found: {directory}", file=sys.stderr)
        return 2
    try:
        report = validate_directory(
            directory,
            args.spec_lock.expanduser().resolve() if args.spec_lock else None,
        )
    except (OSError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    if args.report:
        target = args.report.expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))
    if not report["passed"]:
        return 1
    if args.strict and (report["summary"]["project_warnings"] or report["summary"]["file_warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
