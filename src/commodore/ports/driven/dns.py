"""DNS driven port protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from commodore.ports.driven.base import Change, Result


@dataclass(frozen=True)
class DNSState:
    records: list[dict[str, Any]] = field(default_factory=list)


@runtime_checkable
class DNSPort(Protocol):
    def current_state(self) -> DNSState: ...
    def diff(self, desired: list[dict[str, Any]]) -> list[Change]: ...
    def apply(self, changes: list[Change]) -> Result: ...
