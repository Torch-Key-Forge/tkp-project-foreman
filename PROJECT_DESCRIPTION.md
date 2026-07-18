# Project Foreman

## One-Sentence Description

Project Foreman recovers traceable project state from long AI conversations by generating a project spine, verified authority ledger, continuation brief, and source-linked project package.

## Problem

Long AI conversations often contain valuable project work, but the raw history is difficult to navigate, verify, resume, or hand off. Ordinary summarization may describe what was discussed without preserving who authorized what, what actually failed, where work stopped, or which source turn supports a recovered claim.

## Solution

Project Foreman converts conversation history into a structured project workspace.

The competition build produces:

- a navigable chronology of project-changing events;
- a decision and authority ledger that separates operator commands from assistant suggestions;
- a continuation brief identifying completed work, unresolved items, active boundaries, and the next action;
- exact source-turn traceability;
- an exported Markdown and JSON package with manifests and checksums.

## What Makes It Different

Most conversation tools summarize content.

Project Foreman reconstructs project state.

Its trust model preserves several distinctions that summarization systems often blur:

- operator authority versus assistant proposal;
- command issuance versus execution evidence;
- accepted state versus unresolved work;
- source identity versus duplicate content;
- recovered claim versus supporting source turn.

## Demonstration

The live demo uses a small public-safe hybrid synthetic fixture so the recovery is fast and deterministic.

The underlying pipeline was validated against a private corpus containing:

- 328 conversations;
- 29,345 turns;
- 52 reconstructed forks;
- 180 verified structured operator commands.

The private corpus is not included or displayed.

## Technical Implementation

The competition build is a local Python application with:

- deterministic JSON fixtures;
- structured project and authority models;
- exact source-reference indexing;
- a lightweight local HTTP server;
- a single-screen browser interface;
- validated ZIP export;
- SHA-256 manifests and checksums;
- regression tests;
- no third-party Python dependencies.

## Potential Impact

Project Foreman can help individuals and teams recover unfinished projects from AI history, audit prior decisions, transfer work between people or models, and continue complex work without rereading an entire conversation.

Possible future applications include:

- project handoffs;
- regulated decision records;
- durable AI workspaces;
- support and consulting history;
- research provenance;
- software-development continuity;
- multi-conversation project recovery.

## Build Week Scope

The competition version intentionally focuses on one strong vertical slice:

```text
conversation
→ project spine
→ authority ledger
→ continuation brief
→ exact source trace
→ portable project package
```

The product is local-only, read-only, and uses a public-safe fixture.
