from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .model import (
    BoardConfig,
    BoardSnapshot,
    Card,
    CardResult,
    CardState,
    EvidenceResult,
    EvidenceRule,
    RepositoryState,
    RuleGroup,
)


def load_config(path: Path) -> BoardConfig:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Status configuration not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    config = BoardConfig.from_dict(payload)
    _validate_config(config)
    return config


def _validate_config(config: BoardConfig) -> None:
    ids = [card.card_id for card in config.cards]
    duplicates = sorted({card_id for card_id in ids if ids.count(card_id) > 1})
    if duplicates:
        raise ValueError(f"Duplicate card IDs: {', '.join(duplicates)}")
    known = set(ids)
    for card in config.cards:
        missing = sorted(set(card.dependencies) - known)
        if missing:
            raise ValueError(f"{card.card_id} has unknown dependencies: {', '.join(missing)}")
    hold_ids = [hold.hold_id for hold in config.holds]
    duplicate_holds = sorted({hold_id for hold_id in hold_ids if hold_ids.count(hold_id) > 1})
    if duplicate_holds:
        raise ValueError(f"Duplicate hold IDs: {', '.join(duplicate_holds)}")


def _glob(root: Path, pattern: str) -> tuple[Path, ...]:
    candidate = Path(pattern)
    if candidate.is_absolute():
        return ()
    return tuple(sorted(root.glob(pattern)))


def evaluate_rule(root: Path, rule: EvidenceRule) -> EvidenceResult:
    matches = tuple(path for path in _glob(root, rule.path) if path.exists())
    filtered: list[Path] = []
    reason = ""
    for path in matches:
        if rule.contains is None and rule.regex is None:
            filtered.append(path)
            continue
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if rule.contains is not None and rule.contains not in content:
            continue
        if rule.regex is not None and re.search(rule.regex, content, flags=re.MULTILINE) is None:
            continue
        filtered.append(path)
    matched = len(filtered) >= rule.min_matches
    if not matched:
        reason = f"need {rule.min_matches}, found {len(filtered)}"
    return EvidenceResult(rule=rule, matched=matched, matches=tuple(filtered), reason=reason)


def evaluate_group(root: Path, group: RuleGroup) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:
    if group.empty:
        return False, (), ()
    all_results = tuple(evaluate_rule(root, rule) for rule in group.all)
    any_results = tuple(evaluate_rule(root, rule) for rule in group.any)
    none_results = tuple(evaluate_rule(root, rule) for rule in group.none)

    all_ok = all(result.matched for result in all_results)
    any_ok = True if not any_results else any(result.matched for result in any_results)
    none_ok = all(not result.matched for result in none_results)
    matched = all_ok and any_ok and none_ok

    satisfied = [result.rule.label for result in (*all_results, *any_results) if result.matched]
    satisfied.extend(f"absent: {result.rule.label}" for result in none_results if not result.matched)

    missing = [result.rule.label for result in all_results if not result.matched]
    if any_results and not any(result.matched for result in any_results):
        missing.append("one of: " + "; ".join(result.rule.label for result in any_results))
    missing.extend(f"must be absent: {result.rule.label}" for result in none_results if result.matched)
    return matched, tuple(missing), tuple(satisfied)


def repository_state(root: Path) -> RepositoryState:
    def run(*args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3,
        )
        return completed.stdout.strip()

    try:
        branch = run("branch", "--show-current") or "detached"
        head = run("rev-parse", "--short=12", "HEAD")
        clean = not bool(run("status", "--porcelain"))
        return RepositoryState(branch=branch, clean=clean, head=head, available=True)
    except (OSError, subprocess.SubprocessError):
        return RepositoryState()


def evaluate_board(config: BoardConfig, root: Path) -> BoardSnapshot:
    root = root.resolve()
    hold_map = {hold.hold_id: hold for hold in config.holds}
    results: dict[str, CardResult] = {}
    unresolved = {card.card_id: card for card in config.cards}

    for _ in range(max(1, len(unresolved) + 1)):
        progressed = False
        for card_id, card in tuple(unresolved.items()):
            if any(dep not in results for dep in card.dependencies):
                continue
            results[card_id] = _evaluate_card(card, root, results, hold_map)
            del unresolved[card_id]
            progressed = True
        if not unresolved or not progressed:
            break

    for card in unresolved.values():
        results[card.card_id] = CardResult(
            card=card,
            state=CardState.BLOCKED,
            blockers=("dependency cycle or unresolved dependency",),
        )

    ordered = tuple(results[card.card_id] for card in config.cards)
    return BoardSnapshot(
        config=config,
        root=root,
        cards=ordered,
        repository=repository_state(root),
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def _evaluate_card(
    card: Card,
    root: Path,
    results: dict[str, CardResult],
    hold_map: dict[str, object],
) -> CardResult:
    blockers: list[str] = []
    for hold_id in card.blocked_by_holds:
        hold = hold_map.get(hold_id)
        if hold is None:
            blockers.append(f"unknown hold: {hold_id}")
        elif getattr(hold, "active", False):
            blockers.append(getattr(hold, "title", hold_id))

    blocked_match, _, blocked_evidence = evaluate_group(root, card.blocked_when)
    if blocked_match:
        blockers.extend(blocked_evidence or ("blocking evidence found",))
    if blockers:
        return CardResult(card=card, state=CardState.BLOCKED, blockers=tuple(blockers))

    done_match, done_missing, done_satisfied = evaluate_group(root, card.done_when)
    if done_match:
        return CardResult(card=card, state=CardState.DONE, matched=done_satisfied)

    review_match, review_missing, review_satisfied = evaluate_group(root, card.review_when)
    if review_match:
        missing = done_missing if not card.done_when.empty else ()
        return CardResult(card=card, state=CardState.REVIEW, missing=missing, matched=review_satisfied)

    active_match, active_missing, active_satisfied = evaluate_group(root, card.active_when)
    if active_match:
        missing = review_missing if not card.review_when.empty else done_missing
        return CardResult(card=card, state=CardState.ACTIVE, missing=missing, matched=active_satisfied)

    dependencies_done = all(results[dep].state is CardState.DONE for dep in card.dependencies)
    if dependencies_done:
        missing = active_missing or review_missing or done_missing
        return CardResult(card=card, state=CardState.READY, missing=missing)

    pending = tuple(dep for dep in card.dependencies if results[dep].state is not CardState.DONE)
    return CardResult(card=card, state=CardState.PLANNED, blockers=pending)


def snapshot_to_dict(snapshot: BoardSnapshot) -> dict[str, object]:
    return {
        "generated_at": snapshot.generated_at,
        "project": {
            "id": snapshot.config.project_id,
            "name": snapshot.config.project_name,
            "current_gate": snapshot.config.current_gate,
            "return_point": snapshot.config.return_point,
            "root": str(snapshot.root),
        },
        "repository": {
            "available": snapshot.repository.available,
            "branch": snapshot.repository.branch,
            "head": snapshot.repository.head,
            "clean": snapshot.repository.clean,
        },
        "completion_percent": snapshot.completion_percent,
        "counts": snapshot.counts,
        "holds": [
            {"id": hold.hold_id, "title": hold.title, "active": hold.active, "detail": hold.detail}
            for hold in snapshot.config.holds
        ],
        "cards": [
            {
                "id": result.card.card_id,
                "title": result.card.title,
                "gate": result.card.gate,
                "state": result.state.value,
                "dependencies": list(result.card.dependencies),
                "missing": list(result.missing),
                "matched": list(result.matched),
                "blockers": list(result.blockers),
            }
            for result in snapshot.cards
        ],
    }
