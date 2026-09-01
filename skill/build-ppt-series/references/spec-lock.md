# `spec_lock` Contract

`spec_lock` is a portable series design contract owned by this Skill. It is independent of PPT
Master, Presentations, and any image provider.

## Sources And Priority

Resolve the lock from: supplied lock, full reference audit, explicit design request, or a
context-derived draft. A user without a lock can upload a reference PPTX and build a series. Retain
both the extracted lock and original reference because the lock does not replace real masters,
layouts, or reusable pages.

## Two Levels

`series/spec_lock.md` is the single authority for series invariants. It contains canvas, grid,
typography, color roles, layout families, template behavior, illustration system, citation/footer
rules, invariants, allowed variation, and change state.

`decks/DECK_ID/spec_lock.md` is a generated visual execution snapshot containing parent and input
hashes plus the inherited series lock. It references the current deck plan and overrides but never
embeds their content. Do not edit it directly and never use another deck's snapshot to structure a
new deck.

Never place current page count, page sequence, page-by-page rhythm, current examples, or current
visual tasks in the series lock.

## Aesthetic Calibration

For an unconstrained new series, an approved aesthetic reference set may help derive the first
lock. Store only the selected scene, reference-set ID, random seed, sampled reference-page IDs,
human-approval state, and calibration intent. Do not store or derive a page sequence, coordinate
map, fixed layout recipe, or page-to-reference mapping.

Templates, brand guides, explicit styles, and existing locks take priority and skip random
selection. Later decks reuse the confirmed lock without selecting another reference set.

## Illustration Layer

The lock defines a stable base illustration language and palette binding. It also defines allowed
scene profiles, continuity, reuse, disclosure, editable overlay, and prohibited-content rules.
Page-specific briefs select a scene profile and composition without changing the series identity.
The template remains the root visual constraint.

## Template Extraction

Audit the whole reference deck, not a favorite slide. Extract canvas and master relationships;
layout families and geometry; typography; color roles; image crop and treatment; charts, tables,
diagrams, logos, headers, footers, citations, density, and reusable elements. Record origin and
fidelity. Screenshots may produce a visual approximation but cannot claim exact master or animation
fidelity.

## State And Revision

Use `draft -> confirmed -> locked -> revised`. Never claim confirmation without user approval.
When a locked rule changes, archive the previous lock and increment the version. During batch
production, solve content pressure by selecting another layout or adding pages before changing the
series contract.

## Conflict Boundary

The user is the final decision maker when material, factual source, template fidelity, and explicit
style requests conflict. Routine composition choices remain automatic and are recorded in plans or
generation records.
