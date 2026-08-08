# Claude Code Rules

1. Detect a native presentation backend before promising editable PPTX output.
2. PPT Master is optional for planning, source inspection, template audit, `spec_lock`, visual
   planning, and validation. It is required only for this package's bundled editable SVG conversion
   route unless another verified native backend is configured.
3. If no native backend exists, explain the choices before production: configure PPT Master,
   configure another backend, change the output requirement, or explicitly accept raster output.
4. Detect or configure an image-generation capability before slide layout when the visual plan has
   generated tasks. If none exists, declare it unavailable; do not discover the problem halfway
   through the deck.
5. Keep image integration provider-neutral. Do not assume a model, command, API key, or vendor.
6. Follow the same source priority, risk, prompt, two-attempt, placeholder, and exception contract
   as every other executor.
7. Do not imply that installing this Skill also installs PPT Master or an image provider.
8. Record backend names, editability, rendering method, and checks actually completed.
