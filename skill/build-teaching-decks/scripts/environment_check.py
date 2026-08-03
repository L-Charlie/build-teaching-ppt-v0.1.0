#!/usr/bin/env python3
"""Report teaching-deck workflow capabilities without changing the environment."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys

from runtime_detection import EXECUTORS, detect_executor, find_ppt_master, recommend_route


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def build_report(executor: str = "auto") -> dict[str, object]:
    executables = {
        name: shutil.which(name)
        for name in ("libreoffice", "soffice", "inkscape", "rsvg-convert")
    }
    modules = {
        name: module_available(name)
        for name in ("pptx", "PIL", "cairosvg", "svglib", "reportlab", "lxml", "yaml")
    }
    ppt_master = find_ppt_master()
    svg_renderers = [
        name
        for name, available in (
            ("cairosvg", modules["cairosvg"]),
            ("inkscape", bool(executables["inkscape"])),
            ("rsvg-convert", bool(executables["rsvg-convert"])),
            ("svglib-reportlab", modules["svglib"] and modules["reportlab"]),
        )
        if available
    ]
    office_renderer = executables["libreoffice"] or executables["soffice"]
    executor_info = detect_executor(executor)
    raster_available = modules["pptx"] and bool(svg_renderers)
    routing = recommend_route(executor_info, ppt_master, raster_available)
    return {
        "executor": executor_info,
        "routing": routing,
        "python": {
            "version": ".".join(map(str, sys.version_info[:3])),
            "supported": sys.version_info >= (3, 10),
            "executable": sys.executable,
        },
        "modules": modules,
        "executables": executables,
        "ppt_master_root": str(ppt_master) if ppt_master else None,
        "capabilities": {
            "project_setup": sys.version_info >= (3, 10),
            "template_audit": sys.version_info >= (3, 10),
            "pptx_validation": sys.version_info >= (3, 10),
            "host_presentations_route": routing["preferred_backend"] == "host-presentations",
            "editable_svg_export": ppt_master is not None,
            "raster_pptx_export": raster_available,
            "office_rendering": bool(office_renderer),
            "svg_renderers": svg_renderers,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument(
        "--executor",
        choices=EXECUTORS,
        default="auto",
        help="Override executor detection; TEACHING_DECK_EXECUTOR is also supported",
    )
    parser.add_argument(
        "--require",
        choices=(
            "project-setup",
            "template-audit",
            "pptx-validation",
            "host-presentations-route",
            "editable-svg-export",
            "raster-pptx-export",
            "office-rendering",
        ),
        help="Exit nonzero when the requested capability is unavailable",
    )
    args = parser.parse_args()
    report = build_report(args.executor)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        caps = report["capabilities"]
        executor = report["executor"]
        routing = report["routing"]
        evidence = ", ".join(executor["evidence"]) or "none"
        print(f"Executor: {executor['name']} ({executor['method']}; evidence: {evidence})")
        print(f"Preferred backend: {routing['preferred_backend']}")
        print(f"Guidance: {routing['message']}")
        print(f"Python: {report['python']['version']} ({'OK' if report['python']['supported'] else 'unsupported'})")
        print(f"PPT Master: {report['ppt_master_root'] or 'not detected'}")
        print(f"SVG renderers: {', '.join(caps['svg_renderers']) or 'none'}")
        print(f"Editable SVG export: {'yes' if caps['editable_svg_export'] else 'no'}")
        print(f"Raster PPTX fallback: {'yes' if caps['raster_pptx_export'] else 'no'}")
        print(f"Office rendering: {'yes' if caps['office_rendering'] else 'no'}")
    if args.require:
        key = args.require.replace("-", "_")
        if not report["capabilities"].get(key, False):
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
