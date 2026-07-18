# Project Foreman — Known Limitations

## Competition Build Limitations

1. **Fixture-scoped vertical slice**

   The current interface ships with one hybrid synthetic fixture. It demonstrates the recovery model but is not yet a general-purpose importer for arbitrary public conversation exports.

2. **Deterministic competition outputs**

   The demonstration uses deterministic golden outputs so the three-minute run is fast and reproducible. The underlying Lavatorium pipeline performs broader normalization and authority analysis outside this competition package.

3. **Natural-language authority remains provisional**

   Structured operator commands are canonical. Natural-language approvals, holds, and scope statements are visibly marked provisional until reviewed.

4. **No full supersession graph**

   The current build does not fully resolve every amend, supersede, revoke, or dependency relationship between decisions.

5. **No execution inference from commands**

   A command can authorize work without proving that the work occurred. Completion requires separate evidence.

6. **Local-only application**

   The build runs on the operator's computer and does not provide hosted accounts, cloud collaboration, or team permissions.

7. **Read-only interface**

   The dashboard supports inspection and export. Editing recovered records from the interface is not included.

8. **Windows download protection**

   Windows may mark downloaded ZIP files as Internet-origin content. Users may need to select `Properties → Unblock` before extraction.

9. **Private scale corpus excluded**

   The 29,345-turn corpus is used only as private validation evidence and is not distributed.

## Why These Limitations Are Acceptable

The Build Week version is designed to prove one central claim:

> A long AI conversation can be transformed into a navigable, authority-aware, source-traceable project workspace.

Broader ingestion, hosted deployment, collaborative review, and project-graph intelligence remain future work.
