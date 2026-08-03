#!/usr/bin/env python3
"""Audit a PPTX reference and create portable template facts plus a draft series lock."""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import shutil
import sys
import zipfile
from collections import Counter
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}
EMU_PER_INCH = 914400
SLIDE_RE = re.compile(r"^ppt/slides/slide(\d+)\.xml$")
LAYOUT_RE = re.compile(r"^ppt/slideLayouts/slideLayout(\d+)\.xml$")


def parse_xml(zf: zipfile.ZipFile, name: str) -> ET.Element:
    try:
        return ET.fromstring(zf.read(name))
    except KeyError as exc:
        raise ValueError(f"Missing required package part: {name}") from exc
    except ET.ParseError as exc:
        raise ValueError(f"Invalid XML in {name}: {exc}") from exc


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def numeric_parts(names: list[str], pattern: re.Pattern[str]) -> list[str]:
    indexed: list[tuple[int, str]] = []
    for name in names:
        match = pattern.match(name)
        if match:
            indexed.append((int(match.group(1)), name))
    return [name for _, name in sorted(indexed)]


def relationship_map(zf: zipfile.ZipFile, rels_name: str) -> dict[str, str]:
    if rels_name not in zf.namelist():
        return {}
    root = parse_xml(zf, rels_name)
    return {
        rel.get("Id", ""): rel.get("Target", "")
        for rel in root.findall("pr:Relationship", NS)
    }


def normalize_target(source_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(source_part), target))


def extract_theme(zf: zipfile.ZipFile) -> dict[str, object]:
    theme_names = sorted(name for name in zf.namelist() if name.startswith("ppt/theme/theme") and name.endswith(".xml"))
    if not theme_names:
        return {"part": None, "colors": {}, "fonts": {}}
    part = theme_names[0]
    root = parse_xml(zf, part)
    colors: dict[str, str] = {}
    scheme = root.find(".//a:clrScheme", NS)
    if scheme is not None:
        for role in list(scheme):
            role_name = role.tag.rsplit("}", 1)[-1]
            child = next(iter(role), None)
            if child is None:
                continue
            color_kind = child.tag.rsplit("}", 1)[-1]
            if color_kind == "sysClr":
                value = child.get("lastClr") or child.get("val")
            else:
                value = child.get("val") or child.get("lastClr")
            if value:
                colors[role_name] = f"#{value.upper()}"
    fonts: dict[str, str] = {}
    for prefix, xpath in (("major", ".//a:majorFont"), ("minor", ".//a:minorFont")):
        node = root.find(xpath, NS)
        if node is None:
            continue
        for script in ("latin", "ea", "cs"):
            font = node.find(f"a:{script}", NS)
            if font is not None and font.get("typeface"):
                fonts[f"{prefix}_{script}"] = font.get("typeface", "")
    return {"part": part, "colors": colors, "fonts": fonts}


def extract_canvas(zf: zipfile.ZipFile) -> dict[str, object]:
    root = parse_xml(zf, "ppt/presentation.xml")
    size = root.find("p:sldSz", NS)
    if size is None:
        raise ValueError("ppt/presentation.xml has no p:sldSz")
    cx = int(size.get("cx", "0"))
    cy = int(size.get("cy", "0"))
    width = cx / EMU_PER_INCH
    height = cy / EMU_PER_INCH
    ratio = width / height if height else 0
    common = "16:9" if abs(ratio - 16 / 9) < 0.03 else "4:3" if abs(ratio - 4 / 3) < 0.03 else f"{ratio:.3f}:1"
    declared = size.get("type")
    declared_ratio = {
        "screen4x3": "4:3",
        "screen16x9": "16:9",
        "screen16x10": "16:10",
        "wide": "16:9",
    }.get(declared or "")
    return {
        "cx_emu": cx,
        "cy_emu": cy,
        "width_in": round(width, 4),
        "height_in": round(height, 4),
        "aspect_ratio": common,
        "declared_type": declared,
        "declared_type_consistent": declared_ratio in {None, common},
    }


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


