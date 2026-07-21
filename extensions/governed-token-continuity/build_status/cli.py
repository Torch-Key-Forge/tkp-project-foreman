from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .engine import evaluate_board, load_config, snapshot_to_dict
from .render import render_plain, render_rich


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pf-gtc-status",
        description="Automatic evidence-driven Rich Kanban for the PF-GTC build.",
    )
    parser.add_argument(
        "command",
        choices=("snapshot", "watch", "json"),
        nargs="?",
        default="snapshot",
        help="Render once, watch continuously, or emit machine-readable JSON.",
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root to scan.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("BUILD_STATUS.json"),
        help="Board configuration. Relative paths are resolved from --root.",
    )
    parser.add_argument("--interval", type=float, default=1.0, help="Watch refresh interval in seconds.")
    parser.add_argument("--plain", action="store_true", help="Use plain text instead of Rich.")
    parser.add_argument("--output", type=Path, help="Write JSON snapshot to this path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    config_path = args.config if args.config.is_absolute() else root / args.config
    try:
        if args.command == "watch":
            return _watch(root, config_path, args.interval, args.plain)
        snapshot = evaluate_board(load_config(config_path), root)
        if args.command == "json":
            payload = json.dumps(snapshot_to_dict(snapshot), indent=2)
            if args.output:
                args.output.write_text(payload + "\n", encoding="utf-8")
            else:
                print(payload)
        elif args.plain:
            print(render_plain(snapshot))
        else:
            from rich.console import Console

            Console().print(render_rich(snapshot))
        return 0
    except (ValueError, RuntimeError) as exc:
        print(f"status error: {exc}", file=sys.stderr)
        return 2


def _watch(root: Path, config_path: Path, interval: float, plain: bool) -> int:
    if interval < 0.2:
        raise ValueError("--interval must be at least 0.2 seconds")
    if plain:
        try:
            while True:
                snapshot = evaluate_board(load_config(config_path), root)
                print("\033[2J\033[H" + render_plain(snapshot), flush=True)
                time.sleep(interval)
        except KeyboardInterrupt:
            return 0

    try:
        from rich.live import Live
    except ImportError as exc:
        raise RuntimeError("Rich is required. Install with: python -m pip install rich==15.0.0") from exc

    try:
        initial = evaluate_board(load_config(config_path), root)
        with Live(render_rich(initial), refresh_per_second=4, screen=False) as live:
            while True:
                snapshot = evaluate_board(load_config(config_path), root)
                live.update(render_rich(snapshot), refresh=True)
                time.sleep(interval)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
