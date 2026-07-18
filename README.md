# TKP Project Foreman

**Recover the valuable work trapped inside long AI conversations.**

Project Foreman converts a long, messy AI conversation into a traceable project workspace.

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

## Included Build

The competition build is a local, read-only Python application using only the Python standard library.

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
→ open Continuation Brief
→ verify exact Source Evidence
→ Export Package
```

Validated exports are written to:

`%USERPROFILE%\Downloads\Project_Foreman_Exports`

## Current Scope

This Build Week vertical slice supports:

- the included sanitized fixture;
- deterministic recovery outputs;
- structured operator commands;
- reviewed continuation state;
- exact source-turn inspection;
- validated package export.

## Repository Privacy

The real 29,345-turn validation corpus is private and is not included in the repository, application, screenshots, or demo video.
