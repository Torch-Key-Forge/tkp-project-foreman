from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class CardState(str, Enum):
    PLANNED = "planned"
    READY = "ready"
    ACTIVE = "active"
    REVIEW = "review"
    BLOCKED = "blocked"
    DONE = "done"


@dataclass(frozen=True)
class EvidenceRule:
    label: str
    path: str
    contains: str | None = None
    regex: str | None = None
    min_matches: int = 1

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceRule":
        return cls(
            label=str(data.get("label") or data["path"]),
            path=str(data["path"]),
            contains=data.get("contains"),
            regex=data.get("regex"),
            min_matches=int(data.get("min_matches", 1)),
        )


@dataclass(frozen=True)
class RuleGroup:
    all: tuple[EvidenceRule, ...] = ()
    any: tuple[EvidenceRule, ...] = ()
    none: tuple[EvidenceRule, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "RuleGroup":
        data = data or {}
        return cls(
            all=tuple(EvidenceRule.from_dict(item) for item in data.get("all", [])),
            any=tuple(EvidenceRule.from_dict(item) for item in data.get("any", [])),
            none=tuple(EvidenceRule.from_dict(item) for item in data.get("none", [])),
        )

    @property
    def empty(self) -> bool:
        return not (self.all or self.any or self.none)


@dataclass(frozen=True)
class Hold:
    hold_id: str
    title: str
    active: bool
    detail: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Hold":
        return cls(
            hold_id=str(data["id"]),
            title=str(data["title"]),
            active=bool(data.get("active", True)),
            detail=str(data.get("detail", "")),
        )


@dataclass(frozen=True)
class Card:
    card_id: str
    title: str
    gate: str
    description: str = ""
    dependencies: tuple[str, ...] = ()
    blocked_by_holds: tuple[str, ...] = ()
    active_when: RuleGroup = field(default_factory=RuleGroup)
    review_when: RuleGroup = field(default_factory=RuleGroup)
    done_when: RuleGroup = field(default_factory=RuleGroup)
    blocked_when: RuleGroup = field(default_factory=RuleGroup)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Card":
        return cls(
            card_id=str(data["id"]),
            title=str(data["title"]),
            gate=str(data.get("gate", "")),
            description=str(data.get("description", "")),
            dependencies=tuple(str(v) for v in data.get("dependencies", [])),
            blocked_by_holds=tuple(str(v) for v in data.get("blocked_by_holds", [])),
            active_when=RuleGroup.from_dict(data.get("active_when")),
            review_when=RuleGroup.from_dict(data.get("review_when")),
            done_when=RuleGroup.from_dict(data.get("done_when")),
            blocked_when=RuleGroup.from_dict(data.get("blocked_when")),
        )


@dataclass(frozen=True)
class BoardConfig:
    project_id: str
    project_name: str
    current_gate: str
    return_point: str
    root_hint: str
    cards: tuple[Card, ...]
    holds: tuple[Hold, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BoardConfig":
        project = data.get("project", {})
        return cls(
            project_id=str(project.get("id", "UNKNOWN")),
            project_name=str(project.get("name", "Unnamed project")),
            current_gate=str(project.get("current_gate", "UNSET")),
            return_point=str(project.get("return_point", "UNSET")),
            root_hint=str(project.get("root_hint", ".")),
            cards=tuple(Card.from_dict(item) for item in data.get("cards", [])),
            holds=tuple(Hold.from_dict(item) for item in data.get("holds", [])),
        )


@dataclass(frozen=True)
class EvidenceResult:
    rule: EvidenceRule
    matched: bool
    matches: tuple[Path, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class CardResult:
    card: Card
    state: CardState
    missing: tuple[str, ...] = ()
    matched: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()


@dataclass(frozen=True)
class RepositoryState:
    branch: str = "unknown"
    clean: bool | None = None
    head: str = "unknown"
    available: bool = False


@dataclass(frozen=True)
class BoardSnapshot:
    config: BoardConfig
    root: Path
    cards: tuple[CardResult, ...]
    repository: RepositoryState
    generated_at: str

    def by_state(self, state: CardState) -> tuple[CardResult, ...]:
        return tuple(card for card in self.cards if card.state is state)

    @property
    def counts(self) -> dict[str, int]:
        return {state.value: len(self.by_state(state)) for state in CardState}

    @property
    def completion_percent(self) -> int:
        if not self.cards:
            return 0
        return round(100 * len(self.by_state(CardState.DONE)) / len(self.cards))
