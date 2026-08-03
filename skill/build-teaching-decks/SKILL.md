---
name: build-teaching-decks
description: Create, extend, or improve teaching PowerPoint decks and reusable course-deck series from lesson plans, textbooks, PDFs, Word files, existing PPTX templates, screenshots, or an existing spec_lock. Use for new teaching decks, same-series chapter decks, template extraction, existing-deck optimization, long deck continuation, instructional redesign, SVG-to-PPTX production, and presentation quality assurance.
---

# Build Teaching Decks

Build teaching decks as recoverable projects, not one-off files. Preserve evidence, separate
series identity from deck-specific planning, and verify the exported artifact before delivery.

## Read First

1. Read [workflow.md](references/workflow.md) for routing, inputs, and the end-to-end process.
2. Read [spec-lock.md](references/spec-lock.md) before creating or changing any design lock.
3. Read [backend-routing.md](references/backend-routing.md) before choosing an export backend.
4. Read [quality-gates.md](references/quality-gates.md) before validation or delivery.
5. Run `python3 scripts/environment_check.py` once before choosing the artifact backend.
6. When the detected executor is Codex, read [codex-rules.md](references/codex-rules.md).
7. When the detected executor is Claude Code, read
   [claude-code-rules.md](references/claude-code-rules.md).

Do not load unrelated references.

## Resolve the Artifact Backend

- **Codex**: use the host `Presentations` skill by default. Do not ask the user to install PPT
  Master when `Presentations` is available.
- **Claude Code**: use a detected native PPTX backend. PPT Master is optional for the overall
  workflow but is required for this Skill's bundled editable SVG conversion route. If no native
  backend is available, explain the dependency before promising editable output.
- **Other hosts**: prefer a verified host presentation runtime; otherwise use an explicitly
  configured native backend or an accepted raster fallback.

Executor detection can be overridden with `TEACHING_DECK_EXECUTOR` or
`environment_check.py --executor`. If automatic detection reports `generic` but the agent knows
its host, rerun with the explicit executor. Never infer editability from the executor name alone.

## Route the Request

Choose one route after inspecting the request and attachments:

- **New style**: no reference deck. Derive a draft series lock from subject, audience, teaching
  setting, content density, and explicit style preferences.
- **Template-derived series**: a reference PPTX or visual reference exists. Audit the complete
  reference, create a draft series lock, and retain the original reference.
- **Existing lock**: validate and reuse the supplied lock. Do not regenerate it silently.
- **Improve an existing deck**: preserve content/page order for beautification; use the full
  planning workflow when splitting, merging, reordering, adding, or deleting content.

If the request and attachments are sufficient, proceed. Ask only for missing blocking inputs.
Offer step-by-step guidance when the user asks for guidance or supplies no actionable request.

## Initialize the Project

Use a series root for related decks:

```bash
python3 scripts/init_series.py SERIES_ROOT \
  --series-name "Course name" \
  --deck-id "01-introduction" \
  --deck-title "Introduction"
```

For a reference PPTX, add `--template REFERENCE.pptx`. The script retains the source without
overwriting it and creates a factual template audit plus a draft series lock.

Required structure:

```text
SERIES_ROOT/
  series/
    series.json
    spec_lock.md
    template/
    shared-assets/
    history/
  decks/
    DECK_ID/
      spec_lock.md
      sources/
      images/
      analysis/
      svg_output/
      notes/
      exports/
      backup/
```

Do not put page sequence, deck-specific teaching rhythm, or chapter content into
`series/spec_lock.md`.

## Plan Before Rendering

For each deck:

1. Inspect all relevant source material and establish the exact teaching range.
2. Write `analysis/deck_plan.md` with audience, outcomes, page sequence, per-page teaching task,
   evidence/source, visual role, and density rhythm.
3. Write deck-only exceptions in `analysis/deck_overrides.md`.
4. Recompute template/layout mapping for the current deck. Never map by matching page numbers
   from a previous chapter.
5. Run `scripts/sync_deck_spec.py` to create the deck execution snapshot.
6. Implement the deck through the selected artifact backend:
   - in Codex, follow `Presentations` and retain its editable source module and QA artifacts;
   - on the SVG compatibility route, generate zero-padded files such as `S01_cover.svg`.

Prefer adding or splitting pages over deleting difficult material or shrinking text below a
readable classroom size.

## Use the Bundled Scripts

- `environment_check.py`: detect Codex, Claude Code, or a generic host and report the recommended
  export/render route.
- `runtime_detection.py`: shared executor and optional-backend detection used by the scripts.
- `init_series.py`: create or extend a safe series project.
- `audit_template.py`: inspect a PPTX with standard-library OOXML parsing.
- `sync_deck_spec.py`: create a deck-level execution snapshot from the series lock.
- `validate_svg.py`: validate SVG syntax, order, assets, bounds, and lock color drift when the
  selected route produces SVG.
- `export_deck.py`: Claude Code/generic compatibility exporter for PPT Master or an explicitly
  allowed raster fallback; Codex normally uses `Presentations` instead.
- `validate_pptx.py`: validate the final PPTX package, slide order, relationships, and bounds.

Run scripts from this skill directory or use absolute script paths. Never assume a personal
home directory, operating system, or preinstalled PPT Master checkout.

## Lock and Approval Rules

- Treat `series/spec_lock.md` as the single authority for series-wide design.
- Treat each `decks/DECK_ID/spec_lock.md` as a generated execution snapshot.
- Use lock states `draft`, `confirmed`, `locked`, and `revised`.
- Do not claim user confirmation unless the user actually confirmed the direction.
- Do not silently modify a locked series specification during batch generation.
- Preserve the original reference PPTX. Version new references instead of overwriting.

## Delivery

Deliver the PPTX together with a concise verification report. State:

- export backend and whether slide elements are editable;
- slide count and first/last slide titles;
- structural checks run;
- visual rendering checks run;
- known limitations or checks that were not available.

Never call structural validation "visual QA".
