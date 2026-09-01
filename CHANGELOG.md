# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- Added independent page-count evidence and content-first planning for every new deck.
- Added structural reuse detection for suspicious page-for-page series copies.
- Added seven aesthetic scenes, fourteen direction records, hard exclusions, seeded uniform
  selection, and human-approval gating.

### Changed

- Deck-level design snapshots no longer embed deck plans or page-by-page structure.

## [0.2.0] - 2026-08-08

### Added

- Renamed the installable Skill to `build-ppt-series` for teaching, technical, and business decks.
- Added deck-wide visual planning, one broad candidate search pass, and just-in-time illustration
  generation with user/source images taking priority.
- Added image capability preflight, structured briefs and prompts, two-attempt generation records,
  failure placeholders, provenance checks, and visual asset validation.
- Added Codex and Claude Code backend rules without making PPT Master a universal dependency.
- Added a validated 12-slide NL2SQL Agent showcase with generated illustrations and source records.
- Added nine visual-workflow tests and bilingual README navigation.

### Changed

- Moved to the reusable series project layout and separated `spec_lock` from per-deck planning.
- Kept generated showcase media under version control while excluding reproducible QA caches.

## [0.1.0] - 2026-08-03

### Added

- Initial public release of the teaching-deck skill.
- Series-based project structure with portable `spec_lock` templates.
- Template audit, environment detection, export routing, PPTX/SVG validation, and deck-spec synchronization scripts.
- Public documentation, contribution guidance, licensing, and a Chinese user guide.

### Notes

- Final editable-PPTX production depends on an agent host or separately configured backend.
- No course materials, reference templates, fonts, or third-party media are included.
