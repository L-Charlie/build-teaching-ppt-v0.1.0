# Visual Asset Workflow

## Principle

Use a visual only when it improves comprehension, comparison, credibility, continuity, or recall.
Generated illustrations are explanatory aids, never factual evidence. A deck with zero generated
images can be fully successful.

## Decide Per Slide

Classify `visual_need` before layout:

- `required`: the message depends on a visual, such as a spatial relationship or source figure;
- `helpful`: a visual materially improves understanding but is not essential;
- `unnecessary`: typography, structure, or a native shape is clearer;
- `prohibited`: imagery would be misleading, unsafe, or outside the approved source range.

Then choose one route: `user`, `source`, `external`, `screenshot`, `native`, `generated`, or `none`.

## Source Priority

Use this order unless the user explicitly decides otherwise:

1. user-provided images;
2. source, textbook, or retained template images;
3. reliable, attributable, and licensed external images;
4. real screenshots;
5. native editable diagrams, charts, and tables;
6. generated illustrations;
7. no visual.

The series template and `spec_lock` govern treatment. If an image or style request conflicts with
the template or source material, stop and present the conflict to the user. Ordinary composition,
crop, and layout choices are automatic and logged.

## Plan, Search, Then Generate Just In Time

1. Complete the deck page plan and visual task list.
2. Perform one broad search pass organized by task. Do not fetch a fixed number per slide. Allocate
   more candidates to important or difficult tasks and keep no more than the configured valid
   candidate cap.
3. Reject candidates that are irrelevant, misleading, outside source range, low quality, or not
   legally usable. A task with no valid candidate routes to generation only when its risk and user
   policy allow it.
4. Candidate adaptation may crop, resize, remove a background, or adjust non-semantic color and
   exposure. If the required change alters meaning, reject the candidate and generate a new asset.
5. Determine the slide's frame, aspect ratio, subject position, and reserved whitespace first.
6. Generate only while implementing that slide. Do not pre-generate all assets.

Editing a user-provided image follows the same boundary: non-semantic transforms are automatic;
semantic or generative changes require explicit permission.

## Style And Scene Control

`series/spec_lock.md` defines the stable illustration language: palette binding, line or texture
quality, lighting, character treatment, and disclosure policy. Each image brief selects a
`scene_profile` appropriate to the page, for example conceptual, technical, narrative, business,
or teaching. A comic-like base style may be used, but it is one option, not a universal default.

Assign continuity IDs to recurring people, objects, products, or environments. Reuse an image only
for justified continuity, review, or series identity and record the reason. Shared style references
and explicitly reusable assets belong under `series/shared-assets/`; ordinary candidates and
generated outputs stay inside the deck.

## Structured Brief And Prompt

A visual-plan task uses this shape:

```json
{
  "asset_id": "VIS-007",
  "slide": 7,
  "purpose": "Explain the relationship without claiming evidence",
  "visual_need": "helpful",
  "route": "generated",
  "risk": "low",
  "scene_profile": "conceptual",
  "brief": "image_briefs/VIS-007.json",
  "status": "planned"
}
```

After selection, set `status` to `complete` and add `selected_asset`, `provenance`, and for generated
assets `generation_record`. Candidate, source, brief, prompt, and record paths are relative to the
`analysis/` directory unless absolute.

Create `analysis/image_briefs/ASSET_ID.json` from the supplied template. It must contain:

- purpose and subject;
- required visible facts or relationships;
- base style and scene profile;
- palette, continuity IDs, and factual basis;
- actual aspect ratio, placement, subject position, and reserved whitespace;
- risk, disclosure, and negative constraints.

Compile the provider-neutral prompt with `compile_image_prompt.py`. Never send raw slide text as a
prompt. Do not ask the image model to render educational labels, arrows, citations, logos, or
watermarks. Add those as editable presentation elements.

## Risk Rules

- `low`: decorative or conceptual. Visual QA is sufficient.
- `medium`: source-grounded mechanism, process, or scenario. Check every required visual fact
  against the listed source before acceptance.
- `high`: evidence-like medical, legal, safety, financial, historical, scientific, product, or
  documentary content where a synthetic visual could mislead. Free generation is prohibited unless
  the user explicitly approves a schematic representation and visible disclosure.

Every generated asset keeps provenance. Visible disclosure is required only when a reasonable
viewer could mistake it for real evidence, or when the approved high-risk schematic rule applies.

## Capability And Approval

After the full visual plan, declare the image backend as `available`, `unavailable`, or `unknown`
and run `visual_preflight.py` before slide layout. Host tools must be declared by the agent because
the local script cannot inspect them. The first actual generation verifies that the backend works.

Default new-series mode is `guided`: the first real generated slide is shown as the illustration
style checkpoint. `automatic` mode is allowed only after explicit permission for uninterrupted
production. Material conflicts always stop in either mode.

## Attempts And Failure

Use at most two automatic generation or edit attempts per asset. Save the accepted image,
structured brief, compiled prompt, provider-neutral generation record, and optional file hash.
Do not retain failed image files by default; retain failure reasons.

A generation record contains `asset_id`, `backend`, `prompt` or `prompt_path`, one or two `attempts`,
accepted output path, provenance, and optional SHA-256. It must not contain API keys or tokens.

If both attempts fail:

1. continue the remaining deck;
2. place a simple frame containing `插图待补充` and the asset ID;
3. add an item to `analysis/visual_exceptions.json` containing slide, asset ID, brief path, full
   prompt path or text, negative constraints, attempts, and failure reasons;
4. mark the deck `draft/review`, never final;
5. at delivery, ask whether the user wants a retry or will provide an image.

## Acceptance

Judge route correctness and asset quality, not image count. Validate that each visual serves its
declared purpose, respects the source and template, uses the correct aspect ratio, has provenance,
and avoids misleading content. Validate the rendered slide separately for crop, overlap, contrast,
and legibility.
