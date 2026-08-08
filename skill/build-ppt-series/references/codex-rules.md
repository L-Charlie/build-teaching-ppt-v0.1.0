# Codex Rules

1. Use the host `Presentations` capability for PPTX creation, editing, rendering, and deck QA when
   it is exposed. Do not ask for PPT Master in that case.
2. Treat this Skill as the series orchestration layer. Keep its `spec_lock`, deck plan, visual plan,
   sources, and exception records even when `Presentations` owns artifact implementation.
3. Inspect the host capability list before production. If `imagegen` is exposed, declare
   `--image-backend available`; otherwise declare `unavailable` or `unknown` honestly.
4. Use `imagegen` only for tasks routed to `generated` after user/source/search/native options were
   considered. Generate just in time at the planned aspect ratio.
5. Inspect an existing local image before editing it. Non-semantic adaptation may proceed;
   semantic or generative edits to a user image require permission.
6. Compile prompts from structured image briefs. Keep labels, arrows, citations, and explanatory
   text editable in the slide.
7. Use the first actual generated slide as the style checkpoint in guided mode. Explicit automatic
   mode may continue without checkpoint, but material conflicts always return to the user.
8. Save accepted generated assets and their records under the deck. Do not claim that a bitmap is
   an editable vector object.
9. Complete both structural and rendered QA. A successful PPTX save is not visual verification.
10. Report unresolved `插图待补充` placeholders as draft/review output with the exact recovery
    information required by `visual-assets.md`.
