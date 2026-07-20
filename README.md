# Project Foreman

**Recover valuable work trapped inside long AI conversations.**

Project Foreman converts a long, messy AI conversation into a traceable project workspace.

Current accepted release: **v0.2.0 — Better Staged Progress**.

It produces:

- a navigable Project Spine;
- a verified Decision and Authority Ledger;
- a Continuation Brief showing where work stopped;
- a Source Trace Index linking recovered claims to exact conversation turns;
- a portable Markdown and JSON project package with manifests and checksums.

## Why It Exists

AI conversations increasingly contain serious project work: decisions, requirements, failures, corrections, artifacts, and open questions.

The problem is that raw conversation history is difficult to navigate, verify, resume, or transfer. Conventional summarization compresses the text but often loses authority, provenance, and project state.

Project Foreman treats the conversation as a project record rather than a block of prose.

## Demonstration

**Public Build Week demonstration:** [Watch Project Foreman on YouTube](https://youtu.be/3KQ_LBIXUQc) — 2 minutes 57 seconds.

The included Atlas Workshop fixture is a compact hybrid synthetic conversation modeled on real project behavior.

The live demonstration shows:

1. loading the fixture;
2. reconstructing the Project Spine;
3. separating operator commands from assistant proposals;
4. identifying the last trustworthy state and unresolved work;
5. tracing a recovered claim to its exact source turn;
6. exporting a validated structured package.

The private validation corpus is not included. The underlying pipeline was tested against 328 conversations containing 29,345 turns.

## Trust Model

Project Foreman follows several strict boundaries:

- assistant statements are not operator authority;
- issuing a command does not prove the work was completed;
- natural-language authority candidates remain provisional until reviewed;
- recovered claims retain exact source references;
- source content is read-only;
- exported packages include manifests and SHA-256 checksums.

## Evidence Boundary

Project Foreman packets operate in **evidence-bound mode**:

- `CANONICAL_PROJECT_EVIDENCE` supports claims with included packet evidence and exact source references;
- candidate interpretations remain `PROVISIONAL_REVIEW` and are `HELD_FOR_REVIEW`;
- unresolved matters remain `UNRESOLVED`;
- absent required evidence is marked `SOURCE_UNAVAILABLE`;
- assistant authority promotion is `NONE`;
- execution and completion without evidence remain `NOT_INFERRED`;
- promotion requires `OPERATOR_REVIEW_REQUIRED`.

The public rule is simple: **No source, no claim.**

When a claim is unsupported, Project Foreman fails closed:

> This claim is not established in the imported project evidence.

An inference may be offered only when clearly labeled `PROVISIONAL_INFERENCE`. It remains non-authoritative until operator review.

## Included Build

The competition build is a local, read-only Python application using only the Python standard library.

Recovery and export display truthful stage progress produced by the work itself. The interface reports six recovery stages and six export stages, marks only completed stages as complete, and does not invent an ETA or time-based percentage.

Requirements:

- Python 3.11 or later;
- Windows 10 or later for the provided launchers;
- no network connection after download;
- no external Python packages.

## Launch

After downloading:

1. Right-click the ZIP.
2. Choose `Properties`.
3. Select `Unblock`.
4. Extract the archive.

Then double-click:

`Run_Project_Foreman.bat`

Or run:

```powershell
python -m project_foreman
```

Open:

`http://127.0.0.1:8765`

## Demo Flow

```text
Load Fixture
→ Recover Project
→ inspect Project Spine
→ inspect Authority Ledger
→ inspect Evidence Boundary
→ open Continuation Brief
→ verify exact Source Evidence
→ Export Package
```

Validated exports are written to:

`%USERPROFILE%\Downloads\Project_Foreman_Exports`

Each evidence-bound export contains nine files:

- five governed JSON artifacts: Project Spine, Authority Ledger, Continuation Brief, Source Trace Index, and Evidence Boundary;
- two human-readable Markdown views: Project Spine and Continuation Brief;
- `Manifest.json`;
- `CHECKSUMS.sha256`.

## Current Scope

This Build Week vertical slice supports:

- the included sanitized fixture;
- deterministic recovery outputs;
- structured operator commands;
- reviewed continuation state;
- exact source-turn inspection;
- explicit evidence-bound packet policy;
- validated package export.

## Build Week Development with Codex and GPT-5.6

Project Foreman grew from earlier Torch & Key conversation-recovery research. During the Build Week submission period, that work was meaningfully extended into the public **v0.2.0** vertical slice in this repository:

- a sanitized, deterministic Atlas Workshop fixture and judge-ready local application;
- an explicit fail-closed Evidence Boundary;
- truthful six-stage recovery and export progress;
- a validated nine-file evidence-bound project packet;
- a 27-test regression suite and reconciled release evidence;
- public repository, website, demonstration, and submission materials.

GPT-5.6 was used through Codex as a reasoning model in the submission-period build and reconciliation workflow. Codex helped:

- audit the existing project and determine the strongest competition entry and positioning;
- translate the accepted concept into requirements, action lists, Kanban plans, folder controls, and acceptance criteria;
- implement and reconcile the Python application, interface, evidence rules, staged status mechanism, tests, manifests, checksums, and release metadata;
- organize the supporting GitHub and public website surfaces;
- support video planning and editing, submission continuity, deadline control, and final compliance audits.

The operator retained authority over the product concept, track, scope, public claims, engineering boundaries, merges, publication, and final acceptance. Codex outputs remained proposals until reviewed or explicitly accepted.

Project Foreman itself makes no external model or API calls at runtime. GPT-5.6 and Codex were development and reconciliation tools, not hidden runtime dependencies.

## Verify the Release

From the repository root, run:

```powershell
python -m unittest discover -s tests -v
```

The accepted v0.2.0 release result is **27 tests run, zero failures, zero errors**. The complete machine-readable evidence is preserved in [`PUBLIC_RELEASE_TEST_RECEIPT.txt`](PUBLIC_RELEASE_TEST_RECEIPT.txt), [`RELEASE.json`](RELEASE.json), and [`CHECKSUMS.sha256`](CHECKSUMS.sha256).

## Repository Privacy

The real 29,345-turn validation corpus is private and is not included in the repository, application, screenshots, or demo video.
