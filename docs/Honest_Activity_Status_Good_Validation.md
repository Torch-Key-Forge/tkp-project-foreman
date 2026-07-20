# Project Foreman — Honest Activity Status Good Validation

Branch: `feature/honest-activity-status-good`

## Scope

This bounded interface enhancement adds truthful activity feedback for Load Fixture, Recover Project, and Export Package without changing the backend, API routes, evidence policy, or export package.

## State model

- `IDLE`
- `RUNNING`
- `PASS`
- `FAIL`

The activity strip is indeterminate. It does not claim percentage completion or an estimated time remaining.

## Operator safeguards

- Load, Recover, and Export controls are locked while an operation is running.
- Elapsed time is displayed from operation start.
- Failures preserve a visible error state and permit retry after controls are restored.
- The status region uses `role="status"`, polite live announcements, and `aria-busy`.
- Reduced-motion preferences disable the moving animation.

## Validation

- `node --check project_foreman/static_evidence/app.js` — PASS
- `python -m unittest discover -s tests -p test_honest_activity_status.py -v` — 7 tests PASS
- Static regression coverage confirms existing `/api/fixture`, `/api/recover`, and `/api/export` routes remain in use.
- Dynamic `result.file_count` handling remains intact.

## Export-contract note

The accepted evidence-bound build on `main` currently exports nine files because `Evidence_Boundary.json` was added by PR #5. The authorization wording referred to an eight-file contract from the earlier build. This enhancement changes neither contract nor package contents; it preserves the current nine-file evidence-bound export exactly as found.

## Merge boundary

Implementation and pull-request review are authorized. Merge remains subject to separate operator acceptance.
