#!/usr/bin/env python3
"""Validate a PPTX package, slide order, relationships, titles, and simple bounds."""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
import zipfile
from pathlib import PurePosixPath, Path
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def parse_xml(zf: zipfile.ZipFile, name: str) -> ET.Element:
    return ET.fromstring(zf.read(name))


def source_part_for_rels(rels_name: str) -> str:
    if rels_name == "_rels/.rels":
        return ""
    path = PurePosixPath(rels_name)
    if path.parent.name != "_rels" or not path.name.endswith(".rels"):
        return ""
    source_name = path.name[:-5]
    return str(path.parent.parent / source_name)


def resolve_target(source_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    base = posixpath.dirname(source_part) if source_part else ""
    return posixpath.normpath(posixpath.join(base, target))


def validate_relationships(zf: zipfile.ZipFile) -> list[dict[str, str]]:
    names = set(zf.namelist())
    missing: list[dict[str, str]] = []
    for rels_name in sorted(name for name in names if name.endswith(".rels")):
        root = parse_xml(zf, rels_name)
        source = source_part_for_rels(rels_name)
        for rel in root.findall("pr:Relationship", NS):
            if rel.get("TargetMode") == "External":
                continue
            target = rel.get("Target", "")
            if not target or target.startswith("#"):
                continue
            resolved = resolve_target(source, target)
            if resolved not in names:
                missing.append(
                    {
                        "rels": rels_name,
                        "id": rel.get("Id", ""),
                        "target": target,
                        "resolved": resolved,
                    }
                )
    return missing


def presentation_order(zf: zipfile.ZipFile) -> tuple[list[str], tuple[int, int]]:
    root = parse_xml(zf, "ppt/presentation.xml")
    size = root.find("p:sldSz", NS)
    dimensions = (
        int(size.get("cx", "0")) if size is not None else 0,
        int(size.get("cy", "0")) if size is not None else 0,
    )
    rel_root = parse_xml(zf, "ppt/_rels/presentation.xml.rels")
    relationships = {
        node.get("Id", ""): resolve_target("ppt/presentation.xml", node.get("Target", ""))
        for node in rel_root.findall("pr:Relationship", NS)
    }
    order: list[str] = []
    slide_list = root.find("p:sldIdLst", NS)
    if slide_list is not None:
        for item in slide_list.findall("p:sldId", NS):
            rel_id = item.get(f"{{{NS['r']}}}id", "")
            if rel_id:
                order.append(relationships.get(rel_id, f"MISSING_REL:{rel_id}"))
    return order, dimensions


def slide_title(root: ET.Element) -> str:
    fallback = ""
    for shape in root.findall(".//p:sp", NS):
        text = "".join(node.text or "" for node in shape.findall(".//a:t", NS)).strip()
        if not text:
            continue
        if not fallback:
            fallback = text
        placeholder = shape.find(".//p:nvPr/p:ph", NS)
        if placeholder is not None and placeholder.get("type") in {"title", "ctrTitle"}:
            return text
    return fallback


def simple_bounds(root: ET.Element, width: int, height: int) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    tree = root.find("p:cSld/p:spTree", NS)
    if tree is None:
        return issues
    for child in list(tree):
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "sp":
            xfrm = child.find("p:spPr/a:xfrm", NS)
            name_node = child.find("p:nvSpPr/p:cNvPr", NS)
        elif tag == "pic":
            xfrm = child.find("p:spPr/a:xfrm", NS)
            name_node = child.find("p:nvPicPr/p:cNvPr", NS)
        elif tag == "graphicFrame":
            xfrm = child.find("p:xfrm", NS)
            name_node = child.find("p:nvGraphicFramePr/p:cNvPr", NS)
        elif tag == "cxnSp":
            xfrm = child.find("p:spPr/a:xfrm", NS)
            name_node = child.find("p:nvCxnSpPr/p:cNvPr", NS)
        else:
            continue
        if xfrm is None:
            continue
        offset = xfrm.find("a:off", NS)
        extent = xfrm.find("a:ext", NS)
        if offset is None or extent is None:
            continue
        x = int(offset.get("x", "0"))
        y = int(offset.get("y", "0"))
        cx = int(extent.get("cx", "0"))
        cy = int(extent.get("cy", "0"))
        tolerance = 1000
        if x < -tolerance or y < -tolerance or x + cx > width + tolerance or y + cy > height + tolerance:
            issues.append(
                {
                    "type": tag,
                    "name": name_node.get("name") if name_node is not None else None,
                    "x": x,
                    "y": y,
                    "cx": cx,
                    "cy": cy,
                }
            )
    return issues


def validate(path: Path, expected_count: int | None, first: str | None, last: str | None) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    if not zipfile.is_zipfile(path):
        return {"passed": False, "errors": ["not a valid ZIP/PPTX package"], "warnings": []}
    with zipfile.ZipFile(path) as zf:
        bad = zf.testzip()
        if bad:
            errors.append(f"corrupt ZIP member: {bad}")
        names = set(zf.namelist())
        for required in ("[Content_Types].xml", "ppt/presentation.xml", "ppt/_rels/presentation.xml.rels"):
            if required not in names:
                errors.append(f"missing required part: {required}")
        if errors:
            return {"passed": False, "errors": errors, "warnings": warnings}
        try:
            missing = validate_relationships(zf)
            if missing:
                errors.append(f"{len(missing)} internal relationship target(s) are missing")
            order, dimensions = presentation_order(zf)
            slide_records: list[dict[str, object]] = []
            for index, part in enumerate(order, start=1):
                if part not in names:
                    errors.append(f"slide {index} cannot be resolved: {part}")
                    continue
                root = parse_xml(zf, part)
                bounds = simple_bounds(root, *dimensions)
                if bounds:
                    warnings.append(f"slide {index} has {len(bounds)} simple top-level bounds issue(s)")
                slide_records.append(
                    {
                        "index": index,
                        "part": part,
                        "title": slide_title(root),
                        "bounds_issues": bounds,
                    }
                )
        except (KeyError, ET.ParseError, ValueError) as exc:
            errors.append(f"OOXML parse failure: {exc}")
            order, dimensions, slide_records, missing = [], (0, 0), [], []
        if expected_count is not None and len(order) != expected_count:
            errors.append(f"expected {expected_count} slides, found {len(order)}")
        titles = [str(item["title"]) for item in slide_records]
        if first and (not titles or first.casefold() not in titles[0].casefold()):
            errors.append(f"first title does not contain expected text: {first!r}")
        if last and (not titles or last.casefold() not in titles[-1].casefold()):
            errors.append(f"last title does not contain expected text: {last!r}")
        media = sorted(name for name in names if name.startswith("ppt/media/") and not name.endswith("/"))
        return {
            "schema": "pptx-validation.v1",
            "path": str(path),
            "passed": not errors,
            "errors": errors,
            "warnings": warnings,
            "slide_count": len(order),
            "canvas_emu": list(dimensions),
            "media_count": len(media),
            "missing_relationships": missing,
            "slides": slide_records,
            "first_title": slide_records[0]["title"] if slide_records else "",
            "last_title": slide_records[-1]["title"] if slide_records else "",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--expected-count", type=int)
    parser.add_argument("--expected-first")
    parser.add_argument("--expected-last")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    args = parser.parse_args()
    path = args.pptx.expanduser().resolve()
    if not path.is_file():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 2
    try:
        report = validate(path, args.expected_count, args.expected_first, args.expected_last)
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    if args.report:
        target = args.report.expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "passed": report["passed"],
                "slides": report.get("slide_count", 0),
                "media": report.get("media_count", 0),
                "warnings": len(report["warnings"]),
            }
        )
    )
    if not report["passed"]:
        return 1
    if args.strict and report["warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
