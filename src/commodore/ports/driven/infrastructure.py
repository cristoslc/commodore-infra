"""Infrastructure driven port protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from commodore.ports.driven.base import Change, Result


@dataclass(frozen=True)
class InfraState:
    hosts: list[dict[str, Any]] = field(default_factory=list)


@runtime_checkable
class InfrastructurePort(Protocol):
    def current_state(self) -> InfraState: ...
    def diff(self, desired: list[dict[str, Any]]) -> list[Change]: ...
    def apply(self, changes: list[Change]) -> Result: ...
