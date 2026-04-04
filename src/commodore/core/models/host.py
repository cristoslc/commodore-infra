"""Host domain model (SPEC-001)."""

from __future__ import annotations

from dataclasses import dataclass

from commodore.core.models.classification import SecurityClassification


@dataclass(frozen=True)
class Host:
    name: str
    address: str
    roles: frozenset[str]
    classification: SecurityClassification

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Host requires a non-empty name")
