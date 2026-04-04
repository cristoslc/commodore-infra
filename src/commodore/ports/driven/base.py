"""Shared types for all driven ports."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Change:
    port: str
    action: str  # create, update, delete
    resource_id: str
    before: Any
    after: Any


@dataclass(frozen=True)
class Result:
    success: bool
    changes_applied: int
    errors: list[str] = field(default_factory=list)


class PortError(Exception):
    def __init__(self, port: str, message: str) -> None:
        self.port = port
        super().__init__(f"[{port}] {message}")
