"""Topology domain model (SPEC-001)."""

from __future__ import annotations

from dataclasses import dataclass

from commodore.core.models.host import Host


@dataclass(frozen=True)
class Topology:
    hosts: tuple[Host, ...]

    def __post_init__(self) -> None:
        names = [h.name for h in self.hosts]
        if len(names) != len(set(names)):
            raise ValueError(f"Duplicate host name in topology: {names}")

    def get_host(self, name: str) -> Host | None:
        for host in self.hosts:
            if host.name == name:
                return host
        return None

    def hosts_with_role(self, role: str) -> list[Host]:
        return [h for h in self.hosts if role in h.roles]
