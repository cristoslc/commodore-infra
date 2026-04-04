"""Topology domain model (SPEC-001)."""

from __future__ import annotations

from dataclasses import dataclass

from commodore.core.models.host import Host
from commodore.core.models.segment import NetworkSegment


@dataclass(frozen=True)
class Topology:
    hosts: tuple[Host, ...]
    segments: tuple[NetworkSegment, ...] = ()

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

    def hosts_on_segment(self, segment: str) -> list[Host]:
        return [h for h in self.hosts if segment in h.segments]

    def can_reach(self, source: Host, target: Host) -> bool:
        """Check if source host can reach target host via shared or reachable segments."""
        # Same host is always reachable
        if source.name == target.name:
            return True

        # Shared segment means reachable
        if source.segments & target.segments:
            return True

        # Check directed reachability: source's segments appear in target's segments' reachable_from
        seg_map = {s.name: s for s in self.segments}
        for target_seg_name in target.segments:
            target_seg = seg_map.get(target_seg_name)
            if target_seg and target_seg.reachable_from & source.segments:
                return True

        return False
