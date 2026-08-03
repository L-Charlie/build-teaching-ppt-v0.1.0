# `spec_lock` Contract

## Contents

1. Purpose
2. Sources and priority
3. Two-level model
4. Required series fields
5. Lifecycle
6. Template extraction
7. Change control

## 1. Purpose

`spec_lock` is a portable design contract owned by this skill. It is not tied to PPT Master or
any other exporter.

## 2. Sources and Priority

Resolve design information in this order:

1. A user-supplied `spec_lock.md`.
2. A complete reference PPTX.
3. Explicit user style requirements.
4. A context-derived draft based on subject, audience, and teaching use.

Record whether each important value is a source fact, a user decision, or a generated
recommendation. Never present an inferred value as extracted fact.

## 3. Two-Level Model

`series/spec_lock.md` contains only series-wide invariants. It is the authoritative lock.

`decks/DECK_ID/spec_lock.md` is a generated snapshot. It records the parent lock path/version/hash,
deck metadata, deck plan hash, override hash, export settings, and the inherited series lock.

Do not maintain two independent design systems. Regenerate the deck snapshot when its inputs
change.

## 4. Required Series Fields

Use Markdown with YAML frontmatter. Include:

- schema, scope, status, version, updated date;
- origin type, source name, audit file, and fidelity claim;
- canvas format, dimensions, and aspect ratio;
- mode and visual style;
- color roles;
- typography roles;
- grid, safe margins, columns, and spacing;
- layout families and their teaching purposes;
- image, table, chart, diagram, citation, page-number, and footer rules;
- fixed series invariants;
- allowed deck-level variation;
- prohibited patterns.

Do not include:

- a fixed page count;
- a chapter's page sequence;
- page-by-page rhythm;
- chapter-specific examples or content;
- a page-number mapping to a previous deck.

Put those in `analysis/deck_plan.md` or `analysis/deck_overrides.md`.

## 5. Lifecycle

Use:

```text
draft -> confirmed -> locked -> revised
```

- `draft`: extracted or proposed, not yet confirmed.
- `confirmed`: the user accepts the direction.
- `locked`: batch production has begun; do not change silently.
- `revised`: explicit change produced a new version.

Confirmation is a human gate. An agent may create a draft and continue only when the user's
request authorizes autonomous execution; it must not relabel the draft as confirmed.

## 6. Template Extraction

For a PPTX reference, extract facts from the entire package:

- canvas and aspect ratio;
- themes, color roles, and font families;
- masters, layouts, placeholders, and usage frequency;
- title placement and recurring geometry;
- page-type candidates;
- image/media inventory;
- table/chart presence;
- repeated header, footer, logo, page number, and decorative motifs.

`audit_template.py` creates the package-wide factual intake. It does not complete the visual
interpretation by itself. Before confirming or locking the series, inspect rendered slides or the
original deck and fill the draft fields for visual style, layout-family mapping, recurring
elements, crop behavior, density, and teaching suitability. Call the result a complete template
design extraction only after both factual intake and visual interpretation are finished.

Keep both:

- the generated lock, for cross-deck rules;
- the source PPTX, for exact master/layout and asset reuse.

For screenshots, mark fidelity as `visual-approximation`. Do not claim preservation of masters,
animations, hidden slides, notes, or native charts.

## 7. Change Control

When content does not fit:

1. select another approved layout;
2. split the content;
3. add a page;
4. use a deck-only override;
5. revise the series lock only when the user explicitly changes the series identity.

Archive prior locked versions under `series/history/`.
