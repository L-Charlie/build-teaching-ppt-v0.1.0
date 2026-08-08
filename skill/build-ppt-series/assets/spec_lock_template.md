---
schema: ppt-series-lock.v2
scope: series
state: draft
version: 1
origin:
  type: context-derived
  source: null
  extraction_scope: null
  fidelity: designed
profile: general
---

# Series Specification Lock

This file is the authoritative series-wide design contract. It must not contain a deck's page
sequence, page count, content outline, or page-by-page rhythm.

## Identity And Purpose

- series_name:
- audience:
- presentation_context:
- tone:
- language:

## Canvas And Grid

- aspect_ratio: 16:9
- canvas_size: 13.333 x 7.5 in
- safe_margin: 0.42 in
- title_zone: top 16%
- footer_zone: bottom 7%
- grid: 12 columns
- spacing_unit: 0.08 in

## Typography

- title_font: Aptos Display
- body_font: Aptos
- cjk_fallback: Microsoft YaHei
- title_size: 28-34 pt
- section_title_size: 24-30 pt
- body_size: 17-22 pt
- caption_size: 11-14 pt
- minimum_size: 11 pt
- line_spacing: 1.10-1.25
- letter_spacing: 0

## Color Roles

- background: "#F7F8FA"
- surface: "#FFFFFF"
- primary_text: "#17202A"
- secondary_text: "#52606D"
- brand_primary: "#176B87"
- accent: "#F2B134"
- success: "#2E8B57"
- warning: "#C56A1A"
- danger: "#B23A48"

## Layout Families

- cover: series identity, title, subtitle, restrained focal visual
- section: section transition and orientation
- concept: one core idea with supporting explanation
- evidence: source-backed image, chart, table, or quotation
- process: ordered steps or timeline
- comparison: explicit dimensions and balanced sides
- case: scenario, observation, interpretation, implication
- practice: prompt, task, or decision area
- summary: synthesis and next action

## Illustration System

- base_style: clean editorial illustration aligned with the template geometry and palette
- scene_profiles:
  - conceptual: simplified metaphor with clear subject hierarchy
  - technical: accurate simplified mechanism with editable labels outside the bitmap
  - narrative: coherent recurring subjects and restrained environmental detail
  - business: credible workplace context without stock-photo cliches
  - teaching: age-appropriate explanatory scene with low distraction
- palette_binding: derive dominant and accent colors from Color Roles
- rendering_consistency: keep line quality, texture, lighting, and character treatment stable
- generated_image_role: comprehension aid only; never factual evidence
- editable_overlay_rule: labels, arrows, citations, and explanatory text remain editable in PPT
- continuity_rule: assign stable subject IDs for recurring people, objects, or environments
- reuse_rule: reuse only for justified continuity, review, or series identity; record the reason
- disclosure_rule: visibly label AI-generated or schematic visuals when they may be mistaken for evidence
- prohibited: logos, watermarks, unreadable text, unsupported claims, deceptive photorealism

## Visual Source Priority

1. User-provided images
2. Source, textbook, or template images
3. Reliable and licensed external images
4. Real screenshots
5. Native editable diagrams, charts, and tables
6. Generated illustrations
7. No visual

## Invariants

- Preserve canvas, grid, typography hierarchy, color roles, and footer behavior.
- Preserve illustration language while selecting a scene profile appropriate to each slide.
- Preserve approved reference assets and their provenance.
- Keep template and material conflicts visible to the user for decision.

## Allowed Variation

- Recompute page count, sequence, rhythm, examples, evidence, visuals, and layout mapping per deck.
- Vary scene profile, composition, crop, and visual density to fit the page's communication task.
- Use deck-only overrides when they do not alter series identity.

## Change Control

- draft: generated or extracted but not approved
- confirmed: direction approved
- locked: active for batch production
- revised: changed by explicit user decision; archive the previous version

Never silently change a locked series specification.
