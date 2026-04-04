"""Network segment model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkSegment:
    name: str
    cidr: str = ""
    reachable_from: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("NetworkSegment requires a non-empty name")
