# Quality Gates

## Contents

1. Source and plan
2. Lock
3. SVG
4. Export
5. PPTX package
6. Visual review
7. Delivery report

## 1. Source and Plan

- Confirm the teaching range and source hierarchy.
- Trace each factual slide to a source or mark it as instructional synthesis.
- Check audience, duration, outcomes, exercises, and assessment.
- Ensure difficult content is explained rather than omitted.

## 2. Lock

- Confirm series and deck scopes are separated.
- Confirm the snapshot hash matches the current series lock and plan.
- Confirm a locked series specification was not changed silently.
- Confirm the original template remains unchanged.

## 3. SVG

Apply this gate only when the selected backend produces SVG source slides. For the Codex
`Presentations` route, use the source and layout checks required by that host skill instead.

Run:

```bash
python3 scripts/validate_svg.py DECK/svg_output \
  --spec-lock DECK/spec_lock.md \
  --report DECK/analysis/svg-validation.json
```

Require:

- valid XML and SVG roots;
- zero-padded, unique, contiguous sequence numbers;
- lexicographic order equal to numeric order;
- no missing local image references;
- no unsupported `foreignObject`;
- no obvious canvas overflow;
- no unexplained color drift from the lock.

Warnings require review. Errors block export.

## 4. Export

- Record backend, editability class, source directory, slide count, and output path.
- Do not overwrite the source deck or a prior final export.
- If the backend refuses to overwrite, choose a new explicit output path.

## 5. PPTX Package

Run:

```bash
python3 scripts/validate_pptx.py OUTPUT.pptx \
  --report DECK/analysis/pptx-validation.json
```

Require:

- valid ZIP package;
- presentation relationship order resolves to every slide;
- no missing internal relationship targets;
- expected slide count;
- first and last titles/order match the plan;
- no obvious slide-shape bounds errors.

## 6. Visual Review

Render every slide when a renderer is available. Check:

- overlap, clipping, overflow, broken images, and blank slides;
- contrast, line wrapping, body size, and hierarchy;
- repeated-layout fatigue and deck rhythm;
- image crop, captions, source labels, and chart readability;
- correct/incorrect examples and classroom projection legibility.

Structural checks do not prove visual quality. If rendering is unavailable, state that clearly.

## 7. Delivery Report

Report:

- artifact paths;
- slide count;
- export backend and editability;
- structural checks passed;
- rendered pages inspected;
- warnings accepted;
- unverified items and remaining risk.
