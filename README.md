# DocGuardCLI

## Goal
Identify documentation drift in Python and Markdown files by comparing function names with markdown headings.

## Acceptance Criteria
1. Recursively scan directories for .py and .md files.
2. Parse Python docstrings and Markdown headings.
3. Identify undocumented functions that don't match markdown sections.

## Sprint Status
- Meetings held: 1/3
- Status: Active
- Next steps: Run acceptance tests and verify all criteria pass.

## Completed Work
- Implemented `docguard.py` with core scanning, parsing, and drift detection logic.
- Created `acceptance_tests.py` with robust mocking using `side_effect`.

## Known Bugs
- None currently. Tests are pending execution.

## Next Steps
- Execute acceptance tests.
- Verify CLI integration.
