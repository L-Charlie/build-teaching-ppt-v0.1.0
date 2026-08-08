#!/usr/bin/env python3
"""Detect the agent executor and optional presentation backends."""

from __future__ import annotations

import os
from pathlib import Path

EXECUTORS = ("auto", "codex", "claude-code", "generic")


def normalize_executor(value: str | None) -> str:
    normalized = (value or "auto").strip().lower().replace("_", "-")
    aliases = {
        "cc": "claude-code",
        "claude": "claude-code",
        "chatgpt": "codex",
        "openai": "codex",
    }
    normalized = aliases.get(normalized, normalized)
    if normalized not in EXECUTORS:
        valid = ", ".join(EXECUTORS)
        raise ValueError(f"Unknown executor {value!r}; expected one of: {valid}")
    return normalized


def detect_executor(explicit: str | None = None) -> dict[str, object]:
    requested = normalize_executor(explicit)
    if requested != "auto":
        return {
            "name": requested,
            "method": "argument",
            "evidence": [f"--executor={requested}"],
        }

    override_name = "PPT_SERIES_EXECUTOR"
    override = os.environ.get(override_name)
    if not override:
        override_name = "TEACHING_DECK_EXECUTOR"
        override = os.environ.get(override_name)
    if override:
        selected = normalize_executor(override)
        if selected == "auto":
            raise ValueError(f"{override_name} cannot be set to auto")
        return {
            "name": selected,
            "method": "environment-override",
            "evidence": [override_name],
        }

    codex_markers = (
        "CODEX_THREAD_ID",
        "CODEX_HOME",
        "CODEX_CI",
        "CODEX_INTERNAL_ORIGINATOR_OVERRIDE",
    )
    codex_evidence = [name for name in codex_markers if os.environ.get(name)]
    if codex_evidence:
        return {
            "name": "codex",
            "method": "environment-markers",
            "evidence": codex_evidence,
        }

    claude_markers = (
        "CLAUDECODE",
        "CLAUDE_CODE_ENTRYPOINT",
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDE_CODE_TASK_LIST_ID",
    )
    claude_evidence = [name for name in claude_markers if os.environ.get(name)]
    if claude_evidence:
        return {
            "name": "claude-code",
            "method": "environment-markers",
            "evidence": claude_evidence,
        }

    return {
        "name": "generic",
        "method": "fallback",
        "evidence": [],
    }


def find_ppt_master() -> Path | None:
    candidates: list[Path] = []
    configured = os.environ.get("PPT_MASTER_ROOT")
    if configured:
        candidates.append(Path(configured).expanduser())
    home = Path.home()
    candidates.extend(
        [
            home / ".agents" / "skills" / "ppt-master",
            home / ".codex" / "skills" / "ppt-master",
            home / ".claude" / "skills" / "ppt-master",
        ]
    )
    for candidate in candidates:
        if (candidate / "scripts" / "svg_to_pptx.py").is_file():
            return candidate.resolve()
    return None


def host_presentations_requested(executor: str) -> bool:
    configured = os.environ.get("PPT_SERIES_HOST_PRESENTATIONS")
    if configured is None:
        configured = os.environ.get("TEACHING_DECK_HOST_PRESENTATIONS", "")
    configured = configured.strip().lower()
    return executor == "codex" or configured in {"1", "true", "yes", "on"}


def recommend_route(
    executor_info: dict[str, object],
    ppt_master: Path | None,
    raster_available: bool,
) -> dict[str, object]:
    executor = str(executor_info["name"])
    if host_presentations_requested(executor):
        return {
            "preferred_backend": "host-presentations",
            "action_required_for_editable": False,
            "message": (
                "Use the host Presentations skill/runtime for authoring, export, rendering, "
                "and visual QA. Do not ask the user to install PPT Master."
            ),
        }
    if executor == "claude-code":
        if ppt_master:
            return {
                "preferred_backend": "ppt-master-native",
                "action_required_for_editable": False,
                "message": (
                    "Use the detected PPT Master backend for editable SVG-to-PPTX export."
                ),
            }
        fallback = "raster-fallback" if raster_available else "setup-required"
        return {
            "preferred_backend": fallback,
            "action_required_for_editable": True,
            "message": (
                "Claude Code was detected without an editable presentation backend. "
                "Before promising editable output, tell the user to install/configure PPT "
                "Master or another native PPTX backend. Raster export may be used only with "
                "the user's acceptance."
            ),
        }
    if ppt_master:
        return {
            "preferred_backend": "ppt-master-native",
            "action_required_for_editable": False,
            "message": "Use the detected PPT Master backend for editable SVG-to-PPTX export.",
        }
    return {
        "preferred_backend": "raster-fallback" if raster_available else "setup-required",
        "action_required_for_editable": True,
        "message": (
            "No native presentation backend was detected. Configure a host presentation "
            "runtime or accept the explicitly non-editable raster fallback."
        ),
    }
