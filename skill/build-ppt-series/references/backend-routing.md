# Backend Routing

The workflow is independent of PPT Master. `spec_lock`, planning, sourcing, illustration policy,
and validation belong to this Skill. Presentation and image tools are replaceable execution
backends.

## Executor Override

Use `PPT_SERIES_EXECUTOR=codex|claude-code|generic` or `--executor`. The legacy
`TEACHING_DECK_EXECUTOR` variable is accepted for compatibility. When both are set, the new variable
wins.

## Presentation Backend

- Codex with host `Presentations`: use it for editable authoring, export, rendering, and visual QA.
- Claude Code with PPT Master or another verified native backend: use that backend and record it.
- Generic host with a verified native backend: use it and document editability.
- Raster fallback: only after explicit acceptance; each slide is an image and the report must state
  `editable: false`.

Claude Code does not need PPT Master for planning or lock creation. It needs PPT Master only for
this package's bundled native editable SVG-to-PPTX path. Do not imply that installing this Skill
installs PPT Master.

## Image Backend

Image generation is optional and provider-neutral. The agent declares `available`, `unavailable`,
or `unknown` during environment check. Codex uses host `imagegen` when available. Claude Code uses
an explicitly configured equivalent. Do not embed provider keys, fixed model names, or commercial
API setup in this open-source package.

If the visual plan contains generated tasks and the backend is not available, resolve the issue
before slide layout. A deck with no generated tasks may proceed normally with an unavailable image
backend.

## Editability Contract

Record the actual artifact route, not assumptions based on executor name:

- native objects, template reuse, or editable vector conversion: state what remains editable;
- raster full-slide fallback: `editable: false`;
- generated bitmap illustration inside an otherwise editable deck: the image itself is bitmap,
  while labels and slide composition remain editable.
