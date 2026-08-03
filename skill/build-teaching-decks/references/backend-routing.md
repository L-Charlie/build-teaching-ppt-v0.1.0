# Export Backend Routing

## Contents

1. Executor detection
2. Capability classes
3. Selection order
4. Claude Code editable export
5. Portable fallback
6. Dependency behavior

## 1. Executor Detection

Run this before selecting an export route:

```bash
python3 scripts/environment_check.py
```

Detection may be overridden when necessary:

```bash
TEACHING_DECK_EXECUTOR=claude-code python3 scripts/environment_check.py
python3 scripts/environment_check.py --executor codex
```

The supported executor values are `codex`, `claude-code`, and `generic`. Automatic detection is
advisory; the active agent must also inspect the capabilities exposed by its host.

## 2. Capability Classes

Classify the result before export:

- `editable-native`: SVG elements become native DrawingML shapes.
- `editable-template`: content is filled into native PPTX layouts/placeholders.
- `editable-runtime`: the host presentation tool creates native shapes.
- `raster-fallback`: each slide is a full-slide image.

Never describe a raster fallback as editable.

## 3. Selection Order

Choose the first backend that satisfies the request:

1. In Codex, the host `Presentations` skill/runtime.
2. In another host, a verified presentation runtime with native editing and rendering.
3. In Claude Code, a separately installed PPT Master or another verified native PPTX backend.
4. The bundled raster fallback, only when editability is not required or the user accepts it.

Run:

```bash
python3 scripts/environment_check.py
```

In Codex, follow the host `Presentations` skill instead of calling `export_deck.py` automatically.
In Claude Code or a generic executor, use:

```bash
python3 scripts/export_deck.py PROJECT -o OUTPUT.pptx --backend auto
```

Add `--require-editable` when the output must remain editable.

## 4. Claude Code Editable Export

PPT Master is not required for the teaching workflow, template audit, lock, planning, SVG
generation, or validation. It is an optional companion backend for native editable SVG-to-PPTX
export in Claude Code. When it is installed, set:

```text
PPT_MASTER_ROOT=/path/to/ppt-master
```

`export_deck.py` also checks common user skill directories. It invokes the installed
`scripts/svg_to_pptx.py` without assuming a personal absolute path.

If Claude Code has no verified native backend and editability is required, explain that before
slide production. Offer three choices: install/configure PPT Master, configure another native
backend, or change the output requirement. Do not imply that this Skill installs PPT Master.

Treat PPT Master as an optional execution backend, not the owner of `spec_lock`.

## 5. Portable Fallback

The bundled fallback:

1. renders each SVG to PNG with CairoSVG, Inkscape, `rsvg-convert`, or svglib/reportlab;
2. creates a 16:9 or source-sized PPTX with one full-slide image per page;
3. writes an adjacent export manifest declaring `editable: false`.

Use it only when the quality tradeoff is acceptable. It preserves appearance better than a weak
partial SVG-to-shape implementation, but does not preserve object-level editability.

## 6. Dependency Behavior

Do not install dependencies preemptively. Detect first.

Minimum for template audit, project setup, snapshot generation, and package validation:

```text
Python 3.10+ standard library
```

Portable raster export requires:

```text
python-pptx
one SVG renderer: cairosvg, inkscape, rsvg-convert, or svglib+reportlab
```

Rendering/visual QA may use LibreOffice or a host presentation renderer. If unavailable, report
visual QA as pending rather than calling the deck defective.
