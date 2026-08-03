---
schema: teaching-deck-series-lock.v1
scope: series
status: draft
version: 1
updated: YYYY-MM-DD
origin:
  type: generated
  source: null
  audit: null
  fidelity: designed
---

# Series Design Lock

## Canvas

- format: ppt169
- width_px: 1280
- height_px: 720
- aspect_ratio: 16:9

## Teaching Mode

- mode: instructional
- audience:
- delivery_context:

## Visual Style

- style:
- tone:
- density:

## Colors

- background: #FFFFFF
- surface: #F8FAFC
- primary: #1B4F8A
- secondary: #3A7BD5
- accent: #F5A623
- text: #1E293B
- text_secondary: #64748B
- border: #E2E8F0
- success: #22C55E
- warning: #EF4444

## Typography

- title_family: Arial, "Microsoft YaHei", sans-serif
- body_family: Arial, "Microsoft YaHei", sans-serif
- cover_title_px: 54
- page_title_px: 38
- body_px: 24
- annotation_px: 18
- footnote_px: 14

## Grid and Spacing

- safe_margin_px: 48
- columns: 12
- gutter_px: 20
- card_radius_px: 8
- title_zone_height_px: 86
- footer_zone_height_px: 32

## Layout Families

- cover: course/chapter identity and one clear visual anchor
- chapter: section transition with low density
- concept: definition plus example or diagram
- procedure: numbered operational steps
- comparison: aligned criteria and clear difference
- case: source visual plus observations and judgement
- practice: task, inputs, steps, and acceptance criteria
- diagnosis: symptom, cause, check, and correction
- summary: outcomes, decisions, and next action

## Images

- source_policy:
- crop_policy:
- caption_policy:
- attribution_policy:

## Tables, Charts, and Diagrams

- table_style:
- chart_style:
- diagram_style:

## Recurring Elements

- header:
- footer:
- page_number:
- logo:
- citations:

## Series Invariants

- Keep canvas, color roles, typography roles, margins, and recurring elements stable.
- Preserve the defined visual treatment of images, tables, charts, and diagrams.

## Allowed Deck Variation

- Recompute page count, sequence, teaching rhythm, examples, images, exercises, and layout mapping.
- Add deck-only overrides without changing the series identity.

## Prohibited

- Do not copy a previous deck page-for-page.
- Do not put deck-specific page rhythm or chapter content in this file.
- Do not silently change a locked value.
