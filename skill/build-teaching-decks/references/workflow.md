# Teaching Deck Workflow

## Contents

1. Intent and routes
2. Inputs
3. Project lifecycle
4. Instructional planning
5. Series variation
6. Existing-deck changes
7. Continuation and delivery

## 1. Intent and Routes

Use one unified workflow with four internal routes:

| Route | Trigger | Design source |
|---|---|---|
| New style | No reference deck | User direction or context-derived draft |
| Template-derived series | Reference PPTX or screenshots | Full-deck audit plus retained reference |
| Existing lock | A `spec_lock.md` is supplied | Validated supplied lock |
| Existing-deck improvement | A deck must be beautified or restructured | Existing deck plus change request |

Template extraction is an internal stage of template-derived generation. Treat it as a standalone
task only when the user explicitly asks to create a reusable template without generating a deck.

## 2. Inputs

Inspect attachments before asking questions. Useful inputs include:

- lesson plan, syllabus, outline, textbook, paper, dataset, or source deck;
- reference PPTX, screenshots, brand guide, logo, or existing `spec_lock.md`;
- target learners, teaching setting, duration, page count, language, and delivery mode;
- required diagrams, textbook images, exercises, assessment, notes, or citations.

Ask only for information that cannot be inferred and materially blocks progress. If the user is
new or asks to be guided, collect inputs in this order:

1. New deck, same-series deck, or improvement?
2. Source materials and any reference deck.
3. Audience and teaching situation.
4. Duration/page range and required outputs.
5. Image, notes, citation, and editability requirements.

## 3. Project Lifecycle

1. Initialize or discover the series root.
2. Retain immutable sources under `series/template/` or the deck's `sources/`.
3. Resolve a series lock:
   - validate a supplied lock;
   - audit a reference PPTX and draft one;
   - derive one from explicit user direction;
   - otherwise derive a reasonable draft from the teaching context.
4. Create the current deck directory.
5. Build the deck plan and deck-only overrides.
6. Confirm the deck plan has populated audience, context, source scope, and page rows.
7. Generate a deck-level lock snapshot. Use `--allow-incomplete` only for a clearly labeled
   non-production scaffold.
8. Produce slides and notes through the selected artifact backend.
9. Run backend-appropriate source validation, export, validate PPTX, render, and visually
   inspect. SVG validation applies only to an SVG-producing route.
10. Deliver verified artifacts and preserve recoverable intermediates.

Do not treat a missing lock as a reason to stop. Generate a draft. Do not treat the presence of a
lock as permission to clone the previous deck's page sequence.

## 4. Instructional Planning

Each planned slide needs:

- a teaching purpose;
- a key message;
- learner prerequisites;
- source/evidence;
- content type such as definition, worked example, procedure, comparison, practice, diagnosis,
  assessment, or summary;
- visual role;
- density rhythm: `anchor`, `breathing`, or `dense`;
- acceptance condition: what learners should be able to identify, explain, perform, or judge.

For beginner and vocational learners:

- define terms before strategy;
- explain why a step matters before parameter tuning;
- show correct and incorrect examples;
- include operational steps and troubleshooting;
- define OK/NG criteria;
- retain difficult content and split it across pages when necessary;
- use tasks that can be performed and checked in class.

## 5. Series Variation

Keep these stable across a series:

- canvas, palette roles, typography roles, safe margins, recurring chrome;
- visual treatment for images, tables, diagrams, charts, citations, and page numbers;
- layout families and their intended teaching functions.

Recompute these for every deck:

- page count and page sequence;
- deck rhythm;
- examples, images, and exercises;
- layout selection and template frame mapping;
- chapter-specific overrides.

Never encode `deck 2 page 5 = deck 1 page 5`. Select layouts by teaching function and content
shape. A series must look related without becoming a text-swapped clone.

## 6. Existing-Deck Changes

Classify the request:

- **Beautify**: page count, order, wording, and data remain unchanged. Improve visual execution.
- **Restructure**: split, merge, reorder, add, delete, or rewrite content. Re-enter planning.
- **Same-series extension**: preserve the design system but create a new deck plan.

For existing files, retain the original and export a new version. Do not overwrite the source.

## 7. Continuation and Delivery

Retain `sources/`, `images/`, `analysis/`, `svg_output/`, `notes/`, `exports/`, and `backup/`.
Temporary render caches may be regenerated and need not be retained.

On resume:

1. Read the series manifest and lock.
2. Read the current deck plan, overrides, and snapshot hashes.
3. Inspect existing SVG/output status.
4. Continue from the first incomplete quality gate.

On delivery, report verified facts and unverified limits separately.
