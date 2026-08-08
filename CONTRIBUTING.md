# Contributing

Thank you for improving Build PPT Series.

## Before opening an issue

- Remove confidential material, learner data, credentials, and copyrighted templates.
- State the host agent, operating system, Python version, presentation backend, and image backend.
- Include the smallest reproducible input and the exact command or prompt.

## Pull requests

1. Keep changes scoped to one workflow, script, preset, or documentation improvement.
2. Preserve the distinction between series-wide `spec_lock` rules and deck-specific plans.
3. Preserve the visual priority order and never silently replace user-provided images.
4. Do not add non-redistributable fonts, templates, images, or source material.
5. Run the validation commands below and report host-specific limitations.

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py skill/build-ppt-series
python3 -m unittest discover -s skill/build-ppt-series/tests -v
python3 -m compileall -q skill/build-ppt-series/scripts
```

## Versioning

Use semantic versions. Breaking changes to the Skill layout, required inputs, or `spec_lock`
format require a major-version increase.
