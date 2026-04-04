"""Secret store driven port protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class SecretPort(Protocol):
    def get(self, ref: str) -> str: ...
    def get_batch(self, refs: list[str]) -> dict[str, str]: ...
    def health(self) -> bool: ...
