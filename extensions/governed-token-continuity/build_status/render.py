from __future__ import annotations

from collections import defaultdict

from .model import BoardSnapshot, CardResult, CardState

STATE_LABELS = {
    CardState.PLANNED: "PLANNED",
    CardState.READY: "READY",
    CardState.ACTIVE: "ACTIVE",
    CardState.REVIEW: "REVIEW",
    CardState.BLOCKED: "BLOCKED",
    CardState.DONE: "DONE",
}

STATE_STYLES = {
    CardState.PLANNED: "dim",
    CardState.READY: "cyan",
    CardState.ACTIVE: "bold yellow",
    CardState.REVIEW: "bold magenta",
    CardState.BLOCKED: "bold red",
    CardState.DONE: "bold green",
}


def render_rich(snapshot: BoardSnapshot):
    try:
        from rich.console import Group
        from rich.layout import Layout
        from rich.panel import Panel
        from rich.progress_bar import ProgressBar
        from rich.table import Table
        from rich.text import Text
    except ImportError as exc:
        raise RuntimeError("Rich is required. Install with: python -m pip install rich==15.0.0") from exc

    header = Table.grid(expand=True)
    header.add_column(ratio=3)
    header.add_column(justify="right", ratio=2)
    header.add_row(
        Text(f"{snapshot.config.project_id} · {snapshot.config.project_name}", style="bold"),
        Text(f"Gate: {snapshot.config.current_gate}", style="bold cyan"),
    )
    header.add_row(
        Text(f"Return point: {snapshot.config.return_point}", style="dim"),
        Text(snapshot.generated_at, style="dim"),
    )

    progress = Table.grid(expand=True)
    progress.add_column(ratio=4)
    progress.add_column(width=8, justify="right")
    progress.add_row(ProgressBar(total=100, completed=snapshot.completion_percent), f"{snapshot.completion_percent}%")

    repo = snapshot.repository
    clean_label = "clean" if repo.clean is True else "dirty" if repo.clean is False else "unknown"
    repo_line = (
        f"branch={repo.branch}  head={repo.head}  worktree={clean_label}"
        if repo.available
        else "Git state unavailable"
    )

    summary = Table.grid(expand=True)
    for _ in CardState:
        summary.add_column(justify="center")
    summary.add_row(*(Text(STATE_LABELS[state], style=STATE_STYLES[state]) for state in CardState))
    summary.add_row(*(str(snapshot.counts[state.value]) for state in CardState))

    layout = Layout()
    layout.split_column(
        Layout(Panel(Group(header, progress, Text(repo_line, style="dim")), title="Build Control"), size=8),
        Layout(Panel(summary, title="Board Summary"), size=5),
        Layout(Panel(_kanban_table(snapshot), title="Automatic Kanban"), ratio=3),
        Layout(name="footer", size=9),
    )
    layout["footer"].split_row(Layout(_holds_panel(snapshot)), Layout(_attention_panel(snapshot)))
    return layout


def _kanban_table(snapshot: BoardSnapshot):
    from rich.table import Table
    from rich.text import Text

    table = Table(expand=True, show_header=True, header_style="bold")
    states = list(CardState)
    for state in states:
        table.add_column(STATE_LABELS[state], ratio=1, overflow="fold")

    grouped: dict[CardState, list[CardResult]] = defaultdict(list)
    for result in snapshot.cards:
        grouped[result.state].append(result)
    rows = max([len(grouped[state]) for state in states] + [1])
    for index in range(rows):
        cells = []
        for state in states:
            cards = grouped[state]
            if index >= len(cards):
                cells.append("")
                continue
            result = cards[index]
            text = Text()
            text.append(f"{result.card.card_id}\n", style=STATE_STYLES[state])
            text.append(result.card.title)
            if result.card.gate:
                text.append(f"\n[{result.card.gate}]", style="dim")
            cells.append(text)
        table.add_row(*cells)
    return table


def _holds_panel(snapshot: BoardSnapshot):
    from rich.panel import Panel
    from rich.text import Text

    text = Text()
    active = [hold for hold in snapshot.config.holds if hold.active]
    if not active:
        text.append("No active holds", style="green")
    else:
        for hold in active:
            text.append("● ", style="red")
            text.append(hold.title)
            if hold.detail:
                text.append(f" — {hold.detail}", style="dim")
            text.append("\n")
    return Panel(text, title=f"Active Holds ({len(active)})", border_style="red" if active else "green")


def _attention_panel(snapshot: BoardSnapshot):
    from rich.panel import Panel
    from rich.text import Text

    text = Text()
    attention = [
        result
        for result in snapshot.cards
        if result.state in {CardState.ACTIVE, CardState.REVIEW, CardState.BLOCKED}
    ]
    if not attention:
        ready = snapshot.by_state(CardState.READY)
        if ready:
            text.append("Next ready: ", style="bold")
            text.append(f"{ready[0].card.card_id} — {ready[0].card.title}")
        else:
            text.append("No active attention items", style="dim")
    else:
        for result in attention[:5]:
            text.append(f"{result.card.card_id} · {STATE_LABELS[result.state]}\n", style=STATE_STYLES[result.state])
            details = result.blockers or result.missing
            for item in details[:3]:
                text.append(f"  - {item}\n", style="dim")
    return Panel(text, title="Needs Attention")


def render_plain(snapshot: BoardSnapshot) -> str:
    lines = [
        f"{snapshot.config.project_id} | {snapshot.config.current_gate} | {snapshot.completion_percent}% done",
        f"Return point: {snapshot.config.return_point}",
    ]
    for state in CardState:
        cards = snapshot.by_state(state)
        lines.append(f"\n{STATE_LABELS[state]} ({len(cards)})")
        for result in cards:
            suffix = ""
            if result.blockers:
                suffix = " | blocked by: " + ", ".join(result.blockers)
            elif result.missing:
                suffix = " | missing: " + ", ".join(result.missing)
            lines.append(f"  {result.card.card_id}: {result.card.title}{suffix}")
    return "\n".join(lines)
