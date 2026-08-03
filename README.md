# Build Teaching Decks

**Build Teaching Decks** is an agent skill for creating, extending, and quality-checking teaching PowerPoint decks. It is designed for a single deck or a reusable course-deck series, with a portable `spec_lock` that records the visual system without forcing every chapter into the same page sequence.

Version: **v0.1.0**

中文说明见 [README.zh-CN.md](README.zh-CN.md)。

## What it does

- Turn lesson plans, textbooks, outlines, Word/PDF files, or existing slides into a teaching-deck plan.
- Derive reusable design rules from a reference PowerPoint instead of copying slide order.
- Keep fonts, colour, grid, and component rules stable across a course series.
- Separate series-wide design rules from chapter-specific content and pacing.
- Audit templates and validate PPTX/SVG output before delivery.

## Repository layout

```text
skill/build-teaching-decks/   Installable skill package
docs/                        User documentation
```

The installable package intentionally contains only the skill instructions, scripts, templates, and references. Repository-level documents support public use and contribution.

## Install

Copy the directory `skill/build-teaching-decks` into the skills location used by your agent host, then enable or reload skills according to that host's documentation. The skill's invocation name is:

```text
$build-teaching-decks
```

For a packaged release, use the `build-teaching-decks-skill-v0.1.0.zip` asset, which contains that directory only.

## Quick start

```text
Use $build-teaching-decks to create a 30-slide teaching deck from the uploaded lesson plan.
The students are first-year vocational learners. Preserve technical terms and check every slide for readability.
```

With a reference template:

```text
Use $build-teaching-decks to create a teaching deck from the new materials and this reference PPTX.
Keep the template's visual system, but redesign the teaching sequence for the new content.
```

## Compatibility and output

The skill includes planning, template-audit, series-management, and validation utilities written for Python 3 with the standard library. Final PPTX production depends on the capabilities supplied by the host agent:

| Host capability | Result |
| --- | --- |
| Native editable PPTX authoring | Editable PPTX workflow |
| SVG-to-PPTX backend | Editable workflow when that backend supports it |
| Raster-only export | PowerPoint output may contain non-editable raster slides |
| No presentation backend | Planning, audit, and validation only |

`Presentations` and `PPT Master` are optional host/back-end integrations. They are not bundled with this repository or installed by it.

## Quality checks

From `skill/build-teaching-decks`, run the relevant checks before release:

```bash
python3 scripts/environment_check.py --executor generic
python3 scripts/validate_pptx.py path/to/output.pptx
python3 scripts/validate_svg.py path/to/svg_output
```

See the [Chinese user guide](docs/使用指南.md) for workflows, prompt examples, and known limits.

## Responsible use

Do not commit textbooks, third-party slide templates, logos, fonts, learner data, or images unless you have the right to redistribute them. Verify technical figures, formulas, labels, units, and sources before classroom use.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). By contributing, you agree that your contributions are licensed under [Apache-2.0](LICENSE).

