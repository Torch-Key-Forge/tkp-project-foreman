# PF-GTC Control State

**Control version:** `1.1.0`  
**State:** `FORMATION_SCAFFOLD_ACTIVE_BUILD_STATUS_UTILITY_AUTHORIZED_APPLICATION_HELD`  
**Parent branch:** `main`  
**Feature branch:** `feature/governed-token-continuity`

## Accepted authority

```text
REFERENCE_DOSSIER_V1_0_0: ACCEPTED_CANONICAL_GATE_3_DOD_BASELINE
GATE_3: CLOSED_ACCEPTED
CONTROLLING_GATE_4_PLAN: PF_GTC_Gate_4_Controlled_Good_Build_Plan_v0.1.1
GATE_4_PLAN_STATE: REVISED_PLAN_ONLY
GATE_4A_0: NOT_AUTHORIZED
GATE_4_EXECUTION: NOT_AUTHORIZED
BUILD_STATUS_UTILITY: LIMITED_IMPLEMENTATION_AUTHORIZED
```

## Limited build-status authorization

The operator explicitly authorized an automatic Rich/Python Kanban mechanism for the build project. This permits only:

- `build_status/` evidence-evaluation and rendering code;
- `BUILD_STATUS.json` board configuration;
- local Rich terminal display;
- plain-text and JSON snapshots;
- launchers, tests, documentation, and receipts for that utility.

The utility is non-authoritative. It reports configured evidence and never grants acceptance.

## Good baseline

- custom Python executor;
- local stdio MCP Context Gateway;
- P0-D1 authority-aware context policy;
- Paritok 1.2.3 component-contract adapter;
- deterministic in-process compression fixture for contract testing;
- raw fallback and exact-anchor protection;
- local-only observability;
- synthetic fixtures only.

## Active holds

```text
LIVE_MODEL_PROVIDER: HOLD
JCODE_RUNTIME: HOLD
GITHUB_ACTIONS: HOLD
PRIVATE_PROJECT_FOREMAN_CORPUS: HOLD
HOSTED_PARITOK_SERVICE: HOLD
EXTERNAL_TELEMETRY: HOLD
PRODUCTION_MUTATION_AND_DEPLOYMENT: HOLD
PF_GTC_APPLICATION_IMPLEMENTATION: HOLD
```

## Prohibited repository actions

Until separately authorized:

- no PF-GTC application runtime source files beyond the build-status utility;
- no root package or lockfile changes;
- no workflow files;
- no secrets or provider configuration;
- no private corpus or recovered private conversation material;
- no live API calls;
- no merge into `main`;
- no release or deployment claim.

## Current return point

```text
OPERATOR_REVIEW_OF_GATE_4_CONTROLLED_GOOD_BUILD_PLAN_V0_1_1
AND_BOUNDED_GATE_4A_0_AUTHORIZATION
```

Gate 4A-0 must close the execution-platform decision, Python and dependency lock, offline wheelhouse, Contract Schema Pack v0.2.0, plan-specific reference addendum, tokenizer asset custody, Gate 3 errata, and its closure receipt. The build must then stop again for review.

## Supersession note

The later-created `PF_GTC_Gate_4_Implementation_and_Compatibility_Plan_v0.1.0` does not control execution. The explicit revised Plan v0.1.1 remains controlling. Any authorization referencing the superseded v0.1.0 plan is stale and not grantable as written.

## Merge rule

This branch may be merged only after a future operator acceptance explicitly authorizes the relevant repository state. The automatic status utility and its passing tests do not constitute acceptance of the PF-GTC application build.
