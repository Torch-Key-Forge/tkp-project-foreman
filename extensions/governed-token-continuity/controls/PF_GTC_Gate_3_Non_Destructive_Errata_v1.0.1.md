# PF-GTC Reference Dossier v1.0.1 Non-Destructive Errata

**Errata ID:** `PF-GTC-GATE3-ERRATA-20260721-001`  
**Applies to:** `PF_GTC_Reference_Dossier_v1.0.0`  
**Status:** `ISSUED_NON_DESTRUCTIVE`  
**Original artifacts and checksums:** unchanged

## Correction

Any surviving statement that describes the accepted Gate 3 verification result as **17 tests** is corrected to:

```text
20 tests collected
20 tests passed
0 failures
0 errors
```

The accepted Gate 3 baseline remains v1.0.0. This errata does not rewrite or replace the accepted files.

## Canonical packet hygiene

The next canonical packet must exclude `.pytest_cache/`, `__pycache__/`, `*.pyc`, temporary virtual environments, and transient test output not named in the manifest.

## Authority

This implements Gate 4 Plan v0.1.1 section 3.6 without altering any other accepted Gate 3 decision, tool state, exception, or hold.
