# Codex Rules

Apply these additional rules when the executor is Codex.

1. Inspect the workspace and attachments before proposing a design or asking questions.
2. Read and use the host `Presentations` skill as the default authoring, template-following,
   export, rendering, and visual-QA backend. Do not ask the user to install PPT Master when
   `Presentations` is available.
3. Treat this Skill as the teaching/series orchestration layer and `Presentations` as the
   artifact implementation layer. The series `spec_lock`, deck plan, and retained sources still
   belong to this Skill.
4. Use `scripts/export_deck.py` only when `Presentations` is unavailable or the user explicitly
   requests the raster/PPT-Master compatibility route.
5. Read other presentation/document skill instructions available in the current runtime before
   using their tools. Use the host's bundled workspace dependencies when provided.
6. Derive every path from the current workspace, the skill root, arguments, or environment
   variables. Never use the skill author's personal paths.
7. Inspect `git status` and relevant diffs before edits. Preserve unrelated user changes and
   never revert or overwrite them.
8. Use `python3`. Detect dependencies before installing anything. Request approval only when an
   installation or external access is actually necessary.
9. Use the bundled deterministic scripts for project creation, template audit, lock snapshots,
   SVG checks, and PPTX checks instead of rewriting them ad hoc. Follow `Presentations` for its
   required implementation and QA tools.
10. Keep user-facing deliverables in the workspace's designated output directory. Keep temporary
   renders and scratch data outside the deliverable folder.
11. Preserve source files. Create versioned outputs and backups; do not destructively edit the
   original PPTX, reference template, or locked specification.
12. Send short progress updates during substantial work and continue through implementation,
   validation, and delivery unless the user pauses the task.
13. Do not stop at a plan when the user asked for a deck or a modification. Produce and verify
    the artifact.
14. Do not claim visual QA without rendering and inspecting slides. Name unavailable checks as
    unverified.
15. Do not claim object-level editability unless the selected backend produced native editable
    elements and that capability was verified.
16. For long or series decks, preserve `analysis/` plus the editable source and QA artifacts
    required by `Presentations`. Preserve `svg_output/` when the selected route produces SVG.
17. Before the final response, re-read the newest user request, validate the final artifact, and
    report exact paths, tests, and limitations.