def observed_slide_facts(zf: zipfile.ZipFile, slide_names: list[str]) -> tuple[list[dict[str, object]], Counter[str], Counter[float]]:
    slides: list[dict[str, object]] = []
    colors: Counter[str] = Counter()
    sizes: Counter[float] = Counter()
    for index, name in enumerate(slide_names, start=1):
        root = parse_xml(zf, name)
        for node in root.findall(".//a:srgbClr", NS):
            value = node.get("val")
            if value:
                colors[f"#{value.upper()}"] += 1
        for node in root.findall(".//*[@sz]"):
            raw = node.get("sz", "")
            if raw.isdigit():
                sizes[int(raw) / 100] += 1
        rels = f"ppt/slides/_rels/{PurePosixPath(name).name}.rels"
        rel_map = relationship_map(zf, rels)
        layout_target = next((target for target in rel_map.values() if "slideLayout" in target), None)
        layout_part = normalize_target(name, layout_target) if layout_target else None
        slides.append(
            {
                "index": index,
                "part": name,
                "title": slide_title(root),
                "shape_count": len(root.findall(".//p:sp", NS)),
                "picture_count": len(root.findall(".//p:pic", NS)),
                "graphic_frame_count": len(root.findall(".//p:graphicFrame", NS)),
                "layout_part": layout_part,
            }
        )
    return slides, colors, sizes


def layout_catalog(zf: zipfile.ZipFile, layout_names: list[str], usage: Counter[str]) -> list[dict[str, object]]:
    catalog: list[dict[str, object]] = []
    for name in layout_names:
        root = parse_xml(zf, name)
        placeholders = Counter(
            (node.get("type") or "body")
            for node in root.findall(".//p:nvPr/p:ph", NS)
        )
        c_sld = root.find("p:cSld", NS)
        catalog.append(
            {
                "part": name,
                "name": c_sld.get("name") if c_sld is not None else None,
                "used_by_slides": usage.get(name, 0),
                "shape_count": len(root.findall(".//p:sp", NS)),
                "picture_count": len(root.findall(".//p:pic", NS)),
                "placeholders": dict(placeholders),
            }
        )
    return catalog


def retain_source(source: Path, template_dir: Path) -> Path:
    template_dir.mkdir(parents=True, exist_ok=True)
    primary = template_dir / "source-template.pptx"
    if not primary.exists():
        shutil.copy2(source, primary)
        return primary
    if sha256(primary) == sha256(source):
        return primary
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    versioned = template_dir / f"source-template-{stamp}.pptx"
    shutil.copy2(source, versioned)
    return versioned


def lock_text(source_name: str, audit_rel: str, audit: dict[str, object]) -> str:
    canvas = audit["canvas"]
    theme = audit["theme"]
    colors = theme["colors"]
    fonts = theme["fonts"]
    observed = audit["observed"]
    observed_palette = ", ".join(item["value"] for item in observed["colors"][:16])
    primary = colors.get("accent1") or (observed["colors"][0]["value"] if observed["colors"] else "#1B4F8A")
    secondary = colors.get("accent2") or "#3A7BD5"
    background = colors.get("lt1") or "#FFFFFF"
    text = colors.get("dk1") or "#1E293B"
    title_font = fonts.get("major_ea") or fonts.get("major_latin") or "Arial"
    body_font = fonts.get("minor_ea") or fonts.get("minor_latin") or "Arial"
    return f"""---
schema: teaching-deck-series-lock.v1
scope: series
status: draft
version: 1
updated: {date.today().isoformat()}
origin:
  type: extracted-from-pptx
  source: "{source_name}"
  audit: "{audit_rel}"
  fidelity: exact-template-reference
---

# Series Design Lock

Values below are extracted facts where available. Complete the recommendation fields before
locking the series.

## Canvas

- source_width_in: {canvas['width_in']}
- source_height_in: {canvas['height_in']}
- aspect_ratio: {canvas['aspect_ratio']}
- output_width_px: 1280
- output_height_px: 720

## Teaching Mode

- mode: instructional
- audience:
- delivery_context:

## Visual Style

- style: [recommendation required]
- tone: [recommendation required]
- density: [recommendation required]

## Colors

- background: {background}
- primary: {primary}
- secondary: {secondary}
- accent: {colors.get('accent3', '#F5A623')}
- text: {text}
- text_secondary: {colors.get('dk2', '#64748B')}
- observed_palette: {observed_palette or "none"}

## Typography

- title_family: "{title_font}", sans-serif
- body_family: "{body_font}", sans-serif
- title_sizes_pt_observed: {", ".join(str(item['value']) for item in observed['font_sizes_pt'][:4]) or "unknown"}
- page_title_px: [decision required]
- body_px: [decision required]
- annotation_px: [decision required]

## Template Facts

- slide_count: {audit['slide_count']}
- master_count: {audit['master_count']}
- layout_count: {audit['layout_count']}
- media_count: {audit['media_count']}
- layout_catalog: series/template/layout-catalog.json

## Layout Families

- cover: [map to audited layout]
- chapter: [map to audited layout]
- concept: [map to audited layout]
- procedure: [map to audited layout]
- comparison: [map to audited layout]
- case: [map to audited layout]
- practice: [map to audited layout]
- diagnosis: [map to audited layout]
- summary: [map to audited layout]

## Images

- source_policy: retain original template assets; add only relevant, attributable teaching images
- crop_policy: [decision required]
- caption_policy: [decision required]
- attribution_policy: [decision required]

## Tables, Charts, and Diagrams

- table_style: follow audited template unless readability requires an approved deck override
- chart_style: follow audited template color roles and typography
- diagram_style: follow audited template geometry and line treatment

## Recurring Elements

- header: [audit and decide]
- footer: [audit and decide]
- page_number: [audit and decide]
- logo: preserve according to source template
- citations: [decision required]

## Series Invariants

- Keep canvas, color roles, typography roles, margins, and recurring elements stable.
- Preserve the source PPTX as the exact layout and asset reference.

## Allowed Deck Variation

- Recompute page count, sequence, rhythm, examples, images, exercises, and layout mapping.
- Use deck-only overrides for chapter-specific needs.

## Prohibited

- Do not copy a previous deck page-for-page.
- Do not store deck-specific page rhythm or chapter content here.
- Do not silently change a locked value.
"""


