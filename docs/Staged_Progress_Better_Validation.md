# Project Foreman — Staged Progress Better Validation

Branch: `feature/staged-progress-better`

## Accepted direction

Advance the Good activity indicator into a truthful staged progress mechanism without changing the evidence policy, external dependency boundary, public website, demonstration video, or nine-file export contract.

## Recovery stages

1. Load sanitized fixture
2. Verify source evidence
3. Assemble Project Spine
4. Build Authority Ledger
5. Resolve continuation state
6. Apply evidence boundary

## Export stages

1. Prepare export workspace
2. Collect recovered artifacts
3. Generate Markdown views
4. Build manifest and checksums
5. Create ZIP archive
6. Validate final package

Each stage emits `RUNNING`, then `PASS` or `FAIL`, from the backend at the point where the corresponding work actually occurs. The browser percentage is calculated only from completed stages. No ETA or time-based simulated percentage is generated.

## Transport and interface

- Standard-library NDJSON streaming over `/api/recover/stream` and `/api/export/stream`
- Existing non-streaming endpoints remain available
- Determinate stage bar with accessible value text
- Per-stage pending, running, complete, and failed states
- Collapsible operator log
- Existing elapsed timer, action lock, error recovery, and reduced-motion behavior retained

## Validation performed before branch filing

- `python -m py_compile project_foreman/evidence_bound_server.py` — PASS
- `node --check project_foreman/static_evidence/app.js` — PASS
- Recovery fixture exercise — 6 of 6 stages emitted `PASS`
- Export exercise in a temporary destination — 6 of 6 stages emitted `PASS`
- Export archive validation — 9 files, `ZipFile.testzip()` returned no failed member
- Branch comparison — directly ahead of current `main`, behind by zero commits

## Package boundary

The feature preserves the current evidence-bound package:

- five governed JSON artifacts, including `Evidence_Boundary.json`
- two Markdown views
- `Manifest.json`
- `CHECKSUMS.sha256`
- nine files total inside the validated ZIP

No status receipt or additional export artifact is added at the Better level.

## Merge boundary

Implementation and pull-request review are authorized. Merge requires separate operator acceptance.
