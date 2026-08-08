# NL2SQL Agent Showcase Acceptance

## Scope

- Environment: WSL for project scripts and repository tests.
- Presentation backend: Codex Presentations with Artifact Tool export and rendering.
- Image backend: host imagegen.
- Output: 12-slide editable PPTX.
- Visual routes: 2 generated conceptual illustrations, 9 native editable visuals, 1 no-visual slide.

## Verified

| Check | Result |
|---|---|
| `build-ppt-series` visual workflow tests | 9 passed |
| Visual preflight | 12 tasks, 2 generated tasks, 0 errors, 0 warnings |
| Final visual asset validation | eligible-for-final, no placeholders |
| NL2SQL repository regression suite | 25 passed in 29.36s |
| PPTX structural validation | 12 slides, 2 media files, 0 warnings |
| PPTX package integrity | passed |
| Overflow test | passed; no content outside the slide canvas |
| Rendered visual inspection | all 12 slides inspected individually at 1280x720 |

Both generated assets have structured briefs, final prompts, SHA-256 hashes, provenance, and
generation records. `VIS-002` used the allowed second attempt after the first call returned no
workspace artifact.

## Editability

- Titles, body copy, tables, code blocks, status bands, architecture nodes, and connectors are
  native editable presentation objects.
- The two generated conceptual illustrations are raster images; their labels and captions remain
  editable PowerPoint elements.

## Not Verified

- No real model-provider call was run for the NL2SQL application.
- No BIRD benchmark was run.
- Generated illustrations are conceptual aids and are not treated as factual evidence.

## Deliverable

[`decks/01-overview/exports/NL2SQL_Agent_Overview.pptx`](decks/01-overview/exports/NL2SQL_Agent_Overview.pptx)
