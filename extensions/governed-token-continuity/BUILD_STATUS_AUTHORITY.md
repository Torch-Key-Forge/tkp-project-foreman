# PF-GTC Automatic Build Status Authority

**Status:** `LIMITED_BUILD_CONTROL_IMPLEMENTATION_AUTHORIZED`  
**Scope:** Rich terminal Kanban and evidence-derived build status only

The operator explicitly requested an automatic Rich/Python Kanban mechanism for the build project. This authorization permits the branch-only build-control utility contained in `build_status/`, its status configuration, tests, and documentation.

It does **not** authorize the PF-GTC application runtime, the authority-aware context governor, MCP gateway, Paritok adapter, custom executor, live model calls, hosted CI, private corpus, deployment, or merge to `main`.

The status engine is non-authoritative. It reports the evidence it observes. A card reaches `Done` only when its configured acceptance evidence exists; the display itself never grants acceptance.
