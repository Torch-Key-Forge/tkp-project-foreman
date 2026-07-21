# Governed Token Continuity

**Project ID:** `PF-GTC`  
**Parent product:** Project Foreman  
**Repository status:** Formation scaffold only  
**Implementation status:** Not authorized

Governed Token Continuity is a Project Foreman capability for reducing continuation context while preserving controlling authority, exact execution anchors, provenance, and recoverability.

It is not a separate product identity or an independent agent framework. The Good baseline is planned as a lean Project Foreman extension using a custom Python executor, a local stdio MCP context gateway, an authority-aware context governor, and a replaceable Paritok adapter.

## Controlling architecture

```text
Project Foreman evidence and continuation state
    -> authority-aware context governor
    -> local Foreman context gateway
    -> Paritok component-contract adapter or raw bypass
    -> bounded custom Python executor
    -> verification and local receipts
```

## Current authority state

- Reference Dossier v1.0.0 is the accepted canonical Gate 3 DoD baseline.
- Gate 4 Controlled Good Build Plan v0.1.1 is the controlling revised plan.
- Gate 4A-0 has not been authorized.
- No implementation work is authorized by this scaffold.
- The live-model, jcode-runtime, GitHub Actions, private-corpus, and production/deployment holds remain active.

See [`CONTROL_STATE.md`](CONTROL_STATE.md) for the precise return point and restrictions.

## Planned lanes

These paths describe the intended module shape. They are not implementation claims.

```text
extensions/governed-token-continuity/
├── README.md
├── CONTROL_STATE.md
├── docs/
│   └── REFERENCE_AND_AUTHORITY.md
├── schemas/        # held until Gate 4A-0 authorization
├── src/            # held until Gate 4 execution authorization
├── tests/          # held until Gate 4 execution authorization
└── fixtures/       # synthetic-only when authorized
```

## Evidence boundary

The extension inherits Project Foreman's core rule: **No source, no claim.**

Synthetic component receipts may prove local contracts and invariants, but they may not be presented as live-provider savings, real billing results, or production compatibility.

## Canonical project custody

The governing Drive environment remains:

`I:\My Drive\01_Forge\Paritok_Hack_a_thon`

The Git branch is a controlled code-formation surface, not a replacement for the accepted Drive authority records.