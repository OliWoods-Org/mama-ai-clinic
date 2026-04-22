# Contributing to MAMA AI Clinic

Thank you for your interest in contributing to humanitarian AI infrastructure.

## Who We Need

- **Clinicians** -- Review IMNCI decision trees and dosing tables for accuracy
- **Developers** -- Improve the web app, inference pipeline, and deployment tools
- **Translators** -- Add new languages for field deployment
- **Field Workers** -- Test in real settings and file feedback
- **Hardware Engineers** -- Optimize power consumption, improve case design

## How to Contribute

1. **File a field report** if you've deployed this in the field -- use the Field Report issue template
2. **Review clinical content** -- any clinician can review `app/knowledge/` JSON files
3. **Submit code** -- fork, branch, PR. All PRs must pass CI including safety eval.
4. **Translate** -- see `docs/LOCALIZATION.md` for how to add a language

## Safety-Critical Code

The triage engine (`app/services/triage_engine.py`) and dosing engine (`app/services/dosing_engine.py`) are safety-critical. Changes to these files require:

1. Clinical justification in the PR description
2. All existing tests passing
3. New test cases for any new classification logic
4. Safety evaluation passing (zero red-line failures)

## Code Style

- Python: standard library conventions, type hints where helpful
- HTML/CSS/JS: no frameworks, no build step, mobile-first
- Keep it simple -- this runs on a $35 computer in a village

## License

By contributing, you agree that your contributions will be licensed under Apache 2.0.
