---
name: build-ppt-series
description: Create, extend, or improve PowerPoint decks and reusable presentation series from source files, reference PPTX templates, screenshots, brand guides, or an existing spec_lock. Use for standalone or same-series decks, template extraction, teaching presentations, technical explainers, business reports, existing-deck optimization, long-deck continuation, visual asset planning, just-in-time illustration generation, SVG-to-PPTX production, and presentation quality assurance.
---

# Build PPT Series

Build presentations as recoverable projects. Preserve sources, separate series identity from
deck-specific planning, select visuals by communication need, and verify the exported artifact.

## Read First

1. Read [workflow.md](references/workflow.md) for routing and the end-to-end process.
2. Read [spec-lock.md](references/spec-lock.md) before creating or changing a design lock.
3. Read [visual-assets.md](references/visual-assets.md) before sourcing, editing, generating, or
   placing images.
4. Read [backend-routing.md](references/backend-routing.md) before choosing an export backend.
5. Read [quality-gates.md](references/quality-gates.md) before validation or delivery.
6. Run `python3 scripts/environment_check.py` before production. The agent must explicitly declare
   image-generation capability with `--image-backend available|unavailable|unknown`; a local Python
   script cannot discover host tools by itself.
7. For Codex, read [codex-rules.md](references/codex-rules.md). For Claude Code, read
   [claude-code-rules.md](references/claude-code-rules.md).

Do not load unrelated references.

## Resolve Backends

- **Codex**: use the host `Presentations` capability by default. Use host `imagegen` when exposed.
  Do not ask the user to install PPT Master when `Presentations` is available.
- **Claude Code**: use a detected native PPTX backend. PPT Master is optional for the overall
  workflow but required for this package's bundled editable SVG conversion route. Detect or ask
  the user to configure an image-generation backend before promising generated illustrations.
- **Other hosts**: prefer verified host presentation and image runtimes. A raster slide fallback is
  allowed only after explicit acceptance and must be reported as `editable: false`.

Use `PPT_SERIES_EXECUTOR` or `environment_check.py --executor` when detection is ambiguous. The
legacy `TEACHING_DECK_EXECUTOR` alias remains supported.

## Route the Request

Choose one route after inspecting the request and attachments:

- **New style**: derive a draft series lock from purpose, audience, context, density, and style.
- **Template-derived series**: audit the complete reference, retain it, and derive a series lock.
- **Existing lock**: validate and reuse it. Never regenerate it silently.
- **Improve an existing deck**: preserve content and order for beautification; use the full planning
  workflow when content, pages, or sequence change.

Select a profile such as `general`, `teaching`, `technical`, or `business`. In the `teaching`
profile, preserve the defined instructional range and split difficult material instead of deleting
or over-compressing it. If inputs are sufficient, proceed. Ask only for blocking information or
material conflicts; the user is the final decision maker for conflicts.

## Initialize the Project

```bash
python3 scripts/init_series.py SERIES_ROOT \
  --series-name "Series name" \
  --profile general \
  --deck-id "01-introduction" \
  --deck-title "Introduction"
```

For a reference PPTX, add `--template REFERENCE.pptx`. The source is retained without overwrite.

```text
SERIES_ROOT/
  series/
    series.json
    spec_lock.md
    template/
    shared-assets/
      illustration-style/
      reusable-assets/
    history/
  decks/DECK_ID/
    spec_lock.md
    sources/
    images/
      candidates/
      sourced/
      generated/
    analysis/
      deck_plan.md
      deck_overrides.md
      visual_asset_plan.json
      visual_exceptions.json
      image_briefs/
    svg_output/
    notes/
    exports/
    backup/
```

Keep page sequence, content, and page rhythm out of `series/spec_lock.md`.

## Plan Visuals Before Layout

For every deck:

1. Inspect the source range and write `analysis/deck_plan.md`.
2. Classify each slide's `visual_need` as `required`, `helpful`, `unnecessary`, or `prohibited`.
   Zero generated images is valid.
3. Write `analysis/visual_asset_plan.json`. Prefer, in order: user-provided images, source/template
   images, licensed external images, real screenshots, native diagrams/charts, generated
   illustrations, then no visual.
4. After the deck plan, run one broad search pass organized by visual task, not by a page quota.
   Keep only a few valid candidates per task. Invalid candidates route to generation only when the
   risk and user policy permit it.
5. Determine the layout frame and real aspect ratio before generation. Compile prompts from a
   structured image brief with `scripts/compile_image_prompt.py`, never from raw slide text.
6. Run `scripts/visual_preflight.py` before slide layout. If generation is required and the backend
   is unavailable, resolve that before production.
7. Generate only when building the relevant slide. Use at most two automatic attempts per asset.
   In guided mode, the first actual generated slide is the style checkpoint; in explicit automatic
   mode, continue without that checkpoint unless a material conflict appears.
8. Add labels, arrows, citations, and explanatory text as editable slide elements, not pixels baked
   into a generated image.

Generated illustrations aid comprehension and are never factual evidence. High-risk factual
visuals may not be freely generated without explicit schematic approval and disclosure.

## Produce and Validate

1. Recompute template/layout mapping by content function, never by matching page numbers from a
   previous deck.
2. Run `scripts/sync_deck_spec.py` to create the deck execution snapshot.
3. Author through the selected backend. For SVG routes, use zero-padded names such as
   `S01_cover.svg`.
4. Run applicable SVG and PPTX structural checks.
5. Run `scripts/validate_visual_assets.py` and rendered visual QA.
6. If an illustration still fails after two attempts, keep a simple `插图待补充` placeholder with
   its asset ID, continue other slides, and record the complete prompt, constraints, and failure.
   Any deck with unresolved placeholders is `draft/review`, never final.

## Bundled Scripts

- `environment_check.py`: executor, presentation route, and declared image backend report.
- `init_series.py`: portable project initialization.
- `audit_template.py`: standard-library OOXML template audit.
- `sync_deck_spec.py`: deck-level execution snapshot.
- `visual_preflight.py`: visual-plan, risk, budget, brief, and backend gate.
- `compile_image_prompt.py`: structured brief to provider-neutral generation prompt.
- `validate_visual_assets.py`: asset, provenance, placeholder, record, and hash validation.
- `validate_svg.py`, `export_deck.py`, `validate_pptx.py`: compatibility production and QA.

## Delivery

Deliver the PPTX and a concise verification report stating the backend, editability, slide count,
structural checks, rendered checks, visual asset status, unresolved placeholders, and limitations.
For each unresolved illustration, include slide, asset ID, brief, full prompt, negative constraints,
attempts, and failure reasons; then ask whether the user wants a retry or will provide an image.
Never call structural validation visual QA.
