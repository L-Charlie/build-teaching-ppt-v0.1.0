# Build PPT Series

[简体中文](README.md) | [English](README.en.md)

`build-ppt-series` is a portable Agent Skill for creating a standalone presentation or a reusable
deck series from source material, reference PPTX files, brand guidance, or an existing `spec_lock`.
It turns planning, template constraints, visual decisions, just-in-time illustration generation,
export, and QA into a recoverable project instead of an opaque one-off file.

![NL2SQL Agent example montage](docs/showcase/nl2sql-agent-montage.png)

## Capabilities

- new-style, reference-template, existing-lock, and existing-deck improvement routes;
- separate series `spec_lock` and deck `deck_plan`, preserving identity without copying page order;
- independently derive each deck's page count and content structure before applying series visuals;
- detect suspicious same-count, same-position purpose and layout reuse;
- full reference-deck audit and retained source template;
- visual priority: user assets, source/template assets, licensed external assets, real screenshots,
  native diagrams, generated illustrations, then no visual;
- one broad search pass during planning, with generation delayed until the relevant slide is built;
- image-backend, aspect-ratio, risk, and budget preflight, with at most two automatic attempts;
- explicit illustration placeholders, prompts, and failure records when generation cannot complete;
- PPTX/SVG structural checks, provenance validation, full rendering, and per-slide visual QA.

The repository defines seven scenes, fourteen aesthetic directions, and hard-exclusion-then-uniform
selection. These references calibrate judgment about substance, hierarchy, and workplace usability;
they are not reusable layouts. Original reference pages have not yet completed production and human
review, so production selection rejects these unapproved sets instead of treating text directions
as templates.

## Backend Model

The Skill is **independent of PPT Master**. It owns the workflow, `spec_lock`, visual plan, and
quality gates, while an actual presentation backend is still required to author editable PPTX.

| Host | Default presentation backend | Image generation | PPT Master |
|---|---|---|---|
| Codex | host `Presentations` | host `imagegen` when available | not required |
| Claude Code | a configured native PPTX backend | configured equivalent | required only for this package's editable SVG route |
| Other agents | any verified native backend | optional | not required |

An unavailable image backend is acceptable when the visual plan has no generated tasks. A raster
full-slide fallback requires explicit user acceptance and must be reported as `editable: false`.

## Install

After cloning the repository, copy its Skill directory into the host's Skill directory, keeping
the folder name `build-ppt-series`. From the repository root, a typical Codex installation is:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skill/build-ppt-series "${CODEX_HOME:-$HOME/.codex}/skills/build-ppt-series"
```

Refresh the Skill list or start a new task, then invoke:

```text
Use $build-ppt-series to create a reusable presentation series from my source files.
```

## WSL Quick Check

Run the project scripts inside WSL. Codex may invoke its Windows-hosted Presentations runtime for
export and rendering; this split is expected.

```bash
python3 scripts/environment_check.py --executor codex --image-backend available
python3 scripts/init_series.py ./example-series \
  --series-name "Example Series" \
  --profile technical \
  --deck-id 01-introduction \
  --deck-title "Introduction"
```

Use `--image-backend unknown` when capability has not been confirmed, and do not promise generated
illustrations until preflight resolves it.

## Project Layout

```text
<series-root>/
  series/
    spec_lock.md
    template/
    shared-assets/
    history/
  decks/<deck-id>/
    spec_lock.md
    sources/
    images/{candidates,sourced,generated}/
    analysis/
      deck_plan.md
      visual_asset_plan.json
      image_briefs/
      generation_records/
    svg_output/
    notes/
    exports/
    backup/
```

The series lock contains only cross-deck invariants. Page sequence, content rhythm, and local
exceptions belong to each deck.

## End-to-End Example

The repository includes a 12-slide technical showcase built from a real local codebase:
[`NL2SQL Agent: From Natural Language to Trustworthy SQL`](examples/nl2sql-agent-showcase/decks/01-overview/exports/NL2SQL_Agent_Overview.pptx).

![Cover](docs/showcase/nl2sql-agent-cover.png)

![Editable architecture slide](docs/showcase/nl2sql-agent-architecture.png)

![Execution paths](docs/showcase/nl2sql-agent-execution.png)

The example uses two just-in-time generated conceptual illustrations, nine native editable visual
routes, and one text-only close. See the full [`ACCEPTANCE.md`](examples/nl2sql-agent-showcase/ACCEPTANCE.md).

## Acceptance Contract

Every delivery must report the actual backend, editability, slide count, structural checks,
rendered checks, visual-asset status, unresolved placeholders, and known limitations. Structural
validation never substitutes for rendering and inspecting every slide.

## License

Apache-2.0. See [LICENSE](LICENSE).
