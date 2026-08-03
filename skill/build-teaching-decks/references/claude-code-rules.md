# Claude Code Rules

Apply these additional rules when the executor is Claude Code.

1. Run `python3 scripts/environment_check.py --executor claude-code` before promising an export
   format.
2. Do not require PPT Master for source inspection, template auditing, `spec_lock` creation,
   deck planning, SVG generation, or structural validation.
3. PPT Master is an optional companion backend for this Skill's native editable SVG-to-PPTX
   route. Detect it through `PPT_MASTER_ROOT` or the supported skill locations.
4. When PPT Master or another verified native PPTX backend is available, record the backend and
   use it for editable output.
5. When no native backend is available and the user requires editable slides, pause before
   slide production and explain the choices: install/configure PPT Master, configure another
   native PPTX backend, or change the requirement.
6. When the user accepts a non-editable result and the raster dependencies are available, use
   the bundled raster fallback and label the result `editable: false`.
7. Do not imply that installing the teaching-deck Skill also installs PPT Master. It is a
   separate optional dependency.
8. Derive paths from the workspace, arguments, environment variables, or the Skill directory.
   Never use paths from the Skill author's machine.