def run(source: Path, series_root: Path, replace_lock: bool = False) -> dict[str, Path]:
    if not source.is_file():
        raise FileNotFoundError(source)
    if not zipfile.is_zipfile(source):
        raise ValueError(f"Not a valid PPTX ZIP package: {source}")
    template_dir = series_root / "series" / "template"
    template_dir.mkdir(parents=True, exist_ok=True)
    retained = retain_source(source, template_dir)
    with zipfile.ZipFile(source) as zf:
        bad = zf.testzip()
        if bad:
            raise ValueError(f"Corrupt PPTX member: {bad}")
        names = zf.namelist()
        slide_names = numeric_parts(names, SLIDE_RE)
        layout_names = numeric_parts(names, LAYOUT_RE)
        slides, observed_colors, observed_sizes = observed_slide_facts(zf, slide_names)
        usage = Counter(slide["layout_part"] for slide in slides if slide["layout_part"])
        layouts = layout_catalog(zf, layout_names, usage)
        audit = {
            "schema": "teaching-template-audit.v1",
            "source_original": str(source.resolve()),
            "source_retained": str(retained.relative_to(series_root)),
            "source_sha256": sha256(source),
            "canvas": extract_canvas(zf),
            "theme": extract_theme(zf),
            "slide_count": len(slide_names),
            "master_count": len([name for name in names if re.match(r"^ppt/slideMasters/slideMaster\d+\.xml$", name)]),
            "layout_count": len(layout_names),
            "media_count": len([name for name in names if name.startswith("ppt/media/") and not name.endswith("/")]),
            "slides": slides,
            "observed": {
                "colors": [{"value": value, "uses": count} for value, count in observed_colors.most_common(24)],
                "font_sizes_pt": [{"value": value, "uses": count} for value, count in observed_sizes.most_common(16)],
            },
        }
        audit["warnings"] = []
        if not audit["canvas"]["declared_type_consistent"]:
            audit["warnings"].append(
                "OOXML slide-size type disagrees with physical dimensions; use the physical dimensions and computed aspect ratio."
            )
    audit_path = template_dir / "template-audit.json"
    layout_path = template_dir / "layout-catalog.json"
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    layout_path.write_text(json.dumps({"schema": "layout-catalog.v1", "layouts": layouts}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lock_path = series_root / "series" / "spec_lock.md"
    if replace_lock or not lock_path.exists():
        if lock_path.exists():
            history = series_root / "series" / "history"
            history.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            shutil.copy2(lock_path, history / f"spec_lock-before-audit-{stamp}.md")
        lock_path.write_text(
            lock_text(retained.name, str(audit_path.relative_to(series_root)), audit),
            encoding="utf-8",
        )
    return {"retained": retained, "audit": audit_path, "layouts": layout_path, "lock": lock_path}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Reference PPTX")
    parser.add_argument("series_root", type=Path, help="Series project root")
    parser.add_argument("--replace-lock", action="store_true", help="Archive and replace an existing series lock")
    args = parser.parse_args()
    try:
        outputs = run(args.source.expanduser().resolve(), args.series_root.expanduser().resolve(), args.replace_lock)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
