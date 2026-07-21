# Automatic Rich Build Kanban

This is an evidence-driven build-control display for PF-GTC. Cards move automatically when configured artifacts and receipts appear in the project tree.

## States

- `Planned`: dependencies are incomplete.
- `Ready`: dependencies are done and no blocking hold applies.
- `Active`: start evidence exists.
- `Review`: expected outputs exist but acceptance evidence is missing.
- `Blocked`: an active hold or failure receipt applies.
- `Done`: configured acceptance evidence exists.

The board never treats elapsed time or a manually chosen percentage as proof of completion.

## Run

From `extensions/governed-token-continuity`:

```powershell
python -m pip install -r requirements-status.txt
python -m build_status snapshot --root .
python -m build_status watch --root .
python -m build_status json --root . --output BUILD_STATUS_SNAPSHOT.json
```

Use `--plain` for a non-Rich terminal.

## Configuration

`BUILD_STATUS.json` defines the cards, dependencies, holds, and evidence rules. Evidence paths are project-relative globs. Rules may require a text substring or regular expression and may require multiple matching files.

The engine reloads the configuration during watch mode, so the board can evolve without restarting.

## Trust boundary

This is a reporting mechanism, not a decision authority. The accepted UPSP and operator records remain controlling. The board may surface an inconsistency, but it may not resolve one or promote a draft by itself.
