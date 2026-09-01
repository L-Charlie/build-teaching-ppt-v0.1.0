# Quality Gates

## 1. Source And Content

- Confirm purpose, audience, source hierarchy, and allowed range.
- Verify names, numbers, dates, terminology, quotations, and claims against sources.
- Keep unresolved source or template conflicts visible to the user.
- For teaching profile, retain in-scope difficult content by expansion or page splitting.

## 2. Series And Plan

- Validate series lock state, version, origin, and template fidelity.
- Ensure deck-specific page sequence and rhythm are outside the series lock.
- Require an independently justified page range and page count with
  `previous_deck_page_count_used: false`.
- Confirm each page has purpose, source, density, layout, and visual decision.
- Ensure layout mapping is content-driven, not copied by page number.

For continuing series, run:

```bash
python3 scripts/detect_structural_reuse.py \
  PREVIOUS_DECK/analysis/deck_plan.md \
  CURRENT_DECK/analysis/deck_plan.md \
  --report CURRENT_DECK/analysis/structural_reuse_report.json
```

`suspected_template_copy` blocks production unless the current plan is redesigned or a concrete,
user-reviewed justification is recorded. Equal page counts alone do not fail this gate.

## 3. Visual Preflight

Run:

```bash
python3 scripts/visual_preflight.py DECK/analysis/visual_asset_plan.json \
  --image-backend available \
  --report DECK/analysis/visual_preflight_report.json
```

Require valid enums, budgets, image briefs, risk routing, approval rules, and backend availability.
The number of generated images is not a quality metric.

## 4. Asset Validation

Run:

```bash
python3 scripts/validate_visual_assets.py DECK/analysis/visual_asset_plan.json \
  --exceptions DECK/analysis/visual_exceptions.json \
  --report DECK/analysis/visual_asset_report.json
```

Require files for selected complete assets, provenance for external and generated assets, records
for generation, hashes when declared, and an exception for every placeholder. High-risk schematic
generation requires explicit approval and visible disclosure. Unresolved placeholders force
`draft/review` status.

## 5. SVG And PPTX Structure

When applicable, validate zero-padded SVG order, XML, local assets, canvas bounds, and lock color
drift. Export with no skipped pages. Validate the PPTX ZIP package, slide order, relationships,
media, and bounds. Structural checks do not prove visual quality.

## 6. Rendered Visual QA

Render every slide and inspect:

- overlap, clipping, overflow, broken images, blank slides, and accidental placeholders;
- text fit, hierarchy, contrast, and safe margins;
- image crop, aspect ratio, labels, source marks, and disclosure;
- chart, table, diagram, and classroom or meeting-room readability;
- consistency with the template and illustration base style;
- recurring-subject continuity and scene appropriateness.

## 7. Delivery State

Call a deck final only when required gates pass and no unresolved illustration placeholders remain.
Report export backend, editability, slide count, checks run, unperformed checks, visual exceptions,
and limitations. Never describe a save, parse, or ZIP check as rendered QA.
