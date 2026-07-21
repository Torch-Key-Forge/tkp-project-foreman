# PF-GTC Control State

**Control version:** `1.0.0`  
**State:** `FORMATION_SCAFFOLD_ACTIVE_IMPLEMENTATION_HELD`  
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
```

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
```

## Prohibited repository actions

Until separately authorized:

- no implementation source files;
- no package or lockfile changes;
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

This branch may be merged only after a future operator acceptance explicitly authorizes the relevant repository state. Branch existence and scaffold commits do not constitute implementation acceptance.