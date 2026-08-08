# PPT Series Workflow

## Routes

| Route | Trigger | Series design source |
|---|---|---|
| New style | No approved reference | Purpose, audience, profile, and style request |
| Template-derived | Reference PPTX or screenshots | Full template audit plus retained source |
| Existing lock | Valid `spec_lock.md` supplied | Validated supplied lock |
| Existing deck improvement | A deck is being revised | Existing deck plus requested change boundary |

Beautification preserves page count, order, wording, and data. Any split, merge, reorder, addition,
or deletion is a reconstruction and requires a new deck plan.

## Profiles

- `general`: neutral reusable presentation workflow;
- `teaching`: lesson plans, textbooks, learner level, teaching range, exercises, and notes;
- `technical`: mechanisms, architecture, code, procedures, constraints, and evidence;
- `business`: decisions, metrics, narrative, recommendations, and actions.

Profiles add constraints; they do not replace the common series, source, visual, and QA contracts.

## Intake

Inspect attachments before asking questions. Determine:

- required output and whether this is one deck or a continuing series;
- purpose, audience, context, duration or page range, language, and profile;
- source hierarchy and exact allowed scope;
- reference deck, screenshots, brand guide, logo, or existing lock;
- desired editability, notes, citations, diagrams, charts, exercises, or visual style.

Ask only for missing blocking inputs. If the user wants guidance or provides files without a task,
offer a short route choice. Any conflict between user material, factual sources, and the template is
presented to the user for decision.

## Environment And Project

1. Run `environment_check.py`, explicitly declaring the host image backend.
2. Resolve the presentation backend before promising editability.
3. Initialize or reuse the series root with `init_series.py`.
4. Retain original templates and sources; never overwrite them.
5. Keep intermediate analysis and editable sources so work can resume across sessions.

## Series Lock

Resolve `series/spec_lock.md` before bulk production. Priority:

1. supplied lock;
2. full reference-deck extraction;
3. explicit user design request;
4. context-derived draft.

The lock stores only series invariants. The deck plan stores page count, sequence, communication
rhythm, source mapping, and current visual tasks. A confirmed first deck may become an approved
reference, but later decks still receive new plans and layout mappings.

## Deck And Visual Planning

Write `analysis/deck_plan.md` with one row per page: purpose, content, source, density, layout,
visual need, route, risk, and scene profile. For the teaching profile, difficult in-scope material
is expanded or split rather than omitted or made unreadably small.

Write `analysis/visual_asset_plan.json` and follow `visual-assets.md`:

1. classify visual need without imposing an image quota;
2. reuse user and source assets first;
3. perform one task-oriented search pass after the plan is stable;
4. determine frames and aspect ratios;
5. declare image capability and run visual preflight;
6. generate only when implementing the relevant slide;
7. retain accepted assets, briefs, prompts, records, provenance, and exceptions.

Run `sync_deck_spec.py` only after the plan and deck overrides are sufficiently complete.

## Production

Implement through the selected backend. Recompute layout selection by page function and content
shape. Do not copy the previous deck's page sequence or mechanically map page N to page N.

Use stable page dimensions and safe margins. Keep text, labels, arrows, and citations editable.
Respect the visual budget as a cap. In guided mode, use the first generated slide as the style
checkpoint. Stop only for material conflicts or required approval; otherwise log routine choices.

For an SVG route, use zero-padded page names, validate SVG and local references, then export with a
verified native backend. Raster fallback is non-editable and requires explicit acceptance.

## Validation And Delivery

Run all applicable gates:

- source/content and profile-specific checks;
- lock consistency and template fidelity;
- visual asset plan, risk, provenance, generation record, and placeholder checks;
- SVG/PPTX package structure and page order;
- rendered visual inspection for overflow, crop, overlap, contrast, and blank pages.

Retain `sources/`, `images/`, `analysis/`, `svg_output/`, `notes/`, `exports/`, and `backup/`.
Temporary rendering caches may be discarded. Deliver the deck plus a report that clearly separates
verified results, unavailable checks, and unresolved visual exceptions.
